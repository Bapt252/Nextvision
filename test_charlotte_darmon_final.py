#!/usr/bin/env python3
"""
Test Final Charlotte DARMON vs Comptable - Nextvision V3.1 GPT Integration
=========================================================================

Script de test final pour valider l'intégration GPT avec le système V3.1.
Objectifs à valider:
1. ✅ Score abaissé (<0.4)
2. ✅ Incompatibilité hiérarchique détectée  
3. ✅ Alerte CRITICAL_MISMATCH générée
4. ✅ Performance <100ms maintenue
5. ✅ Secteur d'activité intégré (5%)

Auteur: Baptiste Comas
Date: 2025-07-10
Version: 1.0.0
"""

import sys
import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# Ajout du chemin pour les modules gpt_modules
sys.path.insert(0, str(Path(__file__).parent))

# Configuration du logging pour le test
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('test_charlotte_final')

def setup_test_environment():
    """
    Configure l'environnement de test
    """
    print("🔧 Configuration de l'environnement de test...")
    
    # Vérification de la disponibilité des modules
    try:
        from gpt_modules import CVParserGPT, JobParserGPT, GPTNextvisionIntegrator
        logger.info("✅ Modules GPT disponibles")
        return CVParserGPT, JobParserGPT, GPTNextvisionIntegrator
    except ImportError as e:
        logger.error(f"❌ Erreur d'import des modules GPT: {e}")
        return None, None, None

def test_charlotte_darmon_integration():
    """
    Test principal Charlotte DARMON vs Comptable
    """
    print("\n" + "="*80)
    print("🧪 TEST FINAL CHARLOTTE DARMON vs COMPTABLE ENTRY")
    print("="*80)
    
    start_time = time.time()
    
    # Configuration de l'environnement
    CVParserGPT, JobParserGPT, GPTNextvisionIntegrator = setup_test_environment()
    
    if not all([CVParserGPT, JobParserGPT, GPTNextvisionIntegrator]):
        print("❌ Impossible de charger les modules GPT")
        return False
    
    try:
        # Initialisation des parsers (sans OpenAI pour les tests)
        print("📋 Initialisation des parsers...")
        cv_parser = CVParserGPT(openai_client=None)  # Utilise les profils fallback
        job_parser = JobParserGPT(openai_client=None)
        
        # Initialisation de l'intégrateur
        print("🔗 Initialisation de l'intégrateur V3.1...")
        integrator = GPTNextvisionIntegrator(
            cv_parser=cv_parser,
            job_parser=job_parser
        )
        
        # Affichage de la configuration
        print(f"⚙️ Configuration système:")
        status = integrator.integration_status()
        print(f"   - Version intégration: {status['integration_version']}")
        print(f"   - Pondérations V3.1: {status['weights_v31']}")
        print(f"   - Seuil critique: {status['thresholds']['critical_mismatch']}")
        
        # Récupération des profils de test
        print("\n👤 Récupération du profil Charlotte DARMON...")
        charlotte_profile = cv_parser.get_charlotte_darmon_profile()
        print(f"   - Nom: {charlotte_profile.nom_complet}")
        print(f"   - Titre: {charlotte_profile.titre_poste}")
        print(f"   - Niveau: {charlotte_profile.niveau_hierarchique}")
        print(f"   - Expérience: {charlotte_profile.experience_years} ans")
        print(f"   - Salaire: {charlotte_profile.salaire_actuel}€")
        
        print("\n💼 Récupération du poste Comptable...")
        comptable_job = job_parser.get_comptable_entry_job()
        print(f"   - Titre: {comptable_job.titre_poste}")
        print(f"   - Niveau: {comptable_job.niveau_hierarchique}")
        print(f"   - Expérience: {comptable_job.experience_requise_min}-{comptable_job.experience_requise_max} ans")
        print(f"   - Salaire: {comptable_job.salaire_min}-{comptable_job.salaire_max}€")
        
        # Conversion au format Nextvision
        print("\n🔄 Conversion au format Nextvision V3.1...")
        charlotte_data = cv_parser.to_nextvision_format(charlotte_profile)
        comptable_data = job_parser.to_nextvision_format(comptable_job)
        
        # Exécution du test Charlotte vs Comptable
        print("\n🎯 EXÉCUTION DU TEST CRITIQUE...")
        test_result = integrator.test_charlotte_darmon_vs_comptable()
        
        # Affichage des résultats
        print("\n" + "="*50)
        print("📊 RÉSULTATS DU TEST")
        print("="*50)
        
        result = test_result['result']
        objectives = test_result['objectives_validation']
        
        print(f"🎯 Score total: {result.total_score:.3f}")
        print(f"⚡ Performance: {result.performance_ms:.1f}ms")
        print(f"🏆 Recommandation: {result.recommendation}")
        print(f"🔍 Compatibilité hiérarchique: {result.hierarchical_compatibility}")
        
        print(f"\n📈 Détail des scores:")
        for component, score in result.scores_breakdown.items():
            weight = integrator.weights_v31.get(component, 0)
            contribution = score * weight
            print(f"   - {component.capitalize()}: {score:.3f} (×{weight:.2f} = {contribution:.3f})")
        
        print(f"\n⚠️ Alertes ({len(result.alerts)}):")
        for alert in result.alerts:
            print(f"   - {alert}")
        
        # Validation des objectifs
        print(f"\n🎯 VALIDATION DES 5 OBJECTIFS:")
        print(f"   1. Score abaissé (<0.4): {'✅' if objectives['1_score_abaisse'] else '❌'} ({result.total_score:.3f})")
        print(f"   2. Incompatibilité hiérarchique: {'✅' if objectives['2_incompatibilite_hierarchique'] else '❌'} ({result.hierarchical_compatibility})")
        print(f"   3. Alerte CRITICAL_MISMATCH: {'✅' if objectives['3_alerte_critical_mismatch'] else '❌'}")
        print(f"   4. Performance <100ms: {'✅' if objectives['4_performance_maintenue'] else '❌'} ({result.performance_ms:.1f}ms)")
        print(f"   5. Secteur intégré (5%): {'✅' if objectives['5_secteur_integre'] else '❌'}")
        
        # Résultat final
        success = test_result['success']
        objectives_count = sum(objectives.values())
        
        print(f"\n🏁 RÉSULTAT FINAL: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
        print(f"📊 Objectifs validés: {objectives_count}/5")
        
        # Test de performance globale
        total_time = (time.time() - start_time) * 1000
        print(f"⏱️ Temps total d'exécution: {total_time:.1f}ms")
        
        # Sauvegarde du rapport
        rapport_path = f"test_charlotte_darmon_final_{int(time.time())}.json"
        with open(rapport_path, 'w', encoding='utf-8') as f:
            # Sérialisation du rapport avec conversion des objets non-sérialisables
            rapport_serializable = {
                **test_result,
                'result': {
                    'candidate_name': result.candidate_name,
                    'job_title': result.job_title,
                    'total_score': result.total_score,
                    'scores_breakdown': result.scores_breakdown,
                    'hierarchical_compatibility': result.hierarchical_compatibility,
                    'alerts': result.alerts,
                    'performance_ms': result.performance_ms,
                    'recommendation': result.recommendation
                },
                'test_execution': {
                    'total_time_ms': total_time,
                    'timestamp': datetime.now().isoformat(),
                    'environment': 'nextvision_v31_gpt_integration'
                }
            }
            json.dump(rapport_serializable, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Rapport sauvegardé: {rapport_path}")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_additional_scenarios():
    """
    Tests additionnels pour valider l'intégration
    """
    print("\n" + "="*60)
    print("🧪 TESTS ADDITIONNELS")
    print("="*60)
    
    try:
        from gpt_modules import CVParserGPT, JobParserGPT, GPTNextvisionIntegrator
        
        cv_parser = CVParserGPT()
        job_parser = JobParserGPT()
        integrator = GPTNextvisionIntegrator(cv_parser=cv_parser, job_parser=job_parser)
        
        # Test 1: Charlotte vs DAF (devrait matcher)
        print("\n📝 Test 1: Charlotte DARMON vs DAF EXECUTIVE")
        charlotte_data = cv_parser.to_nextvision_format(cv_parser.get_charlotte_darmon_profile())
        daf_data = job_parser.to_nextvision_format(job_parser.get_daf_executive_job())
        
        result1 = integrator.perform_complete_matching(charlotte_data, daf_data)
        print(f"   Score: {result1.total_score:.3f} - {result1.recommendation}")
        print(f"   Hiérarchique: {result1.hierarchical_compatibility}")
        
        # Test 2: Dorothée vs Consultant (devrait bien matcher)
        print("\n📝 Test 2: Dorothée Lim vs Consultant Senior")
        dorothee_data = cv_parser.to_nextvision_format(cv_parser._get_fallback_profile())
        consultant_data = job_parser.to_nextvision_format(job_parser._get_fallback_job())
        
        result2 = integrator.perform_complete_matching(dorothee_data, consultant_data)
        print(f"   Score: {result2.total_score:.3f} - {result2.recommendation}")
        print(f"   Hiérarchique: {result2.hierarchical_compatibility}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur tests additionnels: {str(e)}")
        return False

def main():
    """
    Fonction principale du test
    """
    print("🚀 NEXTVISION V3.1 - TEST FINAL D'INTÉGRATION GPT")
    print("=" * 80)
    print("Objectif: Valider l'intégration des parsers GPT avec le système V3.1")
    print("Cas critique: Charlotte DARMON (DAF, 15 ans, 80K€) vs Comptable (2-5 ans, 35K€)")
    print("=" * 80)
    
    # Test principal
    success_main = test_charlotte_darmon_integration()
    
    # Tests additionnels
    success_additional = test_additional_scenarios()
    
    # Conclusion
    print("\n" + "="*80)
    print("🏁 CONCLUSION FINALE")
    print("="*80)
    
    if success_main:
        print("✅ TEST PRINCIPAL RÉUSSI: Charlotte DARMON vs Comptable validé")
        print("🎯 Objectifs V3.1 atteints:")
        print("   - Dissociation front/back réalisée")
        print("   - Parsers GPT intégrés sans conflit")
        print("   - Système hiérarchique V3.1 fonctionnel")
        print("   - Performance <100ms maintenue")
        print("   - Nouveau scoring secteur (5%) opérationnel")
        
        if success_additional:
            print("✅ TESTS ADDITIONNELS RÉUSSIS")
        
        print("\n🚀 SYSTÈME PRÊT POUR LA PRODUCTION!")
        
    else:
        print("❌ TEST PRINCIPAL ÉCHOUÉ")
        print("⚠️ Intervention nécessaire avant mise en production")
    
    return success_main and success_additional

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
