"""
💰 Nextvision V3.0 - SalaryProgressionScorer (3% Weight)
=======================================================

Score la compatibilité évolution salariale candidat vs opportunités entreprise
- Analyse salary_progression_expectations candidat vs career_progression_timeline
- Réalisme attentes selon niveau d'expérience et marché
- Compatibilité timeline progression souhaitée vs offerte
- Opportunités concrètes : position_evolution_path vs ambitions
- Integration motivations EVOLUTION_CARRIERE
- Performance ultra-optimisée <5ms (3% du budget 175ms)

Author: NEXTEN Team
Version: 3.0.0 - Salary Progression Intelligence
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
import re

from nextvision.models.extended_bidirectional_models_v3 import (
    ExtendedCandidateProfileV3,
    ExtendedCompanyProfileV3,
    MotivationType
)
from nextvision.models.bidirectional_models import NiveauExperience

logger = logging.getLogger(__name__)

class ProgressionCompatibilityLevel(str, Enum):
    """Niveaux de compatibilité progression salariale"""
    EXCELLENT = "excellent"
    GOOD = "good"
    REALISTIC = "realistic"
    OPTIMISTIC = "optimistic"
    UNREALISTIC = "unrealistic"

class SalaryProgressionScorer:
    """
    💰 Salary Progression Scorer V3.0 - Intelligence Évolution Salariale
    
    Évalue la compatibilité progression salariale avec logique métier avancée :
    - Analyse attentes candidat vs opportunités réelles entreprise
    - Réalisme selon niveau d'expérience et standards marché
    - Compatibilité timeline progression (1-2 ans vs 3-5 ans)
    - Opportunités concrètes : budget formation, évolution path
    - Integration motivations EVOLUTION_CARRIERE
    - Performance <5ms ultra-optimisée
    """
    
    def __init__(self):
        self.name = "SalaryProgressionScorer"
        self.version = "3.0.0"
        
        # Références marché par niveau d'expérience (optimisées performance)
        self.market_progression_standards = {
            NiveauExperience.JUNIOR: {
                "annual_increase_range": (0.05, 0.15),  # 5-15% par an
                "3_year_total_increase": (0.20, 0.45),  # 20-45% sur 3 ans
                "realistic_ceiling": 1.5,  # Max 50% d'augmentation réaliste
                "typical_timeline": "2-3 ans",
                "progression_speed": "moderate"
            },
            NiveauExperience.CONFIRME: {
                "annual_increase_range": (0.03, 0.10),  # 3-10% par an
                "3_year_total_increase": (0.10, 0.30),  # 10-30% sur 3 ans
                "realistic_ceiling": 1.3,  # Max 30% d'augmentation réaliste
                "typical_timeline": "3-4 ans",
                "progression_speed": "steady"
            },
            NiveauExperience.SENIOR: {
                "annual_increase_range": (0.02, 0.08),  # 2-8% par an
                "3_year_total_increase": (0.08, 0.25),  # 8-25% sur 3 ans
                "realistic_ceiling": 1.25,  # Max 25% d'augmentation réaliste
                "typical_timeline": "3-5 ans",
                "progression_speed": "gradual"
            },
            NiveauExperience.EXPERT: {
                "annual_increase_range": (0.02, 0.06),  # 2-6% par an
                "3_year_total_increase": (0.06, 0.20),  # 6-20% sur 3 ans
                "realistic_ceiling": 1.20,  # Max 20% d'augmentation réaliste
                "typical_timeline": "4-6 ans",
                "progression_speed": "slow"
            }
        }
        
        # Modifiers selon contexte entreprise
        self.company_modifiers = {
            "startup": {
                "progression_multiplier": 1.3,
                "timeline_acceleration": 0.8,  # Plus rapide
                "risk_factor": 1.2,
                "description": "Startup - Progression rapide mais risquée"
            },
            "scale-up": {
                "progression_multiplier": 1.2,
                "timeline_acceleration": 0.9,
                "risk_factor": 1.1,
                "description": "Scale-up - Croissance soutenue"
            },
            "growth": {
                "progression_multiplier": 1.15,
                "timeline_acceleration": 0.95,
                "risk_factor": 1.0,
                "description": "Croissance - Opportunités régulières"
            },
            "stable": {
                "progression_multiplier": 1.0,
                "timeline_acceleration": 1.0,
                "risk_factor": 0.9,
                "description": "Stable - Progression prévisible"
            },
            "restructuring": {
                "progression_multiplier": 0.8,
                "timeline_acceleration": 1.3,  # Plus lent
                "risk_factor": 1.4,
                "description": "Restructuration - Progression limitée"
            }
        }
        
        # Timeline parsing (optimisé performance)
        self.timeline_patterns = {
            r"1-2|1 à 2": {"min_years": 1, "max_years": 2, "avg_years": 1.5},
            r"2-3|2 à 3": {"min_years": 2, "max_years": 3, "avg_years": 2.5},
            r"3-4|3 à 4": {"min_years": 3, "max_years": 4, "avg_years": 3.5},
            r"3-5|3 à 5": {"min_years": 3, "max_years": 5, "avg_years": 4.0},
            r"4-6|4 à 6": {"min_years": 4, "max_years": 6, "avg_years": 5.0},
            r"1 an": {"min_years": 1, "max_years": 1, "avg_years": 1.0},
            r"2 ans": {"min_years": 2, "max_years": 2, "avg_years": 2.0},
            r"3 ans": {"min_years": 3, "max_years": 3, "avg_years": 3.0},
        }
        
        # Métriques performance
        self.stats = {
            "calculations": 0,
            "average_processing_time": 0.0,
            "compatibility_distribution": {level.value: 0 for level in ProgressionCompatibilityLevel}
        }
    
    def calculate_salary_progression_score(
        self,
        candidate: ExtendedCandidateProfileV3,
        company: ExtendedCompanyProfileV3,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        💰 Calcule score compatibilité progression salariale
        
        Target: <5ms (3% du budget 175ms)
        """
        start_time = datetime.now()
        self.stats["calculations"] += 1
        
        try:
            # 1. Extraction rapide données progression
            progression_data = self._extract_progression_data(candidate, company)
            
            if not progression_data["has_candidate_expectations"]:
                return self._create_fallback_score("Pas d'attentes progression candidat")
            
            # 2. Analyse réalisme attentes candidat
            realism_analysis = self._analyze_candidate_realism(progression_data)
            
            # 3. Analyse opportunités entreprise
            company_opportunities = self._analyze_company_opportunities(progression_data)
            
            # 4. Calcul compatibilité timeline
            timeline_compatibility = self._calculate_timeline_compatibility(
                progression_data, company_opportunities
            )
            
            # 5. Score final avec modifiers
            final_score = self._calculate_final_progression_score(
                realism_analysis, company_opportunities, timeline_compatibility
            )
            
            # 6. Enrichissement résultat
            result = self._enrich_progression_result(
                final_score, progression_data, realism_analysis,
                company_opportunities, timeline_compatibility, context
            )
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            result["processing_time_ms"] = processing_time
            
            # Mise à jour stats
            self._update_stats(processing_time, realism_analysis["compatibility_level"])
            
            logger.info(
                f"💰 SalaryProgressionScorer: {final_score:.3f} "
                f"({realism_analysis['compatibility_level']}, {processing_time:.1f}ms)"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur SalaryProgressionScorer: {e}")
            return self._create_fallback_score(f"Erreur: {str(e)}")
    
    def _extract_progression_data(
        self,
        candidate: ExtendedCandidateProfileV3,
        company: ExtendedCompanyProfileV3
    ) -> Dict[str, Any]:
        """📊 Extraction données progression salariale"""
        
        # Données candidat
        salary_expectations = candidate.salary_progression_expectations or {}
        current_salary = candidate.base_profile.attentes.salaire_souhaite or 0
        experience_level = candidate.base_profile.experience.niveau
        
        # Motivations évolution carrière
        motivations = candidate.motivations_ranking.motivations_ranking or {}
        career_motivation = motivations.get(MotivationType.EVOLUTION_CARRIERE, 0)
        
        # Données entreprise
        progression_timeline = company.job_benefits.career_progression_timeline or "2-3 ans"
        development_budget = company.job_benefits.professional_development_budget
        bonus_structure = company.job_benefits.bonus_structure or "None"
        evolution_path = company.position_evolution_path or []
        growth_stage = company.company_profile_v3.growth_stage or "stable"
        
        return {
            # Candidat
            "salary_expectations": salary_expectations,
            "current_salary": current_salary,
            "experience_level": experience_level,
            "career_motivation": career_motivation,
            "has_candidate_expectations": bool(salary_expectations),
            
            # Entreprise
            "progression_timeline": progression_timeline,
            "development_budget": development_budget,
            "bonus_structure": bonus_structure,
            "evolution_path": evolution_path,
            "growth_stage": growth_stage,
            
            # Métadonnées
            "has_development_budget": development_budget is not None and development_budget > 0,
            "has_evolution_path": bool(evolution_path),
            "has_variable_compensation": bonus_structure in ["Variable", "Commission"]
        }
    
    def _analyze_candidate_realism(self, progression_data: Dict[str, Any]) -> Dict[str, Any]:
        """🔍 Analyse réalisme attentes candidat"""
        
        expectations = progression_data["salary_expectations"]
        current_salary = progression_data["current_salary"]
        experience_level = progression_data["experience_level"]
        
        if not expectations or current_salary <= 0:
            return {
                "realism_score": 0.5,
                "compatibility_level": ProgressionCompatibilityLevel.REALISTIC,
                "realism_factors": ["Données insuffisantes pour analyse"],
                "concerns": []
            }
        
        # Standards marché pour ce niveau
        market_standards = self.market_progression_standards.get(
            experience_level, self.market_progression_standards[NiveauExperience.CONFIRME]
        )
        
        realism_factors = []
        concerns = []
        total_realism_score = 0.0
        analyses_count = 0
        
        # Analyse par période d'expectation
        for period, target_salary in expectations.items():
            if target_salary <= current_salary:
                continue
            
            years = self._extract_years_from_period(period)
            if years <= 0:
                continue
            
            # Calcul augmentation demandée
            increase_factor = target_salary / current_salary
            annual_increase = (increase_factor ** (1/years)) - 1
            total_increase = increase_factor - 1
            
            # Évaluation réalisme
            annual_range = market_standards["annual_increase_range"]
            total_ceiling = market_standards["realistic_ceiling"] - 1
            
            period_realism = 1.0
            
            # Vérification augmentation annuelle
            if annual_increase <= annual_range[1]:
                if annual_increase >= annual_range[0]:
                    realism_factors.append(f"Augmentation {period} réaliste ({annual_increase:.1%}/an)")
                    period_realism *= 1.0
                else:
                    realism_factors.append(f"Augmentation {period} modeste ({annual_increase:.1%}/an)")
                    period_realism *= 0.9
            else:
                if annual_increase <= annual_range[1] * 1.5:
                    concerns.append(f"Augmentation {period} optimiste ({annual_increase:.1%}/an)")
                    period_realism *= 0.7
                else:
                    concerns.append(f"Augmentation {period} irréaliste ({annual_increase:.1%}/an)")
                    period_realism *= 0.4
            
            # Vérification plafond total
            if total_increase <= total_ceiling:
                period_realism *= 1.0
            elif total_increase <= total_ceiling * 1.3:
                period_realism *= 0.8
            else:
                period_realism *= 0.5
                concerns.append(f"Augmentation totale {period} excessive ({total_increase:.1%})")
            
            total_realism_score += period_realism
            analyses_count += 1
        
        # Score global
        if analyses_count > 0:
            average_realism = total_realism_score / analyses_count
        else:
            average_realism = 0.5
        
        # Détermination niveau compatibilité
        if average_realism >= 0.9:
            compatibility_level = ProgressionCompatibilityLevel.EXCELLENT
        elif average_realism >= 0.75:
            compatibility_level = ProgressionCompatibilityLevel.GOOD
        elif average_realism >= 0.6:
            compatibility_level = ProgressionCompatibilityLevel.REALISTIC
        elif average_realism >= 0.4:
            compatibility_level = ProgressionCompatibilityLevel.OPTIMISTIC
        else:
            compatibility_level = ProgressionCompatibilityLevel.UNREALISTIC
        
        return {
            "realism_score": average_realism,
            "compatibility_level": compatibility_level,
            "realism_factors": realism_factors,
            "concerns": concerns,
            "analyses_count": analyses_count,
            "market_standards": {
                "experience_level": experience_level.value,
                "annual_range": f"{market_standards['annual_increase_range'][0]:.1%}-{market_standards['annual_increase_range'][1]:.1%}",
                "typical_timeline": market_standards["typical_timeline"]
            }
        }
    
    def _analyze_company_opportunities(self, progression_data: Dict[str, Any]) -> Dict[str, Any]:
        """🏢 Analyse opportunités entreprise"""
        
        # Parse timeline entreprise
        timeline_data = self._parse_progression_timeline(progression_data["progression_timeline"])
        
        # Évaluation opportunités
        opportunities_score = 0.5  # Base
        opportunity_factors = []
        limitations = []
        
        # 1. Timeline progression
        if timeline_data["avg_years"] <= 2.5:
            opportunities_score += 0.2
            opportunity_factors.append("Timeline progression rapide")
        elif timeline_data["avg_years"] <= 3.5:
            opportunities_score += 0.1
            opportunity_factors.append("Timeline progression standard")
        else:
            limitations.append("Timeline progression lente")
        
        # 2. Budget développement
        if progression_data["has_development_budget"]:
            budget = progression_data["development_budget"]
            if budget >= 5000:
                opportunities_score += 0.15
                opportunity_factors.append(f"Budget formation élevé ({budget}€)")
            elif budget >= 2000:
                opportunities_score += 0.1
                opportunity_factors.append(f"Budget formation correct ({budget}€)")
            else:
                opportunities_score += 0.05
                opportunity_factors.append(f"Budget formation limité ({budget}€)")
        else:
            limitations.append("Pas de budget formation défini")
        
        # 3. Path d'évolution
        if progression_data["has_evolution_path"]:
            path_length = len(progression_data["evolution_path"])
            if path_length >= 3:
                opportunities_score += 0.15
                opportunity_factors.append(f"Path évolution détaillé ({path_length} étapes)")
            elif path_length >= 2:
                opportunities_score += 0.1
                opportunity_factors.append(f"Path évolution défini ({path_length} étapes)")
            else:
                opportunities_score += 0.05
                opportunity_factors.append("Path évolution basique")
        else:
            limitations.append("Pas de path d'évolution défini")
        
        # 4. Structure rémunération variable
        if progression_data["has_variable_compensation"]:
            opportunities_score += 0.1
            opportunity_factors.append(f"Rémunération variable ({progression_data['bonus_structure']})")
        
        # 5. Modifier selon stade croissance
        growth_stage = progression_data["growth_stage"]
        if growth_stage in self.company_modifiers:
            modifier = self.company_modifiers[growth_stage]
            opportunities_score *= modifier["progression_multiplier"]
            opportunity_factors.append(modifier["description"])
        
        return {
            "opportunities_score": min(1.0, opportunities_score),
            "timeline_data": timeline_data,
            "opportunity_factors": opportunity_factors,
            "limitations": limitations,
            "growth_context": {
                "stage": growth_stage,
                "modifier": self.company_modifiers.get(growth_stage, {})
            }
        }
    
    def _calculate_timeline_compatibility(
        self,
        progression_data: Dict[str, Any],
        company_opportunities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """⏱️ Calcul compatibilité timeline"""
        
        expectations = progression_data["salary_expectations"]
        timeline_data = company_opportunities["timeline_data"]
        company_avg_years = timeline_data["avg_years"]
        
        compatibility_scores = []
        timeline_matches = []
        
        for period, target_salary in expectations.items():
            candidate_years = self._extract_years_from_period(period)
            if candidate_years <= 0:
                continue
            
            # Calcul compatibilité timeline
            if candidate_years <= company_avg_years * 0.8:
                # Candidat plus rapide que l'entreprise
                timeline_score = 0.8
                match_type = "candidate_faster"
            elif candidate_years <= company_avg_years * 1.2:
                # Timeline compatible
                timeline_score = 1.0
                match_type = "compatible"
            elif candidate_years <= company_avg_years * 1.5:
                # Candidat plus patient
                timeline_score = 0.9
                match_type = "candidate_patient"
            else:
                # Timeline incompatible
                timeline_score = 0.6
                match_type = "incompatible"
            
            compatibility_scores.append(timeline_score)
            timeline_matches.append({
                "period": period,
                "candidate_years": candidate_years,
                "company_years": company_avg_years,
                "score": timeline_score,
                "match_type": match_type
            })
        
        # Score global timeline
        if compatibility_scores:
            average_timeline_score = sum(compatibility_scores) / len(compatibility_scores)
        else:
            average_timeline_score = 0.5
        
        return {
            "timeline_score": average_timeline_score,
            "timeline_matches": timeline_matches,
            "company_timeline": f"{timeline_data['min_years']}-{timeline_data['max_years']} ans",
            "compatibility_summary": self._generate_timeline_summary(timeline_matches)
        }
    
    def _calculate_final_progression_score(
        self,
        realism_analysis: Dict[str, Any],
        company_opportunities: Dict[str, Any],
        timeline_compatibility: Dict[str, Any]
    ) -> float:
        """🧮 Calcul score final progression"""
        
        # Pondération des facteurs
        weights = {
            "realism": 0.4,          # 40% réalisme attentes
            "opportunities": 0.35,   # 35% opportunités entreprise
            "timeline": 0.25         # 25% compatibilité timeline
        }
        
        base_score = (
            realism_analysis["realism_score"] * weights["realism"] +
            company_opportunities["opportunities_score"] * weights["opportunities"] +
            timeline_compatibility["timeline_score"] * weights["timeline"]
        )
        
        # Bonus/malus finaux
        final_score = base_score
        
        # Bonus si excellente cohérence
        if (realism_analysis["compatibility_level"] == ProgressionCompatibilityLevel.EXCELLENT 
            and company_opportunities["opportunities_score"] >= 0.8):
            final_score = min(1.0, final_score * 1.1)
        
        # Malus si attentes irréalistes
        if realism_analysis["compatibility_level"] == ProgressionCompatibilityLevel.UNREALISTIC:
            final_score *= 0.7
        
        # Malus si peu d'opportunités
        if company_opportunities["opportunities_score"] < 0.4:
            final_score *= 0.85
        
        return min(1.0, max(0.0, final_score))
    
    def _parse_progression_timeline(self, timeline: str) -> Dict[str, Any]:
        """📅 Parse timeline progression entreprise"""
        
        timeline_lower = timeline.lower()
        
        # Recherche pattern
        for pattern, data in self.timeline_patterns.items():
            if re.search(pattern, timeline_lower):
                return data
        
        # Fallback extraction numérique
        numbers = re.findall(r'\d+', timeline)
        if len(numbers) >= 2:
            min_years = int(numbers[0])
            max_years = int(numbers[1])
            return {
                "min_years": min_years,
                "max_years": max_years,
                "avg_years": (min_years + max_years) / 2
            }
        elif len(numbers) == 1:
            years = int(numbers[0])
            return {
                "min_years": years,
                "max_years": years,
                "avg_years": years
            }
        
        # Défaut
        return {"min_years": 2, "max_years": 3, "avg_years": 2.5}
    
    def _extract_years_from_period(self, period: str) -> float:
        """📊 Extraction années depuis période candidat"""
        
        period_lower = period.lower()
        
        # Patterns communs
        if "1_an" in period_lower or "1an" in period_lower:
            return 1.0
        elif "2_ans" in period_lower or "2ans" in period_lower:
            return 2.0
        elif "3_ans" in period_lower or "3ans" in period_lower:
            return 3.0
        elif "5_ans" in period_lower or "5ans" in period_lower:
            return 5.0
        
        # Extraction numérique
        numbers = re.findall(r'\d+', period)
        if numbers:
            return float(numbers[0])
        
        return 0.0
    
    def _generate_timeline_summary(self, timeline_matches: List[Dict]) -> str:
        """📋 Génération résumé compatibilité timeline"""
        
        if not timeline_matches:
            return "Pas de données timeline"
        
        compatible_count = sum(1 for match in timeline_matches if match["score"] >= 0.9)
        total_count = len(timeline_matches)
        
        if compatible_count == total_count:
            return "Timeline parfaitement compatible"
        elif compatible_count >= total_count * 0.7:
            return "Timeline majoritairement compatible"
        elif compatible_count >= total_count * 0.3:
            return "Timeline partiellement compatible"
        else:
            return "Timeline peu compatible"
    
    def _enrich_progression_result(
        self,
        final_score: float,
        progression_data: Dict[str, Any],
        realism_analysis: Dict[str, Any],
        company_opportunities: Dict[str, Any],
        timeline_compatibility: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """🔧 Enrichissement résultat progression"""
        
        # Recommandations intelligentes
        recommendations = self._generate_progression_recommendations(
            final_score, realism_analysis, company_opportunities, timeline_compatibility
        )
        
        # Analyse détaillée
        detailed_analysis = self._generate_detailed_progression_analysis(
            progression_data, realism_analysis, company_opportunities
        )
        
        return {
            "final_score": final_score,
            "compatibility_level": realism_analysis["compatibility_level"].value,
            "progression_analysis": {
                "candidate_expectations": progression_data["salary_expectations"],
                "current_salary": progression_data["current_salary"],
                "experience_level": progression_data["experience_level"].value,
                "career_motivation": progression_data["career_motivation"],
                "company_timeline": company_opportunities["timeline_data"],
                "realism_score": realism_analysis["realism_score"],
                "opportunities_score": company_opportunities["opportunities_score"]
            },
            "realism_factors": realism_analysis["realism_factors"],
            "concerns": realism_analysis["concerns"],
            "opportunity_factors": company_opportunities["opportunity_factors"],
            "limitations": company_opportunities["limitations"],
            "timeline_compatibility": timeline_compatibility,
            "detailed_analysis": detailed_analysis,
            "recommendations": recommendations,
            "calculated_at": datetime.now().isoformat(),
            "version": self.version,
            "scorer": self.name
        }
    
    def _generate_progression_recommendations(
        self,
        final_score: float,
        realism_analysis: Dict[str, Any],
        company_opportunities: Dict[str, Any],
        timeline_compatibility: Dict[str, Any]
    ) -> List[str]:
        """💡 Génération recommandations progression"""
        
        recommendations = []
        
        # Recommandations globales
        if realism_analysis["compatibility_level"] == ProgressionCompatibilityLevel.EXCELLENT:
            recommendations.append("🌟 Attentes salariales excellentes - Parfaitement réalistes")
        elif realism_analysis["compatibility_level"] == ProgressionCompatibilityLevel.GOOD:
            recommendations.append("✅ Attentes salariales bonnes - Bien calibrées")
        elif realism_analysis["compatibility_level"] == ProgressionCompatibilityLevel.REALISTIC:
            recommendations.append("👍 Attentes salariales réalistes - Négociables")
        elif realism_analysis["compatibility_level"] == ProgressionCompatibilityLevel.OPTIMISTIC:
            recommendations.append("⚠️ Attentes optimistes - À tempérer")
        else:
            recommendations.append("❌ Attentes irréalistes - Revoir les expectations")
        
        # Recommandations opportunités
        if company_opportunities["opportunities_score"] >= 0.8:
            recommendations.append("🚀 Excellentes opportunités progression entreprise")
        elif company_opportunities["opportunities_score"] >= 0.6:
            recommendations.append("📈 Bonnes opportunités progression disponibles")
        else:
            recommendations.append("⚠️ Opportunités progression limitées - Clarifier plan carrière")
        
        # Recommandations timeline
        timeline_score = timeline_compatibility["timeline_score"]
        if timeline_score >= 0.9:
            recommendations.append("⏱️ Timeline progression parfaitement alignée")
        elif timeline_score >= 0.7:
            recommendations.append("📅 Timeline progression compatible")
        else:
            recommendations.append("⏰ Timeline progression à ajuster - Négocier délais")
        
        # Recommandations spécifiques
        if len(company_opportunities["limitations"]) > 2:
            recommendations.append("💡 Mettre en avant les opportunités existantes")
        
        if len(realism_analysis["concerns"]) > 0:
            recommendations.append("🔍 Expliquer la progression salariale réaliste")
        
        return recommendations
    
    def _generate_detailed_progression_analysis(
        self,
        progression_data: Dict[str, Any],
        realism_analysis: Dict[str, Any],
        company_opportunities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """📊 Analyse détaillée progression"""
        
        return {
            "candidate_profile": {
                "experience_level": progression_data["experience_level"].value,
                "career_motivation": progression_data["career_motivation"],
                "expectations_count": len(progression_data["salary_expectations"]),
                "has_realistic_expectations": realism_analysis["realism_score"] >= 0.6
            },
            "company_profile": {
                "growth_stage": progression_data["growth_stage"],
                "has_development_budget": progression_data["has_development_budget"],
                "has_evolution_path": progression_data["has_evolution_path"],
                "has_variable_compensation": progression_data["has_variable_compensation"],
                "progression_timeline": progression_data["progression_timeline"]
            },
            "market_context": realism_analysis["market_standards"],
            "growth_context": company_opportunities["growth_context"],
            "risk_assessment": {
                "candidate_risk": "high" if realism_analysis["compatibility_level"] == ProgressionCompatibilityLevel.UNREALISTIC else "low",
                "company_risk": "high" if company_opportunities["opportunities_score"] < 0.4 else "low"
            }
        }
    
    def _create_fallback_score(self, reason: str) -> Dict[str, Any]:
        """🚨 Score fallback en cas d'erreur"""
        
        logger.warning(f"Fallback SalaryProgressionScorer: {reason}")
        
        return {
            "final_score": 0.5,  # Score neutre
            "compatibility_level": ProgressionCompatibilityLevel.REALISTIC.value,
            "progression_analysis": {
                "candidate_expectations": {},
                "current_salary": 0,
                "experience_level": "confirme",
                "career_motivation": 0,
                "company_timeline": {},
                "realism_score": 0.5,
                "opportunities_score": 0.5
            },
            "realism_factors": [],
            "concerns": [f"Mode dégradé: {reason}"],
            "opportunity_factors": [],
            "limitations": [],
            "timeline_compatibility": {
                "timeline_score": 0.5,
                "compatibility_summary": "Données insuffisantes"
            },
            "detailed_analysis": {},
            "recommendations": [
                f"⚠️ {reason}",
                "🛠️ Vérifier manuellement les attentes progression"
            ],
            "calculated_at": datetime.now().isoformat(),
            "version": f"{self.version}-fallback",
            "scorer": self.name,
            "error": reason
        }
    
    def _update_stats(self, processing_time: float, compatibility_level: ProgressionCompatibilityLevel):
        """📊 Mise à jour statistiques"""
        
        # Moyenne temps de traitement
        total = self.stats["calculations"]
        current_avg = self.stats["average_processing_time"]
        self.stats["average_processing_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        # Distribution compatibilité
        self.stats["compatibility_distribution"][compatibility_level.value] += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """📈 Statistiques performance"""
        
        compatibility_rates = {}
        if self.stats["calculations"] > 0:
            for level, count in self.stats["compatibility_distribution"].items():
                compatibility_rates[level] = count / self.stats["calculations"]
        
        return {
            "scorer_stats": self.stats.copy(),
            "performance_metrics": {
                "average_processing_time_ms": self.stats["average_processing_time"],
                "target_achieved": self.stats["average_processing_time"] < 5.0,
                "compatibility_rates": compatibility_rates
            },
            "market_standards": {
                "levels_covered": len(self.market_progression_standards),
                "company_modifiers": len(self.company_modifiers)
            }
        }
    
    def get_market_standards_preview(self, experience_level: NiveauExperience) -> Dict[str, Any]:
        """📊 Aperçu standards marché"""
        
        if experience_level in self.market_progression_standards:
            standards = self.market_progression_standards[experience_level]
            return {
                "experience_level": experience_level.value,
                "annual_increase_range": f"{standards['annual_increase_range'][0]:.1%}-{standards['annual_increase_range'][1]:.1%}",
                "3_year_total_increase": f"{standards['3_year_total_increase'][0]:.1%}-{standards['3_year_total_increase'][1]:.1%}",
                "realistic_ceiling": f"{(standards['realistic_ceiling'] - 1):.1%}",
                "typical_timeline": standards["typical_timeline"],
                "progression_speed": standards["progression_speed"]
            }
        else:
            return {
                "experience_level": experience_level.value,
                "message": f"Pas de standards définis pour {experience_level.value}"
            }
