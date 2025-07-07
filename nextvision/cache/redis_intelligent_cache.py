"""
🗄️ Nextvision - Intelligent Redis Cache
Enterprise-grade caching with smart strategies, multi-level fallbacks

Features:
- Multi-level cache hierarchy (memory + Redis)
- Intelligent TTL policies
- Cache warming strategies
- Performance optimization
- Graceful degradation
"""

import asyncio
import json
import pickle
import time
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Callable
import logging

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    
from ..logging.structured_logging import get_structured_logger
from ..monitoring.health_metrics import MetricsCollector

logger = get_structured_logger(__name__)


class CacheStrategy(Enum):
    """🎯 Stratégies de cache intelligentes"""
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    CACHE_ASIDE = "cache_aside"
    REFRESH_AHEAD = "refresh_ahead"
    TTL_BASED = "ttl_based"


class TTLPolicy(Enum):
    """⏰ Politiques de TTL"""
    SHORT = 300      # 5 minutes
    MEDIUM = 1800    # 30 minutes
    LONG = 3600      # 1 hour
    VERY_LONG = 21600 # 6 hours
    PERSISTENT = 86400 # 24 hours


@dataclass
class CacheKey:
    """🔑 Clé de cache structurée"""
    namespace: str
    identifier: str
    version: str = "v1"
    params_hash: Optional[str] = None
    
    def to_string(self) -> str:
        """Génère la clé Redis"""
        parts = ["nextvision", self.namespace, self.version, self.identifier]
        if self.params_hash:
            parts.append(self.params_hash)
        return ":".join(parts)
    
    @classmethod
    def generate_params_hash(cls, params: Dict[str, Any]) -> str:
        """Génère un hash des paramètres"""
        # Sérialisation déterministe pour hash consistant
        params_str = json.dumps(params, sort_keys=True, default=str)
        return hashlib.md5(params_str.encode()).hexdigest()[:8]


@dataclass
class CacheStats:
    """📊 Statistiques de cache"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    total_size_bytes: int = 0
    average_access_time_ms: float = 0.0
    hit_rate_percent: float = 0.0
    
    def update_hit_rate(self):
        """Met à jour le taux de hit"""
        total = self.hits + self.misses
        if total > 0:
            self.hit_rate_percent = (self.hits / total) * 100


class MemoryCache:
    """💾 Cache en mémoire local (niveau 1)"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
        self.max_size = max_size
        
    async def get(self, key: str) -> Optional[Any]:
        """Récupère depuis le cache mémoire"""
        if key in self.cache:
            entry = self.cache[key]
            # Vérifier expiration
            if entry["expires_at"] > time.time():
                self.access_times[key] = time.time()
                return entry["value"]
            else:
                # Expiration
                await self.delete(key)
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        """Stocke dans le cache mémoire"""
        # Vérifier taille max
        if len(self.cache) >= self.max_size:
            await self._evict_oldest()
            
        self.cache[key] = {
            "value": value,
            "created_at": time.time(),
            "expires_at": time.time() + ttl
        }
        self.access_times[key] = time.time()
    
    async def delete(self, key: str):
        """Supprime du cache mémoire"""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
    
    async def _evict_oldest(self):
        """Éviction LRU"""
        if not self.access_times:
            return
            
        oldest_key = min(self.access_times.items(), key=lambda x: x[1])[0]
        await self.delete(oldest_key)
    
    def get_size(self) -> int:
        """Taille actuelle du cache"""
        return len(self.cache)


class IntelligentRedisCache:
    """🧠 Cache Redis intelligent avec stratégies avancées"""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        default_ttl: int = TTLPolicy.MEDIUM.value,
        enable_memory_cache: bool = True,
        memory_cache_size: int = 1000,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.redis_client: Optional[redis.Redis] = None
        self.is_connected = False
        
        # Cache mémoire niveau 1
        self.memory_cache = MemoryCache(memory_cache_size) if enable_memory_cache else None
        
        # Statistiques
        self.stats = CacheStats()
        self.metrics = metrics_collector
        
        # Configuration par namespace
        self.namespace_configs = self._setup_namespace_configs()
        
        # Cache warming
        self.warming_tasks: Dict[str, asyncio.Task] = {}
    
    def _setup_namespace_configs(self) -> Dict[str, Dict]:
        """🔧 Configuration par namespace"""
        return {
            "geocoding": {
                "ttl": TTLPolicy.VERY_LONG.value,  # 6h pour géocodage
                "strategy": CacheStrategy.CACHE_ASIDE,
                "warm_on_startup": True
            },
            "transport": {
                "ttl": TTLPolicy.LONG.value,  # 1h pour calculs transport
                "strategy": CacheStrategy.TTL_BASED,
                "warm_on_startup": False
            },
            "matching": {
                "ttl": TTLPolicy.MEDIUM.value,  # 30min pour résultats matching
                "strategy": CacheStrategy.WRITE_THROUGH,
                "warm_on_startup": False
            },
            "bridge_data": {
                "ttl": TTLPolicy.SHORT.value,  # 5min pour données bridge
                "strategy": CacheStrategy.REFRESH_AHEAD,
                "warm_on_startup": True
            },
            "performance": {
                "ttl": TTLPolicy.SHORT.value,  # 5min pour métriques
                "strategy": CacheStrategy.WRITE_BEHIND,
                "warm_on_startup": False
            }
        }
    
    async def connect(self) -> bool:
        """🔗 Connexion à Redis avec fallback gracieux"""
        if not REDIS_AVAILABLE:
            logger.warning("📦 Redis non disponible, mode dégradé (mémoire uniquement)")
            return False
        
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=False,  # Gérer manuellement pour pickle
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connexion
            await self.redis_client.ping()
            self.is_connected = True
            
            logger.info(f"✅ Connexion Redis établie: {self.redis_url}")
            
            # Démarrer cache warming si activé
            await self._start_cache_warming()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur connexion Redis: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """💾 Déconnexion propre"""
        # Arrêter tâches warming
        for task in self.warming_tasks.values():
            task.cancel()
        
        if self.redis_client:
            await self.redis_client.close()
            self.is_connected = False
            logger.info("💾 Déconnexion Redis")
    
    async def get(
        self, 
        cache_key: Union[str, CacheKey], 
        deserialize: bool = True
    ) -> Optional[Any]:
        """📖 Récupération intelligente avec multi-niveau"""
        start_time = time.time()
        key_str = cache_key.to_string() if isinstance(cache_key, CacheKey) else cache_key
        
        try:
            # Niveau 1: Cache mémoire
            if self.memory_cache:
                memory_result = await self.memory_cache.get(key_str)
                if memory_result is not None:
                    self._record_metrics("memory_hit", time.time() - start_time)
                    self.stats.hits += 1
                    logger.debug(f"🎯 Cache memory hit: {key_str[:50]}...")
                    return memory_result
            
            # Niveau 2: Redis
            if self.is_connected and self.redis_client:
                redis_result = await self.redis_client.get(key_str)
                if redis_result is not None:
                    # Désérialiser
                    if deserialize:
                        try:
                            value = pickle.loads(redis_result)
                        except Exception:
                            # Fallback JSON
                            value = json.loads(redis_result.decode())
                    else:
                        value = redis_result
                    
                    # Mettre en cache mémoire pour accès futurs
                    if self.memory_cache:
                        namespace = self._extract_namespace(key_str)
                        ttl = self._get_memory_ttl(namespace)
                        await self.memory_cache.set(key_str, value, ttl)
                    
                    self._record_metrics("redis_hit", time.time() - start_time)
                    self.stats.hits += 1
                    logger.debug(f"🎯 Cache Redis hit: {key_str[:50]}...")
                    return value
            
            # Cache miss
            self.stats.misses += 1
            self._record_metrics("cache_miss", time.time() - start_time)
            logger.debug(f"🚫 Cache miss: {key_str[:50]}...")
            return None
            
        except Exception as e:
            self.stats.errors += 1
            logger.error(f"❌ Erreur cache get: {e}", extra={"key": key_str[:100]})
            return None
        finally:
            self.stats.update_hit_rate()
    
    async def set(
        self,
        cache_key: Union[str, CacheKey],
        value: Any,
        ttl: Optional[int] = None,
        serialize: bool = True
    ) -> bool:
        """💾 Stockage intelligent avec stratégies"""
        start_time = time.time()
        key_str = cache_key.to_string() if isinstance(cache_key, CacheKey) else cache_key
        
        # Déterminer TTL
        if ttl is None:
            namespace = self._extract_namespace(key_str)
            ttl = self._get_namespace_ttl(namespace)
        
        try:
            # Sérialisation
            if serialize:
                try:
                    serialized_value = pickle.dumps(value)
                except Exception:
                    # Fallback JSON
                    serialized_value = json.dumps(value, default=str).encode()
            else:
                serialized_value = value
            
            # Niveau 1: Cache mémoire
            if self.memory_cache:
                memory_ttl = min(ttl, 300)  # Max 5min en mémoire
                await self.memory_cache.set(key_str, value, memory_ttl)
            
            # Niveau 2: Redis
            if self.is_connected and self.redis_client:
                await self.redis_client.setex(key_str, ttl, serialized_value)
                logger.debug(f"💾 Cache set: {key_str[:50]}... (TTL: {ttl}s)")
            
            self.stats.sets += 1
            self._record_metrics("cache_set", time.time() - start_time)
            return True
            
        except Exception as e:
            self.stats.errors += 1
            logger.error(f"❌ Erreur cache set: {e}", extra={"key": key_str[:100]})
            return False
    
    async def delete(self, cache_key: Union[str, CacheKey]) -> bool:
        """🗑️ Suppression multi-niveau"""
        key_str = cache_key.to_string() if isinstance(cache_key, CacheKey) else cache_key
        
        try:
            # Supprimer des deux niveaux
            if self.memory_cache:
                await self.memory_cache.delete(key_str)
            
            if self.is_connected and self.redis_client:
                await self.redis_client.delete(key_str)
            
            self.stats.deletes += 1
            logger.debug(f"🗑️ Cache delete: {key_str[:50]}...")
            return True
            
        except Exception as e:
            self.stats.errors += 1
            logger.error(f"❌ Erreur cache delete: {e}")
            return False
    
    async def get_or_set(
        self,
        cache_key: Union[str, CacheKey],
        value_factory: Callable[[], Any],
        ttl: Optional[int] = None
    ) -> Any:
        """🔄 Pattern get-or-set optimisé"""
        # Tentative récupération
        result = await self.get(cache_key)
        if result is not None:
            return result
        
        # Générer valeur
        try:
            if asyncio.iscoroutinefunction(value_factory):
                new_value = await value_factory()
            else:
                new_value = value_factory()
            
            # Stocker
            await self.set(cache_key, new_value, ttl)
            return new_value
            
        except Exception as e:
            logger.error(f"❌ Erreur value_factory: {e}")
            raise
    
    async def invalidate_namespace(self, namespace: str) -> int:
        """🧹 Invalidation par namespace"""
        if not self.is_connected or not self.redis_client:
            return 0
        
        try:
            pattern = f"nextvision:{namespace}:*"
            keys = await self.redis_client.keys(pattern)
            
            if keys:
                deleted = await self.redis_client.delete(*keys)
                logger.info(f"🧹 Invalidation namespace {namespace}: {deleted} clés")
                return deleted
            
            return 0
            
        except Exception as e:
            logger.error(f"❌ Erreur invalidation namespace: {e}")
            return 0
    
    async def warm_cache(self, warmers: Dict[str, Callable]):
        """🔥 Réchauffage de cache"""
        logger.info(f"🔥 Démarrage cache warming: {len(warmers)} warmers")
        
        for name, warmer_func in warmers.items():
            try:
                if asyncio.iscoroutinefunction(warmer_func):
                    await warmer_func(self)
                else:
                    warmer_func(self)
                logger.info(f"✅ Cache warmer '{name}' terminé")
            except Exception as e:
                logger.error(f"❌ Erreur cache warmer '{name}': {e}")
    
    def _extract_namespace(self, key: str) -> str:
        """📝 Extraction du namespace depuis la clé"""
        parts = key.split(":")
        return parts[1] if len(parts) > 1 else "default"
    
    def _get_namespace_ttl(self, namespace: str) -> int:
        """⏰ TTL selon le namespace"""
        config = self.namespace_configs.get(namespace, {})
        return config.get("ttl", self.default_ttl)
    
    def _get_memory_ttl(self, namespace: str) -> int:
        """⏰ TTL mémoire selon le namespace"""
        redis_ttl = self._get_namespace_ttl(namespace)
        # TTL mémoire = min(TTL Redis, 5 minutes)
        return min(redis_ttl, 300)
    
    def _record_metrics(self, metric_type: str, duration: float):
        """📊 Enregistrement métriques"""
        if self.metrics:
            self.metrics.record_timer(f"cache_{metric_type}_time", duration)
            self.metrics.increment_counter(f"cache_{metric_type}")
    
    async def _start_cache_warming(self):
        """🔥 Démarrage automatique cache warming"""
        # Cache warming pour géocodage courant
        common_addresses = [
            "Paris, France",
            "La Défense, France", 
            "Boulogne-Billancourt, France",
            "Lyon, France",
            "Marseille, France"
        ]
        
        async def geocoding_warmer(cache_instance):
            """Warmer pour géocodage"""
            for address in common_addresses:
                cache_key = CacheKey(
                    namespace="geocoding",
                    identifier=f"address_{hashlib.md5(address.encode()).hexdigest()[:8]}"
                )
                # Pré-chauffer avec données factices si pas en cache
                if await cache_instance.get(cache_key) is None:
                    dummy_data = {
                        "address": address,
                        "coordinates": {"lat": 48.8566, "lng": 2.3522},
                        "cached_at": datetime.now().isoformat()
                    }
                    await cache_instance.set(cache_key, dummy_data)
        
        # Warmer en arrière-plan
        warming_task = asyncio.create_task(geocoding_warmer(self))
        self.warming_tasks["geocoding"] = warming_task
    
    def get_stats(self) -> Dict[str, Any]:
        """📊 Statistiques complètes"""
        self.stats.update_hit_rate()
        
        return {
            "hits": self.stats.hits,
            "misses": self.stats.misses,
            "hit_rate_percent": round(self.stats.hit_rate_percent, 2),
            "sets": self.stats.sets,
            "deletes": self.stats.deletes,
            "errors": self.stats.errors,
            "redis_connected": self.is_connected,
            "memory_cache_enabled": self.memory_cache is not None,
            "memory_cache_size": self.memory_cache.get_size() if self.memory_cache else 0,
            "namespace_configs": self.namespace_configs
        }


class CacheManager:
    """🎯 Gestionnaire principal de cache avec stratégies intelligentes"""
    
    def __init__(self, redis_cache: IntelligentRedisCache):
        self.cache = redis_cache
        self.active_strategies: Dict[str, CacheStrategy] = {}
        
    async def initialize(self) -> bool:
        """🚀 Initialisation complète"""
        success = await self.cache.connect()
        if success:
            logger.info("🎯 CacheManager initialisé avec succès")
        else:
            logger.warning("⚠️ CacheManager en mode dégradé (sans Redis)")
        return success
    
    async def geocoding_cache(
        self,
        address: str,
        geocoding_func: Callable,
        force_refresh: bool = False
    ) -> Any:
        """🗺️ Cache spécialisé géocodage"""
        cache_key = CacheKey(
            namespace="geocoding",
            identifier=f"addr_{hashlib.md5(address.encode()).hexdigest()[:12]}",
            params_hash=CacheKey.generate_params_hash({"address": address})
        )
        
        if not force_refresh:
            result = await self.cache.get(cache_key)
            if result is not None:
                logger.debug(f"🎯 Géocodage depuis cache: {address}")
                return result
        
        # Appel API et mise en cache
        try:
            result = await geocoding_func(address)
            await self.cache.set(cache_key, result, TTLPolicy.VERY_LONG.value)
            logger.debug(f"💾 Géocodage mis en cache: {address}")
            return result
        except Exception as e:
            logger.error(f"❌ Erreur géocodage: {e}")
            raise
    
    async def transport_cache(
        self,
        origin: str,
        destination: str,
        mode: str,
        transport_func: Callable,
        context: Dict[str, Any] = None
    ) -> Any:
        """🚗 Cache spécialisé transport"""
        context = context or {}
        cache_key = CacheKey(
            namespace="transport",
            identifier=f"{mode}_{hashlib.md5(f'{origin}_{destination}'.encode()).hexdigest()[:8]}",
            params_hash=CacheKey.generate_params_hash({
                "origin": origin,
                "destination": destination,
                "mode": mode,
                **context
            })
        )
        
        return await self.cache.get_or_set(
            cache_key,
            lambda: transport_func(origin, destination, mode, **context),
            TTLPolicy.LONG.value
        )
    
    async def matching_cache(
        self,
        candidate_id: str,
        job_id: str,
        matching_func: Callable,
        context: Dict[str, Any] = None
    ) -> Any:
        """🎯 Cache spécialisé matching"""
        context = context or {}
        cache_key = CacheKey(
            namespace="matching",
            identifier=f"c{candidate_id}_j{job_id}",
            params_hash=CacheKey.generate_params_hash(context)
        )
        
        return await self.cache.get_or_set(
            cache_key,
            lambda: matching_func(candidate_id, job_id, **context),
            TTLPolicy.MEDIUM.value
        )
    
    async def performance_cache(
        self,
        metric_name: str,
        calculation_func: Callable,
        ttl: int = TTLPolicy.SHORT.value
    ) -> Any:
        """📊 Cache spécialisé métriques performance"""
        cache_key = CacheKey(
            namespace="performance",
            identifier=f"metric_{metric_name}",
            params_hash=str(int(time.time() // ttl))  # Bucket temporel
        )
        
        return await self.cache.get_or_set(
            cache_key,
            calculation_func,
            ttl
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """❤️ Vérification santé du cache"""
        health = {
            "status": "healthy",
            "redis_connected": self.cache.is_connected,
            "memory_cache_enabled": self.cache.memory_cache is not None
        }
        
        # Test fonctionnel
        try:
            test_key = CacheKey(namespace="health", identifier="test")
            test_value = {"timestamp": time.time(), "test": True}
            
            await self.cache.set(test_key, test_value, 60)
            retrieved = await self.cache.get(test_key)
            
            if retrieved and retrieved.get("test") == True:
                health["functional_test"] = "pass"
            else:
                health["functional_test"] = "fail"
                health["status"] = "degraded"
                
            await self.cache.delete(test_key)
            
        except Exception as e:
            health["functional_test"] = "error"
            health["status"] = "unhealthy"
            health["error"] = str(e)
        
        # Statistiques
        health["stats"] = self.cache.get_stats()
        
        return health
    
    async def cleanup(self):
        """🧹 Nettoyage et déconnexion"""
        await self.cache.disconnect()
        logger.info("🧹 CacheManager nettoyé")


# =====================================
# 🎯 FACTORY & CONFIGURATION
# =====================================

def create_cache_manager(
    redis_url: str = "redis://localhost:6379",
    enable_memory_cache: bool = True,
    metrics_collector: Optional[MetricsCollector] = None
) -> CacheManager:
    """🏭 Factory pour créer un gestionnaire de cache"""
    cache = IntelligentRedisCache(
        redis_url=redis_url,
        enable_memory_cache=enable_memory_cache,
        metrics_collector=metrics_collector
    )
    
    return CacheManager(cache)
