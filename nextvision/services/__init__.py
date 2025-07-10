"""
🌉 Services Nextvision V3.1 Hiérarchique
Services d'intégration et bridge pour NEXTEN avec détection hiérarchique

Author: NEXTEN Team
Version: 3.1.0
"""

# Services existants V3.0
from .commitment_bridge import CommitmentNextvisionBridge, BridgeRequest, BridgeResponse, BridgeConfig
from .enhanced_commitment_bridge_v3_simplified import (
    EnhancedCommitmentBridgeV3Simplified, 
    BridgeMetrics, 
    SimplifiedBridgeFactory
)

# 🆕 Services hiérarchiques V3.1
from .hierarchical_detector import (
    HierarchicalDetector, 
    HierarchicalScoring, 
    HierarchicalLevel, 
    HierarchicalMatch
)
from .enhanced_commitment_bridge_v3_hierarchical import (
    EnhancedCommitmentBridgeV3Hierarchical,
    HierarchicalBridgeFactory,
    HierarchicalBridgeMetrics
)

# Vos imports existants (préservés)
from .google_maps_service import GoogleMapsService
from .transport_calculator import TransportCalculator
from .enhanced_commitment_bridge_v3_integrated import EnhancedCommitmentBridgeV3Integrated

__all__ = [
    # Services V3.0 (compatibilité)
    "CommitmentNextvisionBridge",
    "BridgeRequest", 
    "BridgeResponse",
    "BridgeConfig",
    "EnhancedCommitmentBridgeV3Simplified",
    "BridgeMetrics",
    "SimplifiedBridgeFactory",
    
    # 🆕 Services V3.1 Hiérarchiques
    "HierarchicalDetector",
    "HierarchicalScoring", 
    "HierarchicalLevel",
    "HierarchicalMatch",
    "EnhancedCommitmentBridgeV3Hierarchical",
    "HierarchicalBridgeFactory",
    "HierarchicalBridgeMetrics",
    
    # Vos services existants (préservés)
    "GoogleMapsService",
    "TransportCalculator", 
    "EnhancedCommitmentBridgeV3Integrated"
]

# 🎯 Shortcuts pour utilisation simplifiée
def create_bridge_v30():
    """Crée un bridge V3.0 standard (compatibilité)"""
    return SimplifiedBridgeFactory.create_bridge()

def create_bridge_v31():
    """Crée un bridge V3.1 avec système hiérarchique"""
    return HierarchicalBridgeFactory.create_hierarchical_bridge()

def create_bridge_auto():
    """Crée un bridge automatique (V3.1 avec fallback V3.0)"""
    try:
        return create_bridge_v31()
    except Exception:
        return create_bridge_v30()

# Version par défaut recommandée
create_bridge = create_bridge_v31  # V3.1 par défaut

__version__ = "3.1.0"
