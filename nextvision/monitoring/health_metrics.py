"""
📊 Health Metrics & Monitoring - Production Enterprise Grade

Monitoring temps réel pour production :
• Métriques performance (latence, throughput, erreurs)
• Health checks automatiques
• Alerting intelligent
• Dashboards temps réel
• SLA monitoring
• Resource utilization
• Business metrics

Author: NEXTEN Team - Production Robustness
Version: 1.0.0
"""

import asyncio
import psutil
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
import statistics

from ..logging.structured_logging import get_structured_logger

logger = get_structured_logger(__name__)

class HealthStatus(Enum):
    """🏥 Status de santé des services"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DOWN = "down"
    UNKNOWN = "unknown"

class MetricType(Enum):
    """📊 Types de métriques"""
    COUNTER = "counter"           # Compteur (incrémental)
    GAUGE = "gauge"               # Jauge (valeur instantanée)
    HISTOGRAM = "histogram"       # Distribution de valeurs
    TIMER = "timer"               # Mesure de temps
    RATE = "rate"                 # Taux (par seconde)

@dataclass
class Metric:
    """📏 Métrique individuelle"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""
    description: str = ""

@dataclass
class ServiceHealth:
    """🏥 Santé d'un service"""
    service_name: str
    status: HealthStatus
    last_check: datetime
    response_time_ms: float
    error_rate_percent: float
    uptime_percent: float
    details: Dict[str, Any] = field(default_factory=dict)
    alerts: List[str] = field(default_factory=list)

@dataclass
class PerformanceStats:
    """⚡ Statistiques performance"""
    # Latency Stats
    avg_response_time_ms: float = 0.0
    p50_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    
    # Throughput Stats
    requests_per_second: float = 0.0
    peak_rps: float = 0.0
    
    # Error Stats
    error_rate_percent: float = 0.0
    total_errors: int = 0
    
    # Resource Stats
    cpu_usage_percent: float = 0.0
    memory_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    
    # Business Metrics
    active_users: int = 0
    successful_operations: int = 0
    
    last_updated: datetime = field(default_factory=datetime.now)

class MetricCollector:
    """📊 Collecteur de métriques centralisé"""
    
    def __init__(self, max_history_hours: int = 24):
        self.max_history_hours = max_history_hours
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.timers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Performance tracking
        self.response_times: deque = deque(maxlen=1000)
        self.request_counts: deque = deque(maxlen=100)  # Par minute
        self.error_counts: deque = deque(maxlen=100)
        
        # Timestamps for rate calculations
        self.last_request_count_reset = time.time()
        self.current_minute_requests = 0
        self.current_minute_errors = 0
        
        logger.info("📊 MetricCollector initialized", extra={
            "max_history_hours": max_history_hours
        })
    
    def increment_counter(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None):
        """➕ Incrémente un compteur"""
        self.counters[name] += value
        self._record_metric(name, value, MetricType.COUNTER, tags or {})
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """📏 Met à jour une jauge"""
        self.gauges[name] = value
        self._record_metric(name, value, MetricType.GAUGE, tags or {})
    
    def record_timer(self, name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None):
        """⏱️ Enregistre une mesure de temps"""
        self.timers[name].append(duration_ms)
        self._record_metric(name, duration_ms, MetricType.TIMER, tags or {})
        
        # Track global response times
        if name.endswith('_response_time') or 'response' in name.lower():
            self.response_times.append(duration_ms)
    
    def record_request(self, success: bool = True):
        """📊 Enregistre une requête"""
        current_time = time.time()
        
        # Reset counter chaque minute
        if current_time - self.last_request_count_reset >= 60:
            self.request_counts.append(self.current_minute_requests)
            self.error_counts.append(self.current_minute_errors)
            
            self.current_minute_requests = 0
            self.current_minute_errors = 0
            self.last_request_count_reset = current_time
        
        self.current_minute_requests += 1
        if not success:
            self.current_minute_errors += 1
    
    def _record_metric(self, name: str, value: float, metric_type: MetricType, tags: Dict[str, str]):
        """📝 Enregistre métrique dans l'historique"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.now(),
            tags=tags
        )
        
        self.metrics_history[name].append(metric)
    
    def get_performance_stats(self) -> PerformanceStats:
        """📈 Calcule statistiques performance actuelles"""
        stats = PerformanceStats()
        
        # Response Time Stats
        if self.response_times:
            response_times = list(self.response_times)
            stats.avg_response_time_ms = statistics.mean(response_times)
            
            if len(response_times) >= 2:
                sorted_times = sorted(response_times)
                stats.p50_response_time_ms = self._percentile(sorted_times, 50)
                stats.p95_response_time_ms = self._percentile(sorted_times, 95)
                stats.p99_response_time_ms = self._percentile(sorted_times, 99)
        
        # Throughput Stats
        if self.request_counts:
            stats.requests_per_second = statistics.mean(self.request_counts) / 60.0
            stats.peak_rps = max(self.request_counts) / 60.0
        
        # Error Rate
        total_requests = sum(self.request_counts) if self.request_counts else 0
        total_errors = sum(self.error_counts) if self.error_counts else 0
        if total_requests > 0:
            stats.error_rate_percent = (total_errors / total_requests) * 100
        
        stats.total_errors = total_errors
        
        # Resource Stats
        stats.cpu_usage_percent = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        stats.memory_usage_percent = memory_info.percent
        stats.memory_usage_mb = memory_info.used / 1024 / 1024
        
        # Business Metrics from gauges
        stats.active_users = int(self.gauges.get('active_users', 0))
        stats.successful_operations = int(self.counters.get('successful_operations', 0))
        
        stats.last_updated = datetime.now()
        
        return stats
    
    def _percentile(self, sorted_data: List[float], percentile: int) -> float:
        """📊 Calcule percentile"""
        if not sorted_data:
            return 0.0
        
        index = (percentile / 100.0) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index % 1)
    
    def get_metric_history(self, metric_name: str, hours: int = 1) -> List[Metric]:
        """📈 Récupère historique métrique"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        if metric_name not in self.metrics_history:
            return []
        
        return [m for m in self.metrics_history[metric_name] if m.timestamp >= cutoff_time]
    
    def cleanup_old_metrics(self):
        """🧹 Nettoyage anciennes métriques"""
        cutoff_time = datetime.now() - timedelta(hours=self.max_history_hours)
        
        for metric_name, history in self.metrics_history.items():
            # Supprimer anciennes métriques
            while history and history[0].timestamp < cutoff_time:
                history.popleft()
        
        logger.debug("🧹 Old metrics cleanup completed")

class ServiceHealthCheck:
    """🏥 Health checker pour services"""
    
    def __init__(self):
        self.health_checkers: Dict[str, Callable] = {}
        self.health_status: Dict[str, ServiceHealth] = {}
        self.check_intervals: Dict[str, int] = {}  # service -> seconds
        self.last_checks: Dict[str, datetime] = {}
        
        logger.info("🏥 ServiceHealthCheck initialized")
    
    def register_health_check(self, service_name: str, 
                            check_function: Callable,
                            interval_seconds: int = 60):
        """📋 Enregistre health check pour un service"""
        self.health_checkers[service_name] = check_function
        self.check_intervals[service_name] = interval_seconds
        
        logger.info(f"📋 Health check registered for {service_name}", extra={
            "service": service_name,
            "interval_seconds": interval_seconds
        })
    
    async def check_service_health(self, service_name: str) -> ServiceHealth:
        """🔍 Vérifie santé d'un service"""
        if service_name not in self.health_checkers:
            return ServiceHealth(
                service_name=service_name,
                status=HealthStatus.UNKNOWN,
                last_check=datetime.now(),
                response_time_ms=0.0,
                error_rate_percent=0.0,
                uptime_percent=0.0,
                details={"error": "No health checker registered"}
            )
        
        start_time = time.time()
        
        try:
            check_function = self.health_checkers[service_name]
            
            # Exécution health check
            if asyncio.iscoroutinefunction(check_function):
                result = await check_function()
            else:
                result = check_function()
            
            response_time = (time.time() - start_time) * 1000
            
            # Analyse résultat
            if isinstance(result, dict):
                status = HealthStatus(result.get('status', 'unknown'))
                details = result.get('details', {})
                error_rate = result.get('error_rate', 0.0)
                uptime = result.get('uptime', 100.0)
            elif isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.CRITICAL
                details = {}
                error_rate = 0.0 if result else 100.0
                uptime = 100.0 if result else 0.0
            else:
                status = HealthStatus.HEALTHY
                details = {"result": str(result)}
                error_rate = 0.0
                uptime = 100.0
            
            health = ServiceHealth(
                service_name=service_name,
                status=status,
                last_check=datetime.now(),
                response_time_ms=response_time,
                error_rate_percent=error_rate,
                uptime_percent=uptime,
                details=details
            )
            
            self.health_status[service_name] = health
            self.last_checks[service_name] = datetime.now()
            
            logger.debug(f"🏥 Health check completed for {service_name}", extra={
                "service": service_name,
                "status": status.value,
                "response_time_ms": round(response_time, 2)
            })
            
            return health
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            health = ServiceHealth(
                service_name=service_name,
                status=HealthStatus.CRITICAL,
                last_check=datetime.now(),
                response_time_ms=response_time,
                error_rate_percent=100.0,
                uptime_percent=0.0,
                details={"error": str(e)[:500]},
                alerts=[f"Health check failed: {str(e)[:200]}"]
            )
            
            self.health_status[service_name] = health
            self.last_checks[service_name] = datetime.now()
            
            logger.error(f"❌ Health check failed for {service_name}", extra={
                "service": service_name,
                "error": str(e)[:200],
                "response_time_ms": round(response_time, 2)
            })
            
            return health
    
    async def check_all_services(self) -> Dict[str, ServiceHealth]:
        """🏥 Vérifie santé de tous les services"""
        tasks = []
        
        for service_name in self.health_checkers.keys():
            # Vérifier si check nécessaire selon interval
            last_check = self.last_checks.get(service_name)
            interval = self.check_intervals.get(service_name, 60)
            
            if (not last_check or 
                datetime.now() - last_check >= timedelta(seconds=interval)):
                
                task = self.check_service_health(service_name)
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        return self.health_status.copy()
    
    def get_overall_health(self) -> HealthStatus:
        """🌡️ Calcule santé globale système"""
        if not self.health_status:
            return HealthStatus.UNKNOWN
        
        statuses = [health.status for health in self.health_status.values()]
        
        # Priorisation des status
        if HealthStatus.DOWN in statuses:
            return HealthStatus.DOWN
        elif HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            return HealthStatus.WARNING
        elif all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.WARNING

class PerformanceMonitor:
    """⚡ Moniteur performance principal"""
    
    def __init__(self):
        self.metric_collector = MetricCollector()
        self.health_checker = ServiceHealthCheck()
        
        # Thresholds for alerting
        self.thresholds = {
            'response_time_ms': 1000,      # 1s
            'error_rate_percent': 5.0,      # 5%
            'cpu_usage_percent': 80.0,      # 80%
            'memory_usage_percent': 85.0,   # 85%
            'requests_per_second': 1000     # 1000 RPS max
        }
        
        # SLA targets
        self.sla_targets = {
            'availability_percent': 99.9,
            'response_time_p95_ms': 500,
            'error_rate_percent': 1.0
        }
        
        # Start background cleanup task
        self._cleanup_task = None
        
        logger.info("⚡ PerformanceMonitor initialized", extra={
            "thresholds": self.thresholds,
            "sla_targets": self.sla_targets
        })
    
    async def start_monitoring(self):
        """🚀 Démarre monitoring en arrière-plan"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._background_cleanup())
            logger.info("🚀 Background monitoring started")
    
    async def stop_monitoring(self):
        """🛑 Arrête monitoring"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            logger.info("🛑 Background monitoring stopped")
    
    async def _background_cleanup(self):
        """🔄 Tâche nettoyage en arrière-plan"""
        while True:
            try:
                await asyncio.sleep(300)  # 5 minutes
                self.metric_collector.cleanup_old_metrics()
                await self.health_checker.check_all_services()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Background cleanup error: {e}")
    
    def record_operation(self, operation_name: str, duration_ms: float, success: bool = True, tags: Optional[Dict] = None):
        """📊 Enregistre opération avec métriques"""
        # Record metrics
        self.metric_collector.record_timer(f"{operation_name}_response_time", duration_ms, tags)
        self.metric_collector.increment_counter(f"{operation_name}_total", 1.0, tags)
        
        if success:
            self.metric_collector.increment_counter(f"{operation_name}_success", 1.0, tags)
        else:
            self.metric_collector.increment_counter(f"{operation_name}_error", 1.0, tags)
        
        # Global request tracking
        self.metric_collector.record_request(success)
    
    def record_batch_completion(self, batch_id: str, duration_seconds: float, jobs_per_second: float, success_rate: float):
        """📦 Enregistre completion batch"""
        tags = {"batch_id": batch_id}
        
        self.metric_collector.record_timer("batch_processing_time", duration_seconds * 1000, tags)
        self.metric_collector.set_gauge("batch_jobs_per_second", jobs_per_second, tags)
        self.metric_collector.set_gauge("batch_success_rate", success_rate, tags)
        self.metric_collector.increment_counter("batches_completed", 1.0, tags)
    
    def record_error(self, service_name: str, error_type: str, details: Optional[str] = None):
        """❌ Enregistre erreur"""
        tags = {"service": service_name, "error_type": error_type}
        
        self.metric_collector.increment_counter("errors_total", 1.0, tags)
        self.metric_collector.increment_counter(f"errors_{error_type}", 1.0, tags)
        
        if details:
            logger.warning(f"📊 Error recorded: {error_type}", extra={
                "service": service_name,
                "error_type": error_type,
                "details": details[:200]
            })
    
    def record_success(self, service_name: str, operation_name: str, duration_seconds: float):
        """✅ Enregistre succès"""
        tags = {"service": service_name, "operation": operation_name}
        
        self.metric_collector.record_timer(f"{operation_name}_duration", duration_seconds * 1000, tags)
        self.metric_collector.increment_counter("operations_success", 1.0, tags)
    
    def get_dashboard_data(self) -> Dict:
        """📊 Données pour dashboard temps réel"""
        performance_stats = self.metric_collector.get_performance_stats()
        health_status = self.health_checker.get_overall_health()
        
        # Check SLA compliance
        sla_compliance = self._check_sla_compliance(performance_stats)
        
        # Check alerts
        alerts = self._check_alerts(performance_stats)
        
        return {
            "system_health": {
                "overall_status": health_status.value,
                "services": {name: health.status.value for name, health in self.health_checker.health_status.items()}
            },
            "performance": {
                "response_time_ms": {
                    "avg": round(performance_stats.avg_response_time_ms, 2),
                    "p50": round(performance_stats.p50_response_time_ms, 2),
                    "p95": round(performance_stats.p95_response_time_ms, 2),
                    "p99": round(performance_stats.p99_response_time_ms, 2)
                },
                "throughput": {
                    "requests_per_second": round(performance_stats.requests_per_second, 1),
                    "peak_rps": round(performance_stats.peak_rps, 1)
                },
                "errors": {
                    "error_rate_percent": round(performance_stats.error_rate_percent, 2),
                    "total_errors": performance_stats.total_errors
                }
            },
            "resources": {
                "cpu_usage_percent": round(performance_stats.cpu_usage_percent, 1),
                "memory_usage_percent": round(performance_stats.memory_usage_percent, 1),
                "memory_usage_mb": round(performance_stats.memory_usage_mb, 1)
            },
            "business_metrics": {
                "active_users": performance_stats.active_users,
                "successful_operations": performance_stats.successful_operations
            },
            "sla_compliance": sla_compliance,
            "alerts": alerts,
            "timestamp": datetime.now().isoformat()
        }
    
    def _check_sla_compliance(self, stats: PerformanceStats) -> Dict:
        """📋 Vérification conformité SLA"""
        compliance = {}
        
        # Availability (inverse of error rate)
        availability = 100 - stats.error_rate_percent
        compliance['availability'] = {
            'current': round(availability, 2),
            'target': self.sla_targets['availability_percent'],
            'compliant': availability >= self.sla_targets['availability_percent']
        }
        
        # Response time P95
        compliance['response_time_p95'] = {
            'current': round(stats.p95_response_time_ms, 2),
            'target': self.sla_targets['response_time_p95_ms'],
            'compliant': stats.p95_response_time_ms <= self.sla_targets['response_time_p95_ms']
        }
        
        # Error rate
        compliance['error_rate'] = {
            'current': round(stats.error_rate_percent, 2),
            'target': self.sla_targets['error_rate_percent'],
            'compliant': stats.error_rate_percent <= self.sla_targets['error_rate_percent']
        }
        
        # Overall compliance
        compliance['overall_compliant'] = all(c['compliant'] for c in compliance.values())
        
        return compliance
    
    def _check_alerts(self, stats: PerformanceStats) -> List[Dict]:
        """🚨 Vérification alertes"""
        alerts = []
        
        # Response time alert
        if stats.avg_response_time_ms > self.thresholds['response_time_ms']:
            alerts.append({
                'type': 'performance',
                'severity': 'warning',
                'message': f"High response time: {stats.avg_response_time_ms:.1f}ms > {self.thresholds['response_time_ms']}ms",
                'timestamp': datetime.now().isoformat()
            })
        
        # Error rate alert
        if stats.error_rate_percent > self.thresholds['error_rate_percent']:
            alerts.append({
                'type': 'reliability',
                'severity': 'critical' if stats.error_rate_percent > 10 else 'warning',
                'message': f"High error rate: {stats.error_rate_percent:.1f}% > {self.thresholds['error_rate_percent']}%",
                'timestamp': datetime.now().isoformat()
            })
        
        # Resource alerts
        if stats.cpu_usage_percent > self.thresholds['cpu_usage_percent']:
            alerts.append({
                'type': 'resource',
                'severity': 'warning',
                'message': f"High CPU usage: {stats.cpu_usage_percent:.1f}% > {self.thresholds['cpu_usage_percent']}%",
                'timestamp': datetime.now().isoformat()
            })
        
        if stats.memory_usage_percent > self.thresholds['memory_usage_percent']:
            alerts.append({
                'type': 'resource',
                'severity': 'critical',
                'message': f"High memory usage: {stats.memory_usage_percent:.1f}% > {self.thresholds['memory_usage_percent']}%",
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts

class HealthMetrics:
    """🏥 Classe principale métriques santé - Interface simplifiée"""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        
        # Pre-register common health checks
        self._register_default_health_checks()
        
        logger.info("🏥 HealthMetrics initialized")
    
    def _register_default_health_checks(self):
        """📋 Enregistre health checks par défaut"""
        # System health check
        async def system_health():
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent
            
            if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
                return {
                    'status': 'critical',
                    'details': {
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory_percent,
                        'disk_percent': disk_percent
                    }
                }
            elif cpu_percent > 80 or memory_percent > 80 or disk_percent > 80:
                return {
                    'status': 'warning',
                    'details': {
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory_percent,
                        'disk_percent': disk_percent
                    }
                }
            else:
                return {
                    'status': 'healthy',
                    'details': {
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory_percent,
                        'disk_percent': disk_percent
                    }
                }
        
        self.performance_monitor.health_checker.register_health_check(
            "system_resources", system_health, 30
        )
    
    # Delegate methods to performance monitor
    def record_operation(self, operation_name: str, duration_ms: float, success: bool = True, tags: Optional[Dict] = None):
        return self.performance_monitor.record_operation(operation_name, duration_ms, success, tags)
    
    def record_batch_completion(self, batch_id: str, duration_seconds: float, jobs_per_second: float, success_rate: float):
        return self.performance_monitor.record_batch_completion(batch_id, duration_seconds, jobs_per_second, success_rate)
    
    def record_error(self, service_name: str, error_type: str, details: Optional[str] = None):
        return self.performance_monitor.record_error(service_name, error_type, details)
    
    def record_success(self, service_name: str, operation_name: str, duration_seconds: float):
        return self.performance_monitor.record_success(service_name, operation_name, duration_seconds)
    
    def get_dashboard_data(self) -> Dict:
        return self.performance_monitor.get_dashboard_data()
    
    async def start_monitoring(self):
        await self.performance_monitor.start_monitoring()
    
    async def stop_monitoring(self):
        await self.performance_monitor.stop_monitoring()

# ===============================================
# 🚀 GLOBAL INSTANCES & UTILITIES
# ===============================================

_health_metrics: Optional[HealthMetrics] = None
_performance_monitor: Optional[PerformanceMonitor] = None

def get_health_metrics() -> HealthMetrics:
    """🏥 Récupère l'instance globale HealthMetrics"""
    global _health_metrics
    
    if _health_metrics is None:
        _health_metrics = HealthMetrics()
        logger.info("🚀 Global HealthMetrics instance initialized")
    
    return _health_metrics

def get_performance_monitor() -> PerformanceMonitor:
    """⚡ Récupère l'instance globale PerformanceMonitor"""
    global _performance_monitor
    
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
        logger.info("🚀 Global PerformanceMonitor instance initialized")
    
    return _performance_monitor

# Décorateur pour monitoring automatique
def monitor_performance(operation_name: str = None, tags: Optional[Dict] = None):
    """📊 Décorateur pour monitoring automatique"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            
            health_metrics = get_health_metrics()
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                health_metrics.record_operation(op_name, duration_ms, True, tags)
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                health_metrics.record_operation(op_name, duration_ms, False, tags)
                health_metrics.record_error(op_name, type(e).__name__, str(e)[:200])
                raise
        
        def sync_wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            
            health_metrics = get_health_metrics()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                health_metrics.record_operation(op_name, duration_ms, True, tags)
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                health_metrics.record_operation(op_name, duration_ms, False, tags)
                health_metrics.record_error(op_name, type(e).__name__, str(e)[:200])
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator
