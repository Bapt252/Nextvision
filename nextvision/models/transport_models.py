"""
🗺️ Nextvision - Modèles Transport Avancés Google Maps
Extension des modèles existants pour intégration Google Maps Intelligence

Author: NEXTEN Team  
Version: 2.0.0 (Prompt 2)
Integration: Google Maps API + Pondération Adaptative
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json

# Import des modèles existants
from .questionnaire_advanced import MoyenTransport, TransportPreferences

class GoogleMapsMode(str, Enum):
    """🗺️ Modes de transport Google Maps API"""
    DRIVING = "driving"
    TRANSIT = "transit" 
    WALKING = "walking"
    BICYCLING = "bicycling"

class TrafficModel(str, Enum):
    """🚦 Modèles de trafic Google Maps"""
    BEST_GUESS = "best_guess"
    PESSIMISTIC = "pessimistic"
    OPTIMISTIC = "optimistic"

class TransitMode(str, Enum):
    """🚇 Modes de transport en commun"""
    BUS = "bus"
    SUBWAY = "subway"
    TRAIN = "train"
    TRAM = "tram"
    RAIL = "rail"

class TransportQuality(str, Enum):
    """⭐ Qualité du transport"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    UNAVAILABLE = "unavailable"

class GeocodeResult(BaseModel):
    """📍 Résultat de géocodage d'une adresse"""
    address: str = Field(description="Adresse originale")
    formatted_address: str = Field(description="Adresse formatée par Google")
    latitude: float = Field(description="Latitude")
    longitude: float = Field(description="Longitude")
    place_id: Optional[str] = Field(None, description="Place ID Google")
    types: List[str] = Field(default=[], description="Types de lieu")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confiance du géocodage")
    cached: bool = Field(default=False, description="Résultat du cache")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class RouteStep(BaseModel):
    """🛣️ Étape d'un itinéraire"""
    instruction: str = Field(description="Instruction de l'étape")
    distance_meters: int = Field(description="Distance en mètres")
    duration_seconds: int = Field(description="Durée en secondes")
    transport_mode: GoogleMapsMode = Field(description="Mode de transport")
    
    # Spécifique transport en commun
    transit_details: Optional[Dict] = Field(None, description="Détails transport en commun")
    
    def get_duration_minutes(self) -> int:
        """⏱️ Durée en minutes"""
        return self.duration_seconds // 60
    
    def get_distance_km(self) -> float:
        """📏 Distance en kilomètres"""
        return round(self.distance_meters / 1000, 2)

class TransportRoute(BaseModel):
    """🛤️ Route complète entre deux points"""
    origin: GeocodeResult = Field(description="Point de départ")
    destination: GeocodeResult = Field(description="Point d'arrivée")
    mode: GoogleMapsMode = Field(description="Mode de transport")
    
    # Métriques principales
    total_distance_meters: int = Field(description="Distance totale en mètres")
    total_duration_seconds: int = Field(description="Durée totale en secondes")
    
    # Détails de l'itinéraire
    steps: List[RouteStep] = Field(default=[], description="Étapes de l'itinéraire")
    
    # Conditions de circulation
    duration_in_traffic_seconds: Optional[int] = Field(None, description="Durée avec trafic")
    traffic_model: Optional[TrafficModel] = Field(None, description="Modèle de trafic utilisé")
    
    # Informations supplémentaires
    polyline: Optional[str] = Field(None, description="Polyline encodée de l'itinéraire")
    bounds: Optional[Dict] = Field(None, description="Limites géographiques")
    warnings: List[str] = Field(default=[], description="Avertissements")
    
    # Métadonnées
    calculated_at: datetime = Field(default_factory=datetime.now)
    cached: bool = Field(default=False)
    
    def get_duration_minutes(self) -> int:
        """⏱️ Durée normale en minutes"""
        return self.total_duration_seconds // 60
    
    def get_traffic_duration_minutes(self) -> Optional[int]:
        """🚦 Durée avec trafic en minutes"""
        if self.duration_in_traffic_seconds:
            return self.duration_in_traffic_seconds // 60
        return None
    
    def get_distance_km(self) -> float:
        """📏 Distance en kilomètres"""
        return round(self.total_distance_meters / 1000, 2)
    
    def get_transfer_count(self) -> int:
        """🔄 Nombre de correspondances (transport en commun)"""
        if self.mode != GoogleMapsMode.TRANSIT:
            return 0
        
        transit_steps = [step for step in self.steps if step.transport_mode == GoogleMapsMode.TRANSIT]
        return max(0, len(transit_steps) - 1)
    
    def has_accessibility_issues(self) -> bool:
        """♿ Vérification problèmes d'accessibilité"""
        accessibility_warnings = [
            "stairs", "escalator", "platform", "wheelchair"
        ]
        warning_text = " ".join(self.warnings).lower()
        return any(warning in warning_text for warning in accessibility_warnings)

class TransportConstraint(BaseModel):
    """🚫 Contrainte de transport candidat"""
    mode: GoogleMapsMode = Field(description="Mode de transport")
    max_duration_minutes: int = Field(gt=0, description="Durée maximum acceptée")
    max_duration_peak_minutes: Optional[int] = Field(None, description="Durée max en heures de pointe")
    
    # Contraintes spécifiques
    max_transfers: Optional[int] = Field(None, description="Nombre max de correspondances")
    avoid_tolls: bool = Field(default=False, description="Éviter les péages")
    avoid_highways: bool = Field(default=False, description="Éviter les autoroutes")
    wheelchair_accessible: bool = Field(default=False, description="Accessibilité fauteuil roulant")
    
    # Flexibilité
    tolerance_minutes: int = Field(default=5, description="Tolérance en minutes")
    
    @validator('max_duration_peak_minutes')
    def validate_peak_duration(cls, v, values):
        if v is not None and 'max_duration_minutes' in values:
            if v < values['max_duration_minutes']:
                raise ValueError("La durée en pointe ne peut pas être inférieure à la durée normale")
        return v

class TransportAnalysis(BaseModel):
    """📊 Analyse complète d'un moyen de transport"""
    constraint: TransportConstraint = Field(description="Contrainte appliquée")
    route: Optional[TransportRoute] = Field(None, description="Route calculée")
    
    # Évaluation
    is_viable: bool = Field(description="Transport viable selon contraintes")
    viability_score: float = Field(ge=0.0, le=1.0, description="Score de viabilité 0-1")
    quality_score: float = Field(ge=0.0, le=1.0, description="Score de qualité 0-1")
    
    # Détails de l'évaluation
    exceeds_duration: bool = Field(default=False, description="Dépasse la durée max")
    exceeds_transfers: bool = Field(default=False, description="Trop de correspondances")
    has_accessibility_issues: bool = Field(default=False, description="Problèmes d'accessibilité")
    
    # Explications
    viability_reason: str = Field(description="Raison de la viabilité/non-viabilité")
    quality_explanation: str = Field(description="Explication du score de qualité")
    
    # Estimations
    cost_estimate: Optional[float] = Field(None, description="Coût estimé du trajet")
    comfort_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Score de confort")
    reliability_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Score de fiabilité")
    
    def get_overall_score(self) -> float:
        """🎯 Score global (viabilité + qualité + confort + fiabilité)"""
        if not self.is_viable:
            return 0.0
        
        return (
            self.viability_score * 0.4 +
            self.quality_score * 0.3 +
            self.comfort_score * 0.2 +
            self.reliability_score * 0.1
        )

class CandidatTransportProfile(BaseModel):
    """👤 Profil transport complet d'un candidat"""
    # Informations de base
    candidat_id: Optional[str] = Field(None, description="ID du candidat")
    home_address: str = Field(description="Adresse domicile")
    home_geocode: Optional[GeocodeResult] = Field(None, description="Géocodage domicile")
    
    # Contraintes de transport (étendues depuis questionnaire_advanced)
    constraints: List[TransportConstraint] = Field(default=[], description="Contraintes par mode")
    
    # Préférences héritées
    legacy_transport_prefs: Optional[TransportPreferences] = Field(None, description="Préférences legacy")
    
    # Flexibilité
    accepts_remote_work: bool = Field(default=False, description="Accepte télétravail")
    remote_days_per_week: int = Field(default=0, ge=0, le=5, description="Jours télétravail/semaine")
    flexible_hours: bool = Field(default=False, description="Horaires flexibles")
    
    # Métadonnées
    profile_completed_at: Optional[datetime] = Field(None)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    @validator('constraints')
    def validate_unique_modes(cls, v):
        """Validation que chaque mode n'apparaît qu'une fois"""
        modes = [constraint.mode for constraint in v]
        if len(modes) != len(set(modes)):
            raise ValueError("Chaque mode de transport ne peut avoir qu'une contrainte")
        return v
    
    def get_constraint_for_mode(self, mode: GoogleMapsMode) -> Optional[TransportConstraint]:
        """🔍 Récupère la contrainte pour un mode donné"""
        for constraint in self.constraints:
            if constraint.mode == mode:
                return constraint
        return None
    
    def has_valid_constraints(self) -> bool:
        """✅ Vérifie si le profil a des contraintes valides"""
        return len(self.constraints) > 0
    
    def get_max_commute_time(self) -> int:
        """⏰ Temps de trajet maximum accepté (tous modes confondus)"""
        if not self.constraints:
            return 60  # Default 1h
        
        return max(constraint.max_duration_minutes for constraint in self.constraints)

class JobTransportInfo(BaseModel):
    """🏢 Informations transport d'une offre d'emploi"""
    job_id: str = Field(description="ID de l'offre d'emploi")
    office_address: str = Field(description="Adresse du bureau")
    office_geocode: Optional[GeocodeResult] = Field(None, description="Géocodage bureau")
    
    # Politiques entreprise
    remote_policy: str = Field(default="none", description="Politique télétravail")
    flexible_hours: bool = Field(default=False, description="Horaires flexibles")
    parking_available: bool = Field(default=False, description="Parking disponible")
    bike_storage: bool = Field(default=False, description="Parking vélo")
    
    # Transport entreprise
    company_shuttle: bool = Field(default=False, description="Navette entreprise")
    public_transport_subsidy: bool = Field(default=False, description="Subvention transport")
    
    # Zones géographiques
    catchment_area_km: Optional[float] = Field(None, description="Zone de recrutement (km)")
    priority_locations: List[str] = Field(default=[], description="Zones prioritaires")

class TransportMatchingResult(BaseModel):
    """🎯 Résultat du matching transport entre candidat et job"""
    candidat_profile: CandidatTransportProfile = Field(description="Profil candidat")
    job_info: JobTransportInfo = Field(description="Info job")
    
    # Analyses par mode
    transport_analyses: List[TransportAnalysis] = Field(default=[], description="Analyses par mode")
    
    # Résultat global
    is_transport_compatible: bool = Field(description="Compatible transport")
    best_transport_mode: Optional[GoogleMapsMode] = Field(None, description="Meilleur mode transport")
    overall_transport_score: float = Field(ge=0.0, le=1.0, description="Score transport global")
    
    # Recommandations
    recommended_modes: List[GoogleMapsMode] = Field(default=[], description="Modes recommandés")
    excluded_reasons: List[str] = Field(default=[], description="Raisons d'exclusions")
    
    # Suggestions d'amélioration
    remote_work_suggestion: Optional[str] = Field(None, description="Suggestion télétravail")
    flexible_hours_benefit: Optional[str] = Field(None, description="Bénéfice horaires flexibles")
    
    # Performance
    calculation_duration_ms: Optional[float] = Field(None, description="Temps de calcul")
    google_maps_requests: int = Field(default=0, description="Nombre requêtes Google Maps")
    cache_hits: int = Field(default=0, description="Hits cache")
    
    # Métadonnées
    calculated_at: datetime = Field(default_factory=datetime.now)
    
    def get_best_analysis(self) -> Optional[TransportAnalysis]:
        """🏆 Meilleure analyse transport"""
        viable_analyses = [a for a in self.transport_analyses if a.is_viable]
        if not viable_analyses:
            return None
        
        return max(viable_analyses, key=lambda a: a.get_overall_score())
    
    def get_exclusion_summary(self) -> Dict:
        """📊 Résumé des exclusions"""
        total_modes = len(self.transport_analyses)
        viable_modes = len([a for a in self.transport_analyses if a.is_viable])
        excluded_modes = total_modes - viable_modes
        
        return {
            "total_modes_analyzed": total_modes,
            "viable_modes": viable_modes,
            "excluded_modes": excluded_modes,
            "exclusion_rate": round(excluded_modes / total_modes if total_modes > 0 else 0, 2),
            "exclusion_reasons": self.excluded_reasons
        }

class TransportFilteringReport(BaseModel):
    """📈 Rapport de pré-filtering transport"""
    candidat_id: str = Field(description="ID candidat")
    total_jobs_analyzed: int = Field(description="Nombre total de jobs analysés")
    
    # Résultats filtering
    jobs_included: int = Field(description="Jobs inclus après filtering")
    jobs_excluded: int = Field(description="Jobs exclus par filtering")
    exclusion_rate: float = Field(ge=0.0, le=1.0, description="Taux d'exclusion")
    
    # Performance gains
    cpu_time_saved_ms: Optional[float] = Field(None, description="Temps CPU économisé")
    google_maps_requests: int = Field(description="Requêtes Google Maps utilisées")
    cache_efficiency: float = Field(ge=0.0, le=1.0, description="Efficacité du cache")
    
    # Détails par mode
    exclusion_by_mode: Dict[str, int] = Field(default={}, description="Exclusions par mode")
    
    # Insights
    most_problematic_zones: List[str] = Field(default=[], description="Zones les plus problématiques")
    suggestions: List[str] = Field(default=[], description="Suggestions d'amélioration")
    
    # Métadonnées
    generated_at: datetime = Field(default_factory=datetime.now)
    processing_duration_ms: float = Field(description="Durée du traitement")
    
    def get_efficiency_metrics(self) -> Dict:
        """📊 Métriques d'efficacité du pre-filtering"""
        return {
            "jobs_excluded_percentage": round(self.exclusion_rate * 100, 1),
            "cpu_efficiency": round(self.cpu_time_saved_ms / self.processing_duration_ms if self.processing_duration_ms > 0 else 0, 2),
            "cache_hit_rate": round(self.cache_efficiency * 100, 1),
            "requests_per_job": round(self.google_maps_requests / self.total_jobs_analyzed if self.total_jobs_analyzed > 0 else 0, 2)
        }

# Configuration par défaut pour les contraintes
DEFAULT_TRANSPORT_CONSTRAINTS = {
    GoogleMapsMode.DRIVING: TransportConstraint(
        mode=GoogleMapsMode.DRIVING,
        max_duration_minutes=30,
        max_duration_peak_minutes=45,
        avoid_tolls=False,
        tolerance_minutes=5
    ),
    GoogleMapsMode.TRANSIT: TransportConstraint(
        mode=GoogleMapsMode.TRANSIT,
        max_duration_minutes=45,
        max_duration_peak_minutes=60,
        max_transfers=2,
        tolerance_minutes=10
    ),
    GoogleMapsMode.WALKING: TransportConstraint(
        mode=GoogleMapsMode.WALKING,
        max_duration_minutes=20,
        tolerance_minutes=5
    ),
    GoogleMapsMode.BICYCLING: TransportConstraint(
        mode=GoogleMapsMode.BICYCLING,
        max_duration_minutes=25,
        tolerance_minutes=5
    )
}

def create_default_candidat_profile(
    candidat_id: str,
    home_address: str,
    selected_modes: List[GoogleMapsMode] = None
) -> CandidatTransportProfile:
    """🏗️ Crée un profil candidat avec contraintes par défaut"""
    
    if selected_modes is None:
        selected_modes = [GoogleMapsMode.DRIVING, GoogleMapsMode.TRANSIT]
    
    constraints = []
    for mode in selected_modes:
        if mode in DEFAULT_TRANSPORT_CONSTRAINTS:
            constraints.append(DEFAULT_TRANSPORT_CONSTRAINTS[mode])
    
    return CandidatTransportProfile(
        candidat_id=candidat_id,
        home_address=home_address,
        constraints=constraints,
        profile_completed_at=datetime.now()
    )
