"""
Nextvision v3.0 - Listening Reasons Scorer
==========================================

Le "cerveau adaptatif" du système de matching V3.0
- 3% de poids direct + influence sur 97% restants = composant le plus puissant
- Pondération dynamique selon raison d'écoute candidat
- Impact systémique sur TOUS les autres composants

Author: NEXTEN Development Team
Version: 3.0 - PRIORITÉ ABSOLUE
"""

import nextvision_logging as logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import json

# Import des modèles V3.0
from ..models.extended_matching_models_v3 import (
    ExtendedMatchingProfile,
    ListeningReasonType,
    ListeningReasonProfile,
    AdaptiveWeightingConfig,
    MatchingScore
)


# ================================
# CONFIGURATION SCORER
# ================================

@dataclass
class ListeningReasonScorerConfig:
    """Configuration du scorer raison d'écoute"""
    # Poids base du composant
    base_weight: float = 0.03
    
    # Facteurs d'intensité (1-5 scale impact)
    intensity_multipliers: Dict[int, float] = field(default_factory=lambda: {
        1: 0.6,   # Faible motivation
        2: 0.8,   # Motivation modérée
        3: 1.0,   # Motivation normale
        4: 1.2,   # Forte motivation 
        5: 1.4    # Motivation exceptionnelle
    })
    
    # Bonus pour cohérence raisons primaire/secondaires
    coherence_bonus: float = 0.15
    
    # Pénalité pour incohérence
    incoherence_penalty: float = 0.25
    
    # Boost minimum/maximum pour éviter les extrêmes
    min_adaptive_weight: float = 0.05
    max_adaptive_weight: float = 0.40


# ================================
# ANALYSEUR DE COHÉRENCE
# ================================

class ListeningReasonCoherenceAnalyzer:
    """Analyse la cohérence entre raisons d'écoute et profil candidat"""
    
    def __init__(self):
        self.coherence_rules = {
            ListeningReasonType.REMUNERATION_FAIBLE: {
                "compatible_reasons": [
                    ListeningReasonType.PERSPECTIVES,
                    ListeningReasonType.POSTE_INADEQUAT
                ],
                "incompatible_reasons": [
                    ListeningReasonType.FLEXIBILITE
                ],
                "salary_indicators": ["low_satisfaction", "below_market"]
            },
            ListeningReasonType.POSTE_INADEQUAT: {
                "compatible_reasons": [
                    ListeningReasonType.PERSPECTIVES,
                    ListeningReasonType.REMUNERATION_FAIBLE
                ],
                "incompatible_reasons": [],
                "semantic_indicators": ["skill_mismatch", "underutilized"]
            },
            ListeningReasonType.LOCALISATION: {
                "compatible_reasons": [
                    ListeningReasonType.FLEXIBILITE
                ],
                "incompatible_reasons": [],
                "location_indicators": ["long_commute", "relocation_desired"]
            },
            ListeningReasonType.FLEXIBILITE: {
                "compatible_reasons": [
                    ListeningReasonType.LOCALISATION
                ],
                "incompatible_reasons": [
                    ListeningReasonType.REMUNERATION_FAIBLE
                ],
                "modality_indicators": ["remote_preference", "schedule_flexibility"]
            },
            ListeningReasonType.PERSPECTIVES: {
                "compatible_reasons": [
                    ListeningReasonType.REMUNERATION_FAIBLE,
                    ListeningReasonType.POSTE_INADEQUAT
                ],
                "incompatible_reasons": [],
                "career_indicators": ["growth_stagnation", "skill_development"]
            }
        }
    
    def analyze_coherence(self, profile: ExtendedMatchingProfile) -> Dict[str, Any]:
        """Analyse la cohérence globale du profil avec les raisons d'écoute"""
        
        primary_reason = profile.listening_reason.primary_reason
        secondary_reasons = profile.listening_reason.secondary_reasons
        
        coherence_score = 1.0
        analysis = {
            "primary_reason": primary_reason.value,
            "coherence_score": coherence_score,
            "coherence_factors": [],
            "recommendations": []
        }
        
        # Analyse cohérence raisons primaire/secondaires
        if primary_reason in self.coherence_rules:
            rules = self.coherence_rules[primary_reason]
            
            for secondary in secondary_reasons:
                if secondary in rules["compatible_reasons"]:
                    coherence_score += 0.1
                    analysis["coherence_factors"].append(f"Compatible: {secondary.value}")
                elif secondary in rules["incompatible_reasons"]:
                    coherence_score -= 0.2
                    analysis["coherence_factors"].append(f"Incohérent: {secondary.value}")
        
        # Analyse cohérence avec profil salaire (si raison = rémunération)
        if primary_reason == ListeningReasonType.REMUNERATION_FAIBLE:
            salary_coherence = self._analyze_salary_coherence(profile)
            coherence_score *= salary_coherence["multiplier"]
            analysis["coherence_factors"].extend(salary_coherence["factors"])
        
        # Analyse cohérence avec localisation
        if primary_reason == ListeningReasonType.LOCALISATION:
            location_coherence = self._analyze_location_coherence(profile)
            coherence_score *= location_coherence["multiplier"]
            analysis["coherence_factors"].extend(location_coherence["factors"])
        
        # Analyse cohérence avec modalités de travail
        if primary_reason == ListeningReasonType.FLEXIBILITE:
            modality_coherence = self._analyze_modality_coherence(profile)
            coherence_score *= modality_coherence["multiplier"]
            analysis["coherence_factors"].extend(modality_coherence["factors"])
        
        analysis["coherence_score"] = max(0.0, min(2.0, coherence_score))
        
        return analysis
    
    def _analyze_salary_coherence(self, profile: ExtendedMatchingProfile) -> Dict[str, Any]:
        """Analyse cohérence pour raison rémunération"""
        coherence = {"multiplier": 1.0, "factors": []}
        
        if profile.salary.desired_salary and profile.salary.current_salary:
            gap = (profile.salary.desired_salary - profile.salary.current_salary) / profile.salary.current_salary
            
            if gap > 0.2:  # +20% souhaité
                coherence["multiplier"] = 1.3
                coherence["factors"].append("Écart salarial significatif confirmé")
            elif gap < 0.05:  # <5% souhaité
                coherence["multiplier"] = 0.7
                coherence["factors"].append("Écart salarial faible pour motivation rémunération")
        
        return coherence
    
    def _analyze_location_coherence(self, profile: ExtendedMatchingProfile) -> Dict[str, Any]:
        """Analyse cohérence pour raison localisation"""
        coherence = {"multiplier": 1.0, "factors": []}
        
        if profile.location.commute_time_max > 60:
            coherence["multiplier"] = 1.2
            coherence["factors"].append("Temps trajet élevé confirme motivation localisation")
        
        if profile.work_modality.preferred_modality.value in ["full_remote", "hybrid"]:
            coherence["multiplier"] *= 1.1
            coherence["factors"].append("Préférence remote cohérente avec localisation")
        
        return coherence
    
    def _analyze_modality_coherence(self, profile: ExtendedMatchingProfile) -> Dict[str, Any]:
        """Analyse cohérence pour raison flexibilité"""
        coherence = {"multiplier": 1.0, "factors": []}
        
        if profile.work_modality.modality_flexibility >= 4:
            coherence["multiplier"] = 1.3
            coherence["factors"].append("Forte demande flexibilité confirmée")
        
        if profile.contract_flexibility.contract_duration_flexibility:
            coherence["multiplier"] *= 1.1
            coherence["factors"].append("Flexibilité contractuelle cohérente")
        
        return coherence


# ================================
# MOTEUR PONDÉRATION ADAPTATIVE
# ================================

class AdaptiveWeightingEngine:
    """Moteur de calcul des pondérations adaptatives selon raison d'écoute"""
    
    def __init__(self, config: ListeningReasonScorerConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def calculate_adaptive_weights(
        self, 
        profile: ExtendedMatchingProfile,
        coherence_analysis: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calcule les pondérations adaptatives finales"""
        
        # 1. Récupère les poids de base selon raison d'écoute
        base_adaptive_weights = profile.get_adaptive_weights()
        
        # 2. Applique facteur d'intensité
        intensity = profile.listening_reason.reason_intensity
        intensity_multiplier = self.config.intensity_multipliers.get(intensity, 1.0)
        
        # 3. Applique facteur de cohérence
        coherence_multiplier = coherence_analysis["coherence_score"]
        
        # 4. Calcule pondérations finales
        final_weights = {}
        
        for component, base_weight in base_adaptive_weights.items():
            # Application des multiplicateurs
            adapted_weight = base_weight * intensity_multiplier * coherence_multiplier
            
            # Limitation des extrêmes
            adapted_weight = max(self.config.min_adaptive_weight, 
                               min(self.config.max_adaptive_weight, adapted_weight))
            
            final_weights[component] = adapted_weight
        
        # 5. Normalisation pour somme = 1.0
        final_weights = profile.normalize_weights(final_weights)
        
        self.logger.info(f"Pondérations adaptatives calculées: raison={profile.listening_reason.primary_reason.value}, "
                        f"intensité={intensity}, cohérence={coherence_multiplier:.2f}")
        
        return final_weights
    
    def get_adaptation_metrics(
        self, 
        base_weights: Dict[str, float], 
        adaptive_weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calcule les métriques d'adaptation pour analyse"""
        
        metrics = {
            "total_adaptation": 0.0,
            "component_changes": {},
            "biggest_boost": {"component": "", "factor": 0.0},
            "biggest_reduction": {"component": "", "factor": 0.0}
        }
        
        for component in base_weights:
            if component in adaptive_weights:
                base = base_weights[component]
                adapted = adaptive_weights[component]
                change_factor = adapted / base if base > 0 else 1.0
                
                metrics["component_changes"][component] = {
                    "base": base,
                    "adapted": adapted,
                    "change_factor": change_factor,
                    "change_percentage": (change_factor - 1.0) * 100
                }
                
                metrics["total_adaptation"] += abs(change_factor - 1.0)
                
                if change_factor > metrics["biggest_boost"]["factor"]:
                    metrics["biggest_boost"] = {"component": component, "factor": change_factor}
                
                if change_factor < 1.0 and (metrics["biggest_reduction"]["factor"] == 0.0 or 
                                          change_factor < metrics["biggest_reduction"]["factor"]):
                    metrics["biggest_reduction"] = {"component": component, "factor": change_factor}
        
        return metrics


# ================================
# SCORER PRINCIPAL
# ================================

class ListeningReasonScorer:
    """
    Scorer principal pour les raisons d'écoute - Le cerveau adaptatif V3.0
    
    Impact double:
    1. Score direct (3%) basé sur cohérence et intensité de la motivation
    2. Impact systémique (97%) via pondération adaptative de tous les autres composants
    """
    
    def __init__(self, config: Optional[ListeningReasonScorerConfig] = None):
        self.config = config or ListeningReasonScorerConfig()
        self.coherence_analyzer = ListeningReasonCoherenceAnalyzer()
        self.weighting_engine = AdaptiveWeightingEngine(self.config)
        self.logger = logging.getLogger(__name__)
    
    def score(
        self, 
        candidate_profile: ExtendedMatchingProfile,
        position_requirements: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Calcule le score de cohérence de la raison d'écoute
        
        Returns:
            Tuple[float, Dict]: (score_0_1, detailed_analysis)
        """
        
        start_time = datetime.now()
        
        # 1. Analyse de cohérence
        coherence_analysis = self.coherence_analyzer.analyze_coherence(candidate_profile)
        
        # 2. Score base sur intensité de la motivation
        intensity_score = self._calculate_intensity_score(candidate_profile)
        
        # 3. Score de cohérence avec position (si données disponibles)
        position_alignment_score = self._calculate_position_alignment(
            candidate_profile, position_requirements
        )
        
        # 4. Score final pondéré
        final_score = (
            intensity_score * 0.4 +
            coherence_analysis["coherence_score"] * 0.4 +
            position_alignment_score * 0.2
        )
        
        # Normalisation 0-1
        final_score = max(0.0, min(1.0, final_score))
        
        # 5. Analyse détaillée pour debugging
        detailed_analysis = {
            "listening_reason": candidate_profile.listening_reason.primary_reason.value,
            "secondary_reasons": [r.value for r in candidate_profile.listening_reason.secondary_reasons],
            "intensity": candidate_profile.listening_reason.reason_intensity,
            "scores": {
                "intensity": intensity_score,
                "coherence": coherence_analysis["coherence_score"],
                "position_alignment": position_alignment_score,
                "final": final_score
            },
            "coherence_analysis": coherence_analysis,
            "processing_time_ms": (datetime.now() - start_time).total_seconds() * 1000
        }
        
        self.logger.debug(f"Listening reason score calculated: {final_score:.3f} for {candidate_profile.listening_reason.primary_reason.value}")
        
        return final_score, detailed_analysis
    
    def get_adaptive_weighting(
        self, 
        candidate_profile: ExtendedMatchingProfile
    ) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """
        Calcule et retourne la pondération adaptative pour tous les composants
        
        C'est ici que se produit la magie de l'adaptation systémique ! 🧠
        """
        
        # 1. Analyse cohérence
        coherence_analysis = self.coherence_analyzer.analyze_coherence(candidate_profile)
        
        # 2. Calcul pondérations adaptatives
        adaptive_weights = self.weighting_engine.calculate_adaptive_weights(
            candidate_profile, coherence_analysis
        )
        
        # 3. Métriques d'adaptation
        base_weights = candidate_profile.weighting_config.base_weights
        adaptation_metrics = self.weighting_engine.get_adaptation_metrics(
            base_weights, adaptive_weights
        )
        
        # 4. Analyse d'impact
        impact_analysis = {
            "primary_reason": candidate_profile.listening_reason.primary_reason.value,
            "adaptive_weights": adaptive_weights,
            "adaptation_metrics": adaptation_metrics,
            "coherence_analysis": coherence_analysis,
            "total_impact": adaptation_metrics["total_adaptation"],
            "main_boosts": self._identify_main_boosts(adaptation_metrics),
            "recommendation": self._generate_adaptation_recommendation(
                candidate_profile.listening_reason.primary_reason, adaptation_metrics
            )
        }
        
        self.logger.info(f"Adaptive weighting generated: impact={adaptation_metrics['total_adaptation']:.2f}, "
                        f"main_boost={adaptation_metrics['biggest_boost']['component']}")
        
        return adaptive_weights, impact_analysis
    
    def _calculate_intensity_score(self, profile: ExtendedMatchingProfile) -> float:
        """Calcule le score basé sur l'intensité de la motivation"""
        intensity = profile.listening_reason.reason_intensity
        
        # Score base selon intensité (1-5 → 0.2-1.0)
        base_score = intensity / 5.0
        
        # Bonus si description détaillée fournie
        if len(profile.listening_reason.motivation_description) > 20:
            base_score *= 1.1
        
        return min(1.0, base_score)
    
    def _calculate_position_alignment(
        self, 
        profile: ExtendedMatchingProfile, 
        position_requirements: Dict[str, Any]
    ) -> float:
        """Calcule l'alignement avec les exigences du poste"""
        
        if not position_requirements:
            return 0.5  # Score neutre si pas d'infos position
        
        alignment_score = 0.5
        primary_reason = profile.listening_reason.primary_reason
        
        # Alignement spécifique selon raison d'écoute
        if primary_reason == ListeningReasonType.REMUNERATION_FAIBLE:
            if "salary_range" in position_requirements and profile.salary.desired_salary:
                salary_max = position_requirements.get("salary_max", 0)
                if salary_max >= profile.salary.desired_salary:
                    alignment_score = 0.9
                else:
                    alignment_score = 0.3
        
        elif primary_reason == ListeningReasonType.LOCALISATION:
            if "remote_friendly" in position_requirements:
                if position_requirements["remote_friendly"] and \
                   profile.work_modality.preferred_modality.value in ["full_remote", "hybrid"]:
                    alignment_score = 0.9
        
        elif primary_reason == ListeningReasonType.FLEXIBILITE:
            flexibility_indicators = ["remote_work", "flexible_hours", "hybrid_model"]
            matches = sum(1 for indicator in flexibility_indicators 
                         if position_requirements.get(indicator, False))
            alignment_score = 0.3 + (matches / len(flexibility_indicators)) * 0.6
        
        return alignment_score
    
    def _identify_main_boosts(self, adaptation_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifie les principaux boosts appliqués"""
        main_boosts = []
        
        for component, changes in adaptation_metrics["component_changes"].items():
            if changes["change_factor"] > 1.2:  # Boost significatif > 20%
                main_boosts.append({
                    "component": component,
                    "boost_factor": changes["change_factor"],
                    "boost_percentage": changes["change_percentage"]
                })
        
        # Tri par importance du boost
        main_boosts.sort(key=lambda x: x["boost_factor"], reverse=True)
        
        return main_boosts[:3]  # Top 3 boosts
    
    def _generate_adaptation_recommendation(
        self, 
        primary_reason: ListeningReasonType, 
        adaptation_metrics: Dict[str, Any]
    ) -> str:
        """Génère une recommandation basée sur l'adaptation"""
        
        biggest_boost = adaptation_metrics["biggest_boost"]
        total_impact = adaptation_metrics["total_adaptation"]
        
        if total_impact < 0.5:
            return f"Adaptation légère pour raison '{primary_reason.value}' - profil équilibré"
        elif total_impact < 1.5:
            return f"Adaptation modérée - boost principal sur '{biggest_boost['component']}' ({biggest_boost['factor']:.1f}x)"
        else:
            return f"Adaptation forte - refocus majeur sur '{biggest_boost['component']}' - candidat très motivé"


# === ALIAS POUR COMPATIBILITÉ IMPORTS ===

# Alias pour import attendu dans __init__.py
ListeningReasonsScorerV3 = ListeningReasonScorer


# ================================
# INTÉGRATION ET UTILITAIRES
# ================================

def create_listening_reason_scorer(custom_config: Optional[Dict[str, Any]] = None) -> ListeningReasonScorer:
    """Factory pour créer un scorer avec configuration personnalisée"""
    
    config = ListeningReasonScorerConfig()
    
    if custom_config:
        for key, value in custom_config.items():
            if hasattr(config, key):
                setattr(config, key, value)
    
    return ListeningReasonScorer(config)


# ================================
# TESTS ET VALIDATION
# ================================

def test_listening_reason_scorer():
    """Test complet du scorer raison d'écoute"""
    
    print("=== TEST LISTENING REASON SCORER V3.0 ===")
    
    # Création profil test
    profile = ExtendedMatchingProfile()
    profile.listening_reason.primary_reason = ListeningReasonType.REMUNERATION_FAIBLE
    profile.listening_reason.reason_intensity = 4
    profile.listening_reason.motivation_description = "Salaire actuel très en dessous du marché pour mon niveau d'expérience"
    
    profile.salary.current_salary = 35000
    profile.salary.desired_salary = 50000
    
    # Création scorer
    scorer = ListeningReasonScorer()
    
    # Test scoring
    score, analysis = scorer.score(profile, {"salary_max": 55000})
    print(f"Score: {score:.3f}")
    print(f"Raison: {analysis['listening_reason']}")
    print(f"Intensité: {analysis['intensity']}")
    
    # Test pondération adaptative
    adaptive_weights, impact_analysis = scorer.get_adaptive_weighting(profile)
    print(f"\nPondération adaptative:")
    for component, weight in adaptive_weights.items():
        print(f"  {component}: {weight:.1%}")
    
    print(f"\nBoost principal: {impact_analysis['adaptation_metrics']['biggest_boost']['component']}")
    print(f"Impact total: {impact_analysis['total_impact']:.2f}")
    print(f"Recommandation: {impact_analysis['recommendation']}")


if __name__ == "__main__":
    # Configuration logging
    logging.basicConfig(level=logging.INFO)
    
    # Test du scorer
    test_listening_reason_scorer()
