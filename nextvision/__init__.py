"""
🎯 Nextvision - Main Module
Version 2.0.0 - Google Maps Intelligence (Prompt 2)

Author: NEXTEN Team
Features: Adaptive Weighting + Geospatial Intelligence + Transport Pre-filtering
"""

from .services import *
from .engines import *
from .models import *
from .config import *
from .utils import *

__version__ = "2.0.0"
__title__ = "Nextvision"
__description__ = "Algorithme de matching IA adaptatif avec intelligence géospatiale"
__author__ = "NEXTEN Team"

# Export des innovations principales
__innovations__ = [
    "Pondération Adaptative Contextuelle",
    "Intelligence Géospatiale Google Maps",
    "Pré-filtering Transport Automatique", 
    "Score Localisation Enrichi",
    "Cache Intelligent Multi-niveaux",
    "Bridge Zéro Redondance Commitment-"
]

# Export des features Prompt 2
__prompt2_features__ = [
    "Google Maps Intelligence",
    "Multi-modal Transport Analysis",
    "Pre-filtering Engine",
    "Enhanced Location Scoring",
    "Intelligent Caching",
    "Performance Monitoring",
    "Real-world Testing Framework"
]

__all__ = [
    "__version__",
    "__title__", 
    "__description__",
    "__author__",
    "__innovations__",
    "__prompt2_features__"
]
