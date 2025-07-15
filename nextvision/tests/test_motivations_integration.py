# nextvision/tests/test_motivations_integration.py
"""
Tests complets pour validation de l'intégration MotivationsAlignmentScorer
Compatible avec les données de test existantes : cv_baptiste_test.txt et job_test.txt
Performance cible : < 21ms total (2-5ms pour motivations)
"""

import asyncio
import time
import json
from typing import Dict, Any
import pytest

from nextvision.engines.motivations_scoring_engine import motivations_scoring_engine
from nextvision.services.job_intelligence_service import job_intelligence_service
from nextvision.models.questionnaire_advanced import MotivationsClassees, QuestionnaireComplet
from nextvision.services.gpt_direct_service import JobData, CVData


class MotivationsTestSuite:
    """Suite de tests pour validation complète du système motivations"""
    
    def __init__(self):
        self.test_results = []
        
    async def run_full_test_suite(self) -> Dict[str, Any]:
        """Exécute tous les tests de validation"""
        
        print("🧪 Début des tests MotivationsAlignmentScorer")
        print("=" * 60)
        
        results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "performance_tests": {},
            "integration_tests": {},
            "edge_cases": {},
            "summary": {}
        }
        
        # 1. Tests de performance
        print("\n📊 TESTS DE PERFORMANCE")
        results["performance_tests"] = await self._test_performance()
        
        # 2. Tests d'intégration
        print("\n🔗 TESTS D'INTÉGRATION")
        results["integration_tests"] = await self._test_integration()
        
        # 3. Tests de cas limites
        print("\n⚠️ TESTS CAS LIMITES")
        results["edge_cases"] = await self._test_edge_cases()
        
        # 4. Tests avec données réelles (cv_baptiste_test.txt, job_test.txt)
        print("\n📄 TESTS DONNÉES RÉELLES")
        results["real_data_tests"] = await self._test_real_data()
        
        # 5. Synthèse finale
        results["summary"] = self._generate_summary(results)
        
        print("\n" + "=" * 60)
        print("🎯 RÉSULTATS FINAUX :", results["summary"]["status"])
        
        return results
    
    async def _test_performance(self) -> Dict[str, Any]:
        """Tests de performance - objectif < 5ms pour scoring motivations"""
        
        results = {"target_ms": 5.0, "tests": []}
        
        # Test 1: Performance scoring basique
        test_motivations = MotivationsClassees(
            classees=["Évolution", "Innovation", "Équipe", "Salaire"],
            priorites=[1, 2, 3, 4]
        )
        
        test_job = JobData(
            title="Senior AI Engineer",
            company="TechCorp Innovation",
            benefits=["Formation continue", "Stock options", "Télétravail flexible"],
            responsibilities=["Développement IA", "Leadership équipe", "Innovation produit"]
        )
        
        # Mesure de performance
        times = []
        for i in range(10):  # 10 exécutions pour moyenne
            start = time.perf_counter()
            score = await motivations_scoring_engine.calculate_score(
                candidat_motivations=test_motivations,
                job_data=test_job,
                job_cache_key=f"test_perf_{i}"
            )
            duration_ms = (time.perf_counter() - start) * 1000
            times.append(duration_ms)
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        perf_test = {
            "test_name": "scoring_performance",
            "avg_time_ms": round(avg_time, 2),
            "max_time_ms": round(max_time, 2),
            "min_time_ms": round(min_time, 2),
            "target_met": avg_time < results["target_ms"],
            "status": "✅ PASS" if avg_time < results["target_ms"] else "❌ FAIL"
        }
        
        results["tests"].append(perf_test)
        print(f"Performance Scoring: {avg_time:.2f}ms (cible: {results['target_ms']}ms) {perf_test['status']}")
        
        # Test 2: Performance avec cache
        start = time.perf_counter()
        cached_score = await motivations_scoring_engine.calculate_score(
            candidat_motivations=test_motivations,
            job_data=test_job,
            job_cache_key="test_perf_0"  # Même clé = cache hit
        )
        cache_time = (time.perf_counter() - start) * 1000
        
        cache_test = {
            "test_name": "cache_performance", 
            "time_ms": round(cache_time, 2),
            "improvement": round(avg_time / cache_time, 1) if cache_time > 0 else "inf",
            "status": "✅ PASS" if cache_time < avg_time / 2 else "⚠️ WARN"
        }
        
        results["tests"].append(cache_test)
        print(f"Performance Cache: {cache_time:.2f}ms (amélioration: {cache_test['improvement']}x) {cache_test['status']}")
        
        return results
    
    async def _test_integration(self) -> Dict[str, Any]:
        """Tests d'intégration avec l'architecture existante"""
        
        results = {"tests": []}
        
        # Test 1: Intégration QuestionnaireComplet
        questionnaire = QuestionnaireComplet(
            motivations=MotivationsClassees(
                classees=["Innovation", "Évolution", "Équipe", "Salaire"],
                priorites=[1, 2, 3, 4]
            )
        )
        
        job_data = JobData(
            title="Lead AI Engineer",
            company="InnovCorp",
            benefits=["R&D budget", "Formation", "Équipe agile", "Bonus performance"],
            responsibilities=["Innovation IA", "Encadrement", "Projets cutting-edge"]
        )
        
        try:
            score = await motivations_scoring_engine.calculate_score(
                candidat_motivations=questionnaire.motivations,
                job_data=job_data
            )
            
            integration_test = {
                "test_name": "questionnaire_integration",
                "score": round(score, 3),
                "valid_range": 0.0 <= score <= 1.0,
                "status": "✅ PASS" if 0.0 <= score <= 1.0 else "❌ FAIL"
            }
            
        except Exception as e:
            integration_test = {
                "test_name": "questionnaire_integration",
                "error": str(e),
                "status": "❌ FAIL"
            }
        
        results["tests"].append(integration_test)
        print(f"Intégration Questionnaire: Score {integration_test.get('score', 'ERROR')} {integration_test['status']}")
        
        # Test 2: Job Intelligence Service
        try:
            job_intelligence = await job_intelligence_service.analyze_job_intelligence(
                job_data=job_data,
                cache_key="integration_test"
            )
            
            intelligence_test = {
                "test_name": "job_intelligence_service",
                "culture_type": job_intelligence.culture_type,
                "innovation_level": job_intelligence.innovation_level,
                "confidence": round(job_intelligence.confidence_score, 2),
                "processing_time": round(job_intelligence.processing_time_ms, 2),
                "status": "✅ PASS" if job_intelligence.confidence_score > 0 else "❌ FAIL"
            }
            
        except Exception as e:
            intelligence_test = {
                "test_name": "job_intelligence_service",
                "error": str(e),
                "status": "❌ FAIL"
            }
        
        results["tests"].append(intelligence_test)
        print(f"Job Intelligence: {intelligence_test.get('culture_type', 'ERROR')} {intelligence_test['status']}")
        
        return results
    
    async def _test_edge_cases(self) -> Dict[str, Any]:
        """Tests des cas limites et robustesse"""
        
        results = {"tests": []}
        
        # Test 1: Motivations vides
        empty_motivations = MotivationsClassees(classees=[], priorites=[])
        
        normal_job = JobData(
            title="Developer",
            benefits=["Salaire attractif"],
            responsibilities=["Développement"]
        )
        
        try:
            score = await motivations_scoring_engine.calculate_score(
                candidat_motivations=empty_motivations,
                job_data=normal_job
            )
            
            empty_test = {
                "test_name": "empty_motivations",
                "score": round(score, 3),
                "handled": True,
                "status": "✅ PASS"
            }
            
        except Exception as e:
            empty_test = {
                "test_name": "empty_motivations",
                "error": str(e),
                "handled": False,
                "status": "❌ FAIL"
            }
        
        results["tests"].append(empty_test)
        print(f"Motivations Vides: {empty_test.get('score', 'ERROR')} {empty_test['status']}")
        
        # Test 2: Job sans données
        empty_job = JobData(title="", benefits=[], responsibilities=[])
        
        normal_motivations = MotivationsClassees(
            classees=["Évolution"],
            priorites=[1]
        )
        
        try:
            score = await motivations_scoring_engine.calculate_score(
                candidat_motivations=normal_motivations,
                job_data=empty_job
            )
            
            empty_job_test = {
                "test_name": "empty_job",
                "score": round(score, 3),
                "handled": True,
                "status": "✅ PASS"
            }
            
        except Exception as e:
            empty_job_test = {
                "test_name": "empty_job",
                "error": str(e),
                "handled": False,
                "status": "❌ FAIL"
            }
        
        results["tests"].append(empty_job_test)
        print(f"Job Vide: {empty_job_test.get('score', 'ERROR')} {empty_job_test['status']}")
        
        return results
    
    async def _test_real_data(self) -> Dict[str, Any]:
        """Tests avec les données réelles de l'architecture existante"""
        
        results = {"tests": []}
        
        # Simulation des données cv_baptiste_test.txt
        cv_data_mock = CVData(
            name="Baptiste Test",
            skills=["Python", "FastAPI", "React", "IA", "Machine Learning"],
            experience="5+ ans développement"
        )
        
        # Simulation questionnaire Baptiste (déduit du profil)
        baptiste_motivations = MotivationsClassees(
            classees=["Innovation", "Évolution", "Technologie", "Leadership"],
            priorites=[1, 2, 3, 4]
        )
        
        # Simulation job_test.txt - AI Engineer Senior
        job_data_mock = JobData(
            title="AI Engineer Senior",
            company="TechCorp Innovation",
            benefits=[
                "Formation continue et certifications",
                "Télétravail hybride flexible", 
                "Stock options et intéressement",
                "Budget R&D personnel"
            ],
            responsibilities=[
                "Développement solutions IA innovantes",
                "Leadership technique équipe",
                "Recherche et veille technologique",
                "Encadrement projets cutting-edge"
            ]
        )
        
        try:
            # Test scoring avec données réelles simulées
            start_time = time.perf_counter()
            
            real_score = await motivations_scoring_engine.calculate_score(
                candidat_motivations=baptiste_motivations,
                job_data=job_data_mock,
                job_cache_key="real_data_test"
            )
            
            processing_time = (time.perf_counter() - start_time) * 1000
            
            # Analyse intelligence job
            job_intel = await job_intelligence_service.analyze_job_intelligence(
                job_data=job_data_mock,
                cache_key="real_data_test"
            )
            
            real_data_test = {
                "test_name": "real_data_simulation",
                "score": round(real_score, 3),
                "processing_time_ms": round(processing_time, 2),
                "job_culture": job_intel.culture_type,
                "innovation_level": job_intel.innovation_level,
                "growth_potential": round(job_intel.growth_potential, 2),
                "confidence": round(job_intel.confidence_score, 2),
                "expected_high_score": real_score > 0.7,  # Baptiste = profil innovation/évolution
                "status": "✅ PASS" if real_score > 0.6 else "⚠️ WARN"
            }
            
        except Exception as e:
            real_data_test = {
                "test_name": "real_data_simulation",
                "error": str(e),
                "status": "❌ FAIL"
            }
        
        results["tests"].append(real_data_test)
        print(f"Données Réelles: Score {real_data_test.get('score', 'ERROR')} {real_data_test['status']}")
        
        return results
    
    def _generate_summary(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Génère un résumé final des tests"""
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        warnings = 0
        
        # Compilation des résultats
        for test_category in ["performance_tests", "integration_tests", "edge_cases", "real_data_tests"]:
            if test_category in all_results and "tests" in all_results[test_category]:
                for test in all_results[test_category]["tests"]:
                    total_tests += 1
                    if test["status"].startswith("✅"):
                        passed_tests += 1
                    elif test["status"].startswith("⚠️"):
                        warnings += 1
                        passed_tests += 1  # Warning = passé avec réserve
                    else:
                        failed_tests += 1
        
        # Performance globale
        avg_perf = None
        if "performance_tests" in all_results and all_results["performance_tests"]["tests"]:
            perf_test = all_results["performance_tests"]["tests"][0]
            avg_perf = perf_test.get("avg_time_ms", None)
        
        # Statut final
        if failed_tests == 0 and warnings == 0:
            status = "✅ TOUS TESTS PASSÉS"
        elif failed_tests == 0:
            status = f"⚠️ PASSÉ AVEC {warnings} AVERTISSEMENT(S)"
        else:
            status = f"❌ {failed_tests} TEST(S) ÉCHOUÉ(S)"
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "warnings": warnings,
            "success_rate": round(passed_tests / total_tests * 100, 1) if total_tests > 0 else 0,
            "avg_performance_ms": avg_perf,
            "performance_target_met": avg_perf < 5.0 if avg_perf else False,
            "status": status,
            "ready_for_production": failed_tests == 0 and (avg_perf or 0) < 5.0
        }


# ==========================================
# TESTS SPÉCIFIQUES ENDPOINT
# ==========================================

async def test_endpoint_integration():
    """Test d'intégration complète avec l'endpoint /api/v3/intelligent-matching"""
    
    print("\n🔗 TEST ENDPOINT INTEGRATION")
    
    # Simulation requête complète
    from nextvision.models.questionnaire_advanced import QuestionnaireComplet, MotivationsClassees
    
    mock_request = {
        "questionnaire": QuestionnaireComplet(
            motivations=MotivationsClassees(
                classees=["Innovation", "Évolution", "Équipe"],
                priorites=[1, 2, 3]
            )
        ),
        "job_requirements": JobData(
            title="Senior AI Engineer",
            company="TechCorp",
            benefits=["Formation", "Innovation", "Équipe agile"],
            responsibilities=["IA", "Leadership", "R&D"]
        ),
        "pourquoi_ecoute": "Recherche nouveau défi innovation"
    }
    
    # Test calcul scores complets
    start_time = time.perf_counter()
    
    # Scores existants (simulation)
    static_scores = {
        "semantique": 0.62,
        "hierarchical": 0.66,
        "remuneration": 0.735,
        "experience": 0.5,
        "secteurs": 0.7,
        "localisation": 0.92
    }
    
    # Nouveau score motivations
    motivations_score = await motivations_scoring_engine.calculate_score(
        candidat_motivations=mock_request["questionnaire"].motivations,
        job_data=mock_request["job_requirements"]
    )
    
    # Scores combinés
    all_scores = {**static_scores, "motivations": motivations_score}
    
    # Pondération (exemple)
    weights = {
        "semantique": 0.15,
        "hierarchical": 0.10, 
        "remuneration": 0.15,
        "experience": 0.10,
        "secteurs": 0.15,
        "localisation": 0.15,
        "motivations": 0.20  # Boost pour "innovation"
    }
    
    # Score final
    final_score = sum(all_scores[comp] * weights[comp] for comp in all_scores.keys())
    
    total_time = (time.perf_counter() - start_time) * 1000
    
    print(f"Scores combinés: {all_scores}")
    print(f"Score final: {final_score:.3f}")
    print(f"Temps total: {total_time:.2f}ms")
    print(f"Objectif < 21ms: {'✅ PASS' if total_time < 21 else '❌ FAIL'}")
    
    return {
        "final_score": final_score,
        "motivations_score": motivations_score,
        "total_time_ms": total_time,
        "target_met": total_time < 21
    }


# ==========================================
# COMMANDE DE VALIDATION RAPIDE
# ==========================================

async def quick_validation():
    """Validation rapide pour CI/CD"""
    
    print("⚡ VALIDATION RAPIDE MOTIVATIONS SCORER")
    
    # Test basique
    motivations = MotivationsClassees(classees=["Innovation"], priorites=[1])
    job = JobData(title="AI Engineer", benefits=["Innovation"], responsibilities=["IA"])
    
    score = await motivations_scoring_engine.calculate_score(
        candidat_motivations=motivations,
        job_data=job
    )
    
    valid = 0.0 <= score <= 1.0
    print(f"Score: {score:.3f} | Valide: {'✅' if valid else '❌'}")
    
    return valid


# ==========================================
# EXÉCUTION DES TESTS
# ==========================================

if __name__ == "__main__":
    async def main():
        # Test rapide
        await quick_validation()
        
        # Test endpoint
        await test_endpoint_integration()
        
        # Suite complète
        test_suite = MotivationsTestSuite()
        results = await test_suite.run_full_test_suite()
        
        # Sauvegarde résultats
        with open("motivations_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📊 Résultats sauvegardés dans motivations_test_results.json")
        
        return results
    
    # Exécution
    test_results = asyncio.run(main())
