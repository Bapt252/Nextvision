"""
🎯 Modèles Avancés NEXTEN - Exports
Questionnaires complets Commitment- avec pondération adaptative

Author: NEXTEN Team
Version: 1.0.0
Integration: Commitment- → Nextvision Bridge
"""

# === QUESTIONNAIRES AVANCÉS ===
from .questionnaire_advanced import (
    QuestionnaireCompletAdvanced,
    TimingDisponibilite,
    PreferencesSectorielles,
    ConfigTransport,
    PreferencesContrats,
    RankingMotivations,
    MotivationClassee,
    PreavisConfig,
    
    # Énumérations
    DisponibiliteEnum,
    PourquoiEcouteEnum,
    EnvironnementTravailEnum,
    TypeContratEnum,
    MoyenTransportEnum,
    MotivationEnum
)

# === CANDIDAT COMPLET ===
from .candidate_complete import (
    CandidatCompletNexfen,
    CVDataEnriched,
    CompetenceTechnique,
    ExperienceProfessionnelle,
    FormationAcademique,
    LangueCompetence,
    
    # Énumérations
    NiveauEnum,
    TypeFormationEnum,
    StatutActiviteEnum
)

# === JOB COMPLET ===
from .job_complete import (
    JobDataAdvanced,
    CompetenceRequise,
    MissionPrincipale,
    AvantagesSociaux,
    EnvironnementEntreprise,
    LocalisationPoste,
    ProcessusRecrutement,
    
    # Énumérations
    TailleEntrepriseEnum,
    TypeRecrutementEnum,
    NiveauRequis,
    FlexibiliteTravailEnum
)

# === ANALYSE SECTORIELLE ===
from .sectoral_analysis import (
    AnalyseSectorielleCandidatte,
    SecteurDetaille,
    ExperienceSectorielle,
    PreferenceSectorielle,
    
    # Énumérations
    CategorieSecteurEnum,
    NiveauAffiniteEnum,
    TypeExperienceEnum,
    
    # Fonctions utilitaires
    normaliser_secteur,
    suggerer_secteurs_similaires,
    SECTEURS_STANDARDS
)

# === PRÉFÉRENCES CONTRATS ===
from .contract_preferences import (
    AnalysePreferencesContrats,
    ContractPreference,
    FlexibiliteTravailEnum as FlexibiliteContractuelle,
    FreelanceConfig,
    
    # Énumérations
    StatutJuridiqueEnum,
    AvantageContratEnum,
    RisqueContratEnum
)

# === MOTIVATIONS CLASSÉES ===
from .motivation_ranking import (
    ProfilMotivationnel,
    MotivationDetaillee,
    
    # Énumérations
    IntensiteMotivationEnum,
    CategorieMotivationEnum,
    ImpactCarriereEnum
)

# === EXPORTS GROUPÉS ===

# Modèles principaux
ADVANCED_MODELS = [
    QuestionnaireCompletAdvanced,
    CandidatCompletNexfen,
    JobDataAdvanced,
    AnalyseSectorielleCandidatte,
    AnalysePreferencesContrats,
    ProfilMotivationnel
]

# Composants de questionnaire
QUESTIONNAIRE_COMPONENTS = [
    TimingDisponibilite,
    PreferencesSectorielles,
    ConfigTransport,
    PreferencesContrats,
    RankingMotivations,
    MotivationClassee
]

# Composants de candidat
CANDIDATE_COMPONENTS = [
    CVDataEnriched,
    CompetenceTechnique,
    ExperienceProfessionnelle,
    FormationAcademique,
    LangueCompetence
]

# Composants de job
JOB_COMPONENTS = [
    CompetenceRequise,
    MissionPrincipale,
    AvantagesSociaux,
    EnvironnementEntreprise,
    LocalisationPoste,
    ProcessusRecrutement
]

# Énumérations principales
CORE_ENUMS = [
    PourquoiEcouteEnum,
    MotivationEnum,
    TypeContratEnum,
    EnvironnementTravailEnum,
    NiveauEnum,
    CategorieSecteurEnum,
    IntensiteMotivationEnum
]

# Fonctions utilitaires
UTILITY_FUNCTIONS = [
    normaliser_secteur,
    suggerer_secteurs_similaires
]

__all__ = [
    # === MODÈLES PRINCIPAUX ===
    'QuestionnaireCompletAdvanced',
    'CandidatCompletNexfen', 
    'JobDataAdvanced',
    'AnalyseSectorielleCandidatte',
    'AnalysePreferencesContrats',
    'ProfilMotivationnel',
    
    # === COMPOSANTS QUESTIONNAIRE ===
    'TimingDisponibilite',
    'PreferencesSectorielles',
    'ConfigTransport',
    'PreferencesContrats',
    'RankingMotivations',
    'MotivationClassee',
    'PreavisConfig',
    
    # === COMPOSANTS CANDIDAT ===
    'CVDataEnriched',
    'CompetenceTechnique',
    'ExperienceProfessionnelle',
    'FormationAcademique',
    'LangueCompetence',
    
    # === COMPOSANTS JOB ===
    'CompetenceRequise',
    'MissionPrincipale',
    'AvantagesSociaux',
    'EnvironnementEntreprise',
    'LocalisationPoste',
    'ProcessusRecrutement',
    
    # === COMPOSANTS ANALYSE SECTORIELLE ===
    'SecteurDetaille',
    'ExperienceSectorielle',
    'PreferenceSectorielle',
    
    # === COMPOSANTS CONTRATS ===
    'ContractPreference',
    'FlexibiliteTravailEnum',
    'FreelanceConfig',
    
    # === COMPOSANTS MOTIVATIONS ===
    'MotivationDetaillee',
    
    # === ÉNUMÉRATIONS ===
    'DisponibiliteEnum',
    'PourquoiEcouteEnum',
    'EnvironnementTravailEnum',
    'TypeContratEnum',
    'MoyenTransportEnum',
    'MotivationEnum',
    'NiveauEnum',
    'TypeFormationEnum',
    'StatutActiviteEnum',
    'TailleEntrepriseEnum',
    'TypeRecrutementEnum',
    'NiveauRequis',
    'FlexibiliteTravailEnum',
    'CategorieSecteurEnum',
    'NiveauAffiniteEnum',
    'TypeExperienceEnum',
    'StatutJuridiqueEnum',
    'AvantageContratEnum',
    'RisqueContratEnum',
    'IntensiteMotivationEnum',
    'CategorieMotivationEnum',
    'ImpactCarriereEnum',
    
    # === FONCTIONS UTILITAIRES ===
    'normaliser_secteur',
    'suggerer_secteurs_similaires',
    'SECTEURS_STANDARDS',
    
    # === EXPORTS GROUPÉS ===
    'ADVANCED_MODELS',
    'QUESTIONNAIRE_COMPONENTS',
    'CANDIDATE_COMPONENTS',
    'JOB_COMPONENTS',
    'CORE_ENUMS',
    'UTILITY_FUNCTIONS'
]

# Métadonnées du module
__version__ = "1.0.0"
__author__ = "NEXTEN Team"
__description__ = "Modèles avancés pour questionnaires complets Commitment- avec pondération adaptative"
__integration__ = "Commitment- → Nextvision Bridge"
