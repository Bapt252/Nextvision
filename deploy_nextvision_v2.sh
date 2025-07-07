#!/bin/bash

# 🚀 Nextvision v2.0 - Script de Déploiement Automatisé
# 
# Déploiement complet de l'architecture bidirectionnelle :
# - Validation environnement
# - Installation dépendances  
# - Migration données (69 CVs + 35 FDPs)
# - Tests automatisés
# - Démarrage serveur
#
# Usage: ./deploy_nextvision_v2.sh [--production|--development]

set -e  # Arrêt si erreur

# === CONFIGURATION ===

VERSION="2.0.0"
PYTHON_MIN_VERSION="3.8"
API_PORT=8000
ENVIRONMENT=${1:-development}

# Couleurs pour logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# === FONCTIONS UTILITAIRES ===

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "\n${PURPLE}=== $1 ===${NC}"
}

# === VÉRIFICATIONS PRÉREQUIS ===

check_python_version() {
    log_step "Vérification Python"
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 non trouvé. Installation requise."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    log_info "Python version: $PYTHON_VERSION"
    
    # Vérification version minimale
    if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
        log_error "Python >= $PYTHON_MIN_VERSION requis. Version actuelle: $PYTHON_VERSION"
        exit 1
    fi
    
    log_success "Python version OK"
}

check_git_branch() {
    log_step "Vérification Git"
    
    if ! command -v git &> /dev/null; then
        log_warning "Git non trouvé. Certaines fonctionnalités seront limitées."
        return 0
    fi
    
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
    log_info "Branche Git: $CURRENT_BRANCH"
    
    if [[ "$CURRENT_BRANCH" != "feature/bidirectional-matching-v2" && "$CURRENT_BRANCH" != "main" ]]; then
        log_warning "Branche inattendue. Recommandé: feature/bidirectional-matching-v2"
    fi
    
    log_success "Git configuration OK"
}

check_port_availability() {
    log_step "Vérification Port $API_PORT"
    
    if netstat -tuln 2>/dev/null | grep -q ":$API_PORT "; then
        log_warning "Port $API_PORT déjà utilisé. Arrêt du service existant..."
        
        # Tentative d'arrêt gracieux
        pkill -f "uvicorn.*:$API_PORT" 2>/dev/null || true
        sleep 2
        
        if netstat -tuln 2>/dev/null | grep -q ":$API_PORT "; then
            log_error "Impossible de libérer le port $API_PORT"
            exit 1
        fi
    fi
    
    log_success "Port $API_PORT disponible"
}

# === INSTALLATION ===

setup_python_environment() {
    log_step "Configuration Environnement Python"
    
    # Création virtual environment si nécessaire
    if [[ "$ENVIRONMENT" == "production" ]]; then
        if [[ ! -d "venv" ]]; then
            log_info "Création virtual environment..."
            python3 -m venv venv
        fi
        
        log_info "Activation virtual environment..."
        source venv/bin/activate
    fi
    
    # Mise à jour pip
    log_info "Mise à jour pip..."
    python3 -m pip install --upgrade pip
    
    log_success "Environnement Python configuré"
}

install_dependencies() {
    log_step "Installation Dépendances"
    
    # Installation requirements principal
    if [[ -f "requirements.txt" ]]; then
        log_info "Installation requirements.txt..."
        pip install -r requirements.txt
    fi
    
    # Installation requirements production si nécessaire
    if [[ "$ENVIRONMENT" == "production" && -f "requirements-production.txt" ]]; then
        log_info "Installation requirements-production.txt..."
        pip install -r requirements-production.txt
    fi
    
    # Dépendances tests
    log_info "Installation dépendances tests..."
    pip install pytest pytest-asyncio psutil
    
    log_success "Dépendances installées"
}

setup_configuration() {
    log_step "Configuration Application"
    
    # Configuration .env
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.example" ]]; then
            log_info "Création .env depuis .env.example..."
            cp .env.example .env
            log_warning "Pensez à configurer votre clé Google Maps dans .env"
        else
            log_info "Création .env minimal..."
            cat > .env << EOF
# Nextvision v2.0 Configuration
ENVIRONMENT=$ENVIRONMENT
API_PORT=$API_PORT
LOG_LEVEL=INFO

# Google Maps (optionnel)
GOOGLE_MAPS_API_KEY=YOUR_API_KEY

# Database (optionnel)  
DATABASE_URL=sqlite:///nextvision.db
EOF
        fi
    fi
    
    # Création répertoires nécessaires
    mkdir -p data/{CV_TEST,FDP_TEST,bidirectional_migrated,logs}
    mkdir -p logs
    
    log_success "Configuration OK"
}

# === MIGRATION DONNÉES ===

migrate_data() {
    log_step "Migration Données Bidirectionnelles"
    
    if [[ -f "scripts/migrate_data_to_bidirectional.py" ]]; then
        log_info "Lancement migration 69 CVs + 35 FDPs..."
        
        # Timeout de 5 minutes pour la migration
        timeout 300 python3 scripts/migrate_data_to_bidirectional.py || {
            log_warning "Migration timeout ou échouée. Génération données test..."
            # La migration génère automatiquement des données test si les vrais fichiers ne sont pas trouvés
        }
        
        # Vérification résultats
        if [[ -d "data/bidirectional_migrated" ]]; then
            CANDIDATS_COUNT=$(find data/bidirectional_migrated/candidats -name "*.json" 2>/dev/null | wc -l)
            ENTREPRISES_COUNT=$(find data/bidirectional_migrated/entreprises -name "*.json" 2>/dev/null | wc -l)
            
            log_info "Données migrées: $CANDIDATS_COUNT candidats, $ENTREPRISES_COUNT entreprises"
            log_success "Migration données terminée"
        else
            log_warning "Pas de données migrées - tests avec données synthétiques"
        fi
    else
        log_warning "Script de migration non trouvé - données test seulement"
    fi
}

# === TESTS ===

run_tests() {
    log_step "Exécution Tests Automatisés"
    
    if [[ -f "tests/test_bidirectional_architecture.py" ]]; then
        log_info "Lancement tests bidirectionnels..."
        
        # Tests avec timeout
        timeout 120 python3 -m pytest tests/test_bidirectional_architecture.py \
            -v \
            --tb=short \
            --durations=5 \
            || {
                log_warning "Certains tests ont échoué - déploiement continue"
                return 0
            }
        
        log_success "Tests validés"
    else
        log_warning "Tests automatisés non trouvés"
    fi
}

# === DÉMARRAGE ===

start_server() {
    log_step "Démarrage Serveur Nextvision v2.0"
    
    # Choix du fichier main selon environnement
    MAIN_FILE="main_v2.py"
    if [[ "$ENVIRONMENT" == "production" && -f "main_production.py" ]]; then
        MAIN_FILE="main_production.py"
    fi
    
    if [[ ! -f "$MAIN_FILE" ]]; then
        log_error "Fichier principal $MAIN_FILE non trouvé"
        exit 1
    fi
    
    log_info "Démarrage $MAIN_FILE sur port $API_PORT..."
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        # Mode production : background avec logs
        nohup python3 "$MAIN_FILE" > logs/nextvision.log 2>&1 &
        SERVER_PID=$!
        echo $SERVER_PID > logs/nextvision.pid
        
        sleep 3
        
        # Vérification démarrage
        if kill -0 $SERVER_PID 2>/dev/null; then
            log_success "Serveur démarré en arrière-plan (PID: $SERVER_PID)"
            log_info "Logs: tail -f logs/nextvision.log"
        else
            log_error "Échec démarrage serveur"
            exit 1
        fi
    else
        # Mode développement : foreground
        log_info "Mode développement - serveur en foreground"
        log_info "Arrêt avec Ctrl+C"
        python3 "$MAIN_FILE"
    fi
}

# === VALIDATION POST-DÉPLOIEMENT ===

validate_deployment() {
    log_step "Validation Déploiement"
    
    # Attendre que le serveur soit prêt
    sleep 5
    
    # Test health check
    log_info "Test health check..."
    
    if command -v curl &> /dev/null; then
        if curl -f "http://localhost:$API_PORT/api/v1/health" >/dev/null 2>&1; then
            log_success "Health check v1.0 OK"
        else
            log_warning "Health check v1.0 échoué"
        fi
        
        if curl -f "http://localhost:$API_PORT/api/v2/matching/health" >/dev/null 2>&1; then
            log_success "Health check bidirectionnel v2.0 OK"
        else
            log_warning "Health check bidirectionnel échoué"
        fi
    else
        log_warning "curl non disponible - tests manuels requis"
    fi
    
    # Affichage URLs importantes
    log_info "URLs importantes:"
    echo "  📚 Documentation: http://localhost:$API_PORT/docs"
    echo "  ❤️ Health v1.0: http://localhost:$API_PORT/api/v1/health"
    echo "  🎯 Health v2.0: http://localhost:$API_PORT/api/v2/matching/health"
    echo "  🚀 Pipeline: http://localhost:$API_PORT/api/v2/conversion/commitment/direct-match"
}

# === NETTOYAGE ===

cleanup_on_exit() {
    if [[ "$ENVIRONMENT" == "development" ]]; then
        log_info "Nettoyage ressources développement..."
        # Nettoyage si nécessaire
    fi
}

trap cleanup_on_exit EXIT

# === MENU PRINCIPAL ===

show_banner() {
    echo -e "${PURPLE}"
    echo "🎯 =============================================="
    echo "   NEXTVISION v$VERSION - DÉPLOIEMENT"
    echo "   Matching Bidirectionnel IA Adaptatif"
    echo "=============================================="
    echo -e "${NC}"
    echo "Environment: $ENVIRONMENT"
    echo "Port API: $API_PORT"
    echo ""
}

show_help() {
    echo "Usage: $0 [--production|--development]"
    echo ""
    echo "Options:"
    echo "  --production   Déploiement production (venv, background)"
    echo "  --development  Déploiement développement (foreground)"
    echo "  --help         Affiche cette aide"
    echo ""
    echo "Étapes du déploiement:"
    echo "  1. Vérification prérequis"
    echo "  2. Installation dépendances"
    echo "  3. Configuration application"
    echo "  4. Migration données bidirectionnelles"
    echo "  5. Tests automatisés"
    echo "  6. Démarrage serveur"
    echo "  7. Validation déploiement"
}

# === EXÉCUTION PRINCIPALE ===

main() {
    show_banner
    
    case ${1:-} in
        --help|-h)
            show_help
            exit 0
            ;;
        --production)
            ENVIRONMENT="production"
            ;;
        --development|"")
            ENVIRONMENT="development"
            ;;
        *)
            log_error "Option inconnue: $1"
            show_help
            exit 1
            ;;
    esac
    
    log_info "Démarrage déploiement Nextvision v$VERSION ($ENVIRONMENT)"
    
    # Étapes du déploiement
    check_python_version
    check_git_branch
    check_port_availability
    
    setup_python_environment
    install_dependencies
    setup_configuration
    
    migrate_data
    run_tests
    
    start_server
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        validate_deployment
        
        log_success "🎉 Déploiement production terminé !"
        log_info "Serveur en arrière-plan - PID: $(cat logs/nextvision.pid 2>/dev/null || echo 'N/A')"
        log_info "Arrêt: kill \$(cat logs/nextvision.pid)"
    else
        log_success "🎉 Déploiement développement terminé !"
        log_info "Serveur en foreground - Arrêt avec Ctrl+C"
    fi
}

# Lancement si script exécuté directement
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
