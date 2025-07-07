"""
🗺️ Nextvision - Modèles Transport Géospatial (Prompt 2)
Extension des modèles pour Google Maps Intelligence

Author: NEXTEN Team  
Version: 2.0.0 - Google Maps Intelligence
Integration: TransportPreferences (questionnaire_advanced.py) + Google Maps API
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime
from enum import Enum
from .questionnaire_advanced import TransportPreferences, MoyenTransport

class TravelMode(str, Enum):
    """🚗 Modes de transport Google Maps API"""
    DRIVING = "driving"
    TRANSIT = "transit" 
    WALKING = "walking"
    BICYCLING = "bicycling"

class TrafficModel(str, Enum):
    """🚦 Modèles de trafic"""
    BEST_GUESS = "best_guess"
    PESSIMISTIC = "pessimistic"
    OPTIMISTIC = "optimistic"

class GeocodeQuality(str, Enum):
    """📍 Qualité du géocodage"""
    EXACT = "exact"           # Adresse exacte
    APPROXIMATE = "approximate"  # Approximative
    PARTIAL = "partial"       # Partielle
    FAILED = "failed"         # Échec

class GeocodeResult(BaseModel):
    """📍 Résultat de géocodage Google Maps"""
    address: str = Field(description="Adresse originale")
    formatted_address: str = Field(description="Adresse formatée Google")
    latitude: float = Field(description="Latitude")
    longitude: float = Field(description="Longitude")
    quality: GeocodeQuality = Field(description="Qualité du géocodage")
    place_id: str = Field(description="Google Place ID")
    components: Dict = Field(default={}, description="Composants d'adresse")
    cached_at: datetime = Field(default_factory=datetime.now)
    
    @property
    def coordinates(self) -> Tuple[float, float]:
        """Retourne les coordonnées (lat, lng)"""
        return (self.latitude, self.longitude)

class RouteStep(BaseModel):
    """🛣️ Étape d'un itinéraire"""
    distance_meters: int = Field(description="Distance en mètres")
    duration_seconds: int = Field(description="Durée en secondes")  
    travel_mode: TravelMode = Field(description="Mode de transport")
    instructions: str = Field(description="Instructions de navigation")
    
    @property
    def distance_km(self) -> float:
        """Distance en kilomètres"""
        return round(self.distance_meters / 1000, 2)
    
    @property
    def duration_minutes(self) -> int:
        """Durée en minutes"""
        return round(self.duration_seconds / 60)

class TrafficCondition(BaseModel):
    """🚦 Conditions de trafic"""
    duration_in_traffic_seconds: int = Field(description="Durée avec trafic")
    traffic_factor: float = Field(description="Facteur trafic (1.0 = normal)")
    rush_hour: bool = Field(default=False, description="Heure de pointe")
    
    @property
    def delay_minutes(self) -> int:
        """Délai dû au trafic en minutes"""
        normal_duration = self.duration_in_traffic_seconds / self.traffic_factor
        delay = self.duration_in_traffic_seconds - normal_duration
        return round(delay / 60)

class TransportRoute(BaseModel):
    """🗺️ Itinéraire de transport complet"""
    origin: GeocodeResult = Field(description="Point de départ")
    destination: GeocodeResult = Field(description="Point d'arrivée")
    travel_mode: TravelMode = Field(description="Mode de transport")
    
    # Temps et distance
    distance_meters: int = Field(description="Distance totale en mètres")
    duration_seconds: int = Field(description="Durée normale en secondes")
    traffic: Optional[TrafficCondition] = Field(None, description="Conditions trafic")
    
    # Détails itinéraire
    steps: List[RouteStep] = Field(default=[], description="Étapes de l'itinéraire")
    polyline: str = Field(default="", description="Polyline encodée")
    
    # Métadonnées
    calculated_at: datetime = Field(default_factory=datetime.now)
    cached_until: Optional[datetime] = Field(None, description="Cache valide jusqu'à")
    
    @property
    def distance_km(self) -> float:
        """Distance en kilomètres"""
        return round(self.distance_meters / 1000, 2)
    
    @property
    def duration_minutes(self) -> int:
        """Durée en minutes (avec trafic si disponible)"""
        if self.traffic:
            return round(self.traffic.duration_in_traffic_seconds / 60)
        return round(self.duration_seconds / 60)
    
    @property
    def is_within_time_limit(self) -> bool:
        """Vérifie si le trajet respecte les limites de temps"""
        # Cette méthode sera étendue avec les préférences candidat
        return True

class TransportCompatibility(BaseModel):
    """✅ Compatibilité transport candidat/job"""
    candidat_preferences: TransportPreferences = Field(description="Préférences candidat")
    job_location: GeocodeResult = Field(description="Localisation job")
    candidat_location: GeocodeResult = Field(description="Localisation candidat")
    
    # Résultats par mode de transport
    routes: Dict[TravelMode, TransportRoute] = Field(default={}, description="Itinéraires calculés")
    
    # Évaluation compatibilité
    compatible_modes: List[TravelMode] = Field(default=[], description="Modes compatibles")
    recommended_mode: Optional[TravelMode] = Field(None, description="Mode recommandé")
    compatibility_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Score compatibilité")
    
    # Explications
    compatibility_reasons: List[str] = Field(default=[], description="Raisons compatibilité")
    rejection_reasons: List[str] = Field(default=[], description="Raisons rejet")
    
    def evaluate_compatibility(self) -> bool:
        """🎯 Évalue la compatibilité transport"""
        self.compatible_modes = []
        self.compatibility_reasons = []
        self.rejection_reasons = []
        
        for transport_pref in self.candidat_preferences.moyens_selectionnes:
            # Mapping TransportPreferences → TravelMode
            travel_mode = self._map_transport_to_travel_mode(transport_pref)
            
            if travel_mode in self.routes:
                route = self.routes[travel_mode]
                time_limit = self.candidat_preferences.temps_max.get(
                    transport_pref.value.lower().replace(" ", "_"), 60
                )
                
                if route.duration_minutes <= time_limit:
                    self.compatible_modes.append(travel_mode)
                    self.compatibility_reasons.append(
                        f"{transport_pref.value}: {route.duration_minutes}min ≤ {time_limit}min"
                    )
                else:
                    self.rejection_reasons.append(
                        f"{transport_pref.value}: {route.duration_minutes}min > {time_limit}min"
                    )
        
        # Score basé sur nombre de modes compatibles
        total_modes = len(self.candidat_preferences.moyens_selectionnes)
        compatible_count = len(self.compatible_modes)
        
        if total_modes > 0:
            self.compatibility_score = compatible_count / total_modes
        
        # Mode recommandé : le plus rapide parmi les compatibles
        if self.compatible_modes:
            fastest_mode = min(
                self.compatible_modes,
                key=lambda mode: self.routes[mode].duration_minutes
            )
            self.recommended_mode = fastest_mode
        
        return len(self.compatible_modes) > 0
    
    def _map_transport_to_travel_mode(self, transport: MoyenTransport) -> TravelMode:
        """🗺️ Mapping TransportPreferences → Google Maps TravelMode"""
        mapping = {
            MoyenTransport.VOITURE: TravelMode.DRIVING,
            MoyenTransport.TRANSPORT_COMMUN: TravelMode.TRANSIT,
            MoyenTransport.VELO: TravelMode.BICYCLING,
            MoyenTransport.MARCHE: TravelMode.WALKING,
            MoyenTransport.MOTO: TravelMode.DRIVING,  # Même calcul que voiture
            MoyenTransport.COVOITURAGE: TravelMode.DRIVING
        }
        return mapping.get(transport, TravelMode.DRIVING)
    
    @property
    def is_compatible(self) -> bool:
        """Job compatible avec préférences transport candidat"""
        return len(self.compatible_modes) > 0
    
    @property
    def best_route_info(self) -> Optional[str]:
        """Informations sur le meilleur itinéraire"""
        if not self.recommended_mode or self.recommended_mode not in self.routes:
            return None
            
        route = self.routes[self.recommended_mode]
        mode_name = self._get_mode_display_name(self.recommended_mode)
        
        traffic_info = ""
        if route.traffic and route.traffic.delay_minutes > 5:
            traffic_info = f" (+{route.traffic.delay_minutes}min trafic)"
        
        return f"{route.duration_minutes}min en {mode_name}{traffic_info}"
    
    def _get_mode_display_name(self, mode: TravelMode) -> str:
        """Nom d'affichage du mode de transport"""
        names = {
            TravelMode.DRIVING: "voiture",
            TravelMode.TRANSIT: "transport public", 
            TravelMode.WALKING: "marche",
            TravelMode.BICYCLING: "vélo"
        }
        return names.get(mode, mode.value)

class LocationScore(BaseModel):
    """📍 Score de localisation enrichi (composant 6/7)"""
    base_distance_km: float = Field(description="Distance euclidienne")
    transport_compatibility: TransportCompatibility = Field(description="Compatibilité transport")
    
    # Scores détaillés
    time_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Score temps trajet")
    cost_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Score coût transport")
    comfort_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Score confort")
    reliability_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Score fiabilité")
    
    # Score final
    final_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Score final localisation")
    
    # Explications
    explanations: List[str] = Field(default=[], description="Explications détaillées")
    
    def calculate_score(self) -> float:
        """🧮 Calcule le score de localisation enrichi"""
        
        if not self.transport_compatibility.is_compatible:
            self.final_score = 0.0
            self.explanations.append("❌ Aucun mode de transport compatible")
            return 0.0
        
        # Score temps (inversé : plus c'est court, mieux c'est)
        if self.transport_compatibility.recommended_mode:
            best_route = self.transport_compatibility.routes[
                self.transport_compatibility.recommended_mode
            ]
            # Score basé sur durée : 30min = 1.0, 60min = 0.5, 90min = 0.33
            self.time_score = max(0.0, min(1.0, 30 / max(best_route.duration_minutes, 1)))
            
            self.explanations.append(
                f"⏱️ Temps: {best_route.duration_minutes}min → score {self.time_score:.2f}"
            )
        
        # Score coût (simplifié pour MVP)
        self.cost_score = 0.8  # TODO: Calcul coût réel carburant/tickets
        
        # Score confort (basé sur mode de transport)
        comfort_by_mode = {
            TravelMode.DRIVING: 0.9,
            TravelMode.TRANSIT: 0.7,
            TravelMode.BICYCLING: 0.6,
            TravelMode.WALKING: 0.4
        }
        self.comfort_score = comfort_by_mode.get(
            self.transport_compatibility.recommended_mode, 0.5
        )
        
        # Score fiabilité (trafic, météo)
        if (self.transport_compatibility.recommended_mode and 
            self.transport_compatibility.recommended_mode in self.transport_compatibility.routes):
            route = self.transport_compatibility.routes[self.transport_compatibility.recommended_mode]
            if route.traffic and route.traffic.delay_minutes > 10:
                self.reliability_score = 0.6  # Trafic dense
            else:
                self.reliability_score = 0.9  # Trafic fluide
        
        # Score final pondéré
        weights = {
            "time": 0.4,
            "cost": 0.2, 
            "comfort": 0.2,
            "reliability": 0.2
        }
        
        self.final_score = (
            self.time_score * weights["time"] +
            self.cost_score * weights["cost"] +
            self.comfort_score * weights["comfort"] +
            self.reliability_score * weights["reliability"]
        )
        
        self.explanations.append(
            f"🎯 Score final: {self.final_score:.2f} "
            f"(temps:{self.time_score:.1f} coût:{self.cost_score:.1f} "
            f"confort:{self.comfort_score:.1f} fiabilité:{self.reliability_score:.1f})"
        )
        
        return self.final_score

class ConfigTransport(BaseModel):
    """⚙️ Configuration transport (extension Prompt 1)"""
    
    # Extension des TransportPreferences existantes avec géolocalisation
    adresse_domicile: str = Field(description="Adresse du domicile candidat")
    geocoded_location: Optional[GeocodeResult] = Field(None, description="Géolocalisation validée")
    
    # Préférences transport (réutilise l'existant)
    transport_preferences: TransportPreferences = Field(description="Préférences transport")
    
    # Configuration avancée
    max_geocoding_attempts: int = Field(default=3, description="Tentatives géocodage max")
    cache_duration_hours: int = Field(default=24, description="Durée cache itinéraires")
    
    # Télétravail 
    telework_days_per_week: int = Field(default=0, ge=0, le=5, description="Jours télétravail/semaine")
    telework_flexibility: bool = Field(default=False, description="Flexibilité télétravail")
    
    def is_geocoded(self) -> bool:
        """Vérifie si l'adresse est géocodée"""
        return (self.geocoded_location is not None and 
                self.geocoded_location.quality != GeocodeQuality.FAILED)
    
    def needs_regeocoding(self) -> bool:
        """Vérifie si un nouveau géocodage est nécessaire"""
        if not self.is_geocoded():
            return True
            
        # Re-géocoder si cache expiré (30 jours)
        cache_age = datetime.now() - self.geocoded_location.cached_at
        return cache_age.days > 30
