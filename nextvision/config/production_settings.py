"""
⚙️ Production Settings - Configuration Enterprise Grade

Configuration centralisée pour production :
• Multi-environnements (dev/staging/prod)
• Variables d'environnement sécurisées
• Validation configuration
• Hot-reload pour développement
• Secrets management
• Feature flags
• Performance tuning per environment

Author: NEXTEN Team - Production Robustness
Version: 1.0.0
"""

import os
import json
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from urllib.parse import urlparse

# Pour validation
try:
    from pydantic import BaseModel, Field, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = object
    Field = lambda **kwargs: None
    def validator(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

class Environment(Enum):
    """🌍 Environnements supportés"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class DatabaseType(Enum):
    """🗄️ Types de base de données"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"

@dataclass
class DatabaseConfig:
    """🗄️ Configuration base de données"""
    # Connection
    type: DatabaseType = DatabaseType.POSTGRESQL
    host: str = "localhost"
    port: int = 5432
    database: str = "nextvision"
    username: str = "nextvision"
    password: str = "password"
    
    # Pool Configuration
    min_pool_size: int = 5
    max_pool_size: int = 20
    pool_timeout_seconds: int = 30
    pool_recycle_seconds: int = 3600
    
    # Performance
    query_timeout_seconds: int = 30
    slow_query_threshold_ms: int = 1000
    enable_query_logging: bool = False
    
    # SSL
    ssl_enabled: bool = False
    ssl_cert_path: Optional[str] = None
    
    def get_url(self, mask_password: bool = False) -> str:
        """🔗 Génère URL de connexion"""
        password = "***MASKED***" if mask_password else self.password
        return f"{self.type.value}://{self.username}:{password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def connection_params(self) -> Dict:
        """📋 Paramètres de connexion"""
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.username,
            "password": self.password,
            "minsize": self.min_pool_size,
            "maxsize": self.max_pool_size,
            "command_timeout": self.query_timeout_seconds
        }

@dataclass
class RedisConfig:
    """🔴 Configuration Redis"""
    # Connection
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: Optional[str] = None
    
    # Pool Configuration
    max_connections: int = 50
    retry_on_timeout: bool = True
    socket_keepalive: bool = True
    
    # Timeouts
    socket_timeout_seconds: float = 5.0
    socket_connect_timeout_seconds: float = 5.0
    health_check_interval_seconds: int = 30
    
    # Memory Management
    maxmemory_policy: str = "allkeys-lru"
    
    def get_url(self, mask_password: bool = False) -> str:
        """🔗 Génère URL Redis"""
        if self.password:
            password = "***MASKED***" if mask_password else self.password
            return f"redis://:{password}@{self.host}:{self.port}/{self.database}"
        else:
            return f"redis://{self.host}:{self.port}/{self.database}"

@dataclass 
class GoogleMapsConfig:
    """🗺️ Configuration Google Maps"""
    # API Configuration
    api_key: str = "YOUR_API_KEY"
    
    # Rate Limiting
    daily_request_limit: int = 25000
    requests_per_minute: int = 1000
    requests_per_second: int = 50
    
    # Caching
    enable_memory_cache: bool = True
    enable_redis_cache: bool = True
    geocode_cache_duration_hours: int = 24
    directions_cache_duration_hours: int = 6
    
    # Timeouts
    request_timeout_seconds: int = 10
    retry_attempts: int = 3
    retry_delay_seconds: float = 1.0
    
    # Features
    enable_traffic_data: bool = True
    default_region: str = "fr"
    default_language: str = "fr"
    
    # Fallback
    enable_fallback_mode: bool = True
    log_requests: bool = False
    
    @property
    def is_configured(self) -> bool:
        """✅ Vérifie si API key configurée"""
        return self.api_key != "YOUR_API_KEY" and len(self.api_key) > 10

@dataclass
class SecurityConfig:
    """🔒 Configuration sécurité"""
    # API Security
    api_key_header: str = "X-API-Key"
    enable_api_key_auth: bool = False
    api_keys: List[str] = field(default_factory=list)
    
    # CORS
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    allowed_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    allowed_headers: List[str] = field(default_factory=lambda: ["*"])
    
    # Rate Limiting
    enable_rate_limiting: bool = True
    rate_limit_requests: int = 1000
    rate_limit_window_minutes: int = 60
    
    # Request Validation
    max_request_size_mb: int = 10
    enable_request_validation: bool = True
    
    # Security Headers
    enable_security_headers: bool = True
    
    # Data Protection
    enable_data_encryption: bool = False
    encryption_key: Optional[str] = None
    
    # Audit
    enable_audit_logging: bool = True
    log_sensitive_data: bool = False

@dataclass
class MonitoringConfig:
    """📊 Configuration monitoring"""
    # Health Checks
    enable_health_checks: bool = True
    health_check_interval_seconds: int = 30
    
    # Metrics
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    # Prometheus
    enable_prometheus: bool = False
    prometheus_endpoint: str = "/metrics"
    
    # Logging
    log_level: str = "INFO"
    enable_structured_logging: bool = True
    log_file_max_size_mb: int = 100
    log_file_backup_count: int = 5
    
    # Performance
    enable_performance_monitoring: bool = True
    slow_request_threshold_ms: int = 1000
    
    # Alerting
    enable_alerting: bool = False
    alert_webhook_url: Optional[str] = None
    
    # External Services
    enable_elk_integration: bool = False
    elk_host: Optional[str] = None
    enable_sentry: bool = False
    sentry_dsn: Optional[str] = None

@dataclass
class PerformanceConfig:
    """⚡ Configuration performance"""
    # FastAPI
    workers: int = 4
    worker_class: str = "uvicorn.workers.UvicornWorker"
    max_requests: int = 1000
    max_requests_jitter: int = 100
    
    # Request Processing
    request_timeout_seconds: int = 30
    keep_alive_timeout_seconds: int = 5
    
    # Concurrency
    max_concurrent_requests: int = 1000
    semaphore_limit: int = 100
    
    # Caching
    enable_response_caching: bool = True
    cache_ttl_seconds: int = 300
    
    # Batch Processing
    batch_size: int = 50
    max_batch_size: int = 1000
    batch_timeout_seconds: int = 30
    
    # Connection Pools
    http_pool_connections: int = 20
    http_pool_maxsize: int = 20
    http_max_retries: int = 3

@dataclass
class FeatureFlags:
    """🚩 Feature flags"""
    # Core Features
    enable_adaptive_weighting: bool = True
    enable_google_maps_intelligence: bool = True
    enable_batch_processing: bool = True
    
    # Advanced Features
    enable_ml_predictions: bool = False
    enable_real_time_updates: bool = False
    enable_analytics: bool = True
    
    # Experimental
    enable_experimental_features: bool = False
    experimental_algorithms: List[str] = field(default_factory=list)
    
    # A/B Testing
    enable_ab_testing: bool = False
    ab_test_percentage: float = 0.1  # 10%

class EnvironmentConfig:
    """🌍 Configuration par environnement"""
    
    @staticmethod
    def development() -> Dict:
        """🛠️ Configuration développement"""
        return {
            "database": DatabaseConfig(
                type=DatabaseType.SQLITE,
                database="nextvision_dev.db",
                enable_query_logging=True,
                max_pool_size=5
            ),
            "redis": RedisConfig(
                max_connections=10
            ),
            "google_maps": GoogleMapsConfig(
                daily_request_limit=1000,
                log_requests=True,
                enable_fallback_mode=True
            ),
            "security": SecurityConfig(
                enable_api_key_auth=False,
                allowed_origins=["http://localhost:3000", "http://localhost:8000"],
                enable_rate_limiting=False
            ),
            "monitoring": MonitoringConfig(
                log_level="DEBUG",
                enable_structured_logging=False,  # Format lisible
                health_check_interval_seconds=60
            ),
            "performance": PerformanceConfig(
                workers=1,
                max_concurrent_requests=100,
                batch_size=10
            ),
            "features": FeatureFlags(
                enable_experimental_features=True
            )
        }
    
    @staticmethod
    def staging() -> Dict:
        """🧪 Configuration staging"""
        return {
            "database": DatabaseConfig(
                host=os.getenv("DB_HOST", "localhost"),
                password=os.getenv("DB_PASSWORD", "password"),
                max_pool_size=10,
                enable_query_logging=True
            ),
            "redis": RedisConfig(
                host=os.getenv("REDIS_HOST", "localhost"),
                password=os.getenv("REDIS_PASSWORD"),
                max_connections=20
            ),
            "google_maps": GoogleMapsConfig(
                api_key=os.getenv("GOOGLE_MAPS_API_KEY", "YOUR_API_KEY"),
                daily_request_limit=10000,
                log_requests=True
            ),
            "security": SecurityConfig(
                enable_api_key_auth=True,
                api_keys=[os.getenv("API_KEY", "staging-key")],
                allowed_origins=["https://staging.nexten.app"],
                enable_rate_limiting=True,
                rate_limit_requests=500
            ),
            "monitoring": MonitoringConfig(
                log_level="INFO",
                enable_prometheus=True,
                enable_alerting=True
            ),
            "performance": PerformanceConfig(
                workers=2,
                max_concurrent_requests=500,
                batch_size=25
            ),
            "features": FeatureFlags(
                enable_ab_testing=True,
                ab_test_percentage=0.2
            )
        }
    
    @staticmethod
    def production() -> Dict:
        """🚀 Configuration production"""
        return {
            "database": DatabaseConfig(
                host=os.getenv("DB_HOST", "db.nexten.app"),
                port=int(os.getenv("DB_PORT", "5432")),
                database=os.getenv("DB_NAME", "nextvision_prod"),
                username=os.getenv("DB_USER", "nextvision"),
                password=os.getenv("DB_PASSWORD"),
                min_pool_size=10,
                max_pool_size=50,
                ssl_enabled=True,
                enable_query_logging=False  # Performance
            ),
            "redis": RedisConfig(
                host=os.getenv("REDIS_HOST", "redis.nexten.app"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                password=os.getenv("REDIS_PASSWORD"),
                max_connections=100,
                maxmemory_policy="allkeys-lru"
            ),
            "google_maps": GoogleMapsConfig(
                api_key=os.getenv("GOOGLE_MAPS_API_KEY"),
                daily_request_limit=25000,
                requests_per_minute=1000,
                log_requests=False,  # Privacy
                enable_traffic_data=True
            ),
            "security": SecurityConfig(
                enable_api_key_auth=True,
                api_keys=os.getenv("API_KEYS", "").split(",") if os.getenv("API_KEYS") else [],
                allowed_origins=["https://nexten.app", "https://app.nexten.fr"],
                enable_rate_limiting=True,
                rate_limit_requests=1000,
                enable_data_encryption=True,
                encryption_key=os.getenv("ENCRYPTION_KEY"),
                log_sensitive_data=False
            ),
            "monitoring": MonitoringConfig(
                log_level="WARNING",  # Moins verbose
                enable_prometheus=True,
                enable_alerting=True,
                alert_webhook_url=os.getenv("ALERT_WEBHOOK_URL"),
                enable_elk_integration=True,
                elk_host=os.getenv("ELK_HOST"),
                enable_sentry=True,
                sentry_dsn=os.getenv("SENTRY_DSN")
            ),
            "performance": PerformanceConfig(
                workers=int(os.getenv("WORKERS", "8")),
                max_concurrent_requests=2000,
                batch_size=100,
                max_batch_size=1000,
                enable_response_caching=True
            ),
            "features": FeatureFlags(
                enable_ml_predictions=True,
                enable_real_time_updates=True,
                enable_analytics=True,
                enable_ab_testing=True,
                ab_test_percentage=0.05  # 5% en prod
            )
        }
    
    @staticmethod
    def testing() -> Dict:
        """🧪 Configuration tests"""
        return {
            "database": DatabaseConfig(
                type=DatabaseType.SQLITE,
                database=":memory:",  # In-memory pour tests
                max_pool_size=1
            ),
            "redis": RedisConfig(
                database=15,  # DB Redis dédiée tests
                max_connections=5
            ),
            "google_maps": GoogleMapsConfig(
                api_key="test_key",
                enable_fallback_mode=True,
                log_requests=False
            ),
            "security": SecurityConfig(
                enable_api_key_auth=False,
                enable_rate_limiting=False,
                log_sensitive_data=True  # OK pour tests
            ),
            "monitoring": MonitoringConfig(
                log_level="ERROR",  # Minimal pour tests
                enable_health_checks=False,
                enable_metrics=False
            ),
            "performance": PerformanceConfig(
                workers=1,
                max_concurrent_requests=10,
                batch_size=5
            ),
            "features": FeatureFlags(
                # Toutes les features activées pour tests
                enable_experimental_features=True
            )
        }

class ProductionConfig:
    """⚙️ Configuration principale application"""
    
    def __init__(self, environment: Environment = None):
        # Détection environnement
        if environment is None:
            env_name = os.getenv("ENVIRONMENT", "development").lower()
            try:
                environment = Environment(env_name)
            except ValueError:
                environment = Environment.DEVELOPMENT
        
        self.environment = environment
        
        # Chargement configuration
        self._load_config()
        
        # Validation
        self._validate_config()
    
    def _load_config(self):
        """📥 Charge configuration selon environnement"""
        config_map = {
            Environment.DEVELOPMENT: EnvironmentConfig.development(),
            Environment.STAGING: EnvironmentConfig.staging(),
            Environment.PRODUCTION: EnvironmentConfig.production(),
            Environment.TESTING: EnvironmentConfig.testing()
        }
        
        config = config_map[self.environment]
        
        self.database = config["database"]
        self.redis = config["redis"]
        self.google_maps = config["google_maps"]
        self.security = config["security"]
        self.monitoring = config["monitoring"]
        self.performance = config["performance"]
        self.features = config["features"]
        
        # Configuration générale
        self.app_name = os.getenv("APP_NAME", "nextvision")
        self.app_version = os.getenv("APP_VERSION", "2.0.0")
        self.debug = self.environment == Environment.DEVELOPMENT
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        
        print(f"⚙️ Configuration loaded for environment: {self.environment.value}")
    
    def _validate_config(self):
        """✅ Validation configuration"""
        errors = []
        
        # Validation production
        if self.environment == Environment.PRODUCTION:
            if not self.google_maps.is_configured:
                errors.append("Google Maps API key not configured for production")
            
            if not self.database.password or self.database.password == "password":
                errors.append("Database password not configured for production")
            
            if not self.security.api_keys:
                errors.append("API keys not configured for production")
            
            if self.security.allowed_origins == ["*"]:
                errors.append("CORS origins should be restricted in production")
        
        # Validation Google Maps
        if self.features.enable_google_maps_intelligence and not self.google_maps.is_configured:
            errors.append("Google Maps Intelligence enabled but API key not configured")
        
        # Validation Redis (si cache activé)
        if self.google_maps.enable_redis_cache:
            if not self.redis.host:
                errors.append("Redis cache enabled but host not configured")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors)
            
            if self.environment == Environment.PRODUCTION:
                raise ValueError(error_msg)
            else:
                print(f"⚠️ Configuration warnings:\n{error_msg}")
    
    def get_database_url(self, mask_password: bool = False) -> str:
        """🔗 URL de connexion base de données"""
        return self.database.get_url(mask_password)
    
    def get_redis_url(self, mask_password: bool = False) -> str:
        """🔗 URL de connexion Redis"""
        return self.redis.get_url(mask_password)
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """🚩 Vérifie si feature activée"""
        return getattr(self.features, f"enable_{feature_name}", False)
    
    def get_summary(self) -> Dict:
        """📋 Résumé configuration"""
        return {
            "environment": self.environment.value,
            "app": {
                "name": self.app_name,
                "version": self.app_version,
                "debug": self.debug,
                "host": self.host,
                "port": self.port
            },
            "database": {
                "type": self.database.type.value,
                "host": self.database.host,
                "database": self.database.database,
                "pool_size": f"{self.database.min_pool_size}-{self.database.max_pool_size}"
            },
            "redis": {
                "host": self.redis.host,
                "database": self.redis.database,
                "max_connections": self.redis.max_connections
            },
            "google_maps": {
                "configured": self.google_maps.is_configured,
                "daily_limit": self.google_maps.daily_request_limit,
                "cache_enabled": self.google_maps.enable_redis_cache
            },
            "security": {
                "api_auth": self.security.enable_api_key_auth,
                "rate_limiting": self.security.enable_rate_limiting,
                "cors_origins": len(self.security.allowed_origins)
            },
            "performance": {
                "workers": self.performance.workers,
                "max_requests": self.performance.max_concurrent_requests,
                "batch_size": self.performance.batch_size
            },
            "features": {
                "adaptive_weighting": self.features.enable_adaptive_weighting,
                "google_maps_intelligence": self.features.enable_google_maps_intelligence,
                "batch_processing": self.features.enable_batch_processing,
                "experimental": self.features.enable_experimental_features
            }
        }

# ===============================================
# 🚀 GLOBAL CONFIG & UTILITIES
# ===============================================

_config: Optional[ProductionConfig] = None

def load_environment_config(environment: Environment = None) -> ProductionConfig:
    """📥 Charge configuration environnement"""
    global _config
    _config = ProductionConfig(environment)
    return _config

def get_config() -> ProductionConfig:
    """⚙️ Récupère configuration globale"""
    global _config
    if _config is None:
        _config = ProductionConfig()
    return _config

# Configuration par défaut au démarrage
if __name__ == "__main__":
    # Test configurations
    for env in Environment:
        print(f"\n=== {env.value.upper()} CONFIGURATION ===")
        config = ProductionConfig(env)
        summary = config.get_summary()
        
        for section, details in summary.items():
            print(f"{section.upper()}: {details}")
        
        print(f"Database URL: {config.get_database_url(mask_password=True)}")
        print(f"Redis URL: {config.get_redis_url(mask_password=True)}")

else:
    # Auto-load configuration
    try:
        _config = ProductionConfig()
    except Exception as e:
        print(f"⚠️ Failed to auto-load configuration: {e}")
        _config = None
