"""
🚀 Nextvision V3.0 - Scorers V3 Package (PROMPT 10)
Package des scorers révolutionnés avec Intelligence V3.0

Scorers opérationnels (8/12) :
- LocationTransportScorerV3 : Localisation + transport intelligent (9% poids)
- AvailabilityTimingScorer : Compatibilité timing/disponibilité (4% poids)  
- ContractTypesScorer : Ranking préférences contrat (5% poids)
- WorkEnvironmentScorer : Environnement travail intelligent (4% poids)
- MotivationsScorer : Correspondance aspirations candidat (8% poids)
- ListeningReasonScorer : Cohérence raisons d'écoute (2% poids)
- SectorCompatibilityScorer : Compatibilité secteur candidat-entreprise (6% poids)
- SalaryProgressionScorer : Évolution salariale candidat vs opportunités (3% poids) ✨ NEW

Author: NEXTEN Team
Version: 3.0.0 - Enhanced Intelligence + Salary Progression
"""

from .location_transport_scorer_v3 import LocationTransportScorerV3
from .availability_timing_scorer import AvailabilityTimingScorer
from .contract_types_scorer import ContractTypesScorer
from .work_environment_scorer import WorkEnvironmentScorer
from .motivations_scorer import MotivationsScorer
from .listening_reason_scorer import ListeningReasonScorer
from .sector_compatibility_scorer import SectorCompatibilityScorer
from .salary_progression_scorer import SalaryProgressionScorer

__version__ = "3.0.0"
__all__ = [
    "LocationTransportScorerV3",
    "AvailabilityTimingScorer", 
    "ContractTypesScorer",
    "WorkEnvironmentScorer",
    "MotivationsScorer",
    "ListeningReasonScorer",
    "SectorCompatibilityScorer",
    "SalaryProgressionScorer"
]
