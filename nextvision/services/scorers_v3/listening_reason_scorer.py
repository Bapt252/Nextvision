"""
🧠 Nextvision V3.0 - ListeningReasonScorer (2% Weight)
=====================================================

Score la cohérence des raisons d'écoute candidat avec son profil
- Analyse raisons d'écoute depuis availability_timing.listening_reasons
- Cohérence avec profil candidat (salaire, localisation, flexibilité)
- Interaction avec pondération adaptative (cerveau du système)
- Performance ultra-optimisée <4ms (2% du budget 175ms)

Author: NEXTEN Team
Version: 3.0.0 - Listening Intelligence
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from nextvision.models.extended_bidirectional_models_v3 import (
    ExtendedCandidateProfileV3,
    ExtendedCompanyProfileV3,
    CandidateStatusType,
    WorkModalityType
)
from nextvision.config.adaptive_weighting_config import (
    ListeningReasonType,
    ADAPTIVE_MATRICES_V3
)

logger = logging.getLogger(__name__)

class CoherenceLevel(str, Enum):
    """Niveaux de cohérence raison d'écoute"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    INCOHERENT = "incoherent"

class ListeningReasonScorer:
    """
    🧠 Listening Reason Scorer V3.0 - Cerveau Adaptatif
    
    Évalue la cohérence des raisons d'écoute avec le profil candidat :
    - Analyse raisons multiples depuis availability_timing.listening_reasons
    - Cohérence avec données candidat (salaire, localisation, status)
    - Interaction avec matrices de pondération adaptative
    - Performance ultra-optimisée <4ms (2% poids mais impact systémique)
    """
    
    def __init__(self):
        self.name = "ListeningReasonScorer"
        self.version = "3.0.0"
        
        # Configuration ultra-lightweight pour performance
        self.coherence_rules = {
            ListeningReasonType.REMUNERATION_FAIBLE: {
                "profile_indicators": ["salary_gap", "career_stagnation"],
                "compatible_with": [ListeningReasonType.MANQUE_PERSPECTIVES],
                "weight_multiplier": 1.2
            },
            ListeningReasonType.MANQUE_PERSPECTIVES: {
                "profile_indicators": ["experience_level", "career_goals"],
                "compatible_with": [ListeningReasonType.REMUNERATION_FAIBLE, ListeningReasonType.POSTE_INADEQUAT],
                "weight_multiplier": 1.3
            },
            ListeningReasonType.POSTE_INADEQUAT: {
                "profile_indicators": ["skills_mismatch", "underutilized"],
                "compatible_with": [ListeningReasonType.MANQUE_PERSPECTIVES],
                "weight_multiplier": 1.1
            },
            ListeningReasonType.LOCALISATION: {
                "profile_indicators": ["commute_time", "remote_preference"],
                "compatible_with": [ListeningReasonType.FLEXIBILITE],
                "weight_multiplier": 1.0
            },
            ListeningReasonType.FLEXIBILITE: {
                "profile_indicators": ["work_modality", "schedule_needs"],
                "compatible_with": [ListeningReasonType.LOCALISATION],
                "weight_multiplier": 1.1
            }
        }
        
        # Métriques performance
        self.stats = {
            "calculations": 0,
            "average_processing_time": 0.0,
            "coherence_distribution": {level.value: 0 for level in CoherenceLevel}
        }
    
    def calculate_listening_reason_score(
        self,
        candidate: ExtendedCandidateProfileV3,
        company: ExtendedCompanyProfileV3,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        🧠 Calcule score cohérence raisons d'écoute
        
        Target: <4ms (2% du budget 175ms)
        """
        start_time = datetime.now()
        self.stats["calculations"] += 1
        
        try:
            # 1. Extraction rapide raisons d'écoute
            listening_reasons = candidate.availability_timing.listening_reasons
            
            if not listening_reasons:
                return self._create_fallback_score("Pas de raisons d'écoute détectées")
            
            # 2. Analyse cohérence ultra-rapide
            coherence_analysis = self._analyze_coherence_fast(candidate, listening_reasons)
            
            # 3. Score basé sur cohérence + intensité
            final_score = self._calculate_coherence_score(coherence_analysis, listening_reasons)
            
            # 4. Enrichissement minimal (performance)
            result = self._enrich_result(
                final_score, coherence_analysis, listening_reasons, context
            )
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            result["processing_time_ms"] = processing_time
            
            # Mise à jour stats
            self._update_stats(processing_time, coherence_analysis["coherence_level"])
            
            logger.info(
                f"🧠 ListeningReasonScorer: {final_score:.3f} "
                f"({coherence_analysis['coherence_level']}, {processing_time:.1f}ms)"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur ListeningReasonScorer: {e}")
            return self._create_fallback_score(f"Erreur: {str(e)}")
    
    def _analyze_coherence_fast(
        self,
        candidate: ExtendedCandidateProfileV3,
        listening_reasons: List[ListeningReasonType]
    ) -> Dict[str, Any]:
        """⚡ Analyse cohérence ultra-rapide"""
        
        primary_reason = listening_reasons[0] if listening_reasons else None
        secondary_reasons = listening_reasons[1:] if len(listening_reasons) > 1 else []
        
        coherence_score = 0.5  # Base neutre
        coherence_factors = []
        
        if not primary_reason:
            return {
                "coherence_score": coherence_score,
                "coherence_level": CoherenceLevel.AVERAGE,
                "coherence_factors": ["Pas de raison principale détectée"]
            }
        
        # Analyse cohérence raison principale avec profil
        primary_coherence = self._check_primary_coherence(primary_reason, candidate)
        coherence_score += primary_coherence["boost"]
        coherence_factors.extend(primary_coherence["factors"])
        
        # Analyse cohérence raisons secondaires
        if secondary_reasons:
            secondary_coherence = self._check_secondary_coherence(
                primary_reason, secondary_reasons
            )
            coherence_score += secondary_coherence["boost"] * 0.5
            coherence_factors.extend(secondary_coherence["factors"])
        
        # Bonus cohérence multiple
        if len(listening_reasons) > 1:
            coherence_score += 0.1
            coherence_factors.append("Motivations multiples cohérentes")
        
        # Détermination niveau
        coherence_level = self._determine_coherence_level(coherence_score)
        
        return {
            "primary_reason": primary_reason,
            "secondary_reasons": secondary_reasons,
            "coherence_score": min(1.0, coherence_score),
            "coherence_level": coherence_level,
            "coherence_factors": coherence_factors
        }
    
    def _check_primary_coherence(
        self,
        reason: ListeningReasonType,
        candidate: ExtendedCandidateProfileV3
    ) -> Dict[str, Any]:
        """🔍 Vérification cohérence raison principale"""
        
        boost = 0.0
        factors = []
        
        if reason == ListeningReasonType.REMUNERATION_FAIBLE:
            # Cohérence avec données salariales
            if (candidate.base_profile.attentes.salaire_min and 
                candidate.base_profile.attentes.salaire_max):
                gap = candidate.base_profile.attentes.salaire_max - candidate.base_profile.attentes.salaire_min
                if gap > 10000:  # Écart important souhaité
                    boost += 0.3
                    factors.append("Écart salarial important cohérent")
            
            # Cohérence avec statut
            if candidate.availability_timing.employment_status == CandidateStatusType.EN_POSTE:
                boost += 0.2
                factors.append("En poste - motivation salariale logique")
        
        elif reason == ListeningReasonType.MANQUE_PERSPECTIVES:
            # Cohérence avec expérience
            if candidate.availability_timing.employment_status == CandidateStatusType.EN_POSTE:
                boost += 0.3
                factors.append("En poste - recherche évolution logique")
            
            # Cohérence avec motivations
            if hasattr(candidate, 'motivations_ranking') and candidate.motivations_ranking.motivations_ranking:
                from nextvision.models.extended_bidirectional_models_v3 import MotivationType
                if MotivationType.EVOLUTION_CARRIERE in candidate.motivations_ranking.motivations_ranking:
                    boost += 0.2
                    factors.append("Motivation évolution cohérente")
        
        elif reason == ListeningReasonType.FLEXIBILITE:
            # Cohérence avec préférences travail
            if candidate.transport_preferences.office_preference in [WorkModalityType.HYBRID, WorkModalityType.FULL_REMOTE]:
                boost += 0.3
                factors.append("Préférence remote cohérente")
            
            # Cohérence avec situation personnelle
            if candidate.availability_timing.employment_status == CandidateStatusType.EN_POSTE:
                boost += 0.1
                factors.append("En poste - recherche flexibilité compréhensible")
        
        elif reason == ListeningReasonType.LOCALISATION:
            # Cohérence avec transport
            if candidate.transport_preferences.max_travel_time < 30:
                boost += 0.3
                factors.append("Temps trajet faible cohérent")
            
            # Cohérence avec modalité travail
            if candidate.transport_preferences.office_preference == WorkModalityType.FULL_REMOTE:
                boost += 0.2
                factors.append("Préférence remote cohérente avec localisation")
        
        elif reason == ListeningReasonType.POSTE_INADEQUAT:
            # Cohérence avec compétences
            if candidate.availability_timing.employment_status == CandidateStatusType.EN_POSTE:
                boost += 0.2
                factors.append("En poste - inadéquation actuelle logique")
        
        return {"boost": boost, "factors": factors}
    
    def _check_secondary_coherence(
        self,
        primary_reason: ListeningReasonType,
        secondary_reasons: List[ListeningReasonType]
    ) -> Dict[str, Any]:
        """🔗 Vérification cohérence raisons secondaires"""
        
        boost = 0.0
        factors = []
        
        if primary_reason not in self.coherence_rules:
            return {"boost": boost, "factors": factors}
        
        compatible_reasons = self.coherence_rules[primary_reason]["compatible_with"]
        
        for secondary in secondary_reasons:
            if secondary in compatible_reasons:
                boost += 0.1
                factors.append(f"Raison secondaire {secondary.value} compatible")
            else:
                boost -= 0.05
                factors.append(f"Raison secondaire {secondary.value} peu cohérente")
        
        return {"boost": boost, "factors": factors}
    
    def _determine_coherence_level(self, coherence_score: float) -> CoherenceLevel:
        """📊 Détermination niveau de cohérence"""
        
        if coherence_score >= 0.85:
            return CoherenceLevel.EXCELLENT
        elif coherence_score >= 0.70:
            return CoherenceLevel.GOOD
        elif coherence_score >= 0.50:
            return CoherenceLevel.AVERAGE
        elif coherence_score >= 0.30:
            return CoherenceLevel.POOR
        else:
            return CoherenceLevel.INCOHERENT
    
    def _calculate_coherence_score(
        self,
        coherence_analysis: Dict[str, Any],
        listening_reasons: List[ListeningReasonType]
    ) -> float:
        """🧮 Calcul score final cohérence"""
        
        base_score = coherence_analysis["coherence_score"]
        
        # Bonus intensité (multiple raisons = plus forte motivation)
        intensity_bonus = min(0.2, len(listening_reasons) * 0.1)
        
        # Bonus si raison principale importante pour pondération adaptative
        primary_reason = coherence_analysis.get("primary_reason")
        if primary_reason and primary_reason in ADAPTIVE_MATRICES_V3:
            adaptive_bonus = 0.1
        else:
            adaptive_bonus = 0.0
        
        final_score = base_score + intensity_bonus + adaptive_bonus
        
        return min(1.0, final_score)
    
    def _enrich_result(
        self,
        final_score: float,
        coherence_analysis: Dict[str, Any],
        listening_reasons: List[ListeningReasonType],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """🔧 Enrichissement résultat (minimal pour performance)"""
        
        # Recommandations rapides
        recommendations = self._generate_quick_recommendations(
            final_score, coherence_analysis, listening_reasons
        )
        
        # Analyse impact pondération adaptative
        adaptive_impact = self._analyze_adaptive_impact(listening_reasons)
        
        return {
            "final_score": final_score,
            "coherence_level": coherence_analysis["coherence_level"].value,
            "listening_reasons_analysis": {
                "primary_reason": coherence_analysis["primary_reason"].value if coherence_analysis["primary_reason"] else None,
                "secondary_reasons": [r.value for r in coherence_analysis["secondary_reasons"]],
                "total_reasons": len(listening_reasons),
                "coherence_score": coherence_analysis["coherence_score"]
            },
            "coherence_factors": coherence_analysis["coherence_factors"],
            "adaptive_impact": adaptive_impact,
            "recommendations": recommendations,
            "calculated_at": datetime.now().isoformat(),
            "version": self.version,
            "scorer": self.name
        }
    
    def _generate_quick_recommendations(
        self,
        final_score: float,
        coherence_analysis: Dict[str, Any],
        listening_reasons: List[ListeningReasonType]
    ) -> List[str]:
        """💡 Recommandations rapides"""
        
        recommendations = []
        
        # Recommandations globales
        if coherence_analysis["coherence_level"] == CoherenceLevel.EXCELLENT:
            recommendations.append("🌟 Excellente cohérence - Candidat très motivé")
        elif coherence_analysis["coherence_level"] == CoherenceLevel.GOOD:
            recommendations.append("✅ Bonne cohérence - Motivations crédibles")
        elif coherence_analysis["coherence_level"] == CoherenceLevel.POOR:
            recommendations.append("⚠️ Cohérence faible - Creuser les motivations")
        elif coherence_analysis["coherence_level"] == CoherenceLevel.INCOHERENT:
            recommendations.append("❌ Incohérence détectée - Vérifier authenticité")
        
        # Recommandations spécifiques
        primary_reason = coherence_analysis.get("primary_reason")
        if primary_reason == ListeningReasonType.REMUNERATION_FAIBLE:
            recommendations.append("💰 Prioriser négociation salariale")
        elif primary_reason == ListeningReasonType.MANQUE_PERSPECTIVES:
            recommendations.append("🚀 Mettre en avant opportunités évolution")
        elif primary_reason == ListeningReasonType.FLEXIBILITE:
            recommendations.append("🔄 Souligner flexibilité organisation")
        
        # Bonus raisons multiples
        if len(listening_reasons) > 2:
            recommendations.append("🎯 Candidat multi-motivé - Aborder plusieurs angles")
        
        return recommendations
    
    def _analyze_adaptive_impact(self, listening_reasons: List[ListeningReasonType]) -> Dict[str, Any]:
        """📊 Analyse impact pondération adaptative"""
        
        primary_reason = listening_reasons[0] if listening_reasons else None
        
        if not primary_reason or primary_reason not in ADAPTIVE_MATRICES_V3:
            return {
                "has_adaptive_impact": False,
                "primary_reason": primary_reason.value if primary_reason else None,
                "impact_description": "Pas d'impact sur pondération adaptative"
            }
        
        # Analyse des boosts principaux
        adaptive_matrix = ADAPTIVE_MATRICES_V3[primary_reason]
        
        # Trouver les composants les plus boostés
        base_weights = {
            "semantic": 0.24, "salary": 0.19, "experience": 0.14, "location": 0.09,
            "motivations": 0.08, "sector_compatibility": 0.06, "contract_flexibility": 0.05,
            "timing_compatibility": 0.04, "work_modality": 0.04, "salary_progression": 0.03,
            "listening_reason": 0.02, "candidate_status": 0.02
        }
        
        boosted_components = []
        for component, adaptive_weight in adaptive_matrix.items():
            base_weight = base_weights.get(component, 0.0)
            if base_weight > 0 and adaptive_weight > base_weight * 1.2:  # Boost >20%
                boost_factor = adaptive_weight / base_weight
                boosted_components.append({
                    "component": component,
                    "boost_factor": boost_factor,
                    "new_weight": adaptive_weight
                })
        
        # Tri par importance du boost
        boosted_components.sort(key=lambda x: x["boost_factor"], reverse=True)
        
        return {
            "has_adaptive_impact": True,
            "primary_reason": primary_reason.value,
            "boosted_components": boosted_components[:3],  # Top 3
            "impact_description": f"Boost adaptatif pour {primary_reason.value}"
        }
    
    def _create_fallback_score(self, reason: str) -> Dict[str, Any]:
        """🚨 Score fallback en cas d'erreur"""
        
        logger.warning(f"Fallback ListeningReasonScorer: {reason}")
        
        return {
            "final_score": 0.5,  # Score neutre
            "coherence_level": CoherenceLevel.AVERAGE.value,
            "listening_reasons_analysis": {
                "primary_reason": None,
                "secondary_reasons": [],
                "total_reasons": 0,
                "coherence_score": 0.5
            },
            "coherence_factors": [f"Mode dégradé: {reason}"],
            "adaptive_impact": {
                "has_adaptive_impact": False,
                "impact_description": "Pas d'impact - mode dégradé"
            },
            "recommendations": [
                f"⚠️ {reason}",
                "🛠️ Vérifier manuellement les raisons d'écoute"
            ],
            "calculated_at": datetime.now().isoformat(),
            "version": f"{self.version}-fallback",
            "scorer": self.name,
            "error": reason
        }
    
    def _update_stats(self, processing_time: float, coherence_level: CoherenceLevel):
        """📊 Mise à jour statistiques"""
        
        # Moyenne temps de traitement
        total = self.stats["calculations"]
        current_avg = self.stats["average_processing_time"]
        self.stats["average_processing_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        # Distribution cohérence
        self.stats["coherence_distribution"][coherence_level.value] += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """📈 Statistiques performance"""
        
        coherence_rates = {}
        if self.stats["calculations"] > 0:
            for level, count in self.stats["coherence_distribution"].items():
                coherence_rates[level] = count / self.stats["calculations"]
        
        return {
            "scorer_stats": self.stats.copy(),
            "performance_metrics": {
                "average_processing_time_ms": self.stats["average_processing_time"],
                "target_achieved": self.stats["average_processing_time"] < 4.0,
                "coherence_rates": coherence_rates
            }
        }
    
    def get_adaptive_impact_preview(self, listening_reasons: List[ListeningReasonType]) -> Dict[str, Any]:
        """🔍 Aperçu impact pondération adaptative"""
        
        if not listening_reasons:
            return {"has_impact": False, "message": "Pas de raisons d'écoute"}
        
        primary_reason = listening_reasons[0]
        
        if primary_reason not in ADAPTIVE_MATRICES_V3:
            return {"has_impact": False, "message": f"Pas d'impact pour {primary_reason.value}"}
        
        # Analyse des changements principaux
        adaptive_matrix = ADAPTIVE_MATRICES_V3[primary_reason]
        
        # Composants les plus impactés
        major_changes = []
        for component, weight in adaptive_matrix.items():
            if weight > 0.15:  # Poids significatif
                major_changes.append(f"{component}: {weight:.1%}")
        
        return {
            "has_impact": True,
            "primary_reason": primary_reason.value,
            "major_changes": major_changes[:3],
            "message": f"Pondération adaptative activée pour {primary_reason.value}"
        }
