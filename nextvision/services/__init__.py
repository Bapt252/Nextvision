"""
🚀 Nextvision Services v3.2.1 - ARCHITECTURE OPTIMISÉE
Services d'intégration GPT Direct + Transport Intelligence pour NEXTEN

Version optimisée après nettoyage architecture - Services essentiels uniquement
Doublons supprimés - Performance améliorée

Author: NEXTEN Team
Version: 3.2.1 Optimized
"""

# 🚀 SERVICE PRINCIPAL: GPT Direct unifié
from .gpt_direct_service import (
    GPTDirectService,
    CVData,
    JobData,
    get_gpt_service,
    parse_cv_direct,
    parse_job_direct
)

# 🌉 Bridge Commitment (service principal conservé)
from .commitment_bridge import CommitmentNextvisionBridge, BridgeRequest, BridgeResponse, BridgeConfig

# 🗺️ Transport Intelligence services
from .google_maps_service import GoogleMapsService
from .transport_calculator import TransportCalculator

# 🎯 Matching & Scoring services (si disponibles)
try:
    from .bidirectional_matcher import BidirectionalMatcher
    from .bidirectional_scorer import BidirectionalScorer
    MATCHING_SERVICES_AVAILABLE = True
except ImportError:
    MATCHING_SERVICES_AVAILABLE = False

# 🧮 Advanced scorers (si disponibles) 
try:
    from .listening_reasons_scorer_v3 import ListeningReasonsScorer
    from .motivations_scorer_v3 import MotivationsScorer
    from .professional_motivations_scorer_v3 import ProfessionalMotivationsScorer
    ADVANCED_SCORERS_AVAILABLE = True
except ImportError:
    ADVANCED_SCORERS_AVAILABLE = False

__all__ = [
    # 🚀 Services GPT Direct (PRINCIPAL)
    "GPTDirectService",
    "CVData", 
    "JobData",
    "get_gpt_service",
    "parse_cv_direct",
    "parse_job_direct",
    
    # 🌉 Bridge services (conservés)
    "CommitmentNextvisionBridge",
    "BridgeRequest",
    "BridgeResponse", 
    "BridgeConfig",
    
    # 🗺️ Transport Intelligence
    "GoogleMapsService",
    "TransportCalculator"
]

# Ajout conditionnel des services optionnels
if MATCHING_SERVICES_AVAILABLE:
    __all__.extend(["BidirectionalMatcher", "BidirectionalScorer"])

if ADVANCED_SCORERS_AVAILABLE:
    __all__.extend([
        "ListeningReasonsScorer",
        "MotivationsScorer", 
        "ProfessionalMotivationsScorer"
    ])

# 🎯 Factory functions optimisées
def create_gpt_service():
    """🚀 Créer service GPT Direct (recommandé)"""
    return get_gpt_service()

def create_bridge():
    """🌉 Créer bridge Commitment (legacy)"""
    config = BridgeConfig()
    return CommitmentNextvisionBridge(config)

def create_transport_service():
    """🗺️ Créer service transport"""
    return GoogleMapsService()

# 📊 Status des services
def get_services_status():
    """📊 Status de tous les services disponibles"""
    return {
        "gpt_direct": True,
        "commitment_bridge": True,
        "transport_intelligence": True,
        "matching_services": MATCHING_SERVICES_AVAILABLE,
        "advanced_scorers": ADVANCED_SCORERS_AVAILABLE,
        "version": "3.2.1",
        "architecture": "optimized"
    }

__version__ = "3.2.1"
