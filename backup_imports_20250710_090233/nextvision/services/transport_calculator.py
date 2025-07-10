"""
🧮 Nextvision - Calculateur Transport Intelligent (Prompt 2)
Orchestration des calculs multi-modaux et scoring avancé

Author: NEXTEN Team
Version: 2.0.0 - Google Maps Intelligence
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from .google_maps_service import GoogleMapsService
from ..models.transport_models import (
    TravelMode, TransportCompatibility, TransportRoute, LocationScore,
    GeocodeResult, ConfigTransport
)
from ..models.questionnaire_advanced import TransportPreferences, MoyenTransport

logger = logging.getLogger(__name__)

class TransportCalculator:
    """🧮 Calculateur transport intelligent avec optimisations"""
    
    def __init__(self, google_maps_service: GoogleMapsService):
        self.google_maps_service = google_maps_service
        
        # Cache local pour optimisations
        self._compatibility_cache: Dict[str, TransportCompatibility] = {}
        self._batch_cache: Dict[str, Dict] = {}
        
        # Métriques performance
        self.calculation_count = 0
        self.cache_hits = 0
        self.total_calculation_time = 0.0
    
    async def calculate_transport_compatibility(
        self,
        candidat_config: ConfigTransport,
        job_address: str,
        departure_time: Optional[datetime] = None
    ) -> TransportCompatibility:
        """🎯 Calcule compatibilité transport candidat/job"""
        
        start_time = datetime.now()
        self.calculation_count += 1
        
        try:
            # 1. Géocodage des adresses
            candidat_location = await self._ensure_candidat_geocoded(candidat_config)
            job_location = await self.google_maps_service.geocode_address(job_address)
            
            # 2. Vérification cache compatibilité
            cache_key = self._create_compatibility_cache_key(
                candidat_location, job_location, candidat_config.transport_preferences
            )
            
            if cache_key in self._compatibility_cache:
                self.cache_hits += 1
                logger.debug("Cache hit pour compatibilité transport")
                return self._compatibility_cache[cache_key]
            
            # 3. Calcul itinéraires multi-modaux
            routes = await self._calculate_multimodal_routes(
                candidat_location, 
                job_location,
                candidat_config.transport_preferences,
                departure_time
            )
            
            # 4. Évaluation compatibilité
            compatibility = TransportCompatibility(
                candidat_preferences=candidat_config.transport_preferences,
                job_location=job_location,
                candidat_location=candidat_location,
                routes=routes
            )
            
            # 5. Évaluation et scoring
            is_compatible = compatibility.evaluate_compatibility()
            
            # 6. Ajustements télétravail
            self._adjust_for_telework(compatibility, candidat_config)
            
            # 7. Mise en cache
            self._compatibility_cache[cache_key] = compatibility
            
            # 8. Métriques
            calculation_time = (datetime.now() - start_time).total_seconds()
            self.total_calculation_time += calculation_time
            
            logger.info(
                f"Compatibilité calculée: {is_compatible} "
                f"(score: {compatibility.compatibility_score:.2f}, "
                f"temps: {calculation_time:.2f}s)"
            )
            
            return compatibility
            
        except Exception as e:
            logger.error(f"Erreur calcul compatibilité: {e}")
            
            # Fallback basique
            return self._create_fallback_compatibility(
                candidat_config, job_address
            )
    
    async def batch_calculate_job_compatibility(
        self,
        candidat_config: ConfigTransport,
        job_addresses: List[str],
        max_concurrent: int = 5
    ) -> Dict[str, TransportCompatibility]:
        """🚀 Calcul batch optimisé pour multiple jobs"""
        
        logger.info(f"Calcul batch: {len(job_addresses)} jobs, max_concurrent={max_concurrent}")
        
        # Géocodage candidat une seule fois
        candidat_location = await self._ensure_candidat_geocoded(candidat_config)
        
        # Géocodage batch des jobs
        job_geocode_tasks = [
            self.google_maps_service.geocode_address(addr) 
            for addr in job_addresses
        ]
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def geocode_with_semaphore(task):
            async with semaphore:
                return await task
        
        job_locations = await asyncio.gather(*[
            geocode_with_semaphore(task) for task in job_geocode_tasks
        ], return_exceptions=True)
        
        # Calcul compatibilité pour chaque job
        compatibility_tasks = []
        valid_jobs = []
        
        for i, (job_addr, job_location) in enumerate(zip(job_addresses, job_locations)):
            if isinstance(job_location, Exception):
                logger.error(f"Erreur géocodage {job_addr}: {job_location}")
                continue
                
            valid_jobs.append(job_addr)
            
            # Calcul routes multi-modales
            task = self._calculate_job_compatibility_from_geocoded(
                candidat_config, candidat_location, job_location
            )
            compatibility_tasks.append(task)
        
        # Exécution batch avec limite concurrence
        async def calc_with_semaphore(task):
            async with semaphore:
                return await task
        
        compatibilities = await asyncio.gather(*[
            calc_with_semaphore(task) for task in compatibility_tasks
        ], return_exceptions=True)
        
        # Assemblage résultats
        results = {}
        for job_addr, compatibility in zip(valid_jobs, compatibilities):
            if isinstance(compatibility, Exception):
                logger.error(f"Erreur compatibilité {job_addr}: {compatibility}")
                # Fallback
                results[job_addr] = self._create_fallback_compatibility(candidat_config, job_addr)
            else:
                results[job_addr] = compatibility
        
        logger.info(f"Batch terminé: {len(results)}/{len(job_addresses)} jobs traités")
        return results
    
    async def calculate_location_score(
        self, 
        compatibility: TransportCompatibility
    ) -> LocationScore:
        """📍 Calcule score localisation enrichi (composant 6/7)"""
        
        # Distance euclidienne de base
        base_distance = self._calculate_euclidean_distance(
            compatibility.candidat_location,
            compatibility.job_location
        )
        
        # Création score localisation
        location_score = LocationScore(
            base_distance_km=base_distance,
            transport_compatibility=compatibility
        )
        
        # Calcul du score enrichi
        final_score = location_score.calculate_score()
        
        logger.debug(f"Score localisation: {final_score:.2f} (distance: {base_distance:.1f}km)")
        
        return location_score
    
    async def pre_filter_jobs_by_transport(
        self,
        candidat_config: ConfigTransport,
        job_addresses: List[str],
        strict_mode: bool = True
    ) -> Tuple[List[str], List[str], Dict[str, str]]:
        """🚫 PRE-FILTERING: Exclut jobs incompatibles avant pondération"""
        
        logger.info(f"PRE-FILTERING: {len(job_addresses)} jobs, strict_mode={strict_mode}")
        
        # Calcul batch compatibilités
        compatibilities = await self.batch_calculate_job_compatibility(
            candidat_config, job_addresses
        )
        
        compatible_jobs = []
        incompatible_jobs = []
        rejection_reasons = {}
        
        for job_addr, compatibility in compatibilities.items():
            if compatibility.is_compatible:
                compatible_jobs.append(job_addr)
            else:
                incompatible_jobs.append(job_addr)
                
                # Raisons de rejet pour analytics
                if compatibility.rejection_reasons:
                    rejection_reasons[job_addr] = "; ".join(
                        compatibility.rejection_reasons
                    )
                else:
                    rejection_reasons[job_addr] = "Aucun mode de transport compatible"
        
        # Statistiques
        exclusion_rate = len(incompatible_jobs) / len(job_addresses) * 100
        
        logger.info(
            f"PRE-FILTERING terminé: "
            f"{len(compatible_jobs)} compatibles, "
            f"{len(incompatible_jobs)} exclus "
            f"(taux exclusion: {exclusion_rate:.1f}%)"
        )
        
        return compatible_jobs, incompatible_jobs, rejection_reasons
    
    async def _ensure_candidat_geocoded(self, candidat_config: ConfigTransport) -> GeocodeResult:
        """📍 S'assure que l'adresse candidat est géocodée"""
        
        if candidat_config.is_geocoded() and not candidat_config.needs_regeocoding():
            return candidat_config.geocoded_location
        
        # Géocodage nécessaire
        geocode_result = await self.google_maps_service.geocode_address(
            candidat_config.adresse_domicile
        )
        
        # Mise à jour config (en production, sauvegarder en DB)
        candidat_config.geocoded_location = geocode_result
        
        return geocode_result
    
    async def _calculate_multimodal_routes(
        self,
        origin: GeocodeResult,
        destination: GeocodeResult, 
        transport_preferences: TransportPreferences,
        departure_time: Optional[datetime] = None
    ) -> Dict[TravelMode, TransportRoute]:
        """🗺️ Calcule itinéraires pour tous modes de transport candidat"""
        
        routes = {}
        
        # Mapping préférences → modes Google Maps
        mode_mapping = {
            MoyenTransport.VOITURE: TravelMode.DRIVING,
            MoyenTransport.TRANSPORT_COMMUN: TravelMode.TRANSIT,
            MoyenTransport.VELO: TravelMode.BICYCLING,
            MoyenTransport.MARCHE: TravelMode.WALKING,
            MoyenTransport.MOTO: TravelMode.DRIVING,
            MoyenTransport.COVOITURAGE: TravelMode.DRIVING
        }
        
        # Calcul parallèle des itinéraires
        tasks = []
        travel_modes = []
        
        for transport_pref in transport_preferences.moyens_selectionnes:
            travel_mode = mode_mapping.get(transport_pref, TravelMode.DRIVING)
            travel_modes.append(travel_mode)
            
            task = self.google_maps_service.calculate_route(
                origin, destination, travel_mode, departure_time
            )
            tasks.append(task)
        
        # Exécution parallèle
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Assemblage résultats
        for travel_mode, result in zip(travel_modes, results):
            if isinstance(result, Exception):
                logger.error(f"Erreur calcul route {travel_mode.value}: {result}")
                continue
            
            routes[travel_mode] = result
        
        return routes
    
    async def _calculate_job_compatibility_from_geocoded(
        self,
        candidat_config: ConfigTransport,
        candidat_location: GeocodeResult,
        job_location: GeocodeResult
    ) -> TransportCompatibility:
        """🎯 Calcule compatibilité à partir de locations géocodées"""
        
        # Calcul routes
        routes = await self._calculate_multimodal_routes(
            candidat_location,
            job_location,
            candidat_config.transport_preferences
        )
        
        # Évaluation compatibilité
        compatibility = TransportCompatibility(
            candidat_preferences=candidat_config.transport_preferences,
            job_location=job_location,
            candidat_location=candidat_location,
            routes=routes
        )
        
        compatibility.evaluate_compatibility()
        
        # Ajustements télétravail
        self._adjust_for_telework(compatibility, candidat_config)
        
        return compatibility
    
    def _adjust_for_telework(
        self, 
        compatibility: TransportCompatibility, 
        candidat_config: ConfigTransport
    ):
        """🏠 Ajuste compatibilité selon télétravail"""
        
        if candidat_config.telework_days_per_week > 0:
            # Bonus télétravail: réduit l'impact des longs trajets
            telework_factor = 1 + (candidat_config.telework_days_per_week / 5) * 0.3
            
            # Application du bonus
            compatibility.compatibility_score = min(
                1.0, compatibility.compatibility_score * telework_factor
            )
            
            if candidat_config.telework_days_per_week >= 3:
                compatibility.compatibility_reasons.append(
                    f"📱 Télétravail {candidat_config.telework_days_per_week}j/semaine "
                    f"→ bonus compatibilité"
                )
    
    def _calculate_euclidean_distance(
        self, 
        location1: GeocodeResult, 
        location2: GeocodeResult
    ) -> float:
        """📏 Distance euclidienne en kilomètres"""
        
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Rayon terre en km
        lat1, lon1 = radians(location1.latitude), radians(location1.longitude)
        lat2, lon2 = radians(location2.latitude), radians(location2.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def _create_compatibility_cache_key(
        self,
        candidat_location: GeocodeResult,
        job_location: GeocodeResult,
        transport_preferences: TransportPreferences
    ) -> str:
        """🔑 Clé cache compatibilité"""
        
        import hashlib
        
        key_parts = [
            f"{candidat_location.latitude:.6f},{candidat_location.longitude:.6f}",
            f"{job_location.latitude:.6f},{job_location.longitude:.6f}",
            "_".join(sorted([m.value for m in transport_preferences.moyens_selectionnes])),
            str(hash(frozenset(transport_preferences.temps_max.items())))
        ]
        
        combined = "_".join(key_parts)
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _create_fallback_compatibility(
        self, 
        candidat_config: ConfigTransport, 
        job_address: str
    ) -> TransportCompatibility:
        """🚨 Compatibilité fallback en cas d'erreur"""
        
        # Géocodage fallback
        fallback_job_location = GeocodeResult(
            address=job_address,
            formatted_address=job_address,
            latitude=48.8566,  # Paris centre
            longitude=2.3522,
            quality="failed",
            place_id="fallback",
            components={}
        )
        
        fallback_candidat_location = GeocodeResult(
            address=candidat_config.adresse_domicile,
            formatted_address=candidat_config.adresse_domicile,
            latitude=48.8566,
            longitude=2.3522,
            quality="failed", 
            place_id="fallback",
            components={}
        )
        
        compatibility = TransportCompatibility(
            candidat_preferences=candidat_config.transport_preferences,
            job_location=fallback_job_location,
            candidat_location=fallback_candidat_location,
            routes={},
            compatible_modes=[],
            compatibility_score=0.5,  # Score neutre
            compatibility_reasons=["⚠️ Mode dégradé - vérification manuelle recommandée"],
            rejection_reasons=["Service géolocalisation temporairement indisponible"]
        )
        
        return compatibility
    
    def get_performance_stats(self) -> Dict:
        """📊 Statistiques performance pour monitoring"""
        
        avg_calc_time = (
            self.total_calculation_time / max(self.calculation_count, 1)
        )
        cache_hit_rate = (
            self.cache_hits / max(self.calculation_count, 1) * 100
        )
        
        return {
            "total_calculations": self.calculation_count,
            "cache_hits": self.cache_hits,
            "cache_hit_rate_percent": cache_hit_rate,
            "average_calculation_time_seconds": avg_calc_time,
            "total_calculation_time_seconds": self.total_calculation_time,
            "compatibility_cache_size": len(self._compatibility_cache)
        }
    
    def clear_cache(self):
        """🧹 Nettoie le cache (pour tests ou maintenance)"""
        self._compatibility_cache.clear()
        self._batch_cache.clear()
        logger.info("Cache calculateur transport nettoyé")
