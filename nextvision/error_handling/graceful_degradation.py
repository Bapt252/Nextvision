"""
🛡️ Nextvision - Graceful Degradation & Error Handling
Enterprise-grade error management with intelligent fallbacks for production

Features:
- Multi-level fallback strategies
- Service health monitoring
- Circuit breaker pattern
- Intelligent error classification
- Graceful service degradation
"""

import asyncio
import time
import nextvision_logging as logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
import json
from functools import wraps

from ..logging.structured_logging import get_structured_logger
from ..monitoring.health_metrics import MetricsCollector

logger = get_structured_logger(__name__)


class ErrorSeverity(Enum):
    """🚨 Classification de la sévérité des erreurs"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ServiceStatus(Enum):
    """⚡ État des services"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    DOWN = "down"
    CIRCUIT_OPEN = "circuit_open"


class FallbackStrategy(Enum):
    """🔄 Stratégies de fallback"""
    CACHE_ONLY = "cache_only"
    APPROXIMATE = "approximate"
    DISABLE_FEATURE = "disable_feature"
    SIMPLIFIED_RESPONSE = "simplified_response"
    REDIRECT_SERVICE = "redirect_service"
    MANUAL_INTERVENTION = "manual_intervention"


@dataclass
class ErrorInfo:
    """📊 Informations détaillées d'erreur"""
    error_type: str
    message: str
    severity: ErrorSeverity
    timestamp: datetime
    service: str
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    fallback_applied: Optional[str] = None
    user_impact: str = "none"


@dataclass
class ServiceHealth:
    """❤️ Santé d'un service"""
    service_name: str
    status: ServiceStatus
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    failure_count: int = 0
    success_count: int = 0
    average_response_time: float = 0.0
    circuit_breaker_open_until: Optional[datetime] = None
    fallback_strategy: Optional[FallbackStrategy] = None


class CircuitBreaker:
    """⚡ Circuit Breaker Pattern pour protection des services"""
    
    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 3
    ):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = ServiceStatus.HEALTHY
        
    def record_success(self):
        """✅ Enregistre un succès"""
        self.success_count += 1
        self.failure_count = 0
        
        # Si circuit ouvert et assez de succès, fermer
        if self.state == ServiceStatus.CIRCUIT_OPEN and self.success_count >= self.success_threshold:
            self.state = ServiceStatus.HEALTHY
            logger.info(f"🔄 Circuit breaker fermé pour {self.service_name}",
                       extra={"service": self.service_name, "success_count": self.success_count})
    
    def record_failure(self):
        """❌ Enregistre un échec"""
        self.failure_count += 1
        self.success_count = 0
        self.last_failure_time = datetime.now()
        
        # Ouvrir circuit si trop d'échecs
        if self.failure_count >= self.failure_threshold:
            self.state = ServiceStatus.CIRCUIT_OPEN
            logger.warning(f"⚡ Circuit breaker ouvert pour {self.service_name}",
                          extra={"service": self.service_name, "failure_count": self.failure_count})
    
    def can_execute(self) -> bool:
        """🔍 Vérifie si le service peut être appelé"""
        if self.state != ServiceStatus.CIRCUIT_OPEN:
            return True
            
        # Vérifier si timeout de récupération écoulé
        if self.last_failure_time:
            recovery_time = self.last_failure_time + timedelta(seconds=self.recovery_timeout)
            if datetime.now() > recovery_time:
                self.state = ServiceStatus.DEGRADED
                logger.info(f"🔄 Tentative de récupération pour {self.service_name}")
                return True
                
        return False


class ServiceFallback:
    """🔄 Gestion des fallbacks pour un service"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.fallback_strategies = {}
        self.default_strategy = FallbackStrategy.SIMPLIFIED_RESPONSE
        
    def register_fallback(self, error_type: str, strategy: FallbackStrategy, handler: Callable):
        """📝 Enregistre une stratégie de fallback"""
        self.fallback_strategies[error_type] = {
            "strategy": strategy,
            "handler": handler
        }
        
    async def execute_fallback(
        self, 
        error_type: str, 
        original_error: Exception, 
        context: Dict[str, Any]
    ) -> Any:
        """🔄 Exécute la stratégie de fallback appropriée"""
        
        # Recherche stratégie spécifique
        if error_type in self.fallback_strategies:
            fallback = self.fallback_strategies[error_type]
            logger.info(f"🔄 Fallback {fallback['strategy'].value} pour {self.service_name}",
                       extra={"service": self.service_name, "error_type": error_type})
            
            try:
                return await fallback["handler"](original_error, context)
            except Exception as fallback_error:
                logger.error(f"❌ Erreur fallback pour {self.service_name}: {fallback_error}")
                
        # Fallback par défaut
        return await self._default_fallback(original_error, context)
    
    async def _default_fallback(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """🔧 Fallback par défaut"""
        return {
            "status": "fallback",
            "service": self.service_name,
            "message": "Service temporairement indisponible",
            "fallback_strategy": self.default_strategy.value,
            "error_type": type(error).__name__,
            "timestamp": datetime.now().isoformat()
        }


class GracefulDegradationManager:
    """🛡️ Gestionnaire principal de dégradation gracieuse"""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.service_fallbacks: Dict[str, ServiceFallback] = {}
        self.service_health: Dict[str, ServiceHealth] = {}
        self.metrics = metrics_collector
        
        # Configuration par défaut des services critiques
        self._setup_default_services()
    
    def _setup_default_services(self):
        """🔧 Configuration des services par défaut"""
        critical_services = [
            "google_maps",
            "commitment_bridge", 
            "redis_cache",
            "database",
            "geocoding",
            "transport_calculator"
        ]
        
        for service_name in critical_services:
            self.register_service(service_name)
    
    def register_service(
        self, 
        service_name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60
    ):
        """📝 Enregistre un service pour monitoring"""
        self.circuit_breakers[service_name] = CircuitBreaker(
            service_name, failure_threshold, recovery_timeout
        )
        self.service_fallbacks[service_name] = ServiceFallback(service_name)
        self.service_health[service_name] = ServiceHealth(
            service_name=service_name,
            status=ServiceStatus.HEALTHY
        )
        
        logger.info(f"📝 Service {service_name} enregistré pour monitoring")
    
    def register_fallback(
        self,
        service_name: str,
        error_type: str, 
        strategy: FallbackStrategy,
        handler: Callable
    ):
        """🔄 Enregistre une stratégie de fallback"""
        if service_name not in self.service_fallbacks:
            self.register_service(service_name)
            
        self.service_fallbacks[service_name].register_fallback(
            error_type, strategy, handler
        )
    
    async def execute_with_fallback(
        self,
        service_name: str,
        operation: Callable,
        context: Dict[str, Any] = None
    ) -> Any:
        """🔄 Exécute une opération avec gestion d'erreur et fallback"""
        context = context or {}
        circuit_breaker = self.circuit_breakers.get(service_name)
        
        # Vérifier circuit breaker
        if circuit_breaker and not circuit_breaker.can_execute():
            logger.warning(f"⚡ Service {service_name} circuit ouvert, fallback direct")
            
            if self.metrics:
                self.metrics.increment_counter(f"circuit_breaker_blocked_{service_name}")
            
            return await self._execute_fallback(
                service_name, 
                Exception("Circuit breaker open"), 
                "circuit_breaker_open",
                context
            )
        
        # Tenter l'opération
        start_time = time.time()
        try:
            result = await operation()
            
            # Enregistrer succès
            execution_time = time.time() - start_time
            self._record_success(service_name, execution_time)
            
            if self.metrics:
                self.metrics.record_timer(f"service_response_time_{service_name}", execution_time)
                self.metrics.increment_counter(f"service_success_{service_name}")
            
            return result
            
        except Exception as error:
            execution_time = time.time() - start_time
            error_type = type(error).__name__
            
            # Enregistrer échec
            self._record_failure(service_name, error, execution_time)
            
            if self.metrics:
                self.metrics.increment_counter(f"service_error_{service_name}_{error_type}")
                self.metrics.record_timer(f"service_error_time_{service_name}", execution_time)
            
            # Exécuter fallback
            return await self._execute_fallback(service_name, error, error_type, context)
    
    async def _execute_fallback(
        self,
        service_name: str,
        error: Exception,
        error_type: str,
        context: Dict[str, Any]
    ) -> Any:
        """🔄 Exécute le fallback approprié"""
        if service_name in self.service_fallbacks:
            return await self.service_fallbacks[service_name].execute_fallback(
                error_type, error, context
            )
        
        # Fallback générique
        logger.error(f"❌ Aucun fallback configuré pour {service_name}")
        return {
            "status": "error",
            "service": service_name,
            "message": "Service indisponible",
            "error_type": error_type
        }
    
    def _record_success(self, service_name: str, response_time: float):
        """✅ Enregistre un succès"""
        if service_name in self.circuit_breakers:
            self.circuit_breakers[service_name].record_success()
            
        if service_name in self.service_health:
            health = self.service_health[service_name]
            health.last_success = datetime.now()
            health.success_count += 1
            health.status = ServiceStatus.HEALTHY
            
            # Mise à jour temps de réponse moyen
            if health.average_response_time == 0:
                health.average_response_time = response_time
            else:
                health.average_response_time = (
                    health.average_response_time * 0.8 + response_time * 0.2
                )
    
    def _record_failure(self, service_name: str, error: Exception, response_time: float):
        """❌ Enregistre un échec"""
        if service_name in self.circuit_breakers:
            self.circuit_breakers[service_name].record_failure()
            
        if service_name in self.service_health:
            health = self.service_health[service_name]
            health.last_failure = datetime.now()
            health.failure_count += 1
            
            # Déterminer statut selon les échecs
            if health.failure_count >= 10:
                health.status = ServiceStatus.DOWN
            elif health.failure_count >= 5:
                health.status = ServiceStatus.FAILING
            elif health.failure_count >= 2:
                health.status = ServiceStatus.DEGRADED
                
        # Log structuré de l'erreur
        logger.error(
            f"❌ Échec service {service_name}",
            extra={
                "service": service_name,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "response_time": response_time
            }
        )
    
    def get_service_health(self, service_name: str) -> Optional[ServiceHealth]:
        """❤️ Obtient la santé d'un service"""
        return self.service_health.get(service_name)
    
    def get_all_services_health(self) -> Dict[str, ServiceHealth]:
        """❤️ Obtient la santé de tous les services"""
        return self.service_health.copy()
    
    def get_degraded_services(self) -> List[str]:
        """⚠️ Liste des services dégradés"""
        degraded = []
        for name, health in self.service_health.items():
            if health.status in [ServiceStatus.DEGRADED, ServiceStatus.FAILING, ServiceStatus.DOWN]:
                degraded.append(name)
        return degraded


class ErrorHandler:
    """🛡️ Gestionnaire principal d'erreurs avec classification intelligente"""
    
    def __init__(self, degradation_manager: GracefulDegradationManager):
        self.degradation_manager = degradation_manager
        self.error_patterns = self._setup_error_patterns()
    
    def _setup_error_patterns(self) -> Dict[str, Dict]:
        """🔍 Configuration des patterns d'erreurs"""
        return {
            "google_maps_quota_exceeded": {
                "patterns": ["OVER_QUERY_LIMIT", "quota", "rate limit"],
                "severity": ErrorSeverity.HIGH,
                "service": "google_maps",
                "fallback_strategy": FallbackStrategy.CACHE_ONLY
            },
            "google_maps_invalid_request": {
                "patterns": ["INVALID_REQUEST", "geocoding", "invalid address"],
                "severity": ErrorSeverity.MEDIUM,
                "service": "google_maps",
                "fallback_strategy": FallbackStrategy.APPROXIMATE
            },
            "network_timeout": {
                "patterns": ["timeout", "connection", "network"],
                "severity": ErrorSeverity.MEDIUM,
                "service": "network",
                "fallback_strategy": FallbackStrategy.CACHE_ONLY
            },
            "database_connection_lost": {
                "patterns": ["database", "connection lost", "postgresql"],
                "severity": ErrorSeverity.CRITICAL,
                "service": "database",
                "fallback_strategy": FallbackStrategy.MANUAL_INTERVENTION
            },
            "redis_unavailable": {
                "patterns": ["redis", "cache", "connection refused"],
                "severity": ErrorSeverity.HIGH,
                "service": "redis_cache",
                "fallback_strategy": FallbackStrategy.DISABLE_FEATURE
            }
        }
    
    def classify_error(self, error: Exception, context: Dict[str, Any] = None) -> ErrorInfo:
        """🔍 Classifie intelligemment une erreur"""
        error_message = str(error).lower()
        error_type = type(error).__name__
        context = context or {}
        
        # Recherche de patterns
        for pattern_name, pattern_config in self.error_patterns.items():
            for pattern in pattern_config["patterns"]:
                if pattern in error_message:
                    return ErrorInfo(
                        error_type=pattern_name,
                        message=str(error),
                        severity=pattern_config["severity"],
                        timestamp=datetime.now(),
                        service=pattern_config["service"],
                        context=context
                    )
        
        # Classification par défaut
        return ErrorInfo(
            error_type=error_type,
            message=str(error),
            severity=ErrorSeverity.MEDIUM,
            timestamp=datetime.now(),
            service="unknown",
            context=context
        )
    
    async def handle_error(
        self,
        error: Exception,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """🛡️ Gestion complète d'une erreur"""
        error_info = self.classify_error(error, context)
        
        # Log de l'erreur
        logger.error(
            f"🛡️ Erreur {error_info.severity.value}: {error_info.message}",
            extra={
                "error_type": error_info.error_type,
                "service": error_info.service,
                "severity": error_info.severity.value,
                "context": error_info.context
            }
        )
        
        # Exécution du fallback via le gestionnaire de dégradation
        fallback_result = await self.degradation_manager._execute_fallback(
            error_info.service,
            error,
            error_info.error_type,
            error_info.context
        )
        
        return {
            "error_info": {
                "type": error_info.error_type,
                "severity": error_info.severity.value,
                "service": error_info.service,
                "timestamp": error_info.timestamp.isoformat()
            },
            "fallback_result": fallback_result,
            "status": "handled_with_fallback"
        }


# =====================================
# 🔧 DECORATORS & UTILITIES
# =====================================

def with_graceful_degradation(service_name: str, degradation_manager: GracefulDegradationManager):
    """🎯 Décorateur pour ajouter la dégradation gracieuse à une fonction"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await degradation_manager.execute_with_fallback(
                service_name,
                lambda: func(*args, **kwargs),
                {"function": func.__name__, "args_count": len(args)}
            )
        return wrapper
    return decorator


# =====================================
# 🔧 FALLBACK HANDLERS SPÉCIALISÉS
# =====================================

class GoogleMapsFallbacks:
    """🗺️ Fallbacks spécialisés pour Google Maps"""
    
    @staticmethod
    async def quota_exceeded_fallback(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """🚫 Fallback quota Google Maps dépassé"""
        logger.warning("🗺️ Quota Google Maps dépassé, utilisation cache uniquement")
        
        return {
            "status": "fallback",
            "source": "cache_only",
            "message": "Service de géocodage temporairement limité",
            "accuracy": "cache",
            "fallback_reason": "google_maps_quota_exceeded"
        }
    
    @staticmethod
    async def invalid_address_fallback(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """📍 Fallback adresse invalide"""
        address = context.get("address", "")
        
        # Géocodage approximatif basique
        if "paris" in address.lower():
            return {
                "status": "fallback",
                "source": "approximate",
                "coordinates": {"latitude": 48.8566, "longitude": 2.3522},
                "formatted_address": "Paris, France (approximatif)",
                "accuracy": "city_level",
                "fallback_reason": "invalid_address_approximation"
            }
        
        return {
            "status": "fallback",
            "source": "failed",
            "message": "Adresse non géocodable",
            "fallback_reason": "geocoding_impossible"
        }


class CacheFallbacks:
    """🗄️ Fallbacks pour les problèmes de cache"""
    
    @staticmethod
    async def redis_unavailable_fallback(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """🗄️ Fallback Redis indisponible"""
        logger.warning("🗄️ Redis indisponible, mode sans cache")
        
        return {
            "status": "fallback",
            "cache_mode": "disabled",
            "message": "Cache temporairement indisponible",
            "performance_impact": "high",
            "fallback_reason": "redis_unavailable"
        }


class DatabaseFallbacks:
    """🗃️ Fallbacks pour les problèmes de base de données"""
    
    @staticmethod
    async def connection_lost_fallback(error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """🗃️ Fallback connexion DB perdue"""
        logger.critical("🗃️ Connexion base de données perdue")
        
        return {
            "status": "critical_fallback",
            "message": "Service temporairement indisponible",
            "requires_manual_intervention": True,
            "fallback_reason": "database_connection_lost"
        }
