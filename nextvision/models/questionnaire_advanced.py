"""
🎯 Modèles Questionnaires Avancés NEXTEN
Structures de données enrichies pour questionnaires complets Commitment-

Author: NEXTEN Team
Version: 1.0.0
Integration: Commitment- → Nextvision Bridge
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Union
from enum import Enum
from datetime import datetime

class DisponibiliteEnum(str, Enum):
    """📅 Énumération des types de disponibilité"""
    IMMEDIATEMENT = "Immédiatement"
    UNE_SEMAINE = "Dans une semaine"
    DEUX_SEMAINES = "Dans 2 semaines"
    UN_MOIS = "Dans un mois"
    DEUX_MOIS = "Dans 2 mois"
    TROIS_MOIS = "Dans 3 mois"
    SIX_MOIS = "Dans 6 mois"
    PLUS_TARD = "Plus tard"

class PourquoiEcouteEnum(str, Enum):
    """📋 Énumération des raisons d'écoute (pour pondération adaptative)"""
    REMUNERATION_FAIBLE = "Rémunération trop faible"
    POSTE_INADEQUAT = "Poste ne coïncide pas avec poste proposé"
    TROP_LOIN = "Poste trop loin de mon domicile"
    MANQUE_FLEXIBILITE = "Manque de flexibilité"
    MANQUE_PERSPECTIVES = "Manque de perspectives d'évolution"
    MAUVAISE_AMBIANCE = "Mauvaise ambiance de travail"
    SURCHARGE_TRAVAIL = "Surcharge de travail"
    RECHERCHE_NOUVEAU_DEFI = "Recherche d'un nouveau défi"

class EnvironnementTravailEnum(str, Enum):
    """🏢 Types d'environnements de travail"""
    BUREAU_INDIVIDUEL = "Bureau individuel"
    BUREAU_PARTAGE = "Bureau partagé"
    OPEN_SPACE = "Open space"
    COWORKING = "Espace de coworking"
    DOMICILE = "Télétravail à domicile"
    HYBRIDE = "Hybride (bureau + télétravail)"
    TERRAIN = "Travail sur le terrain"
    ATELIER = "Atelier/Usine"
    INDIFFERENT = "Indifférent"

class TypeContratEnum(str, Enum):
    """📜 Types de contrats de travail"""
    CDI = "CDI"
    CDD = "CDD"
    INTERIM = "Intérim"
    FREELANCE = "Freelance"
    STAGE = "Stage"
    APPRENTISSAGE = "Apprentissage"
    PROFESSIONNALISATION = "Professionnalisation"
    PORTAGE_SALARIAL = "Portage salarial"

class MoyenTransportEnum(str, Enum):
    """🚗 Moyens de transport"""
    VOITURE = "Voiture"
    TRANSPORT_COMMUN = "Transport en commun"
    VELO = "Vélo"
    MARCHE = "À pied"
    MOTO_SCOOTER = "Moto/Scooter"
    COVOITURAGE = "Covoiturage"
    TELETRAVAIL = "Télétravail"

class MotivationEnum(str, Enum):
    """🎯 Types de motivations professionnelles"""
    EVOLUTION = "Évolution"
    SALAIRE = "Salaire"
    FLEXIBILITE = "Flexibilité"
    AMBIANCE = "Ambiance de travail"
    APPRENTISSAGE = "Apprentissage"
    RECONNAISSANCE = "Reconnaissance"
    AUTONOMIE = "Autonomie"
    EQUILIBRE_VIE = "Équilibre vie pro/perso"
    SECURITE = "Sécurité de l'emploi"
    INNOVATION = "Innovation/Créativité"

class PreavisConfig(BaseModel):
    """⏰ Configuration du préavis"""
    duree: str = Field(..., description="Durée du préavis (ex: '2 mois', '3 semaines')")
    negociable: bool = Field(default=False, description="Préavis négociable avec l'employeur")
    reduction_possible: Optional[str] = Field(None, description="Réduction possible du préavis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "duree": "2 mois",
                "negociable": True,
                "reduction_possible": "1 mois si accord mutuel"
            }
        }

class TimingDisponibilite(BaseModel):
    """📅 Timing complet de disponibilité"""
    disponibilite: DisponibiliteEnum = Field(..., description="Période de disponibilité")
    pourquoi_a_lecoute: PourquoiEcouteEnum = Field(..., description="Raison d'écoute (pour pondération adaptative)")
    preavis: Optional[PreavisConfig] = Field(None, description="Configuration du préavis")
    date_souhaitee: Optional[datetime] = Field(None, description="Date souhaitée de prise de poste")
    contraintes_specifiques: Optional[str] = Field(None, description="Contraintes spécifiques de timing")
    
    class Config:
        json_schema_extra = {
            "example": {
                "disponibilite": "Dans 2 mois",
                "pourquoi_a_lecoute": "Rémunération trop faible",
                "preavis": {
                    "duree": "2 mois",
                    "negociable": True
                },
                "date_souhaitee": "2025-09-01T00:00:00Z",
                "contraintes_specifiques": "Préférence pour une prise de poste en début de mois"
            }
        }

class PreferencesSectorielles(BaseModel):
    """🎯 Préférences sectorielles détaillées"""
    preferes: List[str] = Field(default_factory=list, description="Secteurs préférés")
    redhibitoires: List[str] = Field(default_factory=list, description="Secteurs rédhibitoires/refusés")
    experience_acquise: List[str] = Field(default_factory=list, description="Secteurs avec expérience")
    ouverts_decouverte: List[str] = Field(default_factory=list, description="Secteurs ouverts à la découverte")
    score_adaptation: Optional[float] = Field(None, ge=0, le=1, description="Score d'adaptabilité sectorielle")
    
    @validator('score_adaptation')
    def validate_score(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError('Score doit être entre 0 et 1')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "preferes": ["Technologies de l'information", "Finance", "Conseil"],
                "redhibitoires": ["Agriculture", "Industrie lourde"],
                "experience_acquise": ["Technologies de l'information", "E-commerce"],
                "ouverts_decouverte": ["FinTech", "GreenTech"],
                "score_adaptation": 0.8
            }
        }

class ConfigTransport(BaseModel):
    """🚗 Configuration détaillée du transport"""
    moyens_selectionnes: List[MoyenTransportEnum] = Field(..., description="Moyens de transport acceptés")
    temps_max: Dict[str, int] = Field(..., description="Temps maximum par moyen (en minutes)")
    distance_max_km: Optional[int] = Field(None, description="Distance maximum en kilomètres")
    couts_max_mensuel: Optional[int] = Field(None, description="Coût transport maximum par mois (€)")
    flexibilite_horaires: bool = Field(default=False, description="Flexibilité horaires pour transport")
    
    @validator('temps_max')
    def validate_temps_max(cls, v, values):
        """Valide que les temps correspondent aux moyens sélectionnés"""
        if 'moyens_selectionnes' in values:
            moyens = [m.value.lower().replace(' ', '_').replace('/', '_') for m in values['moyens_selectionnes']]
            for moyen_key in v.keys():
                if moyen_key not in moyens:
                    # Mapping flexible pour les clés
                    valid_keys = ['voiture', 'transport_commun', 'velo', 'marche', 'moto_scooter', 'covoiturage', 'teletravail']
                    if moyen_key not in valid_keys:
                        raise ValueError(f'Temps défini pour moyen non sélectionné: {moyen_key}')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "moyens_selectionnes": ["Voiture", "Transport en commun"],
                "temps_max": {
                    "voiture": 30,
                    "transport_commun": 45
                },
                "distance_max_km": 25,
                "couts_max_mensuel": 150,
                "flexibilite_horaires": True
            }
        }

class PreferencesContrats(BaseModel):
    """📜 Préférences de types de contrats"""
    ordre_preference: List[TypeContratEnum] = Field(..., description="Types contrats par ordre de préférence")
    duree_min_cdd: Optional[int] = Field(None, description="Durée minimum CDD en mois")
    ouvert_interim: bool = Field(default=False, description="Ouvert aux missions d'intérim")
    freelance_acceptable: bool = Field(default=False, description="Freelance acceptable")
    taux_journalier_min: Optional[int] = Field(None, description="TJM minimum pour freelance (€)")
    exclusions_specifiques: List[str] = Field(default_factory=list, description="Types de contrats exclus")
    
    @validator('duree_min_cdd')
    def validate_duree_cdd(cls, v):
        if v is not None and v < 1:
            raise ValueError('Durée CDD minimum doit être d\'au moins 1 mois')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "ordre_preference": ["CDI", "CDD", "Freelance"],
                "duree_min_cdd": 6,
                "ouvert_interim": False,
                "freelance_acceptable": True,
                "taux_journalier_min": 450,
                "exclusions_specifiques": ["Stage", "Apprentissage"]
            }
        }

class MotivationClassee(BaseModel):
    """🎯 Motivation avec classement et pondération"""
    motivation: MotivationEnum = Field(..., description="Type de motivation")
    priorite: int = Field(..., ge=1, le=10, description="Priorité (1 = plus important)")
    poids: float = Field(..., ge=0, le=1, description="Poids dans l'évaluation")
    description_personnalisee: Optional[str] = Field(None, description="Description personnalisée")
    
    @validator('priorite')
    def validate_priorite(cls, v):
        if v < 1 or v > 10:
            raise ValueError('Priorité doit être entre 1 et 10')
        return v

class RankingMotivations(BaseModel):
    """🏆 Classement complet des motivations"""
    motivations_classees: List[MotivationClassee] = Field(..., description="Motivations classées par priorité")
    poids_total_normalise: bool = Field(default=True, description="Poids normalisés (somme = 1)")
    facteur_adaptabilite: float = Field(default=0.8, ge=0, le=1, description="Facteur d'adaptabilité motivations")
    
    @validator('motivations_classees')
    def validate_motivations_unique(cls, v):
        """Valide que chaque motivation n'apparaît qu'une fois"""
        motivations = [m.motivation for m in v]
        if len(motivations) != len(set(motivations)):
            raise ValueError('Chaque motivation ne peut apparaître qu\'une seule fois')
        return v
    
    @validator('motivations_classees')
    def validate_priorites_unique(cls, v):
        """Valide que chaque priorité n'apparaît qu'une fois"""
        priorites = [m.priorite for m in v]
        if len(priorites) != len(set(priorites)):
            raise ValueError('Chaque priorité doit être unique')
        return v
    
    def normaliser_poids(self) -> 'RankingMotivations':
        """🔄 Normalise les poids pour que la somme = 1"""
        total_poids = sum(m.poids for m in self.motivations_classees)
        if total_poids > 0:
            for motivation in self.motivations_classees:
                motivation.poids = motivation.poids / total_poids
        self.poids_total_normalise = True
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "motivations_classees": [
                    {
                        "motivation": "Évolution",
                        "priorite": 1,
                        "poids": 0.3,
                        "description_personnalisee": "Accès à des postes de management"
                    },
                    {
                        "motivation": "Salaire",
                        "priorite": 2,
                        "poids": 0.25
                    },
                    {
                        "motivation": "Flexibilité",
                        "priorite": 3,
                        "poids": 0.2
                    }
                ],
                "poids_total_normalise": True,
                "facteur_adaptabilite": 0.8
            }
        }

class QuestionnaireCompletAdvanced(BaseModel):
    """📋 Questionnaire complet enrichi pour Commitment-"""
    timing: TimingDisponibilite = Field(..., description="Timing et disponibilité")
    secteurs: PreferencesSectorielles = Field(..., description="Préférences sectorielles")
    environnement_travail: EnvironnementTravailEnum = Field(..., description="Environnement de travail préféré")
    transport: ConfigTransport = Field(..., description="Configuration transport")
    contrats: PreferencesContrats = Field(..., description="Préférences de contrats")
    motivations: RankingMotivations = Field(..., description="Motivations classées")
    remuneration: Dict[str, int] = Field(..., description="Attentes rémunération (min, max)")
    
    # Métadonnées de questionnaire
    version_questionnaire: str = Field(default="2.0.0", description="Version du questionnaire")
    date_completion: Optional[datetime] = Field(default_factory=datetime.now, description="Date de complétion")
    completude_score: Optional[float] = Field(None, ge=0, le=1, description="Score de complétude")
    
    @validator('remuneration')
    def validate_remuneration(cls, v):
        """Valide la cohérence des attentes salariales"""
        if 'min' not in v or 'max' not in v:
            raise ValueError('Rémunération doit contenir min et max')
        if v['min'] > v['max']:
            raise ValueError('Salaire minimum ne peut être supérieur au maximum')
        if v['min'] < 0 or v['max'] < 0:
            raise ValueError('Salaires doivent être positifs')
        return v
    
    def calculer_score_completude(self) -> float:
        """📊 Calcule le score de complétude du questionnaire"""
        score = 0.0
        total_sections = 7
        
        # Timing (obligatoire)
        score += 1.0
        
        # Secteurs
        if self.secteurs.preferes or self.secteurs.redhibitoires:
            score += 1.0
        
        # Environnement (obligatoire)
        score += 1.0
        
        # Transport
        if self.transport.moyens_selectionnes:
            score += 1.0
        
        # Contrats
        if self.contrats.ordre_preference:
            score += 1.0
        
        # Motivations
        if self.motivations.motivations_classees:
            score += 1.0
        
        # Rémunération (obligatoire)
        score += 1.0
        
        self.completude_score = score / total_sections
        return self.completude_score
    
    class Config:
        json_schema_extra = {
            "example": {
                "timing": {
                    "disponibilite": "Dans 2 mois",
                    "pourquoi_a_lecoute": "Rémunération trop faible",
                    "preavis": {
                        "duree": "2 mois",
                        "negociable": True
                    }
                },
                "secteurs": {
                    "preferes": ["Technologies de l'information", "Finance"],
                    "redhibitoires": ["Agriculture", "Industrie lourde"]
                },
                "environnement_travail": "Bureau individuel",
                "transport": {
                    "moyens_selectionnes": ["Voiture", "Transport en commun"],
                    "temps_max": {
                        "voiture": 30,
                        "transport_commun": 45
                    }
                },
                "contrats": {
                    "ordre_preference": ["CDI", "CDD", "Freelance"]
                },
                "motivations": {
                    "motivations_classees": [
                        {
                            "motivation": "Évolution",
                            "priorite": 1,
                            "poids": 0.4
                        },
                        {
                            "motivation": "Salaire", 
                            "priorite": 2,
                            "poids": 0.35
                        }
                    ]
                },
                "remuneration": {
                    "min": 45000,
                    "max": 60000
                }
            }
        }
