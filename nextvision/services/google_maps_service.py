"""
🗺️ Nextvision - Service Google Maps Core (Prompt 2)
Geocoding, Directions API et gestion cache intelligente

Author: NEXTEN Team
Version: 2.0.0 - Google Maps Intelligence
"""

import asyncio
import aiohttp
import json
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import nextvision_logging as logging
from urllib.parse import urlencode

from ..models.transport_models import (
    GeocodeResult, GeocodeQuality, TravelMode, TransportRoute, 
    TrafficCondition, RouteStep
)

logger = logging.getLogger(__name__)

class GoogleMapsService:
    """🗺️ Service Google Maps avec cache intelligent et rate limiting"""
    
    def __init__(self, api_key: str, cache_duration_hours: int = 24):
        self.api_key = api_key
        self.cache_duration_hours = cache_duration_hours
        self.base_url = "https://maps.googleapis.com/maps/api"
        
        # Cache en mémoire (TODO: Redis en production)
        self._geocode_cache: Dict[str, GeocodeResult] = {}
        self._directions_cache: Dict[str, TransportRoute] = {}
        
        # Rate limiting
        self.requests_per_day = 25000  # Limite Google Maps API
        self.daily_usage = 0
        self.last_reset = datetime.now().date()
        
        # Circuit breaker pour la résilience
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_reset_time = None
    
    async def geocode_address(self, address: str, force_refresh: bool = False) -> GeocodeResult:
        """📍 Géocode une adresse avec cache intelligent"""
        
        # Normalisation de l'adresse pour le cache
        normalized_address = self._normalize_address(address)
        cache_key = f"geocode_{hashlib.md5(normalized_address.encode()).hexdigest()}"
        
        # Vérification cache
        if not force_refresh and cache_key in self._geocode_cache:
            cached_result = self._geocode_cache[cache_key]
            if self._is_cache_valid(cached_result.cached_at):
                logger.debug(f"Cache hit pour géocodage: {address}")
                return cached_result
        
        # Vérification circuit breaker
        if self._is_circuit_breaker_open():
            logger.warning("Circuit breaker ouvert - géocodage en mode dégradé")
            return self._create_fallback_geocode(address)
        
        try:
            # Appel API Google Maps
            geocode_result = await self._call_geocoding_api(normalized_address)
            
            # Mise en cache
            self._geocode_cache[cache_key] = geocode_result
            
            # Reset circuit breaker si succès
            self.circuit_breaker_failures = 0
            
            logger.info(f"Géocodage réussi: {address} → {geocode_result.formatted_address}")
            return geocode_result
            
        except Exception as e:
            logger.error(f"Erreur géocodage {address}: {e}")
            self._handle_api_failure()
            
            # Fallback en cas d'erreur
            return self._create_fallback_geocode(address)
    
    async def calculate_route(
        self, 
        origin: GeocodeResult, 
        destination: GeocodeResult,
        travel_mode: TravelMode,
        departure_time: Optional[datetime] = None
    ) -> TransportRoute:
        """🛣️ Calcule un itinéraire avec gestion trafic"""
        
        cache_key = self._create_route_cache_key(origin, destination, travel_mode, departure_time)
        
        # Vérification cache (plus court pour les itinéraires - 1h)
        if cache_key in self._directions_cache:
            cached_route = self._directions_cache[cache_key]
            if self._is_route_cache_valid(cached_route.calculated_at):
                logger.debug(f"Cache hit pour itinéraire: {travel_mode.value}")
                return cached_route
        
        # Vérification circuit breaker
        if self._is_circuit_breaker_open():
            logger.warning("Circuit breaker ouvert - calcul itinéraire en mode dégradé")
            return self._create_fallback_route(origin, destination, travel_mode)
        
        try:
            # Appel API Directions
            route = await self._call_directions_api(origin, destination, travel_mode, departure_time)
            
            # Mise en cache
            self._directions_cache[cache_key] = route
            
            # Reset circuit breaker
            self.circuit_breaker_failures = 0
            
            logger.info(f"Itinéraire calculé: {travel_mode.value} - {route.duration_minutes}min")
            return route
            
        except Exception as e:
            logger.error(f"Erreur calcul itinéraire: {e}")
            self._handle_api_failure()
            
            # Fallback
            return self._create_fallback_route(origin, destination, travel_mode)
    
    async def batch_calculate_routes(
        self,
        origin: GeocodeResult,
        destinations: List[GeocodeResult], 
        travel_modes: List[TravelMode]
    ) -> Dict[str, Dict[TravelMode, TransportRoute]]:
        """🚀 Calcul batch optimisé pour performance"""
        
        results = {}
        
        # Grouper les requêtes par lots pour respecter les limites API
        batch_size = 10  # Google Distance Matrix limite
        
        for i in range(0, len(destinations), batch_size):
            batch_destinations = destinations[i:i + batch_size]
            
            # Appels parallèles pour différents modes de transport
            tasks = []
            for travel_mode in travel_modes:
                for destination in batch_destinations:
                    task = self.calculate_route(origin, destination, travel_mode)
                    tasks.append((destination.formatted_address, travel_mode, task))
            
            # Exécution parallèle avec limite de concurrence
            semaphore = asyncio.Semaphore(5)  # Max 5 requêtes simultanées
            
            async def execute_with_semaphore(dest_key, mode, task):
                async with semaphore:
                    return dest_key, mode, await task
            
            batch_results = await asyncio.gather(*[
                execute_with_semaphore(dest_key, mode, task) 
                for dest_key, mode, task in tasks
            ], return_exceptions=True)
            
            # Traitement des résultats
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Erreur batch: {result}")
                    continue
                    
                dest_key, mode, route = result
                if dest_key not in results:
                    results[dest_key] = {}
                results[dest_key][mode] = route
        
        return results
    
    async def _call_geocoding_api(self, address: str) -> GeocodeResult:
        """📍 Appel API Geocoding Google Maps"""
        
        params = {
            'address': address,
            'key': self.api_key,
            'language': 'fr',
            'region': 'fr'  # Biais France
        }
        
        url = f"{self.base_url}/geocode/json?" + urlencode(params)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                self._increment_usage()
                
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}: {await response.text()}")
                
                data = await response.json()
                
                if data['status'] != 'OK':
                    raise Exception(f"Geocoding failed: {data['status']}")
                
                if not data['results']:
                    raise Exception("Aucun résultat trouvé")
                
                # Parse premier résultat
                result = data['results'][0]
                geometry = result['geometry']
                location = geometry['location']
                
                # Déterminer qualité géocodage
                quality = self._determine_geocode_quality(geometry.get('location_type', ''))
                
                return GeocodeResult(
                    address=address,
                    formatted_address=result['formatted_address'],
                    latitude=location['lat'],
                    longitude=location['lng'], 
                    quality=quality,
                    place_id=result['place_id'],
                    components=self._extract_address_components(result.get('address_components', [])),
                    cached_at=datetime.now()
                )
    
    async def _call_directions_api(
        self,
        origin: GeocodeResult,
        destination: GeocodeResult, 
        travel_mode: TravelMode,
        departure_time: Optional[datetime] = None
    ) -> TransportRoute:
        """🛣️ Appel API Directions Google Maps"""
        
        params = {
            'origin': f"{origin.latitude},{origin.longitude}",
            'destination': f"{destination.latitude},{destination.longitude}",
            'mode': travel_mode.value,
            'key': self.api_key,
            'language': 'fr',
            'region': 'fr',
            'units': 'metric'
        }
        
        # Gestion trafic pour voiture et transport public
        if travel_mode in [TravelMode.DRIVING, TravelMode.TRANSIT]:
            if departure_time:
                params['departure_time'] = int(departure_time.timestamp())
            else:
                params['departure_time'] = 'now'
                
            if travel_mode == TravelMode.DRIVING:
                params['traffic_model'] = 'best_guess'
        
        url = f"{self.base_url}/directions/json?" + urlencode(params)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                self._increment_usage()
                
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}: {await response.text()}")
                
                data = await response.json()
                
                if data['status'] != 'OK':
                    raise Exception(f"Directions failed: {data['status']}")
                
                if not data['routes']:
                    raise Exception("Aucune route trouvée")
                
                # Parse première route
                route_data = data['routes'][0]
                leg = route_data['legs'][0]  # Premier segment
                
                # Extraction steps
                steps = []
                for step_data in leg.get('steps', []):
                    step = RouteStep(
                        distance_meters=step_data['distance']['value'],
                        duration_seconds=step_data['duration']['value'],
                        travel_mode=TravelMode(step_data.get('travel_mode', travel_mode.value).lower()),
                        instructions=step_data.get('html_instructions', '').replace('<[^>]+>', '')  # Strip HTML
                    )
                    steps.append(step)
                
                # Gestion trafic
                traffic = None
                if 'duration_in_traffic' in leg:
                    normal_duration = leg['duration']['value']
                    traffic_duration = leg['duration_in_traffic']['value']
                    
                    traffic = TrafficCondition(
                        duration_in_traffic_seconds=traffic_duration,
                        traffic_factor=traffic_duration / max(normal_duration, 1),
                        rush_hour=self._is_rush_hour(departure_time)
                    )
                
                # Cache validity (1h pour itinéraires)
                cached_until = datetime.now() + timedelta(hours=1)
                
                return TransportRoute(
                    origin=origin,
                    destination=destination,
                    travel_mode=travel_mode,
                    distance_meters=leg['distance']['value'],
                    duration_seconds=leg['duration']['value'],
                    traffic=traffic,
                    steps=steps,
                    polyline=route_data.get('overview_polyline', {}).get('points', ''),
                    calculated_at=datetime.now(),
                    cached_until=cached_until
                )
    
    def _normalize_address(self, address: str) -> str:
        """🔧 Normalise une adresse pour cache cohérent"""
        return address.strip().lower().replace(',', ' ').replace('  ', ' ')
    
    def _determine_geocode_quality(self, location_type: str) -> GeocodeQuality:
        """📍 Détermine la qualité du géocodage"""
        quality_map = {
            'ROOFTOP': GeocodeQuality.EXACT,
            'RANGE_INTERPOLATED': GeocodeQuality.APPROXIMATE, 
            'GEOMETRIC_CENTER': GeocodeQuality.APPROXIMATE,
            'APPROXIMATE': GeocodeQuality.PARTIAL
        }
        return quality_map.get(location_type, GeocodeQuality.PARTIAL)
    
    def _extract_address_components(self, components: List[Dict]) -> Dict:
        """🏠 Extrait composants d'adresse structurés"""
        extracted = {}
        for component in components:
            types = component.get('types', [])
            if 'street_number' in types:
                extracted['street_number'] = component['long_name']
            elif 'route' in types:
                extracted['street'] = component['long_name']
            elif 'locality' in types:
                extracted['city'] = component['long_name']
            elif 'postal_code' in types:
                extracted['postal_code'] = component['long_name']
        return extracted
    
    def _create_route_cache_key(
        self, 
        origin: GeocodeResult, 
        destination: GeocodeResult,
        travel_mode: TravelMode,
        departure_time: Optional[datetime]
    ) -> str:
        """🔑 Crée clé cache pour itinéraires"""
        key_parts = [
            f"{origin.latitude:.6f},{origin.longitude:.6f}",
            f"{destination.latitude:.6f},{destination.longitude:.6f}",
            travel_mode.value
        ]
        
        # Arrondir departure_time à l'heure pour cache plus efficace
        if departure_time:
            hour_rounded = departure_time.replace(minute=0, second=0, microsecond=0)
            key_parts.append(hour_rounded.isoformat())
        
        combined = "_".join(key_parts)
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _is_cache_valid(self, cached_at: datetime) -> bool:
        """⏰ Vérifie validité cache géocodage (24h)"""
        return datetime.now() - cached_at < timedelta(hours=self.cache_duration_hours)
    
    def _is_route_cache_valid(self, calculated_at: datetime) -> bool:
        """⏰ Vérifie validité cache itinéraires (1h)"""
        return datetime.now() - calculated_at < timedelta(hours=1)
    
    def _is_rush_hour(self, departure_time: Optional[datetime]) -> bool:
        """🚦 Détermine si c'est l'heure de pointe"""
        if not departure_time:
            departure_time = datetime.now()
        
        hour = departure_time.hour
        weekday = departure_time.weekday()
        
        # Lundi-Vendredi: 7h-9h et 17h-19h
        if weekday < 5:  # Lundi = 0, Vendredi = 4
            return (7 <= hour <= 9) or (17 <= hour <= 19)
        
        return False
    
    def _increment_usage(self):
        """📊 Incrémente compteur usage API"""
        today = datetime.now().date()
        if today != self.last_reset:
            self.daily_usage = 0
            self.last_reset = today
        
        self.daily_usage += 1
        
        if self.daily_usage > self.requests_per_day * 0.9:  # Alerte à 90%
            logger.warning(f"Usage API élevé: {self.daily_usage}/{self.requests_per_day}")
    
    def _is_circuit_breaker_open(self) -> bool:
        """🔌 Vérifie état circuit breaker"""
        if self.circuit_breaker_failures < self.circuit_breaker_threshold:
            return False
        
        if self.circuit_breaker_reset_time is None:
            self.circuit_breaker_reset_time = datetime.now() + timedelta(minutes=5)
        
        if datetime.now() > self.circuit_breaker_reset_time:
            # Reset circuit breaker
            self.circuit_breaker_failures = 0
            self.circuit_breaker_reset_time = None
            return False
        
        return True
    
    def _handle_api_failure(self):
        """❌ Gère les échecs API"""
        self.circuit_breaker_failures += 1
        logger.error(f"Échec API Google Maps ({self.circuit_breaker_failures}/{self.circuit_breaker_threshold})")
    
    def _create_fallback_geocode(self, address: str) -> GeocodeResult:
        """🚨 Géocodage de fallback basique"""
        # Fallback très simple - centre de Paris
        logger.warning(f"Fallback géocodage pour: {address}")
        return GeocodeResult(
            address=address,
            formatted_address=f"{address} (approximatif)",
            latitude=48.8566,  # Notre-Dame
            longitude=2.3522,
            quality=GeocodeQuality.FAILED,
            place_id="fallback",
            components={},
            cached_at=datetime.now()
        )
    
    def _create_fallback_route(
        self, 
        origin: GeocodeResult, 
        destination: GeocodeResult,
        travel_mode: TravelMode
    ) -> TransportRoute:
        """🚨 Itinéraire de fallback basé sur distance euclidienne"""
        
        # Calcul distance euclidienne approximative
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371000  # Rayon terre en mètres
        lat1, lon1 = radians(origin.latitude), radians(origin.longitude)
        lat2, lon2 = radians(destination.latitude), radians(destination.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance_meters = int(R * c)
        
        # Estimation durée selon mode transport
        speed_kmh_by_mode = {
            TravelMode.WALKING: 5,
            TravelMode.BICYCLING: 15,
            TravelMode.DRIVING: 30,  # Moyenne urbaine
            TravelMode.TRANSIT: 20
        }
        
        speed = speed_kmh_by_mode.get(travel_mode, 20)
        duration_seconds = int((distance_meters / 1000) / speed * 3600)
        
        logger.warning(f"Fallback itinéraire: {distance_meters}m en {duration_seconds//60}min")
        
        return TransportRoute(
            origin=origin,
            destination=destination,
            travel_mode=travel_mode,
            distance_meters=distance_meters,
            duration_seconds=duration_seconds,
            traffic=None,
            steps=[],
            polyline="",
            calculated_at=datetime.now(),
            cached_until=datetime.now() + timedelta(minutes=30)  # Cache court pour fallback
        )
    
    def get_cache_stats(self) -> Dict:
        """📊 Statistiques cache pour monitoring"""
        return {
            "geocode_cache_size": len(self._geocode_cache),
            "directions_cache_size": len(self._directions_cache),
            "daily_usage": self.daily_usage,
            "daily_limit": self.requests_per_day,
            "usage_percentage": (self.daily_usage / self.requests_per_day) * 100,
            "circuit_breaker_failures": self.circuit_breaker_failures,
            "circuit_breaker_open": self._is_circuit_breaker_open()
        }
