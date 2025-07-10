"""
📝 Nextvision - Structured Logging
Enterprise-grade structured logging with JSON output for production debugging

Features:
- JSON structured logs
- Request correlation IDs
- Performance tracking
- Error context preservation
- Multi-environment configuration
- Log aggregation ready
"""

import json
import logging
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Union
import traceback
import threading
from functools import wraps


class LogLevel(Enum):
    """📏 Niveaux de log"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogComponent(Enum):
    """🧩 Composants système"""
    API = "api"
    MATCHING = "matching"
    CACHE = "cache"
    DATABASE = "database"
    GOOGLE_MAPS = "google_maps"
    COMMITMENT_BRIDGE = "commitment_bridge"
    BATCH_PROCESSING = "batch_processing"
    MONITORING = "monitoring"
    ERROR_HANDLING = "error_handling"
    RETRY = "retry"
    SYSTEM = "system"


@dataclass
class LogContext:
    """📝 Contexte de log"""
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    component: Optional[LogComponent] = None
    operation: Optional[str] = None
    correlation_id: Optional[str] = None
    performance_data: Dict[str, Any] = field(default_factory=dict)
    business_context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire pour serialisation"""
        result = {}
        for key, value in asdict(self).items():
            if value is not None:
                if isinstance(value, Enum):
                    result[key] = value.value
                else:
                    result[key] = value
        return result


class ContextualFilter(logging.Filter):
    """🗺️ Filtre pour ajouter le contexte aux logs"""
    
    def filter(self, record):
        # Ajouter contexte depuis thread-local storage
        context = get_current_context()
        if context:
            for key, value in context.to_dict().items():
                setattr(record, key, value)
        
        # Ajouter timestamp ISO
        record.timestamp_iso = datetime.now().isoformat()
        
        # Ajouter info thread
        record.thread_name = threading.current_thread().name
        record.thread_id = threading.get_ident()
        
        return True


class StructuredFormatter(logging.Formatter):
    """📏 Formateur JSON pour logs structurés"""
    
    def __init__(self, include_extra_fields: bool = True):
        super().__init__()
        self.include_extra_fields = include_extra_fields
        
        # Champs système standard
        self.system_fields = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
            'filename', 'module', 'funcName', 'lineno', 'created', 
            'msecs', 'relativeCreated', 'thread', 'threadName', 
            'processName', 'process', 'stack_info', 'exc_info', 'exc_text'
        }
    
    def format(self, record):
        # Structure de base
        log_entry = {
            "timestamp": getattr(record, 'timestamp_iso', datetime.now().isoformat()),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": {
                "name": getattr(record, 'thread_name', 'unknown'),
                "id": getattr(record, 'thread_id', 0)
            }
        }
        
        # Ajout contexte si disponible
        context_fields = [
            'request_id', 'user_id', 'session_id', 'component', 
            'operation', 'correlation_id', 'performance_data', 'business_context'
        ]
        
        context = {}
        for field in context_fields:
            value = getattr(record, field, None)
            if value is not None:
                context[field] = value
        
        if context:
            log_entry["context"] = context
        
        # Exception si présente
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        # Champs extra personnalisés
        if self.include_extra_fields:
            extra = {}
            for key, value in record.__dict__.items():
                if key not in self.system_fields and key not in context_fields:
                    if not key.startswith('_'):
                        try:
                            # Vérifier que la valeur est JSON serializable
                            json.dumps(value)
                            extra[key] = value
                        except (TypeError, ValueError):
                            extra[key] = str(value)
            
            if extra:
                log_entry["extra"] = extra
        
        # Sérialisation JSON
        try:
            return json.dumps(log_entry, ensure_ascii=False, default=str)
        except Exception as e:
            # Fallback si problème serialisation
            fallback = {
                "timestamp": datetime.now().isoformat(),
                "level": "ERROR",
                "logger": "structured_logging",
                "message": f"Failed to serialize log entry: {e}",
                "original_message": record.getMessage()
            }
            return json.dumps(fallback, ensure_ascii=False)


class LogFormatter:
    """🎯 Factory pour différents formats de log"""
    
    @staticmethod
    def get_production_formatter() -> StructuredFormatter:
        """Formateur pour production (JSON complet)"""
        return StructuredFormatter(include_extra_fields=True)
    
    @staticmethod
    def get_development_formatter() -> logging.Formatter:
        """Formateur pour développement (lisible)"""
        return logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s:%(lineno)-3d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    @staticmethod
    def get_debug_formatter() -> logging.Formatter:
        """Formateur pour debug (très détaillé)"""
        return logging.Formatter(
            fmt='%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-25s | %(pathname)s:%(lineno)-4d | %(funcName)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


# =====================================
# 💾 CONTEXT MANAGEMENT
# =====================================

# Thread-local storage pour le contexte
_context_storage = threading.local()


def set_log_context(context: LogContext):
    """📝 Définit le contexte de log pour le thread actuel"""
    _context_storage.context = context


def get_current_context() -> Optional[LogContext]:
    """🔍 Récupère le contexte actuel"""
    return getattr(_context_storage, 'context', None)


def clear_log_context():
    """🧹 Efface le contexte actuel"""
    if hasattr(_context_storage, 'context'):
        delattr(_context_storage, 'context')


@contextmanager
def log_context(context: LogContext):
    """📝 Context manager pour logs"""
    old_context = get_current_context()
    set_log_context(context)
    try:
        yield
    finally:
        if old_context:
            set_log_context(old_context)
        else:
            clear_log_context()


@contextmanager
def log_operation(
    operation: str, 
    component: LogComponent, 
    extra_context: Dict[str, Any] = None
):
    """🎯 Context manager pour tracer une opération"""
    extra_context = extra_context or {}
    
    # Créer contexte d'opération
    operation_id = str(uuid.uuid4())[:8]
    current_context = get_current_context() or LogContext()
    
    operation_context = LogContext(
        request_id=current_context.request_id,
        user_id=current_context.user_id,
        session_id=current_context.session_id,
        component=component,
        operation=operation,
        correlation_id=operation_id,
        business_context={**current_context.business_context, **extra_context}
    )
    
    logger = get_structured_logger(f"nextvision.{component.value}")
    start_time = time.time()
    
    with log_context(operation_context):
        logger.info(f"Starting operation: {operation}", extra={
            "operation_id": operation_id,
            "operation_start": True
        })
        
        try:
            yield operation_id
            
            # Succès
            duration = time.time() - start_time
            logger.info(f"Operation completed: {operation}", extra={
                "operation_id": operation_id,
                "operation_success": True,
                "duration_seconds": duration,
                "performance": {"duration_ms": duration * 1000}
            })
            
        except Exception as e:
            # Échec
            duration = time.time() - start_time
            logger.error(f"Operation failed: {operation}", extra={
                "operation_id": operation_id,
                "operation_failure": True,
                "duration_seconds": duration,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }, exc_info=True)
            raise


class RequestTracker:
    """🔍 Tracking des requêtes avec correlation"""
    
    def __init__(self):
        self.active_requests: Dict[str, Dict[str, Any]] = {}
    
    def start_request(self, request_id: str, endpoint: str, method: str, user_id: str = None) -> LogContext:
        """🚀 Démarre le tracking d'une requête"""
        context = LogContext(
            request_id=request_id,
            user_id=user_id,
            component=LogComponent.API,
            operation=f"{method} {endpoint}",
            business_context={
                "endpoint": endpoint,
                "http_method": method
            }
        )
        
        self.active_requests[request_id] = {
            "start_time": time.time(),
            "endpoint": endpoint,
            "method": method,
            "user_id": user_id,
            "context": context
        }
        
        return context
    
    def end_request(self, request_id: str, status_code: int, response_size: int = None):
        """🏁 Termine le tracking d'une requête"""
        if request_id not in self.active_requests:
            return
        
        request_data = self.active_requests.pop(request_id)
        duration = time.time() - request_data["start_time"]
        
        logger = get_structured_logger("nextvision.api")
        
        log_data = {
            "request_completed": True,
            "duration_seconds": duration,
            "status_code": status_code,
            "performance": {
                "duration_ms": duration * 1000,
                "status_code": status_code
            }
        }
        
        if response_size:
            log_data["response_size_bytes"] = response_size
            log_data["performance"]["response_size_bytes"] = response_size
        
        with log_context(request_data["context"]):
            if status_code < 400:
                logger.info(f"Request completed: {request_data['method']} {request_data['endpoint']}", extra=log_data)
            elif status_code < 500:
                logger.warning(f"Request completed with client error: {request_data['method']} {request_data['endpoint']}", extra=log_data)
            else:
                logger.error(f"Request completed with server error: {request_data['method']} {request_data['endpoint']}", extra=log_data)
    
    def get_active_requests_count(self) -> int:
        """📊 Nombre de requêtes actives"""
        return len(self.active_requests)
    
    def get_active_requests(self) -> List[Dict[str, Any]]:
        """📊 Détails des requêtes actives"""
        current_time = time.time()
        
        return [
            {
                "request_id": req_id,
                "endpoint": data["endpoint"],
                "method": data["method"],
                "user_id": data["user_id"],
                "duration_seconds": current_time - data["start_time"]
            }
            for req_id, data in self.active_requests.items()
        ]


# =====================================
# 🏭 LOGGER FACTORY
# =====================================

# Cache des loggers configurés
_configured_loggers: Dict[str, logging.Logger] = {}
_request_tracker = RequestTracker()


def get_structured_logger(name: str) -> logging.Logger:
    """🏭 Obtient un logger structuré configuré"""
    if name in _configured_loggers:
        return _configured_loggers[name]
    
    logger = logging.getLogger(name)
    
    # Éviter la duplication si déjà configuré
    if not logger.handlers:
        # Handler pour stdout
        handler = logging.StreamHandler()
        handler.addFilter(ContextualFilter())
        
        # Format selon l'environnement
        import os
        env = os.getenv('NEXTVISION_ENV', 'development')
        
        if env == 'production':
            handler.setFormatter(LogFormatter.get_production_formatter())
        elif env == 'debug':
            handler.setFormatter(LogFormatter.get_debug_formatter())
        else:
            handler.setFormatter(LogFormatter.get_development_formatter())
        
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Empêcher propagation vers root logger
        logger.propagate = False
    
    _configured_loggers[name] = logger
    return logger


def setup_production_logging(
    log_level: str = "INFO",
    enable_file_logging: bool = True,
    log_file_path: str = "/var/log/nextvision/app.log",
    max_file_size_mb: int = 100,
    backup_count: int = 5
) -> Dict[str, Any]:
    """🔧 Configuration complète pour production"""
    import os
    from logging.handlers import RotatingFileHandler
    
    # Configuration niveau global
    log_level_obj = getattr(logging, log_level.upper(), logging.INFO)
    
    # Logger racine Nextvision
    root_logger = logging.getLogger('nextvision')
    root_logger.setLevel(log_level_obj)
    
    # Effacer handlers existants
    root_logger.handlers.clear()
    
    # Handler console (JSON structuré)
    console_handler = logging.StreamHandler()
    console_handler.addFilter(ContextualFilter())
    console_handler.setFormatter(LogFormatter.get_production_formatter())
    console_handler.setLevel(log_level_obj)
    root_logger.addHandler(console_handler)
    
    # Handler fichier si activé
    if enable_file_logging:
        try:
            # Créer répertoire si nécessaire
            os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
            
            file_handler = RotatingFileHandler(
                log_file_path,
                maxBytes=max_file_size_mb * 1024 * 1024,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.addFilter(ContextualFilter())
            file_handler.setFormatter(LogFormatter.get_production_formatter())
            file_handler.setLevel(log_level_obj)
            root_logger.addHandler(file_handler)
            
        except Exception as e:
            # Log warning si impossible de configurer fichier
            console_logger = get_structured_logger('nextvision.logging')
            console_logger.warning(f"Failed to setup file logging: {e}")
    
    # Empêcher propagation
    root_logger.propagate = False
    
    # Configuration des loggers externes
    external_loggers_config = {
        'uvicorn': logging.WARNING,
        'uvicorn.access': logging.WARNING,
        'fastapi': logging.INFO,
        'aiohttp': logging.WARNING,
        'redis': logging.WARNING,
        'urllib3': logging.WARNING
    }
    
    for logger_name, level in external_loggers_config.items():
        external_logger = logging.getLogger(logger_name)
        external_logger.setLevel(level)
    
    # Log de confirmation
    setup_logger = get_structured_logger('nextvision.logging')
    setup_logger.info("Production logging configured", extra={
        "log_level": log_level,
        "file_logging_enabled": enable_file_logging,
        "log_file_path": log_file_path if enable_file_logging else None,
        "handlers_count": len(root_logger.handlers)
    })
    
    return {
        "status": "configured",
        "log_level": log_level,
        "handlers": [
            {"type": "console", "formatter": "structured_json"},
            {"type": "file", "path": log_file_path, "enabled": enable_file_logging}
        ],
        "external_loggers": external_loggers_config
    }


def get_request_tracker() -> RequestTracker:
    """🔍 Obtient l'instance du request tracker"""
    return _request_tracker


# =====================================
# 🎯 DECORATORS
# =====================================

def log_function_call(
    component: LogComponent, 
    include_args: bool = False, 
    include_result: bool = False
):
    """🎯 Décorateur pour logger les appels de fonction"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = get_structured_logger(f"nextvision.{component.value}")
            func_name = func.__name__
            
            log_data = {"function_call": True}
            if include_args:
                log_data["arguments"] = {
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys())
                }
            
            with log_operation(func_name, component, log_data):
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    
                    duration = time.time() - start_time
                    log_data.update({
                        "function_success": True,
                        "duration_seconds": duration
                    })
                    
                    if include_result and result is not None:
                        log_data["result_type"] = type(result).__name__
                    
                    logger.debug(f"Function call completed: {func_name}", extra=log_data)
                    return result
                    
                except Exception as e:
                    duration = time.time() - start_time
                    log_data.update({
                        "function_error": True,
                        "duration_seconds": duration,
                        "error_type": type(e).__name__
                    })
                    
                    logger.error(f"Function call failed: {func_name}", extra=log_data, exc_info=True)
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = get_structured_logger(f"nextvision.{component.value}")
            func_name = func.__name__
            
            log_data = {"function_call": True}
            if include_args:
                log_data["arguments"] = {
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys())
                }
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                log_data.update({
                    "function_success": True,
                    "duration_seconds": duration
                })
                
                if include_result and result is not None:
                    log_data["result_type"] = type(result).__name__
                
                logger.debug(f"Function call completed: {func_name}", extra=log_data)
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                log_data.update({
                    "function_error": True,
                    "duration_seconds": duration,
                    "error_type": type(e).__name__
                })
                
                logger.error(f"Function call failed: {func_name}", extra=log_data, exc_info=True)
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# =====================================
# 📊 LOGGING ANALYTICS
# =====================================

class LogAnalytics:
    """📊 Analyse des logs pour insights"""
    
    def __init__(self):
        self.log_buffer: List[Dict[str, Any]] = []
        self.max_buffer_size = 1000
        self.analytics_enabled = True
    
    def capture_log_entry(self, log_entry: Dict[str, Any]):
        """📝 Capture une entrée de log pour analyse"""
        if not self.analytics_enabled:
            return
        
        self.log_buffer.append({
            **log_entry,
            "captured_at": datetime.now().isoformat()
        })
        
        # Limitation de la taille du buffer
        if len(self.log_buffer) > self.max_buffer_size:
            self.log_buffer = self.log_buffer[-self.max_buffer_size:]
    
    def get_error_patterns(self, hours: int = 1) -> Dict[str, Any]:
        """🔍 Analyse des patterns d'erreurs"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_errors = [
            entry for entry in self.log_buffer
            if entry.get("level") in ["ERROR", "CRITICAL"]
            and datetime.fromisoformat(entry.get("captured_at", "")) > cutoff_time
        ]
        
        if not recent_errors:
            return {"status": "no_errors"}
        
        # Analyse par composant
        component_errors = {}
        for error in recent_errors:
            component = error.get("context", {}).get("component", "unknown")
            if component not in component_errors:
                component_errors[component] = []
            component_errors[component].append(error)
        
        # Top erreurs
        error_messages = [e.get("message", "") for e in recent_errors]
        message_counts = {}
        for msg in error_messages:
            message_counts[msg] = message_counts.get(msg, 0) + 1
        
        top_errors = sorted(message_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_errors": len(recent_errors),
            "time_window_hours": hours,
            "errors_by_component": {k: len(v) for k, v in component_errors.items()},
            "top_error_messages": top_errors,
            "error_rate_per_hour": len(recent_errors) / hours
        }
    
    def get_performance_insights(self, hours: int = 1) -> Dict[str, Any]:
        """📈 Insights de performance depuis les logs"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        performance_logs = [
            entry for entry in self.log_buffer
            if "performance" in entry.get("extra", {})
            and datetime.fromisoformat(entry.get("captured_at", "")) > cutoff_time
        ]
        
        if not performance_logs:
            return {"status": "no_performance_data"}
        
        # Extraction des durées
        durations = []
        for log in performance_logs:
            perf_data = log.get("extra", {}).get("performance", {})
            duration = perf_data.get("duration_seconds") or perf_data.get("duration_ms", 0) / 1000
            if duration:
                durations.append(duration)
        
        if not durations:
            return {"status": "no_duration_data"}
        
        # Statistiques
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)
        
        # Slow operations (> 1s)
        slow_ops = [d for d in durations if d > 1.0]
        
        return {
            "total_operations": len(durations),
            "average_duration_seconds": round(avg_duration, 3),
            "max_duration_seconds": round(max_duration, 3),
            "min_duration_seconds": round(min_duration, 3),
            "slow_operations_count": len(slow_ops),
            "slow_operations_percent": round((len(slow_ops) / len(durations)) * 100, 2)
        }


# Instance globale pour analytics
_log_analytics = LogAnalytics()


def get_log_analytics() -> LogAnalytics:
    """📊 Obtient l'instance d'analytics des logs"""
    return _log_analytics
