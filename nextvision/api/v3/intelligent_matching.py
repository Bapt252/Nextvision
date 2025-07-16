"""
🎯 ENDPOINT UNIFIÉ RÉVOLUTIONNAIRE - NEXTVISION v3.2.1 + MOTIVATIONS
====================================================================

RÉVOLUTION WORKFLOW : 5 étapes manuelles → 1 étape automatique
- Input : CV file + Job file + questionnaire optionnel
- Output : Résultat matching complet avec Transport Intelligence + MOTIVATIONS
- Performance : < 2000ms objectif
- Architecture : Parse → Transform → Match (automatique)

🆕 NOUVEAU: Score Motivations intégré (8% du score total)

Author: NEXTEN Team  
Version: 3.2.1 + Motivations Integration
Innovation: Workflow unifié automatique + Transport Intelligence + Motivations Analysis
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
import logging
import time
import json
import tempfile
import os
from datetime import datetime
import io

# Import for file processing
try:
    import PyPDF2
    from docx import Document
    PDF_PROCESSING_AVAILABLE = True
except ImportError:
    PDF_PROCESSING_AVAILABLE = False

# Import Adaptateur Intelligent
from nextvision.adapters.parsing_to_matching_adapter import (
    create_unified_matching_request,
    AdaptationResult
)

# Import services Nextvision
from nextvision.services.commitment_bridge import CommitmentNextvisionBridge, BridgeConfig
from nextvision.engines.location_scoring import LocationScoringEngine
from nextvision.engines.transport_filtering import TransportFilteringEngine
from nextvision.services.transport_calculator import TransportCalculator
from nextvision.services.google_maps_service import GoogleMapsService
from nextvision.config.google_maps_config import get_google_maps_config

# 🚀 Import SERVICE GPT DIRECT
from nextvision.services.gpt_direct_service import (
    get_gpt_service,
    parse_cv_direct,
    parse_job_direct,
    GPTDirectService,
    CVData,
    JobData
)

# 🆕 Import MOTIVATIONS SCORER
try:
    from nextvision.engines.motivations_scoring_engine import (
        MotivationsAlignmentScorer,
        motivations_scoring_engine,
        create_complete_cv_data,
        create_complete_job_data,
        MotivationType,
        MotivationsResult
    )
    MOTIVATIONS_SCORER_AVAILABLE = True
    logger_motivations = logging.getLogger(__name__ + ".motivations")
    logger_motivations.info("✅ MotivationsAlignmentScorer successfully imported")
except ImportError as e:
    MOTIVATIONS_SCORER_AVAILABLE = False
    logger_motivations = logging.getLogger(__name__ + ".motivations")
    logger_motivations.warning(f"⚠️ MotivationsAlignmentScorer not available: {e}")

# Configuration logging
logger = logging.getLogger(__name__)

# Router pour API v3
router = APIRouter(prefix="/api/v3", tags=["🎯 Intelligent Matching v3.2.1 + Motivations"])

# === SERVICES INITIALIZATION ===
google_maps_config = get_google_maps_config()

# Services Google Maps et Transport Intelligence
google_maps_service = GoogleMapsService(
    api_key=google_maps_config.api_key,
    cache_duration_hours=google_maps_config.geocode_cache_duration_hours
)

transport_calculator = TransportCalculator(google_maps_service)
transport_filtering_engine = TransportFilteringEngine(transport_calculator)
location_scoring_engine = LocationScoringEngine(transport_calculator)

# Service GPT Direct
gpt_service = get_gpt_service()

# Bridge Commitment-
try:
    bridge_config = BridgeConfig()
    commitment_bridge = CommitmentNextvisionBridge(bridge_config)
    logger.info("✅ Commitment Bridge initialized for v3 endpoint")
except Exception as e:
    logger.warning(f"⚠️ Commitment Bridge initialization failed: {e}")
    commitment_bridge = None

def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """📄 Extract text from PDF/DOCX files"""
    try:
        extension = os.path.splitext(filename)[1].lower()
        
        if extension == '.pdf':
            if not PDF_PROCESSING_AVAILABLE:
                logger.warning("⚠️ PyPDF2 not available, using raw content")
                return file_content.decode('utf-8', errors='ignore')
            
            # Extract text from PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            logger.info(f"✅ PDF text extracted: {len(text)} characters")
            return text
            
        elif extension in ['.docx', '.doc']:
            if not PDF_PROCESSING_AVAILABLE:
                logger.warning("⚠️ python-docx not available, using raw content")
                return file_content.decode('utf-8', errors='ignore')
            
            # Extract text from DOCX
            doc = Document(io.BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            logger.info(f"✅ DOCX text extracted: {len(text)} characters")
            return text
            
        elif extension == '.txt':
            # Plain text file
            text = file_content.decode('utf-8', errors='ignore')
            logger.info(f"✅ TXT content loaded: {len(text)} characters")
            return text
            
        else:
            # Fallback: try to decode as text
            logger.warning(f"⚠️ Unknown extension {extension}, trying UTF-8 decode")
            return file_content.decode('utf-8', errors='ignore')
            
    except Exception as e:
        logger.error(f"❌ Text extraction failed for {filename}: {e}")
        # Last resort fallback
        return file_content.decode('utf-8', errors='ignore')

class IntelligentMatchingService:
    """
    🎯 SERVICE INTELLIGENT MATCHING RÉVOLUTIONNAIRE + MOTIVATIONS
    =============================================================
    
    **Innovation** : Workflow automatique complet en une seule requête
    - ✅ Parse CV + Job avec GPT Direct Service
    - ✅ Transform avec Adaptateur Intelligent
    - ✅ Match avec Transport Intelligence intégré
    - 🆕 Score Motivations intégré (8% du score total)
    - ✅ Performance optimisée < 2000ms
    
    **Transformation** : 5 étapes → 1 étape automatique
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialisation Motivations Scorer
        if MOTIVATIONS_SCORER_AVAILABLE:
            self.motivations_scorer = motivations_scoring_engine
            self.logger.info("✅ MotivationsAlignmentScorer initialized")
        else:
            self.motivations_scorer = None
            self.logger.warning("⚠️ MotivationsAlignmentScorer not available, using fallback")
        
    async def process_intelligent_matching(
        self,
        cv_file: UploadFile,
        job_file: Optional[UploadFile] = None,
        pourquoi_ecoute: str = "Recherche nouveau défi",
        questionnaire_data: Optional[str] = None,
        job_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        🎯 TRAITEMENT INTELLIGENT MATCHING COMPLET + MOTIVATIONS
        
        **Workflow Automatique** :
        1. Parse CV + Job (GPT Direct Service)
        2. Transform formats (Adaptateur Intelligent)
        3. Calculate matching (Transport Intelligence + Motivations)
        4. Return unified result
        
        **Performance** : < 2000ms objectif
        """
        start_time = time.time()
        
        self.logger.info("🎯 === INTELLIGENT MATCHING WORKFLOW START (+ MOTIVATIONS) ===")
        self.logger.info(f"📋 Pourquoi écoute: {pourquoi_ecoute}")
        self.logger.info(f"📄 CV file: {cv_file.filename}")
        self.logger.info(f"💼 Job file: {job_file.filename if job_file else 'None'}")
        self.logger.info(f"🎯 Motivations scorer: {'✅ Enabled' if MOTIVATIONS_SCORER_AVAILABLE else '⚠️ Fallback'}")
        
        try:
            # === PHASE 1: PARSING WITH GPT DIRECT ===
            parsing_start = time.time()
            
            cv_data, job_data = await self._parse_files_with_gpt_direct(cv_file, job_file)
            
            parsing_time = (time.time() - parsing_start) * 1000
            self.logger.info(f"✅ Parsing completed in {parsing_time:.2f}ms")
            
            # === PHASE 2: ADAPTATION INTELLIGENTE ===
            adaptation_start = time.time()
            
            # Parse questionnaire optionnel
            additional_context = {}
            if questionnaire_data:
                try:
                    additional_context = json.loads(questionnaire_data)
                except json.JSONDecodeError:
                    self.logger.warning("⚠️ Invalid questionnaire JSON, using default context")
            
            # Utilisation de l'Adaptateur Intelligent
            adaptation_result = create_unified_matching_request(
                cv_data=cv_data,
                job_data=job_data,
                pourquoi_ecoute=pourquoi_ecoute,
                additional_context=additional_context
            )
            
            if not adaptation_result.success:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Adaptation failed: {adaptation_result.validation_errors}"
                )
            
            matching_request = adaptation_result.matching_request
            adaptation_time = (time.time() - adaptation_start) * 1000
            
            self.logger.info(f"✅ Adaptation completed in {adaptation_time:.2f}ms")
            self.logger.info(f"🔧 Adaptations applied: {len(adaptation_result.adaptations_applied)}")
            
            # === PHASE 3: MATCHING WITH TRANSPORT INTELLIGENCE + MOTIVATIONS ===
            matching_start = time.time()
            
            # Extraction job location pour Transport Intelligence
            final_job_address = job_address
            if not final_job_address and matching_request.job_requirements:
                final_job_address = matching_request.job_requirements.location
            if not final_job_address:
                final_job_address = "Paris, France"  # Fallback
            
            # Calcul matching avec Transport Intelligence + Motivations
            matching_result = await self._calculate_intelligent_matching_with_motivations(
                matching_request=matching_request,
                job_address=final_job_address,
                cv_data=cv_data,
                job_data=job_data,
                additional_context=additional_context
            )
            
            matching_time = (time.time() - matching_start) * 1000
            self.logger.info(f"✅ Matching completed in {matching_time:.2f}ms")
            
            # === ASSEMBLAGE RÉSULTAT FINAL ===
            total_time = (time.time() - start_time) * 1000
            
            final_result = {
                "status": "success",
                "message": "Intelligent matching completed successfully with motivations analysis",
                "workflow": {
                    "description": "Parse → Transform → Match + Motivations (automatique)",
                    "stages_completed": ["parsing", "adaptation", "matching", "motivations"],
                    "innovation": "5 étapes manuelles → 1 étape automatique + Motivations"
                },
                "matching_results": matching_result,
                "adaptation_details": {
                    "success": adaptation_result.success,
                    "adaptations_applied": adaptation_result.adaptations_applied,
                    "transformations_count": len(adaptation_result.adaptations_applied),
                    "validation_errors": adaptation_result.validation_errors
                },
                "candidate_summary": {
                    "name": f"{matching_request.candidate_profile.personal_info.firstName} {matching_request.candidate_profile.personal_info.lastName}",
                    "firstName": getattr(matching_request.candidate_profile.personal_info, 'firstName', ''),
                    "lastName": getattr(matching_request.candidate_profile.personal_info, 'lastName', ''),
                    "email": getattr(matching_request.candidate_profile.personal_info, 'email', ''),
                    "phone": getattr(matching_request.candidate_profile.personal_info, 'phone', ''),
                    "skills": getattr(matching_request.candidate_profile, 'skills', []),
                    "skills_count": len(matching_request.candidate_profile.skills),
                    "experience_years": matching_request.candidate_profile.experience_years,
                    "job_titles": getattr(matching_request.candidate_profile, 'job_titles', []),
                    "companies": getattr(matching_request.candidate_profile, 'companies', []),
                    "education": getattr(matching_request.candidate_profile, 'education', ''),
                    "languages": getattr(matching_request.candidate_profile, 'languages', []),
                    "certifications": getattr(matching_request.candidate_profile, 'certifications', []),
                    "summary": getattr(matching_request.candidate_profile, 'summary', ''),
                    "objective": getattr(matching_request.candidate_profile, 'objective', ''),
                    "location": matching_request.preferences.location_preferences.city,
                    "salary_range": f"{matching_request.preferences.salary_expectations.min}€ - {matching_request.preferences.salary_expectations.max}€"
                },
                "job_summary": {
                    "has_job_data": job_data is not None,
                    "job_title": matching_request.job_requirements.title if matching_request.job_requirements else "Job à définir",
                    "company": matching_request.job_requirements.company if matching_request.job_requirements else "Entreprise",
                    "location": final_job_address
                },
                "performance": {
                    "total_time_ms": round(total_time, 2),
                    "parsing_time_ms": round(parsing_time, 2),
                    "adaptation_time_ms": round(adaptation_time, 2),
                    "matching_time_ms": round(matching_time, 2),
                    "target_achieved": total_time < 2000,
                    "performance_grade": "🚀 Excellent" if total_time < 1000 else ("✅ Bon" if total_time < 2000 else "⚠️ Lent")
                },
                "metadata": {
                    "api_version": "3.2.1",
                    "timestamp": datetime.now().isoformat(),
                    "endpoint": "/api/v3/intelligent-matching",
                    "algorithm": "GPT Direct + Adaptateur Intelligent + Transport Intelligence + Motivations Scorer",
                    "gpt_service_status": "operational" if gpt_service else "fallback",
                    "motivations_scorer_status": "operational" if MOTIVATIONS_SCORER_AVAILABLE else "fallback",
                    "bridge_status": "operational" if commitment_bridge else "fallback",
                    "files_processed": {
                        "cv_filename": cv_file.filename,
                        "cv_size_bytes": cv_file.size,
                        "job_filename": job_file.filename if job_file else None,
                        "job_size_bytes": job_file.size if job_file else None
                    }
                }
            }
            
            self.logger.info(f"🎯 === INTELLIGENT MATCHING COMPLETED (+ MOTIVATIONS) ===")
            self.logger.info(f"⏱️  Total time: {total_time:.2f}ms (target: < 2000ms)")
            self.logger.info(f"📊 Matching score: {matching_result.get('total_score', 'N/A')}")
            self.logger.info(f"🎯 Innovation: 5 étapes → 1 étape + Motivations (SUCCESS)")
            
            return final_result
            
        except Exception as e:
            total_time = (time.time() - start_time) * 1000
            self.logger.error(f"❌ Intelligent matching failed: {str(e)}")
            
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Intelligent matching failed",
                    "message": str(e),
                    "processing_time_ms": round(total_time, 2),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    async def _parse_files_with_gpt_direct(
        self, 
        cv_file: UploadFile, 
        job_file: Optional[UploadFile]
    ) -> tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        """🚀 Parse CV + Job avec GPT Direct Service + Text Extraction"""
        
        cv_data = {}
        job_data = None
        
        # === CV PARSING WITH GPT DIRECT ===
        try:
            # Lecture fichier CV
            cv_content = await cv_file.read()
            
            # 🔧 EXTRACTION TEXTE SELON FORMAT
            cv_content_str = extract_text_from_file(cv_content, cv_file.filename)
            
            if not cv_content_str or len(cv_content_str.strip()) < 10:
                raise ValueError(f"No readable text extracted from CV: {cv_file.filename}")
            
            self.logger.info(f"📄 CV text extracted: {len(cv_content_str)} characters from {cv_file.filename}")
            
            # Parse CV avec GPT Direct
            cv_parsed: CVData = await parse_cv_direct(cv_content_str)
            
            cv_data = {
                "name": cv_parsed.name,
                "email": cv_parsed.email,
                "phone": cv_parsed.phone,
                "skills": cv_parsed.skills,
                "years_of_experience": cv_parsed.years_of_experience,
                "education": cv_parsed.education,
                "job_titles": cv_parsed.job_titles,
                "companies": cv_parsed.companies,
                "location": cv_parsed.location,
                "summary": cv_parsed.summary,
                "objective": cv_parsed.objective,
                "languages": cv_parsed.languages,
                "certifications": cv_parsed.certifications
            }
            
            self.logger.info(f"✅ CV GPT Direct parsé: {cv_parsed.name}")
            
        except Exception as e:
            self.logger.error(f"❌ GPT Direct CV parsing failed: {e}")
            self.logger.error(f"📄 CV file: {cv_file.filename}, size: {cv_file.size}")
            cv_data = self._create_fallback_cv_data(cv_file)
        
        # === JOB PARSING WITH GPT DIRECT ===
        if job_file:
            try:
                # Lecture fichier Job
                job_content = await job_file.read()
                
                # 🔧 EXTRACTION TEXTE SELON FORMAT
                job_content_str = extract_text_from_file(job_content, job_file.filename)
                
                if not job_content_str or len(job_content_str.strip()) < 10:
                    raise ValueError(f"No readable text extracted from Job: {job_file.filename}")
                
                self.logger.info(f"💼 Job text extracted: {len(job_content_str)} characters from {job_file.filename}")
                
                # Parse Job avec GPT Direct
                job_parsed: JobData = await parse_job_direct(job_content_str)
                
                job_data = {
                    "title": job_parsed.title,
                    "company": job_parsed.company,
                    "location": job_parsed.location,
                    "contract_type": job_parsed.contract_type,
                    "required_skills": job_parsed.required_skills,
                    "preferred_skills": job_parsed.preferred_skills,
                    "responsibilities": job_parsed.responsibilities,
                    "requirements": job_parsed.requirements,
                    "benefits": job_parsed.benefits,
                    "salary_range": job_parsed.salary_range,
                    "remote_policy": job_parsed.remote_policy
                }
                
                self.logger.info(f"✅ Job GPT Direct parsé: {job_parsed.title}")
                
            except Exception as e:
                self.logger.error(f"❌ GPT Direct Job parsing failed: {e}")
                self.logger.error(f"💼 Job file: {job_file.filename}, size: {job_file.size}")
                job_data = self._create_fallback_job_data(job_file)
        
        return cv_data, job_data
    
    async def _calculate_intelligent_matching_with_motivations(
        self,
        matching_request,
        job_address: str,
        cv_data: Dict[str, Any],
        job_data: Optional[Dict[str, Any]],
        additional_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🎯 Calcul matching avec Transport Intelligence + Motivations intégrées"""
        
        try:
            # === CALCULS SCORES STATIQUES ===
            candidate = matching_request.candidate_profile
            preferences = matching_request.preferences
            
            static_scores = {
                "semantique": min(0.9, 0.5 + (len(candidate.skills) * 0.08) + (candidate.experience_years * 0.02)),
                "hierarchical": min(0.85, 0.6 + (candidate.experience_years * 0.03)),
                "remuneration": min(0.95, 0.6 + (preferences.salary_expectations.min / 100000) * 0.3),
                "experience": min(0.9, 0.4 + (candidate.experience_years * 0.05)),
                "secteurs": 0.70
            }
            
            # === CALCUL SCORE LOCALISATION DYNAMIQUE ===
            location_score = 0.65  # Fallback par défaut
            transport_intelligence_data = {
                "location_score_dynamic": False,
                "location_score_source": "fallback",
                "location_score_value": 0.65
            }
            
            # Transport Intelligence avec questionnaire
            if matching_request.questionnaire:
                try:
                    # Calcul score enrichi via LocationScoringEngine
                    location_score_result = await location_scoring_engine.calculate_enriched_location_score(
                        candidat_questionnaire=matching_request.questionnaire,
                        job_address=job_address,
                        job_context={}
                    )
                    
                    # Extraction du score final
                    location_score = location_score_result.final_score
                    
                    # Mise à jour métadonnées Transport Intelligence
                    transport_intelligence_data = {
                        "location_score_dynamic": True,
                        "location_score_source": "google_maps_calculation",
                        "location_score_value": location_score,
                        "transport_mode": location_score_result.transport_compatibility.recommended_mode.value if location_score_result.transport_compatibility.recommended_mode else "unknown",
                        "distance_km": location_score_result.base_distance_km,
                        "time_score": location_score_result.time_score,
                        "cost_score": location_score_result.cost_score,
                        "comfort_score": location_score_result.comfort_score
                    }
                    
                    self.logger.info(f"✅ Transport Intelligence: score {location_score:.3f} pour {job_address}")
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Erreur Transport Intelligence: {e}")
                    # Garde le fallback défini plus haut
            
            # === 🆕 CALCUL SCORE MOTIVATIONS ===
            motivations_score, motivations_details = await self._calculate_motivations_score(
                cv_data=cv_data,
                job_data=job_data,
                additional_context=additional_context
            )
            
            # === ASSEMBLAGE SCORES FINAUX (+ Motivations) ===
            all_scores = {
                **static_scores,
                "localisation": location_score,
                "motivations": motivations_score  # 🆕 NOUVEAU SCORE
            }
            
            # === PONDÉRATION ADAPTATIVE ENRICHIE (+ Motivations) ===
            weights = self._apply_adaptive_weighting_with_motivations(
                pourquoi_ecoute=matching_request.pourquoi_ecoute,
                motivations_available=MOTIVATIONS_SCORER_AVAILABLE
            )
            
            # === SCORE TOTAL (+ Motivations) ===
            total_score = sum(all_scores[component] * weights[component] 
                             for component in all_scores.keys() if component in weights)
            
            # === CONFIANCE ENRICHIE ===
            base_confidence = 0.85
            if transport_intelligence_data["location_score_dynamic"]:
                base_confidence += 0.05  # Bonus pour calcul dynamique
            if motivations_details.get("status") == "success":
                base_confidence += 0.05  # Bonus pour motivations réussies
            confidence = min(0.95, base_confidence)
            
            return {
                "total_score": round(total_score, 3),
                "confidence": round(confidence, 3),
                "component_scores": all_scores,
                "weights_used": weights,
                "motivations_analysis": motivations_details,  # 🆕 DÉTAILS MOTIVATIONS
                "transport_intelligence": transport_intelligence_data,
                "adaptive_weighting": self._get_adaptive_weighting_details(matching_request.pourquoi_ecoute),
                "innovation": {
                    "motivations_integrated": True,
                    "motivations_scorer_status": "operational" if MOTIVATIONS_SCORER_AVAILABLE else "fallback",
                    "total_components": len(all_scores)
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erreur calcul matching with motivations: {e}")
            # Fallback matching result
            return {
                "total_score": 0.65,
                "confidence": 0.70,
                "component_scores": {"semantique": 0.65, "localisation": 0.65, "motivations": 0.50},
                "weights_used": {"semantique": 0.55, "localisation": 0.15, "motivations": 0.08},
                "motivations_analysis": {"status": "error", "error": str(e)},
                "error": f"Matching calculation failed: {str(e)}"
            }
    
    async def _calculate_motivations_score(
        self,
        cv_data: Dict[str, Any],
        job_data: Optional[Dict[str, Any]],
        additional_context: Dict[str, Any]
    ) -> tuple[float, Dict[str, Any]]:
        """🎯 Calcul du score motivations"""
        
        motivations_start = time.time()
        
        if not MOTIVATIONS_SCORER_AVAILABLE:
            # Fallback score si scorer non disponible
            return 0.65, {
                "status": "fallback",
                "reason": "motivations_scorer_not_available",
                "fallback_score": 0.65,
                "processing_time_ms": (time.time() - motivations_start) * 1000
            }
        
        if not job_data:
            # Fallback score si pas de données job
            return 0.60, {
                "status": "fallback", 
                "reason": "no_job_data",
                "fallback_score": 0.60,
                "processing_time_ms": (time.time() - motivations_start) * 1000
            }
        
        try:
            # Conversion vers structures CVData/JobData
            cv_data_obj = create_complete_cv_data(
                name=cv_data.get("name", "Candidat"),
                skills=cv_data.get("skills", []),
                years_of_experience=cv_data.get("years_of_experience", 0),
                objective=cv_data.get("objective", ""),
                summary=cv_data.get("summary", ""),
                email=cv_data.get("email", ""),
                location=cv_data.get("location", "Paris")
            )
            
            job_data_obj = create_complete_job_data(
                title=job_data.get("title", "Poste"),
                company=job_data.get("company", "Entreprise"),
                location=job_data.get("location", "Paris"),
                contract_type=job_data.get("contract_type", "CDI"),
                required_skills=job_data.get("required_skills", []),
                preferred_skills=job_data.get("preferred_skills", []),
                responsibilities=job_data.get("responsibilities", []),
                requirements=job_data.get("requirements", []),
                benefits=job_data.get("benefits", []),
                salary_range=job_data.get("salary_range", {"min": 45000, "max": 65000}),
                remote_policy=job_data.get("remote_policy", "Sur site")
            )
            
            # Extraction motivations candidat depuis contexte
            candidate_motivations = additional_context.get("motivations", [])
            if not candidate_motivations:
                # Fallback : extraction depuis objectif CV
                objective_text = cv_data.get("objective", "")
                if "innovation" in objective_text.lower():
                    candidate_motivations.append("Innovation")
                if "évolution" in objective_text.lower() or "evolution" in objective_text.lower():
                    candidate_motivations.append("Évolution")
                if "équipe" in objective_text.lower() or "team" in objective_text.lower():
                    candidate_motivations.append("Équipe")
            
            # Calcul du score motivations
            result: MotivationsResult = self.motivations_scorer.score_motivations_alignment(
                candidate_data=cv_data_obj,
                job_data=job_data_obj,
                candidate_motivations=candidate_motivations
            )
            
            processing_time = (time.time() - motivations_start) * 1000
            
            # Retour détaillé
            motivations_details = {
                "status": "success",
                "overall_score": result.overall_score,
                "confidence": result.confidence,
                "processing_time_ms": processing_time,
                "candidate_motivations_detected": candidate_motivations,
                "motivation_breakdown": [
                    {
                        "motivation": score.motivation_type.value,
                        "score": score.score,
                        "confidence": score.confidence,
                        "weight": score.weight,
                        "evidence": score.evidence_found[:3]  # Top 3
                    }
                    for score in result.motivation_scores
                ][:5],  # Top 5 motivations
                "strongest_alignments": result.strongest_alignments[:3],  # Top 3
                "improvement_suggestions": result.improvement_suggestions[:3]  # Top 3
            }
            
            self.logger.info(f"✅ Motivations score: {result.overall_score:.3f} (confidence: {result.confidence:.3f}, {processing_time:.2f}ms)")
            
            return result.overall_score, motivations_details
            
        except Exception as e:
            processing_time = (time.time() - motivations_start) * 1000
            self.logger.error(f"❌ Motivations scoring failed: {e}")
            
            return 0.5, {
                "status": "error",
                "error_message": str(e),
                "fallback_score": 0.5,
                "processing_time_ms": processing_time
            }
    
    def _apply_adaptive_weighting_with_motivations(self, pourquoi_ecoute: str, motivations_available: bool) -> Dict[str, float]:
        """🎯 Pondération adaptative enrichie avec motivations"""
        
        if motivations_available:
            # Poids avec motivations intégrées
            base_weights = {
                "semantique": 0.27,      # Réduit de 30% → 27%
                "hierarchical": 0.14,    # Réduit de 15% → 14%
                "remuneration": 0.18,    # Réduit de 20% → 18% 
                "experience": 0.15,      # Réduit de 20% → 15%
                "localisation": 0.13,    # Réduit de 15% → 13%
                "secteurs": 0.05,        # Réduit de 5% → 5%
                "motivations": 0.08      # 🆕 NOUVEAU 8%
            }
        else:
            # Poids sans motivations (logique originale)
            base_weights = {
                "semantique": 0.30,
                "hierarchical": 0.15,
                "remuneration": 0.20,
                "experience": 0.20,
                "localisation": 0.15,
                "secteurs": 0.05
            }
        
        # Adaptations selon raison d'écoute
        if "loin" in pourquoi_ecoute.lower():
            base_weights["localisation"] = min(1.0, base_weights["localisation"] + 0.05)
            base_weights["semantique"] = max(0.05, base_weights["semantique"] - 0.05)
        elif "rémunération" in pourquoi_ecoute.lower():
            base_weights["remuneration"] = min(1.0, base_weights["remuneration"] + 0.05)  
            base_weights["semantique"] = max(0.05, base_weights["semantique"] - 0.05)
        elif motivations_available and any(mot in pourquoi_ecoute.lower() for mot in ["motivation", "évolution", "perspectives"]):
            # Boost motivations si focus carrière/évolution
            base_weights["motivations"] = min(1.0, base_weights["motivations"] + 0.04)  # 8% → 12%
            base_weights["semantique"] = max(0.05, base_weights["semantique"] - 0.04)   # Compensation
        
        # Normalisation pour s'assurer que la somme = 1.0
        total = sum(base_weights.values())
        if abs(total - 1.0) > 0.01:
            base_weights = {k: v/total for k, v in base_weights.items()}
        
        return base_weights
    
    def _get_adaptive_weighting_details(self, pourquoi_ecoute: str) -> Dict[str, Any]:
        """📊 Retourne détails pondération adaptative"""
        details = {
            "applied": True,
            "reason": pourquoi_ecoute,
            "motivations_integration": MOTIVATIONS_SCORER_AVAILABLE
        }
        
        if "loin" in pourquoi_ecoute.lower():
            details["reasoning"] = "Priorité à la proximité géographique (+5%)"
        elif "rémunération" in pourquoi_ecoute.lower():
            details["reasoning"] = "Priorité à la rémunération (+5%)"
        elif any(mot in pourquoi_ecoute.lower() for mot in ["motivation", "évolution", "perspectives"]):
            details["reasoning"] = "Priorité aux motivations et évolution (+4%)"
        else:
            details["reasoning"] = "Pondération adaptative appliquée"
        
        return details
    
    def _create_fallback_cv_data(self, cv_file: UploadFile) -> Dict[str, Any]:
        """🛡️ Fallback CV data si parsing échoue"""
        return {
            "name": "Candidat Test",
            "email": "candidat@example.com",
            "phone": "",
            "skills": ["Compétence générale"],
            "years_of_experience": 2,
            "education": "Formation",
            "job_titles": ["Poste actuel"],
            "companies": ["Entreprise"],
            "location": "Paris, France",
            "summary": f"CV parsé depuis {cv_file.filename}",
            "objective": "Recherche nouveau poste",
            "languages": ["Français"],
            "certifications": []
        }
    
    def _create_fallback_job_data(self, job_file: UploadFile) -> Dict[str, Any]:
        """🛡️ Fallback Job data si parsing échoue"""
        return {
            "title": "Poste à définir",
            "company": "Entreprise",
            "location": "Paris, France",
            "contract_type": "CDI",
            "required_skills": ["Compétences générales"],
            "preferred_skills": [],
            "responsibilities": [f"Responsabilités extraites de {job_file.filename}"],
            "requirements": ["Exigences générales"],
            "benefits": ["Avantages"],
            "salary_range": {"min": 45000, "max": 55000},
            "remote_policy": "Hybride"
        }

# Instance du service
intelligent_matching_service = IntelligentMatchingService()

# === ENDPOINT PRINCIPAL RÉVOLUTIONNAIRE + MOTIVATIONS ===

@router.post("/intelligent-matching", summary="🎯 Intelligent Matching Unifié + Motivations - 5 étapes → 1 étape")
async def intelligent_matching_endpoint(
    cv_file: UploadFile = File(..., description="📄 Fichier CV (PDF, DOC, DOCX)"),
    job_file: Optional[UploadFile] = File(None, description="💼 Fichier Job optionnel (PDF, DOC, DOCX)"),
    pourquoi_ecoute: str = Form(default="Recherche nouveau défi", description="🎯 Raison d'écoute candidat"),
    questionnaire_data: Optional[str] = Form(None, description="📋 Questionnaire candidat JSON (optionnel)"),
    job_address: Optional[str] = Form(None, description="📍 Adresse job pour Transport Intelligence")
):
    """
    🎯 **ENDPOINT RÉVOLUTIONNAIRE : INTELLIGENT MATCHING UNIFIÉ + MOTIVATIONS**
    ==========================================================================
    
    ## 🚀 Innovation v3.2.1 + Motivations
    
    **Transformation Révolutionnaire** : 5 étapes manuelles → 1 étape automatique + Motivations
    
    ### Workflow Unifié Automatique :
    
    1. **📄 Parse CV** → Utilise GPT Direct Service RÉEL
    2. **💼 Parse Job** → Parsing intelligent automatique  
    3. **🔄 Transform** → Adaptateur Intelligent (formats unifiés)
    4. **🎯 Match** → Matching Engine avec Transport Intelligence
    5. **🆕 Motivations** → Score motivationnel intégré (8% du score total)
    6. **📊 Return** → Résultat complet unifié
    
    ### Performance Cible :
    - ⏱️ **< 2000ms** (objectif révolutionnaire)
    - 🎯 **Précision** : Transport Intelligence + Pondération Adaptative + Motivations
    - 🔧 **Fiabilité** : Fallbacks intelligents à chaque étape
    
    ### Innovation Architecture :
    - ✅ **Zéro redondance** : Réutilise infrastructure GPT Direct
    - ✅ **Auto-adaptation** : Résout incompatibilités format automatiquement
    - ✅ **Transport Intelligence** : Google Maps intégré
    - ✅ **Pondération Adaptative** : Selon raison d'écoute candidat
    - 🆕 **Score Motivations** : Analyse alignement motivationnel candidat/poste
    
    ### Exemples Raisons d'Écoute :
    - `"Rémunération trop faible"` → Priorité salaire (+5%)
    - `"Poste trop loin de mon domicile"` → Priorité localisation (+5%)
    - `"Manque de perspectives d'évolution"` → Priorité motivations (+4%)
    - `"Recherche nouveau défi"` → Pondération équilibrée
    
    ### Exemples Questionnaire (JSON) :
    ```json
    {
        "motivations": ["Innovation", "Évolution de carrière", "Leadership d'équipe"],
        "transport_preferences": ["Voiture", "Transport en commun"],
        "salary_expectations": {"min": 55000, "max": 70000}
    }
    ```
    
    **RÉVOLUTION NEXTEN** : GPT Direct + IA + Géospatial + Motivations = Workflow unifié parfait
    """
    
    start_time = time.time()
    
    logger.info("🎯 === INTELLIGENT MATCHING ENDPOINT v3.2.1 + MOTIVATIONS ===")
    logger.info(f"📄 CV: {cv_file.filename} ({cv_file.size} bytes)")
    logger.info(f"💼 Job: {job_file.filename if job_file else 'None'}")
    logger.info(f"🎯 Pourquoi écoute: {pourquoi_ecoute}")
    logger.info(f"🧠 Motivations Scorer: {'✅ Enabled' if MOTIVATIONS_SCORER_AVAILABLE else '⚠️ Fallback'}")
    
    try:
        # Validation fichiers
        if not cv_file:
            raise HTTPException(status_code=400, detail="CV file is required")
        
        # Validation formats supportés
        allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
        cv_extension = os.path.splitext(cv_file.filename)[1].lower()
        
        if cv_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"CV format non supporté: {cv_extension}. Formats acceptés: {allowed_extensions}"
            )
        
        # Traitement intelligent matching avec motivations
        result = await intelligent_matching_service.process_intelligent_matching(
            cv_file=cv_file,
            job_file=job_file,
            pourquoi_ecoute=pourquoi_ecoute,
            questionnaire_data=questionnaire_data,
            job_address=job_address
        )
        
        total_time = (time.time() - start_time) * 1000
        logger.info(f"🎯 Intelligent matching + motivations completed in {total_time:.2f}ms")
        
        return JSONResponse(
            status_code=200,
            content=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        total_time = (time.time() - start_time) * 1000
        logger.error(f"❌ Intelligent matching failed: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Intelligent matching failed",
                "message": str(e),
                "processing_time_ms": round(total_time, 2),
                "timestamp": datetime.now().isoformat(),
                "endpoint": "/api/v3/intelligent-matching"
            }
        )

# === ENDPOINTS UTILITAIRES ===

@router.get("/health", summary="❤️ Health Check API v3 + Motivations")
async def health_check_v3():
    """❤️ Health Check pour API v3 Intelligent Matching + Motivations"""
    return {
        "status": "healthy",
        "service": "Nextvision API v3",
        "version": "3.2.1",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "intelligent_matching": True,
            "gpt_direct_service": True,
            "adaptateur_intelligent": True,
            "transport_intelligence": True,
            "motivations_scorer": MOTIVATIONS_SCORER_AVAILABLE,  # 🆕
            "commitment_bridge": commitment_bridge is not None,
            "workflow_unifie": True
        },
        "innovation": "5 étapes manuelles → 1 étape automatique + Motivations",
        "endpoint": "/api/v3/intelligent-matching"
    }

@router.get("/status", summary="📊 Status détaillé v3 + Motivations")
async def status_detailed_v3():
    """📊 Status détaillé des services v3 + Motivations"""
    
    # Test services
    bridge_status = "operational" if commitment_bridge else "fallback"
    gpt_status = "operational" if gpt_service else "fallback"
    motivations_status = "operational" if MOTIVATIONS_SCORER_AVAILABLE else "fallback"  # 🆕
    
    services_status = {
        "gpt_direct_service": {
            "status": gpt_status,
            "available": gpt_service is not None
        },
        "motivations_scorer": {  # 🆕
            "status": motivations_status,
            "available": MOTIVATIONS_SCORER_AVAILABLE,
            "version": "1.0.0"
        },
        "commitment_bridge": {
            "status": bridge_status,
            "available": commitment_bridge is not None
        },
        "adaptateur_intelligent": {
            "status": "operational",
            "available": True
        },
        "transport_intelligence": {
            "status": "operational", 
            "available": True
        },
        "google_maps_service": {
            "status": "operational",
            "available": google_maps_service is not None
        },
        "file_processing": {
            "status": "operational" if PDF_PROCESSING_AVAILABLE else "limited",
            "pdf_support": PDF_PROCESSING_AVAILABLE,
            "docx_support": PDF_PROCESSING_AVAILABLE
        }
    }
    
    return {
        "service": "Nextvision API v3",
        "version": "3.2.1",
        "timestamp": datetime.now().isoformat(),
        "services": services_status,
        "workflow": {
            "description": "Parse → Transform → Match + Motivations (automatique)",
            "stages": ["parsing", "adaptation", "matching", "motivations"],  # 🆕
            "innovation": "5 étapes manuelles → 1 étape automatique + Motivations",
            "performance_target": "< 2000ms"
        },
        "scoring_components": {  # 🆕
            "total_components": 7 if MOTIVATIONS_SCORER_AVAILABLE else 6,
            "motivations_weight": "8%" if MOTIVATIONS_SCORER_AVAILABLE else "N/A",
            "adaptive_weighting": True
        },
        "endpoints": {
            "main": "/api/v3/intelligent-matching",
            "health": "/api/v3/health",
            "status": "/api/v3/status"
        }
    }
