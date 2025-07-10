"""
🛡️ Nextvision - Error Handling & Graceful Degradation
Enterprise-grade error management with intelligent fallbacks
"""

from .graceful_degradation import (
    ErrorHandler,
    GracefulDegradationManager,
    ServiceFallback,
    FallbackStrategy,
    ServiceStatus,
    ErrorSeverity
)

__all__ = [
    "ErrorHandler",
    "GracefulDegradationManager", 
    "ServiceFallback",
    "FallbackStrategy",
    "ServiceStatus",
    "ErrorSeverity"
]