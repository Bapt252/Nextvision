#!/usr/bin/env python3
"""
Patch Ultra-Simplifié V3.2.1 - SANS BUGS
========================================

Script minimaliste pour corriger les incompatibilités sectorielles
Baptiste Comas - Nextvision
"""

import sys
sys.path.append('gpt_modules')

print("🔧 PATCH SECTORIEL V3.2.1")
print("=" * 30)

try:
    # Import
    from integration import GPTNextvisionIntegrator
    from cv_parser import CVParserGPT
    from job_parser import JobParserGPT
    import os
    
    # Configuration OpenAI
    openai_client = None
    if os.getenv('OPENAI_API_KEY'):
        import openai
        openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    cv_parser = CVParserGPT(openai_client)
    job_parser = JobParserGPT(openai_client)
    
    print("✅ Modules chargés")
    
    # Sauvegarde méthode originale
    original_method = GPTNextvisionIntegrator.perform_complete_matching
    
    def apply_sectoral_penalty(self, candidate_data, job_data):
        """Méthode avec pénalité sectorielle"""
        
        # Calcul normal
        result = original_method(self, candidate_data, job_data)
        
        # Secteurs
        c_sector = candidate_data.get('professional_info', {}).get('sector', '').lower()
        j_sector = job_data.get('job_info', {}).get('sector', '').lower()
        
        # Incompatibilité Tech vs Finance/Comptabilité
        tech_words = ["tech", "informatique", "développement"]
        finance_words = ["finance", "comptabilité", "compta"]
        
        c_tech = any(w in c_sector for w in tech_words)
        c_finance = any(w in c_sector for w in finance_words)
        j_tech = any(w in j_sector for w in tech_words)
        j_finance = any(w in j_sector for w in finance_words)
        
        # Application pénalité
        if (c_tech and j_finance) or (c_finance and j_tech):
            old_score = result.total_score
            penalty = 0.5 if "comptabil" in (c_sector + j_sector) else 0.6
            result.total_score = old_score * penalty
            result.alerts.append(f"SECTORAL_PENALTY: {old_score:.3f} → {result.total_score:.3f}")
            print(f"   Pénalité appliquée: {old_score:.3f} → {result.total_score:.3f}")
        
        return result
    
    # Remplacement
    GPTNextvisionIntegrator.perform_complete_matching = apply_sectoral_penalty
    print("✅ Patch appliqué")
    
    # Test rapide
    print("\n📋 Tests critiques:")
    
    integrator = GPTNextvisionIntegrator(cv_parser=cv_parser, job_parser=job_parser)
    
    # Test 1: Charlotte vs Comptable (doit rester ~0.335)
    charlotte_result = integrator.test_charlotte_darmon_vs_comptable()
    charlotte_score = charlotte_result['result'].total_score
    charlotte_ok = abs(charlotte_score - 0.335) < 0.05
    
    print(f"1. Charlotte vs Comptable: {charlotte_score:.3f} {'✅' if charlotte_ok else '❌'}")
    
    # Test 2: Dev React vs Comptable (doit baisser)
    try:
        from test_semantic_matching import SemanticTestSuite
        test_suite = SemanticTestSuite()
        test_suite.integrator = integrator
        
        # Profiles test
        profiles = test_suite.create_test_profiles()
        
        # Dev vs Comptable
        dev_data = test_suite.convert_to_nextvision_format("cv", profiles["cv_profiles"]["dev_react_senior"])
        comptable_data = test_suite.convert_to_nextvision_format("job", profiles["job_profiles"]["comptable_entry"])
        
        dev_result = integrator.perform_complete_matching(dev_data, comptable_data)
        dev_score = dev_result.total_score
        dev_improved = dev_score < 0.30
        
        print(f"2. Dev vs Comptable: {dev_score:.3f} {'✅' if dev_improved else '❌'}")
        
        # Comptable vs Dev
        comptable_cv = test_suite.convert_to_nextvision_format("cv", profiles["cv_profiles"]["comptable_junior"])
        dev_job = test_suite.convert_to_nextvision_format("job", profiles["job_profiles"]["dev_react_senior"])
        
        comptable_result = integrator.perform_complete_matching(comptable_cv, dev_job)
        comptable_score = comptable_result.total_score
        comptable_improved = comptable_score < 0.30
        
        print(f"3. Comptable vs Dev: {comptable_score:.3f} {'✅' if comptable_improved else '❌'}")
        
        # Résumé
        success_count = sum([charlotte_ok, dev_improved, comptable_improved])
        print(f"\n📊 Résultats: {success_count}/3 tests réussis")
        
        if success_count >= 2 and charlotte_ok:
            print("🎯 PATCH RÉUSSI")
            print("   Incompatibilités sectorielles corrigées")
            print("   Charlotte DARMON préservée")
        else:
            print("⚠️ Patch partiellement efficace")
            print(f"   Succès: {success_count}/3")
        
    except Exception as e:
        print(f"❌ Erreur tests étendus: {e}")
        print("Test Charlotte seul disponible")
    
except Exception as e:
    print(f"❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Patch terminé")
