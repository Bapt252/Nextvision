"""
Nextvision v3.0 - Extended Matching Models
===========================================

Modèles étendus pour le système de matching bidirectionnel V3.0
- Extension de 4 à 12 composants de matching
- Pondération adaptative selon raison d'écoute
- Compatibilité totale avec V2.0 (héritage préservé)

Author: NEXTEN Development Team
Version: 3.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum
import json


# ================================
# ENUMS - Nouveaux types V3.0
# ================================

class ListeningReasonType(Enum):
    """Types de raisons d'écoute pour pondération adaptative"""
    REMUNERATION_FAIBLE = "remuneration_faible"
    POSTE_INADEQUAT = "poste_inadequat" 
    LOCALISATION = "localisation"
    FLEXIBILITE = "flexibilite"
    PERSPECTIVES = "perspectives"
    AUTRE = "autre"


class ContractType(Enum):
    """Types de contrats préférés"""
    CDI = "cdi"
    CDD = "cdd"
    FREELANCE = "freelance"
    STAGE = "stage"
    INTERIM = "interim"


class WorkModalityType(Enum):
    """Modalités de travail"""
    FULL_REMOTE = "full_remote"
    HYBRID = "hybrid"
    ON_SITE = "on_site"
    FLEXIBLE = "flexible"


class MotivationType(Enum):
    """Types de motivations professionnelles"""
    CHALLENGE_TECHNIQUE = "challenge_technique"
    EVOLUTION_CARRIERE = "evolution_carriere"
    AUTONOMIE = "autonomie"
    IMPACT_BUSINESS = "impact_business"
    APPRENTISSAGE = "apprentissage"
    LEADERSHIP = "leadership"
    INNOVATION = "innovation"
    EQUILIBRE_VIE = "equilibre_vie"


class CandidateStatus(Enum):
    """Statut du candidat"""
    EN_POSTE = "en_poste"
    DEMANDEUR_EMPLOI = "demandeur_emploi"
    ETUDIANT = "etudiant"
    FREELANCE = "freelance"


# ================================
# MODÈLES V2.0 PRÉSERVÉS
# ================================

@dataclass
class SemanticProfile:
    """Profil sémantique - V2.0 préservé avec poids ajusté"""
    skills: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    experience_description: str = ""
    weight: float = 0.25  # Ajusté de 35% à 25%


@dataclass
class SalaryProfile:
    """Profil salarial - V2.0 préservé avec poids ajusté"""
    current_salary: Optional[float] = None
    desired_salary: Optional[float] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_negotiable: bool = True
    weight: float = 0.20  # Ajusté de 25% à 20%


@dataclass
class ExperienceProfile:
    """Profil expérience - V2.0 préservé avec poids ajusté"""
    years_total: int = 0
    years_domain_specific: int = 0
    seniority_level: str = "junior"  # junior, medior, senior, expert
    required_min_years: int = 0
    weight: float = 0.15  # Ajusté de 25% à 15%


@dataclass
class LocationProfile:
    """Profil localisation - V2.0 préservé avec poids ajusté"""
    candidate_location: str = ""
    position_location: str = ""
    max_distance_km: int = 50
    accepts_relocation: bool = False
    commute_time_max: int = 60  # minutes
    weight: float = 0.10  # Ajusté de 15% à 10%


# ================================
# NOUVEAUX MODÈLES V3.0
# ================================

@dataclass
class ProfessionalMotivationsProfile:
    """Motivations professionnelles - Nouveau V3.0"""
    candidate_motivations: Dict[MotivationType, int] = field(default_factory=dict)  # 1-5 ranking
    position_motivations_alignment: Dict[MotivationType, int] = field(default_factory=dict)
    motivation_priorities: List[MotivationType] = field(default_factory=list)
    weight: float = 0.08


@dataclass
class SectorCompatibilityProfile:
    """Compatibilité sectorielle - Nouveau V3.0"""
    preferred_sectors: List[str] = field(default_factory=list)
    avoided_sectors: List[str] = field(default_factory=list)
    current_sector: str = ""
    position_sector: str = ""
    sector_transition_openness: int = 3  # 1-5 scale
    weight: float = 0.06


@dataclass
class ContractFlexibilityProfile:
    """Flexibilité contractuelle - Nouveau V3.0"""
    contract_preferences: Dict[ContractType, int] = field(default_factory=dict)  # 1-5 ranking
    position_contract_type: ContractType = ContractType.CDI
    contract_duration_flexibility: bool = True
    trial_period_acceptance: bool = True
    weight: float = 0.05


@dataclass
class TimingCompatibilityProfile:
    """Compatibilité timing - Nouveau V3.0"""
    availability_date: str = ""  # ISO format
    notice_period_weeks: int = 0
    recruitment_urgency: int = 3  # 1-5 scale (1=urgent, 5=can wait)
    flexibility_start_date: int = 2  # weeks flexibility
    weight: float = 0.04


@dataclass
class WorkModalityProfile:
    """Modalités de travail - Nouveau V3.0"""
    preferred_modality: WorkModalityType = WorkModalityType.HYBRID
    remote_days_per_week: int = 2
    office_days_per_week: int = 3
    commute_tolerance: int = 45  # minutes
    position_modality: WorkModalityType = WorkModalityType.HYBRID
    modality_flexibility: int = 3  # 1-5 scale
    weight: float = 0.04


@dataclass
class SalaryProgressionProfile:
    """Progression salariale - Nouveau V3.0"""
    current_salary: Optional[float] = None
    desired_salary: Optional[float] = None
    salary_gap_percentage: float = 0.0
    progression_expectations: int = 3  # 1-5 scale
    position_salary_evolution: Dict[str, float] = field(default_factory=dict)  # year: salary
    weight: float = 0.03


@dataclass
class ListeningReasonProfile:
    """Raison d'écoute - COMPOSANT CLEF V3.0"""
    primary_reason: ListeningReasonType = ListeningReasonType.AUTRE
    secondary_reasons: List[ListeningReasonType] = field(default_factory=list)
    reason_intensity: int = 3  # 1-5 scale
    motivation_description: str = ""
    weight: float = 0.03  # Poids direct faible mais impact systémique énorme


@dataclass
class CandidateStatusProfile:
    """Profil situation candidat - Nouveau V3.0"""
    current_status: CandidateStatus = CandidateStatus.EN_POSTE
    job_search_urgency: int = 3  # 1-5 scale
    employment_stability: int = 3  # 1-5 scale
    career_transition_phase: bool = False
    recruitment_constraints: List[str] = field(default_factory=list)
    weight: float = 0.02


# ================================
# PONDÉRATION ADAPTATIVE V3.0
# ================================

@dataclass
class AdaptiveWeightingConfig:
    """Configuration des pondérations adaptatives selon raison d'écoute"""
    base_weights: Dict[str, float] = field(default_factory=dict)
    adaptive_boosts: Dict[ListeningReasonType, Dict[str, float]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialise les pondérations par défaut"""
        if not self.base_weights:
            self.base_weights = {
                "semantic": 0.25,
                "salary": 0.20,
                "experience": 0.15,
                "location": 0.10,
                "motivations": 0.08,
                "sector_compatibility": 0.06,
                "contract_flexibility": 0.05,
                "timing_compatibility": 0.04,
                "work_modality": 0.04,
                "salary_progression": 0.03,
                "listening_reason": 0.03,
                "candidate_status": 0.02
            }
        
        if not self.adaptive_boosts:
            self.adaptive_boosts = {
                ListeningReasonType.REMUNERATION_FAIBLE: {
                    "salary": 0.35,  # Boost majeur
                    "salary_progression": 0.05,
                    "semantic": 0.20,  # Réduit
                    "motivations": 0.05,
                    "experience": 0.12,
                    "location": 0.08,
                    "sector_compatibility": 0.05,
                    "contract_flexibility": 0.04,
                    "timing_compatibility": 0.03,
                    "work_modality": 0.03
                },
                ListeningReasonType.POSTE_INADEQUAT: {
                    "semantic": 0.35,  # Boost majeur
                    "sector_compatibility": 0.10,  # Boost secondaire
                    "motivations": 0.12,
                    "salary": 0.15,
                    "experience": 0.12,
                    "location": 0.08,
                    "contract_flexibility": 0.04,
                    "timing_compatibility": 0.03,
                    "work_modality": 0.03,
                    "salary_progression": 0.03
                },
                ListeningReasonType.LOCALISATION: {
                    "location": 0.25,  # Boost majeur
                    "work_modality": 0.06,  # Boost secondaire
                    "semantic": 0.20,
                    "salary": 0.18,
                    "motivations": 0.08,
                    "experience": 0.12,
                    "sector_compatibility": 0.05,
                    "contract_flexibility": 0.03,
                    "timing_compatibility": 0.03
                },
                ListeningReasonType.FLEXIBILITE: {
                    "work_modality": 0.08,  # Boost majeur
                    "contract_flexibility": 0.10,  # Boost secondaire
                    "timing_compatibility": 0.06,
                    "semantic": 0.22,
                    "salary": 0.18,
                    "location": 0.12,
                    "motivations": 0.10,
                    "experience": 0.12,
                    "sector_compatibility": 0.05
                },
                ListeningReasonType.PERSPECTIVES: {
                    "experience": 0.25,  # Boost majeur
                    "motivations": 0.15,  # Boost secondaire
                    "semantic": 0.20,
                    "salary": 0.15,
                    "sector_compatibility": 0.08,
                    "location": 0.08,
                    "salary_progression": 0.04,
                    "contract_flexibility": 0.03,
                    "timing_compatibility": 0.02
                }
            }


# ================================
# MODÈLE GLOBAL V3.0
# ================================

@dataclass
class ExtendedMatchingProfile:
    """Profil complet de matching V3.0 - 12 composants"""
    
    # V2.0 Préservés (poids ajustés)
    semantic: SemanticProfile = field(default_factory=SemanticProfile)
    salary: SalaryProfile = field(default_factory=SalaryProfile)
    experience: ExperienceProfile = field(default_factory=ExperienceProfile)
    location: LocationProfile = field(default_factory=LocationProfile)
    
    # V3.0 Nouveaux
    motivations: ProfessionalMotivationsProfile = field(default_factory=ProfessionalMotivationsProfile)
    sector_compatibility: SectorCompatibilityProfile = field(default_factory=SectorCompatibilityProfile)
    contract_flexibility: ContractFlexibilityProfile = field(default_factory=ContractFlexibilityProfile)
    timing_compatibility: TimingCompatibilityProfile = field(default_factory=TimingCompatibilityProfile)
    work_modality: WorkModalityProfile = field(default_factory=WorkModalityProfile)
    salary_progression: SalaryProgressionProfile = field(default_factory=SalaryProgressionProfile)
    listening_reason: ListeningReasonProfile = field(default_factory=ListeningReasonProfile)
    candidate_status: CandidateStatusProfile = field(default_factory=CandidateStatusProfile)
    
    # Configuration pondération adaptative
    weighting_config: AdaptiveWeightingConfig = field(default_factory=AdaptiveWeightingConfig)
    
    def get_adaptive_weights(self) -> Dict[str, float]:
        """Calcule les pondérations adaptatives selon la raison d'écoute"""
        primary_reason = self.listening_reason.primary_reason
        
        if primary_reason in self.weighting_config.adaptive_boosts:
            return self.weighting_config.adaptive_boosts[primary_reason].copy()
        
        return self.weighting_config.base_weights.copy()
    
    def validate_weights_sum(self, weights: Dict[str, float]) -> bool:
        """Valide que la somme des poids est proche de 1.0"""
        total = sum(weights.values())
        return 0.98 <= total <= 1.02
    
    def normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Normalise les poids pour que leur somme soit exactement 1.0"""
        total = sum(weights.values())
        if total == 0:
            return weights
        
        return {key: value / total for key, value in weights.items()}


@dataclass
class MatchingScore:
    """Score de matching V3.0 avec détail par composant"""
    total_score: float = 0.0
    component_scores: Dict[str, float] = field(default_factory=dict)
    component_weights: Dict[str, float] = field(default_factory=dict)
    adaptive_reason: Optional[ListeningReasonType] = None
    confidence_level: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Sérialisation pour API/logs"""
        return {
            "total_score": self.total_score,
            "component_scores": self.component_scores,
            "component_weights": self.component_weights,
            "adaptive_reason": self.adaptive_reason.value if self.adaptive_reason else None,
            "confidence_level": self.confidence_level
        }


# ================================
# UTILITAIRES DE CONVERSION V2.0
# ================================

def convert_v2_to_v3_profile(v2_data: Dict[str, Any]) -> ExtendedMatchingProfile:
    """Convertit un profil V2.0 vers V3.0 (rétrocompatibilité)"""
    profile = ExtendedMatchingProfile()
    
    # Mapping V2.0 → V3.0
    if "semantic" in v2_data:
        profile.semantic = SemanticProfile(**v2_data["semantic"])
    
    if "salary" in v2_data:
        profile.salary = SalaryProfile(**v2_data["salary"])
    
    if "experience" in v2_data:
        profile.experience = ExperienceProfile(**v2_data["experience"])
    
    if "location" in v2_data:
        profile.location = LocationProfile(**v2_data["location"])
    
    return profile


def get_component_list() -> List[str]:
    """Retourne la liste des 12 composants V3.0"""
    return [
        "semantic", "salary", "experience", "location",
        "motivations", "sector_compatibility", "contract_flexibility",
        "timing_compatibility", "work_modality", "salary_progression",
        "listening_reason", "candidate_status"
    ]


# ================================
# VALIDATION ET TESTS
# ================================

def validate_extended_profile(profile: ExtendedMatchingProfile) -> Tuple[bool, List[str]]:
    """Valide la cohérence d'un profil étendu V3.0"""
    errors = []
    
    # Validation pondérations
    weights = profile.get_adaptive_weights()
    if not profile.validate_weights_sum(weights):
        errors.append(f"Somme des poids incorrecte: {sum(weights.values())}")
    
    # Validation composants obligatoires
    required_components = get_component_list()
    for component in required_components:
        if not hasattr(profile, component):
            errors.append(f"Composant manquant: {component}")
    
    # Validation logique métier
    if profile.salary.desired_salary and profile.salary.current_salary:
        if profile.salary.desired_salary < profile.salary.current_salary:
            errors.append("Salaire désiré inférieur au salaire actuel")
    
    return len(errors) == 0, errors


if __name__ == "__main__":
    # Test de base
    profile = ExtendedMatchingProfile()
    
    # Test pondération adaptative
    profile.listening_reason.primary_reason = ListeningReasonType.REMUNERATION_FAIBLE
    adaptive_weights = profile.get_adaptive_weights()
    
    print("=== NEXTVISION V3.0 - Test Modèles ===")
    print(f"Composants V3.0: {len(get_component_list())}")
    print(f"Raison d'écoute: {profile.listening_reason.primary_reason.value}")
    print(f"Poids adaptatifs: {adaptive_weights}")
    print(f"Boost salary: {adaptive_weights.get('salary', 0) * 100:.1f}%")
    
    is_valid, errors = validate_extended_profile(profile)
    print(f"Validation: {'✅ OK' if is_valid else '❌ Erreurs'}")
    if errors:
        for error in errors:
            print(f"  - {error}")
