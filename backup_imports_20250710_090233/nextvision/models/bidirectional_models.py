"""
🎯 Nextvision v2.0 - Modèles Bidirectionnels pour Matching IA Adaptatif

Architecture révolutionnaire pour matching candidat ↔ entreprise avec :
- Pondération adaptative bidirectionnelle
- 4 composants business prioritaires (Sémantique 35%, Salaire 25%, Expérience 25%, Localisation 15%)
- Intégration ChatGPT Commitment- existant
- Support questionnaires candidat (4 parties) + entreprise (5 étapes)

Author: NEXTEN Team  
Version: 2.0.0 - Bidirectional Matching
"""

from pydantic import BaseModel, Field, model_validator
from typing import Dict, List, Optional, Union, Literal
from enum import Enum
from datetime import datetime
import json

# === ENUMS BIDIRECTIONNELS ===

class RaisonEcouteCandidat(str, Enum):
    """Raisons d'écoute candidat pour pondération adaptative"""
    REMUNERATION_TROP_FAIBLE = "Rémunération trop faible"
    POSTE_NE_COINCIDE_PAS = "Poste ne coïncide pas avec poste proposé"
    POSTE_TROP_LOIN = "Poste trop loin de mon domicile"
    MANQUE_FLEXIBILITE = "Manque de flexibilité"
    MANQUE_PERSPECTIVES = "Manque de perspectives d'évolution"

class UrgenceRecrutement(str, Enum):
    """Urgence entreprise pour pondération adaptative"""
    CRITIQUE = "Critique (< 2 semaines)"
    URGENT = "Urgent (< 1 mois)"
    NORMAL = "Normal (1-3 mois)"
    LONG_TERME = "Long terme (> 3 mois)"

class TypeContrat(str, Enum):
    CDI = "CDI"
    CDD = "CDD"
    FREELANCE = "Freelance"
    STAGE = "Stage"
    ALTERNANCE = "Alternance"

class NiveauExperience(str, Enum):
    DEBUTANT = "0-2 ans"
    JUNIOR = "2-5 ans"
    CONFIRME = "5-10 ans"
    SENIOR = "10+ ans"

# === CANDIDAT BIDIRECTIONNEL ===

class PersonalInfoBidirectional(BaseModel):
    """Informations personnelles candidat - compatible Enhanced Universal Parser v4.0"""
    firstName: str
    lastName: str
    email: str
    phone: Optional[str] = None
    age: Optional[int] = None
    linkedin_url: Optional[str] = None

class ExperienceProfessionnelle(BaseModel):
    """Expérience professionnelle détaillée"""
    poste: str
    entreprise: str
    duree: str  # Format: "2 ans - 5 ans" (compatible ChatGPT Commitment-)
    description: Optional[str] = None
    competences_acquises: List[str] = []

class CompetencesProfessionnelles(BaseModel):
    """Compétences extraites par Enhanced Universal Parser v4.0"""
    competences_techniques: List[str] = []  # Format: ["Maîtrise du logiciel comptable CEGID", "Gestion comptable et fiscale"]
    logiciels_maitrise: List[str] = []
    langues: Dict[str, str] = {}  # {"Français": "Natif", "Anglais": "Courant"}
    certifications: List[str] = []

class AttentesCandidat(BaseModel):
    """Attentes et préférences candidat"""
    salaire_min: int
    salaire_max: int
    salaire_actuel: Optional[int] = None
    localisation_preferee: str
    distance_max_km: Optional[int] = 50
    remote_accepte: bool = False
    secteurs_preferes: List[str] = []
    types_contrat: List[TypeContrat] = [TypeContrat.CDI]
    
class MotivationsCandidat(BaseModel):
    """Motivations et raisons d'écoute pour pondération adaptative"""
    raison_ecoute: RaisonEcouteCandidat
    motivations_principales: List[str] = []
    elements_bloquants_actuels: List[str] = []
    objectifs_carriere: Optional[str] = None

class BiDirectionalCandidateProfile(BaseModel):
    """🎯 Profil candidat bidirectionnel avec pondération adaptative"""
    
    # Partie 1 : Informations personnelles
    personal_info: PersonalInfoBidirectional
    
    # Partie 2 : Expérience et compétences (Enhanced Universal Parser v4.0)
    experience_globale: NiveauExperience
    experiences_detaillees: List[ExperienceProfessionnelle] = []
    competences: CompetencesProfessionnelles
    formation: Optional[str] = None
    
    # Partie 3 : Attentes et préférences
    attentes: AttentesCandidat
    
    # Partie 4 : Motivations et pondération adaptative
    motivations: MotivationsCandidat
    
    # Métadonnées parsing
    parsing_source: Literal["manual", "enhanced_parser_v4", "chatgpt_commitment"] = "manual"
    parsed_at: datetime = Field(default_factory=datetime.now)
    confidence_score: Optional[float] = None

# === ENTREPRISE BIDIRECTIONNELLE ===

class InformationsEntreprise(BaseModel):
    """Informations entreprise de base"""
    nom: str
    secteur: str
    taille: Optional[str] = None  # "PME", "ETI", "Grand Groupe"
    localisation: str
    description: Optional[str] = None
    site_web: Optional[str] = None

class DescriptionPoste(BaseModel):
    """Description de poste - compatible parsing ChatGPT Commitment-"""
    titre: str
    localisation: str
    type_contrat: TypeContrat = TypeContrat.CDI
    salaire_min: Optional[int] = None  # Format: 35000 (pour "35K à 38K annuels")
    salaire_max: Optional[int] = None  # Format: 38000
    description: Optional[str] = None
    
    # Extraction ChatGPT format spécifique
    missions_principales: List[str] = []
    competences_requises: List[str] = []  # Format: ["Maîtrise du logiciel comptable CEGID", "Gestion comptable et fiscale"]

class ExigencesPoste(BaseModel):
    """Exigences et critères de sélection"""
    experience_requise: str  # Format: "5 ans - 10 ans" (compatible ChatGPT Commitment-)
    competences_obligatoires: List[str] = []
    competences_souhaitees: List[str] = []
    formations_requises: List[str] = []
    langues_requises: Dict[str, str] = {}

class ConditionsTravail(BaseModel):
    """Conditions de travail et avantages"""
    horaires: Optional[str] = None
    remote_possible: bool = False
    avantages: List[str] = []
    environnement_travail: Optional[str] = None

class CriteresRecrutement(BaseModel):
    """Critères de sélection et urgence pour pondération adaptative"""
    urgence: UrgenceRecrutement = UrgenceRecrutement.NORMAL
    criteres_prioritaires: List[str] = []  # ["expérience", "compétences_techniques", "localisation"]
    criteres_eliminatoires: List[str] = []
    nombre_postes: int = 1
    
class BiDirectionalCompanyProfile(BaseModel):
    """🏢 Profil entreprise bidirectionnel avec pondération adaptative"""
    
    # Étape 1 : Informations entreprise
    entreprise: InformationsEntreprise
    
    # Étape 2 : Description du poste (ChatGPT parsing)
    poste: DescriptionPoste
    
    # Étape 3 : Exigences et compétences
    exigences: ExigencesPoste
    
    # Étape 4 : Conditions de travail
    conditions: ConditionsTravail
    
    # Étape 5 : Critères de recrutement et urgence
    recrutement: CriteresRecrutement
    
    # Métadonnées parsing ChatGPT
    parsing_source: Literal["manual", "chatgpt_commitment", "fiche_poste_upload"] = "manual"
    fiche_poste_originale: Optional[str] = None  # Contenu original de la fiche de poste
    badges_auto_rempli: List[str] = []  # ["Auto-rempli"] pour suivi parsing
    parsed_at: datetime = Field(default_factory=datetime.now)
    confidence_score: Optional[float] = None

# === MATCHING BIDIRECTIONNEL ===

class ComponentWeights(BaseModel):
    """Poids des 4 composants business prioritaires"""
    semantique: float = Field(default=0.35, ge=0.0, le=1.0)  # 35% - Correspondance CV ↔ Fiche de poste
    salaire: float = Field(default=0.25, ge=0.0, le=1.0)     # 25% - Budget entreprise vs attentes candidat  
    experience: float = Field(default=0.25, ge=0.0, le=1.0)  # 25% - Années d'expérience requises (corrigé de 0.20 à 0.25)
    localisation: float = Field(default=0.15, ge=0.0, le=1.0) # 15% - Impact géographique (Google Maps Intelligence)
    
    @model_validator(mode='after')
    def weights_sum_to_one(self):
        """Validation que la somme des poids = 1.0"""
        total = self.semantique + self.salaire + self.experience + self.localisation
        if abs(total - 1.0) > 0.01:  # Tolérance 1%
            raise ValueError(f"La somme des poids doit être égale à 1.0, actuellement: {total}")
        return self

class AdaptiveWeightingConfig(BaseModel):
    """Configuration pondération adaptative bidirectionnelle"""
    candidat_weights: ComponentWeights
    entreprise_weights: ComponentWeights
    raison_candidat: RaisonEcouteCandidat
    urgence_entreprise: UrgenceRecrutement
    reasoning_candidat: str
    reasoning_entreprise: str

class MatchingComponentScores(BaseModel):
    """Scores détaillés par composant business"""
    semantique_score: float = Field(ge=0.0, le=1.0)
    semantique_details: Dict = {}
    
    salaire_score: float = Field(ge=0.0, le=1.0) 
    salaire_details: Dict = {}
    
    experience_score: float = Field(ge=0.0, le=1.0)
    experience_details: Dict = {}
    
    localisation_score: float = Field(ge=0.0, le=1.0)
    localisation_details: Dict = {}  # Google Maps Intelligence

class BiDirectionalMatchingRequest(BaseModel):
    """🎯 Requête de matching bidirectionnel candidat ↔ entreprise"""
    candidat: BiDirectionalCandidateProfile
    entreprise: BiDirectionalCompanyProfile
    
    # Configuration matching
    force_adaptive_weighting: bool = True
    use_google_maps_intelligence: bool = True
    strict_mode: bool = False
    
    # Métadonnées
    matching_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class BiDirectionalMatchingResponse(BaseModel):
    """📊 Réponse de matching bidirectionnel avec détails complets"""
    
    # Résultats matching
    matching_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    compatibility: Literal["excellent", "good", "average", "poor", "incompatible"]
    
    # Scores détaillés par composant
    component_scores: MatchingComponentScores
    
    # Pondération adaptative appliquée
    adaptive_weighting: AdaptiveWeightingConfig
    
    # Recommandations
    recommandations_candidat: List[str] = []
    recommandations_entreprise: List[str] = []
    points_forts: List[str] = []
    points_attention: List[str] = []
    
    # Performance et métadonnées
    processing_time_ms: float
    timestamp: datetime = Field(default_factory=datetime.now)
    algorithm_version: str = "2.0.0-bidirectional"

# === UTILITAIRES ===

class ChatGPTCommitmentFormat(BaseModel):
    """Format d'échange avec le système ChatGPT de Commitment-"""
    
    # Format spécifique mentionné par l'utilisateur
    experience_format: str = Field(
        default="5 ans - 10 ans",
        description="Format d'expérience compatible ChatGPT Commitment-"
    )
    
    competences_format: List[str] = Field(
        default=["Maîtrise du logiciel comptable CEGID", "Gestion comptable et fiscale"],
        description="Format de compétences avec badges Auto-rempli"
    )
    
    extraction_fields: Dict = Field(
        default={
            "titre": "string",
            "localisation": "string", 
            "contrat": "CDI",
            "salaire": "35K à 38K annuels"
        },
        description="Champs d'extraction automatique"
    )

def convert_chatgpt_to_bidirectional(chatgpt_data: Dict) -> BiDirectionalCompanyProfile:
    """🔄 Convertit données ChatGPT Commitment- vers format bidirectionnel"""
    # Implémentation de la conversion
    # TODO: Implémenter la logique de conversion complète
    pass

def convert_enhanced_parser_to_bidirectional(parser_data: Dict) -> BiDirectionalCandidateProfile:
    """🔄 Convertit données Enhanced Universal Parser v4.0 vers format bidirectionnel"""
    # Implémentation de la conversion
    # TODO: Implémenter la logique de conversion complète
    pass

# === EXEMPLES DE VALIDATION ===

if __name__ == "__main__":
    # Test des modèles avec données réelles mentionnées
    
    # Exemple candidat
    candidat_exemple = BiDirectionalCandidateProfile(
        personal_info=PersonalInfoBidirectional(
            firstName="John",
            lastName="Doe", 
            email="john.doe@exemple.com",
            phone="+33 6 12 34 56 78"
        ),
        experience_globale=NiveauExperience.CONFIRME,
        competences=CompetencesProfessionnelles(
            competences_techniques=["Maîtrise du logiciel comptable CEGID", "Gestion comptable et fiscale"],
            logiciels_maitrise=["CEGID", "Excel", "SAP"],
            langues={"Français": "Natif", "Anglais": "Courant"}
        ),
        attentes=AttentesCandidat(
            salaire_min=35000,
            salaire_max=45000,
            localisation_preferee="Paris 8ème",
            distance_max_km=30
        ),
        motivations=MotivationsCandidat(
            raison_ecoute=RaisonEcouteCandidat.REMUNERATION_TROP_FAIBLE,
            motivations_principales=["Évolution salariale", "Nouvelles responsabilités"]
        )
    )
    
    # Exemple entreprise (poste "Comptable Unique H/F" mentionné)
    entreprise_exemple = BiDirectionalCompanyProfile(
        entreprise=InformationsEntreprise(
            nom="Cabinet Comptable XYZ",
            secteur="Comptabilité",
            localisation="Paris 8ème"
        ),
        poste=DescriptionPoste(
            titre="Comptable Unique H/F",
            localisation="Paris 8ème",
            type_contrat=TypeContrat.CDI,
            salaire_min=35000,
            salaire_max=38000,
            competences_requises=["Maîtrise du logiciel comptable CEGID", "Gestion comptable et fiscale"]
        ),
        exigences=ExigencesPoste(
            experience_requise="5 ans - 10 ans"  # Format ChatGPT Commitment-
        ),
        recrutement=CriteresRecrutement(
            urgence=UrgenceRecrutement.URGENT,
            criteres_prioritaires=["expérience", "compétences_techniques"]
        ),
        badges_auto_rempli=["Auto-rempli"]  # Badge ChatGPT
    )
    
    print("✅ Modèles bidirectionnels validés avec succès !")
    print(f"📊 Candidat: {candidat_exemple.personal_info.firstName} {candidat_exemple.personal_info.lastName}")
    print(f"🏢 Entreprise: {entreprise_exemple.entreprise.nom} - {entreprise_exemple.poste.titre}")
    print(f"🎯 Pondération adaptative: {candidat_exemple.motivations.raison_ecoute.value} + {entreprise_exemple.recrutement.urgence.value}")
