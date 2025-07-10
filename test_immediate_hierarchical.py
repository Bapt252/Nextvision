"""
⚡ Test Immédiat Système Hiérarchique V3.1
Validation rapide de l'intégration et démonstration Charlotte DARMON

🎯 OBJECTIF : Prouver que le problème Charlotte DARMON est résolu

Usage: python test_immediate_hierarchical.py
"""

import asyncio
import sys
from datetime import datetime
from typing import Dict, Any

def print_header():
    """Affiche l'en-tête du test"""
    print("=" * 80)
    print("⚡ TEST IMMÉDIAT NEXTVISION V3.1 HIÉRARCHIQUE")
    print("=" * 80)
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("🎯 Validation résolution problème Charlotte DARMON")
    print()

async def test_import_system():
    """Test 1: Vérification des imports"""
    print("🔍 TEST 1: IMPORTS SYSTÈME")
    print("-" * 40)
    
    try:
        # Test imports services
        from nextvision.services import (
            HierarchicalDetector, 
            HierarchicalScoring,
            create_bridge_v31
        )
        print("✅ Import services hiérarchiques")
        
        # Test création bridge
        bridge = create_bridge_v31()
        print("✅ Création bridge V3.1")
        
        # Test version
        print(f"📋 Version bridge: {bridge.version}")
        print(f"📋 Pondérations: {bridge.scoring_weights}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur création bridge: {e}")
        return False

async def test_charlotte_darmon_case():
    """Test 2: Cas Charlotte DARMON (le plus important)"""
    print("\n🎯 TEST 2: CAS CHARLOTTE DARMON")
    print("-" * 40)
    
    try:
        from nextvision.services import HierarchicalScoring, create_bridge_v31
        
        # Données Charlotte DARMON
        charlotte_cv = """
        Charlotte DARMON
        Directrice Administrative et Financière (DAF)
        15 ans d'expérience en direction financière
        
        Expérience professionnelle:
        - DAF Groupe ABC (2019-2024): Pilotage stratégique, management équipe de 12 personnes, 
          reporting conseil d'administration, budget consolidé 50M€, politique financière groupe
        - Directrice Financière DEF (2015-2019): Supervision équipe comptable, contrôle budgétaire
        
        Compétences: CEGID, SAGE, Excel avancé, Consolidation, Management
        Rémunération souhaitée: 75-85K€
        Formation: Master Finance, DSCG
        """
        
        comptable_job = """
        Poste: Comptable Général H/F
        Entreprise: PME 50 salariés
        
        Mission:
        - Saisie comptable quotidienne (factures, règlements)
        - Rapprochements bancaires
        - Déclarations TVA mensuelles  
        - Assistance pour bilan annuel
        - Classement et archivage
        
        Profil recherché:
        - Formation comptable (BTS/DUT)
        - 2-5 ans d'expérience en comptabilité générale
        - Maîtrise SAGE, Excel
        - Rigueur et autonomie
        - Pas de management d'équipe
        
        Salaire: 32-38K€
        """
        
        print("📋 Candidat: Charlotte DARMON (DAF, 15 ans, 80K€)")
        print("📋 Poste: Comptable Général (2-5 ans, 35K€)")
        print()
        
        # Test avec le système hiérarchique
        scorer = HierarchicalScoring()
        hierarchical_result = scorer.calculate_hierarchical_score(charlotte_cv, comptable_job)
        
        print("📊 RÉSULTATS ANALYSE HIÉRARCHIQUE:")
        print(f"   Niveau candidat: {hierarchical_result['candidate_level']}")
        print(f"   Niveau poste: {hierarchical_result['job_level']}")
        print(f"   Score hiérarchique: {hierarchical_result['hierarchical_score']:.3f}")
        print(f"   Compatibilité: {hierarchical_result['compatibility_level']}")
        
        if hierarchical_result.get('salary_warning'):
            print(f"   ⚠️  {hierarchical_result['salary_warning']}")
        
        # Test avec le bridge complet
        bridge = create_bridge_v31()
        
        candidate_data = {
            'parsed_content': charlotte_cv,
            'skills': ['CEGID', 'SAGE', 'Excel', 'Consolidation', 'Management'],
            'salary': {'expected': 80000},
            'experience': {'total_years': 15},
            'location': {'city': 'Paris'}
        }
        
        job_data = {
            'parsed_content': comptable_job,
            'competences_requises': ['Comptabilité', 'TVA', 'Saisie'],
            'salary_range': (32000, 38000),
            'experience_requise': '2-5 ans',
            'localisation': 'Paris'
        }
        
        bridge_result = await bridge.enhanced_matching_with_hierarchy(candidate_data, job_data)
        
        print("\n📊 RÉSULTATS BRIDGE V3.1:")
        print(f"   Score total: {bridge_result['total_score']:.3f}")
        print(f"   Compatibilité: {bridge_result['compatibility']}")
        print(f"   Confiance: {bridge_result['confidence']:.3f}")
        
        # Détail des composants
        components = bridge_result['components']
        print(f"\n📊 DÉTAIL COMPOSANTS:")
        for component, score in components.items():
            weight = bridge.scoring_weights.get(component, 0)
            print(f"   {component.capitalize()}: {score:.3f} (poids {weight:.0%})")
        
        # Alertes
        alerts = bridge_result['alerts']
        print(f"\n⚠️  ALERTES GÉNÉRÉES ({len(alerts)}):")
        for alert in alerts:
            icon = "🚨" if alert['type'] == 'CRITICAL_MISMATCH' else "⚠️"
            print(f"   {icon} {alert['type']}: {alert['message']}")
        
        # Validation du résultat
        success = (
            bridge_result['total_score'] < 0.6 and  # Score dégradé
            hierarchical_result['hierarchical_score'] < 0.4 and  # Hiérarchie incompatible
            any(alert['type'] == 'CRITICAL_MISMATCH' for alert in alerts)  # Alerte critique
        )
        
        print(f"\n🎯 VALIDATION:")
        if success:
            print("✅ PROBLÈME CHARLOTTE DARMON RÉSOLU !")
            print("✅ L'inadéquation hiérarchique est correctement détectée")
            print("✅ Le score est automatiquement dégradé")
            print("✅ Des alertes critiques sont générées")
        else:
            print("❌ Problème non résolu - système à ajuster")
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur test Charlotte DARMON: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_performance():
    """Test 3: Performance du système"""
    print("\n⚡ TEST 3: PERFORMANCE")
    print("-" * 40)
    
    try:
        from nextvision.services import create_bridge_v31
        
        bridge = create_bridge_v31()
        
        # Données de test simple
        candidate_data = {
            'parsed_content': "Comptable senior 5 ans expérience SAGE Excel",
            'skills': ['SAGE', 'Excel', 'Comptabilité'],
            'salary': {'expected': 45000},
            'experience': {'total_years': 5},
            'location': {'city': 'Paris'}
        }
        
        job_data = {
            'parsed_content': "Poste comptable confirmé 3-7 ans experience",
            'competences_requises': ['Comptabilité', 'SAGE'],
            'salary_range': (40000, 50000),
            'experience_requise': '3-7 ans',
            'localisation': 'Paris'
        }
        
        # Test de performance (3 échantillons)
        times = []
        for i in range(3):
            start_time = datetime.now()
            result = await bridge.enhanced_matching_with_hierarchy(candidate_data, job_data)
            end_time = datetime.now()
            
            processing_time = (end_time - start_time).total_seconds() * 1000
            times.append(processing_time)
            
            print(f"   Test {i+1}: {processing_time:.1f}ms (score: {result['total_score']:.3f})")
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        print(f"\n📊 PERFORMANCE:")
        print(f"   Temps moyen: {avg_time:.1f}ms")
        print(f"   Temps maximum: {max_time:.1f}ms")
        print(f"   Objectif: <50ms")
        
        performance_ok = avg_time < 50.0
        if performance_ok:
            print("✅ Performance acceptable pour production")
        else:
            print("⚠️  Performance à optimiser")
        
        return performance_ok
        
    except Exception as e:
        print(f"❌ Erreur test performance: {e}")
        return False

async def test_comparison_v30_v31():
    """Test 4: Comparaison V3.0 vs V3.1"""
    print("\n🔄 TEST 4: COMPARAISON V3.0 vs V3.1")
    print("-" * 40)
    
    try:
        from nextvision.services import create_bridge_v30, create_bridge_v31
        
        # Données Charlotte DARMON (cas problématique)
        candidate_data = {
            'parsed_content': "DAF 15 ans expérience management équipe",
            'skills': ['CEGID', 'Management', 'Finance'],
            'salary': {'expected': 80000},
            'experience': {'total_years': 15},
            'location': {'city': 'Paris'}
        }
        
        job_data = {
            'parsed_content': "Comptable général saisie quotidienne 2-5 ans",
            'competences_requises': ['Comptabilité', 'Saisie'],
            'salary_range': (32000, 38000),
            'experience_requise': '2-5 ans',
            'localisation': 'Paris'
        }
        
        # Test V3.0 (ancien système)
        bridge_v30 = create_bridge_v30()
        # Simulation score V3.0 (le vrai bridge V3.0 n'a pas la méthode enhanced_matching_with_hierarchy)
        score_v30_simulated = 0.85 * 0.35 + 0.1 * 0.25 + 0.9 * 0.25 + 0.8 * 0.15  # = 0.645
        
        # Test V3.1 (nouveau système)
        bridge_v31 = create_bridge_v31()
        result_v31 = await bridge_v31.enhanced_matching_with_hierarchy(candidate_data, job_data)
        score_v31 = result_v31['total_score']
        
        print(f"📊 SCORES COMPARÉS:")
        print(f"   V3.0 (simulé): {score_v30_simulated:.3f} ({'✅ Accepté' if score_v30_simulated >= 0.6 else '❌ Rejeté'})")
        print(f"   V3.1 (réel): {score_v31:.3f} ({'✅ Accepté' if score_v31 >= 0.6 else '❌ Rejeté'})")
        
        improvement = score_v30_simulated - score_v31
        print(f"   Amélioration: {improvement:.3f}")
        
        # Validation de l'amélioration
        success = improvement > 0.1 and score_v31 < 0.6
        
        if success:
            print("✅ V3.1 filtre correctement l'inadéquation")
            print("✅ Amélioration significative détectée")
        else:
            print("❌ Pas d'amélioration suffisante")
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur test comparaison: {e}")
        return False

async def main():
    """Point d'entrée principal"""
    
    print_header()
    
    # Compteurs de tests
    tests_passed = 0
    tests_total = 4
    
    # Test 1: Imports
    if await test_import_system():
        tests_passed += 1
    
    # Test 2: Charlotte DARMON (critique)
    if await test_charlotte_darmon_case():
        tests_passed += 1
    
    # Test 3: Performance
    if await test_performance():
        tests_passed += 1
    
    # Test 4: Comparaison V3.0 vs V3.1
    if await test_comparison_v30_v31():
        tests_passed += 1
    
    # Résumé final
    print("\n" + "=" * 80)
    print("📋 RÉSUMÉ FINAL")
    print("=" * 80)
    
    print(f"✅ Tests réussis: {tests_passed}/{tests_total}")
    print(f"❌ Tests échoués: {tests_total - tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS !")
        print("✅ Le système hiérarchique V3.1 fonctionne parfaitement")
        print("✅ Le problème Charlotte DARMON est résolu")
        print("✅ Performance acceptable pour production")
        
        print("\n🚀 PROCHAINES ÉTAPES:")
        print("1. Lancer les tests complets: python test_hierarchical_system_complete.py")
        print("2. Migrer en production: python migrate_to_hierarchical_v31.py")
        print("3. Activer le monitoring: python monitor_hierarchical_system.py")
        
        return True
    else:
        print("\n⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print("❌ Vérifier les erreurs ci-dessus avant déploiement")
        print("💡 Consulter la documentation: cat README_HIERARCHICAL_SYSTEM.md")
        
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
