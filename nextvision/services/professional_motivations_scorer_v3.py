"""
Nextvision v3.0 - Professional Motivations Scorer
=================================================

Scorer pour les motivations professionnelles - Composant #5 V3.0 (8% poids)
- Analyse des 8 types de motivations candidat vs poste
- Score de compatibilité motivationnelle intelligent
- Intégration avec pondération adaptative
- Boost automatique selon raison d'écoute (perspectives/poste inadéquat)

Author: NEXTEN Development Team
Version: 3.0 - MOTIVATION INTELLIGENCE
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import statistics
from collections import defaultdict

# Import des modèles V3.0
from ..models.extended_matching_models_v3 import (
    ExtendedMatchingProfile,
    MotivationType,
    ProfessionalMotivationsProfile,
    ListeningReasonType
)


# ================================
# CONFIGURATION MOTIVATIONS SCORER
# ================================

@dataclass
class MotivationsScorerConfig:
    """Configuration du scorer motivations professionnelles"""
    
    # Poids du composant
    base_weight: float = 0.08
    
    # Seuils de scoring
    excellent_alignment_threshold: float = 0.85  # Score excellent si > 85%
    good_alignment_threshold: float = 0.70      # Score bon si > 70%
    acceptable_alignment_threshold: float = 0.50 # Score acceptable si > 50%
    
    # Facteurs de pondération interne
    priority_factor: float = 1.5     # Boost pour motivations prioritaires candidat
    alignment_factor: float = 1.3    # Boost pour alignement position
    mismatch_penalty: float = 0.7    # Pénalité pour désalignement important
    
    # Bonus/Malus spéciaux
    coherence_bonus: float = 0.15    # Bonus cohérence motivation/raison d'écoute
    diversity_bonus: float = 0.10    # Bonus pour diversité motivations bien équilibrées
    focus_bonus: float = 0.05        # Bonus pour focus clair (1-2 motivations principales)


# ================================
# ANALYSEUR DE MOTIVATIONS
# ================================

class MotivationAnalyzer:
    """Analyse les motivations professionnelles candidat vs poste"""
    
    def __init__(self, config: MotivationsScorerConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Mapping motivations → indicateurs poste
        self.motivation_indicators = {
            MotivationType.CHALLENGE_TECHNIQUE: {
                "keywords": ["technique", "technologie", "innovation", "développement", "architecture", "R&D"],
                "position_types": ["développeur", "ingénieur", "architecte", "tech lead", "CTO"],
                "company_indicators": ["startup tech", "scale-up", "innovation", "produit technique"],
                "weight_factor": 1.2  # Motivation très recherchée
            },
            MotivationType.EVOLUTION_CARRIERE: {
                "keywords": ["évolution", "carrière", "promotion", "management", "responsabilités", "growth"],
                "position_types": ["senior", "lead", "manager", "directeur", "head of"],
                "company_indicators": ["croissance", "expansion", "scale-up", "opportunités"],
                "weight_factor": 1.3  # Motivation clé pour rétention
            },
            MotivationType.AUTONOMIE: {
                "keywords": ["autonomie", "indépendant", "liberté", "remote", "flexible", "ownership"],
                "position_types": ["senior", "expert", "consultant", "freelance"],
                "company_indicators": ["culture autonomie", "remote-first", "confiance", "ownership"],
                "weight_factor": 1.1
            },
            MotivationType.IMPACT_BUSINESS: {
                "keywords": ["impact", "business", "résultats", "croissance", "performance", "ROI"],
                "position_types": ["business", "commercial", "product", "growth", "revenue"],
                "company_indicators": ["scale-up", "croissance", "impact", "mission"],
                "weight_factor": 1.2
            },
            MotivationType.APPRENTISSAGE: {
                "keywords": ["apprentissage", "formation", "nouvelles technologies", "compétences", "learning"],
                "position_types": ["junior", "développeur", "consultant", "analyst"],
                "company_indicators": ["formation", "learning", "technologies récentes", "R&D"],
                "weight_factor": 1.0
            },
            MotivationType.LEADERSHIP: {
                "keywords": ["leadership", "équipe", "management", "encadrement", "mentor", "coaching"],
                "position_types": ["manager", "lead", "directeur", "head", "senior"],
                "company_indicators": ["management", "équipe", "croissance équipe", "culture leadership"],
                "weight_factor": 1.2
            },
            MotivationType.INNOVATION: {
                "keywords": ["innovation", "créativité", "nouveauté", "disruptif", "avant-garde", "R&D"],
                "position_types": ["product", "innovation", "R&D", "startup", "tech"],
                "company_indicators": ["innovation", "startup", "disruption", "nouveaux produits"],
                "weight_factor": 1.1
            },
            MotivationType.EQUILIBRE_VIE: {
                "keywords": ["équilibre", "vie privée", "famille", "bien-être", "télétravail", "horaires"],
                "position_types": ["remote", "temps partiel", "flexible"],
                "company_indicators": ["work-life balance", "télétravail", "flexibilité", "bien-être"],
                "weight_factor": 1.0
            }
        }
    
    def analyze_candidate_motivations(self, profile: ExtendedMatchingProfile) -> Dict[str, Any]:
        """Analyse les motivations du candidat"""
        
        motivations = profile.motivations.candidate_motivations
        priorities = profile.motivations.motivation_priorities
        
        analysis = {
            "total_motivations": len(motivations),
            "top_motivations": [],
            "motivation_scores": {},
            "motivation_distribution": {},
            "focus_score": 0.0,
            "coherence_with_listening_reason": 0.0
        }
        
        if not motivations:
            self.logger.warning("No candidate motivations found")
            return analysis
        
        # 1. Analyse distribution et scores
        total_score = sum(motivations.values())
        for motivation, score in motivations.items():
            normalized_score = score / 5.0  # Normalisation 1-5 → 0-1
            weight_factor = self.motivation_indicators[motivation]["weight_factor"]
            weighted_score = normalized_score * weight_factor
            
            analysis["motivation_scores"][motivation.value] = weighted_score
            analysis["motivation_distribution"][motivation.value] = score / total_score if total_score > 0 else 0
        
        # 2. Top motivations (score >= 4/5)
        top_motivations = [
            (motivation, score) for motivation, score in motivations.items() 
            if score >= 4
        ]
        top_motivations.sort(key=lambda x: x[1], reverse=True)
        analysis["top_motivations"] = [(m.value, s) for m, s in top_motivations[:3]]
        
        # 3. Score de focus (concentration sur quelques motivations clés)
        if len(motivations) > 0:
            scores = list(motivations.values())
            max_score = max(scores)
            high_scores = [s for s in scores if s >= 4]
            analysis["focus_score"] = len(high_scores) / len(scores) if len(high_scores) <= 3 else 0.5
        
        # 4. Cohérence avec raison d'écoute
        analysis["coherence_with_listening_reason"] = self._analyze_listening_coherence(
            profile.listening_reason.primary_reason, motivations
        )
        
        return analysis
    
    def analyze_position_alignment(
        self, 
        candidate_motivations: Dict[MotivationType, int],
        position_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyse l'alignement motivations candidat vs poste"""
        
        alignment = {
            "motivation_alignments": {},
            "overall_alignment": 0.0,
            "strong_matches": [],
            "potential_mismatches": [],
            "alignment_factors": []
        }
        
        if not candidate_motivations or not position_requirements:
            return alignment
        
        total_alignment = 0.0
        motivation_count = len(candidate_motivations)
        
        for motivation, candidate_score in candidate_motivations.items():
            motivation_alignment = self._calculate_motivation_alignment(
                motivation, candidate_score, position_requirements
            )
            
            alignment["motivation_alignments"][motivation.value] = motivation_alignment
            total_alignment += motivation_alignment["score"]
            
            # Classification des matches
            if motivation_alignment["score"] > 0.8 and candidate_score >= 4:
                alignment["strong_matches"].append({
                    "motivation": motivation.value,
                    "score": motivation_alignment["score"],
                    "factors": motivation_alignment["factors"]
                })
            elif motivation_alignment["score"] < 0.3 and candidate_score >= 4:
                alignment["potential_mismatches"].append({
                    "motivation": motivation.value,
                    "candidate_score": candidate_score,
                    "alignment_score": motivation_alignment["score"]
                })
        
        alignment["overall_alignment"] = total_alignment / motivation_count if motivation_count > 0 else 0.0
        
        return alignment
    
    def _calculate_motivation_alignment(
        self, 
        motivation: MotivationType, 
        candidate_score: int,
        position_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calcule l'alignement d'une motivation spécifique"""
        
        indicators = self.motivation_indicators[motivation]
        alignment_score = 0.0
        factors = []
        
        # 1. Analyse du titre/description du poste
        position_text = " ".join([
            position_requirements.get("title", ""),
            position_requirements.get("description", ""),
            position_requirements.get("responsibilities", "")
        ]).lower()
        
        keyword_matches = sum(1 for keyword in indicators["keywords"] if keyword in position_text)
        if keyword_matches > 0:
            keyword_factor = min(keyword_matches / len(indicators["keywords"]), 1.0)
            alignment_score += keyword_factor * 0.4
            factors.append(f"Keywords match: {keyword_matches}/{len(indicators['keywords'])}")
        
        # 2. Analyse du type de poste
        position_type_match = any(
            pos_type in position_text for pos_type in indicators["position_types"]
        )
        if position_type_match:
            alignment_score += 0.3
            factors.append("Position type match")
        
        # 3. Analyse des indicateurs entreprise
        company_text = " ".join([
            position_requirements.get("company_description", ""),
            position_requirements.get("company_culture", ""),
            position_requirements.get("sector", "")
        ]).lower()
        
        company_matches = sum(1 for indicator in indicators["company_indicators"] if indicator in company_text)
        if company_matches > 0:
            company_factor = min(company_matches / len(indicators["company_indicators"]), 1.0)
            alignment_score += company_factor * 0.3
            factors.append(f"Company indicators: {company_matches}/{len(indicators['company_indicators'])}")
        
        # 4. Motivations explicites du poste
        explicit_motivations = position_requirements.get("motivations_offered", {})
        if motivation.value in explicit_motivations:
            explicit_score = explicit_motivations[motivation.value] / 5.0
            alignment_score += explicit_score * 0.2
            factors.append(f"Explicit motivation score: {explicit_score:.2f}")
        
        return {
            "score": min(alignment_score, 1.0),
            "factors": factors,
            "weight_factor": indicators["weight_factor"]
        }
    
    def _analyze_listening_coherence(
        self, 
        listening_reason: ListeningReasonType, 
        motivations: Dict[MotivationType, int]
    ) -> float:
        """Analyse la cohérence motivations vs raison d'écoute"""
        
        coherence_mappings = {
            ListeningReasonType.PERSPECTIVES: [
                MotivationType.EVOLUTION_CARRIERE,
                MotivationType.APPRENTISSAGE,
                MotivationType.LEADERSHIP,
                MotivationType.CHALLENGE_TECHNIQUE
            ],
            ListeningReasonType.POSTE_INADEQUAT: [
                MotivationType.CHALLENGE_TECHNIQUE,
                MotivationType.AUTONOMIE,
                MotivationType.IMPACT_BUSINESS,
                MotivationType.INNOVATION
            ],
            ListeningReasonType.FLEXIBILITE: [
                MotivationType.AUTONOMIE,
                MotivationType.EQUILIBRE_VIE
            ],
            ListeningReasonType.REMUNERATION_FAIBLE: [
                MotivationType.EVOLUTION_CARRIERE,
                MotivationType.IMPACT_BUSINESS
            ]
        }
        
        expected_motivations = coherence_mappings.get(listening_reason, [])
        if not expected_motivations:
            return 0.5  # Score neutre si pas de mapping
        
        coherence_score = 0.0
        for motivation in expected_motivations:
            if motivation in motivations:
                # Plus la motivation est forte, plus la cohérence est élevée
                motivation_strength = motivations[motivation] / 5.0
                coherence_score += motivation_strength
        
        return min(coherence_score / len(expected_motivations), 1.0)


# ================================
# SCORER PRINCIPAL
# ================================

class ProfessionalMotivationsScorer:
    """
    Scorer principal pour les motivations professionnelles - V3.0
    
    Fonctionnalités:
    - Analyse des 8 types de motivations candidat
    - Alignement motivations vs opportunités poste
    - Score de compatibilité motivationnelle intelligent
    - Intégration avec pondération adaptative
    """
    
    def __init__(self, config: Optional[MotivationsScorerConfig] = None):
        self.config = config or MotivationsScorerConfig()
        self.analyzer = MotivationAnalyzer(self.config)
        self.logger = logging.getLogger(__name__)
    
    def score(
        self, 
        candidate_profile: ExtendedMatchingProfile,
        position_requirements: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Calcule le score de compatibilité motivationnelle
        
        Args:
            candidate_profile: Profil candidat V3.0 complet
            position_requirements: Exigences et opportunités du poste
        
        Returns:
            Tuple[float, Dict]: (score_0_1, detailed_analysis)
        """
        
        start_time = datetime.now()
        
        # 1. Analyse motivations candidat
        candidate_analysis = self.analyzer.analyze_candidate_motivations(candidate_profile)
        
        # 2. Analyse alignement avec poste
        position_alignment = self.analyzer.analyze_position_alignment(
            candidate_profile.motivations.candidate_motivations,
            position_requirements
        )
        
        # 3. Calcul score base
        base_score = self._calculate_base_score(candidate_analysis, position_alignment)
        
        # 4. Application des bonus/malus
        adjusted_score = self._apply_scoring_adjustments(
            base_score, candidate_analysis, position_alignment, candidate_profile
        )
        
        # 5. Normalisation finale
        final_score = max(0.0, min(1.0, adjusted_score))
        
        # 6. Analyse détaillée
        detailed_analysis = {
            "motivations_score": final_score,
            "candidate_analysis": candidate_analysis,
            "position_alignment": position_alignment,
            "scoring_factors": self._get_scoring_factors(candidate_analysis, position_alignment),
            "recommendations": self._generate_recommendations(candidate_analysis, position_alignment),
            "processing_time_ms": (datetime.now() - start_time).total_seconds() * 1000
        }
        
        self.logger.debug(f"Motivations score calculated: {final_score:.3f}")
        
        return final_score, detailed_analysis
    
    def _calculate_base_score(
        self, 
        candidate_analysis: Dict[str, Any], 
        position_alignment: Dict[str, Any]
    ) -> float:
        """Calcule le score de base motivationnel"""
        
        # Score basé sur l'alignement global
        alignment_score = position_alignment["overall_alignment"]
        
        # Facteur de focus candidat (bonus si motivations claires)
        focus_factor = 1.0 + (candidate_analysis["focus_score"] * 0.2)
        
        # Facteur nombre de strong matches
        strong_matches_count = len(position_alignment["strong_matches"])
        strong_matches_factor = 1.0 + (strong_matches_count * 0.1)
        
        # Pénalité pour mismatches importants
        mismatches_count = len(position_alignment["potential_mismatches"])
        mismatch_penalty = max(0.8, 1.0 - (mismatches_count * 0.1))
        
        base_score = alignment_score * focus_factor * strong_matches_factor * mismatch_penalty
        
        return base_score
    
    def _apply_scoring_adjustments(
        self, 
        base_score: float,
        candidate_analysis: Dict[str, Any],
        position_alignment: Dict[str, Any],
        candidate_profile: ExtendedMatchingProfile
    ) -> float:
        """Applique les ajustements de scoring (bonus/malus)"""
        
        adjusted_score = base_score
        
        # 1. Bonus cohérence avec raison d'écoute
        coherence_score = candidate_analysis["coherence_with_listening_reason"]
        if coherence_score > 0.7:
            coherence_bonus = self.config.coherence_bonus * coherence_score
            adjusted_score += coherence_bonus
        
        # 2. Bonus diversité motivations équilibrées
        motivation_count = candidate_analysis["total_motivations"]
        if 3 <= motivation_count <= 5:  # Sweet spot
            adjusted_score += self.config.diversity_bonus
        
        # 3. Bonus focus (1-2 motivations principales très fortes)
        top_motivations = candidate_analysis["top_motivations"]
        if len(top_motivations) <= 2 and len(top_motivations) > 0:
            # Vérifie que les motivations principales sont vraiment dominantes
            if all(score >= 4 for _, score in top_motivations):
                adjusted_score += self.config.focus_bonus
        
        # 4. Boost selon raison d'écoute (déjà géré par pondération adaptative)
        listening_reason = candidate_profile.listening_reason.primary_reason
        if listening_reason in [ListeningReasonType.PERSPECTIVES, ListeningReasonType.POSTE_INADEQUAT]:
            # Boost additionnel pour ces raisons d'écoute liées aux motivations
            adjusted_score *= 1.1
        
        return adjusted_score
    
    def _get_scoring_factors(
        self, 
        candidate_analysis: Dict[str, Any], 
        position_alignment: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Retourne les facteurs qui ont influencé le score"""
        
        factors = []
        
        # Facteurs positifs
        if position_alignment["overall_alignment"] > self.config.excellent_alignment_threshold:
            factors.append({
                "type": "positive",
                "factor": "Excellent alignment",
                "impact": position_alignment["overall_alignment"],
                "description": "Les motivations du candidat s'alignent parfaitement avec le poste"
            })
        
        strong_matches = len(position_alignment["strong_matches"])
        if strong_matches > 0:
            factors.append({
                "type": "positive", 
                "factor": "Strong motivation matches",
                "impact": strong_matches * 0.1,
                "description": f"{strong_matches} motivation(s) fortement alignée(s)"
            })
        
        # Facteurs négatifs
        mismatches = len(position_alignment["potential_mismatches"])
        if mismatches > 0:
            factors.append({
                "type": "negative",
                "factor": "Potential mismatches",
                "impact": mismatches * 0.1,
                "description": f"{mismatches} motivation(s) potentiellement mal alignée(s)"
            })
        
        # Facteurs de qualité
        focus_score = candidate_analysis["focus_score"]
        if focus_score > 0.7:
            factors.append({
                "type": "quality",
                "factor": "Clear motivation focus",
                "impact": focus_score * 0.2,
                "description": "Motivations claires et bien définies"
            })
        
        return factors
    
    def _generate_recommendations(
        self, 
        candidate_analysis: Dict[str, Any], 
        position_alignment: Dict[str, Any]
    ) -> List[str]:
        """Génère des recommandations basées sur l'analyse"""
        
        recommendations = []
        
        # Recommandations basées sur l'alignement
        overall_alignment = position_alignment["overall_alignment"]
        
        if overall_alignment > self.config.excellent_alignment_threshold:
            recommendations.append("✅ Excellent fit motivationnel - candidat parfaitement aligné")
        elif overall_alignment > self.config.good_alignment_threshold:
            recommendations.append("👍 Bon fit motivationnel - alignement satisfaisant")
        elif overall_alignment > self.config.acceptable_alignment_threshold:
            recommendations.append("⚠️ Fit motivationnel modéré - vérifier points de friction")
        else:
            recommendations.append("❌ Fit motivationnel faible - risque de désengagement")
        
        # Recommandations spécifiques
        strong_matches = position_alignment["strong_matches"]
        if strong_matches:
            top_match = strong_matches[0]
            recommendations.append(f"🎯 Mettre en avant: {top_match['motivation']} - forte motivation alignée")
        
        mismatches = position_alignment["potential_mismatches"]
        if mismatches:
            top_mismatch = mismatches[0]
            recommendations.append(f"⚠️ Point d'attention: {top_mismatch['motivation']} - vérifier si poste peut combler cette attente")
        
        # Recommandations d'entretien
        focus_score = candidate_analysis["focus_score"]
        if focus_score < 0.5:
            recommendations.append("🔍 Approfondir en entretien: motivations peu claires, creuser les priorités réelles")
        
        return recommendations


# ================================
# INTÉGRATION ET UTILITAIRES  
# ================================

def create_motivations_scorer(custom_config: Optional[Dict[str, Any]] = None) -> ProfessionalMotivationsScorer:
    """Factory pour créer un scorer motivations avec configuration personnalisée"""
    
    config = MotivationsScorerConfig()
    
    if custom_config:
        for key, value in custom_config.items():
            if hasattr(config, key):
                setattr(config, key, value)
    
    return ProfessionalMotivationsScorer(config)


def get_motivation_insights(motivation_type: MotivationType) -> Dict[str, Any]:
    """Retourne des insights sur un type de motivation spécifique"""
    
    analyzer = MotivationAnalyzer(MotivationsScorerConfig())
    indicators = analyzer.motivation_indicators.get(motivation_type, {})
    
    return {
        "motivation": motivation_type.value,
        "description": _get_motivation_description(motivation_type),
        "keywords": indicators.get("keywords", []),
        "ideal_positions": indicators.get("position_types", []),
        "company_fit": indicators.get("company_indicators", []),
        "weight_factor": indicators.get("weight_factor", 1.0),
        "tips": _get_motivation_tips(motivation_type)
    }


def _get_motivation_description(motivation: MotivationType) -> str:
    """Descriptions des types de motivations"""
    descriptions = {
        MotivationType.CHALLENGE_TECHNIQUE: "Recherche de défis techniques complexes et innovants",
        MotivationType.EVOLUTION_CARRIERE: "Volonté d'évolution et de progression professionnelle",
        MotivationType.AUTONOMIE: "Besoin d'indépendance et de liberté dans le travail",
        MotivationType.IMPACT_BUSINESS: "Motivation par l'impact business et les résultats",
        MotivationType.APPRENTISSAGE: "Passion pour l'apprentissage et le développement de compétences",
        MotivationType.LEADERSHIP: "Intérêt pour le management et l'encadrement d'équipes",
        MotivationType.INNOVATION: "Attrait pour l'innovation et la créativité",
        MotivationType.EQUILIBRE_VIE: "Recherche d'équilibre entre vie professionnelle et personnelle"
    }
    return descriptions.get(motivation, "Motivation professionnelle")


def _get_motivation_tips(motivation: MotivationType) -> List[str]:
    """Tips pour satisfaire chaque type de motivation"""
    tips = {
        MotivationType.CHALLENGE_TECHNIQUE: [
            "Proposer des projets techniques ambitieux",
            "Accès aux dernières technologies",
            "Participation à l'architecture technique"
        ],
        MotivationType.EVOLUTION_CARRIERE: [
            "Plan de carrière clair",
            "Opportunités de promotion",
            "Nouvelles responsabilités régulières"
        ],
        MotivationType.AUTONOMIE: [
            "Télétravail ou flexibilité horaires",
            "Ownership sur les projets",
            "Liberté dans les méthodes de travail"
        ],
        MotivationType.IMPACT_BUSINESS: [
            "Lien direct avec les objectifs business",
            "Métriques de performance visibles",
            "Participation aux décisions stratégiques"
        ],
        MotivationType.APPRENTISSAGE: [
            "Budget formation conséquent",
            "Veille technologique",
            "Mentorat et coaching"
        ],
        MotivationType.LEADERSHIP: [
            "Opportunités d'encadrement",
            "Projets transverses",
            "Formation management"
        ],
        MotivationType.INNOVATION: [
            "Temps dédié à l'innovation",
            "Culture expérimentation",
            "Hackathons et projets créatifs"
        ],
        MotivationType.EQUILIBRE_VIE: [
            "Horaires flexibles",
            "Télétravail possible",
            "Respect vie privée"
        ]
    }
    return tips.get(motivation, [])


# ================================
# TESTS ET VALIDATION
# ================================

def test_motivations_scorer():
    """Test complet du scorer motivations professionnelles"""
    
    print("=== TEST MOTIVATIONS SCORER V3.0 ===")
    
    # Import pour test
    from ..models.extended_matching_models_v3 import ExtendedMatchingProfile, ListeningReasonType
    
    # Création profil test
    profile = ExtendedMatchingProfile()
    
    # Motivations candidat
    profile.motivations.candidate_motivations = {
        MotivationType.CHALLENGE_TECHNIQUE: 5,
        MotivationType.EVOLUTION_CARRIERE: 4,
        MotivationType.APPRENTISSAGE: 4,
        MotivationType.AUTONOMIE: 3,
        MotivationType.EQUILIBRE_VIE: 2
    }
    
    profile.listening_reason.primary_reason = ListeningReasonType.PERSPECTIVES
    
    # Requirements poste
    position_requirements = {
        "title": "Senior Software Engineer",
        "description": "Développement d'architecture technique innovante, leadership technique équipe",
        "responsibilities": "Conception architecture, mentoring développeurs junior, veille technologique",
        "company_description": "Startup tech en forte croissance, culture innovation",
        "motivations_offered": {
            "challenge_technique": 5,
            "evolution_carriere": 4,
            "apprentissage": 4,
            "autonomie": 3
        }
    }
    
    # Test scoring
    scorer = ProfessionalMotivationsScorer()
    score, analysis = scorer.score(profile, position_requirements)
    
    print(f"Score motivations: {score:.3f}")
    print(f"Alignement global: {analysis['position_alignment']['overall_alignment']:.3f}")
    print(f"Strong matches: {len(analysis['position_alignment']['strong_matches'])}")
    print(f"Focus score: {analysis['candidate_analysis']['focus_score']:.3f}")
    
    print("\nTop motivations candidat:")
    for motivation, score in analysis['candidate_analysis']['top_motivations']:
        print(f"  - {motivation}: {score}/5")
    
    print("\nStrong matches:")
    for match in analysis['position_alignment']['strong_matches']:
        print(f"  - {match['motivation']}: {match['score']:.3f}")
    
    print("\nRecommandations:")
    for rec in analysis['recommendations']:
        print(f"  {rec}")


if __name__ == "__main__":
    # Configuration logging
    logging.basicConfig(level=logging.INFO)
    
    # Test du scorer
    test_motivations_scorer()
    
    # Test insights motivation
    print("\n=== INSIGHTS MOTIVATION ===")
    insights = get_motivation_insights(MotivationType.CHALLENGE_TECHNIQUE)
    print(f"Motivation: {insights['motivation']}")
    print(f"Description: {insights['description']}")
    print(f"Positions idéales: {insights['ideal_positions']}")
    print(f"Tips: {insights['tips']}")
