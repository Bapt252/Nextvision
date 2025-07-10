"""
⚙️ Nextvision - Production Configuration Management
Enterprise-grade configuration with environment-specific settings

Features:
- Multi-environment configuration (dev/staging/prod)
- Secure secrets management
- Database connection pooling settings
- Cache configuration
- Performance tuning parameters
- Monitoring and logging configuration
"""

import os
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import nextvision_logging as logging


class Environment(Enum):
    """🌍 Environnements supportés"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(Enum):
    """📝 Niveaux de log"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class DatabaseConfig:
    """🗃️ Configuration base de données"""
    # Connexion
    host: str = "localhost"
    port: int = 5432
    database: str = "nextvision"
    username: str = "nextvision_user"
    password: str = "nextvision_password"
    
    # Pool de connexions
    min_pool_size: int = 5
    max_pool_size: int = 20
    pool_timeout: int = 30
    pool_overflow: int = 10
    
    # Timeouts
    connection_timeout: int = 30
    query_timeout: int = 60
    
    # SSL
    ssl_enabled: bool = False
    ssl_cert_path: Optional[str] = None
    
    # Performance
    echo_queries: bool = False
    enable_query_cache: bool = True
    
    def get_connection_string(self) -> str:
        """🔗 String de connexion PostgreSQL"""
        return (
            f"postgresql://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
        )
    
    def get_async_connection_string(self) -> str:
        """🔗 String de connexion asyncpg"""
        return (
            f"postgresql://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
        )


@dataclass
class RedisConfig:
    """🗂️ Configuration Redis"""
    # Connexion
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    database: int = 0
    
    # Pool de connexions
    max_connections: int = 50
    connection_timeout: int = 5
    socket_timeout: int = 5
    
    # Retry
    retry_on_timeout: bool = True
    health_check_interval: int = 30
    
    # Clustering
    cluster_enabled: bool = False
    cluster_nodes: List[str] = field(default_factory=list)
    
    # Performance
    decode_responses: bool = False
    
    def get_connection_url(self) -> str:
        """🔗 URL de connexion Redis"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.database}"
        return f"redis://{self.host}:{self.port}/{self.database}"


@dataclass
class GoogleMapsConfig:
    """🗺️ Configuration Google Maps API"""
    api_key: str = "YOUR_API_KEY"
    
    # Rate limiting
    daily_request_limit: int = 40000
    requests_per_second: int = 50
    
    # Caching
    enable_memory_cache: bool = True
    enable_redis_cache: bool = True
    geocode_cache_duration_hours: int = 24
    directions_cache_duration_hours: int = 6
    
    # Timeouts
    api_timeout_seconds: int = 10
    
    # Fallback
    enable_fallback_mode: bool = True
    fallback_coordinates: Dict[str, Any] = field(default_factory=lambda: {
        "default": {"lat": 48.8566, "lng": 2.3522}  # Paris
    })
    
    # Monitoring
    log_requests: bool = False
    enable_metrics: bool = True


@dataclass
class SecurityConfig:
    """🔐 Configuration sécurité"""
    # API Keys
    secret_key: str = "your-secret-key-change-in-production"
    api_key_header: str = "X-API-Key"
    
    # CORS
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = field(default_factory=lambda: ["*"])
    cors_allow_headers: List[str] = field(default_factory=lambda: ["*"])
    
    # Rate Limiting
    enable_rate_limiting: bool = True
    rate_limit_requests_per_minute: int = 100
    rate_limit_burst: int = 20
    
    # Headers sécurité
    security_headers: Dict[str, str] = field(default_factory=lambda: {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    })
    
    # Validation
    max_request_size_mb: int = 10
    request_timeout_seconds: int = 30


@dataclass
class PerformanceConfig:
    """⚡ Configuration performance"""
    # Workers
    worker_count: int = 4
    worker_connections: int = 1000
    
    # Batch Processing
    default_batch_size: int = 50
    max_batch_size: int = 200
    max_concurrent_batches: int = 10
    
    # Caching
    cache_enabled: bool = True
    cache_default_ttl: int = 3600
    cache_max_size_mb: int = 512
    
    # Timeouts
    api_timeout: int = 30
    database_timeout: int = 60
    external_api_timeout: int = 15
    
    # Circuit Breaker
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: int = 60
    
    # Resource Limits
    max_memory_usage_mb: int = 2048
    max_cpu_usage_percent: int = 80


@dataclass
class MonitoringConfig:
    """📊 Configuration monitoring"""
    # Metrics
    enable_prometheus: bool = True
    prometheus_port: int = 8090
    metrics_retention_hours: int = 24
    
    # Health Checks
    enable_health_checks: bool = True
    health_check_interval: int = 60
    
    # System Monitoring
    enable_system_monitoring: bool = True
    system_monitoring_interval: int = 30
    
    # Alerting
    enable_alerting: bool = True
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "cpu_usage_percent": 85.0,
        "memory_usage_percent": 90.0,
        "disk_usage_percent": 85.0,
        "error_rate_percent": 5.0,
        "response_time_ms": 2000.0
    })
    
    # External Monitoring
    sentry_dsn: Optional[str] = None
    datadog_api_key: Optional[str] = None
    enable_external_monitoring: bool = False


@dataclass
class LoggingConfig:
    """📝 Configuration logging"""
    # Niveau global
    log_level: LogLevel = LogLevel.INFO
    
    # Format
    enable_json_logging: bool = True
    enable_structured_logging: bool = True
    
    # Fichiers
    enable_file_logging: bool = True
    log_file_path: str = "/var/log/nextvision/app.log"
    max_file_size_mb: int = 100
    backup_count: int = 5
    
    # Niveaux par composant
    component_log_levels: Dict[str, str] = field(default_factory=lambda: {
        "nextvision.api": "INFO",
        "nextvision.matching": "INFO",
        "nextvision.cache": "WARNING",
        "nextvision.database": "WARNING",
        "nextvision.google_maps": "INFO",
        "nextvision.monitoring": "WARNING",
        "uvicorn": "WARNING",
        "fastapi": "INFO"
    })
    
    # Request logging
    log_requests: bool = True
    log_request_body: bool = False  # Attention aux données sensibles
    log_response_body: bool = False
    
    # Performance logging
    log_slow_queries: bool = True
    slow_query_threshold_ms: int = 1000
    log_performance_metrics: bool = True


@dataclass
class BaseConfig:
    """⚙️ Configuration de base"""
    # Environnement
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    
    # Application
    app_name: str = "Nextvision"
    app_version: str = "2.0.0"
    api_prefix: str = "/api"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # Composants
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    google_maps: GoogleMapsConfig = field(default_factory=GoogleMapsConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Feature flags
    features: Dict[str, bool] = field(default_factory=lambda: {
        "adaptive_weighting": True,
        "google_maps_intelligence": True,
        "batch_processing": True,
        "caching": True,
        "retry_mechanisms": True,
        "health_monitoring": True,
        "structured_logging": True,
        "performance_optimization": True
    })
    
    def is_production(self) -> bool:
        """🏭 Vérifie si environnement de production"""
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """🛠️ Vérifie si environnement de développement"""
        return self.environment == Environment.DEVELOPMENT
    
    def get_database_url(self) -> str:
        """🔗 URL de base de données"""
        return self.database.get_connection_string()
    
    def get_redis_url(self) -> str:
        """🔗 URL Redis"""
        return self.redis.get_connection_url()


class DevelopmentConfig(BaseConfig):
    """🛠️ Configuration développement"""
    
    def __init__(self):
        super().__init__()
        self.environment = Environment.DEVELOPMENT
        self.debug = True
        self.reload = True
        
        # Base de données locale
        self.database.host = "localhost"
        self.database.database = "nextvision_dev"
        self.database.echo_queries = True
        self.database.min_pool_size = 2
        self.database.max_pool_size = 10
        
        # Redis local
        self.redis.host = "localhost"
        self.redis.database = 1  # DB différente
        
        # Google Maps en mode test
        self.google_maps.log_requests = True
        self.google_maps.enable_fallback_mode = True
        
        # Sécurité assouplie
        self.security.enable_rate_limiting = False
        self.security.cors_origins = ["http://localhost:3000", "http://localhost:8080"]
        
        # Performance relâchée
        self.performance.worker_count = 1
        self.performance.cache_enabled = True
        
        # Monitoring local
        self.monitoring.enable_prometheus = True
        self.monitoring.prometheus_port = 8090
        self.monitoring.enable_external_monitoring = False
        
        # Logs verbeux
        self.logging.log_level = LogLevel.DEBUG
        self.logging.enable_json_logging = False  # Plus lisible en dev
        self.logging.enable_file_logging = False
        self.logging.log_requests = True
        self.logging.log_performance_metrics = True


class TestingConfig(BaseConfig):
    """🧪 Configuration tests"""
    
    def __init__(self):
        super().__init__()
        self.environment = Environment.TESTING
        self.debug = False
        self.reload = False
        
        # Base de données test
        self.database.host = "localhost"
        self.database.database = "nextvision_test"
        self.database.echo_queries = False
        self.database.min_pool_size = 1
        self.database.max_pool_size = 5
        
        # Redis test
        self.redis.host = "localhost"
        self.redis.database = 2  # DB test
        
        # Google Maps mock
        self.google_maps.api_key = "TEST_API_KEY"
        self.google_maps.enable_fallback_mode = True
        self.google_maps.log_requests = False
        
        # Sécurité minimale
        self.security.enable_rate_limiting = False
        self.security.cors_origins = ["*"]
        
        # Performance basique
        self.performance.worker_count = 1
        self.performance.cache_enabled = False  # Tests isolés
        self.performance.default_batch_size = 10
        
        # Monitoring désactivé
        self.monitoring.enable_prometheus = False
        self.monitoring.enable_health_checks = False
        self.monitoring.enable_system_monitoring = False
        self.monitoring.enable_alerting = False
        
        # Logs minimaux
        self.logging.log_level = LogLevel.WARNING
        self.logging.enable_json_logging = False
        self.logging.enable_file_logging = False
        self.logging.log_requests = False


class ProductionConfig(BaseConfig):
    """🏭 Configuration production"""
    
    def __init__(self):
        super().__init__()
        self.environment = Environment.PRODUCTION
        self.debug = False
        self.reload = False
        
        # Base de données production
        self.database.host = os.getenv("DB_HOST", "localhost")
        self.database.port = int(os.getenv("DB_PORT", "5432"))
        self.database.database = os.getenv("DB_NAME", "nextvision_prod")
        self.database.username = os.getenv("DB_USER", "nextvision_user")
        self.database.password = os.getenv("DB_PASSWORD", "")
        self.database.ssl_enabled = True
        self.database.echo_queries = False
        self.database.min_pool_size = 10
        self.database.max_pool_size = 50
        self.database.pool_timeout = 30
        
        # Redis production
        self.redis.host = os.getenv("REDIS_HOST", "localhost")
        self.redis.port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis.password = os.getenv("REDIS_PASSWORD")
        self.redis.database = 0
        self.redis.max_connections = 100
        
        # Google Maps production
        self.google_maps.api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
        self.google_maps.daily_request_limit = 100000
        self.google_maps.enable_memory_cache = True
        self.google_maps.enable_redis_cache = True
        self.google_maps.log_requests = False
        
        # Sécurité renforcée
        self.security.secret_key = os.getenv("SECRET_KEY", "")
        self.security.cors_origins = os.getenv("CORS_ORIGINS", "").split(",")
        self.security.enable_rate_limiting = True
        self.security.rate_limit_requests_per_minute = 1000
        self.security.max_request_size_mb = 50
        
        # Performance optimisée
        self.performance.worker_count = int(os.getenv("WORKER_COUNT", "8"))
        self.performance.worker_connections = 2000
        self.performance.cache_enabled = True
        self.performance.cache_max_size_mb = 2048
        self.performance.max_memory_usage_mb = 8192
        
        # Monitoring complet
        self.monitoring.enable_prometheus = True
        self.monitoring.prometheus_port = int(os.getenv("PROMETHEUS_PORT", "8090"))
        self.monitoring.enable_health_checks = True
        self.monitoring.enable_system_monitoring = True
        self.monitoring.enable_alerting = True
        self.monitoring.sentry_dsn = os.getenv("SENTRY_DSN")
        self.monitoring.enable_external_monitoring = bool(self.monitoring.sentry_dsn)
        
        # Logs production
        self.logging.log_level = LogLevel.INFO
        self.logging.enable_json_logging = True
        self.logging.enable_structured_logging = True
        self.logging.enable_file_logging = True
        self.logging.log_file_path = os.getenv("LOG_FILE_PATH", "/var/log/nextvision/app.log")
        self.logging.max_file_size_mb = 500
        self.logging.backup_count = 10
        self.logging.log_requests = True
        self.logging.log_request_body = False  # Sécurité
        
        # Validation environnement
        self._validate_production_config()
    
    def _validate_production_config(self):
        """✅ Validation configuration production"""
        required_env_vars = [
            "DB_PASSWORD", "SECRET_KEY", "GOOGLE_MAPS_API_KEY"
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(
                f"Configuration production incomplète. "
                f"Variables manquantes: {', '.join(missing_vars)}"
            )
        
        # Validation sécurité
        if self.security.secret_key == "your-secret-key-change-in-production":
            raise ValueError("SECRET_KEY par défaut détectée en production !")
        
        if len(self.security.secret_key) < 32:
            raise ValueError("SECRET_KEY trop courte (minimum 32 caractères)")
        
        if not self.database.password:
            raise ValueError("Mot de passe base de données requis en production")


class ConfigManager:
    """🎛️ Gestionnaire de configuration central"""
    
    def __init__(self):
        self.current_config: Optional[BaseConfig] = None
        self._config_cache: Dict[Environment, BaseConfig] = {}
    
    def get_config(self, environment: Optional[Environment] = None) -> BaseConfig:
        """📋 Obtient la configuration pour un environnement"""
        if environment is None:
            environment = self._detect_environment()
        
        # Cache de configuration
        if environment in self._config_cache:
            return self._config_cache[environment]
        
        # Création de la configuration
        if environment == Environment.PRODUCTION:
            config = ProductionConfig()
        elif environment == Environment.TESTING:
            config = TestingConfig()
        else:
            config = DevelopmentConfig()
        
        # Application des overrides depuis l'environnement
        self._apply_environment_overrides(config)
        
        # Cache et retour
        self._config_cache[environment] = config
        self.current_config = config
        
        return config
    
    def _detect_environment(self) -> Environment:
        """🔍 Détection automatique de l'environnement"""
        env_str = os.getenv("NEXTVISION_ENV", "development").lower()
        
        try:
            return Environment(env_str)
        except ValueError:
            logging.warning(f"Environnement inconnu '{env_str}', utilisation de development")
            return Environment.DEVELOPMENT
    
    def _apply_environment_overrides(self, config: BaseConfig):
        """🔧 Application des overrides depuis les variables d'environnement"""
        # Host/Port
        if os.getenv("HOST"):
            config.host = os.getenv("HOST")
        if os.getenv("PORT"):
            config.port = int(os.getenv("PORT"))
        
        # Debug mode
        if os.getenv("DEBUG"):
            config.debug = os.getenv("DEBUG").lower() in ("true", "1", "on")
        
        # Log level
        if os.getenv("LOG_LEVEL"):
            try:
                config.logging.log_level = LogLevel(os.getenv("LOG_LEVEL").upper())
            except ValueError:
                logging.warning(f"Niveau de log invalide: {os.getenv('LOG_LEVEL')}")
        
        # Worker count
        if os.getenv("WORKER_COUNT"):
            config.performance.worker_count = int(os.getenv("WORKER_COUNT"))
        
        # Feature flags depuis env
        for feature, default_value in config.features.items():
            env_var = f"FEATURE_{feature.upper()}"
            if os.getenv(env_var):
                config.features[feature] = os.getenv(env_var).lower() in ("true", "1", "on")
    
    def load_from_file(self, config_path: str) -> BaseConfig:
        """📁 Chargement depuis fichier JSON/YAML"""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Fichier de configuration non trouvé: {config_path}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.suffix.lower() == '.json':
                    config_data = json.load(f)
                elif config_file.suffix.lower() in ('.yaml', '.yml'):
                    import yaml
                    config_data = yaml.safe_load(f)
                else:
                    raise ValueError(f"Format de fichier non supporté: {config_file.suffix}")
        
        except Exception as e:
            raise ValueError(f"Erreur lecture fichier de configuration: {e}")
        
        # Application de la configuration
        environment = Environment(config_data.get("environment", "development"))
        config = self.get_config(environment)
        
        # Override avec les valeurs du fichier
        self._apply_config_data(config, config_data)
        
        return config
    
    def _apply_config_data(self, config: BaseConfig, config_data: Dict[str, Any]):
        """📝 Application des données de configuration"""
        # Implementation simplifiée - en production, utiliser une librairie comme Pydantic
        for section, values in config_data.items():
            if hasattr(config, section) and isinstance(values, dict):
                config_section = getattr(config, section)
                for key, value in values.items():
                    if hasattr(config_section, key):
                        setattr(config_section, key, value)
    
    def export_config(self, config: BaseConfig, format: str = "json") -> str:
        """💾 Export de la configuration"""
        config_dict = self._config_to_dict(config)
        
        if format.lower() == "json":
            return json.dumps(config_dict, indent=2, default=str)
        elif format.lower() in ("yaml", "yml"):
            import yaml
            return yaml.dump(config_dict, default_flow_style=False)
        else:
            raise ValueError(f"Format d'export non supporté: {format}")
    
    def _config_to_dict(self, config: BaseConfig) -> Dict[str, Any]:
        """📋 Conversion configuration en dictionnaire"""
        # Implémentation simplifiée
        result = {}
        
        for attr_name in dir(config):
            if not attr_name.startswith('_') and not callable(getattr(config, attr_name)):
                attr_value = getattr(config, attr_name)
                
                if hasattr(attr_value, '__dict__'):  # Objet dataclass
                    result[attr_name] = {}
                    for sub_attr in dir(attr_value):
                        if not sub_attr.startswith('_') and not callable(getattr(attr_value, sub_attr)):
                            sub_value = getattr(attr_value, sub_attr)
                            if isinstance(sub_value, Enum):
                                result[attr_name][sub_attr] = sub_value.value
                            else:
                                result[attr_name][sub_attr] = sub_value
                elif isinstance(attr_value, Enum):
                    result[attr_name] = attr_value.value
                else:
                    result[attr_name] = attr_value
        
        return result
    
    def validate_config(self, config: BaseConfig) -> List[str]:
        """✅ Validation complète de la configuration"""
        issues = []
        
        # Validation base de données
        if not config.database.host:
            issues.append("Host de base de données manquant")
        if not config.database.username:
            issues.append("Nom d'utilisateur base de données manquant")
        
        # Validation Redis
        if not config.redis.host:
            issues.append("Host Redis manquant")
        
        # Validation Google Maps
        if config.google_maps.api_key == "YOUR_API_KEY":
            issues.append("Clé API Google Maps par défaut")
        
        # Validation sécurité
        if config.security.secret_key == "your-secret-key-change-in-production":
            issues.append("Clé secrète par défaut")
        
        # Validation production spécifique
        if config.is_production():
            if config.debug:
                issues.append("Mode debug activé en production")
            if not config.database.ssl_enabled:
                issues.append("SSL base de données désactivé en production")
            if "*" in config.security.cors_origins:
                issues.append("CORS ouvert à tous en production")
        
        return issues


# =====================================
# 🏭 FACTORY & UTILITIES
# =====================================

# Instance globale du gestionnaire
_config_manager = ConfigManager()


def get_config(environment: Optional[Environment] = None) -> BaseConfig:
    """🏭 Factory pour obtenir la configuration"""
    return _config_manager.get_config(environment)


def get_current_config() -> Optional[BaseConfig]:
    """📋 Configuration actuellement chargée"""
    return _config_manager.current_config


def load_config_from_file(config_path: str) -> BaseConfig:
    """📁 Chargement depuis fichier"""
    return _config_manager.load_from_file(config_path)


def validate_current_config() -> List[str]:
    """✅ Validation de la configuration actuelle"""
    config = get_current_config()
    if not config:
        return ["Aucune configuration chargée"]
    
    return _config_manager.validate_config(config)


def export_current_config(format: str = "json") -> str:
    """💾 Export de la configuration actuelle"""
    config = get_current_config()
    if not config:
        raise ValueError("Aucune configuration chargée")
    
    return _config_manager.export_config(config, format)


# =====================================
# 🔍 CONFIGURATION HEALTH CHECK
# =====================================

def health_check_config() -> Dict[str, Any]:
    """🏥 Vérification santé de la configuration"""
    config = get_current_config()
    
    if not config:
        return {
            "status": "error",
            "message": "No configuration loaded"
        }
    
    # Validation
    issues = _config_manager.validate_config(config)
    
    # Tests de connectivité
    connectivity_tests = {
        "database": test_database_connectivity(config.database),
        "redis": test_redis_connectivity(config.redis)
    }
    
    # Résumé
    return {
        "status": "healthy" if not issues else "issues_found",
        "environment": config.environment.value,
        "validation_issues": issues,
        "connectivity_tests": connectivity_tests,
        "features_enabled": config.features,
        "config_summary": {
            "database_host": config.database.host,
            "redis_host": config.redis.host,
            "debug_mode": config.debug,
            "worker_count": config.performance.worker_count,
            "monitoring_enabled": config.monitoring.enable_prometheus
        }
    }


def test_database_connectivity(db_config: DatabaseConfig) -> Dict[str, Any]:
    """🗃️ Test connectivité base de données"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((db_config.host, db_config.port))
        sock.close()
        
        return {
            "status": "reachable" if result == 0 else "unreachable",
            "host": db_config.host,
            "port": db_config.port
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def test_redis_connectivity(redis_config: RedisConfig) -> Dict[str, Any]:
    """🗂️ Test connectivité Redis"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((redis_config.host, redis_config.port))
        sock.close()
        
        return {
            "status": "reachable" if result == 0 else "unreachable",
            "host": redis_config.host,
            "port": redis_config.port
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
