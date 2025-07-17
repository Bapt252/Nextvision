"""
🚀 Nextvision V3.0 - Package Principal CORRIGÉ
===============================================

Système de matching intelligent candidat-entreprise basé sur l'IA.
Version 3.0.0 Enhanced avec 12 scorers opérationnels.

🔧 CORRECTION COUVERTURE DE CODE:
- Suppression des try/except qui masquaient les erreurs d'import
- Import direct des modules pour permettre à coverage de les détecter
- Gestion d'erreurs explicite pour debugging

Author: NEXTEN Team
Version: 3.0.0 - Enhanced Performance
"""

__version__ = "3.0.0"
__author__ = "NEXTEN Team"

# ============================================================================
# IMPORTS DIRECTS POUR COUVERTURE DE CODE
# ============================================================================

# Import des classes principales pour faciliter l'accès
# IMPORTANT: Pas de try/except pour permettre à coverage de détecter les modules
from nextvision.services.enhanced_bidirectional_scorer_v3 import EnhancedBidirectionalScorerV3
from nextvision.services.bidirectional_scorer import BidirectionalScorer

# Import des scorers V3.0 supplémentaires  
from nextvision.services.motivations_scorer_v3 import MotivationsScorerV3
from nextvision.services.listening_reasons_scorer_v3 import ListeningReasonsScorerV3
from nextvision.services.professional_motivations_scorer_v3 import ProfessionalMotivationsScorerV3

# Import des scorers du sous-package scorers_v3
from nextvision.services.scorers_v3.location_transport_scorer_v3 import LocationTransportScorerV3

# Import des services utilitaires
from nextvision.services.google_maps_service import GoogleMapsService
from nextvision.services.transport_calculator import TransportCalculator

__all__ = [
    # Classes principales
    'EnhancedBidirectionalScorerV3',
    'BidirectionalScorer',
    
    # Scorers V3.0
    'MotivationsScorerV3',
    'ListeningReasonsScorerV3', 
    'ProfessionalMotivationsScorerV3',
    'LocationTransportScorerV3',
    
    # Services utilitaires
    'GoogleMapsService',
    'TransportCalculator'
]

# ============================================================================
# MÉTADONNÉES POUR DEBUGGING
# ============================================================================

def get_available_scorers():
    """Retourne la liste des scorers disponibles pour validation."""
    return {
        'enhanced_bidirectional_v3': EnhancedBidirectionalScorerV3,
        'bidirectional': BidirectionalScorer,
        'motivations_v3': MotivationsScorerV3,
        'listening_reasons_v3': ListeningReasonsScorerV3,
        'professional_motivations_v3': ProfessionalMotivationsScorerV3,
        'location_transport_v3': LocationTransportScorerV3,
        'google_maps': GoogleMapsService,
        'transport_calculator': TransportCalculator
    }

def validate_imports():
    """Valide que tous les modules sont correctement importés."""
    try:
        scorers = get_available_scorers()
        print(f"✅ {len(scorers)} modules Nextvision importés avec succès")
        for name, cls in scorers.items():
            print(f"  📦 {name}: {cls.__name__}")
        return True
    except Exception as e:
        print(f"❌ Erreur validation imports: {e}")
        return False

# ============================================================================
# AUTO-VALIDATION AU CHARGEMENT (DEBUG MODE)
# ============================================================================

import os
if os.environ.get('NEXTVISION_DEBUG', '').lower() == 'true':
    print("🔍 Mode debug activé - Validation des imports...")
    validate_imports()
