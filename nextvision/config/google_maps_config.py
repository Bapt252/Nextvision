"""
⚙️ Nextvision - Configuration Google Maps (Prompt 2)
Gestion sécurisée API keys, rate limiting et configuration production

Author: NEXTEN Team
Version: 2.0.0 - Google Maps Intelligence
"""

import os
import nextvision_logging as logging
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class Environment(str, Enum):
    """🌍 Environnements déploiement"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

@dataclass
class GoogleMapsConfig:
    """⚙️ Configuration Google Maps complète"""
    
    # API Configuration
    api_key: str
    api_endpoint: str = "https://maps.googleapis.com/maps/api"
    
    # Rate Limiting
    daily_request_limit: int = 25000
    requests_per_second: int = 50
    burst_limit: int = 100
    
    # Cache Configuration
    geocode_cache_duration_hours: int = 24 * 30  # 30 jours
    directions_cache_duration_hours: int = 1     # 1 heure
    enable_memory_cache: bool = True
    enable_redis_cache: bool = False
    redis_url: Optional[str] = None
    
    # Timeout Configuration
    request_timeout_seconds: int = 30
    connection_timeout_seconds: int = 10
    
    # Retry Configuration
    max_retries: int = 3
    retry_backoff_factor: float = 2.0
    retry_on_status_codes: List[int] = None
    
    # Circuit Breaker
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout_minutes: int = 5
    
    # Fallback Configuration
    enable_fallback_mode: bool = True
    fallback_coordinates: tuple = (48.8566, 2.3522)  # Paris Notre-Dame
    
    # Logging
    log_requests: bool = False
    log_cache_stats: bool = True
    
    def __post_init__(self):
        if self.retry_on_status_codes is None:
            self.retry_on_status_codes = [429, 500, 502, 503, 504]
        
        # Validation
        if not self.api_key or self.api_key.startswith("YOUR_"):
            raise ValueError(
                "Google Maps API key invalide. "
                "Configurez GOOGLE_MAPS_API_KEY dans les variables d'environnement."
            )

class GoogleMapsConfigManager:
    """📋 Gestionnaire configuration Google Maps selon environnement"""
    
    def __init__(self, environment: Environment = None):
        self.environment = environment or self._detect_environment()
        self._config_cache: Optional[GoogleMapsConfig] = None
    
    def get_config(self, force_reload: bool = False) -> GoogleMapsConfig:
        """📂 Récupère configuration selon environnement"""
        
        if self._config_cache is None or force_reload:
            self._config_cache = self._load_config()
        
        return self._config_cache
    
    def _load_config(self) -> GoogleMapsConfig:
        """🔧 Charge configuration selon environnement"""
        
        # Configuration par défaut
        base_config = {
            "api_key": self._get_api_key(),
            "log_requests": self.environment != Environment.PRODUCTION,
            "log_cache_stats": True
        }
        
        # Configurations spécifiques par environnement
        env_configs = {
            Environment.DEVELOPMENT: {
                "daily_request_limit": 1000,
                "requests_per_second": 10,
                "enable_redis_cache": False,
                "log_requests": True,
                "max_retries": 1
            },
            
            Environment.STAGING: {
                "daily_request_limit": 5000,
                "requests_per_second": 25,
                "enable_redis_cache": True,
                "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
                "log_requests": False
            },
            
            Environment.PRODUCTION: {
                "daily_request_limit": 25000,
                "requests_per_second": 50,
                "enable_redis_cache": True,
                "redis_url": os.getenv("REDIS_URL"),
                "log_requests": False,
                "request_timeout_seconds": 20,
                "max_retries": 3
            },
            
            Environment.TESTING: {
                "daily_request_limit": 100,
                "requests_per_second": 5,
                "enable_redis_cache": False,
                "enable_fallback_mode": True,
                "log_requests": True,
                "max_retries": 1
            }
        }
        
        # Fusion configuration
        config_dict = {**base_config, **env_configs.get(self.environment, {})}
        
        # Variables d'environnement optionnelles
        self._apply_env_overrides(config_dict)
        
        logger.info(f"Configuration Google Maps chargée pour {self.environment.value}")
        
        return GoogleMapsConfig(**config_dict)
    
    def _get_api_key(self) -> str:
        """🔑 Récupère API key sécurisée"""
        
        # Sources possibles par ordre de priorité
        api_key_sources = [
            os.getenv("GOOGLE_MAPS_API_KEY"),
            os.getenv("GOOGLE_API_KEY"),
            os.getenv("MAPS_API_KEY")
        ]
        
        for api_key in api_key_sources:
            if api_key and not api_key.startswith("YOUR_"):
                return api_key
        
        # Mode test avec clé factice
        if self.environment == Environment.TESTING:
            return "TEST_API_KEY_MOCK"
        
        raise ValueError(
            "Aucune clé API Google Maps trouvée. "
            "Définissez GOOGLE_MAPS_API_KEY dans les variables d'environnement."
        )
    
    def _apply_env_overrides(self, config_dict: Dict):
        """🔧 Applique surcharges variables d'environnement"""
        
        env_overrides = {
            "GOOGLE_MAPS_DAILY_LIMIT": ("daily_request_limit", int),
            "GOOGLE_MAPS_RPS_LIMIT": ("requests_per_second", int),
            "GOOGLE_MAPS_TIMEOUT": ("request_timeout_seconds", int),
            "GOOGLE_MAPS_MAX_RETRIES": ("max_retries", int),
            "GOOGLE_MAPS_ENABLE_REDIS": ("enable_redis_cache", self._str_to_bool),
            "REDIS_URL": ("redis_url", str),
            "GOOGLE_MAPS_LOG_REQUESTS": ("log_requests", self._str_to_bool)
        }
        
        for env_var, (config_key, converter) in env_overrides.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    config_dict[config_key] = converter(env_value)
                    logger.debug(f"Override {config_key} = {config_dict[config_key]} depuis {env_var}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"Erreur override {env_var}: {e}")
    
    def _detect_environment(self) -> Environment:
        """🔍 Détecte environnement automatiquement"""
        
        env_var = os.getenv("ENVIRONMENT", os.getenv("ENV", "development")).lower()
        
        env_mapping = {
            "dev": Environment.DEVELOPMENT,
            "development": Environment.DEVELOPMENT,
            "local": Environment.DEVELOPMENT,
            
            "staging": Environment.STAGING,
            "stage": Environment.STAGING,
            "preprod": Environment.STAGING,
            
            "prod": Environment.PRODUCTION,
            "production": Environment.PRODUCTION,
            
            "test": Environment.TESTING,
            "testing": Environment.TESTING,
            "tests": Environment.TESTING
        }
        
        detected_env = env_mapping.get(env_var, Environment.DEVELOPMENT)
        logger.info(f"Environnement détecté: {detected_env.value}")
        
        return detected_env
    
    @staticmethod
    def _str_to_bool(value: str) -> bool:
        """🔄 Convertit string en bool"""
        return value.lower() in ("true", "1", "yes", "on", "enabled")

class GoogleMapsSecrets:
    """🔐 Gestionnaire sécurisé des secrets Google Maps"""
    
    @staticmethod
    def rotate_api_key(new_api_key: str) -> bool:
        """🔄 Rotation API key (pour sécurité)"""
        try:
            # TODO: Implémenter rotation sécurisée
            # - Validation nouvelle clé
            # - Test connectivité
            # - Sauvegarde ancienne clé
            # - Mise à jour configuration
            
            logger.info("Rotation API key simulée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur rotation API key: {e}")
            return False
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """✅ Valide format API key Google"""
        
        if not api_key or len(api_key) < 20:
            return False
        
        # Google API keys commencent généralement par "AIza"
        if not api_key.startswith("AIza") and api_key != "TEST_API_KEY_MOCK":
            logger.warning("Format API key Google Maps inhabituel")
        
        return True
    
    @staticmethod
    def get_quota_info(api_key: str) -> Dict:
        """📊 Informations quota API (simulation)"""
        
        # TODO: Appel réel API Google pour quota
        return {
            "daily_limit": 25000,
            "daily_used": 0,
            "remaining": 25000,
            "reset_time": "00:00 UTC",
            "status": "active"
        }

# Instance globale pour faciliter l'utilisation
config_manager = GoogleMapsConfigManager()

def get_google_maps_config() -> GoogleMapsConfig:
    """🚀 Fonction utilitaire pour récupérer configuration"""
    return config_manager.get_config()

def set_environment(env: Environment):
    """🌍 Force un environnement spécifique"""
    global config_manager
    config_manager = GoogleMapsConfigManager(env)

def reload_config():
    """🔄 Force rechargement configuration"""
    global config_manager
    config_manager.get_config(force_reload=True)

# Configuration logging pour Google Maps
def setup_google_maps_logging(config: GoogleMapsConfig):
    """📝 Configure logging Google Maps"""
    
    gmaps_logger = logging.getLogger("nextvision.google_maps")
    
    if config.log_requests:
        gmaps_logger.setLevel(logging.DEBUG)
    else:
        gmaps_logger.setLevel(logging.INFO)
    
    # Handler console si pas déjà configuré
    if not gmaps_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        gmaps_logger.addHandler(handler)
    
    gmaps_logger.info(f"Logging Google Maps configuré (env: {config_manager.environment.value})")
