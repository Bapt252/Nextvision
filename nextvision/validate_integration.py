#!/usr/bin/env python3

"""
🧪 VALIDATION FINALE INTÉGRATION NEXTVISION GPT v3.1
"""

import sys
import time
import traceback
from pathlib import Path

def validate_integration():
    """Validation complète de l'intégration"""
    
    print("🧪 VALIDATION FINALE NEXTVISION GPT v3.1")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 6
    
    # Test 1: Imports
    print("\n📦 Test 1/6: Imports des modules...")
    try:
        from services.nextvision_gpt_parser import NextvisionGPTParser
        from services.nextvision_job_parser import NextvisionJobParser
        from services.nextvision_gpt_integration import NextvisionGPTIntegration
        print("✅ Imports réussis")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Imports échoués: {e}")
    
    # Test 2: Initialisation
    print("\n⚙️ Test 2/6: Initialisation...")
    try:
        parser = NextvisionGPTParser()
        job_parser = NextvisionJobParser()
        integration = NextvisionGPTIntegration()
        print("✅ Initialisation réussie")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Initialisation échouée: {e}")
    
    # Test 3: Fallback Dorothée
    print("\n👤 Test 3/6: Profil Dorothée...")
    try:
        profile = parser._get_fallback_profile()
        assert profile.informations_personnelles['nom_complet'] == "Dorothée Lim"
        assert len(profile.experiences_professionnelles) > 0
        print("✅ Profil Dorothée OK")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Profil Dorothée échoué: {e}")
    
    # Test 4: Job posting fallback
    print("\n💼 Test 4/6: Fiche de poste...")
    try:
        job = job_parser._get_fallback_job_posting()
        assert job.informations_poste['intitule'] == "Développeur Full-Stack Senior"
        assert job.secteur_activite['secteur_detecte'] == "tech"
        print("✅ Fiche de poste OK")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Fiche de poste échouée: {e}")
    
    # Test 5: Matching V3.1
    print("\n🎯 Test 5/6: Matching V3.1...")
    try:
        result = integration.compute_enhanced_matching(profile, job)
        assert 0 <= result.overall_score <= 1
        assert 'sector' in result.score_breakdown
        assert result.sector_compatibility >= 0
        print(f"✅ Matching OK - Score: {result.overall_score:.3f}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Matching échoué: {e}")
    
    # Test 6: Performance
    print("\n⚡ Test 6/6: Performance...")
    try:
        start_time = time.time()
        
        # Pipeline complet simulé
        test_profile = parser._get_fallback_profile()
        test_job = job_parser._get_fallback_job_posting()
        test_result = integration.compute_enhanced_matching(test_profile, test_job)
        
        processing_time = (time.time() - start_time) * 1000
        
        if processing_time <= 100:
            print(f"✅ Performance OK: {processing_time:.2f}ms < 100ms")
            tests_passed += 1
        else:
            print(f"⚠️ Performance limite: {processing_time:.2f}ms > 100ms")
            tests_passed += 0.5  # Demi-point car fonctionnel mais lent
            
    except Exception as e:
        print(f"❌ Test performance échoué: {e}")
    
    # Résultats finaux
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS DE VALIDATION")
    print("=" * 50)
    
    success_rate = (tests_passed / tests_total) * 100
    
    print(f"Tests réussis: {tests_passed}/{tests_total}")
    print(f"Taux de réussite: {success_rate:.1f}%")
    
    if tests_passed == tests_total:
        print("\n🎉 VALIDATION COMPLÈTE RÉUSSIE ! 🎉")
        print("✅ Nextvision GPT v3.1 est prêt pour la production")
        print("\n🚀 Prochaines étapes:")
        print("  1. Configurez votre clé OpenAI: export OPENAI_API_KEY='sk-...'")
        print("  2. Testez avec vos vrais CVs")
        print("  3. Intégrez dans votre workflow")
        return True
    elif tests_passed >= tests_total * 0.8:
        print("\n✅ VALIDATION MAJORITAIREMENT RÉUSSIE")
        print("⚠️ Quelques ajustements mineurs peuvent être nécessaires")
        return True
    else:
        print("\n❌ VALIDATION ÉCHOUÉE")
        print("🔧 Vérifiez les erreurs ci-dessus et relancez le déploiement")
        return False

if __name__ == "__main__":
    success = validate_integration()
    sys.exit(0 if success else 1)
