"""
🔧 Alias pour compatibilité structured_logging
Redirige vers nextvision.logging.structured_logging
"""

# Import et re-export de tous les éléments
from nextvision.logging.structured_logging import *

# Rééxport explicite des éléments principaux
from nextvision.logging.structured_logging import (
    LogLevel, LogComponent, LogContext, StructuredFormatter,
    get_structured_logger, setup_production_logging,
    log_context, log_operation, get_request_tracker,
    LogAnalytics, get_log_analytics
)
