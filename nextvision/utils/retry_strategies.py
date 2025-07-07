"""
🔄 Nextvision - Adaptive Retry Strategies
Enterprise-grade retry logic for APIs, databases, and external services

Features:
- Exponential backoff with jitter
- Circuit breaker integration
- Service-specific retry policies
- Intelligent failure analysis
- Cost optimization for API calls
"""

import asyncio
import random
import time
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Type
import logging

from ..logging.structured_logging import get_structured_logger
from ..monitoring.health_metrics import MetricsCollector

logger = get_structured_logger(__name__)


class RetryStrategy(Enum):
    """🎯 Stratégies de retry"""
    FIXED_DELAY = "fixed_delay"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIBONACCI_BACKOFF = "fibonacci_backoff"
    ADAPTIVE = "adaptive"
    SMART_BACKOFF = "smart_backoff"


class FailureCategory(Enum):
    """📊 Catégories d'échecs"""
    NETWORK_TIMEOUT = "network_timeout"
    RATE_LIMIT = "rate_limit"
    SERVER_ERROR = "server_error"
    CLIENT_ERROR = "client_error"
    AUTHENTICATION = "authentication"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    TEMPORARY_UNAVAILABLE = "temporary_unavailable"
    UNKNOWN = "unknown"


@dataclass
class RetryConfig:
    """⚙️ Configuration de retry"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter_range: float = 0.1
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    retryable_exceptions: List[Type[Exception]] = field(default_factory=list)
    non_retryable_exceptions: List[Type[Exception]] = field(default_factory=list)
    

@dataclass
class RetryAttempt:
    """🔄 Tentative de retry"""
    attempt_number: int
    timestamp: datetime
    delay_used: float
    error: Optional[Exception] = None
    success: bool = False
    response_time: float = 0.0
    failure_category: FailureCategory = FailureCategory.UNKNOWN


@dataclass
class RetryResult:
    """📊 Résultat de retry"""
    success: bool
    attempts_made: int
    total_time: float
    final_result: Any = None
    final_error: Optional[Exception] = None
    attempts_history: List[RetryAttempt] = field(default_factory=list)
    fallback_used: bool = False
    cost_estimate: float = 0.0


class FailureAnalyzer:
    """🔍 Analyseur d'échecs intelligent"""
    
    def __init__(self):
        self.failure_patterns = self._setup_failure_patterns()
        self.failure_history: Dict[str, List[FailureCategory]] = {}
    
    def _setup_failure_patterns(self) -> Dict[str, Dict]:
        """🔧 Configuration des patterns d'échecs"""
        return {
            "google_maps": {
                "rate_limit_indicators": ["OVER_QUERY_LIMIT", "quota", "rate limit"],
                "timeout_indicators": ["timeout", "timed out", "connection timeout"],
                "server_error_indicators": ["UNKNOWN_ERROR", "internal error", "500"],
                "auth_indicators": ["REQUEST_DENIED", "API key", "unauthorized"]
            },
            "database": {
                "connection_indicators": ["connection", "pool", "database"],
                "timeout_indicators": ["timeout", "deadlock", "lock"],
                "resource_indicators": ["too many", "limit", "quota"]
            },
            "redis": {
                "connection_indicators": ["connection refused", "no route", "unreachable"],
                "memory_indicators": ["out of memory", "oom", "memory"]
            },
            "commitment_bridge": {
                "api_indicators": ["500", "502", "503", "504"],
                "timeout_indicators": ["timeout", "slow"],
                "auth_indicators": ["401", "403", "unauthorized"]
            }
        }
    
    def analyze_failure(
        self, 
        service: str, 
        error: Exception, 
        context: Dict[str, Any] = None
    ) -> FailureCategory:
        """🔍 Analyse intelligente d'un échec"""
        error_message = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Patterns spécifiques au service
        service_patterns = self.failure_patterns.get(service, {})
        
        # Vérification des patterns
        for pattern_type, indicators in service_patterns.items():
            for indicator in indicators:
                if indicator in error_message or indicator in error_type:
                    category = self._map_pattern_to_category(pattern_type)
                    self._record_failure(service, category)
                    return category
        
        # Classification générique
        if "timeout" in error_message or "timeout" in error_type:
            category = FailureCategory.NETWORK_TIMEOUT
        elif "rate" in error_message or "limit" in error_message:
            category = FailureCategory.RATE_LIMIT
        elif "500" in error_message or "internal" in error_message:
            category = FailureCategory.SERVER_ERROR
        elif "400" in error_message or "client" in error_message:
            category = FailureCategory.CLIENT_ERROR
        elif "auth" in error_message or "unauthorized" in error_message:
            category = FailureCategory.AUTHENTICATION
        elif "unavailable" in error_message or "down" in error_message:
            category = FailureCategory.TEMPORARY_UNAVAILABLE
        else:
            category = FailureCategory.UNKNOWN
        
        self._record_failure(service, category)
        return category
    
    def _map_pattern_to_category(self, pattern_type: str) -> FailureCategory:
        """🗺️ Mapping pattern vers catégorie"""
        mapping = {
            "rate_limit_indicators": FailureCategory.RATE_LIMIT,
            "timeout_indicators": FailureCategory.NETWORK_TIMEOUT,
            "server_error_indicators": FailureCategory.SERVER_ERROR,
            "auth_indicators": FailureCategory.AUTHENTICATION,
            "connection_indicators": FailureCategory.TEMPORARY_UNAVAILABLE,
            "resource_indicators": FailureCategory.RESOURCE_EXHAUSTED,
            "memory_indicators": FailureCategory.RESOURCE_EXHAUSTED,
            "api_indicators": FailureCategory.SERVER_ERROR
        }
        return mapping.get(pattern_type, FailureCategory.UNKNOWN)
    
    def _record_failure(self, service: str, category: FailureCategory):
        """📝 Enregistrement historique des échecs"""
        if service not in self.failure_history:
            self.failure_history[service] = []
        
        self.failure_history[service].append(category)
        
        # Garder seulement les 50 dernières
        if len(self.failure_history[service]) > 50:
            self.failure_history[service] = self.failure_history[service][-50:]
    
    def get_failure_trends(self, service: str) -> Dict[str, Any]:
        """📊 Tendances d'échecs pour un service"""
        if service not in self.failure_history:
            return {"status": "no_data"}
        
        history = self.failure_history[service]
        recent_failures = history[-10:]  # 10 dernières
        
        # Comptage par catégorie
        category_counts = {}
        for category in recent_failures:
            category_counts[category.value] = category_counts.get(category.value, 0) + 1
        
        # Catégorie dominante
        dominant_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None
        
        return {
            "total_failures": len(history),
            "recent_failures": len(recent_failures),
            "category_distribution": category_counts,
            "dominant_failure_type": dominant_category,
            "failure_rate_trend": "increasing" if len(recent_failures) > 5 else "stable"
        }


class AdaptiveDelayCalculator:
    """🧠 Calculateur de délai adaptatif"""
    
    def __init__(self):
        self.service_performance: Dict[str, List[float]] = {}
        self.fibonacci_cache = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
    
    def calculate_delay(
        self,
        attempt: int,
        config: RetryConfig,
        failure_category: FailureCategory,
        service: str = "default"
    ) -> float:
        """🔢 Calcul de délai adaptatif"""
        
        base_delay = self._get_category_adjusted_delay(config.base_delay, failure_category)
        
        if config.strategy == RetryStrategy.FIXED_DELAY:
            delay = base_delay
            
        elif config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = base_delay * (config.exponential_base ** (attempt - 1))
            
        elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = base_delay * attempt
            
        elif config.strategy == RetryStrategy.FIBONACCI_BACKOFF:
            fib_multiplier = self._get_fibonacci(attempt)
            delay = base_delay * fib_multiplier
            
        elif config.strategy == RetryStrategy.ADAPTIVE:
            delay = self._calculate_adaptive_delay(attempt, base_delay, service)
            
        elif config.strategy == RetryStrategy.SMART_BACKOFF:
            delay = self._calculate_smart_backoff(attempt, config, failure_category, service)
            
        else:
            delay = base_delay * (config.exponential_base ** (attempt - 1))
        
        # Application du jitter
        if config.jitter_range > 0:
            jitter = random.uniform(-config.jitter_range, config.jitter_range)
            delay = delay * (1 + jitter)
        
        # Limitation du délai maximum
        delay = min(delay, config.max_delay)
        delay = max(delay, 0.1)  # Délai minimum
        
        return delay
    
    def _get_category_adjusted_delay(self, base_delay: float, category: FailureCategory) -> float:
        """🎯 Ajustement délai selon la catégorie d'échec"""
        adjustments = {
            FailureCategory.RATE_LIMIT: 3.0,  # Délai plus long pour rate limit
            FailureCategory.NETWORK_TIMEOUT: 1.5,
            FailureCategory.SERVER_ERROR: 2.0,
            FailureCategory.TEMPORARY_UNAVAILABLE: 2.5,
            FailureCategory.RESOURCE_EXHAUSTED: 4.0,  # Le plus long
            FailureCategory.CLIENT_ERROR: 0.5,  # Plus court (souvent inutile)
            FailureCategory.AUTHENTICATION: 0.2,  # Très court (souvent inutile)
        }
        
        multiplier = adjustments.get(category, 1.0)
        return base_delay * multiplier
    
    def _get_fibonacci(self, n: int) -> int:
        """🔢 Nombre de Fibonacci avec cache"""
        if n <= len(self.fibonacci_cache):
            return self.fibonacci_cache[n - 1]
        
        # Extension du cache si nécessaire
        while len(self.fibonacci_cache) < n:
            next_fib = self.fibonacci_cache[-1] + self.fibonacci_cache[-2]
            self.fibonacci_cache.append(next_fib)
        
        return self.fibonacci_cache[n - 1]
    
    def _calculate_adaptive_delay(
        self, 
        attempt: int, 
        base_delay: float, 
        service: str
    ) -> float:
        """🧠 Délai adaptatif basé sur l'historique du service"""
        if service not in self.service_performance:
            return base_delay * (2 ** (attempt - 1))  # Fallback exponentiel
        
        # Analyse des performances historiques
        performance_history = self.service_performance[service]
        avg_response_time = sum(performance_history) / len(performance_history)
        
        # Ajustement selon la performance moyenne
        if avg_response_time > 5.0:  # Service lent
            multiplier = 3.0
        elif avg_response_time > 2.0:  # Service moyen
            multiplier = 2.0
        else:  # Service rapide
            multiplier = 1.5
        
        return base_delay * (multiplier ** (attempt - 1))
    
    def _calculate_smart_backoff(
        self,
        attempt: int,
        config: RetryConfig,
        failure_category: FailureCategory,
        service: str
    ) -> float:
        """🧠 Smart backoff combinant plusieurs stratégies"""
        
        # Base exponentielle
        exp_delay = config.base_delay * (config.exponential_base ** (attempt - 1))
        
        # Ajustement par catégorie
        category_delay = self._get_category_adjusted_delay(config.base_delay, failure_category)
        
        # Ajustement adaptatif
        adaptive_delay = self._calculate_adaptive_delay(attempt, config.base_delay, service)
        
        # Combinaison pondérée
        smart_delay = (
            exp_delay * 0.4 +
            category_delay * 0.3 +
            adaptive_delay * 0.3
        )
        
        return smart_delay
    
    def record_service_performance(self, service: str, response_time: float):
        """📊 Enregistrement performance du service"""
        if service not in self.service_performance:
            self.service_performance[service] = []
        
        self.service_performance[service].append(response_time)
        
        # Garder seulement les 20 dernières mesures
        if len(self.service_performance[service]) > 20:
            self.service_performance[service] = self.service_performance[service][-20:]


class RetryExecutor:
    """🚀 Exécuteur de retry avec intelligence"""
    
    def __init__(
        self,
        failure_analyzer: Optional[FailureAnalyzer] = None,
        delay_calculator: Optional[AdaptiveDelayCalculator] = None,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        self.failure_analyzer = failure_analyzer or FailureAnalyzer()
        self.delay_calculator = delay_calculator or AdaptiveDelayCalculator()
        self.metrics = metrics_collector
        
        # Configurations par service
        self.service_configs = self._setup_service_configs()
    
    def _setup_service_configs(self) -> Dict[str, RetryConfig]:
        """🔧 Configurations spécifiques par service"""
        return {
            "google_maps": RetryConfig(
                max_attempts=4,
                base_delay=2.0,
                max_delay=120.0,
                strategy=RetryStrategy.SMART_BACKOFF,
                retryable_exceptions=[ConnectionError, TimeoutError]
            ),
            "database": RetryConfig(
                max_attempts=5,
                base_delay=0.5,
                max_delay=30.0,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
                retryable_exceptions=[ConnectionError]
            ),
            "redis": RetryConfig(
                max_attempts=3,
                base_delay=0.2,
                max_delay=10.0,
                strategy=RetryStrategy.LINEAR_BACKOFF,
                retryable_exceptions=[ConnectionError]
            ),
            "commitment_bridge": RetryConfig(
                max_attempts=3,
                base_delay=1.0,
                max_delay=60.0,
                strategy=RetryStrategy.ADAPTIVE,
                retryable_exceptions=[ConnectionError, TimeoutError]
            ),
            "default": RetryConfig(
                max_attempts=3,
                base_delay=1.0,
                max_delay=30.0,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF
            )
        }
    
    async def execute_with_retry(
        self,
        operation: Callable,
        service: str = "default",
        config: Optional[RetryConfig] = None,
        context: Dict[str, Any] = None,
        fallback: Optional[Callable] = None
    ) -> RetryResult:
        """🚀 Exécution avec retry intelligent"""
        
        # Configuration
        retry_config = config or self.service_configs.get(service, self.service_configs["default"])
        context = context or {}
        
        # Initialisation
        start_time = time.time()
        attempts_history = []
        final_result = None
        final_error = None
        
        logger.info(f"🚀 Démarrage retry pour {service} (max {retry_config.max_attempts} tentatives)")
        
        for attempt in range(1, retry_config.max_attempts + 1):
            attempt_start = time.time()
            
            try:
                # Exécution de l'opération
                if asyncio.iscoroutinefunction(operation):
                    result = await operation()
                else:
                    result = operation()
                
                # Succès !
                response_time = time.time() - attempt_start
                self.delay_calculator.record_service_performance(service, response_time)
                
                attempt_record = RetryAttempt(
                    attempt_number=attempt,
                    timestamp=datetime.now(),
                    delay_used=0.0,
                    success=True,
                    response_time=response_time
                )
                attempts_history.append(attempt_record)
                
                total_time = time.time() - start_time
                
                # Métriques de succès
                if self.metrics:
                    self.metrics.increment_counter(f"retry_success_{service}")
                    self.metrics.record_timer(f"retry_total_time_{service}", total_time)
                    self.metrics.record_gauge(f"retry_attempts_{service}", attempt)
                
                logger.info(f"✅ Succès {service} tentative {attempt}/{retry_config.max_attempts} ({response_time:.3f}s)")
                
                return RetryResult(
                    success=True,
                    attempts_made=attempt,
                    total_time=total_time,
                    final_result=result,
                    attempts_history=attempts_history
                )
                
            except Exception as error:
                response_time = time.time() - attempt_start
                
                # Analyse de l'échec
                failure_category = self.failure_analyzer.analyze_failure(service, error, context)
                
                # Vérifier si l'erreur est retry-able
                if not self._is_retryable_error(error, retry_config, failure_category):
                    logger.warning(f"❌ Erreur non-retry-able {service}: {error}")
                    
                    # Métriques d'échec non-retry-able
                    if self.metrics:
                        self.metrics.increment_counter(f"retry_non_retryable_{service}")
                    
                    # Tentative de fallback
                    if fallback:
                        try:
                            fallback_result = await fallback() if asyncio.iscoroutinefunction(fallback) else fallback()
                            return RetryResult(
                                success=True,
                                attempts_made=attempt,
                                total_time=time.time() - start_time,
                                final_result=fallback_result,
                                attempts_history=attempts_history,
                                fallback_used=True
                            )
                        except Exception as fallback_error:
                            logger.error(f"❌ Fallback échoué {service}: {fallback_error}")
                    
                    return RetryResult(
                        success=False,
                        attempts_made=attempt,
                        total_time=time.time() - start_time,
                        final_error=error,
                        attempts_history=attempts_history
                    )
                
                # Enregistrement de la tentative
                attempt_record = RetryAttempt(
                    attempt_number=attempt,
                    timestamp=datetime.now(),
                    delay_used=0.0,
                    error=error,
                    success=False,
                    response_time=response_time,
                    failure_category=failure_category
                )
                attempts_history.append(attempt_record)
                
                # Dernière tentative ?
                if attempt >= retry_config.max_attempts:
                    final_error = error
                    logger.error(f"❌ Échec final {service} après {attempt} tentatives: {error}")
                    
                    # Métriques d'échec final
                    if self.metrics:
                        self.metrics.increment_counter(f"retry_final_failure_{service}")
                        self.metrics.record_gauge(f"retry_max_attempts_{service}", attempt)
                    
                    # Tentative de fallback
                    if fallback:
                        try:
                            fallback_result = await fallback() if asyncio.iscoroutinefunction(fallback) else fallback()
                            return RetryResult(
                                success=True,
                                attempts_made=attempt,
                                total_time=time.time() - start_time,
                                final_result=fallback_result,
                                attempts_history=attempts_history,
                                fallback_used=True
                            )
                        except Exception as fallback_error:
                            logger.error(f"❌ Fallback échoué {service}: {fallback_error}")
                    
                    break
                
                # Calcul du délai avant prochaine tentative
                delay = self.delay_calculator.calculate_delay(
                    attempt + 1, retry_config, failure_category, service
                )
                
                attempt_record.delay_used = delay
                
                logger.warning(
                    f"⚠️ Échec {service} tentative {attempt}/{retry_config.max_attempts}: {error} "
                    f"(catégorie: {failure_category.value}, délai: {delay:.1f}s)"
                )
                
                # Métriques de retry
                if self.metrics:
                    self.metrics.increment_counter(f"retry_attempt_{service}")
                    self.metrics.record_timer(f"retry_delay_{service}", delay)
                
                # Attente avant prochaine tentative
                await asyncio.sleep(delay)
        
        # Échec après toutes les tentatives
        total_time = time.time() - start_time
        
        return RetryResult(
            success=False,
            attempts_made=retry_config.max_attempts,
            total_time=total_time,
            final_error=final_error,
            attempts_history=attempts_history
        )
    
    def _is_retryable_error(
        self,
        error: Exception,
        config: RetryConfig,
        failure_category: FailureCategory
    ) -> bool:
        """🔍 Détermine si une erreur est retry-able"""
        
        # Vérifier exceptions explicitement non-retry-ables
        for non_retryable in config.non_retryable_exceptions:
            if isinstance(error, non_retryable):
                return False
        
        # Vérifier exceptions explicitement retry-ables
        if config.retryable_exceptions:
            for retryable in config.retryable_exceptions:
                if isinstance(error, retryable):
                    return True
            return False  # Si liste définie mais erreur pas dedans
        
        # Classification par catégorie
        non_retryable_categories = {
            FailureCategory.CLIENT_ERROR,  # Erreurs 4xx
            FailureCategory.AUTHENTICATION  # Erreurs d'auth
        }
        
        return failure_category not in non_retryable_categories
    
    def get_service_stats(self, service: str) -> Dict[str, Any]:
        """📊 Statistiques pour un service"""
        failure_trends = self.failure_analyzer.get_failure_trends(service)
        
        config = self.service_configs.get(service, self.service_configs["default"])
        
        return {
            "service": service,
            "retry_config": {
                "max_attempts": config.max_attempts,
                "strategy": config.strategy.value,
                "base_delay": config.base_delay,
                "max_delay": config.max_delay
            },
            "failure_analysis": failure_trends,
            "performance_history": self.delay_calculator.service_performance.get(service, [])
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """📊 Statistiques globales"""
        return {
            "configured_services": list(self.service_configs.keys()),
            "service_stats": {
                service: self.get_service_stats(service)
                for service in self.service_configs.keys()
            },
            "global_failure_trends": {
                service: self.failure_analyzer.get_failure_trends(service)
                for service in self.failure_analyzer.failure_history.keys()
            }
        }


# =====================================
# 🎯 DECORATORS & UTILITIES
# =====================================

def with_retry(
    service: str = "default",
    config: Optional[RetryConfig] = None,
    executor: Optional[RetryExecutor] = None
):
    """🎯 Décorateur pour ajouter retry à une fonction"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            retry_executor = executor or RetryExecutor()
            
            async def operation():
                return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            result = await retry_executor.execute_with_retry(
                operation=operation,
                service=service,
                config=config
            )
            
            if result.success:
                return result.final_result
            else:
                raise result.final_error
        
        return wrapper
    return decorator


# =====================================
# 🏭 FACTORY & CONFIGURATION
# =====================================

def create_retry_executor(
    metrics_collector: Optional[MetricsCollector] = None
) -> RetryExecutor:
    """🏭 Factory pour créer un exécuteur de retry"""
    failure_analyzer = FailureAnalyzer()
    delay_calculator = AdaptiveDelayCalculator()
    
    return RetryExecutor(
        failure_analyzer=failure_analyzer,
        delay_calculator=delay_calculator,
        metrics_collector=metrics_collector
    )


def get_optimized_config(service: str, load_level: str = "medium") -> RetryConfig:
    """🎯 Configurations optimisées selon la charge"""
    
    base_configs = {
        "google_maps": {
            "low": RetryConfig(max_attempts=5, base_delay=1.0, strategy=RetryStrategy.EXPONENTIAL_BACKOFF),
            "medium": RetryConfig(max_attempts=4, base_delay=2.0, strategy=RetryStrategy.SMART_BACKOFF),
            "high": RetryConfig(max_attempts=3, base_delay=3.0, strategy=RetryStrategy.ADAPTIVE)
        },
        "database": {
            "low": RetryConfig(max_attempts=5, base_delay=0.5, strategy=RetryStrategy.EXPONENTIAL_BACKOFF),
            "medium": RetryConfig(max_attempts=4, base_delay=1.0, strategy=RetryStrategy.EXPONENTIAL_BACKOFF),
            "high": RetryConfig(max_attempts=3, base_delay=1.5, strategy=RetryStrategy.LINEAR_BACKOFF)
        }
    }
    
    service_configs = base_configs.get(service, base_configs.get("database"))
    return service_configs.get(load_level, service_configs["medium"])
