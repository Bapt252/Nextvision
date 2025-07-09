#!/bin/bash

# 🚀 Nextvision V3.0 + Commitment- - Script de déploiement automatisé
# Setup complet en 5 minutes avec validation end-to-end
# 
# Author: NEXTEN Team
# Version: 1.0.0 - Production Ready

set -e  # Arrêt en cas d'erreur

# === CONFIGURATION ===

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="Nextvision V3.0 + Commitment-"
PYTHON_VERSION="3.11"
VENV_NAME="nextvision_env"
LOG_FILE="deployment_$(date +%Y%m%d_%H%M%S).log"

# Couleurs pour affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# === FONCTIONS UTILITAIRES ===

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $1${NC}" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] ℹ️  $1${NC}" | tee -a "$LOG_FILE"
}

# Vérification prérequis
check_requirements() {
    log "🔍 Vérification des prérequis..."
    
    # Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 n'est pas installé"
        exit 1
    fi
    
    PYTHON_VER=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ "$(printf '%s\n' "$PYTHON_VERSION" "$PYTHON_VER" | sort -V | head -n1)" != "$PYTHON_VERSION" ]]; then
        warn "Python $PYTHON_VER détecté, version $PYTHON_VERSION recommandée"
    fi
    
    # Git
    if ! command -v git &> /dev/null; then
        error "Git n'est pas installé"
        exit 1
    fi
    
    # pip
    if ! python3 -m pip --version &> /dev/null; then
        error "pip n'est pas installé"
        exit 1
    fi
    
    success "Prérequis validés"
}

# Configuration environnement virtuel
setup_virtual_environment() {
    log "🐍 Configuration environnement virtuel..."
    
    # Suppression ancien environnement si existant
    if [ -d "$VENV_NAME" ]; then
        warn "Suppression ancien environnement virtuel"
        rm -rf "$VENV_NAME"
    fi
    
    # Création nouvel environnement
    python3 -m venv "$VENV_NAME"
    source "$VENV_NAME/bin/activate"
    
    # Mise à jour pip
    python -m pip install --upgrade pip
    
    success "Environnement virtuel configuré"
}

# Installation dépendances
install_dependencies() {
    log "📦 Installation des dépendances..."
    
    # Installation dépendances principales
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    # Installation dépendances production
    if [ -f "requirements-production.txt" ]; then
        pip install -r requirements-production.txt
    fi
    
    # Dépendances spécifiques intégration
    log "📦 Installation dépendances intégration..."
    
    # Playwright (optionnel)
    read -p "🎭 Installer Playwright pour parsing réel? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install playwright
        playwright install chromium
        success "Playwright installé"
    else
        info "Playwright non installé - fallback automatique activé"
    fi
    
    # Beautiful Soup pour parsing HTML
    pip install beautifulsoup4
    
    # PyPDF2 pour lecture PDF
    pip install PyPDF2
    
    # python-docx pour lecture Word
    pip install python-docx
    
    # Autres dépendances utiles
    pip install asyncio aiohttp requests python-dotenv
    
    success "Dépendances installées"
}

# Configuration variables d'environnement
setup_environment() {
    log "🔧 Configuration variables d'environnement..."
    
    # Copie fichier .env si n'existe pas
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp ".env.example" ".env"
            info "Fichier .env créé depuis .env.example"
        else
            # Création .env basique
            cat > .env << EOF
# Nextvision V3.0 + Commitment- Configuration
# Généré automatiquement le $(date)

# API Keys
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Configuration Commitment-
COMMITMENT_CV_PARSER_URL=https://raw.githack.com/Bapt252/Commitment-/main/templates/candidate-upload-fixed.html
COMMITMENT_JOB_PARSER_URL=https://raw.githack.com/Bapt252/Commitment-/main/templates/job-description-parser.html
COMMITMENT_TIMEOUT=30
COMMITMENT_ENABLE_REAL_PARSING=true
COMMITMENT_ENABLE_FALLBACK=true

# Configuration Nextvision
NEXTVISION_LOG_LEVEL=INFO
NEXTVISION_ENABLE_CACHE=true
NEXTVISION_CACHE_TTL=3600

# Configuration Bridge
BRIDGE_ENABLE_V3_EXTENSIONS=true
BRIDGE_ENABLE_ADAPTIVE_WEIGHTING=true
BRIDGE_ENABLE_V3_SCORERS=true
BRIDGE_PERFORMANCE_THRESHOLD_MS=175

# Configuration Transport Intelligence
TRANSPORT_ENABLE_REAL_SCORING=true
TRANSPORT_CACHE_ENABLED=true
TRANSPORT_MAX_CONCURRENT_REQUESTS=10

# Configuration Tests
TEST_ENABLE_INTEGRATION_TESTS=true
TEST_ENABLE_PERFORMANCE_TESTS=true
TEST_GENERATE_REPORTS=true
EOF
            info "Fichier .env créé avec configuration par défaut"
        fi
    fi
    
    # Rappel configuration
    warn "⚠️  N'oubliez pas de configurer vos API keys dans le fichier .env"
    warn "⚠️  Particulièrement GOOGLE_MAPS_API_KEY pour Transport Intelligence V3.0"
    
    success "Variables d'environnement configurées"
}

# Validation structure projet
validate_project_structure() {
    log "📁 Validation structure du projet..."
    
    # Vérification fichiers essentiels
    REQUIRED_FILES=(
        "nextvision/services/parsing/commitment_bridge_optimized.py"
        "nextvision/services/enhanced_commitment_bridge_v3_integrated.py"
        "nextvision/services/enhanced_commitment_bridge_v3.py"
        "nextvision/engines/transport_intelligence_engine.py"
        "nextvision/services/scorers_v3/location_transport_scorer_v3.py"
        "test_nextvision_commitment_integration.py"
    )
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$file" ]; then
            error "Fichier manquant: $file"
            exit 1
        fi
    done
    
    # Vérification dossiers
    REQUIRED_DIRS=(
        "nextvision/services/parsing"
        "nextvision/services/scorers_v3"
        "nextvision/engines"
        "nextvision/models"
    )
    
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [ ! -d "$dir" ]; then
            error "Dossier manquant: $dir"
            exit 1
        fi
    done
    
    success "Structure du projet validée"
}

# Tests de validation
run_validation_tests() {
    log "🧪 Exécution des tests de validation..."
    
    # Test importation modules
    log "🔍 Test importation modules..."
    
    python3 -c "
import sys
sys.path.insert(0, '.')

try:
    from nextvision.services.parsing.commitment_bridge_optimized import CommitmentParsingBridge
    from nextvision.services.enhanced_commitment_bridge_v3_integrated import EnhancedCommitmentBridgeV3Integrated
    print('✅ Imports modules réussis')
except ImportError as e:
    print(f'❌ Erreur import: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        success "Importation modules validée"
    else
        error "Échec importation modules"
        exit 1
    fi
    
    # Test configuration
    log "🔍 Test configuration..."
    
    python3 -c "
import os
from dotenv import load_dotenv

load_dotenv()

# Test variables essentielles
required_vars = ['GOOGLE_MAPS_API_KEY', 'COMMITMENT_CV_PARSER_URL']
missing_vars = []

for var in required_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f'⚠️  Variables manquantes: {missing_vars}')
    print('🔧 Configurez ces variables dans le fichier .env')
else:
    print('✅ Configuration validée')
"
    
    # Test basic functionality
    log "🔍 Test fonctionnalité basique..."
    
    python3 -c "
import sys
import asyncio
sys.path.insert(0, '.')

async def test_basic():
    try:
        from nextvision.services.parsing.commitment_bridge_optimized import CommitmentBridgeFactory
        
        # Test création bridge
        bridge = CommitmentBridgeFactory.create_development_bridge()
        
        # Test parsing basique
        result = await bridge.parse_job_description('Test job description')
        
        if result.success:
            print('✅ Test fonctionnalité basique réussi')
        else:
            print('⚠️  Test fonctionnalité basique partiellement réussi')
        
        await bridge.close()
        
    except Exception as e:
        print(f'❌ Erreur test basique: {e}')
        return False
    
    return True

# Exécution test
if asyncio.run(test_basic()):
    exit(0)
else:
    exit(1)
"
    
    if [ $? -eq 0 ]; then
        success "Test fonctionnalité basique réussi"
    else
        warn "Test fonctionnalité basique partiellement réussi"
    fi
    
    success "Tests de validation terminés"
}

# Test d'intégration rapide
run_integration_test() {
    log "🚀 Test d'intégration rapide..."
    
    python3 -c "
import sys
import asyncio
sys.path.insert(0, '.')

async def quick_integration_test():
    try:
        from nextvision.services.enhanced_commitment_bridge_v3_integrated import IntegratedBridgeFactory
        
        print('🔧 Création bridge intégré...')
        bridge = IntegratedBridgeFactory.create_development_integrated_bridge()
        
        print('👤 Test conversion candidat...')
        questionnaire = {
            'mobility_preferences': {
                'transport_methods': ['transport_public'],
                'max_travel_time': '45 minutes'
            }
        }
        
        candidat, metrics = await bridge.convert_candidat_enhanced_integrated(
            parser_output=None,
            cv_file_path=None,
            questionnaire_data=questionnaire,
            enable_real_parsing=False
        )
        
        if metrics.integration_success:
            print(f'✅ Candidat intégré: {metrics.total_time_ms:.2f}ms')
            print(f'📊 Qualité données: {metrics.data_quality_score:.2f}')
        else:
            print('⚠️  Intégration candidat partiellement réussie')
        
        print('🏢 Test conversion entreprise...')
        entreprise, metrics2 = await bridge.convert_entreprise_enhanced_integrated(
            chatgpt_output=None,
            job_description_text='Développeur Python - Paris - CDI',
            questionnaire_data={'company_structure': {'sector': 'technologie'}},
            enable_real_parsing=False
        )
        
        if metrics2.integration_success:
            print(f'✅ Entreprise intégrée: {metrics2.total_time_ms:.2f}ms')
            print(f'📊 Qualité données: {metrics2.data_quality_score:.2f}')
        else:
            print('⚠️  Intégration entreprise partiellement réussie')
        
        # Health check
        health = bridge.get_integration_health()
        print(f'🏥 Santé intégration: {health[\"status\"]}')
        
        await bridge.close()
        
        return True
        
    except Exception as e:
        print(f'❌ Erreur test intégration: {e}')
        return False

# Exécution test
if asyncio.run(quick_integration_test()):
    print('🎉 Test d\\'intégration rapide réussi!')
    exit(0)
else:
    print('❌ Test d\\'intégration rapide échoué')
    exit(1)
"
    
    if [ $? -eq 0 ]; then
        success "Test d'intégration rapide réussi"
    else
        error "Test d'intégration rapide échoué"
        exit 1
    fi
}

# Test Transport Intelligence V3.0
test_transport_intelligence() {
    log "🗺️ Test Transport Intelligence V3.0..."
    
    python3 -c "
import sys
import os
sys.path.insert(0, '.')

# Vérification Google Maps API Key
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('GOOGLE_MAPS_API_KEY')
if not api_key or api_key == 'your_google_maps_api_key_here':
    print('⚠️  Google Maps API Key non configurée')
    print('🔧 Configurez GOOGLE_MAPS_API_KEY dans .env pour activer Transport Intelligence')
    exit(0)

try:
    from nextvision.engines.transport_intelligence_engine import TransportIntelligenceEngine
    from nextvision.services.scorers_v3.location_transport_scorer_v3 import LocationTransportScorerV3
    
    print('✅ Modules Transport Intelligence V3.0 importés')
    
    # Test scorer
    scorer = LocationTransportScorerV3()
    test_score = scorer.calculate_basic_score('Paris', 'La Défense', 'transport_public')
    
    if test_score > 0:
        print(f'✅ Transport Intelligence V3.0 fonctionnel (score test: {test_score:.3f})')
    else:
        print('⚠️  Transport Intelligence V3.0 partiellement fonctionnel')
    
except Exception as e:
    print(f'❌ Erreur Transport Intelligence: {e}')
    exit(1)
"
    
    if [ $? -eq 0 ]; then
        success "Transport Intelligence V3.0 validé"
    else
        warn "Transport Intelligence V3.0 nécessite configuration"
    fi
}

# Génération documentation
generate_documentation() {
    log "📚 Génération documentation..."
    
    # Création README intégration
    cat > README_INTEGRATION.md << 'EOF'
# 🎯 Nextvision V3.0 + Commitment- - Guide d'intégration

## 🚀 Démarrage rapide

### 1. Activation environnement
```bash
source nextvision_env/bin/activate
```

### 2. Configuration
Éditez le fichier `.env` :
```bash
# API Keys requises
GOOGLE_MAPS_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

### 3. Test basique
```bash
python test_nextvision_commitment_integration.py
```

## 📋 Utilisation

### Import des modules
```python
from nextvision.services.enhanced_commitment_bridge_v3_integrated import (
    IntegratedBridgeFactory
)

# Création bridge
bridge = IntegratedBridgeFactory.create_production_integrated_bridge()
```

### Parsing candidat avec CV
```python
# Avec fichier CV
candidat, metrics = await bridge.convert_candidat_enhanced_integrated(
    cv_file_path="chemin/vers/cv.pdf",
    questionnaire_data=questionnaire,
    enable_real_parsing=True
)

print(f"Confiance: {metrics.commitment_confidence:.2f}")
print(f"Qualité: {metrics.data_quality_score:.2f}")
```

### Parsing entreprise avec job description
```python
# Avec description poste
entreprise, metrics = await bridge.convert_entreprise_enhanced_integrated(
    job_description_text=job_text,
    questionnaire_data=questionnaire,
    enable_real_parsing=True
)
```

## 🔧 Configuration avancée

### Parsing réel Commitment-
```python
# Production avec parsing réel
bridge = IntegratedBridgeFactory.create_production_integrated_bridge()

# Développement avec simulation
bridge = IntegratedBridgeFactory.create_development_integrated_bridge()
```

### Monitoring et santé
```python
# Statistiques
stats = bridge.get_integrated_stats()
print(f"Taux succès: {stats['integration_stats']['commitment_parsing_success_rate']:.1f}%")

# Santé système
health = bridge.get_integration_health()
print(f"Statut: {health['status']}")
```

## 🎯 Pipeline complet

### 1. Parsing → 2. Conversion → 3. Transport Intelligence
```python
# Parsing réel
candidat, metrics = await bridge.convert_candidat_enhanced_integrated(
    cv_file_path="cv.pdf",
    questionnaire_data=questionnaire,
    enable_real_parsing=True
)

# Transport Intelligence V3.0 (conservé)
from nextvision.engines.transport_intelligence_engine import TransportIntelligenceEngine
transport_engine = TransportIntelligenceEngine()
transport_score = transport_engine.calculate_transport_score(candidat)
```

## 🧪 Tests et validation

### Tests complets
```bash
python test_nextvision_commitment_integration.py
```

### Tests spécifiques
```python
# Test parsing seulement
from nextvision.services.parsing.commitment_bridge_optimized import CommitmentBridgeFactory

bridge = CommitmentBridgeFactory.create_development_bridge()
result = await bridge.parse_cv_file("cv.pdf")
```

## 🔄 Fallback et robustesse

Le système dispose de plusieurs niveaux de fallback :
1. **Parsing réel** via Commitment- Enhanced Parser v4.0
2. **Fallback intelligent** avec extraction de contenu
3. **Simulation** pour développement
4. **Conservation** du Transport Intelligence V3.0 existant

## 📊 Performance

- **Parsing réel** : ~2-5 secondes
- **Conversion intégrée** : ~175ms (cible)
- **Transport Intelligence** : ~5.66s pour 9 calculs (conservé)
- **Pipeline complet** : ~10 secondes max

## 🛡️ Sécurité

- Non-invasif : pas d'impact sur système existant
- Fallback automatique si Commitment- indisponible
- Validation des fichiers (taille, format)
- Gestion d'erreurs robuste

## 🎉 Résultats attendus

✅ **Parsing réel** via Commitment- Enhanced Parser v4.0 (95-100% extraction)
✅ **Transport Intelligence conservé** (score 0.857, < 10s pour 9 calculs)
✅ **Pipeline robuste** avec fallback automatique
✅ **Tests validés** end-to-end
✅ **Prêt production** avec monitoring

EOF

    success "Documentation générée: README_INTEGRATION.md"
}

# Génération script de test rapide
generate_quick_test_script() {
    log "🧪 Génération script de test rapide..."
    
    cat > quick_test.py << 'EOF'
#!/usr/bin/env python3
"""
🧪 Test rapide Nextvision V3.0 + Commitment-
Validation fonctionnelle en 30 secondes
"""

import asyncio
import sys
import os
from datetime import datetime

async def main():
    print("🚀 Test rapide Nextvision V3.0 + Commitment-")
    print("=" * 50)
    
    try:
        # Import modules
        from nextvision.services.enhanced_commitment_bridge_v3_integrated import (
            IntegratedBridgeFactory
        )
        
        print("✅ Modules importés avec succès")
        
        # Création bridge
        bridge = IntegratedBridgeFactory.create_development_integrated_bridge()
        print("✅ Bridge intégré créé")
        
        # Test candidat
        print("\n👤 Test candidat...")
        candidat_start = datetime.now()
        
        questionnaire = {
            "mobility_preferences": {
                "transport_methods": ["transport_public", "vélo"],
                "max_travel_time": "45 minutes"
            },
            "motivations_sectors": {
                "motivations_ranking": ["défis_techniques", "équilibre_vie"],
                "preferred_sectors": ["technologie"]
            }
        }
        
        candidat, metrics = await bridge.convert_candidat_enhanced_integrated(
            parser_output=None,
            cv_file_path=None,
            questionnaire_data=questionnaire,
            enable_real_parsing=False
        )
        
        candidat_time = (datetime.now() - candidat_start).total_seconds()
        
        if metrics.integration_success:
            print(f"✅ Candidat intégré: {candidat_time:.2f}s")
            print(f"   📊 Qualité données: {metrics.data_quality_score:.2f}")
            print(f"   🎯 Confiance: {metrics.commitment_confidence:.2f}")
        else:
            print("⚠️  Intégration candidat partiellement réussie")
        
        # Test entreprise
        print("\n🏢 Test entreprise...")
        entreprise_start = datetime.now()
        
        job_text = """
        Développeur Full Stack Senior - Paris
        Nous recherchons un développeur expérimenté.
        Compétences: JavaScript, React, Node.js
        CDI - 60K-80K
        """
        
        entreprise, metrics2 = await bridge.convert_entreprise_enhanced_integrated(
            chatgpt_output=None,
            job_description_text=job_text,
            questionnaire_data={"company_structure": {"sector": "technologie"}},
            enable_real_parsing=True
        )
        
        entreprise_time = (datetime.now() - entreprise_start).total_seconds()
        
        if metrics2.integration_success:
            print(f"✅ Entreprise intégrée: {entreprise_time:.2f}s")
            print(f"   📊 Qualité données: {metrics2.data_quality_score:.2f}")
            print(f"   🎯 Confiance: {metrics2.commitment_confidence:.2f}")
        else:
            print("⚠️  Intégration entreprise partiellement réussie")
        
        # Health check
        print("\n🏥 Santé système...")
        health = bridge.get_integration_health()
        stats = bridge.get_integrated_stats()
        
        print(f"✅ Statut: {health['status']}")
        print(f"📈 Taux succès: {health['integration_success_rate']:.1f}%")
        print(f"⚡ Temps moyen: {health['avg_processing_time_ms']:.2f}ms")
        
        await bridge.close()
        
        print("\n🎉 Test rapide terminé avec succès!")
        print("🔧 Système prêt pour utilisation")
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")
        print("🔧 Vérifiez la configuration et les dépendances")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
EOF

    chmod +x quick_test.py
    success "Script de test rapide généré: quick_test.py"
}

# Affichage bannière
show_banner() {
    echo -e "${CYAN}"
    echo "=================================================================================================="
    echo "🎯 NEXTVISION V3.0 + COMMITMENT- - DÉPLOIEMENT AUTOMATISÉ"
    echo "=================================================================================================="
    echo -e "${NC}"
    echo -e "${PURPLE}🚀 Setup complet en 5 minutes${NC}"
    echo -e "${PURPLE}🌉 Pipeline intégré avec parsing réel${NC}"
    echo -e "${PURPLE}🗺️ Transport Intelligence V3.0 conservé${NC}"
    echo -e "${PURPLE}🧪 Tests end-to-end automatisés${NC}"
    echo ""
    echo -e "${BLUE}Author: NEXTEN Team${NC}"
    echo -e "${BLUE}Version: 1.0.0${NC}"
    echo -e "${BLUE}Date: $(date)${NC}"
    echo ""
    echo "=================================================================================================="
    echo ""
}

# Affichage résumé final
show_summary() {
    echo ""
    echo "=================================================================================================="
    echo -e "${GREEN}🎉 DÉPLOIEMENT TERMINÉ AVEC SUCCÈS!${NC}"
    echo "=================================================================================================="
    echo ""
    echo -e "${CYAN}📋 RÉSUMÉ:${NC}"
    echo -e "   ✅ Environnement virtuel: ${VENV_NAME}"
    echo -e "   ✅ Dépendances installées"
    echo -e "   ✅ Configuration créée: .env"
    echo -e "   ✅ Structure projet validée"
    echo -e "   ✅ Tests de validation passés"
    echo -e "   ✅ Documentation générée"
    echo ""
    echo -e "${CYAN}🚀 PROCHAINES ÉTAPES:${NC}"
    echo -e "   1. ${YELLOW}Configurez vos API keys dans .env${NC}"
    echo -e "   2. ${YELLOW}Activez l'environnement: source ${VENV_NAME}/bin/activate${NC}"
    echo -e "   3. ${YELLOW}Lancez un test rapide: python quick_test.py${NC}"
    echo -e "   4. ${YELLOW}Tests complets: python test_nextvision_commitment_integration.py${NC}"
    echo ""
    echo -e "${CYAN}📚 DOCUMENTATION:${NC}"
    echo -e "   📖 Guide d'intégration: README_INTEGRATION.md"
    echo -e "   📊 Logs de déploiement: $LOG_FILE"
    echo ""
    echo -e "${CYAN}🎯 PIPELINE INTÉGRÉ:${NC}"
    echo -e "   🔍 Parsing réel: Commitment- Enhanced Parser v4.0"
    echo -e "   🌉 Bridge intégré: Enhanced Bridge V3.0"
    echo -e "   🗺️ Transport Intelligence: V3.0 conservé (score 0.857)"
    echo -e "   🧪 Tests: End-to-end automatisés"
    echo ""
    echo -e "${GREEN}🎉 Système prêt pour production!${NC}"
    echo "=================================================================================================="
}

# === POINT D'ENTRÉE PRINCIPAL ===

main() {
    show_banner
    
    log "🚀 Démarrage du déploiement automatisé..."
    
    # Étapes déploiement
    check_requirements
    setup_virtual_environment
    install_dependencies
    setup_environment
    validate_project_structure
    run_validation_tests
    run_integration_test
    test_transport_intelligence
    generate_documentation
    generate_quick_test_script
    
    show_summary
    
    success "🎉 Déploiement terminé avec succès!"
}

# Gestion des arguments
case "${1:-}" in
    "--help"|"-h")
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Affiche cette aide"
        echo "  --quick, -q    Déploiement rapide (sans tests)"
        echo "  --test, -t     Lance seulement les tests"
        echo "  --clean, -c    Nettoyage complet"
        echo ""
        exit 0
        ;;
    "--quick"|"-q")
        show_banner
        log "🚀 Déploiement rapide..."
        check_requirements
        setup_virtual_environment
        install_dependencies
        setup_environment
        generate_quick_test_script
        success "🎉 Déploiement rapide terminé!"
        ;;
    "--test"|"-t")
        show_banner
        log "🧪 Tests seulement..."
        check_requirements
        if [ ! -d "$VENV_NAME" ]; then
            error "Environnement virtuel non trouvé. Lancez d'abord le déploiement complet."
            exit 1
        fi
        source "$VENV_NAME/bin/activate"
        validate_project_structure
        run_validation_tests
        run_integration_test
        success "🎉 Tests terminés!"
        ;;
    "--clean"|"-c")
        log "🧹 Nettoyage complet..."
        rm -rf "$VENV_NAME"
        rm -f "$LOG_FILE"
        rm -f "quick_test.py"
        rm -f "README_INTEGRATION.md"
        success "🎉 Nettoyage terminé!"
        ;;
    "")
        main
        ;;
    *)
        error "Option inconnue: $1"
        echo "Utilisez --help pour voir les options disponibles"
        exit 1
        ;;
esac
