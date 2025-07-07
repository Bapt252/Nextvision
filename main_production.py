"""
🎯 Nextvision - Production-Ready Main Application
Enterprise-grade FastAPI application with full robustness stack

Features:
- Graceful degradation & error handling
- Intelligent Redis caching
- High-performance batch processing
- Adaptive retry strategies  
- Real-time monitoring & metrics
- Structured JSON logging
- Multi-environment configuration
- Stress testing & health checks
"""

import asyncio
import signal
import sys
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Nextvision core imports
from nextvision.config.production_settings import get_config, Environment, health_check_config
from nextvision.logging.structured_logging import (
    setup_production_logging, get_structured_logger, get_request_tracker,
    log_operation, LogComponent, LogContext
)
from nextvision.monitoring.health_metrics import create_monitoring_stack
from nextvision.cache.redis_intelligent_cache import create_cache_manager
from nextvision.error_handling.graceful_degradation import (
    GracefulDegradationManager, GoogleMapsFallbacks, CacheFallbacks, DatabaseFallbacks
)
from nextvision.utils.retry_strategies import create_retry_executor
from nextvision.performance.batch_processing import BatchProcessor, PerformanceOptimizer
from nextvision.tests.stress_testing import PerformanceTestRunner

# Original Nextvision imports
from nextvision.services.commitment_bridge import CommitmentNextvisionBridge, BridgeConfig
from nextvision.services.google_maps_service import GoogleMapsService
from nextvision.services.transport_calculator import TransportCalculator
from nextvision.engines.transport_filtering import TransportFilteringEngine
from nextvision.engines.location_scoring import LocationScoringEngine

# Configuration et logging
config = get_config()
logger = get_structured_logger("nextvision.main")
request_tracker = get_request_tracker()

# Variables globales pour les services
app_state = {
    "monitoring_stack": None,
    "cache_manager": None,
    "degradation_manager": None,
    "retry_executor": None,
    "batch_processor": None,
    "performance_optimizer": None,
    "google_maps_service": None,
    "transport_calculator": None,
    "filtering_engine": None,
    "location_scoring_engine": None,
    "commitment_bridge": None,
    "startup_time": None,
    "shutdown_initiated": False
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    🔄 Gestionnaire de cycle de vie de l'application
    Initialisation et nettoyage des ressources
    """
    # === STARTUP ===
    startup_start = time.time()
    logger.info("🚀 Nextvision production startup initiated")
    
    try:
        await initialize_production_services()
        
        startup_time = time.time() - startup_start
        app_state["startup_time"] = startup_time
        
        logger.info(
            "✅ Nextvision production ready",
            extra={
                "startup_time_seconds": startup_time,
                "environment": config.environment.value,
                "services_initialized": len([k for k, v in app_state.items() if v is not None])
            }
        )
        
        yield  # L'application fonctionne ici
        
    except Exception as e:
        logger.critical(f"💥 Critical startup failure: {e}", exc_info=True)
        raise
    
    finally:
        # === SHUTDOWN ===
        logger.info("🛑 Nextvision production shutdown initiated")
        app_state["shutdown_initiated"] = True
        
        await cleanup_production_services()
        
        logger.info("✅ Nextvision production shutdown complete")


async def initialize_production_services():
    """
    🔧 Initialisation de tous les services en production
    """
    
    with log_operation("production_services_initialization", LogComponent.SYSTEM):
        
        # 1. Configuration et logging
        if config.is_production():
            setup_production_logging(
                log_level=config.logging.log_level.value,
                enable_file_logging=config.logging.enable_file_logging,
                log_file_path=config.logging.log_file_path,
                max_file_size_mb=config.logging.max_file_size_mb,
                backup_count=config.logging.backup_count
            )
        
        logger.info("📋 Production configuration loaded", extra={
            "environment": config.environment.value,
            "debug_mode": config.debug,
            "worker_count": config.performance.worker_count,
            "features_enabled": config.features
        })
        
        # 2. Monitoring stack
        if config.monitoring.enable_prometheus or config.monitoring.enable_health_checks:
            app_state["monitoring_stack"] = create_monitoring_stack(
                enable_prometheus=config.monitoring.enable_prometheus,
                prometheus_port=config.monitoring.prometheus_port,
                enable_system_monitoring=config.monitoring.enable_system_monitoring,
                enable_health_checks=config.monitoring.enable_health_checks
            )
            logger.info("📊 Monitoring stack initialized")
        
        # 3. Cache manager
        if config.performance.cache_enabled:
            app_state["cache_manager"] = create_cache_manager(
                redis_url=config.get_redis_url(),
                enable_memory_cache=config.google_maps.enable_memory_cache,
                metrics_collector=app_state["monitoring_stack"]["metrics_collector"] if app_state["monitoring_stack"] else None
            )
            
            cache_initialized = await app_state["cache_manager"].initialize()
            if cache_initialized:
                logger.info("🗄️ Cache manager initialized with Redis")
            else:
                logger.warning("⚠️ Cache manager running in memory-only mode")
        
        # 4. Graceful degradation manager
        app_state["degradation_manager"] = GracefulDegradationManager(
            metrics_collector=app_state["monitoring_stack"]["metrics_collector"] if app_state["monitoring_stack"] else None
        )
        
        # Configuration des fallbacks
        degradation_mgr = app_state["degradation_manager"]
        
        # Google Maps fallbacks
        degradation_mgr.register_fallback(
            "google_maps", "google_maps_quota_exceeded", 
            "cache_only", GoogleMapsFallbacks.quota_exceeded_fallback
        )
        degradation_mgr.register_fallback(
            "google_maps", "google_maps_invalid_request",
            "approximate", GoogleMapsFallbacks.invalid_address_fallback
        )
        
        # Cache fallbacks
        degradation_mgr.register_fallback(
            "redis_cache", "redis_unavailable",
            "disable_feature", CacheFallbacks.redis_unavailable_fallback
        )
        
        # Database fallbacks
        degradation_mgr.register_fallback(
            "database", "database_connection_lost",
            "manual_intervention", DatabaseFallbacks.connection_lost_fallback
        )
        
        logger.info("🛡️ Graceful degradation manager configured")
        
        # 5. Retry executor
        app_state["retry_executor"] = create_retry_executor(
            metrics_collector=app_state["monitoring_stack"]["metrics_collector"] if app_state["monitoring_stack"] else None
        )
        logger.info("🔄 Retry executor initialized")
        
        # 6. Batch processor
        app_state["batch_processor"] = BatchProcessor(
            initial_batch_size=config.performance.default_batch_size,
            max_concurrency=config.performance.max_concurrent_batches,
            cache_manager=app_state["cache_manager"],
            metrics_collector=app_state["monitoring_stack"]["metrics_collector"] if app_state["monitoring_stack"] else None
        )
        
        app_state["performance_optimizer"] = PerformanceOptimizer(app_state["batch_processor"])
        logger.info("⚡ Batch processor and performance optimizer ready")
        
        # 7. Google Maps service avec robustesse
        app_state["google_maps_service"] = GoogleMapsService(
            api_key=config.google_maps.api_key,
            cache_duration_hours=config.google_maps.geocode_cache_duration_hours
        )
        
        # Wrapping avec retry et degradation
        original_geocode = app_state["google_maps_service"].geocode_address
        
        async def robust_geocode(address: str, force_refresh: bool = False):
            return await app_state["degradation_manager"].execute_with_fallback(
                "google_maps",
                lambda: app_state["retry_executor"].execute_with_retry(
                    lambda: original_geocode(address, force_refresh),
                    "google_maps",
                    context={"address": address}
                ),
                {"address": address}
            )
        
        app_state["google_maps_service"].geocode_address = robust_geocode
        
        # 8. Transport services
        app_state["transport_calculator"] = TransportCalculator(app_state["google_maps_service"])
        app_state["filtering_engine"] = TransportFilteringEngine(app_state["transport_calculator"])
        app_state["location_scoring_engine"] = LocationScoringEngine(app_state["transport_calculator"])
        
        logger.info("🗺️ Google Maps and transport services initialized")
        
        # 9. Commitment Bridge (optionnel)
        try:
            bridge_config = BridgeConfig(
                base_url="http://localhost:3000",  # À configurer selon l'environnement
                timeout=30,
                max_retries=3
            )
            app_state["commitment_bridge"] = CommitmentNextvisionBridge(bridge_config)
            logger.info("🌉 Commitment Bridge initialized")
        except Exception as e:
            logger.warning(f"⚠️ Commitment Bridge not available: {e}")
        
        # 10. Health checks registration
        if app_state["monitoring_stack"] and app_state["monitoring_stack"]["health_checker"]:
            health_checker = app_state["monitoring_stack"]["health_checker"]
            
            # Cache health check
            if app_state["cache_manager"]:
                health_checker.register_health_check(
                    "redis_cache",
                    app_state["cache_manager"].health_check
                )
            
            # Google Maps health check
            async def google_maps_health():
                try:
                    test_result = await app_state["google_maps_service"].geocode_address("Paris, France")
                    return {"status": "healthy", "test_geocoding": bool(test_result)}
                except Exception as e:
                    return {"status": "unhealthy", "error": str(e)}
            
            health_checker.register_health_check("google_maps", google_maps_health)
            
            logger.info("❤️ Health checks registered")


async def cleanup_production_services():
    """
    🧹 Nettoyage propre de tous les services
    """
    
    with log_operation("production_services_cleanup", LogComponent.SYSTEM):
        
        # Arrêt monitoring
        if app_state["monitoring_stack"]:
            if app_state["monitoring_stack"]["system_monitor"]:
                app_state["monitoring_stack"]["system_monitor"].stop_monitoring()
            if app_state["monitoring_stack"]["health_checker"]:
                app_state["monitoring_stack"]["health_checker"].stop_health_checks()
            logger.info("📊 Monitoring stack stopped")
        
        # Nettoyage cache
        if app_state["cache_manager"]:
            await app_state["cache_manager"].cleanup()
            logger.info("🗄️ Cache manager cleaned up")
        
        logger.info("✅ All services cleaned up successfully")


# === CRÉATION DE L'APPLICATION FASTAPI ===

app = FastAPI(
    title="🎯 Nextvision Production API",
    description="""
    **Enterprise-grade Nextvision API with Full Robustness Stack**
    
    ## 🛡️ Production Features
    
    * **Graceful Degradation**: Intelligent fallbacks for all external services
    * **Smart Caching**: Multi-level Redis + Memory caching with TTL policies
    * **Batch Processing**: High-performance processing of 1000+ jobs
    * **Adaptive Retry**: Intelligent retry strategies with exponential backoff
    * **Real-time Monitoring**: Prometheus metrics + health checks
    * **Structured Logging**: JSON logs with correlation IDs
    * **Multi-environment**: Production/staging/development configurations
    * **Stress Testing**: Built-in load testing and failover validation
    
    ## 🎯 Core Nextvision Features
    
    * **Adaptive Weighting**: Context-aware matching algorithm
    * **Google Maps Intelligence**: Transport-aware job filtering
    * **Commitment Bridge**: Seamless integration with Commitment-
    
    ## 📊 Performance Targets
    
    * **Throughput**: 500+ requests/second
    * **Latency**: P95 < 2 seconds
    * **Memory**: < 2GB under load
    * **Availability**: 99.9% uptime
    """,
    version="2.1.0-production",
    lifespan=lifespan
)

# === MIDDLEWARE CONFIGURATION ===

# CORS avec configuration sécurisée
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.security.cors_origins,
    allow_credentials=config.security.cors_allow_credentials,
    allow_methods=config.security.cors_allow_methods,
    allow_headers=config.security.cors_allow_headers,
)

# Trusted hosts en production
if config.is_production():
    trusted_hosts = ["nextvision.com", "*.nextvision.com", "localhost"]
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)

# Rate limiting middleware (basique)
from collections import defaultdict
from time import time as current_time

request_counts = defaultdict(list)

@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    if config.security.enable_rate_limiting:
        client_ip = request.client.host
        current_minute = int(current_time() // 60)
        
        # Nettoyer anciennes requêtes
        request_counts[client_ip] = [
            req_time for req_time in request_counts[client_ip]
            if req_time > current_minute - 1
        ]
        
        # Vérifier limite
        if len(request_counts[client_ip]) >= config.security.rate_limit_requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"}
            )
        
        request_counts[client_ip].append(current_minute)
    
    response = await call_next(request)
    return response

# Request tracking middleware
@app.middleware("http")
async def request_tracking_middleware(request: Request, call_next):
    import uuid
    
    # Générer request ID
    request_id = str(uuid.uuid4())
    
    # Démarrer tracking
    context = request_tracker.start_request(
        request_id=request_id,
        endpoint=str(request.url.path),
        method=request.method,
        user_id=request.headers.get("X-User-ID")
    )
    
    # Ajouter headers de réponse
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        # Terminer tracking
        processing_time = time.time() - start_time
        response_size = response.headers.get("content-length")
        
        request_tracker.end_request(
            request_id=request_id,
            status_code=response.status_code,
            response_size=int(response_size) if response_size else None
        )
        
        # Ajouter headers de debugging
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Processing-Time"] = f"{processing_time:.3f}s"
        
        # Métriques
        if app_state["monitoring_stack"] and app_state["monitoring_stack"]["metrics_collector"]:
            metrics = app_state["monitoring_stack"]["metrics_collector"]
            metrics.increment_counter(
                "api_requests_total",
                labels={
                    "endpoint": request.url.path,
                    "method": request.method,
                    "status": str(response.status_code)
                }
            )
            metrics.record_timer(
                "api_request_duration",
                processing_time,
                labels={
                    "endpoint": request.url.path,
                    "method": request.method
                }
            )
        
        return response
        
    except Exception as e:
        # Erreur pendant traitement
        processing_time = time.time() - start_time
        
        request_tracker.end_request(
            request_id=request_id,
            status_code=500
        )
        
        logger.error(
            f"Request processing error: {e}",
            extra={
                "request_id": request_id,
                "endpoint": request.url.path,
                "method": request.method,
                "processing_time": processing_time
            },
            exc_info=True
        )
        
        raise

# === ENDPOINTS DE ROBUSTESSE ===

@app.get("/", tags=["Root"])
async def root():
    """🏠 Root endpoint avec informations de production"""
    return {
        "service": "Nextvision Production",
        "version": "2.1.0-production",
        "environment": config.environment.value,
        "status": "operational",
        "startup_time": app_state.get("startup_time"),
        "features": {
            "graceful_degradation": True,
            "intelligent_caching": bool(app_state["cache_manager"]),
            "batch_processing": bool(app_state["batch_processor"]),
            "adaptive_retry": bool(app_state["retry_executor"]),
            "real_time_monitoring": bool(app_state["monitoring_stack"]),
            "structured_logging": True,
            "stress_testing": True
        },
        "documentation": "/docs",
        "health_checks": {
            "overall": "/health",
            "detailed": "/health/detailed",
            "readiness": "/health/ready",
            "liveness": "/health/live"
        },
        "monitoring": {
            "metrics": "/metrics" if config.monitoring.enable_prometheus else None,
            "performance": "/monitoring/performance",
            "system": "/monitoring/system"
        },
        "administration": {
            "stress_tests": "/admin/stress-test",
            "configuration": "/admin/config",
            "cache_stats": "/admin/cache/stats"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """❤️ Health check rapide"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime_seconds": time.time() - app_state.get("startup_time", time.time()),
        "environment": config.environment.value,
        "version": "2.1.0-production"
    }

@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """❤️ Health check détaillé avec tous les services"""
    
    health_status = {
        "overall_status": "healthy",
        "timestamp": time.time(),
        "environment": config.environment.value,
        "services": {}
    }
    
    try:
        # Configuration health
        config_health = health_check_config()
        health_status["services"]["configuration"] = config_health
        
        # Cache health
        if app_state["cache_manager"]:
            cache_health = await app_state["cache_manager"].health_check()
            health_status["services"]["cache"] = cache_health
        
        # Monitoring health
        if app_state["monitoring_stack"] and app_state["monitoring_stack"]["health_checker"]:
            overall_health = app_state["monitoring_stack"]["health_checker"].get_overall_health()
            health_status["services"]["monitoring"] = overall_health
        
        # Degradation manager health
        if app_state["degradation_manager"]:
            degraded_services = app_state["degradation_manager"].get_degraded_services()
            health_status["services"]["degradation"] = {
                "degraded_services_count": len(degraded_services),
                "degraded_services": degraded_services
            }
        
        # Déterminer statut global
        service_issues = []
        for service_name, service_health in health_status["services"].items():
            if isinstance(service_health, dict):
                service_status = service_health.get("status", "unknown")
                if service_status not in ["healthy", "pass"]:
                    service_issues.append(f"{service_name}: {service_status}")
        
        if service_issues:
            health_status["overall_status"] = "degraded"
            health_status["issues"] = service_issues
        
    except Exception as e:
        health_status["overall_status"] = "error"
        health_status["error"] = str(e)
        logger.error(f"Health check error: {e}", exc_info=True)
    
    return health_status

@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """✅ Readiness probe pour Kubernetes"""
    if app_state["shutdown_initiated"]:
        raise HTTPException(status_code=503, detail="Shutdown in progress")
    
    # Vérifier services essentiels
    essential_services = ["degradation_manager", "retry_executor"]
    
    for service in essential_services:
        if not app_state.get(service):
            raise HTTPException(
                status_code=503, 
                detail=f"Essential service {service} not ready"
            )
    
    return {"status": "ready"}

@app.get("/health/live", tags=["Health"])
async def liveness_check():
    """💓 Liveness probe pour Kubernetes"""
    if app_state["shutdown_initiated"]:
        raise HTTPException(status_code=503, detail="Shutdown in progress")
    
    return {"status": "alive"}

# === ENDPOINTS DE MONITORING ===

@app.get("/monitoring/performance", tags=["Monitoring"])
async def get_performance_metrics():
    """📊 Métriques de performance"""
    
    performance_data = {
        "timestamp": time.time(),
        "environment": config.environment.value
    }
    
    # Métriques batch processor
    if app_state["batch_processor"]:
        performance_data["batch_processing"] = app_state["batch_processor"].get_performance_stats()
    
    # Métriques cache
    if app_state["cache_manager"]:
        performance_data["cache"] = app_state["cache_manager"].cache.get_stats()
    
    # Métriques retry
    if app_state["retry_executor"]:
        performance_data["retry_strategies"] = app_state["retry_executor"].get_all_stats()
    
    # Métriques système
    if app_state["monitoring_stack"] and app_state["monitoring_stack"]["system_monitor"]:
        try:
            system_resources = app_state["monitoring_stack"]["system_monitor"].get_system_resources()
            performance_data["system_resources"] = {
                "cpu_percent": system_resources.cpu_percent,
                "memory_percent": system_resources.memory_percent,
                "memory_used_mb": system_resources.memory_used_mb,
                "disk_percent": system_resources.disk_percent
            }
        except Exception as e:
            performance_data["system_resources"] = {"error": str(e)}
    
    # Requests actives
    performance_data["active_requests"] = {
        "count": request_tracker.get_active_requests_count(),
        "details": request_tracker.get_active_requests()
    }
    
    return performance_data

@app.get("/monitoring/system", tags=["Monitoring"])
async def get_system_metrics():
    """🖥️ Métriques système détaillées"""
    
    if not app_state["monitoring_stack"] or not app_state["monitoring_stack"]["system_monitor"]:
        raise HTTPException(status_code=503, detail="System monitoring not available")
    
    try:
        system_monitor = app_state["monitoring_stack"]["system_monitor"]
        resources = system_monitor.get_system_resources()
        
        return {
            "timestamp": resources.timestamp.isoformat(),
            "cpu": {
                "percent": resources.cpu_percent,
                "load_average": resources.load_average
            },
            "memory": {
                "percent": resources.memory_percent,
                "used_mb": resources.memory_used_mb,
                "available_mb": resources.memory_available_mb
            },
            "disk": {
                "percent": resources.disk_percent,
                "used_gb": resources.disk_used_gb
            },
            "network": {
                "bytes_sent": resources.network_bytes_sent,
                "bytes_received": resources.network_bytes_recv
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System metrics error: {str(e)}")

# === ENDPOINTS D'ADMINISTRATION ===

@app.post("/admin/stress-test", tags=["Administration"])
async def run_stress_test(
    scenario: str = "medium_load",
    custom_params: Dict[str, Any] = None
):
    """🧪 Exécution des tests de stress"""
    
    if not config.debug and config.is_production():
        raise HTTPException(
            status_code=403, 
            detail="Stress testing disabled in production"
        )
    
    try:
        test_runner = PerformanceTestRunner()
        
        if scenario == "full_suite":
            # Suite complète
            report = await test_runner.run_complete_test_suite()
        else:
            # Scénario spécifique
            await test_runner.initialize_test_environment()
            
            # Trouver le scénario
            target_scenario = None
            for s in test_runner.stress_suite.predefined_scenarios:
                if s.name == scenario:
                    target_scenario = s
                    break
            
            if not target_scenario:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unknown scenario: {scenario}"
                )
            
            # Appliquer params personnalisés
            if custom_params:
                for key, value in custom_params.items():
                    if hasattr(target_scenario, key):
                        setattr(target_scenario, key, value)
            
            result = await test_runner.stress_suite.run_scenario(target_scenario)
            report = {
                "scenario": scenario,
                "result": result.to_dict(),
                "timestamp": time.time()
            }
        
        return report
        
    except Exception as e:
        logger.error(f"Stress test error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Stress test failed: {str(e)}")

@app.get("/admin/config", tags=["Administration"])
async def get_current_configuration():
    """⚙️ Configuration actuelle"""
    
    return {
        "environment": config.environment.value,
        "debug_mode": config.debug,
        "features_enabled": config.features,
        "performance_config": {
            "worker_count": config.performance.worker_count,
            "default_batch_size": config.performance.default_batch_size,
            "max_concurrent_batches": config.performance.max_concurrent_batches,
            "cache_enabled": config.performance.cache_enabled
        },
        "monitoring_config": {
            "prometheus_enabled": config.monitoring.enable_prometheus,
            "health_checks_enabled": config.monitoring.enable_health_checks,
            "system_monitoring_enabled": config.monitoring.enable_system_monitoring
        },
        "security_config": {
            "rate_limiting_enabled": config.security.enable_rate_limiting,
            "cors_origins": config.security.cors_origins
        }
    }

@app.get("/admin/cache/stats", tags=["Administration"])
async def get_cache_statistics():
    """🗄️ Statistiques détaillées du cache"""
    
    if not app_state["cache_manager"]:
        raise HTTPException(status_code=503, detail="Cache not available")
    
    cache_stats = app_state["cache_manager"].cache.get_stats()
    
    return {
        "timestamp": time.time(),
        "cache_statistics": cache_stats,
        "performance_summary": {
            "hit_rate_percent": cache_stats.get("hit_rate_percent", 0),
            "total_operations": cache_stats.get("hits", 0) + cache_stats.get("misses", 0),
            "redis_connected": cache_stats.get("redis_connected", False),
            "memory_cache_size": cache_stats.get("memory_cache_size", 0)
        }
    }

# === HANDLERS D'ERREURS GLOBAUX ===

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """🛡️ Gestionnaire d'erreurs global avec graceful degradation"""
    
    if app_state["degradation_manager"]:
        # Utiliser le gestionnaire de dégradation
        error_result = await app_state["degradation_manager"].degradation_manager.handle_error(
            exc,
            context={
                "endpoint": str(request.url.path),
                "method": request.method,
                "request_id": request.headers.get("X-Request-ID")
            }
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "fallback_applied": True,
                "error_id": error_result.get("error_info", {}).get("type", "unknown"),
                "timestamp": time.time()
            }
        )
    else:
        # Fallback basique
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "timestamp": time.time()
            }
        )

# === SIGNAL HANDLERS ===

def setup_signal_handlers():
    """📡 Configuration des gestionnaires de signaux"""
    
    def signal_handler(signum, frame):
        logger.info(f"🛑 Signal {signum} received, initiating graceful shutdown")
        app_state["shutdown_initiated"] = True
        
        # Donner du temps pour terminer les requêtes en cours
        import threading
        def delayed_exit():
            time.sleep(5)
            sys.exit(0)
        
        threading.Thread(target=delayed_exit, daemon=True).start()
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

# === IMPORTS DES ENDPOINTS ORIGINAUX ===

# Ici, nous pourrions importer et inclure les endpoints originaux de main.py
# Pour l'instant, on garde la structure de base

# TODO: Inclure les endpoints de matching, Google Maps, etc. depuis main.py original

if __name__ == "__main__":
    # Configuration des signal handlers
    setup_signal_handlers()
    
    print("🎯 === NEXTVISION PRODUCTION STARTUP ===")
    print(f"🌍 Environment: {config.environment.value}")
    print(f"🐛 Debug mode: {config.debug}")
    print(f"⚡ Worker count: {config.performance.worker_count}")
    print(f"🗄️ Cache enabled: {config.performance.cache_enabled}")
    print(f"📊 Monitoring: {config.monitoring.enable_prometheus}")
    print(f"🛡️ Rate limiting: {config.security.enable_rate_limiting}")
    print("")
    print("🚀 Starting Nextvision with full robustness stack...")
    print("===============================================")
    
    # Configuration Uvicorn selon l'environnement
    if config.is_production():
        # Production: utiliser Gunicorn + Uvicorn workers
        uvicorn.run(
            "main_production:app",
            host=config.host,
            port=config.port,
            workers=config.performance.worker_count,
            access_log=config.logging.log_requests,
            log_level=config.logging.log_level.value.lower(),
            proxy_headers=True,
            forwarded_allow_ips="*"
        )
    else:
        # Développement: mode reload
        uvicorn.run(
            "main_production:app",
            host=config.host,
            port=config.port,
            reload=config.reload,
            access_log=config.logging.log_requests,
            log_level=config.logging.log_level.value.lower()
        )
