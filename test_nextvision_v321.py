#!/usr/bin/env python3
"""
🧪 SCRIPT DE TEST AUTOMATISÉ - NEXTVISION v3.2.1
================================================

VALIDATION RÉVOLUTION ARCHITECTURE : Tests automatisés complets
- Endpoint Intelligent v3 : Workflow unifié opérationnel
- Adaptateur Intelligent : Transformations format automatiques
- Performance : < 2000ms validation
- Architecture : Tous composants fonctionnels

Author: NEXTEN Team
Version: 3.2.1
Innovation: Tests complets workflow révolutionnaire
"""

import asyncio
import aiohttp
import json
import time
import tempfile
import os
import sys
from pathlib import Path
import logging
from typing import Dict, Any, List

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NextvisionV3Tester:
    """
    🧪 TESTEUR AUTOMATISÉ NEXTVISION v3.2.1
    ========================================
    
    **Mission** : Valider automatiquement toutes les innovations v3.2.1
    
    **Tests** :
    - ✅ API Health Checks complets
    - ✅ Endpoint Intelligent v3 fonctionnel 
    - ✅ Adaptateur Intelligent opérationnel
    - ✅ Workflow unifié automatique
    - ✅ Performance < 2000ms
    - ✅ Transport Intelligence intégré
    
    **Résultat** : Validation complète révolution architecture
    """
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "performance_tests": [],
            "details": []
        }
        
    async def run_complete_tests(self) -> Dict[str, Any]:
        """🚀 Lance tous les tests automatisés"""
        
        logger.info("🧪 === DÉMARRAGE TESTS NEXTVISION v3.2.1 ===")
        start_time = time.time()
        
        # Créer session HTTP
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # === SUITE DE TESTS COMPLÈTE ===
            await self._test_api_health()
            await self._test_v3_endpoints()
            await self._test_intelligent_workflow()
            await self._test_adaptateur_direct()
            await self._test_performance_targets()
            await self._test_integration_complete()
            
        # Calcul résultats finaux
        total_time = time.time() - start_time
        success_rate = (self.test_results["passed"] / max(1, self.test_results["total_tests"])) * 100
        
        final_report = {
            "status": "success" if success_rate >= 80 else "partial" if success_rate >= 60 else "failed",
            "summary": {
                "total_tests": self.test_results["total_tests"],
                "passed": self.test_results["passed"],
                "failed": self.test_results["failed"],
                "success_rate": round(success_rate, 1),
                "test_duration_seconds": round(total_time, 2)
            },
            "performance": {
                "tests_completed": len(self.test_results["performance_tests"]),
                "average_response_time": self._calculate_avg_performance(),
                "target_2000ms_achieved": all(t["time_ms"] < 2000 for t in self.test_results["performance_tests"])
            },
            "architecture_validation": {
                "api_health": any("health" in test["name"] and test["passed"] for test in self.test_results["details"]),
                "endpoint_v3": any("v3" in test["name"] and test["passed"] for test in self.test_results["details"]),
                "workflow_unifie": any("workflow" in test["name"] and test["passed"] for test in self.test_results["details"]),
                "adaptateur_intelligent": any("adaptateur" in test["name"] and test["passed"] for test in self.test_results["details"])
            },
            "detailed_results": self.test_results["details"],
            "recommendations": self._generate_recommendations()
        }
        
        # Affichage résultats
        self._display_results(final_report)
        
        return final_report
    
    async def _test_api_health(self):
        """❤️ Test health checks API"""
        logger.info("🔍 Test API Health Checks...")
        
        health_endpoints = [
            "/api/v1/health",
            "/api/v3/health", 
            "/api/v3/status",
            "/api/v1/integration/health",
            "/api/v2/maps/health"
        ]
        
        for endpoint in health_endpoints:
            await self._test_endpoint_get(
                endpoint=endpoint,
                test_name=f"health_check_{endpoint.split('/')[-1]}",
                expected_status=200,
                required_fields=["status"]
            )
    
    async def _test_v3_endpoints(self):
        """🎯 Test endpoints v3 spécifiques"""
        logger.info("🎯 Test Endpoints v3...")
        
        # Test endpoint principal
        await self._test_endpoint_get(
            endpoint="/",
            test_name="root_endpoint_v3_integration",
            expected_status=200,
            required_fields=["version", "revolutionary_endpoint"]
        )
        
        # Test status détaillé v3
        await self._test_endpoint_get(
            endpoint="/api/v3/status",
            test_name="v3_status_detailed",
            expected_status=200,
            required_fields=["version", "workflow", "services"]
        )
    
    async def _test_intelligent_workflow(self):
        """🚀 Test workflow intelligent unifié"""
        logger.info("🚀 Test Workflow Intelligent...")
        
        # Créer fichiers de test
        cv_content = """John Doe
john.doe@example.com
+33 6 12 34 56 78

COMPÉTENCES:
- Python (5 ans)
- JavaScript (3 ans) 
- FastAPI (2 ans)
- React (2 ans)

EXPÉRIENCE:
2019-2024: Développeur Senior chez TechCorp
- Développement APIs REST
- Architecture microservices
- Management équipe 3 personnes

FORMATION:
2017: Master Informatique, Université Paris-Saclay
"""
        
        job_content = """OFFRE D'EMPLOI: Développeur Full-Stack Senior
ENTREPRISE: InnovTech Solutions
LOCALISATION: Paris 15ème, France
CONTRAT: CDI

COMPÉTENCES REQUISES:
- Python/FastAPI (4+ ans)
- JavaScript/React (3+ ans)
- Architecture API
- Leadership technique

MISSIONS:
- Conception architecture technique
- Développement applications web
- Encadrement équipe développement
- Optimisation performance

SALAIRE: 55k-70k€
TÉLÉTRAVAIL: 3j/semaine
"""
        
        # Test avec fichiers temporaires
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as cv_file:
            cv_file.write(cv_content)
            cv_file_path = cv_file.name
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as job_file:
            job_file.write(job_content)
            job_file_path = job_file.name
        
        try:
            await self._test_intelligent_matching_endpoint(cv_file_path, job_file_path)
        finally:
            # Nettoyage fichiers temporaires
            os.unlink(cv_file_path)
            os.unlink(job_file_path)
    
    async def _test_intelligent_matching_endpoint(self, cv_path: str, job_path: str):
        """🎯 Test endpoint intelligent matching"""
        
        start_time = time.time()
        
        try:
            # Préparer données multipart
            data = aiohttp.FormData()
            
            # Ajouter fichier CV
            with open(cv_path, 'rb') as cv_file:
                data.add_field('cv_file', cv_file, filename='test_cv.txt', content_type='text/plain')
                
                # Ajouter fichier Job
                with open(job_path, 'rb') as job_file:
                    data.add_field('job_file', job_file, filename='test_job.txt', content_type='text/plain')
                    
                    # Ajouter paramètres
                    data.add_field('pourquoi_ecoute', 'Poste trop loin de mon domicile')
                    data.add_field('job_address', 'Paris 15ème, France')
                    
                    # Appel endpoint
                    async with self.session.post(
                        f"{self.base_url}/api/v3/intelligent-matching",
                        data=data
                    ) as response:
                        
                        response_time = (time.time() - start_time) * 1000
                        response_text = await response.text()
                        
                        # Validation réponse
                        if response.status == 200:
                            try:
                                result = json.loads(response_text)
                                
                                # Validation structure réponse
                                required_fields = [
                                    "status", "workflow", "matching_results", 
                                    "candidate_summary", "performance"
                                ]
                                
                                missing_fields = [field for field in required_fields if field not in result]
                                
                                if not missing_fields:
                                    # Test réussi
                                    self._record_test_success(
                                        "intelligent_workflow_complete",
                                        f"Workflow unifié fonctionnel ({response_time:.0f}ms)",
                                        {"response_time": response_time, "result": result}
                                    )
                                    
                                    # Enregistrer performance
                                    self.test_results["performance_tests"].append({
                                        "test": "intelligent_matching",
                                        "time_ms": response_time,
                                        "target_achieved": response_time < 2000
                                    })
                                    
                                else:
                                    self._record_test_failure(
                                        "intelligent_workflow_structure",
                                        f"Champs manquants: {missing_fields}"
                                    )
                            except json.JSONDecodeError as e:
                                self._record_test_failure(
                                    "intelligent_workflow_json",
                                    f"Réponse JSON invalide: {str(e)}"
                                )
                        else:
                            self._record_test_failure(
                                "intelligent_workflow_http",
                                f"Status HTTP {response.status}: {response_text}"
                            )
        
        except Exception as e:
            self._record_test_failure(
                "intelligent_workflow_exception",
                f"Exception: {str(e)}"
            )
    
    async def _test_adaptateur_direct(self):
        """🔄 Test adaptateur intelligent directement"""
        logger.info("🔄 Test Adaptateur Intelligent...")
        
        try:
            # Import et test direct
            sys.path.insert(0, os.getcwd())
            
            from nextvision.adapters.parsing_to_matching_adapter import create_unified_matching_request
            
            # Données de test
            cv_data = {
                "name": "Alice Martin",
                "email": "alice.martin@example.com",
                "phone": "+33 6 12 34 56 78",
                "skills": ["Python", "React", "PostgreSQL", "Docker"],
                "years_of_experience": 4,
                "education": "Master Informatique",
                "location": "Lyon, France"
            }
            
            job_data = {
                "title": "Développeuse Full-Stack",
                "company": "TechStartup",
                "location": "Lyon, France",
                "required_skills": ["Python", "React", "Base de données"],
                "salary_range": {"min": 45000, "max": 55000},
                "contract_type": "CDI"
            }
            
            # Test transformation
            start_time = time.time()
            result = create_unified_matching_request(
                cv_data=cv_data,
                job_data=job_data,
                pourquoi_ecoute="Rémunération trop faible"
            )
            adaptation_time = (time.time() - start_time) * 1000
            
            # Validation résultat
            if result.success and result.matching_request:
                self._record_test_success(
                    "adaptateur_intelligent_direct",
                    f"Transformation réussie ({adaptation_time:.0f}ms)",
                    {
                        "adaptations_applied": result.adaptations_applied,
                        "processing_time": result.processing_time_ms
                    }
                )
            else:
                self._record_test_failure(
                    "adaptateur_intelligent_validation",
                    f"Erreurs: {result.validation_errors}"
                )
                
        except ImportError as e:
            self._record_test_failure(
                "adaptateur_intelligent_import",
                f"Import failed: {str(e)}"
            )
        except Exception as e:
            self._record_test_failure(
                "adaptateur_intelligent_exception",
                f"Exception: {str(e)}"
            )
    
    async def _test_performance_targets(self):
        """⚡ Test cibles de performance"""
        logger.info("⚡ Test Performance Targets...")
        
        # Test multiple appels pour mesurer performance moyenne
        performance_tests = [
            ("/api/v1/health", "health_performance"),
            ("/api/v3/health", "v3_health_performance"), 
            ("/api/v3/status", "v3_status_performance")
        ]
        
        for endpoint, test_name in performance_tests:
            times = []
            
            # 3 appels pour moyenne
            for i in range(3):
                start_time = time.time()
                
                try:
                    async with self.session.get(f"{self.base_url}{endpoint}") as response:
                        await response.text()
                        response_time = (time.time() - start_time) * 1000
                        times.append(response_time)
                        
                except Exception:
                    times.append(5000)  # Timeout simulé
            
            avg_time = sum(times) / len(times)
            
            # Validation cible performance
            if avg_time < 1000:  # < 1s pour endpoints simples
                self._record_test_success(
                    test_name,
                    f"Performance excellente ({avg_time:.0f}ms moyenne)"
                )
            else:
                self._record_test_failure(
                    test_name,
                    f"Performance lente ({avg_time:.0f}ms moyenne)"
                )
            
            # Enregistrer métrique
            self.test_results["performance_tests"].append({
                "test": test_name,
                "time_ms": avg_time,
                "target_achieved": avg_time < 1000
            })
    
    async def _test_integration_complete(self):
        """🔗 Test intégration complète"""
        logger.info("🔗 Test Intégration Complète...")
        
        # Test cohérence version API
        try:
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Vérifier version 3.2.1
                    if result.get("version") == "3.2.1":
                        self._record_test_success(
                            "integration_version_consistency",
                            "Version 3.2.1 cohérente"
                        )
                    else:
                        self._record_test_failure(
                            "integration_version_mismatch",
                            f"Version incohérente: {result.get('version')}"
                        )
                    
                    # Vérifier endpoint révolutionnaire
                    if "revolutionary_endpoint" in result:
                        endpoint_info = result["revolutionary_endpoint"]
                        if endpoint_info.get("url") == "/api/v3/intelligent-matching":
                            self._record_test_success(
                                "integration_revolutionary_endpoint",
                                "Endpoint révolutionnaire correctement référencé"
                            )
                        else:
                            self._record_test_failure(
                                "integration_endpoint_config",
                                f"URL endpoint incorrecte: {endpoint_info.get('url')}"
                            )
        
        except Exception as e:
            self._record_test_failure(
                "integration_complete_exception",
                f"Exception intégration: {str(e)}"
            )
    
    async def _test_endpoint_get(self, endpoint: str, test_name: str, expected_status: int = 200, required_fields: List[str] = None):
        """🌐 Test endpoint GET générique"""
        
        start_time = time.time()
        
        try:
            async with self.session.get(f"{self.base_url}{endpoint}") as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == expected_status:
                    try:
                        result = await response.json()
                        
                        # Vérifier champs requis
                        if required_fields:
                            missing_fields = [field for field in required_fields if field not in result]
                            
                            if missing_fields:
                                self._record_test_failure(
                                    test_name,
                                    f"Champs manquants: {missing_fields}"
                                )
                                return
                        
                        self._record_test_success(
                            test_name,
                            f"Endpoint fonctionnel ({response_time:.0f}ms)"
                        )
                        
                    except json.JSONDecodeError:
                        self._record_test_failure(
                            test_name,
                            "Réponse JSON invalide"
                        )
                else:
                    response_text = await response.text()
                    self._record_test_failure(
                        test_name,
                        f"Status HTTP {response.status}: {response_text[:200]}"
                    )
        
        except Exception as e:
            self._record_test_failure(
                test_name,
                f"Exception: {str(e)}"
            )
    
    def _record_test_success(self, test_name: str, message: str, details: Dict = None):
        """✅ Enregistrer test réussi"""
        self.test_results["total_tests"] += 1
        self.test_results["passed"] += 1
        self.test_results["details"].append({
            "name": test_name,
            "status": "PASSED",
            "message": message,
            "details": details,
            "passed": True
        })
        logger.info(f"✅ {test_name}: {message}")
    
    def _record_test_failure(self, test_name: str, message: str):
        """❌ Enregistrer test échoué"""
        self.test_results["total_tests"] += 1
        self.test_results["failed"] += 1
        self.test_results["details"].append({
            "name": test_name,
            "status": "FAILED",
            "message": message,
            "passed": False
        })
        logger.error(f"❌ {test_name}: {message}")
    
    def _calculate_avg_performance(self) -> float:
        """📊 Calcule performance moyenne"""
        if not self.test_results["performance_tests"]:
            return 0.0
        
        total_time = sum(test["time_ms"] for test in self.test_results["performance_tests"])
        return round(total_time / len(self.test_results["performance_tests"]), 2)
    
    def _generate_recommendations(self) -> List[str]:
        """💡 Génère recommandations"""
        recommendations = []
        
        success_rate = (self.test_results["passed"] / max(1, self.test_results["total_tests"])) * 100
        
        if success_rate < 80:
            recommendations.append("🔧 Vérifier configuration API et dépendances")
        
        if self.test_results["failed"] > 0:
            recommendations.append("📋 Consulter logs détaillés pour erreurs spécifiques")
        
        avg_performance = self._calculate_avg_performance()
        if avg_performance > 2000:
            recommendations.append("⚡ Optimiser performance - cible < 2000ms non atteinte")
        
        if success_rate >= 90:
            recommendations.append("🚀 Excellent ! Prêt pour production")
        
        return recommendations
    
    def _display_results(self, report: Dict[str, Any]):
        """📊 Affiche résultats de test"""
        
        print("\n" + "="*80)
        print("🧪 RAPPORT DE TEST NEXTVISION v3.2.1")
        print("="*80)
        
        print(f"\n📊 RÉSUMÉ:")
        print(f"   • Tests total: {report['summary']['total_tests']}")
        print(f"   • Tests réussis: {report['summary']['passed']} ✅")
        print(f"   • Tests échoués: {report['summary']['failed']} ❌")
        print(f"   • Taux de succès: {report['summary']['success_rate']}%")
        print(f"   • Durée totale: {report['summary']['test_duration_seconds']}s")
        
        print(f"\n⚡ PERFORMANCE:")
        print(f"   • Tests performance: {report['performance']['tests_completed']}")
        print(f"   • Temps moyen: {report['performance']['average_response_time']}ms")
        print(f"   • Cible < 2000ms: {'✅ ATTEINTE' if report['performance']['target_2000ms_achieved'] else '❌ NON ATTEINTE'}")
        
        print(f"\n🏗️ VALIDATION ARCHITECTURE:")
        for component, status in report['architecture_validation'].items():
            status_icon = "✅" if status else "❌"
            print(f"   • {component}: {status_icon}")
        
        if report['recommendations']:
            print(f"\n💡 RECOMMANDATIONS:")
            for rec in report['recommendations']:
                print(f"   • {rec}")
        
        # Status final
        status_color = {
            "success": "🟢",
            "partial": "🟡", 
            "failed": "🔴"
        }
        
        print(f"\n🎯 STATUT FINAL: {status_color.get(report['status'], '⚪')} {report['status'].upper()}")
        
        if report['status'] == 'success':
            print("\n🚀 RÉVOLUTION NEXTVISION v3.2.1 VALIDÉE AVEC SUCCÈS !")
            print("   Architecture optimisée et workflow unifié opérationnels")
        
        print("="*80)

# === FONCTION PRINCIPALE ===

async def main():
    """🚀 Fonction principale de test"""
    
    print("🧪 === NEXTVISION v3.2.1 TEST AUTOMATISÉ ===")
    print("🎯 Validation complète révolution architecture")
    print("=" * 50)
    
    # Vérifier que l'API est démarrée
    print("\n⚠️  PRÉREQUIS:")
    print("   • API Nextvision doit être démarrée sur http://localhost:8001")
    print("   • Commande: python main.py")
    print("")
    
    response = input("🤔 L'API est-elle démarrée ? (y/N): ")
    if response.lower() != 'y':
        print("❌ Démarrer l'API avant de lancer les tests")
        print("   cd /Users/baptistecomas/Nextvision/")
        print("   source nextvision_env/bin/activate")
        print("   python main.py")
        return
    
    # Lancer tests
    tester = NextvisionV3Tester()
    
    try:
        report = await tester.run_complete_tests()
        
        # Sauvegarder rapport
        report_file = f"test_report_v321_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Rapport sauvegardé: {report_file}")
        
        # Exit code selon résultat
        if report['status'] == 'success':
            sys.exit(0)
        elif report['status'] == 'partial':
            sys.exit(1)
        else:
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n❌ Tests interrompus par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erreur critique lors des tests: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
