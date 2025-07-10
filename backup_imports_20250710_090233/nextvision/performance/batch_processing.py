""" 
⚡ Nextvision - Batch Processing & Performance Optimization
Enterprise-grade batch processing for 1000+ jobs simultaneously

Features:
- Intelligent batch size optimization
- Adaptive concurrency management
- Memory-efficient streaming
- Progress tracking
- Graceful degradation under load
"""

import asyncio
import time
import psutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional, Callable, AsyncGenerator, Union
import logging
import math
from concurrent.futures import ThreadPoolExecutor

from ..logging.structured_logging import get_structured_logger
from ..monitoring.health_metrics import MetricsCollector
from ..cache.redis_intelligent_cache import CacheManager

logger = get_structured_logger(__name__)


class BatchStrategy(Enum):
    """🎯 Stratégies de traitement batch"""
    FIXED_SIZE = "fixed_size"
    ADAPTIVE_SIZE = "adaptive_size"
    MEMORY_BASED = "memory_based"
    PERFORMANCE_BASED = "performance_based"
    HYBRID = "hybrid"


@dataclass
class BatchJob:
    """📋 Job individuel dans un batch"""
    id: str
    data: Dict[str, Any]
    priority: int = 1
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    processing_time_ms: Optional[float] = None


@dataclass 
class BatchResult:
    """📊 Résultat de traitement batch"""
    batch_id: str
    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    processing_time_seconds: float
    jobs_per_second: float
    memory_peak_mb: float
    batch_size_used: int
    concurrency_used: int
    cache_hit_rate: float = 0.0
    performance_rating: str = "unknown"
    errors: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Taux de succès"""
        if self.total_jobs == 0:
            return 0.0
        return (self.successful_jobs / self.total_jobs) * 100


class PerformanceMonitor:
    """📊 Monitoring performance temps réel"""
    
    def __init__(self):
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        self.peak_memory = self.start_memory
        
    def update_peak_memory(self):
        """Mise à jour pic mémoire"""
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
        self.peak_memory = max(self.peak_memory, current_memory)
    
    def get_current_stats(self) -> Dict[str, float]:
        """Stats actuelles"""
        current_time = time.time()
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        return {
            "elapsed_time": current_time - self.start_time,
            "current_memory_mb": current_memory,
            "peak_memory_mb": self.peak_memory,
            "memory_growth_mb": current_memory - self.start_memory,
            "cpu_percent": psutil.cpu_percent()
        }


class ConcurrencyManager:
    """🔄 Gestionnaire de concurrence adaptatif"""
    
    def __init__(
        self,
        initial_concurrency: int = 10,
        max_concurrency: int = 50,
        target_memory_mb: int = 2048
    ):
        self.current_concurrency = initial_concurrency
        self.max_concurrency = max_concurrency
        self.target_memory_mb = target_memory_mb
        self.performance_history: List[Dict[str, float]] = []
        self.adjustment_cooldown = 0
        
    def should_adjust_concurrency(self) -> bool:
        """Détermine si ajustement nécessaire"""
        if self.adjustment_cooldown > 0:
            self.adjustment_cooldown -= 1
            return False
        return True
    
    def adjust_concurrency(self, performance_stats: Dict[str, float]) -> int:
        """Ajuste la concurrence selon les performances"""
        if not self.should_adjust_concurrency():
            return self.current_concurrency
            
        current_memory = performance_stats.get("current_memory_mb", 0)
        cpu_percent = performance_stats.get("cpu_percent", 0)
        
        # Réduction si consommation mémoire élevée
        if current_memory > self.target_memory_mb * 0.9:
            new_concurrency = max(1, self.current_concurrency - 2)
            logger.warning(f"🔻 Réduction concurrence: {self.current_concurrency} → {new_concurrency} (mémoire: {current_memory:.1f}MB)")
            
        # Réduction si CPU saturé
        elif cpu_percent > 85:
            new_concurrency = max(1, self.current_concurrency - 1)
            logger.warning(f"🔻 Réduction concurrence: {self.current_concurrency} → {new_concurrency} (CPU: {cpu_percent:.1f}%)")
            
        # Augmentation si ressources disponibles
        elif (current_memory < self.target_memory_mb * 0.7 and 
              cpu_percent < 60 and 
              self.current_concurrency < self.max_concurrency):
            new_concurrency = min(self.max_concurrency, self.current_concurrency + 1)
            logger.info(f"🔺 Augmentation concurrence: {self.current_concurrency} → {new_concurrency}")
            
        else:
            return self.current_concurrency
        
        self.current_concurrency = new_concurrency
        self.adjustment_cooldown = 5  # Cooldown 5 batches
        return new_concurrency


class BatchSizeOptimizer:
    """📏 Optimiseur de taille de batch adaptatif"""
    
    def __init__(
        self,
        initial_batch_size: int = 50,
        min_batch_size: int = 10,
        max_batch_size: int = 200
    ):
        self.current_batch_size = initial_batch_size
        self.min_batch_size = min_batch_size
        self.max_batch_size = max_batch_size
        self.performance_history: List[float] = []
        
    def optimize_batch_size(
        self,
        jobs_per_second: float,
        memory_usage_mb: float,
        target_memory_mb: int = 2048
    ) -> int:
        """Optimise la taille de batch selon les performances"""
        self.performance_history.append(jobs_per_second)
        
        # Garder historique des 10 dernières performances
        if len(self.performance_history) > 10:
            self.performance_history.pop(0)
        
        # Pas assez d'historique
        if len(self.performance_history) < 3:
            return self.current_batch_size
        
        # Analyse de tendance
        recent_avg = sum(self.performance_history[-3:]) / 3
        older_avg = sum(self.performance_history[:-3]) / max(1, len(self.performance_history) - 3)
        
        # Calcul ajustement
        if memory_usage_mb > target_memory_mb * 0.8:
            # Réduire si mémoire élevée
            new_size = max(self.min_batch_size, int(self.current_batch_size * 0.8))
            logger.info(f"📉 Réduction batch size: {self.current_batch_size} → {new_size} (mémoire)")
            
        elif recent_avg > older_avg * 1.1 and memory_usage_mb < target_memory_mb * 0.5:
            # Augmenter si performances s'améliorent
            new_size = min(self.max_batch_size, int(self.current_batch_size * 1.2))
            logger.info(f"📈 Augmentation batch size: {self.current_batch_size} → {new_size} (performance)")
            
        elif recent_avg < older_avg * 0.8:
            # Réduire si performances se dégradent
            new_size = max(self.min_batch_size, int(self.current_batch_size * 0.9))
            logger.info(f"📉 Réduction batch size: {self.current_batch_size} → {new_size} (dégradation)")
            
        else:
            return self.current_batch_size
        
        self.current_batch_size = new_size
        return new_size


class BatchProcessor:
    """⚡ Processeur batch haute performance pour 1000+ jobs"""
    
    def __init__(
        self,
        strategy: BatchStrategy = BatchStrategy.HYBRID,
        initial_batch_size: int = 50,
        initial_concurrency: int = 10,
        max_concurrency: int = 50,
        cache_manager: Optional[CacheManager] = None,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        self.strategy = strategy
        self.cache_manager = cache_manager
        self.metrics = metrics_collector
        
        # Gestionnaires adaptatifs
        self.concurrency_manager = ConcurrencyManager(
            initial_concurrency, max_concurrency
        )
        self.batch_optimizer = BatchSizeOptimizer(
            initial_batch_size, min_batch_size=10, max_batch_size=200
        )
        
        # État
        self.active_batches: Dict[str, List[BatchJob]] = {}
        self.completed_batches: List[BatchResult] = []
        
    async def process_jobs(
        self,
        jobs: List[BatchJob],
        processor_func: Callable,
        progress_callback: Optional[Callable] = None
    ) -> BatchResult:
        """🚀 Traitement principal optimisé pour gros volumes"""
        batch_id = f"batch_{int(time.time())}_{len(jobs)}"
        logger.info(f"🚀 Démarrage batch {batch_id}: {len(jobs)} jobs")
        
        # Monitoring performance
        perf_monitor = PerformanceMonitor()
        start_time = time.time()
        
        # Résultats
        successful_jobs = 0
        failed_jobs = 0
        errors = []
        cache_hits = 0
        
        try:
            # Traitement par chunks adaptatifs
            total_processed = 0
            current_batch_size = self.batch_optimizer.current_batch_size
            current_concurrency = self.concurrency_manager.current_concurrency
            
            # Générateur de chunks
            async for batch_chunk in self._create_adaptive_chunks(jobs, current_batch_size):
                
                # Ajustement dynamique de la concurrence
                perf_stats = perf_monitor.get_current_stats()
                current_concurrency = self.concurrency_manager.adjust_concurrency(perf_stats)
                
                # Traitement concurrent du chunk
                chunk_results = await self._process_chunk_concurrent(
                    batch_chunk,
                    processor_func,
                    current_concurrency
                )
                
                # Agrégation résultats
                for result in chunk_results:
                    if result.get("success", False):
                        successful_jobs += 1
                        if result.get("from_cache", False):
                            cache_hits += 1
                    else:
                        failed_jobs += 1
                        errors.append({
                            "job_id": result.get("job_id", "unknown"),
                            "error": result.get("error", "Unknown error"),
                            "retry_count": result.get("retry_count", 0)
                        })
                
                total_processed += len(batch_chunk)
                
                # Callback progress
                if progress_callback:
                    await progress_callback({
                        "batch_id": batch_id,
                        "processed": total_processed,
                        "total": len(jobs),
                        "success_rate": (successful_jobs / total_processed) * 100 if total_processed > 0 else 0,
                        "current_concurrency": current_concurrency,
                        "current_batch_size": current_batch_size
                    })
                
                # Optimisation batch size pour prochain chunk
                chunk_time = time.time() - start_time
                jobs_per_second = total_processed / chunk_time if chunk_time > 0 else 0
                current_batch_size = self.batch_optimizer.optimize_batch_size(
                    jobs_per_second,
                    perf_stats["current_memory_mb"]
                )
                
                # Mise à jour pic mémoire
                perf_monitor.update_peak_memory()
                
                logger.debug(f"📊 Chunk terminé: {len(batch_chunk)} jobs, {jobs_per_second:.1f} jobs/s")
            
            # Statistiques finales
            total_time = time.time() - start_time
            final_stats = perf_monitor.get_current_stats()
            jobs_per_second = len(jobs) / total_time if total_time > 0 else 0
            
            # Classification performance
            performance_rating = self._classify_performance(jobs_per_second, len(jobs))
            
            # Création résultat
            result = BatchResult(
                batch_id=batch_id,
                total_jobs=len(jobs),
                successful_jobs=successful_jobs,
                failed_jobs=failed_jobs,
                processing_time_seconds=total_time,
                jobs_per_second=jobs_per_second,
                memory_peak_mb=final_stats["peak_memory_mb"],
                batch_size_used=self.batch_optimizer.current_batch_size,
                concurrency_used=self.concurrency_manager.current_concurrency,
                cache_hit_rate=(cache_hits / len(jobs)) * 100 if len(jobs) > 0 else 0,
                performance_rating=performance_rating,
                errors=errors[:10]  # Limite erreurs
            )
            
            # Metrics
            if self.metrics:
                self.metrics.record_timer("batch_processing_time", total_time)
                self.metrics.record_gauge("batch_jobs_per_second", jobs_per_second)
                self.metrics.record_gauge("batch_success_rate", result.success_rate)
                self.metrics.increment_counter("batch_processed", len(jobs))
            
            self.completed_batches.append(result)
            logger.info(f"✅ Batch {batch_id} terminé: {jobs_per_second:.1f} jobs/s, {result.success_rate:.1f}% succès")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur critique batch {batch_id}: {e}")
            
            # Résultat d'erreur
            return BatchResult(
                batch_id=batch_id,
                total_jobs=len(jobs),
                successful_jobs=successful_jobs,
                failed_jobs=len(jobs) - successful_jobs,
                processing_time_seconds=time.time() - start_time,
                jobs_per_second=0,
                memory_peak_mb=perf_monitor.get_current_stats()["peak_memory_mb"],
                batch_size_used=self.batch_optimizer.current_batch_size,
                concurrency_used=self.concurrency_manager.current_concurrency,
                performance_rating="failed",
                errors=[{"error": str(e), "type": "critical"}]
            )
    
    async def _create_adaptive_chunks(
        self, 
        jobs: List[BatchJob], 
        initial_batch_size: int
    ) -> AsyncGenerator[List[BatchJob], None]:
        """🔄 Générateur de chunks adaptatifs"""
        current_batch_size = initial_batch_size
        
        for i in range(0, len(jobs), current_batch_size):
            chunk = jobs[i:i + current_batch_size]
            yield chunk
            
            # Ajustement dynamique pour le prochain chunk
            current_batch_size = self.batch_optimizer.current_batch_size
    
    async def _process_chunk_concurrent(
        self,
        chunk: List[BatchJob],
        processor_func: Callable,
        concurrency: int
    ) -> List[Dict[str, Any]]:
        """⚡ Traitement concurrent d'un chunk"""
        semaphore = asyncio.Semaphore(concurrency)
        
        async def process_single_job(job: BatchJob) -> Dict[str, Any]:
            async with semaphore:
                return await self._process_single_job_with_cache(job, processor_func)
        
        # Exécution concurrente
        tasks = [process_single_job(job) for job in chunk]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Traitement des exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "job_id": chunk[i].id,
                    "success": False,
                    "error": str(result),
                    "from_cache": False
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _process_single_job_with_cache(
        self,
        job: BatchJob,
        processor_func: Callable
    ) -> Dict[str, Any]:
        """🎯 Traitement d'un job avec cache intelligent"""
        job.started_at = datetime.now()
        start_time = time.time()
        
        try:
            # Vérification cache si disponible
            if self.cache_manager:
                cache_key = f"job_result_{job.id}_{hash(str(job.data))}"
                cached_result = await self.cache_manager.cache.get(cache_key)
                
                if cached_result is not None:
                    job.completed_at = datetime.now()
                    job.processing_time_ms = (time.time() - start_time) * 1000
                    
                    return {
                        "job_id": job.id,
                        "success": True,
                        "result": cached_result,
                        "from_cache": True,
                        "processing_time_ms": job.processing_time_ms
                    }
            
            # Traitement réel
            if asyncio.iscoroutinefunction(processor_func):
                result = await processor_func(job)
            else:
                # Exécution synchrone dans thread pool
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor(max_workers=1) as executor:
                    result = await loop.run_in_executor(executor, processor_func, job)
            
            # Mise en cache du résultat
            if self.cache_manager and result:
                cache_key = f"job_result_{job.id}_{hash(str(job.data))}"
                await self.cache_manager.cache.set(cache_key, result, 3600)  # 1h TTL
            
            job.completed_at = datetime.now()
            job.processing_time_ms = (time.time() - start_time) * 1000
            
            return {
                "job_id": job.id,
                "success": True,
                "result": result,
                "from_cache": False,
                "processing_time_ms": job.processing_time_ms
            }
            
        except Exception as e:
            job.error = str(e)
            job.retry_count += 1
            job.processing_time_ms = (time.time() - start_time) * 1000
            
            logger.warning(f"⚠️ Erreur job {job.id}: {e} (tentative {job.retry_count}/{job.max_retries})")
            
            return {
                "job_id": job.id,
                "success": False,
                "error": str(e),
                "retry_count": job.retry_count,
                "from_cache": False,
                "processing_time_ms": job.processing_time_ms
            }
    
    def _classify_performance(self, jobs_per_second: float, total_jobs: int) -> str:
        """📊 Classification des performances"""
        # Objectifs: 1000 jobs < 2s = 500 jobs/s minimum
        if jobs_per_second >= 500:
            return "excellent"
        elif jobs_per_second >= 300:
            return "good"
        elif jobs_per_second >= 150:
            return "acceptable"
        elif jobs_per_second >= 50:
            return "poor"
        else:
            return "critical"
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """📊 Statistiques de performance globales"""
        if not self.completed_batches:
            return {"status": "no_data"}
        
        # Agrégation des résultats
        total_jobs = sum(batch.total_jobs for batch in self.completed_batches)
        total_successful = sum(batch.successful_jobs for batch in self.completed_batches)
        total_time = sum(batch.processing_time_seconds for batch in self.completed_batches)
        
        avg_jobs_per_second = sum(batch.jobs_per_second for batch in self.completed_batches) / len(self.completed_batches)
        avg_success_rate = (total_successful / total_jobs) * 100 if total_jobs > 0 else 0
        avg_cache_hit_rate = sum(batch.cache_hit_rate for batch in self.completed_batches) / len(self.completed_batches)
        
        # Performance rating moyen
        ratings = [batch.performance_rating for batch in self.completed_batches]
        rating_counts = {rating: ratings.count(rating) for rating in set(ratings)}
        most_common_rating = max(rating_counts, key=rating_counts.get) if rating_counts else "unknown"
        
        return {
            "batches_processed": len(self.completed_batches),
            "total_jobs_processed": total_jobs,
            "overall_success_rate": round(avg_success_rate, 2),
            "average_jobs_per_second": round(avg_jobs_per_second, 2),
            "average_cache_hit_rate": round(avg_cache_hit_rate, 2),
            "total_processing_time_seconds": round(total_time, 2),
            "current_batch_size": self.batch_optimizer.current_batch_size,
            "current_concurrency": self.concurrency_manager.current_concurrency,
            "predominant_performance_rating": most_common_rating,
            "target_achieved": avg_jobs_per_second >= 500
        }


class PerformanceOptimizer:
    """🎯 Optimiseur de performance global"""
    
    def __init__(self, batch_processor: BatchProcessor):
        self.batch_processor = batch_processor
        self.optimization_history: List[Dict[str, Any]] = []
    
    async def optimize_for_load(
        self,
        expected_job_count: int,
        job_complexity: str = "medium"
    ) -> Dict[str, int]:
        """🎯 Optimisation pour charge attendue"""
        logger.info(f"🎯 Optimisation pour {expected_job_count} jobs (complexité: {job_complexity})")
        
        # Paramètres selon complexité
        complexity_configs = {
            "low": {"batch_size_multiplier": 1.5, "concurrency_multiplier": 1.3},
            "medium": {"batch_size_multiplier": 1.0, "concurrency_multiplier": 1.0},
            "high": {"batch_size_multiplier": 0.7, "concurrency_multiplier": 0.8}
        }
        
        config = complexity_configs.get(job_complexity, complexity_configs["medium"])
        
        # Calcul paramètres optimaux
        if expected_job_count <= 100:
            optimal_batch_size = int(25 * config["batch_size_multiplier"])
            optimal_concurrency = int(5 * config["concurrency_multiplier"])
        elif expected_job_count <= 500:
            optimal_batch_size = int(50 * config["batch_size_multiplier"])
            optimal_concurrency = int(10 * config["concurrency_multiplier"])
        elif expected_job_count <= 1000:
            optimal_batch_size = int(75 * config["batch_size_multiplier"])
            optimal_concurrency = int(15 * config["concurrency_multiplier"])
        else:
            optimal_batch_size = int(100 * config["batch_size_multiplier"])
            optimal_concurrency = int(20 * config["concurrency_multiplier"])
        
        # Application des optimisations
        self.batch_processor.batch_optimizer.current_batch_size = optimal_batch_size
        self.batch_processor.concurrency_manager.current_concurrency = optimal_concurrency
        
        optimization = {
            "batch_size": optimal_batch_size,
            "concurrency": optimal_concurrency,
            "expected_jobs": expected_job_count,
            "complexity": job_complexity,
            "timestamp": datetime.now().isoformat()
        }
        
        self.optimization_history.append(optimization)
        
        logger.info(f"✅ Optimisation appliquée: batch_size={optimal_batch_size}, concurrency={optimal_concurrency}")
        
        return optimization
    
    def get_recommendations(self) -> Dict[str, Any]:
        """💡 Recommandations d'optimisation"""
        stats = self.batch_processor.get_performance_stats()
        
        recommendations = []
        
        # Analyse performance
        if stats.get("average_jobs_per_second", 0) < 200:
            recommendations.append({
                "type": "performance",
                "message": "Performance faible détectée. Considérer augmentation de la concurrence.",
                "action": "increase_concurrency",
                "priority": "high"
            })
        
        # Analyse cache
        if stats.get("average_cache_hit_rate", 0) < 30:
            recommendations.append({
                "type": "cache",
                "message": "Taux de cache faible. Optimiser la stratégie de mise en cache.",
                "action": "optimize_caching",
                "priority": "medium"
            })
        
        # Analyse succès
        if stats.get("overall_success_rate", 0) < 95:
            recommendations.append({
                "type": "reliability",
                "message": "Taux d'échec élevé. Améliorer la gestion d'erreurs.",
                "action": "improve_error_handling",
                "priority": "high"
            })
        
        return {
            "current_performance": stats,
            "recommendations": recommendations,
            "optimization_history": self.optimization_history[-5:]  # 5 dernières
        }
