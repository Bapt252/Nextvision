"""
🛠️ Nextvision - Utilitaires Google Maps (Prompt 2)
Helpers, cache, métriques et fonctions utilitaires

Author: NEXTEN Team  
Version: 2.0.0 - Google Maps Intelligence
"""

import asyncio
import json
import time
import hashlib
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from functools import wraps
import aioredis
import pickle

from ..models.transport_models import GeocodeResult, TransportRoute, TravelMode

logger = logging.getLogger(__name__)

@dataclass
class CacheStats:
    """📊 Statistiques cache"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    @property
    def hit_rate_percent(self) -> float:
        return self.hit_rate * 100

class GoogleMapsCache:
    """💾 Cache intelligent multi-niveau pour Google Maps"""
    
    def __init__(self, redis_url: Optional[str] = None, enable_memory: bool = True):
        self.redis_url = redis_url
        self.enable_memory = enable_memory
        
        # Cache mémoire (Level 1)
        self._memory_cache: Dict[str, Tuple[Any, datetime]] = {}
        self._memory_cache_stats = CacheStats()
        
        # Cache Redis (Level 2) 
        self._redis_pool: Optional[aioredis.Redis] = None
        self._redis_cache_stats = CacheStats()
        
        # Configuration
        self.memory_max_size = 1000
        self.memory_ttl_seconds = 3600  # 1 heure
        self.redis_ttl_seconds = 86400   # 24 heures
        
        # Métriques
        self.total_requests = 0
        self.cache_operations = 0
    
    async def initialize(self):
        """🚀 Initialise connections cache"""
        if self.redis_url:
            try:
                self._redis_pool = aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=False  # Pour données binaires
                )
                # Test connection
                await self._redis_pool.ping()
                logger.info(f"Cache Redis connecté: {self.redis_url}")
            except Exception as e:
                logger.warning(f"Échec connexion Redis: {e} - cache mémoire uniquement")
                self._redis_pool = None
    
    async def get(self, key: str) -> Optional[Any]:
        """📤 Récupère valeur depuis cache multi-niveau"""
        self.total_requests += 1
        
        # Level 1: Mémoire
        if self.enable_memory:
            memory_result = self._get_from_memory(key)
            if memory_result is not None:
                self._memory_cache_stats.hits += 1
                logger.debug(f"Cache hit mémoire: {key}")
                return memory_result
            else:
                self._memory_cache_stats.misses += 1
        
        # Level 2: Redis
        if self._redis_pool:
            redis_result = await self._get_from_redis(key)
            if redis_result is not None:
                self._redis_cache_stats.hits += 1
                
                # Promotion vers cache mémoire
                if self.enable_memory:
                    self._set_in_memory(key, redis_result)
                
                logger.debug(f"Cache hit Redis: {key}")
                return redis_result
            else:
                self._redis_cache_stats.misses += 1
        
        return None
    
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """📥 Stocke valeur dans cache multi-niveau"""
        self.cache_operations += 1
        
        # Level 1: Mémoire
        if self.enable_memory:
            self._set_in_memory(key, value)
        
        # Level 2: Redis
        if self._redis_pool:
            await self._set_in_redis(key, value, ttl_seconds or self.redis_ttl_seconds)
    
    def _get_from_memory(self, key: str) -> Optional[Any]:
        """📤 Récupère depuis cache mémoire"""
        if key not in self._memory_cache:
            return None
        
        value, expiry = self._memory_cache[key]
        
        # Vérification expiration
        if datetime.now() > expiry:
            del self._memory_cache[key]
            return None
        
        return value
    
    def _set_in_memory(self, key: str, value: Any):
        """📥 Stocke en cache mémoire avec éviction LRU"""
        
        # Éviction si taille max atteinte
        if len(self._memory_cache) >= self.memory_max_size:
            # LRU simple: supprime le plus ancien
            oldest_key = min(
                self._memory_cache.keys(),
                key=lambda k: self._memory_cache[k][1]
            )
            del self._memory_cache[oldest_key]
            self._memory_cache_stats.evictions += 1
        
        expiry = datetime.now() + timedelta(seconds=self.memory_ttl_seconds)
        self._memory_cache[key] = (value, expiry)
        self._memory_cache_stats.size = len(self._memory_cache)
    
    async def _get_from_redis(self, key: str) -> Optional[Any]:
        """📤 Récupère depuis Redis"""
        try:
            data = await self._redis_pool.get(f"nextvision:gmaps:{key}")
            if data:
                return pickle.loads(data)
        except Exception as e:
            logger.error(f"Erreur lecture Redis {key}: {e}")
        
        return None
    
    async def _set_in_redis(self, key: str, value: Any, ttl_seconds: int):
        """📥 Stocke dans Redis"""
        try:
            serialized = pickle.dumps(value)
            await self._redis_pool.setex(
                f"nextvision:gmaps:{key}",
                ttl_seconds,
                serialized
            )
        except Exception as e:
            logger.error(f"Erreur écriture Redis {key}: {e}")
    
    async def clear(self):
        """🧹 Vide cache"""
        if self.enable_memory:
            self._memory_cache.clear()
            self._memory_cache_stats = CacheStats()
        
        if self._redis_pool:
            try:
                keys = await self._redis_pool.keys("nextvision:gmaps:*")
                if keys:
                    await self._redis_pool.delete(*keys)
            except Exception as e:
                logger.error(f"Erreur clear Redis: {e}")
    
    def get_stats(self) -> Dict:
        """📊 Statistiques cache"""
        return {
            "memory": asdict(self._memory_cache_stats),
            "redis": asdict(self._redis_cache_stats),
            "total_requests": self.total_requests,
            "cache_operations": self.cache_operations,
            "overall_hit_rate": self._calculate_overall_hit_rate()
        }
    
    def _calculate_overall_hit_rate(self) -> float:
        """📈 Taux hit global multi-niveau"""
        total_hits = self._memory_cache_stats.hits + self._redis_cache_stats.hits
        total_requests = max(self.total_requests, 1)
        return total_hits / total_requests

class GoogleMapsHelpers:
    """🛠️ Fonctions utilitaires Google Maps"""
    
    @staticmethod
    def create_cache_key(prefix: str, *args) -> str:
        """🔑 Crée clé cache sécurisée"""
        # Normalisation des arguments
        normalized_args = []
        for arg in args:
            if isinstance(arg, (dict, list)):
                normalized_args.append(json.dumps(arg, sort_keys=True))
            elif isinstance(arg, datetime):
                normalized_args.append(arg.isoformat())
            else:
                normalized_args.append(str(arg))
        
        # Hash SHA-256 pour clé courte et sécurisée
        combined = f"{prefix}:" + ":".join(normalized_args)
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    @staticmethod
    def normalize_address(address: str) -> str:
        """📍 Normalise adresse pour géocodage cohérent"""
        if not address:
            return ""
        
        # Nettoyage de base
        normalized = address.strip().lower()
        
        # Remplacements courants
        replacements = {
            "  ": " ",
            " ,": ",",
            ", ": ",",
            "avenue": "av",
            "boulevard": "bd", 
            "rue ": "r ",
            "place ": "pl "
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        return normalized
    
    @staticmethod
    def calculate_haversine_distance(
        lat1: float, lon1: float, 
        lat2: float, lon2: float
    ) -> float:
        """📏 Distance haversine en kilomètres"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Rayon terre en km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    @staticmethod
    def estimate_travel_time_simple(
        distance_km: float, 
        travel_mode: TravelMode
    ) -> int:
        """⏱️ Estimation temps trajet simple (minutes)"""
        
        # Vitesses moyennes par mode (km/h)
        speeds = {
            TravelMode.WALKING: 5,
            TravelMode.BICYCLING: 15,
            TravelMode.DRIVING: 30,    # Urbain avec trafic
            TravelMode.TRANSIT: 20     # Avec correspondances
        }
        
        speed_kmh = speeds.get(travel_mode, 20)
        time_hours = distance_km / speed_kmh
        
        return max(1, int(time_hours * 60))  # Minimum 1 minute
    
    @staticmethod
    def is_within_paris_region(lat: float, lon: float) -> bool:
        """🗼 Vérifie si coordonnées dans région parisienne"""
        
        # Bounding box approximatif Île-de-France
        return (
            48.1 <= lat <= 49.0 and
            1.4 <= lon <= 3.6
        )
    
    @staticmethod
    def format_duration_human(seconds: int) -> str:
        """⏰ Formate durée en texte lisible"""
        
        if seconds < 60:
            return f"{seconds}s"
        
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes}min"
        
        hours = minutes // 60
        remaining_minutes = minutes % 60
        
        if remaining_minutes == 0:
            return f"{hours}h"
        else:
            return f"{hours}h{remaining_minutes:02d}"
    
    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> bool:
        """✅ Valide coordonnées géographiques"""
        return (
            -90 <= lat <= 90 and
            -180 <= lon <= 180
        )
    
    @staticmethod
    def extract_city_from_address(address: str) -> Optional[str]:
        """🏙️ Extrait ville depuis adresse"""
        
        # Patterns courants français
        import re
        
        # Code postal + ville
        pattern = r'\b\d{5}\s+([A-Za-zÀ-ÿ\s-]+)'
        match = re.search(pattern, address)
        if match:
            return match.group(1).strip().title()
        
        # Recherche par mots-clés
        city_keywords = ["Paris", "Lyon", "Marseille", "Lille", "Toulouse"]
        for keyword in city_keywords:
            if keyword.lower() in address.lower():
                return keyword
        
        return None

class PerformanceMonitor:
    """📈 Monitoring performance Google Maps"""
    
    def __init__(self):
        self.metrics = {
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0,
            "timeouts": 0,
            "total_time": 0.0,
            "average_time": 0.0
        }
        
        self.start_time = time.time()
        self.operation_times: List[float] = []
    
    def record_api_call(self, duration: float, success: bool = True):
        """📊 Enregistre appel API"""
        self.metrics["api_calls"] += 1
        self.metrics["total_time"] += duration
        
        if success:
            self.operation_times.append(duration)
        else:
            self.metrics["errors"] += 1
        
        self._update_average()
    
    def record_cache_hit(self):
        """💾 Enregistre hit cache"""
        self.metrics["cache_hits"] += 1
    
    def record_cache_miss(self):
        """❌ Enregistre miss cache"""
        self.metrics["cache_misses"] += 1
    
    def record_timeout(self):
        """⏰ Enregistre timeout"""
        self.metrics["timeouts"] += 1
        self.metrics["errors"] += 1
    
    def _update_average(self):
        """📈 Met à jour temps moyen"""
        if self.operation_times:
            self.metrics["average_time"] = sum(self.operation_times) / len(self.operation_times)
    
    @property
    def cache_hit_rate(self) -> float:
        """📊 Taux de hit cache"""
        total = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        return self.metrics["cache_hits"] / total if total > 0 else 0.0
    
    @property
    def error_rate(self) -> float:
        """❌ Taux d'erreur"""
        total = self.metrics["api_calls"]
        return self.metrics["errors"] / total if total > 0 else 0.0
    
    @property
    def uptime_hours(self) -> float:
        """⏰ Uptime en heures"""
        return (time.time() - self.start_time) / 3600
    
    def get_summary(self) -> Dict:
        """📋 Résumé performance"""
        return {
            **self.metrics,
            "cache_hit_rate_percent": self.cache_hit_rate * 100,
            "error_rate_percent": self.error_rate * 100,
            "uptime_hours": self.uptime_hours,
            "requests_per_hour": self.metrics["api_calls"] / max(self.uptime_hours, 0.1)
        }

def async_retry(max_retries: int = 3, backoff_factor: float = 2.0):
    """🔄 Décorateur retry asynchrone"""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        break
                    
                    # Backoff exponentiel
                    delay = backoff_factor ** attempt
                    logger.warning(
                        f"Retry {attempt + 1}/{max_retries} pour {func.__name__} "
                        f"dans {delay}s: {e}"
                    )
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator

def timing_decorator(func):
    """⏱️ Décorateur timing pour performance"""
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"{func.__name__} terminé en {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} échoué après {duration:.3f}s: {e}")
            raise
    
    return wrapper

# Instance globale du cache
_global_cache: Optional[GoogleMapsCache] = None
_global_monitor = PerformanceMonitor()

async def get_cache() -> GoogleMapsCache:
    """🚀 Récupère instance cache globale"""
    global _global_cache
    
    if _global_cache is None:
        from ..config.google_maps_config import get_google_maps_config
        config = get_google_maps_config()
        
        _global_cache = GoogleMapsCache(
            redis_url=config.redis_url if config.enable_redis_cache else None,
            enable_memory=config.enable_memory_cache
        )
        await _global_cache.initialize()
    
    return _global_cache

def get_performance_monitor() -> PerformanceMonitor:
    """📈 Récupère monitor performance global"""
    return _global_monitor
