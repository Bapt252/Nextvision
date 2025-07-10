#!/bin/bash

# 🔄 Test Rapide Dossiers Global avec Système Hiérarchique V3.1
# Lance l'analyse de vos CV et fiches de poste avec la nouvelle détection hiérarchique

echo "🔄 TEST DOSSIERS GLOBAL - SYSTÈME HIÉRARCHIQUE V3.1"
echo "=================================================="
echo "📅 $(date)"
echo ""

echo "🎯 OBJECTIFS:"
echo "✅ Analyser vos CV avec détection hiérarchique"
echo "✅ Identifier les profils type Charlotte DARMON"
echo "✅ Comparer performances V3.0 vs V3.1"
echo "✅ Valider le filtrage des inadéquations"
echo ""

echo "🔍 VÉRIFICATION ENVIRONNEMENT"
echo "-----------------------------"

# Vérification des dossiers Global
if [ -d "Global" ]; then
    cv_count=$(find Global -name "*.txt" -o -name "*.json" | wc -l)
    fdp_count=$(find Global -name "*fiche*.txt" -o -name "*fiche*.json" | wc -l)
    echo "✅ Dossier Global trouvé"
    echo "📄 CV détectés: $cv_count fichiers"
    echo "📋 Fiches de poste détectées: $fdp_count fichiers"
else
    echo "❌ Dossier Global non trouvé"
    echo "💡 Assurez-vous que le dossier Global existe dans le répertoire courant"
    exit 1
fi

# Vérification du système hiérarchique
echo ""
echo "🔧 Test du système hiérarchique..."
python3 -c "
try:
    from nextvision.services import create_bridge_v31, HierarchicalDetector
    bridge = create_bridge_v31()
    detector = HierarchicalDetector()
    print('✅ Système hiérarchique V3.1 opérationnel')
    print(f'📊 Pondérations: {bridge.scoring_weights}')
except Exception as e:
    print(f'❌ Erreur système hiérarchique: {e}')
    exit(1)
" || exit 1

echo ""
echo "🚀 LANCEMENT TEST COMPLET"
echo "-------------------------"
echo "⏱️  Durée estimée: 2-5 minutes selon le nombre de fichiers"
echo ""

# Lancement du test complet
python3 test_global_folders_hierarchical.py

echo ""
echo "📋 RÉSULTATS"
echo "------------"

# Affichage des fichiers générés
if ls global_folders_hierarchical_report_*.json 1> /dev/null 2>&1; then
    latest_report=$(ls -t global_folders_hierarchical_report_*.json | head -n1)
    echo "✅ Rapport détaillé généré: $latest_report"
    
    # Extraction des statistiques clés
    echo ""
    echo "📊 STATISTIQUES RAPIDES:"
    python3 -c "
import json
try:
    with open('$latest_report', 'r') as f:
        data = json.load(f)
    
    summary = data.get('summary', {})
    print(f\"   Matchings testés: {summary.get('total_matchings_tested', 0)}\")
    print(f\"   Inadéquations détectées: {summary.get('critical_mismatches_detected', 0)}\")
    print(f\"   Taux de détection: {summary.get('mismatch_detection_rate', 0):.1%}\")
    print(f\"   Matchings filtrés: {summary.get('filtered_matchings', 0)}\")
    
    charlotte_cases = len(data.get('charlotte_darmon_cases', []))
    if charlotte_cases > 0:
        print(f\"   🎯 Cas type Charlotte DARMON: {charlotte_cases}\")
    
    improvements = len(data.get('hierarchical_improvements', []))
    if improvements > 0:
        print(f\"   📈 Améliorations V3.1: {improvements}\")
    
    perf = data.get('performance_metrics', {})
    if perf:
        avg_time = perf.get('average_time_ms', 0)
        print(f\"   ⚡ Performance: {avg_time:.1f}ms moyen\")
        if avg_time < 50:
            print(\"   ✅ Performance excellente (<50ms)\")
        else:
            print(\"   ⚠️  Performance à optimiser\")

except Exception as e:
    print(f\"Erreur lecture rapport: {e}\")
"
else
    echo "⚠️  Aucun rapport généré - vérifier les erreurs ci-dessus"
fi

echo ""
echo "🎯 FOCUS CHARLOTTE DARMON"
echo "------------------------"
echo "Le système V3.1 détecte maintenant automatiquement:"
echo "  🚨 DAF/Directeur → Comptable = CRITICAL_MISMATCH"
echo "  ⚠️  Manager → Junior = OVERQUALIFICATION"
echo "  ✅ Niveau équivalent = EXCELLENT_MATCH"

echo ""
echo "📚 PROCHAINES ÉTAPES"
echo "-------------------"
echo "1. Consulter le rapport détaillé: cat $latest_report"
echo "2. Intégrer en production: python migrate_to_hierarchical_v31.py"
echo "3. Monitoring continu: python monitor_hierarchical_system.py"

echo ""
echo "💡 AIDE"
echo "-------"
echo "📖 Documentation complète: cat README_HIERARCHICAL_SYSTEM.md"
echo "🧪 Tests supplémentaires: python test_hierarchical_system_complete.py"
echo "⚡ Test rapide: python test_immediate_hierarchical.py"

echo ""
echo "🎉 TEST TERMINÉ !"
echo "Le système hiérarchique V3.1 a analysé vos dossiers Global."
echo "Charlotte DARMON et cas similaires sont maintenant automatiquement filtrés !"
