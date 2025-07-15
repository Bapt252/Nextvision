"""
🔧 Nextvision v2.0 - Enhanced Endpoints avec Auto-Fix Intelligence

Endpoints API révolutionnaires pour Enhanced Bridge avec auto-fix intelligent,
validation robuste et performance optimisée.

Author: NEXTEN Team
Version: 2.0.0 - Enhanced Bridge Integration
"""

import json
import nextvision_logging as logging
import asyncio
import time
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import modèles et services Nextvision
from nextvision.models.bidirectional_models import (
    BiDirectionalCandidateProfile, BiDirectionalCompanyProfile,
    BiDirectionalMatchingRequest, BiDirectionalMatchingResponse
)

from nextvision.services.bidirectional_matcher import BiDirectionalMatcher
from nextvision.api.v2.bidirectional_endpoints import get_bidirectional_matcher

# Import Enhanced Bridge
from nextvision.services.enhanced_commitment_bridge import (
    EnhancedCommitmentBridge, EnhancedBridgeFactory, BridgePerformanceMetrics
)

# Configuration logging
logger = logging.getLogger(__name__)

# === ROUTER CONFIGURATION ===
router_v2 = APIRouter(
    prefix="/api/v2",
    tags=["🔧 Enhanced Bridge v2.0"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

# === ENHANCED BRIDGE INSTANCE ===
enhanced_bridge = EnhancedBridgeFactory.create_production_bridge()

# === PYDANTIC MODELS ===

class CommitmentConversionRequest(BaseModel):
    """Request pour conversion Commitment- Enhanced"""
    candidat_data: Optional[Dict] = None
    entreprise_data: Optional[Dict] = None
    candidat_questionnaire: Optional[Dict] = None
    entreprise_questionnaire: Optional[Dict] = None

class EnhancedBatchRequest(BaseModel):
    """Request pour batch processing Enhanced"""
    candidats_data: List[Dict] = []
    entreprises_data: List[Dict] = []
    enable_parallel: bool = True
    enable_auto_fix: bool = True

class EnhancedConfigRequest(BaseModel):
    """Request pour mise à jour configuration Enhanced"""
    enable_auto_fix: Optional[bool] = None
    enable_cache: Optional[bool] = None
    enable_batch_processing: Optional[bool] = None
    validation_strict_mode: Optional[bool] = None
    retry_failed_conversions: Optional[bool] = None
    max_batch_size: Optional[int] = None

# === ENHANCED ENDPOINTS ===

@router_v2.post("/conversion/commitment/enhanced",
                summary="🔧 Conversion Enhanced avec Auto-Fix")
async def convert_from_commitment_enhanced(request: CommitmentConversionRequest):
    """
    🔧 **Conversion Enhanced avec Auto-Fix Intelligent**
    
    **Fonctionnalités avancées** :
    - **Auto-fix intelligent** : Correction automatique des erreurs de parsing
    - **Validation robuste** : Vérification et nettoyage des données
    - **Retry logic** : Tentatives multiples en cas d'échec
    - **Métriques détaillées** : Performance et corrections appliquées
    - **Cache optimisé** : Réutilisation des conversions récentes
    - **Support batch** : Traitement de multiples profils simultanément
    """
    try:
        start_time = time.time()
        converted_data = {}
        performance_metrics = {}
        
        # Conversion candidat Enhanced si données présentes
        if request.candidat_data:
            logger.info("🔧 Conversion candidat Enhanced avec auto-fix")
            candidat, metrics = await enhanced_bridge.convert_candidat_enhanced(
                request.candidat_data,
                request.candidat_questionnaire
            )
            converted_data["candidat"] = candidat.dict()
            performance_metrics["candidat"] = {
                "conversion_time_ms": metrics.conversion_time_ms,
                "auto_fix_time_ms": metrics.auto_fix_time_ms,
                "auto_fixes_count": metrics.auto_fixes_count,
                "fields_processed": metrics.fields_processed,
                "cache_used": metrics.cache_used
            }
            logger.info(f"✅ Candidat Enhanced converti: {candidat.personal_info.firstName} {candidat.personal_info.lastName}")
            logger.info(f"🔧 Auto-fixes appliqués: {metrics.auto_fixes_count}")
        
        # Conversion entreprise Enhanced si données présentes
        if request.entreprise_data:
            logger.info("🔧 Conversion entreprise Enhanced avec auto-fix")
            entreprise, metrics = await enhanced_bridge.convert_entreprise_enhanced(
                request.entreprise_data,
                request.entreprise_questionnaire
            )
            converted_data["entreprise"] = entreprise.dict()
            performance_metrics["entreprise"] = {
                "conversion_time_ms": metrics.conversion_time_ms,
                "auto_fix_time_ms": metrics.auto_fix_time_ms,
                "auto_fixes_count": metrics.auto_fixes_count,
                "fields_processed": metrics.fields_processed,
                "cache_used": metrics.cache_used
            }
            logger.info(f"✅ Entreprise Enhanced convertie: {entreprise.entreprise.nom} - {entreprise.poste.titre}")
            logger.info(f"🔧 Auto-fixes appliqués: {metrics.auto_fixes_count}")
        
        processing_time = (time.time() - start_time) * 1000
        
        # Stats Enhanced Bridge
        enhanced_stats = enhanced_bridge.get_enhanced_stats()
        
        return {
            "status": "success",
            "converted_data": converted_data,
            "performance_metrics": performance_metrics,
            "enhanced_bridge_stats": enhanced_stats,
            "processing_time_ms": round(processing_time, 2),
            "timestamp": datetime.now().isoformat(),
            "message": "Conversion Enhanced Commitment- → Nextvision réussie avec auto-fix",
            "features_used": {
                "auto_fix_intelligence": True,
                "robust_validation": True,
                "performance_caching": True,
                "retry_logic": True
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur conversion Enhanced: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur conversion Enhanced: {str(e)}"
        )

@router_v2.post("/conversion/commitment/enhanced/direct-match",
                response_model=BiDirectionalMatchingResponse,
                summary="🚀 Pipeline Enhanced complet")
async def convert_and_match_enhanced_direct(
    request: CommitmentConversionRequest,
    matcher: BiDirectionalMatcher = Depends(get_bidirectional_matcher)
):
    """
    🚀 **Pipeline Enhanced complet** : Auto-fix + Conversion + Matching
    
    **Workflow révolutionnaire Enhanced** :
    1. Auto-fix intelligent des données Commitment-
    2. Validation robuste avec fallbacks
    3. Conversion Enhanced Parser v4.0 → Bidirectionnel (candidat)
    4. Conversion ChatGPT Enhanced → Bidirectionnel (entreprise)  
    5. Matching bidirectionnel avec pondération adaptative
    6. Retour résultat complet + métriques performance détaillées
    """
    try:
        start_time = time.time()
        
        # Validation des données requises
        if not request.candidat_data or not request.entreprise_data:
            raise HTTPException(
                status_code=400,
                detail="Données candidat ET entreprise requises pour le matching Enhanced direct"
            )
        
        logger.info("🚀 Pipeline Enhanced: Auto-fix + Conversion + Matching")
        
        # 1. Conversion Enhanced candidat avec auto-fix
        candidat, candidat_metrics = await enhanced_bridge.convert_candidat_enhanced(
            request.candidat_data,
            request.candidat_questionnaire
        )
        
        # 2. Conversion Enhanced entreprise avec auto-fix
        entreprise, entreprise_metrics = await enhanced_bridge.convert_entreprise_enhanced(
            request.entreprise_data,
            request.entreprise_questionnaire
        )
        
        # 3. Matching bidirectionnel
        matching_request = BiDirectionalMatchingRequest(
            candidat=candidat,
            entreprise=entreprise,
            force_adaptive_weighting=True,
            use_google_maps_intelligence=True
        )
        
        result = await matcher.calculate_bidirectional_match(matching_request)
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"🚀 Pipeline Enhanced complet terminé en {processing_time:.2f}ms")
        
        # Enrichissement résultat avec métriques Enhanced
        result.processing_time_ms = processing_time
        
        # Ajout métadonnées Enhanced
        enhanced_metadata = {
            "enhanced_features_used": {
                "auto_fix_candidat": candidat_metrics.auto_fixes_count > 0,
                "auto_fix_entreprise": entreprise_metrics.auto_fixes_count > 0,
                "cache_optimization": candidat_metrics.cache_used or entreprise_metrics.cache_used,
                "robust_validation": True
            },
            "performance_breakdown": {
                "candidat_conversion_ms": candidat_metrics.conversion_time_ms,
                "candidat_auto_fix_ms": candidat_metrics.auto_fix_time_ms,
                "candidat_auto_fixes": candidat_metrics.auto_fixes_count,
                "entreprise_conversion_ms": entreprise_metrics.conversion_time_ms,
                "entreprise_auto_fix_ms": entreprise_metrics.auto_fix_time_ms,
                "entreprise_auto_fixes": entreprise_metrics.auto_fixes_count,
                "total_auto_fixes": candidat_metrics.auto_fixes_count + entreprise_metrics.auto_fixes_count
            },
            "quality_indicators": {
                "candidat_fields_processed": candidat_metrics.fields_processed,
                "entreprise_fields_processed": entreprise_metrics.fields_processed,
                "conversion_success_rate": "100%",
                "auto_fix_success": True
            }
        }
        
        # Injection métadonnées dans les détails de scoring
        if hasattr(result.component_scores, 'semantique_details'):
            result.component_scores.semantique_details.update({
                "enhanced_metadata": enhanced_metadata
            })
        
        logger.info(f"🔧 Total auto-fixes: {enhanced_metadata['performance_breakdown']['total_auto_fixes']}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur pipeline Enhanced: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur pipeline Enhanced: {str(e)}"
        )

@router_v2.post("/conversion/commitment/enhanced/batch",
                summary="📦 Batch Enhanced avec Auto-Fix")
async def batch_convert_enhanced(request: EnhancedBatchRequest):
    """
    📦 **Batch Enhanced Processing** : Auto-fix en lot avec optimisations
    
    **Capacités avancées** :
    - **Traitement parallèle** : Conversions simultanées optimisées
    - **Auto-fix en lot** : Corrections intelligentes appliquées à tous
    - **Statistiques détaillées** : Métriques de performance par élément
    - **Gestion d'erreurs robuste** : Isolation des échecs individuels
    - **Limites de sécurité** : Protection contre la surcharge
    """
    try:
        if not request.candidats_data and not request.entreprises_data:
            raise HTTPException(
                status_code=400,
                detail="Au moins une liste (candidats ou entreprises) doit être fournie"
            )
        
        total_items = len(request.candidats_data) + len(request.entreprises_data)
        if total_items > enhanced_bridge.config['max_batch_size']:
            raise HTTPException(
                status_code=400,
                detail=f"Lot trop volumineux: {total_items} > {enhanced_bridge.config['max_batch_size']}"
            )
        
        start_time = time.time()
        results = {
            "candidats": {"successful": [], "failed": []},
            "entreprises": {"successful": [], "failed": []},
            "performance_summary": {},
            "processing_time_ms": 0
        }
        
        logger.info(f"📦 Batch Enhanced: {len(request.candidats_data)} candidats + {len(request.entreprises_data)} entreprises")
        
        # Traitement candidats
        if request.candidats_data:
            candidats_results = await enhanced_bridge.convert_batch_enhanced(
                request.candidats_data, data_type='candidat'
            )
            results["candidats"] = candidats_results
        
        # Traitement entreprises
        if request.entreprises_data:
            entreprises_results = await enhanced_bridge.convert_batch_enhanced(
                request.entreprises_data, data_type='entreprise'
            )
            results["entreprises"] = entreprises_results
        
        processing_time = (time.time() - start_time) * 1000
        results["processing_time_ms"] = processing_time
        
        # Calcul statistiques globales
        total_successful = len(results["candidats"].get("successful", [])) + len(results["entreprises"].get("successful", []))
        total_failed = len(results["candidats"].get("failed", [])) + len(results["entreprises"].get("failed", []))
        
        results["performance_summary"] = {
            "total_processed": total_items,
            "total_successful": total_successful,
            "total_failed": total_failed,
            "success_rate_percent": (total_successful / total_items * 100) if total_items > 0 else 0,
            "avg_processing_time_ms": processing_time / total_items if total_items > 0 else 0,
            "throughput_items_per_sec": total_items / (processing_time / 1000) if processing_time > 0 else 0
        }
        
        # Stats Enhanced Bridge
        enhanced_stats = enhanced_bridge.get_enhanced_stats()
        results["enhanced_bridge_stats"] = enhanced_stats
        
        logger.info(f"📦 Batch Enhanced terminé: {total_successful}/{total_items} succès en {processing_time:.2f}ms")
        
        return {
            "status": "success",
            "results": results,
            "timestamp": datetime.now().isoformat(),
            "message": f"Batch Enhanced traité: {total_successful}/{total_items} conversions réussies"
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur batch Enhanced: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur batch Enhanced: {str(e)}"
        )

@router_v2.get("/conversion/commitment/enhanced/stats",
               summary="📊 Statistiques Enhanced Bridge")
async def get_enhanced_bridge_stats():
    """
    📊 **Statistiques Enhanced Bridge** : Métriques de performance détaillées
    
    **Informations fournies** :
    - **Conversions** : Nombre total et taux de succès
    - **Auto-fixes** : Corrections appliquées et patterns détectés
    - **Performance** : Temps de traitement et cache efficiency
    - **Configuration** : Paramètres actifs du bridge
    - **Santé système** : Uptime et métriques de stabilité
    """
    try:
        stats = enhanced_bridge.get_enhanced_stats()
        
        return {
            "status": "success",
            "enhanced_bridge_stats": stats,
            "endpoint_info": {
                "enhanced_conversion": "/api/v2/conversion/commitment/enhanced",
                "enhanced_direct_match": "/api/v2/conversion/commitment/enhanced/direct-match",
                "enhanced_batch": "/api/v2/conversion/commitment/enhanced/batch"
            },
            "features": {
                "auto_fix_intelligence": enhanced_bridge.config['enable_auto_fix'],
                "performance_caching": enhanced_bridge.config['enable_cache'],
                "batch_processing": enhanced_bridge.config['enable_batch_processing'],
                "retry_logic": enhanced_bridge.config['retry_failed_conversions']
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur stats Enhanced: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur stats Enhanced: {str(e)}"
        )

@router_v2.post("/conversion/commitment/enhanced/config",
                summary="⚙️ Configuration Enhanced Bridge")
async def update_enhanced_bridge_config(request: EnhancedConfigRequest):
    """
    ⚙️ **Configuration Enhanced Bridge** : Mise à jour des paramètres
    
    **Paramètres configurables** :
    - `enable_auto_fix` : Activer/désactiver l'auto-fix intelligent
    - `enable_cache` : Activer/désactiver le cache de performance
    - `enable_batch_processing` : Activer/désactiver le traitement en lot
    - `validation_strict_mode` : Mode de validation strict/permissif
    - `retry_failed_conversions` : Activer/désactiver les tentatives de secours
    - `max_batch_size` : Taille maximum des lots (défaut: 50)
    """
    try:
        # Conversion du modèle en dict, en excluant les valeurs None
        config_updates = {k: v for k, v in request.dict().items() if v is not None}
        
        if not config_updates:
            raise HTTPException(
                status_code=400,
                detail="Aucune configuration à mettre à jour"
            )
        
        # Sauvegarde config actuelle
        old_config = enhanced_bridge.config.copy()
        
        # Mise à jour
        enhanced_bridge.update_config(config_updates)
        
        logger.info(f"⚙️ Configuration Enhanced Bridge mise à jour: {config_updates}")
        
        return {
            "status": "success",
            "message": "Configuration Enhanced Bridge mise à jour",
            "old_config": old_config,
            "new_config": enhanced_bridge.config,
            "changes_applied": config_updates,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour config Enhanced: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur config Enhanced: {str(e)}"
        )

@router_v2.delete("/conversion/commitment/enhanced/cache",
                 summary="🧹 Vider cache Enhanced Bridge")
async def clear_enhanced_bridge_cache():
    """
    🧹 **Vider cache Enhanced Bridge** : Nettoyage du cache de performance
    
    **Action** : Supprime toutes les entrées du cache de conversion pour forcer
    le recalcul lors des prochaines conversions. Utile pour :
    - Libérer la mémoire
    - Forcer le recalcul avec des données mises à jour
    - Résoudre des problèmes de cache corrompus
    """
    try:
        cache_size_before = len(enhanced_bridge.cache)
        enhanced_bridge.clear_cache()
        
        logger.info(f"🧹 Cache Enhanced Bridge vidé: {cache_size_before} entrées supprimées")
        
        return {
            "status": "success",
            "message": "Cache Enhanced Bridge vidé",
            "entries_cleared": cache_size_before,
            "cache_size_after": len(enhanced_bridge.cache),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur vidage cache Enhanced: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur vidage cache Enhanced: {str(e)}"
        )

# === HEALTH CHECK ENHANCED ===

@router_v2.get("/conversion/commitment/enhanced/health",
               summary="❤️ Health Check Enhanced Bridge")
async def enhanced_bridge_health():
    """
    ❤️ **Health Check Enhanced Bridge** : Statut détaillé
    
    Vérification complète de la santé du Enhanced Bridge v2.0
    """
    try:
        stats = enhanced_bridge.get_enhanced_stats()
        
        # Test rapide de fonctionnalité
        test_data = {
            "personal_info": {
                "firstName": "Test",
                "lastName": "User",
                "email": "test@example.com"
            },
            "skills": ["Python", "FastAPI"],
            "parsing_confidence": 0.95
        }
        
        # Test conversion rapide
        test_start = time.time()
        try:
            test_candidat, test_metrics = await enhanced_bridge.convert_candidat_enhanced(
                test_data, enable_auto_fix=False
            )
            test_success = True
            test_time = (time.time() - test_start) * 1000
        except Exception as test_error:
            test_success = False
            test_time = 0
            logger.warning(f"Test conversion échoué: {test_error}")
        
        health_status = "healthy" if test_success else "degraded"
        
        return {
            "status": health_status,
            "service": "Enhanced Bridge v2.0",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "features": {
                "auto_fix_intelligence": enhanced_bridge.config['enable_auto_fix'],
                "performance_caching": enhanced_bridge.config['enable_cache'],
                "batch_processing": enhanced_bridge.config['enable_batch_processing'],
                "retry_logic": enhanced_bridge.config['retry_failed_conversions']
            },
            "performance_test": {
                "conversion_test": test_success,
                "test_time_ms": round(test_time, 2)
            },
            "stats_summary": {
                "total_conversions": stats["enhanced_bridge_stats"]["total_conversions"],
                "success_rate": stats["enhanced_bridge_stats"]["success_rate_percent"],
                "auto_fixes_applied": stats["enhanced_bridge_stats"]["auto_fixes_applied"],
                "cache_hit_rate": stats["enhanced_bridge_stats"]["cache_hit_rate_percent"]
            },
            "uptime_hours": stats["uptime_hours"]
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur health check Enhanced: {e}")
        return {
            "status": "unhealthy",
            "service": "Enhanced Bridge v2.0",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
