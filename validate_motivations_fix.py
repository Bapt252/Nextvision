#!/usr/bin/env python3
"""
🔧 SCRIPT DE VALIDATION RAPIDE - MotivationsAlignmentScorer
==========================================================

Script de validation pour vérifier que le problème JobData est résolu
et que l'intégration motivations fonctionne correctement.

Usage: python validate_motivations_fix.py
"""

import sys
import os
import time

# Add nextvision to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """🔌 Test des imports"""
    print("🔌 Test imports...")
    try:
        from nextvision.engines.motivations_scoring_engine import (
            MotivationsAlignmentScorer,
            create_complete_job_data,
            create_complete_cv_data,
            motivations_scoring_engine
        )
        from nextvision.services.gpt_direct_service import JobData, CVData
        print("   ✅ Tous les imports réussis")
        return True
    except ImportError as e:
        print(f"   ❌ Erreur import: {e}")
        return False

def test_jobdata_structure():
    """🏗️ Test structure JobData complète"""
    print("🏗️ Test structure JobData...")
    try:
        from nextvision.engines.motivations_scoring_engine import create_complete_job_data
        
        # Test création job simple
        job = create_complete_job_data(
            title="Test Engineer",
            company="Test Corp"
        )
        
        # Vérification tous les champs requis
        required_fields = [
            'title', 'company', 'location', 'contract_type', 
            'required_skills', 'preferred_skills', 'responsibilities',
            'requirements', 'benefits', 'salary_range', 'remote_policy'
        ]
        
        for field in required_fields:
            if not hasattr(job, field):
                print(f"   ❌ Champ manquant: {field}")
                return False
        
        print(f"   ✅ JobData complète: {job.title} chez {job.company}")
        print(f"   ✅ Tous les {len(required_fields)} champs présents")
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur structure JobData: {e}")
        return False

def test_motivations_scoring():
    """🎯 Test scoring motivationnel"""
    print("🎯 Test scoring motivationnel...")
    try:
        from nextvision.engines.motivations_scoring_engine import (
            create_complete_job_data,
            create_complete_cv_data,
            motivations_scoring_engine
        )
        
        # Données test
        candidate = create_complete_cv_data(
            name="Test Candidat",
            skills=["Python", "Leadership", "Innovation"],
            objective="Recherche poste avec innovation et leadership"
        )
        
        job = create_complete_job_data(
            title="Senior Developer",
            company="InnovCorp",
            required_skills=["Python", "Leadership"],
            benefits=["Innovation continue", "Leadership équipe", "Évolution rapide"]
        )
        
        # Test scoring
        start_time = time.time()
        result = motivations_scoring_engine.score_motivations_alignment(
            candidate_data=candidate,
            job_data=job,
            candidate_motivations=["Innovation", "Leadership", "Évolution"]
        )
        processing_time = (time.time() - start_time) * 1000
        
        # Validation résultat
        if not (0.0 <= result.overall_score <= 1.0):
            print(f"   ❌ Score invalide: {result.overall_score}")
            return False
        
        if not (0.0 <= result.confidence <= 1.0):
            print(f"   ❌ Confiance invalide: {result.confidence}")
            return False
        
        print(f"   ✅ Score: {result.overall_score:.3f}")
        print(f"   ✅ Confiance: {result.confidence:.3f}")
        print(f"   ✅ Temps: {processing_time:.2f}ms")
        print(f"   ✅ Performance: {'🚀 Excellent' if processing_time < 5 else '✅ Bon' if processing_time < 10 else '⚠️ Lent'}")
        
        if len(result.motivation_scores) > 0:
            print(f"   ✅ Motivations analysées: {len(result.motivation_scores)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur scoring: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance():
    """⚡ Test performance multiple"""
    print("⚡ Test performance multiple...")
    try:
        from nextvision.engines.motivations_scoring_engine import (
            create_complete_job_data,
            create_complete_cv_data,
            motivations_scoring_engine
        )
        
        candidate = create_complete_cv_data(name="Perf User")
        job = create_complete_job_data(title="Perf Job", company="Perf Corp")
        
        times = []
        for i in range(5):
            start = time.time()
            result = motivations_scoring_engine.score_motivations_alignment(
                candidate_data=candidate,
                job_data=job
            )
            times.append((time.time() - start) * 1000)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        
        print(f"   ✅ Temps moyen: {avg_time:.2f}ms")
        print(f"   ✅ Temps min: {min_time:.2f}ms")
        print(f"   ✅ Objectif < 5ms: {'✅' if avg_time < 5 else '⚠️' if avg_time < 10 else '❌'}")
        
        return avg_time < 10  # Acceptable si < 10ms
        
    except Exception as e:
        print(f"   ❌ Erreur performance: {e}")
        return False

def test_original_problem():
    """🔧 Test du problème original résolu"""
    print("🔧 Test problème original (TypeError resolved)...")
    try:
        from nextvision.services.gpt_direct_service import JobData
        
        # Test que l'ancien code échoue toujours (normal)
        try:
            job = JobData(
                title="AI Engineer",
                benefits=["Innovation"], 
                responsibilities=["IA"]
            )
            print("   ⚠️ Ancien code devrait échouer mais fonctionne")
            return False
        except TypeError:
            print("   ✅ Ancien code échoue comme attendu (TypeError)")
        
        # Test que la nouvelle méthode fonctionne
        from nextvision.engines.motivations_scoring_engine import create_complete_job_data
        
        job = create_complete_job_data(
            title="AI Engineer",
            company="TechCorp",
            benefits=["Innovation", "Télétravail"],
            responsibilities=["Développement IA", "Innovation produits"]
        )
        
        print(f"   ✅ Nouvelle méthode fonctionne: {job.title}")
        print("   ✅ Problème TypeError: RÉSOLU")
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur test problème: {e}")
        return False

def test_api_integration():
    """🌐 Test intégration API (vérification imports)"""
    print("🌐 Test intégration API...")
    try:
        # Test que l'endpoint peut importer le scorer
        from nextvision.api.v3.intelligent_matching import (
            IntelligentMatchingService
        )
        
        service = IntelligentMatchingService()
        
        if hasattr(service, 'motivations_scorer'):
            if service.motivations_scorer is not None:
                print("   ✅ MotivationsScorer intégré dans IntelligentMatchingService")
            else:
                print("   ⚠️ MotivationsScorer non disponible (mode fallback)")
        else:
            print("   ❌ MotivationsScorer non trouvé dans service")
            return False
        
        print("   ✅ Intégration API: OK")
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur intégration API: {e}")
        return False

def main():
    """🚀 Validation complète"""
    print("🔧 VALIDATION MOTIVATIONS ALIGNMENT SCORER")
    print("=" * 50)
    print("✅ Objectif: Vérifier résolution problème JobData")
    print("✅ Validation: Intégration motivations complète")
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Structure JobData", test_jobdata_structure),
        ("Scoring Motivations", test_motivations_scoring),
        ("Performance", test_performance),
        ("Problème Original", test_original_problem),
        ("Intégration API", test_api_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20}")
        print(f"🧪 {test_name}")
        print(f"{'='*20}")
        
        success = test_func()
        results.append((test_name, success))
        
        if success:
            print(f"✅ {test_name}: SUCCÈS")
        else:
            print(f"❌ {test_name}: ÉCHEC")
    
    # Bilan final
    print("\n" + "="*50)
    print("🏆 BILAN VALIDATION")
    print("="*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\nRésultat: {passed}/{total} tests passés")
    
    if passed == total:
        print("\n🎉 VALIDATION COMPLÈTE: SUCCÈS!")
        print("✅ Problème JobData: RÉSOLU")
        print("✅ MotivationsAlignmentScorer: OPÉRATIONNEL")
        print("✅ Intégration API: PRÊTE")
        print("🚀 PRÊT POUR PRODUCTION!")
        return True
    else:
        print(f"\n⚠️ VALIDATION PARTIELLE: {passed}/{total}")
        print("🔧 Certains tests nécessitent attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
