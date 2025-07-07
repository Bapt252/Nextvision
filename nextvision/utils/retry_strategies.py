"""
🔄 Retry Strategies - Production Enterprise Grade

Logique de retry adaptative pour APIs externes et services :
• Google Maps API failures → Retry intelligent avec backoff
• Network timeouts → Retry escalating
• Database connections → Reconnection strategy
• Service unavailable → Circuit breaker integration
• Rate limiting → Intelligent throttling

Author: NEXTEN Team - Production Robustness
Version: 1.0.0
"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from functools import wraps

import aiohttp
from aiohttp import ClientError, ClientTimeout

from ..logging.structured_logging import get_structured_logger
from ..monitoring.health_metrics import HealthMetrics
from ..error_handling.graceful_degradation import ErrorCategory, get_degradation_manager

logger = get_structured_logger(__name__)
health_metrics = HealthMetrics()

class RetryStrategy(Enum):
    """🎯 Stratégies de retry disponibles"""
    FIXED_DELAY = "fixed_delay"           # Délai fixe
    EXPONENTIAL_BACKOFF = "exponential"   # Backoff exponentiel
    LINEAR_BACKOFF = "linear"             # Backoff linéaire
    FIBONACCI_BACKOFF = "fibonacci"       # Séquence Fibonacci
    ADAPTIVE_SMART = "adaptive"           # Adaptatif intelligent
    JITTERED_EXPONENTIAL = "jittered"     # Exponentiel avec jitter

class RetryCondition(Enum):
    """🎯 Conditions de retry"""
    ALL_EXCEPTIONS = "all"
    NETWORK_ERRORS = "network"
    TIMEOUT_ERRORS = "timeout"
    SERVER_ERRORS = "server"  # 5xx
    RATE_LIMIT_ERRORS = "rate_limit"  # 429
    SPECIFIC_EXCEPTIONS = "specific"
    CUSTOM_CONDITION = "custom"

@dataclass
class RetryConfig:
    """⚙️ Configuration retry adaptative"""
    # Retry Strategy
    strategy: RetryStrategy = RetryStrategy.JITTERED_EXPONENTIAL
    max_attempts: int = 5
    
    # Timing Configuration
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    exponential_base: float = 2.0
    jitter_factor: float = 0.1  # 10% jitter
    
    # Conditions
    retry_condition: RetryCondition = RetryCondition.NETWORK_ERRORS
    retryable_exceptions: Tuple[type, ...] = (
        ConnectionError, TimeoutError, aiohttp.ClientError
    )
    retryable_status_codes: Tuple[int, ...] = (429, 502, 503, 504)
    
    # Adaptive Features
    enable_adaptive_timing: bool = True
    success_rate_threshold: float = 0.8  # Ajuster délai si succès < 80%
    
    # Circuit Breaker Integration
    enable_circuit_breaker: bool = True
    circuit_failure_threshold: int = 5
    circuit_timeout_seconds: int = 30
    
    # Monitoring
    enable_detailed_logging: bool = True
    track_performance_metrics: bool = True

@dataclass
class RetryAttempt:
    """📊 Informations tentative retry"""
    attempt_number: int
    delay_used: float
    error: Optional[Exception]
    duration_ms: float
    timestamp: datetime
    success: bool = False
    
@dataclass
class RetryResult:
    """📈 Résultat complet avec historique"""
    success: bool
    result: Any = None
    final_error: Optional[Exception] = None
    
    # Statistiques
    total_attempts: int = 0
    total_duration_seconds: float = 0.0
    attempts_history: List[RetryAttempt] = field(default_factory=list)
    
    # Métadonnées
    strategy_used: RetryStrategy = RetryStrategy.FIXED_DELAY
    circuit_breaker_triggered: bool = False
    adaptive_adjustments_made: int = 0

class RetryManager:
    """🔄 Gestionnaire principal retry intelligent"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
        
        # Adaptive Learning
        self.service_performance: Dict[str, Dict] = {}  # service -> stats
        self.fibonacci_sequence = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
        
        # Circuit Breakers per service
        self.circuit_breakers: Dict[str, Dict] = {}
        
        logger.info("🔄 RetryManager initialized", extra={
            "strategy": config.strategy.value,
            "max_attempts": config.max_attempts,
            "adaptive_enabled": config.enable_adaptive_timing
        })
    
    async def execute_with_retry(self, 
                               func: Callable,
                               service_name: str = "default",
                               operation_name: str = "operation",
                               config_override: Optional[RetryConfig] = None,
                               *args, **kwargs) -> RetryResult:
        """🎯 Exécution avec retry intelligent"""
        
        effective_config = config_override or self.config
        start_time = time.time()
        attempts_history = []
        
        # Vérification circuit breaker
        if self._is_circuit_open(service_name):
            logger.warning(f"🚫 Circuit breaker OPEN for {service_name}", extra={
                "service": service_name,
                "operation": operation_name
            })
            return RetryResult(
                success=False,
                final_error=Exception(f"Circuit breaker OPEN for {service_name}"),
                circuit_breaker_triggered=True
            )
        
        logger.info(f"🚀 Starting retry execution", extra={
            "service": service_name,
            "operation": operation_name,
            "strategy": effective_config.strategy.value,
            "max_attempts": effective_config.max_attempts
        })
        
        last_error = None
        adaptive_adjustments = 0
        
        for attempt in range(1, effective_config.max_attempts + 1):
            attempt_start = time.time()
            
            try:
                logger.debug(f"🔄 Attempt {attempt}/{effective_config.max_attempts}", extra={
                    "service": service_name,
                    "operation": operation_name,
                    "attempt": attempt
                })
                
                # Exécution fonction
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Succès !
                attempt_duration = (time.time() - attempt_start) * 1000
                
                attempt_record = RetryAttempt(
                    attempt_number=attempt,
                    delay_used=0.0,
                    error=None,
                    duration_ms=attempt_duration,
                    timestamp=datetime.now(),
                    success=True
                )
                attempts_history.append(attempt_record)
                
                # Mise à jour performance service
                self._update_service_performance(service_name, True, attempt, time.time() - start_time)
                
                # Reset circuit breaker
                self._reset_circuit_breaker(service_name)
                
                logger.info(f"✅ Operation succeeded", extra={
                    "service": service_name,
                    "operation": operation_name,
                    "attempt": attempt,
                    "total_duration_ms": round((time.time() - start_time) * 1000, 2)
                })
                
                return RetryResult(
                    success=True,
                    result=result,
                    total_attempts=attempt,
                    total_duration_seconds=time.time() - start_time,
                    attempts_history=attempts_history,
                    strategy_used=effective_config.strategy,
                    adaptive_adjustments_made=adaptive_adjustments
                )
                
            except Exception as error:
                last_error = error
                attempt_duration = (time.time() - attempt_start) * 1000
                
                # Analyse si on doit retry
                should_retry = self._should_retry(error, effective_config)
                
                if not should_retry or attempt == effective_config.max_attempts:
                    # Échec final
                    attempt_record = RetryAttempt(
                        attempt_number=attempt,
                        delay_used=0.0,
                        error=error,
                        duration_ms=attempt_duration,
                        timestamp=datetime.now(),
                        success=False
                    )
                    attempts_history.append(attempt_record)
                    
                    self._update_service_performance(service_name, False, attempt, time.time() - start_time)
                    self._record_circuit_breaker_failure(service_name)
                    
                    logger.error(f"❌ Operation failed permanently", extra={
                        "service": service_name,
                        "operation": operation_name,
                        "total_attempts": attempt,
                        "final_error": str(error)[:300],
                        "should_retry": should_retry
                    })
                    
                    health_metrics.record_error(service_name, "retry_exhausted")
                    
                    return RetryResult(
                        success=False,
                        final_error=error,
                        total_attempts=attempt,
                        total_duration_seconds=time.time() - start_time,
                        attempts_history=attempts_history,
                        strategy_used=effective_config.strategy,
                        adaptive_adjustments_made=adaptive_adjustments
                    )
                
                # Calcul delay pour retry
                delay = self._calculate_delay(attempt, effective_config, service_name)
                
                # Adaptive adjustment si nécessaire
                if effective_config.enable_adaptive_timing:
                    adjusted_delay = self._adaptive_delay_adjustment(service_name, delay)
                    if adjusted_delay != delay:
                        adaptive_adjustments += 1
                        delay = adjusted_delay
                
                attempt_record = RetryAttempt(
                    attempt_number=attempt,
                    delay_used=delay,
                    error=error,
                    duration_ms=attempt_duration,
                    timestamp=datetime.now(),
                    success=False
                )
                attempts_history.append(attempt_record)
                
                logger.warning(f"⚠️ Attempt {attempt} failed, retrying in {delay:.2f}s", extra={
                    "service": service_name,
                    "operation": operation_name,
                    "attempt": attempt,
                    "error_type": type(error).__name__,
                    "error_message": str(error)[:200],
                    "delay_seconds": delay
                })
                
                # Attente avant retry
                await asyncio.sleep(delay)
        
        # Ne devrait jamais arriver, mais sécurité
        return RetryResult(
            success=False,
            final_error=last_error or Exception("Unknown retry failure"),
            total_attempts=effective_config.max_attempts,
            total_duration_seconds=time.time() - start_time,
            attempts_history=attempts_history,
            strategy_used=effective_config.strategy
        )
    
    def _should_retry(self, error: Exception, config: RetryConfig) -> bool:
        """🤔 Détermine si on doit retry selon l'erreur"""
        
        if config.retry_condition == RetryCondition.ALL_EXCEPTIONS:
            return True
        
        elif config.retry_condition == RetryCondition.SPECIFIC_EXCEPTIONS:
            return isinstance(error, config.retryable_exceptions)
        
        elif config.retry_condition == RetryCondition.NETWORK_ERRORS:
            network_errors = (
                ConnectionError, TimeoutError, 
                aiohttp.ClientError, aiohttp.ClientConnectorError,
                aiohttp.ClientTimeout, aiohttp.ServerTimeoutError
            )
            return isinstance(error, network_errors)
        
        elif config.retry_condition == RetryCondition.TIMEOUT_ERRORS:
            timeout_errors = (TimeoutError, asyncio.TimeoutError, aiohttp.ClientTimeout)
            return isinstance(error, timeout_errors)
        
        elif config.retry_condition == RetryCondition.SERVER_ERRORS:
            if hasattr(error, 'status') and hasattr(error.status, '__int__'):
                return 500 <= int(error.status) < 600
            return False
        
        elif config.retry_condition == RetryCondition.RATE_LIMIT_ERRORS:
            if hasattr(error, 'status') and hasattr(error.status, '__int__'):
                return int(error.status) == 429
            return "rate limit" in str(error).lower()
        
        return False
    
    def _calculate_delay(self, attempt: int, config: RetryConfig, service_name: str) -> float:
        """⏱️ Calcule délai selon la stratégie"""
        
        if config.strategy == RetryStrategy.FIXED_DELAY:
            delay = config.base_delay_seconds
        
        elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = config.base_delay_seconds * attempt
        
        elif config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = config.base_delay_seconds * (config.exponential_base ** (attempt - 1))
        
        elif config.strategy == RetryStrategy.FIBONACCI_BACKOFF:
            fib_index = min(attempt - 1, len(self.fibonacci_sequence) - 1)
            delay = config.base_delay_seconds * self.fibonacci_sequence[fib_index]
        
        elif config.strategy == RetryStrategy.JITTERED_EXPONENTIAL:
            base_delay = config.base_delay_seconds * (config.exponential_base ** (attempt - 1))
            jitter = base_delay * config.jitter_factor * (random.random() - 0.5)
            delay = base_delay + jitter
        
        elif config.strategy == RetryStrategy.ADAPTIVE_SMART:
            # Délai adaptatif basé sur performance service
            delay = self._adaptive_smart_delay(attempt, config, service_name)
        
        else:
            delay = config.base_delay_seconds
        
        # Limites
        delay = max(0.1, min(delay, config.max_delay_seconds))
        
        return delay
    
    def _adaptive_smart_delay(self, attempt: int, config: RetryConfig, service_name: str) -> float:
        """🧠 Délai adaptatif intelligent"""
        service_stats = self.service_performance.get(service_name, {})
        
        # Base exponentielle
        base_delay = config.base_delay_seconds * (config.exponential_base ** (attempt - 1))
        
        # Ajustement selon performance historique
        success_rate = service_stats.get('success_rate', 1.0)
        avg_response_time = service_stats.get('avg_response_time_ms', 100) / 1000.0
        
        # Si service lent ou instable, délais plus longs
        if success_rate < 0.5:  # Service très instable
            adjustment_factor = 2.0
        elif success_rate < 0.8:  # Service instable
            adjustment_factor = 1.5
        else:  # Service stable
            adjustment_factor = 1.0
        
        # Ajustement selon temps de réponse
        if avg_response_time > 5.0:  # Service très lent
            adjustment_factor *= 1.5
        elif avg_response_time > 2.0:  # Service lent
            adjustment_factor *= 1.2
        
        adaptive_delay = base_delay * adjustment_factor
        
        # Jitter pour éviter thundering herd
        jitter = adaptive_delay * 0.1 * (random.random() - 0.5)
        
        return adaptive_delay + jitter
    
    def _adaptive_delay_adjustment(self, service_name: str, base_delay: float) -> float:
        """🎯 Ajustement adaptatif du délai"""
        service_stats = self.service_performance.get(service_name, {})
        current_success_rate = service_stats.get('success_rate', 1.0)
        
        # Si taux de succès faible, augmenter délais
        if current_success_rate < self.config.success_rate_threshold:
            # Augmentation proportionnelle à la dégradation
            degradation_factor = self.config.success_rate_threshold / max(current_success_rate, 0.1)
            adjusted_delay = base_delay * degradation_factor
            
            logger.debug(f"🎯 Adaptive delay adjustment", extra={
                "service": service_name,
                "success_rate": current_success_rate,
                "original_delay": base_delay,
                "adjusted_delay": adjusted_delay,
                "factor": degradation_factor
            })
            
            return min(adjusted_delay, self.config.max_delay_seconds)
        
        return base_delay
    
    # ===============================================
    # 🔧 SERVICE PERFORMANCE TRACKING
    # ===============================================
    
    def _update_service_performance(self, service_name: str, success: bool, attempts: int, duration: float):
        """📊 Mise à jour performance service"""
        if service_name not in self.service_performance:
            self.service_performance[service_name] = {
                'total_calls': 0,
                'successful_calls': 0,
                'total_duration': 0.0,
                'total_attempts': 0,
                'success_rate': 1.0,
                'avg_response_time_ms': 100.0,
                'avg_attempts': 1.0,
                'last_updated': datetime.now()
            }
        
        stats = self.service_performance[service_name]
        stats['total_calls'] += 1
        stats['total_duration'] += duration
        stats['total_attempts'] += attempts
        
        if success:
            stats['successful_calls'] += 1
        
        # Recalcul moyennes
        stats['success_rate'] = stats['successful_calls'] / stats['total_calls']
        stats['avg_response_time_ms'] = (stats['total_duration'] / stats['total_calls']) * 1000
        stats['avg_attempts'] = stats['total_attempts'] / stats['total_calls']
        stats['last_updated'] = datetime.now()
    
    # ===============================================
    # 🔌 CIRCUIT BREAKER INTEGRATION
    # ===============================================
    
    def _is_circuit_open(self, service_name: str) -> bool:
        """🔌 Vérification circuit breaker"""
        if not self.config.enable_circuit_breaker:
            return False
        
        circuit = self.circuit_breakers.get(service_name)
        if not circuit:
            return False
        
        # Vérifier si on peut réessayer
        if circuit.get('open_until') and datetime.now() < circuit['open_until']:
            return True
        
        # Reset si timeout écoulé
        if circuit.get('open_until') and datetime.now() >= circuit['open_until']:
            circuit['failures'] = 0
            circuit['open_until'] = None
            logger.info(f"🔄 Circuit breaker reset for {service_name}")
        
        return False
    
    def _record_circuit_breaker_failure(self, service_name: str):
        """📊 Enregistrement échec circuit breaker"""
        if not self.config.enable_circuit_breaker:
            return
        
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = {'failures': 0, 'open_until': None}
        
        circuit = self.circuit_breakers[service_name]
        circuit['failures'] += 1
        
        if circuit['failures'] >= self.config.circuit_failure_threshold:
            circuit['open_until'] = datetime.now() + timedelta(seconds=self.config.circuit_timeout_seconds)
            
            logger.warning(f"🚨 Circuit breaker OPEN for {service_name}", extra={
                "service": service_name,
                "failures": circuit['failures'],
                "open_until": circuit['open_until'].isoformat()
            })
            
            health_metrics.record_error(service_name, "circuit_breaker_open")
    
    def _reset_circuit_breaker(self, service_name: str):
        """✅ Reset circuit breaker après succès"""
        if service_name in self.circuit_breakers:
            self.circuit_breakers[service_name] = {'failures': 0, 'open_until': None}
    
    # ===============================================
    # 📊 MONITORING & STATS
    # ===============================================
    
    def get_performance_stats(self) -> Dict:
        """📊 Statistiques performance retry"""
        total_services = len(self.service_performance)
        healthy_services = sum(1 for stats in self.service_performance.values() 
                             if stats['success_rate'] > 0.9)
        
        circuit_breaker_stats = {}
        for service, circuit in self.circuit_breakers.items():
            circuit_breaker_stats[service] = {
                'failures': circuit.get('failures', 0),
                'is_open': circuit.get('open_until') is not None and datetime.now() < circuit.get('open_until', datetime.now()),
                'open_until': circuit.get('open_until').isoformat() if circuit.get('open_until') else None
            }
        
        return {
            "retry_configuration": {
                "strategy": self.config.strategy.value,
                "max_attempts": self.config.max_attempts,
                "adaptive_enabled": self.config.enable_adaptive_timing,
                "circuit_breaker_enabled": self.config.enable_circuit_breaker
            },
            "service_health": {
                "total_services": total_services,
                "healthy_services": healthy_services,
                "health_rate_percent": round((healthy_services / total_services * 100) if total_services > 0 else 100, 1)
            },
            "service_performance": self.service_performance,
            "circuit_breakers": circuit_breaker_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    def reset_service_stats(self, service_name: Optional[str] = None):
        """🔄 Reset statistiques service"""
        if service_name:
            if service_name in self.service_performance:
                del self.service_performance[service_name]
            if service_name in self.circuit_breakers:
                del self.circuit_breakers[service_name]
            logger.info(f"🔄 Reset stats for {service_name}")
        else:
            self.service_performance.clear()
            self.circuit_breakers.clear()
            logger.info("🔄 Reset all service stats")

# ===============================================
# 🚀 GLOBAL INSTANCE & UTILITIES
# ===============================================

_retry_manager: Optional[RetryManager] = None

def get_retry_manager(config: Optional[RetryConfig] = None) -> RetryManager:
    """🔄 Récupère l'instance globale du retry manager"""
    global _retry_manager
    
    if _retry_manager is None:
        if config is None:
            config = RetryConfig()  # Configuration par défaut
        
        _retry_manager = RetryManager(config)
        logger.info("🚀 Global retry manager initialized")
    
    return _retry_manager

# Fonction utilitaire pour retry simple
async def retry_async(func: Callable, 
                     service_name: str = "default",
                     max_attempts: int = 3,
                     strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
                     *args, **kwargs) -> Any:
    """🔄 Retry simple pour fonctions async"""
    config = RetryConfig(
        strategy=strategy,
        max_attempts=max_attempts
    )
    
    manager = get_retry_manager(config)
    result = await manager.execute_with_retry(func, service_name, "async_call", None, *args, **kwargs)
    
    if result.success:
        return result.result
    else:
        raise result.final_error

# Décorateur pour retry automatique
def with_retry(service_name: str = "default",
              max_attempts: int = 3,
              strategy: RetryStrategy = RetryStrategy.JITTERED_EXPONENTIAL,
              base_delay: float = 1.0):
    """🔄 Décorateur pour retry automatique"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            config = RetryConfig(
                strategy=strategy,
                max_attempts=max_attempts,
                base_delay_seconds=base_delay
            )
            
            manager = get_retry_manager(config)
            result = await manager.execute_with_retry(
                func, service_name, func.__name__, config, *args, **kwargs
            )
            
            if result.success:
                return result.result
            else:
                raise result.final_error
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Version synchrone
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Configurations prédéfinies
class RetryConfigs:
    """🎯 Configurations prédéfinies pour différents services"""
    
    GOOGLE_MAPS = RetryConfig(
        strategy=RetryStrategy.JITTERED_EXPONENTIAL,
        max_attempts=4,
        base_delay_seconds=0.5,
        max_delay_seconds=15.0,
        retry_condition=RetryCondition.NETWORK_ERRORS,
        retryable_status_codes=(429, 502, 503, 504),
        enable_adaptive_timing=True,
        circuit_failure_threshold=3,
        circuit_timeout_seconds=60
    )
    
    DATABASE = RetryConfig(
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        max_attempts=5,
        base_delay_seconds=0.1,
        max_delay_seconds=5.0,
        retry_condition=RetryCondition.SPECIFIC_EXCEPTIONS,
        retryable_exceptions=(ConnectionError, TimeoutError),
        enable_adaptive_timing=True,
        circuit_failure_threshold=5,
        circuit_timeout_seconds=30
    )
    
    COMMITMENT_SERVICE = RetryConfig(
        strategy=RetryStrategy.FIBONACCI_BACKOFF,
        max_attempts=3,
        base_delay_seconds=1.0,
        max_delay_seconds=30.0,
        retry_condition=RetryCondition.SERVER_ERRORS,
        retryable_status_codes=(502, 503, 504),
        enable_adaptive_timing=True,
        circuit_failure_threshold=2,
        circuit_timeout_seconds=120
    )
    
    FAST_API = RetryConfig(
        strategy=RetryStrategy.LINEAR_BACKOFF,
        max_attempts=2,
        base_delay_seconds=0.1,
        max_delay_seconds=1.0,
        retry_condition=RetryCondition.TIMEOUT_ERRORS,
        enable_adaptive_timing=False,  # Réponses rapides attendues
        circuit_failure_threshold=10,
        circuit_timeout_seconds=15
    )

# Exemples d'utilisation avec les services Nextvision
@with_retry(service_name="google_maps", max_attempts=4, strategy=RetryStrategy.JITTERED_EXPONENTIAL)
async def geocode_with_retry(address: str):
    """📍 Géocodage avec retry intelligent"""
    # Votre logique de géocodage ici
    pass

@with_retry(service_name="commitment_service", max_attempts=3, strategy=RetryStrategy.FIBONACCI_BACKOFF)
async def fetch_commitment_data_with_retry(endpoint: str):
    """🌉 Récupération données Commitment- avec retry"""
    # Votre logique d'appel Commitment- ici
    pass
