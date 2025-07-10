#!/bin/bash

# 🚀 Nextvision V3.1 Hiérarchique - Guide de Démarrage Rapide
# Script de test et validation du système de détection hiérarchique

echo "🎯 NEXTVISION V3.1 - SYSTÈME HIÉRARCHIQUE"
echo "========================================"
echo "📅 $(date)"
echo ""

echo "🔍 1. VÉRIFICATION DE L'ENVIRONNEMENT"
echo "------------------------------------"

# Vérification Python
if command -v python3 &> /dev/null; then
    echo "✅ Python3 disponible: $(python3 --version)"
else
    echo "❌ Python3 non trouvé"
    exit 1
fi

# Vérification des fichiers essentiels
files=(
    "nextvision/services/hierarchical_detector.py"
    "nextvision/services/enhanced_commitment_bridge_v3_hierarchical.py"
    "test_hierarchical_system_complete.py"
    "migrate_to_hierarchical_v31.py"
    "README_HIERARCHICAL_SYSTEM.md"
)

echo ""
echo "📁 Vérification des fichiers:"
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file manquant"
        exit 1
    fi
done

echo ""
echo "🧪 2. TESTS SYSTÈME HIÉRARCHIQUE"
echo "--------------------------------"

# Test rapide des imports
echo "🔍 Test des imports..."
python3 -c "
try:
    from nextvision.services.hierarchical_detector import HierarchicalDetector, HierarchicalScoring
    from nextvision.services.enhanced_commitment_bridge_v3_hierarchical import HierarchicalBridgeFactory
    print('✅ Tous les imports fonctionnent')
except ImportError as e:
    print(f'❌ Erreur import: {e}')
    exit(1)
" || exit 1

echo ""
echo "🎯 Test du cas Charlotte DARMON..."
python3 -c "
import asyncio
from nextvision.services.hierarchical_detector import HierarchicalScoring

async def test_charlotte():
    scorer = HierarchicalScoring()
    
    charlotte_cv = '''
    Charlotte DARMON - Directrice Administrative et Financière (DAF)
    15 ans d'expérience en direction financière
    DAF Groupe ABC: Pilotage stratégique, management équipe de 12 personnes
    '''
    
    comptable_job = '''
    Poste: Comptable Général H/F
    Saisie comptable quotidienne, rapprochements bancaires
    2-5 ans d'expérience, pas de management d'équipe
    Salaire: 32-38K€
    '''
    
    result = scorer.calculate_hierarchical_score(charlotte_cv, comptable_job)
    score = result['hierarchical_score']
    compatibility = result['compatibility_level']
    
    print(f'📊 Score hiérarchique: {score:.3f}')
    print(f'📊 Compatibilité: {compatibility}')
    
    if score < 0.4:
        print('✅ Inadéquation correctement détectée (score faible)')
    else:
        print('❌ Inadéquation non détectée (score trop élevé)')
        return False
    
    if 'incompatible' in compatibility.lower():
        print('✅ Compatibilité correctement évaluée')
    else:
        print('⚠️  Compatibilité à vérifier')
    
    return True

if not asyncio.run(test_charlotte()):
    exit(1)
" || exit 1

echo ""
echo "🚀 3. MIGRATION (OPTIONNELLE)"
echo "-----------------------------"
echo "Pour migrer automatiquement vers V3.1:"
echo "   python3 migrate_to_hierarchical_v31.py"
echo ""
echo "Pour tester le système complet:"
echo "   python3 test_hierarchical_system_complete.py"
echo ""

echo "📊 4. RÉSULTATS ATTENDUS"
echo "------------------------"
echo "✅ Charlotte DARMON (DAF) ne sera plus matchée sur postes comptables"
echo "✅ Alertes automatiques pour surqualifications"
echo "✅ Nouveau scoring avec composant hiérarchique (15%)"
echo "✅ Performance maintenue (<50ms par matching)"
echo ""

echo "📚 5. DOCUMENTATION"
echo "-------------------"
echo "📖 README_HIERARCHICAL_SYSTEM.md - Guide complet"
echo "🧪 test_hierarchical_system_complete.py - Tests détaillés"
echo "🔄 migrate_to_hierarchical_v31.py - Migration automatique"
echo ""

echo "🎉 INSTALLATION RÉUSSIE !"
echo "========================"
echo "Le système hiérarchique Nextvision V3.1 est prêt à utiliser."
echo ""
echo "🚀 PROCHAINES ÉTAPES:"
echo "1. Lire: cat README_HIERARCHICAL_SYSTEM.md"
echo "2. Tester: python3 test_hierarchical_system_complete.py"
echo "3. Migrer: python3 migrate_to_hierarchical_v31.py"
echo "4. Monitorer: python3 monitor_hierarchical_system.py"
echo ""
echo "💡 Le problème Charlotte DARMON est maintenant résolu !"
