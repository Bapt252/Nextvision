"""
🎯 Nextvision - Location Scoring Avancé
Enrichissement du composant "localisation" (7/7) avec intelligence géospatiale

Author: NEXTEN Team
Version: 2.0.0 (Prompt 2)
Integration: Google Maps Intelligence + Pondération Adaptative Existante
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from ..models.transport_models import (
    CandidatTransportProfile, JobTransportInfo, TransportMatchingResult,
    GoogleMapsMode, TransportAnalysis
)
from ..config import get_config

logger = logging.getLogger(__name__)

class LocationScoreType(str, Enum):
    """📊 Types de scores de localisation"""
    DISTANCE_BASED = "distance_based"
    TIME_BASED = "time_based"
    MULTI_MODAL = "multi_modal"
    QUALITY_WEIGHTED = "quality_weighted"

class LocationZone(str, Enum):
    """🗺️ Zones géographiques"""
    IMMEDIATE = "immediate"      # < 15min
    CLOSE = "close"             # 15-30min
    ACCEPTABLE = "acceptable"    # 30-45min
    DISTANT = "distant"         # 45-60min
    VERY_DISTANT = "very_distant"  # > 60min

@dataclass
class LocationScoreComponents:
    """🧮 Composants détaillés du score localisation"""
    base_distance_score: float         # Score basé sur distance (0-1)
    time_efficiency_score: float       # Score efficacité temps (0-1)
    transport_quality_score: float     # Score qualité transport (0-1)
    cost_efficiency_score: float       # Score coût transport (0-1)
    flexibility_bonus: float           # Bonus flexibilité (télétravail, horaires)
    peak_hour_penalty: float           # Pénalité heures pointe
    weather_resilience: float          # Résilience conditions météo
    accessibility_score: float         # Score accessibilité
    
    @property
    def weighted_total(self) -> float:
        """🎯 Score total pondéré"""
        return min(1.0, max(0.0, 
            self.base_distance_score * 0.20 +
            self.time_efficiency_score * 0.25 +
            self.transport_quality_score * 0.20 +
            self.cost_efficiency_score * 0.10 +
            self.flexibility_bonus * 0.10 +
            self.peak_hour_penalty * 0.05 +
            self.weather_resilience * 0.05 +
            self.accessibility_score * 0.05
        ))

class LocationScoringEngine:
    """🎯 Engine de scoring localisation avancé"""
    
    def __init__(self):
        self.config = get_config()
        
        # Scoring weights par mode de transport
        self.mode_weights = {
            GoogleMapsMode.WALKING: {"health": 0.3, "eco": 0.4, "cost": 0.3},
            GoogleMapsMode.BICYCLING: {"health": 0.4, "eco": 0.4, "cost": 0.2},
            GoogleMapsMode.DRIVING: {"convenience": 0.6, "time": 0.3, "cost": 0.1},
            GoogleMapsMode.TRANSIT: {"eco": 0.3, "cost": 0.4, "social": 0.3}
        }
        
        # Seuils de distance par zone
        self.zone_thresholds = {
            LocationZone.IMMEDIATE: 15,
            LocationZone.CLOSE: 30,
            LocationZone.ACCEPTABLE: 45,
            LocationZone.DISTANT: 60,
            LocationZone.VERY_DISTANT: float('inf')
        }
    
    def _determine_location_zone(self, duration_minutes: int) -> LocationZone:
        """🗺️ Détermine la zone géographique basée sur le temps"""
        for zone, threshold in self.zone_thresholds.items():
            if duration_minutes <= threshold:
                return zone
        return LocationZone.VERY_DISTANT
    
    def _calculate_distance_score(self, transport_result: TransportMatchingResult) -> float:
        """📏 Score basé sur la distance physique"""
        if not transport_result.transport_analyses:
            return 0.5  # Score neutre si pas de données
        
        # Prendre la meilleure analyse viable
        best_analysis = transport_result.get_best_analysis()
        if not best_analysis or not best_analysis.route:
            return 0.3  # Score faible si pas d'analyse
        
        distance_km = best_analysis.route.get_distance_km()
        
        # Score dégressif basé sur la distance
        if distance_km <= 5:
            return 1.0
        elif distance_km <= 15:
            return 0.9 - (distance_km - 5) * 0.05  # -5% par km
        elif distance_km <= 30:
            return 0.6 - (distance_km - 15) * 0.02  # -2% par km
        elif distance_km <= 50:
            return 0.3 - (distance_km - 30) * 0.01  # -1% par km
        else:
            return 0.1  # Score minimal pour très longues distances
    
    def _calculate_time_efficiency_score(self, transport_result: TransportMatchingResult) -> float:
        """⏱️ Score d'efficacité temporelle"""
        if not transport_result.transport_analyses:
            return 0.5
        
        # Analyser tous les modes viables
        viable_analyses = [a for a in transport_result.transport_analyses if a.is_viable]
        if not viable_analyses:
            return 0.2
        
        # Score basé sur le meilleur temps
        best_time = min(
            a.route.get_traffic_duration_minutes() or a.route.get_duration_minutes()
            for a in viable_analyses if a.route
        )
        
        # Zone-based scoring
        zone = self._determine_location_zone(best_time)
        zone_scores = {
            LocationZone.IMMEDIATE: 1.0,
            LocationZone.CLOSE: 0.8,
            LocationZone.ACCEPTABLE: 0.6,
            LocationZone.DISTANT: 0.4,
            LocationZone.VERY_DISTANT: 0.2
        }
        
        base_score = zone_scores.get(zone, 0.2)
        
        # Bonus pour options multiples
        if len(viable_analyses) > 1:
            base_score += 0.1  # Bonus flexibilité
        
        return min(1.0, base_score)
    
    def _calculate_transport_quality_score(self, transport_result: TransportMatchingResult) -> float:
        """⭐ Score de qualité du transport"""
        if not transport_result.transport_analyses:
            return 0.5
        
        viable_analyses = [a for a in transport_result.transport_analyses if a.is_viable]
        if not viable_analyses:
            return 0.2
        
        # Score pondéré par qualité de chaque mode
        total_quality = 0
        total_weight = 0
        
        for analysis in viable_analyses:
            # Poids basé sur le score global de l'analyse
            weight = analysis.get_overall_score()
            quality = analysis.quality_score
            
            total_quality += quality * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.4
        
        average_quality = total_quality / total_weight
        
        # Bonus pour diversité des modes
        mode_diversity_bonus = min(0.2, len(viable_analyses) * 0.05)
        
        return min(1.0, average_quality + mode_diversity_bonus)
    
    def _calculate_cost_efficiency_score(self, transport_result: TransportMatchingResult) -> float:
        """💰 Score d'efficacité coût"""
        if not transport_result.transport_analyses:
            return 0.5
        
        viable_analyses = [a for a in transport_result.transport_analyses if a.is_viable]
        if not viable_analyses:
            return 0.3
        
        # Récupérer les coûts
        costs = []
        for analysis in viable_analyses:
            if analysis.cost_estimate is not None:
                costs.append(analysis.cost_estimate)
        
        if not costs:
            return 0.6  # Score neutre si pas de données coût
        
        min_cost = min(costs)
        
        # Score inversement proportionnel au coût minimum
        if min_cost <= 2.0:  # Très économique (walking, bike, transport)
            return 1.0
        elif min_cost <= 5.0:  # Économique
            return 0.8
        elif min_cost <= 10.0:  # Modéré
            return 0.6
        elif min_cost <= 20.0:  # Coûteux
            return 0.4
        else:  # Très coûteux
            return 0.2
    
    def _calculate_flexibility_bonus(self, 
                                   candidat_profile: CandidatTransportProfile,
                                   job_info: JobTransportInfo,
                                   transport_result: TransportMatchingResult) -> float:
        """🔄 Bonus pour flexibilité (télétravail, horaires)"""
        bonus = 0.0
        
        # Bonus télétravail
        if candidat_profile.accepts_remote_work and job_info.remote_policy != "none":
            remote_days = candidat_profile.remote_days_per_week
            if remote_days >= 3:
                bonus += 0.3  # Télétravail majoritaire
            elif remote_days >= 2:
                bonus += 0.2  # Télétravail partiel
            elif remote_days >= 1:
                bonus += 0.1  # Télétravail occasionnel
        
        # Bonus horaires flexibles
        if candidat_profile.flexible_hours and job_info.flexible_hours:
            bonus += 0.2  # Évite les heures de pointe
        
        # Bonus modes de transport flexibles
        viable_modes = len([a for a in transport_result.transport_analyses if a.is_viable])
        if viable_modes >= 3:
            bonus += 0.1  # Très flexible
        elif viable_modes >= 2:
            bonus += 0.05  # Flexible
        
        return min(0.5, bonus)  # Maximum 50% de bonus
    
    def _calculate_peak_hour_penalty(self, transport_result: TransportMatchingResult) -> float:
        """🚦 Pénalité pour problèmes heures de pointe"""
        if not transport_result.transport_analyses:
            return 0.0
        
        penalty = 0.0
        
        for analysis in transport_result.transport_analyses:
            if not analysis.route:
                continue
            
            normal_duration = analysis.route.get_duration_minutes()
            traffic_duration = analysis.route.get_traffic_duration_minutes()
            
            if traffic_duration and traffic_duration > normal_duration:
                # Pénalité proportionnelle à l'augmentation
                increase_ratio = (traffic_duration - normal_duration) / normal_duration
                penalty += min(0.3, increase_ratio * 0.5)  # Max 30% de pénalité
        
        return -min(0.3, penalty)  # Pénalité négative
    
    def _calculate_weather_resilience(self, transport_result: TransportMatchingResult) -> float:
        """🌧️ Score de résilience aux conditions météo"""
        if not transport_result.transport_analyses:
            return 0.5
        
        # Modes résilients aux conditions météo
        weather_resilience = {
            GoogleMapsMode.DRIVING: 0.9,
            GoogleMapsMode.TRANSIT: 0.8,
            GoogleMapsMode.WALKING: 0.3,
            GoogleMapsMode.BICYCLING: 0.2
        }
        
        viable_analyses = [a for a in transport_result.transport_analyses if a.is_viable]
        if not viable_analyses:
            return 0.3
        
        # Score pondéré par viabilité de chaque mode
        total_resilience = 0
        total_weight = 0
        
        for analysis in viable_analyses:
            mode = analysis.constraint.mode
            resilience = weather_resilience.get(mode, 0.5)
            weight = analysis.viability_score
            
            total_resilience += resilience * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.5
        
        return total_resilience / total_weight
    
    def _calculate_accessibility_score(self, transport_result: TransportMatchingResult) -> float:
        """♿ Score d'accessibilité"""
        if not transport_result.transport_analyses:
            return 0.8  # Score neutre par défaut
        
        accessibility_issues = 0
        total_analyses = len(transport_result.transport_analyses)
        
        for analysis in transport_result.transport_analyses:
            if analysis.has_accessibility_issues:
                accessibility_issues += 1
        
        if total_analyses == 0:
            return 0.8
        
        # Score inversement proportionnel aux problèmes
        accessibility_ratio = 1 - (accessibility_issues / total_analyses)
        return max(0.3, accessibility_ratio)
    
    def calculate_enhanced_location_score(self,
                                        candidat_profile: CandidatTransportProfile,
                                        job_info: JobTransportInfo,
                                        transport_result: TransportMatchingResult,
                                        score_type: LocationScoreType = LocationScoreType.QUALITY_WEIGHTED) -> Tuple[float, LocationScoreComponents, Dict]:
        """🎯 Calcul du score de localisation enrichi"""
        
        start_time = datetime.now()
        
        try:
            # Calcul des composants
            components = LocationScoreComponents(
                base_distance_score=self._calculate_distance_score(transport_result),
                time_efficiency_score=self._calculate_time_efficiency_score(transport_result),
                transport_quality_score=self._calculate_transport_quality_score(transport_result),
                cost_efficiency_score=self._calculate_cost_efficiency_score(transport_result),
                flexibility_bonus=self._calculate_flexibility_bonus(candidat_profile, job_info, transport_result),
                peak_hour_penalty=self._calculate_peak_hour_penalty(transport_result),
                weather_resilience=self._calculate_weather_resilience(transport_result),
                accessibility_score=self._calculate_accessibility_score(transport_result)
            )
            
            # Score final selon le type
            if score_type == LocationScoreType.DISTANCE_BASED:
                final_score = components.base_distance_score
            elif score_type == LocationScoreType.TIME_BASED:
                final_score = components.time_efficiency_score
            elif score_type == LocationScoreType.MULTI_MODAL:
                final_score = (components.transport_quality_score + components.flexibility_bonus) / 2
            else:  # QUALITY_WEIGHTED
                final_score = components.weighted_total
            
            # Métadonnées détaillées
            metadata = {
                "calculation_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
                "score_type": score_type.value,
                "location_zone": self._determine_location_zone(
                    transport_result.get_best_analysis().route.get_duration_minutes()
                    if transport_result.get_best_analysis() and transport_result.get_best_analysis().route
                    else 60
                ).value,
                "viable_transport_modes": len([a for a in transport_result.transport_analyses if a.is_viable]),
                "has_remote_work_bonus": candidat_profile.accepts_remote_work and job_info.remote_policy != "none",
                "best_transport_mode": transport_result.best_transport_mode.value if transport_result.best_transport_mode else None,
                "transport_diversity_bonus": len([a for a in transport_result.transport_analyses if a.is_viable]) * 0.05,
                "explanation": self._generate_score_explanation(components, transport_result)
            }
            
            logger.debug(f"🎯 Location score calculé: {final_score:.3f} ({score_type.value})")
            
            return final_score, components, metadata
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul location score: {e}")
            
            # Score par défaut en cas d'erreur
            default_components = LocationScoreComponents(
                base_distance_score=0.5,
                time_efficiency_score=0.5,
                transport_quality_score=0.5,
                cost_efficiency_score=0.5,
                flexibility_bonus=0.0,
                peak_hour_penalty=0.0,
                weather_resilience=0.5,
                accessibility_score=0.8
            )
            
            return 0.5, default_components, {
                "error": str(e),
                "fallback_score": True
            }
    
    def _generate_score_explanation(self, 
                                  components: LocationScoreComponents,
                                  transport_result: TransportMatchingResult) -> str:
        """📝 Génère une explication du score"""
        
        explanations = []
        
        # Distance
        if components.base_distance_score >= 0.8:
            explanations.append("très proche")
        elif components.base_distance_score >= 0.6:
            explanations.append("proche")
        elif components.base_distance_score >= 0.4:
            explanations.append("distance acceptable")
        else:
            explanations.append("distant")
        
        # Transport
        viable_count = len([a for a in transport_result.transport_analyses if a.is_viable])
        if viable_count >= 3:
            explanations.append("excellentes options transport")
        elif viable_count >= 2:
            explanations.append("bonnes options transport")
        elif viable_count >= 1:
            explanations.append("transport limité")
        else:
            explanations.append("transport difficile")
        
        # Flexibilité
        if components.flexibility_bonus >= 0.2:
            explanations.append("très flexible (télétravail/horaires)")
        elif components.flexibility_bonus >= 0.1:
            explanations.append("flexible")
        
        # Coût
        if components.cost_efficiency_score >= 0.8:
            explanations.append("économique")
        elif components.cost_efficiency_score <= 0.4:
            explanations.append("coûteux")
        
        return ", ".join(explanations)
    
    def integrate_with_adaptive_weighting(self,
                                        original_location_score: float,
                                        enhanced_score: float,
                                        components: LocationScoreComponents,
                                        pourquoi_ecoute: str) -> Tuple[float, Dict]:
        """🔗 Intégration avec la pondération adaptative existante"""
        
        # Coefficients d'intégration selon la raison d'écoute
        integration_weights = {
            "Poste trop loin de mon domicile": {
                "enhanced_weight": 0.8,    # Prioriser score enrichi
                "original_weight": 0.2,
                "bonus_factors": ["time_efficiency", "flexibility"]
            },
            "Manque de flexibilité": {
                "enhanced_weight": 0.6,
                "original_weight": 0.4,
                "bonus_factors": ["flexibility", "transport_quality"]
            },
            "Rémunération trop faible": {
                "enhanced_weight": 0.3,    # Score enrichi moins important
                "original_weight": 0.7,
                "bonus_factors": ["cost_efficiency"]
            },
            "default": {
                "enhanced_weight": 0.5,
                "original_weight": 0.5,
                "bonus_factors": []
            }
        }
        
        weights = integration_weights.get(pourquoi_ecoute, integration_weights["default"])
        
        # Score hybride
        hybrid_score = (
            enhanced_score * weights["enhanced_weight"] +
            original_location_score * weights["original_weight"]
        )
        
        # Bonus contextuels
        bonus = 0.0
        for factor in weights["bonus_factors"]:
            if factor == "time_efficiency":
                bonus += components.time_efficiency_score * 0.1
            elif factor == "flexibility":
                bonus += components.flexibility_bonus * 0.2
            elif factor == "transport_quality":
                bonus += components.transport_quality_score * 0.1
            elif factor == "cost_efficiency":
                bonus += components.cost_efficiency_score * 0.1
        
        final_score = min(1.0, hybrid_score + bonus)
        
        integration_metadata = {
            "hybrid_composition": {
                "enhanced_contribution": enhanced_score * weights["enhanced_weight"],
                "original_contribution": original_location_score * weights["original_weight"],
                "contextual_bonus": bonus
            },
            "adaptation_reason": pourquoi_ecoute,
            "enhancement_impact": enhanced_score - original_location_score,
            "final_improvement": final_score - original_location_score
        }
        
        return final_score, integration_metadata

# Fonctions helper pour intégration avec l'existant

def enhance_location_component_score(candidat_profile: CandidatTransportProfile,
                                   job_info: JobTransportInfo,
                                   transport_result: TransportMatchingResult,
                                   original_score: float,
                                   pourquoi_ecoute: str) -> Tuple[float, Dict]:
    """🚀 Fonction principale d'enrichissement du score localisation"""
    
    engine = LocationScoringEngine()
    
    # Calcul score enrichi
    enhanced_score, components, metadata = engine.calculate_enhanced_location_score(
        candidat_profile=candidat_profile,
        job_info=job_info,
        transport_result=transport_result,
        score_type=LocationScoreType.QUALITY_WEIGHTED
    )
    
    # Intégration avec pondération adaptative
    final_score, integration_metadata = engine.integrate_with_adaptive_weighting(
        original_location_score=original_score,
        enhanced_score=enhanced_score,
        components=components,
        pourquoi_ecoute=pourquoi_ecoute
    )
    
    # Métadonnées complètes
    complete_metadata = {
        "enhanced_scoring": metadata,
        "integration": integration_metadata,
        "score_breakdown": components.__dict__,
        "enhancement_summary": {
            "original_score": original_score,
            "enhanced_score": enhanced_score,
            "final_score": final_score,
            "improvement": final_score - original_score
        }
    }
    
    logger.info(f"🎯 Location score enrichi: {original_score:.3f} → {final_score:.3f} (+{final_score-original_score:.3f})")
    
    return final_score, complete_metadata

def get_location_zone_recommendation(transport_result: TransportMatchingResult) -> Dict:
    """🗺️ Recommandations basées sur la zone géographique"""
    
    engine = LocationScoringEngine()
    
    if not transport_result.transport_analyses:
        return {"zone": "unknown", "recommendation": "Données insuffisantes"}
    
    best_analysis = transport_result.get_best_analysis()
    if not best_analysis or not best_analysis.route:
        return {"zone": "unknown", "recommendation": "Aucun transport viable"}
    
    duration = best_analysis.route.get_traffic_duration_minutes() or best_analysis.route.get_duration_minutes()
    zone = engine._determine_location_zone(duration)
    
    recommendations = {
        LocationZone.IMMEDIATE: {
            "message": "🟢 Localisation excellente - Très proche",
            "suggestions": ["Envisager marche à pied ou vélo", "Horaires flexibles recommandés"]
        },
        LocationZone.CLOSE: {
            "message": "🟡 Bonne localisation - Trajet court",
            "suggestions": ["Transport en commun efficace", "Covoiturage possible"]
        },
        LocationZone.ACCEPTABLE: {
            "message": "🟠 Localisation acceptable - Trajet modéré", 
            "suggestions": ["Négocier télétravail partiel", "Éviter heures de pointe"]
        },
        LocationZone.DISTANT: {
            "message": "🔴 Localisation éloignée - Long trajet",
            "suggestions": ["Télétravail fortement recommandé", "Horaires décalés"]
        },
        LocationZone.VERY_DISTANT: {
            "message": "⚫ Localisation très éloignée - Trajet difficile",
            "suggestions": ["Télétravail majoritaire nécessaire", "Évaluer déménagement"]
        }
    }
    
    recommendation = recommendations.get(zone, recommendations[LocationZone.ACCEPTABLE])
    
    return {
        "zone": zone.value,
        "duration_minutes": duration,
        "recommendation": recommendation["message"],
        "suggestions": recommendation["suggestions"],
        "viable_modes": [a.constraint.mode.value for a in transport_result.transport_analyses if a.is_viable]
    }
