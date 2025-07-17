#!/bin/bash

# 🚀 Nextvision V3.0 - Script de Tests avec Couverture de Code
# ============================================================
#
# Script optimisé pour lancer les tests Nextvision V3.0 avec 
# couverture de code réelle sur modules nextvision.services.*
#
# Usage:
#   ./run_tests_v3.sh                    # Tests basiques
#   ./run_tests_v3.sh coverage           # Tests + couverture
#   ./run_tests_v3.sh real-modules       # Tests modules réels seulement
#   ./run_tests_v3.sh performance        # Tests performance
#   ./run_tests_v3.sh clean              # Nettoie rapports précédents
#
# Version: 3.0.0 - Coverage & Performance Optimization
# Author: NEXTEN Team - Coverage Fix

set -e  # Arrête le script en cas d'erreur

# ============================================================================
# CONFIGURATION & COULEURS
# ============================================================================

# Couleurs pour affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Répertoires
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORTS_DIR="$PROJECT_ROOT/reports"
COVERAGE_DIR="$REPORTS_DIR/coverage_html"
LOG_FILE="$REPORTS_DIR/test_execution.log"

# Configuration pytest
PYTEST_ARGS=""
MODE="basic"

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

print_header() {
    echo -e "${BLUE}🚀 NEXTVISION V3.0 - TESTS & COUVERTURE DE CODE${NC}"
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${CYAN}📅 $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${CYAN}📂 Répertoire: $PROJECT_ROOT${NC}"
    echo -e "${CYAN}🔧 Mode: $MODE${NC}"
    echo ""
}

print_section() {
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}$(printf '=%.0s' {1..60})${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}📋 $1${NC}"
}

# ============================================================================
# PRÉPARATION ENVIRONNEMENT
# ============================================================================

setup_environment() {
    print_section "🔧 PRÉPARATION ENVIRONNEMENT"
    
    # Création répertoires de rapports
    mkdir -p "$REPORTS_DIR"
    mkdir -p "$COVERAGE_DIR"
    
    # Variables d'environnement pour tests
    export NEXTVISION_ENV=test
    export NEXTVISION_DEBUG=false
    export NEXTVISION_CACHE_ENABLED=true
    export NEXTVISION_LOG_LEVEL=WARNING
    export PYTEST_RUNNING=true
    export PYTHONDONTWRITEBYTECODE=1
    
    print_success "Environnement configuré"
    print_info "Répertoire rapports: $REPORTS_DIR"
    print_info "Variables d'environnement définies"
    echo ""
}

# ============================================================================
# VÉRIFICATIONS PRÉ-TESTS
# ============================================================================

check_dependencies() {
    print_section "🔍 VÉRIFICATION DÉPENDANCES"
    
    # Vérification pytest
    if ! command -v pytest &> /dev/null; then
        print_error "pytest non installé"
        exit 1
    fi
    
    # Vérification pytest-cov
    if ! python -c "import pytest_cov" &> /dev/null; then
        print_warning "pytest-cov non installé, installation..."
        pip install pytest-cov
    fi
    
    # Vérification structure projet
    if [ ! -d "nextvision" ]; then
        print_error "Répertoire nextvision/ non trouvé"
        exit 1
    fi
    
    if [ ! -d "tests" ]; then
        print_error "Répertoire tests/ non trouvé"
        exit 1
    fi
    
    print_success "Toutes les dépendances sont disponibles"
    echo ""
}

diagnose_modules() {
    print_section "🔍 DIAGNOSTIC MODULES NEXTVISION"
    
    # Liste des modules attendus
    EXPECTED_MODULES=(
        "nextvision.services.bidirectional_scorer"
        "nextvision.services.enhanced_bidirectional_scorer_v3"
        "nextvision.services.google_maps_service"
        "nextvision.services.transport_calculator"
        "nextvision.services.motivations_scorer_v3"
        "nextvision.services.listening_reasons_scorer_v3"
        "nextvision.services.professional_motivations_scorer_v3"
        "nextvision.services.scorers_v3.location_transport_scorer_v3"
    )
    
    AVAILABLE_COUNT=0
    MISSING_COUNT=0
    
    for module in "${EXPECTED_MODULES[@]}"; do
        if python -c "import $module" &> /dev/null; then
            print_success "Module disponible: $module"
            ((AVAILABLE_COUNT++))
        else
            print_warning "Module manquant/erreur: $module"
            ((MISSING_COUNT++))
        fi
    done
    
    echo ""
    print_info "Modules disponibles: $AVAILABLE_COUNT"
    print_info "Modules manquants: $MISSING_COUNT"
    
    if [ $AVAILABLE_COUNT -eq 0 ]; then
        print_error "Aucun module nextvision.services importable !"
        print_info "Vérifiez que le module enhanced_bidirectional_scorer_v3.py a été créé"
        exit 1
    fi
    
    echo ""
}

# ============================================================================
# NETTOYAGE
# ============================================================================

clean_previous_reports() {
    if [ "$MODE" = "clean" ]; then
        print_section "🧹 NETTOYAGE RAPPORTS PRÉCÉDENTS"
        
        rm -rf "$COVERAGE_DIR"
        rm -f "$REPORTS_DIR"/*.xml
        rm -f "$REPORTS_DIR"/*.json
        rm -f "$REPORTS_DIR"/*.log
        rm -rf .pytest_cache
        rm -rf .coverage
        
        print_success "Rapports précédents supprimés"
        exit 0
    fi
    
    # Nettoyage partiel pour nouveaux tests
    rm -f "$LOG_FILE"
    rm -f .coverage
}

# ============================================================================
# CONFIGURATION TESTS PAR MODE
# ============================================================================

configure_basic_tests() {
    print_section "⚙️ CONFIGURATION TESTS BASIQUES"
    
    PYTEST_ARGS="-v --tb=short --color=yes"
    print_info "Tests basiques configurés"
}

configure_coverage_tests() {
    print_section "📊 CONFIGURATION TESTS COUVERTURE"
    
    PYTEST_ARGS="-v --tb=short --color=yes \
        --cov=nextvision.services \
        --cov=nextvision.models \
        --cov-report=term-missing \
        --cov-report=html:$COVERAGE_DIR \
        --cov-report=xml:$REPORTS_DIR/coverage.xml \
        --cov-report=json:$REPORTS_DIR/coverage.json \
        --cov-fail-under=30"
    
    print_info "Couverture configurée avec seuil 30%"
    print_info "Rapports: terminal + HTML + XML + JSON"
}

configure_real_modules_tests() {
    print_section "🎯 CONFIGURATION TESTS MODULES RÉELS"
    
    PYTEST_ARGS="-v --tb=short --color=yes \
        -m real_modules \
        --cov=nextvision.services \
        --cov-report=term-missing \
        --cov-report=html:$COVERAGE_DIR \
        --cov-fail-under=20"
    
    print_info "Tests modules réels uniquement"
}

configure_performance_tests() {
    print_section "⚡ CONFIGURATION TESTS PERFORMANCE"
    
    PYTEST_ARGS="-v --tb=short --color=yes \
        -m performance \
        --durations=10"
    
    print_info "Tests performance configurés"
}

# ============================================================================
# EXÉCUTION TESTS
# ============================================================================

run_tests() {
    print_section "🚀 EXÉCUTION DES TESTS"
    
    # Fichiers de tests prioritaires
    TEST_FILES=(
        "tests/test_nextvision_real_modules.py"
        "tests/test_enhanced_scorer_v3_integration.py"
    )
    
    # Commande pytest finale
    PYTEST_CMD="pytest $PYTEST_ARGS"
    
    # Ajout des fichiers de tests si ils existent
    for test_file in "${TEST_FILES[@]}"; do
        if [ -f "$test_file" ]; then
            PYTEST_CMD="$PYTEST_CMD $test_file"
        fi
    done
    
    print_info "Commande: $PYTEST_CMD"
    echo ""
    
    # Exécution avec logging
    if $PYTEST_CMD 2>&1 | tee "$LOG_FILE"; then
        TESTS_SUCCESS=true
        print_success "Tests exécutés avec succès"
    else
        TESTS_SUCCESS=false
        print_error "Échec lors de l'exécution des tests"
    fi
    
    echo ""
}

# ============================================================================
# GÉNÉRATION RAPPORTS
# ============================================================================

generate_reports() {
    print_section "📋 GÉNÉRATION RAPPORTS"
    
    # Rapport d'exécution
    EXECUTION_REPORT="$REPORTS_DIR/execution_report_$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$EXECUTION_REPORT" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "mode": "$MODE",
    "tests_success": $TESTS_SUCCESS,
    "project_root": "$PROJECT_ROOT",
    "pytest_command": "$PYTEST_CMD",
    "reports": {
        "log_file": "$LOG_FILE",
        "coverage_html": "$COVERAGE_DIR/index.html",
        "coverage_xml": "$REPORTS_DIR/coverage.xml",
        "coverage_json": "$REPORTS_DIR/coverage.json"
    }
}
EOF
    
    print_success "Rapport d'exécution: $EXECUTION_REPORT"
    
    # Affichage liens rapports
    if [ -f "$COVERAGE_DIR/index.html" ]; then
        print_info "📊 Rapport HTML couverture: file://$COVERAGE_DIR/index.html"
    fi
    
    if [ -f "$REPORTS_DIR/coverage.xml" ]; then
        print_info "📄 Rapport XML couverture: $REPORTS_DIR/coverage.xml"
    fi
}

display_summary() {
    print_section "📊 RÉSUMÉ FINAL"
    
    # Extraction stats de couverture si disponible
    if [ -f "$REPORTS_DIR/coverage.json" ]; then
        COVERAGE_PERCENT=$(python3 -c "
import json
try:
    with open('$REPORTS_DIR/coverage.json') as f:
        data = json.load(f)
    print(f\"{data['totals']['percent_covered']:.1f}%\")
except:
    print('N/A')
" 2>/dev/null || echo "N/A")
        
        if [ "$COVERAGE_PERCENT" != "N/A" ]; then
            print_info "🎯 Couverture de code: $COVERAGE_PERCENT"
        fi
    fi
    
    # Status final
    if [ "$TESTS_SUCCESS" = true ]; then
        print_success "TESTS RÉUSSIS ✅"
        echo -e "${GREEN}🎉 Nextvision V3.0 - Tests validés avec succès !${NC}"
    else
        print_error "TESTS ÉCHOUÉS ❌"
        echo -e "${RED}💥 Nextvision V3.0 - Échec des tests${NC}"
    fi
    
    echo ""
    print_info "📂 Tous les rapports sont dans: $REPORTS_DIR"
    print_info "📋 Log détaillé: $LOG_FILE"
}

# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

main() {
    # Analyse des arguments
    case "${1:-basic}" in
        "coverage")
            MODE="coverage"
            ;;
        "real-modules")
            MODE="real-modules"
            ;;
        "performance")
            MODE="performance"
            ;;
        "clean")
            MODE="clean"
            ;;
        *)
            MODE="basic"
            ;;
    esac
    
    # Exécution séquentielle
    print_header
    setup_environment
    check_dependencies
    diagnose_modules
    clean_previous_reports
    
    case "$MODE" in
        "coverage")
            configure_coverage_tests
            ;;
        "real-modules")
            configure_real_modules_tests
            ;;
        "performance")
            configure_performance_tests
            ;;
        *)
            configure_basic_tests
            ;;
    esac
    
    run_tests
    generate_reports
    display_summary
    
    # Code de sortie basé sur succès des tests
    if [ "$TESTS_SUCCESS" = true ]; then
        exit 0
    else
        exit 1
    fi
}

# ============================================================================
# AIDE
# ============================================================================

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    echo "🚀 Nextvision V3.0 - Script de Tests & Couverture"
    echo ""
    echo "Usage:"
    echo "  ./run_tests_v3.sh [MODE]"
    echo ""
    echo "Modes disponibles:"
    echo "  basic        Tests basiques (défaut)"
    echo "  coverage     Tests + couverture de code complète"
    echo "  real-modules Tests modules réels seulement"
    echo "  performance  Tests performance uniquement"
    echo "  clean        Nettoie les rapports précédents"
    echo ""
    echo "Exemples:"
    echo "  ./run_tests_v3.sh coverage     # Tests avec couverture"
    echo "  ./run_tests_v3.sh clean        # Nettoyage rapports"
    echo ""
    exit 0
fi

# Lancement du script principal
main "$@"
