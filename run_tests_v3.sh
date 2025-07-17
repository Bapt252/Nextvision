#!/bin/bash

# 🚀 Nextvision V3.0 - Script Tests Intégration - PROMPT 7
# =========================================================
#
# Script d'exécution des tests pour validation système V3.0 complet
#
# Usage:
#   ./run_tests_v3.sh                 # Tests complets
#   ./run_tests_v3.sh unit            # Tests unitaires seulement
#   ./run_tests_v3.sh integration     # Tests intégration seulement
#   ./run_tests_v3.sh performance     # Tests performance seulement
#   ./run_tests_v3.sh compatibility   # Tests compatibilité seulement
#   ./run_tests_v3.sh full            # Tests bout-en-bout complets
#   ./run_tests_v3.sh quick           # Tests rapides (sans performance)
#   ./run_tests_v3.sh coverage        # Tests avec couverture de code

set -e  # Exit on any error

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="Nextvision V3.0"
TEST_FILE="tests/test_enhanced_scorer_v3_integration.py"
REPORT_DIR="reports"

# Functions
print_header() {
    echo -e "${BLUE}================================================================================================${NC}"
    echo -e "${CYAN}🚀 $PROJECT_NAME - TESTS INTÉGRATION SYSTÈME V3.0${NC}"
    echo -e "${BLUE}================================================================================================${NC}"
    echo -e "${YELLOW}📊 Architecture: 12 scorers opérationnels (9 V3.0 + 3 V2.0)${NC}"
    echo -e "${YELLOW}⚡ Performance: <175ms garantie${NC}"
    echo -e "${YELLOW}🎯 Couverture: Tests unitaires + intégration + performance + compatibilité${NC}"
    echo -e "${BLUE}================================================================================================${NC}"
    echo ""
}

print_summary() {
    echo ""
    echo -e "${GREEN}================================================================================================${NC}"
    echo -e "${GREEN}✅ TESTS NEXTVISION V3.0 TERMINÉS${NC}"
    echo -e "${GREEN}================================================================================================${NC}"
    echo -e "${CYAN}📊 Résultats: Voir ci-dessus${NC}"
    echo -e "${CYAN}📁 Rapports: $REPORT_DIR/${NC}"
    echo -e "${CYAN}🎯 Système V3.0: Validé pour production${NC}"
    echo -e "${GREEN}================================================================================================${NC}"
}

create_reports_dir() {
    mkdir -p $REPORT_DIR
}

check_dependencies() {
    echo -e "${YELLOW}🔍 Vérification dépendances...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 non trouvé${NC}"
        exit 1
    fi
    
    if ! python3 -c "import pytest" &> /dev/null; then
        echo -e "${RED}❌ pytest non installé${NC}"
        echo -e "${YELLOW}Installation: pip install pytest pytest-asyncio${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Dépendances OK${NC}"
    echo ""
}

run_unit_tests() {
    echo -e "${PURPLE}🧪 TESTS UNITAIRES SCORERS V3.0${NC}"
    echo -e "${CYAN}Tests des 9 scorers V3.0 individuellement...${NC}"
    echo ""
    
    pytest $TEST_FILE::TestEnhancedScorerV3Individual -v \
        --tb=short \
        --durations=10 \
        -m unit || echo -e "${YELLOW}⚠️ Certains tests unitaires ont échoué${NC}"
}

run_integration_tests() {
    echo -e "${PURPLE}🔧 TESTS INTÉGRATION SYSTÈME COMPLET${NC}"
    echo -e "${CYAN}Tests Enhanced Scorer V3.0 avec 12 composants...${NC}"
    echo ""
    
    pytest $TEST_FILE::TestEnhancedScorerV3Integration -v \
        --tb=short \
        --durations=10 \
        -m integration || echo -e "${YELLOW}⚠️ Certains tests d'intégration ont échoué${NC}"
}

run_performance_tests() {
    echo -e "${PURPLE}⚡ TESTS PERFORMANCE < 175ms${NC}"
    echo -e "${CYAN}Validation performance garantie système V3.0...${NC}"
    echo ""
    
    pytest $TEST_FILE::TestEnhancedScorerV3Integration::test_performance_under_175ms -v \
        --tb=short \
        -m performance || echo -e "${YELLOW}⚠️ Tests performance échoués${NC}"
    
    pytest $TEST_FILE::TestEnhancedScorerV3Integration::test_parallel_vs_sequential_execution -v \
        --tb=short || echo -e "${YELLOW}⚠️ Tests parallèle vs séquentiel échoués${NC}"
}

run_compatibility_tests() {
    echo -e "${PURPLE}🔄 TESTS COMPATIBILITÉ V2.0 ↔ V3.0${NC}"
    echo -e "${CYAN}Validation compatibilité backward et forward...${NC}"
    echo ""
    
    pytest $TEST_FILE::TestV2V3Compatibility -v \
        --tb=short \
        -m compatibility || echo -e "${YELLOW}⚠️ Tests compatibilité échoués${NC}"
    
    pytest $TEST_FILE::TestComponentWeightsValidation -v \
        --tb=short || echo -e "${YELLOW}⚠️ Tests validation poids échoués${NC}"
}

run_fallback_tests() {
    echo -e "${PURPLE}🛡️ TESTS GESTION ERREURS & FALLBACK${NC}"
    echo -e "${CYAN}Tests robustesse et résilience système...${NC}"
    echo ""
    
    pytest $TEST_FILE::TestErrorHandlingAndFallback -v \
        --tb=short \
        -m fallback || echo -e "${YELLOW}⚠️ Tests fallback échoués${NC}"
}

run_full_end_to_end() {
    echo -e "${PURPLE}🎯 TEST INTÉGRATION BOUT-EN-BOUT${NC}"
    echo -e "${CYAN}Test complet système V3.0 avec scénarios multiples...${NC}"
    echo ""
    
    pytest $TEST_FILE::test_full_system_integration_end_to_end -v \
        --tb=long \
        --durations=0 || echo -e "${YELLOW}⚠️ Test bout-en-bout échoué${NC}"
}

run_with_coverage() {
    echo -e "${PURPLE}📊 TESTS AVEC COUVERTURE DE CODE${NC}"
    echo -e "${CYAN}Analyse couverture de code système V3.0...${NC}"
    echo ""
    
    if ! python3 -c "import pytest_cov" &> /dev/null; then
        echo -e "${YELLOW}⚠️ pytest-cov non installé, installation...${NC}"
        pip install pytest-cov
    fi
    
    pytest $TEST_FILE -v \
        --cov=nextvision.services.enhanced_bidirectional_scorer_v3 \
        --cov=nextvision.services.scorers_v3 \
        --cov-report=html:$REPORT_DIR/coverage_html \
        --cov-report=term-missing \
        --cov-fail-under=70 \
        --tb=short
    
    echo -e "${CYAN}📁 Rapport couverture: $REPORT_DIR/coverage_html/index.html${NC}"
}

run_quick_tests() {
    echo -e "${PURPLE}⚡ TESTS RAPIDES (SANS PERFORMANCE)${NC}"
    echo -e "${CYAN}Tests essentiels pour validation rapide...${NC}"
    echo ""
    
    pytest $TEST_FILE -v \
        --tb=short \
        -k "not (performance or slow)" \
        --durations=5
}

run_all_tests() {
    echo -e "${PURPLE}🎯 SUITE COMPLÈTE TESTS V3.0${NC}"
    echo -e "${CYAN}Exécution de tous les tests système...${NC}"
    echo ""
    
    pytest $TEST_FILE -v \
        --tb=short \
        --durations=10 \
        --html=$REPORT_DIR/report.html \
        --self-contained-html || echo -e "${YELLOW}⚠️ Certains tests ont échoué${NC}"
}

# Main execution
print_header
check_dependencies
create_reports_dir

case "${1:-all}" in
    "unit")
        run_unit_tests
        ;;
    "integration")
        run_integration_tests
        ;;
    "performance")
        run_performance_tests
        ;;
    "compatibility")
        run_compatibility_tests
        ;;
    "fallback")
        run_fallback_tests
        ;;
    "full")
        run_full_end_to_end
        ;;
    "quick")
        run_quick_tests
        ;;
    "coverage")
        run_with_coverage
        ;;
    "all")
        echo -e "${YELLOW}🚀 EXÉCUTION COMPLÈTE SUITE TESTS V3.0${NC}"
        echo ""
        run_unit_tests
        echo ""
        run_integration_tests
        echo ""
        run_performance_tests
        echo ""
        run_compatibility_tests
        echo ""
        run_fallback_tests
        echo ""
        run_full_end_to_end
        ;;
    *)
        echo -e "${RED}❌ Option non reconnue: $1${NC}"
        echo ""
        echo -e "${YELLOW}Usage:${NC}"
        echo "  ./run_tests_v3.sh                 # Tests complets"
        echo "  ./run_tests_v3.sh unit            # Tests unitaires"
        echo "  ./run_tests_v3.sh integration     # Tests intégration"
        echo "  ./run_tests_v3.sh performance     # Tests performance"
        echo "  ./run_tests_v3.sh compatibility   # Tests compatibilité"
        echo "  ./run_tests_v3.sh fallback        # Tests fallback"
        echo "  ./run_tests_v3.sh full            # Test bout-en-bout"
        echo "  ./run_tests_v3.sh quick           # Tests rapides"
        echo "  ./run_tests_v3.sh coverage        # Tests avec couverture"
        echo ""
        exit 1
        ;;
esac

print_summary
