"""
🎯 Nextvision - Modèles Questionnaires Avancés pour Commitment-
Structures de données enrichies pour questionnaires complets des candidats

Author: NEXTEN Team
Version: 1.0.0
Source: https://github.com/Bapt252/Commitment-
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Union
from datetime import datetime
from enum import Enum

class DisponibiliteType(str, Enum):
    """🕐 Types de disponibilité candidat"""
    IMMEDIAT = "Immédiat"
    DANS_1_MOIS = "Dans 1 mois"
    DANS_2_MOIS = "Dans 2 mois"
    DANS_3_MOIS = "Dans 3 mois"
    DANS_6_MOIS = "Dans 6 mois"
    NON_DEFINI = "Non défini"

class RaisonEcoute(str, Enum):
    """🎧 Raisons d'être à l'écoute (pondération adaptative)"""
    REMUNERATION_FAIBLE = "Rémunération trop faible"
    POSTE_INADEQUAT = "Poste ne coïncide pas avec poste proposé"
    POSTE_TROP_LOIN = "Poste trop loin de mon domicile"
    MANQUE_FLEXIBILITE = "Manque de flexibilité"
    MANQUE_PERSPECTIVES = "Manque de perspectives d'évolution"

class EnvironnementTravail(str, Enum):
    """🏢 Types d'environnement de travail"""
    BUREAU_INDIVIDUEL = "Bureau individuel"
    OPEN_SPACE = "Open space"
    COWORKING = "Espace de coworking"
    DOMICILE = "Télétravail complet"
    HYBRIDE = "Télétravail hybride"
    TERRAIN = "Travail sur le terrain"

class TypeContrat(str, Enum):
    """📋 Types de contrats de travail"""
    CDI = "CDI"
    CDD = "CDD"
    FREELANCE = "Freelance"
    INTERIM = "Intérim"
    STAGE = "Stage"
    APPRENTISSAGE = "Apprentissage"

class MoyenTransport(str, Enum):
    """🚗 Moyens de transport"""
    VOITURE = "Voiture"
    TRANSPORT_COMMUN = "Transport en commun"
    VELO = "Vélo"
    MARCHE = "Marche à pied"
    MOTO = "Moto/Scooter"
    COVOITURAGE = "Covoiturage"

class TimingInfo(BaseModel):
    """⏰ Informations de timing du candidat"""
    disponibilite: DisponibiliteType
    pourquoi_a_lecoute: RaisonEcoute
    preavis: Dict[str, Union[str, bool]] = Field(
        default={"durée": "", "négociable": False},
        description="Informations sur le préavis actuel"
    )
    
    @validator('preavis')
    def validate_preavis(cls, v):
        required_keys = {"durée", "négociable"}
        if not all(key in v for key in required_keys):
            raise ValueError(f"preavis doit contenir les clés: {required_keys}")
        return v

class SecteursPreferences(BaseModel):
    """🏭 Préférences sectorielles du candidat"""
    preferes: List[str] = Field(default=[], description="Secteurs préférés")
    redhibitoires: List[str] = Field(default=[], description="Secteurs à éviter absolument")
    
    @validator('preferes', 'redhibitoires')
    def validate_secteurs(cls, v):
        # Validation que les secteurs sont des strings non-vides
        return [s.strip() for s in v if s and s.strip()]

class TransportPreferences(BaseModel):
    """🚊 Préférences de transport"""
    moyens_selectionnes: List[MoyenTransport] = Field(default=[], description="Moyens de transport acceptés")
    temps_max: Dict[str, int] = Field(
        default={"voiture": 30, "transport_commun": 45},
        description="Temps de trajet maximum en minutes par moyen"
    )
    
    @validator('temps_max')
    def validate_temps_max(cls, v):
        # Validation que les temps sont positifs
        for transport, temps in v.items():
            if temps < 0:
                raise ValueError(f"Temps de trajet pour {transport} doit être positif")
        return v

class ContratsPreferences(BaseModel):
    """📝 Préférences contractuelles"""
    ordre_preference: List[TypeContrat] = Field(default=[], description="Types de contrats par ordre de préférence")
    
    @validator('ordre_preference')
    def validate_ordre(cls, v):
        # Vérifier qu'il n'y a pas de doublons
        if len(v) != len(set(v)):
            raise ValueError("Pas de doublons autorisés dans l'ordre de préférence")
        return v

class MotivationsClassees(BaseModel):
    """🎯 Motivations classées par priorité"""
    classees: List[str] = Field(default=[], description="Motivations par ordre d'importance")
    priorites: List[int] = Field(default=[], description="Scores de priorité (1=max, 5=min)")
    
    @validator('priorites')
    def validate_priorites(cls, v, values):
        if 'classees' in values and len(v) != len(values['classees']):
            raise ValueError("Le nombre de priorités doit correspondre au nombre de motivations")
        if any(p < 1 or p > 5 for p in v):
            raise ValueError("Les priorités doivent être entre 1 et 5")
        return v

class RemunerationAttentes(BaseModel):
    """💰 Attentes de rémunération"""
    min: int = Field(gt=0, description="Salaire minimum souhaité")
    max: int = Field(gt=0, description="Salaire maximum espéré")
    actuel: Optional[int] = Field(None, description="Salaire actuel (si renseigné)")
    
    @validator('max')
    def validate_max_gte_min(cls, v, values):
        if 'min' in values and v < values['min']:
            raise ValueError("Le salaire maximum doit être supérieur ou égal au minimum")
        return v

class QuestionnaireComplet(BaseModel):
    """📋 Questionnaire complet du candidat Commitment-"""
    
    # Timing et disponibilité
    timing: TimingInfo
    
    # Préférences sectorielles
    secteurs: SecteursPreferences
    
    # Environnement de travail
    environnement_travail: EnvironnementTravail
    
    # Transport
    transport: TransportPreferences
    
    # Contrats
    contrats: ContratsPreferences
    
    # Motivations
    motivations: MotivationsClassees
    
    # Rémunération
    remuneration: RemunerationAttentes
    
    # Métadonnées
    completion_date: Optional[datetime] = Field(default_factory=datetime.now)
    completion_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Taux de complétion du questionnaire")
    
    def calculate_completion_rate(self) -> float:
        """🧮 Calcule le taux de complétion du questionnaire"""
        fields_completed = 0
        total_fields = 7  # timing, secteurs, environnement, transport, contrats, motivations, remuneration
        
        # Vérification timing
        if self.timing.disponibilite and self.timing.pourquoi_a_lecoute:
            fields_completed += 1
            
        # Vérification secteurs
        if self.secteurs.preferes or self.secteurs.redhibitoires:
            fields_completed += 1
            
        # Vérification environnement
        if self.environnement_travail:
            fields_completed += 1
            
        # Vérification transport
        if self.transport.moyens_selectionnes:
            fields_completed += 1
            
        # Vérification contrats
        if self.contrats.ordre_preference:
            fields_completed += 1
            
        # Vérification motivations
        if self.motivations.classees:
            fields_completed += 1
            
        # Vérification rémunération
        if self.remuneration.min > 0 and self.remuneration.max > 0:
            fields_completed += 1
        
        completion_rate = fields_completed / total_fields
        self.completion_rate = completion_rate
        return completion_rate
    
    def get_adaptive_weighting_reason(self) -> str:
        """🎯 Retourne la raison pour la pondération adaptative"""
        return self.timing.pourquoi_a_lecoute.value
    
    def get_secteur_compatibility_data(self) -> Dict:
        """🏭 Données pour analyse sectorielle"""
        return {
            "secteurs_preferes": self.secteurs.preferes,
            "secteurs_redhibitoires": self.secteurs.redhibitoires,
            "flexibilite_sectorielle": len(self.secteurs.preferes) > 3
        }
    
    def get_transport_constraints(self) -> Dict:
        """🚗 Contraintes de transport pour matching géographique"""
        return {
            "moyens_disponibles": [m.value for m in self.transport.moyens_selectionnes],
            "temps_max": self.transport.temps_max,
            "flexibilite_transport": len(self.transport.moyens_selectionnes) > 2
        }
    
    def get_contract_preferences_weighted(self) -> Dict:
        """📋 Préférences contractuelles avec pondération"""
        weights = {}
        total_contracts = len(self.contrats.ordre_preference)
        
        for i, contract_type in enumerate(self.contrats.ordre_preference):
            # Score inversé : 1er choix = score max
            weight = (total_contracts - i) / total_contracts
            weights[contract_type.value] = weight
            
        return weights
    
    def get_motivation_priority_scores(self) -> Dict:
        """🎯 Scores de priorité des motivations (inversés)"""
        scores = {}
        for motivation, priority in zip(self.motivations.classees, self.motivations.priorites):
            # Score inversé : priorité 1 = score 5, priorité 5 = score 1
            score = 6 - priority  # Inversion pour que 1 = max score
            scores[motivation] = score / 5  # Normalisation 0-1
            
        return scores

class QuestionnaireMetadata(BaseModel):
    """📊 Métadonnées du questionnaire"""
    source: str = "https://github.com/Bapt252/Commitment-"
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    candidat_id: Optional[str] = None
    completion_time_seconds: Optional[int] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
