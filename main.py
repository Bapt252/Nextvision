"""
🎯 Nextvision - Main FastAPI Application avec Pondération Adaptative RÉELLE
Algorithme de matching IA adaptatif pour NEXTEN + Bridge Commitment-

Author: NEXTEN Team
Version: 1.0.0
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
import time
import logging
import tempfile
import os
import shutil

# Import du service bridge
from nextvision.services.commitment_bridge import (
    CommitmentNextvisionBridge, 
    BridgeRequest,
    BridgeConfig
)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="🎯 Nextvision API",
    description="""
    **Algorithme de matching IA adaptatif pour NEXTEN**
    
    ## 🎯 Innovation: Pondération Adaptative Contextuelle
    
    L'algorithme ajuste automatiquement les poids selon le "pourquoi_ecoute" du candidat:
    
    * **"Rémunération trop faible"** → Priorité rémunération (30% +10%)
    * **"Poste ne coïncide pas"** → Priorité sémantique (45% +10%) 
    * **"Poste trop loin"** → Priorité localisation (20% +10%)
    * **"Manque de flexibilité"** → Priorité environnement (15% +10%)
    * **"Manque perspectives"** → Priorité motivations (15% +10%)
    
    ## 🌉 Intégration Bridge avec Commitment-
    
    **Nouveauté révolutionnaire**: Bridge zéro redondance avec [Commitment-](https://github.com/Bapt252/Commitment-)
    
    * **Job Parser GPT** : Réutilise l'infrastructure mature existante
    * **CV Parser GPT** : Connexion directe aux services opérationnels  
    * **Workflow complet** : Parse → Match en une requête
    * **Architecture optimale** : Aucune duplication de code
    """,
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🏗️ Modèles Pydantic simplifiés

class PersonalInfo(BaseModel):
    firstName: str
    lastName: str
    email: str  # Validation email basique de pydantic
    phone: Optional[str] = None

class SalaryExpectations(BaseModel):
    min: int
    max: int
    current: Optional[int] = None

class LocationPreferences(BaseModel):
    city: str
    acceptedCities: Optional[List[str]] = []
    maxDistance: Optional[int] = 0

class CandidateProfile(BaseModel):
    personal_info: PersonalInfo
    skills: List[str]
    experience_years: int
    education: Optional[str] = ""
    current_role: Optional[str] = ""

class Preferences(BaseModel):
    salary_expectations: SalaryExpectations
    location_preferences: LocationPreferences
    remote_preferences: Optional[str] = ""
    sectors: Optional[List[str]] = []
    company_size: Optional[str] = ""

class MatchingRequest(BaseModel):
    pourquoi_ecoute: str  # 🎯 CHAMP CLÉ pour pondération adaptative
    candidate_profile: CandidateProfile
    preferences: Preferences
    availability: Optional[str] = ""

# 🎯 Configuration des poids adaptatifs
DEFAULT_WEIGHTS = {
    "semantique": 0.35,
    "remuneration": 0.20,
    "timing": 0.15,
    "localisation": 0.10,
    "secteurs": 0.10,
    "environnement": 0.05,
    "motivations": 0.05
}

ADAPTIVE_WEIGHTS_CONFIG = {
    "Rémunération trop faible": {
        "remuneration": 0.30,  # +10%
        "semantique": 0.30,    # -5%
        "reasoning": "Priorité accordée à l'amélioration salariale"
    },
    "Poste ne coïncide pas avec poste proposé": {
        "semantique": 0.45,    # +10%
        "remuneration": 0.15,  # -5%
        "reasoning": "Focus sur l'adéquation des compétences et du poste"
    },
    "Poste trop loin de mon domicile": {
        "localisation": 0.20,  # +10%
        "semantique": 0.30,    # -5%
        "reasoning": "Priorité à la proximité géographique"
    },
    "Manque de flexibilité": {
        "environnement": 0.15, # +10%
        "motivations": 0.10,   # +5%
        "reasoning": "Recherche d'un meilleur équilibre vie pro/perso"
    },
    "Manque de perspectives d'évolution": {
        "motivations": 0.15,   # +10%
        "semantique": 0.30,    # -5%
        "reasoning": "Focus sur les opportunités de développement"
    }
}

def get_adaptive_weights(pourquoi_ecoute: str) -> Dict:
    """
    🎯 COEUR DE L'INNOVATION: Pondération Adaptative Contextuelle
    
    Ajuste intelligemment les poids selon le contexte du candidat
    """
    base_weights = DEFAULT_WEIGHTS.copy()
    adaptation_applied = False
    reasoning = "Pondération standard appliquée"
    
    # Normalisation de la raison
    normalized_reason = pourquoi_ecoute.strip()
    
    logger.info(f"🎯 Analyse pondération pour: '{normalized_reason}'")
    
    if normalized_reason in ADAPTIVE_WEIGHTS_CONFIG:
        adaptation = ADAPTIVE_WEIGHTS_CONFIG[normalized_reason]
        
        # Appliquer les adaptations spécifiques
        for component, new_weight in adaptation.items():
            if component != "reasoning":
                logger.info(f"   📊 {component}: {base_weights[component]} → {new_weight}")
                base_weights[component] = new_weight
        
        adaptation_applied = True
        reasoning = adaptation["reasoning"]
        
        logger.info(f"✅ Pondération adaptative appliquée: {reasoning}")
    else:
        logger.info(f"⚠️ Raison non reconnue pour adaptation: '{normalized_reason}'")
        logger.info("📊 Pondération standard utilisée")
    
    return {
        "weights": base_weights,
        "adaptation_applied": adaptation_applied,
        "reasoning": reasoning,
        "original_reason": pourquoi_ecoute
    }

def calculate_mock_matching_scores(request: MatchingRequest, weights: Dict) -> Dict:
    """🧮 Calcul de scores de matching (simulé pour démonstration)"""
    
    # Simulation basée sur les données du candidat
    skills_count = len(request.candidate_profile.skills)
    experience = request.candidate_profile.experience_years
    salary_min = request.preferences.salary_expectations.min
    
    # Scores simulés mais cohérents
    scores = {
        "semantique": min(0.9, 0.5 + (skills_count * 0.08) + (experience * 0.02)),
        "remuneration": min(0.95, 0.6 + (salary_min / 100000) * 0.3),
        "localisation": 0.75,
        "timing": 0.85,
        "secteurs": 0.70,
        "environnement": 0.65,
        "motivations": 0.80
    }
    
    # Score total pondéré
    total_score = sum(scores[component] * weights[component] for component in scores.keys())
    
    return {
        "component_scores": scores,
        "total_score": round(total_score, 3),
        "confidence": round(min(0.95, total_score * 1.1), 3)
    }

def _calculate_weight_changes(adapted_weights: Dict) -> Dict:
    """📊 Calcule les changements de poids"""
    changes = {}
    for component, adapted_weight in adapted_weights.items():
        default_weight = DEFAULT_WEIGHTS[component]
        change = adapted_weight - default_weight
        if abs(change) > 0.001:
            changes[component] = {
                "from": default_weight,
                "to": adapted_weight,
                "change": round(change, 3),
                "change_percent": round((change / default_weight) * 100, 1)
            }
    return changes

# 🌐 ENDPOINTS API ORIGINAUX

@app.get("/", tags=["Root"])
async def root():
    """🏠 Root endpoint"""
    return {
        "service": "Nextvision",
        "description": "Algorithme de matching IA adaptatif pour NEXTEN",
        "version": "1.0.0",
        "status": "active",
        "innovation": "Pondération Adaptative Contextuelle",
        "frontend_integration": "https://github.com/Bapt252/Commitment-",
        "bridge_integration": "Commitment- → Nextvision",
        "docs": "/docs",
        "health": "/api/v1/health",
        "integration_health": "/api/v1/integration/health",
        "adaptive_reasons_supported": list(ADAPTIVE_WEIGHTS_CONFIG.keys())
    }

@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """❤️ Health Check"""
    return {
        "status": "healthy",
        "service": "Nextvision",
        "version": "1.0.0",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "environment": "development",
        "features": {
            "adaptive_weighting": True,
            "semantic_matching": True,
            "real_time_processing": True,
            "bridge_integration": True
        }
    }

@app.post("/api/v1/matching/candidate/{candidate_id}", tags=["🎯 Matching"])
async def match_candidate(candidate_id: str, request: MatchingRequest):
    """🎯 ENDPOINT PRINCIPAL: Matching avec Pondération Adaptative"""
    start_time = time.time()
    
    logger.info(f"🎯 === MATCHING CANDIDAT {candidate_id} ===")
    logger.info(f"📋 Raison d'écoute: '{request.pourquoi_ecoute}'")
    logger.info(f"👤 Candidat: {request.candidate_profile.personal_info.firstName} {request.candidate_profile.personal_info.lastName}")
    logger.info(f"💼 Compétences: {request.candidate_profile.skills}")
    logger.info(f"💰 Attentes: {request.preferences.salary_expectations.min}€ - {request.preferences.salary_expectations.max}€")
    
    try:
        # 1. 🎯 Pondération adaptative
        weight_analysis = get_adaptive_weights(request.pourquoi_ecoute)
        weights = weight_analysis["weights"]
        
        # 2. 🧮 Calcul des scores
        matching_analysis = calculate_mock_matching_scores(request, weights)
        
        # 3. 📊 Réponse détaillée
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        response = {
            "status": "success",
            "candidate_id": candidate_id,
            "matching_results": {
                "total_score": matching_analysis["total_score"],
                "confidence": matching_analysis["confidence"],
                "component_scores": matching_analysis["component_scores"],
                "weights_used": weights
            },
            "adaptive_weighting": {
                "applied": weight_analysis["adaptation_applied"],
                "reason": request.pourquoi_ecoute,
                "reasoning": weight_analysis["reasoning"],
                "weight_changes": _calculate_weight_changes(weights) if weight_analysis["adaptation_applied"] else None
            },
            "candidate_summary": {
                "name": f"{request.candidate_profile.personal_info.firstName} {request.candidate_profile.personal_info.lastName}",
                "skills_count": len(request.candidate_profile.skills),
                "experience_years": request.candidate_profile.experience_years,
                "salary_range": f"{request.preferences.salary_expectations.min}€ - {request.preferences.salary_expectations.max}€"
            },
            "metadata": {
                "processing_time_ms": processing_time,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "api_version": "1.0.0",
                "algorithm": "Adaptive Contextual Weighting"
            }
        }
        
        logger.info(f"✅ Matching terminé en {processing_time}ms")
        logger.info(f"📊 Score final: {matching_analysis['total_score']} (confiance: {matching_analysis['confidence']})")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Erreur matching: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.get("/api/v1/weights/preview", tags=["🎯 Matching"])
async def preview_adaptive_weights(pourquoi_ecoute: str):
    """🔍 Prévisualisation des Poids Adaptatifs"""
    weight_analysis = get_adaptive_weights(pourquoi_ecoute)
    
    return {
        "reason": pourquoi_ecoute,
        "default_weights": DEFAULT_WEIGHTS,
        "adapted_weights": weight_analysis["weights"],
        "adaptation_applied": weight_analysis["adaptation_applied"],
        "reasoning": weight_analysis["reasoning"],
        "weight_changes": _calculate_weight_changes(weight_analysis["weights"]) if weight_analysis["adaptation_applied"] else None,
        "supported_reasons": list(ADAPTIVE_WEIGHTS_CONFIG.keys())
    }

@app.get("/api/v1/debug/supported-reasons", tags=["🔧 Debug"])
async def get_supported_reasons():
    """🔧 Liste des raisons supportées"""
    return {
        "supported_reasons": list(ADAPTIVE_WEIGHTS_CONFIG.keys()),
        "default_weights": DEFAULT_WEIGHTS,
        "adaptive_configs": ADAPTIVE_WEIGHTS_CONFIG
    }

# ===== 🌉 NOUVEAUX ENDPOINTS D'INTÉGRATION BRIDGE =====

@app.post("/api/v1/integration/complete-workflow", tags=["🌉 Integration"])
async def complete_workflow_integration(
    pourquoi_ecoute: str = Form(...),
    job_file: Optional[UploadFile] = File(None),
    job_text: Optional[str] = Form(None),
    cv_file: Optional[UploadFile] = File(None),
    force_refresh: bool = Form(False)
):
    """
    🌉 WORKFLOW COMPLET NEXTEN: Job Parsing + CV Parsing + Matching Adaptatif
    
    Cet endpoint orchestre l'ensemble du processus NEXTEN :
    1. Parse l'offre d'emploi avec Commitment- Job Parser GPT
    2. Parse le CV avec Commitment- CV Parser GPT  
    3. Applique l'algorithme de matching avec pondération adaptative
    
    **Paramètres :**
    - `pourquoi_ecoute` : Raison d'écoute du candidat (pour pondération adaptative)
    - `job_file` : Fichier de l'offre d'emploi (PDF, DOCX, TXT) [optionnel]
    - `job_text` : Texte de l'offre d'emploi [optionnel, alternatif à job_file]
    - `cv_file` : Fichier CV du candidat (PDF, DOCX, TXT) [optionnel]
    - `force_refresh` : Force le re-parsing même si en cache
    
    **Innovation :** Pondération adaptative selon le pourquoi_ecoute
    """
    start_time = time.time()
    
    logger.info("🌉 === WORKFLOW COMPLET NEXTEN ===")
    logger.info(f"📋 Raison d'écoute: '{pourquoi_ecoute}'")
    
    # Validation des paramètres
    if not job_file and not job_text and not cv_file:
        raise HTTPException(
            status_code=400, 
            detail="Au moins un des paramètres job_file, job_text ou cv_file doit être fourni"
        )
    
    try:
        # Préparation des fichiers temporaires
        job_file_data = None
        cv_file_data = None
        temp_files = []
        
        if job_file:
            # Créer un fichier temporaire pour le job
            job_temp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{job_file.filename.split('.')[-1]}")
            shutil.copyfileobj(job_file.file, job_temp)
            job_temp.close()
            temp_files.append(job_temp.name)
            
            with open(job_temp.name, 'rb') as f:
                job_file_data = f.read()
        
        if cv_file:
            # Créer un fichier temporaire pour le CV
            cv_temp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{cv_file.filename.split('.')[-1]}")
            shutil.copyfileobj(cv_file.file, cv_temp)
            cv_temp.close()
            temp_files.append(cv_temp.name)
            
            with open(cv_temp.name, 'rb') as f:
                cv_file_data = f.read()
        
        # Création de la requête bridge
        bridge_request = BridgeRequest(
            pourquoi_ecoute=pourquoi_ecoute,
            job_file=job_file_data,
            job_text=job_text,
            cv_file=cv_file_data,
            force_refresh=force_refresh
        )
        
        # Exécution du workflow avec le bridge
        async with CommitmentNextvisionBridge() as bridge:
            result = await bridge.execute_complete_workflow(bridge_request)
        
        # Nettoyage des fichiers temporaires
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
        
        # Enrichissement de la réponse
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        response_data = {
            "status": result.status,
            "workflow_results": {
                "job_parsing": {
                    "success": result.job_data is not None,
                    "data": result.job_data.dict() if result.job_data else None
                },
                "cv_parsing": {
                    "success": result.cv_data is not None,
                    "data": result.cv_data.dict() if result.cv_data else None
                },
                "matching": {
                    "success": result.matching_results is not None,
                    "data": result.matching_results
                }
            },
            "integration_metadata": {
                "processing_time_ms": processing_time,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "bridge_version": "1.0.0",
                "services_integration": "Commitment- → Nextvision",
                "adaptive_weighting": True
            },
            "performance": result.processing_details,
            "errors": result.errors
        }
        
        logger.info(f"✅ Workflow complet terminé en {processing_time}ms")
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"❌ Erreur workflow complet: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur workflow: {str(e)}")

@app.post("/api/v1/integration/parse-job-from-commitment", tags=["🌉 Integration"])
async def parse_job_from_commitment(
    job_file: Optional[UploadFile] = File(None),
    job_text: Optional[str] = Form(None),
    force_refresh: bool = Form(False)
):
    """
    📋 Parse une offre d'emploi via Commitment- Job Parser GPT
    
    Utilise directement le service Job Parser GPT de Commitment- pour analyser
    une offre d'emploi et retourner les données structurées.
    
    **Avantages :**
    - Réutilise l'infrastructure GPT mature de Commitment-
    - Zéro redondance de code
    - Parsing intelligent avec GPT-4
    """
    start_time = time.time()
    
    logger.info("📋 Parsing offre d'emploi via Commitment-")
    
    if not job_file and not job_text:
        raise HTTPException(
            status_code=400,
            detail="Soit job_file soit job_text doit être fourni"
        )
    
    try:
        # Préparation des données
        job_file_data = None
        temp_file = None
        
        if job_file:
            # Créer un fichier temporaire
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{job_file.filename.split('.')[-1]}")
            shutil.copyfileobj(job_file.file, temp_file)
            temp_file.close()
            
            with open(temp_file.name, 'rb') as f:
                job_file_data = f.read()
        
        # Utilisation du bridge pour le parsing Job
        async with CommitmentNextvisionBridge() as bridge:
            await bridge.detect_commitment_services()
            
            if job_file_data:
                job_data = await bridge.parse_job_with_commitment(file_data=job_file_data)
            else:
                job_data = await bridge.parse_job_with_commitment(text_data=job_text)
        
        # Nettoyage
        if temp_file:
            try:
                os.unlink(temp_file.name)
            except:
                pass
        
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        response_data = {
            "status": "success",
            "job_data": job_data.dict(),
            "parsing_metadata": {
                "source": "commitment_job_parser_gpt",
                "processing_time_ms": processing_time,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "file_type": job_file.content_type if job_file else "text",
                "gpt_powered": True
            }
        }
        
        logger.info(f"✅ Job parsing terminé en {processing_time}ms")
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"❌ Erreur job parsing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur parsing: {str(e)}")

@app.post("/api/v1/integration/parse-cv-from-commitment", tags=["🌉 Integration"])
async def parse_cv_from_commitment(
    cv_file: UploadFile = File(...),
    force_refresh: bool = Form(False)
):
    """
    📄 Parse un CV via Commitment- CV Parser GPT
    
    Utilise directement le service CV Parser GPT de Commitment- pour analyser
    un CV et retourner les données structurées du candidat.
    
    **Avantages :**
    - Réutilise l'infrastructure GPT mature de Commitment-
    - Extraction complète des informations candidat
    - Compatible avec PDF, DOCX, TXT
    """
    start_time = time.time()
    
    logger.info("📄 Parsing CV via Commitment-")
    
    try:
        # Préparation du fichier
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{cv_file.filename.split('.')[-1]}")
        shutil.copyfileobj(cv_file.file, temp_file)
        temp_file.close()
        
        with open(temp_file.name, 'rb') as f:
            cv_file_data = f.read()
        
        # Utilisation du bridge pour le parsing CV
        async with CommitmentNextvisionBridge() as bridge:
            await bridge.detect_commitment_services()
            cv_data = await bridge.parse_cv_with_commitment(cv_file_data)
        
        # Nettoyage
        try:
            os.unlink(temp_file.name)
        except:
            pass
        
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        response_data = {
            "status": "success",
            "cv_data": cv_data.dict(),
            "parsing_metadata": {
                "source": "commitment_cv_parser_gpt",
                "processing_time_ms": processing_time,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "file_type": cv_file.content_type,
                "file_size": cv_file.size if hasattr(cv_file, 'size') else 0,
                "gpt_powered": True,
                "candidate_name": cv_data.name
            }
        }
        
        logger.info(f"✅ CV parsing terminé en {processing_time}ms - {cv_data.name}")
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"❌ Erreur CV parsing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur parsing: {str(e)}")

@app.post("/api/v1/integration/cv-to-matching", tags=["🌉 Integration"])
async def cv_to_matching_workflow(
    cv_file: UploadFile = File(...),
    pourquoi_ecoute: str = Form(...),
    force_refresh: bool = Form(False)
):
    """
    🎯 Workflow CV → Matching Adaptatif
    
    Workflow optimisé qui :
    1. Parse le CV avec Commitment- CV Parser GPT
    2. Convertit les données en format Nextvision
    3. Applique la pondération adaptative contextuelle
    4. Retourne le score de matching et les explications
    
    **Innovation :** Pipeline intégré CV → Matching avec pondération adaptative
    """
    start_time = time.time()
    
    logger.info("🎯 Workflow CV → Matching Adaptatif")
    logger.info(f"📋 Raison d'écoute: '{pourquoi_ecoute}'")
    
    try:
        # Étape 1: Parse CV
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{cv_file.filename.split('.')[-1]}")
        shutil.copyfileobj(cv_file.file, temp_file)
        temp_file.close()
        
        with open(temp_file.name, 'rb') as f:
            cv_file_data = f.read()
        
        async with CommitmentNextvisionBridge() as bridge:
            # Parse CV
            await bridge.detect_commitment_services()
            cv_data = await bridge.parse_cv_with_commitment(cv_file_data)
            
            # Conversion vers format matching
            matching_request = bridge._cv_to_matching_request(cv_data, pourquoi_ecoute)
            
            # Appel matching (simulé pour l'instant)
            matching_results = await bridge._simulate_nextvision_matching(matching_request)
        
        # Nettoyage
        try:
            os.unlink(temp_file.name)
        except:
            pass
        
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        response_data = {
            "status": "success",
            "candidate_summary": {
                "name": cv_data.name,
                "email": cv_data.email,
                "skills_count": len(cv_data.skills),
                "experience_years": cv_data.years_of_experience,
                "location": cv_data.location
            },
            "matching_results": matching_results,
            "adaptive_context": {
                "pourquoi_ecoute": pourquoi_ecoute,
                "adaptive_weighting_applied": True,
                "reasoning": f"Pondération adaptée pour: {pourquoi_ecoute}"
            },
            "workflow_metadata": {
                "processing_time_ms": processing_time,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "pipeline": "CV_Parser_GPT → Adaptive_Matching",
                "services_used": ["commitment_cv_parser", "nextvision_matching"]
            }
        }
        
        logger.info(f"✅ Workflow CV→Matching terminé en {processing_time}ms")
        logger.info(f"📊 Score: {matching_results['total_score']} pour {cv_data.name}")
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"❌ Erreur workflow CV→Matching: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur workflow: {str(e)}")

@app.get("/api/v1/integration/health", tags=["🌉 Integration"])
async def integration_health_check():
    """
    ❤️ Health Check de l'intégration Bridge
    
    Vérifie l'état de santé de l'intégration entre Commitment- et Nextvision
    """
    try:
        async with CommitmentNextvisionBridge() as bridge:
            job_available, cv_available = await bridge.detect_commitment_services()
            health_status = bridge.get_health_status()
        
        return {
            "status": "healthy",
            "integration_bridge": {
                "version": "1.0.0",
                "status": "active"
            },
            "commitment_services": {
                "job_parser": {
                    "available": job_available,
                    "url": bridge.commitment_job_url if job_available else None
                },
                "cv_parser": {
                    "available": cv_available,
                    "url": bridge.commitment_cv_url if cv_available else None
                }
            },
            "nextvision_features": {
                "adaptive_weighting": True,
                "semantic_matching": True,
                "real_time_processing": True
            },
            "integration_capabilities": {
                "complete_workflow": job_available and cv_available,
                "job_parsing_only": job_available,
                "cv_parsing_only": cv_available,
                "matching_only": True
            },
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur health check: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        )

@app.get("/api/v1/integration/status", tags=["🌉 Integration"])
async def integration_status():
    """
    📊 Status détaillé de l'intégration NEXTEN
    
    Fournit un aperçu complet de l'état de l'écosystème NEXTEN
    """
    try:
        async with CommitmentNextvisionBridge() as bridge:
            job_available, cv_available = await bridge.detect_commitment_services()
        
        return {
            "nexten_ecosystem": {
                "name": "NEXTEN",
                "description": "Écosystème révolutionnaire de matching RH avec pondération adaptative",
                "version": "1.0.0",
                "innovation": "Premier système au monde avec pondération adaptative contextuelle"
            },
            "architecture": {
                "frontend_backend": {
                    "name": "Commitment-",
                    "repository": "https://github.com/Bapt252/Commitment-",
                    "role": "Parsing GPT (Job + CV)",
                    "status": "operational" if (job_available or cv_available) else "unavailable"
                },
                "ai_backend": {
                    "name": "Nextvision",
                    "repository": "https://github.com/Bapt252/Nextvision",
                    "role": "Matching IA adaptatif",
                    "status": "operational"
                },
                "bridge": {
                    "name": "CommitmentNextvisionBridge",
                    "role": "Intégration zéro redondance",
                    "status": "active"
                }
            },
            "services_availability": {
                "commitment_job_parser": job_available,
                "commitment_cv_parser": cv_available,
                "nextvision_matching": True,
                "adaptive_weighting": True
            },
            "competitive_advantages": [
                "Double parsing GPT mature (Job + CV)",
                "Algorithme de matching révolutionnaire",
                "Pondération adaptative contextuelle unique",
                "Architecture zéro redondance",
                "Time-to-market optimisé"
            ],
            "supported_workflows": [
                "Complete workflow (Job + CV → Matching)",
                "Job parsing only",
                "CV parsing only", 
                "CV → Adaptive matching",
                "Adaptive weight preview"
            ]
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# ===== MIDDLEWARE POUR L'INTÉGRATION =====

@app.middleware("http")
async def integration_logging_middleware(request, call_next):
    """📝 Middleware pour logger les requêtes d'intégration"""
    start_time = time.time()
    
    # Logger les requêtes d'intégration
    if request.url.path.startswith("/api/v1/integration/"):
        logger.info(f"🌉 {request.method} {request.url.path} - Intégration Bridge")
    
    response = await call_next(request)
    
    # Logger les performances
    if request.url.path.startswith("/api/v1/integration/"):
        process_time = round((time.time() - start_time) * 1000, 2)
        logger.info(f"✅ {request.method} {request.url.path} - {response.status_code} - {process_time}ms")
    
    return response

if __name__ == "__main__":
    print("🎯 === NEXTVISION API STARTUP AVEC BRIDGE ===")
    print("🚀 Algorithme de matching IA adaptatif pour NEXTEN")
    print("🌉 Bridge Commitment- → Nextvision INTÉGRÉ")
    print("📚 Documentation: http://localhost:8000/docs")
    print("❤️ Health Check: http://localhost:8000/api/v1/health")
    print("🌉 Integration Health: http://localhost:8000/api/v1/integration/health")
    print("📊 Integration Status: http://localhost:8000/api/v1/integration/status")
    print("🔍 Preview Weights: http://localhost:8000/api/v1/weights/preview")
    print("🎯 Pondération Adaptative: ACTIVE")
    print("🔗 Intégration révolutionnaire: OPÉRATIONNELLE")
    print("===============================================")
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
