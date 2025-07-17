"""
💰 Nextvision V3.0 - SalaryProgressionScorer (3% Weight)
========================================================

Score la compatibilité évolution salariale candidat vs opportunités entreprise
- Analyse salary_progression_expectations candidat vs career_progression_timeline
- Validation réalisme attentes selon niveau d'expérience
- Evaluation opportunités concrètes (position_evolution_path, budget formation)
- Cohérence avec motivations évolution carrière
- Performance ultra-optimisée <5ms (3% du budget 175ms)

Author: NEXTEN Team
Version: 3.0.0 - Salary Progression Intelligence
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import re

from nextvision.models.extended_bidirectional_models_v3 import (
    ExtendedCandidateProfileV3,
    ExtendedCompanyProfileV3,
    NiveauExperience,
    MotivationType
)

logger = logging.getLogger(__name__)

class ProgressionRealism(str, Enum):
    """Niveaux de réalisme progression"""
    REALISTIC = "realistic"
    OPTIMISTIC = "optimistic"
    AGGRESSIVE = "aggressive"
    UNREALISTIC = "unrealistic"

class TimelineCompatibility(str, Enum):
    """Niveaux compatibilité timeline"""
    PERFECT = "perfect"
    ALIGNED = "aligned"
    ACCEPTABLE = "acceptable"
    MISALIGNED = "misaligned"
    INCOMPATIBLE = "incompatible"

class SalaryProgressionScorer:
    """
    💰 Salary Progression Scorer V3.0 - Intelligence Évolution Salariale
    
    Évalue la compatibilité évolution salariale avec logique métier :
    - Compatibilité timeline progression candidat vs entreprise
    - Validation réalisme attentes selon niveau d'expérience
    - Évaluation opportunités concrètes d'évolution
    - Cohérence avec motivations évolution carrière
    - Performance ultra-optimisée <5ms
    """
    
    def __init__(self):
        self.name = "SalaryProgressionScorer"
        self.version = "3.0.0"
        
        # Grilles salariales de référence par niveau (données marché)
        self.salary_benchmarks = {
            NiveauExperience.JUNIOR: {
                "base_range": (30000, 45000),
                "progression_1_year": 1.15,  # +15% après 1 an
                "progression_3_years": 1.40,  # +40% après 3 ans
                "max_realistic": 55000
            },
            NiveauExperience.CONFIRME: {
                "base_range": (45000, 65000),
                "progression_1_year": 1.10,  # +10% après 1 an
                "progression_3_years": 1.25,  # +25% après 3 ans
                "max_realistic": 80000
            },
            NiveauExperience.SENIOR: {
                "base_range": (65000, 90000),
                "progression_1_year": 1.08,  # +8% après 1 an
                "progression_3_years": 1.20,  # +20% après 3 ans
                "max_realistic": 120000
            },
            NiveauExperience.EXPERT: {
                "base_range": (90000, 150000),
                "progression_1_year": 1.05,  # +5% après 1 an
                "progression_3_years": 1.15,  # +15% après 3 ans
                "max_realistic": 200000
            }
        }
        
        # Parsing timeline entreprise
        self.timeline_patterns = {
            "immediat": 0,
            "6mois": 0.5,
            "1an": 1,
            "1-2ans": 1.5,
            "2ans": 2,
            "2-3ans": 2.5,
            "3ans": 3,
            "3-5ans": 4,
            "5ans": 5,
            "long terme": 6
        }
        
        # Métriques
        self.stats = {
            "calculations": 0,
            "average_processing_time": 0.0,
            "realism_distribution": {level.value: 0 for level in ProgressionRealism},
            "timeline_distribution": {level.value: 0 for level in TimelineCompatibility}
        }
    
    def calculate_salary_progression_score(
        self,
        candidate: ExtendedCandidateProfileV3,
        company: ExtendedCompanyProfileV3,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        💰 Calcule score compatibilité évolution salariale
        
        Target: <5ms (3% du budget 175ms)
        """
        start_time = datetime.now()
        self.stats["calculations"] += 1
        
        try:
            # 1. Extraction rapide données progression
            progression_data = self._extract_progression_data(candidate, company)
            
            if not progression_data["has_expectations"]:
                return self._create_fallback_score("Pas d'attentes progression salariale")
            
            # 2. Analyse réalisme attentes candidat
            realism_analysis = self._analyze_expectations_realism(progression_data)
            
            # 3. Analyse compatibilité timeline
            timeline_analysis = self._analyze_timeline_compatibility(progression_data)
            
            # 4. Evaluation opportunités entreprise
            opportunities_analysis = self._evaluate_company_opportunities(progression_data)
            
            # 5. Score final pondéré
            final_score = self._calculate_weighted_progression_score(
                realism_analysis, timeline_analysis, opportunities_analysis
            )
            
            # 6. Enrichissement résultat
            result = self._enrich_progression_result(
                final_score, realism_analysis, timeline_analysis, 
                opportunities_analysis, progression_data, context
            )
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            result["processing_time_ms"] = processing_time
            
            # Mise à jour stats
            self._update_stats(processing_time, realism_analysis["realism_level"], 
                             timeline_analysis["timeline_compatibility"])
            
            logger.info(
                f"💰 SalaryProgressionScorer: {final_score:.3f} "
                f"({realism_analysis['realism_level']}/{timeline_analysis['timeline_compatibility']}, "
                f"{processing_time:.1f}ms)"
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
        progression_expectations = candidate.salary_progression_expectations
        current_salary = candidate.base_profile.attentes.salaire_souhaite or 0
        experience_level = candidate.base_profile.experience.niveau
        
        # Motivations évolution carrière
        evolution_motivation_score = 0
        if candidate.motivations_ranking.motivations_ranking:
            evolution_motivation_score = candidate.motivations_ranking.motivations_ranking.get(
                MotivationType.EVOLUTION_CARRIERE, 0
            )
        
        # Données entreprise
        career_timeline = company.job_benefits.career_progression_timeline
        evolution_path = company.position_evolution_path
        development_budget = company.job_benefits.professional_development_budget
        bonus_structure = company.job_benefits.bonus_structure
        
        return {
            "has_expectations": bool(progression_expectations),
            "progression_expectations": progression_expectations,
            "current_salary": current_salary,
            "experience_level": experience_level,
            "evolution_motivation_score": evolution_motivation_score,
            "career_timeline": career_timeline,
            "evolution_path": evolution_path,
            "development_budget": development_budget,
            "bonus_structure": bonus_structure
        }
    
    def _analyze_expectations_realism(self, progression_data: Dict[str, Any]) -> Dict[str, Any]:
        """🎯 Analyse réalisme attentes candidat"""
        
        experience_level = progression_data["experience_level"]
        current_salary = progression_data["current_salary"]
        expectations = progression_data["progression_expectations"]
        
        if not expectations or experience_level not in self.salary_benchmarks:
            return {
                "realism_level": ProgressionRealism.REALISTIC,
                "realism_score": 0.5,
                "realism_factors": ["Données insuffisantes pour analyse réalisme"]
            }
        
        benchmark = self.salary_benchmarks[experience_level]
        realism_factors = []
        realism_score = 1.0
        
        # Analyse attentes 1 an
        if "1_an" in expectations:
            target_1_year = expectations["1_an"]
            expected_1_year = current_salary * benchmark["progression_1_year"]
            
            if target_1_year <= expected_1_year:
                realism_factors.append("Attentes 1 an réalistes")
            elif target_1_year <= expected_1_year * 1.1:
                realism_factors.append("Attentes 1 an légèrement optimistes")
                realism_score *= 0.9
            elif target_1_year <= expected_1_year * 1.2:
                realism_factors.append("Attentes 1 an ambitieuses")
                realism_score *= 0.7
            else:
                realism_factors.append("Attentes 1 an irréalistes")
                realism_score *= 0.5
        
        # Analyse attentes 3 ans
        if "3_ans" in expectations:
            target_3_years = expectations["3_ans"]
            expected_3_years = current_salary * benchmark["progression_3_years"]
            max_realistic = benchmark["max_realistic"]
            
            if target_3_years <= expected_3_years:
                realism_factors.append("Attentes 3 ans réalistes")
            elif target_3_years <= max_realistic:
                realism_factors.append("Attentes 3 ans ambitieuses mais possibles")
                realism_score *= 0.8
            else:
                realism_factors.append("Attentes 3 ans dépassent le marché")
                realism_score *= 0.6
        
        # Cohérence progression
        if "1_an" in expectations and "3_ans" in expectations:
            progression_rate = expectations["3_ans"] / expectations["1_an"]
            if 1.1 <= progression_rate <= 1.4:
                realism_factors.append("Progression cohérente entre 1 et 3 ans")
            else:
                realism_factors.append("Progression incohérente entre 1 et 3 ans")
                realism_score *= 0.85
        
        # Détermination niveau réalisme
        if realism_score >= 0.9:
            realism_level = ProgressionRealism.REALISTIC
        elif realism_score >= 0.7:
            realism_level = ProgressionRealism.OPTIMISTIC
        elif realism_score >= 0.5:
            realism_level = ProgressionRealism.AGGRESSIVE
        else:
            realism_level = ProgressionRealism.UNREALISTIC
        
        return {
            "realism_level": realism_level,
            "realism_score": realism_score,
            "realism_factors": realism_factors,
            "benchmark_analysis": {
                "experience_level": experience_level.value,
                "expected_1_year": current_salary * benchmark["progression_1_year"] if current_salary else 0,
                "expected_3_years": current_salary * benchmark["progression_3_years"] if current_salary else 0,
                "max_realistic": benchmark["max_realistic"]
            }
        }
    
    def _analyze_timeline_compatibility(self, progression_data: Dict[str, Any]) -> Dict[str, Any]:
        """⏰ Analyse compatibilité timeline progression"""
        
        career_timeline = progression_data["career_timeline"]
        expectations = progression_data["progression_expectations"]
        
        if not career_timeline:
            return {
                "timeline_compatibility": TimelineCompatibility.ACCEPTABLE,
                "compatibility_score": 0.5,
                "timeline_factors": ["Timeline entreprise non définie"]
            }
        
        # Parsing timeline entreprise
        company_timeline_years = self._parse_timeline(career_timeline)
        
        timeline_factors = []
        compatibility_score = 1.0
        
        # Analyse compatibilité avec attentes candidat
        if expectations:
            # Si candidat a des attentes 1 an et entreprise > 2 ans
            if "1_an" in expectations and company_timeline_years > 2:
                timeline_factors.append("Candidat attend évolution 1 an, entreprise propose > 2 ans")
                compatibility_score *= 0.6
            
            # Si candidat a des attentes 3 ans et entreprise < 1 an
            elif "3_ans" in expectations and company_timeline_years < 1:
                timeline_factors.append("Timeline entreprise plus rapide qu'attendu")
                compatibility_score *= 1.1  # Légèrement positif
            
            # Timeline alignée
            elif "1_an" in expectations and 1 <= company_timeline_years <= 2:
                timeline_factors.append("Timeline progression bien alignée")
            elif "3_ans" in expectations and 2 <= company_timeline_years <= 4:
                timeline_factors.append("Timeline progression bien alignée")
            else:
                timeline_factors.append("Timeline partiellement alignée")
                compatibility_score *= 0.8
        
        # Analyse qualité timeline entreprise
        if company_timeline_years <= 2:
            timeline_factors.append("Progression rapide offerte")
            compatibility_score *= 1.05
        elif company_timeline_years <= 3:
            timeline_factors.append("Progression standard")
        else:
            timeline_factors.append("Progression lente")
            compatibility_score *= 0.9
        
        # Détermination niveau compatibilité
        if compatibility_score >= 1.0:
            timeline_compatibility = TimelineCompatibility.PERFECT
        elif compatibility_score >= 0.8:
            timeline_compatibility = TimelineCompatibility.ALIGNED
        elif compatibility_score >= 0.6:
            timeline_compatibility = TimelineCompatibility.ACCEPTABLE
        elif compatibility_score >= 0.4:
            timeline_compatibility = TimelineCompatibility.MISALIGNED
        else:
            timeline_compatibility = TimelineCompatibility.INCOMPATIBLE
        
        return {
            "timeline_compatibility": timeline_compatibility,
            "compatibility_score": min(1.0, compatibility_score),
            "timeline_factors": timeline_factors,
            "company_timeline_years": company_timeline_years,
            "timeline_analysis": {
                "raw_timeline": career_timeline,
                "parsed_years": company_timeline_years
            }
        }
    
    def _parse_timeline(self, timeline: str) -> float:
        """🔍 Parsing timeline entreprise vers années"""
        
        timeline_lower = timeline.lower().strip()
        
        # Vérification patterns prédéfinis
        for pattern, years in self.timeline_patterns.items():
            if pattern in timeline_lower:
                return years
        
        # Extraction numérique avec regex
        # Exemples: "2-3 ans", "18 mois", "1.5 années"
        
        # Recherche années
        year_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:an|year)', timeline_lower)
        if year_match:
            return float(year_match.group(1))
        
        # Recherche mois
        month_match = re.search(r'(\d+)\s*mois', timeline_lower)
        if month_match:
            return float(month_match.group(1)) / 12
        
        # Recherche range (ex: "2-3")
        range_match = re.search(r'(\d+)-(\d+)', timeline_lower)
        if range_match:
            start, end = float(range_match.group(1)), float(range_match.group(2))
            return (start + end) / 2
        
        # Valeur par défaut
        return 2.5
    
    def _evaluate_company_opportunities(self, progression_data: Dict[str, Any]) -> Dict[str, Any]:
        """🚀 Évaluation opportunités entreprise"""
        
        evolution_path = progression_data["evolution_path"]
        development_budget = progression_data["development_budget"]
        bonus_structure = progression_data["bonus_structure"]
        
        opportunities_score = 0.5  # Base neutre
        opportunity_factors = []
        
        # Analyse chemin d'évolution
        if evolution_path:
            if len(evolution_path) >= 3:
                opportunities_score += 0.3
                opportunity_factors.append(f"Chemin évolution clair ({len(evolution_path)} niveaux)")
            elif len(evolution_path) >= 2:
                opportunities_score += 0.2
                opportunity_factors.append(f"Évolution possible ({len(evolution_path)} niveaux)")
            else:
                opportunities_score += 0.1
                opportunity_factors.append("Évolution limitée")
        else:
            opportunity_factors.append("Pas de chemin d'évolution défini")
        
        # Analyse budget développement
        if development_budget:
            if development_budget >= 3000:
                opportunities_score += 0.2
                opportunity_factors.append(f"Budget formation important ({development_budget}€)")
            elif development_budget >= 1000:
                opportunities_score += 0.1
                opportunity_factors.append(f"Budget formation correct ({development_budget}€)")
            else:
                opportunities_score += 0.05
                opportunity_factors.append(f"Budget formation limité ({development_budget}€)")
        else:
            opportunity_factors.append("Budget formation non précisé")
        
        # Analyse structure bonus
        if bonus_structure and bonus_structure != "None":
            if bonus_structure == "Variable":
                opportunities_score += 0.15
                opportunity_factors.append("Rémunération variable liée performance")
            elif bonus_structure == "Commission":
                opportunities_score += 0.1
                opportunity_factors.append("Rémunération commission possible")
            elif bonus_structure == "Fixed":
                opportunities_score += 0.05
                opportunity_factors.append("Bonus fixe prévu")
        
        return {
            "opportunities_score": min(1.0, opportunities_score),
            "opportunity_factors": opportunity_factors,
            "concrete_opportunities": {
                "evolution_levels": len(evolution_path) if evolution_path else 0,
                "development_budget": development_budget,
                "bonus_available": bonus_structure != "None" if bonus_structure else False
            }
        }
    
    def _calculate_weighted_progression_score(
        self,
        realism_analysis: Dict[str, Any],
        timeline_analysis: Dict[str, Any],
        opportunities_analysis: Dict[str, Any]
    ) -> float:
        """🧮 Calcul score progression pondéré"""
        
        # Pondération des composants
        weights = {
            "realism": 0.40,        # 40% - Réalisme attentes
            "timeline": 0.35,       # 35% - Compatibilité timeline
            "opportunities": 0.25   # 25% - Opportunités entreprise
        }
        
        final_score = (
            realism_analysis["realism_score"] * weights["realism"] +
            timeline_analysis["compatibility_score"] * weights["timeline"] +
            opportunities_analysis["opportunities_score"] * weights["opportunities"]
        )
        
        return min(1.0, final_score)
    
    def _enrich_progression_result(
        self,
        final_score: float,
        realism_analysis: Dict[str, Any],
        timeline_analysis: Dict[str, Any],
        opportunities_analysis: Dict[str, Any],
        progression_data: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """🔧 Enrichissement résultat progression"""
        
        # Recommandations intelligentes
        recommendations = self._generate_progression_recommendations(
            final_score, realism_analysis, timeline_analysis, 
            opportunities_analysis, progression_data
        )
        
        # Analyse détaillée
        detailed_analysis = self._generate_detailed_progression_analysis(
            realism_analysis, timeline_analysis, opportunities_analysis, progression_data
        )
        
        return {
            "final_score": final_score,
            "progression_analysis": {
                "realism_level": realism_analysis["realism_level"].value,
                "timeline_compatibility": timeline_analysis["timeline_compatibility"].value,
                "opportunities_score": opportunities_analysis["opportunities_score"],
                "evolution_motivation_score": progression_data["evolution_motivation_score"]
            },
            "score_breakdown": {
                "realism_score": realism_analysis["realism_score"],
                "timeline_score": timeline_analysis["compatibility_score"],
                "opportunities_score": opportunities_analysis["opportunities_score"],
                "weighted_final": final_score
            },
            "analysis_factors": {
                "realism_factors": realism_analysis["realism_factors"],
                "timeline_factors": timeline_analysis["timeline_factors"],
                "opportunity_factors": opportunities_analysis["opportunity_factors"]
            },
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
        timeline_analysis: Dict[str, Any],
        opportunities_analysis: Dict[str, Any],
        progression_data: Dict[str, Any]
    ) -> List[str]:
        """💡 Génération recommandations progression"""
        
        recommendations = []
        
        # Recommandations globales
        if final_score >= 0.8:
            recommendations.append("🌟 Excellente compatibilité évolution salariale")
        elif final_score >= 0.6:
            recommendations.append("✅ Bonne compatibilité progression - Négociation possible")
        elif final_score >= 0.4:
            recommendations.append("⚠️ Compatibilité modérée - Clarifier attentes")
        else:
            recommendations.append("❌ Faible compatibilité - Risque désaccord salarial")
        
        # Recommandations réalisme
        realism_level = realism_analysis["realism_level"]
        if realism_level == ProgressionRealism.UNREALISTIC:
            recommendations.append("🎯 Recadrer attentes candidat - Irréalistes pour son niveau")
        elif realism_level == ProgressionRealism.AGGRESSIVE:
            recommendations.append("📈 Attentes ambitieuses - Justifier par performance")
        elif realism_level == ProgressionRealism.REALISTIC:
            recommendations.append("✅ Attentes réalistes - Bon profil progression")
        
        # Recommandations timeline
        timeline_compat = timeline_analysis["timeline_compatibility"]
        if timeline_compat == TimelineCompatibility.INCOMPATIBLE:
            recommendations.append("⏰ Timeline incompatible - Revoir planning évolution")
        elif timeline_compat == TimelineCompatibility.PERFECT:
            recommendations.append("🎯 Timeline parfaitement alignée")
        
        # Recommandations opportunités
        if opportunities_analysis["opportunities_score"] < 0.4:
            recommendations.append("🚀 Améliorer offre évolution - Budget formation, chemin carrière")
        elif opportunities_analysis["opportunities_score"] > 0.8:
            recommendations.append("💼 Excellentes opportunités - Mettre en avant")
        
        # Recommandations selon motivation
        evolution_motivation = progression_data["evolution_motivation_score"]
        if evolution_motivation >= 4:
            recommendations.append("🎯 Évolution prioritaire - Candidat très motivé")
        elif evolution_motivation <= 2:
            recommendations.append("💡 Évolution secondaire - Autres motivations prioritaires")
        
        return recommendations
    
    def _generate_detailed_progression_analysis(
        self,
        realism_analysis: Dict[str, Any],
        timeline_analysis: Dict[str, Any],
        opportunities_analysis: Dict[str, Any],
        progression_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """📊 Analyse détaillée progression"""
        
        return {
            "candidate_profile": {
                "current_salary": progression_data["current_salary"],
                "experience_level": progression_data["experience_level"].value,
                "expectations": progression_data["progression_expectations"],
                "evolution_motivation": progression_data["evolution_motivation_score"],
                "realism_assessment": realism_analysis["realism_level"].value
            },
            "company_profile": {
                "career_timeline": progression_data["career_timeline"],
                "timeline_years": timeline_analysis.get("company_timeline_years", 0),
                "evolution_path": progression_data["evolution_path"],
                "development_budget": progression_data["development_budget"],
                "bonus_structure": progression_data["bonus_structure"]
            },
            "compatibility_analysis": {
                "timeline_match": timeline_analysis["timeline_compatibility"].value,
                "opportunities_level": "high" if opportunities_analysis["opportunities_score"] > 0.7 else 
                                     "medium" if opportunities_analysis["opportunities_score"] > 0.4 else "low",
                "overall_fit": "excellent" if final_score > 0.8 else
                              "good" if final_score > 0.6 else
                              "moderate" if final_score > 0.4 else "poor"
            },
            "market_benchmarks": realism_analysis.get("benchmark_analysis", {})
        }
    
    def _create_fallback_score(self, reason: str) -> Dict[str, Any]:
        """🚨 Score fallback en cas d'erreur"""
        
        logger.warning(f"Fallback SalaryProgressionScorer: {reason}")
        
        return {
            "final_score": 0.5,  # Score neutre
            "progression_analysis": {
                "realism_level": ProgressionRealism.REALISTIC.value,
                "timeline_compatibility": TimelineCompatibility.ACCEPTABLE.value,
                "opportunities_score": 0.5,
                "evolution_motivation_score": 0
            },
            "score_breakdown": {
                "realism_score": 0.5,
                "timeline_score": 0.5,
                "opportunities_score": 0.5,
                "weighted_final": 0.5
            },
            "analysis_factors": {
                "realism_factors": [f"Mode dégradé: {reason}"],
                "timeline_factors": [],
                "opportunity_factors": []
            },
            "detailed_analysis": {},
            "recommendations": [
                f"⚠️ {reason}",
                "🛠️ Vérifier manuellement la progression salariale"
            ],
            "calculated_at": datetime.now().isoformat(),
            "version": f"{self.version}-fallback",
            "scorer": self.name,
            "error": reason
        }
    
    def _update_stats(self, processing_time: float, realism_level: ProgressionRealism, 
                     timeline_compatibility: TimelineCompatibility):
        """📊 Mise à jour statistiques"""
        
        # Moyenne temps de traitement
        total = self.stats["calculations"]
        current_avg = self.stats["average_processing_time"]
        self.stats["average_processing_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        # Distribution réalisme et timeline
        self.stats["realism_distribution"][realism_level.value] += 1
        self.stats["timeline_distribution"][timeline_compatibility.value] += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """📈 Statistiques performance"""
        
        # Calcul taux distribution
        realism_rates = {}
        timeline_rates = {}
        
        if self.stats["calculations"] > 0:
            for level, count in self.stats["realism_distribution"].items():
                realism_rates[level] = count / self.stats["calculations"]
            for level, count in self.stats["timeline_distribution"].items():
                timeline_rates[level] = count / self.stats["calculations"]
        
        return {
            "scorer_stats": self.stats.copy(),
            "performance_metrics": {
                "average_processing_time_ms": self.stats["average_processing_time"],
                "target_achieved": self.stats["average_processing_time"] < 5.0,
                "realism_rates": realism_rates,
                "timeline_rates": timeline_rates
            },
            "benchmark_info": {
                "experience_levels": list(self.salary_benchmarks.keys()),
                "timeline_patterns": len(self.timeline_patterns)
            }
        }
    
    def get_salary_benchmark_preview(self, experience_level: NiveauExperience) -> Dict[str, Any]:
        """🔍 Aperçu benchmarks salariaux"""
        
        if experience_level in self.salary_benchmarks:
            benchmark = self.salary_benchmarks[experience_level]
            return {
                "experience_level": experience_level.value,
                "has_benchmark": True,
                "base_range": benchmark["base_range"],
                "progression_1_year": f"+{(benchmark['progression_1_year'] - 1) * 100:.0f}%",
                "progression_3_years": f"+{(benchmark['progression_3_years'] - 1) * 100:.0f}%",
                "max_realistic": benchmark["max_realistic"]
            }
        else:
            return {
                "experience_level": experience_level.value if experience_level else "unknown",
                "has_benchmark": False,
                "message": f"Pas de benchmark pour {experience_level.value if experience_level else 'ce niveau'}"
            }
