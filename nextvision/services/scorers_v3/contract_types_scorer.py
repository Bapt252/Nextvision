"""
🚀 Nextvision V3.0 - ContractTypesScorer (PROMPT 7)
Score basé sur ordre préférence candidat vs offre entreprise

Fonctionnalités :
- Match exact = score 1.0
- Position dans ranking = score dégressif
- Pénalité si contrat proposé pas dans ranking
- Bonus si salaire compatible

Author: NEXTEN Team
Version: 3.0.0 - Contract Intelligence
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum

from nextvision.models.extended_bidirectional_models_v3 import (
    ExtendedCandidateProfileV3,
    ExtendedCompanyProfileV3,
    TypeContrat
)

logger = logging.getLogger(__name__)

class ContractCompatibilityLevel(str, Enum):
    """Niveaux de compatibilité contrat"""
    IDEAL = "ideal"
    PREFERRED = "preferred"
    ACCEPTABLE = "acceptable"
    NEGOTIABLE = "negotiable"
    INCOMPATIBLE = "incompatible"

class ContractTypesScorer:
    """
    📋 Scorer Contrats V3.0 - Contract Intelligence
    
    Évalue la compatibilité type contrat avec :
    - Ranking préférences candidat
    - Analyse salaire vs type contrat
    - Bonus/malus selon flexibilité
    - Intelligence négociation
    """
    
    def __init__(self):
        self.name = "ContractTypesScorer"
        self.version = "3.0.0"
        
        # Configuration scoring
        self.scoring_config = {
            "weights": {
                "contract_preference": 0.50,     # Position dans ranking
                "salary_compatibility": 0.30,   # Compatibilité salariale
                "flexibility_bonus": 0.15,      # Bonus flexibilité
                "negotiation_potential": 0.05   # Potentiel négociation
            },
            "preference_scoring": {
                1: 1.0,      # Première préférence
                2: 0.85,     # Deuxième préférence
                3: 0.65,     # Troisième préférence
                4: 0.40,     # Quatrième préférence
                5: 0.20      # Cinquième préférence
            },
            "contract_stability_weights": {
                TypeContrat.CDI: 1.0,
                TypeContrat.CDD: 0.7,
                TypeContrat.FREELANCE: 0.6,
                TypeContrat.INTERIM: 0.5,
                TypeContrat.STAGE: 0.3
            }
        }
        
        # Métriques performance
        self.stats = {
            "total_calculations": 0,
            "perfect_matches": 0,
            "incompatible_matches": 0,
            "most_preferred_contract": {},
            "average_score": 0.0
        }
    
    def calculate_contract_types_score(
        self,
        candidate: ExtendedCandidateProfileV3,
        company: ExtendedCompanyProfileV3,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        🎯 Calcule score compatibilité types contrat
        
        Args:
            candidate: Profil candidat V3.0
            company: Profil entreprise V3.0
            context: Contexte additionnel
            
        Returns:
            Score contrat avec détails et recommandations
        """
        
        start_time = datetime.now()
        self.stats["total_calculations"] += 1
        
        try:
            # 1. Extraction préférences candidat
            candidate_preferences = self._extract_candidate_preferences(candidate)
            
            # 2. Extraction offre entreprise
            company_offer = self._extract_company_offer(company)
            
            # 3. Calcul score préférence contrat
            preference_score = self._calculate_preference_score(
                candidate_preferences, company_offer
            )
            
            # 4. Analyse compatibilité salariale
            salary_compatibility = self._analyze_salary_compatibility(
                candidate_preferences, company_offer
            )
            
            # 5. Évaluation flexibilité
            flexibility_bonus = self._evaluate_flexibility_bonus(
                candidate_preferences, company_offer
            )
            
            # 6. Potentiel négociation
            negotiation_potential = self._assess_negotiation_potential(
                candidate_preferences, company_offer, context
            )
            
            # 7. Score final pondéré
            final_score = self._calculate_weighted_score(
                preference_score, salary_compatibility, 
                flexibility_bonus, negotiation_potential
            )
            
            # 8. Enrichissement avec détails
            result = self._enrich_contract_result(
                final_score, candidate_preferences, company_offer,
                preference_score, salary_compatibility, 
                flexibility_bonus, negotiation_potential,
                context
            )
            
            # 9. Mise à jour statistiques
            self._update_stats(final_score, company_offer["contract_type"])
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            result["processing_time_ms"] = processing_time
            
            logger.info(
                f"📋 ContractTypesScorer: {final_score:.3f} "
                f"({result['compatibility_level']}, {processing_time:.1f}ms)"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur ContractTypesScorer: {e}")
            return self._create_fallback_score(candidate, company, str(e))
    
    def _extract_candidate_preferences(self, candidate: ExtendedCandidateProfileV3) -> Dict[str, Any]:
        """📊 Extraction préférences candidat"""
        
        base_profile = candidate.base_profile
        transport_prefs = candidate.transport_preferences
        
        # Ranking contrats depuis transport_preferences
        contract_ranking = transport_prefs.contract_ranking
        
        # Si pas de ranking, utiliser données base
        if not contract_ranking:
            contract_ranking = [TypeContrat.CDI, TypeContrat.CDD, TypeContrat.FREELANCE]
        
        # Attentes salariales
        salary_expectations = {
            "min": base_profile.attentes.salaire_min,
            "max": base_profile.attentes.salaire_max,
            "currency": "EUR"
        }
        
        # Évaluation flexibilité
        flexibility_level = self._evaluate_candidate_flexibility(candidate)
        
        return {
            "contract_ranking": contract_ranking,
            "salary_expectations": salary_expectations,
            "flexibility_level": flexibility_level,
            "experience_level": base_profile.experience_globale,
            "current_status": candidate.availability_timing.employment_status,
            "listening_reasons": candidate.availability_timing.listening_reasons
        }
    
    def _extract_company_offer(self, company: ExtendedCompanyProfileV3) -> Dict[str, Any]:
        """🏢 Extraction offre entreprise"""
        
        base_profile = company.base_profile
        job_benefits = company.job_benefits
        
        # Type contrat proposé
        contract_type = job_benefits.contract_nature
        
        # Fourchette salariale
        salary_range = {
            "min": base_profile.poste.salaire_min or 0,
            "max": base_profile.poste.salaire_max or 999999,
            "currency": "EUR"
        }
        
        # Évaluation marge négociation
        negotiation_margin = self._evaluate_negotiation_margin(company)
        
        return {
            "contract_type": contract_type,
            "salary_range": salary_range,
            "negotiation_margin": negotiation_margin,
            "urgency_level": base_profile.recrutement.urgence,
            "benefits": job_benefits.job_benefits,
            "bonus_structure": job_benefits.bonus_structure,
            "trial_period": company.recruitment_process.trial_period_duration
        }
    
    def _calculate_preference_score(
        self,
        candidate_preferences: Dict[str, Any],
        company_offer: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🎯 Calcul score préférence contrat"""
        
        contract_ranking = candidate_preferences["contract_ranking"]
        offered_contract = company_offer["contract_type"]
        
        # Recherche position dans ranking
        try:
            position = contract_ranking.index(offered_contract) + 1
            preference_score = self.scoring_config["preference_scoring"].get(position, 0.0)
            
            if position == 1:
                preference_level = ContractCompatibilityLevel.IDEAL
            elif position == 2:
                preference_level = ContractCompatibilityLevel.PREFERRED
            elif position <= 3:
                preference_level = ContractCompatibilityLevel.ACCEPTABLE
            else:
                preference_level = ContractCompatibilityLevel.NEGOTIABLE
            
        except ValueError:
            # Contrat non dans ranking
            preference_score = 0.1
            preference_level = ContractCompatibilityLevel.INCOMPATIBLE
            position = len(contract_ranking) + 1
        
        return {
            "score": preference_score,
            "level": preference_level,
            "position_in_ranking": position,
            "total_preferences": len(contract_ranking),
            "offered_contract": offered_contract.value
        }
    
    def _analyze_salary_compatibility(
        self,
        candidate_preferences: Dict[str, Any],
        company_offer: Dict[str, Any]
    ) -> Dict[str, Any]:
        """💰 Analyse compatibilité salariale"""
        
        candidate_min = candidate_preferences["salary_expectations"]["min"]
        candidate_max = candidate_preferences["salary_expectations"]["max"]
        company_min = company_offer["salary_range"]["min"]
        company_max = company_offer["salary_range"]["max"]
        
        # Calcul overlap
        overlap_exists = company_max >= candidate_min and company_min <= candidate_max
        
        if overlap_exists:
            overlap_amount = min(candidate_max, company_max) - max(candidate_min, company_min)
            candidate_range = candidate_max - candidate_min
            company_range = company_max - company_min
            avg_range = (candidate_range + company_range) / 2
            
            if avg_range > 0:
                compatibility_score = min(1.0, overlap_amount / avg_range)
            else:
                compatibility_score = 1.0
        else:
            # Pas d'overlap - calculer distance
            if candidate_min > company_max:
                gap = candidate_min - company_max
                compatibility_score = max(0.0, 1.0 - (gap / candidate_min))
            else:
                gap = company_min - candidate_max
                compatibility_score = max(0.0, 1.0 - (gap / company_min))
        
        # Ajustement selon type contrat
        contract_type = company_offer["contract_type"]
        stability_weight = self.scoring_config["contract_stability_weights"].get(contract_type, 1.0)
        
        # Bonus si CDI avec salaire correct
        if contract_type == TypeContrat.CDI and compatibility_score > 0.7:
            compatibility_score = min(1.0, compatibility_score * 1.1)
        
        return {
            "score": compatibility_score,
            "overlap_exists": overlap_exists,
            "overlap_amount": overlap_amount if overlap_exists else 0,
            "contract_stability_weight": stability_weight,
            "candidate_range": f"{candidate_min}€ - {candidate_max}€",
            "company_range": f"{company_min}€ - {company_max}€"
        }
    
    def _evaluate_flexibility_bonus(
        self,
        candidate_preferences: Dict[str, Any],
        company_offer: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🔄 Évaluation bonus flexibilité"""
        
        bonus_score = 0.0
        bonus_details = []
        
        # Bonus si candidat flexible sur contrats
        flexibility_level = candidate_preferences["flexibility_level"]
        if flexibility_level >= 0.8:
            bonus_score += 0.3
            bonus_details.append("Candidat très flexible sur types contrat")
        elif flexibility_level >= 0.6:
            bonus_score += 0.2
            bonus_details.append("Candidat moyennement flexible")
        
        # Bonus si entreprise propose avantages
        benefits = company_offer.get("benefits", [])
        if len(benefits) >= 5:
            bonus_score += 0.2
            bonus_details.append(f"Nombreux avantages proposés ({len(benefits)})")
        elif len(benefits) >= 3:
            bonus_score += 0.1
            bonus_details.append("Avantages intéressants")
        
        # Bonus structure bonus
        bonus_structure = company_offer.get("bonus_structure", "None")
        if bonus_structure != "None":
            bonus_score += 0.1
            bonus_details.append(f"Structure bonus: {bonus_structure}")
        
        # Bonus si période d'essai raisonnable
        trial_period = company_offer.get("trial_period", 0)
        if trial_period <= 3:
            bonus_score += 0.1
            bonus_details.append("Période d'essai raisonnable")
        
        return {
            "score": min(1.0, bonus_score),
            "details": bonus_details
        }
    
    def _assess_negotiation_potential(
        self,
        candidate_preferences: Dict[str, Any],
        company_offer: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """🤝 Évaluation potentiel négociation"""
        
        negotiation_score = 0.5  # Base neutre
        negotiation_factors = []
        
        # Facteur urgence entreprise
        urgency_level = company_offer["urgency_level"]
        if urgency_level.value in ["CRITIQUE", "URGENT"]:
            negotiation_score += 0.2
            negotiation_factors.append("Urgence entreprise favorable")
        
        # Facteur expérience candidat
        experience_level = candidate_preferences["experience_level"]
        if experience_level.value in ["CONFIRME", "SENIOR"]:
            negotiation_score += 0.2
            negotiation_factors.append("Expérience candidat valorisable")
        
        # Facteur marge négociation entreprise
        negotiation_margin = company_offer["negotiation_margin"]
        if negotiation_margin >= 0.8:
            negotiation_score += 0.2
            negotiation_factors.append("Entreprise flexible sur négociation")
        elif negotiation_margin >= 0.6:
            negotiation_score += 0.1
            negotiation_factors.append("Marge négociation correcte")
        
        # Facteur statut candidat
        current_status = candidate_preferences["current_status"]
        if current_status.value == "EN_POSTE":
            negotiation_score += 0.1
            negotiation_factors.append("Candidat en poste - position forte")
        
        return {
            "score": min(1.0, negotiation_score),
            "factors": negotiation_factors
        }
    
    def _calculate_weighted_score(
        self,
        preference_score: Dict[str, Any],
        salary_compatibility: Dict[str, Any],
        flexibility_bonus: Dict[str, Any],
        negotiation_potential: Dict[str, Any]
    ) -> float:
        """🧮 Calcul score final pondéré"""
        
        weights = self.scoring_config["weights"]
        
        final_score = (
            preference_score["score"] * weights["contract_preference"] +
            salary_compatibility["score"] * weights["salary_compatibility"] +
            flexibility_bonus["score"] * weights["flexibility_bonus"] +
            negotiation_potential["score"] * weights["negotiation_potential"]
        )
        
        return min(1.0, final_score)
    
    def _enrich_contract_result(
        self,
        final_score: float,
        candidate_preferences: Dict[str, Any],
        company_offer: Dict[str, Any],
        preference_score: Dict[str, Any],
        salary_compatibility: Dict[str, Any],
        flexibility_bonus: Dict[str, Any],
        negotiation_potential: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """🔧 Enrichissement résultat contrat"""
        
        # Détermination niveau compatibilité
        if final_score >= 0.9:
            compatibility_level = ContractCompatibilityLevel.IDEAL
        elif final_score >= 0.75:
            compatibility_level = ContractCompatibilityLevel.PREFERRED
        elif final_score >= 0.5:
            compatibility_level = ContractCompatibilityLevel.ACCEPTABLE
        elif final_score >= 0.25:
            compatibility_level = ContractCompatibilityLevel.NEGOTIABLE
        else:
            compatibility_level = ContractCompatibilityLevel.INCOMPATIBLE
        
        # Génération explications
        explanations = self._generate_contract_explanations(
            final_score, candidate_preferences, company_offer,
            preference_score, salary_compatibility, flexibility_bonus
        )
        
        # Recommandations
        recommendations = self._generate_contract_recommendations(
            compatibility_level, candidate_preferences, company_offer,
            negotiation_potential
        )
        
        return {
            "final_score": final_score,
            "compatibility_level": compatibility_level.value,
            "score_breakdown": {
                "contract_preference": preference_score["score"],
                "salary_compatibility": salary_compatibility["score"],
                "flexibility_bonus": flexibility_bonus["score"],
                "negotiation_potential": negotiation_potential["score"]
            },
            "contract_analysis": {
                "preferred_contracts": [c.value for c in candidate_preferences["contract_ranking"]],
                "offered_contract": company_offer["contract_type"].value,
                "position_in_ranking": preference_score["position_in_ranking"],
                "salary_overlap": salary_compatibility["overlap_exists"],
                "negotiation_margin": company_offer["negotiation_margin"]
            },
            "explanations": explanations,
            "recommendations": recommendations,
            "calculated_at": datetime.now().isoformat(),
            "version": self.version,
            "scorer": self.name
        }
    
    def _generate_contract_explanations(
        self,
        final_score: float,
        candidate_preferences: Dict[str, Any],
        company_offer: Dict[str, Any],
        preference_score: Dict[str, Any],
        salary_compatibility: Dict[str, Any],
        flexibility_bonus: Dict[str, Any]
    ) -> List[str]:
        """📝 Génération explications contrat"""
        
        explanations = []
        
        # Score principal
        explanations.append(
            f"📋 Score contrat: {final_score:.2f}/1.0 "
            f"({preference_score['offered_contract']} vs préférences candidat)"
        )
        
        # Position dans ranking
        position = preference_score["position_in_ranking"]
        total = preference_score["total_preferences"]
        
        if position == 1:
            explanations.append("🌟 Contrat = première préférence candidat")
        elif position <= total:
            explanations.append(
                f"📊 Contrat = {position}e choix sur {total} préférences"
            )
        else:
            explanations.append("❌ Contrat non dans préférences candidat")
        
        # Compatibilité salariale
        if salary_compatibility["overlap_exists"]:
            explanations.append(
                f"💰 Fourchettes compatibles: {salary_compatibility['overlap_amount']}€ d'overlap"
            )
        else:
            explanations.append("⚠️ Fourchettes salariales non compatibles")
        
        # Bonus flexibilité
        if flexibility_bonus["score"] > 0:
            explanations.append(
                f"🔄 Bonus flexibilité: +{flexibility_bonus['score']:.1%}"
            )
        
        return explanations
    
    def _generate_contract_recommendations(
        self,
        compatibility_level: ContractCompatibilityLevel,
        candidate_preferences: Dict[str, Any],
        company_offer: Dict[str, Any],
        negotiation_potential: Dict[str, Any]
    ) -> List[str]:
        """💡 Génération recommandations contrat"""
        
        recommendations = []
        
        if compatibility_level == ContractCompatibilityLevel.IDEAL:
            recommendations.append("🌟 Contrat idéal - procéder sans négociation")
        
        elif compatibility_level == ContractCompatibilityLevel.PREFERRED:
            recommendations.append("✅ Bon contrat - négociation légère possible")
        
        elif compatibility_level == ContractCompatibilityLevel.ACCEPTABLE:
            recommendations.append("⚠️ Contrat acceptable - négocier avantages")
            
            # Suggestions spécifiques
            if negotiation_potential["score"] > 0.7:
                recommendations.append("💡 Bonne marge négociation - améliorer conditions")
        
        elif compatibility_level == ContractCompatibilityLevel.NEGOTIABLE:
            recommendations.append("🤝 Contrat négociable - discussion approfondie requise")
            
            # Suggestions basées sur préférences
            ranking = candidate_preferences["contract_ranking"]
            if len(ranking) > 0:
                preferred = ranking[0].value
                recommendations.append(f"💡 Candidat préfère: {preferred}")
        
        else:  # INCOMPATIBLE
            recommendations.append("❌ Contrat incompatible - revoir proposition")
            
            # Suggestions alternatives
            if len(candidate_preferences["contract_ranking"]) > 0:
                alternatives = [c.value for c in candidate_preferences["contract_ranking"][:2]]
                recommendations.append(f"🔄 Alternatives: {', '.join(alternatives)}")
        
        return recommendations
    
    def _evaluate_candidate_flexibility(self, candidate: ExtendedCandidateProfileV3) -> float:
        """🔄 Évaluation flexibilité candidat"""
        
        flexibility = 0.5  # Base neutre
        
        # Bonus selon nombre de contrats acceptés
        contract_count = len(candidate.transport_preferences.contract_ranking)
        if contract_count >= 4:
            flexibility += 0.3
        elif contract_count >= 3:
            flexibility += 0.2
        elif contract_count >= 2:
            flexibility += 0.1
        
        # Bonus selon statut
        if candidate.availability_timing.employment_status.value == "DEMANDEUR_EMPLOI":
            flexibility += 0.2
        
        # Bonus selon listening reasons
        listening_reasons = candidate.availability_timing.listening_reasons
        if any("FLEXIBILITE" in reason.value for reason in listening_reasons):
            flexibility += 0.2
        
        return min(1.0, flexibility)
    
    def _evaluate_negotiation_margin(self, company: ExtendedCompanyProfileV3) -> float:
        """🤝 Évaluation marge négociation entreprise"""
        
        margin = 0.5  # Base neutre
        
        # Bonus selon urgence
        urgency = company.base_profile.recrutement.urgence
        if urgency.value in ["CRITIQUE", "URGENT"]:
            margin += 0.3
        elif urgency.value == "NORMAL":
            margin += 0.1
        
        # Bonus selon avantages proposés
        benefits_count = len(company.job_benefits.job_benefits)
        if benefits_count >= 5:
            margin += 0.2
        elif benefits_count >= 3:
            margin += 0.1
        
        return min(1.0, margin)
    
    def _update_stats(self, score: float, contract_type: TypeContrat):
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
        
        # Compteur types contrats
        contract_key = contract_type.value
        if contract_key not in self.stats["most_preferred_contract"]:
            self.stats["most_preferred_contract"][contract_key] = 0
        self.stats["most_preferred_contract"][contract_key] += 1
    
    def _create_fallback_score(
        self,
        candidate: ExtendedCandidateProfileV3,
        company: ExtendedCompanyProfileV3,
        error_message: str
    ) -> Dict[str, Any]:
        """🚨 Score fallback en cas d'erreur"""
        
        logger.warning(f"Fallback ContractTypesScorer: {error_message}")
        
        # Score neutre conservateur
        fallback_score = 0.6
        
        # Ajustement heuristique
        if company.job_benefits.contract_nature == TypeContrat.CDI:
            fallback_score = 0.7  # Bonus CDI
        
        return {
            "final_score": fallback_score,
            "compatibility_level": ContractCompatibilityLevel.ACCEPTABLE.value,
            "score_breakdown": {
                "contract_preference": fallback_score,
                "salary_compatibility": fallback_score,
                "flexibility_bonus": 0.0,
                "negotiation_potential": fallback_score
            },
            "contract_analysis": {
                "offered_contract": company.job_benefits.contract_nature.value,
                "position_in_ranking": None,
                "salary_overlap": None
            },
            "explanations": [
                f"⚠️ Mode dégradé: {error_message}",
                f"📊 Score estimé: {fallback_score:.2f}"
            ],
            "recommendations": [
                "🛠️ Vérifier manuellement la compatibilité contrat",
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
                "most_preferred_contracts": self.stats["most_preferred_contract"]
            },
            "configuration": self.scoring_config
        }
    
    def reset_stats(self):
        """🔄 Reset statistiques"""
        self.stats = {
            "total_calculations": 0,
            "perfect_matches": 0,
            "incompatible_matches": 0,
            "most_preferred_contract": {},
            "average_score": 0.0
        }
