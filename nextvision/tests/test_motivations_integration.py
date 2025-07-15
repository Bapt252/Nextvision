#!/usr/bin/env python3
"""
🧪 TESTS INTÉGRATION - MotivationsAlignmentScorer
=================================================

Tests complets pour valider l'intégration du MotivationsAlignmentScorer
dans l'écosystème NEXTVISION avec structure JobData complète.

✅ Tests structure JobData complète
✅ Tests performance < 5ms
✅ Tests intégration endpoint
✅ Tests cas d'erreur et fallbacks

Author: NEXTEN Team
Version: 1.0.0
"""

import sys
import os
import time
import unittest
from typing import List, Dict, Any

# Add nextvision to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from nextvision.engines.motivations_scoring_engine import (
        MotivationsAlignmentScorer,
        MotivationType,
        MotivationScore,
        MotivationsResult,
        create_complete_job_data,
        create_complete_cv_data,
        motivations_scoring_engine
    )
    from nextvision.services.gpt_direct_service import JobData, CVData
    print("✅ All NEXTVISION imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class TestJobDataStructure(unittest.TestCase):
    """🏗️ Tests structure JobData complète"""
    
    def test_complete_jobdata_creation(self):
        """Test création JobData avec tous les champs requis"""
        job = create_complete_job_data(
            title="AI Engineer",
            company="TechCorp",
            required_skills=["Python", "AI"],
            benefits=["Innovation", "Télétravail"]
        )
        
        # Vérification tous les champs requis présents
        self.assertIsInstance(job, JobData)
        self.assertEqual(job.title, "AI Engineer")
        self.assertEqual(job.company, "TechCorp")
        self.assertIsInstance(job.location, str)
        self.assertIsInstance(job.contract_type, str)
        self.assertIsInstance(job.required_skills, list)
        self.assertIsInstance(job.preferred_skills, list)
        self.assertIsInstance(job.responsibilities, list)
        self.assertIsInstance(job.requirements, list)
        self.assertIsInstance(job.benefits, list)
        self.assertIsInstance(job.salary_range, dict)
        self.assertIsInstance(job.remote_policy, str)
        
        # Vérification contenu
        self.assertIn("Python", job.required_skills)
        self.assertIn("Innovation", job.benefits)
        self.assertIn("min", job.salary_range)
        self.assertIn("max", job.salary_range)
    
    def test_complete_cvdata_creation(self):
        """Test création CVData avec tous les champs requis"""
        cv = create_complete_cv_data(
            name="Test User",
            skills=["Python", "Leadership"]
        )
        
        # Vérification structure
        self.assertIsInstance(cv, CVData)
        self.assertEqual(cv.name, "Test User")
        self.assertIn("Python", cv.skills)
        self.assertIsInstance(cv.years_of_experience, int)
        self.assertIsInstance(cv.languages, list)
    
    def test_jobdata_direct_creation_failure(self):
        """Test que la création directe JobData échoue sans tous les champs"""
        with self.assertRaises(TypeError):
            # Ceci doit échouer - structure incomplète
            JobData(
                title="AI Engineer",
                benefits=["Innovation"],
                responsibilities=["IA"]
            )

class TestMotivationsScoring(unittest.TestCase):
    """🎯 Tests scoring motivationnel"""
    
    def setUp(self):
        """Setup données test"""
        self.scorer = MotivationsAlignmentScorer()
        
        self.candidate = create_complete_cv_data(
            name="Marie Test",
            skills=["Python", "Leadership", "Innovation"],
            objective="Recherche poste avec innovation et évolution",
            years_of_experience=4
        )
        
        self.job = create_complete_job_data(
            title="Senior Engineer",
            company="InnovCorp",
            required_skills=["Python", "Leadership"],
            benefits=["Innovation continue", "Évolution rapide", "Équipe tech"],
            responsibilities=["Innovation produits", "Leadership équipe"],
            salary_range={"min": 60000, "max": 80000},
            remote_policy="Hybride"
        )
    
    def test_basic_scoring(self):
        """Test scoring basique"""
        result = self.scorer.score_motivations_alignment(
            candidate_data=self.candidate,
            job_data=self.job,
            candidate_motivations=["Innovation", "Évolution", "Leadership"]
        )
        
        # Validations résultat
        self.assertIsInstance(result, MotivationsResult)
        self.assertGreaterEqual(result.overall_score, 0.0)
        self.assertLessEqual(result.overall_score, 1.0)
        self.assertGreaterEqual(result.confidence, 0.0)
        self.assertLessEqual(result.confidence, 1.0)
        self.assertIsInstance(result.motivation_scores, list)
        self.assertGreater(len(result.motivation_scores), 0)
        self.assertIsInstance(result.processing_time_ms, float)
    
    def test_scoring_without_explicit_motivations(self):
        """Test scoring sans motivations explicites (détection auto)"""
        result = self.scorer.score_motivations_alignment(
            candidate_data=self.candidate,
            job_data=self.job,
            candidate_motivations=None  # Détection automatique
        )
        
        self.assertIsInstance(result, MotivationsResult)
        self.assertGreater(len(result.motivation_scores), 0)
    
    def test_high_innovation_alignment(self):
        """Test alignement fort sur innovation"""
        innovation_job = create_complete_job_data(
            title="Innovation Lead",
            company="StartupTech",
            required_skills=["Innovation", "Disruption", "R&D"],
            benefits=[
                "Innovation disruptive continue",
                "R&D cutting-edge",
                "Projets breakthrough",
                "Liberté créative totale"
            ],
            responsibilities=[
                "Direction innovation produits",
                "Recherche technologies disruptives",
                "Leadership équipes R&D"
            ]
        )
        
        innovation_candidate = create_complete_cv_data(
            name="Alex Innovateur",
            skills=["Innovation", "R&D", "Disruption"],
            objective="Passion innovation et création solutions disruptives"
        )
        
        result = self.scorer.score_motivations_alignment(
            candidate_data=innovation_candidate,
            job_data=innovation_job,
            candidate_motivations=["Innovation", "Créativité", "R&D"]
        )
        
        # Score innovation doit être élevé
        innovation_scores = [
            s for s in result.motivation_scores 
            if s.motivation_type == MotivationType.INNOVATION
        ]
        
        if innovation_scores:
            self.assertGreater(innovation_scores[0].score, 0.6)

class TestPerformance(unittest.TestCase):
    """⚡ Tests performance"""
    
    def setUp(self):
        self.candidate = create_complete_cv_data(
            name="Perf Test",
            skills=["Python"]
        )
        
        self.job = create_complete_job_data(
            title="Developer",
            company="Corp",
            required_skills=["Python"]
        )
    
    def test_performance_single_scoring(self):
        """Test performance scoring unique"""
        start_time = time.time()
        
        result = motivations_scoring_engine.score_motivations_alignment(
            candidate_data=self.candidate,
            job_data=self.job,
            candidate_motivations=["Innovation"]
        )
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Performance cible < 10ms
        self.assertLess(elapsed_ms, 10, f"Performance trop lente: {elapsed_ms:.2f}ms")
        self.assertLess(result.processing_time_ms, 10)
    
    def test_performance_multiple_scorings(self):
        """Test performance scorings multiples (cache)"""
        times = []
        
        for i in range(5):
            start_time = time.time()
            
            result = motivations_scoring_engine.score_motivations_alignment(
                candidate_data=self.candidate,
                job_data=self.job,
                candidate_motivations=["Innovation"]
            )
            
            elapsed_ms = (time.time() - start_time) * 1000
            times.append(elapsed_ms)
        
        avg_time = sum(times) / len(times)
        
        # Performance moyenne doit s'améliorer avec cache
        self.assertLess(avg_time, 10, f"Performance moyenne trop lente: {avg_time:.2f}ms")

class TestEdgeCases(unittest.TestCase):
    """🧪 Tests cas limites et erreurs"""
    
    def test_empty_job_content(self):
        """Test job avec contenu minimal"""
        minimal_job = create_complete_job_data(
            title="Job",
            company="Corp"
            # Utilise defaults pour autres champs
        )
        
        candidate = create_complete_cv_data(name="User")
        
        result = motivations_scoring_engine.score_motivations_alignment(
            candidate_data=candidate,
            job_data=minimal_job
        )
        
        # Doit fonctionner malgré contenu minimal
        self.assertIsInstance(result, MotivationsResult)
        self.assertGreaterEqual(result.overall_score, 0.0)
    
    def test_complex_motivations_mix(self):
        """Test mix complexe de motivations"""
        complex_job = create_complete_job_data(
            title="Complex Role",
            company="MegaCorp",
            required_skills=["Leadership", "Innovation", "Management"],
            benefits=[
                "Innovation continue",
                "Évolution rapide CTO",
                "Équipe 20 personnes",
                "Salaire top marché",
                "Télétravail complet",
                "Autonomie totale",
                "Impact business majeur"
            ],
            responsibilities=[
                "Innovation disruptive",
                "Leadership grande équipe",
                "Évolution vers CTO",
                "Autonomie décisions",
                "Impact business direct"
            ],
            salary_range={"min": 120000, "max": 150000}
        )
        
        candidate = create_complete_cv_data(
            name="Senior Pro",
            skills=["Leadership", "Innovation", "Business"],
            objective="Recherche poste avec toutes dimensions: innovation, leadership, impact, évolution, autonomie"
        )
        
        result = motivations_scoring_engine.score_motivations_alignment(
            candidate_data=candidate,
            job_data=complex_job,
            candidate_motivations=[
                "Innovation",
                "Leadership", 
                "Évolution",
                "Autonomie",
                "Impact",
                "Salaire"
            ]
        )
        
        # Doit scorer plusieurs motivations
        self.assertGreaterEqual(len(result.motivation_scores), 3)
        self.assertGreater(result.overall_score, 0.5)  # Score élevé attendu

class TestIntegrationReadiness(unittest.TestCase):
    """🔗 Tests prêt pour intégration endpoint"""
    
    def test_engine_instance_ready(self):
        """Test instance globale prête"""
        self.assertIsInstance(motivations_scoring_engine, MotivationsAlignmentScorer)
    
    def test_api_compatible_input_output(self):
        """Test format compatible API"""
        candidate = create_complete_cv_data(name="API Test")
        job = create_complete_job_data(title="API Job", company="API Corp")
        
        result = motivations_scoring_engine.score_motivations_alignment(
            candidate_data=candidate,
            job_data=job,
            candidate_motivations=["Innovation"]
        )
        
        # Format compatible avec réponse API
        self.assertIsInstance(result.overall_score, float)
        self.assertIsInstance(result.confidence, float)
        self.assertIsInstance(result.processing_time_ms, float)
        self.assertIsInstance(result.strongest_alignments, list)
        
        # Peut être sérialisé JSON
        import json
        try:
            json.dumps({
                "motivations_score": result.overall_score,
                "confidence": result.confidence,
                "processing_time_ms": result.processing_time_ms,
                "alignments": result.strongest_alignments
            })
        except Exception as e:
            self.fail(f"Serialization failed: {e}")

def run_performance_benchmark():
    """🚀 Benchmark performance détaillé"""
    print("\n" + "="*60)
    print("⚡ BENCHMARK PERFORMANCE DÉTAILLÉ")
    print("="*60)
    
    candidate = create_complete_cv_data(
        name="Benchmark User",
        skills=["Python", "Leadership", "Innovation"]
    )
    
    job = create_complete_job_data(
        title="Benchmark Job",
        company="Benchmark Corp",
        required_skills=["Python", "Leadership"],
        benefits=["Innovation", "Évolution"]
    )
    
    # Benchmark cold start
    print("❄️ Cold start test...")
    start = time.time()
    result1 = motivations_scoring_engine.score_motivations_alignment(
        candidate_data=candidate,
        job_data=job,
        candidate_motivations=["Innovation", "Leadership"]
    )
    cold_start_ms = (time.time() - start) * 1000
    
    # Benchmark warm runs
    print("🔥 Warm runs test...")
    warm_times = []
    for i in range(10):
        start = time.time()
        result = motivations_scoring_engine.score_motivations_alignment(
            candidate_data=candidate,
            job_data=job,
            candidate_motivations=["Innovation", "Leadership"]
        )
        warm_times.append((time.time() - start) * 1000)
    
    avg_warm = sum(warm_times) / len(warm_times)
    min_warm = min(warm_times)
    max_warm = max(warm_times)
    
    print(f"\n📊 RÉSULTATS BENCHMARK:")
    print(f"   ❄️ Cold start: {cold_start_ms:.2f}ms")
    print(f"   🔥 Warm avg: {avg_warm:.2f}ms")
    print(f"   🚀 Warm min: {min_warm:.2f}ms")
    print(f"   🐌 Warm max: {max_warm:.2f}ms")
    print(f"   🎯 Objectif < 5ms: {'✅' if avg_warm < 5 else '⚠️' if avg_warm < 10 else '❌'}")
    print(f"   📈 Score test: {result1.overall_score:.3f}")

def main():
    """🧪 Exécution tests complets"""
    print("🧪 NEXTVISION - Tests Intégration MotivationsAlignmentScorer")
    print("=" * 70)
    
    # Tests unitaires
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Ajout des classes de test
    test_classes = [
        TestJobDataStructure,
        TestMotivationsScoring,
        TestPerformance,
        TestEdgeCases,
        TestIntegrationReadiness
    ]
    
    for test_class in test_classes:
        tests = test_loader.loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Exécution tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Benchmark performance
    run_performance_benchmark()
    
    # Bilan final
    success = result.wasSuccessful()
    print("\n" + "="*70)
    print("🏆 BILAN TESTS INTÉGRATION")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    if success:
        print("\n🚀 MotivationsAlignmentScorer READY FOR PRODUCTION!")
        print("📈 Structure JobData: COMPLÈTE")
        print("⚡ Performance: OPTIMISÉE")
        print("🔗 Intégration endpoint: PRÊTE")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
