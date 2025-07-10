"""
🎯 Nextvision V3.0 - Extended Bidirectional Models
==================================================

Extension des modèles bidirectionnels V2.0 → V3.0 avec :
- ExtendedComponentWeights : 4 → 12 composants de matching
- Poids corrigés pour totaliser exactement 1.0
- Rétrocompatibilité totale avec modèles V2.0

Author: NEXTEN Team
Version: 3.0.0 - Extended Bidirectional Models
"""

from pydantic import BaseModel, Field, model_validator
from typing import Dict, List, Optional, Union, Literal, Any
from enum import Enum
from datetime import datetime, date
import json
import sys
import os

# Import relatif correct
try:
    from .bidirectional_models import (
        BiDirectionalCandidateProfile,
        BiDirectionalCompanyProfile,
        ComponentWeights,
        AdaptiveWeightingConfig,
        RaisonEcouteCandidat,
        UrgenceRecrutement,
        TypeContrat,
        NiveauExperience
    )
except ImportError:
    # Fallback pour tests directs
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from nextvision.models.bidirectional_models import (
        BiDirectionalCandidateProfile,
        BiDirectionalCompanyProfile,
        ComponentWeights,
        AdaptiveWeightingConfig,
        RaisonEcouteCandidat,
        UrgenceRecrutement,
        TypeContrat,
        NiveauExperience
    )

# === ENUMS ÉTENDUS V3.0 ===

class ListeningReasonType(str, Enum):
    """Types étendus de raisons d'écoute pour pondération adaptative V3.0"""
    REMUNERATION_FAIBLE = "remuneration_faible"
    POSTE_INADEQUAT = "poste_inadequat"
    LOCALISATION_PROBLEMATIQUE = "localisation_problematique"
    MANQUE_FLEXIBILITE = "manque_flexibilite"
    MANQUE_PERSPECTIVES = "manque_perspectives"

class WorkModalityType(str, Enum):
    """Types de modalités de travail"""
    FULL_REMOTE = "full_remote"
    HYBRID = "hybrid"
    ON_SITE = "on_site"
    FLEXIBLE = "flexible"

class MotivationType(str, Enum):
    """Types de motivations professionnelles"""
    TECHNICAL_CHALLENGE = "technical_challenge"
    CAREER_EVOLUTION = "career_evolution"
    SALARY_INCREASE = "salary_increase"
    WORK_LIFE_BALANCE = "work_life_balance"
    AUTONOMY = "autonomy"

# === EXTENDED COMPONENT WEIGHTS V3.0 ===

class ExtendedComponentWeights(BaseModel):
    """🎯 Pondération étendue V3.0 : 12 composants (compatible V2.0) - POIDS CORRIGÉS"""
    
    # V2.0 Preserved (poids ajustés pour totaliser 1.0)
    semantique: float = Field(default=0.24, ge=0.0, le=1.0)           # 24%
    salaire: float = Field(default=0.19, ge=0.0, le=1.0)              # 19%
    experience: float = Field(default=0.14, ge=0.0, le=1.0)           # 14%
    localisation: float = Field(default=0.09, ge=0.0, le=1.0)         # 9%
    
    # V3.0 New Components (poids ajustés)
    professional_motivations: float = Field(default=0.08, ge=0.0, le=1.0)  # 8%
    sector_compatibility: float = Field(default=0.06, ge=0.0, le=1.0)      # 6%
    contract_flexibility: float = Field(default=0.05, ge=0.0, le=1.0)      # 5%
    timing_compatibility: float = Field(default=0.04, ge=0.0, le=1.0)      # 4%
    work_modality: float = Field(default=0.04, ge=0.0, le=1.0)             # 4%
    salary_progression: float = Field(default=0.03, ge=0.0, le=1.0)        # 3%
    listening_reason: float = Field(default=0.02, ge=0.0, le=1.0)          # 2%
    candidate_status: float = Field(default=0.02, ge=0.0, le=1.0)          # 2%
    
    # Total = 24+19+14+9+8+6+5+4+4+3+2+2 = 100% = 1.00 ✅
    
    @model_validator(mode='after')
    def weights_sum_to_one(self):
        """Validation que la somme des 12 poids = 1.0"""
        total = (
            self.semantique + self.salaire + self.experience + self.localisation +
            self.professional_motivations + self.sector_compatibility + 
            self.contract_flexibility + self.timing_compatibility + 
            self.work_modality + self.salary_progression + 
            self.listening_reason + self.candidate_status
        )
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"La somme des 12 poids doit être égale à 1.0, actuellement: {total}")
        return self
    
    def get_v2_weights(self) -> ComponentWeights:
        """Convertit vers format V2.0 (rétrocompatibilité)"""
        # Normaliser les 4 composants V2.0 pour qu'ils totalisent 1.0
        v2_total = self.semantique + self.salaire + self.experience + self.localisation
        if v2_total > 0:
            return ComponentWeights(
                semantique=self.semantique / v2_total,
                salaire=self.salaire / v2_total,
                experience=self.experience / v2_total,
                localisation=self.localisation / v2_total
            )
        else:
            # Fallback vers poids V2.0 par défaut
            return ComponentWeights()

# === MODÈLES ÉTENDUS V3.0 ===

class ProfessionalMotivationsProfile(BaseModel):
    """Modèle motivations professionnelles (8% poids)"""
    primary_motivations: List[MotivationType] = []
    motivation_ranking: Dict[MotivationType, int] = {}
    alignment_score: Optional[float] = None

class ExtendedCandidateProfileV3(BiDirectionalCandidateProfile):
    """🎯 Profil candidat étendu V3.0 (hérite de V2.0)"""
    
    # Nouveaux composants V3.0
    professional_motivations: Optional[ProfessionalMotivationsProfile] = None
    preferred_work_modality: Optional[WorkModalityType] = None
    listening_reason_primary: Optional[ListeningReasonType] = None
    
    # Métadonnées V3.0
    v3_components_count: int = Field(default=0, ge=0, le=12)
    questionnaire_exploitation_rate: float = Field(default=0.15, ge=0.0, le=1.0)

# === UTILITAIRES ===

def convert_v3_to_v2_weights(v3_weights: ExtendedComponentWeights) -> ComponentWeights:
    """Convertit pondération V3.0 → V2.0 (rétrocompatibilité)"""
    return v3_weights.get_v2_weights()

def get_component_list_v3() -> List[str]:
    """Retourne liste des 12 composants V3.0"""
    return [
        "semantique", "salaire", "experience", "localisation",
        "professional_motivations", "sector_compatibility", 
        "contract_flexibility", "timing_compatibility",
        "work_modality", "salary_progression", 
        "listening_reason", "candidate_status"
    ]

# === VALIDATION TESTS ===

if __name__ == "__main__":
    print("🧪 Test modèles V3.0 corrigés")
    
    # Test ExtendedComponentWeights
    weights_v3 = ExtendedComponentWeights()
    total = sum([
        weights_v3.semantique, weights_v3.salaire, weights_v3.experience, 
        weights_v3.localisation, weights_v3.professional_motivations,
        weights_v3.sector_compatibility, weights_v3.contract_flexibility,
        weights_v3.timing_compatibility, weights_v3.work_modality,
        weights_v3.salary_progression, weights_v3.listening_reason,
        weights_v3.candidate_status
    ])
    print(f"✅ ExtendedComponentWeights validé : somme = {total:.3f}")
    
    # Test conversion V2.0
    v2_weights = convert_v3_to_v2_weights(weights_v3)
    v2_total = v2_weights.semantique + v2_weights.salaire + v2_weights.experience + v2_weights.localisation
    print(f"✅ Conversion V3→V2 réussie : somme V2 = {v2_total:.3f}")
    
    # Test composants
    components = get_component_list_v3()
    print(f"✅ {len(components)} composants V3.0 définis")
    
    print("🎉 Modèles V3.0 corrigés et validés !")
