#!/usr/bin/env python3
"""
🎯 NEXTVISION V3.2.1 - SUITE DE TESTS END-TO-END COMPLÈTE

Test complet du parcours utilisateur :
1. Upload CV → Parsing GPT
2. Géocodage Google Maps
3. Calcul Transport Intelligence
4. Matching avec pondération V3.2.1
5. Validation Bridge Commitment-

Version: 3.2.1
Date: 2025-07-11
Auteur: Assistant Claude
"""

import asyncio
import time
import json
import traceback
import aiohttp
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('nextvision_e2e')

@dataclass
class TestResult:
    """Résultat d'un test individuel"""
    test_name: str
    success: bool
    duration_ms: float
    data: Optional[Dict] = None
    error: Optional[str] = None
    warnings: List[str] = None

@dataclass
class PerformanceMetrics:
    """Métriques de performance"""
    avg_response_time: float
    max_response_time: float
    min_response_time: float
    success_rate: float
    total_requests: int
    errors: List[str]

class NextvisionE2ETestSuite:
    """Suite de tests end-to-end pour Nextvision V3.2.1"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = None
        self.results: List[TestResult] = []
        self.start_time = None
        
        # Configuration des tests
        self.test_configs = {
            'timeout': 30,  # secondes
            'max_concurrent': 10,
            'stress_test_users': 50,
            'performance_threshold_ms': 2000
        }
        
        # Données de test
        self.sample_candidates = self._generate_test_candidates()
        self.sample_jobs = self._generate_test_jobs()
    
    async def __aenter__(self):
        """Initialisation asynchrone"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.test_configs['timeout'])
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Nettoyage asynchrone"""
        if self.session:
            await self.session.close()
    
    def _generate_test_candidates(self) -> List[Dict]:
        """Génère des candidats de test diversifiés"""
        return [
            {
                "name": "Charlotte DARMON",
                "experience": "15 ans d'expérience en tant que DAF",
                "skills": ["Finance", "Comptabilité", "Management", "Direction"],
                "salary_expectation": "80000",
                "location": "Paris 8ème",
                "level": "EXECUTIVE"
            },
            {
                "name": "Marie DURAND",
                "experience": "3 ans d'expérience comptable",
                "skills": ["Comptabilité", "Sage", "Excel"],
                "salary_expectation": "35000",
                "location": "Lyon 3ème",
                "level": "JUNIOR"
            },
            {
                "name": "Pierre MARTIN",
                "experience": "8 ans Chef comptable",
                "skills": ["Comptabilité", "Management", "Fiscalité"],
                "salary_expectation": "55000",
                "location": "Marseille",
                "level": "MANAGER"
            },
            {
                "name": "Sophie BERNARD",
                "experience": "12 ans Directrice comptable",
                "skills": ["Comptabilité", "Management", "Audit", "Direction"],
                "salary_expectation": "70000",
                "location": "Toulouse",
                "level": "DIRECTOR"
            },
            {
                "name": "Thomas LEBLANC",
                "experience": "1 an Assistant comptable",
                "skills": ["Comptabilité", "Saisie", "Excel"],
                "salary_expectation": "28000",
                "location": "Nantes",
                "level": "ENTRY"
            }
        ]
    
    def _generate_test_jobs(self) -> List[Dict]:
        """Génère des offres d'emploi de test"""
        return [
            {
                "title": "Comptable Général",
                "description": "Poste de comptable général pour PME",
                "required_experience": "2-5 ans",
                "salary_range": "32000-38000",
                "location": "Paris 15ème",
                "required_level": "JUNIOR",
                "skills": ["Comptabilité", "Sage"]
            },
            {
                "title": "Chef Comptable",
                "description": "Management d'équipe comptable",
                "required_experience": "5-10 ans",
                "salary_range": "50000-60000",
                "location": "Lyon",
                "required_level": "MANAGER",
                "skills": ["Comptabilité", "Management"]
            },
            {
                "title": "Directeur Administratif et Financier",
                "description": "Direction financière groupe",
                "required_experience": "10+ ans",
                "salary_range": "80000-120000",
                "location": "Paris La Défense",
                "required_level": "EXECUTIVE",
                "skills": ["Finance", "Direction", "Management"]
            },
            {
                "title": "Assistant Comptable",
                "description": "Support équipe comptabilité",
                "required_experience": "0-2 ans",
                "salary_range": "25000-30000",
                "location": "Bordeaux",
                "required_level": "ENTRY",
                "skills": ["Comptabilité", "Saisie"]
            }
        ]
    
    async def test_api_health(self) -> TestResult:
        """Test 1: Vérification de l'état de l'API"""
        test_name = "API Health Check"
        start_time = time.time()
        
        try:
            # Test endpoints de base
            endpoints = [
                "/api/v1/health",
                "/api/v2/maps/health", 
                "/api/v1/integration/health"
            ]
            
            all_healthy = True
            health_data = {}
            
            for endpoint in endpoints:
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    if response.status != 200:
                        all_healthy = False
                    health_data[endpoint] = {
                        "status": response.status,
                        "response": await response.json() if response.content_type == 'application/json' else await response.text()
                    }
            
            duration = (time.time() - start_time) * 1000
            
            return TestResult(
                test_name=test_name,
                success=all_healthy,
                duration_ms=duration,
                data=health_data,
                error=None if all_healthy else "Some endpoints are not healthy"
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name=test_name,
                success=False,
                duration_ms=duration,
                error=str(e)
            )
    
    async def test_cv_parsing_flow(self) -> TestResult:
        """Test 2: Flux de parsing CV via Bridge Commitment-"""
        test_name = "CV Parsing Flow"
        start_time = time.time()
        
        try:
            # Simulation d'un CV via le bridge
            cv_data = {
                "candidate_info": self.sample_candidates[0],
                "cv_content": f"""
                CV - {self.sample_candidates[0]['name']}
                
                EXPÉRIENCE PROFESSIONNELLE
                {self.sample_candidates[0]['experience']}
                
                COMPÉTENCES
                {', '.join(self.sample_candidates[0]['skills'])}
                
                PRÉTENTIONS SALARIALES
                {self.sample_candidates[0]['salary_expectation']}€ brut/an
                """
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v2/conversion/commitment/enhanced",
                json=cv_data
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"CV parsing failed: {response.status} - {error_text}")
                
                parsed_data = await response.json()
                
                # Validation des données parsées
                required_fields = ['candidate_profile', 'skills_extracted', 'location_detected']
                missing_fields = [field for field in required_fields if field not in parsed_data]
                
                if missing_fields:
                    raise Exception(f"Missing required fields: {missing_fields}")
                
                duration = (time.time() - start_time) * 1000
                
                return TestResult(
                    test_name=test_name,
                    success=True,
                    duration_ms=duration,
                    data=parsed_data,
                    warnings=[] if not missing_fields else [f"Missing fields: {missing_fields}"]
                )
                
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name=test_name,
                success=False,
                duration_ms=duration,
                error=str(e)
            )
    
    async def test_geocoding_flow(self) -> TestResult:
        """Test 3: Géocodage Google Maps"""
        test_name = "Google Maps Geocoding"
        start_time = time.time()
        
        try:
            test_locations = [
                "Paris 8ème",
                "Lyon 3ème", 
                "Marseille",
                "La Défense, Paris"
            ]
            
            geocoding_results = {}
            all_success = True
            
            for location in test_locations:
                async with self.session.post(
                    f"{self.base_url}/api/v2/maps/geocode",
                    json={"address": location}
                ) as response:
                    
                    if response.status != 200:
                        all_success = False
                        geocoding_results[location] = {"error": f"Status {response.status}"}
                    else:
                        result = await response.json()
                        geocoding_results[location] = result
                        
                        # Validation des coordonnées
                        if 'lat' not in result or 'lng' not in result:
                            all_success = False
                            geocoding_results[location]['validation_error'] = "Missing coordinates"
            
            duration = (time.time() - start_time) * 1000
            
            return TestResult(
                test_name=test_name,
                success=all_success,
                duration_ms=duration,
                data=geocoding_results,
                error=None if all_success else "Some geocoding requests failed"
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name=test_name,
                success=False,
                duration_ms=duration,
                error=str(e)
            )
    
    async def test_transport_intelligence(self) -> TestResult:
        """Test 4: Transport Intelligence"""
        test_name = "Transport Intelligence"
        start_time = time.time()
        
        try:
            # Test de compatibilité transport entre candidat et job
            transport_data = {
                "candidate_location": "Paris 8ème",
                "job_location": "Paris 15ème",
                "transport_preferences": ["metro", "bus", "walking"],
                "max_commute_time": 45
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v2/transport/compatibility",
                json=transport_data
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Transport compatibility failed: {response.status} - {error_text}")
                
                transport_result = await response.json()
                
                # Validation des résultats transport
                required_fields = ['commute_time', 'transport_score', 'route_options']
                missing_fields = [field for field in required_fields if field not in transport_result]
                
                duration = (time.time() - start_time) * 1000
                
                return TestResult(
                    test_name=test_name,
                    success=len(missing_fields) == 0,
                    duration_ms=duration,
                    data=transport_result,
                    error=None if not missing_fields else f"Missing fields: {missing_fields}",
                    warnings=[] if not missing_fields else [f"Transport data incomplete"]
                )
                
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name=test_name,
                success=False,
                duration_ms=duration,
                error=str(e)
            )
    
    async def test_complete_matching_flow(self) -> TestResult:
        """Test 5: Flux de matching complet avec V3.2.1"""
        test_name = "Complete Matching V3.2.1"
        start_time = time.time()
        
        try:
            # Test du matching complet avec Charlotte DARMON vs Comptable Général
            candidate = self.sample_candidates[0]  # Charlotte DARMON (DAF, 15 ans)
            job = self.sample_jobs[0]  # Comptable Général (2-5 ans)
            
            matching_data = {
                "candidate": candidate,
                "job": job,
                "matching_config": {
                    "weights": {
                        "semantic": 0.30,
                        "hierarchical": 0.15,
                        "salary": 0.20,
                        "experience": 0.20,
                        "location": 0.15,
                        "sector": 0.05
                    },
                    "enable_hierarchical_detection": True
                }
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/matching/enhanced",
                json=matching_data
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Matching failed: {response.status} - {error_text}")
                
                matching_result = await response.json()
                
                # Validation spécifique au cas Charlotte DARMON
                expected_rejection = matching_result.get('overall_score', 1.0) < 0.6
                has_hierarchical_alert = any(
                    alert.get('type') == 'CRITICAL_MISMATCH' 
                    for alert in matching_result.get('alerts', [])
                )
                
                success = expected_rejection and has_hierarchical_alert
                
                duration = (time.time() - start_time) * 1000
                
                return TestResult(
                    test_name=test_name,
                    success=success,
                    duration_ms=duration,
                    data=matching_result,
                    error=None if success else "Charlotte DARMON should be rejected with hierarchical alert",
                    warnings=[] if success else ["Hierarchical system may not be working correctly"]
                )
                
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name=test_name,
                success=False,
                duration_ms=duration,
                error=str(e)
            )
    
    async def test_stress_performance(self) -> TestResult:
        """Test 6: Test de charge et performance"""
        test_name = "Stress Test Performance"
        start_time = time.time()
        
        try:
            # Préparation des requêtes simultanées
            tasks = []
            num_requests = self.test_configs['stress_test_users']
            
            for i in range(num_requests):
                candidate = self.sample_candidates[i % len(self.sample_candidates)]
                job = self.sample_jobs[i % len(self.sample_jobs)]
                
                task = self._single_matching_request(candidate, job, i)
                tasks.append(task)
            
            # Exécution des requêtes simultanées
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Analyse des résultats
            successful_requests = [r for r in results if isinstance(r, dict) and r.get('success')]
            failed_requests = [r for r in results if not isinstance(r, dict) or not r.get('success')]
            
            response_times = [r.get('duration_ms', 0) for r in successful_requests]
            
            performance_metrics = PerformanceMetrics(
                avg_response_time=statistics.mean(response_times) if response_times else 0,
                max_response_time=max(response_times) if response_times else 0,
                min_response_time=min(response_times) if response_times else 0,
                success_rate=len(successful_requests) / num_requests,
                total_requests=num_requests,
                errors=[str(r) for r in failed_requests]
            )
            
            # Critères de succès
            success = (
                performance_metrics.success_rate >= 0.95 and 
                performance_metrics.avg_response_time <= self.test_configs['performance_threshold_ms']
            )
            
            duration = (time.time() - start_time) * 1000
            
            return TestResult(
                test_name=test_name,
                success=success,
                duration_ms=duration,
                data=performance_metrics.__dict__,
                error=None if success else f"Performance below threshold: {performance_metrics.avg_response_time:.1f}ms avg, {performance_metrics.success_rate:.1%} success rate"
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name=test_name,
                success=False,
                duration_ms=duration,
                error=str(e)
            )
    
    async def _single_matching_request(self, candidate: Dict, job: Dict, request_id: int) -> Dict:
        """Requête de matching individuelle pour le test de charge"""
        request_start = time.time()
        
        try:
            matching_data = {
                "candidate": candidate,
                "job": job,
                "request_id": request_id
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/matching/enhanced",
                json=matching_data
            ) as response:
                
                duration_ms = (time.time() - request_start) * 1000
                
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "duration_ms": duration_ms,
                        "request_id": request_id,
                        "score": result.get('overall_score', 0)
                    }
                else:
                    return {
                        "success": False,
                        "duration_ms": duration_ms,
                        "request_id": request_id,
                        "error": f"HTTP {response.status}"
                    }
                    
        except Exception as e:
            duration_ms = (time.time() - request_start) * 1000
            return {
                "success": False,
                "duration_ms": duration_ms,
                "request_id": request_id,
                "error": str(e)
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Exécute tous les tests end-to-end"""
        logger.info("🚀 Démarrage des tests end-to-end Nextvision V3.2.1")
        self.start_time = time.time()
        
        # Liste des tests à exécuter
        tests = [
            self.test_api_health,
            self.test_cv_parsing_flow,
            self.test_geocoding_flow,
            self.test_transport_intelligence,
            self.test_complete_matching_flow,
            self.test_stress_performance
        ]
        
        # Exécution séquentielle des tests
        for test_func in tests:
            logger.info(f"🧪 Exécution: {test_func.__name__}")
            try:
                result = await test_func()
                self.results.append(result)
                
                status = "✅ PASS" if result.success else "❌ FAIL"
                logger.info(f"{status} {result.test_name} ({result.duration_ms:.1f}ms)")
                
                if not result.success:
                    logger.error(f"   Error: {result.error}")
                if result.warnings:
                    for warning in result.warnings:
                        logger.warning(f"   Warning: {warning}")
                        
            except Exception as e:
                logger.error(f"❌ CRASH {test_func.__name__}: {str(e)}")
                self.results.append(TestResult(
                    test_name=test_func.__name__,
                    success=False,
                    duration_ms=0,
                    error=f"Test crashed: {str(e)}"
                ))
        
        return self._generate_final_report()
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """Génère le rapport final des tests"""
        total_duration = time.time() - self.start_time if self.start_time else 0
        
        successful_tests = [r for r in self.results if r.success]
        failed_tests = [r for r in self.results if not r.success]
        
        report = {
            "summary": {
                "total_tests": len(self.results),
                "successful_tests": len(successful_tests),
                "failed_tests": len(failed_tests),
                "success_rate": len(successful_tests) / len(self.results) if self.results else 0,
                "total_duration_seconds": total_duration,
                "timestamp": datetime.now().isoformat()
            },
            "test_results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "duration_ms": r.duration_ms,
                    "error": r.error,
                    "warnings": r.warnings,
                    "data_keys": list(r.data.keys()) if r.data else []
                }
                for r in self.results
            ],
            "recommendations": self._generate_recommendations(),
            "detailed_results": {r.test_name: r.data for r in self.results if r.data}
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Génère des recommandations basées sur les résultats"""
        recommendations = []
        
        failed_tests = [r for r in self.results if not r.success]
        
        if not failed_tests:
            recommendations.append("🎉 Tous les tests sont passés ! Le système est prêt pour la production.")
        else:
            recommendations.append(f"⚠️ {len(failed_tests)} test(s) ont échoué. Investigation requise.")
            
            for test in failed_tests:
                if "API Health" in test.test_name:
                    recommendations.append("🔧 Vérifier que l'API Nextvision est démarrée et accessible")
                elif "CV Parsing" in test.test_name:
                    recommendations.append("🔧 Vérifier la configuration du Bridge Commitment-")
                elif "Geocoding" in test.test_name:
                    recommendations.append("🔧 Vérifier la clé API Google Maps")
                elif "Transport" in test.test_name:
                    recommendations.append("🔧 Vérifier le module Transport Intelligence")
                elif "Matching" in test.test_name:
                    recommendations.append("🔧 Vérifier le système hiérarchique V3.2.1")
                elif "Stress" in test.test_name:
                    recommendations.append("🔧 Optimiser les performances ou augmenter les ressources")
        
        # Recommandations sur les performances
        performance_tests = [r for r in self.results if "performance" in r.test_name.lower() and r.data]
        for test in performance_tests:
            if test.data.get('avg_response_time', 0) > 1000:
                recommendations.append("⚡ Performances dégradées détectées. Optimisation recommandée.")
        
        return recommendations


async def main():
    """Fonction principale pour exécuter les tests"""
    print("🎯 NEXTVISION V3.2.1 - TESTS END-TO-END")
    print("=" * 50)
    
    async with NextvisionE2ETestSuite() as test_suite:
        report = await test_suite.run_all_tests()
        
        # Affichage du rapport final
        print("\n" + "=" * 50)
        print("📊 RAPPORT FINAL")
        print("=" * 50)
        
        summary = report['summary']
        print(f"Tests exécutés: {summary['total_tests']}")
        print(f"Succès: {summary['successful_tests']}")
        print(f"Échecs: {summary['failed_tests']}")
        print(f"Taux de réussite: {summary['success_rate']:.1%}")
        print(f"Durée totale: {summary['total_duration_seconds']:.1f}s")
        
        print("\n📋 RECOMMANDATIONS:")
        for rec in report['recommendations']:
            print(f"  {rec}")
        
        # Sauvegarde du rapport
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"nextvision_e2e_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Rapport détaillé sauvegardé: {report_file}")
        
        # Code de sortie
        exit_code = 0 if summary['failed_tests'] == 0 else 1
        print(f"\n🎯 Tests terminés avec le code: {exit_code}")
        
        return exit_code


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrompus par l'utilisateur")
        exit(2)
    except Exception as e:
        print(f"\n❌ Erreur critique: {str(e)}")
        traceback.print_exc()
        exit(3)
