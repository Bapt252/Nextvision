"""
💾 Redis Intelligent Cache - Production Enterprise Grade

Cache Redis multi-niveaux optimisé pour :
• Geocoding results (24h TTL)
• Transport calculations (6h TTL) 
• Job matching results (1h TTL)
• Performance: < 0.2ms access time
• Intelligent invalidation
• Memory + Redis layers
• Compression pour gros objets

Author: NEXTEN Team - Production Robustness
Version: 1.0.0
"""

import asyncio
import hashlib
import json
import pickle
import time
import zlib
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field

import aioredis
import orjson
from redis.exceptions import ConnectionError, TimeoutError

from ..logging.structured_logging import get_structured_logger
from ..monitoring.health_metrics import HealthMetrics

logger = get_structured_logger(__name__)
health_metrics = HealthMetrics()

class CacheStrategy(Enum):
    """🎯 Stratégies de cache intelligentes"""
    MEMORY_ONLY = "memory_only"
    REDIS_ONLY = "redis_only"
    LAYERED = "layered"  # Memory L1 + Redis L2
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    READ_THROUGH = "read_through"

@dataclass
class CacheConfig:
    """⚙️ Configuration cache intelligente"""
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 20
    redis_retry_on_timeout: bool = True
    redis_socket_keepalive: bool = True
    redis_socket_keepalive_options: Dict = field(default_factory=dict)
    
    # Cache Strategy
    default_strategy: CacheStrategy = CacheStrategy.LAYERED
    
    # TTL Configuration (seconds)
    ttl_geocoding: int = 24 * 3600  # 24h
    ttl_transport: int = 6 * 3600   # 6h
    ttl_matching: int = 1 * 3600    # 1h
    ttl_default: int = 30 * 60      # 30min
    
    # Memory Cache Limits
    memory_max_size_mb: int = 256
    memory_max_items: int = 10000
    
    # Performance
    compression_threshold_bytes: int = 1024  # Compresser si > 1KB
    max_key_length: int = 250
    
    # Monitoring
    enable_stats: bool = True
    stats_window_minutes: int = 60
    
    # Failover
    fallback_to_memory: bool = True
    redis_timeout_seconds: float = 0.1  # 100ms max pour Redis

@dataclass
class CacheKey:
    """🔑 Clé de cache intelligente avec métadonnées"""
    namespace: str
    identifier: str
    version: str = "v1"
    params_hash: Optional[str] = None
    
    def __post_init__(self):
        """🔧 Validation et normalisation"""
        if self.params_hash and len(self.params_hash) > 32:
            # Hasher si trop long
            self.params_hash = hashlib.md5(self.params_hash.encode()).hexdigest()
    
    def to_redis_key(self) -> str:
        """🎯 Génère clé Redis optimisée"""
        parts = ["nextvision", self.namespace, self.version, self.identifier]
        if self.params_hash:
            parts.append(self.params_hash)
        
        key = ":".join(parts)
        
        # Limitation taille clé
        if len(key) > 250:
            # Hasher la clé complète si trop longue
            key_hash = hashlib.sha256(key.encode()).hexdigest()[:16]
            key = f"nextvision:hashed:{key_hash}"
        
        return key
    
    @classmethod
    def create_geocoding(cls, address: str) -> "CacheKey":
        """📍 Clé pour géocodage"""
        addr_hash = hashlib.md5(address.lower().strip().encode()).hexdigest()[:16]
        return cls(
            namespace="geocoding",
            identifier="address",
            params_hash=addr_hash
        )
    
    @classmethod
    def create_transport(cls, origin: str, destination: str, mode: str) -> "CacheKey":
        """🚗 Clé pour calcul transport"""
        transport_str = f"{origin}|{destination}|{mode}"
        transport_hash = hashlib.md5(transport_str.lower().encode()).hexdigest()[:16]
        return cls(
            namespace="transport",
            identifier="route",
            params_hash=transport_hash
        )
    
    @classmethod
    def create_matching(cls, candidate_id: str, job_id: str, weights_hash: str) -> "CacheKey":
        """🎯 Clé pour résultat matching"""
        match_str = f"{candidate_id}|{job_id}|{weights_hash}"
        match_hash = hashlib.md5(match_str.encode()).hexdigest()[:16]
        return cls(
            namespace="matching",
            identifier="result",
            params_hash=match_hash
        )

@dataclass
class CacheStats:
    """📊 Statistiques cache détaillées"""
    # Global Stats
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    
    # Performance Stats
    avg_get_time_ms: float = 0.0
    avg_set_time_ms: float = 0.0
    p95_get_time_ms: float = 0.0
    
    # Layer Stats
    memory_hits: int = 0
    redis_hits: int = 0
    memory_size_mb: float = 0.0
    redis_size_mb: float = 0.0
    
    # Error Stats
    redis_errors: int = 0
    memory_evictions: int = 0
    
    # Efficiency
    compression_ratio: float = 0.0
    hit_rate_percent: float = 0.0
    
    def calculate_hit_rate(self):
        """📈 Calcule le taux de hit"""
        if self.total_requests > 0:
            self.hit_rate_percent = (self.cache_hits / self.total_requests) * 100
        else:
            self.hit_rate_percent = 0.0

class IntelligentCache:
    """💾 Cache intelligent multi-niveaux Redis + Memory"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis_pool: Optional[aioredis.ConnectionPool] = None
        self.redis: Optional[aioredis.Redis] = None
        
        # Memory Cache (L1)
        self.memory_cache: Dict[str, Tuple[Any, datetime, int]] = {}  # key -> (value, expires_at, size_bytes)
        self.memory_access_times: Dict[str, datetime] = {}  # LRU tracking
        self.memory_size_bytes = 0
        
        # Statistics
        self.stats = CacheStats()
        self.performance_history: List[Dict] = []
        
        # Locks
        self._memory_lock = asyncio.Lock()
        self._redis_lock = asyncio.Lock()
        
        logger.info("💾 IntelligentCache initialized", extra={
            "strategy": config.default_strategy.value,
            "memory_max_mb": config.memory_max_size_mb,
            "redis_url": config.redis_url.split('@')[-1] if '@' in config.redis_url else config.redis_url  # Sans credentials
        })
    
    async def initialize(self):
        """🚀 Initialise les connexions Redis"""
        try:
            self.redis_pool = aioredis.ConnectionPool.from_url(
                self.config.redis_url,
                max_connections=self.config.redis_max_connections,
                retry_on_timeout=self.config.redis_retry_on_timeout,
                socket_keepalive=self.config.redis_socket_keepalive,
                socket_keepalive_options=self.config.redis_socket_keepalive_options,
                health_check_interval=30
            )
            
            self.redis = aioredis.Redis(connection_pool=self.redis_pool)
            
            # Test connexion
            await self.redis.ping()
            
            logger.info("✅ Redis connection established", extra={
                "max_connections": self.config.redis_max_connections
            })
            
        except Exception as e:
            logger.error(f"❌ Redis initialization failed: {e}", extra={
                "fallback_enabled": self.config.fallback_to_memory
            })
            
            if not self.config.fallback_to_memory:
                raise e
    
    async def get(self, key: Union[str, CacheKey], default: Any = None) -> Any:
        """🔍 Récupération intelligente avec fallback"""
        start_time = time.time()
        
        try:
            # Normalisation clé
            redis_key = key.to_redis_key() if isinstance(key, CacheKey) else key
            
            self.stats.total_requests += 1
            
            # L1: Memory Cache
            if self.config.default_strategy in [CacheStrategy.LAYERED, CacheStrategy.MEMORY_ONLY]:
                memory_result = await self._get_from_memory(redis_key)
                if memory_result is not None:
                    self.stats.cache_hits += 1
                    self.stats.memory_hits += 1
                    
                    # Performance tracking
                    get_time = (time.time() - start_time) * 1000
                    self._update_performance_stats("get", get_time)
                    
                    logger.debug(f"💾 Memory cache hit: {redis_key[:50]}...", extra={
                        "cache_layer": "memory",
                        "get_time_ms": round(get_time, 2)
                    })
                    
                    return memory_result
            
            # L2: Redis Cache
            if self.config.default_strategy in [CacheStrategy.LAYERED, CacheStrategy.REDIS_ONLY] and self.redis:
                redis_result = await self._get_from_redis(redis_key)
                if redis_result is not None:
                    self.stats.cache_hits += 1
                    self.stats.redis_hits += 1
                    
                    # Promotion vers memory cache si layered
                    if self.config.default_strategy == CacheStrategy.LAYERED:
                        await self._set_to_memory(redis_key, redis_result, self._get_ttl_for_key(redis_key))
                    
                    # Performance tracking
                    get_time = (time.time() - start_time) * 1000
                    self._update_performance_stats("get", get_time)
                    
                    logger.debug(f"🔴 Redis cache hit: {redis_key[:50]}...", extra={
                        "cache_layer": "redis",
                        "get_time_ms": round(get_time, 2)
                    })
                    
                    return redis_result
            
            # Cache miss
            self.stats.cache_misses += 1
            
            logger.debug(f"❌ Cache miss: {redis_key[:50]}...", extra={
                "total_requests": self.stats.total_requests,
                "hit_rate": round(self.stats.hit_rate_percent, 1)
            })
            
            return default
            
        except Exception as e:
            logger.error(f"❌ Cache get error: {e}", extra={
                "key": str(key)[:100],
                "error_type": type(e).__name__
            })
            health_metrics.record_error("cache", "get_operation")
            return default
    
    async def set(self, key: Union[str, CacheKey], value: Any, ttl: Optional[int] = None) -> bool:
        """💾 Stockage intelligent multi-niveaux"""
        start_time = time.time()
        
        try:
            # Normalisation clé et TTL
            redis_key = key.to_redis_key() if isinstance(key, CacheKey) else key
            effective_ttl = ttl or self._get_ttl_for_key(redis_key)
            
            # Sérialisation et compression
            serialized_value, size_bytes = await self._serialize_and_compress(value)
            
            success = True
            
            # Memory Cache (L1)
            if self.config.default_strategy in [CacheStrategy.LAYERED, CacheStrategy.MEMORY_ONLY]:
                memory_success = await self._set_to_memory(redis_key, value, effective_ttl)
                if not memory_success:
                    success = False
            
            # Redis Cache (L2)
            if self.config.default_strategy in [CacheStrategy.LAYERED, CacheStrategy.REDIS_ONLY] and self.redis:
                redis_success = await self._set_to_redis(redis_key, serialized_value, effective_ttl)
                if not redis_success:
                    success = False
            
            # Performance tracking
            set_time = (time.time() - start_time) * 1000
            self._update_performance_stats("set", set_time)
            
            logger.debug(f"💾 Cache set: {redis_key[:50]}...", extra={
                "size_bytes": size_bytes,
                "ttl_seconds": effective_ttl,
                "set_time_ms": round(set_time, 2),
                "success": success
            })
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Cache set error: {e}", extra={
                "key": str(key)[:100],
                "error_type": type(e).__name__
            })
            health_metrics.record_error("cache", "set_operation")
            return False
    
    async def delete(self, key: Union[str, CacheKey]) -> bool:
        """🗑️ Suppression cache multi-niveaux"""
        try:
            redis_key = key.to_redis_key() if isinstance(key, CacheKey) else key
            
            success = True
            
            # Memory Cache
            async with self._memory_lock:
                if redis_key in self.memory_cache:
                    _, _, size_bytes = self.memory_cache.pop(redis_key)
                    self.memory_size_bytes -= size_bytes
                    self.memory_access_times.pop(redis_key, None)
            
            # Redis Cache
            if self.redis:
                try:
                    deleted = await self.redis.delete(redis_key)
                    if deleted == 0:
                        success = False
                except Exception as e:
                    logger.warning(f"⚠️ Redis delete failed: {e}")
                    success = False
            
            logger.debug(f"🗑️ Cache delete: {redis_key[:50]}...", extra={"success": success})
            return success
            
        except Exception as e:
            logger.error(f"❌ Cache delete error: {e}")
            return False
    
    async def clear(self, namespace: Optional[str] = None) -> int:
        """🧹 Nettoyage cache (par namespace optionnel)"""
        try:
            cleared_count = 0
            
            if namespace:
                # Nettoyage par namespace
                pattern = f"nextvision:{namespace}:*"
                
                # Memory cache
                async with self._memory_lock:
                    keys_to_remove = [k for k in self.memory_cache.keys() if k.startswith(f"nextvision:{namespace}:")]
                    for key in keys_to_remove:
                        _, _, size_bytes = self.memory_cache.pop(key)
                        self.memory_size_bytes -= size_bytes
                        self.memory_access_times.pop(key, None)
                        cleared_count += 1
                
                # Redis cache
                if self.redis:
                    try:
                        redis_keys = await self.redis.keys(pattern)
                        if redis_keys:
                            deleted = await self.redis.delete(*redis_keys)
                            cleared_count += deleted
                    except Exception as e:
                        logger.warning(f"⚠️ Redis namespace clear failed: {e}")
            else:
                # Nettoyage complet
                async with self._memory_lock:
                    cleared_count = len(self.memory_cache)
                    self.memory_cache.clear()
                    self.memory_access_times.clear()
                    self.memory_size_bytes = 0
                
                if self.redis:
                    try:
                        await self.redis.flushdb()
                    except Exception as e:
                        logger.warning(f"⚠️ Redis flush failed: {e}")
            
            logger.info(f"🧹 Cache cleared", extra={
                "namespace": namespace,
                "cleared_count": cleared_count
            })
            
            return cleared_count
            
        except Exception as e:
            logger.error(f"❌ Cache clear error: {e}")
            return 0
    
    # ===============================================
    # 💾 MEMORY CACHE OPERATIONS
    # ===============================================
    
    async def _get_from_memory(self, key: str) -> Optional[Any]:
        """🧠 Récupération memory cache avec expiration"""
        async with self._memory_lock:
            if key not in self.memory_cache:
                return None
            
            value, expires_at, _ = self.memory_cache[key]
            
            # Vérification expiration
            if datetime.now() >= expires_at:
                # Expirée - nettoyage
                _, _, size_bytes = self.memory_cache.pop(key)
                self.memory_size_bytes -= size_bytes
                self.memory_access_times.pop(key, None)
                return None
            
            # Update LRU
            self.memory_access_times[key] = datetime.now()
            return value
    
    async def _set_to_memory(self, key: str, value: Any, ttl: int) -> bool:
        """🧠 Stockage memory cache avec éviction LRU"""
        try:
            # Estimation taille
            value_size = len(pickle.dumps(value))
            
            async with self._memory_lock:
                # Vérification limites
                await self._ensure_memory_capacity(value_size)
                
                # Stockage
                expires_at = datetime.now() + timedelta(seconds=ttl)
                self.memory_cache[key] = (value, expires_at, value_size)
                self.memory_access_times[key] = datetime.now()
                self.memory_size_bytes += value_size
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Memory cache set failed: {e}")
            return False
    
    async def _ensure_memory_capacity(self, needed_bytes: int):
        """🧹 Éviction LRU pour libérer l'espace mémoire"""
        max_bytes = self.config.memory_max_size_mb * 1024 * 1024
        max_items = self.config.memory_max_items
        
        # Vérification space
        while (self.memory_size_bytes + needed_bytes > max_bytes or 
               len(self.memory_cache) >= max_items) and self.memory_cache:
            
            # Trouver clé LRU
            lru_key = min(self.memory_access_times.keys(), 
                         key=lambda k: self.memory_access_times[k])
            
            # Éviction
            if lru_key in self.memory_cache:
                _, _, size_bytes = self.memory_cache.pop(lru_key)
                self.memory_size_bytes -= size_bytes
                self.memory_access_times.pop(lru_key, None)
                self.stats.memory_evictions += 1
                
                logger.debug(f"🗑️ Memory eviction: {lru_key[:50]}...", extra={
                    "evicted_size_bytes": size_bytes,
                    "remaining_items": len(self.memory_cache)
                })
    
    # ===============================================
    # 🔴 REDIS CACHE OPERATIONS
    # ===============================================
    
    async def _get_from_redis(self, key: str) -> Optional[Any]:
        """🔴 Récupération Redis avec timeout strict"""
        try:
            async with asyncio.timeout(self.config.redis_timeout_seconds):
                async with self._redis_lock:
                    data = await self.redis.get(key)
                    
                if data is None:
                    return None
                
                # Désérialisation et décompression
                return await self._decompress_and_deserialize(data)
                
        except (ConnectionError, TimeoutError, asyncio.TimeoutError) as e:
            logger.warning(f"⚠️ Redis timeout/connection: {e}")
            self.stats.redis_errors += 1
            health_metrics.record_error("cache", "redis_timeout")
            return None
        except Exception as e:
            logger.error(f"❌ Redis get error: {e}")
            self.stats.redis_errors += 1
            health_metrics.record_error("cache", "redis_get")
            return None
    
    async def _set_to_redis(self, key: str, serialized_data: bytes, ttl: int) -> bool:
        """🔴 Stockage Redis avec timeout strict"""
        try:
            async with asyncio.timeout(self.config.redis_timeout_seconds):
                async with self._redis_lock:
                    await self.redis.setex(key, ttl, serialized_data)
                return True
                
        except (ConnectionError, TimeoutError, asyncio.TimeoutError) as e:
            logger.warning(f"⚠️ Redis set timeout/connection: {e}")
            self.stats.redis_errors += 1
            health_metrics.record_error("cache", "redis_timeout")
            return False
        except Exception as e:
            logger.error(f"❌ Redis set error: {e}")
            self.stats.redis_errors += 1
            health_metrics.record_error("cache", "redis_set")
            return False
    
    # ===============================================
    # 🗜️ SERIALIZATION & COMPRESSION
    # ===============================================
    
    async def _serialize_and_compress(self, value: Any) -> Tuple[bytes, int]:
        """🗜️ Sérialisation et compression optimisées"""
        try:
            # Sérialisation avec orjson (plus rapide)
            if isinstance(value, (dict, list, str, int, float, bool)) or value is None:
                serialized = orjson.dumps(value)
            else:
                # Fallback pickle pour objets complexes
                serialized = pickle.dumps(value)
            
            original_size = len(serialized)
            
            # Compression si nécessaire
            if original_size > self.config.compression_threshold_bytes:
                compressed = zlib.compress(serialized, level=6)
                compression_ratio = len(compressed) / original_size
                
                # Utiliser compression seulement si bénéfique
                if compression_ratio < 0.9:  # Au moins 10% de gain
                    self.stats.compression_ratio = compression_ratio
                    # Préfixer pour indiquer compression
                    return b'COMPRESSED:' + compressed, len(compressed)
            
            return serialized, original_size
            
        except Exception as e:
            logger.error(f"❌ Serialization error: {e}")
            # Fallback pickle simple
            fallback_data = pickle.dumps(value)
            return fallback_data, len(fallback_data)
    
    async def _decompress_and_deserialize(self, data: bytes) -> Any:
        """🔓 Décompression et désérialisation"""
        try:
            # Vérifier compression
            if data.startswith(b'COMPRESSED:'):
                compressed_data = data[11:]  # Enlever préfixe
                data = zlib.decompress(compressed_data)
            
            # Tentative orjson d'abord
            try:
                return orjson.loads(data)
            except (orjson.JSONDecodeError, TypeError):
                # Fallback pickle
                return pickle.loads(data)
                
        except Exception as e:
            logger.error(f"❌ Deserialization error: {e}")
            raise e
    
    # ===============================================
    # 📊 MONITORING & STATS
    # ===============================================
    
    def _get_ttl_for_key(self, key: str) -> int:
        """⏰ Détermine TTL selon le namespace"""
        if ":geocoding:" in key:
            return self.config.ttl_geocoding
        elif ":transport:" in key:
            return self.config.ttl_transport
        elif ":matching:" in key:
            return self.config.ttl_matching
        else:
            return self.config.ttl_default
    
    def _update_performance_stats(self, operation: str, duration_ms: float):
        """📈 Mise à jour statistiques performance"""
        if operation == "get":
            # Calcul moyenne mobile
            if self.stats.avg_get_time_ms == 0:
                self.stats.avg_get_time_ms = duration_ms
            else:
                self.stats.avg_get_time_ms = (self.stats.avg_get_time_ms * 0.9) + (duration_ms * 0.1)
        elif operation == "set":
            if self.stats.avg_set_time_ms == 0:
                self.stats.avg_set_time_ms = duration_ms
            else:
                self.stats.avg_set_time_ms = (self.stats.avg_set_time_ms * 0.9) + (duration_ms * 0.1)
        
        # Historique pour P95
        self.performance_history.append({
            "operation": operation,
            "duration_ms": duration_ms,
            "timestamp": time.time()
        })
        
        # Garder seulement dernière heure
        cutoff_time = time.time() - (self.config.stats_window_minutes * 60)
        self.performance_history = [h for h in self.performance_history if h["timestamp"] > cutoff_time]
        
        # Calcul P95
        if len(self.performance_history) > 10:
            get_times = [h["duration_ms"] for h in self.performance_history if h["operation"] == "get"]
            if get_times:
                get_times.sort()
                p95_index = int(len(get_times) * 0.95)
                self.stats.p95_get_time_ms = get_times[p95_index] if p95_index < len(get_times) else get_times[-1]
        
        # Update hit rate
        self.stats.calculate_hit_rate()
    
    async def get_stats(self) -> Dict:
        """📊 Récupère statistiques complètes"""
        # Stats mémoire actuelle
        self.stats.memory_size_mb = self.memory_size_bytes / (1024 * 1024)
        
        # Stats Redis
        redis_info = {}
        if self.redis:
            try:
                info = await self.redis.info("memory")
                redis_info = {
                    "used_memory_mb": info.get("used_memory", 0) / (1024 * 1024),
                    "connected_clients": info.get("connected_clients", 0)
                }
            except Exception as e:
                logger.warning(f"⚠️ Redis info failed: {e}")
        
        return {
            "performance": {
                "total_requests": self.stats.total_requests,
                "hit_rate_percent": round(self.stats.hit_rate_percent, 2),
                "avg_get_time_ms": round(self.stats.avg_get_time_ms, 2),
                "avg_set_time_ms": round(self.stats.avg_set_time_ms, 2),
                "p95_get_time_ms": round(self.stats.p95_get_time_ms, 2)
            },
            "cache_layers": {
                "memory": {
                    "hits": self.stats.memory_hits,
                    "size_mb": round(self.stats.memory_size_mb, 2),
                    "items_count": len(self.memory_cache),
                    "evictions": self.stats.memory_evictions
                },
                "redis": {
                    "hits": self.stats.redis_hits,
                    "errors": self.stats.redis_errors,
                    "connected": self.redis is not None,
                    **redis_info
                }
            },
            "efficiency": {
                "compression_ratio": round(self.stats.compression_ratio, 3),
                "memory_usage_percent": round(
                    (self.memory_size_bytes / (self.config.memory_max_size_mb * 1024 * 1024)) * 100, 1
                )
            },
            "configuration": {
                "strategy": self.config.default_strategy.value,
                "ttl_geocoding_hours": self.config.ttl_geocoding // 3600,
                "ttl_transport_hours": self.config.ttl_transport // 3600,
                "memory_max_mb": self.config.memory_max_size_mb
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def cleanup(self):
        """🧹 Nettoyage ressources"""
        try:
            if self.redis_pool:
                await self.redis_pool.disconnect()
            
            async with self._memory_lock:
                self.memory_cache.clear()
                self.memory_access_times.clear()
                self.memory_size_bytes = 0
            
            logger.info("🧹 Cache cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Cache cleanup error: {e}")

# ===============================================
# 🚀 GLOBAL INSTANCE & UTILITIES
# ===============================================

_cache_instance: Optional[IntelligentCache] = None

async def get_cache_instance(config: Optional[CacheConfig] = None) -> IntelligentCache:
    """💾 Récupère l'instance globale du cache"""
    global _cache_instance
    
    if _cache_instance is None:
        if config is None:
            config = CacheConfig()  # Configuration par défaut
        
        _cache_instance = IntelligentCache(config)
        await _cache_instance.initialize()
        
        logger.info("🚀 Global cache instance initialized")
    
    return _cache_instance

# Utility functions pour usage simple
async def get_cached(key: Union[str, CacheKey], default: Any = None) -> Any:
    """🔍 Récupération cache simple"""
    cache = await get_cache_instance()
    return await cache.get(key, default)

async def set_cached(key: Union[str, CacheKey], value: Any, ttl: Optional[int] = None) -> bool:
    """💾 Stockage cache simple"""
    cache = await get_cache_instance()
    return await cache.set(key, value, ttl)

async def delete_cached(key: Union[str, CacheKey]) -> bool:
    """🗑️ Suppression cache simple"""
    cache = await get_cache_instance()
    return await cache.delete(key)

# Décorateur pour mise en cache automatique
def cached(ttl: Optional[int] = None, namespace: str = "default"):
    """💾 Décorateur pour mise en cache automatique de fonctions"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Génération clé cache
            func_name = f"{func.__module__}.{func.__name__}"
            args_str = "|".join(str(arg) for arg in args)
            kwargs_str = "|".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = CacheKey(
                namespace=namespace,
                identifier=func_name,
                params_hash=hashlib.md5(f"{args_str}|{kwargs_str}".encode()).hexdigest()[:16]
            )
            
            # Tentative récupération cache
            cached_result = await get_cached(cache_key)
            if cached_result is not None:
                logger.debug(f"💾 Cached function result: {func_name}")
                return cached_result
            
            # Exécution fonction
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # Mise en cache
            await set_cached(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator
