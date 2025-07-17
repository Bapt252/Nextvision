"""
🚀 Nextvision V3.0 - Package Scorers V3 CORRIGÉ
===============================================

Sous-package contenant les scorers spécialisés V3.0.
Import direct pour couverture de code optimale.

🔧 CORRECTION COUVERTURE DE CODE:
- Import direct du LocationTransportScorerV3
- Pas de try/except masquant les erreurs
- Exposition complète pour coverage

Author: NEXTEN Team
Version: 3.0.0 - Coverage Fix
"""

# ============================================================================
# IMPORTS DIRECTS SCORERS V3.0 SPÉCIALISÉS
# ============================================================================

# Scorer localisation et transport V3.0
from .location_transport_scorer_v3 import LocationTransportScorerV3

# ============================================================================
# EXPOSITION PUBLIQUE
# ============================================================================

__all__ = [
    'LocationTransportScorerV3'
]

# ============================================================================
# MÉTADONNÉES & VALIDATION
# ============================================================================

def get_scorers_v3_info():
    """Retourne les informations sur les scorers V3 spécialisés."""
    return {
        'version': '3.0.0',
        'package': 'nextvision.services.scorers_v3',
        'scorers': {
            'location_transport_v3': {
                'class': 'LocationTransportScorerV3',
                'description': 'Scorer géolocalisation et transport V3.0',
                'features': [
                    'Calcul distances Google Maps',
                    'Analyse temps transport',
                    'Scoring accessibilité'
                ]
            }
        }
    }

def validate_scorers_v3():
    """Valide que tous les scorers V3 spécialisés sont disponibles."""
    try:
        info = get_scorers_v3_info()
        available_count = 0
        
        for scorer_name in __all__:
            if scorer_name in globals():
                available_count += 1
                print(f"✅ Scorer V3 disponible: {scorer_name}")
            else:
                print(f"❌ Scorer V3 manquant: {scorer_name}")
        
        total_expected = len(__all__)
        print(f"\n📊 Scorers V3: {available_count}/{total_expected} disponibles")
        return available_count == total_expected
        
    except Exception as e:
        print(f"❌ Erreur validation scorers V3: {e}")
        return False

# Version info
__version__ = "3.0.0"
__author__ = "NEXTEN Team"

# ============================================================================
# AUTO-VALIDATION (MODE DEBUG)
# ============================================================================

import os
if os.environ.get('NEXTVISION_DEBUG', '').lower() == 'true':
    print("🔍 Validation automatique scorers V3...")
    validate_scorers_v3()
