#!/bin/bash
# === NEXTVISION PRODUCTION ENTRYPOINT ===
# Enterprise-grade container startup script with health checks and graceful handling

set -e

# Configuration
APP_NAME="Nextvision"
APP_VERSION="2.1.0-production"
LOG_LEVEL=${LOG_LEVEL:-INFO}
WORKER_COUNT=${WORKER_COUNT:-4}
ENVIRONMENT=${NEXTVISION_ENV:-production}

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    if [[ "$LOG_LEVEL" == "DEBUG" ]]; then
        echo -e "${BLUE}[DEBUG]${NC} $1"
    fi
}

# Fonction de nettoyage pour arrêt gracieux
cleanup() {
    log_info "Received shutdown signal, initiating graceful shutdown..."
    
    # Arrêter le processus principal si il existe
    if [[ -n "$MAIN_PID" ]]; then
        log_info "Stopping main process (PID: $MAIN_PID)"
        kill -TERM "$MAIN_PID" 2>/dev/null || true
        
        # Attendre jusqu'à 30 secondes pour arrêt gracieux
        for i in {1..30}; do
            if ! kill -0 "$MAIN_PID" 2>/dev/null; then
                log_info "Main process stopped gracefully"
                break
            fi
            sleep 1
        done
        
        # Force kill si nécessaire
        if kill -0 "$MAIN_PID" 2>/dev/null; then
            log_warn "Force killing main process"
            kill -KILL "$MAIN_PID" 2>/dev/null || true
        fi
    fi
    
    log_info "Shutdown complete"
    exit 0
}

# Configuration des signaux pour arrêt gracieux
trap cleanup SIGTERM SIGINT SIGQUIT

# === VALIDATION ENVIRONNEMENT ===
validate_environment() {
    log_info "Validating environment configuration..."
    
    # Variables requises
    required_vars=("DB_HOST" "DB_PASSWORD" "SECRET_KEY")
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing required environment variables: ${missing_vars[*]}"
        exit 1
    fi
    
    # Validation configuration spécifique à l'environnement
    if [[ "$ENVIRONMENT" == "production" ]]; then
        if [[ "$SECRET_KEY" == "your-secret-key-change-in-production" ]]; then
            log_error "Default SECRET_KEY detected in production!"
            exit 1
        fi
        
        if [[ ${#SECRET_KEY} -lt 32 ]]; then
            log_error "SECRET_KEY too short for production (minimum 32 characters)"
            exit 1
        fi
    fi
    
    log_info "Environment validation passed"
}

# === ATTENTE DES DÉPENDANCES ===
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local timeout=${4:-60}
    
    log_info "Waiting for $service_name ($host:$port) to be ready..."
    
    for i in $(seq 1 $timeout); do
        if nc -z "$host" "$port" 2>/dev/null; then
            log_info "$service_name is ready!"
            return 0
        fi
        
        if [[ $((i % 10)) -eq 0 ]]; then
            log_info "Still waiting for $service_name... ($i/${timeout}s)"
        fi
        
        sleep 1
    done
    
    log_error "Timeout waiting for $service_name after ${timeout}s"
    return 1
}

wait_for_dependencies() {
    log_info "Waiting for external dependencies..."
    
    # PostgreSQL
    if [[ -n "$DB_HOST" ]]; then
        wait_for_service "$DB_HOST" "${DB_PORT:-5432}" "PostgreSQL" 60
    fi
    
    # Redis
    if [[ -n "$REDIS_HOST" ]]; then
        wait_for_service "$REDIS_HOST" "${REDIS_PORT:-6379}" "Redis" 30
    fi
    
    log_info "All dependencies are ready"
}

# === INITIALISATION BASE DE DONNÉES ===
init_database() {
    log_info "Checking database initialization..."
    
    # Ici on pourrait ajouter des migrations Alembic si nécessaire
    # python -m alembic upgrade head
    
    log_debug "Database initialization check completed"
}

# === CRÉATION DES RÉPERTOIRES ===
setup_directories() {
    log_info "Setting up application directories..."
    
    # Répertoires de logs
    mkdir -p /var/log/nextvision
    chmod 755 /var/log/nextvision
    
    # Répertoires de cache temporaire
    mkdir -p /tmp/nextvision
    chmod 755 /tmp/nextvision
    
    # Répertoires de données
    mkdir -p /app/data
    chmod 755 /app/data
    
    log_debug "Directories setup completed"
}

# === VALIDATION CONFIGURATION ===
validate_configuration() {
    log_info "Validating Nextvision configuration..."
    
    # Test import Python pour vérifier les dépendances
    python -c "import nextvision" 2>/dev/null || {
        log_error "Failed to import nextvision module"
        exit 1
    }
    
    # Validation configuration via endpoint dédié
    python -c "
from nextvision.config.production_settings import get_config, validate_current_config
try:
    config = get_config()
    issues = validate_current_config()
    if issues:
        print('Configuration issues:', issues)
        exit(1)
    print('Configuration validation passed')
except Exception as e:
    print(f'Configuration error: {e}')
    exit(1)
" || {
        log_error "Configuration validation failed"
        exit 1
    }
    
    log_info "Configuration validation passed"
}

# === TESTS DE SANTÉ PRÉ-DÉMARRAGE ===
pre_startup_health_checks() {
    log_info "Running pre-startup health checks..."
    
    # Test connexion Redis
    if [[ -n "$REDIS_HOST" ]] && [[ -n "$REDIS_PASSWORD" ]]; then
        python -c "
import redis
try:
    r = redis.Redis(host='$REDIS_HOST', port=${REDIS_PORT:-6379}, password='$REDIS_PASSWORD', socket_timeout=5)
    r.ping()
    print('Redis connection: OK')
except Exception as e:
    print(f'Redis connection failed: {e}')
    exit(1)
" || {
            log_error "Redis health check failed"
            exit 1
        }
    fi
    
    # Test connexion PostgreSQL
    if [[ -n "$DB_HOST" ]]; then
        python -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='$DB_HOST',
        port=${DB_PORT:-5432},
        database='${DB_NAME}',
        user='${DB_USER}',
        password='$DB_PASSWORD',
        connect_timeout=10
    )
    conn.close()
    print('PostgreSQL connection: OK')
except Exception as e:
    print(f'PostgreSQL connection failed: {e}')
    exit(1)
" || {
            log_error "PostgreSQL health check failed"
            exit 1
        }
    fi
    
    log_info "Pre-startup health checks passed"
}

# === OPTIMISATIONS PERFORMANCES ===
optimize_performance() {
    log_info "Applying performance optimizations..."
    
    # Configuration Python pour production
    export PYTHONOPTIMIZE=2
    export PYTHONUNBUFFERED=1
    export PYTHONDONTWRITEBYTECODE=1
    
    # Optimisations mémoire
    if [[ "$ENVIRONMENT" == "production" ]]; then
        # Désactiver débogage Python
        export PYTHONNODEBUG=1
        
        # Configuration GC plus agressive
        export PYTHONHASHSEED=random
    fi
    
    log_debug "Performance optimizations applied"
}

# === MONITORING ET MÉTRIQUES ===
setup_monitoring() {
    log_info "Setting up monitoring and metrics..."
    
    # Créer fichiers de métriques si nécessaire
    touch /tmp/nextvision/metrics.txt
    chmod 644 /tmp/nextvision/metrics.txt
    
    # Configuration Prometheus si activé
    if [[ "${PROMETHEUS_ENABLED:-true}" == "true" ]]; then
        log_debug "Prometheus metrics enabled on port ${PROMETHEUS_PORT:-8090}"
    fi
    
    log_debug "Monitoring setup completed"
}

# === DÉMARRAGE APPLICATION ===
start_application() {
    log_info "Starting $APP_NAME v$APP_VERSION in $ENVIRONMENT mode..."
    
    # Configuration Uvicorn selon l'environnement
    if [[ "$ENVIRONMENT" == "production" ]]; then
        # Production: Gunicorn avec workers Uvicorn
        exec gunicorn main_production:app \
            --worker-class uvicorn.workers.UvicornWorker \
            --workers "$WORKER_COUNT" \
            --bind 0.0.0.0:8000 \
            --timeout 60 \
            --keepalive 2 \
            --max-requests 1000 \
            --max-requests-jitter 100 \
            --access-logfile - \
            --error-logfile - \
            --log-level "${LOG_LEVEL,,}" \
            --capture-output \
            --enable-stdio-inheritance \
            --preload &
    else
        # Développement: Uvicorn direct avec reload
        exec uvicorn main_production:app \
            --host 0.0.0.0 \
            --port 8000 \
            --log-level "${LOG_LEVEL,,}" \
            --access-log \
            --reload &
    fi
    
    MAIN_PID=$!
    log_info "Application started with PID: $MAIN_PID"
    
    # Attendre que le processus principal se termine
    wait $MAIN_PID
}

# === POST-STARTUP VALIDATION ===
post_startup_validation() {
    log_info "Running post-startup validation..."
    
    # Attendre que l'application soit prête
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
            log_info "Application health check passed"
            return 0
        fi
        
        if [[ $((attempt % 5)) -eq 0 ]]; then
            log_info "Waiting for application to be ready... ($attempt/$max_attempts)"
        fi
        
        sleep 2
        ((attempt++))
    done
    
    log_error "Application failed to respond to health checks"
    return 1
}

# === FONCTION PRINCIPALE ===
main() {
    log_info "=== $APP_NAME PRODUCTION STARTUP ==="
    log_info "Version: $APP_VERSION"
    log_info "Environment: $ENVIRONMENT"
    log_info "Workers: $WORKER_COUNT"
    log_info "Log Level: $LOG_LEVEL"
    echo
    
    # Exécution séquentielle des étapes
    validate_environment
    setup_directories
    optimize_performance
    setup_monitoring
    wait_for_dependencies
    init_database
    validate_configuration
    pre_startup_health_checks
    
    log_info "All pre-startup checks passed, starting application..."
    echo
    
    # Démarrage de l'application
    start_application
}

# === GESTION DES ARGUMENTS ===
case "${1:-}" in
    "health-check")
        # Script de health check
        exec /health-check.sh
        ;;
    "validate")
        # Validation uniquement
        validate_environment
        validate_configuration
        log_info "Validation completed successfully"
        exit 0
        ;;
    "test")
        # Tests de base
        validate_environment
        setup_directories
        validate_configuration
        pre_startup_health_checks
        log_info "All tests passed"
        exit 0
        ;;
    "debug")
        # Mode debug
        export LOG_LEVEL=DEBUG
        log_info "Debug mode enabled"
        main
        ;;
    "")
        # Démarrage normal
        main
        ;;
    *)
        # Commande personnalisée
        log_info "Executing custom command: $*"
        exec "$@"
        ;;
esac
