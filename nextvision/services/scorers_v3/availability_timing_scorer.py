"""
🚀 Nextvision V3.0 - AvailabilityTimingScorer (PROMPT 7)
Score la compatibilité timing candidat vs urgence entreprise

Fonctionnalités :
- Gestion préavis si candidat en poste
- Bonus/malus selon flexibilité timing
- Pénalité si décalage timing trop important
- Intégration avec les données V3.0

Author: NEXTEN Team
Version: 3.0.0 - Timing Intelligence
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum

from nextvision.models.extended_bidirectional_models_v3 import (
    ExtendedCandidateProfileV3,
    ExtendedCompanyProfileV3,
    CandidateStatusType,
    UrgenceRecrutement
)

logger = logging.getLogger(__name__)

class TimingCompatibilityLevel(str, Enum):
    """Niveaux de compatibilité timing"""
    PERFECT = "perfect"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    PROBLEMATIC = "problematic"
    INCOMPATIBLE = "incompatible"

class AvailabilityTimingScorer:
    """
    🕐 Scorer Timing V3.0 - Disponibilité Intelligence
    
    Évalue la compatibilité timing candidat vs urgence entreprise avec :
    - Analyse préavis vs délais recrutement
    - Bonus flexibilité mutuelle
    - Pénalité décalage timing critique
    - Intelligence statut candidat
    """
    
    def __init__(self):
        self.name = "AvailabilityTimingScorer"
        self.version = "3.0.0"
        
        # Configuration scoring
        self.scoring_config = {
            "weights": {
                "timing_compatibility": 0.45,    # Compatibilité timing de base
                "flexibility_bonus": 0.25,       # Bonus flexibilité
                "notice_management": 0.20,       # Gestion préavis
                "urgency_alignment": 0.10        # Alignement urgence
            },
            "timing_mappings": {
                "immediat": 0,
                "1mois": 4,
                "2mois": 8,
                "3mois": 12
            },
            "urgency_tolerance": {
                UrgenceRecrutement.CRITIQUE: 2,    # Max 2 semaines
                UrgenceRecrutement.URGENT: 6,      # Max 6 semaines
                UrgenceRecrutement.NORMAL: 12,     # Max 12 semaines
                UrgenceRecrutement.FLEXIBLE: 24    # Max 24 semaines
            }
        }
        
        # Métriques performance
        self.stats = {
            "total_calculations": 0,
            "perfect_matches": 0,
            "incompatible_matches": 0,
            "average_score": 0.0
        }
    
    def calculate_availability_timing_score(
        self,
        candidate: ExtendedCandidateProfileV3,
        company: ExtendedCompanyProfileV3,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        🎯 Calcule score timing disponibilité vs urgence
        
        Args:
            candidate: Profil candidat V3.0
            company: Profil entreprise V3.0
            context: Contexte additionnel
            
        Returns:
            Score timing avec détails et recommandations
        """
        
        start_time = datetime.now()
        self.stats["total_calculations"] += 1
        
        try:
            # 1. Extraction données timing candidat
            candidate_timing = self._extract_candidate_timing(candidate)
            
            # 2. Extraction données urgence entreprise
            company_urgency = self._extract_company_urgency(company)
            
            # 3. Calcul compatibilité timing de base
            base_compatibility = self._calculate_base_timing_compatibility(
                candidate_timing, company_urgency
            )
            
            # 4. Calcul bonus flexibilité
            flexibility_bonus = self._calculate_flexibility_bonus(
                candidate_timing, company_urgency
            )
            
            # 5. Évaluation gestion préavis
            notice_management_score = self._evaluate_notice_management(
                candidate_timing, company_urgency
            )
            
            # 6. Alignement urgence
            urgency_alignment_score = self._calculate_urgency_alignment(
                candidate_timing, company_urgency
            )
            
            # 7. Score final pondéré
            final_score = self._calculate_weighted_score(
                base_compatibility, flexibility_bonus, 
                notice_management_score, urgency_alignment_score
            )
            
            # 8. Enrichissement avec détails
            result = self._enrich_timing_result(
                final_score, candidate_timing, company_urgency,
                base_compatibility, flexibility_bonus, 
                notice_management_score, urgency_alignment_score,
                context
            )
            
            # 9. Mise à jour statistiques
            self._update_stats(final_score)
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            result["processing_time_ms"] = processing_time
            
            logger.info(
                f"🕐 AvailabilityTimingScorer: {final_score:.3f} "
                f"({result['compatibility_level']}, {processing_time:.1f}ms)"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur AvailabilityTimingScorer: {e}")
            return self._create_fallback_score(candidate, company, str(e))
    
    def _extract_candidate_timing(self, candidate: ExtendedCandidateProfileV3) -> Dict[str, Any]:
        """📊 Extraction données timing candidat"""
        
        availability = candidate.availability_timing
        base_profile = candidate.base_profile
        
        # Conversion timing vers semaines
        timing_weeks = self._convert_timing_to_weeks(availability.timing)
        
        # Détection préavis si en poste
        notice_weeks = 0
        if availability.employment_status == CandidateStatusType.EN_POSTE:
            notice_weeks = availability.notice_period_weeks
        
        # Évaluation flexibilité
        flexibility_level = self._evaluate_candidate_flexibility(availability)
        
        return {
            "timing_preference": availability.timing,
            "timing_weeks": timing_weeks,
            "employment_status": availability.employment_status,
            "notice_period_weeks": notice_weeks,
            "start_date_flexibility": availability.start_date_flexibility,
            "discretion_required": availability.recruitment_discretion_required,
            "flexibility_level": flexibility_level,
            "current_salary": availability.current_salary,
            "listening_reasons": availability.listening_reasons
        }
    
    def _extract_company_urgency(self, company: ExtendedCompanyProfileV3) -> Dict[str, Any]:
        """🏢 Extraction données urgence entreprise"""
        
        base_profile = company.base_profile
        recruitment_process = company.recruitment_process
        
        # Parsing délais de recrutement
        recruitment_weeks = self._parse_recruitment_delays(
            recruitment_process.recruitment_delays
        )
        
        # Évaluation gestion préavis
        notice_tolerance = self._evaluate_notice_tolerance(
            recruitment_process.notice_management
        )
        
        return {
            "urgency_level": base_profile.recrutement.urgence,
            "recruitment_delays": recruitment_process.recruitment_delays,
            "recruitment_weeks": recruitment_weeks,
            "notice_management": recruitment_process.notice_management,
            "notice_tolerance": notice_tolerance,
            "interview_stages": recruitment_process.interview_stages,
            "trial_period": recruitment_process.trial_period_duration,
            "urgency_context": base_profile.recrutement.contexte_urgence
        }
    
    def _calculate_base_timing_compatibility(
        self, 
        candidate_timing: Dict[str, Any], 
        company_urgency: Dict[str, Any]
    ) -> Dict[str, Any]:
        """⚖️ Calcul compatibilité timing de base"""
        
        candidate_weeks = candidate_timing["timing_weeks"]
        company_weeks = company_urgency["recruitment_weeks"]
        notice_weeks = candidate_timing["notice_period_weeks"]
        
        # Temps total candidat (disponibilité + préavis)
        total_candidate_weeks = candidate_weeks + notice_weeks
        
        # Calcul compatibilité
        if total_candidate_weeks <= company_weeks:
            compatibility_score = 1.0
            compatibility_level = TimingCompatibilityLevel.PERFECT
        elif total_candidate_weeks <= company_weeks + 2:
            compatibility_score = 0.8
            compatibility_level = TimingCompatibilityLevel.GOOD
        elif total_candidate_weeks <= company_weeks + 4:
            compatibility_score = 0.6
            compatibility_level = TimingCompatibilityLevel.ACCEPTABLE
        elif total_candidate_weeks <= company_weeks + 8:
            compatibility_score = 0.3
            compatibility_level = TimingCompatibilityLevel.PROBLEMATIC
        else:
            compatibility_score = 0.0
            compatibility_level = TimingCompatibilityLevel.INCOMPATIBLE
        
        return {
            "score": compatibility_score,
            "level": compatibility_level,
            "candidate_total_weeks": total_candidate_weeks,
            "company_max_weeks": company_weeks,
            "gap_weeks": max(0, total_candidate_weeks - company_weeks)
        }
    
    def _calculate_flexibility_bonus(
        self, 
        candidate_timing: Dict[str, Any], 
        company_urgency: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🔄 Calcul bonus flexibilité"""
        
        bonus_score = 0.0
        bonus_details = []
        
        # Bonus flexibilité candidat
        if candidate_timing["start_date_flexibility"] >= 4:
            bonus_score += 0.2
            bonus_details.append("Candidat très flexible sur date de début")
        elif candidate_timing["start_date_flexibility"] >= 2:
            bonus_score += 0.1
            bonus_details.append("Candidat moyennement flexible")
        
        # Bonus si candidat demandeur d'emploi (disponible rapidement)
        if candidate_timing["employment_status"] == CandidateStatusType.DEMANDEUR_EMPLOI:
            bonus_score += 0.3
            bonus_details.append("Candidat demandeur d'emploi - disponible rapidement")
        
        # Bonus si pas de discrétion requise
        if not candidate_timing["discretion_required"]:
            bonus_score += 0.1
            bonus_details.append("Pas de contrainte de discrétion")
        
        # Bonus si entreprise flexible sur timing
        if company_urgency["notice_tolerance"] >= 0.8:
            bonus_score += 0.2
            bonus_details.append("Entreprise très tolérante sur préavis")
        
        return {
            "score": min(1.0, bonus_score),
            "details": bonus_details
        }
    
    def _evaluate_notice_management(
        self, 
        candidate_timing: Dict[str, Any], 
        company_urgency: Dict[str, Any]
    ) -> Dict[str, Any]:
        """📋 Évaluation gestion préavis"""
        
        notice_weeks = candidate_timing["notice_period_weeks"]
        notice_tolerance = company_urgency["notice_tolerance"]
        urgency_level = company_urgency["urgency_level"]
        
        if notice_weeks == 0:
            return {
                "score": 1.0,
                "evaluation": "Pas de préavis - optimal"
            }
        
        # Calcul score selon tolérance entreprise
        if notice_tolerance >= 0.8:
            score = 1.0
            evaluation = "Entreprise très tolérante sur préavis"
        elif notice_tolerance >= 0.6:
            score = 0.8
            evaluation = "Entreprise moyennement tolérante"
        elif notice_tolerance >= 0.4:
            score = 0.6
            evaluation = "Entreprise peu tolérante"
        else:
            score = 0.3
            evaluation = "Entreprise stricte sur timing"
        
        # Pénalité selon urgence
        if urgency_level == UrgenceRecrutement.CRITIQUE and notice_weeks > 2:
            score *= 0.5
            evaluation += " - Pénalité urgence critique"
        elif urgency_level == UrgenceRecrutement.URGENT and notice_weeks > 4:
            score *= 0.7
            evaluation += " - Pénalité urgence élevée"
        
        return {
            "score": score,
            "evaluation": evaluation,
            "notice_weeks": notice_weeks,
            "tolerance_level": notice_tolerance
        }
    
    def _calculate_urgency_alignment(
        self, 
        candidate_timing: Dict[str, Any], 
        company_urgency: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🎯 Calcul alignement urgence"""
        
        urgency_level = company_urgency["urgency_level"]
        candidate_weeks = candidate_timing["timing_weeks"]
        
        # Tolérance par niveau d'urgence
        max_tolerance = self.scoring_config["urgency_tolerance"][urgency_level]
        
        if candidate_weeks <= max_tolerance:
            score = 1.0
            alignment = "Parfait alignement"
        elif candidate_weeks <= max_tolerance * 1.5:
            score = 0.7
            alignment = "Bon alignement"
        elif candidate_weeks <= max_tolerance * 2:
            score = 0.4
            alignment = "Alignement moyen"
        else:
            score = 0.1
            alignment = "Mauvais alignement"
        
        return {
            "score": score,
            "alignment": alignment,
            "max_tolerance_weeks": max_tolerance,
            "candidate_weeks": candidate_weeks
        }
    
    def _calculate_weighted_score(
        self,
        base_compatibility: Dict[str, Any],
        flexibility_bonus: Dict[str, Any],
        notice_management: Dict[str, Any],
        urgency_alignment: Dict[str, Any]
    ) -> float:
        """🧮 Calcul score final pondéré"""
        
        weights = self.scoring_config["weights"]
        
        final_score = (
            base_compatibility["score"] * weights["timing_compatibility"] +
            flexibility_bonus["score"] * weights["flexibility_bonus"] +
            notice_management["score"] * weights["notice_management"] +
            urgency_alignment["score"] * weights["urgency_alignment"]
        )
        
        return min(1.0, final_score)
    
    def _enrich_timing_result(
        self,
        final_score: float,
        candidate_timing: Dict[str, Any],
        company_urgency: Dict[str, Any],
        base_compatibility: Dict[str, Any],
        flexibility_bonus: Dict[str, Any],
        notice_management: Dict[str, Any],
        urgency_alignment: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """🔧 Enrichissement résultat timing"""
        
        # Détermination niveau compatibilité
        if final_score >= 0.9:
            compatibility_level = TimingCompatibilityLevel.PERFECT
        elif final_score >= 0.75:
            compatibility_level = TimingCompatibilityLevel.GOOD
        elif final_score >= 0.5:
            compatibility_level = TimingCompatibilityLevel.ACCEPTABLE
        elif final_score >= 0.25:
            compatibility_level = TimingCompatibilityLevel.PROBLEMATIC
        else:
            compatibility_level = TimingCompatibilityLevel.INCOMPATIBLE
        
        # Génération explications
        explanations = self._generate_timing_explanations(
            final_score, candidate_timing, company_urgency,
            base_compatibility, flexibility_bonus, notice_management
        )
        
        # Recommandations
        recommendations = self._generate_timing_recommendations(
            compatibility_level, candidate_timing, company_urgency
        )
        
        return {
            "final_score": final_score,
            "compatibility_level": compatibility_level.value,
            "score_breakdown": {
                "timing_compatibility": base_compatibility["score"],
                "flexibility_bonus": flexibility_bonus["score"],
                "notice_management": notice_management["score"],
                "urgency_alignment": urgency_alignment["score"]
            },
            "timing_analysis": {
                "candidate_availability": candidate_timing["timing_preference"],
                "candidate_weeks": candidate_timing["timing_weeks"],
                "notice_period_weeks": candidate_timing["notice_period_weeks"],
                "company_max_weeks": company_urgency["recruitment_weeks"],
                "urgency_level": company_urgency["urgency_level"].value,
                "gap_weeks": base_compatibility.get("gap_weeks", 0)
            },
            "explanations": explanations,
            "recommendations": recommendations,
            "calculated_at": datetime.now().isoformat(),
            "version": self.version,
            "scorer": self.name
        }
    
    def _generate_timing_explanations(
        self,
        final_score: float,
        candidate_timing: Dict[str, Any],
        company_urgency: Dict[str, Any],
        base_compatibility: Dict[str, Any],
        flexibility_bonus: Dict[str, Any],
        notice_management: Dict[str, Any]
    ) -> List[str]:
        """📝 Génération explications timing"""
        
        explanations = []
        
        # Score principal
        explanations.append(
            f"🕐 Score timing: {final_score:.2f}/1.0 "
            f"(candidat: {candidate_timing['timing_preference']}, "
            f"entreprise: {company_urgency['recruitment_delays']})"
        )
        
        # Détail compatibilité
        if base_compatibility["gap_weeks"] == 0:
            explanations.append("✅ Timing parfaitement compatible")
        elif base_compatibility["gap_weeks"] > 0:
            explanations.append(
                f"⚠️ Écart: {base_compatibility['gap_weeks']} semaines "
                f"({base_compatibility['candidate_total_weeks']} vs {base_compatibility['company_max_weeks']})"
            )
        
        # Préavis
        if candidate_timing["notice_period_weeks"] > 0:
            explanations.append(
                f"📋 Préavis: {candidate_timing['notice_period_weeks']} semaines "
                f"({notice_management['evaluation']})"
            )
        
        # Bonus flexibilité
        if flexibility_bonus["score"] > 0:
            explanations.append(
                f"🔄 Bonus flexibilité: +{flexibility_bonus['score']:.1%}"
            )
        
        return explanations
    
    def _generate_timing_recommendations(
        self,
        compatibility_level: TimingCompatibilityLevel,
        candidate_timing: Dict[str, Any],
        company_urgency: Dict[str, Any]
    ) -> List[str]:
        """💡 Génération recommandations timing"""
        
        recommendations = []
        
        if compatibility_level == TimingCompatibilityLevel.PERFECT:
            recommendations.append("🌟 Timing idéal - procéder rapidement")
        
        elif compatibility_level == TimingCompatibilityLevel.GOOD:
            recommendations.append("✅ Bon timing - négociation simple")
        
        elif compatibility_level == TimingCompatibilityLevel.ACCEPTABLE:
            recommendations.append("⚠️ Timing acceptable - négocier flexibilité")
            
            if candidate_timing["notice_period_weeks"] > 0:
                recommendations.append(
                    f"💡 Négocier réduction préavis ou démarrage différé"
                )
        
        elif compatibility_level == TimingCompatibilityLevel.PROBLEMATIC:
            recommendations.append("🚨 Timing problématique - solutions requises")
            
            if company_urgency["urgency_level"] == UrgenceRecrutement.CRITIQUE:
                recommendations.append("⚡ Urgence critique - chercher alternatives")
            else:
                recommendations.append("🔄 Réévaluer urgence ou accepter délai")
        
        else:  # INCOMPATIBLE
            recommendations.append("❌ Timing incompatible - abandon recommandé")
        
        return recommendations
    
    def _convert_timing_to_weeks(self, timing: str) -> int:
        """🔄 Conversion timing vers semaines"""
        
        timing_lower = timing.lower()
        
        if "immédiat" in timing_lower or "immediate" in timing_lower:
            return 0
        elif "1 mois" in timing_lower or "1mois" in timing_lower:
            return 4
        elif "2 mois" in timing_lower or "2mois" in timing_lower:
            return 8
        elif "3 mois" in timing_lower or "3mois" in timing_lower:
            return 12
        else:
            # Tentative extraction numérique
            import re
            match = re.search(r'(\d+)\s*mois', timing_lower)
            if match:
                return int(match.group(1)) * 4
            return 4  # Défaut 1 mois
    
    def _parse_recruitment_delays(self, delays: str) -> int:
        """📊 Parsing délais recrutement"""
        
        delays_lower = delays.lower()
        
        if "immédiat" in delays_lower or "urgent" in delays_lower:
            return 2
        elif "1 mois" in delays_lower or "1-2" in delays_lower:
            return 6
        elif "2 mois" in delays_lower or "2-3" in delays_lower:
            return 10
        elif "3 mois" in delays_lower or "flexible" in delays_lower:
            return 16
        else:
            return 8  # Défaut 2 mois
    
    def _evaluate_candidate_flexibility(self, availability) -> float:
        """🔄 Évaluation flexibilité candidat"""
        
        flexibility = 0.5  # Base neutre
        
        # Bonus flexibilité date début
        if availability.start_date_flexibility >= 4:
            flexibility += 0.3
        elif availability.start_date_flexibility >= 2:
            flexibility += 0.2
        
        # Bonus si demandeur d'emploi
        if availability.employment_status == CandidateStatusType.DEMANDEUR_EMPLOI:
            flexibility += 0.2
        
        # Malus si discrétion requise
        if availability.recruitment_discretion_required:
            flexibility -= 0.1
        
        return min(1.0, flexibility)
    
    def _evaluate_notice_tolerance(self, notice_management: str) -> float:
        """📋 Évaluation tolérance préavis entreprise"""
        
        notice_lower = notice_management.lower()
        
        if "flexible" in notice_lower or "adaptable" in notice_lower:
            return 0.9
        elif "possible" in notice_lower or "gérable" in notice_lower:
            return 0.7
        elif "difficile" in notice_lower or "compliqué" in notice_lower:
            return 0.4
        elif "impossible" in notice_lower or "strict" in notice_lower:
            return 0.1
        else:
            return 0.6  # Défaut moyen
    
    def _update_stats(self, score: float):
        """📊 Mise à jour statistiques"""
        
        total = self.stats["total_calculations"]
        current_avg = self.stats["average_score"]
        
        # Mise à jour moyenne
        self.stats["average_score"] = (
            (current_avg * (total - 1) + score) / total
        )
        
        # Compteurs niveaux
        if score >= 0.9:
            self.stats["perfect_matches"] += 1
        elif score <= 0.2:
            self.stats["incompatible_matches"] += 1
    
    def _create_fallback_score(
        self,
        candidate: ExtendedCandidateProfileV3,
        company: ExtendedCompanyProfileV3,
        error_message: str
    ) -> Dict[str, Any]:
        """🚨 Score fallback en cas d'erreur"""
        
        logger.warning(f"Fallback AvailabilityTimingScorer: {error_message}")
        
        # Score neutre conservateur
        fallback_score = 0.5
        
        # Ajustement heuristique
        if candidate.availability_timing.employment_status == CandidateStatusType.DEMANDEUR_EMPLOI:
            fallback_score = 0.7  # Bonus disponibilité
        
        return {
            "final_score": fallback_score,
            "compatibility_level": TimingCompatibilityLevel.ACCEPTABLE.value,
            "score_breakdown": {
                "timing_compatibility": fallback_score,
                "flexibility_bonus": 0.0,
                "notice_management": fallback_score,
                "urgency_alignment": fallback_score
            },
            "timing_analysis": {
                "candidate_availability": candidate.availability_timing.timing,
                "urgency_level": company.base_profile.recrutement.urgence.value,
                "gap_weeks": None
            },
            "explanations": [
                f"⚠️ Mode dégradé: {error_message}",
                f"📊 Score estimé: {fallback_score:.2f}"
            ],
            "recommendations": [
                "🛠️ Vérifier manuellement la compatibilité timing",
                "⏰ Réessayer plus tard avec service complet"
            ],
            "calculated_at": datetime.now().isoformat(),
            "version": f"{self.version}-fallback",
            "scorer": self.name,
            "error": error_message
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """📈 Statistiques performance"""
        
        perfect_rate = 0.0
        incompatible_rate = 0.0
        
        if self.stats["total_calculations"] > 0:
            perfect_rate = self.stats["perfect_matches"] / self.stats["total_calculations"]
            incompatible_rate = self.stats["incompatible_matches"] / self.stats["total_calculations"]
        
        return {
            "scorer_stats": self.stats.copy(),
            "performance_metrics": {
                "perfect_match_rate": perfect_rate,
                "incompatible_rate": incompatible_rate,
                "average_score": self.stats["average_score"]
            },
            "configuration": self.scoring_config
        }
    
    def reset_stats(self):
        """🔄 Reset statistiques"""
        self.stats = {
            "total_calculations": 0,
            "perfect_matches": 0,
            "incompatible_matches": 0,
            "average_score": 0.0
        }
