"""
🧮 Nextvision - Service Calcul Transport Intelligent
Calculs avancés de transport avec prise en compte multi-modale, heures de pointe, coûts et scoring

Author: NEXTEN Team
Version: 2.0.0 (Prompt 2)  
Features: Multi-modal, Peak hours, Cost estimation, Quality scoring, Weather adjustments
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

from ..models.transport_models import (
    GoogleMapsMode, TransportConstraint, TransportAnalysis, TransportRoute,
    CandidatTransportProfile, JobTransportInfo, TransportMatchingResult,
    TransportQuality, GeocodeResult
)
from ..config import get_config, GoogleMapsProductionConfig
from .google_maps_service import GoogleMapsService

logger = logging.getLogger(__name__)

class WeatherCondition(str, Enum):
    """🌤️ Conditions météorologiques"""
    SUNNY = "sunny"
    RAINY = "rainy"
    SNOWY = "snowy"
    STORMY = "stormy"
    FOGGY = "foggy"

class TimeOfDay(str, Enum):
    """🕐 Périodes de la journée"""
    EARLY_MORNING = "early_morning"  # 5h-7h
    MORNING_PEAK = "morning_peak"    # 7h-10h
    MIDDAY = "midday"               # 10h-16h
    EVENING_PEAK = "evening_peak"   # 16h-19h
    EVENING = "evening"             # 19h-23h
    NIGHT = "night"                 # 23h-5h

class TransportCalculatorService:
    """🧮 Service de calcul transport intelligent"""
    
    def __init__(self, 
                 google_maps_service: Optional[GoogleMapsService] = None,
                 config: Optional[GoogleMapsProductionConfig] = None):
        self.google_maps = google_maps_service
        self.config = config or get_config()
        
        # Métriques de performance
        self.calculation_stats = {
            "total_calculations": 0,
            "multi_modal_calculations": 0,
            "weather_adjustments": 0,
            "peak_hour_calculations": 0
        }
    
    async def __aenter__(self):
        """🔌 Initialisation async"""
        if not self.google_maps:
            from .google_maps_service import get_google_maps_service
            self.google_maps = await get_google_maps_service()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """🔌 Nettoyage async"""
        pass
    
    def _get_time_of_day(self, dt: datetime) -> TimeOfDay:
        """🕐 Détermine la période de la journée"""
        hour = dt.hour
        
        if 5 <= hour < 7:
            return TimeOfDay.EARLY_MORNING
        elif 7 <= hour < 10:
            return TimeOfDay.MORNING_PEAK
        elif 10 <= hour < 16:
            return TimeOfDay.MIDDAY
        elif 16 <= hour < 19:
            return TimeOfDay.EVENING_PEAK
        elif 19 <= hour < 23:
            return TimeOfDay.EVENING
        else:
            return TimeOfDay.NIGHT
    
    def _estimate_weather_impact(self, 
                                mode: GoogleMapsMode, 
                                weather: WeatherCondition) -> float:
        """🌧️ Estime l'impact météo sur le temps de trajet"""
        
        impact_matrix = {
            GoogleMapsMode.WALKING: {
                WeatherCondition.SUNNY: 1.0,
                WeatherCondition.RAINY: 1.3,
                WeatherCondition.SNOWY: 1.8,
                WeatherCondition.STORMY: 2.0,
                WeatherCondition.FOGGY: 1.1
            },
            GoogleMapsMode.BICYCLING: {
                WeatherCondition.SUNNY: 1.0,
                WeatherCondition.RAINY: 1.5,
                WeatherCondition.SNOWY: 2.5,
                WeatherCondition.STORMY: 3.0,
                WeatherCondition.FOGGY: 1.2
            },
            GoogleMapsMode.DRIVING: {
                WeatherCondition.SUNNY: 1.0,
                WeatherCondition.RAINY: 1.1,
                WeatherCondition.SNOWY: 1.4,
                WeatherCondition.STORMY: 1.3,
                WeatherCondition.FOGGY: 1.2
            },
            GoogleMapsMode.TRANSIT: {
                WeatherCondition.SUNNY: 1.0,
                WeatherCondition.RAINY: 1.05,
                WeatherCondition.SNOWY: 1.2,
                WeatherCondition.STORMY: 1.1,
                WeatherCondition.FOGGY: 1.05
            }
        }
        
        return impact_matrix.get(mode, {}).get(weather, 1.0)
    
    def _calculate_transport_cost(self, 
                                 mode: GoogleMapsMode, 
                                 route: TransportRoute,
                                 time_of_day: TimeOfDay) -> float:
        """💰 Calcule le coût du transport"""
        
        distance_km = route.get_distance_km()
        duration_hours = route.get_duration_minutes() / 60
        
        if mode == GoogleMapsMode.TRANSIT:
            # Coût fixe du ticket
            base_cost = self.config.transport.cost_estimates["transit_ticket"]
            
            # Supplément zones/correspondances
            transfers = route.get_transfer_count()
            if transfers > 1:
                base_cost *= (1 + transfers * 0.1)  # +10% par correspondance
            
            return base_cost
            
        elif mode == GoogleMapsMode.DRIVING:
            # Coût carburant + usure
            fuel_cost = distance_km * self.config.transport.cost_estimates["driving_cost_per_km"]
            
            # Coût stationnement (estimé)
            parking_cost = 0
            if time_of_day in [TimeOfDay.MORNING_PEAK, TimeOfDay.EVENING_PEAK]:
                parking_cost = duration_hours * self.config.transport.cost_estimates["parking_cost_per_hour"]
            
            # Péages (estimation simple)
            toll_cost = distance_km * 0.1 if distance_km > 20 else 0
            
            return fuel_cost + parking_cost + toll_cost
            
        elif mode == GoogleMapsMode.BICYCLING:
            # Coût d'entretien minimal
            return distance_km * self.config.transport.cost_estimates["bike_maintenance_per_km"]
            
        elif mode == GoogleMapsMode.WALKING:
            # Gratuit (sauf usure chaussures 😉)
            return 0.0
        
        return 0.0
    
    def _calculate_comfort_score(self, 
                                mode: GoogleMapsMode, 
                                route: TransportRoute,
                                weather: WeatherCondition = WeatherCondition.SUNNY) -> float:
        """😌 Calcule le score de confort (0-1)"""
        
        base_comfort = {
            GoogleMapsMode.DRIVING: 0.9,
            GoogleMapsMode.TRANSIT: 0.7,
            GoogleMapsMode.WALKING: 0.5,
            GoogleMapsMode.BICYCLING: 0.6
        }
        
        comfort = base_comfort.get(mode, 0.5)
        
        # Ajustements
        if mode == GoogleMapsMode.TRANSIT:
            # Pénalité pour correspondances multiples
            transfers = route.get_transfer_count()
            comfort -= transfers * 0.15
            
            # Bonus pour lignes directes (RER, Metro)
            if any("RER" in step.instruction for step in route.steps):
                comfort += 0.1
        
        elif mode in [GoogleMapsMode.WALKING, GoogleMapsMode.BICYCLING]:
            # Impact météo significatif
            weather_factor = self._estimate_weather_impact(mode, weather)
            comfort /= weather_factor
        
        # Distance impact
        distance_km = route.get_distance_km()
        if mode == GoogleMapsMode.WALKING and distance_km > 2:
            comfort -= (distance_km - 2) * 0.1
        elif mode == GoogleMapsMode.BICYCLING and distance_km > 15:
            comfort -= (distance_km - 15) * 0.05
        
        return max(0.0, min(1.0, comfort))
    
    def _calculate_reliability_score(self, 
                                   mode: GoogleMapsMode, 
                                   route: TransportRoute,
                                   time_of_day: TimeOfDay) -> float:
        """⏰ Calcule le score de fiabilité (0-1)"""
        
        base_reliability = {
            GoogleMapsMode.WALKING: 0.95,
            GoogleMapsMode.BICYCLING: 0.90,
            GoogleMapsMode.DRIVING: 0.75,
            GoogleMapsMode.TRANSIT: 0.80
        }
        
        reliability = base_reliability.get(mode, 0.75)
        
        # Ajustements heures de pointe
        if time_of_day in [TimeOfDay.MORNING_PEAK, TimeOfDay.EVENING_PEAK]:
            if mode == GoogleMapsMode.DRIVING:
                reliability -= 0.2  # Embouteillages
            elif mode == GoogleMapsMode.TRANSIT:
                reliability -= 0.1  # Surcharge
        
        # Ajustements spécifiques
        if mode == GoogleMapsMode.TRANSIT:
            transfers = route.get_transfer_count()
            reliability -= transfers * 0.05  # Risque de retard
        
        return max(0.0, min(1.0, reliability))
    
    def _calculate_quality_score(self, 
                                mode: GoogleMapsMode, 
                                route: TransportRoute,
                                time_of_day: TimeOfDay,
                                weather: WeatherCondition = WeatherCondition.SUNNY) -> float:
        """⭐ Calcule le score de qualité global (0-1)"""
        
        # Composants du score
        duration_score = max(0, 1 - (route.get_duration_minutes() / 120))  # Pénalité après 2h
        comfort_score = self._calculate_comfort_score(mode, route, weather)
        reliability_score = self._calculate_reliability_score(mode, route, time_of_day)
        
        # Bonus/malus spécifiques
        bonus_malus = 0
        
        if mode == GoogleMapsMode.TRANSIT:
            # Bonus écologique
            bonus_malus += 0.1
            
            # Malus correspondances
            transfers = route.get_transfer_count()
            if transfers > 2:
                bonus_malus -= 0.1
        
        elif mode == GoogleMapsMode.WALKING:
            # Bonus santé et écologie
            if route.get_distance_km() <= 2:
                bonus_malus += 0.2
        
        elif mode == GoogleMapsMode.BICYCLING:
            # Bonus écologie et santé
            bonus_malus += 0.15
        
        # Score pondéré
        weights = self.config.transport.quality_weights
        quality_score = (
            duration_score * weights["duration"] +
            comfort_score * weights["comfort"] +
            reliability_score * weights["reliability"] +
            bonus_malus
        )
        
        return max(0.0, min(1.0, quality_score))
    
    async def analyze_transport_mode(self,
                                   constraint: TransportConstraint,
                                   origin: str,
                                   destination: str,
                                   departure_time: Optional[datetime] = None,
                                   weather: WeatherCondition = WeatherCondition.SUNNY) -> TransportAnalysis:
        """🔍 Analyse complète d'un mode de transport"""
        
        departure_time = departure_time or datetime.now()
        time_of_day = self._get_time_of_day(departure_time)
        
        try:
            # Calcul de l'itinéraire
            route = await self.google_maps.get_directions(
                origin=origin,
                destination=destination,
                mode=constraint.mode,
                departure_time=departure_time
            )
            
            if not route:
                return TransportAnalysis(
                    constraint=constraint,
                    route=None,
                    is_viable=False,
                    viability_score=0.0,
                    quality_score=0.0,
                    viability_reason="Aucun itinéraire trouvé",
                    quality_explanation="Itinéraire indisponible"
                )
            
            # Ajustement météo
            if weather != WeatherCondition.SUNNY:
                weather_factor = self._estimate_weather_impact(constraint.mode, weather)
                route.total_duration_seconds = int(route.total_duration_seconds * weather_factor)
                if route.duration_in_traffic_seconds:
                    route.duration_in_traffic_seconds = int(route.duration_in_traffic_seconds * weather_factor)
                self.calculation_stats["weather_adjustments"] += 1
            
            # Évaluation de viabilité
            actual_duration = route.get_traffic_duration_minutes() or route.get_duration_minutes()
            max_duration = constraint.max_duration_peak_minutes or constraint.max_duration_minutes
            
            if time_of_day in [TimeOfDay.MORNING_PEAK, TimeOfDay.EVENING_PEAK]:
                max_duration = constraint.max_duration_peak_minutes or constraint.max_duration_minutes
                self.calculation_stats["peak_hour_calculations"] += 1
            
            exceeds_duration = actual_duration > (max_duration + constraint.tolerance_minutes)
            
            # Vérifications spécifiques
            exceeds_transfers = False
            has_accessibility_issues = False
            
            if constraint.mode == GoogleMapsMode.TRANSIT:
                transfers = route.get_transfer_count()
                if constraint.max_transfers and transfers > constraint.max_transfers:
                    exceeds_transfers = True
                
                has_accessibility_issues = route.has_accessibility_issues() and constraint.wheelchair_accessible
            
            # Viabilité
            is_viable = not (exceeds_duration or exceeds_transfers or has_accessibility_issues)
            
            # Scores
            viability_score = 1.0 if is_viable else max(0, 1 - (actual_duration - max_duration) / max_duration)
            quality_score = self._calculate_quality_score(constraint.mode, route, time_of_day, weather)
            
            # Coûts et scores additionnels
            cost_estimate = self._calculate_transport_cost(constraint.mode, route, time_of_day)
            comfort_score = self._calculate_comfort_score(constraint.mode, route, weather)
            reliability_score = self._calculate_reliability_score(constraint.mode, route, time_of_day)
            
            # Explications
            viability_reason = self._generate_viability_explanation(
                is_viable, exceeds_duration, exceeds_transfers, has_accessibility_issues,
                actual_duration, max_duration, constraint
            )
            
            quality_explanation = self._generate_quality_explanation(
                constraint.mode, quality_score, comfort_score, reliability_score, route
            )
            
            analysis = TransportAnalysis(
                constraint=constraint,
                route=route,
                is_viable=is_viable,
                viability_score=viability_score,
                quality_score=quality_score,
                exceeds_duration=exceeds_duration,
                exceeds_transfers=exceeds_transfers,
                has_accessibility_issues=has_accessibility_issues,
                viability_reason=viability_reason,
                quality_explanation=quality_explanation,
                cost_estimate=cost_estimate,
                comfort_score=comfort_score,
                reliability_score=reliability_score
            )
            
            self.calculation_stats["total_calculations"] += 1
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse transport {constraint.mode}: {e}")
            
            return TransportAnalysis(
                constraint=constraint,
                route=None,
                is_viable=False,
                viability_score=0.0,
                quality_score=0.0,
                viability_reason=f"Erreur calcul: {str(e)}",
                quality_explanation="Calcul impossible"
            )
    
    def _generate_viability_explanation(self,
                                      is_viable: bool,
                                      exceeds_duration: bool,
                                      exceeds_transfers: bool,
                                      has_accessibility_issues: bool,
                                      actual_duration: int,
                                      max_duration: int,
                                      constraint: TransportConstraint) -> str:
        """📝 Génère l'explication de viabilité"""
        
        if is_viable:
            return f"✅ Compatible - {actual_duration}min ≤ {max_duration}min accepté"
        
        reasons = []
        if exceeds_duration:
            excess = actual_duration - max_duration
            reasons.append(f"Durée excessive: +{excess}min")
        
        if exceeds_transfers:
            reasons.append(f"Trop de correspondances (max: {constraint.max_transfers})")
        
        if has_accessibility_issues:
            reasons.append("Problèmes d'accessibilité")
        
        return f"❌ Non viable - {', '.join(reasons)}"
    
    def _generate_quality_explanation(self,
                                    mode: GoogleMapsMode,
                                    quality_score: float,
                                    comfort_score: float,
                                    reliability_score: float,
                                    route: TransportRoute) -> str:
        """📝 Génère l'explication de qualité"""
        
        quality_level = "Excellent" if quality_score > 0.8 else \
                       "Bon" if quality_score > 0.6 else \
                       "Moyen" if quality_score > 0.4 else "Faible"
        
        details = []
        
        if mode == GoogleMapsMode.TRANSIT:
            transfers = route.get_transfer_count()
            if transfers == 0:
                details.append("direct")
            elif transfers == 1:
                details.append("1 correspondance")
            else:
                details.append(f"{transfers} correspondances")
        
        if comfort_score > 0.8:
            details.append("confortable")
        elif comfort_score < 0.4:
            details.append("inconfortable")
        
        if reliability_score > 0.9:
            details.append("très fiable")
        elif reliability_score < 0.6:
            details.append("fiabilité limitée")
        
        detail_str = f" ({', '.join(details)})" if details else ""
        
        return f"{quality_level} - Score: {quality_score:.2f}{detail_str}"
    
    async def calculate_multi_modal_options(self,
                                          candidat_profile: CandidatTransportProfile,
                                          job_info: JobTransportInfo,
                                          departure_time: Optional[datetime] = None,
                                          weather: WeatherCondition = WeatherCondition.SUNNY) -> TransportMatchingResult:
        """🚀 Calcul multi-modal complet"""
        
        start_time = time.time()
        departure_time = departure_time or datetime.now()
        
        try:
            # Analyses par mode
            analyses = []
            
            for constraint in candidat_profile.constraints:
                analysis = await self.analyze_transport_mode(
                    constraint=constraint,
                    origin=candidat_profile.home_address,
                    destination=job_info.office_address,
                    departure_time=departure_time,
                    weather=weather
                )
                analyses.append(analysis)
            
            # Évaluation globale
            viable_analyses = [a for a in analyses if a.is_viable]
            is_compatible = len(viable_analyses) > 0
            
            # Meilleur mode
            best_mode = None
            best_analysis = None
            if viable_analyses:
                best_analysis = max(viable_analyses, key=lambda a: a.get_overall_score())
                best_mode = best_analysis.constraint.mode
            
            # Score global
            if viable_analyses:
                overall_score = max(a.get_overall_score() for a in viable_analyses)
            else:
                overall_score = 0.0
            
            # Modes recommandés (top 3)
            recommended_modes = [
                a.constraint.mode for a in 
                sorted(viable_analyses, key=lambda a: a.get_overall_score(), reverse=True)[:3]
            ]
            
            # Raisons d'exclusion
            excluded_reasons = []
            for analysis in analyses:
                if not analysis.is_viable:
                    excluded_reasons.append(
                        f"{analysis.constraint.mode.value}: {analysis.viability_reason}"
                    )
            
            # Suggestions
            remote_suggestion = None
            flexible_hours_benefit = None
            
            if not is_compatible and candidat_profile.accepts_remote_work:
                remote_suggestion = f"Télétravail {candidat_profile.remote_days_per_week}j/semaine recommandé"
            
            if any(a.exceeds_duration for a in analyses):
                flexible_hours_benefit = "Horaires flexibles réduiraient les temps de trajet"
            
            # Métriques de performance
            calculation_duration = (time.time() - start_time) * 1000
            
            result = TransportMatchingResult(
                candidat_profile=candidat_profile,
                job_info=job_info,
                transport_analyses=analyses,
                is_transport_compatible=is_compatible,
                best_transport_mode=best_mode,
                overall_transport_score=overall_score,
                recommended_modes=recommended_modes,
                excluded_reasons=excluded_reasons,
                remote_work_suggestion=remote_suggestion,
                flexible_hours_benefit=flexible_hours_benefit,
                calculation_duration_ms=calculation_duration,
                google_maps_requests=len(analyses),  # Une requête par mode
                cache_hits=0  # À implémenter avec le cache
            )
            
            self.calculation_stats["multi_modal_calculations"] += 1
            
            logger.info(
                f"🧮 Multi-modal calculé: {len(viable_analyses)}/{len(analyses)} modes viables "
                f"en {calculation_duration:.1f}ms"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul multi-modal: {e}")
            
            # Résultat d'erreur
            return TransportMatchingResult(
                candidat_profile=candidat_profile,
                job_info=job_info,
                transport_analyses=[],
                is_transport_compatible=False,
                overall_transport_score=0.0,
                recommended_modes=[],
                excluded_reasons=[f"Erreur calcul: {str(e)}"],
                calculation_duration_ms=(time.time() - start_time) * 1000
            )
    
    def get_calculation_stats(self) -> Dict:
        """📊 Statistiques des calculs"""
        return self.calculation_stats.copy()

# Fonction helper pour usage simple
async def calculate_transport_compatibility(
    candidat_address: str,
    job_address: str,
    transport_constraints: List[TransportConstraint],
    departure_time: Optional[datetime] = None
) -> TransportMatchingResult:
    """🚀 Fonction helper pour calcul de compatibilité transport"""
    
    async with TransportCalculatorService() as calculator:
        # Création profils temporaires
        candidat_profile = CandidatTransportProfile(
            home_address=candidat_address,
            constraints=transport_constraints
        )
        
        job_info = JobTransportInfo(
            job_id="temp",
            office_address=job_address
        )
        
        return await calculator.calculate_multi_modal_options(
            candidat_profile=candidat_profile,
            job_info=job_info,
            departure_time=departure_time
        )
