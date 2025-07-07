"""
🛡️ Error Handling Package - Nextvision Production Robustness

Gestion d'erreurs intelligente et fallbacks gracieux pour production enterprise-grade.
"""

from .graceful_degradation import (
    ErrorHandler,
    GracefulDegradationManager,
    FallbackStrategy,
    ServiceHealthStatus,
    CircuitBreaker,
    ErrorCategory
)

__all__ = [
    "ErrorHandler",
    "GracefulDegradationManager", 
    "FallbackStrategy",
    "ServiceHealthStatus",
    "CircuitBreaker",
    "ErrorCategory"
]
