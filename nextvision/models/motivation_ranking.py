"""
🎯 Modèles Motivations Classées NEXTEN
Système avancé de motivation candidat avec pondération et impact matching

Author: NEXTEN Team
Version: 1.0.0
Integration: Commitment- → Nextvision Bridge
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime
from enum import Enum
import math

# Import des énumérations communes
from .questionnaire_advanced import MotivationEnum, PourquoiEcouteEnum

class IntensiteMotivationEnum(str, Enum):
    """🔥 Intensité de motivation"""
    CRITIQUE = "Critique"  # Deal-breaker
    TRES_IMPORTANTE = "Très importante"
    IMPORTANTE = "Importante"
    MODEREE = "Modérée"
    FAIBLE = "Faible"

class CategorieMotivationEnum(str, Enum):
    """📂 Catégories de motivations"""
    FINANCIERE = "Financière"
    PROFESSIONNELLE = "Professionnelle"
    PERSONNELLE = "Personnelle"
    SOCIALE = "Sociale"
    ENVIRONNEMENTALE = "Environnementale"

class ImpactCarriereEnum(str, Enum):
    """🚀 Impact sur la carrière"""
    TRANSFORMATION = "Transformation"
    ACCELERATION = "Accélération"
    CONSOLIDATION = "Consolidation"
    TRANSITION = "Transition"
    MAINTIEN = "Maintien"

class MotivationDetaillee(BaseModel):
    """🎯 Motivation détaillée avec contexte et pondération"""
    
    motivation: MotivationEnum = Field(..., description="Type de motivation")
    intensite: IntensiteMotivationEnum = Field(..., description="Intensité de la motivation")
    priorite: int = Field(..., ge=1, le=20, description="Priorité dans le classement (1=plus important)")
    poids: float = Field(..., ge=0, le=1, description="Poids dans l'évaluation finale")
    
    # Contexte et justification
    description_personnalisee: Optional[str] = Field(None, description="Description personnalisée")
    contexte_actuel: Optional[str] = Field(None, description="Contexte actuel qui motive")
    objectif_vise: Optional[str] = Field(None, description="Objectif visé")
    
    # Critères d'évaluation
    criteres_evaluation: List[str] = Field(default_factory=list, description="Critères pour évaluer cette motivation")
    seuil_satisfaction: Optional[int] = Field(None, ge=0, le=100, description="Seuil de satisfaction (% ou score)")
    
    # Évolution temporelle
    importance_passee: Optional[IntensiteMotivationEnum] = Field(None, description="Importance dans le passé")
    tendance_evolution: Optional[str] = Field(None, description="Tendance d'évolution (stable/croissante/décroissante)")
    impact_carriere_attendu: Optional[ImpactCarriereEnum] = Field(None, description="Impact attendu sur la carrière")
    
    # Négociabilité
    negociable: bool = Field(default=True, description="Cette motivation est-elle négociable")
    alternatives_acceptables: List[str] = Field(default_factory=list, description="Alternatives acceptables")
    conditions_flexibilite: List[str] = Field(default_factory=list, description="Conditions de flexibilité")
    
    @validator('priorite')
    def validate_priorite(cls, v):
        if v < 1 or v > 20:
            raise ValueError('Priorité doit être entre 1 et 20')
        return v
    
    @validator('poids')
    def validate_poids(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Poids doit être entre 0 et 1')
        return v
    
    def calculer_score_impact(self) -> float:
        """💥 Calcule le score d'impact de cette motivation"""
        
        # Score basé sur l'intensité
        intensite_scores = {
            IntensiteMotivationEnum.CRITIQUE: 1.0,
            IntensiteMotivationEnum.TRES_IMPORTANTE: 0.8,
            IntensiteMotivationEnum.IMPORTANTE: 0.6,
            IntensiteMotivationEnum.MODEREE: 0.4,
            IntensiteMotivationEnum.FAIBLE: 0.2
        }
        
        score_base = intensite_scores.get(self.intensite, 0.5)
        
        # Modulation par la priorité (plus la priorité est haute = numéro faible, plus le score augmente)
        bonus_priorite = max(0, (21 - self.priorite) / 20 * 0.2)
        
        # Bonus si non-négociable (motivation ferme)
        bonus_fermete = 0.1 if not self.negociable else 0.0
        
        # Bonus pour spécificité (critères définis)
        bonus_specificite = 0.05 if self.criteres_evaluation else 0.0
        
        score_final = min(1.0, score_base + bonus_priorite + bonus_fermete + bonus_specificite)
        return round(score_final, 3)
    
    def evaluer_adequation_offre(self, caracteristiques_offre: Dict[str, Any]) -> Dict[str, Any]:
        """🎯 Évalue l'adéquation avec une offre spécifique"""
        
        score_adequation = 0.0
        details_evaluation = []
        alertes = []
        
        # Évaluation spécifique par type de motivation
        if self.motivation == MotivationEnum.SALAIRE:
            if 'salaire_propose' in caracteristiques_offre and 'salaire_min_candidat' in caracteristiques_offre:
                salaire_propose = caracteristiques_offre['salaire_propose']
                salaire_min = caracteristiques_offre['salaire_min_candidat']
                
                if salaire_propose >= salaire_min * 1.2:  # +20%
                    score_adequation = 1.0
                    details_evaluation.append("Salaire très attractif (+20% minimum)")
                elif salaire_propose >= salaire_min:
                    score_adequation = 0.7
                    details_evaluation.append("Salaire conforme aux attentes")
                else:
                    score_adequation = 0.3
                    alertes.append(f"Salaire sous les attentes ({salaire_propose} vs {salaire_min})")
        
        elif self.motivation == MotivationEnum.EVOLUTION:
            if 'perspectives_evolution' in caracteristiques_offre:
                if caracteristiques_offre['perspectives_evolution']:
                    score_adequation = 0.8
                    details_evaluation.append("Perspectives d'évolution présentes")
                else:
                    score_adequation = 0.2
                    alertes.append("Pas de perspectives d'évolution mentionnées")
        
        elif self.motivation == MotivationEnum.FLEXIBILITE:
            if 'teletravail_jours' in caracteristiques_offre:
                jours_tt = caracteristiques_offre['teletravail_jours']
                if jours_tt >= 3:
                    score_adequation = 1.0
                    details_evaluation.append(f"Forte flexibilité ({jours_tt}j télétravail)")
                elif jours_tt >= 2:
                    score_adequation = 0.7
                    details_evaluation.append(f"Flexibilité modérée ({jours_tt}j télétravail)")
                else:
                    score_adequation = 0.3
                    alertes.append("Flexibilité limitée")
        
        elif self.motivation == MotivationEnum.APPRENTISSAGE:
            if 'budget_formation' in caracteristiques_offre:
                budget = caracteristiques_offre['budget_formation']
                if budget >= 3000:
                    score_adequation = 1.0
                    details_evaluation.append(f"Excellent budget formation ({budget}€)")
                elif budget >= 1500:
                    score_adequation = 0.7
                    details_evaluation.append(f"Budget formation correct ({budget}€)")
                else:
                    score_adequation = 0.4
                    alertes.append("Budget formation limité")
        
        elif self.motivation == MotivationEnum.AMBIANCE:
            if 'culture_entreprise' in caracteristiques_offre:
                culture = caracteristiques_offre['culture_entreprise']
                if any(keyword in culture.lower() for keyword in ['collaborative', 'bienveillante', 'conviviale']):
                    score_adequation = 0.8
                    details_evaluation.append("Culture d'entreprise alignée")
                else:
                    score_adequation = 0.5
                    details_evaluation.append("Culture d'entreprise à valider")
        
        # Prise en compte de l'intensité de la motivation
        score_final = score_adequation * self.calculer_score_impact()
        
        return {
            "score_adequation": round(score_final, 3),
            "score_adequation_brut": round(score_adequation, 3),
            "score_impact_motivation": self.calculer_score_impact(),
            "details_evaluation": details_evaluation,
            "alertes": alertes,
            "motivation": self.motivation,
            "intensite": self.intensite,
            "negociable": self.negociable
        }
    
    def definir_categorie(self) -> CategorieMotivationEnum:
        """📂 Définit automatiquement la catégorie de motivation"""
        
        categories_mapping = {
            MotivationEnum.SALAIRE: CategorieMotivationEnum.FINANCIERE,
            MotivationEnum.EVOLUTION: CategorieMotivationEnum.PROFESSIONNELLE,
            MotivationEnum.APPRENTISSAGE: CategorieMotivationEnum.PROFESSIONNELLE,
            MotivationEnum.RECONNAISSANCE: CategorieMotivationEnum.PROFESSIONNELLE,
            MotivationEnum.AUTONOMIE: CategorieMotivationEnum.PROFESSIONNELLE,
            MotivationEnum.FLEXIBILITE: CategorieMotivationEnum.PERSONNELLE,
            MotivationEnum.EQUILIBRE_VIE: CategorieMotivationEnum.PERSONNELLE,
            MotivationEnum.AMBIANCE: CategorieMotivationEnum.SOCIALE,
            MotivationEnum.SECURITE: CategorieMotivationEnum.FINANCIERE,
            MotivationEnum.INNOVATION: CategorieMotivationEnum.PROFESSIONNELLE
        }
        
        return categories_mapping.get(self.motivation, CategorieMotivationEnum.PROFESSIONNELLE)
    
    class Config:
        json_schema_extra = {
            "example": {
                "motivation": "Évolution",
                "intensite": "Très importante",
                "priorite": 1,
                "poids": 0.3,
                "description_personnalisee": "Accès à des responsabilités managériales",
                "contexte_actuel": "Bloqué dans le poste actuel sans perspective",
                "objectif_vise": "Devenir lead developer puis manager dans 2-3 ans",
                "criteres_evaluation": ["Possibilité de management", "Formation leadership", "Plan de carrière défini"],
                "seuil_satisfaction": 80,
                "impact_carriere_attendu": "Accélération",
                "negociable": False,
                "alternatives_acceptables": ["Formation managériale", "Responsabilité technique senior"]
            }
        }

class ProfilMotivationnel(BaseModel):
    """🧠 Profil motivationnel complet du candidat"""
    
    motivations_classees: List[MotivationDetaillee] = Field(..., description="Motivations classées par priorité")
    coherence_avec_raison_ecoute: Optional[float] = Field(None, ge=0, le=1, description="Cohérence avec raison d'écoute")
    
    # Analyse par catégories
    repartition_categories: Dict[CategorieMotivationEnum, float] = Field(default_factory=dict, description="Répartition par catégories")
    motivation_dominante_categorie: Optional[CategorieMotivationEnum] = Field(None, description="Catégorie dominante")
    
    # Scores globaux
    score_determination: Optional[float] = Field(None, ge=0, le=1, description="Score de détermination global")
    score_flexibilite_motivations: Optional[float] = Field(None, ge=0, le=1, description="Score de flexibilité motivations")
    stabilite_motivations: Optional[float] = Field(None, ge=0, le=1, description="Stabilité des motivations dans le temps")
    
    # Métadonnées
    date_evaluation: datetime = Field(default_factory=datetime.now, description="Date d'évaluation")
    contexte_evaluation: Optional[str] = Field(None, description="Contexte de l'évaluation")
    
    @validator('motivations_classees')
    def validate_motivations_uniques(cls, v):
        """Valide que chaque motivation n'apparaît qu'une fois"""
        motivations = [m.motivation for m in v]
        if len(motivations) != len(set(motivations)):
            raise ValueError('Chaque motivation ne peut apparaître qu\'une seule fois')
        return v
    
    @validator('motivations_classees')
    def validate_priorites_uniques(cls, v):
        """Valide que chaque priorité n'apparaît qu'une fois"""
        priorites = [m.priorite for m in v]
        if len(priorites) != len(set(priorites)):
            raise ValueError('Chaque priorité doit être unique')
        return v
    
    def normaliser_poids(self) -> 'ProfilMotivationnel':
        """🔄 Normalise les poids pour que la somme = 1"""
        total_poids = sum(m.poids for m in self.motivations_classees)
        if total_poids > 0:
            for motivation in self.motivations_classees:
                motivation.poids = motivation.poids / total_poids
        return self
    
    def analyser_repartition_categories(self) -> Dict[CategorieMotivationEnum, float]:
        """📊 Analyse la répartition par catégories de motivations"""
        
        repartition = {}
        total_poids = sum(m.poids for m in self.motivations_classees)
        
        if total_poids == 0:
            return repartition
        
        for motivation in self.motivations_classees:
            categorie = motivation.definir_categorie()
            if categorie not in repartition:
                repartition[categorie] = 0.0
            repartition[categorie] += motivation.poids
        
        # Normalisation pour obtenir des pourcentages
        for categorie in repartition:
            repartition[categorie] = round(repartition[categorie] / total_poids, 3)
        
        self.repartition_categories = repartition
        
        # Identification de la catégorie dominante
        if repartition:
            self.motivation_dominante_categorie = max(repartition.keys(), key=lambda k: repartition[k])
        
        return repartition
    
    def calculer_score_determination(self) -> float:
        """💪 Calcule un score de détermination basé sur l'intensité des motivations"""
        
        if not self.motivations_classees:
            return 0.0
        
        # Score basé sur l'intensité moyenne pondérée
        score_total = 0.0
        poids_total = 0.0
        
        intensite_valeurs = {
            IntensiteMotivationEnum.CRITIQUE: 1.0,
            IntensiteMotivationEnum.TRES_IMPORTANTE: 0.8,
            IntensiteMotivationEnum.IMPORTANTE: 0.6,
            IntensiteMotivationEnum.MODEREE: 0.4,
            IntensiteMotivationEnum.FAIBLE: 0.2
        }
        
        for motivation in self.motivations_classees:
            valeur_intensite = intensite_valeurs.get(motivation.intensite, 0.5)
            score_total += valeur_intensite * motivation.poids
            poids_total += motivation.poids
        
        score_base = score_total / poids_total if poids_total > 0 else 0.0
        
        # Bonus pour motivations non-négociables
        motivations_fermes = len([m for m in self.motivations_classees if not m.negociable])
        bonus_fermete = min(0.2, motivations_fermes / len(self.motivations_classees) * 0.2)
        
        # Bonus pour définition précise des critères
        motivations_avec_criteres = len([m for m in self.motivations_classees if m.criteres_evaluation])
        bonus_precision = min(0.1, motivations_avec_criteres / len(self.motivations_classees) * 0.1)
        
        score_final = min(1.0, score_base + bonus_fermete + bonus_precision)
        self.score_determination = round(score_final, 3)
        return self.score_determination
    
    def calculer_score_flexibilite(self) -> float:
        """🔄 Calcule un score de flexibilité motivationnelle"""
        
        if not self.motivations_classees:
            return 1.0  # Flexibilité maximale si pas de motivations définies
        
        # Pourcentage de motivations négociables
        motivations_negociables = len([m for m in self.motivations_classees if m.negociable])
        ratio_negociable = motivations_negociables / len(self.motivations_classees)
        
        # Présence d'alternatives pour les motivations importantes
        motivations_importantes = [m for m in self.motivations_classees 
                                 if m.intensite in [IntensiteMotivationEnum.CRITIQUE, IntensiteMotivationEnum.TRES_IMPORTANTE]]
        
        alternatives_score = 0.0
        if motivations_importantes:
            motivations_avec_alternatives = len([m for m in motivations_importantes if m.alternatives_acceptables])
            alternatives_score = motivations_avec_alternatives / len(motivations_importantes)
        
        # Diversité des catégories (plus de diversité = plus de flexibilité)
        nb_categories = len(set(m.definir_categorie() for m in self.motivations_classees))
        diversite_score = min(1.0, nb_categories / 4)  # Max 4 catégories principales
        
        # Score final
        score_flexibilite = (ratio_negociable * 0.4 + alternatives_score * 0.3 + diversite_score * 0.3)
        
        self.score_flexibilite_motivations = round(score_flexibilite, 3)
        return self.score_flexibilite_motivations
    
    def analyser_coherence_raison_ecoute(self, raison_ecoute: PourquoiEcouteEnum) -> float:
        """🎯 Analyse la cohérence entre motivations et raison d'écoute"""
        
        if not self.motivations_classees:
            return 0.5  # Neutre si pas de motivations
        
        # Mapping cohérence raison/motivations
        coherences_attendues = {
            PourquoiEcouteEnum.REMUNERATION_FAIBLE: [MotivationEnum.SALAIRE],
            PourquoiEcouteEnum.MANQUE_PERSPECTIVES: [MotivationEnum.EVOLUTION, MotivationEnum.APPRENTISSAGE, MotivationEnum.RECONNAISSANCE],
            PourquoiEcouteEnum.MANQUE_FLEXIBILITE: [MotivationEnum.FLEXIBILITE, MotivationEnum.EQUILIBRE_VIE, MotivationEnum.AUTONOMIE],
            PourquoiEcouteEnum.MAUVAISE_AMBIANCE: [MotivationEnum.AMBIANCE, MotivationEnum.RECONNAISSANCE],
            PourquoiEcouteEnum.SURCHARGE_TRAVAIL: [MotivationEnum.EQUILIBRE_VIE, MotivationEnum.FLEXIBILITE],
            PourquoiEcouteEnum.RECHERCHE_NOUVEAU_DEFI: [MotivationEnum.INNOVATION, MotivationEnum.APPRENTISSAGE, MotivationEnum.EVOLUTION]
        }
        
        motivations_attendues = coherences_attendues.get(raison_ecoute, [])
        
        if not motivations_attendues:
            self.coherence_avec_raison_ecoute = 0.5
            return 0.5
        
        # Vérification si les motivations prioritaires correspondent
        top_3_motivations = [m.motivation for m in sorted(self.motivations_classees, key=lambda x: x.priorite)[:3]]
        
        coherences_trouvees = len([m for m in top_3_motivations if m in motivations_attendues])
        score_coherence = coherences_trouvees / min(3, len(motivations_attendues))
        
        self.coherence_avec_raison_ecoute = round(score_coherence, 3)
        return self.coherence_avec_raison_ecoute
    
    def evaluer_adequation_offre_complete(self, caracteristiques_offre: Dict[str, Any]) -> Dict[str, Any]:
        """🎯 Évaluation complète de l'adéquation avec une offre"""
        
        evaluations_individuelles = []
        score_global = 0.0
        alertes_critiques = []
        points_forts = []
        
        for motivation in self.motivations_classees:
            evaluation = motivation.evaluer_adequation_offre(caracteristiques_offre)
            evaluations_individuelles.append(evaluation)
            
            # Contribution au score global (pondérée)
            score_global += evaluation['score_adequation'] * motivation.poids
            
            # Alertes critiques (motivations critiques mal satisfaites)
            if (motivation.intensite == IntensiteMotivationEnum.CRITIQUE and 
                evaluation['score_adequation'] < 0.5):
                alertes_critiques.extend(evaluation['alertes'])
            
            # Points forts (motivations bien satisfaites)
            if evaluation['score_adequation'] >= 0.8:
                points_forts.extend(evaluation['details_evaluation'])
        
        # Analyse par catégorie
        scores_par_categorie = {}
        for categorie in CategorieMotivationEnum:
            motivations_cat = [m for m in self.motivations_classees if m.definir_categorie() == categorie]
            if motivations_cat:
                score_cat = sum(
                    next(e['score_adequation'] for e in evaluations_individuelles if e['motivation'] == m.motivation) 
                    * m.poids for m in motivations_cat
                ) / sum(m.poids for m in motivations_cat)
                scores_par_categorie[categorie] = round(score_cat, 3)
        
        # Recommandations
        recommandations = self._generer_recommandations_offre(evaluations_individuelles, score_global)
        
        return {
            "score_adequation_global": round(score_global, 3),
            "evaluations_detaillees": evaluations_individuelles,
            "scores_par_categorie": scores_par_categorie,
            "alertes_critiques": alertes_critiques,
            "points_forts": list(set(points_forts)),
            "recommandations": recommandations,
            "resume": {
                "motivations_bien_satisfaites": len([e for e in evaluations_individuelles if e['score_adequation'] >= 0.7]),
                "motivations_critiques_problematiques": len([e for e in evaluations_individuelles 
                                                          if e['score_adequation'] < 0.5 and 
                                                          any(m.intensite == IntensiteMotivationEnum.CRITIQUE 
                                                              for m in self.motivations_classees 
                                                              if m.motivation == e['motivation'])]),
                "categorie_mieux_satisfaite": max(scores_par_categorie.keys(), key=lambda k: scores_par_categorie[k]) if scores_par_categorie else None
            }
        }
    
    def _generer_recommandations_offre(self, evaluations: List[Dict], score_global: float) -> List[str]:
        """💡 Génère des recommandations basées sur l'évaluation"""
        
        recommandations = []
        
        if score_global >= 0.8:
            recommandations.append("Excellent match motivationnel - candidat très aligné")
        elif score_global >= 0.6:
            recommandations.append("Bon match motivationnel - quelques points à clarifier")
        else:
            recommandations.append("Match motivationnel faible - ajustements nécessaires")
        
        # Recommandations spécifiques par motivation mal satisfaite
        motivations_problematiques = [e for e in evaluations if e['score_adequation'] < 0.5]
        
        for eval_pb in motivations_problematiques:
            if eval_pb['motivation'] == MotivationEnum.SALAIRE:
                recommandations.append("Revoir la proposition salariale ou mettre en avant les avantages")
            elif eval_pb['motivation'] == MotivationEnum.EVOLUTION:
                recommandations.append("Clarifier les perspectives d'évolution et le plan de carrière")
            elif eval_pb['motivation'] == MotivationEnum.FLEXIBILITE:
                recommandations.append("Améliorer la flexibilité (télétravail, horaires)")
            elif eval_pb['motivation'] == MotivationEnum.APPRENTISSAGE:
                recommandations.append("Mettre en avant les opportunités de formation")
        
        # Recommandations pour les points forts
        motivations_fortes = [e for e in evaluations if e['score_adequation'] >= 0.8]
        if motivations_fortes:
            recommandations.append(f"Capitaliser sur les points forts: {', '.join([e['motivation'].value for e in motivations_fortes[:2]])}")
        
        return recommandations
    
    def generer_profil_motivationnel_resume(self) -> Dict[str, Any]:
        """📊 Génère un résumé du profil motivationnel"""
        
        # Calculs des scores
        self.analyser_repartition_categories()
        score_determination = self.calculer_score_determination()
        score_flexibilite = self.calculer_score_flexibilite()
        
        # Top 3 motivations
        top_3 = sorted(self.motivations_classees, key=lambda x: x.priorite)[:3]
        
        # Profil type
        if score_determination >= 0.8:
            if score_flexibilite >= 0.6:
                profil_type = "Déterminé mais adaptable"
            else:
                profil_type = "Très déterminé et exigeant"
        elif score_flexibilite >= 0.8:
            profil_type = "Très flexible et adaptable"
        else:
            profil_type = "Profil équilibré"
        
        return {
            "profil_type": profil_type,
            "top_3_motivations": [
                {
                    "motivation": m.motivation,
                    "intensite": m.intensite,
                    "poids": m.poids,
                    "negociable": m.negociable
                } for m in top_3
            ],
            "repartition_categories": self.repartition_categories,
            "motivation_dominante_categorie": self.motivation_dominante_categorie,
            "scores": {
                "determination": score_determination,
                "flexibilite": score_flexibilite,
                "coherence_raison_ecoute": self.coherence_avec_raison_ecoute
            },
            "caracteristiques": {
                "nb_motivations_totales": len(self.motivations_classees),
                "nb_motivations_critiques": len([m for m in self.motivations_classees if m.intensite == IntensiteMotivationEnum.CRITIQUE]),
                "nb_motivations_negociables": len([m for m in self.motivations_classees if m.negociable]),
                "nb_categories_representees": len(self.repartition_categories)
            },
            "insights": self._generer_insights_profil(profil_type, score_determination, score_flexibilite)
        }
    
    def _generer_insights_profil(self, profil_type: str, determination: float, flexibilite: float) -> List[str]:
        """🔍 Génère des insights sur le profil motivationnel"""
        
        insights = []
        
        if determination >= 0.8:
            insights.append("Candidat avec des objectifs très clairs")
        
        if flexibilite >= 0.8:
            insights.append("Grande capacité d'adaptation aux opportunités")
        
        if self.motivation_dominante_categorie == CategorieMotivationEnum.FINANCIERE:
            insights.append("Motivations principalement financières")
        elif self.motivation_dominante_categorie == CategorieMotivationEnum.PROFESSIONNELLE:
            insights.append("Orienté développement professionnel")
        elif self.motivation_dominante_categorie == CategorieMotivationEnum.PERSONNELLE:
            insights.append("Privilégie l'équilibre personnel")
        
        if len(self.motivations_classees) >= 7:
            insights.append("Profil motivationnel riche et diversifié")
        
        motivations_critiques = [m for m in self.motivations_classees if m.intensite == IntensiteMotivationEnum.CRITIQUE]
        if len(motivations_critiques) >= 3:
            insights.append("Plusieurs motivations critiques - candidat exigeant")
        
        return insights
    
    class Config:
        json_schema_extra = {
            "example": {
                "motivations_classees": [
                    {
                        "motivation": "Évolution",
                        "intensite": "Très importante",
                        "priorite": 1,
                        "poids": 0.3,
                        "description_personnalisee": "Accès au management",
                        "negociable": False
                    },
                    {
                        "motivation": "Salaire",
                        "intensite": "Importante",
                        "priorite": 2,
                        "poids": 0.25,
                        "negociable": True
                    }
                ],
                "coherence_avec_raison_ecoute": 0.8
            }
        }
