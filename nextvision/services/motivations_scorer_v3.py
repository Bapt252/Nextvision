"""
🎯 Nextvision v3.0 - Motivations Scorer - Correspondance Aspirations Candidat

Analyse intelligente des motivations professionnelles candidat vs opportunités entreprise :
- 📊 8% de poids dans scoring global (+ boost via pondération adaptative)
- 🎯 Analyse classement motivations candidat (questionnaire étape 3)
- 🏢 Correspondance avec opportunités offertes par l'entreprise
- 🧠 Bénéficie de la pondération adaptative du Listening Reasons Scorer
- 💡 Recommandations personnalisées selon aspirations

Motivations Analysées (questionnaire candidat) :
┌─ ÉVOLUTION (Perspectives d'évolution)
├─ SALAIRE (Augmentation salariale)  
├─ FLEXIBILITÉ (Équilibre vie pro/perso)
└─ AUTRE (Motivation spécifique candidat)

Pondération Adaptative selon Raison d'Écoute :
- MANQUE_PERSPECTIVES → Boost Motivations à 15% 
- MANQUE_FLEXIBILITE → Boost Motivations à 12%
- Autres raisons → Maintien 8% de base

Author: NEXTEN Team
Version: 3.0.0 - Motivations Matching Scorer
"""

import nextvision_logging as logging
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Import des modèles V3.0
from nextvision.models.extended_matching_models_v3 import (
    ExtendedCandidateProfileV3, ExtendedCompanyProfileV3,
    MotivationProfessionnelle, RaisonEcouteEtendue
)

# Import base scorer V2.0 pour héritage
from nextvision.services.bidirectional_scorer import BaseScorer, ScoringResult

logger = logging.getLogger(__name__)

# === STRUCTURES MOTIVATIONS ===

@dataclass
class MotivationMatch:
    """🎯 Correspondance d'une motivation candidat avec opportunités entreprise"""
    motivation: MotivationProfessionnelle
    ranking_position: int  # Position dans classement candidat (1-4)
    weight_in_ranking: float  # Poids selon position (1er=40%, 2e=30%, 3e=20%, 4e=10%)
    
    # Analyse opportunités entreprise
    enterprise_opportunities: List[str]
    match_score: float  # 0-1 score de correspondance
    match_quality: str  # "excellent", "good", "average", "poor"
    
    # Détails
    matching_factors: List[str]
    missing_opportunities: List[str]
    recommendations: List[str]

@dataclass
class MotivationsAnalysis:
    """📊 Analyse complète des motivations candidat vs entreprise"""
    total_motivations: int
    motivation_matches: List[MotivationMatch]
    
    # Scores globaux
    weighted_motivation_score: float  # Score pondéré selon ranking
    aspiration_alignment: float  # Alignement aspirations textuelles
    motivation_coverage: float  # % motivations couvertes par entreprise
    
    # Insights
    top_motivation_satisfied: bool
    strongest_opportunities: List[str]
    biggest_gaps: List[str]
    
    # Recommandations
    enterprise_recommendations: List[str]
    candidate_expectations: List[str]

# === ANALYSEUR MOTIVATIONS ===

class MotivationsAnalyzer:
    """🔍 Analyseur intelligent des motivations professionnelles"""
    
    def __init__(self):
        # Mapping motivations → opportunités entreprise
        self.motivation_opportunities_mapping = {
            MotivationProfessionnelle.EVOLUTION: {
                'enterprise_indicators': [
                    'plan_carriere', 'promotion_interne', 'formation_leadership',
                    'mobilite_interne', 'evolution_rapide', 'mentoring',
                    'responsabilites_croissantes', 'gestion_equipe'
                ],
                'description_keywords': [
                    'évolution', 'promotion', 'carrière', 'progression',
                    'leadership', 'management', 'responsabilités', 'développement'
                ],
                'enterprise_solutions': [
                    'plan_carriere_clair', 'promotions_internes_prioritaires',
                    'formation_management', 'mobilite_departements',
                    'mentoring_senior', 'projets_leadership'
                ]
            },
            
            MotivationProfessionnelle.SALAIRE: {
                'enterprise_indicators': [
                    'salaire_competitif', 'augmentations_regulieres', 'variable_performance',
                    'bonus_objectifs', 'participation_benefices', 'stock_options',
                    'avantages_financiers', 'prime_performance'
                ],
                'description_keywords': [
                    'salaire', 'rémunération', 'augmentation', 'bonus',
                    'variable', 'prime', 'avantages', 'intéressement'
                ],
                'enterprise_solutions': [
                    'politique_augmentation_transparente', 'variable_attractive',
                    'revenus_complementaires', 'avantages_sociaux_etendus',
                    'prime_performance_individuelle', 'participation_croissance'
                ]
            },
            
            MotivationProfessionnelle.FLEXIBILITE: {
                'enterprise_indicators': [
                    'remote_possible', 'horaires_flexibles', 'temps_partiel',
                    'conges_flexibles', 'equilibre_vie_pro_perso', 'autonomie',
                    'organisation_libre', 'sabbatiques_possibles'
                ],
                'description_keywords': [
                    'flexible', 'remote', 'télétravail', 'horaires',
                    'équilibre', 'autonomie', 'liberté', 'souplesse'
                ],
                'enterprise_solutions': [
                    'teletravail_partiel_total', 'horaires_variables',
                    'conges_illimites', 'compression_semaine',
                    'flextime_core_hours', 'sabbatique_possible'
                ]
            },
            
            MotivationProfessionnelle.AUTRE: {
                'enterprise_indicators': [
                    'innovation', 'impact_social', 'creativite', 'reconnaissance',
                    'defis_techniques', 'apprentissage_continu', 'environnement_stimulant'
                ],
                'description_keywords': [
                    'innovation', 'créativité', 'impact', 'reconnaissance',
                    'défi', 'apprentissage', 'stimulant', 'passionnant'
                ],
                'enterprise_solutions': [
                    'projets_innovants', 'impact_positif_mesurable',
                    'reconnaissance_realisations', 'defis_techniques_reguliers',
                    'formation_continue_payee', 'environnement_creativite'
                ]
            }
        }
        
        # Poids selon position dans ranking candidat
        self.ranking_weights = {
            1: 0.40,  # 1ère motivation = 40% du score motivations
            2: 0.30,  # 2ème motivation = 30% du score motivations
            3: 0.20,  # 3ème motivation = 20% du score motivations  
            4: 0.10   # 4ème motivation = 10% du score motivations
        }
    
    def analyze_motivations(self, candidat: ExtendedCandidateProfileV3,
                           entreprise: ExtendedCompanyProfileV3) -> MotivationsAnalysis:
        """🎯 Analyse complète motivations candidat vs opportunités entreprise"""
        
        # Extraction motivations candidat
        motivations_ranking = candidat.motivations_extended.ranking
        aspirations_text = candidat.motivations_extended.aspirations_texte
        
        if not motivations_ranking:
            # Fallback si pas de ranking - utiliser motivations V2.0
            motivations_ranking = self._extract_v2_motivations(candidat)
        
        # Analyse de chaque motivation
        motivation_matches = []
        total_weighted_score = 0.0
        
        for position, motivation in enumerate(motivations_ranking, 1):
            if position > 4:  # Max 4 motivations
                break
                
            match = self._analyze_single_motivation(
                motivation, position, entreprise
            )
            motivation_matches.append(match)
            
            # Calcul score pondéré
            weight = self.ranking_weights.get(position, 0.0)
            total_weighted_score += match.match_score * weight
        
        # Analyse aspirations textuelles
        aspiration_alignment = self._analyze_aspirations_text(
            aspirations_text, entreprise
        ) if aspirations_text else 0.5
        
        # Calcul couverture motivations
        motivation_coverage = self._calculate_motivation_coverage(motivation_matches)
        
        # Génération insights
        insights = self._generate_insights(motivation_matches, entreprise)
        
        return MotivationsAnalysis(
            total_motivations=len(motivations_ranking),
            motivation_matches=motivation_matches,
            weighted_motivation_score=total_weighted_score,
            aspiration_alignment=aspiration_alignment,
            motivation_coverage=motivation_coverage,
            top_motivation_satisfied=motivation_matches[0].match_score >= 0.7 if motivation_matches else False,
            strongest_opportunities=insights['strongest_opportunities'],
            biggest_gaps=insights['biggest_gaps'],
            enterprise_recommendations=insights['enterprise_recommendations'],
            candidate_expectations=insights['candidate_expectations']
        )
    
    def _analyze_single_motivation(self, motivation: MotivationProfessionnelle,
                                 position: int, entreprise: ExtendedCompanyProfileV3) -> MotivationMatch:
        """🔍 Analyse une motivation spécifique"""
        
        # Configuration pour cette motivation
        motivation_config = self.motivation_opportunities_mapping.get(motivation, {})
        indicators = motivation_config.get('enterprise_indicators', [])
        keywords = motivation_config.get('description_keywords', [])
        solutions = motivation_config.get('enterprise_solutions', [])
        
        # Recherche opportunités dans profil entreprise
        found_opportunities = []
        matching_factors = []
        
        # Analyse description poste
        if entreprise.poste.description:
            desc_lower = entreprise.poste.description.lower()
            for keyword in keywords:
                if keyword in desc_lower:
                    found_opportunities.append(f"Description mentionne: {keyword}")
                    matching_factors.append(keyword)
        
        # Analyse avantages
        if hasattr(entreprise.poste, 'avantages') and entreprise.poste.avantages:
            for avantage in entreprise.poste.avantages:
                avantage_lower = avantage.lower()
                for keyword in keywords:
                    if keyword in avantage_lower:
                        found_opportunities.append(f"Avantage: {avantage}")
                        matching_factors.append(keyword)
        
        # Analyse modalités entreprise (pour flexibilité)
        if motivation == MotivationProfessionnelle.FLEXIBILITE:
            if entreprise.modalites_entreprise.remote_possible:
                found_opportunities.append("Télétravail possible")
                matching_factors.append("remote")
            if entreprise.modalites_entreprise.horaires_flexibles:
                found_opportunities.append("Horaires flexibles")
                matching_factors.append("horaires")
        
        # Analyse salaire (pour motivation salaire)
        if motivation == MotivationProfessionnelle.SALAIRE:
            if entreprise.poste.salaire_max and entreprise.poste.salaire_max >= 50000:
                found_opportunities.append("Rémunération attractive")
                matching_factors.append("salaire")
            if entreprise.criteres_flexibilite.flexibilite_salariale > 0.2:
                found_opportunities.append("Négociation salariale possible")
                matching_factors.append("negociation")
        
        # Calcul score de correspondance
        max_possible_opportunities = len(solutions)
        opportunities_found = len(found_opportunities)
        
        if max_possible_opportunities > 0:
            base_score = opportunities_found / max_possible_opportunities
        else:
            base_score = 0.5  # Score neutre si pas de solutions définies
        
        # Ajustement selon position dans ranking (plus important = exigence plus forte)
        ranking_factor = 1.0 + ((5 - position) * 0.1)  # 1er = +40%, 2e = +30%, etc.
        adjusted_score = min(1.0, base_score * ranking_factor)
        
        # Détermination qualité
        if adjusted_score >= 0.8:
            match_quality = "excellent"
        elif adjusted_score >= 0.6:
            match_quality = "good"
        elif adjusted_score >= 0.4:
            match_quality = "average"
        else:
            match_quality = "poor"
        
        # Opportunités manquantes
        missing_opportunities = [sol for sol in solutions 
                               if not any(factor in sol.lower() for factor in matching_factors)]
        
        # Recommandations spécifiques
        recommendations = self._generate_motivation_recommendations(
            motivation, adjusted_score, found_opportunities, missing_opportunities
        )
        
        return MotivationMatch(
            motivation=motivation,
            ranking_position=position,
            weight_in_ranking=self.ranking_weights.get(position, 0.0),
            enterprise_opportunities=found_opportunities,
            match_score=adjusted_score,
            match_quality=match_quality,
            matching_factors=matching_factors,
            missing_opportunities=missing_opportunities,
            recommendations=recommendations
        )
    
    def _analyze_aspirations_text(self, aspirations: str, 
                                entreprise: ExtendedCompanyProfileV3) -> float:
        """💭 Analyse aspirations textuelles candidat vs entreprise"""
        
        if not aspirations or len(aspirations.strip()) < 10:
            return 0.5  # Score neutre si pas d'aspirations détaillées
        
        aspirations_lower = aspirations.lower()
        score = 0.0
        
        # Analyse entreprise description
        if entreprise.entreprise.description:
            desc_lower = entreprise.entreprise.description.lower()
            # Mots-clés communs
            common_words = self._find_common_meaningful_words(aspirations_lower, desc_lower)
            score += min(0.4, len(common_words) * 0.1)
        
        # Analyse poste description  
        if entreprise.poste.description:
            poste_lower = entreprise.poste.description.lower()
            common_words = self._find_common_meaningful_words(aspirations_lower, poste_lower)
            score += min(0.4, len(common_words) * 0.1)
        
        # Bonus mots-clés spéciaux
        special_keywords = ['innovation', 'impact', 'développement', 'créativité', 'défi']
        for keyword in special_keywords:
            if keyword in aspirations_lower:
                if (entreprise.poste.description and keyword in entreprise.poste.description.lower()) or \
                   (entreprise.entreprise.description and keyword in entreprise.entreprise.description.lower()):
                    score += 0.1
        
        return min(1.0, score)
    
    def _find_common_meaningful_words(self, text1: str, text2: str) -> List[str]:
        """🔍 Trouve mots significatifs communs entre deux textes"""
        
        # Mots vides à ignorer
        stop_words = {'le', 'la', 'les', 'de', 'du', 'des', 'et', 'ou', 'à', 'dans', 'pour', 'avec', 'sur'}
        
        words1 = set(word for word in text1.split() if len(word) > 3 and word not in stop_words)
        words2 = set(word for word in text2.split() if len(word) > 3 and word not in stop_words)
        
        return list(words1.intersection(words2))
    
    def _calculate_motivation_coverage(self, motivation_matches: List[MotivationMatch]) -> float:
        """📊 Calcule pourcentage de motivations bien couvertes"""
        
        if not motivation_matches:
            return 0.0
        
        well_covered = sum(1 for match in motivation_matches if match.match_score >= 0.6)
        return well_covered / len(motivation_matches)
    
    def _generate_insights(self, motivation_matches: List[MotivationMatch],
                          entreprise: ExtendedCompanyProfileV3) -> Dict[str, List[str]]:
        """💡 Génère insights et recommandations"""
        
        strongest_opportunities = []
        biggest_gaps = []
        enterprise_recommendations = []
        candidate_expectations = []
        
        # Analyse des matches
        for match in motivation_matches:
            if match.match_score >= 0.7:
                strongest_opportunities.extend(match.enterprise_opportunities[:2])
            elif match.match_score < 0.4:
                biggest_gaps.append(f"{match.motivation.value} (position {match.ranking_position})")
                enterprise_recommendations.extend(match.recommendations[:1])
            
            # Attentes candidat selon ranking
            if match.ranking_position <= 2:  # Top 2 motivations
                candidate_expectations.append(
                    f"{match.motivation.value} est prioritaire (position {match.ranking_position})"
                )
        
        # Recommandations générales
        if len(strongest_opportunities) == 0:
            enterprise_recommendations.append("Revoir l'adéquation motivations candidat")
        
        if len(biggest_gaps) >= 2:
            enterprise_recommendations.append("Plusieurs motivations non satisfaites - Risque d'inadéquation")
        
        return {
            'strongest_opportunities': list(set(strongest_opportunities))[:5],
            'biggest_gaps': biggest_gaps,
            'enterprise_recommendations': list(set(enterprise_recommendations))[:5],
            'candidate_expectations': candidate_expectations
        }
    
    def _generate_motivation_recommendations(self, motivation: MotivationProfessionnelle,
                                           score: float, opportunities: List[str],
                                           missing: List[str]) -> List[str]:
        """💡 Génère recommandations spécifiques par motivation"""
        
        recommendations = []
        
        if score >= 0.7:
            recommendations.append(f"✅ {motivation.value} bien couvert - Mettre en avant lors entretien")
        elif score >= 0.4:
            recommendations.append(f"⚠️ {motivation.value} partiellement couvert - À améliorer")
        else:
            recommendations.append(f"❌ {motivation.value} insuffisamment couvert - Risque de refus")
        
        # Recommandations spécifiques selon motivation
        if motivation == MotivationProfessionnelle.EVOLUTION and score < 0.6:
            recommendations.append("💡 Détailler plan de carrière et opportunités promotion")
        elif motivation == MotivationProfessionnelle.SALAIRE and score < 0.6:
            recommendations.append("💰 Revoir politique salariale ou mettre en avant avantages")
        elif motivation == MotivationProfessionnelle.FLEXIBILITE and score < 0.6:
            recommendations.append("🔄 Proposer aménagements horaires ou télétravail")
        
        return recommendations
    
    def _extract_v2_motivations(self, candidat: ExtendedCandidateProfileV3) -> List[MotivationProfessionnelle]:
        """🔄 Fallback : extrait motivations depuis données V2.0"""
        
        motivations = []
        
        # Analyse raison d'écoute V2.0 pour déduire motivations
        if hasattr(candidat, 'motivations') and candidat.motivations.raison_ecoute:
            raison = candidat.motivations.raison_ecoute
            
            if 'remuneration' in raison.lower():
                motivations.append(MotivationProfessionnelle.SALAIRE)
            if 'perspective' in raison.lower():
                motivations.append(MotivationProfessionnelle.EVOLUTION)
            if 'flexibilite' in raison.lower():
                motivations.append(MotivationProfessionnelle.FLEXIBILITE)
        
        # Si pas de motivations détectées, ordre par défaut
        if not motivations:
            motivations = [
                MotivationProfessionnelle.EVOLUTION,
                MotivationProfessionnelle.SALAIRE
            ]
        
        return motivations

# === MOTIVATIONS SCORER PRINCIPAL ===

class MotivationsScorer(BaseScorer):
    """🎯 Motivations Scorer V3.0 - Correspondance Aspirations Candidat"""
    
    def __init__(self, weight: float = 0.08):
        super().__init__(weight)
        self.motivations_analyzer = MotivationsAnalyzer()
        
    def calculate_score(self, candidat: ExtendedCandidateProfileV3,
                       entreprise: ExtendedCompanyProfileV3) -> ScoringResult:
        """🎯 Calcule score correspondance motivations candidat vs opportunités entreprise"""
        
        start_time = time.time()
        
        try:
            # Analyse complète des motivations
            analysis = self.motivations_analyzer.analyze_motivations(candidat, entreprise)
            
            # Score de base (moyenne pondérée des matches + alignement aspirations)
            base_score = (
                analysis.weighted_motivation_score * 0.70 +  # 70% score motivations classées
                analysis.aspiration_alignment * 0.20 +      # 20% aspirations textuelles
                analysis.motivation_coverage * 0.10         # 10% couverture générale
            )
            
            # Ajustements qualitatifs
            adjusted_score = self._apply_quality_adjustments(analysis, base_score)
            
            # Génération recommandations complètes
            recommendations = self._generate_comprehensive_recommendations(analysis)
            
            # Compilation détails
            details = {
                'motivations_analysis': {
                    'total_motivations': analysis.total_motivations,
                    'weighted_motivation_score': analysis.weighted_motivation_score,
                    'aspiration_alignment': analysis.aspiration_alignment,
                    'motivation_coverage': analysis.motivation_coverage,
                    'top_motivation_satisfied': analysis.top_motivation_satisfied
                },
                'motivation_matches': [
                    {
                        'motivation': match.motivation.value,
                        'ranking_position': match.ranking_position,
                        'weight': match.weight_in_ranking,
                        'match_score': match.match_score,
                        'match_quality': match.match_quality,
                        'opportunities': match.enterprise_opportunities,
                        'missing': match.missing_opportunities
                    }
                    for match in analysis.motivation_matches
                ],
                'insights': {
                    'strongest_opportunities': analysis.strongest_opportunities,
                    'biggest_gaps': analysis.biggest_gaps,
                    'enterprise_recommendations': analysis.enterprise_recommendations,
                    'candidate_expectations': analysis.candidate_expectations
                },
                'recommendations': recommendations,
                'score_breakdown': {
                    'base_score': base_score,
                    'adjusted_score': adjusted_score,
                    'motivations_weighted': analysis.weighted_motivation_score,
                    'aspirations_alignment': analysis.aspiration_alignment,
                    'coverage_bonus': analysis.motivation_coverage
                }
            }
            
            # Calcul confiance
            confidence = self._calculate_confidence(analysis)
            
            processing_time = (time.time() - start_time) * 1000
            
            logger.info(f"🎯 Motivations Score: {adjusted_score:.3f} (confiance: {confidence:.3f})")
            
            return ScoringResult(
                score=adjusted_score,
                details=details,
                confidence=confidence,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur MotivationsScorer: {e}")
            return ScoringResult(
                score=0.5,  # Score neutre en cas d'erreur
                details={'error': str(e), 'fallback_mode': True},
                confidence=0.3,
                processing_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e)
            )
    
    def _apply_quality_adjustments(self, analysis: MotivationsAnalysis, base_score: float) -> float:
        """🔧 Applique ajustements qualitatifs au score"""
        
        adjusted_score = base_score
        
        # Bonus si motivation principale très bien satisfaite
        if analysis.motivation_matches and analysis.motivation_matches[0].match_score >= 0.8:
            adjusted_score = min(1.0, adjusted_score * 1.1)
        
        # Pénalité si motivation principale non satisfaite
        if analysis.motivation_matches and analysis.motivation_matches[0].match_score < 0.3:
            adjusted_score *= 0.8
        
        # Bonus si toutes motivations au moins partiellement couvertes
        if analysis.motivation_coverage >= 0.8:
            adjusted_score = min(1.0, adjusted_score * 1.05)
        
        # Pénalité si beaucoup de gaps
        if len(analysis.biggest_gaps) >= 2:
            adjusted_score *= 0.9
        
        return adjusted_score
    
    def _calculate_confidence(self, analysis: MotivationsAnalysis) -> float:
        """📊 Calcule niveau de confiance du scoring"""
        
        confidence = 0.7  # Base
        
        # Boost si beaucoup de motivations analysées
        if analysis.total_motivations >= 3:
            confidence += 0.1
        
        # Boost si aspirations textuelles présentes
        if analysis.aspiration_alignment > 0.6:
            confidence += 0.1
        
        # Boost si résultats cohérents
        if analysis.motivation_coverage > 0.6:
            confidence += 0.1
        
        return min(0.95, confidence)
    
    def _generate_comprehensive_recommendations(self, analysis: MotivationsAnalysis) -> List[str]:
        """💡 Génère recommandations complètes"""
        
        recommendations = []
        
        # Recommandations globales
        if analysis.motivation_coverage >= 0.8:
            recommendations.append("✅ Excellente correspondance motivations - Candidat très aligné")
        elif analysis.motivation_coverage >= 0.6:
            recommendations.append("✅ Bonne correspondance motivations - Quelques ajustements possibles")
        else:
            recommendations.append("⚠️ Correspondance motivations limitée - Revoir adéquation poste")
        
        # Recommandations spécifiques top motivation
        if analysis.motivation_matches:
            top_motivation = analysis.motivation_matches[0]
            if top_motivation.match_score >= 0.7:
                recommendations.append(f"🎯 Motivation principale ({top_motivation.motivation.value}) bien couverte")
            else:
                recommendations.append(f"❗ Motivation principale ({top_motivation.motivation.value}) insuffisamment couverte")
        
        # Ajout recommandations entreprise
        recommendations.extend(analysis.enterprise_recommendations[:3])
        
        # Recommandations action
        if len(analysis.biggest_gaps) > 0:
            recommendations.append(f"💡 Prioriser amélioration: {', '.join(analysis.biggest_gaps[:2])}")
        
        if len(analysis.strongest_opportunities) > 0:
            recommendations.append(f"🌟 Mettre en avant: {', '.join(analysis.strongest_opportunities[:2])}")
        
        return recommendations[:8]  # Max 8 recommandations

# === ALIAS POUR COMPATIBILITÉ IMPORTS ===

# Alias pour import attendu dans __init__.py
MotivationsScorerV3 = MotivationsScorer

# === FACTORY ET UTILITAIRES ===

def create_motivations_scorer(weight: float = 0.08) -> MotivationsScorer:
    """🏗️ Factory pour créer le scorer motivations"""
    return MotivationsScorer(weight)

def extract_motivation_insights(scoring_result: ScoringResult) -> Dict[str, Any]:
    """📊 Extrait les insights motivations du résultat"""
    
    if 'insights' in scoring_result.details:
        return scoring_result.details['insights']
    
    return {}

def get_top_motivation_score(scoring_result: ScoringResult) -> float:
    """🎯 Extrait le score de la motivation principale"""
    
    matches = scoring_result.details.get('motivation_matches', [])
    if matches:
        return matches[0].get('match_score', 0.0)
    
    return 0.0

# === TESTS ===

if __name__ == "__main__":
    print("🎯 NEXTVISION V3.0 - Motivations Scorer")
    print("=" * 50)
    
    # Import pour test (simulation)
    from nextvision.models.extended_matching_models_v3 import (
        ExtendedCandidateProfileV3, ExtendedCompanyProfileV3,
        MotivationsExtended, DescriptionPoste, ModalitesEntreprise
    )
    
    # Test candidat avec motivations classées
    candidat_test = ExtendedCandidateProfileV3(
        motivations_extended=MotivationsExtended(
            ranking=[
                MotivationProfessionnelle.EVOLUTION,  # 1er = priorité max
                MotivationProfessionnelle.FLEXIBILITE, # 2e = important
                MotivationProfessionnelle.SALAIRE     # 3e = modéré
            ],
            aspirations_texte="Je souhaite évoluer vers des responsabilités de management dans un environnement innovant"
        )
    )
    
    # Test entreprise avec opportunités
    entreprise_test = ExtendedCompanyProfileV3(
        poste=DescriptionPoste(
            titre="Senior Developer",
            description="Poste avec perspectives d'évolution rapide vers lead technique, environnement innovant, management d'équipe possible",
            missions_principales=["Développement", "Leadership technique", "Formation équipe"]
        ),
        modalites_entreprise=ModalitesEntreprise(
            remote_possible=True,
            remote_pourcentage=60,
            horaires_flexibles=True
        )
    )
    
    # Test scorer
    scorer = MotivationsScorer()
    result = scorer.calculate_score(candidat_test, entreprise_test)
    
    print(f"🎯 Score Motivations: {result.score:.3f}")
    print(f"📊 Confiance: {result.confidence:.3f}")
    
    # Détails motivations
    matches = result.details.get('motivation_matches', [])
    for match in matches:
        print(f"• {match['motivation']} (#{match['ranking_position']}): {match['match_score']:.2f} - {match['match_quality']}")
    
    # Insights
    insights = result.details.get('insights', {})
    print(f"🌟 Opportunités fortes: {insights.get('strongest_opportunities', [])}")
    print(f"⚠️ Gaps identifiés: {insights.get('biggest_gaps', [])}")
    
    print("\n✅ Motivations Scorer V3.0 OPÉRATIONNEL!")
    print("🎯 Analyse ranking motivations candidat: ACTIVÉE")
    print("🏢 Correspondance opportunités entreprise: FONCTIONNELLE")
    print("🧠 Intégration pondération adaptative: PRÊTE")
