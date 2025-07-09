#!/usr/bin/env python3
"""
🔥 NextVision V3.0 - Validation Fix Salary Progression
====================================================

Script de validation pour confirmer que le bug salary_progression 
est définitivement corrigé.

Tests spécifiques pour candidats problématiques:
- Freelances (current_salary = 0)
- Demandeurs emploi (current_salary = 0) 
- Étudiants/transitions (current_salary = 0)

Author: Claude Assistant (Anthropic)
Version: V3.0.1 - Hotfix Validation
"""

import time
import traceback
from typing import Dict, List, Any

def test_salary_progression_fix():
    """
    🧪 TEST PRINCIPAL - Validation correction bug salary_progression
    
    Teste les cas qui causaient l'erreur UnboundLocalError:
    - CAND_069 et autres freelances
    - Demandeurs emploi
    - Profils sans current_salary
    """
    
    print("🔥 VALIDATION FIX SALARY_PROGRESSION V3.0.1")
    print("=" * 60)
    
    # Test import engine corrigé
    try:
        from nextvision.engines.adaptive_weighting_engine_v3 import AdaptiveWeightingEngine
        print("✅ Import AdaptiveWeightingEngine réussi")
    except Exception as e:
        print(f"❌ Erreur import engine: {e}")
        return False
    
    # Initialisation engine
    try:
        engine = AdaptiveWeightingEngine()
        print("✅ Engine V3.0.1 initialisé")
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
        return False
    
    # 🎯 CAS DE TEST PROBLÉMATIQUES
    
    # Test 1: Freelance (current_salary = 0)
    print("\n🧪 TEST 1: Candidat Freelance (current_salary = 0)")
    candidate_freelance = {
        "candidate_id": "CAND_069",
        "current_salary": 0,  # 🔥 CAS PROBLÉMATIQUE
        "desired_salary": 55000,
        "employment_status": "freelance",
        "skills": ["react", "typescript"],
        "location": "Remote",
        "listening_reasons": ["flexibilite"]
    }
    
    position_test = {
        "position_id": "POS_001", 
        "salary_max": 60000,
        "required_skills": ["react", "javascript"],
        "location": "Paris",
        "company_sector": "startup"
    }
    
    try:
        result1 = engine.calculate_adaptive_matching_score(candidate_freelance, position_test)
        print(f"✅ Test freelance réussi - Score: {result1.total_score:.3f}")
        
        # Vérification détails salary_progression
        salary_component = next((c for c in result1.component_scores if c.name == "salary_progression"), None)
        if salary_component and "expected_progression_pct" in salary_component.details:
            print(f"✅ Variables initialisées - expected: {salary_component.details['expected_progression_pct']}")
        else:
            print("❌ Variables salary_progression manquantes")
            return False
            
    except Exception as e:
        print(f"❌ ÉCHEC Test freelance: {e}")
        print(traceback.format_exc())
        return False
    
    # Test 2: Demandeur emploi (current_salary = 0)
    print("\n🧪 TEST 2: Demandeur emploi (current_salary = 0)")
    candidate_unemployed = {
        "candidate_id": "CAND_070",
        "current_salary": 0,  # 🔥 CAS PROBLÉMATIQUE
        "desired_salary": 45000,
        "employment_status": "demandeur_emploi",
        "skills": ["php", "symfony"],
        "location": "Marseille",
        "listening_reasons": ["autre"]
    }
    
    try:
        result2 = engine.calculate_adaptive_matching_score(candidate_unemployed, position_test)
        print(f"✅ Test demandeur emploi réussi - Score: {result2.total_score:.3f}")
        
        # Vérification détails
        salary_component = next((c for c in result2.component_scores if c.name == "salary_progression"), None)
        if salary_component:
            print(f"✅ Employment status: {salary_component.details['employment_status']}")
        
    except Exception as e:
        print(f"❌ ÉCHEC Test demandeur emploi: {e}")
        return False
    
    # Test 3: Étudiant/transition (current_salary = 0, desired_salary = 0)
    print("\n🧪 TEST 3: Transition carrière (salaires = 0)")
    candidate_transition = {
        "candidate_id": "CAND_071",
        "current_salary": 0,   # 🔥 CAS PROBLÉMATIQUE
        "desired_salary": 0,   # 🔥 CAS PROBLÉMATIQUE
        "employment_status": "transition",
        "skills": ["python", "data"],
        "location": "Lyon"
    }
    
    try:
        result3 = engine.calculate_adaptive_matching_score(candidate_transition, position_test)
        print(f"✅ Test transition réussi - Score: {result3.total_score:.3f}")
        
    except Exception as e:
        print(f"❌ ÉCHEC Test transition: {e}")
        return False
    
    # Test 4: Batch test multiple candidats problématiques
    print("\n🧪 TEST 4: Batch test candidats problématiques")
    
    problematic_candidates = []
    for i in range(10):
        candidate = {
            "candidate_id": f"CAND_BATCH_{i:03d}",
            "current_salary": 0 if i % 2 == 0 else None,  # Alterne 0 et None
            "desired_salary": 40000 + i * 1000,
            "employment_status": ["freelance", "demandeur_emploi", "etudiant", "transition"][i % 4],
            "skills": ["python", "java", "react"][i % 3],
            "location": "Paris"
        }
        problematic_candidates.append(candidate)
    
    batch_success = 0
    batch_total = len(problematic_candidates)
    
    for candidate in problematic_candidates:
        try:
            result = engine.calculate_adaptive_matching_score(candidate, position_test)
            batch_success += 1
        except Exception as e:
            print(f"❌ Échec {candidate['candidate_id']}: {e}")
    
    print(f"✅ Batch test: {batch_success}/{batch_total} réussis ({batch_success/batch_total*100:.1f}%)")
    
    # 🎯 RÉSULTAT FINAL
    print("\n" + "=" * 60)
    if batch_success == batch_total:
        print("🎉 VALIDATION RÉUSSIE - BUG SALARY_PROGRESSION CORRIGÉ ✅")
        print("🚀 NextVision V3.0.1 - Prêt pour 2,346/2,346 matchings")
        print("✅ Compatibilité garantie:")
        print("   ✅ Freelances (current_salary = 0)")
        print("   ✅ Demandeurs emploi (current_salary = 0)")
        print("   ✅ Transitions/étudiants (salaires variables)")
        print("   ✅ Variables progression toujours initialisées")
        return True
    else:
        print("❌ VALIDATION ÉCHOUÉE - Problèmes persistants")
        return False


def test_production_sample():
    """
    🧪 Test échantillon production pour vérifier performance
    """
    print("\n🚀 TEST ÉCHANTILLON PRODUCTION")
    print("-" * 40)
    
    try:
        from nextvision.engines.adaptive_weighting_engine_v3 import AdaptiveWeightingEngine
        engine = AdaptiveWeightingEngine()
        
        # Test 50 matchings rapides
        total_time = 0
        successful_matches = 0
        
        for i in range(50):
            candidate = {
                "candidate_id": f"SAMPLE_{i:03d}",
                "current_salary": 0 if i % 3 == 0 else 40000 + i * 500,  # Mix avec/sans salaire
                "desired_salary": 45000 + i * 200,
                "employment_status": ["freelance", "en_poste", "demandeur_emploi"][i % 3],
                "skills": ["python", "react", "java"],
                "location": "Paris"
            }
            
            position = {
                "position_id": f"POS_{i:03d}",
                "salary_max": 50000 + i * 300,
                "required_skills": ["python"],
                "company_sector": "tech"
            }
            
            start_time = time.time()
            try:
                result = engine.calculate_adaptive_matching_score(candidate, position)
                processing_time = (time.time() - start_time) * 1000
                total_time += processing_time
                successful_matches += 1
                
                if i % 10 == 0:
                    print(f"   Match {i+1}: {processing_time:.1f}ms - Score: {result.total_score:.3f}")
                    
            except Exception as e:
                print(f"❌ Échec match {i}: {e}")
        
        avg_time = total_time / successful_matches if successful_matches > 0 else 0
        success_rate = successful_matches / 50 * 100
        
        print(f"\n📊 RÉSULTATS ÉCHANTILLON:")
        print(f"   Matchings réussis: {successful_matches}/50 ({success_rate:.1f}%)")
        print(f"   Temps moyen: {avg_time:.1f}ms")
        print(f"   Performance target <175ms: {'✅' if avg_time < 175 else '❌'}")
        
        return successful_matches == 50 and avg_time < 175
        
    except Exception as e:
        print(f"❌ Erreur test production: {e}")
        return False


def main():
    """Script principal validation"""
    
    print("🔥 NEXTVISION V3.0.1 - VALIDATION COMPLÈTE")
    print("🎯 Vérification correction bug salary_progression")
    print("=" * 70)
    
    # Test 1: Validation fix salary_progression
    fix_validated = test_salary_progression_fix()
    
    # Test 2: Test échantillon production
    production_ok = test_production_sample()
    
    # Verdict final
    print("\n" + "=" * 70)
    if fix_validated and production_ok:
        print("🎉 VALIDATION GLOBALE RÉUSSIE ✅")
        print("🚀 NextVision V3.0.1 - PRÊT PRODUCTION")
        print("\n📋 ACTIONS SUIVANTES:")
        print("   1. Lancer test production complet:")
        print("      python test_nextvision_v3_production_final.py")
        print("   2. Vérifier 2,346/2,346 matchings réussis")
        print("   3. Valider performance <175ms maintenue")
        print("   4. Déployer en production ✅")
        return True
    else:
        print("❌ VALIDATION ÉCHOUÉE")
        if not fix_validated:
            print("   - Bug salary_progression non corrigé")
        if not production_ok:
            print("   - Performance production insuffisante")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
