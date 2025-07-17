"""
🚀 Nextvision V3.0 - Package Principal
=====================================

Système de matching intelligent candidat-entreprise basé sur l'IA.
Version 3.0.0 Enhanced avec 12 scorers opérationnels.

Author: NEXTEN Team
Version: 3.0.0 - Enhanced Performance
"""

__version__ = "3.0.0"
__author__ = "NEXTEN Team"

# Import des classes principales pour faciliter l'accès
try:
    from nextvision.services.enhanced_bidirectional_scorer_v3 import EnhancedBidirectionalScorerV3
except ImportError:
    EnhancedBidirectionalScorerV3 = None

try:
    from nextvision.services.bidirectional_scorer import BidirectionalScorer
except ImportError:
    BidirectionalScorer = None

__all__ = [
    'EnhancedBidirectionalScorerV3',
    'BidirectionalScorer'
]
