"""
🚀 Nextvision V3.0 - WorkEnvironmentScorer (PROMPT 7)
Score environment candidat vs entreprise

Fonctionnalités :
- Office preference vs environment type
- Remote compatibility
- Extraction environment depuis job_benefits
- Bonus/malus selon modalités travail

Author: NEXTEN Team
Version: 3.0.0 - Environment Intelligence
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum

from nextvision.models.extended_bidirectional_models_v3 import (
    ExtendedCandidateProfileV3,
    ExtendedCompanyProfileV3,
    WorkModalityType
)

logger = logging.getLogger(__name__)

class EnvironmentCompatibilityLevel(str, Enum):
    """Niveaux de compatibilité environnement"""
    PERFECT = "perfect"
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    PROBLEMATIC = "problematic"
    INCOMPATIBLE = "incompatible"

class WorkEnvironmentScorer:
    """
    🏢 Scorer Environnement V3.0 - Environment Intelligence
    
    Évalue la compatibilité environnement de travail avec :
    - Modalités télétravail vs préférences
    - Compatibilité horaires flexibles
    - Analyse trajets domicile-travail
    - Intelligence culture d'entreprise
    """
    
    def __init__(self):
        self.name = "WorkEnvironmentScorer"
        self.version = "3.0.0"
        
        # Configuration scoring
        self.scoring_config = {
            "weights": {
                "remote_compatibility": 0.35,      # Compatibilité télétravail
                "schedule_flexibility": 0.25,      # Flexibilité horaires
                "commute_analysis": 0.20,          # Analyse trajets
                "culture_alignment": 0.15,         # Alignement culture
                "workplace_benefits": 0.05         # Avantages lieu travail
            },
            "remote_compatibility_matrix": {
                # candidat -> entreprise -> score
                WorkModalityType.FULL_REMOTE: {
                    WorkModalityType.FULL_REMOTE: 1.0,
                    WorkModalityType.HYBRID: 0.8,
                    WorkModalityType.ON_SITE: 0.1,
                    WorkModalityType.FLEXIBLE: 0.9
                },
                WorkModalityType.HYBRID: {
                    WorkModalityType.FULL_REMOTE: 0.9,
                    WorkModalityType.HYBRID: 1.0,
                    WorkModalityType.ON_SITE: 0.6,
                    WorkModalityType.FLEXIBLE: 0.95
                },
                WorkModalityType.ON_SITE: {
                    WorkModalityType.FULL_REMOTE: 0.3,
                    WorkModalityType.HYBRID: 0.7,
                    WorkModalityType.ON_SITE: 1.0,
                    WorkModalityType.FLEXIBLE: 0.8
                },
                WorkModalityType.FLEXIBLE: {
                    WorkModalityType.FULL_REMOTE: 0.8,
                    WorkModalityType.HYBRID: 0.9,
                    WorkModalityType.ON_SITE: 0.7,
                    WorkModalityType.FLEXIBLE: 1.0
                }
            }
        }
        
        # Métriques performance
        self.stats = {
            "total_calculations": 0,
            "perfect_matches": 0,
            "incompatible_matches": 0,
            "remote_preference_stats": {},
            "average_score": 0.0
        }
    
    def calculate_work_environment_score(
        self,
        candidate: ExtendedCandidateProfileV3,
        company: ExtendedCompanyProfileV3,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        🎯 Calcule score compatibilité environnement de travail
        
        Args:
            candidate: Profil candidat V3.0
            company: Profil entreprise V3.0
            context: Contexte additionnel
            
        Returns:
            Score environnement avec détails et recommandations
        """
        
        start_time = datetime.now()
        self.stats["total_calculations"] += 1
        
        try:
            # 1. Extraction préférences environnement candidat
            candidate_preferences = self._extract_candidate_environment_preferences(candidate)
            
            # 2. Extraction environnement entreprise
            company_environment = self._extract_company_environment(company)
            
            # 3. Analyse compatibilité télétravail
            remote_compatibility = self._analyze_remote_compatibility(
                candidate_preferences, company_environment
            )
            
            # 4. Évaluation flexibilité horaires
            schedule_flexibility = self._evaluate_schedule_flexibility(
                candidate_preferences, company_environment
            )
            
            # 5. Analyse trajets domicile-travail
            commute_analysis = self._analyze_commute_compatibility(
                candidate_preferences, company_environment, context
            )
            
            # 6. Alignement culture entreprise
            culture_alignment = self._assess_culture_alignment(
                candidate_preferences, company_environment
            )
            
            # 7. Avantages lieu de travail
            workplace_benefits = self._evaluate_workplace_benefits(
                candidate_preferences, company_environment
            )
            
            # 8. Score final pondéré
            final_score = self._calculate_weighted_score(
                remote_compatibility, schedule_flexibility, commute_analysis,
                culture_alignment, workplace_benefits
            )
            
            # 9. Enrichissement avec détails
            result = self._enrich_environment_result(
                final_score, candidate_preferences, company_environment,
                remote_compatibility, schedule_flexibility, commute_analysis,
                culture_alignment, workplace_benefits, context
            )
            
            # 10. Mise à jour statistiques
            self._update_stats(final_score, candidate_preferences["office_preference"])
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            result["processing_time_ms"] = processing_time
            
            logger.info(
                f"🏢 WorkEnvironmentScorer: {final_score:.3f} "
                f"({result['compatibility_level']}, {processing_time:.1f}ms)"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur WorkEnvironmentScorer: {e}")
            return self._create_fallback_score(candidate, company, str(e))
    
    def _extract_candidate_environment_preferences(self, candidate: ExtendedCandidateProfileV3) -> Dict[str, Any]:
        """📊 Extraction préférences environnement candidat"""
        
        transport_prefs = candidate.transport_preferences
        base_profile = candidate.base_profile
        
        # Préférences bureau/télétravail
        office_preference = transport_prefs.office_preference
        
        # Temps trajet maximum
        max_travel_time = transport_prefs.max_travel_time
        
        # Évaluation importance horaires flexibles
        flexible_hours_important = transport_prefs.flexible_hours_important
        
        # Besoin parking
        parking_required = transport_prefs.parking_required
        
        # Accessibilité transports publics
        public_transport_accessibility = transport_prefs.public_transport_accessibility
        
        return {
            "office_preference": office_preference,
            "max_travel_time": max_travel_time,
            "flexible_hours_important": flexible_hours_important,
            "parking_required": parking_required,
            "public_transport_accessibility": public_transport_accessibility,
            "remote_experience": candidate.remote_work_experience,
            "management_experience": candidate.management_experience,
            "work_schedule_preference": "flexible" if flexible_hours_important else "fixed"
        }
    
    def _extract_company_environment(self, company: ExtendedCompanyProfileV3) -> Dict[str, Any]:
        """🏢 Extraction environnement entreprise"""
        
        job_benefits = company.job_benefits
        base_profile = company.base_profile
        company_profile = company.company_profile_v3
        
        # Politique télétravail
        remote_policy = job_benefits.remote_policy
        
        # Localisation bureau
        office_location = base_profile.poste.localisation
        
        # Culture entreprise
        company_culture = company_profile.company_culture
        
        # Taille équipe
        team_size = company_profile.team_size_hiring_for
        
        # Avantages liés au lieu de travail
        workplace_benefits = self._extract_workplace_benefits(job_benefits.job_benefits)
        
        return {
            "remote_policy": remote_policy,
            "office_location": office_location,
            "company_culture": company_culture,
            "team_size": team_size,
            "workplace_benefits": workplace_benefits,
            "growth_stage": company_profile.growth_stage,
            "company_size": company_profile.company_size,
            "schedule_flexibility": self._infer_schedule_flexibility(company)
        }
    
    def _analyze_remote_compatibility(
        self,
        candidate_preferences: Dict[str, Any],
        company_environment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🏠 Analyse compatibilité télétravail"""
        
        candidate_preference = candidate_preferences["office_preference"]
        company_policy = company_environment["remote_policy"]
        
        # Utilisation matrice compatibilité
        compatibility_matrix = self.scoring_config["remote_compatibility_matrix"]
        base_score = compatibility_matrix[candidate_preference][company_policy]
        
        # Bonus si candidat a expérience remote
        if candidate_preferences["remote_experience"] and company_policy in [
            WorkModalityType.FULL_REMOTE, WorkModalityType.HYBRID, WorkModalityType.FLEXIBLE
        ]:
            base_score = min(1.0, base_score * 1.1)
        
        # Bonus si management experience et remote
        if (candidate_preferences["management_experience"] and 
            company_policy == WorkModalityType.FULL_REMOTE):
            base_score = min(1.0, base_score * 1.05)
        
        # Évaluation niveau compatibilité
        if base_score >= 0.9:
            compatibility_level = "perfect"
        elif base_score >= 0.8:
            compatibility_level = "excellent"
        elif base_score >= 0.6:
            compatibility_level = "good"
        elif base_score >= 0.4:
            compatibility_level = "acceptable"
        else:
            compatibility_level = "problematic"
        
        return {
            "score": base_score,
            "compatibility_level": compatibility_level,
            "candidate_preference": candidate_preference.value,
            "company_policy": company_policy.value,
            "remote_experience_bonus": candidate_preferences["remote_experience"]
        }
    
    def _evaluate_schedule_flexibility(
        self,
        candidate_preferences: Dict[str, Any],
        company_environment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """⏰ Évaluation flexibilité horaires"""
        
        candidate_needs_flexibility = candidate_preferences["flexible_hours_important"]
        company_flexibility = company_environment["schedule_flexibility"]
        
        # Calcul score flexibilité
        if candidate_needs_flexibility:
            if company_flexibility >= 0.8:
                score = 1.0
                evaluation = "Excellente flexibilité horaires"
            elif company_flexibility >= 0.6:
                score = 0.8
                evaluation = "Bonne flexibilité horaires"
            elif company_flexibility >= 0.4:
                score = 0.6
                evaluation = "Flexibilité limitée"
            else:
                score = 0.3
                evaluation = "Horaires rigides"
        else:
            # Candidat n'a pas besoin de flexibilité
            score = 0.9
            evaluation = "Pas de contrainte horaires"
        
        # Bonus si startup/scale-up (généralement plus flexible)
        if company_environment["growth_stage"] in ["startup", "growth"]:
            score = min(1.0, score * 1.1)
            evaluation += " (startup/scale-up)"
        
        return {
            "score": score,
            "evaluation": evaluation,
            "candidate_needs_flexibility": candidate_needs_flexibility,
            "company_flexibility_level": company_flexibility
        }
    
    def _analyze_commute_compatibility(
        self,
        candidate_preferences: Dict[str, Any],
        company_environment: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """🚗 Analyse compatibilité trajets"""
        
        max_travel_time = candidate_preferences["max_travel_time"]
        office_location = company_environment["office_location"]
        remote_policy = company_environment["remote_policy"]
        
        # Si full remote, trajets non critiques
        if remote_policy == WorkModalityType.FULL_REMOTE:
            return {
                "score": 1.0,
                "evaluation": "Trajets non applicables (full remote)",
                "estimated_commute_time": 0,
                "parking_compatibility": True
            }
        
        # Estimation temps trajet (heuristique)
        estimated_commute = self._estimate_commute_time(office_location, context)
        
        # Calcul score trajet
        if estimated_commute <= max_travel_time:
            if estimated_commute <= max_travel_time * 0.7:
                score = 1.0
                evaluation = "Trajet très acceptable"
            else:
                score = 0.8
                evaluation = "Trajet acceptable"
        else:
            excess = estimated_commute - max_travel_time
            if excess <= 10:
                score = 0.6
                evaluation = "Trajet légèrement long"
            elif excess <= 20:
                score = 0.4
                evaluation = "Trajet problématique"
            else:
                score = 0.2
                evaluation = "Trajet trop long"
        
        # Bonus si hybrid (moins de trajets)
        if remote_policy == WorkModalityType.HYBRID:
            score = min(1.0, score * 1.2)
            evaluation += " (compensé par hybrid)"
        
        # Évaluation parking
        parking_compatibility = self._evaluate_parking_compatibility(
            candidate_preferences, company_environment
        )
        
        return {
            "score": score,
            "evaluation": evaluation,
            "estimated_commute_time": estimated_commute,
            "max_acceptable_time": max_travel_time,
            "parking_compatibility": parking_compatibility
        }
    
    def _assess_culture_alignment(
        self,
        candidate_preferences: Dict[str, Any],
        company_environment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🎭 Évaluation alignement culture"""
        
        company_culture = company_environment["company_culture"]
        remote_preference = candidate_preferences["office_preference"]
        
        # Score de base neutre
        score = 0.7
        alignment_factors = []
        
        # Analyse culture vs préférences travail
        if "Autonomie" in company_culture:
            if remote_preference in [WorkModalityType.FULL_REMOTE, WorkModalityType.HYBRID]:
                score += 0.2
                alignment_factors.append("Culture autonomie + préférence remote")
        
        if "Collaboration" in company_culture:
            if remote_preference in [WorkModalityType.ON_SITE, WorkModalityType.HYBRID]:
                score += 0.15
                alignment_factors.append("Culture collaboration + préférence présentiel")
        
        if "Innovation" in company_culture:
            if remote_preference == WorkModalityType.FLEXIBLE:
                score += 0.1
                alignment_factors.append("Culture innovation + flexibilité")
        
        # Bonus si management experience et culture leadership
        if (candidate_preferences["management_experience"] and 
            "Leadership" in company_culture):
            score += 0.1
            alignment_factors.append("Management experience + culture leadership")
        
        # Ajustement selon taille équipe
        team_size = company_environment["team_size"]
        if team_size <= 5 and remote_preference != WorkModalityType.FULL_REMOTE:
            score += 0.05
            alignment_factors.append("Petite équipe + préférence collaboration")
        
        score = min(1.0, score)
        
        return {
            "score": score,
            "alignment_factors": alignment_factors,
            "company_culture": company_culture,
            "culture_remote_compatibility": self._assess_culture_remote_compatibility(company_culture)
        }
    
    def _evaluate_workplace_benefits(
        self,
        candidate_preferences: Dict[str, Any],
        company_environment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🎁 Évaluation avantages lieu travail"""
        
        workplace_benefits = company_environment["workplace_benefits"]
        parking_required = candidate_preferences["parking_required"]
        
        score = 0.5  # Base neutre
        benefit_match = []
        
        # Évaluation parking
        if parking_required:
            if workplace_benefits.get("parking_provided", False):
                score += 0.3
                benefit_match.append("Parking fourni")
            else:
                score -= 0.2
                benefit_match.append("Parking manquant (requis)")
        
        # Bonus autres avantages liés au lieu
        if workplace_benefits.get("restaurant_tickets", False):
            score += 0.1
            benefit_match.append("Tickets restaurant")
        
        if workplace_benefits.get("gym_access", False):
            score += 0.1
            benefit_match.append("Accès salle sport")
        
        if workplace_benefits.get("coffee_snacks", False):
            score += 0.05
            benefit_match.append("Café/collations")
        
        # Bonus si bonne accessibilité transport public
        public_transport_score = candidate_preferences["public_transport_accessibility"]
        if public_transport_score >= 4:
            score += 0.1
            benefit_match.append("Bonne accessibilité transport public")
        
        score = min(1.0, max(0.0, score))
        
        return {
            "score": score,
            "matched_benefits": benefit_match,
            "workplace_benefits": workplace_benefits
        }
    
    def _calculate_weighted_score(
        self,
        remote_compatibility: Dict[str, Any],
        schedule_flexibility: Dict[str, Any],
        commute_analysis: Dict[str, Any],
        culture_alignment: Dict[str, Any],
        workplace_benefits: Dict[str, Any]
    ) -> float:
        """🧮 Calcul score final pondéré"""
        
        weights = self.scoring_config["weights"]
        
        final_score = (
            remote_compatibility["score"] * weights["remote_compatibility"] +
            schedule_flexibility["score"] * weights["schedule_flexibility"] +
            commute_analysis["score"] * weights["commute_analysis"] +
            culture_alignment["score"] * weights["culture_alignment"] +
            workplace_benefits["score"] * weights["workplace_benefits"]
        )
        
        return min(1.0, final_score)
    
    def _enrich_environment_result(
        self,
        final_score: float,
        candidate_preferences: Dict[str, Any],
        company_environment: Dict[str, Any],
        remote_compatibility: Dict[str, Any],
        schedule_flexibility: Dict[str, Any],
        commute_analysis: Dict[str, Any],
        culture_alignment: Dict[str, Any],
        workplace_benefits: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """🔧 Enrichissement résultat environnement"""
        
        # Détermination niveau compatibilité
        if final_score >= 0.9:
            compatibility_level = EnvironmentCompatibilityLevel.PERFECT
        elif final_score >= 0.8:
            compatibility_level = EnvironmentCompatibilityLevel.EXCELLENT
        elif final_score >= 0.7:
            compatibility_level = EnvironmentCompatibilityLevel.GOOD
        elif final_score >= 0.5:
            compatibility_level = EnvironmentCompatibilityLevel.ACCEPTABLE
        elif final_score >= 0.3:
            compatibility_level = EnvironmentCompatibilityLevel.PROBLEMATIC
        else:
            compatibility_level = EnvironmentCompatibilityLevel.INCOMPATIBLE
        
        # Génération explications
        explanations = self._generate_environment_explanations(
            final_score, candidate_preferences, company_environment,
            remote_compatibility, schedule_flexibility, commute_analysis
        )
        
        # Recommandations
        recommendations = self._generate_environment_recommendations(
            compatibility_level, candidate_preferences, company_environment,
            remote_compatibility, commute_analysis
        )
        
        return {
            "final_score": final_score,
            "compatibility_level": compatibility_level.value,
            "score_breakdown": {
                "remote_compatibility": remote_compatibility["score"],
                "schedule_flexibility": schedule_flexibility["score"],
                "commute_analysis": commute_analysis["score"],
                "culture_alignment": culture_alignment["score"],
                "workplace_benefits": workplace_benefits["score"]
            },
            "environment_analysis": {
                "candidate_office_preference": candidate_preferences["office_preference"].value,
                "company_remote_policy": company_environment["remote_policy"].value,
                "estimated_commute_time": commute_analysis["estimated_commute_time"],
                "max_acceptable_time": candidate_preferences["max_travel_time"],
                "culture_alignment_factors": culture_alignment["alignment_factors"],
                "workplace_benefits_matched": workplace_benefits["matched_benefits"]
            },
            "explanations": explanations,
            "recommendations": recommendations,
            "calculated_at": datetime.now().isoformat(),
            "version": self.version,
            "scorer": self.name
        }
    
    def _generate_environment_explanations(
        self,
        final_score: float,
        candidate_preferences: Dict[str, Any],
        company_environment: Dict[str, Any],
        remote_compatibility: Dict[str, Any],
        schedule_flexibility: Dict[str, Any],
        commute_analysis: Dict[str, Any]
    ) -> List[str]:
        """📝 Génération explications environnement"""
        
        explanations = []
        
        # Score principal
        explanations.append(
            f"🏢 Score environnement: {final_score:.2f}/1.0 "
            f"({candidate_preferences['office_preference'].value} vs {company_environment['remote_policy'].value})"
        )
        
        # Compatibilité télétravail
        explanations.append(
            f"🏠 Télétravail: {remote_compatibility['score']:.1%} "
            f"({remote_compatibility['compatibility_level']})"
        )
        
        # Flexibilité horaires
        explanations.append(
            f"⏰ Horaires: {schedule_flexibility['evaluation']}"
        )
        
        # Trajets
        if commute_analysis["estimated_commute_time"] > 0:
            explanations.append(
                f"🚗 Trajet: {commute_analysis['estimated_commute_time']}min "
                f"(max accepté: {commute_analysis['max_acceptable_time']}min)"
            )
        
        return explanations
    
    def _generate_environment_recommendations(
        self,
        compatibility_level: EnvironmentCompatibilityLevel,
        candidate_preferences: Dict[str, Any],
        company_environment: Dict[str, Any],
        remote_compatibility: Dict[str, Any],
        commute_analysis: Dict[str, Any]
    ) -> List[str]:
        """💡 Génération recommandations environnement"""
        
        recommendations = []
        
        if compatibility_level == EnvironmentCompatibilityLevel.PERFECT:
            recommendations.append("🌟 Environnement idéal - parfait match")
        
        elif compatibility_level == EnvironmentCompatibilityLevel.EXCELLENT:
            recommendations.append("✨ Excellent environnement - très bon match")
        
        elif compatibility_level == EnvironmentCompatibilityLevel.GOOD:
            recommendations.append("✅ Bon environnement - quelques ajustements possibles")
        
        elif compatibility_level == EnvironmentCompatibilityLevel.ACCEPTABLE:
            recommendations.append("⚠️ Environnement acceptable - négociation recommandée")
            
            # Suggestions spécifiques
            if remote_compatibility["score"] < 0.7:
                recommendations.append("💡 Négocier modalités télétravail")
            
            if commute_analysis["score"] < 0.6:
                recommendations.append("🚗 Considérer solutions transport/horaires")
        
        elif compatibility_level == EnvironmentCompatibilityLevel.PROBLEMATIC:
            recommendations.append("🚨 Environnement problématique - solutions requises")
            
            if remote_compatibility["score"] < 0.5:
                recommendations.append("🏠 Revoir politique télétravail")
            
            if commute_analysis["score"] < 0.4:
                recommendations.append("⏰ Horaires décalés ou aide transport")
        
        else:  # INCOMPATIBLE
            recommendations.append("❌ Environnement incompatible")
            
            candidate_pref = candidate_preferences["office_preference"]
            company_policy = company_environment["remote_policy"]
            
            if candidate_pref == WorkModalityType.FULL_REMOTE and company_policy == WorkModalityType.ON_SITE:
                recommendations.append("🏠 Candidat exige full remote, entreprise 100% présentiel")
            elif candidate_pref == WorkModalityType.ON_SITE and company_policy == WorkModalityType.FULL_REMOTE:
                recommendations.append("🏢 Candidat préfère présentiel, entreprise full remote")
        
        return recommendations
    
    def _extract_workplace_benefits(self, job_benefits: List[str]) -> Dict[str, bool]:
        """🎁 Extraction avantages lieu travail"""
        
        benefits = {
            "parking_provided": False,
            "restaurant_tickets": False,
            "gym_access": False,
            "coffee_snacks": False,
            "transport_allowance": False
        }
        
        for benefit in job_benefits:
            benefit_lower = benefit.lower()
            
            if "parking" in benefit_lower:
                benefits["parking_provided"] = True
            elif "restaurant" in benefit_lower or "ticket" in benefit_lower:
                benefits["restaurant_tickets"] = True
            elif "sport" in benefit_lower or "gym" in benefit_lower:
                benefits["gym_access"] = True
            elif "café" in benefit_lower or "coffee" in benefit_lower:
                benefits["coffee_snacks"] = True
            elif "transport" in benefit_lower or "navette" in benefit_lower:
                benefits["transport_allowance"] = True
        
        return benefits
    
    def _estimate_commute_time(self, office_location: str, context: Optional[Dict] = None) -> int:
        """🕐 Estimation temps trajet (heuristique)"""
        
        if context and "estimated_commute_time" in context:
            return context["estimated_commute_time"]
        
        # Heuristiques basiques
        location_lower = office_location.lower()
        
        if "paris" in location_lower:
            if "1er" in location_lower or "2e" in location_lower:
                return 25  # Paris centre
            elif "défense" in location_lower:
                return 35  # La Défense
            else:
                return 30  # Paris général
        elif "boulogne" in location_lower or "neuilly" in location_lower:
            return 30  # Proche banlieue
        elif "saint-denis" in location_lower or "montreuil" in location_lower:
            return 40  # Banlieue
        else:
            return 35  # Défaut
    
    def _evaluate_parking_compatibility(
        self,
        candidate_preferences: Dict[str, Any],
        company_environment: Dict[str, Any]
    ) -> bool:
        """🅿️ Évaluation compatibilité parking"""
        
        parking_required = candidate_preferences["parking_required"]
        parking_provided = company_environment["workplace_benefits"].get("parking_provided", False)
        
        if parking_required:
            return parking_provided
        else:
            return True  # Pas de contrainte
    
    def _infer_schedule_flexibility(self, company: ExtendedCompanyProfileV3) -> float:
        """⏰ Inférence flexibilité horaires"""
        
        flexibility = 0.5  # Base neutre
        
        # Bonus selon politique remote
        remote_policy = company.job_benefits.remote_policy
        if remote_policy == WorkModalityType.FLEXIBLE:
            flexibility += 0.3
        elif remote_policy in [WorkModalityType.FULL_REMOTE, WorkModalityType.HYBRID]:
            flexibility += 0.2
        
        # Bonus selon culture
        culture = company.company_profile_v3.company_culture
        if "Autonomie" in culture:
            flexibility += 0.2
        if "Innovation" in culture:
            flexibility += 0.1
        
        # Bonus selon taille entreprise
        company_size = company.company_profile_v3.company_size
        if company_size.value in ["startup", "pme"]:
            flexibility += 0.1
        
        return min(1.0, flexibility)
    
    def _assess_culture_remote_compatibility(self, company_culture: List[str]) -> float:
        """🎭 Évaluation compatibilité culture-remote"""
        
        compatibility = 0.5  # Base neutre
        
        positive_factors = ["Autonomie", "Innovation", "Confiance", "Résultats"]
        negative_factors = ["Collaboration", "Présence", "Contrôle"]
        
        for factor in positive_factors:
            if factor in company_culture:
                compatibility += 0.15
        
        for factor in negative_factors:
            if factor in company_culture:
                compatibility -= 0.1
        
        return min(1.0, max(0.0, compatibility))
    
    def _update_stats(self, score: float, office_preference: WorkModalityType):
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
        elif score <= 0.3:
            self.stats["incompatible_matches"] += 1
        
        # Compteur préférences remote
        pref_key = office_preference.value
        if pref_key not in self.stats["remote_preference_stats"]:
            self.stats["remote_preference_stats"][pref_key] = 0
        self.stats["remote_preference_stats"][pref_key] += 1
    
    def _create_fallback_score(
        self,
        candidate: ExtendedCandidateProfileV3,
        company: ExtendedCompanyProfileV3,
        error_message: str
    ) -> Dict[str, Any]:
        """🚨 Score fallback en cas d'erreur"""
        
        logger.warning(f"Fallback WorkEnvironmentScorer: {error_message}")
        
        # Score neutre conservateur
        fallback_score = 0.6
        
        # Ajustement heuristique
        candidate_pref = candidate.transport_preferences.office_preference
        company_policy = company.job_benefits.remote_policy
        
        if candidate_pref == company_policy:
            fallback_score = 0.8  # Bonus si match direct
        
        return {
            "final_score": fallback_score,
            "compatibility_level": EnvironmentCompatibilityLevel.ACCEPTABLE.value,
            "score_breakdown": {
                "remote_compatibility": fallback_score,
                "schedule_flexibility": fallback_score,
                "commute_analysis": fallback_score,
                "culture_alignment": fallback_score,
                "workplace_benefits": fallback_score
            },
            "environment_analysis": {
                "candidate_office_preference": candidate_pref.value,
                "company_remote_policy": company_policy.value,
                "estimated_commute_time": None
            },
            "explanations": [
                f"⚠️ Mode dégradé: {error_message}",
                f"📊 Score estimé: {fallback_score:.2f}"
            ],
            "recommendations": [
                "🛠️ Vérifier manuellement la compatibilité environnement",
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
                "average_score": self.stats["average_score"],
                "remote_preference_distribution": self.stats["remote_preference_stats"]
            },
            "configuration": self.scoring_config
        }
    
    def reset_stats(self):
        """🔄 Reset statistiques"""
        self.stats = {
            "total_calculations": 0,
            "perfect_matches": 0,
            "incompatible_matches": 0,
            "remote_preference_stats": {},
            "average_score": 0.0
        }
