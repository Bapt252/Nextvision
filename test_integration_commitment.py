#!/usr/bin/env python3
"""
🌐 NEXTVISION V3.2.1 - TEST INTÉGRATION FRONTEND COMMITMENT-

Validation de l'intégration complète :
- Frontend Commitment- (parseurs GPT)
- Bridge API Nextvision
- Flux end-to-end réel
- Tests avec fichiers réels
- Validation UX complète

Version: 3.2.1
Date: 2025-07-11
Auteur: Assistant Claude
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import base64
import io

@dataclass
class IntegrationTestResult:
    """Résultat d'un test d'intégration"""
    test_name: str
    success: bool
    duration_ms: float
    frontend_url: str
    backend_response: Dict
    error: Optional[str] = None
    user_journey_step: str = ""

class CommitmentIntegrationTester:
    """Testeur d'intégration Commitment- ↔ Nextvision"""
    
    def __init__(self):
        self.nextvision_url = "http://localhost:8001"
        self.commitment_urls = {
            "cv_parser": "https://bapt252.github.io/Commitment-/templates/candidate-upload.html",
            "job_parser": "https://bapt252.github.io/Commitment-/templates/client-questionnaire.html"
        }
        self.results: List[IntegrationTestResult] = []
        
        # Données de test réalistes
        self.test_cv_content = """
        CHARLOTTE DARMON
        Directrice Administrative et Financière
        
        EXPÉRIENCE PROFESSIONNELLE
        
        2018 - Présent : DAF - Société INNOV (Paris 8ème)
        • Direction de l'équipe comptable et financière (12 personnes)
        • Pilotage budgétaire et contrôle de gestion
        • Reporting consolidé mensuel
        • Relations bancaires et investisseurs
        
        2015 - 2018 : Directrice Comptable - Groupe TECH (La Défense)
        • Management équipe de 8 comptables
        • Clôtures mensuelles et consolidation
        • Audit et contrôle interne
        
        2012 - 2015 : Chef Comptable Senior - Cabinet AUDIT+ (Paris 9ème)
        • Supervision missions d'audit
        • Formation équipes juniors
        • Client portfolio management
        
        FORMATION
        • Master CCA - Université Paris Dauphine (2012)
        • DSCG - 2011
        
        COMPÉTENCES
        • Direction d'équipe et management
        • Consolidation et reporting
        • Contrôle de gestion et budgets
        • Relations bancaires
        • SAP, Sage, Excel avancé
        
        PRÉTENTIONS SALARIALES
        80 000€ brut annuel + variable
        
        LOCALISATION
        Paris 8ème - Mobilité Île-de-France
        """
        
        self.test_job_content = {
            "company": "PME Innovante",
            "position": "Comptable Général",
            "location": "Paris 15ème",
            "description": """
            Nous recherchons un Comptable Général pour rejoindre notre équipe.
            
            MISSIONS :
            • Tenue de la comptabilité générale
            • Préparation des déclarations fiscales  
            • Suivi de la trésorerie
            • Relations avec l'expert-comptable
            • Participation aux clôtures mensuelles
            
            PROFIL RECHERCHÉ :
            • Formation comptable (BTS/DUT)
            • 2 à 5 ans d'expérience en comptabilité
            • Maîtrise Sage et Excel
            • Autonomie et rigueur
            • Esprit d'équipe
            
            RÉMUNÉRATION :
            32 000€ à 38 000€ selon expérience
            
            TYPE DE CONTRAT :
            CDI - 35h/semaine
            """,
            "required_experience": "2-5 ans",
            "salary_min": 32000,
            "salary_max": 38000,
            "contract_type": "CDI",
            "required_skills": ["Comptabilité", "Sage", "Excel", "Fiscalité"],
            "level": "JUNIOR"
        }
    
    async def test_cv_parsing_integration(self) -> IntegrationTestResult:
        """Test l'intégration du parsing CV"""
        test_name = "CV Parsing Integration"
        start_time = time.time()
        
        try:
            # Simulation de l'envoi depuis le frontend Commitment-
            cv_payload = {
                "cv_text": self.test_cv_content,
                "candidate_name": "Charlotte DARMON",
                "source": "commitment_frontend",
                "timestamp": datetime.now().isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.nextvision_url}/api/v2/conversion/commitment/enhanced",
                    json=cv_payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    duration_ms = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        backend_response = await response.json()
                        
                        # Validation des données parsées
                        required_fields = [
                            'candidate_profile',
                            'skills_extracted', 
                            'experience_level',
                            'salary_expectation',
                            'location_detected'
                        ]
                        
                        missing_fields = [
                            field for field in required_fields 
                            if field not in backend_response
                        ]
                        
                        # Validation spécifique Charlotte DARMON
                        profile = backend_response.get('candidate_profile', {})
                        charlotte_validations = [
                            profile.get('experience_years', 0) >= 10,  # 15 ans d'expérience
                            'DAF' in str(profile.get('title', '')).upper(),
                            profile.get('level') == 'EXECUTIVE',
                            backend_response.get('salary_expectation', 0) >= 70000
                        ]
                        
                        success = (
                            len(missing_fields) == 0 and 
                            all(charlotte_validations)
                        )
                        
                        return IntegrationTestResult(
                            test_name=test_name,
                            success=success,
                            duration_ms=duration_ms,
                            frontend_url=self.commitment_urls["cv_parser"],
                            backend_response=backend_response,
                            user_journey_step="CV Upload → Parse → Profile Creation",
                            error=None if success else f"Missing fields: {missing_fields} or validation failed"
                        )
                    
                    else:
                        error_text = await response.text()
                        return IntegrationTestResult(
                            test_name=test_name,
                            success=False,
                            duration_ms=duration_ms,
                            frontend_url=self.commitment_urls["cv_parser"],
                            backend_response={},
                            error=f"HTTP {response.status}: {error_text}"
                        )
                        
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return IntegrationTestResult(
                test_name=test_name,
                success=False,
                duration_ms=duration_ms,
                frontend_url=self.commitment_urls["cv_parser"],
                backend_response={},
                error=str(e)
            )
    
    async def test_job_parsing_integration(self) -> IntegrationTestResult:
        """Test l'intégration du parsing fiche de poste"""
        test_name = "Job Parsing Integration"
        start_time = time.time()
        
        try:
            # Simulation de l'envoi depuis le frontend Commitment-
            job_payload = {
                "job_data": self.test_job_content,
                "source": "commitment_frontend",
                "timestamp": datetime.now().isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.nextvision_url}/api/v2/conversion/commitment/job",
                    json=job_payload,
                    timeout=aiohttp.ClientTimeout(total=20)
                ) as response:
                    
                    duration_ms = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        backend_response = await response.json()
                        
                        # Validation des données parsées
                        required_fields = [
                            'job_profile',
                            'required_skills',
                            'experience_required',
                            'salary_range',
                            'location'
                        ]
                        
                        missing_fields = [
                            field for field in required_fields 
                            if field not in backend_response
                        ]
                        
                        # Validation spécifique du job
                        job_profile = backend_response.get('job_profile', {})
                        job_validations = [
                            'comptable' in str(job_profile.get('title', '')).lower(),
                            job_profile.get('level') == 'JUNIOR',
                            backend_response.get('salary_range', {}).get('min', 0) >= 30000,
                            len(backend_response.get('required_skills', [])) >= 3
                        ]
                        
                        success = (
                            len(missing_fields) == 0 and 
                            all(job_validations)
                        )
                        
                        return IntegrationTestResult(
                            test_name=test_name,
                            success=success,
                            duration_ms=duration_ms,
                            frontend_url=self.commitment_urls["job_parser"],
                            backend_response=backend_response,
                            user_journey_step="Job Description → Parse → Requirements",
                            error=None if success else f"Missing fields: {missing_fields} or validation failed"
                        )
                    
                    else:
                        error_text = await response.text()
                        return IntegrationTestResult(
                            test_name=test_name,
                            success=False,
                            duration_ms=duration_ms,
                            frontend_url=self.commitment_urls["job_parser"],
                            backend_response={},
                            error=f"HTTP {response.status}: {error_text}"
                        )
                        
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return IntegrationTestResult(
                test_name=test_name,
                success=False,
                duration_ms=duration_ms,
                frontend_url=self.commitment_urls["job_parser"],
                backend_response={},
                error=str(e)
            )
    
    async def test_complete_matching_flow(self) -> IntegrationTestResult:
        """Test le flux complet de matching"""
        test_name = "Complete Matching Flow"
        start_time = time.time()
        
        try:
            # 1. Parser le CV (Charlotte DARMON)
            cv_result = await self.test_cv_parsing_integration()
            if not cv_result.success:
                raise Exception(f"CV parsing failed: {cv_result.error}")
            
            # 2. Parser le job (Comptable Général)
            job_result = await self.test_job_parsing_integration()
            if not job_result.success:
                raise Exception(f"Job parsing failed: {job_result.error}")
            
            # 3. Lancer le matching
            matching_payload = {
                "candidate": cv_result.backend_response.get('candidate_profile'),
                "job": job_result.backend_response.get('job_profile'),
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
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.nextvision_url}/api/v1/matching/enhanced",
                    json=matching_payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    duration_ms = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        matching_result = await response.json()
                        
                        # Validation du cas Charlotte DARMON
                        # Elle DOIT être rejetée (score < 0.6) avec une alerte hiérarchique
                        overall_score = matching_result.get('overall_score', 1.0)
                        alerts = matching_result.get('alerts', [])
                        
                        hierarchical_alert = any(
                            alert.get('type') == 'CRITICAL_MISMATCH' 
                            for alert in alerts
                        )
                        
                        # Critères de succès
                        success_criteria = [
                            overall_score < 0.6,  # Charlotte doit être rejetée
                            hierarchical_alert,   # Alerte hiérarchique obligatoire
                            'scores_detail' in matching_result,  # Détails disponibles
                        ]
                        
                        success = all(success_criteria)
                        
                        # Enrichir la réponse avec des métriques
                        enhanced_response = {
                            **matching_result,
                            "integration_metrics": {
                                "cv_parsing_duration": cv_result.duration_ms,
                                "job_parsing_duration": job_result.duration_ms,
                                "total_flow_duration": duration_ms,
                                "hierarchical_detection_working": hierarchical_alert,
                                "charlotte_darmon_correctly_rejected": overall_score < 0.6
                            }
                        }
                        
                        return IntegrationTestResult(
                            test_name=test_name,
                            success=success,
                            duration_ms=duration_ms,
                            frontend_url="Full Integration Flow",
                            backend_response=enhanced_response,
                            user_journey_step="CV Upload → Job Create → Matching → Results",
                            error=None if success else f"Charlotte DARMON not properly rejected: score={overall_score:.3f}, hierarchical_alert={hierarchical_alert}"
                        )
                    
                    else:
                        error_text = await response.text()
                        return IntegrationTestResult(
                            test_name=test_name,
                            success=False,
                            duration_ms=duration_ms,
                            frontend_url="Full Integration Flow",
                            backend_response={},
                            error=f"Matching API error: HTTP {response.status}: {error_text}"
                        )
                        
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return IntegrationTestResult(
                test_name=test_name,
                success=False,
                duration_ms=duration_ms,
                frontend_url="Full Integration Flow",
                backend_response={},
                error=str(e)
            )
    
    async def test_frontend_accessibility(self) -> IntegrationTestResult:
        """Test l'accessibilité des frontends Commitment-"""
        test_name = "Frontend Accessibility"
        start_time = time.time()
        
        try:
            frontend_results = {}
            
            async with aiohttp.ClientSession() as session:
                for name, url in self.commitment_urls.items():
                    try:
                        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                            frontend_results[name] = {
                                "url": url,
                                "status": response.status,
                                "accessible": response.status == 200,
                                "content_length": len(await response.text()) if response.status == 200 else 0
                            }
                    except Exception as e:
                        frontend_results[name] = {
                            "url": url,
                            "status": 0,
                            "accessible": False,
                            "error": str(e)
                        }
            
            # Validation
            accessible_frontends = sum(1 for result in frontend_results.values() if result.get('accessible', False))
            success = accessible_frontends >= len(self.commitment_urls) / 2  # Au moins 50% accessibles
            
            duration_ms = (time.time() - start_time) * 1000
            
            return IntegrationTestResult(
                test_name=test_name,
                success=success,
                duration_ms=duration_ms,
                frontend_url="Multiple URLs",
                backend_response=frontend_results,
                user_journey_step="Frontend Access Validation",
                error=None if success else f"Only {accessible_frontends}/{len(self.commitment_urls)} frontends accessible"
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return IntegrationTestResult(
                test_name=test_name,
                success=False,
                duration_ms=duration_ms,
                frontend_url="Multiple URLs",
                backend_response={},
                error=str(e)
            )
    
    async def run_all_integration_tests(self) -> Dict[str, Any]:
        """Lance tous les tests d'intégration"""
        print("🌐 TESTS D'INTÉGRATION COMMITMENT- ↔ NEXTVISION V3.2.1")
        print("=" * 60)
        
        # Liste des tests d'intégration
        tests = [
            ("Frontend Accessibility", self.test_frontend_accessibility),
            ("CV Parsing Integration", self.test_cv_parsing_integration),
            ("Job Parsing Integration", self.test_job_parsing_integration),
            ("Complete Matching Flow", self.test_complete_matching_flow)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🧪 Exécution: {test_name}")
            print("-" * 40)
            
            try:
                result = await test_func()
                self.results.append(result)
                
                status = "✅ PASS" if result.success else "❌ FAIL"
                print(f"{status} {result.test_name} ({result.duration_ms:.1f}ms)")
                
                if result.user_journey_step:
                    print(f"   Journey: {result.user_journey_step}")
                
                if not result.success:
                    print(f"   Error: {result.error}")
                
                # Affichage des détails critiques
                if result.test_name == "Complete Matching Flow" and result.backend_response:
                    metrics = result.backend_response.get('integration_metrics', {})
                    score = result.backend_response.get('overall_score', 0)
                    print(f"   Charlotte DARMON Score: {score:.3f}")
                    print(f"   Hierarchical Detection: {'✅' if metrics.get('hierarchical_detection_working') else '❌'}")
                    print(f"   Correctly Rejected: {'✅' if metrics.get('charlotte_darmon_correctly_rejected') else '❌'}")
                
            except Exception as e:
                print(f"❌ CRASH {test_name}: {str(e)}")
                self.results.append(IntegrationTestResult(
                    test_name=test_name,
                    success=False,
                    duration_ms=0,
                    frontend_url="",
                    backend_response={},
                    error=f"Test crashed: {str(e)}"
                ))
        
        return self._generate_integration_report()
    
    def _generate_integration_report(self) -> Dict[str, Any]:
        """Génère le rapport d'intégration"""
        successful_tests = [r for r in self.results if r.success]
        failed_tests = [r for r in self.results if not r.success]
        
        # Métriques spéciales pour Charlotte DARMON
        charlotte_test = next(
            (r for r in self.results if r.test_name == "Complete Matching Flow"),
            None
        )
        
        charlotte_metrics = {}
        if charlotte_test and charlotte_test.backend_response:
            metrics = charlotte_test.backend_response.get('integration_metrics', {})
            charlotte_metrics = {
                "test_executed": True,
                "correctly_rejected": metrics.get('charlotte_darmon_correctly_rejected', False),
                "hierarchical_alert_triggered": metrics.get('hierarchical_detection_working', False),
                "overall_score": charlotte_test.backend_response.get('overall_score', 0),
                "total_flow_duration_ms": metrics.get('total_flow_duration', 0)
            }
        
        report = {
            "summary": {
                "total_tests": len(self.results),
                "successful_tests": len(successful_tests),
                "failed_tests": len(failed_tests),
                "success_rate": len(successful_tests) / len(self.results) if self.results else 0,
                "integration_ready": len(successful_tests) >= 3,  # Au moins 3/4 tests réussis
                "timestamp": datetime.now().isoformat()
            },
            "charlotte_darmon_validation": charlotte_metrics,
            "frontend_status": {
                url_name: {
                    "accessible": any(
                        r.backend_response.get(url_name, {}).get('accessible', False)
                        for r in self.results if r.test_name == "Frontend Accessibility"
                    ),
                    "url": url
                }
                for url_name, url in self.commitment_urls.items()
            },
            "test_results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "duration_ms": r.duration_ms,
                    "user_journey": r.user_journey_step,
                    "error": r.error
                }
                for r in self.results
            ],
            "recommendations": self._generate_integration_recommendations()
        }
        
        return report
    
    def _generate_integration_recommendations(self) -> List[str]:
        """Génère les recommandations d'intégration"""
        recommendations = []
        
        failed_tests = [r for r in self.results if not r.success]
        
        if not failed_tests:
            recommendations.extend([
                "🎉 Intégration Commitment- ↔ Nextvision parfaitement fonctionnelle",
                "✅ Le système hiérarchique fonctionne correctement",
                "✅ Charlotte DARMON est bien rejetée automatiquement",
                "🚀 Prêt pour la mise en production"
            ])
        else:
            for test in failed_tests:
                if "Frontend Accessibility" in test.test_name:
                    recommendations.append("🔧 Vérifier la disponibilité des frontends Commitment-")
                elif "CV Parsing" in test.test_name:
                    recommendations.append("🔧 Corriger l'intégration du parsing CV")
                elif "Job Parsing" in test.test_name:
                    recommendations.append("🔧 Corriger l'intégration du parsing Job")
                elif "Complete Matching Flow" in test.test_name:
                    recommendations.append("🔧 Corriger le flux de matching intégré")
        
        # Recommandations spécifiques Charlotte DARMON
        charlotte_test = next(
            (r for r in self.results if r.test_name == "Complete Matching Flow"),
            None
        )
        
        if charlotte_test:
            if charlotte_test.success:
                recommendations.append("✅ Cas Charlotte DARMON validé - Protection hiérarchique active")
            else:
                recommendations.append("⚠️ Cas Charlotte DARMON à corriger - Risque de matching inapproprié")
        
        return recommendations


async def main():
    """Fonction principale"""
    print("🌐 NEXTVISION V3.2.1 - TEST INTÉGRATION FRONTEND")
    print("=" * 60)
    print("Validation de l'intégration Commitment- ↔ Nextvision")
    print("Test du parcours utilisateur complet")
    print("=" * 60)
    print()
    
    tester = CommitmentIntegrationTester()
    report = await tester.run_all_integration_tests()
    
    # Affichage du rapport final
    print("\n" + "=" * 60)
    print("📊 RAPPORT D'INTÉGRATION")
    print("=" * 60)
    
    summary = report['summary']
    print(f"Tests exécutés: {summary['total_tests']}")
    print(f"Succès: {summary['successful_tests']}")
    print(f"Échecs: {summary['failed_tests']}")
    print(f"Taux de réussite: {summary['success_rate']:.1%}")
    print(f"Intégration prête: {'✅ OUI' if summary['integration_ready'] else '❌ NON'}")
    
    # Status Charlotte DARMON
    charlotte = report['charlotte_darmon_validation']
    if charlotte.get('test_executed'):
        print(f"\n🎯 VALIDATION CHARLOTTE DARMON:")
        print(f"Score obtenu: {charlotte.get('overall_score', 0):.3f}")
        print(f"Correctement rejetée: {'✅' if charlotte.get('correctly_rejected') else '❌'}")
        print(f"Alerte hiérarchique: {'✅' if charlotte.get('hierarchical_alert_triggered') else '❌'}")
    
    print("\n📋 RECOMMANDATIONS:")
    for rec in report['recommendations']:
        print(f"  {rec}")
    
    # Sauvegarde du rapport
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"integration_commitment_nextvision_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Rapport détaillé sauvegardé: {report_file}")
    
    # Code de sortie
    exit_code = 0 if summary['integration_ready'] else 1
    print(f"\n🎯 Tests d'intégration terminés avec le code: {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Tests d'intégration interrompus")
        exit(2)
    except Exception as e:
        print(f"\n❌ Erreur critique: {str(e)}")
        exit(3)
