"""
🧠 Nextvision V3.0 - Transport Intelligence Engine (PROMPT 5)
Orchestrateur intelligent du scoring géographique révolutionné

RÉVOLUTIONNE: Le système de scoring localisation avec intelligence Google Maps
INTÈGRE: LocationTransportScorerV3 + GoogleMapsService + nouvelles données questionnaire

Author: NEXTEN Team
Version: 3.0.0 - Transport Intelligence Revolution
Architecture: Engine → LocationTransportScorerV3 → GoogleMapsService → Google Maps API
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json

# IMPORTS ABSOLUS (CORRIGÉS OPTION 1)
from nextvision.services.google_maps_service import GoogleMapsService
from nextvision.services.transport_calculator import TransportCalculator
from nextvision.services.scorers_v3.location_transport_scorer_v3 import LocationTransportScorerV3

logger = logging.getLogger(__name__)

class TransportIntelligenceEngine:
    """🧠 Engine Transport Intelligence V3.0 - Orchestrateur du scoring révolutionné
    
    MISSION PROMPT 5:
    - Orchestrer LocationTransportScorerV3 
    - Intégrer nouvelles données questionnaire (transport_methods + travel_times)
    - Optimiser performance avec batch processing
    - Tester avec adresses réelles Paris
    - Monitoring et analytics avancés
    """
    
    def __init__(self, google_maps_service: GoogleMapsService, 
                 transport_calculator: TransportCalculator):
        self.google_maps_service = google_maps_service
        self.transport_calculator = transport_calculator
        
        # Initialisation LocationTransportScorerV3
        self.location_transport_scorer_v3 = LocationTransportScorerV3(
            google_maps_service, transport_calculator
        )
        
        # Configuration engine
        self.engine_config = {
            "version": "3.0.0",
            "batch_processing": {
                "max_concurrent_jobs": 10,
                "chunk_size": 50,
                "timeout_seconds": 30
            },
            "performance_optimization": {
                "enable_caching": True,
                "cache_duration_hours": 2,
                "enable_batch_geocoding": True,
                "enable_parallel_processing": True
            },
            "fallback_strategy": {
                "max_retries": 2,
                "fallback_score": 0.6,
                "enable_intelligent_fallback": True
            }
        }
        
        # Analytics et monitoring
        self.analytics = {
            "total_scoring_requests": 0,
            "successful_scorings": 0,
            "failed_scorings": 0,
            "batch_operations": 0,
            "average_processing_time": 0.0,
            "google_maps_api_calls": 0,
            "cache_efficiency": {
                "hits": 0,
                "misses": 0
            },
            "transport_methods_usage": {},
            "performance_by_mode": {}
        }
        
        # Test addresses Paris pour validation
        self.paris_test_addresses = {
            "candidat_samples": [
                "13 rue du Champ de Mars, 75007 Paris",
                "25 avenue des Champs-Élysées, 75008 Paris", 
                "10 place de la République, 75011 Paris",
                "45 rue de Rivoli, 75001 Paris",
                "123 boulevard Saint-Germain, 75006 Paris"
            ],
            "entreprise_samples": [
                "La Défense, 92400 Courbevoie",
                "Place Vendôme, 75001 Paris",
                "Gare de Lyon, 75012 Paris",
                "Châtelet-Les Halles, 75001 Paris",
                "Montparnasse, 75014 Paris"
            ]
        }
    
    async def calculate_intelligent_location_score(
        self,
        candidat_address: str,
        entreprise_address: str,
        transport_methods: List[str],
        travel_times: Dict[str, int],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """🎯 Point d'entrée principal pour scoring localisation intelligent V3.0
        
        Args:
            candidat_address: Adresse exacte candidat (Google Maps autocomplete)
            entreprise_address: Adresse exacte entreprise  
            transport_methods: ['public-transport', 'vehicle', 'bike', 'walking']
            travel_times: {'public-transport': 30, 'vehicle': 25, 'bike': 20, 'walking': 15}
            context: Contexte additionnel (télétravail, parking, horaires flexibles, etc.)
            
        Returns:
            Résultat scoring enrichi avec intelligence transport
        """
        
        start_time = datetime.now()
        self.analytics["total_scoring_requests"] += 1
        
        try:
            # Validation des données d'entrée
            self._validate_input_data(candidat_address, entreprise_address, transport_methods, travel_times)
            
            # Enrichissement contexte avec intelligence
            enriched_context = await self._enrich_context_with_intelligence(context)
            
            # Appel LocationTransportScorerV3
            scoring_result = await self.location_transport_scorer_v3.calculate_location_transport_score_v3(
                candidat_address=candidat_address,
                entreprise_address=entreprise_address,
                transport_methods=transport_methods,
                travel_times=travel_times,
                context=enriched_context
            )
            
            # Post-traitement et enrichissement engine
            final_result = await self._post_process_scoring_result(
                scoring_result, candidat_address, entreprise_address, context
            )
            
            # Analytics et monitoring
            self._update_analytics(scoring_result, transport_methods, start_time, success=True)
            
            logger.info(
                f"🧠 TransportIntelligenceEngine: Score {final_result['final_score']:.3f} "
                f"calculé en {(datetime.now() - start_time).total_seconds():.2f}s"
            )
            
            self.analytics["successful_scorings"] += 1
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Erreur TransportIntelligenceEngine: {e}")
            self.analytics["failed_scorings"] += 1
            
            # Fallback intelligent de l'engine
            fallback_result = await self._create_engine_fallback_score(
                candidat_address, entreprise_address, transport_methods, travel_times, str(e)
            )
            
            self._update_analytics(fallback_result, transport_methods, start_time, success=False)
            return fallback_result
    
    async def batch_calculate_intelligent_scores(
        self,
        candidat_address: str,
        jobs_data: List[Dict],
        enable_optimization: bool = True
    ) -> Dict[str, Any]:
        """🚀 Calcul batch intelligent optimisé pour performance maximale
        
        Args:
            candidat_address: Adresse candidat
            jobs_data: Liste des données jobs avec transport_methods et travel_times
            enable_optimization: Active optimisations batch (grouping, parallélisation)
            
        Returns:
            Résultats batch avec analytics détaillés
        """
        
        start_time = datetime.now()
        self.analytics["batch_operations"] += 1
        
        logger.info(f"🚀 Batch Transport Intelligence: {len(jobs_data)} jobs à traiter")
        
        try:
            # Preprocessing et optimisation batch
            if enable_optimization:
                optimized_jobs_data = await self._optimize_batch_processing(jobs_data)
            else:
                optimized_jobs_data = jobs_data
            
            # Calcul par chunks pour performance
            chunk_size = self.engine_config["batch_processing"]["chunk_size"]
            max_concurrent = self.engine_config["batch_processing"]["max_concurrent_jobs"]
            
            all_results = {}
            processing_stats = {
                "total_jobs": len(optimized_jobs_data),
                "successful_jobs": 0,
                "failed_jobs": 0,
                "chunks_processed": 0,
                "total_google_maps_calls": 0
            }
            
            # Traitement par chunks
            for i in range(0, len(optimized_jobs_data), chunk_size):
                chunk = optimized_jobs_data[i:i + chunk_size]
                
                chunk_results = await self.location_transport_scorer_v3.batch_calculate_location_scores_v3(
                    candidat_address=candidat_address,
                    jobs_data=chunk,
                    max_concurrent=max_concurrent
                )
                
                # Fusion résultats
                all_results.update(chunk_results)
                processing_stats["chunks_processed"] += 1
                
                # Analytics par chunk
                for job_address, result in chunk_results.items():
                    if not result.get("error"):
                        processing_stats["successful_jobs"] += 1
                    else:
                        processing_stats["failed_jobs"] += 1
            
            # Post-traitement batch avec analytics
            batch_analytics = await self._analyze_batch_results(all_results, start_time)
            
            # Résultat final enrichi
            return {
                "scores": all_results,
                "batch_analytics": batch_analytics,
                "processing_stats": processing_stats,
                "engine_config": self.engine_config,
                "calculated_at": datetime.now().isoformat(),
                "version": "3.0.0",
                "engine": "TransportIntelligenceEngine"
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur batch TransportIntelligenceEngine: {e}")
            
            return {
                "scores": {},
                "error": str(e),
                "batch_analytics": {"error": "Batch processing failed"},
                "processing_stats": {"total_jobs": len(jobs_data), "successful_jobs": 0, "failed_jobs": len(jobs_data)},
                "calculated_at": datetime.now().isoformat(),
                "version": "3.0.0-error",
                "engine": "TransportIntelligenceEngine"
            }
    
    async def run_paris_validation_tests(self) -> Dict[str, Any]:
        """🧪 Tests validation avec adresses réelles Paris (mission prompt 5)
        
        Teste la précision du système avec des adresses parisiennes réelles
        pour valider l'intelligence transport V3.0
        """
        
        logger.info("🧪 Début tests validation Paris - Transport Intelligence V3.0")
        
        test_results = {
            "test_suite": "Paris Transport Intelligence Validation",
            "version": "3.0.0",
            "executed_at": datetime.now().isoformat(),
            "test_scenarios": [],
            "summary": {
                "total_tests": 0,
                "successful_tests": 0,
                "failed_tests": 0,
                "average_score": 0.0,
                "performance_metrics": {}
            }
        }
        
        # Scénarios de test avec données réalistes
        test_scenarios = [
            {
                "name": "Candidat Paris Centre → La Défense",
                "candidat": "25 avenue des Champs-Élysées, 75008 Paris",
                "entreprise": "1 Place de la Défense, 92400 Courbevoie",
                "transport_methods": ["public-transport", "vehicle"],
                "travel_times": {"public-transport": 45, "vehicle": 35},
                "context": {"parking_provided": True, "flexible_hours": True}
            },
            {
                "name": "Candidat Bastille → Châtelet (intra-Paris)",
                "candidat": "10 place de la République, 75011 Paris",
                "entreprise": "Châtelet-Les Halles, 75001 Paris",
                "transport_methods": ["public-transport", "bike", "walking"],
                "travel_times": {"public-transport": 25, "bike": 20, "walking": 45},
                "context": {"remote_days_per_week": 2}
            },
            {
                "name": "Candidat Flexible Multi-modal",
                "candidat": "45 rue de Rivoli, 75001 Paris",
                "entreprise": "Gare de Lyon, 75012 Paris",
                "transport_methods": ["public-transport", "vehicle", "bike", "walking"],
                "travel_times": {"public-transport": 30, "vehicle": 25, "bike": 20, "walking": 15},
                "context": {"supports_remote": True, "parking_provided": False}
            },
            {
                "name": "Candidat Contraintes Strictes",
                "candidat": "123 boulevard Saint-Germain, 75006 Paris",
                "entreprise": "Montparnasse, 75014 Paris",
                "transport_methods": ["vehicle"],
                "travel_times": {"vehicle": 20},
                "context": {"flexible_hours": False, "parking_provided": True}
            }
        ]
        
        # Exécution des tests
        for scenario in test_scenarios:
            try:
                test_start = datetime.now()
                
                result = await self.calculate_intelligent_location_score(
                    candidat_address=scenario["candidat"],
                    entreprise_address=scenario["entreprise"],
                    transport_methods=scenario["transport_methods"],
                    travel_times=scenario["travel_times"],
                    context=scenario["context"]
                )
                
                test_duration = (datetime.now() - test_start).total_seconds()
                
                # Analyse résultat test
                test_analysis = {
                    "scenario": scenario["name"],
                    "status": "SUCCESS" if not result.get("error") else "FAILED",
                    "final_score": result.get("final_score", 0.0),
                    "compatible_modes": result.get("compatibility_analysis", {}).get("compatible_modes", []),
                    "best_transport": result.get("best_transport_option", {}),
                    "performance": {
                        "calculation_time_seconds": test_duration,
                        "google_maps_calls": len(result.get("all_routes", {}))
                    },
                    "intelligence_validation": {
                        "has_real_routes": len(result.get("all_routes", {})) > 0,
                        "flexibility_bonus_applied": result.get("score_breakdown", {}).get("flexibility_bonus", 0) > 0,
                        "context_bonuses_applied": len(result.get("recommendations", [])) > 0
                    }
                }
                
                test_results["test_scenarios"].append(test_analysis)
                
                if test_analysis["status"] == "SUCCESS":
                    test_results["summary"]["successful_tests"] += 1
                else:
                    test_results["summary"]["failed_tests"] += 1
                
                test_results["summary"]["total_tests"] += 1
                
                logger.info(f"✅ Test '{scenario['name']}': score {result.get('final_score', 0):.3f}")
                
            except Exception as e:
                logger.error(f"❌ Test '{scenario['name']}' failed: {e}")
                
                test_results["test_scenarios"].append({
                    "scenario": scenario["name"],
                    "status": "ERROR",
                    "error": str(e),
                    "final_score": 0.0
                })
                
                test_results["summary"]["failed_tests"] += 1
                test_results["summary"]["total_tests"] += 1
        
        # Calcul métriques globales
        if test_results["summary"]["successful_tests"] > 0:
            successful_scores = [
                test["final_score"] for test in test_results["test_scenarios"] 
                if test["status"] == "SUCCESS"
            ]
            test_results["summary"]["average_score"] = sum(successful_scores) / len(successful_scores)
        
        # Rapport final
        success_rate = (
            test_results["summary"]["successful_tests"] / 
            test_results["summary"]["total_tests"] * 100
        )
        
        logger.info(
            f"🧪 Tests Paris terminés: {success_rate:.1f}% succès "
            f"(score moyen: {test_results['summary']['average_score']:.3f})"
        )
        
        return test_results
    
    def _validate_input_data(
        self, 
        candidat_address: str, 
        entreprise_address: str, 
        transport_methods: List[str], 
        travel_times: Dict[str, int]
    ):
        """✅ Validation des données d'entrée"""
        
        if not candidat_address or not candidat_address.strip():
            raise ValueError("Adresse candidat requise")
        
        if not entreprise_address or not entreprise_address.strip():
            raise ValueError("Adresse entreprise requise")
        
        if not transport_methods:
            raise ValueError("Au moins un mode de transport requis")
        
        valid_methods = ['public-transport', 'vehicle', 'bike', 'walking']
        invalid_methods = [m for m in transport_methods if m not in valid_methods]
        if invalid_methods:
            raise ValueError(f"Modes transport invalides: {invalid_methods}")
        
        if not travel_times:
            raise ValueError("Temps de trajet requis")
        
        for method in transport_methods:
            if method not in travel_times:
                raise ValueError(f"Temps manquant pour mode: {method}")
            
            if not isinstance(travel_times[method], int) or travel_times[method] <= 0:
                raise ValueError(f"Temps invalide pour {method}: {travel_times[method]}")
    
    async def _enrich_context_with_intelligence(self, context: Optional[Dict]) -> Dict:
        """🔧 Enrichissement contexte avec intelligence engine"""
        
        enriched = context.copy() if context else {}
        
        # Détection automatique caractéristiques
        if "auto_detect" not in enriched:
            enriched.update({
                "engine_version": "3.0.0",
                "intelligent_scoring_enabled": True,
                "batch_processing_compatible": True,
                "google_maps_enhanced": True
            })
        
        # Enrichissement horaires par défaut
        if "flexible_hours" not in enriched:
            enriched["flexible_hours"] = False
        
        # Enrichissement télétravail
        if "remote_days_per_week" not in enriched:
            enriched["remote_days_per_week"] = 0
        
        return enriched
    
    async def _post_process_scoring_result(
        self,
        scoring_result: Dict[str, Any],
        candidat_address: str,
        entreprise_address: str,
        context: Optional[Dict]
    ) -> Dict[str, Any]:
        """🔧 Post-traitement résultat avec enrichissements engine"""
        
        # Copie résultat de base
        enhanced_result = scoring_result.copy()
        
        # Ajout métadonnées engine
        enhanced_result["engine_metadata"] = {
            "processed_by": "TransportIntelligenceEngine",
            "version": "3.0.0",
            "candidat_address": candidat_address,
            "entreprise_address": entreprise_address,
            "processing_context": context,
            "enhancements_applied": []
        }
        
        # Enrichissement recommandations engine
        engine_recommendations = self._generate_engine_recommendations(scoring_result)
        enhanced_result["recommendations"].extend(engine_recommendations)
        enhanced_result["engine_metadata"]["enhancements_applied"].append("engine_recommendations")
        
        # Analyse intelligente patterns
        pattern_analysis = self._analyze_transport_patterns(scoring_result)
        enhanced_result["pattern_analysis"] = pattern_analysis
        enhanced_result["engine_metadata"]["enhancements_applied"].append("pattern_analysis")
        
        return enhanced_result
    
    def _generate_engine_recommendations(self, scoring_result: Dict[str, Any]) -> List[str]:
        """💡 Génération recommandations intelligentes engine"""
        
        recommendations = []
        
        final_score = scoring_result.get("final_score", 0.0)
        compatibility_analysis = scoring_result.get("compatibility_analysis", {})
        
        # Recommandations selon score
        if final_score >= 0.8:
            recommendations.append("🌟 Excellente compatibilité transport - candidat hautement recommandé")
        elif final_score >= 0.6:
            recommendations.append("✅ Bonne compatibilité transport - candidat viable")
        elif final_score >= 0.4:
            recommendations.append("⚠️ Compatibilité modérée - évaluer flexibilité candidat")
        else:
            recommendations.append("❌ Faible compatibilité transport - considérer ajustements")
        
        # Recommandations selon modes compatibles
        compatible_count = len(compatibility_analysis.get("compatible_modes", []))
        if compatible_count >= 3:
            recommendations.append("🔄 Candidate très flexible - plusieurs options transport")
        elif compatible_count == 1:
            recommendations.append("⚡ Un seul mode compatible - risque si problème transport")
        
        return recommendations
    
    def _analyze_transport_patterns(self, scoring_result: Dict[str, Any]) -> Dict[str, Any]:
        """📊 Analyse patterns transport pour insights"""
        
        compatibility_details = scoring_result.get("compatibility_analysis", {}).get("compatibility_details", {})
        
        patterns = {
            "preferred_modes": [],
            "time_efficiency_by_mode": {},
            "potential_bottlenecks": [],
            "optimization_opportunities": []
        }
        
        # Analyse efficacité par mode
        for mode, details in compatibility_details.items():
            if details.get("is_compatible", False):
                efficiency = details.get("time_efficiency", 0.0)
                patterns["time_efficiency_by_mode"][mode] = efficiency
                
                if efficiency >= 0.8:
                    patterns["preferred_modes"].append(mode)
            else:
                # Identifier bottlenecks
                if details.get("actual_time_minutes"):
                    overage = details["actual_time_minutes"] - details["time_limit_minutes"]
                    if overage <= 10:
                        patterns["optimization_opportunities"].append(
                            f"{mode}: seulement {overage}min au-dessus de la limite"
                        )
                    else:
                        patterns["potential_bottlenecks"].append(mode)
        
        return patterns
    
    async def _optimize_batch_processing(self, jobs_data: List[Dict]) -> List[Dict]:
        """⚡ Optimisation traitement batch"""
        
        # Pour l'instant, retourne les données telles quelles
        # TODO: Implémenter grouping intelligent par zones géographiques
        return jobs_data
    
    async def _analyze_batch_results(self, results: Dict[str, Any], start_time: datetime) -> Dict[str, Any]:
        """📊 Analyse résultats batch pour insights"""
        
        total_time = (datetime.now() - start_time).total_seconds()
        
        if not results:
            return {"error": "No results to analyze"}
        
        scores = [r.get("final_score", 0) for r in results.values() if "final_score" in r]
        compatible_jobs = [r for r in results.values() if r.get("final_score", 0) >= 0.6]
        
        return {
            "processing_time_seconds": total_time,
            "total_jobs_processed": len(results),
            "score_distribution": {
                "average": sum(scores) / len(scores) if scores else 0,
                "min": min(scores) if scores else 0,
                "max": max(scores) if scores else 0
            },
            "compatibility_stats": {
                "compatible_jobs": len(compatible_jobs),
                "compatibility_rate": len(compatible_jobs) / len(results) if results else 0
            },
            "performance_metrics": {
                "jobs_per_second": len(results) / total_time if total_time > 0 else 0,
                "average_job_time": total_time / len(results) if results else 0
            }
        }
    
    async def _create_engine_fallback_score(
        self,
        candidat_address: str,
        entreprise_address: str,
        transport_methods: List[str],
        travel_times: Dict[str, int],
        error_message: str
    ) -> Dict[str, Any]:
        """🚨 Fallback intelligent niveau engine"""
        
        fallback_score = self.engine_config["fallback_strategy"]["fallback_score"]
        
        return {
            "final_score": fallback_score,
            "score_breakdown": {
                "final_score": fallback_score,
                "time_compatibility_score": fallback_score,
                "flexibility_bonus": 0.0,
                "efficiency_score": fallback_score,
                "reliability_score": fallback_score
            },
            "compatibility_analysis": {
                "compatible_modes": transport_methods[:1],  # Assume premier mode compatible
                "incompatible_modes": transport_methods[1:],
                "compatibility_rate": 1.0 / len(transport_methods) if transport_methods else 0.0
            },
            "explanations": [
                f"🚨 Engine fallback activé: {error_message}",
                f"📊 Score conservateur: {fallback_score}",
                "🔧 Système en mode dégradé - vérification manuelle recommandée"
            ],
            "recommendations": [
                "🛠️ Réessayer plus tard avec service complet",
                "📞 Validation manuelle transport recommandée",
                "⚠️ Score calculé en mode dégradé"
            ],
            "error": error_message,
            "fallback_mode": True,
            "engine_metadata": {
                "processed_by": "TransportIntelligenceEngine",
                "version": "3.0.0-fallback",
                "fallback_reason": error_message
            },
            "calculated_at": datetime.now().isoformat()
        }
    
    def _update_analytics(
        self, 
        result: Dict[str, Any], 
        transport_methods: List[str],
        start_time: datetime,
        success: bool
    ):
        """📈 Mise à jour analytics engine"""
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Mise à jour moyenne temps traitement
        total_requests = self.analytics["total_scoring_requests"]
        current_avg = self.analytics["average_processing_time"]
        self.analytics["average_processing_time"] = (
            (current_avg * (total_requests - 1) + processing_time) / total_requests
        )
        
        # Analytics par mode de transport
        for method in transport_methods:
            if method not in self.analytics["transport_methods_usage"]:
                self.analytics["transport_methods_usage"][method] = 0
            self.analytics["transport_methods_usage"][method] += 1
        
        # Performance par mode
        if success and "all_routes" in result:
            for mode in result["all_routes"]:
                if mode not in self.analytics["performance_by_mode"]:
                    self.analytics["performance_by_mode"][mode] = {
                        "count": 0,
                        "total_time": 0.0
                    }
                self.analytics["performance_by_mode"][mode]["count"] += 1
                self.analytics["performance_by_mode"][mode]["total_time"] += processing_time
    
    def get_engine_analytics(self) -> Dict[str, Any]:
        """📊 Analytics complètes engine pour monitoring"""
        
        # Statistiques scoring
        scoring_stats = self.location_transport_scorer_v3.get_performance_stats()
        
        # Analytics engine
        return {
            "engine_analytics": self.analytics.copy(),
            "scorer_analytics": scoring_stats,
            "configuration": self.engine_config,
            "health_status": {
                "is_healthy": self.analytics["failed_scorings"] / max(self.analytics["total_scoring_requests"], 1) < 0.1,
                "success_rate": self.analytics["successful_scorings"] / max(self.analytics["total_scoring_requests"], 1),
                "average_performance": self.analytics["average_processing_time"]
            },
            "test_addresses": self.paris_test_addresses
        }
    
    def reset_analytics(self):
        """🔄 Reset analytics (pour tests/maintenance)"""
        
        self.analytics = {
            "total_scoring_requests": 0,
            "successful_scorings": 0,
            "failed_scorings": 0,
            "batch_operations": 0,
            "average_processing_time": 0.0,
            "google_maps_api_calls": 0,
            "cache_efficiency": {"hits": 0, "misses": 0},
            "transport_methods_usage": {},
            "performance_by_mode": {}
        }
        
        self.location_transport_scorer_v3.clear_cache()
        logger.info("Analytics TransportIntelligenceEngine réinitialisées")
