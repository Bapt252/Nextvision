"""
🚀 Nextvision V3.0 - Scorers V3 Package (PROMPT 7)
Package des scorers révolutionnés avec Intelligence V3.0

Nouveaux scorers timing & contrats & environnement :
- AvailabilityTimingScorer : Compatibilité timing/disponibilité
- ContractTypesScorer : Ranking préférences contrat
- WorkEnvironmentScorer : Environnement travail intelligent

Author: NEXTEN Team
Version: 3.0.0 - Enhanced Intelligence
"""

from .location_transport_scorer_v3 import LocationTransportScorerV3
from .availability_timing_scorer import AvailabilityTimingScorer
from .contract_types_scorer import ContractTypesScorer
from .work_environment_scorer import WorkEnvironmentScorer

__version__ = "3.0.0"
__all__ = [
    "LocationTransportScorerV3",
    "AvailabilityTimingScorer", 
    "ContractTypesScorer",
    "WorkEnvironmentScorer"
]
