"""
📝 Structured Logging - Production Enterprise Grade

Logging JSON structuré pour debugging production :
• Logs JSON formatés avec contexte
• Niveaux adaptatifs selon environnement
• Filtrage de données sensibles
• Corrélation des requêtes
• Métriques de performance intégrées
• Intégration ELK/Prometheus
• Rotation automatique

Author: NEXTEN Team - Production Robustness
Version: 1.0.0
"""

import asyncio
import json
import logging
import logging.handlers
import os
import time
import traceback
import uuid
from contextvars import ContextVar
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
import sys

class LogLevel(Enum):
    """📊 Niveaux de logging"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogEnvironment(Enum):
    """🌍 Environnements de déploiement"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

@dataclass
class LogConfig:
    """⚙️ Configuration logging structuré"""
    # Environment & Levels
    environment: LogEnvironment = LogEnvironment.DEVELOPMENT
    log_level: LogLevel = LogLevel.INFO
    
    # Output Configuration
    enable_console: bool = True
    enable_file: bool = True
    enable_json_format: bool = True
    
    # File Configuration
    log_dir: str = "logs"
    log_filename: str = "nextvision.log"
    max_file_size_mb: int = 100
    backup_count: int = 5
    
    # Performance Logging
    enable_performance_logs: bool = True
    slow_query_threshold_ms: float = 1000.0
    
    # Security & Privacy
    enable_security_filtering: bool = True
    mask_sensitive_data: bool = True
    
    # Request Correlation
    enable_request_correlation: bool = True
    correlation_header_name: str = "X-Correlation-ID"
    
    # Structured Fields
    service_name: str = "nextvision"
    service_version: str = "2.0.0"
    
    # External Integrations
    enable_elk_integration: bool = False
    elk_host: str = "localhost:9200"
    enable_prometheus_metrics: bool = False
    
    # Sampling (pour high-traffic)
    enable_sampling: bool = False
    sample_rate: float = 0.1  # 10% des logs

# Context variables pour corrélation
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
user_id: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
request_id: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
session_id: ContextVar[Optional[str]] = ContextVar('session_id', default=None)

class ContextManager:
    """🔗 Gestionnaire de contexte pour corrélation"""
    
    @staticmethod
    def set_correlation_id(cid: str):
        """🆔 Définit ID de corrélation"""
        correlation_id.set(cid)
    
    @staticmethod
    def get_correlation_id() -> Optional[str]:
        """🆔 Récupère ID de corrélation"""
        return correlation_id.get()
    
    @staticmethod
    def set_user_id(uid: str):
        """👤 Définit ID utilisateur"""
        user_id.set(uid)
    
    @staticmethod
    def get_user_id() -> Optional[str]:
        """👤 Récupère ID utilisateur"""
        return user_id.get()
    
    @staticmethod
    def set_request_id(rid: str):
        """📨 Définit ID requête"""
        request_id.set(rid)
    
    @staticmethod
    def get_request_id() -> Optional[str]:
        """📨 Récupère ID requête"""
        return request_id.get()
    
    @staticmethod
    def generate_correlation_id() -> str:
        """🎲 Génère nouvel ID de corrélation"""
        return str(uuid.uuid4())
    
    @staticmethod
    def get_context() -> Dict[str, Any]:
        """🔗 Récupère contexte complet"""
        return {
            "correlation_id": correlation_id.get(),
            "user_id": user_id.get(),
            "request_id": request_id.get(),
            "session_id": session_id.get()
        }

class SecurityFilter:
    """🔒 Filtre de sécurité pour données sensibles"""
    
    def __init__(self):
        # Patterns à masquer
        self.sensitive_keys = {
            'password', 'passwd', 'pwd', 'secret', 'token', 'key', 'api_key',
            'authorization', 'auth', 'credential', 'private', 'confidential',
            'ssn', 'social_security', 'credit_card', 'card_number', 'cvv',
            'email', 'phone', 'address', 'ip_address'
        }
        
        # Patterns regex pour détection automatique
        self.sensitive_patterns = [
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Carte crédit
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN US
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b(?:\d{1,3}\.){3}\d{1,3}\b',  # IP Address
        ]
    
    def filter_sensitive_data(self, data: Any) -> Any:
        """🔒 Filtre données sensibles"""
        if isinstance(data, dict):
            return {k: self._mask_value(k, v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.filter_sensitive_data(item) for item in data]
        elif isinstance(data, str):
            return self._mask_string_patterns(data)
        else:
            return data
    
    def _mask_value(self, key: str, value: Any) -> Any:
        """🎭 Masque valeur selon la clé"""
        if isinstance(key, str) and key.lower() in self.sensitive_keys:
            return "***MASKED***"
        
        if isinstance(value, dict):
            return self.filter_sensitive_data(value)
        elif isinstance(value, list):
            return [self.filter_sensitive_data(item) for item in value]
        elif isinstance(value, str):
            return self._mask_string_patterns(value)
        else:
            return value
    
    def _mask_string_patterns(self, text: str) -> str:
        """🎭 Masque patterns sensibles dans texte"""
        import re
        
        masked_text = text
        for pattern in self.sensitive_patterns:
            masked_text = re.sub(pattern, "***MASKED***", masked_text)
        
        return masked_text

class StructuredFormatter(logging.Formatter):
    """📋 Formateur JSON structuré"""
    
    def __init__(self, config: LogConfig):
        super().__init__()
        self.config = config
        self.security_filter = SecurityFilter() if config.mask_sensitive_data else None
        self.hostname = os.uname().nodename if hasattr(os, 'uname') else 'unknown'
    
    def format(self, record: logging.LogRecord) -> str:
        """📝 Formate log en JSON structuré"""
        # Base log entry
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process
        }
        
        # Service metadata
        log_entry["service"] = {
            "name": self.config.service_name,
            "version": self.config.service_version,
            "environment": self.config.environment.value,
            "hostname": self.hostname
        }
        
        # Context correlation
        if self.config.enable_request_correlation:
            context = ContextManager.get_context()
            if any(context.values()):
                log_entry["context"] = {k: v for k, v in context.items() if v is not None}
        
        # Extra fields from log record
        if hasattr(record, 'extra') and record.extra:
            extra_data = record.extra
            if self.security_filter and self.config.mask_sensitive_data:
                extra_data = self.security_filter.filter_sensitive_data(extra_data)
            log_entry["extra"] = extra_data
        
        # Performance data
        if hasattr(record, 'duration_ms'):
            log_entry["performance"] = {
                "duration_ms": record.duration_ms,
                "is_slow": record.duration_ms > self.config.slow_query_threshold_ms
            }
        
        # Exception info
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }
        
        # Stack trace pour erreurs
        if record.levelno >= logging.ERROR and not record.exc_info:
            log_entry["stack_trace"] = ''.join(traceback.format_stack())
        
        # Sampling (pour réduire volume en production)
        if self.config.enable_sampling:
            import random
            if random.random() > self.config.sample_rate:
                return ""  # Skip ce log
        
        if self.config.enable_json_format:
            return json.dumps(log_entry, default=str, ensure_ascii=False)
        else:
            # Format traditionnel pour développement
            return f"{log_entry['timestamp']} [{log_entry['level']}] {log_entry['logger']}: {log_entry['message']}"

class PerformanceLogger:
    """⚡ Logger performance avec métriques"""
    
    def __init__(self, logger: logging.Logger, config: LogConfig):
        self.logger = logger
        self.config = config
        self.operation_times: Dict[str, List[float]] = {}
    
    def log_operation(self, operation_name: str, duration_ms: float, success: bool = True, extra: Optional[Dict] = None):
        """📊 Log opération avec performance"""
        # Enregistrer timing
        if operation_name not in self.operation_times:
            self.operation_times[operation_name] = []
        self.operation_times[operation_name].append(duration_ms)
        
        # Log entry avec performance
        log_data = {
            "operation": operation_name,
            "duration_ms": round(duration_ms, 2),
            "success": success,
            "is_slow": duration_ms > self.config.slow_query_threshold_ms
        }
        
        if extra:
            log_data.update(extra)
        
        # Niveau selon performance
        if not success:
            level = logging.ERROR
        elif duration_ms > self.config.slow_query_threshold_ms:
            level = logging.WARNING
        else:
            level = logging.INFO
        
        # Log avec extra data
        old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.extra = log_data
            record.duration_ms = duration_ms
            return record
        
        logging.setLogRecordFactory(record_factory)
        
        try:
            self.logger.log(level, f"Operation {operation_name} completed")
        finally:
            logging.setLogRecordFactory(old_factory)
    
    def get_operation_stats(self, operation_name: str) -> Dict:
        """📈 Statistiques opération"""
        if operation_name not in self.operation_times:
            return {}
        
        times = self.operation_times[operation_name]
        if not times:
            return {}
        
        import statistics
        
        return {
            "count": len(times),
            "avg_ms": round(statistics.mean(times), 2),
            "min_ms": round(min(times), 2),
            "max_ms": round(max(times), 2),
            "median_ms": round(statistics.median(times), 2),
            "p95_ms": round(self._percentile(sorted(times), 95), 2) if len(times) > 1 else round(times[0], 2)
        }
    
    def _percentile(self, sorted_data: List[float], percentile: int) -> float:
        """📊 Calcule percentile"""
        index = (percentile / 100.0) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index % 1)

class StructuredLogger:
    """📝 Logger structuré principal"""
    
    def __init__(self, name: str, config: LogConfig):
        self.name = name
        self.config = config
        self.logger = logging.getLogger(name)
        self.performance_logger = PerformanceLogger(self.logger, config)
        
        # Configuration niveau
        self.logger.setLevel(getattr(logging, config.log_level.value))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Setup handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """🔧 Configuration handlers"""
        formatter = StructuredFormatter(self.config)
        
        # Console handler
        if self.config.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # File handler avec rotation
        if self.config.enable_file:
            # Créer répertoire logs
            log_dir = Path(self.config.log_dir)
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / self.config.log_filename
            
            file_handler = logging.handlers.RotatingFileHandler(
                filename=log_file,
                maxBytes=self.config.max_file_size_mb * 1024 * 1024,
                backupCount=self.config.backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, msg: str, **kwargs):
        """🐛 Log debug"""
        self._log(logging.DEBUG, msg, kwargs)
    
    def info(self, msg: str, **kwargs):
        """ℹ️ Log info"""
        self._log(logging.INFO, msg, kwargs)
    
    def warning(self, msg: str, **kwargs):
        """⚠️ Log warning"""
        self._log(logging.WARNING, msg, kwargs)
    
    def error(self, msg: str, **kwargs):
        """❌ Log error"""
        self._log(logging.ERROR, msg, kwargs)
    
    def critical(self, msg: str, **kwargs):
        """🚨 Log critical"""
        self._log(logging.CRITICAL, msg, kwargs)
    
    def _log(self, level: int, msg: str, extra: Dict):
        """📝 Log avec extra data"""
        # Filter sensitive data
        if self.config.mask_sensitive_data:
            security_filter = SecurityFilter()
            extra = security_filter.filter_sensitive_data(extra)
        
        # Create log record factory with extra
        old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.extra = extra
            return record
        
        logging.setLogRecordFactory(record_factory)
        
        try:
            self.logger.log(level, msg)
        finally:
            logging.setLogRecordFactory(old_factory)
    
    def log_performance(self, operation_name: str, duration_ms: float, success: bool = True, **extra):
        """⚡ Log performance"""
        self.performance_logger.log_operation(operation_name, duration_ms, success, extra)
    
    def log_request(self, method: str, path: str, status_code: int, duration_ms: float, **extra):
        """🌐 Log requête HTTP"""
        request_data = {
            "http": {
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": round(duration_ms, 2)
            },
            **extra
        }
        
        # Niveau selon status code
        if status_code >= 500:
            level = "error"
        elif status_code >= 400:
            level = "warning"
        else:
            level = "info"
        
        getattr(self, level)(f"{method} {path} - {status_code}", **request_data)
    
    def log_exception(self, exception: Exception, context: Optional[Dict] = None):
        """💥 Log exception avec contexte"""
        exc_data = {
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "context": context or {}
        }
        
        self.error(f"Exception occurred: {type(exception).__name__}", exc_info=True, **exc_data)
    
    def get_performance_stats(self) -> Dict:
        """📊 Statistiques performance"""
        return {
            op_name: self.performance_logger.get_operation_stats(op_name)
            for op_name in self.performance_logger.operation_times.keys()
        }

# ===============================================
# 🚀 SETUP & UTILITIES
# ===============================================

_loggers: Dict[str, StructuredLogger] = {}
_config: Optional[LogConfig] = None

def setup_production_logging(config: LogConfig) -> None:
    """🚀 Setup logging production"""
    global _config
    _config = config
    
    # Configuration logging global
    logging.basicConfig(
        level=getattr(logging, config.log_level.value),
        format='%(message)s'  # Le formateur structuré gère le format
    )
    
    # Disable noisy loggers en production
    if config.environment == LogEnvironment.PRODUCTION:
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('aiohttp').setLevel(logging.WARNING)
        logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    print(f"📝 Production logging configured - Environment: {config.environment.value}, Level: {config.log_level.value}")

def get_structured_logger(name: str, config: Optional[LogConfig] = None) -> StructuredLogger:
    """📝 Récupère logger structuré"""
    global _loggers, _config
    
    if name not in _loggers:
        effective_config = config or _config or LogConfig()
        _loggers[name] = StructuredLogger(name, effective_config)
    
    return _loggers[name]

# Context managers pour corrélation
class correlation_context:
    """🔗 Context manager pour corrélation"""
    
    def __init__(self, correlation_id: Optional[str] = None, user_id: Optional[str] = None):
        self.correlation_id = correlation_id or ContextManager.generate_correlation_id()
        self.user_id = user_id
        self.previous_correlation_id = None
        self.previous_user_id = None
    
    def __enter__(self):
        self.previous_correlation_id = ContextManager.get_correlation_id()
        self.previous_user_id = ContextManager.get_user_id()
        
        ContextManager.set_correlation_id(self.correlation_id)
        if self.user_id:
            ContextManager.set_user_id(self.user_id)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.previous_correlation_id:
            ContextManager.set_correlation_id(self.previous_correlation_id)
        if self.previous_user_id:
            ContextManager.set_user_id(self.previous_user_id)

class performance_context:
    """⚡ Context manager pour logging performance"""
    
    def __init__(self, logger: StructuredLogger, operation_name: str, **extra):
        self.logger = logger
        self.operation_name = operation_name
        self.extra = extra
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        success = exc_type is None
        
        if exc_type:
            self.extra['exception'] = {
                'type': exc_type.__name__,
                'message': str(exc_val)
            }
        
        self.logger.log_performance(self.operation_name, duration_ms, success, **self.extra)

# Décorateurs utiles
def log_performance(operation_name: str = None, logger_name: str = "nextvision"):
    """⚡ Décorateur logging performance"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            logger = get_structured_logger(logger_name)
            
            with performance_context(logger, op_name):
                return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            logger = get_structured_logger(logger_name)
            
            with performance_context(logger, op_name):
                return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def log_exceptions(logger_name: str = "nextvision"):
    """💥 Décorateur logging exceptions"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            logger = get_structured_logger(logger_name)
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.log_exception(e, {
                    'function': func.__name__,
                    'module': func.__module__,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys())
                })
                raise
        
        def sync_wrapper(*args, **kwargs):
            logger = get_structured_logger(logger_name)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.log_exception(e, {
                    'function': func.__name__,
                    'module': func.__module__,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys())
                })
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Configurations prédéfinies
class LogConfigs:
    """🎯 Configurations logging prédéfinies"""
    
    DEVELOPMENT = LogConfig(
        environment=LogEnvironment.DEVELOPMENT,
        log_level=LogLevel.DEBUG,
        enable_json_format=False,  # Format lisible pour dev
        enable_performance_logs=True,
        mask_sensitive_data=False,  # Pas de masquage en dev
        enable_sampling=False
    )
    
    STAGING = LogConfig(
        environment=LogEnvironment.STAGING,
        log_level=LogLevel.INFO,
        enable_json_format=True,
        enable_performance_logs=True,
        mask_sensitive_data=True,
        enable_sampling=False,
        slow_query_threshold_ms=500.0
    )
    
    PRODUCTION = LogConfig(
        environment=LogEnvironment.PRODUCTION,
        log_level=LogLevel.WARNING,  # Moins verbose en prod
        enable_json_format=True,
        enable_performance_logs=True,
        mask_sensitive_data=True,
        enable_sampling=True,
        sample_rate=0.1,  # 10% des logs
        slow_query_threshold_ms=1000.0,
        max_file_size_mb=200,
        backup_count=10
    )
    
    TESTING = LogConfig(
        environment=LogEnvironment.TESTING,
        log_level=LogLevel.ERROR,  # Minimal pour tests
        enable_console=False,
        enable_file=False,
        enable_performance_logs=False,
        mask_sensitive_data=False
    )

# Usage examples
if __name__ == "__main__":
    # Setup pour développement
    setup_production_logging(LogConfigs.DEVELOPMENT)
    
    # Logger exemple
    logger = get_structured_logger("example")
    
    # Usage basique
    logger.info("Application started", version="2.0.0", environment="dev")
    
    # Avec contexte
    with correlation_context(user_id="user123"):
        logger.info("Processing user request", action="geocoding", address="Paris")
        
        # Performance logging
        with performance_context(logger, "geocoding_operation", address="Paris"):
            import time
            time.sleep(0.1)  # Simulate work
    
    # Exception logging
    try:
        raise ValueError("Example error")
    except Exception as e:
        logger.log_exception(e, {"context": "example"})
    
    # Stats
    stats = logger.get_performance_stats()
    print(f"Performance stats: {stats}")
