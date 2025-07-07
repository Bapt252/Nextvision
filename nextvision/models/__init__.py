"""
📊 Nextvision Models Module  
Transport & Questionnaire Models for Google Maps Intelligence (Prompt 2)

Author: NEXTEN Team
Version: 2.0.0
"""

# Modèles existants
from .questionnaire_advanced import (
    QuestionnaireComplet,
    DisponibiliteType,
    RaisonEcoute,
    EnvironnementTravail,
    TypeContrat,
    MoyenTransport,
    TransportPreferences,
    TimingInfo,
    SecteursPreferences,
    ContratsPreferences,
    MotivationsClassees,
    RemunerationAttentes,
    QuestionnaireMetadata
)

# 🗺️ Nouveaux modèles Google Maps Intelligence (Prompt 2)
from .transport_models import (
    # Enums
    GoogleMapsMode,
    TrafficModel,
    TransitMode,
    TransportQuality,
    
    # Core Models
    GeocodeResult,
    RouteStep,
    TransportRoute,
    TransportConstraint,
    TransportAnalysis,
    
    # Profils & Info
    CandidatTransportProfile,
    JobTransportInfo,
    
    # Résultats
    TransportMatchingResult,
    TransportFilteringReport,
    
    # Helpers
    create_default_candidat_profile,
    DEFAULT_TRANSPORT_CONSTRAINTS
)

__all__ = [
    # Questionnaire existant
    "QuestionnaireComplet",
    "DisponibiliteType",
    "RaisonEcoute", 
    "EnvironnementTravail",
    "TypeContrat",
    "MoyenTransport",
    "TransportPreferences",
    "TimingInfo",
    "SecteursPreferences",
    "ContratsPreferences",
    "MotivationsClassees",
    "RemunerationAttentes",
    "QuestionnaireMetadata",
    
    # Transport Models (Prompt 2)
    "GoogleMapsMode",
    "TrafficModel",
    "TransitMode",
    "TransportQuality",
    "GeocodeResult",
    "RouteStep", 
    "TransportRoute",
    "TransportConstraint",
    "TransportAnalysis",
    "CandidatTransportProfile",
    "JobTransportInfo",
    "TransportMatchingResult",
    "TransportFilteringReport",
    "create_default_candidat_profile",
    "DEFAULT_TRANSPORT_CONSTRAINTS"
]
