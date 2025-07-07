"""
📊 Nextvision - Health Monitoring & Real-time Metrics
Enterprise-grade monitoring with comprehensive health checks and performance metrics

Features:
- Real-time performance metrics
- System resource monitoring
- Service health tracking
- Alert management
- Dashboard-ready metrics
"""

import asyncio
import time
import psutil
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
import json
import logging
from collections import defaultdict, deque

try:
    from prometheus_client import Counter, Histogram, Gauge, Info, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from ..logging.structured_logging import get_structured_logger

logger = get_structured_logger(__name__)


class MetricType(Enum):
    """📏 Types de métriques"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    INFO = "info"


class HealthStatus(Enum):
    """❤️ États de santé"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class AlertSeverity(Enum):
    """🚨 Niveaux d'alerte"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetricValue:
    """📊 Valeur de métrique avec métadonnées"""
    name: str
    value: Union[int, float]
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


@dataclass
class ServiceHealth:
    """❤️ État de santé d'un service"""
    service_name: str
    status: HealthStatus
    last_check: datetime
    response_time_ms: float
    success_rate: float
    error_count: int
    uptime_seconds: float
    details: Dict[str, Any] = field(default_factory=dict)
    alerts: List[str] = field(default_factory=list)


@dataclass
class SystemResources:
    """💾 Ressources système"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_percent: float
    disk_used_gb: float
    network_bytes_sent: int
    network_bytes_recv: int
    load_average: List[float]
    timestamp: datetime = field(default_factory=datetime.now)


class MetricsCollector:
    """📊 Collecteur de métriques central"""
    
    def __init__(
        self,
        enable_prometheus: bool = True,
        prometheus_port: int = 8090,
        retention_hours: int = 24
    ):
        self.enable_prometheus = enable_prometheus and PROMETHEUS_AVAILABLE
        self.prometheus_port = prometheus_port
        self.retention_hours = retention_hours
        
        # Stockage des métriques
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.current_metrics: Dict[str, MetricValue] = {}
        
        # Métriques Prometheus si disponible
        self.prometheus_metrics: Dict[str, Any] = {}
        
        # Statistiques d'usage
        self.stats = {
            "metrics_collected": 0,
            "alerts_generated": 0,
            "start_time": datetime.now()
        }
        
        # Initialisation
        if self.enable_prometheus:
            self._setup_prometheus()
    
    def _setup_prometheus(self):
        """🔧 Configuration Prometheus"""
        try:
            # Métriques core Nextvision
            self.prometheus_metrics.update({
                # Performance
                "api_requests_total": Counter(
                    "nextvision_api_requests_total",
                    "Total API requests",
                    ["endpoint", "method", "status"]
                ),
                "api_request_duration": Histogram(
                    "nextvision_api_request_duration_seconds",
                    "API request duration",
                    ["endpoint", "method"]
                ),
                "matching_jobs_processed": Counter(
                    "nextvision_matching_jobs_processed_total",
                    "Total matching jobs processed",
                    ["status"]
                ),
                "matching_duration": Histogram(
                    "nextvision_matching_duration_seconds",
                    "Matching job duration",
                    ["job_type"]
                ),
                
                # Cache
                "cache_operations": Counter(
                    "nextvision_cache_operations_total",
                    "Cache operations",
                    ["operation", "cache_type", "result"]
                ),
                "cache_hit_rate": Gauge(
                    "nextvision_cache_hit_rate",
                    "Cache hit rate percentage",
                    ["cache_type"]
                ),
                
                # Services externes
                "external_api_calls": Counter(
                    "nextvision_external_api_calls_total",
                    "External API calls",
                    ["service", "status"]
                ),
                "external_api_duration": Histogram(
                    "nextvision_external_api_duration_seconds",
                    "External API call duration",
                    ["service"]
                ),
                
                # Système
                "system_cpu_usage": Gauge(
                    "nextvision_system_cpu_usage_percent",
                    "System CPU usage percentage"
                ),
                "system_memory_usage": Gauge(
                    "nextvision_system_memory_usage_percent",
                    "System memory usage percentage"
                ),
                "system_disk_usage": Gauge(
                    "nextvision_system_disk_usage_percent",
                    "System disk usage percentage"
                ),
                
                # Business metrics
                "active_candidates": Gauge(
                    "nextvision_active_candidates",
                    "Number of active candidates"
                ),
                "job_matches_per_hour": Gauge(
                    "nextvision_job_matches_per_hour",
                    "Job matches generated per hour"
                ),
                "error_rate": Gauge(
                    "nextvision_error_rate_percent",
                    "Overall error rate percentage",
                    ["service"]
                )
            })
            
            # Démarrer serveur Prometheus
            start_http_server(self.prometheus_port)
            logger.info(f"📊 Serveur Prometheus démarré sur port {self.prometheus_port}")
            
        except Exception as e:
            logger.error(f"❌ Erreur setup Prometheus: {e}")
            self.enable_prometheus = False
    
    def increment_counter(
        self, 
        name: str, 
        value: float = 1.0, 
        labels: Dict[str, str] = None
    ):
        """📈 Incrémenter un compteur"""
        labels = labels or {}
        
        # Stockage interne
        metric = MetricValue(
            name=name,
            value=value,
            timestamp=datetime.now(),
            labels=labels,
            metric_type=MetricType.COUNTER
        )
        
        self._store_metric(metric)
        
        # Prometheus si disponible
        if self.enable_prometheus and name in self.prometheus_metrics:
            if labels:
                self.prometheus_metrics[name].labels(**labels).inc(value)
            else:
                self.prometheus_metrics[name].inc(value)
    
    def record_gauge(
        self, 
        name: str, 
        value: float, 
        labels: Dict[str, str] = None
    ):
        """📏 Enregistrer une jauge"""
        labels = labels or {}
        
        metric = MetricValue(
            name=name,
            value=value,
            timestamp=datetime.now(),
            labels=labels,
            metric_type=MetricType.GAUGE
        )
        
        self._store_metric(metric)
        
        # Prometheus
        if self.enable_prometheus and name in self.prometheus_metrics:
            if labels:
                self.prometheus_metrics[name].labels(**labels).set(value)
            else:
                self.prometheus_metrics[name].set(value)
    
    def record_timer(
        self, 
        name: str, 
        duration: float, 
        labels: Dict[str, str] = None
    ):
        """⏱️ Enregistrer une durée"""
        labels = labels or {}
        
        metric = MetricValue(
            name=name,
            value=duration,
            timestamp=datetime.now(),
            labels=labels,
            metric_type=MetricType.TIMER
        )
        
        self._store_metric(metric)
        
        # Prometheus histogram
        histogram_name = name.replace("_time", "_duration")
        if self.enable_prometheus and histogram_name in self.prometheus_metrics:
            if labels:
                self.prometheus_metrics[histogram_name].labels(**labels).observe(duration)
            else:
                self.prometheus_metrics[histogram_name].observe(duration)
    
    def record_histogram(
        self, 
        name: str, 
        value: float, 
        labels: Dict[str, str] = None
    ):
        """📊 Enregistrer dans un histogramme"""
        self.record_timer(name, value, labels)  # Same logic
    
    def _store_metric(self, metric: MetricValue):
        """💾 Stockage interne de métrique"""
        key = f"{metric.name}_{json.dumps(metric.labels, sort_keys=True)}"
        
        self.metrics_history[key].append(metric)
        self.current_metrics[key] = metric
        self.stats["metrics_collected"] += 1
        
        # Nettoyage automatique
        self._cleanup_old_metrics()
    
    def _cleanup_old_metrics(self):
        """🧹 Nettoyage des métriques anciennes"""
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        
        for key, history in self.metrics_history.items():
            # Supprimer les métriques trop anciennes
            while history and history[0].timestamp < cutoff_time:
                history.popleft()
    
    def get_metric_summary(self, name: str, hours: int = 1) -> Dict[str, Any]:
        """📊 Résumé d'une métrique"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Collecter toutes les valeurs pour cette métrique
        values = []
        for key, history in self.metrics_history.items():
            if key.startswith(name):
                recent_values = [
                    m.value for m in history 
                    if m.timestamp >= cutoff_time
                ]
                values.extend(recent_values)
        
        if not values:
            return {"status": "no_data"}
        
        # Calculs statistiques
        return {
            "metric_name": name,
            "time_window_hours": hours,
            "sample_count": len(values),
            "current_value": values[-1] if values else None,
            "min_value": min(values),
            "max_value": max(values),
            "avg_value": sum(values) / len(values),
            "sum_value": sum(values),
            "recent_trend": self._calculate_trend(values)
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """📈 Calcul de tendance"""
        if len(values) < 2:
            return "stable"
        
        recent_half = values[len(values)//2:]
        older_half = values[:len(values)//2]
        
        if not older_half or not recent_half:
            return "stable"
        
        recent_avg = sum(recent_half) / len(recent_half)
        older_avg = sum(older_half) / len(older_half)
        
        change_percent = ((recent_avg - older_avg) / older_avg) * 100 if older_avg != 0 else 0
        
        if change_percent > 10:
            return "increasing"
        elif change_percent < -10:
            return "decreasing"
        else:
            return "stable"
    
    def get_all_metrics_summary(self) -> Dict[str, Any]:
        """📊 Résumé de toutes les métriques"""
        # Métriques uniques
        unique_metrics = set()
        for key in self.metrics_history.keys():
            metric_name = key.split("_{")[0]  # Enlever les labels
            unique_metrics.add(metric_name)
        
        summaries = {}
        for metric_name in unique_metrics:
            summaries[metric_name] = self.get_metric_summary(metric_name)
        
        return {
            "collector_stats": self.stats,
            "metrics_count": len(unique_metrics),
            "prometheus_enabled": self.enable_prometheus,
            "metric_summaries": summaries
        }


class SystemMonitor:
    """💾 Monitoring des ressources système"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.monitoring_active = False
        self.monitor_thread = None
        self.monitor_interval = 30  # secondes
    
    def start_monitoring(self):
        """🚀 Démarre le monitoring système"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("💾 Monitoring système démarré")
    
    def stop_monitoring(self):
        """🛑 Arrête le monitoring système"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info("💾 Monitoring système arrêté")
    
    def _monitor_loop(self):
        """🔄 Boucle de monitoring"""
        while self.monitoring_active:
            try:
                resources = self.get_system_resources()
                self._record_system_metrics(resources)
                time.sleep(self.monitor_interval)
            except Exception as e:
                logger.error(f"❌ Erreur monitoring système: {e}")
                time.sleep(self.monitor_interval)
    
    def get_system_resources(self) -> SystemResources:
        """📊 Collecte des ressources système"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Mémoire
            memory = psutil.virtual_memory()
            
            # Disque
            disk = psutil.disk_usage('/')
            
            # Réseau
            network = psutil.net_io_counters()
            
            # Load average (Unix/Linux uniquement)
            try:
                load_avg = list(psutil.getloadavg())
            except AttributeError:
                load_avg = [0.0, 0.0, 0.0]  # Windows fallback
            
            return SystemResources(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                memory_available_mb=memory.available / 1024 / 1024,
                disk_percent=disk.percent,
                disk_used_gb=disk.used / 1024 / 1024 / 1024,
                network_bytes_sent=network.bytes_sent,
                network_bytes_recv=network.bytes_recv,
                load_average=load_avg
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte ressources: {e}")
            raise
    
    def _record_system_metrics(self, resources: SystemResources):
        """📊 Enregistrement des métriques système"""
        # CPU
        self.metrics.record_gauge("system_cpu_usage", resources.cpu_percent)
        
        # Mémoire
        self.metrics.record_gauge("system_memory_usage", resources.memory_percent)
        self.metrics.record_gauge("system_memory_used_mb", resources.memory_used_mb)
        self.metrics.record_gauge("system_memory_available_mb", resources.memory_available_mb)
        
        # Disque
        self.metrics.record_gauge("system_disk_usage", resources.disk_percent)
        self.metrics.record_gauge("system_disk_used_gb", resources.disk_used_gb)
        
        # Réseau
        self.metrics.record_gauge("system_network_bytes_sent", resources.network_bytes_sent)
        self.metrics.record_gauge("system_network_bytes_recv", resources.network_bytes_recv)
        
        # Load average
        if resources.load_average:
            self.metrics.record_gauge("system_load_1m", resources.load_average[0])
            self.metrics.record_gauge("system_load_5m", resources.load_average[1])
            self.metrics.record_gauge("system_load_15m", resources.load_average[2])


class HealthChecker:
    """❤️ Vérificateur de santé des services"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.service_healths: Dict[str, ServiceHealth] = {}
        self.health_checks: Dict[str, Callable] = {}
        self.check_interval = 60  # secondes
        self.checking_active = False
        self.check_thread = None
    
    def register_health_check(self, service_name: str, check_function: Callable):
        """📝 Enregistre un check de santé"""
        self.health_checks[service_name] = check_function
        logger.info(f"❤️ Health check enregistré pour {service_name}")
    
    def start_health_checks(self):
        """🚀 Démarre les checks de santé périodiques"""
        if self.checking_active:
            return
        
        self.checking_active = True
        self.check_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self.check_thread.start()
        
        logger.info("❤️ Health checks démarrés")
    
    def stop_health_checks(self):
        """🛑 Arrête les checks de santé"""
        self.checking_active = False
        if self.check_thread:
            self.check_thread.join(timeout=5)
        
        logger.info("❤️ Health checks arrêtés")
    
    def _health_check_loop(self):
        """🔄 Boucle de health checks"""
        while self.checking_active:
            try:
                asyncio.run(self._run_all_health_checks())
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ Erreur health check loop: {e}")
                time.sleep(self.check_interval)
    
    async def _run_all_health_checks(self):
        """🏃 Exécute tous les health checks"""
        for service_name, check_function in self.health_checks.items():
            try:
                await self.check_service_health(service_name, check_function)
            except Exception as e:
                logger.error(f"❌ Erreur health check {service_name}: {e}")
    
    async def check_service_health(
        self, 
        service_name: str, 
        check_function: Callable
    ) -> ServiceHealth:
        """🔍 Vérifie la santé d'un service"""
        start_time = time.time()
        
        try:
            # Exécution du check
            if asyncio.iscoroutinefunction(check_function):
                check_result = await check_function()
            else:
                check_result = check_function()
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            # Analyse du résultat
            if isinstance(check_result, dict):
                status = HealthStatus(check_result.get("status", "unknown"))
                details = check_result.get("details", {})
                success_rate = check_result.get("success_rate", 100.0)
                error_count = check_result.get("error_count", 0)
            else:
                # Résultat booléen simple
                status = HealthStatus.HEALTHY if check_result else HealthStatus.UNHEALTHY
                details = {}
                success_rate = 100.0 if check_result else 0.0
                error_count = 0 if check_result else 1
            
            # Calcul uptime
            previous_health = self.service_healths.get(service_name)
            if previous_health and previous_health.status == HealthStatus.HEALTHY:
                uptime_seconds = previous_health.uptime_seconds + self.check_interval
            else:
                uptime_seconds = self.check_interval if status == HealthStatus.HEALTHY else 0
            
            # Création résultat
            health = ServiceHealth(
                service_name=service_name,
                status=status,
                last_check=datetime.now(),
                response_time_ms=response_time,
                success_rate=success_rate,
                error_count=error_count,
                uptime_seconds=uptime_seconds,
                details=details
            )
            
            # Stockage
            self.service_healths[service_name] = health
            
            # Métriques
            self.metrics.record_gauge(
                "service_health_status", 
                1 if status == HealthStatus.HEALTHY else 0,
                {"service": service_name}
            )
            self.metrics.record_timer(
                "service_health_check_time",
                response_time / 1000,  # secondes
                {"service": service_name}
            )
            self.metrics.record_gauge(
                "service_success_rate",
                success_rate,
                {"service": service_name}
            )
            
            return health
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            # Health en erreur
            health = ServiceHealth(
                service_name=service_name,
                status=HealthStatus.CRITICAL,
                last_check=datetime.now(),
                response_time_ms=response_time,
                success_rate=0.0,
                error_count=1,
                uptime_seconds=0,
                details={"error": str(e)},
                alerts=[f"Health check failed: {str(e)}"]
            )
            
            self.service_healths[service_name] = health
            
            # Métriques d'erreur
            self.metrics.record_gauge(
                "service_health_status", 
                0,
                {"service": service_name}
            )
            self.metrics.increment_counter(
                "service_health_check_errors",
                1,
                {"service": service_name}
            )
            
            logger.error(f"❌ Health check failed for {service_name}: {e}")
            return health
    
    def get_service_health(self, service_name: str) -> Optional[ServiceHealth]:
        """🔍 Obtient la santé d'un service"""
        return self.service_healths.get(service_name)
    
    def get_all_services_health(self) -> Dict[str, ServiceHealth]:
        """📊 Santé de tous les services"""
        return self.service_healths.copy()
    
    def get_overall_health(self) -> Dict[str, Any]:
        """🌍 Santé globale du système"""
        if not self.service_healths:
            return {
                "status": "unknown",
                "message": "No services monitored"
            }
        
        # Analyse globale
        statuses = [health.status for health in self.service_healths.values()]
        healthy_count = sum(1 for s in statuses if s == HealthStatus.HEALTHY)
        total_count = len(statuses)
        
        # Détermination statut global
        if healthy_count == total_count:
            overall_status = HealthStatus.HEALTHY
        elif healthy_count > total_count * 0.7:
            overall_status = HealthStatus.DEGRADED
        elif healthy_count > 0:
            overall_status = HealthStatus.UNHEALTHY
        else:
            overall_status = HealthStatus.CRITICAL
        
        # Services problématiques
        unhealthy_services = [
            name for name, health in self.service_healths.items()
            if health.status != HealthStatus.HEALTHY
        ]
        
        return {
            "status": overall_status.value,
            "healthy_services": healthy_count,
            "total_services": total_count,
            "health_percentage": (healthy_count / total_count) * 100,
            "unhealthy_services": unhealthy_services,
            "last_check": max(
                health.last_check for health in self.service_healths.values()
            ).isoformat(),
            "services_detail": {
                name: {
                    "status": health.status.value,
                    "response_time_ms": health.response_time_ms,
                    "success_rate": health.success_rate,
                    "uptime_hours": health.uptime_seconds / 3600
                }
                for name, health in self.service_healths.items()
            }
        }


# =====================================
# 🏭 FACTORY & SETUP
# =====================================

def create_monitoring_stack(
    enable_prometheus: bool = True,
    prometheus_port: int = 8090,
    enable_system_monitoring: bool = True,
    enable_health_checks: bool = True
) -> Dict[str, Any]:
    """🏭 Factory pour créer la stack de monitoring complète"""
    
    # Collecteur de métriques
    metrics_collector = MetricsCollector(
        enable_prometheus=enable_prometheus,
        prometheus_port=prometheus_port
    )
    
    # Moniteur système
    system_monitor = None
    if enable_system_monitoring:
        system_monitor = SystemMonitor(metrics_collector)
        system_monitor.start_monitoring()
    
    # Health checker
    health_checker = None
    if enable_health_checks:
        health_checker = HealthChecker(metrics_collector)
        health_checker.start_health_checks()
    
    logger.info("🏭 Stack de monitoring initialisée")
    
    return {
        "metrics_collector": metrics_collector,
        "system_monitor": system_monitor,
        "health_checker": health_checker
    }


# =====================================
# 📊 HEALTH CHECKS STANDARDS
# =====================================

async def standard_redis_health_check(redis_client) -> Dict[str, Any]:
    """❤️ Health check standard pour Redis"""
    try:
        start_time = time.time()
        await redis_client.ping()
        response_time = time.time() - start_time
        
        return {
            "status": "healthy",
            "response_time_ms": response_time * 1000,
            "details": {"ping_successful": True}
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "details": {"error": str(e)}
        }


async def standard_database_health_check(db_pool) -> Dict[str, Any]:
    """❤️ Health check standard pour base de données"""
    try:
        start_time = time.time()
        # Test simple query
        async with db_pool.acquire() as connection:
            await connection.execute("SELECT 1")
        response_time = time.time() - start_time
        
        return {
            "status": "healthy",
            "response_time_ms": response_time * 1000,
            "details": {"query_successful": True}
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "details": {"error": str(e)}
        }


async def standard_http_health_check(url: str, timeout: int = 5) -> Dict[str, Any]:
    """❤️ Health check standard pour service HTTP"""
    try:
        import aiohttp
        start_time = time.time()
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.get(url) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    return {
                        "status": "healthy",
                        "response_time_ms": response_time * 1000,
                        "details": {"http_status": response.status}
                    }
                else:
                    return {
                        "status": "degraded",
                        "response_time_ms": response_time * 1000,
                        "details": {"http_status": response.status}
                    }
                    
    except Exception as e:
        return {
            "status": "unhealthy",
            "details": {"error": str(e)}
        }
