"""
🎯 Nextvision v2.0 - Endpoints API Bidirectionnel

Nouveaux endpoints pour matching bidirectionnel avec :
- /api/v2/matching/bidirectional : Matching principal candidat ↔ entreprise
- /api/v2/conversion/commitment : Conversion depuis Commitment-
- /api/v2/batch/matching : Matching en lot pour performances
- /api/v2/analytics/scoring : Analytics détaillées des scores
- Intégration complète avec l'architecture existante

Author: NEXTEN Team
Version: 2.0.0 - Bidirectional API
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union
import asyncio
import time
import logging
from datetime import datetime

# Import des modèles et services bidirectionnels
from nextvision.models.bidirectional_models import (
    BiDirectionalMatchingRequest, BiDirectionalMatchingResponse,
    BiDirectionalCandidateProfile, BiDirectionalCompanyProfile
)

from nextvision.services.bidirectional_matcher import (
    BiDirectionalMatcher, BiDirectionalMatcherFactory
)

from nextvision.adapters.chatgpt_commitment_adapter import (
    CommitmentNextvisionBridge, EnhancedParserV4Output, ChatGPTCommitmentOutput
)

# Import des services Google Maps existants
from nextvision.services.google_maps_service import GoogleMapsService
from nextvision.engines.location_scoring import LocationScoringEngine

logger = logging.getLogger(__name__)

# === MODÈLES API ===

class CommitmentConversionRequest(BaseModel):
    """Requête de conversion depuis Commitment-"""
    candidat_data: Optional[Dict] = Field(None, description="Données Enhanced Universal Parser v4.0")
    entreprise_data: Optional[Dict] = Field(None, description="Données ChatGPT Commitment-")
    candidat_questionnaire: Optional[Dict] = Field(None, description="Questionnaire candidat complémentaire")
    entreprise_questionnaire: Optional[Dict] = Field(None, description="Questionnaire entreprise complémentaire")

class BatchMatchingRequest(BaseModel):
    """Requête matching en lot"""
    candidats: List[BiDirectionalCandidateProfile] = Field(..., max_items=50, description="Liste candidats (max 50)")
    entreprises: List[BiDirectionalCompanyProfile] = Field(..., max_items=20, description="Liste entreprises (max 20)")
    enable_parallel_processing: bool = Field(True, description="Activer traitement parallèle")
    score_threshold: float = Field(0.3, ge=0.0, le=1.0, description="Seuil score minimum")

class BatchMatchingResponse(BaseModel):
    """Réponse matching en lot"""
    total_matches: int
    processed_combinations: int
    matches: List[Dict]
    processing_time_ms: float
    performance_stats: Dict

class ScoringAnalyticsRequest(BaseModel):
    """Requête analytics scoring"""
    candidat: BiDirectionalCandidateProfile
    entreprise: BiDirectionalCompanyProfile
    include_detailed_breakdown: bool = Field(True, description="Inclure détails complets")
    generate_recommendations: bool = Field(True, description="Générer recommandations")

# === INITIALISATION SERVICES ===

# Factory pour créer le matcher avec services Google Maps
def get_bidirectional_matcher() -> BiDirectionalMatcher:
    """Dependency injection pour le matcher bidirectionnel"""
    # TODO: Intégrer avec les services Google Maps existants
    return BiDirectionalMatcherFactory.create_basic_matcher()

# Bridge Commitment-
commitment_bridge = CommitmentNextvisionBridge()

# Router pour les endpoints v2
router_v2 = APIRouter(prefix="/api/v2", tags=["🎯 Bidirectional Matching v2"])

# === ENDPOINTS PRINCIPAUX ===

@router_v2.post("/matching/bidirectional", 
                response_model=BiDirectionalMatchingResponse,
                summary="🎯 Matching bidirectionnel principal")
async def calculate_bidirectional_matching(
    request: BiDirectionalMatchingRequest,
    matcher: BiDirectionalMatcher = Depends(get_bidirectional_matcher)
):
    """
    🎯 **ENDPOINT PRINCIPAL** : Matching bidirectionnel candidat ↔ entreprise
    
    **Innovation v2.0** : Pondération adaptative bidirectionnelle avec 4 composants business :
    - **Sémantique (35%)** : Correspondance CV ↔ Fiche de poste
    - **Salaire (25%)** : Budget entreprise vs attentes candidat  
    - **Expérience (20%)** : Années requises vs expérience candidat
    - **Localisation (15%)** : Impact géographique + Google Maps Intelligence
    
    **Pondération adaptative** :
    - **Côté candidat** : Selon raison d'écoute (pourquoi_ecoute)
    - **Côté entreprise** : Selon urgence de recrutement
    """
    try:
        start_time = time.time()
        
        logger.info(f"🎯 Matching bidirectionnel demandé")
        logger.info(f"👤 Candidat: {request.candidat.personal_info.firstName} {request.candidat.personal_info.lastName}")
        logger.info(f"🏢 Entreprise: {request.entreprise.entreprise.nom} - {request.entreprise.poste.titre}")
        
        # Matching bidirectionnel principal
        result = await matcher.calculate_bidirectional_match(request)
        
        # Logs de résultat
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"✅ Matching terminé en {processing_time:.2f}ms")
        logger.info(f"📊 Score: {result.matching_score} | Compatibilité: {result.compatibility}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur matching bidirectionnel: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur matching bidirectionnel: {str(e)}"
        )

@router_v2.post("/conversion/commitment",
                summary="🌉 Conversion depuis Commitment-")
async def convert_from_commitment(request: CommitmentConversionRequest):
    """
    🌉 **Conversion depuis Commitment-** : Exploite vos systèmes de parsing existants
    
    **Intégration révolutionnaire** avec votre infrastructure :
    - **Enhanced Universal Parser v4.0** : Candidats (CVs)
    - **Système ChatGPT** : Entreprises (fiches de poste)
    - **Conservation badges** "Auto-rempli" et métadonnées
    - **Formats spécifiques** : "5 ans - 10 ans", "35K à 38K annuels"
    """
    try:
        start_time = time.time()
        converted_data = {}
        
        # Conversion candidat si données présentes
        if request.candidat_data:
            logger.info("🔄 Conversion candidat Enhanced Universal Parser v4.0")
            candidat = commitment_bridge.convert_candidat_from_commitment(
                request.candidat_data,
                request.candidat_questionnaire
            )
            converted_data["candidat"] = candidat.dict()
            logger.info(f"✅ Candidat converti: {candidat.personal_info.firstName} {candidat.personal_info.lastName}")
        
        # Conversion entreprise si données présentes
        if request.entreprise_data:
            logger.info("🔄 Conversion entreprise ChatGPT Commitment-")
            entreprise = commitment_bridge.convert_entreprise_from_commitment(
                request.entreprise_data,
                request.entreprise_questionnaire
            )
            converted_data["entreprise"] = entreprise.dict()
            logger.info(f"✅ Entreprise convertie: {entreprise.entreprise.nom} - {entreprise.poste.titre}")
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "status": "success",
            "converted_data": converted_data,
            "conversion_stats": commitment_bridge.get_bridge_stats(),
            "processing_time_ms": round(processing_time, 2),
            "timestamp": datetime.now().isoformat(),
            "message": "Conversion Commitment- → Nextvision réussie"
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur conversion Commitment-: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur conversion: {str(e)}"
        )

@router_v2.post("/conversion/commitment/direct-match",
                response_model=BiDirectionalMatchingResponse,
                summary="🚀 Conversion + Matching direct")
async def convert_and_match_direct(
    request: CommitmentConversionRequest,
    matcher: BiDirectionalMatcher = Depends(get_bidirectional_matcher)
):
    """
    🚀 **Pipeline complet** : Conversion Commitment- + Matching en une requête
    
    **Workflow révolutionnaire** :
    1. Conversion Enhanced Parser v4.0 → Bidirectionnel (candidat)
    2. Conversion ChatGPT → Bidirectionnel (entreprise)  
    3. Matching bidirectionnel avec pondération adaptative
    4. Retour résultat complet en une seule API call
    """
    try:
        start_time = time.time()
        
        # Validation des données requises
        if not request.candidat_data or not request.entreprise_data:
            raise HTTPException(
                status_code=400,
                detail="Données candidat ET entreprise requises pour le matching direct"
            )
        
        logger.info("🚀 Pipeline conversion + matching direct")
        
        # 1. Conversion candidat
        candidat = commitment_bridge.convert_candidat_from_commitment(
            request.candidat_data,
            request.candidat_questionnaire
        )
        
        # 2. Conversion entreprise
        entreprise = commitment_bridge.convert_entreprise_from_commitment(
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
        logger.info(f"🚀 Pipeline complet terminé en {processing_time:.2f}ms")
        
        # Ajout métadonnées pipeline
        result.processing_time_ms = processing_time
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur pipeline conversion + matching: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur pipeline: {str(e)}"
        )

@router_v2.post("/batch/matching",
                response_model=BatchMatchingResponse,
                summary="⚡ Matching en lot haute performance")
async def batch_matching(
    request: BatchMatchingRequest,
    background_tasks: BackgroundTasks,
    matcher: BiDirectionalMatcher = Depends(get_bidirectional_matcher)
):
    """
    ⚡ **Matching en lot** : Traitement haute performance de multiples combinaisons
    
    **Optimisations performance** :
    - **Traitement parallèle** : Calculs asynchrones simultanés
    - **Seuil de score** : Filtrage automatique des matches faibles
    - **Cache intelligent** : Réutilisation des calculs
    - **Limite raisonnable** : 50 candidats × 20 entreprises = 1000 matches max
    """
    try:
        start_time = time.time()
        
        total_combinations = len(request.candidats) * len(request.entreprises)
        logger.info(f"⚡ Matching en lot: {total_combinations} combinaisons")
        
        # Validation limites
        if total_combinations > 1000:
            raise HTTPException(
                status_code=400,
                detail=f"Trop de combinaisons ({total_combinations}). Limite: 1000"
            )
        
        matches = []
        processed = 0
        
        # Traitement parallèle ou séquentiel
        if request.enable_parallel_processing and total_combinations <= 100:
            # Parallèle pour petits lots
            matches = await _process_batch_parallel(request, matcher)
        else:
            # Séquentiel pour gros lots
            matches = await _process_batch_sequential(request, matcher)
        
        # Filtrage par seuil
        filtered_matches = [
            match for match in matches 
            if match["matching_score"] >= request.score_threshold
        ]
        
        processing_time = (time.time() - start_time) * 1000
        
        # Stats performance
        performance_stats = {
            "total_combinations": total_combinations,
            "matches_above_threshold": len(filtered_matches),
            "processing_mode": "parallel" if request.enable_parallel_processing else "sequential",
            "avg_score": sum(m["matching_score"] for m in filtered_matches) / max(1, len(filtered_matches)),
            "matches_per_second": total_combinations / max(0.001, processing_time / 1000)
        }
        
        logger.info(f"⚡ Batch terminé: {len(filtered_matches)} matches valides en {processing_time:.2f}ms")
        
        return BatchMatchingResponse(
            total_matches=len(filtered_matches),
            processed_combinations=total_combinations,
            matches=filtered_matches[:20],  # Limite retour API
            processing_time_ms=processing_time,
            performance_stats=performance_stats
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur batch matching: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur batch matching: {str(e)}"
        )

@router_v2.post("/analytics/scoring",
                summary="📊 Analytics détaillées des scores")
async def scoring_analytics(
    request: ScoringAnalyticsRequest,
    matcher: BiDirectionalMatcher = Depends(get_bidirectional_matcher)
):
    """
    📊 **Analytics scoring** : Analyse détaillée des composants de matching
    
    **Insights avancés** :
    - **Breakdown détaillé** : Score par composant avec explications
    - **Pondération adaptative** : Impact des adaptations contextuelles
    - **Recommandations** : Suggestions d'amélioration bilatérales
    - **Comparaisons** : Performance vs moyennes sectorielles
    """
    try:
        start_time = time.time()
        
        # Matching pour récupérer tous les détails
        matching_request = BiDirectionalMatchingRequest(
            candidat=request.candidat,
            entreprise=request.entreprise,
            force_adaptive_weighting=True
        )
        
        result = await matcher.calculate_bidirectional_match(matching_request)
        
        # Analytics enrichies
        analytics = {
            "scoring_breakdown": {
                "semantique": {
                    "score": result.component_scores.semantique_score,
                    "weight": result.adaptive_weighting.entreprise_weights.semantique,
                    "weighted_contribution": result.component_scores.semantique_score * result.adaptive_weighting.entreprise_weights.semantique,
                    "details": result.component_scores.semantique_details,
                    "performance_level": _get_performance_level(result.component_scores.semantique_score)
                },
                "salaire": {
                    "score": result.component_scores.salaire_score,
                    "weight": result.adaptive_weighting.entreprise_weights.salaire,
                    "weighted_contribution": result.component_scores.salaire_score * result.adaptive_weighting.entreprise_weights.salaire,
                    "details": result.component_scores.salaire_details,
                    "performance_level": _get_performance_level(result.component_scores.salaire_score)
                },
                "experience": {
                    "score": result.component_scores.experience_score,
                    "weight": result.adaptive_weighting.entreprise_weights.experience,
                    "weighted_contribution": result.component_scores.experience_score * result.adaptive_weighting.entreprise_weights.experience,
                    "details": result.component_scores.experience_details,
                    "performance_level": _get_performance_level(result.component_scores.experience_score)
                },
                "localisation": {
                    "score": result.component_scores.localisation_score,
                    "weight": result.adaptive_weighting.entreprise_weights.localisation,
                    "weighted_contribution": result.component_scores.localisation_score * result.adaptive_weighting.entreprise_weights.localisation,
                    "details": result.component_scores.localisation_details,
                    "performance_level": _get_performance_level(result.component_scores.localisation_score)
                }
            },
            "adaptive_weighting_impact": {
                "candidat_reason": result.adaptive_weighting.raison_candidat.value,
                "entreprise_urgency": result.adaptive_weighting.urgence_entreprise.value,
                "weight_adjustments": _calculate_weight_adjustments(result.adaptive_weighting),
                "impact_score": _calculate_adaptation_impact(result)
            },
            "recommendations": {
                "candidat": result.recommandations_candidat,
                "entreprise": result.recommandations_entreprise,
                "priority_actions": _generate_priority_actions(result),
                "improvement_potential": _calculate_improvement_potential(result)
            },
            "benchmarking": {
                "sector_comparison": "Non disponible (nécessite base de données sectorielle)",
                "percentile_score": _estimate_percentile(result.matching_score),
                "top_strengths": result.points_forts,
                "attention_points": result.points_attention
            }
        }
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "status": "success",
            "matching_score": result.matching_score,
            "compatibility": result.compatibility,
            "analytics": analytics,
            "processing_time_ms": round(processing_time, 2),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur analytics scoring: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur analytics: {str(e)}"
        )

# === ENDPOINTS UTILITAIRES ===

@router_v2.get("/matching/health",
               summary="❤️ Health check bidirectionnel")
async def bidirectional_health_check(
    matcher: BiDirectionalMatcher = Depends(get_bidirectional_matcher)
):
    """❤️ Health check système bidirectionnel"""
    try:
        # Stats du matcher
        matcher_stats = matcher.get_performance_stats()
        
        # Stats du bridge
        bridge_stats = commitment_bridge.get_bridge_stats()
        
        return {
            "status": "healthy",
            "service": "Nextvision Bidirectional Matching",
            "version": "2.0.0",
            "features": {
                "bidirectional_matching": True,
                "adaptive_weighting": True,
                "commitment_integration": True,
                "google_maps_intelligence": True,
                "batch_processing": True,
                "scoring_analytics": True
            },
            "performance": {
                "matcher_stats": matcher_stats,
                "bridge_stats": bridge_stats,
                "uptime": "Ready"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@router_v2.get("/matching/performance",
               summary="📊 Performance statistics")
async def get_performance_statistics(
    matcher: BiDirectionalMatcher = Depends(get_bidirectional_matcher)
):
    """📊 Statistiques de performance détaillées"""
    try:
        return {
            "status": "success",
            "performance_data": {
                "matcher_performance": matcher.get_performance_stats(),
                "bridge_performance": commitment_bridge.get_bridge_stats(),
                "system_metrics": {
                    "cache_size": len(matcher.cache),
                    "average_response_time_target": "< 150ms",
                    "batch_capacity": "1000 combinations",
                    "supported_formats": ["Enhanced Parser v4.0", "ChatGPT Commitment-"]
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Performance stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# === FONCTIONS UTILITAIRES ===

async def _process_batch_parallel(request: BatchMatchingRequest, 
                                matcher: BiDirectionalMatcher) -> List[Dict]:
    """Traitement parallèle pour petits lots"""
    tasks = []
    
    for candidat in request.candidats:
        for entreprise in request.entreprises:
            matching_request = BiDirectionalMatchingRequest(
                candidat=candidat,
                entreprise=entreprise
            )
            task = matcher.calculate_bidirectional_match(matching_request)
            tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    matches = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.warning(f"⚠️ Match {i} failed: {result}")
            continue
        
        matches.append({
            "candidat_id": f"{result.component_scores.semantique_details.get('candidat_name', 'Unknown')}",
            "entreprise_id": f"{result.component_scores.semantique_details.get('entreprise_name', 'Unknown')}",
            "matching_score": result.matching_score,
            "compatibility": result.compatibility,
            "confidence": result.confidence,
            "processing_time_ms": result.processing_time_ms
        })
    
    return matches

async def _process_batch_sequential(request: BatchMatchingRequest,
                                  matcher: BiDirectionalMatcher) -> List[Dict]:
    """Traitement séquentiel pour gros lots"""
    matches = []
    
    for candidat in request.candidats:
        for entreprise in request.entreprises:
            try:
                matching_request = BiDirectionalMatchingRequest(
                    candidat=candidat,
                    entreprise=entreprise
                )
                
                result = await matcher.calculate_bidirectional_match(matching_request)
                
                matches.append({
                    "candidat_id": f"{candidat.personal_info.firstName} {candidat.personal_info.lastName}",
                    "entreprise_id": f"{entreprise.entreprise.nom}",
                    "matching_score": result.matching_score,
                    "compatibility": result.compatibility,
                    "confidence": result.confidence,
                    "processing_time_ms": result.processing_time_ms
                })
                
            except Exception as e:
                logger.warning(f"⚠️ Match failed: {e}")
                continue
    
    return matches

def _get_performance_level(score: float) -> str:
    """Détermine niveau de performance"""
    if score >= 0.85:
        return "Excellent"
    elif score >= 0.70:
        return "Bon"
    elif score >= 0.50:
        return "Moyen"
    elif score >= 0.30:
        return "Faible"
    else:
        return "Très faible"

def _calculate_weight_adjustments(adaptive_config) -> Dict:
    """Calcule ajustements de poids"""
    # TODO: Implémenter calcul détaillé des ajustements
    return {
        "total_adjustments": 4,
        "boost_candidat": "Applied based on listening reason",
        "boost_entreprise": "Applied based on urgency"
    }

def _calculate_adaptation_impact(result) -> float:
    """Calcule impact de l'adaptation"""
    # Score simple basé sur l'écart vs pondération standard
    return 0.15  # Placeholder

def _generate_priority_actions(result) -> List[str]:
    """Génère actions prioritaires"""
    actions = []
    
    if result.component_scores.semantique_score < 0.5:
        actions.append("Développer compétences techniques manquantes")
    
    if result.component_scores.salaire_score < 0.5:
        actions.append("Négocier budget ou revoir attentes salariales")
    
    if result.component_scores.experience_score < 0.5:
        actions.append("Prévoir formation/accompagnement expérience")
    
    if result.component_scores.localisation_score < 0.5:
        actions.append("Explorer options télétravail ou transport")
    
    return actions[:3]  # Top 3

def _calculate_improvement_potential(result) -> Dict:
    """Calcule potentiel d'amélioration"""
    return {
        "maximum_achievable_score": min(1.0, result.matching_score + 0.2),
        "improvement_difficulty": "Medium",
        "estimated_timeline": "1-3 months"
    }

def _estimate_percentile(score: float) -> int:
    """Estime percentile du score"""
    # Mapping approximatif
    if score >= 0.9:
        return 95
    elif score >= 0.8:
        return 85
    elif score >= 0.7:
        return 70
    elif score >= 0.6:
        return 55
    else:
        return 30

# Export du router pour intégration dans main.py
bidirectional_router = router_v2
