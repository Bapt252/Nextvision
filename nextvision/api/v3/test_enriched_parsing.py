"""
🧪 ENDPOINT TEST ENRICHI - VALIDATION STRUCTURE SÉMANTIQUE
=========================================================

Endpoint de test pour valider la nouvelle structure enrichie
avant intégration complète dans l'API principale.

Test du parsing sémantique complet avec structure 10x plus riche.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging
import time
import os
from datetime import datetime

# Import du nouveau service enrichi
from nextvision.services.gpt_direct_service_enriched import (
    get_gpt_service_enriched,
    parse_cv_enriched,
    CVDataEnriched
)

# Configuration logging
logger = logging.getLogger(__name__)

# Router pour les tests enrichis
router = APIRouter(prefix="/api/v3/test", tags=["🧪 Test Parsing Enrichi"])

def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """📄 Extract text from files (fonction réutilisée)"""
    try:
        import PyPDF2
        from docx import Document
        import io
        
        extension = os.path.splitext(filename)[1].lower()
        
        if extension == '.pdf':
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        elif extension in ['.docx', '.doc']:
            doc = Document(io.BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        elif extension == '.txt':
            return file_content.decode('utf-8', errors='ignore')
        else:
            return file_content.decode('utf-8', errors='ignore')
    except Exception as e:
        logger.error(f"❌ Text extraction failed: {e}")
        return file_content.decode('utf-8', errors='ignore')

def serialize_cv_enriched(cv_data: CVDataEnriched) -> Dict[str, Any]:
    """🔄 Sérialisation CVDataEnriched en dictionnaire"""
    return {
        "personal_info": {
            "name": cv_data.name,
            "firstName": cv_data.firstName,
            "lastName": cv_data.lastName,
            "email": cv_data.email,
            "phone": cv_data.phone,
            "location": cv_data.location
        },
        "experiences": [
            {
                "job_title": exp.job_title,
                "company": exp.company,
                "sector": exp.sector,
                "location": exp.location,
                "start_date": exp.start_date,
                "end_date": exp.end_date,
                "duration_months": exp.duration_months,
                "contract_type": exp.contract_type,
                "is_current": exp.is_current,
                "missions": exp.missions,
                "achievements": exp.achievements,
                "skills_used": exp.skills_used,
                "tools_used": exp.tools_used,
                "team_size": exp.team_size,
                "budget_managed": exp.budget_managed,
                "international_scope": exp.international_scope,
                "languages_used": exp.languages_used
            }
            for exp in cv_data.experiences
        ],
        "formations": [
            {
                "degree": form.degree,
                "institution": form.institution,
                "location": form.location,
                "start_date": form.start_date,
                "end_date": form.end_date,
                "grade": form.grade,
                "specialization": form.specialization,
                "main_subjects": form.main_subjects,
                "international_programs": form.international_programs,
                "skills_acquired": form.skills_acquired
            }
            for form in cv_data.formations
        ],
        "competences": [
            {
                "name": comp.name,
                "category": comp.category,
                "level": comp.level,
                "years_experience": comp.years_experience,
                "contexts_used": comp.contexts_used
            }
            for comp in cv_data.competences
        ],
        "languages": cv_data.languages,
        "certifications": cv_data.certifications,
        "career_goals": cv_data.career_goals,
        "preferred_sectors": cv_data.preferred_sectors,
        "geographic_mobility": cv_data.geographic_mobility,
        "remote_preferences": cv_data.remote_preferences,
        "current_situation": cv_data.current_situation,
        "reason_for_change": cv_data.reason_for_change,
        "total_experience_years": cv_data.total_experience_years,
        "parsing_completeness": cv_data.parsing_completeness
    }

@router.post("/parsing-enrichi", summary="🧪 Test Parsing CV Enrichi - Structure Sémantique Complète")
async def test_parsing_enrichi(
    cv_file: UploadFile = File(..., description="📄 Fichier CV à tester"),
    include_analysis: bool = Form(default=True, description="🔍 Inclure analyse comparative")
):
    """
    🧪 **ENDPOINT TEST PARSING ENRICHI**
    
    Teste la nouvelle structure enrichie pour maximiser le matching sémantique.
    
    ## 🚀 Nouveautés testées :
    
    1. **Expériences multiples** : Tous les postes avec missions détaillées
    2. **Compétences contextualisées** : Utilisées dans quels contextes
    3. **Formations enrichies** : Programmes internationaux, compétences acquises
    4. **Aspirations captées** : Objectifs de carrière, secteurs préférés
    5. **Mobilité détaillée** : Géographique, remote, transport
    
    ## 📊 Structure enrichie vs structure actuelle :
    
    **Structure actuelle** :
    - `skills: []` (liste simple)
    - `job_titles: []` (liste simple)
    - `companies: []` (liste simple)
    
    **Structure enrichie** :
    - `experiences: [{ job_title, company, sector, missions[], achievements[], skills_used[] }]`
    - `competences: [{ name, category, level, years_experience, contexts_used[] }]`
    - `formations: [{ degree, institution, main_subjects[], international_programs[] }]`
    
    ## 🎯 Objectif :
    Valider que la nouvelle structure capture 10x plus de détails
    pour un matching sémantique optimal.
    """
    
    start_time = time.time()
    
    logger.info("🧪 === TEST PARSING ENRICHI START ===")
    logger.info(f"📄 CV file: {cv_file.filename}")
    
    try:
        # Validation format
        allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
        cv_extension = os.path.splitext(cv_file.filename)[1].lower()
        
        if cv_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Format non supporté: {cv_extension}. Formats acceptés: {allowed_extensions}"
            )
        
        # === EXTRACTION CONTENU ===
        extraction_start = time.time()
        
        cv_content = await cv_file.read()
        cv_content_str = extract_text_from_file(cv_content, cv_file.filename)
        
        extraction_time = (time.time() - extraction_start) * 1000
        
        # === PARSING ENRICHI ===
        parsing_start = time.time()
        
        cv_data_enriched = await parse_cv_enriched(cv_content_str)
        
        parsing_time = (time.time() - parsing_start) * 1000
        
        # === SÉRIALISATION ===
        serialization_start = time.time()
        
        cv_serialized = serialize_cv_enriched(cv_data_enriched)
        
        serialization_time = (time.time() - serialization_start) * 1000
        
        # === ANALYSE COMPARATIVE ===
        analysis = {}
        if include_analysis:
            analysis = {
                "structure_comparison": {
                    "experiences_count": len(cv_data_enriched.experiences),
                    "formations_count": len(cv_data_enriched.formations),
                    "competences_count": len(cv_data_enriched.competences),
                    "total_missions": sum(len(exp.missions) for exp in cv_data_enriched.experiences),
                    "total_achievements": sum(len(exp.achievements) for exp in cv_data_enriched.experiences),
                    "total_skills_contextualized": sum(len(exp.skills_used) for exp in cv_data_enriched.experiences),
                    "international_programs": sum(len(form.international_programs) for form in cv_data_enriched.formations),
                    "career_goals_captured": len(cv_data_enriched.career_goals),
                    "preferred_sectors_captured": len(cv_data_enriched.preferred_sectors)
                },
                "data_richness": {
                    "personal_info_completeness": len([v for v in [cv_data_enriched.email, cv_data_enriched.phone, cv_data_enriched.location] if v]),
                    "experience_detail_score": sum(len(exp.missions) + len(exp.achievements) + len(exp.skills_used) for exp in cv_data_enriched.experiences),
                    "formation_detail_score": sum(len(form.main_subjects) + len(form.international_programs) for form in cv_data_enriched.formations),
                    "competence_contextualization": sum(len(comp.contexts_used) for comp in cv_data_enriched.competences),
                    "parsing_completeness": cv_data_enriched.parsing_completeness
                },
                "semantic_matching_potential": {
                    "job_matching_signals": len(cv_data_enriched.experiences) * 5,  # missions, achievements, skills par exp
                    "skill_matching_signals": len(cv_data_enriched.competences) * 3,  # name, category, level
                    "sector_matching_signals": len(set(exp.sector for exp in cv_data_enriched.experiences if exp.sector)),
                    "mobility_matching_signals": len([v for v in [cv_data_enriched.geographic_mobility, cv_data_enriched.remote_preferences] if v]),
                    "total_matching_signals": len(cv_data_enriched.experiences) * 8 + len(cv_data_enriched.competences) * 3 + len(cv_data_enriched.career_goals)
                }
            }
        
        # === RÉSULTAT FINAL ===
        total_time = (time.time() - start_time) * 1000
        
        result = {
            "status": "success",
            "message": "Parsing enrichi terminé avec succès",
            "cv_data_enriched": cv_serialized,
            "analysis": analysis,
            "performance": {
                "total_time_ms": round(total_time, 2),
                "extraction_time_ms": round(extraction_time, 2),
                "parsing_time_ms": round(parsing_time, 2),
                "serialization_time_ms": round(serialization_time, 2),
                "performance_grade": "🚀 Excellent" if total_time < 5000 else ("✅ Bon" if total_time < 15000 else "⚠️ Lent")
            },
            "metadata": {
                "api_version": "3.2.1-enriched-test",
                "timestamp": datetime.now().isoformat(),
                "endpoint": "/api/v3/test/parsing-enrichi",
                "parsing_method": "gpt-3.5-turbo-enriched",
                "file_info": {
                    "filename": cv_file.filename,
                    "size_bytes": cv_file.size,
                    "content_length": len(cv_content_str),
                    "format": cv_extension
                }
            }
        }
        
        logger.info(f"✅ Test parsing enrichi terminé en {total_time:.2f}ms")
        logger.info(f"📊 Expériences: {len(cv_data_enriched.experiences)}, Formations: {len(cv_data_enriched.formations)}")
        logger.info(f"🎯 Compétences: {len(cv_data_enriched.competences)}, Objectifs: {len(cv_data_enriched.career_goals)}")
        
        return JSONResponse(
            status_code=200,
            content=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        total_time = (time.time() - start_time) * 1000
        logger.error(f"❌ Test parsing enrichi failed: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Test parsing enrichi failed",
                "message": str(e),
                "processing_time_ms": round(total_time, 2),
                "timestamp": datetime.now().isoformat()
            }
        )

@router.get("/status-enrichi", summary="📊 Status Service Enrichi")
async def status_service_enrichi():
    """📊 Status du service de parsing enrichi"""
    
    service = get_gpt_service_enriched()
    
    return {
        "service": "GPT Direct Service Enrichi",
        "version": "3.2.1-enriched",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "experiences_multiples": True,
            "missions_detaillees": True,
            "competences_contextualisees": True,
            "formations_enrichies": True,
            "aspirations_captees": True,
            "mobilite_detaillee": True,
            "parsing_semantique": True
        },
        "structure_enrichie": {
            "experiences": "job_title, company, sector, missions[], achievements[], skills_used[]",
            "formations": "degree, institution, main_subjects[], international_programs[]",
            "competences": "name, category, level, years_experience, contexts_used[]",
            "aspirations": "career_goals[], preferred_sectors[], geographic_mobility"
        },
        "performance": {
            "target_time": "< 15s",
            "model": "gpt-3.5-turbo",
            "prompt_size": "2500 chars",
            "max_tokens": "1500"
        },
        "api_key_configured": service.api_key is not None,
        "endpoint_test": "/api/v3/test/parsing-enrichi"
    }
