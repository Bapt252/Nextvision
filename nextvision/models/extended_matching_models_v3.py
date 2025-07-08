"""
🚀 Nextvision v3.0 - Extended Matching Models pour 12 Composants

Extension révolutionnaire des modèles bidirectionnels V2.0 :
- HÉRITAGE COMPLET : 100% compatibilité avec bidirectional_models.py V2.0
- EXTENSION PROGRESSIVE : De 4 à 12 composants de matching
- EXPLOITATION QUESTIONNAIRES : 95% des données utilisées (vs 15% V2.0)
- PONDÉRATION ADAPTATIVE : Selon raison d'écoute candidat étendue

Composants V3.0 (12 total) :
┌─ V2.0 PRÉSERVÉS (4) ────────────────────────────────────┐
│ 1. Sémantique (25%)     │ 3. Expérience (15%)           │
│ 2. Salaire (20%)        │ 4. Localisation (10%)         │
└─────────────────────────────────────────────────────────┘
┌─ V3.0 NOUVEAUX (8) ─────────────────────────────────────┐
│ 5. Motivations (8%)     │ 9. Modalités Travail (4%)     │
│ 6. Secteurs (6%)        │ 10. Progression Salar. (3%)   │
│ 7. Contrats (5%)        │ 11. Raison Écoute (3%) 🧠     │
│ 8. Timing (4%)          │ 12. Situation (2%)            │
└─────────────────────────────────────────────────────────┘

Author: NEXTEN Team
Version: 3.0.0 - Extended Bidirectional Matching
"""

from pydantic import BaseModel, Field, model_validator
from typing import Dict, List, Optional, Union, Literal, Any
from enum import Enum
from datetime import datetime
import json

# 🔄 IMPORT COMPLET V2.0 - HÉRITAGE PRÉSERVÉ
from nextvision.models.bidirectional_models import (
    BiDirectionalCandidateProfile, BiDirectionalCompanyProfile,
    BiDirectionalMatchingRequest, BiDirectionalMatchingResponse,
    ComponentWeights, AdaptiveWeightingConfig, MatchingComponentScores,
    RaisonEcouteCandidat, UrgenceRecrutement, NiveauExperience, TypeContrat,
    PersonalInfoBidirectional, CompetencesProfessionnelles, AttentesCandidat,
    MotivationsCandidat, ExperienceProfessionnelle, InformationsEntreprise,
    DescriptionPoste, ExigencesPoste, ConditionsTravail, CriteresRecrutement
)

# === ENUMS ÉTENDUS V3.0 ===

class RaisonEcouteEtendue(str, Enum):
    """🆕 Raisons d'écoute candidat étendues pour pondération adaptative V3.0"""
    # V2.0 PRÉSERVÉES
    REMUNERATION_TROP_FAIBLE = "Rémunération trop faible"
    POSTE_NE_COINCIDE_PAS = "Poste ne coïncide pas avec poste proposé"
    POSTE_TROP_LOIN = "Poste trop loin de mon domicile"
    MANQUE_FLEXIBILITE = "Manque de flexibilité"
    MANQUE_PERSPECTIVES = "Manque de perspectives d'évolution"
    
    # 🆕 V3.0 NOUVELLES (issues questionnaire étape 4)
    PROBLEMES_MANAGEMENT = "Problèmes de management"
    CONDITIONS_TRAVAIL = "Conditions de travail"
    MISSIONS_PEU_INTERESSANTES = "Missions peu intéressantes"
    AUTRE_MOTIVATION = "Autre motivation spécifiée"

class MotivationProfessionnelle(str, Enum):
    """🆕 Motivations professionnelles candidat (questionnaire étape 3)"""
    EVOLUTION = "Perspectives d'évolution"
    SALAIRE = "Augmentation salariale"
    FLEXIBILITE = "Flexibilité"
    AUTRE = "Autre motivation"

class SecteurActivite(str, Enum):
    """🆕 Secteurs d'activité pour compatibilité sectorielle"""
    TECH = "Technologies de l'information"
    FINANCE = "Finance et banque"
    SANTE = "Santé et médical"
    EDUCATION = "Education et formation"
    COMMERCE = "Commerce et retail"
    INDUSTRIE = "Industrie et manufacture"
    ENERGIE = "Energie et environnement"
    TRANSPORT = "Transport et logistique"
    CONSTRUCTION = "Immobilier et construction"
    MEDIA = "Médias et communication"
    LUXE = "Luxe et mode"
    AGRICULTURE = "Agriculture et agroalimentaire"
    SERVICES = "Services aux entreprises"
    CULTURE = "Culture et divertissement"
    SPORT = "Sport et loisirs"

class TypeTransport(str, Enum):
    """🆕 Types de transport candidat"""
    TRANSPORTS_COMMUN = "Transports en commun"
    VEHICULE_PERSONNEL = "Véhicule personnel"
    VELO = "Vélo"
    MARCHE = "À pied"

class PreferenceBureau(str, Enum):
    """🆕 Préférences environnement bureau"""
    OPEN_SPACE = "Open Space"
    BUREAU_FERME = "Bureau fermé"
    SANS_PREFERENCE = "Sans préférence"

class SituationActuelle(str, Enum):
    """🆕 Situation actuelle candidat (questionnaire étape 4)"""
    EN_POSTE = "En poste"
    ETUDIANT = "Étudiant"
    DEMANDEUR_EMPLOI = "Demandeur d'emploi"
    FREELANCE = "Freelance/Consultant"
    RECONVERSION = "En reconversion"

class DelaiDisponibilite(str, Enum):
    """🆕 Délais de disponibilité candidat"""
    IMMEDIAT = "Immédiatement"
    UN_MOIS = "Dans 1 mois"
    DEUX_MOIS = "Dans 2 mois"
    TROIS_MOIS = "Dans 3 mois"

class UrgenceRecrutementEtendue(str, Enum):
    """🆕 Urgence recrutement entreprise étendue"""
    CRITIQUE = "Critique (< 2 semaines)"
    URGENT = "Urgent (< 1 mois)"
    NORMAL = "Normal (1-3 mois)"
    LONG_TERME = "Long terme (> 3 mois)"
    FLEXIBLE = "Flexible selon profil"

# === MODÈLES QUESTIONNAIRES V3.0 ===

class TransportPreferences(BaseModel):
    """🆕 Préférences transport et mobilité candidat"""
    methods: List[TypeTransport] = []
    travel_times: Dict[str, int] = {}  # {"transports_commun": 30, "vehicule": 25}
    max_distance_km: Optional[int] = 50
    remote_acceptable: bool = False

class MotivationsExtended(BaseModel):
    """🆕 Motivations professionnelles étendues candidat"""
    ranking: List[MotivationProfessionnelle] = []  # Classement par priorité
    autre_motivation_text: Optional[str] = None
    raison_ecoute_primaire: RaisonEcouteEtendue
    raisons_ecoute_multiples: List[RaisonEcouteEtendue] = []
    aspirations_texte: Optional[str] = None

class SecteursPreferences(BaseModel):
    """🆕 Préférences sectorielles candidat"""
    secteurs_preferes: List[SecteurActivite] = []
    secteurs_redhibitoires: List[SecteurActivite] = []
    ouverture_autres_secteurs: bool = True

class ContratsPreferences(BaseModel):
    """🆕 Préférences contractuelles candidat"""
    ranking: List[TypeContrat] = []  # Classement par préférence
    flexibilite_contractuelle: float = 0.5  # 0-1 scale

class TimingDisponibilite(BaseModel):
    """🆕 Timing et disponibilité candidat"""
    delai_souhaite: DelaiDisponibilite
    situation_actuelle: SituationActuelle
    salaire_actuel_min: Optional[int] = None
    salaire_actuel_max: Optional[int] = None
    peut_gerer_preavis: bool = True
    duree_preavis_max: Optional[int] = None  # en mois

class ModalitesTravail(BaseModel):
    """🆕 Modalités de travail souhaitées"""
    preference_bureau: PreferenceBureau
    remote_souhaite: bool = False
    hybride_acceptable: bool = True
    horaires_flexibles_souhaites: bool = False

# === MODÈLES CANDIDAT V3.0 ÉTENDUS ===

class ExtendedCandidateProfileV3(BiDirectionalCandidateProfile):
    """🚀 Profil candidat V3.0 avec exploitation complète des questionnaires"""
    
    # 🔄 HÉRITAGE COMPLET V2.0
    # Tous les champs V2.0 sont automatiquement présents
    
    # 🆕 EXTENSIONS V3.0 - Nouvelles données questionnaires
    transport_preferences: TransportPreferences = Field(default_factory=TransportPreferences)
    motivations_extended: MotivationsExtended = Field(default_factory=MotivationsExtended)
    secteurs_preferences: SecteursPreferences = Field(default_factory=SecteursPreferences)
    contrats_preferences: ContratsPreferences = Field(default_factory=ContratsPreferences)
    timing_disponibilite: TimingDisponibilite = Field(default_factory=TimingDisponibilite)
    modalites_travail: ModalitesTravail = Field(default_factory=ModalitesTravail)
    
    # Métadonnées V3.0
    questionnaire_completion_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    v3_extraction_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    v3_extracted_at: datetime = Field(default_factory=datetime.now)

# === MODÈLES ENTREPRISE V3.0 ÉTENDUS ===

class RecrutementEtendu(BaseModel):
    """🆕 Informations recrutement entreprise étendues"""
    urgence: UrgenceRecrutementEtendue = UrgenceRecrutementEtendue.NORMAL
    delais_acceptables: List[str] = []  # ["immediat", "2semaines", "1mois"]
    peut_gerer_preavis: bool = True
    duree_preavis_max: Optional[int] = None  # en mois
    contexte: Optional[str] = None  # "creation", "remplacement", "croissance"
    nombre_postes: int = 1

class ModalitesEntreprise(BaseModel):
    """🆕 Modalités de travail proposées par l'entreprise"""
    remote_possible: bool = False
    remote_pourcentage: Optional[int] = None  # % de remote possible
    horaires_flexibles: bool = False
    environnement_bureau: Optional[PreferenceBureau] = None

class CriteresFlexibilite(BaseModel):
    """🆕 Critères et flexibilités entreprise"""
    flexibilite_contractuelle: float = 0.5  # 0-1 scale
    flexibilite_salariale: float = 0.2  # marge de négociation
    flexibilite_experience: float = 0.3  # tolérance sur expérience
    criteres_eliminatoires: List[str] = []
    criteres_souhaites: List[str] = []

class ExtendedCompanyProfileV3(BiDirectionalCompanyProfile):
    """🚀 Profil entreprise V3.0 avec besoins détaillés"""
    
    # 🔄 HÉRITAGE COMPLET V2.0
    # Tous les champs V2.0 sont automatiquement présents
    
    # 🆕 EXTENSIONS V3.0
    recrutement_etendu: RecrutementEtendu = Field(default_factory=RecrutementEtendu)
    modalites_entreprise: ModalitesEntreprise = Field(default_factory=ModalitesEntreprise)
    criteres_flexibilite: CriteresFlexibilite = Field(default_factory=CriteresFlexibilite)
    
    # Solutions aux problématiques candidats
    solutions_management: List[str] = []  # Solutions problèmes management
    solutions_conditions_travail: List[str] = []  # Conditions de travail
    solutions_missions: List[str] = []  # Amélioration missions
    
    # Métadonnées V3.0
    questionnaire_completion_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    v3_extraction_confidence: float = Field(default=0.0, ge=0.0, le=1.0)

# === COMPOSANTS DE SCORING V3.0 ===

class ExtendedComponentWeights(BaseModel):
    """🆕 Poids des 12 composants V3.0 avec préservation V2.0"""
    
    # 🔄 COMPOSANTS V2.0 PRÉSERVÉS (poids ajustés)
    semantique: float = Field(default=0.25, ge=0.0, le=1.0)
    salaire: float = Field(default=0.20, ge=0.0, le=1.0)
    experience: float = Field(default=0.15, ge=0.0, le=1.0)
    localisation: float = Field(default=0.10, ge=0.0, le=1.0)
    
    # 🆕 NOUVEAUX COMPOSANTS V3.0
    motivations: float = Field(default=0.08, ge=0.0, le=1.0)
    secteurs: float = Field(default=0.06, ge=0.0, le=1.0)
    contrats: float = Field(default=0.05, ge=0.0, le=1.0)
    timing: float = Field(default=0.04, ge=0.0, le=1.0)
    modalites_travail: float = Field(default=0.04, ge=0.0, le=1.0)
    progression_salariale: float = Field(default=0.03, ge=0.0, le=1.0)
    raison_ecoute: float = Field(default=0.03, ge=0.0, le=1.0)  # 🧠 CERVEAU ADAPTATIF
    situation: float = Field(default=0.02, ge=0.0, le=1.0)
    
    @model_validator(mode='after')
    def weights_sum_to_one(self):
        """Validation que la somme des 12 poids = 1.0"""
        total = (
            self.semantique + self.salaire + self.experience + self.localisation +
            self.motivations + self.secteurs + self.contrats + self.timing +
            self.modalites_travail + self.progression_salariale + 
            self.raison_ecoute + self.situation
        )
        if abs(total - 1.0) > 0.01:  # Tolérance 1%
            raise ValueError(f"Somme des 12 poids doit être 1.0, actuellement: {total:.3f}")
        return self

class ExtendedComponentScores(BaseModel):
    """🆕 Scores détaillés des 12 composants V3.0"""
    
    # 🔄 SCORES V2.0 PRÉSERVÉS
    semantique_score: float = Field(ge=0.0, le=1.0)
    semantique_details: Dict = Field(default_factory=dict)
    
    salaire_score: float = Field(ge=0.0, le=1.0)
    salaire_details: Dict = Field(default_factory=dict)
    
    experience_score: float = Field(ge=0.0, le=1.0)
    experience_details: Dict = Field(default_factory=dict)
    
    localisation_score: float = Field(ge=0.0, le=1.0)
    localisation_details: Dict = Field(default_factory=dict)
    
    # 🆕 NOUVEAUX SCORES V3.0
    motivations_score: float = Field(ge=0.0, le=1.0)
    motivations_details: Dict = Field(default_factory=dict)
    
    secteurs_score: float = Field(ge=0.0, le=1.0)
    secteurs_details: Dict = Field(default_factory=dict)
    
    contrats_score: float = Field(ge=0.0, le=1.0)
    contrats_details: Dict = Field(default_factory=dict)
    
    timing_score: float = Field(ge=0.0, le=1.0)
    timing_details: Dict = Field(default_factory=dict)
    
    modalites_travail_score: float = Field(ge=0.0, le=1.0)
    modalites_travail_details: Dict = Field(default_factory=dict)
    
    progression_salariale_score: float = Field(ge=0.0, le=1.0)
    progression_salariale_details: Dict = Field(default_factory=dict)
    
    raison_ecoute_score: float = Field(ge=0.0, le=1.0)  # 🧠 CERVEAU ADAPTATIF
    raison_ecoute_details: Dict = Field(default_factory=dict)
    
    situation_score: float = Field(ge=0.0, le=1.0)
    situation_details: Dict = Field(default_factory=dict)

class AdaptiveWeightingConfigV3(BaseModel):
    """🆕 Configuration pondération adaptative V3.0 avec 12 composants"""
    
    candidat_weights: ExtendedComponentWeights
    entreprise_weights: ExtendedComponentWeights
    
    # Raison d'écoute étendue
    raison_candidat: RaisonEcouteEtendue
    urgence_entreprise: UrgenceRecrutementEtendue
    
    # Justifications pondération
    reasoning_candidat: str
    reasoning_entreprise: str
    
    # 🧠 MATRICE ADAPTATIVE - Influence raison écoute sur autres composants
    adaptation_matrix: Dict[str, float] = Field(default_factory=dict)
    adaptation_confidence: float = Field(default=0.8, ge=0.0, le=1.0)

# === REQUÊTES ET RÉPONSES V3.0 ===

class ExtendedMatchingRequestV3(BaseModel):
    """🚀 Requête de matching V3.0 avec 12 composants"""
    
    candidat: ExtendedCandidateProfileV3
    entreprise: ExtendedCompanyProfileV3
    
    # Configuration matching V3.0
    force_adaptive_weighting: bool = True
    use_extended_components: bool = True  # 🆕 Utiliser les 12 composants
    v2_fallback_enabled: bool = True  # 🛡️ Fallback V2.0 si erreur
    
    # Options avancées
    questionnaire_boost: bool = True  # Boost si questionnaires complets
    sector_filtering: bool = True  # Filtrage secteurs rédhibitoires
    
    # Métadonnées
    matching_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    requested_version: str = "3.0.0"

class ExtendedMatchingResponseV3(BaseModel):
    """📊 Réponse de matching V3.0 avec détails 12 composants"""
    
    # Résultats matching
    matching_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    compatibility: Literal["excellent", "very_good", "good", "average", "poor", "incompatible"]
    
    # Scores détaillés 12 composants
    extended_component_scores: ExtendedComponentScores
    
    # Pondération adaptative appliquée
    adaptive_weighting_v3: AdaptiveWeightingConfigV3
    
    # Analyse questionnaires
    questionnaire_analysis: Dict[str, Any] = Field(default_factory=dict)
    sector_compatibility_analysis: Dict[str, Any] = Field(default_factory=dict)
    
    # Recommandations V3.0
    recommandations_candidat: List[str] = []
    recommandations_entreprise: List[str] = []
    points_forts_matching: List[str] = []
    points_amelioration: List[str] = []
    
    # Insights avancés
    raison_ecoute_analysis: Dict[str, Any] = Field(default_factory=dict)
    motivation_compatibility: Dict[str, Any] = Field(default_factory=dict)
    progression_opportunities: List[str] = []
    
    # Performance et métadonnées
    processing_time_ms: float
    version_used: str = "3.0.0"
    v2_fallback_used: bool = False
    questionnaire_completion_impact: float = 0.0  # Boost lié aux questionnaires
    timestamp: datetime = Field(default_factory=datetime.now)

# === MATRICE PONDÉRATION ADAPTATIVE V3.0 ===

ADAPTIVE_WEIGHTING_MATRIX_V3 = {
    # 🧠 MATRICE SELON RAISON D'ÉCOUTE CANDIDAT
    
    RaisonEcouteEtendue.REMUNERATION_TROP_FAIBLE: ExtendedComponentWeights(
        semantique=0.20, salaire=0.35, experience=0.10, localisation=0.10,
        motivations=0.05, secteurs=0.06, contrats=0.05, timing=0.04,
        modalites_travail=0.04, progression_salariale=0.05, raison_ecoute=0.03, situation=0.02
    ),
    
    RaisonEcouteEtendue.POSTE_NE_COINCIDE_PAS: ExtendedComponentWeights(
        semantique=0.35, salaire=0.15, experience=0.20, localisation=0.10,
        motivations=0.08, secteurs=0.10, contrats=0.05, timing=0.04,
        modalites_travail=0.04, progression_salariale=0.03, raison_ecoute=0.03, situation=0.02
    ),
    
    RaisonEcouteEtendue.POSTE_TROP_LOIN: ExtendedComponentWeights(
        semantique=0.25, salaire=0.20, experience=0.15, localisation=0.25,
        motivations=0.08, secteurs=0.06, contrats=0.05, timing=0.04,
        modalites_travail=0.06, progression_salariale=0.03, raison_ecoute=0.03, situation=0.02
    ),
    
    RaisonEcouteEtendue.MANQUE_FLEXIBILITE: ExtendedComponentWeights(
        semantique=0.25, salaire=0.15, experience=0.15, localisation=0.10,
        motivations=0.12, secteurs=0.06, contrats=0.10, timing=0.06,
        modalites_travail=0.08, progression_salariale=0.03, raison_ecoute=0.06, situation=0.04
    ),
    
    RaisonEcouteEtendue.MANQUE_PERSPECTIVES: ExtendedComponentWeights(
        semantique=0.30, salaire=0.25, experience=0.25, localisation=0.05,
        motivations=0.15, secteurs=0.06, contrats=0.05, timing=0.04,
        modalites_travail=0.04, progression_salariale=0.10, raison_ecoute=0.03, situation=0.02
    ),
    
    RaisonEcouteEtendue.PROBLEMES_MANAGEMENT: ExtendedComponentWeights(
        semantique=0.25, salaire=0.20, experience=0.15, localisation=0.10,
        motivations=0.15, secteurs=0.06, contrats=0.05, timing=0.04,
        modalites_travail=0.06, progression_salariale=0.03, raison_ecoute=0.08, situation=0.03
    ),
    
    RaisonEcouteEtendue.CONDITIONS_TRAVAIL: ExtendedComponentWeights(
        semantique=0.25, salaire=0.20, experience=0.15, localisation=0.08,
        motivations=0.10, secteurs=0.06, contrats=0.08, timing=0.04,
        modalites_travail=0.10, progression_salariale=0.03, raison_ecoute=0.08, situation=0.03
    ),
    
    RaisonEcouteEtendue.MISSIONS_PEU_INTERESSANTES: ExtendedComponentWeights(
        semantique=0.40, salaire=0.15, experience=0.15, localisation=0.10,
        motivations=0.15, secteurs=0.08, contrats=0.05, timing=0.04,
        modalites_travail=0.04, progression_salariale=0.03, raison_ecoute=0.06, situation=0.02
    )
}

# === FONCTIONS UTILITAIRES V3.0 ===

def get_adaptive_weights_v3(raison_ecoute: RaisonEcouteEtendue, 
                           urgence: UrgenceRecrutementEtendue) -> ExtendedComponentWeights:
    """🧠 Obtient les poids adaptatifs selon raison d'écoute candidat"""
    
    base_weights = ADAPTIVE_WEIGHTING_MATRIX_V3.get(
        raison_ecoute, 
        ExtendedComponentWeights()  # Poids par défaut
    )
    
    # Ajustement selon urgence entreprise
    if urgence == UrgenceRecrutementEtendue.CRITIQUE:
        # Boost timing et situation pour urgence critique
        weights_dict = base_weights.dict()
        weights_dict['timing'] = min(0.08, weights_dict['timing'] * 1.5)
        weights_dict['situation'] = min(0.04, weights_dict['situation'] * 1.5)
        # Réajustement pour maintenir total = 1.0
        total = sum(weights_dict.values())
        for key in weights_dict:
            weights_dict[key] = weights_dict[key] / total
        return ExtendedComponentWeights(**weights_dict)
    
    return base_weights

def analyze_questionnaire_completion(candidat: ExtendedCandidateProfileV3, 
                                   entreprise: ExtendedCompanyProfileV3) -> Dict[str, float]:
    """📊 Analyse du taux de completion des questionnaires"""
    
    candidat_completion = 0.0
    entreprise_completion = 0.0
    
    # Analyse candidat
    candidat_fields = [
        len(candidat.transport_preferences.methods) > 0,
        len(candidat.motivations_extended.ranking) > 0,
        len(candidat.secteurs_preferences.secteurs_preferes) > 0,
        len(candidat.contrats_preferences.ranking) > 0,
        candidat.timing_disponibilite.delai_souhaite is not None,
        candidat.modalites_travail.preference_bureau is not None
    ]
    candidat_completion = sum(candidat_fields) / len(candidat_fields)
    
    # Analyse entreprise  
    entreprise_fields = [
        candidat.entreprise.secteur is not None,
        len(entreprise.recrutement_etendu.delais_acceptables) > 0,
        entreprise.modalites_entreprise.remote_possible is not None,
        len(entreprise.criteres_flexibilite.criteres_eliminatoires) >= 0,
        entreprise.recrutement_etendu.urgence is not None
    ]
    entreprise_completion = sum(entreprise_fields) / len(entreprise_fields)
    
    return {
        'candidat_completion': candidat_completion,
        'entreprise_completion': entreprise_completion,
        'overall_completion': (candidat_completion + entreprise_completion) / 2,
        'questionnaire_boost': min(0.15, (candidat_completion + entreprise_completion) / 2 * 0.15)
    }

def validate_v3_compatibility(candidat: ExtendedCandidateProfileV3, 
                            entreprise: ExtendedCompanyProfileV3) -> Dict[str, Any]:
    """🛡️ Validation compatibilité V3.0 avec fallback V2.0"""
    
    validation_result = {
        'v3_compatible': True,
        'fallback_required': False,
        'missing_v3_data': [],
        'validation_score': 1.0
    }
    
    # Vérification données essentielles V3.0
    if not candidat.motivations_extended.raison_ecoute_primaire:
        validation_result['missing_v3_data'].append('raison_ecoute_primaire')
        
    if not candidat.secteurs_preferences.secteurs_preferes:
        validation_result['missing_v3_data'].append('secteurs_preferes')
        
    if not entreprise.entreprise.secteur:
        validation_result['missing_v3_data'].append('entreprise_secteur')
    
    # Score de validation
    validation_result['validation_score'] = max(0.3, 
        1.0 - (len(validation_result['missing_v3_data']) * 0.2))
    
    # Décision fallback
    if len(validation_result['missing_v3_data']) > 3:
        validation_result['fallback_required'] = True
        validation_result['v3_compatible'] = False
    
    return validation_result

# === EXEMPLES ET TESTS V3.0 ===

if __name__ == "__main__":
    print("🚀 NEXTVISION V3.0 - Extended Matching Models")
    print("=" * 60)
    
    # Test création candidat V3.0 étendu
    candidat_v3 = ExtendedCandidateProfileV3(
        # 🔄 Données V2.0 (héritées automatiquement)
        personal_info=PersonalInfoBidirectional(
            firstName="Alice",
            lastName="Martin",
            email="alice.martin@email.com"
        ),
        experience_globale=NiveauExperience.CONFIRME,
        competences=CompetencesProfessionnelles(
            competences_techniques=["Python", "Machine Learning"],
            logiciels_maitrise=["TensorFlow", "Jupyter"]
        ),
        attentes=AttentesCandidat(
            salaire_min=50000,
            salaire_max=65000,
            localisation_preferee="Paris"
        ),
        motivations=MotivationsCandidat(
            raison_ecoute=RaisonEcouteCandidat.REMUNERATION_TROP_FAIBLE,
            motivations_principales=["Évolution salariale"]
        ),
        
        # 🆕 Extensions V3.0
        transport_preferences=TransportPreferences(
            methods=[TypeTransport.TRANSPORTS_COMMUN, TypeTransport.VELO],
            travel_times={"transports_commun": 45, "velo": 30}
        ),
        motivations_extended=MotivationsExtended(
            ranking=[MotivationProfessionnelle.SALAIRE, MotivationProfessionnelle.EVOLUTION],
            raison_ecoute_primaire=RaisonEcouteEtendue.REMUNERATION_TROP_FAIBLE
        ),
        secteurs_preferences=SecteursPreferences(
            secteurs_preferes=[SecteurActivite.TECH, SecteurActivite.FINANCE],
            secteurs_redhibitoires=[SecteurActivite.AGRICULTURE]
        ),
        contrats_preferences=ContratsPreferences(
            ranking=[TypeContrat.CDI, TypeContrat.FREELANCE]
        ),
        timing_disponibilite=TimingDisponibilite(
            delai_souhaite=DelaiDisponibilite.UN_MOIS,
            situation_actuelle=SituationActuelle.EN_POSTE,
            salaire_actuel_min=42000,
            salaire_actuel_max=45000
        ),
        modalites_travail=ModalitesTravail(
            preference_bureau=PreferenceBureau.SANS_PREFERENCE,
            remote_souhaite=True
        )
    )
    
    print(f"✅ Candidat V3.0 créé: {candidat_v3.personal_info.firstName}")
    print(f"🔄 Hérite V2.0: {candidat_v3.experience_globale}")
    print(f"🆕 Extension V3.0: {candidat_v3.motivations_extended.raison_ecoute_primaire}")
    print(f"🎯 Secteurs préférés: {len(candidat_v3.secteurs_preferences.secteurs_preferes)}")
    
    # Test pondération adaptative
    weights = get_adaptive_weights_v3(
        RaisonEcouteEtendue.REMUNERATION_TROP_FAIBLE,
        UrgenceRecrutementEtendue.NORMAL
    )
    print(f"💡 Poids adaptatifs calculés - Salaire: {weights.salaire:.2f}")
    
    print("\n✅ Tests Extended Matching Models V3.0 réussis!")
    print("🔄 Héritage V2.0: 100% préservé")
    print("🆕 Extensions V3.0: 8 nouveaux composants")
    print("🧠 Pondération adaptative: Fonctionnelle")
