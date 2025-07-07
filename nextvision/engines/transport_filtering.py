"""
🚫 Nextvision - Engine de Pré-Filtering Transport
Exclusion automatique des jobs incompatibles AVANT la pondération adaptative

Author: NEXTEN Team  
Version: 2.0.0 (Prompt 2)
Innovation: PRE-FILTERING pour performance + précision matching
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass

from ..models.transport_models import (
    CandidatTransportProfile, JobTransportInfo, TransportMatchingResult,
    TransportFilteringReport, GoogleMapsMode, TransportConstraint,
    create_default_candidat_profile
)
from ..services.transport_calculator import TransportCalculatorService
from ..services.google_maps_service import GoogleMapsService
from ..config import get_config

logger = logging.getLogger(__name__)

@dataclass
class FilteringStats:
    """📊 Statistiques de filtering en temps réel"""
    total_jobs: int = 0
    jobs_included: int = 0
    jobs_excluded: int = 0
    processing_time_ms: float = 0
    google_maps_calls: int = 0
    cache_hits: int = 0
    
    @property
    def exclusion_rate(self) -> float:
        return self.jobs_excluded / self.total_jobs if self.total_jobs > 0 else 0
    
    @property  
    def cpu_efficiency_gain(self) -> float:
        """Gain CPU théorique en évitant la pondération adaptative"""
        return self.jobs_excluded * 0.68  # 0.68ms par job évité

class TransportFilteringEngine:
    """🚫 Engine de pré-filtering transport intelligent"""
    
    def __init__(self,
                 google_maps_service: Optional[GoogleMapsService] = None,
                 transport_calculator: Optional[TransportCalculatorService] = None):
        self.google_maps = google_maps_service
        self.transport_calculator = transport_calculator
        self.config = get_config()
        
        # Cache interne pour optimisation
        self.geocoding_cache: Dict[str, Any] = {}
        self.filtering_cache: Dict[str, bool] = {}  # Cache décisions de filtering
        
        # Statistiques globales
        self.global_stats = {
            "total_filtering_sessions": 0,
            "total_jobs_processed": 0,
            "total_jobs_excluded": 0,
            "average_exclusion_rate": 0.0,
            "total_cpu_time_saved_ms": 0.0
        }
    
    async def __aenter__(self):
        """🔌 Initialisation async"""
        if not self.google_maps:
            from ..services.google_maps_service import get_google_maps_service
            self.google_maps = await get_google_maps_service()
        
        if not self.transport_calculator:
            self.transport_calculator = TransportCalculatorService(self.google_maps)
            await self.transport_calculator.__aenter__()
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """🔌 Nettoyage async"""
        if self.transport_calculator:
            await self.transport_calculator.__aexit__(exc_type, exc_val, exc_tb)
    
    def _generate_filtering_cache_key(self, 
                                     candidat_address: str,
                                     job_address: str,
                                     constraints_hash: str) -> str:
        """🔑 Génère clé de cache pour décision de filtering"""
        import hashlib
        
        key_data = f"{candidat_address}|{job_address}|{constraints_hash}"
        return f"filter:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def _hash_constraints(self, constraints: List[TransportConstraint]) -> str:
        """#️⃣ Hash des contraintes pour cache"""
        import hashlib
        import json
        
        constraint_dict = {
            str(i): {
                "mode": c.mode.value,
                "max_duration": c.max_duration_minutes,
                "max_duration_peak": c.max_duration_peak_minutes,
                "max_transfers": c.max_transfers
            }
            for i, c in enumerate(constraints)
        }
        
        constraint_str = json.dumps(constraint_dict, sort_keys=True)
        return hashlib.md5(constraint_str.encode()).hexdigest()[:8]
    
    async def _quick_viability_check(self,
                                   candidat_profile: CandidatTransportProfile,
                                   job_info: JobTransportInfo) -> Tuple[bool, str, Dict]:
        """⚡ Vérification rapide de viabilité (pre-check)"""
        
        try:
            # Vérification cache
            constraints_hash = self._hash_constraints(candidat_profile.constraints)
            cache_key = self._generate_filtering_cache_key(
                candidat_profile.home_address,
                job_info.office_address,
                constraints_hash
            )
            
            if cache_key in self.filtering_cache:
                logger.debug(f"📥 Cache hit pour filtering: {job_info.job_id}")
                return self.filtering_cache[cache_key], "Cache hit", {"cache_used": True}
            
            # Géocodage des adresses (avec cache)
            origin_geo = await self.google_maps.geocode_address(candidat_profile.home_address)
            dest_geo = await self.google_maps.geocode_address(job_info.office_address)
            
            if not origin_geo or not dest_geo:
                logger.warning(f"⚠️ Géocodage échoué pour job {job_info.job_id}")
                # Inclure par défaut si géocodage échoue
                return True, "Géocodage échoué - inclusion par défaut", {"geocoding_failed": True}
            
            # Calcul distance à vol d'oiseau pour pré-screening
            from math import radians, sin, cos, sqrt, atan2
            
            lat1, lon1 = radians(origin_geo.latitude), radians(origin_geo.longitude)
            lat2, lon2 = radians(dest_geo.latitude), radians(dest_geo.longitude)
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            
            crow_flies_km = 6371 * c
            
            # Estimation rapide des temps selon distance
            estimated_times = {
                GoogleMapsMode.WALKING: crow_flies_km / 5 * 60,  # 5 km/h
                GoogleMapsMode.BICYCLING: crow_flies_km / 15 * 60,  # 15 km/h
                GoogleMapsMode.DRIVING: crow_flies_km * 1.4 / 40 * 60,  # 40 km/h avec détours
                GoogleMapsMode.TRANSIT: crow_flies_km * 1.6 / 25 * 60   # 25 km/h avec correspondances
            }
            
            # Vérification si au moins un mode semble viable
            viable_modes = []
            for constraint in candidat_profile.constraints:
                estimated_time = estimated_times.get(constraint.mode, float('inf'))
                max_time = constraint.max_duration_peak_minutes or constraint.max_duration_minutes
                
                if estimated_time <= (max_time + constraint.tolerance_minutes):
                    viable_modes.append(constraint.mode)
            
            is_viable = len(viable_modes) > 0
            reason = f"Distance: {crow_flies_km:.1f}km - Modes viables: {[m.value for m in viable_modes]}"
            
            details = {
                "crow_flies_km": crow_flies_km,
                "estimated_times": {m.value: t for m, t in estimated_times.items()},
                "viable_modes": [m.value for m in viable_modes],
                "cache_used": False
            }
            
            # Mise en cache de la décision
            self.filtering_cache[cache_key] = is_viable
            
            return is_viable, reason, details
            
        except Exception as e:
            logger.error(f"❌ Erreur quick viability check: {e}")
            # En cas d'erreur, inclure par défaut
            return True, f"Erreur pré-check: {str(e)}", {"error": True}
    
    async def _detailed_transport_analysis(self,
                                         candidat_profile: CandidatTransportProfile,
                                         job_info: JobTransportInfo) -> TransportMatchingResult:
        """🔍 Analyse transport détaillée pour décision finale"""
        
        return await self.transport_calculator.calculate_multi_modal_options(
            candidat_profile=candidat_profile,
            job_info=job_info,
            departure_time=datetime.now()
        )
    
    async def filter_single_job(self,
                              candidat_profile: CandidatTransportProfile,
                              job_data: Dict,
                              quick_mode: bool = True) -> Tuple[bool, Dict]:
        """🎯 Filtre un job unique"""
        
        start_time = time.time()
        
        try:
            # Extraction des infos job
            job_info = JobTransportInfo(
                job_id=job_data.get("id", "unknown"),
                office_address=job_data.get("address", ""),
                remote_policy=job_data.get("remote_policy", "none"),
                flexible_hours=job_data.get("flexible_hours", False),
                parking_available=job_data.get("parking", False)
            )
            
            # Vérification adresse valide
            if not job_info.office_address.strip():
                logger.debug(f"📋 Job {job_info.job_id}: Pas d'adresse - INCLUS par défaut")
                return True, {
                    "inclusion_reason": "Pas d'adresse spécifiée",
                    "processing_time_ms": (time.time() - start_time) * 1000,
                    "transport_analysis": None
                }
            
            # Mode rapide (pre-screening)
            if quick_mode:
                is_viable, reason, details = await self._quick_viability_check(
                    candidat_profile, job_info
                )
                
                processing_time = (time.time() - start_time) * 1000
                
                result = {
                    "inclusion_reason" if is_viable else "exclusion_reason": reason,
                    "processing_time_ms": processing_time,
                    "quick_check_details": details,
                    "transport_analysis": None
                }
                
                if is_viable:
                    logger.debug(f"✅ Job {job_info.job_id}: INCLUS - {reason}")
                else:
                    logger.debug(f"❌ Job {job_info.job_id}: EXCLU - {reason}")
                
                return is_viable, result
            
            # Mode détaillé (analyse complète)
            else:
                transport_result = await self._detailed_transport_analysis(
                    candidat_profile, job_info
                )
                
                is_viable = transport_result.is_transport_compatible
                processing_time = (time.time() - start_time) * 1000
                
                reason = (
                    f"Compatible - {len(transport_result.recommended_modes)} modes viables" 
                    if is_viable else 
                    f"Incompatible - {'; '.join(transport_result.excluded_reasons)}"
                )
                
                result = {
                    "inclusion_reason" if is_viable else "exclusion_reason": reason,
                    "processing_time_ms": processing_time,
                    "transport_analysis": transport_result.dict(),
                    "best_mode": transport_result.best_transport_mode.value if transport_result.best_transport_mode else None,
                    "overall_score": transport_result.overall_transport_score
                }
                
                if is_viable:
                    logger.info(f"✅ Job {job_info.job_id}: INCLUS - Score {transport_result.overall_transport_score:.2f}")
                else:
                    logger.info(f"❌ Job {job_info.job_id}: EXCLU - {reason}")
                
                return is_viable, result
            
        except Exception as e:
            logger.error(f"❌ Erreur filtering job {job_data.get('id', 'unknown')}: {e}")
            
            # En cas d'erreur, inclure par défaut
            return True, {
                "inclusion_reason": f"Erreur filtering: {str(e)}",
                "processing_time_ms": (time.time() - start_time) * 1000,
                "transport_analysis": None,
                "error": True
            }
    
    async def filter_jobs_batch(self,
                              candidat_profile: CandidatTransportProfile,
                              jobs: List[Dict],
                              quick_mode: bool = True,
                              max_concurrent: int = 10) -> Tuple[List[Dict], List[Dict], TransportFilteringReport]:
        """🚀 Filtre un batch de jobs avec parallélisation"""
        
        start_time = time.time()
        stats = FilteringStats(total_jobs=len(jobs))
        
        logger.info(f"🚫 Démarrage pré-filtering: {len(jobs)} jobs à analyser")
        
        # Semaphore pour limiter la concurrence
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def filter_job_with_semaphore(job_data):
            async with semaphore:
                return await self.filter_single_job(candidat_profile, job_data, quick_mode)
        
        try:
            # Traitement parallèle
            filtering_tasks = [
                filter_job_with_semaphore(job) for job in jobs
            ]
            
            results = await asyncio.gather(*filtering_tasks, return_exceptions=True)
            
            # Tri des résultats
            jobs_included = []
            jobs_excluded = []
            exclusion_details = {}
            exclusion_by_mode = {}
            
            for i, result in enumerate(results):
                job = jobs[i]
                
                if isinstance(result, Exception):
                    logger.error(f"❌ Exception pour job {job.get('id')}: {result}")
                    # Inclure en cas d'exception
                    job_with_metadata = job.copy()
                    job_with_metadata["filtering_metadata"] = {
                        "status": "error",
                        "error": str(result)
                    }
                    jobs_included.append(job_with_metadata)
                    stats.jobs_included += 1
                    continue
                
                is_included, metadata = result
                
                job_with_metadata = job.copy()
                job_with_metadata["filtering_metadata"] = metadata
                
                if is_included:
                    jobs_included.append(job_with_metadata)
                    stats.jobs_included += 1
                else:
                    jobs_excluded.append(job_with_metadata)
                    stats.jobs_excluded += 1
                    
                    # Collecte stats d'exclusion
                    exclusion_reason = metadata.get("exclusion_reason", "Unknown")
                    exclusion_details[job.get("id", f"job_{i}")] = exclusion_reason
                    
                    # Stats par mode (si analyse détaillée)
                    if not quick_mode and "transport_analysis" in metadata:
                        transport_analysis = metadata["transport_analysis"]
                        for excluded_reason in transport_analysis.get("excluded_reasons", []):
                            if ":" in excluded_reason:
                                mode = excluded_reason.split(":")[0]
                                exclusion_by_mode[mode] = exclusion_by_mode.get(mode, 0) + 1
            
            # Finalisation des stats
            processing_time = (time.time() - start_time) * 1000
            stats.processing_time_ms = processing_time
            
            # Métriques Google Maps (estimation)
            stats.google_maps_calls = len(jobs) * 2 if quick_mode else len(jobs) * 4  # Géocodage + directions
            stats.cache_hits = sum(1 for result in results 
                                 if isinstance(result, tuple) and 
                                 result[1].get("quick_check_details", {}).get("cache_used", False))
            
            # Rapport de filtering
            report = TransportFilteringReport(
                candidat_id=candidat_profile.candidat_id or "unknown",
                total_jobs_analyzed=stats.total_jobs,
                jobs_included=stats.jobs_included,
                jobs_excluded=stats.jobs_excluded,
                exclusion_rate=stats.exclusion_rate,
                cpu_time_saved_ms=stats.cpu_efficiency_gain,
                google_maps_requests=stats.google_maps_calls,
                cache_efficiency=stats.cache_hits / stats.total_jobs if stats.total_jobs > 0 else 0,
                exclusion_by_mode=exclusion_by_mode,
                processing_duration_ms=processing_time
            )
            
            # Mise à jour des stats globales
            self._update_global_stats(stats)
            
            # Logs de résumé
            logger.info(f"✅ Pré-filtering terminé:")
            logger.info(f"   📊 {stats.jobs_included} jobs INCLUS / {stats.jobs_excluded} jobs EXCLUS")
            logger.info(f"   📈 Taux d'exclusion: {stats.exclusion_rate:.1%}")
            logger.info(f"   ⚡ Temps CPU économisé: {stats.cpu_efficiency_gain:.1f}ms")
            logger.info(f"   🕐 Durée totale: {processing_time:.1f}ms")
            logger.info(f"   💾 Cache hits: {stats.cache_hits}/{stats.total_jobs}")
            
            return jobs_included, jobs_excluded, report
            
        except Exception as e:
            logger.error(f"❌ Erreur critique pendant filtering batch: {e}")
            
            # En cas d'erreur critique, retourner tous les jobs inclus
            report = TransportFilteringReport(
                candidat_id=candidat_profile.candidat_id or "unknown",
                total_jobs_analyzed=len(jobs),
                jobs_included=len(jobs),
                jobs_excluded=0,
                exclusion_rate=0.0,
                processing_duration_ms=(time.time() - start_time) * 1000,
                google_maps_requests=0,
                cache_efficiency=0.0
            )
            
            return jobs, [], report
    
    def _update_global_stats(self, session_stats: FilteringStats):
        """📊 Met à jour les statistiques globales"""
        self.global_stats["total_filtering_sessions"] += 1
        self.global_stats["total_jobs_processed"] += session_stats.total_jobs
        self.global_stats["total_jobs_excluded"] += session_stats.jobs_excluded
        self.global_stats["total_cpu_time_saved_ms"] += session_stats.cpu_efficiency_gain
        
        # Moyenne mobile du taux d'exclusion
        total_jobs = self.global_stats["total_jobs_processed"]
        if total_jobs > 0:
            self.global_stats["average_exclusion_rate"] = (
                self.global_stats["total_jobs_excluded"] / total_jobs
            )
    
    async def create_candidat_profile_from_legacy(self,
                                                candidat_data: Dict,
                                                default_constraints: Optional[List[TransportConstraint]] = None) -> CandidatTransportProfile:
        """🔄 Convertit données legacy candidat en profil transport"""
        
        candidat_id = candidat_data.get("id", "unknown")
        
        # Extraction adresse
        home_address = ""
        if "location_preferences" in candidat_data:
            location_prefs = candidat_data["location_preferences"]
            home_address = location_prefs.get("city", "")
        
        if not home_address and "personal_info" in candidat_data:
            # Fallback sur autres champs
            home_address = candidat_data["personal_info"].get("city", "Paris, France")
        
        # Contraintes par défaut si non spécifiées
        if default_constraints:
            constraints = default_constraints
        else:
            # Contraintes basiques voiture + transport en commun
            constraints = [
                TransportConstraint(
                    mode=GoogleMapsMode.DRIVING,
                    max_duration_minutes=30,
                    max_duration_peak_minutes=45
                ),
                TransportConstraint(
                    mode=GoogleMapsMode.TRANSIT,
                    max_duration_minutes=45,
                    max_duration_peak_minutes=60,
                    max_transfers=2
                )
            ]
        
        return CandidatTransportProfile(
            candidat_id=candidat_id,
            home_address=home_address,
            constraints=constraints,
            accepts_remote_work=candidat_data.get("remote_work_acceptable", False),
            remote_days_per_week=candidat_data.get("remote_days_per_week", 0),
            flexible_hours=candidat_data.get("flexible_hours", False)
        )
    
    def get_global_stats(self) -> Dict:
        """📊 Retourne les statistiques globales"""
        return self.global_stats.copy()
    
    def clear_cache(self):
        """🧹 Vide les caches internes"""
        self.geocoding_cache.clear()
        self.filtering_cache.clear()
        logger.info("🧹 Caches de filtering vidés")

# Fonctions helper pour usage simplifié

async def quick_filter_jobs(candidat_address: str,
                          transport_constraints: List[TransportConstraint],
                          jobs: List[Dict],
                          candidat_id: str = "temp") -> Tuple[List[Dict], List[Dict]]:
    """⚡ Fonction helper pour filtering rapide"""
    
    async with TransportFilteringEngine() as engine:
        # Création profil candidat
        candidat_profile = CandidatTransportProfile(
            candidat_id=candidat_id,
            home_address=candidat_address,
            constraints=transport_constraints
        )
        
        included, excluded, _ = await engine.filter_jobs_batch(
            candidat_profile=candidat_profile,
            jobs=jobs,
            quick_mode=True
        )
        
        return included, excluded

async def detailed_filter_jobs(candidat_profile: CandidatTransportProfile,
                             jobs: List[Dict]) -> TransportFilteringReport:
    """🔍 Fonction helper pour filtering détaillé avec rapport complet"""
    
    async with TransportFilteringEngine() as engine:
        _, _, report = await engine.filter_jobs_batch(
            candidat_profile=candidat_profile,
            jobs=jobs,
            quick_mode=False
        )
        
        return report
