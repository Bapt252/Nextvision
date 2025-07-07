"""
⚡ Nextvision - Google Maps Performance Helpers  
Utilitaires de cache intelligent, batch processing et optimisation performance

Author: NEXTEN Team
Version: 2.0.0 (Prompt 2)
Features: Intelligent caching, Batch processing, Performance monitoring, Rate limiting helpers
"""

import asyncio
import time
import json
import hashlib
import logging
from typing import Dict, List, Optional, Tuple, Any, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
from functools import wraps

import redis.asyncio as redis

from ..config import get_config, CacheBackend
from ..models.transport_models import GeocodeResult, TransportRoute, GoogleMapsMode

logger = logging.getLogger(__name__)

@dataclass
class CacheStats:
    """📊 Statistiques détaillées du cache"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    total_size_bytes: int = 0
    avg_hit_time_ms: float = 0
    avg_miss_time_ms: float = 0
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0
    
    @property
    def total_requests(self) -> int:
        return self.hits + self.misses

@dataclass
class PerformanceMetrics:
    """📈 Métriques de performance"""
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    cache_hit: bool = False
    google_maps_call: bool = False
    batch_size: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    
    def finish(self, success: bool = True, error: Optional[str] = None):
        """🏁 Finalise les métriques"""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        self.success = success
        self.error_message = error

class IntelligentCache:
    """🧠 Cache intelligent avec TTL adaptatif et compression"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.config = get_config()
        self.redis_client = redis_client
        self.memory_cache: Dict[str, Dict] = {}
        self.stats = CacheStats()
        self.key_prefixes = {
            "geocode": "geo",
            "directions": "dir", 
            "distance_matrix": "matrix",
            "transport_analysis": "trans"
        }
        
    async def _get_ttl_for_data_type(self, data_type: str, data: Any) -> int:
        """⏰ TTL adaptatif selon le type de données"""
        base_ttls = {
            "geocode": self.config.cache.geocoding_ttl,
            "directions": self.config.cache.directions_ttl,
            "distance_matrix": self.config.cache.distance_matrix_ttl,
            "transport_analysis": 3600  # 1h pour analyses
        }
        
        base_ttl = base_ttls.get(data_type, 3600)
        
        # Ajustements adaptatifs
        if data_type == "directions":
            # TTL réduit pour heures de pointe
            current_hour = datetime.now().hour
            if current_hour in [7, 8, 9, 17, 18, 19]:
                return min(base_ttl, self.config.cache.peak_directions_ttl)
        
        elif data_type == "geocode":
            # TTL plus long pour adresses bien formées
            if isinstance(data, dict) and data.get("confidence", 0) > 0.9:
                return base_ttl * 2
        
        return base_ttl
    
    def _generate_smart_key(self, data_type: str, **params) -> str:
        """🔑 Génération de clés intelligentes avec déduplication"""
        prefix = self.key_prefixes.get(data_type, "cache")
        
        # Normalisation des paramètres selon le type
        normalized_params = self._normalize_cache_params(data_type, params)
        
        # Hash stable
        params_str = json.dumps(normalized_params, sort_keys=True)
        hash_obj = hashlib.sha256(params_str.encode())
        key_hash = hash_obj.hexdigest()[:16]  # 16 chars suffisent
        
        return f"nx:{prefix}:{key_hash}"
    
    def _normalize_cache_params(self, data_type: str, params: Dict) -> Dict:
        """🎯 Normalise les paramètres pour optimiser le cache"""
        normalized = params.copy()
        
        if data_type == "directions":
            # Arrondir les coordonnées pour regrouper les requêtes proches
            for coord_field in ["origin", "destination"]:
                if coord_field in normalized and isinstance(normalized[coord_field], tuple):
                    lat, lng = normalized[coord_field]
                    # Arrondir à 4 décimales (~10m de précision)
                    normalized[coord_field] = (round(lat, 4), round(lng, 4))
            
            # Regrouper par heure pour le departure_time
            if "departure_time" in normalized:
                dt = normalized["departure_time"]
                if isinstance(dt, datetime):
                    # Regrouper par heure
                    normalized["departure_time"] = dt.replace(minute=0, second=0, microsecond=0)
        
        elif data_type == "geocode":
            # Normaliser les adresses
            address = normalized.get("address", "")
            # Supprimer espaces multiples, normaliser casse
            normalized["address"] = " ".join(address.strip().split())
        
        return normalized
    
    async def get(self, data_type: str, **params) -> Optional[Any]:
        """📥 Récupération intelligente depuis le cache"""
        start_time = time.time()
        
        try:
            cache_key = self._generate_smart_key(data_type, **params)
            
            # Essayer Redis d'abord
            if self.config.cache.backend == CacheBackend.REDIS and self.redis_client:
                try:
                    cached_data = await self.redis_client.get(cache_key)
                    if cached_data:
                        result = json.loads(cached_data)
                        self.stats.hits += 1
                        self.stats.avg_hit_time_ms = (time.time() - start_time) * 1000
                        logger.debug(f"📥 Redis cache hit: {cache_key}")
                        return result
                except Exception as e:
                    logger.warning(f"⚠️ Redis cache error: {e}")
                    self.stats.errors += 1
            
            # Fallback vers cache mémoire
            if cache_key in self.memory_cache:
                cache_entry = self.memory_cache[cache_key]
                if cache_entry["expires_at"] > time.time():
                    self.stats.hits += 1
                    self.stats.avg_hit_time_ms = (time.time() - start_time) * 1000
                    logger.debug(f"📥 Memory cache hit: {cache_key}")
                    return cache_entry["data"]
                else:
                    # Entrée expirée
                    del self.memory_cache[cache_key]
            
            # Cache miss
            self.stats.misses += 1
            self.stats.avg_miss_time_ms = (time.time() - start_time) * 1000
            return None
            
        except Exception as e:
            logger.error(f"❌ Cache get error: {e}")
            self.stats.errors += 1
            return None
    
    async def set(self, data_type: str, data: Any, **params) -> bool:
        """📤 Stockage intelligent avec compression"""
        try:
            cache_key = self._generate_smart_key(data_type, **params)
            ttl = await self._get_ttl_for_data_type(data_type, data)
            
            # Sérialisation avec compression pour gros objets
            serialized_data = json.dumps(data, default=str)
            
            # Compression si données volumineuses (>1KB)
            if len(serialized_data) > 1024:
                import gzip
                serialized_data = gzip.compress(serialized_data.encode()).decode('latin1')
                # Marquer comme compressé
                cache_entry = {
                    "data": serialized_data,
                    "compressed": True,
                    "original_size": len(json.dumps(data, default=str))
                }
            else:
                cache_entry = {
                    "data": data,
                    "compressed": False
                }
            
            # Redis
            if self.config.cache.backend == CacheBackend.REDIS and self.redis_client:
                try:
                    await self.redis_client.setex(
                        cache_key, 
                        ttl, 
                        json.dumps(cache_entry, default=str)
                    )
                    logger.debug(f"📤 Redis cache set: {cache_key} (TTL: {ttl}s)")
                except Exception as e:
                    logger.warning(f"⚠️ Redis cache set error: {e}")
                    # Fallback vers mémoire
                    self.config.cache.backend = CacheBackend.MEMORY
            
            # Cache mémoire (toujours en backup)
            if len(self.memory_cache) > self.config.cache.max_memory_entries:
                await self._cleanup_memory_cache()
            
            self.memory_cache[cache_key] = {
                **cache_entry,
                "expires_at": time.time() + ttl
            }
            
            self.stats.sets += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache set error: {e}")
            self.stats.errors += 1
            return False
    
    async def _cleanup_memory_cache(self):
        """🧹 Nettoyage intelligent du cache mémoire"""
        current_time = time.time()
        
        # Supprimer les entrées expirées
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if entry["expires_at"] <= current_time
        ]
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        # Si encore trop plein, supprimer les plus anciennes
        if len(self.memory_cache) > self.config.cache.max_memory_entries:
            # Trier par expires_at et garder les plus récentes
            sorted_items = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1]["expires_at"],
                reverse=True
            )
            
            # Garder seulement max_memory_entries - 10%
            keep_count = int(self.config.cache.max_memory_entries * 0.9)
            
            self.memory_cache = dict(sorted_items[:keep_count])
        
        logger.debug(f"🧹 Memory cache cleaned: {len(expired_keys)} expired, {len(self.memory_cache)} remaining")
    
    def get_stats(self) -> Dict:
        """📊 Statistiques détaillées du cache"""
        return {
            "performance": asdict(self.stats),
            "memory_cache_size": len(self.memory_cache),
            "redis_available": self.config.cache.backend == CacheBackend.REDIS and self.redis_client is not None,
            "cache_backend": self.config.cache.backend.value
        }

class BatchProcessor:
    """📦 Processeur batch optimisé pour Google Maps"""
    
    def __init__(self, max_batch_size: int = 25, max_concurrent: int = 10):
        self.max_batch_size = max_batch_size
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.processing_stats = {
            "total_batches": 0,
            "total_items": 0,
            "avg_batch_time": 0,
            "success_rate": 0
        }
    
    async def process_batch(self, 
                          items: List[Any], 
                          processor_func: Callable,
                          batch_size: Optional[int] = None) -> List[Tuple[Any, Any]]:
        """🚀 Traitement par batch avec gestion d'erreurs"""
        
        batch_size = batch_size or self.max_batch_size
        results = []
        batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
        
        start_time = time.time()
        
        async def process_single_batch(batch):
            async with self.semaphore:
                batch_results = []
                for item in batch:
                    try:
                        result = await processor_func(item)
                        batch_results.append((item, result))
                    except Exception as e:
                        logger.error(f"❌ Batch processing error for item {item}: {e}")
                        batch_results.append((item, None))
                return batch_results
        
        # Traitement parallèle des batches
        batch_tasks = [process_single_batch(batch) for batch in batches]
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        # Collecte des résultats
        for batch_result in batch_results:
            if isinstance(batch_result, Exception):
                logger.error(f"❌ Batch exception: {batch_result}")
                continue
            results.extend(batch_result)
        
        # Mise à jour des statistiques
        processing_time = time.time() - start_time
        self.processing_stats["total_batches"] += len(batches)
        self.processing_stats["total_items"] += len(items)
        self.processing_stats["avg_batch_time"] = (
            (self.processing_stats["avg_batch_time"] * (self.processing_stats["total_batches"] - len(batches)) + processing_time) / 
            self.processing_stats["total_batches"]
        )
        
        success_count = len([r for r in results if r[1] is not None])
        self.processing_stats["success_rate"] = success_count / len(results) if results else 0
        
        logger.info(f"📦 Batch processing complete: {len(batches)} batches, {success_count}/{len(items)} successful")
        
        return results

class PerformanceMonitor:
    """📊 Moniteur de performance en temps réel"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.alerts_config = {
            "slow_operation_ms": 1000,
            "high_error_rate": 0.1,
            "cache_hit_rate_low": 0.5
        }
        self.alert_callbacks: List[Callable] = []
    
    @asynccontextmanager
    async def measure_operation(self, operation_name: str, **kwargs):
        """⏱️ Context manager pour mesurer les opérations"""
        metrics = PerformanceMetrics(
            operation_name=operation_name,
            start_time=time.time(),
            **kwargs
        )
        
        try:
            yield metrics
            metrics.finish(success=True)
        except Exception as e:
            metrics.finish(success=False, error=str(e))
            raise
        finally:
            self.metrics.append(metrics)
            await self._check_alerts(metrics)
    
    async def _check_alerts(self, metrics: PerformanceMetrics):
        """🚨 Vérification des seuils d'alerte"""
        alerts = []
        
        # Opération lente
        if metrics.duration_ms and metrics.duration_ms > self.alerts_config["slow_operation_ms"]:
            alerts.append({
                "type": "slow_operation",
                "message": f"Opération lente: {metrics.operation_name} ({metrics.duration_ms:.1f}ms)",
                "metrics": metrics
            })
        
        # Taux d'erreur élevé (sur les 100 dernières opérations)
        recent_metrics = self.metrics[-100:]
        if len(recent_metrics) >= 10:
            error_rate = len([m for m in recent_metrics if not m.success]) / len(recent_metrics)
            if error_rate > self.alerts_config["high_error_rate"]:
                alerts.append({
                    "type": "high_error_rate", 
                    "message": f"Taux d'erreur élevé: {error_rate:.1%}",
                    "error_rate": error_rate
                })
        
        # Exécuter les callbacks d'alerte
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    logger.error(f"❌ Alert callback error: {e}")
    
    def add_alert_callback(self, callback: Callable):
        """🔔 Ajouter un callback d'alerte"""
        self.alert_callbacks.append(callback)
    
    def get_performance_summary(self, minutes: int = 60) -> Dict:
        """📈 Résumé de performance des N dernières minutes"""
        cutoff_time = time.time() - (minutes * 60)
        recent_metrics = [m for m in self.metrics if m.start_time > cutoff_time]
        
        if not recent_metrics:
            return {"period_minutes": minutes, "no_data": True}
        
        # Calculs des métriques
        total_operations = len(recent_metrics)
        successful_ops = len([m for m in recent_metrics if m.success])
        success_rate = successful_ops / total_operations
        
        durations = [m.duration_ms for m in recent_metrics if m.duration_ms]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        cache_hits = len([m for m in recent_metrics if m.cache_hit])
        cache_hit_rate = cache_hits / total_operations
        
        google_maps_calls = len([m for m in recent_metrics if m.google_maps_call])
        
        # Groupement par opération
        operations = {}
        for metric in recent_metrics:
            op_name = metric.operation_name
            if op_name not in operations:
                operations[op_name] = {"count": 0, "avg_duration": 0, "success_rate": 0}
            
            operations[op_name]["count"] += 1
            if metric.duration_ms:
                operations[op_name]["avg_duration"] += metric.duration_ms
            if metric.success:
                operations[op_name]["success_rate"] += 1
        
        # Finaliser les moyennes
        for op_data in operations.values():
            if op_data["count"] > 0:
                op_data["avg_duration"] /= op_data["count"]
                op_data["success_rate"] /= op_data["count"]
        
        return {
            "period_minutes": minutes,
            "total_operations": total_operations,
            "success_rate": success_rate,
            "avg_duration_ms": avg_duration,
            "cache_hit_rate": cache_hit_rate,
            "google_maps_calls": google_maps_calls,
            "operations_breakdown": operations,
            "alerts": {
                "slow_operations": len([m for m in recent_metrics if m.duration_ms and m.duration_ms > self.alerts_config["slow_operation_ms"]]),
                "failed_operations": total_operations - successful_ops
            }
        }

# Décorateurs utilitaires

def cache_result(data_type: str, cache: Optional[IntelligentCache] = None):
    """🎯 Décorateur pour cache automatique des résultats"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal cache
            if cache is None:
                cache = IntelligentCache()
            
            # Essayer le cache d'abord
            cache_params = {f"arg_{i}": arg for i, arg in enumerate(args)}
            cache_params.update(kwargs)
            
            cached_result = await cache.get(data_type, **cache_params)
            if cached_result is not None:
                return cached_result
            
            # Exécuter la fonction et cacher le résultat
            result = await func(*args, **kwargs)
            if result is not None:
                await cache.set(data_type, result, **cache_params)
            
            return result
        return wrapper
    return decorator

def monitor_performance(operation_name: str, monitor: Optional[PerformanceMonitor] = None):
    """📊 Décorateur pour monitoring automatique"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal monitor
            if monitor is None:
                monitor = PerformanceMonitor()
            
            async with monitor.measure_operation(operation_name) as metrics:
                result = await func(*args, **kwargs)
                # Ajouter des métadonnées si possible
                if hasattr(result, '__dict__'):
                    metrics.batch_size = getattr(result, 'batch_size', None)
                return result
        return wrapper
    return decorator

# Fonctions helper globales

async def batch_geocode_addresses(addresses: List[str], 
                                cache: Optional[IntelligentCache] = None) -> List[Tuple[str, Optional[GeocodeResult]]]:
    """🗺️ Géocodage en batch avec cache intelligent"""
    
    from ..services.google_maps_service import get_google_maps_service
    
    if cache is None:
        cache = IntelligentCache()
    
    processor = BatchProcessor(max_batch_size=10, max_concurrent=5)
    
    async def geocode_single(address: str) -> Optional[GeocodeResult]:
        # Vérifier cache d'abord
        cached = await cache.get("geocode", address=address)
        if cached:
            return GeocodeResult(**cached)
        
        # Géocoder
        gmaps_service = await get_google_maps_service()
        result = await gmaps_service.geocode_address(address)
        
        # Cacher le résultat
        if result:
            await cache.set("geocode", result.dict(), address=address)
        
        return result
    
    return await processor.process_batch(addresses, geocode_single)

async def optimize_transport_calculations(candidat_profiles: List[Any],
                                        jobs: List[Any],
                                        cache: Optional[IntelligentCache] = None) -> Dict:
    """⚡ Optimisation globale des calculs transport"""
    
    start_time = time.time()
    stats = {
        "total_combinations": len(candidat_profiles) * len(jobs),
        "cache_hits": 0,
        "google_maps_calls": 0,
        "processing_time_ms": 0
    }
    
    if cache is None:
        cache = IntelligentCache()
    
    # Pré-géocodage de toutes les adresses uniques
    all_addresses = set()
    for profile in candidat_profiles:
        all_addresses.add(profile.home_address)
    for job in jobs:
        if hasattr(job, 'office_address'):
            all_addresses.add(job.office_address)
    
    logger.info(f"⚡ Pré-géocodage de {len(all_addresses)} adresses uniques")
    geocode_results = await batch_geocode_addresses(list(all_addresses), cache)
    
    # Construire un index des géocodes
    geocode_index = {addr: result for addr, result in geocode_results if result}
    
    stats["processing_time_ms"] = (time.time() - start_time) * 1000
    stats["geocoded_addresses"] = len(geocode_index)
    stats["geocoding_success_rate"] = len(geocode_index) / len(all_addresses) if all_addresses else 0
    
    logger.info(f"✅ Optimisation transport: {stats['geocoded_addresses']}/{len(all_addresses)} adresses géocodées en {stats['processing_time_ms']:.1f}ms")
    
    return {
        "geocode_index": geocode_index,
        "stats": stats,
        "cache": cache
    }

# Instance globale des helpers
_global_cache: Optional[IntelligentCache] = None
_global_performance_monitor: Optional[PerformanceMonitor] = None

async def get_global_cache() -> IntelligentCache:
    """🌍 Instance globale du cache"""
    global _global_cache
    if _global_cache is None:
        _global_cache = IntelligentCache()
    return _global_cache

async def get_global_performance_monitor() -> PerformanceMonitor:
    """🌍 Instance globale du moniteur de performance"""
    global _global_performance_monitor
    if _global_performance_monitor is None:
        _global_performance_monitor = PerformanceMonitor()
    return _global_performance_monitor

async def cleanup_global_helpers():
    """🧹 Nettoyage des instances globales"""
    global _global_cache, _global_performance_monitor
    _global_cache = None
    _global_performance_monitor = None
