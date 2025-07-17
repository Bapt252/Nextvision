"""
🎯 Nextvision V3.0 - MotivationsScorer (8% Weight)
==================================================

Score la correspondance aspirations candidat vs opportunités entreprise
- Analyse ranking motivations candidat (questionnaire étape 3)
- Correspondance avec opportunités offertes par l'entreprise  
- Boost automatique via pondération adaptative (MANQUE_PERSPECTIVES)
- Performance optimisée <15ms (8% du budget 175ms)

Author: NEXTEN Team
Version: 3.0.0 - Motivations Intelligence
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

from nextvision.models.extended_bidirectional_models_v3 import (
    ExtendedCandidateProfileV3,
    ExtendedCompanyProfileV3,
    MotivationType,
    WorkModalityType,
    CandidateStatusType
)

logger = logging.getLogger(__name__)

class MotivationAlignment(str, Enum):
    """Niveaux d'alignement motivation"""
    EXCELLENT = "excellent"
    GOOD = "good" 
    AVERAGE = "average"
    POOR = "poor"
    MISSING = "missing"

@dataclass
class MotivationMatch:
    """Correspondance d'une motivation avec les opportunités entreprise"""
    motivation: MotivationType
    candidate_score: int  # 1-5 du questionnaire
    ranking_position: int  # Position dans le ranking
    weight_factor: float  # Poids selon position
    
    # Analyse entreprise
    enterprise_score: float  # 0-1 score opportunités
    alignment_level: MotivationAlignment
    matching_factors: List[str]
    missing_opportunities: List[str]
    
    # Score final pondéré
    final_score: float

class MotivationsScorer:
    """
    🎯 Motivations Scorer V3.0 - Correspondance Aspirations
    
    Évalue la correspondance motivations candidat vs opportunités entreprise :
    - Analyse ranking motivations questionnaire V3.0
    - Correspondance intelligente avec profil entreprise
    - Pondération adaptative automatique
    - Performance optimisée <15ms
    """
    
    def __init__(self):
        self.name = "MotivationsScorer"
        self.version = "3.0.0"
        
        # Configuration scoring
        self.scoring_config = {
            "ranking_weights": {
                1: 0.40,  # 1ère motivation = 40%
                2: 0.30,  # 2ème motivation = 30% 
                3: 0.20,  # 3ème motivation = 20%
                4: 0.10   # 4ème motivation = 10%
            },
            "alignment_thresholds": {
                "excellent": 0.8,
                "good": 0.6,
                "average": 0.4,
                "poor": 0.2
            }
        }
        
        # Mapping motivations → opportunités entreprise (optimisé performance)
        self.motivation_indicators = {
            MotivationType.CHALLENGE_TECHNIQUE: {
                "keywords": ["technique", "technologie", "innovation", "développement", "architecture"],
                "enterprise_signals": ["startup", "tech", "R&D", "innovation"],
                "weight_multiplier": 1.2
            },
            MotivationType.EVOLUTION_CARRIERE: {
                "keywords": ["évolution", "carrière", "promotion", "management", "responsabilités"],
                "enterprise_signals": ["croissance", "promotion", "scale-up", "opportunities"],
                "weight_multiplier": 1.3
            },
            MotivationType.AUTONOMIE: {
                "keywords": ["autonomie", "indépendant", "liberté", "remote", "flexible"],
                "enterprise_signals": ["remote", "autonomie", "ownership", "flexible"],
                "weight_multiplier": 1.1
            },
            MotivationType.IMPACT_BUSINESS: {
                "keywords": ["impact", "business", "résultats", "croissance", "performance"],
                "enterprise_signals": ["scale-up", "impact", "growth", "business"],
                "weight_multiplier": 1.2
            },
            MotivationType.APPRENTISSAGE: {
                "keywords": ["apprentissage", "formation", "compétences", "learning"],
                "enterprise_signals": ["formation", "learning", "technologies", "training"],
                "weight_multiplier": 1.0
            },
            MotivationType.LEADERSHIP: {
                "keywords": ["leadership", "équipe", "management", "encadrement"],
                "enterprise_signals": ["management", "équipe", "leadership", "team"],
                "weight_multiplier": 1.2
            },
            MotivationType.INNOVATION: {
                "keywords": ["innovation", "créativité", "nouveauté", "disruptif"],
                "enterprise_signals": ["innovation", "startup", "créativité", "R&D"],
                "weight_multiplier": 1.1
            },
            MotivationType.EQUILIBRE_VIE: {
                "keywords": ["équilibre", "vie privée", "télétravail", "horaires"],
                "enterprise_signals": ["work-life", "télétravail", "flexibilité", "remote"],
                "weight_multiplier": 1.0
            }
        }
        
        # Cache pour performance
        self._enterprise_analysis_cache = {}
        
        # Métriques
        self.stats = {
            "calculations": 0,
            "cache_hits": 0,
            "average_processing_time": 0.0
        }
    
    def calculate_motivations_score(
        self,
        candidate: ExtendedCandidateProfileV3,
        company: ExtendedCompanyProfileV3,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        🎯 Calcule score correspondance motivations candidat vs entreprise
        
        Target: <15ms (8% du budget 175ms)
        """
        start_time = datetime.now()
        self.stats["calculations"] += 1
        
        try:
            # 1. Extraction rapide motivations candidat
            candidate_motivations = self._extract_candidate_motivations(candidate)
            
            if not candidate_motivations:
                return self._create_fallback_score("Pas de motivations candidat détectées")
            
            # 2. Analyse entreprise (avec cache)
            enterprise_opportunities = self._analyze_enterprise_opportunities(company)
            
            # 3. Calcul correspondances motivations
            motivation_matches = self._calculate_motivation_matches(
                candidate_motivations, enterprise_opportunities
            )
            
            # 4. Score global pondéré
            final_score = self._calculate_weighted_score(motivation_matches)
            
            # 5. Enrichissement résultat
            result = self._enrich_motivations_result(
                final_score, motivation_matches, candidate_motivations, 
                enterprise_opportunities, context
            )
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            result["processing_time_ms"] = processing_time
            
            # Mise à jour statistiques
            self._update_stats(processing_time)
            
            logger.info(
                f"🎯 MotivationsScorer: {final_score:.3f} "
                f"({len(motivation_matches)} matches, {processing_time:.1f}ms)"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur MotivationsScorer: {e}")
            return self._create_fallback_score(f"Erreur: {str(e)}")
    
    def _extract_candidate_motivations(self, candidate: ExtendedCandidateProfileV3) -> Dict[MotivationType, int]:
        """📊 Extraction rapide motivations candidat"""
        
        # Données V3.0 prioritaires
        if candidate.motivations_ranking.motivations_ranking:
            return candidate.motivations_ranking.motivations_ranking
        
        # Fallback V2.0 si disponible
        motivations = {}
        
        # Déduction depuis raison d'écoute
        listening_reasons = candidate.availability_timing.listening_reasons
        for reason in listening_reasons:
            if "perspective" in str(reason).lower():
                motivations[MotivationType.EVOLUTION_CARRIERE] = 4
            elif "inadequat" in str(reason).lower():
                motivations[MotivationType.CHALLENGE_TECHNIQUE] = 4
            elif "flexibilite" in str(reason).lower():
                motivations[MotivationType.EQUILIBRE_VIE] = 4
            elif "remuneration" in str(reason).lower():
                motivations[MotivationType.EVOLUTION_CARRIERE] = 3
        
        # Motivations par défaut si rien détecté
        if not motivations:
            motivations = {
                MotivationType.EVOLUTION_CARRIERE: 4,
                MotivationType.CHALLENGE_TECHNIQUE: 3
            }
        
        return motivations
    
    def _analyze_enterprise_opportunities(self, company: ExtendedCompanyProfileV3) -> Dict[str, float]:
        """🏢 Analyse opportunités entreprise (avec cache)"""
        
        # Cache basé sur hash du profil entreprise
        cache_key = f"{company.base_profile.entreprise.nom}_{company.base_profile.poste.titre}"
        
        if cache_key in self._enterprise_analysis_cache:
            self.stats["cache_hits"] += 1
            return self._enterprise_analysis_cache[cache_key]
        
        opportunities = {}
        
        # Analyse description poste
        job_description = company.base_profile.poste.description or ""
        job_text = job_description.lower()
        
        # Analyse description entreprise
        company_description = company.base_profile.entreprise.description or ""
        company_text = company_description.lower()
        
        # Analyse avantages
        benefits_text = " ".join(company.job_benefits.job_benefits).lower()
        
        # Texte complet pour analyse
        full_text = f"{job_text} {company_text} {benefits_text}"
        
        # Scoring par motivation
        for motivation, config in self.motivation_indicators.items():
            score = 0.0
            
            # Analyse mots-clés
            keyword_matches = sum(1 for keyword in config["keywords"] if keyword in full_text)
            score += min(0.4, keyword_matches * 0.1)
            
            # Analyse signaux entreprise
            signal_matches = sum(1 for signal in config["enterprise_signals"] if signal in full_text)
            score += min(0.3, signal_matches * 0.15)
            
            # Bonus spécifiques
            if motivation == MotivationType.EQUILIBRE_VIE:
                if company.job_benefits.remote_policy in [WorkModalityType.HYBRID, WorkModalityType.FULL_REMOTE]:
                    score += 0.3
            
            elif motivation == MotivationType.EVOLUTION_CARRIERE:
                if company.company_profile_v3.company_size.value in ["startup", "pme"]:
                    score += 0.2  # Plus d'opportunités dans petites structures
            
            elif motivation == MotivationType.AUTONOMIE:
                if company.job_benefits.remote_policy != WorkModalityType.ON_SITE:
                    score += 0.2
            
            # Application multiplicateur
            score *= config["weight_multiplier"]
            opportunities[motivation.value] = min(1.0, score)
        
        # Mise en cache
        self._enterprise_analysis_cache[cache_key] = opportunities
        
        return opportunities
    
    def _calculate_motivation_matches(
        self, 
        candidate_motivations: Dict[MotivationType, int],
        enterprise_opportunities: Dict[str, float]
    ) -> List[MotivationMatch]:
        """⚖️ Calcul correspondances motivation par motivation"""
        
        matches = []
        
        # Tri par score candidat (ranking implicite)
        sorted_motivations = sorted(
            candidate_motivations.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        for position, (motivation, candidate_score) in enumerate(sorted_motivations, 1):
            # Score opportunités entreprise
            enterprise_score = enterprise_opportunities.get(motivation.value, 0.0)
            
            # Détermination alignement
            alignment_level = self._determine_alignment_level(enterprise_score)
            
            # Facteurs positifs/négatifs
            matching_factors, missing_opportunities = self._analyze_motivation_factors(
                motivation, enterprise_score, candidate_score
            )
            
            # Poids selon position ranking
            weight_factor = self.scoring_config["ranking_weights"].get(position, 0.05)
            
            # Score final pondéré pour cette motivation
            final_score = enterprise_score * (candidate_score / 5.0) * weight_factor
            
            match = MotivationMatch(
                motivation=motivation,
                candidate_score=candidate_score,
                ranking_position=position,
                weight_factor=weight_factor,
                enterprise_score=enterprise_score,
                alignment_level=alignment_level,
                matching_factors=matching_factors,
                missing_opportunities=missing_opportunities,
                final_score=final_score
            )
            
            matches.append(match)
        
        return matches
    
    def _determine_alignment_level(self, enterprise_score: float) -> MotivationAlignment:
        """📊 Détermine niveau d'alignement selon score"""
        
        thresholds = self.scoring_config["alignment_thresholds"]
        
        if enterprise_score >= thresholds["excellent"]:
            return MotivationAlignment.EXCELLENT
        elif enterprise_score >= thresholds["good"]:
            return MotivationAlignment.GOOD
        elif enterprise_score >= thresholds["average"]:
            return MotivationAlignment.AVERAGE
        elif enterprise_score >= thresholds["poor"]:
            return MotivationAlignment.POOR
        else:
            return MotivationAlignment.MISSING
    
    def _analyze_motivation_factors(
        self, 
        motivation: MotivationType, 
        enterprise_score: float, 
        candidate_score: int
    ) -> Tuple[List[str], List[str]]:
        """🔍 Analyse facteurs positifs/négatifs pour une motivation"""
        
        matching_factors = []
        missing_opportunities = []
        
        config = self.motivation_indicators[motivation]
        
        if enterprise_score >= 0.6:
            matching_factors.append(f"Bonne correspondance {motivation.value}")
            if enterprise_score >= 0.8:
                matching_factors.append("Opportunités excellentes détectées")
        
        if enterprise_score < 0.3:
            missing_opportunities.append(f"Faible couverture {motivation.value}")
            if candidate_score >= 4:
                missing_opportunities.append("Motivation importante mal couverte")
        
        # Facteurs spécifiques par motivation
        if motivation == MotivationType.EVOLUTION_CARRIERE:
            if enterprise_score >= 0.5:
                matching_factors.append("Perspectives évolution identifiées")
            else:
                missing_opportunities.append("Plan carrière à clarifier")
        
        elif motivation == MotivationType.EQUILIBRE_VIE:
            if enterprise_score >= 0.5:
                matching_factors.append("Flexibilité travail disponible")
            else:
                missing_opportunities.append("Flexibilité limitée")
        
        return matching_factors, missing_opportunities
    
    def _calculate_weighted_score(self, motivation_matches: List[MotivationMatch]) -> float:
        """🧮 Calcul score global pondéré"""
        
        if not motivation_matches:
            return 0.0
        
        # Somme des scores pondérés
        total_weighted_score = sum(match.final_score for match in motivation_matches)
        
        # Bonus alignement motivation principale
        if motivation_matches:
            top_motivation = motivation_matches[0]
            if top_motivation.alignment_level in [MotivationAlignment.EXCELLENT, MotivationAlignment.GOOD]:
                total_weighted_score *= 1.1
        
        # Pénalité si motivation principale mal couverte
        if motivation_matches and motivation_matches[0].alignment_level == MotivationAlignment.MISSING:
            total_weighted_score *= 0.7
        
        return min(1.0, total_weighted_score)
    
    def _enrich_motivations_result(
        self,
        final_score: float,
        motivation_matches: List[MotivationMatch], 
        candidate_motivations: Dict[MotivationType, int],
        enterprise_opportunities: Dict[str, float],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """🔧 Enrichissement résultat motivations"""
        
        # Classification score
        if final_score >= 0.8:
            compatibility_level = "excellent"
        elif final_score >= 0.6:
            compatibility_level = "good"
        elif final_score >= 0.4:
            compatibility_level = "average"
        elif final_score >= 0.2:
            compatibility_level = "poor"
        else:
            compatibility_level = "incompatible"
        
        # Analyse détaillée
        top_matches = [m for m in motivation_matches if m.alignment_level in [MotivationAlignment.EXCELLENT, MotivationAlignment.GOOD]]
        poor_matches = [m for m in motivation_matches if m.alignment_level in [MotivationAlignment.POOR, MotivationAlignment.MISSING]]
        
        # Recommandations
        recommendations = self._generate_recommendations(final_score, motivation_matches, compatibility_level)
        
        return {
            "final_score": final_score,
            "compatibility_level": compatibility_level,
            "motivation_analysis": {
                "total_motivations": len(candidate_motivations),
                "strong_alignments": len(top_matches),
                "weak_alignments": len(poor_matches),
                "top_motivation_satisfied": motivation_matches[0].alignment_level != MotivationAlignment.MISSING if motivation_matches else False
            },
            "detailed_matches": [
                {
                    "motivation": match.motivation.value,
                    "candidate_score": match.candidate_score,
                    "ranking_position": match.ranking_position,
                    "enterprise_score": match.enterprise_score,
                    "alignment_level": match.alignment_level.value,
                    "weight_factor": match.weight_factor,
                    "final_score": match.final_score,
                    "matching_factors": match.matching_factors,
                    "missing_opportunities": match.missing_opportunities
                }
                for match in motivation_matches
            ],
            "recommendations": recommendations,
            "insights": {
                "strongest_motivation": motivation_matches[0].motivation.value if motivation_matches else None,
                "best_enterprise_opportunity": max(enterprise_opportunities.items(), key=lambda x: x[1])[0] if enterprise_opportunities else None,
                "alignment_score": sum(m.enterprise_score for m in motivation_matches) / len(motivation_matches) if motivation_matches else 0,
                "coverage_rate": len(top_matches) / len(motivation_matches) if motivation_matches else 0
            },
            "calculated_at": datetime.now().isoformat(),
            "version": self.version,
            "scorer": self.name
        }
    
    def _generate_recommendations(
        self, 
        final_score: float, 
        motivation_matches: List[MotivationMatch],
        compatibility_level: str
    ) -> List[str]:
        """💡 Génération recommandations intelligentes"""
        
        recommendations = []
        
        # Recommandations globales
        if compatibility_level == "excellent":
            recommendations.append("🌟 Excellente correspondance motivations - Candidat très aligné")
        elif compatibility_level == "good":
            recommendations.append("✅ Bonne correspondance motivations - Quelques ajustements possibles")
        elif compatibility_level == "average":
            recommendations.append("⚠️ Correspondance modérée - Vérifier points critiques")
        else:
            recommendations.append("❌ Correspondance faible - Risque d'inadéquation motivationnelle")
        
        # Recommandations spécifiques
        if motivation_matches:
            top_motivation = motivation_matches[0]
            
            if top_motivation.alignment_level == MotivationAlignment.EXCELLENT:
                recommendations.append(f"🎯 Mettre en avant: {top_motivation.motivation.value} parfaitement couvert")
            elif top_motivation.alignment_level == MotivationAlignment.MISSING:
                recommendations.append(f"🚨 Attention: {top_motivation.motivation.value} (priorité #1) non couverte")
        
        # Points d'attention
        poor_matches = [m for m in motivation_matches if m.candidate_score >= 4 and m.enterprise_score < 0.3]
        if poor_matches:
            recommendations.append(f"⚠️ Creuser en entretien: {', '.join([m.motivation.value for m in poor_matches[:2]])}")
        
        return recommendations
    
    def _create_fallback_score(self, reason: str) -> Dict[str, Any]:
        """🚨 Score fallback en cas d'erreur"""
        
        logger.warning(f"Fallback MotivationsScorer: {reason}")
        
        return {
            "final_score": 0.5,  # Score neutre
            "compatibility_level": "average",
            "motivation_analysis": {
                "total_motivations": 0,
                "strong_alignments": 0, 
                "weak_alignments": 0,
                "top_motivation_satisfied": False
            },
            "detailed_matches": [],
            "recommendations": [
                f"⚠️ Mode dégradé: {reason}",
                "🛠️ Vérifier manuellement les motivations candidat"
            ],
            "insights": {
                "coverage_rate": 0.5
            },
            "calculated_at": datetime.now().isoformat(),
            "version": f"{self.version}-fallback",
            "scorer": self.name,
            "error": reason
        }
    
    def _update_stats(self, processing_time: float):
        """📊 Mise à jour statistiques performance"""
        
        total = self.stats["calculations"]
        current_avg = self.stats["average_processing_time"]
        
        self.stats["average_processing_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """📈 Statistiques performance"""
        
        cache_hit_rate = 0.0
        if self.stats["calculations"] > 0:
            cache_hit_rate = self.stats["cache_hits"] / self.stats["calculations"]
        
        return {
            "scorer_stats": self.stats.copy(),
            "performance_metrics": {
                "average_processing_time_ms": self.stats["average_processing_time"],
                "cache_hit_rate": cache_hit_rate,
                "target_achieved": self.stats["average_processing_time"] < 15.0
            },
            "cache_size": len(self._enterprise_analysis_cache)
        }
    
    def clear_cache(self):
        """🧹 Nettoyage cache"""
        self._enterprise_analysis_cache.clear()
