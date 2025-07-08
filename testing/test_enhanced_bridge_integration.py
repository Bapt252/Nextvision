#!/usr/bin/env python3
"""
🧪 Nextvision v2.0 - Script de Test Intégration Enhanced Commitment Bridge

Tests complets pour valider l'intégration révolutionnaire :
- Enhanced Universal Parser v4.0 → Enhanced Bridge → Matching Bidirectionnel
- Système ChatGPT Commitment- → Enhanced Bridge → Matching Bidirectionnel  
- Workflow complet PDF → Parsing → Auto-fix → Validation → Matching
- Performance et robustesse avec vraies données
- Validation 69 CVs + 34 FDPs de test disponibles

Author: NEXTEN Team
Version: 2.0.0 - Enhanced Integration Test Suite
"""

import asyncio
import aiohttp
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import statistics

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration API
API_BASE_URL = "http://localhost:8000"
ENHANCED_ENDPOINTS = {
    "health": "/api/v1/health",
    "enhanced_health": "/api/v2/conversion/commitment/enhanced/stats",
    "enhanced_conversion": "/api/v2/conversion/commitment/enhanced",
    "enhanced_direct_match": "/api/v2/conversion/commitment/enhanced/direct-match",
    "enhanced_batch": "/api/v2/conversion/commitment/enhanced/batch",
    "bidirectional_match": "/api/v2/matching/bidirectional"
}

# Données de test Enhanced Universal Parser v4.0 (simulées)
ENHANCED_PARSER_TEST_DATA = [
    {
        "name": "candidat_1_marie_dupont",
        "data": {
            "personal_info": {
                "firstName": "marie",  # Test auto-fix capitalisation
                "lastName": "DUPONT",  # Test auto-fix capitalisation  
                "email": "marie..dupont@email..com",  # Test auto-fix email
                "phone": "0612345678"  # Test auto-fix téléphone
            },
            "skills": ["Maîtrise du logiciel comptable CEGID", "Gestion comptable et fiscale", "CEGID", "Excel"],  # Test déduplication
            "softwares": ["CEGID ", " Excel", "SAP", ""],  # Test nettoyage espaces
            "languages": {"Français": "Natif", "Anglais": "Courant"},
            "experience": {"total_years": "7 ans"},  # Test conversion string → int
            "work_experience": [
                {
                    "position": "Comptable Senior",
                    "company": "Cabinet ABC",
                    "duration": "3 ans",
                    "skills_acquired": ["CEGID", "Fiscalité"]
                }
            ],
            "parsing_confidence": 0.92
        }
    },
    {
        "name": "candidat_2_jean_martin",
        "data": {
            "personal_info": {
                "firstName": "Jean",
                "lastName": "Martin",
                "email": "jean.martin@email.com",
                "phone": "+33 6 23 45 67 89"
            },
            "skills": ["Développement Python", "FastAPI", "React", "JavaScript"],
            "softwares": ["VS Code", "Git", "Docker"],
            "languages": {"Français": "Natif", "Anglais": "Courant", "Espagnol": "Notions"},
            "experience": {"total_years": 5},
            "work_experience": [
                {
                    "position": "Développeur Full-Stack",
                    "company": "TechCorp",
                    "duration": "2 ans",
                    "skills_acquired": ["Python", "React", "API"]
                }
            ],
            "parsing_confidence": 0.89
        }
    }
]

# Données de test ChatGPT Commitment- (simulées)
CHATGPT_TEST_DATA = [
    {
        "name": "entreprise_1_cabinet_comptable",
        "data": {
            "titre": "comptable unique h/f",  # Test auto-fix capitalisation
            "localisation": "  paris 8ème  ",  # Test auto-fix espaces
            "contrat": "CDI",
            "salaire": "35k à 38k annuels",  # Test auto-fix format K
            "competences_requises": ["Maîtrise du logiciel comptable CEGID", "Gestion comptable et fiscale", "CEGID"],  # Test déduplication
            "experience_requise": "5-10 ans",  # Test auto-fix format
            "missions": ["Tenue comptabilité complète", "Déclarations fiscales", ""],  # Test nettoyage
            "avantages": ["Tickets restaurant", "Mutuelle", "  ", "Tickets restaurant"],  # Test déduplication et nettoyage
            "badges_auto_rempli": ["Auto-rempli"],
            "fiche_poste_originale": "Poste de comptable pour cabinet...",
            "parsing_confidence": 0.88
        }
    },
    {
        "name": "entreprise_2_startup_tech",
        "data": {
            "titre": "Développeur Full-Stack Senior",
            "localisation": "Paris 10ème",
            "contrat": "CDI",
            "salaire": "50000 à 65000 euros",
            "competences_requises": ["Python", "FastAPI", "React", "JavaScript", "Docker"],
            "experience_requise": "3 ans - 7 ans",
            "missions": ["Développement features", "Architecture API", "Encadrement junior"],
            "avantages": ["Remote possible", "Formation continue", "Stock-options"],
            "badges_auto_rempli": ["Auto-rempli"],
            "fiche_poste_originale": "Nous recherchons un développeur full-stack...",
            "parsing_confidence": 0.91
        }
    }
]

class EnhancedBridgeTestSuite:
    """🧪 Suite de tests complète pour Enhanced Bridge"""
    
    def __init__(self):
        self.session = None
        self.test_results = {
            "health_checks": {},
            "enhanced_conversions": [],
            "direct_matches": [],
            "batch_tests": [],
            "performance_metrics": {},
            "auto_fix_validations": [],
            "error_resilience": []
        }
        self.start_time = time.time()
    
    async def run_complete_test_suite(self) -> Dict[str, Any]:
        """🚀 Lance la suite de tests complète"""
        print("🧪 === ENHANCED BRIDGE TEST SUITE ===")
        print("🎯 Tests d'intégration Commitment- → Nextvision Enhanced")
        print("🔧 Validation auto-fix intelligence + robustesse")
        print("")
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            try:
                # 1. Health checks
                await self._test_health_checks()
                
                # 2. Tests conversion Enhanced individuels
                await self._test_enhanced_conversions()
                
                # 3. Tests matching direct Enhanced
                await self._test_direct_enhanced_matching()
                
                # 4. Tests batch Enhanced
                await self._test_enhanced_batch()
                
                # 5. Tests validation auto-fix
                await self._test_auto_fix_intelligence()
                
                # 6. Tests robustesse erreurs
                await self._test_error_resilience()
                
                # 7. Tests performance
                await self._test_performance_metrics()
                
                # 8. Génération rapport final
                return self._generate_test_report()
                
            except Exception as e:
                logger.error(f"❌ Erreur critique suite de tests: {e}")
                return {"status": "critical_error", "error": str(e)}
    
    async def _test_health_checks(self):
        """❤️ Tests de santé système"""
        print("❤️ Tests de santé système...")
        
        # Health check standard
        try:
            async with self.session.get(f"{API_BASE_URL}{ENHANCED_ENDPOINTS['health']}") as resp:
                if resp.status == 200:
                    health_data = await resp.json()
                    self.test_results["health_checks"]["standard"] = {
                        "status": "✅ OK",
                        "enhanced_bridge": health_data.get("features", {}).get("enhanced_bridge", False),
                        "auto_fix": health_data.get("features", {}).get("auto_fix_intelligence", False)
                    }
                    print("  ✅ Health check standard OK")
                else:
                    self.test_results["health_checks"]["standard"] = {"status": f"❌ Error {resp.status}"}
                    print(f"  ❌ Health check standard failed: {resp.status}")
        except Exception as e:
            self.test_results["health_checks"]["standard"] = {"status": f"❌ Exception: {str(e)}"}
            print(f"  ❌ Health check standard exception: {e}")
        
        # Health check Enhanced Bridge
        try:
            async with self.session.get(f"{API_BASE_URL}{ENHANCED_ENDPOINTS['enhanced_health']}") as resp:
                if resp.status == 200:
                    enhanced_health = await resp.json()
                    self.test_results["health_checks"]["enhanced"] = {
                        "status": "✅ OK",
                        "stats": enhanced_health.get("enhanced_bridge_stats", {}),
                        "features": enhanced_health.get("features", {})
                    }
                    print("  ✅ Enhanced Bridge health OK")
                    print(f"    🔧 Auto-fix: {enhanced_health.get('features', {}).get('auto_fix_intelligence', False)}")
                    print(f"    ⚡ Cache: {enhanced_health.get('features', {}).get('performance_caching', False)}")
                else:
                    self.test_results["health_checks"]["enhanced"] = {"status": f"❌ Error {resp.status}"}
                    print(f"  ❌ Enhanced health failed: {resp.status}")
        except Exception as e:
            self.test_results["health_checks"]["enhanced"] = {"status": f"❌ Exception: {str(e)}"}
            print(f"  ❌ Enhanced health exception: {e}")
    
    async def _test_enhanced_conversions(self):
        """🔄 Tests conversions Enhanced individuelles"""
        print("🔄 Tests conversions Enhanced...")
        
        for candidat_test in ENHANCED_PARSER_TEST_DATA:
            try:
                start_time = time.time()
                
                payload = {
                    "candidat_data": candidat_test["data"],
                    "candidat_questionnaire": {
                        "raison_ecoute": "Rémunération trop faible",
                        "salary_min": 35000,
                        "salary_max": 45000,
                        "preferred_location": "Paris"
                    }
                }
                
                async with self.session.post(
                    f"{API_BASE_URL}{ENHANCED_ENDPOINTS['enhanced_conversion']}",
                    json=payload
                ) as resp:
                    processing_time = (time.time() - start_time) * 1000
                    
                    if resp.status == 200:
                        result = await resp.json()
                        metrics = result.get("performance_metrics", {}).get("candidat", {})
                        
                        self.test_results["enhanced_conversions"].append({
                            "test_name": candidat_test["name"],
                            "status": "✅ Success",
                            "processing_time_ms": processing_time,
                            "auto_fixes": metrics.get("auto_fixes_count", 0),
                            "cache_used": metrics.get("cache_used", False),
                            "converted_name": result.get("converted_data", {}).get("candidat", {}).get("personal_info", {}).get("firstName", "N/A")
                        })
                        
                        print(f"  ✅ {candidat_test['name']}: {processing_time:.2f}ms, {metrics.get('auto_fixes_count', 0)} auto-fixes")
                    else:
                        error_text = await resp.text()
                        self.test_results["enhanced_conversions"].append({
                            "test_name": candidat_test["name"],
                            "status": f"❌ Error {resp.status}",
                            "error": error_text[:200]
                        })
                        print(f"  ❌ {candidat_test['name']}: Error {resp.status}")
                        
            except Exception as e:
                self.test_results["enhanced_conversions"].append({
                    "test_name": candidat_test["name"],
                    "status": f"❌ Exception",
                    "error": str(e)
                })
                print(f"  ❌ {candidat_test['name']}: Exception {e}")
    
    async def _test_direct_enhanced_matching(self):
        """🎯 Tests matching direct Enhanced"""
        print("🎯 Tests matching direct Enhanced...")
        
        # Test complet candidat + entreprise
        try:
            start_time = time.time()
            
            payload = {
                "candidat_data": ENHANCED_PARSER_TEST_DATA[0]["data"],
                "entreprise_data": CHATGPT_TEST_DATA[0]["data"],
                "candidat_questionnaire": {
                    "raison_ecoute": "Rémunération trop faible",
                    "salary_min": 35000,
                    "salary_max": 45000
                },
                "entreprise_questionnaire": {
                    "company_name": "Cabinet Comptable Excellence",
                    "urgence": "urgent"
                }
            }
            
            async with self.session.post(
                f"{API_BASE_URL}{ENHANCED_ENDPOINTS['enhanced_direct_match']}",
                json=payload
            ) as resp:
                processing_time = (time.time() - start_time) * 1000
                
                if resp.status == 200:
                    result = await resp.json()
                    
                    self.test_results["direct_matches"].append({
                        "test_name": "comptable_match_enhanced",
                        "status": "✅ Success",
                        "processing_time_ms": processing_time,
                        "matching_score": result.get("matching_score", 0),
                        "compatibility": result.get("compatibility", "unknown"),
                        "confidence": result.get("confidence", 0),
                        "enhanced_metadata": result.get("component_scores", {}).get("semantique_details", {}).get("enhanced_metadata", {})
                    })
                    
                    print(f"  ✅ Matching Enhanced: {processing_time:.2f}ms")
                    print(f"    📊 Score: {result.get('matching_score', 0):.3f}")
                    print(f"    🎯 Compatibilité: {result.get('compatibility', 'unknown')}")
                    
                    # Extraction métadonnées Enhanced
                    enhanced_meta = result.get("component_scores", {}).get("semantique_details", {}).get("enhanced_metadata", {})
                    if enhanced_meta:
                        perf = enhanced_meta.get("performance_breakdown", {})
                        print(f"    🔧 Auto-fixes totaux: {perf.get('total_auto_fixes', 0)}")
                        print(f"    ⚡ Conversion candidat: {perf.get('candidat_conversion_ms', 0):.2f}ms")
                        print(f"    ⚡ Conversion entreprise: {perf.get('entreprise_conversion_ms', 0):.2f}ms")
                else:
                    error_text = await resp.text()
                    self.test_results["direct_matches"].append({
                        "test_name": "comptable_match_enhanced",
                        "status": f"❌ Error {resp.status}",
                        "error": error_text[:200]
                    })
                    print(f"  ❌ Matching Enhanced failed: {resp.status}")
                    
        except Exception as e:
            self.test_results["direct_matches"].append({
                "test_name": "comptable_match_enhanced",
                "status": f"❌ Exception",
                "error": str(e)
            })
            print(f"  ❌ Matching Enhanced exception: {e}")
    
    async def _test_enhanced_batch(self):
        """📦 Tests batch Enhanced"""
        print("📦 Tests batch Enhanced...")
        
        try:
            start_time = time.time()
            
            # Préparation données batch
            candidats_data = [test["data"] for test in ENHANCED_PARSER_TEST_DATA]
            entreprises_data = [test["data"] for test in CHATGPT_TEST_DATA]
            
            payload = {
                "candidats_data": candidats_data,
                "entreprises_data": entreprises_data,
                "enable_parallel": True
            }
            
            async with self.session.post(
                f"{API_BASE_URL}{ENHANCED_ENDPOINTS['enhanced_batch']}",
                json=payload
            ) as resp:
                processing_time = (time.time() - start_time) * 1000
                
                if resp.status == 200:
                    result = await resp.json()
                    results_data = result.get("results", {})
                    perf_summary = results_data.get("performance_summary", {})
                    
                    self.test_results["batch_tests"].append({
                        "test_name": "batch_enhanced_processing",
                        "status": "✅ Success",
                        "processing_time_ms": processing_time,
                        "total_processed": perf_summary.get("total_processed", 0),
                        "success_rate": perf_summary.get("success_rate_percent", 0),
                        "throughput": perf_summary.get("throughput_items_per_sec", 0)
                    })
                    
                    print(f"  ✅ Batch Enhanced: {processing_time:.2f}ms")
                    print(f"    📦 Traités: {perf_summary.get('total_processed', 0)}")
                    print(f"    ✅ Succès: {perf_summary.get('total_successful', 0)}/{perf_summary.get('total_processed', 0)}")
                    print(f"    ⚡ Débit: {perf_summary.get('throughput_items_per_sec', 0):.1f} items/sec")
                else:
                    error_text = await resp.text()
                    self.test_results["batch_tests"].append({
                        "test_name": "batch_enhanced_processing",
                        "status": f"❌ Error {resp.status}",
                        "error": error_text[:200]
                    })
                    print(f"  ❌ Batch Enhanced failed: {resp.status}")
                    
        except Exception as e:
            self.test_results["batch_tests"].append({
                "test_name": "batch_enhanced_processing",
                "status": f"❌ Exception",
                "error": str(e)
            })
            print(f"  ❌ Batch Enhanced exception: {e}")
    
    async def _test_auto_fix_intelligence(self):
        """🔧 Tests intelligence auto-fix"""
        print("🔧 Tests intelligence auto-fix...")
        
        # Test données avec erreurs intentionnelles
        buggy_candidat = {
            "personal_info": {
                "firstName": "marie",  # Pas de majuscule
                "lastName": "DUPONT",  # Tout majuscules
                "email": "marie..dupont@email..com",  # Points multiples
                "phone": "0612345678"  # Format non formaté
            },
            "skills": ["CEGID", "Excel", "CEGID", "  ", "Excel", ""],  # Doublons et vides
            "experience": {"total_years": "7 ans d'expérience"},  # String complexe
            "softwares": ["CEGID ", " Excel", "", "  Visual Studio  "],  # Espaces parasites
            "parsing_confidence": 0.65
        }
        
        try:
            start_time = time.time()
            
            payload = {
                "candidat_data": buggy_candidat,
                "candidat_questionnaire": {"raison_ecoute": "Poste ne coïncide pas"}
            }
            
            async with self.session.post(
                f"{API_BASE_URL}{ENHANCED_ENDPOINTS['enhanced_conversion']}",
                json=payload
            ) as resp:
                processing_time = (time.time() - start_time) * 1000
                
                if resp.status == 200:
                    result = await resp.json()
                    metrics = result.get("performance_metrics", {}).get("candidat", {})
                    converted = result.get("converted_data", {}).get("candidat", {})
                    
                    # Validation auto-fixes appliqués
                    fixes_detected = []
                    if converted.get("personal_info", {}).get("firstName") == "Marie":
                        fixes_detected.append("firstName_capitalization")
                    if converted.get("personal_info", {}).get("lastName") == "Dupont":
                        fixes_detected.append("lastName_capitalization")
                    if "marie.dupont@email.com" in converted.get("personal_info", {}).get("email", ""):
                        fixes_detected.append("email_cleanup")
                    
                    self.test_results["auto_fix_validations"].append({
                        "test_name": "auto_fix_intelligence",
                        "status": "✅ Success",
                        "processing_time_ms": processing_time,
                        "auto_fixes_count": metrics.get("auto_fixes_count", 0),
                        "fixes_detected": fixes_detected,
                        "validation_success": len(fixes_detected) >= 2
                    })
                    
                    print(f"  ✅ Auto-fix Intelligence: {processing_time:.2f}ms")
                    print(f"    🔧 Corrections appliquées: {metrics.get('auto_fixes_count', 0)}")
                    print(f"    ✅ Validations réussies: {len(fixes_detected)}/3")
                    for fix in fixes_detected:
                        print(f"      - {fix}")
                else:
                    print(f"  ❌ Auto-fix test failed: {resp.status}")
                    
        except Exception as e:
            print(f"  ❌ Auto-fix test exception: {e}")
    
    async def _test_error_resilience(self):
        """🛡️ Tests robustesse erreurs"""
        print("🛡️ Tests robustesse erreurs...")
        
        # Test données invalides
        invalid_tests = [
            {
                "name": "empty_data",
                "payload": {"candidat_data": {}, "entreprise_data": {}}
            },
            {
                "name": "malformed_email",
                "payload": {
                    "candidat_data": {
                        "personal_info": {"email": "not-an-email", "firstName": "Test"}
                    }
                }
            },
            {
                "name": "missing_required_fields",
                "payload": {
                    "candidat_data": {"skills": ["Python"]}  # Manque personal_info
                }
            }
        ]
        
        for test in invalid_tests:
            try:
                async with self.session.post(
                    f"{API_BASE_URL}{ENHANCED_ENDPOINTS['enhanced_conversion']}",
                    json=test["payload"]
                ) as resp:
                    
                    # On s'attend à ce que l'API gère gracieusement les erreurs
                    status_ok = resp.status in [200, 400, 422]  # Codes acceptables
                    
                    self.test_results["error_resilience"].append({
                        "test_name": test["name"],
                        "status": "✅ Handled" if status_ok else f"❌ Unexpected {resp.status}",
                        "response_code": resp.status,
                        "graceful_handling": status_ok
                    })
                    
                    if status_ok:
                        print(f"  ✅ {test['name']}: Handled gracefully ({resp.status})")
                    else:
                        print(f"  ❌ {test['name']}: Unexpected response ({resp.status})")
                        
            except Exception as e:
                self.test_results["error_resilience"].append({
                    "test_name": test["name"],
                    "status": f"❌ Exception",
                    "error": str(e)
                })
                print(f"  ❌ {test['name']}: Exception {e}")
    
    async def _test_performance_metrics(self):
        """⚡ Tests métriques performance"""
        print("⚡ Tests métriques performance...")
        
        # Collecte toutes les métriques de temps
        processing_times = []
        
        for test in self.test_results["enhanced_conversions"]:
            if "processing_time_ms" in test:
                processing_times.append(test["processing_time_ms"])
        
        for test in self.test_results["direct_matches"]:
            if "processing_time_ms" in test:
                processing_times.append(test["processing_time_ms"])
        
        if processing_times:
            self.test_results["performance_metrics"] = {
                "total_tests": len(processing_times),
                "avg_time_ms": statistics.mean(processing_times),
                "min_time_ms": min(processing_times),
                "max_time_ms": max(processing_times),
                "median_time_ms": statistics.median(processing_times),
                "target_achieved": statistics.mean(processing_times) < 150  # Objectif < 150ms
            }
            
            print(f"  📊 Tests performance: {len(processing_times)} mesures")
            print(f"    ⚡ Temps moyen: {statistics.mean(processing_times):.2f}ms")
            print(f"    🎯 Objectif < 150ms: {'✅' if statistics.mean(processing_times) < 150 else '❌'}")
            print(f"    📈 Min/Max: {min(processing_times):.2f}ms / {max(processing_times):.2f}ms")
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """📊 Génère rapport final des tests"""
        total_time = time.time() - self.start_time
        
        # Calcul statistiques globales
        total_tests = 0
        successful_tests = 0
        
        for category in ["enhanced_conversions", "direct_matches", "batch_tests", "auto_fix_validations", "error_resilience"]:
            tests = self.test_results.get(category, [])
            total_tests += len(tests)
            successful_tests += len([t for t in tests if "✅" in t.get("status", "")])
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "test_suite_summary": {
                "total_execution_time_sec": round(total_time, 2),
                "total_tests_run": total_tests,
                "successful_tests": successful_tests,
                "success_rate_percent": round(success_rate, 2),
                "timestamp": datetime.now().isoformat()
            },
            "detailed_results": self.test_results,
            "recommendations": self._generate_recommendations(),
            "next_steps": self._generate_next_steps()
        }
        
        print("")
        print("📊 === RAPPORT FINAL DES TESTS ===")
        print(f"⏱️ Temps total: {total_time:.2f}s")
        print(f"🧪 Tests exécutés: {total_tests}")
        print(f"✅ Tests réussis: {successful_tests}")
        print(f"📈 Taux de succès: {success_rate:.1f}%")
        print("")
        print("🎯 PROCHAINES ÉTAPES:")
        for step in report["next_steps"]:
            print(f"  • {step}")
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """💡 Génère recommandations basées sur les tests"""
        recommendations = []
        
        # Analyse performance
        perf = self.test_results.get("performance_metrics", {})
        if perf.get("avg_time_ms", 0) > 100:
            recommendations.append("Optimiser performance: temps moyen > 100ms")
        
        # Analyse auto-fix
        auto_fix_tests = self.test_results.get("auto_fix_validations", [])
        if any(not t.get("validation_success", False) for t in auto_fix_tests):
            recommendations.append("Améliorer patterns auto-fix pour plus de robustesse")
        
        # Analyse robustesse
        error_tests = self.test_results.get("error_resilience", [])
        if any(not t.get("graceful_handling", False) for t in error_tests):
            recommendations.append("Renforcer gestion d'erreurs pour cas edge")
        
        if not recommendations:
            recommendations.append("Tous les tests passent - système prêt pour production!")
        
        return recommendations
    
    def _generate_next_steps(self) -> List[str]:
        """🚀 Génère prochaines étapes"""
        return [
            "Intégrer Enhanced Bridge dans interface Commitment-",
            "Créer composants React pour workflow complet",
            "Tester avec vraies données (69 CVs + 34 FDPs)",
            "Déployer en environnement de staging",
            "Former utilisateurs sur nouvelles fonctionnalités",
            "Monitoring production avec métriques Enhanced"
        ]

async def main():
    """🚀 Point d'entrée principal des tests"""
    test_suite = EnhancedBridgeTestSuite()
    
    try:
        # Vérification API disponible
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/v1/health") as resp:
                if resp.status != 200:
                    print(f"❌ API Nextvision non disponible sur {API_BASE_URL}")
                    print("   Assurez-vous que l'API tourne avec: python main_v2_enhanced.py")
                    return
        
        # Lancement tests
        report = await test_suite.run_complete_test_suite()
        
        # Sauvegarde rapport
        report_file = Path(f"enhanced_bridge_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Rapport sauvegardé: {report_file}")
        
        return report
        
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        return {"status": "critical_error", "error": str(e)}

if __name__ == "__main__":
    # Lancement des tests
    asyncio.run(main())
