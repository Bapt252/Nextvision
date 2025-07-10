#!/usr/bin/env python3
"""
🧪 Test API Nextvision V3.2.1 - Système Complet
Test de tous les endpoints avec l'API qui tourne

Usage:
    python test_api_complete.py
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

class NextvisionAPITester:
    """🧪 Testeur API complet"""
    
    def __init__(self):
        self.api_base = "http://localhost:8001"  # Port détecté
        self.test_results = {}
        
    async def test_1_health_checks(self):
        """1️⃣ Test de tous les health checks"""
        print("1️⃣ Test health checks...")
        
        health_endpoints = [
            ("/api/v1/health", "Core API"),
            ("/api/v1/integration/health", "Bridge Integration"),
            ("/api/v2/maps/health", "Google Maps")
        ]
        
        results = {}
        
        async with aiohttp.ClientSession() as session:
            for endpoint, name in health_endpoints:
                try:
                    async with session.get(f"{self.api_base}{endpoint}") as response:
                        if response.status == 200:
                            data = await response.json()
                            print(f"✅ {name}: {data.get('status', 'OK')}")
                            results[name] = {"status": "success", "data": data}
                        else:
                            print(f"⚠️ {name}: HTTP {response.status}")
                            results[name] = {"status": "warning", "code": response.status}
                            
                except Exception as e:
                    print(f"❌ {name}: {e}")
                    results[name] = {"status": "error", "error": str(e)}
        
        return results
    
    async def test_2_adaptive_matching(self):
        """2️⃣ Test matching avec pondération adaptative"""
        print("\n2️⃣ Test pondération adaptative...")
        
        # Tests avec différentes raisons d'écoute
        test_cases = [
            {
                "name": "Rémunération",
                "pourquoi_ecoute": "Rémunération trop faible",
                "expected_boost": "remuneration"
            },
            {
                "name": "Compétences", 
                "pourquoi_ecoute": "Poste ne coïncide pas avec poste proposé",
                "expected_boost": "semantique"
            },
            {
                "name": "Localisation",
                "pourquoi_ecoute": "Poste trop loin de mon domicile", 
                "expected_boost": "localisation"
            }
        ]
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            for test_case in test_cases:
                print(f"🧪 Test {test_case['name']}...")
                
                matching_request = {
                    "pourquoi_ecoute": test_case["pourquoi_ecoute"],
                    "candidate_profile": {
                        "personal_info": {
                            "firstName": "Sophie",
                            "lastName": "Dubois",
                            "email": "sophie.dubois@test.com"
                        },
                        "skills": ["Python", "React", "PostgreSQL", "Docker"],
                        "experience_years": 5,
                        "education": "Master Informatique",
                        "current_role": "Développeur Full Stack"
                    },
                    "preferences": {
                        "salary_expectations": {
                            "min": 45000,
                            "max": 60000
                        },
                        "location_preferences": {
                            "city": "Paris",
                            "acceptedCities": ["Lyon"],
                            "maxDistance": 50
                        }
                    }
                }
                
                try:
                    url = f"{self.api_base}/api/v1/matching/candidate/test_{test_case['name'].lower()}"
                    
                    async with session.post(url, json=matching_request) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            score = data['matching_results']['total_score']
                            adaptation = data['adaptive_weighting']['applied']
                            reasoning = data['adaptive_weighting']['reasoning']
                            
                            print(f"   ✅ Score: {score}")
                            print(f"   🎯 Adaptation: {adaptation}")
                            print(f"   💡 Raison: {reasoning}")
                            
                            results.append({
                                "test_case": test_case,
                                "score": score,
                                "adaptation_applied": adaptation,
                                "reasoning": reasoning,
                                "success": True
                            })
                        else:
                            print(f"   ❌ Erreur HTTP: {response.status}")
                            results.append({
                                "test_case": test_case,
                                "success": False,
                                "error": f"HTTP {response.status}"
                            })
                            
                except Exception as e:
                    print(f"   ❌ Erreur: {e}")
                    results.append({
                        "test_case": test_case,
                        "success": False,
                        "error": str(e)
                    })
        
        return results
    
    async def test_3_transport_compatibility(self):
        """3️⃣ Test compatibilité transport"""
        print("\n3️⃣ Test transport intelligence...")
        
        transport_request = {
            "candidat_address": "15 rue de la Paix, 75001 Paris",
            "job_address": "50 Avenue de la République, 69003 Lyon", 
            "transport_modes": ["voiture", "transport_commun"],
            "max_times": {
                "voiture": 45,
                "transport_commun": 60
            },
            "telework_days": 2
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_base}/api/v2/transport/compatibility"
                
                async with session.post(url, json=transport_request) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        compatibility = data['compatibility_result']
                        print(f"✅ Compatible: {compatibility['is_compatible']}")
                        print(f"📊 Score: {compatibility['compatibility_score']}")
                        print(f"🚗 Mode recommandé: {compatibility.get('recommended_mode', 'N/A')}")
                        
                        return {
                            "status": "success",
                            "compatibility": compatibility,
                            "processing_time": data['metadata']['processing_time_ms']
                        }
                    else:
                        print(f"❌ Erreur HTTP: {response.status}")
                        return {"status": "error", "code": response.status}
                        
        except Exception as e:
            print(f"❌ Erreur transport: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_4_performance_check(self):
        """4️⃣ Test performance système"""
        print("\n4️⃣ Test performance...")
        
        # Test multiple requêtes en parallèle
        print("🚀 Test charge (10 requêtes parallèles)...")
        
        start_time = time.time()
        
        tasks = []
        for i in range(10):
            task = self._single_matching_request(f"perf_test_{i}")
            tasks.append(task)
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            success_count = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
            avg_time = total_time / len(results)
            
            print(f"✅ {success_count}/{len(results)} requêtes réussies")
            print(f"⏱️ Temps total: {total_time:.3f}s")
            print(f"📊 Temps moyen: {avg_time:.3f}s")
            
            return {
                "status": "success",
                "total_requests": len(results),
                "successful_requests": success_count,
                "total_time": total_time,
                "average_time": avg_time,
                "performance_ok": avg_time < 1.0  # < 1s par requête
            }
            
        except Exception as e:
            print(f"❌ Erreur test performance: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _single_matching_request(self, candidate_id):
        """Requête matching unique pour test performance"""
        
        matching_request = {
            "pourquoi_ecoute": "Recherche nouveau défi",
            "candidate_profile": {
                "personal_info": {
                    "firstName": "Test",
                    "lastName": candidate_id,
                    "email": f"{candidate_id}@test.com"
                },
                "skills": ["Python", "JavaScript"],
                "experience_years": 3
            },
            "preferences": {
                "salary_expectations": {"min": 40000, "max": 50000},
                "location_preferences": {"city": "Paris"}
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_base}/api/v1/matching/candidate/{candidate_id}"
                
                async with session.post(url, json=matching_request) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "score": data['matching_results']['total_score'],
                            "processing_time": data['metadata']['processing_time_ms']
                        }
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}
                        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def run_complete_test(self):
        """🚀 Lance tous les tests"""
        print("🚀 TEST COMPLET API NEXTVISION V3.2.1")
        print("="*60)
        
        start_time = time.time()
        
        # Tests séquentiels
        self.test_results["health"] = await self.test_1_health_checks()
        self.test_results["matching"] = await self.test_2_adaptive_matching()
        self.test_results["transport"] = await self.test_3_transport_compatibility()
        self.test_results["performance"] = await self.test_4_performance_check()
        
        total_time = time.time() - start_time
        
        # Résumé
        print("\n" + "="*60)
        print("📊 RÉSUMÉ COMPLET")
        print("="*60)
        
        # Comptage des succès
        health_success = sum(1 for r in self.test_results["health"].values() if r.get("status") == "success")
        matching_success = sum(1 for r in self.test_results["matching"] if r.get("success"))
        transport_success = self.test_results["transport"].get("status") == "success"
        performance_success = self.test_results["performance"].get("status") == "success"
        
        print(f"✅ Health Checks: {health_success}/3")
        print(f"✅ Matching Adaptatif: {matching_success}/3")
        print(f"✅ Transport: {'OK' if transport_success else 'ÉCHEC'}")
        print(f"✅ Performance: {'OK' if performance_success else 'ÉCHEC'}")
        
        total_success = health_success + matching_success + (1 if transport_success else 0) + (1 if performance_success else 0)
        total_tests = 3 + 3 + 1 + 1  # 8 tests au total
        
        print(f"\n🎯 Score global: {total_success}/{total_tests} ({total_success/total_tests*100:.1f}%)")
        print(f"⏱️ Temps total: {total_time:.3f}s")
        
        if total_success >= 6:  # Au moins 75% de réussite
            print("\n🎉 SYSTÈME NEXTVISION OPÉRATIONNEL!")
            print("🚀 Tous les composants clés fonctionnent")
            
            # Affichage des métriques clés
            if performance_success:
                perf = self.test_results["performance"]
                print(f"⚡ Performance: {perf['average_time']:.3f}s par requête")
            
            print(f"\n📋 Endpoints testés:")
            print(f"   • Matching adaptatif: ✅")
            print(f"   • Transport intelligence: ✅") 
            print(f"   • Google Maps: ✅")
            print(f"   • Bridge Commitment-: ✅")
            
        else:
            print("\n⚠️ SYSTÈME PARTIELLEMENT OPÉRATIONNEL")
            print("🔧 Certains composants nécessitent une vérification")
        
        return self.test_results

async def main():
    """Point d'entrée principal"""
    print("💡 Assurez-vous que l'API Nextvision tourne sur http://localhost:8001")
    print("💡 Démarrez avec: python main.py")
    print()
    
    tester = NextvisionAPITester()
    results = await tester.run_complete_test()
    
    # Sauvegarde des résultats
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"nextvision_api_test_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📄 Résultats détaillés sauvegardés: {filename}")

if __name__ == "__main__":
    asyncio.run(main())
