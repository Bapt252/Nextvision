#!/bin/bash
# === NEXTVISION HEALTH CHECK SCRIPT ===
# Comprehensive health check for production deployment

set -e

# Configuration
HEALTH_ENDPOINT="http://localhost:8000/health"
DETAILED_HEALTH_ENDPOINT="http://localhost:8000/health/detailed"
TIMEOUT=10
RETRIES=3

# Codes de sortie
EXIT_OK=0
EXIT_WARNING=1
EXIT_CRITICAL=2
EXIT_UNKNOWN=3

log_info() {
    echo "[INFO] $1" >&2
}

log_warn() {
    echo "[WARN] $1" >&2
}

log_error() {
    echo "[ERROR] $1" >&2
}

# Test de base HTTP
basic_health_check() {
    local attempt=1
    
    while [[ $attempt -le $RETRIES ]]; do
        if curl -s -f --max-time $TIMEOUT "$HEALTH_ENDPOINT" > /dev/null 2>&1; then
            return 0
        fi
        
        log_warn "Health check attempt $attempt/$RETRIES failed"
        ((attempt++))
        sleep 1
    done
    
    return 1
}

# Test détaillé avec réponse JSON
detailed_health_check() {
    local response
    local status
    
    response=$(curl -s --max-time $TIMEOUT "$DETAILED_HEALTH_ENDPOINT" 2>/dev/null || echo "{}")
    
    if [[ -z "$response" ]] || [[ "$response" == "{}" ]]; then
        log_error "Failed to get detailed health status"
        return $EXIT_CRITICAL
    fi
    
    # Parse du statut global
    status=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('overall_status', 'unknown'))" 2>/dev/null || echo "unknown")
    
    case "$status" in
        "healthy")
            log_info "Overall status: HEALTHY"
            return $EXIT_OK
            ;;
        "degraded")
            log_warn "Overall status: DEGRADED"
            # Afficher les services dégradés
            echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    issues = data.get('issues', [])
    if issues:
        print('Issues detected:')
        for issue in issues:
            print(f'  - {issue}')
except:
    pass
" 2>/dev/null
            return $EXIT_WARNING
            ;;
        "error")
            log_error "Overall status: ERROR"
            return $EXIT_CRITICAL
            ;;
        *)
            log_error "Unknown overall status: $status"
            return $EXIT_UNKNOWN
            ;;
    esac
}

# Test de performance
performance_check() {
    local start_time
    local end_time
    local response_time
    
    start_time=$(date +%s.%N)
    
    if curl -s -f --max-time $TIMEOUT "$HEALTH_ENDPOINT" > /dev/null 2>&1; then
        end_time=$(date +%s.%N)
        response_time=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
        
        # Convertir en millisecondes
        response_time_ms=$(echo "$response_time * 1000" | bc -l 2>/dev/null || echo "0")
        response_time_ms=${response_time_ms%.*}  # Enlever les décimales
        
        if [[ $response_time_ms -gt 5000 ]]; then
            log_warn "Slow response time: ${response_time_ms}ms"
            return $EXIT_WARNING
        elif [[ $response_time_ms -gt 2000 ]]; then
            log_warn "Elevated response time: ${response_time_ms}ms"
        else
            log_info "Response time: ${response_time_ms}ms"
        fi
        
        return $EXIT_OK
    else
        log_error "Performance check failed"
        return $EXIT_CRITICAL
    fi
}

# Test de readiness (pour Kubernetes)
readiness_check() {
    local ready_endpoint="http://localhost:8000/health/ready"
    
    if curl -s -f --max-time $TIMEOUT "$ready_endpoint" > /dev/null 2>&1; then
        log_info "Service is ready"
        return $EXIT_OK
    else
        log_error "Service is not ready"
        return $EXIT_CRITICAL
    fi
}

# Test de liveness (pour Kubernetes)
liveness_check() {
    local live_endpoint="http://localhost:8000/health/live"
    
    if curl -s -f --max-time $TIMEOUT "$live_endpoint" > /dev/null 2>&1; then
        log_info "Service is alive"
        return $EXIT_OK
    else
        log_error "Service is not alive"
        return $EXIT_CRITICAL
    fi
}

# Test des métriques Prometheus
metrics_check() {
    local metrics_endpoint="http://localhost:8090/metrics"
    
    if curl -s --max-time $TIMEOUT "$metrics_endpoint" > /dev/null 2>&1; then
        log_info "Metrics endpoint accessible"
        return $EXIT_OK
    else
        log_warn "Metrics endpoint not accessible"
        return $EXIT_WARNING
    fi
}

# Fonction principale
main() {
    local check_type="${1:-basic}"
    local exit_code=$EXIT_OK
    
    case "$check_type" in
        "basic")
            if basic_health_check; then
                log_info "Basic health check: PASS"
                exit_code=$EXIT_OK
            else
                log_error "Basic health check: FAIL"
                exit_code=$EXIT_CRITICAL
            fi
            ;;
        
        "detailed")
            detailed_health_check
            exit_code=$?
            ;;
        
        "performance")
            performance_check
            exit_code=$?
            ;;
        
        "readiness")
            readiness_check
            exit_code=$?
            ;;
        
        "liveness")
            liveness_check
            exit_code=$?
            ;;
        
        "metrics")
            metrics_check
            exit_code=$?
            ;;
        
        "full")
            log_info "Running comprehensive health check..."
            
            # Test de base
            if ! basic_health_check; then
                log_error "Basic health check failed"
                exit $EXIT_CRITICAL
            fi
            
            # Test détaillé
            detailed_result=$(detailed_health_check)
            detailed_exit=$?
            
            if [[ $detailed_exit -eq $EXIT_CRITICAL ]]; then
                exit $EXIT_CRITICAL
            elif [[ $detailed_exit -eq $EXIT_WARNING ]]; then
                exit_code=$EXIT_WARNING
            fi
            
            # Test de performance
            performance_check
            perf_exit=$?
            
            if [[ $perf_exit -eq $EXIT_WARNING ]] && [[ $exit_code -eq $EXIT_OK ]]; then
                exit_code=$EXIT_WARNING
            fi
            
            # Test des métriques (non critique)
            metrics_check
            
            if [[ $exit_code -eq $EXIT_OK ]]; then
                log_info "Comprehensive health check: PASS"
            else
                log_warn "Comprehensive health check: ISSUES DETECTED"
            fi
            ;;
        
        *)
            echo "Usage: $0 [basic|detailed|performance|readiness|liveness|metrics|full]"
            echo ""
            echo "Health check types:"
            echo "  basic       - Simple HTTP health check (default)"
            echo "  detailed    - Detailed health status with service breakdown"
            echo "  performance - Response time performance check"
            echo "  readiness   - Kubernetes readiness probe"
            echo "  liveness    - Kubernetes liveness probe"
            echo "  metrics     - Prometheus metrics endpoint check"
            echo "  full        - Comprehensive check (all tests)"
            exit $EXIT_UNKNOWN
            ;;
    esac
    
    exit $exit_code
}

# Vérifier que curl est disponible
if ! command -v curl > /dev/null 2>&1; then
    log_error "curl is required but not installed"
    exit $EXIT_UNKNOWN
fi

# Exécuter la fonction principale
main "$@"
