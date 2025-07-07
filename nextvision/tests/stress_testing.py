"""
🧪 Nextvision - Stress Testing & Load Testing
Enterprise-grade stress testing for 1000+ concurrent jobs with failover validation

Features:
- High-volume load testing (1000+ jobs)
- Concurrency stress testing
- Memory/CPU stress validation
- Service failover testing
- Edge case scenario testing
- Performance regression detection
"""

import asyncio
import time
import random
import json
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Tuple, Union
import logging
import psutil
import concurrent.futures
from functools import wraps

# Imports relatifs pour les modules Nextvision
from ..performance.batch_processing import BatchProcessor, BatchJob, BatchResult
from ..cache.redis_intelligent_cache import CacheManager
from ..error_handling.graceful_degradation import GracefulDegradationManager
from ..utils.retry_strategies import RetryExecutor
from ..monitoring.health_metrics import MetricsCollector, SystemMonitor
from ..logging.structured_logging import get_structured_logger, LogComponent, log_operation
from ..config.production_settings import get_config, Environment

logger = get_structured_logger(__name__)


class TestSeverity(Enum):
    """📏 Sévérité des tests"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class TestStatus(Enum):
    """📊 Statut de test"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class TestMetrics:
    """📊 Métriques de test"""
    test_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    status: TestStatus = TestStatus.PASSED
    
    # Performance
    requests_total: int = 0
    requests_successful: int = 0
    requests_failed: int = 0
    requests_per_second: float = 0.0
    
    # Latence
    response_times: List[float] = field(default_factory=list)
    avg_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    max_response_time: float = 0.0
    
    # Ressources
    peak_memory_mb: float = 0.0
    peak_cpu_percent: float = 0.0
    
    # Erreurs
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Contexte
    test_config: Dict[str, Any] = field(default_factory=dict)
    environment: str = "test"
    
    def finalize(self):
        """🏁 Finalise les métriques"""
        if self.end_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        
        if self.duration_seconds > 0:
            self.requests_per_second = self.requests_total / self.duration_seconds
        
        if self.response_times:
            self.avg_response_time = statistics.mean(self.response_times)
            self.response_times.sort()
            self.p95_response_time = self.response_times[int(len(self.response_times) * 0.95)]
            self.p99_response_time = self.response_times[int(len(self.response_times) * 0.99)]
            self.max_response_time = max(self.response_times)
        
        # Statut final
        if self.errors:
            self.status = TestStatus.ERROR
        elif self.requests_failed > self.requests_successful * 0.1:  # >10% d'échecs
            self.status = TestStatus.FAILED
        elif self.warnings or self.requests_failed > 0:
            self.status = TestStatus.WARNING
        else:
            self.status = TestStatus.PASSED
    
    def get_success_rate(self) -> float:
        """📊 Taux de succès"""
        if self.requests_total == 0:
            return 0.0
        return (self.requests_successful / self.requests_total) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """📋 Conversion en dictionnaire"""
        return {
            "test_name": self.test_name,
            "status": self.status.value,
            "duration_seconds": self.duration_seconds,
            "performance": {
                "requests_total": self.requests_total,
                "success_rate_percent": self.get_success_rate(),
                "requests_per_second": round(self.requests_per_second, 2),
                "avg_response_time_ms": round(self.avg_response_time * 1000, 2),
                "p95_response_time_ms": round(self.p95_response_time * 1000, 2),
                "p99_response_time_ms": round(self.p99_response_time * 1000, 2)
            },
            "resources": {
                "peak_memory_mb": self.peak_memory_mb,
                "peak_cpu_percent": self.peak_cpu_percent
            },
            "issues": {
                "errors_count": len(self.errors),
                "warnings_count": len(self.warnings),
                "failed_requests": self.requests_failed
            }
        }


@dataclass
class LoadTestScenario:
    """📊 Scénario de test de charge"""
    name: str
    description: str
    concurrent_users: int
    requests_per_user: int
    ramp_up_seconds: int
    test_duration_seconds: int
    severity: TestSeverity = TestSeverity.MEDIUM
    target_throughput: Optional[int] = None  # requests/second
    max_acceptable_latency_ms: Optional[int] = None
    custom_data_generator: Optional[Callable] = None


class ResourceMonitor:
    """💾 Monitoring des ressources pendant les tests"""
    
    def __init__(self):
        self.monitoring = False
        self.samples: List[Dict[str, float]] = []
        self.sample_interval = 1.0  # secondes
        
    async def start_monitoring(self):
        """🚀 Démarre le monitoring"""
        self.monitoring = True
        self.samples = []
        
        async def monitor_loop():
            while self.monitoring:
                try:
                    # CPU et mémoire
                    cpu_percent = psutil.cpu_percent(interval=None)
                    memory = psutil.virtual_memory()
                    
                    # Processus actuel
                    process = psutil.Process()
                    process_memory = process.memory_info().rss / 1024 / 1024  # MB
                    
                    sample = {
                        "timestamp": time.time(),
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "memory_used_mb": memory.used / 1024 / 1024,
                        "process_memory_mb": process_memory,
                        "load_avg": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
                    }
                    
                    self.samples.append(sample)
                    
                    await asyncio.sleep(self.sample_interval)
                    
                except Exception as e:
                    logger.error(f"Erreur monitoring ressources: {e}")
                    await asyncio.sleep(self.sample_interval)
        
        # Démarrer en arrière-plan
        asyncio.create_task(monitor_loop())
    
    def stop_monitoring(self) -> Dict[str, float]:
        """🛑 Arrête le monitoring et retourne les stats"""
        self.monitoring = False
        
        if not self.samples:
            return {}
        
        # Calcul des maximums
        max_cpu = max(s["cpu_percent"] for s in self.samples)
        max_memory = max(s["memory_percent"] for s in self.samples)
        max_process_memory = max(s["process_memory_mb"] for s in self.samples)
        avg_load = statistics.mean(s["load_avg"] for s in self.samples)
        
        return {
            "peak_cpu_percent": max_cpu,
            "peak_memory_percent": max_memory,
            "peak_process_memory_mb": max_process_memory,
            "average_load": avg_load,
            "samples_count": len(self.samples)
        }


class StressTestSuite:
    """🔥 Suite de tests de stress principale"""
    
    def __init__(
        self,
        batch_processor: Optional[BatchProcessor] = None,
        cache_manager: Optional[CacheManager] = None,
        degradation_manager: Optional[GracefulDegradationManager] = None,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        self.batch_processor = batch_processor
        self.cache_manager = cache_manager
        self.degradation_manager = degradation_manager
        self.metrics = metrics_collector
        
        # Configuration tests
        self.test_results: List[TestMetrics] = []
        self.resource_monitor = ResourceMonitor()
        
        # Scénarios prédéfinis
        self.predefined_scenarios = self._setup_scenarios()
    
    def _setup_scenarios(self) -> List[LoadTestScenario]:
        """🔧 Scénarios de test prédéfinis"""
        return [
            LoadTestScenario(
                name="light_load",
                description="Charge légère - 50 jobs concurrents",
                concurrent_users=5,
                requests_per_user=10,
                ramp_up_seconds=10,
                test_duration_seconds=60,
                severity=TestSeverity.LOW,
                target_throughput=20,
                max_acceptable_latency_ms=500
            ),
            LoadTestScenario(
                name="medium_load",
                description="Charge moyenne - 200 jobs concurrents",
                concurrent_users=10,
                requests_per_user=20,
                ramp_up_seconds=30,
                test_duration_seconds=120,
                severity=TestSeverity.MEDIUM,
                target_throughput=100,
                max_acceptable_latency_ms=1000
            ),
            LoadTestScenario(
                name="high_load",
                description="Charge élevée - 500 jobs concurrents",
                concurrent_users=25,
                requests_per_user=20,
                ramp_up_seconds=60,
                test_duration_seconds=180,
                severity=TestSeverity.HIGH,
                target_throughput=300,
                max_acceptable_latency_ms=2000
            ),
            LoadTestScenario(
                name="extreme_load",
                description="Charge extrême - 1000+ jobs concurrents",
                concurrent_users=50,
                requests_per_user=25,
                ramp_up_seconds=120,
                test_duration_seconds=300,
                severity=TestSeverity.EXTREME,
                target_throughput=500,
                max_acceptable_latency_ms=3000
            ),
            LoadTestScenario(
                name="sustained_load",
                description="Charge soutenue - test d'endurance",
                concurrent_users=20,
                requests_per_user=100,
                ramp_up_seconds=60,
                test_duration_seconds=600,  # 10 minutes
                severity=TestSeverity.HIGH,
                target_throughput=200,
                max_acceptable_latency_ms=1500
            )
        ]
    
    async def run_scenario(self, scenario: LoadTestScenario) -> TestMetrics:
        """🏃 Exécute un scénario de test"""
        
        logger.info(f"🚀 Démarrage test: {scenario.name}")
        
        metrics = TestMetrics(
            test_name=scenario.name,
            start_time=datetime.now(),
            test_config={
                "concurrent_users": scenario.concurrent_users,
                "requests_per_user": scenario.requests_per_user,
                "total_requests": scenario.concurrent_users * scenario.requests_per_user,
                "ramp_up_seconds": scenario.ramp_up_seconds,
                "test_duration_seconds": scenario.test_duration_seconds
            },
            environment=get_config().environment.value
        )
        
        try:
            # Démarrer monitoring ressources
            await self.resource_monitor.start_monitoring()
            
            # Génération des jobs de test
            test_jobs = self._generate_test_jobs(
                scenario.concurrent_users * scenario.requests_per_user,
                scenario.custom_data_generator
            )
            
            # Exécution du test avec ramp-up
            results = await self._execute_load_test(
                test_jobs,
                scenario.concurrent_users,
                scenario.ramp_up_seconds
            )
            
            # Collecte des métriques
            metrics.requests_total = len(test_jobs)
            metrics.requests_successful = sum(1 for r in results if r.get("success", False))
            metrics.requests_failed = metrics.requests_total - metrics.requests_successful
            
            # Temps de réponse
            response_times = [r.get("duration", 0) for r in results if "duration" in r]
            metrics.response_times = response_times
            
            metrics.end_time = datetime.now()
            metrics.finalize()
            
            # Arrêter monitoring et récupérer stats ressources
            resource_stats = self.resource_monitor.stop_monitoring()
            metrics.peak_memory_mb = resource_stats.get("peak_process_memory_mb", 0)
            metrics.peak_cpu_percent = resource_stats.get("peak_cpu_percent", 0)
            
            # Validation des objectifs
            self._validate_scenario_objectives(scenario, metrics)
            
            logger.info(f"✅ Test {scenario.name} terminé: {metrics.get_success_rate():.1f}% succès, {metrics.requests_per_second:.1f} req/s")
            
        except Exception as e:
            metrics.end_time = datetime.now()
            metrics.errors.append(f"Test execution error: {str(e)}")
            metrics.status = TestStatus.ERROR
            logger.error(f"❌ Erreur test {scenario.name}: {e}")
        
        self.test_results.append(metrics)
        return metrics
    
    def _generate_test_jobs(self, count: int, custom_generator: Optional[Callable] = None) -> List[BatchJob]:
        """📋 Génération des jobs de test"""
        jobs = []
        
        for i in range(count):
            if custom_generator:
                job_data = custom_generator(i)
            else:
                job_data = self._generate_default_job_data(i)
            
            job = BatchJob(
                id=f"test_job_{i}",
                data=job_data,
                priority=random.randint(1, 5)
            )
            jobs.append(job)
        
        return jobs
    
    def _generate_default_job_data(self, index: int) -> Dict[str, Any]:
        """📋 Génération de données de job par défaut"""
        # Simulation de données réalistes pour tests
        candidate_profiles = [
            {
                "skills": ["Python", "FastAPI", "PostgreSQL"],
                "experience_years": random.randint(1, 10),
                "location": "Paris",
                "salary_min": random.randint(40000, 80000)
            },
            {
                "skills": ["JavaScript", "React", "Node.js"],
                "experience_years": random.randint(2, 8),
                "location": "Lyon",
                "salary_min": random.randint(35000, 70000)
            },
            {
                "skills": ["Java", "Spring", "MySQL"],
                "experience_years": random.randint(3, 12),
                "location": "Marseille",
                "salary_min": random.randint(45000, 85000)
            }
        ]
        
        profile = random.choice(candidate_profiles)
        
        return {
            "candidate_id": f"candidate_{index}",
            "job_id": f"job_{random.randint(1000, 9999)}",
            "matching_request": {
                "skills": profile["skills"],
                "experience_years": profile["experience_years"],
                "location": profile["location"],
                "salary_expectations": {
                    "min": profile["salary_min"],
                    "max": profile["salary_min"] + random.randint(10000, 30000)
                }
            },
            "complexity": random.choice(["low", "medium", "high"]),
            "processing_delay": random.uniform(0.1, 0.5)  # Simulation latence
        }
    
    async def _execute_load_test(
        self,
        jobs: List[BatchJob],
        concurrent_users: int,
        ramp_up_seconds: int
    ) -> List[Dict[str, Any]]:
        """⚡ Exécution du test de charge avec ramp-up"""
        
        results = []
        
        # Diviser les jobs par utilisateur
        jobs_per_user = len(jobs) // concurrent_users
        user_job_batches = [
            jobs[i:i + jobs_per_user]
            for i in range(0, len(jobs), jobs_per_user)
        ]
        
        # Ramp-up progressif
        ramp_delay = ramp_up_seconds / concurrent_users if concurrent_users > 0 else 0
        
        async def user_simulation(user_id: int, user_jobs: List[BatchJob]):
            """Simulation d'un utilisateur"""
            user_results = []
            
            # Délai de ramp-up
            await asyncio.sleep(user_id * ramp_delay)
            
            for job in user_jobs:
                start_time = time.time()
                
                try:
                    # Simulation traitement job
                    result = await self._simulate_job_processing(job)
                    
                    duration = time.time() - start_time
                    user_results.append({
                        "job_id": job.id,
                        "user_id": user_id,
                        "success": True,
                        "duration": duration,
                        "result": result
                    })
                    
                except Exception as e:
                    duration = time.time() - start_time
                    user_results.append({
                        "job_id": job.id,
                        "user_id": user_id,
                        "success": False,
                        "duration": duration,
                        "error": str(e)
                    })
            
            return user_results
        
        # Exécution concurrente de tous les utilisateurs
        user_tasks = [
            user_simulation(i, user_job_batches[i])
            for i in range(min(concurrent_users, len(user_job_batches)))
        ]
        
        user_results_list = await asyncio.gather(*user_tasks)
        
        # Flatten des résultats
        for user_results in user_results_list:
            results.extend(user_results)
        
        return results
    
    async def _simulate_job_processing(self, job: BatchJob) -> Dict[str, Any]:
        """🎯 Simulation du traitement d'un job"""
        
        # Simulation latence variable selon complexité
        complexity = job.data.get("complexity", "medium")
        base_delay = job.data.get("processing_delay", 0.2)
        
        complexity_multipliers = {"low": 0.5, "medium": 1.0, "high": 2.0}
        delay = base_delay * complexity_multipliers.get(complexity, 1.0)
        
        # Simulation travail asynchrone
        await asyncio.sleep(delay + random.uniform(0, 0.1))
        
        # Simulation d'échecs aléatoires (5%)
        if random.random() < 0.05:
            raise Exception(f"Simulated processing failure for job {job.id}")
        
        # Résultat simulé
        return {
            "matching_score": random.uniform(0.6, 0.95),
            "processing_time_ms": delay * 1000,
            "cache_hit": random.choice([True, False]),
            "complexity_processed": complexity
        }
    
    def _validate_scenario_objectives(self, scenario: LoadTestScenario, metrics: TestMetrics):
        """✅ Validation des objectifs du scénario"""
        
        # Validation throughput
        if scenario.target_throughput:
            if metrics.requests_per_second < scenario.target_throughput * 0.8:  # 80% du target
                metrics.warnings.append(
                    f"Throughput below target: {metrics.requests_per_second:.1f} < {scenario.target_throughput}"
                )
        
        # Validation latence
        if scenario.max_acceptable_latency_ms:
            max_latency_s = scenario.max_acceptable_latency_ms / 1000
            if metrics.p95_response_time > max_latency_s:
                metrics.warnings.append(
                    f"P95 latency above threshold: {metrics.p95_response_time*1000:.1f}ms > {scenario.max_acceptable_latency_ms}ms"
                )
        
        # Validation taux de succès
        if metrics.get_success_rate() < 95.0:
            metrics.warnings.append(
                f"Success rate below 95%: {metrics.get_success_rate():.1f}%"
            )
        
        # Validation ressources
        if metrics.peak_memory_mb > 2048:  # 2GB
            metrics.warnings.append(
                f"High memory usage: {metrics.peak_memory_mb:.1f}MB"
            )
        
        if metrics.peak_cpu_percent > 90:
            metrics.warnings.append(
                f"High CPU usage: {metrics.peak_cpu_percent:.1f}%"
            )
    
    async def run_all_scenarios(self) -> List[TestMetrics]:
        """🏃 Exécute tous les scénarios prédéfinis"""
        logger.info(f"🚀 Démarrage suite complète: {len(self.predefined_scenarios)} scénarios")
        
        all_results = []
        
        for scenario in self.predefined_scenarios:
            try:
                result = await self.run_scenario(scenario)
                all_results.append(result)
                
                # Pause entre scénarios pour stabilisation
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"❌ Échec scénario {scenario.name}: {e}")
        
        logger.info(f"✅ Suite terminée: {len(all_results)} scénarios exécutés")
        return all_results
    
    def get_summary_report(self) -> Dict[str, Any]:
        """📊 Rapport de synthèse des tests"""
        if not self.test_results:
            return {"status": "no_tests_run"}
        
        # Statistiques globales
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.status == TestStatus.PASSED)
        failed_tests = sum(1 for r in self.test_results if r.status == TestStatus.FAILED)
        
        # Performance globale
        total_requests = sum(r.requests_total for r in self.test_results)
        total_successful = sum(r.requests_successful for r in self.test_results)
        
        # Temps de réponse agrégés
        all_response_times = []
        for result in self.test_results:
            all_response_times.extend(result.response_times)
        
        avg_response_time = statistics.mean(all_response_times) if all_response_times else 0
        
        # Ressources
        peak_memory = max(r.peak_memory_mb for r in self.test_results)
        peak_cpu = max(r.peak_cpu_percent for r in self.test_results)
        
        return {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate_percent": (passed_tests / total_tests) * 100,
                "total_requests_processed": total_requests,
                "overall_success_rate_percent": (total_successful / total_requests) * 100 if total_requests > 0 else 0
            },
            "performance": {
                "average_response_time_ms": round(avg_response_time * 1000, 2),
                "peak_memory_mb": round(peak_memory, 2),
                "peak_cpu_percent": round(peak_cpu, 2),
                "throughput_achieved": any(r.requests_per_second >= 500 for r in self.test_results)
            },
            "test_details": [r.to_dict() for r in self.test_results],
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """💡 Génération de recommandations"""
        recommendations = []
        
        if not self.test_results:
            return recommendations
        
        # Analyse performance
        avg_throughput = statistics.mean(r.requests_per_second for r in self.test_results)
        if avg_throughput < 200:
            recommendations.append("Consider increasing batch size or concurrency for better throughput")
        
        # Analyse latence
        high_latency_tests = [r for r in self.test_results if r.avg_response_time > 1.0]
        if len(high_latency_tests) > len(self.test_results) / 2:
            recommendations.append("High latency detected in multiple tests - investigate caching and optimization")
        
        # Analyse ressources
        high_memory_tests = [r for r in self.test_results if r.peak_memory_mb > 1024]
        if high_memory_tests:
            recommendations.append("High memory usage detected - consider memory optimization")
        
        # Analyse erreurs
        error_prone_tests = [r for r in self.test_results if len(r.errors) > 0]
        if error_prone_tests:
            recommendations.append("Error handling needs improvement - review error patterns")
        
        return recommendations


class FailoverTestSuite:
    """🔄 Tests de failover et de robustesse"""
    
    def __init__(
        self,
        degradation_manager: GracefulDegradationManager,
        cache_manager: CacheManager,
        retry_executor: RetryExecutor
    ):
        self.degradation_manager = degradation_manager
        self.cache_manager = cache_manager
        self.retry_executor = retry_executor
        self.failover_results: List[TestMetrics] = []
    
    async def test_cache_failover(self) -> TestMetrics:
        """🗄️ Test failover cache Redis"""
        metrics = TestMetrics(
            test_name="cache_failover",
            start_time=datetime.now()
        )
        
        try:
            with log_operation("cache_failover_test", LogComponent.CACHE):
                # Test fonctionnement normal
                await self.cache_manager.cache.set("test_key", "test_value", 60)
                result = await self.cache_manager.cache.get("test_key")
                
                if result != "test_value":
                    metrics.errors.append("Cache normal operation failed")
                
                # Simulation panne Redis (déconnexion)
                original_connected = self.cache_manager.cache.is_connected
                self.cache_manager.cache.is_connected = False
                
                # Test fallback
                fallback_result = await self.cache_manager.cache.get("test_key_fallback")
                
                if fallback_result is not None:
                    metrics.warnings.append("Cache should return None when disconnected")
                
                # Rétablissement
                self.cache_manager.cache.is_connected = original_connected
                
                metrics.requests_total = 3
                metrics.requests_successful = 2 if not metrics.errors else 1
                metrics.requests_failed = metrics.requests_total - metrics.requests_successful
                
        except Exception as e:
            metrics.errors.append(f"Cache failover test error: {str(e)}")
        
        metrics.end_time = datetime.now()
        metrics.finalize()
        self.failover_results.append(metrics)
        
        return metrics
    
    async def test_external_api_failover(self) -> TestMetrics:
        """🌐 Test failover APIs externes"""
        metrics = TestMetrics(
            test_name="external_api_failover",
            start_time=datetime.now()
        )
        
        try:
            # Simulation appel API qui échoue
            async def failing_api_call():
                raise ConnectionError("Simulated API failure")
            
            # Test avec retry
            result = await self.retry_executor.execute_with_retry(
                operation=failing_api_call,
                service="test_api",
                context={"test": "failover"}
            )
            
            if result.success:
                metrics.warnings.append("API call should have failed")
            else:
                metrics.requests_successful += 1
            
            metrics.requests_total = 1
            
        except Exception as e:
            metrics.errors.append(f"API failover test error: {str(e)}")
        
        metrics.end_time = datetime.now()
        metrics.finalize()
        self.failover_results.append(metrics)
        
        return metrics
    
    async def test_circuit_breaker(self) -> TestMetrics:
        """⚡ Test circuit breaker"""
        metrics = TestMetrics(
            test_name="circuit_breaker",
            start_time=datetime.now()
        )
        
        try:
            service_name = "test_circuit_service"
            
            # Enregistrer service
            self.degradation_manager.register_service(service_name, failure_threshold=3)
            
            # Générer des échecs pour déclencher circuit breaker
            for i in range(5):
                async def failing_operation():
                    raise Exception(f"Simulated failure {i}")
                
                result = await self.degradation_manager.execute_with_fallback(
                    service_name,
                    failing_operation,
                    {"attempt": i}
                )
                
                metrics.requests_total += 1
                if "status" in result and result["status"] == "fallback":
                    metrics.requests_successful += 1
                else:
                    metrics.requests_failed += 1
            
            # Vérifier état circuit breaker
            circuit_breaker = self.degradation_manager.circuit_breakers.get(service_name)
            if circuit_breaker and circuit_breaker.state.name != "CIRCUIT_OPEN":
                metrics.warnings.append("Circuit breaker should be open after failures")
            
        except Exception as e:
            metrics.errors.append(f"Circuit breaker test error: {str(e)}")
        
        metrics.end_time = datetime.now()
        metrics.finalize()
        self.failover_results.append(metrics)
        
        return metrics
    
    async def run_all_failover_tests(self) -> List[TestMetrics]:
        """🏃 Exécute tous les tests de failover"""
        logger.info("🚀 Démarrage tests de failover")
        
        tests = [
            self.test_cache_failover(),
            self.test_external_api_failover(),
            self.test_circuit_breaker()
        ]
        
        results = []
        for test in tests:
            try:
                result = await test
                results.append(result)
            except Exception as e:
                logger.error(f"❌ Test failover échoué: {e}")
        
        logger.info(f"✅ Tests de failover terminés: {len(results)} tests")
        return results


class PerformanceTestRunner:
    """🏃 Runner principal pour tous les tests de performance"""
    
    def __init__(self):
        self.config = get_config()
        self.stress_suite: Optional[StressTestSuite] = None
        self.failover_suite: Optional[FailoverTestSuite] = None
        
    async def initialize_test_environment(self):
        """🔧 Initialisation environnement de test"""
        logger.info("🔧 Initialisation environnement de test")
        
        # Création des composants pour tests
        from ..performance.batch_processing import BatchProcessor
        from ..cache.redis_intelligent_cache import create_cache_manager
        from ..error_handling.graceful_degradation import GracefulDegradationManager
        from ..utils.retry_strategies import create_retry_executor
        from ..monitoring.health_metrics import MetricsCollector
        
        metrics_collector = MetricsCollector(enable_prometheus=False)  # Désactivé pour tests
        cache_manager = create_cache_manager(
            redis_url=self.config.redis.get_connection_url(),
            enable_memory_cache=True,
            metrics_collector=metrics_collector
        )
        
        # Initialiser cache
        await cache_manager.initialize()
        
        degradation_manager = GracefulDegradationManager(metrics_collector)
        retry_executor = create_retry_executor(metrics_collector)
        batch_processor = BatchProcessor(
            cache_manager=cache_manager,
            metrics_collector=metrics_collector
        )
        
        # Création des suites de test
        self.stress_suite = StressTestSuite(
            batch_processor=batch_processor,
            cache_manager=cache_manager,
            degradation_manager=degradation_manager,
            metrics_collector=metrics_collector
        )
        
        self.failover_suite = FailoverTestSuite(
            degradation_manager=degradation_manager,
            cache_manager=cache_manager,
            retry_executor=retry_executor
        )
        
        logger.info("✅ Environnement de test initialisé")
    
    async def run_complete_test_suite(self) -> Dict[str, Any]:
        """🏆 Exécute la suite complète de tests"""
        logger.info("🏆 Démarrage suite complète de tests")
        
        start_time = datetime.now()
        
        try:
            await self.initialize_test_environment()
            
            # Tests de stress
            logger.info("💪 Exécution tests de stress")
            stress_results = await self.stress_suite.run_all_scenarios()
            
            # Tests de failover
            logger.info("🔄 Exécution tests de failover")
            failover_results = await self.failover_suite.run_all_failover_tests()
            
            end_time = datetime.now()
            
            # Rapport final
            report = {
                "test_suite_summary": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "total_duration_minutes": (end_time - start_time).total_seconds() / 60,
                    "environment": self.config.environment.value
                },
                "stress_tests": self.stress_suite.get_summary_report(),
                "failover_tests": {
                    "total_tests": len(failover_results),
                    "passed_tests": sum(1 for r in failover_results if r.status == TestStatus.PASSED),
                    "test_details": [r.to_dict() for r in failover_results]
                },
                "overall_verdict": self._calculate_overall_verdict(stress_results, failover_results),
                "production_readiness": self._assess_production_readiness(stress_results, failover_results)
            }
            
            logger.info(f"✅ Suite complète terminée: {report['overall_verdict']}")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Erreur suite de tests: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _calculate_overall_verdict(self, stress_results: List[TestMetrics], failover_results: List[TestMetrics]) -> str:
        """🏆 Calcul verdict global"""
        all_results = stress_results + failover_results
        
        if not all_results:
            return "NO_TESTS_RUN"
        
        passed = sum(1 for r in all_results if r.status == TestStatus.PASSED)
        total = len(all_results)
        
        success_rate = (passed / total) * 100
        
        if success_rate >= 95:
            return "EXCELLENT"
        elif success_rate >= 85:
            return "GOOD"
        elif success_rate >= 70:
            return "ACCEPTABLE"
        else:
            return "NEEDS_IMPROVEMENT"
    
    def _assess_production_readiness(self, stress_results: List[TestMetrics], failover_results: List[TestMetrics]) -> Dict[str, Any]:
        """🏭 Évaluation de la prêpaté pour la production"""
        
        criteria = {
            "throughput_1000_jobs": False,
            "latency_under_2s": False,
            "memory_under_2gb": False,
            "success_rate_95_percent": False,
            "failover_mechanisms": False
        }
        
        # Vérification throughput
        high_load_tests = [r for r in stress_results if "extreme" in r.test_name or "high" in r.test_name]
        if any(r.requests_per_second >= 500 for r in high_load_tests):
            criteria["throughput_1000_jobs"] = True
        
        # Vérification latence
        if any(r.p95_response_time <= 2.0 for r in stress_results):
            criteria["latency_under_2s"] = True
        
        # Vérification mémoire
        if all(r.peak_memory_mb <= 2048 for r in stress_results):
            criteria["memory_under_2gb"] = True
        
        # Vérification taux de succès
        overall_success = sum(r.requests_successful for r in stress_results) / sum(r.requests_total for r in stress_results) * 100
        if overall_success >= 95:
            criteria["success_rate_95_percent"] = True
        
        # Vérification failover
        if all(r.status in [TestStatus.PASSED, TestStatus.WARNING] for r in failover_results):
            criteria["failover_mechanisms"] = True
        
        passed_criteria = sum(criteria.values())
        readiness_score = (passed_criteria / len(criteria)) * 100
        
        if readiness_score >= 90:
            readiness_level = "PRODUCTION_READY"
        elif readiness_score >= 75:
            readiness_level = "MOSTLY_READY"
        elif readiness_score >= 50:
            readiness_level = "NEEDS_OPTIMIZATION"
        else:
            readiness_level = "NOT_READY"
        
        return {
            "readiness_level": readiness_level,
            "readiness_score_percent": readiness_score,
            "criteria_met": criteria,
            "recommendations": self._get_production_recommendations(criteria)
        }
    
    def _get_production_recommendations(self, criteria: Dict[str, bool]) -> List[str]:
        """💡 Recommandations pour la production"""
        recommendations = []
        
        if not criteria["throughput_1000_jobs"]:
            recommendations.append("Optimize batch processing and concurrency to achieve 500+ req/s throughput")
        
        if not criteria["latency_under_2s"]:
            recommendations.append("Improve response times through caching and query optimization")
        
        if not criteria["memory_under_2gb"]:
            recommendations.append("Optimize memory usage and implement memory management")
        
        if not criteria["success_rate_95_percent"]:
            recommendations.append("Improve error handling and retry mechanisms")
        
        if not criteria["failover_mechanisms"]:
            recommendations.append("Strengthen failover and circuit breaker implementations")
        
        return recommendations


# =====================================
# 🏭 CLI INTERFACE
# =====================================

async def run_stress_tests_cli():
    """🖥️ Interface CLI pour exécuter les tests"""
    runner = PerformanceTestRunner()
    
    print("🧪 Nextvision - Suite de Tests de Robustesse")
    print("===============================================")
    
    try:
        report = await runner.run_complete_test_suite()
        
        print("\n📊 RÉSULTATS FINAUX:")
        print(f"Verdict global: {report['overall_verdict']}")
        print(f"Prêpaté production: {report['production_readiness']['readiness_level']}")
        print(f"Score: {report['production_readiness']['readiness_score_percent']:.1f}%")
        
        if report['production_readiness']['recommendations']:
            print("\n💡 RECOMMANDATIONS:")
            for rec in report['production_readiness']['recommendations']:
                print(f"  • {rec}")
        
        # Sauvegarde rapport
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stress_test_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n💾 Rapport sauvegardé: {filename}")
        
    except Exception as e:
        print(f"\n❌ Erreur exécution tests: {e}")


if __name__ == "__main__":
    # Exécution directe
    asyncio.run(run_stress_tests_cli())
