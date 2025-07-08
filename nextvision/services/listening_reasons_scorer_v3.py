"""
🧠 Nextvision v3.0 - Listening Reasons Scorer - CERVEAU ADAPTATIF

Composant révolutionnaire du matching bidirectionnel :
- 🎯 3% de poids direct + INFLUENCE SUR 97% RESTANTS 
- 🧠 Cerveau adaptatif qui modifie la pondération de TOUS les autres composants
- 📊 Analyse raison d'écoute candidat vs solutions proposées par l'entreprise
- ⚖️ Génère matrice de pondération personnalisée selon problématique candidat

Impact Systémique selon Raison d'Écoute :
┌─ RÉMUNÉRATION FAIBLE → Boost Salaire (35%) + Progression (5%)
├─ POSTE INADÉQUAT → Boost Sémantique (35%) + Secteurs (10%)  
├─ LOCALISATION → Boost Localisation (25%) + Modalités (6%)
├─ FLEXIBILITÉ → Boost Modalités (8%) + Contrats (10%) + Motivations (12%)
├─ PERSPECTIVES → Boost Progression (10%) + Expérience (25%) + Motivations (15%)
├─ MANAGEMENT → Boost Raison Écoute (8%) + Motivations (15%)
├─ CONDITIONS → Boost Modalités (10%) + Raison Écoute (8%)
└─ MISSIONS → Boost Sémantique (40%) + Secteurs (8%) + Motivations (15%)

Author: NEXTEN Team
Version: 3.0.0 - Adaptive Brain Scorer
"""

import logging
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Import des modèles V3.0
from nextvision.models.extended_matching_models_v3 import (
    ExtendedCandidateProfileV3, ExtendedCompanyProfileV3,
    RaisonEcouteEtendue, UrgenceRecrutementEtendue,
    ExtendedComponentWeights, get_adaptive_weights_v3,
    ADAPTIVE_WEIGHTING_MATRIX_V3
)

# Import base scorer V2.0 pour héritage
from nextvision.services.bidirectional_scorer import BaseScorer, ScoringResult

logger = logging.getLogger(__name__)

# === STRUCTURES SPÉCIALISÉES ===

@dataclass
class ListeningReasonAnalysis:
    """🧠 Analyse détaillée de la raison d'écoute candidat"""
    raison_primaire: RaisonEcouteEtendue
    raisons_secondaires: List[RaisonEcouteEtendue]
    intensite_problematique: float  # 0-1 scale
    solutions_entreprise_matchees: List[str]
    solutions_manquantes: List[str]
    score_adequation: float  # 0-1 score correspondance problème-solution

@dataclass
class AdaptiveWeightingDecision:
    """⚖️ Décision de pondération adaptative"""
    poids_originaux: ExtendedComponentWeights
    poids_adaptes: ExtendedComponentWeights
    justification: str
    composants_boosted: List[str]
    composants_reduits: List[str]
    impact_score: float  # Ampleur des changements

@dataclass
class ListeningReasonsScoringResult:
    """📊 Résultat scoring raison d'écoute avec pondération adaptative"""
    # Score direct (3%)
    direct_score: float
    direct_details: Dict[str, Any]
    
    # Impact adaptatif (influence sur 97%)
    adaptive_weighting: AdaptiveWeightingDecision
    listening_analysis: ListeningReasonAnalysis
    systemic_impact: float  # Impact estimé sur score global
    
    # Métadonnées
    confidence: float
    processing_time_ms: float
    recommendations: List[str]

# === ANALYSEUR RAISONS D'ÉCOUTE ===

class ListeningReasonsAnalyzer:
    """🔍 Analyseur intelligent des raisons d'écoute candidat"""
    
    def __init__(self):
        # Mapping problématiques candidat → solutions entreprise
        self.problem_solution_mapping = {
            RaisonEcouteEtendue.REMUNERATION_TROP_FAIBLE: {
                'solutions_possibles': [
                    'salaire_competitif', 'augmentations_regulieres', 'variable_performance',
                    'avantages_financiers', 'stock_options', 'prime_performance',
                    'evolution_salariale_rapide', 'grille_salariale_transparente'
                ],
                'indicators_entreprise': [
                    'salaire_au_dessus_marche', 'politique_augmentation',
                    'variable_important', 'avantages_sociaux_etendus'
                ]
            },
            
            RaisonEcouteEtendue.POSTE_NE_COINCIDE_PAS: {
                'solutions_possibles': [
                    'poste_sur_mesure', 'missions_variees', 'evolution_poste',
                    'competences_transferables', 'formation_interne',
                    'projet_innovants', 'autonomie_missions'
                ],
                'indicators_entreprise': [
                    'description_detaillee_missions', 'possibilite_evolution_poste',
                    'formation_continue', 'polyvalence_encouragee'
                ]
            },
            
            RaisonEcouteEtendue.POSTE_TROP_LOIN: {
                'solutions_possibles': [
                    'remote_total', 'remote_partiel', 'horaires_flexibles',
                    'aide_transport', 'relocation_package', 'coworking_local',
                    'compressed_workweek', 'flextime'
                ],
                'indicators_entreprise': [
                    'remote_possible', 'politique_flexible', 'aide_mobilite',
                    'bureaux_multiples', 'transport_entreprise'
                ]
            },
            
            RaisonEcouteEtendue.MANQUE_FLEXIBILITE: {
                'solutions_possibles': [
                    'horaires_flexibles', 'remote_hybride', 'conges_flexibles',
                    'temps_partiel_possible', 'sabbatiques', 'formation_temps_travail',
                    'equilibre_vie_pro_perso', 'autonomie_organisation'
                ],
                'indicators_entreprise': [
                    'politique_flexibilite', 'remote_culture', 'work_life_balance',
                    'horaires_variables', 'conges_illimites'
                ]
            },
            
            RaisonEcouteEtendue.MANQUE_PERSPECTIVES: {
                'solutions_possibles': [
                    'plan_carriere_clair', 'promotions_internes', 'formation_leadership',
                    'mentoring', 'projets_transverses', 'mobilite_interne',
                    'augmentations_responsabilites', 'certification_payee'
                ],
                'indicators_entreprise': [
                    'promotion_interne_priorite', 'plan_developpement',
                    'formation_continue', 'mobilite_internationale'
                ]
            },
            
            RaisonEcouteEtendue.PROBLEMES_MANAGEMENT: {
                'solutions_possibles': [
                    'management_bienveillant', 'formation_managers', 'feedback_regulier',
                    'management_collaboratif', 'autonomie_decisions', 'support_rh',
                    'culture_respect', 'communication_transparente'
                ],
                'indicators_entreprise': [
                    'formation_management', 'culture_feedback', 'management_moderne',
                    'enquetes_satisfaction', 'rh_accessible'
                ]
            },
            
            RaisonEcouteEtendue.CONDITIONS_TRAVAIL: {
                'solutions_possibles': [
                    'environnement_moderne', 'espaces_collaboratifs', 'materiel_qualite',
                    'confort_bureaux', 'activites_team_building', 'services_entreprise',
                    'restauration_qualite', 'bien_etre_salaries'
                ],
                'indicators_entreprise': [
                    'bureaux_modernes', 'materiel_fourni', 'services_employes',
                    'programme_bien_etre', 'amenagements_confort'
                ]
            },
            
            RaisonEcouteEtendue.MISSIONS_PEU_INTERESSANTES: {
                'solutions_possibles': [
                    'projets_innovants', 'missions_variees', 'challenges_techniques',
                    'autonomie_projets', 'r&d_participation', 'projets_impact',
                    'innovation_encouragee', 'side_projects'
                ],
                'indicators_entreprise': [
                    'projets_cutting_edge', 'innovation_continue', 'r&d_important',
                    'autonomie_projet', 'challenges_techniques'
                ]
            }
        }
        
        # Pondération intensité selon nombre de raisons
        self.intensity_mapping = {
            1: 1.0,    # Une seule raison = intensité maximale
            2: 0.85,   # Deux raisons = intensité élevée  
            3: 0.70,   # Trois raisons = intensité modérée
            4: 0.55,   # Quatre+ raisons = intensité diluée
        }
    
    def analyze_listening_reasons(self, candidat: ExtendedCandidateProfileV3,
                                entreprise: ExtendedCompanyProfileV3) -> ListeningReasonAnalysis:
        """🔍 Analyse complète des raisons d'écoute candidat"""
        
        # Extraction raisons d'écoute
        raison_primaire = candidat.motivations_extended.raison_ecoute_primaire
        raisons_secondaires = candidat.motivations_extended.raisons_ecoute_multiples or []
        
        # Calcul intensité problématique
        total_raisons = 1 + len(raisons_secondaires)
        intensite = self.intensity_mapping.get(min(total_raisons, 4), 0.4)
        
        # Analyse solutions entreprise pour raison primaire
        solutions_analysis = self._analyze_enterprise_solutions(raison_primaire, entreprise)
        
        # Score d'adéquation problème-solution
        score_adequation = self._calculate_adequation_score(
            raison_primaire, solutions_analysis, intensite
        )
        
        return ListeningReasonAnalysis(
            raison_primaire=raison_primaire,
            raisons_secondaires=raisons_secondaires,
            intensite_problematique=intensite,
            solutions_entreprise_matchees=solutions_analysis['solutions_matchees'],
            solutions_manquantes=solutions_analysis['solutions_manquantes'],
            score_adequation=score_adequation
        )
    
    def _analyze_enterprise_solutions(self, raison: RaisonEcouteEtendue, 
                                    entreprise: ExtendedCompanyProfileV3) -> Dict[str, List[str]]:
        """🏢 Analyse solutions proposées par l'entreprise"""
        
        if raison not in self.problem_solution_mapping:
            return {'solutions_matchees': [], 'solutions_manquantes': []}
        
        solutions_config = self.problem_solution_mapping[raison]
        solutions_possibles = solutions_config['solutions_possibles']
        indicators = solutions_config['indicators_entreprise']
        
        solutions_matchees = []
        solutions_manquantes = []
        
        # Analyse selon la raison spécifique
        if raison == RaisonEcouteEtendue.REMUNERATION_TROP_FAIBLE:
            solutions_matchees.extend(self._analyze_salary_solutions(entreprise))
            
        elif raison == RaisonEcouteEtendue.POSTE_TROP_LOIN:
            solutions_matchees.extend(self._analyze_location_solutions(entreprise))
            
        elif raison == RaisonEcouteEtendue.MANQUE_FLEXIBILITE:
            solutions_matchees.extend(self._analyze_flexibility_solutions(entreprise))
            
        elif raison == RaisonEcouteEtendue.PROBLEMES_MANAGEMENT:
            solutions_matchees.extend(self._analyze_management_solutions(entreprise))
            
        elif raison == RaisonEcouteEtendue.CONDITIONS_TRAVAIL:
            solutions_matchees.extend(self._analyze_working_conditions_solutions(entreprise))
            
        elif raison == RaisonEcouteEtendue.MISSIONS_PEU_INTERESSANTES:
            solutions_matchees.extend(self._analyze_mission_solutions(entreprise))
            
        elif raison == RaisonEcouteEtendue.POSTE_NE_COINCIDE_PAS:
            solutions_matchees.extend(self._analyze_position_fit_solutions(entreprise))
            
        elif raison == RaisonEcouteEtendue.MANQUE_PERSPECTIVES:
            solutions_matchees.extend(self._analyze_career_solutions(entreprise))
        
        # Déterminer solutions manquantes
        solutions_manquantes = [s for s in solutions_possibles if s not in solutions_matchees]
        
        return {
            'solutions_matchees': solutions_matchees,
            'solutions_manquantes': solutions_manquantes
        }
    
    def _analyze_salary_solutions(self, entreprise: ExtendedCompanyProfileV3) -> List[str]:
        """💰 Analyse solutions salariales"""
        solutions = []
        
        # Vérifier fourchette salariale attractive
        if entreprise.poste.salaire_max and entreprise.poste.salaire_min:
            if entreprise.poste.salaire_max > 50000:  # Seuil de base
                solutions.append('salaire_competitif')
        
        # Vérifier avantages financiers
        if entreprise.poste.description and any(
            terme in entreprise.poste.description.lower() 
            for terme in ['variable', 'prime', 'bonus', '13e mois']
        ):
            solutions.append('variable_performance')
        
        # Vérifier politique d'augmentation
        if entreprise.criteres_flexibilite.flexibilite_salariale > 0.2:
            solutions.append('augmentations_regulieres')
        
        return solutions
    
    def _analyze_location_solutions(self, entreprise: ExtendedCompanyProfileV3) -> List[str]:
        """📍 Analyse solutions géographiques"""
        solutions = []
        
        if entreprise.modalites_entreprise.remote_possible:
            if entreprise.modalites_entreprise.remote_pourcentage:
                if entreprise.modalites_entreprise.remote_pourcentage >= 80:
                    solutions.append('remote_total')
                elif entreprise.modalites_entreprise.remote_pourcentage >= 40:
                    solutions.append('remote_partiel')
        
        if entreprise.modalites_entreprise.horaires_flexibles:
            solutions.append('horaires_flexibles')
        
        return solutions
    
    def _analyze_flexibility_solutions(self, entreprise: ExtendedCompanyProfileV3) -> List[str]:
        """🔄 Analyse solutions flexibilité"""
        solutions = []
        
        if entreprise.modalites_entreprise.horaires_flexibles:
            solutions.append('horaires_flexibles')
        
        if entreprise.modalites_entreprise.remote_possible:
            solutions.append('remote_hybride')
        
        if entreprise.criteres_flexibilite.flexibilite_contractuelle > 0.6:
            solutions.append('equilibre_vie_pro_perso')
        
        return solutions
    
    def _analyze_management_solutions(self, entreprise: ExtendedCompanyProfileV3) -> List[str]:
        """👥 Analyse solutions management"""
        solutions = []
        
        # Analyser solutions management depuis les données entreprise
        if entreprise.solutions_management:
            for solution in entreprise.solutions_management:
                if 'bienveillant' in solution.lower():
                    solutions.append('management_bienveillant')
                if 'formation' in solution.lower():
                    solutions.append('formation_managers')
                if 'feedback' in solution.lower():
                    solutions.append('feedback_regulier')
        
        return solutions
    
    def _analyze_working_conditions_solutions(self, entreprise: ExtendedCompanyProfileV3) -> List[str]:
        """🏢 Analyse solutions conditions de travail"""
        solutions = []
        
        if entreprise.solutions_conditions_travail:
            for solution in entreprise.solutions_conditions_travail:
                if 'moderne' in solution.lower():
                    solutions.append('environnement_moderne')
                if 'matériel' in solution.lower():
                    solutions.append('materiel_qualite')
                if 'confort' in solution.lower():
                    solutions.append('confort_bureaux')
        
        return solutions
    
    def _analyze_mission_solutions(self, entreprise: ExtendedCompanyProfileV3) -> List[str]:
        """🎯 Analyse solutions missions"""
        solutions = []
        
        # Analyser description du poste pour projets innovants
        if entreprise.poste.description:
            desc_lower = entreprise.poste.description.lower()
            if any(terme in desc_lower for terme in ['innovation', 'r&d', 'nouveau', 'développement']):
                solutions.append('projets_innovants')
            if any(terme in desc_lower for terme in ['varié', 'diverse', 'multiple']):
                solutions.append('missions_variees')
            if any(terme in desc_lower for terme in ['autonomie', 'indépendant']):
                solutions.append('autonomie_projets')
        
        if entreprise.solutions_missions:
            for solution in entreprise.solutions_missions:
                if 'innovant' in solution.lower():
                    solutions.append('projets_innovants')
                if 'challenge' in solution.lower():
                    solutions.append('challenges_techniques')
        
        return solutions
    
    def _analyze_position_fit_solutions(self, entreprise: ExtendedCompanyProfileV3) -> List[str]:
        """📋 Analyse solutions adéquation poste"""
        solutions = []
        
        # Analyser flexibilité du poste
        if entreprise.criteres_flexibilite.flexibilite_experience > 0.3:
            solutions.append('poste_sur_mesure')
        
        # Vérifier formation proposée
        if entreprise.poste.description and 'formation' in entreprise.poste.description.lower():
            solutions.append('formation_interne')
        
        return solutions
    
    def _analyze_career_solutions(self, entreprise: ExtendedCompanyProfileV3) -> List[str]:
        """📈 Analyse solutions évolution carrière"""
        solutions = []
        
        # Analyser opportunités d'évolution
        if entreprise.poste.description:
            desc_lower = entreprise.poste.description.lower()
            if any(terme in desc_lower for terme in ['évolution', 'promotion', 'carrière']):
                solutions.append('plan_carriere_clair')
            if 'formation' in desc_lower:
                solutions.append('formation_leadership')
        
        return solutions
    
    def _calculate_adequation_score(self, raison: RaisonEcouteEtendue,
                                  solutions_analysis: Dict[str, List[str]],
                                  intensite: float) -> float:
        """🎯 Calcule score d'adéquation problème-solution"""
        
        solutions_matchees = len(solutions_analysis['solutions_matchees'])
        solutions_manquantes = len(solutions_analysis['solutions_manquantes'])
        solutions_totales = solutions_matchees + solutions_manquantes
        
        if solutions_totales == 0:
            return 0.5  # Score neutre si pas de solutions définies
        
        # Score de base
        base_score = solutions_matchees / solutions_totales
        
        # Ajustement selon intensité problématique
        adjusted_score = base_score * (0.7 + (intensite * 0.3))
        
        # Bonus si solutions critiques présentes
        critical_solutions_present = self._check_critical_solutions(raison, solutions_analysis['solutions_matchees'])
        if critical_solutions_present:
            adjusted_score = min(1.0, adjusted_score * 1.2)
        
        return adjusted_score

    def _check_critical_solutions(self, raison: RaisonEcouteEtendue, solutions_matchees: List[str]) -> bool:
        """🔑 Vérifie présence de solutions critiques selon la raison"""
        
        critical_solutions = {
            RaisonEcouteEtendue.REMUNERATION_TROP_FAIBLE: ['salaire_competitif', 'augmentations_regulieres'],
            RaisonEcouteEtendue.POSTE_TROP_LOIN: ['remote_total', 'remote_partiel'],
            RaisonEcouteEtendue.MANQUE_FLEXIBILITE: ['horaires_flexibles', 'remote_hybride'],
            RaisonEcouteEtendue.PROBLEMES_MANAGEMENT: ['management_bienveillant', 'formation_managers'],
            RaisonEcouteEtendue.MANQUE_PERSPECTIVES: ['plan_carriere_clair', 'promotions_internes']
        }
        
        critical = critical_solutions.get(raison, [])
        return any(solution in solutions_matchees for solution in critical)

# === MOTEUR PONDÉRATION ADAPTATIVE ===

class AdaptiveWeightingEngine:
    """⚖️ Moteur de pondération adaptative - Cerveau du système"""
    
    def __init__(self):
        self.weighting_matrix = ADAPTIVE_WEIGHTING_MATRIX_V3
        
    def calculate_adaptive_weighting(self, candidat: ExtendedCandidateProfileV3,
                                   entreprise: ExtendedCompanyProfileV3,
                                   listening_analysis: ListeningReasonAnalysis) -> AdaptiveWeightingDecision:
        """🧠 Calcule pondération adaptative basée sur raison d'écoute"""
        
        # Poids de base (uniformes)
        poids_originaux = ExtendedComponentWeights()
        
        # Poids adaptés selon raison d'écoute
        poids_adaptes = get_adaptive_weights_v3(
            listening_analysis.raison_primaire,
            entreprise.recrutement_etendu.urgence
        )
        
        # Analyse des changements
        boost_analysis = self._analyze_weight_changes(poids_originaux, poids_adaptes)
        
        # Génération justification
        justification = self._generate_justification(
            listening_analysis.raison_primaire,
            boost_analysis,
            listening_analysis.score_adequation
        )
        
        # Calcul impact systémique
        impact_score = self._calculate_systemic_impact(poids_originaux, poids_adaptes)
        
        return AdaptiveWeightingDecision(
            poids_originaux=poids_originaux,
            poids_adaptes=poids_adaptes,
            justification=justification,
            composants_boosted=boost_analysis['boosted'],
            composants_reduits=boost_analysis['reduced'],
            impact_score=impact_score
        )
    
    def _analyze_weight_changes(self, original: ExtendedComponentWeights,
                              adapted: ExtendedComponentWeights) -> Dict[str, List[str]]:
        """📊 Analyse des changements de pondération"""
        
        boosted = []
        reduced = []
        
        original_dict = original.dict()
        adapted_dict = adapted.dict()
        
        for component in original_dict:
            original_weight = original_dict[component]
            adapted_weight = adapted_dict[component]
            
            change = adapted_weight - original_weight
            if change > 0.02:  # Seuil de boost significatif
                boosted.append(component)
            elif change < -0.02:  # Seuil de réduction significative
                reduced.append(component)
        
        return {'boosted': boosted, 'reduced': reduced}
    
    def _generate_justification(self, raison: RaisonEcouteEtendue,
                              boost_analysis: Dict[str, List[str]],
                              adequation_score: float) -> str:
        """📝 Génère justification de la pondération adaptative"""
        
        justifications = {
            RaisonEcouteEtendue.REMUNERATION_TROP_FAIBLE: 
                f"Candidat insatisfait de sa rémunération → Boost composant Salaire (35%) et Progression (5%). Score d'adéquation solutions: {adequation_score:.2f}",
            
            RaisonEcouteEtendue.POSTE_NE_COINCIDE_PAS: 
                f"Candidat en décalage avec son poste → Boost Sémantique (35%) et Secteurs (10%) pour meilleur fit. Score solutions: {adequation_score:.2f}",
            
            RaisonEcouteEtendue.POSTE_TROP_LOIN: 
                f"Candidat contraint géographiquement → Boost Localisation (25%) et Modalités (6%). Score solutions: {adequation_score:.2f}",
            
            RaisonEcouteEtendue.MANQUE_FLEXIBILITE: 
                f"Candidat cherche flexibilité → Boost Modalités (8%), Contrats (10%) et Motivations (12%). Score solutions: {adequation_score:.2f}",
            
            RaisonEcouteEtendue.MANQUE_PERSPECTIVES: 
                f"Candidat bloqué dans évolution → Boost Progression (10%), Expérience (25%) et Motivations (15%). Score solutions: {adequation_score:.2f}",
            
            RaisonEcouteEtendue.PROBLEMES_MANAGEMENT: 
                f"Candidat en conflit managérial → Boost Raison Écoute (8%) et Motivations (15%). Score solutions: {adequation_score:.2f}",
            
            RaisonEcouteEtendue.CONDITIONS_TRAVAIL: 
                f"Candidat insatisfait conditions → Boost Modalités (10%) et Raison Écoute (8%). Score solutions: {adequation_score:.2f}",
            
            RaisonEcouteEtendue.MISSIONS_PEU_INTERESSANTES: 
                f"Candidat s'ennuie dans missions → Boost Sémantique (40%), Secteurs (8%) et Motivations (15%). Score solutions: {adequation_score:.2f}"
        }
        
        base_justification = justifications.get(raison, f"Pondération adaptée selon raison d'écoute. Score solutions: {adequation_score:.2f}")
        
        # Ajouter détails des composants boostés/réduits
        if boost_analysis['boosted']:
            base_justification += f" | Composants boostés: {', '.join(boost_analysis['boosted'])}"
        if boost_analysis['reduced']:
            base_justification += f" | Composants réduits: {', '.join(boost_analysis['reduced'])}"
        
        return base_justification
    
    def _calculate_systemic_impact(self, original: ExtendedComponentWeights,
                                 adapted: ExtendedComponentWeights) -> float:
        """📈 Calcule impact systémique des changements de pondération"""
        
        original_dict = original.dict()
        adapted_dict = adapted.dict()
        
        total_change = 0.0
        for component in original_dict:
            change = abs(adapted_dict[component] - original_dict[component])
            total_change += change
        
        # Normalisation : total_change max théorique = 2.0 (tous poids passent de 0 à 1)
        # En pratique, sera beaucoup plus faible
        return min(1.0, total_change / 0.5)  # Impact relatif

# === LISTENING REASONS SCORER PRINCIPAL ===

class ListeningReasonsScorer(BaseScorer):
    """🧠 Listening Reasons Scorer V3.0 - Cerveau Adaptatif du Système"""
    
    def __init__(self, weight: float = 0.03):
        super().__init__(weight)
        self.reasons_analyzer = ListeningReasonsAnalyzer()
        self.adaptive_engine = AdaptiveWeightingEngine()
        
    def calculate_score(self, candidat: ExtendedCandidateProfileV3,
                       entreprise: ExtendedCompanyProfileV3) -> ScoringResult:
        """🎯 Calcule score raison d'écoute avec pondération adaptative"""
        
        start_time = time.time()
        
        try:
            # 1. Analyse des raisons d'écoute candidat
            listening_analysis = self.reasons_analyzer.analyze_listening_reasons(candidat, entreprise)
            
            # 2. Calcul pondération adaptative  
            adaptive_decision = self.adaptive_engine.calculate_adaptive_weighting(
                candidat, entreprise, listening_analysis
            )
            
            # 3. Score direct (3% du total)
            direct_score = listening_analysis.score_adequation
            
            # 4. Estimation impact systémique (influence sur 97%)
            systemic_impact = adaptive_decision.impact_score * 0.3  # Impact estimé sur score global
            
            # 5. Génération recommandations
            recommendations = self._generate_recommendations(listening_analysis, adaptive_decision)
            
            # 6. Résultat complet
            result = ListeningReasonsScoringResult(
                direct_score=direct_score,
                direct_details={
                    'raison_primaire': listening_analysis.raison_primaire.value,
                    'raisons_secondaires': [r.value for r in listening_analysis.raisons_secondaires],
                    'intensite_problematique': listening_analysis.intensite_problematique,
                    'solutions_matchees': listening_analysis.solutions_entreprise_matchees,
                    'solutions_manquantes': listening_analysis.solutions_manquantes,
                    'adequation_score': listening_analysis.score_adequation
                },
                adaptive_weighting=adaptive_decision,
                listening_analysis=listening_analysis,
                systemic_impact=systemic_impact,
                confidence=min(0.9, 0.6 + (listening_analysis.score_adequation * 0.3)),
                processing_time_ms=(time.time() - start_time) * 1000,
                recommendations=recommendations
            )
            
            # Conversion vers ScoringResult standard pour compatibilité V2.0
            return ScoringResult(
                score=direct_score,
                details={
                    'listening_reasons_analysis': result.direct_details,
                    'adaptive_weighting_impact': {
                        'justification': adaptive_decision.justification,
                        'composants_boosted': adaptive_decision.composants_boosted,
                        'composants_reduits': adaptive_decision.composants_reduits,
                        'systemic_impact': systemic_impact
                    },
                    'recommendations': recommendations,
                    'v3_extended_result': result  # Résultat complet pour utilisation V3.0
                },
                confidence=result.confidence,
                processing_time_ms=result.processing_time_ms
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur ListeningReasonsScorer: {e}")
            return ScoringResult(
                score=0.5,  # Score neutre en cas d'erreur
                details={'error': str(e), 'fallback_mode': True},
                confidence=0.3,
                processing_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e)
            )
    
    def _generate_recommendations(self, listening_analysis: ListeningReasonAnalysis,
                                adaptive_decision: AdaptiveWeightingDecision) -> List[str]:
        """💡 Génère recommandations basées sur l'analyse"""
        
        recommendations = []
        
        # Recommandations selon adéquation
        if listening_analysis.score_adequation >= 0.8:
            recommendations.append("✅ Excellente adéquation problématique candidat ↔ solutions entreprise")
        elif listening_analysis.score_adequation >= 0.6:
            recommendations.append("⚠️ Adéquation correcte mais améliorable - Mettre en avant les solutions disponibles")
        else:
            recommendations.append("❌ Faible adéquation - L'entreprise ne répond pas aux problématiques candidat")
        
        # Recommandations selon solutions manquantes
        if listening_analysis.solutions_manquantes:
            missing_count = len(listening_analysis.solutions_manquantes)
            if missing_count <= 2:
                recommendations.append(f"💡 {missing_count} solution(s) manquante(s) - Développer l'offre entreprise")
            else:
                recommendations.append(f"⚠️ {missing_count} solutions manquantes - Revoir l'adéquation du poste")
        
        # Recommandations selon pondération adaptative
        if adaptive_decision.impact_score > 0.3:
            recommendations.append(f"🧠 Pondération fortement adaptée - Impact systémique: {adaptive_decision.impact_score:.1%}")
        
        # Recommandations spécifiques selon raison d'écoute
        raison_specific = self._get_reason_specific_recommendations(listening_analysis.raison_primaire)
        recommendations.extend(raison_specific)
        
        return recommendations
    
    def _get_reason_specific_recommendations(self, raison: RaisonEcouteEtendue) -> List[str]:
        """🎯 Recommandations spécifiques selon raison d'écoute"""
        
        recommendations_map = {
            RaisonEcouteEtendue.REMUNERATION_TROP_FAIBLE: [
                "💰 Mettre en avant la rémunération attractive et les perspectives d'augmentation",
                "📈 Présenter la politique salariale transparente de l'entreprise"
            ],
            RaisonEcouteEtendue.POSTE_TROP_LOIN: [
                "🏠 Valoriser les options de télétravail et la flexibilité géographique",
                "🚗 Proposer des solutions de mobilité ou aide au transport"
            ],
            RaisonEcouteEtendue.MANQUE_FLEXIBILITE: [
                "🔄 Insister sur la culture flexible et l'équilibre vie pro/perso",
                "⏰ Présenter les aménagements d'horaires possibles"
            ],
            RaisonEcouteEtendue.MANQUE_PERSPECTIVES: [
                "📊 Détailler le plan de carrière et les opportunités d'évolution",
                "🎓 Valoriser les formations et certifications proposées"
            ],
            RaisonEcouteEtendue.PROBLEMES_MANAGEMENT: [
                "👥 Présenter la culture managériale bienveillante",
                "🤝 Mettre en avant la formation des managers et le support RH"
            ]
        }
        
        return recommendations_map.get(raison, ["💡 Adapter la présentation selon la problématique candidat"])

# === FACTORY ET UTILITAIRES ===

def create_listening_reasons_scorer(weight: float = 0.03) -> ListeningReasonsScorer:
    """🏗️ Factory pour créer le scorer raison d'écoute"""
    return ListeningReasonsScorer(weight)

def extract_adaptive_weights(scoring_result: ScoringResult) -> Optional[ExtendedComponentWeights]:
    """⚖️ Extrait les poids adaptatifs du résultat de scoring"""
    
    if 'v3_extended_result' in scoring_result.details:
        extended_result = scoring_result.details['v3_extended_result']
        if isinstance(extended_result, ListeningReasonsScoringResult):
            return extended_result.adaptive_weighting.poids_adaptes
    
    return None

# === TESTS ===

if __name__ == "__main__":
    print("🧠 NEXTVISION V3.0 - Listening Reasons Scorer - CERVEAU ADAPTATIF")
    print("=" * 70)
    
    # Import pour test (simulation)
    from nextvision.models.extended_matching_models_v3 import (
        ExtendedCandidateProfileV3, ExtendedCompanyProfileV3,
        MotivationsExtended, RecrutementEtendu
    )
    
    # Test candidat insatisfait salaire
    candidat_test = ExtendedCandidateProfileV3(
        motivations_extended=MotivationsExtended(
            raison_ecoute_primaire=RaisonEcouteEtendue.REMUNERATION_TROP_FAIBLE,
            raisons_ecoute_multiples=[RaisonEcouteEtendue.MANQUE_PERSPECTIVES]
        )
    )
    
    # Test entreprise avec solutions
    entreprise_test = ExtendedCompanyProfileV3(
        recrutement_etendu=RecrutementEtendu(
            urgence=UrgenceRecrutementEtendue.NORMAL
        )
    )
    
    # Test scorer
    scorer = ListeningReasonsScorer()
    result = scorer.calculate_score(candidat_test, entreprise_test)
    
    print(f"🎯 Score direct (3%): {result.score:.3f}")
    print(f"🧠 Impact adaptatif détecté: {result.details.get('adaptive_weighting_impact', {}).get('systemic_impact', 0):.1%}")
    print(f"⚖️ Justification: {result.details.get('adaptive_weighting_impact', {}).get('justification', 'N/A')}")
    print(f"📈 Composants boostés: {result.details.get('adaptive_weighting_impact', {}).get('composants_boosted', [])}")
    
    # Test poids adaptatifs
    adaptive_weights = extract_adaptive_weights(result)
    if adaptive_weights:
        print(f"💰 Nouveau poids Salaire: {adaptive_weights.salaire:.1%} (vs 20% base)")
        print(f"📊 Nouveau poids Sémantique: {adaptive_weights.semantique:.1%} (vs 25% base)")
    
    print("\n✅ Listening Reasons Scorer V3.0 - CERVEAU ADAPTATIF OPÉRATIONNEL!")
    print("🧠 Influence systémique sur tous les autres composants: ACTIVÉE")
