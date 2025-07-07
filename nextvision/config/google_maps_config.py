"""
🔧 Nextvision - Configuration Google Maps Production
Configuration sécurisée et optimisée pour l'API Google Maps

Author: NEXTEN Team
Version: 2.0.0 (Prompt 2)
Integration: Google Maps API + Redis Cache + Rate Limiting
"""

import os
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum

class Environment(str, Enum):
    """🌍 Environnements d'exécution"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class CacheBackend(str, Enum):
    """💾 Types de cache supportés"""
    REDIS = "redis"
    MEMORY = "memory"
    DISABLED = "disabled"

class GoogleMapsConfig(BaseModel):
    """⚙️ Configuration Google Maps API"""
    
    # API Keys Management
    api_key: str = Field(description="Google Maps API Key")
    api_key_backup: Optional[str] = Field(None, description="Backup API Key")
    
    # Rate Limiting
    requests_per_second: int = Field(default=50, description="Requêtes par seconde max")
    requests_per_day: int = Field(default=25000, description="Requêtes par jour max")
    burst_limit: int = Field(default=100, description="Limite de rafales")
    
    # Timeout Configuration
    request_timeout_seconds: int = Field(default=10, description="Timeout requête")
    retry_attempts: int = Field(default=3, description="Tentatives de retry")
    retry_backoff_factor: float = Field(default=2.0, description="Facteur backoff exponentiel")
    
    # Regional Settings
    language: str = Field(default="fr", description="Langue par défaut")
    region: str = Field(default="FR", description="Région par défaut")
    
    # Performance Optimizations
    batch_size: int = Field(default=25, description="Taille des batchs")
    enable_compression: bool = Field(default=True, description="Compression des réponses")
    
    @validator('api_key')
    def validate_api_key(cls, v):
        if not v or len(v) < 30:
            raise ValueError("API Key Google Maps invalide")
        return v
    
    @validator('requests_per_second')
    def validate_rate_limit(cls, v):
        if v > 300:  # Limite raisonnable
            raise ValueError("Rate limit trop élevé pour Google Maps")
        return v

class CacheConfig(BaseModel):
    """💾 Configuration du cache"""
    
    backend: CacheBackend = Field(default=CacheBackend.REDIS, description="Type de cache")
    
    # Redis Configuration
    redis_host: str = Field(default="localhost", description="Host Redis")
    redis_port: int = Field(default=6379, description="Port Redis")
    redis_db: int = Field(default=0, description="Base Redis")
    redis_password: Optional[str] = Field(None, description="Mot de passe Redis")
    redis_ssl: bool = Field(default=False, description="SSL Redis")
    
    # TTL Configuration (en secondes)
    geocoding_ttl: int = Field(default=30*24*3600, description="TTL géocodage (30 jours)")
    directions_ttl: int = Field(default=3600, description="TTL directions (1h)")
    peak_directions_ttl: int = Field(default=1800, description="TTL directions pointe (30min)")
    distance_matrix_ttl: int = Field(default=7200, description="TTL matrix (2h)")
    
    # Memory Cache (fallback)
    max_memory_entries: int = Field(default=1000, description="Entrées max en mémoire")
    memory_cleanup_interval: int = Field(default=300, description="Interval nettoyage (5min)")
    
    @validator('backend')
    def validate_backend(cls, v):
        return v

class FallbackConfig(BaseModel):
    """🔄 Configuration de fallback en cas d'indisponibilité"""
    
    enable_fallback: bool = Field(default=True, description="Activer fallback")
    
    # Distance approximative (facteur vol d'oiseau)
    crow_flies_factor: float = Field(default=1.4, description="Facteur distance vol d'oiseau")
    
    # Vitesses moyennes approximatives (km/h)
    average_speeds: Dict[str, int] = Field(
        default={
            "driving": 40,
            "transit": 25, 
            "walking": 5,
            "bicycling": 15
        },
        description="Vitesses moyennes par mode"
    )
    
    # Base de données pré-calculées (optionnel)
    precomputed_routes_file: Optional[str] = Field(None, description="Fichier routes précalculées")
    
    # Notifications admin
    notify_on_fallback: bool = Field(default=True, description="Notifier en cas de fallback")
    admin_email: Optional[str] = Field(None, description="Email admin pour notifications")

class MonitoringConfig(BaseModel):
    """📊 Configuration monitoring et métriques"""
    
    enable_monitoring: bool = Field(default=True, description="Activer monitoring")
    
    # Seuils d'alerte
    latency_alert_ms: int = Field(default=500, description="Alerte latence (ms)")
    error_rate_alert_percent: float = Field(default=5.0, description="Alerte taux erreur (%)")
    quota_alert_percent: float = Field(default=80.0, description="Alerte quota (%)")
    
    # Métriques
    track_cache_hit_rate: bool = Field(default=True, description="Tracker cache hit rate")
    track_response_times: bool = Field(default=True, description="Tracker temps réponse")
    track_error_details: bool = Field(default=True, description="Tracker détails erreurs")
    
    # Export des métriques
    metrics_export_interval: int = Field(default=60, description="Interval export métriques (s)")
    metrics_retention_days: int = Field(default=30, description="Rétention métriques (jours)")

class TransportConfig(BaseModel):
    """🚗 Configuration spécifique au transport"""
    
    # Modes supportés par défaut
    default_modes: List[str] = Field(
        default=["driving", "transit", "walking", "bicycling"],
        description="Modes par défaut"
    )
    
    # Paramètres heures de pointe
    peak_hours_morning: List[int] = Field(default=[7, 8, 9], description="Heures pointe matin")
    peak_hours_evening: List[int] = Field(default=[17, 18, 19], description="Heures pointe soir")
    
    # Contraintes par défaut
    default_max_duration_minutes: Dict[str, int] = Field(
        default={
            "driving": 30,
            "transit": 45,
            "walking": 20,
            "bicycling": 25
        },
        description="Durées max par défaut"
    )
    
    # Coûts estimés
    cost_estimates: Dict[str, float] = Field(
        default={
            "transit_ticket": 1.90,  # Prix ticket Paris
            "driving_cost_per_km": 0.60,  # Essence + usure
            "parking_cost_per_hour": 3.00,  # Stationnement Paris
            "bike_maintenance_per_km": 0.05  # Entretien vélo
        },
        description="Coûts estimés"
    )
    
    # Scoring qualité
    quality_weights: Dict[str, float] = Field(
        default={
            "duration": 0.4,
            "transfers": 0.3,
            "comfort": 0.2,
            "reliability": 0.1
        },
        description="Poids scoring qualité"
    )

class GoogleMapsProductionConfig(BaseModel):
    """🏭 Configuration complète pour production"""
    
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=False, description="Mode debug")
    
    # Configurations modules
    google_maps: GoogleMapsConfig
    cache: CacheConfig
    fallback: FallbackConfig
    monitoring: MonitoringConfig
    transport: TransportConfig
    
    # Sécurité
    enable_request_validation: bool = Field(default=True, description="Validation requêtes")
    enable_response_sanitization: bool = Field(default=True, description="Sanitisation réponses")
    log_sensitive_data: bool = Field(default=False, description="Logger données sensibles")
    
    class Config:
        env_prefix = "NEXTVISION_GMAPS_"
        case_sensitive = False

def load_config_from_env() -> GoogleMapsProductionConfig:
    """🔧 Charge la configuration depuis les variables d'environnement"""
    
    # Google Maps API Config
    google_maps_config = GoogleMapsConfig(
        api_key=os.getenv("GOOGLE_MAPS_API_KEY", ""),
        api_key_backup=os.getenv("GOOGLE_MAPS_API_KEY_BACKUP"),
        requests_per_second=int(os.getenv("GOOGLE_MAPS_RPS", "50")),
        requests_per_day=int(os.getenv("GOOGLE_MAPS_RPD", "25000")),
        language=os.getenv("GOOGLE_MAPS_LANGUAGE", "fr"),
        region=os.getenv("GOOGLE_MAPS_REGION", "FR")
    )
    
    # Cache Config
    cache_config = CacheConfig(
        backend=CacheBackend(os.getenv("CACHE_BACKEND", "redis")),
        redis_host=os.getenv("REDIS_HOST", "localhost"),
        redis_port=int(os.getenv("REDIS_PORT", "6379")),
        redis_password=os.getenv("REDIS_PASSWORD"),
        geocoding_ttl=int(os.getenv("CACHE_GEOCODING_TTL", str(30*24*3600))),
        directions_ttl=int(os.getenv("CACHE_DIRECTIONS_TTL", "3600"))
    )
    
    # Fallback Config
    fallback_config = FallbackConfig(
        enable_fallback=os.getenv("ENABLE_FALLBACK", "true").lower() == "true",
        notify_on_fallback=os.getenv("NOTIFY_ON_FALLBACK", "true").lower() == "true",
        admin_email=os.getenv("ADMIN_EMAIL")
    )
    
    # Monitoring Config
    monitoring_config = MonitoringConfig(
        enable_monitoring=os.getenv("ENABLE_MONITORING", "true").lower() == "true",
        latency_alert_ms=int(os.getenv("LATENCY_ALERT_MS", "500")),
        error_rate_alert_percent=float(os.getenv("ERROR_RATE_ALERT", "5.0"))
    )
    
    # Transport Config
    transport_config = TransportConfig()
    
    # Configuration principale
    return GoogleMapsProductionConfig(
        environment=Environment(os.getenv("ENVIRONMENT", "development")),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        google_maps=google_maps_config,
        cache=cache_config,
        fallback=fallback_config,
        monitoring=monitoring_config,
        transport=transport_config
    )

def get_config_by_environment(env: Environment) -> GoogleMapsProductionConfig:
    """🌍 Configuration optimisée par environnement"""
    
    base_config = load_config_from_env()
    base_config.environment = env
    
    if env == Environment.PRODUCTION:
        # Configuration production optimisée
        base_config.debug = False
        base_config.google_maps.requests_per_second = 100
        base_config.google_maps.requests_per_day = 50000
        base_config.cache.backend = CacheBackend.REDIS
        base_config.monitoring.enable_monitoring = True
        base_config.log_sensitive_data = False
        
    elif env == Environment.STAGING:
        # Configuration staging
        base_config.debug = True
        base_config.google_maps.requests_per_day = 10000
        base_config.monitoring.enable_monitoring = True
        
    elif env == Environment.DEVELOPMENT:
        # Configuration développement
        base_config.debug = True
        base_config.google_maps.requests_per_day = 5000
        base_config.cache.backend = CacheBackend.MEMORY
        base_config.fallback.enable_fallback = True
        base_config.log_sensitive_data = True
        
    elif env == Environment.TESTING:
        # Configuration tests
        base_config.debug = True
        base_config.cache.backend = CacheBackend.MEMORY
        base_config.fallback.enable_fallback = False
        base_config.monitoring.enable_monitoring = False
        
    return base_config

# Instance globale de configuration
_config_instance: Optional[GoogleMapsProductionConfig] = None

def get_config() -> GoogleMapsProductionConfig:
    """🔧 Récupère l'instance de configuration (singleton)"""
    global _config_instance
    
    if _config_instance is None:
        env = Environment(os.getenv("ENVIRONMENT", "development"))
        _config_instance = get_config_by_environment(env)
    
    return _config_instance

def reset_config():
    """🔄 Reset configuration (pour les tests)"""
    global _config_instance
    _config_instance = None

# Configurations prédéfinies pour tests
TEST_CONFIG = GoogleMapsProductionConfig(
    environment=Environment.TESTING,
    debug=True,
    google_maps=GoogleMapsConfig(api_key="test_key_12345678901234567890"),
    cache=CacheConfig(backend=CacheBackend.MEMORY),
    fallback=FallbackConfig(enable_fallback=False),
    monitoring=MonitoringConfig(enable_monitoring=False),
    transport=TransportConfig()
)

DEVELOPMENT_CONFIG = GoogleMapsProductionConfig(
    environment=Environment.DEVELOPMENT,
    debug=True,
    google_maps=GoogleMapsConfig(api_key=os.getenv("GOOGLE_MAPS_API_KEY", "dev_key")),
    cache=CacheConfig(backend=CacheBackend.MEMORY),
    fallback=FallbackConfig(enable_fallback=True),
    monitoring=MonitoringConfig(enable_monitoring=True),
    transport=TransportConfig()
)

# Validation de la configuration au démarrage
def validate_production_config(config: GoogleMapsProductionConfig) -> List[str]:
    """✅ Valide la configuration pour la production"""
    
    issues = []
    
    # Validation API Key
    if not config.google_maps.api_key or len(config.google_maps.api_key) < 30:
        issues.append("Google Maps API Key invalide ou manquante")
    
    # Validation Redis en production
    if config.environment == Environment.PRODUCTION:
        if config.cache.backend != CacheBackend.REDIS:
            issues.append("Redis requis en production")
        
        if not config.monitoring.enable_monitoring:
            issues.append("Monitoring requis en production")
    
    # Validation rate limits
    if config.google_maps.requests_per_day > 100000:
        issues.append("Rate limit quotidien très élevé - vérifier le budget Google")
    
    # Validation fallback
    if config.environment == Environment.PRODUCTION and not config.fallback.enable_fallback:
        issues.append("Fallback recommandé en production")
    
    return issues

if __name__ == "__main__":
    # Test de la configuration
    config = get_config()
    print(f"🔧 Configuration chargée pour: {config.environment}")
    print(f"🗺️ Google Maps: {config.google_maps.language}/{config.google_maps.region}")
    print(f"💾 Cache: {config.cache.backend}")
    print(f"📊 Monitoring: {config.monitoring.enable_monitoring}")
    
    # Validation
    issues = validate_production_config(config)
    if issues:
        print("⚠️ Issues de configuration:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ Configuration valide")
