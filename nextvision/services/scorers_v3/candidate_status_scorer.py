"""
🎯 Nextvision V3.0 - CandidateStatusScorer (PROMPT 5) 
Score la compatibilité statut candidat vs besoins/urgence entreprise

💼 DERNIER SCORER V3.0 - Finalise l'architecture 12/12 composants

Fonctionnalités :
- Analyse statut candidat (EN_POSTE, DEMANDEUR_EMPLOI, FREELANCE, ETUDIANT)
- Compatibilité préavis vs urgence recrutement
- Gestion discrétion recrutement selon statut
- Intelligence timing/flexibilité mutuelle
- Performance <4ms (2% budget 175ms)

Author: NEXTEN Team
Version: 3.0.0 - Candidate Status Intelligence
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import re

from nextvision.models.extended_bidirectional_models_v3 import (
    ExtendedCandidateProfileV3,
    ExtendedCompanyProfileV3,
    CandidateStatusType,
    UrgenceRecrutement
)

logger = logging.getLogger(__name__)

class StatusCompatibilityLevel(str, Enum):
    """Niveaux de compatibilité statut"""
    PERFECT = "perfect"
    OPTIMAL = "optimal"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    CHALLENGING = "challenging"
    PROBLEMATIC = "problematic"
    INCOMPATIBLE = "incompatible"

class UrgencyImpact(str, Enum):
    """Impact urgence sur compatibilité statut"""
    NO_IMPACT = "no_impact"
    MINOR_IMPACT = "minor_impact"
    MODERATE_IMPACT = "moderate_impact"
    MAJOR_IMPACT = "major_impact"
    CRITICAL_IMPACT = "critical_impact"

class DiscretionLevel(str, Enum):
    """Niveaux de discrétion recrutement"""
    NONE_REQUIRED = "none_required"
    LOW_DISCRETION = "low_discretion"
    MODERATE_DISCRETION = "moderate_discretion"
    HIGH_DISCRETION = "high_discretion"
    MAXIMUM_DISCRETION = "maximum_discretion"

class CandidateStatusScorer:
    """
    💼 Candidate Status Scorer V3.0 - Intelligence Statut Candidat
    
    DERNIER SCORER V3.0 - Finalise l'architecture 12/12 composants
    
    Évalue la compatibilité statut candidat vs besoins entreprise :
    - Analyse impact statut (en poste, demandeur emploi, freelance)
    - Gestion préavis vs urgence recrutement
    - Évaluation contraintes discrétion
    - Intelligence flexibilité mutuelle
    - Performance ultra-optimisée <4ms
    """
    
    def __init__(self):
        self.name = "CandidateStatusScorer"
        self.version = "3.0.0"
        
        # Configuration pondération des composants
        self.scoring_weights = {
            "status_urgency_compatibility": 0.40,  # Compatibilité statut vs urgence
            "notice_period_impact": 0.25,          # Impact préavis
            "discretion_management": 0.20,         # Gestion discrétion
            "flexibility_bonus": 0.15              # Bonus flexibilité mutuelle
        }
        
        # Matrices de compatibilité statut vs urgence
        self.status_urgency_matrix = {
            CandidateStatusType.DEMANDEUR_EMPLOI: {
                UrgenceRecrutement.CRITIQUE: 1.0,   # Parfait - disponible immédiatement
                UrgenceRecrutement.URGENT: 1.0,     # Parfait - très compatible
                UrgenceRecrutement.NORMAL: 0.9,     # Excellent
                UrgenceRecrutement.FLEXIBLE: 0.8    # Bon
            },
            CandidateStatusType.FREELANCE: {
                UrgenceRecrutement.CRITIQUE: 0.9,   # Excellent - flexible
                UrgenceRecrutement.URGENT: 0.85,    # Très bon
                UrgenceRecrutement.NORMAL: 0.8,     # Bon
                UrgenceRecrutement.FLEXIBLE: 0.9    # Excellent - très flexible
            },
            CandidateStatusType.ETUDIANT: {
                UrgenceRecrutement.CRITIQUE: 0.7,   # Acceptable - contraintes études
                UrgenceRecrutement.URGENT: 0.75,    # Bon
                UrgenceRecrutement.NORMAL: 0.85,    # Très bon
                UrgenceRecrutement.FLEXIBLE: 0.9    # Excellent
            },
            CandidateStatusType.EN_POSTE: {
                UrgenceRecrutement.CRITIQUE: 0.3,   # Problématique - préavis
                UrgenceRecrutement.URGENT: 0.5,     # Moyen - négociation préavis
                UrgenceRecrutement.NORMAL: 0.8,     # Bon - timing normal
                UrgenceRecrutement.FLEXIBLE: 0.9    # Excellent - pas de stress
            }
        }
        
        # Impact préavis selon urgence (pénalités)
        self.notice_penalty_matrix = {
            UrgenceRecrutement.CRITIQUE: {
                0: 1.0,     # Pas de préavis - parfait
                1: 0.8,     # 1 semaine - acceptable
                2: 0.6,     # 2 semaines - limite
                4: 0.3,     # 1 mois - problématique
                8: 0.1,     # 2 mois - critique
                12: 0.05    # 3 mois - quasi-incompatible
            },
            UrgenceRecrutement.URGENT: {
                0: 1.0,     # Parfait
                1: 0.9,     # Excellent
                2: 0.85,    # Très bon
                4: 0.7,     # Bon
                8: 0.4,     # Moyen
                12: 0.2     # Difficile
            },
            UrgenceRecrutement.NORMAL: {
                0: 1.0,     # Parfait
                1: 0.95,    # Excellent
                2: 0.9,     # Très bon
                4: 0.85,    # Bon
                8: 0.7,     # Acceptable
                12: 0.5     # Moyen
            },
            UrgenceRecrutement.FLEXIBLE: {
                0: 1.0,     # Parfait
                1: 0.95,    # Excellent
                2: 0.95,    # Excellent
                4: 0.9,     # Très bon
                8: 0.85,    # Bon
                12: 0.8     # Bon
            }
        }
        
        # Parsing délais recrutement vers semaines
        self.recruitment_delay_patterns = {
            "immédiat": 0,
            "urgent": 1,
            "1 mois": 4,
            "1-2 mois": 6,
            "2 mois": 8,
            "2-3 mois": 10,
            "3 mois": 12,
            "3-6 mois": 20,
            "6 mois": 24,
            "flexible": 16
        }
        
        # Niveaux discrétion selon statut
        self.discretion_levels = {
            CandidateStatusType.EN_POSTE: DiscretionLevel.HIGH_DISCRETION,
            CandidateStatusType.DEMANDEUR_EMPLOI: DiscretionLevel.NONE_REQUIRED,
            CandidateStatusType.FREELANCE: DiscretionLevel.LOW_DISCRETION,
            CandidateStatusType.ETUDIANT: DiscretionLevel.LOW_DISCRETION
        }
        
        # Métriques performance
        self.stats = {
            "calculations": 0,
            "average_processing_time": 0.0,
            "status_distribution": {status.value: 0 for status in CandidateStatusType},
            "compatibility_distribution": {level.value: 0 for level in StatusCompatibilityLevel},
            "urgency_impact_distribution": {impact.value: 0 for impact in UrgencyImpact}
        }
    
    def calculate_candidate_status_score(
        self,
        candidate: ExtendedCandidateProfileV3,
        company: ExtendedCompanyProfileV3,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        💼 Calcule score compatibilité statut candidat
        
        DERNIER SCORER V3.0 - Performance <4ms (2% du budget 175ms)
        
        Args:
            candidate: Profil candidat V3.0
            company: Profil entreprise V3.0
            context: Contexte additionnel
            
        Returns:
            Score statut avec analyse détaillée et recommandations
        """
        
        start_time = datetime.now()
        self.stats["calculations"] += 1
        
        try:
            # 1. Extraction rapide données statut candidat
            candidate_status_data = self._extract_candidate_status_data(candidate)
            
            # 2. Extraction rapide données besoins entreprise
            company_requirements_data = self._extract_company_requirements_data(company)
            
            # 3. Analyse compatibilité statut vs urgence
            status_urgency_analysis = self._analyze_status_urgency_compatibility(
                candidate_status_data, company_requirements_data
            )
            
            # 4. Évaluation impact préavis
            notice_period_analysis = self._evaluate_notice_period_impact(
                candidate_status_data, company_requirements_data
            )
            
            # 5. Analyse gestion discrétion
            discretion_analysis = self._analyze_discretion_management(
                candidate_status_data, company_requirements_data
            )
            
            # 6. Calcul bonus flexibilité
            flexibility_analysis = self._calculate_flexibility_bonus(
                candidate_status_data, company_requirements_data
            )
            
            # 7. Score final pondéré
            final_score = self._calculate_weighted_status_score(
                status_urgency_analysis, notice_period_analysis,
                discretion_analysis, flexibility_analysis
            )
            
            # 8. Enrichissement résultat complet
            result = self._enrich_status_result(
                final_score, candidate_status_data, company_requirements_data,
                status_urgency_analysis, notice_period_analysis,
                discretion_analysis, flexibility_analysis, context
            )
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            result["processing_time_ms"] = processing_time
            
            # 9. Mise à jour statistiques
            self._update_stats(
                processing_time, candidate_status_data["employment_status"],
                result["compatibility_level"], result["urgency_impact"]
            )
            
            logger.info(
                f"💼 CandidateStatusScorer: {final_score:.3f} "
                f"({result['compatibility_level']}/{result['urgency_impact']}, "
                f"{processing_time:.1f}ms)"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur CandidateStatusScorer: {e}")
            return self._create_fallback_score(f"Erreur: {str(e)}")
    
    def _extract_candidate_status_data(self, candidate: ExtendedCandidateProfileV3) -> Dict[str, Any]:
        """📊 Extraction données statut candidat"""
        
        availability = candidate.availability_timing
        
        return {
            "employment_status": availability.employment_status,
            "notice_period_weeks": availability.notice_period_weeks,
            "start_date_flexibility": availability.start_date_flexibility,
            "discretion_required": availability.recruitment_discretion_required,
            "timing_preference": availability.timing,
            "listening_reasons": availability.listening_reasons,
            "current_salary": availability.current_salary
        }
    
    def _extract_company_requirements_data(self, company: ExtendedCompanyProfileV3) -> Dict[str, Any]:
        """🏢 Extraction données besoins entreprise"""
        
        recruitment = company.recruitment_process
        base_profile = company.base_profile
        
        # Parsing délais recrutement
        recruitment_weeks = self._parse_recruitment_delays(recruitment.recruitment_delays)
        
        # Évaluation tolérance préavis
        notice_tolerance = self._evaluate_notice_tolerance(recruitment.notice_management)
        
        return {
            "urgency_level": base_profile.recrutement.urgence,
            "recruitment_delays": recruitment.recruitment_delays,
            "recruitment_weeks": recruitment_weeks,
            "notice_management": recruitment.notice_management,
            "notice_tolerance": notice_tolerance,
            "trial_period_duration": recruitment.trial_period_duration,
            "interview_stages": recruitment.interview_stages,
            "remote_interview_possible": recruitment.remote_interview_possible
        }
    
    def _analyze_status_urgency_compatibility(
        self,
        candidate_data: Dict[str, Any],
        company_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """⚡ Analyse compatibilité statut vs urgence"""
        
        status = candidate_data["employment_status"]
        urgency = company_data["urgency_level"]
        
        # Score de base depuis matrice
        base_score = self.status_urgency_matrix[status][urgency]
        
        # Détermination impact urgence
        if urgency == UrgenceRecrutement.CRITIQUE and status == CandidateStatusType.EN_POSTE:
            impact = UrgencyImpact.CRITICAL_IMPACT
        elif urgency == UrgenceRecrutement.URGENT and status == CandidateStatusType.EN_POSTE:
            impact = UrgencyImpact.MAJOR_IMPACT
        elif urgency in [UrgenceRecrutement.CRITIQUE, UrgenceRecrutement.URGENT] and status == CandidateStatusType.ETUDIANT:
            impact = UrgencyImpact.MODERATE_IMPACT
        elif urgency == UrgenceRecrutement.CRITIQUE:
            impact = UrgencyImpact.MINOR_IMPACT
        else:
            impact = UrgencyImpact.NO_IMPACT
        
        # Facteurs d'analyse
        analysis_factors = []
        
        if status == CandidateStatusType.DEMANDEUR_EMPLOI:
            analysis_factors.append("✅ Candidat demandeur d'emploi - disponibilité optimale")
        elif status == CandidateStatusType.FREELANCE:
            analysis_factors.append("🔄 Freelance - flexibilité élevée")
        elif status == CandidateStatusType.ETUDIANT:
            analysis_factors.append("🎓 Étudiant - contraintes académiques possibles")
        elif status == CandidateStatusType.EN_POSTE:
            if urgency == UrgenceRecrutement.CRITIQUE:
                analysis_factors.append("🚨 En poste + urgence critique - très problématique")
            else:
                analysis_factors.append("💼 En poste - gestion préavis nécessaire")
        
        return {
            "base_score": base_score,
            "urgency_impact": impact,
            "status": status.value,
            "urgency_level": urgency.value,
            "analysis_factors": analysis_factors
        }
    
    def _evaluate_notice_period_impact(
        self,
        candidate_data: Dict[str, Any],
        company_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """📋 Évaluation impact préavis"""
        
        notice_weeks = candidate_data["notice_period_weeks"]
        urgency = company_data["urgency_level"]
        status = candidate_data["employment_status"]
        
        # Si pas en poste, pas de préavis
        if status != CandidateStatusType.EN_POSTE:
            return {
                "impact_score": 1.0,
                "notice_weeks": 0,
                "impact_level": "no_impact",
                "impact_explanation": "Pas de préavis - candidat disponible"
            }
        
        # Score depuis matrice de pénalités
        penalty_matrix = self.notice_penalty_matrix[urgency]
        
        # Trouver le niveau de préavis le plus proche
        closest_weeks = min(penalty_matrix.keys(), key=lambda x: abs(x - notice_weeks))
        impact_score = penalty_matrix[closest_weeks]
        
        # Ajustement pour préavis exact
        if notice_weeks > closest_weeks and closest_weeks < max(penalty_matrix.keys()):
            next_weeks = min(w for w in penalty_matrix.keys() if w > closest_weeks)
            # Interpolation linéaire
            ratio = (notice_weeks - closest_weeks) / (next_weeks - closest_weeks)
            impact_score = impact_score * (1 - ratio) + penalty_matrix[next_weeks] * ratio
        
        # Détermination niveau impact
        if impact_score >= 0.9:
            impact_level = "minimal_impact"
        elif impact_score >= 0.7:
            impact_level = "low_impact"
        elif impact_score >= 0.5:
            impact_level = "moderate_impact"
        elif impact_score >= 0.3:
            impact_level = "high_impact"
        else:
            impact_level = "critical_impact"
        
        # Explication impact
        if notice_weeks == 0:
            explanation = "Pas de préavis - optimal"
        elif urgency == UrgenceRecrutement.CRITIQUE and notice_weeks > 2:
            explanation = f"Préavis {notice_weeks} sem. + urgence critique - très problématique"
        elif urgency == UrgenceRecrutement.URGENT and notice_weeks > 4:
            explanation = f"Préavis {notice_weeks} sem. + urgence - négociation difficile"
        else:
            explanation = f"Préavis {notice_weeks} sem. - impact {impact_level}"
        
        return {
            "impact_score": impact_score,
            "notice_weeks": notice_weeks,
            "impact_level": impact_level,
            "impact_explanation": explanation,
            "urgency_context": urgency.value
        }
    
    def _analyze_discretion_management(
        self,
        candidate_data: Dict[str, Any],
        company_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🤫 Analyse gestion discrétion recrutement"""
        
        status = candidate_data["employment_status"]
        discretion_required = candidate_data["discretion_required"]
        remote_interview_possible = company_data["remote_interview_possible"]
        
        # Niveau de discrétion selon statut
        discretion_level = self.discretion_levels[status]
        
        # Score de base
        if not discretion_required:
            base_score = 1.0
            discretion_analysis = "Aucune contrainte de discrétion"
        else:
            # Score selon niveau requis
            if discretion_level == DiscretionLevel.NONE_REQUIRED:
                base_score = 1.0
                discretion_analysis = "Discrétion demandée mais non nécessaire"
            elif discretion_level == DiscretionLevel.LOW_DISCRETION:
                base_score = 0.9
                discretion_analysis = "Discrétion légère requise"
            elif discretion_level == DiscretionLevel.MODERATE_DISCRETION:
                base_score = 0.7
                discretion_analysis = "Discrétion modérée nécessaire"
            elif discretion_level == DiscretionLevel.HIGH_DISCRETION:
                base_score = 0.5
                discretion_analysis = "Haute discrétion requise"
            else:  # MAXIMUM_DISCRETION
                base_score = 0.3
                discretion_analysis = "Discrétion maximale critique"
        
        # Bonus si entretiens à distance possibles
        if discretion_required and remote_interview_possible:
            base_score = min(1.0, base_score + 0.2)
            discretion_analysis += " + entretiens distants facilitent discrétion"
        
        # Gestion spécifique selon statut
        discretion_factors = []
        
        if status == CandidateStatusType.EN_POSTE and discretion_required:
            discretion_factors.append("💼 En poste - discrétion critique pour éviter conflits")
            if not remote_interview_possible:
                discretion_factors.append("⚠️ Entretiens présentiels - risque exposition")
        elif status == CandidateStatusType.DEMANDEUR_EMPLOI:
            discretion_factors.append("✅ Demandeur emploi - pas de contrainte discrétion")
        elif status == CandidateStatusType.FREELANCE:
            discretion_factors.append("🔄 Freelance - discrétion modérée client")
        
        return {
            "discretion_score": base_score,
            "discretion_level": discretion_level.value,
            "discretion_required": discretion_required,
            "discretion_analysis": discretion_analysis,
            "discretion_factors": discretion_factors,
            "remote_interview_bonus": remote_interview_possible and discretion_required
        }
    
    def _calculate_flexibility_bonus(
        self,
        candidate_data: Dict[str, Any],
        company_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🔄 Calcul bonus flexibilité mutuelle"""
        
        flexibility_score = 0.0
        flexibility_factors = []
        
        # Flexibilité candidat date de début
        start_flexibility = candidate_data["start_date_flexibility"]
        if start_flexibility >= 4:
            flexibility_score += 0.3
            flexibility_factors.append(f"Candidat très flexible dates (+{start_flexibility} sem.)")
        elif start_flexibility >= 2:
            flexibility_score += 0.2
            flexibility_factors.append(f"Candidat moyennement flexible (+{start_flexibility} sem.)")
        
        # Bonus selon statut
        status = candidate_data["employment_status"]
        if status == CandidateStatusType.FREELANCE:
            flexibility_score += 0.2
            flexibility_factors.append("Freelance - flexibilité naturelle")
        elif status == CandidateStatusType.DEMANDEUR_EMPLOI:
            flexibility_score += 0.3
            flexibility_factors.append("Demandeur emploi - très disponible")
        
        # Tolérance entreprise sur préavis
        notice_tolerance = company_data["notice_tolerance"]
        if notice_tolerance >= 0.8:
            flexibility_score += 0.2
            flexibility_factors.append("Entreprise très tolérante préavis")
        elif notice_tolerance >= 0.6:
            flexibility_score += 0.1
            flexibility_factors.append("Entreprise moyennement tolérante")
        
        # Bonus entretiens à distance
        if company_data["remote_interview_possible"]:
            flexibility_score += 0.1
            flexibility_factors.append("Entretiens distants possibles")
        
        # Bonus période d'essai courte
        trial_period = company_data["trial_period_duration"]
        if trial_period == 0:
            flexibility_score += 0.1
            flexibility_factors.append("Pas de période d'essai")
        elif trial_period <= 2:
            flexibility_score += 0.05
            flexibility_factors.append("Période d'essai courte")
        
        return {
            "flexibility_score": min(1.0, flexibility_score),
            "flexibility_factors": flexibility_factors,
            "candidate_flexibility": start_flexibility,
            "company_tolerance": notice_tolerance
        }
    
    def _calculate_weighted_status_score(
        self,
        status_urgency_analysis: Dict[str, Any],
        notice_period_analysis: Dict[str, Any],
        discretion_analysis: Dict[str, Any],
        flexibility_analysis: Dict[str, Any]
    ) -> float:
        """🧮 Calcul score statut pondéré"""
        
        final_score = (
            status_urgency_analysis["base_score"] * self.scoring_weights["status_urgency_compatibility"] +
            notice_period_analysis["impact_score"] * self.scoring_weights["notice_period_impact"] +
            discretion_analysis["discretion_score"] * self.scoring_weights["discretion_management"] +
            flexibility_analysis["flexibility_score"] * self.scoring_weights["flexibility_bonus"]
        )
        
        return min(1.0, final_score)
    
    def _enrich_status_result(
        self,
        final_score: float,
        candidate_data: Dict[str, Any],
        company_data: Dict[str, Any],
        status_urgency_analysis: Dict[str, Any],
        notice_period_analysis: Dict[str, Any],
        discretion_analysis: Dict[str, Any],
        flexibility_analysis: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """🔧 Enrichissement résultat statut"""
        
        # Détermination niveau compatibilité
        compatibility_level = self._determine_compatibility_level(final_score)
        
        # Recommandations intelligentes
        recommendations = self._generate_status_recommendations(
            final_score, compatibility_level, candidate_data, company_data,
            status_urgency_analysis, notice_period_analysis, discretion_analysis
        )
        
        # Analyse détaillée
        detailed_analysis = self._generate_detailed_status_analysis(
            candidate_data, company_data, status_urgency_analysis,
            notice_period_analysis, discretion_analysis, flexibility_analysis
        )
        
        return {
            "final_score": final_score,
            "compatibility_level": compatibility_level.value,
            "urgency_impact": status_urgency_analysis["urgency_impact"].value,
            "score_breakdown": {
                "status_urgency_score": status_urgency_analysis["base_score"],
                "notice_period_score": notice_period_analysis["impact_score"],
                "discretion_score": discretion_analysis["discretion_score"],
                "flexibility_score": flexibility_analysis["flexibility_score"],
                "weighted_final": final_score
            },
            "status_analysis": {
                "candidate_status": candidate_data["employment_status"].value,
                "notice_period_weeks": candidate_data["notice_period_weeks"],
                "urgency_level": company_data["urgency_level"].value,
                "discretion_required": candidate_data["discretion_required"],
                "compatibility_factors": self._extract_compatibility_factors(
                    status_urgency_analysis, notice_period_analysis, 
                    discretion_analysis, flexibility_analysis
                )
            },
            "detailed_analysis": detailed_analysis,
            "recommendations": recommendations,
            "calculated_at": datetime.now().isoformat(),
            "version": self.version,
            "scorer": self.name
        }
    
    def _determine_compatibility_level(self, score: float) -> StatusCompatibilityLevel:
        """📊 Détermination niveau compatibilité"""
        
        if score >= 0.95:
            return StatusCompatibilityLevel.PERFECT
        elif score >= 0.85:
            return StatusCompatibilityLevel.OPTIMAL
        elif score >= 0.70:
            return StatusCompatibilityLevel.GOOD
        elif score >= 0.50:
            return StatusCompatibilityLevel.ACCEPTABLE
        elif score >= 0.30:
            return StatusCompatibilityLevel.CHALLENGING
        elif score >= 0.15:
            return StatusCompatibilityLevel.PROBLEMATIC
        else:
            return StatusCompatibilityLevel.INCOMPATIBLE
    
    def _generate_status_recommendations(
        self,
        final_score: float,
        compatibility_level: StatusCompatibilityLevel,
        candidate_data: Dict[str, Any],
        company_data: Dict[str, Any],
        status_urgency_analysis: Dict[str, Any],
        notice_period_analysis: Dict[str, Any],
        discretion_analysis: Dict[str, Any]
    ) -> List[str]:
        """💡 Génération recommandations statut"""
        
        recommendations = []
        
        # Recommandations globales
        if compatibility_level == StatusCompatibilityLevel.PERFECT:
            recommendations.append("🌟 Statut parfait - Procéder immédiatement")
        elif compatibility_level == StatusCompatibilityLevel.OPTIMAL:
            recommendations.append("✨ Statut optimal - Excellente compatibilité")
        elif compatibility_level == StatusCompatibilityLevel.GOOD:
            recommendations.append("✅ Bon statut - Négociation simple")
        elif compatibility_level == StatusCompatibilityLevel.ACCEPTABLE:
            recommendations.append("⚠️ Statut acceptable - Clarifier modalités")
        elif compatibility_level == StatusCompatibilityLevel.CHALLENGING:
            recommendations.append("🔄 Statut difficile - Solutions créatives requises")
        elif compatibility_level == StatusCompatibilityLevel.PROBLEMATIC:
            recommendations.append("🚨 Statut problématique - Réévaluer faisabilité")
        else:
            recommendations.append("❌ Statut incompatible - Abandon recommandé")
        
        # Recommandations spécifiques préavis
        notice_weeks = notice_period_analysis["notice_weeks"]
        urgency = company_data["urgency_level"]
        
        if notice_weeks > 0 and urgency in [UrgenceRecrutement.CRITIQUE, UrgenceRecrutement.URGENT]:
            if notice_weeks <= 2:
                recommendations.append("⏰ Préavis court - Négocier accélération")
            elif notice_weeks <= 4:
                recommendations.append("📋 Préavis moyen - Négocier avec employeur actuel")
            else:
                recommendations.append("🔄 Préavis long - Envisager solutions alternatives")
        
        # Recommandations discrétion
        if discretion_analysis["discretion_required"]:
            if candidate_data["employment_status"] == CandidateStatusType.EN_POSTE:
                recommendations.append("🤫 Gérer discrétion - Entretiens hors heures/distance")
            else:
                recommendations.append("💼 Discrétion modérée - Process standard")
        
        # Recommandations selon statut
        status = candidate_data["employment_status"]
        if status == CandidateStatusType.DEMANDEUR_EMPLOI:
            recommendations.append("🚀 Candidat disponible - Accélérer process")
        elif status == CandidateStatusType.FREELANCE:
            recommendations.append("🔄 Freelance - Négocier transition mission/CDI")
        elif status == CandidateStatusType.ETUDIANT:
            recommendations.append("🎓 Étudiant - Coordonner avec calendrier académique")
        
        return recommendations
    
    def _generate_detailed_status_analysis(
        self,
        candidate_data: Dict[str, Any],
        company_data: Dict[str, Any],
        status_urgency_analysis: Dict[str, Any],
        notice_period_analysis: Dict[str, Any],
        discretion_analysis: Dict[str, Any],
        flexibility_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """📊 Analyse détaillée statut"""
        
        return {
            "candidate_profile": {
                "status": candidate_data["employment_status"].value,
                "notice_period": f"{candidate_data['notice_period_weeks']} semaines",
                "flexibility": f"{candidate_data['start_date_flexibility']} semaines",
                "discretion_needs": discretion_analysis["discretion_required"]
            },
            "company_profile": {
                "urgency": company_data["urgency_level"].value,
                "recruitment_timeline": company_data["recruitment_delays"],
                "notice_tolerance": f"{company_data['notice_tolerance']:.0%}",
                "remote_interviews": company_data["remote_interview_possible"]
            },
            "compatibility_matrix": {
                "status_urgency_fit": f"{status_urgency_analysis['base_score']:.2f}",
                "notice_period_impact": notice_period_analysis["impact_level"],
                "discretion_level": discretion_analysis["discretion_level"],
                "overall_flexibility": f"{flexibility_analysis['flexibility_score']:.2f}"
            },
            "risk_factors": self._identify_risk_factors(
                candidate_data, company_data, status_urgency_analysis, notice_period_analysis
            ),
            "success_factors": self._identify_success_factors(
                candidate_data, company_data, flexibility_analysis, discretion_analysis
            )
        }
    
    def _extract_compatibility_factors(
        self,
        status_urgency_analysis: Dict[str, Any],
        notice_period_analysis: Dict[str, Any],
        discretion_analysis: Dict[str, Any],
        flexibility_analysis: Dict[str, Any]
    ) -> List[str]:
        """📋 Extraction facteurs compatibilité"""
        
        factors = []
        
        # Facteurs statut/urgence
        factors.extend(status_urgency_analysis["analysis_factors"])
        
        # Facteurs préavis
        if notice_period_analysis["impact_explanation"]:
            factors.append(f"📋 {notice_period_analysis['impact_explanation']}")
        
        # Facteurs discrétion
        factors.extend(discretion_analysis["discretion_factors"])
        
        # Facteurs flexibilité
        factors.extend(flexibility_analysis["flexibility_factors"])
        
        return factors
    
    def _identify_risk_factors(
        self,
        candidate_data: Dict[str, Any],
        company_data: Dict[str, Any],
        status_urgency_analysis: Dict[str, Any],
        notice_period_analysis: Dict[str, Any]
    ) -> List[str]:
        """⚠️ Identification facteurs de risque"""
        
        risks = []
        
        # Risque urgence vs statut
        if status_urgency_analysis["urgency_impact"] in [UrgencyImpact.MAJOR_IMPACT, UrgencyImpact.CRITICAL_IMPACT]:
            risks.append("🚨 Incompatibilité urgence/statut critique")
        
        # Risque préavis
        if notice_period_analysis["notice_weeks"] > 8:
            risks.append("⏰ Préavis très long - risque abandon process")
        
        # Risque discrétion
        if (candidate_data["discretion_required"] and 
            candidate_data["employment_status"] == CandidateStatusType.EN_POSTE and
            not company_data["remote_interview_possible"]):
            risks.append("🤫 Discrétion difficile - entretiens présentiels")
        
        return risks
    
    def _identify_success_factors(
        self,
        candidate_data: Dict[str, Any],
        company_data: Dict[str, Any],
        flexibility_analysis: Dict[str, Any],
        discretion_analysis: Dict[str, Any]
    ) -> List[str]:
        """✅ Identification facteurs de succès"""
        
        success = []
        
        # Succès disponibilité
        if candidate_data["employment_status"] == CandidateStatusType.DEMANDEUR_EMPLOI:
            success.append("🚀 Disponibilité immédiate")
        
        # Succès flexibilité
        if flexibility_analysis["flexibility_score"] > 0.7:
            success.append("🔄 Forte flexibilité mutuelle")
        
        # Succès entretiens distants
        if company_data["remote_interview_possible"]:
            success.append("💻 Entretiens distants facilitent process")
        
        # Succès tolérance préavis
        if company_data["notice_tolerance"] > 0.7:
            success.append("📋 Entreprise tolérante sur timing")
        
        return success
    
    def _parse_recruitment_delays(self, delays: str) -> int:
        """📅 Parsing délais recrutement"""
        
        delays_lower = delays.lower().strip()
        
        # Vérification patterns prédéfinis
        for pattern, weeks in self.recruitment_delay_patterns.items():
            if pattern in delays_lower:
                return weeks
        
        # Extraction numérique avec regex
        month_match = re.search(r'(\d+)\s*mois', delays_lower)
        if month_match:
            return int(month_match.group(1)) * 4
        
        week_match = re.search(r'(\d+)\s*semaine', delays_lower)
        if week_match:
            return int(week_match.group(1))
        
        # Valeur par défaut
        return 8  # 2 mois
    
    def _evaluate_notice_tolerance(self, notice_management: str) -> float:
        """📋 Évaluation tolérance préavis"""
        
        notice_lower = notice_management.lower().strip()
        
        if any(word in notice_lower for word in ["flexible", "adaptable", "négociable"]):
            return 0.9
        elif any(word in notice_lower for word in ["possible", "gérable", "acceptable"]):
            return 0.7
        elif any(word in notice_lower for word in ["selon", "profil", "cas par cas"]):
            return 0.6
        elif any(word in notice_lower for word in ["difficile", "compliqué", "problématique"]):
            return 0.3
        elif any(word in notice_lower for word in ["impossible", "strict", "non négociable"]):
            return 0.1
        else:
            return 0.5  # Défaut neutre
    
    def _create_fallback_score(self, reason: str) -> Dict[str, Any]:
        """🚨 Score fallback en cas d'erreur"""
        
        logger.warning(f"Fallback CandidateStatusScorer: {reason}")
        
        return {
            "final_score": 0.5,  # Score neutre
            "compatibility_level": StatusCompatibilityLevel.ACCEPTABLE.value,
            "urgency_impact": UrgencyImpact.NO_IMPACT.value,
            "score_breakdown": {
                "status_urgency_score": 0.5,
                "notice_period_score": 0.5,
                "discretion_score": 0.5,
                "flexibility_score": 0.5,
                "weighted_final": 0.5
            },
            "status_analysis": {
                "candidate_status": "unknown",
                "notice_period_weeks": 0,
                "urgency_level": "unknown",
                "discretion_required": False,
                "compatibility_factors": [f"Mode dégradé: {reason}"]
            },
            "detailed_analysis": {},
            "recommendations": [
                f"⚠️ {reason}",
                "🛠️ Vérifier manuellement compatibilité statut",
                "🔄 Réessayer avec données complètes"
            ],
            "calculated_at": datetime.now().isoformat(),
            "version": f"{self.version}-fallback",
            "scorer": self.name,
            "error": reason
        }
    
    def _update_stats(
        self, 
        processing_time: float, 
        status: CandidateStatusType,
        compatibility: str,
        urgency_impact: str
    ):
        """📊 Mise à jour statistiques"""
        
        # Moyenne temps de traitement
        total = self.stats["calculations"]
        current_avg = self.stats["average_processing_time"]
        self.stats["average_processing_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        # Distribution statuts
        self.stats["status_distribution"][status.value] += 1
        
        # Distribution compatibilité
        self.stats["compatibility_distribution"][compatibility] += 1
        
        # Distribution impact urgence
        self.stats["urgency_impact_distribution"][urgency_impact] += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """📈 Statistiques performance"""
        
        # Calcul taux distributions
        status_rates = {}
        compatibility_rates = {}
        impact_rates = {}
        
        if self.stats["calculations"] > 0:
            for status, count in self.stats["status_distribution"].items():
                status_rates[status] = count / self.stats["calculations"]
            for level, count in self.stats["compatibility_distribution"].items():
                compatibility_rates[level] = count / self.stats["calculations"]
            for impact, count in self.stats["urgency_impact_distribution"].items():
                impact_rates[impact] = count / self.stats["calculations"]
        
        return {
            "scorer_stats": self.stats.copy(),
            "performance_metrics": {
                "average_processing_time_ms": self.stats["average_processing_time"],
                "target_achieved": self.stats["average_processing_time"] < 4.0,
                "status_distribution": status_rates,
                "compatibility_distribution": compatibility_rates,
                "urgency_impact_distribution": impact_rates
            },
            "configuration_info": {
                "scoring_weights": self.scoring_weights,
                "status_types_supported": list(CandidateStatusType),
                "urgency_levels_supported": list(UrgenceRecrutement)
            }
        }
    
    def get_status_compatibility_preview(
        self, 
        status: CandidateStatusType, 
        urgency: UrgenceRecrutement
    ) -> Dict[str, Any]:
        """🔍 Aperçu compatibilité statut/urgence"""
        
        if status in self.status_urgency_matrix and urgency in self.status_urgency_matrix[status]:
            base_score = self.status_urgency_matrix[status][urgency]
            discretion_level = self.discretion_levels[status]
            
            return {
                "status": status.value,
                "urgency": urgency.value,
                "base_compatibility": base_score,
                "compatibility_percentage": f"{base_score:.0%}",
                "discretion_level": discretion_level.value,
                "recommended": base_score >= 0.7,
                "notice_period_tolerance": urgency != UrgenceRecrutement.CRITIQUE
            }
        else:
            return {
                "status": status.value if status else "unknown",
                "urgency": urgency.value if urgency else "unknown",
                "error": "Combinaison non supportée",
                "base_compatibility": 0.5
            }
