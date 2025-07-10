"""
🧪 Nextvision V3.0 - Tests Validation Transport Intelligence (PROMPT 5)
Script de test avec adresses réelles Paris pour valider précision

OBJECTIF PROMPT 5: "TESTE avec adresses réelles de Paris pour valider précision"

Author: NEXTEN Team
Version: 3.0.0 - Transport Intelligence Tests
Usage: python -m nextvision.tests.test_transport_intelligence_paris
"""

import asyncio
import logging
import json
from typing import Dict, Any
from datetime import datetime

# Configuration logging pour tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TransportIntelligenceParisValidator:
    """🧪 Validateur Transport Intelligence avec adresses réelles Paris"""
    
    def __init__(self):
        self.test_suite_name = "Transport Intelligence V3.0 - Paris Validation"
        self.version = "3.0.0"
        
        # Adresses réelles Paris pour tests de précision
        self.real_paris_addresses = {
            "candidates": [
                {
                    "name": "Candidat Châtelet",
                    "address": "1 Place du Châtelet, 75001 Paris",
                    "profile": "Centre Paris, très bien desservi"
                },
                {
                    "name": "Candidat République", 
                    "address": "Place de la République, 75011 Paris",
                    "profile": "Est parisien, métro/vélo facile"
                },
                {
                    "name": "Candidat Champs-Élysées",
                    "address": "Avenue des Champs-Élysées, 75008 Paris",
                    "profile": "Ouest parisien, prestige mais circulation"
                },
                {
                    "name": "Candidat Montparnasse",
                    "address": "Tour Montparnasse, 75014 Paris", 
                    "profile": "Sud Paris, gare importante"
                },
                {
                    "name": "Candidat Bastille",
                    "address": "Place de la Bastille, 75012 Paris",
                    "profile": "Est Paris, RER A accessible"
                }
            ],
            "companies": [
                {
                    "name": "Entreprise La Défense",
                    "address": "1 Place de la Défense, 92400 Courbevoie",
                    "profile": "Zone business principale, RER/métro"
                },
                {
                    "name": "Entreprise Opéra",
                    "address": "Place de l'Opéra, 75009 Paris",
                    "profile": "Centre Paris, excellente desserte"
                },
                {
                    "name": "Entreprise Gare de Lyon",
                    "address": "Place Louis Armand, 75012 Paris",
                    "profile": "Hub transport, RER/métro/trains"
                },
                {
                    "name": "Entreprise Saint-Germain",
                    "address": "Boulevard Saint-Germain, 75006 Paris",
                    "profile": "Rive gauche, métro dense"
                },
                {
                    "name": "Entreprise Invalides",
                    "address": "Esplanade des Invalides, 75007 Paris",
                    "profile": "Zone gouvernementale, RER C"
                }
            ]
        }
        
        # Scénarios de test réalistes
        self.test_scenarios = [
            {
                "name": "Candidat Flexible Multi-modal",
                "transport_methods": ["public-transport", "vehicle", "bike", "walking"],
                "travel_times": {"public-transport": 45, "vehicle": 35, "bike": 25, "walking": 60},
                "context": {"remote_days_per_week": 2, "flexible_hours": True}
            },
            {
                "name": "Candidat Transport Public Only",
                "transport_methods": ["public-transport"],
                "travel_times": {"public-transport": 60},
                "context": {"parking_provided": False, "flexible_hours": False}
            },
            {
                "name": "Candidat Voiture + Vélo",
                "transport_methods": ["vehicle", "bike"],
                "travel_times": {"vehicle": 30, "bike": 20},
                "context": {"parking_provided": True, "flexible_hours": True}
            },
            {
                "name": "Candidat Contraintes Strictes",
                "transport_methods": ["vehicle"],
                "travel_times": {"vehicle": 25},
                "context": {"parking_provided": True, "flexible_hours": False}
            },
            {
                "name": "Candidat Écologique",
                "transport_methods": ["bike", "walking", "public-transport"],
                "travel_times": {"bike": 30, "walking": 45, "public-transport": 40},
                "context": {"remote_days_per_week": 3, "eco_conscious": True}
            }
        ]
    
    async def run_full_validation_suite(self, transport_intelligence_engine) -> Dict[str, Any]:
        """🧪 Suite complète de validation avec adresses réelles Paris"""
        
        logger.info(f"🧪 Début validation {self.test_suite_name}")
        start_time = datetime.now()
        
        validation_results = {
            "test_suite": self.test_suite_name,
            "version": self.version,
            "started_at": start_time.isoformat(),
            "test_matrix": [],
            "summary": {
                "total_combinations": 0,
                "successful_tests": 0,
                "failed_tests": 0,
                "average_score": 0.0,
                "score_distribution": {},
                "performance_metrics": {}
            },
            "insights": {
                "best_combinations": [],
                "challenging_routes": [],
                "transport_method_effectiveness": {},
                "geographic_patterns": {}
            }
        }
        
        # Matrice de tests : chaque candidat × chaque entreprise × chaque scénario
        test_count = 0
        all_scores = []
        
        for candidate in self.real_paris_addresses["candidates"]:
            for company in self.real_paris_addresses["companies"]:
                for scenario in self.test_scenarios:
                    test_count += 1
                    
                    test_result = await self._run_single_test(
                        transport_intelligence_engine,
                        candidate, company, scenario
                    )
                    
                    validation_results["test_matrix"].append(test_result)
                    
                    if test_result["status"] == "SUCCESS":
                        validation_results["summary"]["successful_tests"] += 1
                        all_scores.append(test_result["score"])
                    else:
                        validation_results["summary"]["failed_tests"] += 1
                    
                    # Log progression
                    if test_count % 5 == 0:
                        logger.info(f"🧪 Progression: {test_count} tests exécutés...")
        
        validation_results["summary"]["total_combinations"] = test_count
        
        # Calcul métriques globales
        if all_scores:
            validation_results["summary"]["average_score"] = sum(all_scores) / len(all_scores)
            validation_results["summary"]["score_distribution"] = self._analyze_score_distribution(all_scores)
        
        # Analyse insights avancés
        validation_results["insights"] = await self._generate_validation_insights(
            validation_results["test_matrix"]
        )
        
        # Métriques performance globales
        total_time = (datetime.now() - start_time).total_seconds()
        validation_results["summary"]["performance_metrics"] = {
            "total_execution_time_seconds": total_time,
            "tests_per_second": test_count / total_time if total_time > 0 else 0,
            "average_test_time_seconds": total_time / test_count if test_count > 0 else 0
        }
        
        validation_results["completed_at"] = datetime.now().isoformat()
        
        # Rapport final
        success_rate = validation_results["summary"]["successful_tests"] / test_count * 100
        logger.info(
            f"✅ Validation terminée: {success_rate:.1f}% succès "
            f"({validation_results['summary']['successful_tests']}/{test_count} tests), "
            f"score moyen: {validation_results['summary']['average_score']:.3f}"
        )
        
        return validation_results
    
    async def _run_single_test(
        self, 
        transport_intelligence_engine,
        candidate: Dict,
        company: Dict, 
        scenario: Dict
    ) -> Dict[str, Any]:
        """🎯 Exécution test unique avec validation précision"""
        
        test_name = f"{candidate['name']} → {company['name']} ({scenario['name']})"
        
        try:
            test_start = datetime.now()
            
            # Appel Transport Intelligence Engine V3.0
            result = await transport_intelligence_engine.calculate_intelligent_location_score(
                candidat_address=candidate["address"],
                entreprise_address=company["address"],
                transport_methods=scenario["transport_methods"],
                travel_times=scenario["travel_times"],
                context=scenario["context"]
            )
            
            test_duration = (datetime.now() - test_start).total_seconds()
            
            # Validation précision résultats
            precision_validation = self._validate_result_precision(result, candidate, company, scenario)
            
            return {
                "test_name": test_name,
                "status": "SUCCESS" if not result.get("error") else "FAILED",
                "score": result.get("final_score", 0.0),
                "candidate": candidate["name"],
                "company": company["name"],
                "scenario": scenario["name"],
                "result_details": {
                    "compatible_modes": result.get("compatibility_analysis", {}).get("compatible_modes", []),
                    "best_transport": result.get("best_transport_option", {}),
                    "score_breakdown": result.get("score_breakdown", {}),
                    "routes_calculated": len(result.get("all_routes", {}))
                },
                "precision_validation": precision_validation,
                "performance": {
                    "calculation_time_seconds": test_duration,
                    "google_maps_calls": len(result.get("all_routes", {})),
                    "cache_used": "cached_at" in str(result)
                },
                "addresses": {
                    "candidat": candidate["address"],
                    "entreprise": company["address"]
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Test failed: {test_name} - {e}")
            
            return {
                "test_name": test_name,
                "status": "ERROR",
                "score": 0.0,
                "candidate": candidate["name"],
                "company": company["name"], 
                "scenario": scenario["name"],
                "error": str(e),
                "precision_validation": {"validation_passed": False, "error": str(e)}
            }
    
    def _validate_result_precision(
        self, 
        result: Dict[str, Any],
        candidate: Dict,
        company: Dict,
        scenario: Dict
    ) -> Dict[str, Any]:
        """✅ Validation précision résultats Google Maps"""
        
        validation = {
            "validation_passed": True,
            "checks": [],
            "warnings": [],
            "errors": []
        }
        
        # Check 1: Score dans range valide
        score = result.get("final_score", 0.0)
        if 0.0 <= score <= 1.0:
            validation["checks"].append("✅ Score dans range valide [0.0, 1.0]")
        else:
            validation["errors"].append(f"❌ Score invalide: {score}")
            validation["validation_passed"] = False
        
        # Check 2: Routes calculées pour modes demandés
        all_routes = result.get("all_routes", {})
        requested_methods = scenario["transport_methods"]
        
        routes_found = len(all_routes)
        if routes_found > 0:
            validation["checks"].append(f"✅ {routes_found} routes calculées via Google Maps")
        else:
            validation["warnings"].append("⚠️ Aucune route calculée - mode fallback possible")
        
        # Check 3: Cohérence modes compatibles
        compatibility_analysis = result.get("compatibility_analysis", {})
        compatible_modes = compatibility_analysis.get("compatible_modes", [])
        
        for mode in compatible_modes:
            if mode in requested_methods:
                validation["checks"].append(f"✅ Mode compatible cohérent: {mode}")
            else:
                validation["warnings"].append(f"⚠️ Mode compatible non demandé: {mode}")
        
        # Check 4: Présence explications intelligentes
        explanations = result.get("explanations", [])
        if len(explanations) >= 3:
            validation["checks"].append("✅ Explications détaillées présentes")
        else:
            validation["warnings"].append("⚠️ Explications limitées")
        
        # Check 5: Recommandations contextuelles
        recommendations = result.get("recommendations", [])
        if recommendations:
            validation["checks"].append("✅ Recommandations générées")
        else:
            validation["warnings"].append("⚠️ Aucune recommandation")
        
        # Check 6: Cohérence géographique (Paris/Île-de-France)
        if "paris" in candidate["address"].lower() and "paris" in company["address"].lower():
            # Pour intra-Paris, au moins un mode devrait être compatible
            if compatible_modes:
                validation["checks"].append("✅ Cohérence géographique intra-Paris")
            else:
                validation["warnings"].append("⚠️ Aucun mode compatible intra-Paris (suspect)")
        
        return validation
    
    def _analyze_score_distribution(self, scores: List[float]) -> Dict[str, Any]:
        """📊 Analyse distribution des scores"""
        
        if not scores:
            return {}
        
        scores_sorted = sorted(scores)
        n = len(scores)
        
        return {
            "min": min(scores),
            "max": max(scores),
            "mean": sum(scores) / n,
            "median": scores_sorted[n // 2],
            "quartiles": {
                "q1": scores_sorted[n // 4],
                "q3": scores_sorted[3 * n // 4]
            },
            "score_ranges": {
                "excellent_0.8_1.0": len([s for s in scores if s >= 0.8]),
                "good_0.6_0.8": len([s for s in scores if 0.6 <= s < 0.8]),
                "moderate_0.4_0.6": len([s for s in scores if 0.4 <= s < 0.6]),
                "poor_0.0_0.4": len([s for s in scores if s < 0.4])
            }
        }
    
    async def _generate_validation_insights(self, test_matrix: List[Dict]) -> Dict[str, Any]:
        """🧠 Génération insights validation avancés"""
        
        insights = {
            "best_combinations": [],
            "challenging_routes": [],
            "transport_method_effectiveness": {},
            "geographic_patterns": {}
        }
        
        # Top 5 meilleures combinaisons
        successful_tests = [t for t in test_matrix if t["status"] == "SUCCESS"]
        best_tests = sorted(successful_tests, key=lambda x: x["score"], reverse=True)[:5]
        
        insights["best_combinations"] = [
            {
                "combination": f"{t['candidate']} → {t['company']}",
                "score": t["score"],
                "scenario": t["scenario"],
                "compatible_modes": t["result_details"]["compatible_modes"]
            }
            for t in best_tests
        ]
        
        # Routes les plus difficiles (score < 0.4)
        challenging_tests = [t for t in successful_tests if t["score"] < 0.4]
        insights["challenging_routes"] = [
            {
                "combination": f"{t['candidate']} → {t['company']}",
                "score": t["score"],
                "scenario": t["scenario"],
                "issues": "Temps de trajet dépassés" if not t["result_details"]["compatible_modes"] else "Score faible malgré compatibilité"
            }
            for t in challenging_tests[:5]
        ]
        
        # Efficacité par méthode transport
        method_stats = {}
        for test in successful_tests:
            scenario_methods = test.get("result_details", {}).get("compatible_modes", [])
            for method in scenario_methods:
                if method not in method_stats:
                    method_stats[method] = {"count": 0, "total_score": 0.0}
                method_stats[method]["count"] += 1
                method_stats[method]["total_score"] += test["score"]
        
        insights["transport_method_effectiveness"] = {
            method: {
                "compatibility_rate": stats["count"],
                "average_score": stats["total_score"] / stats["count"] if stats["count"] > 0 else 0
            }
            for method, stats in method_stats.items()
        }
        
        # Patterns géographiques (analyse basique)
        paris_intra = [t for t in successful_tests if "paris" in t["addresses"]["candidat"].lower() and "paris" in t["addresses"]["entreprise"].lower()]
        paris_suburb = [t for t in successful_tests if ("paris" in t["addresses"]["candidat"].lower()) != ("paris" in t["addresses"]["entreprise"].lower())]
        
        insights["geographic_patterns"] = {
            "intra_paris": {
                "count": len(paris_intra),
                "average_score": sum(t["score"] for t in paris_intra) / len(paris_intra) if paris_intra else 0
            },
            "paris_suburb": {
                "count": len(paris_suburb),
                "average_score": sum(t["score"] for t in paris_suburb) / len(paris_suburb) if paris_suburb else 0
            }
        }
        
        return insights
    
    def save_validation_report(self, validation_results: Dict[str, Any], filename: str = None):
        """💾 Sauvegarde rapport validation"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transport_intelligence_validation_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(validation_results, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"📄 Rapport validation sauvegardé: {filename}")
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde rapport: {e}")
    
    def print_validation_summary(self, validation_results: Dict[str, Any]):
        """📋 Affichage résumé validation"""
        
        summary = validation_results["summary"]
        insights = validation_results["insights"]
        
        print("\n" + "="*80)
        print(f"🧪 {validation_results['test_suite']} - RÉSUMÉ")
        print("="*80)
        
        print(f"\n📊 STATISTIQUES GLOBALES:")
        print(f"   Tests exécutés: {summary['total_combinations']}")
        print(f"   Succès: {summary['successful_tests']} ({summary['successful_tests']/summary['total_combinations']*100:.1f}%)")
        print(f"   Échecs: {summary['failed_tests']}")
        print(f"   Score moyen: {summary['average_score']:.3f}")
        
        if "score_distribution" in summary and summary["score_distribution"]:
            dist = summary["score_distribution"]["score_ranges"]
            print(f"\n📈 DISTRIBUTION SCORES:")
            print(f"   Excellent (0.8-1.0): {dist['excellent_0.8_1.0']} tests")
            print(f"   Bon (0.6-0.8): {dist['good_0.6_0.8']} tests")
            print(f"   Modéré (0.4-0.6): {dist['moderate_0.4_0.6']} tests")
            print(f"   Faible (0.0-0.4): {dist['poor_0.0_0.4']} tests")
        
        print(f"\n🎯 TOP 3 MEILLEURES COMBINAISONS:")
        for i, combo in enumerate(insights["best_combinations"][:3], 1):
            print(f"   {i}. {combo['combination']}: {combo['score']:.3f}")
            print(f"      Modes: {', '.join(combo['compatible_modes'])}")
        
        print(f"\n🚧 ROUTES DIFFICILES:")
        for route in insights["challenging_routes"][:3]:
            print(f"   • {route['combination']}: {route['score']:.3f} - {route['issues']}")
        
        print(f"\n🚗 EFFICACITÉ PAR MODE TRANSPORT:")
        for method, stats in insights["transport_method_effectiveness"].items():
            print(f"   {method}: {stats['compatibility_rate']} utilisations, score moyen {stats['average_score']:.3f}")
        
        perf = summary["performance_metrics"]
        print(f"\n⚡ PERFORMANCE:")
        print(f"   Temps total: {perf['total_execution_time_seconds']:.1f}s")
        print(f"   Tests/seconde: {perf['tests_per_second']:.1f}")
        print(f"   Temps moyen/test: {perf['average_test_time_seconds']:.2f}s")
        
        print("\n" + "="*80)


# Exemple d'utilisation (à adapter selon votre architecture)
async def main():
    """🚀 Point d'entrée principal pour tests validation"""
    
    print("🧪 Initialisation Transport Intelligence Paris Validator V3.0")
    
    # NOTE: Ces imports doivent être adaptés selon votre structure
    # from nextvision.services.google_maps_service import GoogleMapsService  
    # from nextvision.services.transport_calculator import TransportCalculator
    # from nextvision.engines.transport_intelligence_engine import TransportIntelligenceEngine
    
    # Configuration pour tests (adaptez vos clés API)
    # google_maps_service = GoogleMapsService(api_key="YOUR_GOOGLE_MAPS_API_KEY")
    # transport_calculator = TransportCalculator(google_maps_service)
    # transport_intelligence_engine = TransportIntelligenceEngine(google_maps_service, transport_calculator)
    
    # Validation
    validator = TransportIntelligenceParisValidator()
    
    print("🚧 DEMO MODE - Services réels requis pour validation complète")
    print("   Initialisez GoogleMapsService avec votre clé API pour tests réels")
    
    # Pour tests réels, décommentez:
    # validation_results = await validator.run_full_validation_suite(transport_intelligence_engine)
    # validator.print_validation_summary(validation_results)
    # validator.save_validation_report(validation_results)
    
    print("✅ Validator configuré et prêt pour validation Transport Intelligence V3.0")

if __name__ == "__main__":
    asyncio.run(main())
