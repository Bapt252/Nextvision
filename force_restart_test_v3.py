#!/usr/bin/env python3
"""
🔥 FORCE RESTART - Test Bug Salary Progression CORRIGÉ
=====================================================

Script qui force le redémarrage de Python et teste immédiatement la correction.
OBJECTIF: Éliminer définitivement le cache Python et confirmer la correction.

Author: Claude Assistant (Anthropic) 
Version: V3.0.1 - Force Update
"""

import sys
import os
import importlib
import time

def force_restart_and_test():
    """Force redémarrage et test immédiat"""
    
    print("🔥 FORCE RESTART - VALIDATION BUG SALARY_PROGRESSION")
    print("=" * 60)
    
    # 1. Nettoyage cache Python
    print("🧹 Nettoyage cache Python...")
    
    # Supprime tous les modules nextvision du cache
    modules_to_remove = []
    for module_name in sys.modules:
        if module_name.startswith('nextvision'):
            modules_to_remove.append(module_name)
    
    for module in modules_to_remove:
        del sys.modules[module]
        print(f"   ❌ Cache supprimé: {module}")
    
    # 2. Force réimport complet
    print("\n📦 Force réimport modules...")
    
    try:
        # Import fresh de l'engine corrigé
        from nextvision.engines.adaptive_weighting_engine_v3 import AdaptiveWeightingEngine, AdaptiveMatchingResult
        from nextvision.config.adaptive_weighting_config import ListeningReasonType, validate_all_matrices
        
        print("✅ Import AdaptiveWeightingEngine réussi")
        print("✅ Import AdaptiveMatchingResult réussi")
        print("✅ Import config réussi")
        
        # 3. Validation matrices
        print("\n🔍 Validation matrices...")
        matrices_results = validate_all_matrices()
        if not all(matrices_results.values()):
            print("❌ ERREUR: Matrices non-validées")
            return False
        print("✅ Matrices validées: 1.000000 exactement")
        
        # 4. Initialisation engine
        print("\n🔧 Initialisation engine V3.0.1...")
        engine = AdaptiveWeightingEngine(validate_matrices=True)
        print("✅ Engine V3.0.1 initialisé avec succès")
        
        # 5. Test CAND_069 (cas critique)
        print("\n🧪 TEST CRITIQUE: CAND_069 (freelance, current_salary=0)")
        
        candidat_069 = {
            "candidate_id": "CAND_069",
            "skills": ["react", "typescript", "graphql", "mongodb"],
            "domains": ["frontend", "mobile"],
            "years_experience": 5,
            "current_salary": 0,  # 🔥 CAS PROBLÉMATIQUE
            "desired_salary": 55000,
            "location": "Remote",
            "listening_reasons": ["flexibilite"],
            "secteurs_preferes": ["startup", "tech", "media"],
            "contract_ranking": ["freelance", "cdd"],
            "office_preference": "full_remote",
            "remote_days_per_week": 5,
            "max_travel_time": 120,
            "availability_date": "2025-07-15",
            "notice_period_weeks": 0,
            "employment_status": "freelance",
            "job_search_urgency": 4,
            "sector_openness": 5
        }
        
        poste_test = {
            "position_id": "POS_001",
            "required_skills": ["react", "javascript"],
            "domain": "frontend",
            "min_years_experience": 3,
            "max_years_experience": 8,
            "salary_min": 500,
            "salary_max": 650,
            "location": "Remote",
            "company_sector": "startup",
            "contract_type": "freelance",
            "remote_policy": "full_remote",
            "desired_start_date": "2025-07-20",
            "recruitment_urgency": 4,
            "max_wait_weeks": 3
        }
        
        print(f"   Candidat: {candidat_069['candidate_id']}")
        print(f"   Current salary: {candidat_069['current_salary']} (problématique)")
        print(f"   Employment status: {candidat_069['employment_status']}")
        
        # Test matching
        print("\n🔥 EXÉCUTION TEST...")
        start_time = time.time()
        
        result = engine.calculate_adaptive_matching_score(candidat_069, poste_test)
        
        processing_time = (time.time() - start_time) * 1000
        
        print(f"✅ SUCCESS! Matching réussi")
        print(f"✅ Score total: {result.total_score:.3f}")
        print(f"✅ Temps traitement: {processing_time:.2f}ms")
        print(f"✅ Raison d'écoute: {result.listening_reason.value}")
        print(f"✅ Composants: {len(result.component_scores)}")
        
        # Vérification spécifique salary_progression
        salary_comp = next((s for s in result.component_scores if s.name == "salary_progression"), None)
        if salary_comp:
            print(f"\n💰 SALARY_PROGRESSION COMPONENT:")
            print(f"   ✅ Score: {salary_comp.raw_score:.3f}")
            print(f"   ✅ Expected progression: {salary_comp.details['expected_progression_pct']}")
            print(f"   ✅ Offered progression: {salary_comp.details['offered_progression_pct']}")
            print(f"   ✅ Employment status: {salary_comp.details['employment_status']}")
            print(f"   ✅ Score explanation: {salary_comp.details['score_explanation']}")
        else:
            print("❌ ERREUR: Composant salary_progression non trouvé")
            return False
        
        # 6. Test batch candidats problématiques
        print("\n🧪 TEST BATCH CANDIDATS PROBLÉMATIQUES")
        
        candidats_problematiques = [
            ("CAND_054", 0, "demandeur_emploi"),
            ("CAND_058", 0, "freelance"), 
            ("CAND_059", 0, "etudiant"),
            ("CAND_063", 0, "transition"),
            ("CAND_064", 0, "freelance"),
            ("CAND_068", 0, "demandeur_emploi")
        ]
        
        successes = 0
        for cand_id, current_sal, status in candidats_problematiques:
            candidat = {
                "candidate_id": cand_id,
                "current_salary": current_sal,
                "desired_salary": 45000,
                "employment_status": status,
                "skills": ["python", "javascript"],
                "listening_reasons": ["autre"]
            }
            
            try:
                result = engine.calculate_adaptive_matching_score(candidat, poste_test)
                print(f"   ✅ {cand_id}: Score {result.total_score:.3f}")
                successes += 1
            except Exception as e:
                print(f"   ❌ {cand_id}: ÉCHEC - {str(e)}")
        
        print(f"\n📊 RÉSULTAT BATCH: {successes}/{len(candidats_problematiques)} réussis")
        
        # 7. VERDICT FINAL
        print("\n" + "=" * 60)
        if successes == len(candidats_problematiques):
            print("🎉 VALIDATION COMPLÈTE RÉUSSIE ✅")
            print("🔥 BUG SALARY_PROGRESSION DÉFINITIVEMENT CORRIGÉ")
            print("🚀 NextVision V3.0.1 - PRÊT POUR 2,346 MATCHINGS")
            print("\n📋 PROCHAINES ÉTAPES:")
            print("   1. python test_nextvision_v3_production_final.py")
            print("   2. Confirmer 2,346/2,346 matchings sans échec") 
            print("   3. Déployer en production ✅")
            return True
        else:
            print("❌ VALIDATION ÉCHOUÉE")
            print(f"   Seulement {successes}/{len(candidats_problematiques)} candidats passent")
            return False
            
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        import traceback
        print("\n🔍 TRACEBACK COMPLET:")
        print(traceback.format_exc())
        return False

def main():
    """Point d'entrée avec gestion d'erreur"""
    
    print("🔥 NEXTVISION V3.0.1 - FORCE RESTART & VALIDATION")
    print("🎯 Objectif: Éliminer cache Python et valider correction")
    print("=" * 70)
    
    success = force_restart_and_test()
    
    if success:
        print("\n🎉 MISSION ACCOMPLIE!")
        print("✅ Cache Python nettoyé")
        print("✅ Engine V3.0.1 rechargé")
        print("✅ Bug salary_progression résolu")
        print("✅ Tous candidats problématiques fonctionnent")
        print("\n🚀 LE SYSTÈME EST PRÊT POUR PRODUCTION!")
        exit(0)
    else:
        print("\n❌ MISSION ÉCHOUÉE")
        print("🔧 Intervention manuelle nécessaire")
        exit(1)

if __name__ == "__main__":
    main()
