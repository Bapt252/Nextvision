"""
🚀 Nextvision V3.0 - LocationTransportScorerV3 (PROMPT 5)
Révolution du scoring géographique avec Transport Intelligence

REMPLACE: LocationScorer V2.0 basique (bidirectional_scorer.py)
NOUVEAU: Intelligence Google Maps + nouvelles données questionnaire

Author: NEXTEN Team  
Version: 3.0.0 - Transport Intelligence Revolution
Architecture: GoogleMapsService + TransportCalculator + nouvelles données
"""

import asyncio
import nextvision_logging as logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import hashlib

# IMPORTS ABSOLUS (CORRIGÉS OPTION 1)
from nextvision.services.google_maps_service import GoogleMapsService
from nextvision.services.transport_calculator import TransportCalculator
from nextvision.models.transport_models import (
    TravelMode, TransportRoute, GeocodeResult, 
    TransportCompatibility, LocationScore
)

logger = logging.getLogger(__name__)

class LocationTransportScorerV3:
    """🚀 Scorer Localisation V3.0 - Transport Intelligence Revolution
    
    RÉVOLUTIONNE le scoring géographique avec :
    - Temps de trajet réels Google Maps
    - Support transport_methods + travel_times du questionnaire
    - Intelligence multi-modale avec bonus flexibilité  
    - Cache optimisé + fallback intelligent
    """
    
    def __init__(self, google_maps_service: GoogleMapsService, 
                 transport_calculator: TransportCalculator):
        self.google_maps_service = google_maps_service
        self.transport_calculator = transport_calculator
        
        # Cache intelligent LocationTransportScorerV3
        self._scoring_cache: Dict[str, Dict] = {}
        self._batch_results_cache: Dict[str, Dict] = {}
        
        # Configuration scoring avancé
        self.scoring_config = {
            "weights": {
                "time_compatibility": 0.50,    # Temps acceptables vs réels
                "flexibility_bonus": 0.25,     # Bonus multi-modes
                "travel_efficiency": 0.15,     # Efficacité trajet
                "reliability_factor": 0.10     # Fiabilité mode transport
            },
            "flexibility_multipliers": {
                1: 1.0,    # Un seul mode = pas de bonus
                2: 1.15,   # Deux modes = +15%
                3: 1.25,   # Trois modes = +25%
                4: 1.35    # Quatre modes = +35%
            }
        }
        
        # Mapping nouvelles données questionnaire → Google Maps
        self.transport_method_mapping = {
            'public-transport': TravelMode.TRANSIT,
            'vehicle': TravelMode.DRIVING,
            'bike': TravelMode.BICYCLING,
            'walking': TravelMode.WALKING
        }
        
        # Métriques performance
        self.scoring_stats = {
            "total_calculations": 0,
            "cache_hits": 0,
            "google_maps_calls": 0,
            "fallback_activations": 0,
            "average_calculation_time": 0.0
        }
    
    async def calculate_location_transport_score_v3(
        self,
        candidat_address: str,
        entreprise_address: str,
        transport_methods: List[str],  # ['public-transport', 'vehicle', 'bike', 'walking']
        travel_times: Dict[str, int],  # {'public-transport': 30, 'vehicle': 25, 'bike': 20, 'walking': 15}
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """🎯 Calcule score localisation V3.0 avec Transport Intelligence
        
        Args:
            candidat_address: Adresse exacte candidat (Google Maps autocomplete)
            entreprise_address: Adresse exacte entreprise
            transport_methods: Liste modes transport candidat
            travel_times: Temps max acceptés par mode
            context: Contexte additionnel (télétravail, etc.)
            
        Returns:
            Score enrichi avec détails intelligence transport
        """
        
        start_time = datetime.now()
        self.scoring_stats["total_calculations"] += 1
        
        try:
            # 1. Vérification cache intelligent
            cache_key = self._create_cache_key(
                candidat_address, entreprise_address, transport_methods, travel_times
            )
            
            if cache_key in self._scoring_cache:
                self.scoring_stats["cache_hits"] += 1
                cached_result = self._scoring_cache[cache_key]
                if self._is_cache_valid(cached_result["calculated_at"]):
                    logger.debug(f"Cache hit V3: {candidat_address} → {entreprise_address}")
                    return cached_result
            
            # 2. Géocodage adresses avec Google Maps
            candidat_location, entreprise_location = await self._geocode_addresses_parallel(
                candidat_address, entreprise_address
            )
            
            # 3. Calcul itinéraires réels Google Maps par mode
            routes_by_mode = await self._calculate_real_routes_by_transport_methods(
                candidat_location, entreprise_location, transport_methods
            )
            
            # 4. Évaluation compatibilité selon temps acceptables
            compatibility_analysis = self._analyze_transport_compatibility_v3(
                routes_by_mode, transport_methods, travel_times
            )
            
            # 5. Calcul score V3.0 avec intelligence
            transport_score = self._calculate_transport_intelligence_score(
                compatibility_analysis, context
            )
            
            # 6. Enrichissement avec explications détaillées
            enriched_result = await self._enrich_scoring_result_v3(
                transport_score, routes_by_mode, compatibility_analysis, context
            )
            
            # 7. Mise en cache avec expiration intelligente
            self._cache_scoring_result(cache_key, enriched_result)
            
            # 8. Métriques performance
            calculation_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_stats(calculation_time)
            
            logger.info(
                f"🚀 LocationTransportScorerV3: {transport_score['final_score']:.3f} "
                f"({len(compatibility_analysis['compatible_modes'])}/"
                f"{len(transport_methods)} modes, {calculation_time:.2f}s)"
            )
            
            return enriched_result
            
        except Exception as e:
            logger.error(f"❌ Erreur LocationTransportScorerV3: {e}")
            self.scoring_stats["fallback_activations"] += 1
            
            # Fallback intelligent
            return await self._create_intelligent_fallback_score(
                candidat_address, entreprise_address, transport_methods, travel_times, str(e)
            )
    
    async def batch_calculate_location_scores_v3(
        self,
        candidat_address: str,
        jobs_data: List[Dict],  # [{"address": "...", "transport_methods": [...], "travel_times": {...}}, ...]
        max_concurrent: int = 5
    ) -> Dict[str, Dict]:
        """🚀 Calcul batch optimisé V3.0 pour performance maximale"""
        
        logger.info(f"🚀 Batch LocationTransportScorerV3: {len(jobs_data)} jobs, max_concurrent={max_concurrent}")
        
        # Géocodage candidat une seule fois
        candidat_location = await self.google_maps_service.geocode_address(candidat_address)
        
        # Préparation tâches avec limitation concurrence
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def calculate_single_job_score(job_data: Dict) -> Tuple[str, Dict]:
            async with semaphore:
                job_address = job_data["address"]
                transport_methods = job_data.get("transport_methods", ["public-transport", "vehicle"])
                travel_times = job_data.get("travel_times", {"public-transport": 45, "vehicle": 45})
                context = job_data.get("context", {})
                
                score = await self.calculate_location_transport_score_v3(
                    candidat_address, job_address, transport_methods, travel_times, context
                )
                return job_address, score
        
        # Exécution batch avec gestion erreurs
        tasks = [calculate_single_job_score(job_data) for job_data in jobs_data]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Assemblage résultats
        batch_scores = {}
        successful_scores = 0
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Erreur batch job: {result}")
                continue
                
            job_address, score = result
            batch_scores[job_address] = score
            successful_scores += 1
        
        logger.info(f"✅ Batch terminé: {successful_scores}/{len(jobs_data)} scores calculés")
        
        return batch_scores
    
    async def _geocode_addresses_parallel(
        self, candidat_address: str, entreprise_address: str
    ) -> Tuple[GeocodeResult, GeocodeResult]:
        """📍 Géocodage parallèle optimisé"""
        
        tasks = [
            self.google_maps_service.geocode_address(candidat_address),
            self.google_maps_service.geocode_address(entreprise_address)
        ]
        
        candidat_location, entreprise_location = await asyncio.gather(*tasks)
        self.scoring_stats["google_maps_calls"] += 2
        
        return candidat_location, entreprise_location
    
    async def _calculate_real_routes_by_transport_methods(
        self,
        candidat_location: GeocodeResult,
        entreprise_location: GeocodeResult,
        transport_methods: List[str]
    ) -> Dict[str, TransportRoute]:
        """🗺️ Calcul itinéraires réels Google Maps par mode transport candidat"""
        
        routes_by_mode = {}
        
        # Conversion transport_methods → Google Maps TravelMode
        travel_modes = []
        for method in transport_methods:
            if method in self.transport_method_mapping:
                travel_modes.append(self.transport_method_mapping[method])
        
        if not travel_modes:
            logger.warning(f"Aucun mode transport reconnu dans: {transport_methods}")
            return routes_by_mode
        
        # Calcul parallèle des itinéraires réels
        route_tasks = []
        for travel_mode in travel_modes:
            task = self.google_maps_service.calculate_route(
                candidat_location, entreprise_location, travel_mode
            )
            route_tasks.append((travel_mode, task))
        
        # Exécution avec gestion erreurs
        for travel_mode, task in route_tasks:
            try:
                route = await task
                
                # Mapping inverse TravelMode → transport_method pour cohérence
                method_name = self._map_travel_mode_to_transport_method(travel_mode)
                routes_by_mode[method_name] = route
                
                self.scoring_stats["google_maps_calls"] += 1
                
            except Exception as e:
                logger.error(f"Erreur calcul route {travel_mode.value}: {e}")
                continue
        
        return routes_by_mode
    
    def _analyze_transport_compatibility_v3(
        self,
        routes_by_mode: Dict[str, TransportRoute],
        transport_methods: List[str],
        travel_times: Dict[str, int]
    ) -> Dict[str, Any]:
        """🎯 Analyse compatibilité V3.0 - temps acceptables vs temps réels"""
        
        compatible_modes = []
        incompatible_modes = []
        compatibility_details = {}
        
        for method in transport_methods:
            time_limit = travel_times.get(method, 60)  # Default 60min
            
            if method in routes_by_mode:
                route = routes_by_mode[method]
                actual_time = route.duration_minutes
                
                is_compatible = actual_time <= time_limit
                
                compatibility_details[method] = {
                    "actual_time_minutes": actual_time,
                    "time_limit_minutes": time_limit,
                    "is_compatible": is_compatible,
                    "time_efficiency": min(1.0, time_limit / max(actual_time, 1)),
                    "route_details": {
                        "distance_km": route.distance_km,
                        "has_traffic_delay": (
                            route.traffic and route.traffic.delay_minutes > 5
                        ) if route.traffic else False
                    }
                }
                
                if is_compatible:
                    compatible_modes.append(method)
                else:
                    incompatible_modes.append(method)
                    
            else:
                # Mode sans route calculée (erreur Google Maps)
                compatibility_details[method] = {
                    "actual_time_minutes": None,
                    "time_limit_minutes": time_limit,
                    "is_compatible": False,
                    "time_efficiency": 0.0,
                    "error": "Itinéraire non calculable"
                }
                incompatible_modes.append(method)
        
        return {
            "compatible_modes": compatible_modes,
            "incompatible_modes": incompatible_modes,
            "compatibility_details": compatibility_details,
            "compatibility_rate": len(compatible_modes) / len(transport_methods) if transport_methods else 0.0
        }
    
    def _calculate_transport_intelligence_score(
        self,
        compatibility_analysis: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """🧠 Calcul score avec intelligence transport V3.0"""
        
        compatible_modes = compatibility_analysis["compatible_modes"]
        compatibility_details = compatibility_analysis["compatibility_details"]
        
        if not compatible_modes:
            return {
                "final_score": 0.0,
                "time_compatibility_score": 0.0,
                "flexibility_bonus": 0.0,
                "efficiency_score": 0.0,
                "reliability_score": 0.0,
                "explanation": "Aucun mode de transport compatible"
            }
        
        # 1. Score compatibilité temps (50% du score total)
        time_compatibility_score = compatibility_analysis["compatibility_rate"]
        
        # 2. Bonus flexibilité selon nombre de modes compatibles (25% du score)
        num_compatible = len(compatible_modes)
        flexibility_multiplier = self.scoring_config["flexibility_multipliers"].get(
            num_compatible, 1.0
        )
        flexibility_bonus = (flexibility_multiplier - 1.0) * 2.5  # Conversion en score 0-1
        
        # 3. Score efficacité trajet - moyenne des efficacités (15% du score)
        efficiency_scores = [
            details["time_efficiency"] 
            for details in compatibility_details.values() 
            if details["is_compatible"]
        ]
        efficiency_score = sum(efficiency_scores) / len(efficiency_scores) if efficiency_scores else 0.0
        
        # 4. Score fiabilité - impact trafic/retards (10% du score)
        reliability_scores = []
        for method in compatible_modes:
            details = compatibility_details[method]
            route_details = details.get("route_details", {})
            
            if route_details.get("has_traffic_delay", False):
                reliability_scores.append(0.6)  # Pénalité trafic
            else:
                reliability_scores.append(0.9)  # Bon trafic
        
        reliability_score = sum(reliability_scores) / len(reliability_scores) if reliability_scores else 0.0
        
        # 5. Score final pondéré selon configuration
        weights = self.scoring_config["weights"]
        final_score = (
            time_compatibility_score * weights["time_compatibility"] +
            flexibility_bonus * weights["flexibility_bonus"] +
            efficiency_score * weights["travel_efficiency"] +
            reliability_score * weights["reliability_factor"]
        )
        
        # 6. Application bonus contextuels (télétravail, etc.)
        if context:
            final_score = self._apply_contextual_bonuses(final_score, context)
        
        # Limitation score max = 1.0
        final_score = min(1.0, final_score)
        
        return {
            "final_score": final_score,
            "time_compatibility_score": time_compatibility_score,
            "flexibility_bonus": flexibility_bonus,
            "efficiency_score": efficiency_score,
            "reliability_score": reliability_score,
            "compatible_modes_count": num_compatible,
            "flexibility_multiplier": flexibility_multiplier
        }
    
    async def _enrich_scoring_result_v3(
        self,
        transport_score: Dict[str, Any],
        routes_by_mode: Dict[str, TransportRoute],
        compatibility_analysis: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """🔧 Enrichissement résultat avec détails intelligence V3.0"""
        
        # Sélection meilleur mode parmi compatibles
        best_mode = None
        best_route = None
        
        if compatibility_analysis["compatible_modes"]:
            # Mode le plus efficace parmi compatibles
            best_mode = max(
                compatibility_analysis["compatible_modes"],
                key=lambda mode: compatibility_analysis["compatibility_details"][mode]["time_efficiency"]
            )
            best_route = routes_by_mode.get(best_mode)
        
        # Construction explications détaillées
        explanations = self._generate_detailed_explanations_v3(
            transport_score, compatibility_analysis, best_mode, context
        )
        
        # Recommandations intelligentes
        recommendations = self._generate_intelligent_recommendations(
            compatibility_analysis, routes_by_mode, context
        )
        
        return {
            "final_score": transport_score["final_score"],
            "score_breakdown": transport_score,
            "compatibility_analysis": compatibility_analysis,
            "best_transport_option": {
                "mode": best_mode,
                "duration_minutes": best_route.duration_minutes if best_route else None,
                "distance_km": best_route.distance_km if best_route else None,
                "has_traffic_delays": (
                    best_route.traffic and best_route.traffic.delay_minutes > 5
                ) if best_route and best_route.traffic else False
            },
            "all_routes": {
                mode: {
                    "duration_minutes": route.duration_minutes,
                    "distance_km": route.distance_km,
                    "travel_mode": route.travel_mode.value
                }
                for mode, route in routes_by_mode.items()
            },
            "explanations": explanations,
            "recommendations": recommendations,
            "calculated_at": datetime.now().isoformat(),
            "version": "3.0.0",
            "scorer": "LocationTransportScorerV3"
        }
    
    def _generate_detailed_explanations_v3(
        self,
        transport_score: Dict[str, Any],
        compatibility_analysis: Dict[str, Any],
        best_mode: Optional[str],
        context: Optional[Dict]
    ) -> List[str]:
        """📝 Génération explications détaillées V3.0"""
        
        explanations = []
        
        # Score principal
        explanations.append(
            f"🎯 Score transport: {transport_score['final_score']:.2f}/1.0 "
            f"({len(compatibility_analysis['compatible_modes'])}"
            f"/{len(compatibility_analysis['compatible_modes']) + len(compatibility_analysis['incompatible_modes'])} modes compatibles)"
        )
        
        # Détail compatibilité par mode
        for mode, details in compatibility_analysis["compatibility_details"].items():
            if details["is_compatible"]:
                explanations.append(
                    f"✅ {mode}: {details['actual_time_minutes']}min ≤ {details['time_limit_minutes']}min "
                    f"(efficacité: {details['time_efficiency']:.1%})"
                )
            else:
                if details.get("error"):
                    explanations.append(f"❌ {mode}: {details['error']}")
                else:
                    explanations.append(
                        f"❌ {mode}: {details['actual_time_minutes']}min > {details['time_limit_minutes']}min"
                    )
        
        # Bonus flexibilité
        if transport_score["flexibility_bonus"] > 0:
            explanations.append(
                f"🔄 Bonus flexibilité: +{transport_score['flexibility_bonus']:.1%} "
                f"(×{transport_score['flexibility_multiplier']:.2f} pour {transport_score['compatible_modes_count']} modes)"
            )
        
        # Meilleure option
        if best_mode:
            explanations.append(f"🌟 Recommandé: {best_mode}")
        
        return explanations
    
    def _generate_intelligent_recommendations(
        self,
        compatibility_analysis: Dict[str, Any],
        routes_by_mode: Dict[str, TransportRoute],
        context: Optional[Dict]
    ) -> List[str]:
        """💡 Génération recommandations intelligentes"""
        
        recommendations = []
        
        compatible_modes = compatibility_analysis["compatible_modes"]
        incompatible_modes = compatibility_analysis["incompatible_modes"]
        
        if not compatible_modes:
            recommendations.append(
                "⚠️ Aucun mode de transport compatible - négocier télétravail ou ajuster contraintes temps"
            )
        elif len(compatible_modes) == 1:
            recommendations.append(
                f"📍 Un seul mode compatible: {compatible_modes[0]} - "
                "considérer ajouter des alternatives pour plus de flexibilité"
            )
        else:
            recommendations.append(
                f"✨ Excellente flexibilité avec {len(compatible_modes)} modes compatibles"
            )
        
        # Recommandations spécifiques par mode incompatible
        for mode in incompatible_modes:
            details = compatibility_analysis["compatibility_details"][mode]
            if not details.get("error") and details["actual_time_minutes"]:
                gap = details["actual_time_minutes"] - details["time_limit_minutes"]
                recommendations.append(
                    f"💡 {mode}: augmenter limite de {gap}min pour rendre compatible "
                    f"({details['time_limit_minutes']}min → {details['actual_time_minutes']}min)"
                )
        
        # Recommandation télétravail si contexte
        if context and context.get("supports_remote", False):
            if len(incompatible_modes) > 0:
                recommendations.append(
                    "🏠 Télétravail disponible - peut compenser trajets plus longs"
                )
        
        return recommendations
    
    def _map_travel_mode_to_transport_method(self, travel_mode: TravelMode) -> str:
        """🔄 Mapping inverse TravelMode → transport_method"""
        reverse_mapping = {
            TravelMode.TRANSIT: 'public-transport',
            TravelMode.DRIVING: 'vehicle',
            TravelMode.BICYCLING: 'bike',
            TravelMode.WALKING: 'walking'
        }
        return reverse_mapping.get(travel_mode, travel_mode.value)
    
    def _apply_contextual_bonuses(self, base_score: float, context: Dict) -> float:
        """🎁 Application bonus contextuels"""
        
        adjusted_score = base_score
        
        # Bonus télétravail
        remote_days = context.get("remote_days_per_week", 0)
        if remote_days > 0:
            remote_bonus = min(0.2, remote_days / 5 * 0.3)  # Max 20% bonus
            adjusted_score += remote_bonus
        
        # Bonus horaires flexibles
        if context.get("flexible_hours", False):
            adjusted_score += 0.1  # +10% pour flexibilité horaires
        
        # Bonus parking fourni
        if context.get("parking_provided", False):
            adjusted_score += 0.05  # +5% si parking fourni
        
        return adjusted_score
    
    async def _create_intelligent_fallback_score(
        self,
        candidat_address: str,
        entreprise_address: str,
        transport_methods: List[str],
        travel_times: Dict[str, int],
        error_message: str
    ) -> Dict[str, Any]:
        """🚨 Score fallback intelligent en cas d'erreur"""
        
        logger.warning(f"Fallback LocationTransportScorerV3: {error_message}")
        
        # Score neutre basé sur heuristiques simples
        base_score = 0.6  # Score neutre conservateur
        
        # Ajustements heuristiques
        if "paris" in candidat_address.lower() and "paris" in entreprise_address.lower():
            base_score = 0.7  # Bonus intra-Paris
        
        # Bonus si candidat accepte plusieurs modes
        if len(transport_methods) >= 3:
            base_score += 0.1  # Bonus flexibilité
        
        # Bonus si temps acceptés généreux
        avg_time_limit = sum(travel_times.values()) / len(travel_times)
        if avg_time_limit >= 45:
            base_score += 0.1  # Bonus temps généreux
        
        base_score = min(1.0, base_score)
        
        return {
            "final_score": base_score,
            "score_breakdown": {
                "final_score": base_score,
                "time_compatibility_score": base_score,
                "flexibility_bonus": 0.0,
                "efficiency_score": base_score,
                "reliability_score": base_score
            },
            "compatibility_analysis": {
                "compatible_modes": transport_methods,  # Assume tous compatibles en fallback
                "incompatible_modes": [],
                "compatibility_rate": 1.0,
                "compatibility_details": {
                    method: {
                        "actual_time_minutes": None,
                        "time_limit_minutes": travel_times.get(method, 60),
                        "is_compatible": True,
                        "time_efficiency": base_score,
                        "error": "Mode dégradé - vérification manuelle recommandée"
                    }
                    for method in transport_methods
                }
            },
            "best_transport_option": {
                "mode": transport_methods[0] if transport_methods else "vehicle",
                "duration_minutes": None,
                "distance_km": None,
                "has_traffic_delays": False
            },
            "all_routes": {},
            "explanations": [
                f"⚠️ Mode dégradé: {error_message}",
                f"📊 Score estimé: {base_score:.2f} (vérification manuelle recommandée)",
                "🔧 Service Google Maps temporairement indisponible"
            ],
            "recommendations": [
                "🛠️ Vérifier manuellement la compatibilité transport",
                "📞 Contacter candidat pour confirmer faisabilité trajet",
                "⏰ Réessayer plus tard avec service complet"
            ],
            "calculated_at": datetime.now().isoformat(),
            "version": "3.0.0-fallback",
            "scorer": "LocationTransportScorerV3",
            "error": error_message
        }
    
    def _create_cache_key(
        self,
        candidat_address: str,
        entreprise_address: str,
        transport_methods: List[str],
        travel_times: Dict[str, int]
    ) -> str:
        """🔑 Génération clé cache optimisée"""
        
        # Normalisation pour cache cohérent
        normalized_methods = sorted(transport_methods)
        normalized_times = sorted(travel_times.items())
        
        key_components = [
            candidat_address.lower().strip(),
            entreprise_address.lower().strip(),
            "|".join(normalized_methods),
            "|".join(f"{k}:{v}" for k, v in normalized_times)
        ]
        
        combined_key = "::".join(key_components)
        return hashlib.md5(combined_key.encode()).hexdigest()
    
    def _is_cache_valid(self, calculated_at: str) -> bool:
        """⏰ Vérification validité cache (2h pour itinéraires)"""
        try:
            cache_time = datetime.fromisoformat(calculated_at.replace('Z', '+00:00'))
            return datetime.now() - cache_time < timedelta(hours=2)
        except:
            return False
    
    def _cache_scoring_result(self, cache_key: str, result: Dict):
        """💾 Mise en cache avec limitation taille"""
        
        # Limitation taille cache (max 1000 entrées)
        if len(self._scoring_cache) > 1000:
            # Suppression 20% des plus anciennes entrées
            sorted_entries = sorted(
                self._scoring_cache.items(),
                key=lambda x: x[1].get("calculated_at", "")
            )
            
            for old_key, _ in sorted_entries[:200]:
                del self._scoring_cache[old_key]
        
        self._scoring_cache[cache_key] = result
    
    def _update_performance_stats(self, calculation_time: float):
        """📊 Mise à jour statistiques performance"""
        
        total = self.scoring_stats["total_calculations"]
        current_avg = self.scoring_stats["average_calculation_time"]
        
        # Moyenne mobile
        self.scoring_stats["average_calculation_time"] = (
            (current_avg * (total - 1) + calculation_time) / total
        )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """📈 Statistiques performance pour monitoring"""
        
        cache_hit_rate = 0.0
        if self.scoring_stats["total_calculations"] > 0:
            cache_hit_rate = (
                self.scoring_stats["cache_hits"] / 
                self.scoring_stats["total_calculations"] * 100
            )
        
        return {
            "scoring_stats": self.scoring_stats.copy(),
            "cache_stats": {
                "cache_size": len(self._scoring_cache),
                "cache_hit_rate_percent": cache_hit_rate
            },
            "configuration": self.scoring_config,
            "transport_method_mapping": self.transport_method_mapping
        }
    
    def clear_cache(self):
        """🧹 Nettoyage cache (maintenance/tests)"""
        
        self._scoring_cache.clear()
        self._batch_results_cache.clear()
        logger.info("Cache LocationTransportScorerV3 nettoyé")
