"""
🗺️ Nextvision - Google Maps Service Principal  
Service central pour intégration Google Maps API avec cache intelligent et rate limiting

Author: NEXTEN Team
Version: 2.0.0 (Prompt 2)
Features: Geocoding, Directions, Distance Matrix, Cache Redis, Fallback
"""

import asyncio
import time
import json
import hashlib
import logging
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass

import googlemaps
import redis.asyncio as redis
from googlemaps.exceptions import GoogleMapsException, TransportError, Timeout, ApiError

from ..config import get_config, GoogleMapsProductionConfig, CacheBackend
from ..models.transport_models import (
    GeocodeResult, TransportRoute, RouteStep, GoogleMapsMode, 
    TrafficModel, TransitMode, TransportConstraint
)

logger = logging.getLogger(__name__)

@dataclass
class RateLimiter:
    """🚦 Rate limiter pour Google Maps API"""
    requests_per_second: int
    last_request_time: float = 0.0
    request_count: int = 0
    window_start: float = 0.0
    
    async def wait_if_needed(self):
        """⏳ Attend si nécessaire pour respecter le rate limit"""
        current_time = time.time()
        
        # Reset window si nécessaire
        if current_time - self.window_start >= 1.0:
            self.window_start = current_time
            self.request_count = 0
        
        # Vérifier si on dépasse le rate limit
        if self.request_count >= self.requests_per_second:
            sleep_time = 1.0 - (current_time - self.window_start)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                # Reset après attente
                self.window_start = time.time()
                self.request_count = 0
        
        self.request_count += 1
        self.last_request_time = current_time

class GoogleMapsService:
    """🗺️ Service principal Google Maps avec cache intelligent"""
    
    def __init__(self, config: Optional[GoogleMapsProductionConfig] = None):
        self.config = config or get_config()
        self.gmaps = googlemaps.Client(
            key=self.config.google_maps.api_key,
            timeout=self.config.google_maps.request_timeout_seconds
        )
        
        # Rate limiting
        self.rate_limiter = RateLimiter(
            requests_per_second=self.config.google_maps.requests_per_second
        )
        
        # Cache
        self.redis_client: Optional[redis.Redis] = None
        self.memory_cache: Dict[str, Dict] = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "total_requests": 0
        }
        
        # Métriques
        self.metrics = {
            "total_requests": 0,
            "geocoding_requests": 0,
            "directions_requests": 0,
            "errors": 0,
            "fallback_used": 0
        }
        
        # État de santé
        self.is_healthy = True
        self.last_error: Optional[str] = None
        
    async def __aenter__(self):
        """🔌 Initialisation async"""
        await self._initialize_cache()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """🔌 Nettoyage async"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def _initialize_cache(self):
        """💾 Initialise le cache Redis si configuré"""
        if self.config.cache.backend == CacheBackend.REDIS:
            try:
                self.redis_client = redis.Redis(
                    host=self.config.cache.redis_host,
                    port=self.config.cache.redis_port,
                    db=self.config.cache.redis_db,
                    password=self.config.cache.redis_password,
                    ssl=self.config.cache.redis_ssl,
                    decode_responses=True
                )
                # Test de connexion
                await self.redis_client.ping()
                logger.info("✅ Redis cache connecté")
            except Exception as e:
                logger.error(f"❌ Erreur connexion Redis: {e}")
                logger.info("🔄 Fallback vers cache mémoire")
                self.config.cache.backend = CacheBackend.MEMORY
    
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """🔑 Génère une clé de cache unique"""
        # Tri des paramètres pour cohérence
        sorted_params = sorted(kwargs.items())
        params_str = json.dumps(sorted_params, sort_keys=True)
        hash_obj = hashlib.md5(params_str.encode())
        return f"nextvision:{prefix}:{hash_obj.hexdigest()}"
    
    async def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """📥 Récupère depuis le cache"""
        try:
            if self.config.cache.backend == CacheBackend.REDIS and self.redis_client:
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    self.cache_stats["hits"] += 1
                    return json.loads(cached_data)
            
            elif self.config.cache.backend == CacheBackend.MEMORY:
                if cache_key in self.memory_cache:
                    cache_entry = self.memory_cache[cache_key]
                    # Vérifier expiration
                    if cache_entry["expires_at"] > time.time():
                        self.cache_stats["hits"] += 1
                        return cache_entry["data"]
                    else:
                        # Nettoyage entrée expirée
                        del self.memory_cache[cache_key]
            
            self.cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur lecture cache: {e}")
            self.cache_stats["misses"] += 1
            return None
    
    async def _set_to_cache(self, cache_key: str, data: Dict, ttl: int):
        """📤 Sauvegarde dans le cache"""
        try:
            if self.config.cache.backend == CacheBackend.REDIS and self.redis_client:
                await self.redis_client.setex(
                    cache_key, 
                    ttl, 
                    json.dumps(data, default=str)
                )
            
            elif self.config.cache.backend == CacheBackend.MEMORY:
                # Nettoyage périodique du cache mémoire
                if len(self.memory_cache) > self.config.cache.max_memory_entries:
                    await self._cleanup_memory_cache()
                
                self.memory_cache[cache_key] = {
                    "data": data,
                    "expires_at": time.time() + ttl
                }
                
        except Exception as e:
            logger.error(f"❌ Erreur écriture cache: {e}")
    
    async def _cleanup_memory_cache(self):
        """🧹 Nettoie le cache mémoire des entrées expirées"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if entry["expires_at"] <= current_time
        ]
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        logger.debug(f"🧹 Cache mémoire nettoyé: {len(expired_keys)} entrées supprimées")
    
    async def _make_google_request(self, request_func, *args, **kwargs):
        """🌐 Exécute une requête Google Maps avec gestion d'erreurs"""
        await self.rate_limiter.wait_if_needed()
        self.metrics["total_requests"] += 1
        
        for attempt in range(self.config.google_maps.retry_attempts):
            try:
                result = request_func(*args, **kwargs)
                self.is_healthy = True
                return result
                
            except (Timeout, TransportError) as e:
                logger.warning(f"⏱️ Timeout Google Maps (tentative {attempt + 1}): {e}")
                if attempt < self.config.google_maps.retry_attempts - 1:
                    wait_time = (2 ** attempt) * self.config.google_maps.retry_backoff_factor
                    await asyncio.sleep(wait_time)
                    continue
                raise
                
            except ApiError as e:
                logger.error(f"❌ Erreur API Google Maps: {e}")
                self.metrics["errors"] += 1
                self.is_healthy = False
                self.last_error = str(e)
                
                # Utiliser la clé backup si disponible
                if (self.config.google_maps.api_key_backup and 
                    "OVER_QUERY_LIMIT" in str(e) and
                    attempt == 0):
                    
                    logger.info("🔄 Tentative avec clé API backup")
                    backup_client = googlemaps.Client(
                        key=self.config.google_maps.api_key_backup
                    )
                    # Remplacer temporairement le client
                    original_client = self.gmaps
                    self.gmaps = backup_client
                    try:
                        result = request_func(*args, **kwargs)
                        return result
                    finally:
                        self.gmaps = original_client
                
                raise
                
            except Exception as e:
                logger.error(f"❌ Erreur inattendue Google Maps: {e}")
                self.metrics["errors"] += 1
                raise
        
        raise GoogleMapsException("Toutes les tentatives ont échoué")
    
    async def geocode_address(self, address: str, region: Optional[str] = None) -> Optional[GeocodeResult]:
        """📍 Géocode une adresse avec cache"""
        cache_key = self._generate_cache_key(
            "geocode",
            address=address,
            region=region or self.config.google_maps.region
        )
        
        # Vérifier cache
        cached_result = await self._get_from_cache(cache_key)
        if cached_result:
            logger.debug(f"📥 Geocoding cache hit: {address}")
            return GeocodeResult(**cached_result, cached=True)
        
        try:
            logger.debug(f"🌐 Geocoding API call: {address}")
            result = await self._make_google_request(
                self.gmaps.geocode,
                address,
                region=region or self.config.google_maps.region,
                language=self.config.google_maps.language
            )
            
            if not result:
                logger.warning(f"⚠️ Aucun résultat géocodage pour: {address}")
                return None
            
            # Premier résultat (meilleur match)
            location_data = result[0]
            location = location_data['geometry']['location']
            
            geocode_result = GeocodeResult(
                address=address,
                formatted_address=location_data.get('formatted_address', address),
                latitude=location['lat'],
                longitude=location['lng'],
                place_id=location_data.get('place_id'),
                types=location_data.get('types', []),
                confidence=1.0,  # Google retourne généralement de bons résultats
                cached=False
            )
            
            # Mise en cache
            await self._set_to_cache(
                cache_key,
                geocode_result.dict(exclude={'cached'}),
                self.config.cache.geocoding_ttl
            )
            
            self.metrics["geocoding_requests"] += 1
            return geocode_result
            
        except Exception as e:
            logger.error(f"❌ Erreur géocodage {address}: {e}")
            
            # Fallback si activé
            if self.config.fallback.enable_fallback:
                return await self._fallback_geocode(address)
            
            return None
    
    async def _fallback_geocode(self, address: str) -> Optional[GeocodeResult]:
        """🔄 Géocodage de fallback (approximatif)"""
        logger.info(f"🔄 Fallback géocodage pour: {address}")
        self.metrics["fallback_used"] += 1
        
        # Logique simplifiée pour Paris (exemple)
        if "paris" in address.lower():
            # Centre approximatif de Paris
            return GeocodeResult(
                address=address,
                formatted_address=f"Paris, France - Approximation",
                latitude=48.8566,
                longitude=2.3522,
                confidence=0.5,  # Confiance réduite pour fallback
                cached=False
            )
        
        # Autres fallbacks possibles...
        return None
    
    async def get_directions(
        self,
        origin: Union[str, Tuple[float, float]],
        destination: Union[str, Tuple[float, float]],
        mode: GoogleMapsMode,
        departure_time: Optional[datetime] = None,
        traffic_model: TrafficModel = TrafficModel.BEST_GUESS,
        avoid: Optional[List[str]] = None
    ) -> Optional[TransportRoute]:
        """🛣️ Calcule un itinéraire avec cache"""
        
        # Préparation des paramètres
        departure_time = departure_time or datetime.now()
        avoid = avoid or []
        
        cache_key = self._generate_cache_key(
            "directions",
            origin=str(origin),
            destination=str(destination),
            mode=mode.value,
            departure_hour=departure_time.hour,  # Cache par heure pour optimiser
            traffic_model=traffic_model.value,
            avoid=sorted(avoid)
        )
        
        # Vérifier cache
        is_peak_hour = departure_time.hour in (
            self.config.transport.peak_hours_morning + 
            self.config.transport.peak_hours_evening
        )
        cache_ttl = (
            self.config.cache.peak_directions_ttl if is_peak_hour
            else self.config.cache.directions_ttl
        )
        
        cached_result = await self._get_from_cache(cache_key)
        if cached_result:
            logger.debug(f"📥 Directions cache hit: {origin} → {destination}")
            return TransportRoute(**cached_result, cached=True)
        
        try:
            logger.debug(f"🌐 Directions API call: {origin} → {destination} ({mode.value})")
            
            # Paramètres de la requête
            request_params = {
                'origin': origin,
                'destination': destination,
                'mode': mode.value,
                'language': self.config.google_maps.language,
                'region': self.config.google_maps.region,
                'alternatives': True  # Récupérer des alternatives
            }
            
            # Paramètres spécifiques au mode
            if mode == GoogleMapsMode.DRIVING:
                request_params.update({
                    'departure_time': departure_time,
                    'traffic_model': traffic_model.value,
                    'avoid': avoid
                })
            elif mode == GoogleMapsMode.TRANSIT:
                request_params.update({
                    'departure_time': departure_time,
                    'transit_routing_preference': 'fewer_transfers'
                })
            
            result = await self._make_google_request(
                self.gmaps.directions,
                **request_params
            )
            
            if not result:
                logger.warning(f"⚠️ Aucun itinéraire trouvé: {origin} → {destination}")
                return None
            
            # Prendre le premier itinéraire (meilleur)
            route_data = result[0]
            leg = route_data['legs'][0]
            
            # Construire les étapes
            steps = []
            for step_data in leg.get('steps', []):
                step = RouteStep(
                    instruction=step_data.get('html_instructions', ''),
                    distance_meters=step_data['distance']['value'],
                    duration_seconds=step_data['duration']['value'],
                    transport_mode=GoogleMapsMode(step_data.get('travel_mode', mode.value).lower()),
                    transit_details=step_data.get('transit_details')
                )
                steps.append(step)
            
            # Géocoder origin et destination si ce sont des strings
            origin_geocode = None
            destination_geocode = None
            
            if isinstance(origin, str):
                origin_geocode = await self.geocode_address(origin)
            if isinstance(destination, str):
                destination_geocode = await self.geocode_address(destination)
            
            # Construire la route
            transport_route = TransportRoute(
                origin=origin_geocode or GeocodeResult(
                    address=str(origin),
                    formatted_address=str(origin),
                    latitude=origin[0] if isinstance(origin, tuple) else 0,
                    longitude=origin[1] if isinstance(origin, tuple) else 0
                ),
                destination=destination_geocode or GeocodeResult(
                    address=str(destination),
                    formatted_address=str(destination),
                    latitude=destination[0] if isinstance(destination, tuple) else 0,
                    longitude=destination[1] if isinstance(destination, tuple) else 0
                ),
                mode=mode,
                total_distance_meters=leg['distance']['value'],
                total_duration_seconds=leg['duration']['value'],
                duration_in_traffic_seconds=leg.get('duration_in_traffic', {}).get('value'),
                traffic_model=traffic_model,
                steps=steps,
                polyline=route_data.get('overview_polyline', {}).get('points'),
                bounds=route_data.get('bounds'),
                warnings=route_data.get('warnings', []),
                cached=False
            )
            
            # Mise en cache
            await self._set_to_cache(
                cache_key,
                transport_route.dict(exclude={'cached', 'calculated_at'}),
                cache_ttl
            )
            
            self.metrics["directions_requests"] += 1
            return transport_route
            
        except Exception as e:
            logger.error(f"❌ Erreur directions {origin} → {destination}: {e}")
            
            # Fallback si activé
            if self.config.fallback.enable_fallback:
                return await self._fallback_directions(origin, destination, mode)
            
            return None
    
    async def _fallback_directions(
        self,
        origin: Union[str, Tuple[float, float]],
        destination: Union[str, Tuple[float, float]],
        mode: GoogleMapsMode
    ) -> Optional[TransportRoute]:
        """🔄 Calcul d'itinéraire de fallback (approximatif)"""
        logger.info(f"🔄 Fallback directions: {origin} → {destination}")
        self.metrics["fallback_used"] += 1
        
        try:
            # Géocoder si nécessaire
            if isinstance(origin, str):
                origin_geo = await self.geocode_address(origin)
                if not origin_geo:
                    return None
                origin_coords = (origin_geo.latitude, origin_geo.longitude)
            else:
                origin_coords = origin
            
            if isinstance(destination, str):
                dest_geo = await self.geocode_address(destination)
                if not dest_geo:
                    return None
                dest_coords = (dest_geo.latitude, dest_geo.longitude)
            else:
                dest_coords = destination
            
            # Calcul distance à vol d'oiseau
            from math import radians, sin, cos, sqrt, atan2
            
            lat1, lon1 = radians(origin_coords[0]), radians(origin_coords[1])
            lat2, lon2 = radians(dest_coords[0]), radians(dest_coords[1])
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            
            # Rayon de la Terre en km
            earth_radius_km = 6371
            crow_flies_distance = earth_radius_km * c
            
            # Ajustement par facteur route
            road_distance = crow_flies_distance * self.config.fallback.crow_flies_factor
            
            # Estimation durée selon vitesse moyenne
            average_speed = self.config.fallback.average_speeds.get(mode.value, 25)
            estimated_duration_hours = road_distance / average_speed
            estimated_duration_seconds = int(estimated_duration_hours * 3600)
            
            # Construire route approximative
            fallback_route = TransportRoute(
                origin=GeocodeResult(
                    address=str(origin),
                    formatted_address=f"Origin - Fallback",
                    latitude=origin_coords[0],
                    longitude=origin_coords[1],
                    confidence=0.5
                ),
                destination=GeocodeResult(
                    address=str(destination),
                    formatted_address=f"Destination - Fallback",
                    latitude=dest_coords[0],
                    longitude=dest_coords[1],
                    confidence=0.5
                ),
                mode=mode,
                total_distance_meters=int(road_distance * 1000),
                total_duration_seconds=estimated_duration_seconds,
                steps=[],
                warnings=["Itinéraire approximatif - Google Maps indisponible"],
                cached=False
            )
            
            return fallback_route
            
        except Exception as e:
            logger.error(f"❌ Erreur fallback directions: {e}")
            return None
    
    def get_cache_stats(self) -> Dict:
        """📊 Statistiques du cache"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (
            self.cache_stats["hits"] / total_requests 
            if total_requests > 0 else 0
        )
        
        return {
            "cache_hits": self.cache_stats["hits"],
            "cache_misses": self.cache_stats["misses"],
            "hit_rate": round(hit_rate, 3),
            "total_cache_requests": total_requests,
            "memory_cache_size": len(self.memory_cache),
            "backend": self.config.cache.backend.value
        }
    
    def get_metrics(self) -> Dict:
        """📊 Métriques complètes du service"""
        return {
            "requests": self.metrics,
            "cache": self.get_cache_stats(),
            "health": {
                "is_healthy": self.is_healthy,
                "last_error": self.last_error
            },
            "rate_limit": {
                "requests_per_second": self.config.google_maps.requests_per_second,
                "current_requests": self.rate_limiter.request_count
            }
        }
    
    async def health_check(self) -> Dict:
        """❤️ Vérification santé du service"""
        try:
            # Test simple de géocodage
            test_result = await self.geocode_address("Paris, France")
            
            return {
                "status": "healthy" if test_result else "degraded",
                "google_maps_api": "available" if test_result else "limited",
                "cache": "connected" if self.redis_client else "memory",
                "metrics": self.get_metrics(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "metrics": self.get_metrics(),
                "timestamp": datetime.now().isoformat()
            }

# Instance globale du service (singleton pattern)
_service_instance: Optional[GoogleMapsService] = None

async def get_google_maps_service() -> GoogleMapsService:
    """🗺️ Récupère l'instance du service Google Maps (singleton)"""
    global _service_instance
    
    if _service_instance is None:
        _service_instance = GoogleMapsService()
        await _service_instance.__aenter__()
    
    return _service_instance

async def close_google_maps_service():
    """🔌 Ferme le service Google Maps"""
    global _service_instance
    
    if _service_instance:
        await _service_instance.__aexit__(None, None, None)
        _service_instance = None
