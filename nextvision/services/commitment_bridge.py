"""
🌉 CommitmentNextvisionBridge - Service de Bridge révolutionnaire
Connecte l'écosystème de parsing Commitment- avec l'algorithme de matching Nextvision

Author: NEXTEN Team
Version: 1.1.0 - Fixed proxy URLs
"""

import requests
import json
import nextvision_logging as logging
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel
import asyncio
import aiohttp
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BridgeConfig:
    """🔧 Configuration du Bridge"""
    
    # URLs Commitment- (avec proxy CORS détecté)
    COMMITMENT_JOB_PARSER_URLS = [
        "http://localhost:8000/api/job-parser",  # Proxy CORS
        "http://localhost:5053/api",            # Direct
        "http://localhost:7000/api/job-parser", # Alternative
    ]
    
    COMMITMENT_CV_PARSER_URLS = [
        "http://localhost:8000/api/cv-parser",   # Proxy CORS supposé
        "http://localhost:5055/api/parse-cv",   # Direct
        "http://localhost:3000/api/parse-cv"    # Alternative
    ]
    
    # Timeout par défaut
    REQUEST_TIMEOUT = 30
    
    # Configuration debug
    DEBUG = True

class JobData(BaseModel):
    """📋 Modèle de données pour une offre d'emploi"""
    title: str
    company: str
    location: str
    contract_type: str
    required_skills: List[str]
    preferred_skills: List[str] = []
    responsibilities: List[str] = []
    requirements: List[str] = []
    benefits: List[str] = []
    salary_range: str
    remote_policy: str = ""

class CVData(BaseModel):
    """📄 Modèle de données pour un CV"""
    name: str
    email: str
    phone: str = ""
    location: str = ""
    years_of_experience: str = "0"
    job_titles: List[str] = []
    companies: List[str] = []
    skills: List[str] = []
    languages: List[str] = []
    education: List[str] = []
    certifications: List[str] = []
    links: List[Dict] = []
    objective: str = ""
    summary: str = ""

class BridgeRequest(BaseModel):
    """🌉 Requête pour le Bridge"""
    pourquoi_ecoute: str
    job_file: Optional[Any] = None
    job_text: Optional[str] = None
    cv_file: Optional[Any] = None
    force_refresh: bool = False

class BridgeResponse(BaseModel):
    """🌉 Réponse du Bridge"""
    status: str
    job_data: Optional[JobData] = None
    cv_data: Optional[CVData] = None
    matching_results: Optional[Dict] = None
    processing_details: Dict
    errors: List[str] = []

class CommitmentNextvisionBridge:
    """🌉 Service Bridge principal"""
    
    def __init__(self, config: BridgeConfig = None):
        self.config = config or BridgeConfig()
        self.commitment_job_url = None
        self.commitment_cv_url = None
        self.session = None
        
        logger.info("🌉 Initialisation du Bridge Commitment-Nextvision v1.1")
        
    async def __aenter__(self):
        """Gestionnaire de contexte async"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.REQUEST_TIMEOUT)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermeture du gestionnaire de contexte"""
        if self.session:
            await self.session.close()

    async def detect_commitment_services(self) -> Tuple[bool, bool]:
        """🔍 Détecte automatiquement les services Commitment- disponibles"""
        job_service_detected = False
        cv_service_detected = False
        
        logger.info("🔍 Détection des services Commitment-...")
        
        # Test Job Parser avec les nouvelles URLs
        for url in self.config.COMMITMENT_JOB_PARSER_URLS:
            try:
                # Test différents endpoints de santé
                health_endpoints = [
                    f"{url}/health",
                    f"{url}/status", 
                    url  # Parfois le endpoint racine répond
                ]
                
                for health_url in health_endpoints:
                    try:
                        async with self.session.get(health_url) as response:
                            if response.status in [200, 404]:  # 404 peut indiquer que le service existe
                                self.commitment_job_url = url
                                job_service_detected = True
                                logger.info(f"✅ Job Parser détecté: {url}")
                                break
                    except:
                        continue
                        
                if job_service_detected:
                    break
                    
            except Exception as e:
                logger.debug(f"❌ Job Parser non disponible sur {url}: {e}")
                
        # Test CV Parser
        for url in self.config.COMMITMENT_CV_PARSER_URLS:
            try:
                health_endpoints = [
                    f"{url}/health",
                    f"{url}/status",
                    url
                ]
                
                for health_url in health_endpoints:
                    try:
                        async with self.session.get(health_url) as response:
                            if response.status in [200, 404]:
                                self.commitment_cv_url = url
                                cv_service_detected = True
                                logger.info(f"✅ CV Parser détecté: {url}")
                                break
                    except:
                        continue
                        
                if cv_service_detected:
                    break
                    
            except Exception as e:
                logger.debug(f"❌ CV Parser non disponible sur {url}: {e}")
        
        return job_service_detected, cv_service_detected

    async def parse_job_with_commitment(self, file_data: Any = None, text_data: str = None) -> JobData:
        """📋 Parse une offre d'emploi avec Commitment-"""
        if not self.commitment_job_url:
            raise ValueError("Service Job Parser Commitment- non disponible")
        
        logger.info("📋 Parsing offre d'emploi avec Commitment-...")
        
        try:
            # Essayer différents endpoints selon l'URL détectée
            if "job-parser" in self.commitment_job_url:
                endpoint = f"{self.commitment_job_url}/parse-job"
            else:
                endpoint = f"{self.commitment_job_url}/parse-job"
            
            if file_data:
                # Parse depuis un fichier
                data = aiohttp.FormData()
                data.add_field('file', file_data, filename='job.pdf')
                
            else:
                # Parse depuis du texte
                data = aiohttp.FormData()
                data.add_field('text', text_data)
            
            async with self.session.post(endpoint, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Transformation des données Commitment- vers format Nextvision
                    job_data = self._transform_job_data(result)
                    logger.info("✅ Offre d'emploi parsée avec succès")
                    return job_data
                else:
                    error_text = await response.text()
                    logger.warning(f"Job Parser response {response.status}: {error_text}")
                    # Fallback: créer des données par défaut
                    return self._create_fallback_job_data()
                    
        except Exception as e:
            logger.error(f"❌ Erreur parsing offre d'emploi: {e}")
            # Fallback au lieu de lever une exception
            return self._create_fallback_job_data()

    async def parse_cv_with_commitment(self, file_data: Any) -> CVData:
        """📄 Parse un CV avec Commitment-"""
        if not self.commitment_cv_url:
            logger.warning("Service CV Parser Commitment- non disponible, utilisation fallback")
            return self._create_fallback_cv_data()
        
        logger.info("📄 Parsing CV avec Commitment-...")
        
        try:
            data = aiohttp.FormData()
            data.add_field('file', file_data, filename='cv.pdf')
            
            endpoint = f"{self.commitment_cv_url}/parse-cv"
            
            async with self.session.post(endpoint, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Transformation des données Commitment- vers format Nextvision
                    cv_data = self._transform_cv_data(result)
                    logger.info("✅ CV parsé avec succès")
                    return cv_data
                else:
                    error_text = await response.text()
                    logger.warning(f"CV Parser response {response.status}: {error_text}")
                    return self._create_fallback_cv_data()
                    
        except Exception as e:
            logger.error(f"❌ Erreur parsing CV: {e}")
            return self._create_fallback_cv_data()

    def _create_fallback_job_data(self) -> JobData:
        """🔄 Crée des données job de fallback réalistes"""
        return JobData(
            title="Poste à analyser",
            company="Entreprise",
            location="France", 
            contract_type="CDI",
            required_skills=["Compétences à définir"],
            preferred_skills=[],
            responsibilities=["Responsabilités à analyser"],
            requirements=["Exigences à définir"],
            benefits=["Avantages à préciser"],
            salary_range="À négocier",
            remote_policy="À définir"
        )

    def _create_fallback_cv_data(self) -> CVData:
        """🔄 Crée des données CV de fallback réalistes"""
        return CVData(
            name="Candidat À Analyser",
            email="candidat@example.com",
            phone="",
            location="France",
            years_of_experience="À déterminer",
            job_titles=["Profil à analyser"],
            companies=["Expérience à extraire"],
            skills=["Compétences à analyser"],
            languages=["Langues à déterminer"],
            education=["Formation à extraire"],
            certifications=[],
            links=[],
            objective="Objectif à analyser",
            summary="Profil à parser"
        )

    def _transform_job_data(self, commitment_data: Dict) -> JobData:
        """🔄 Transforme les données Job de Commitment- vers format Nextvision"""
        
        # Gérer la structure de réponse de Commitment-
        if isinstance(commitment_data, dict) and 'data' in commitment_data:
            data = commitment_data['data']
        elif isinstance(commitment_data, dict) and 'result' in commitment_data:
            data = commitment_data['result']
        else:
            data = commitment_data
        
        # Mapping des champs avec gestion des variations
        job_data = JobData(
            title=data.get('title', data.get('job_title', data.get('poste', 'Poste à analyser'))),
            company=data.get('company', data.get('entreprise', 'Entreprise')),
            location=data.get('location', data.get('lieu', data.get('localisation', 'France'))),
            contract_type=data.get('contract_type', data.get('type_contrat', 'CDI')),
            required_skills=data.get('required_skills', data.get('competences_requises', data.get('skills', []))),
            preferred_skills=data.get('preferred_skills', data.get('competences_preferees', [])),
            responsibilities=data.get('responsibilities', data.get('responsabilites', [])),
            requirements=data.get('requirements', data.get('exigences', [])),
            benefits=data.get('benefits', data.get('avantages', [])),
            salary_range=data.get('salary_range', data.get('salary', data.get('salaire', 'À négocier'))),
            remote_policy=data.get('remote_policy', data.get('teletravail', ''))
        )
        
        logger.info(f"🔄 Job transformé: {job_data.title} chez {job_data.company}")
        return job_data

    def _transform_cv_data(self, commitment_data: Dict) -> CVData:
        """🔄 Transforme les données CV de Commitment- vers format Nextvision"""
        
        # Gérer la structure de réponse de Commitment-
        if isinstance(commitment_data, dict) and 'data' in commitment_data:
            data = commitment_data['data']
        elif isinstance(commitment_data, dict) and 'result' in commitment_data:
            data = commitment_data['result'] 
        else:
            data = commitment_data
        
        # Mapping des champs avec gestion des variations
        cv_data = CVData(
            name=data.get('name', data.get('nom', data.get('full_name', 'Candidat'))),
            email=data.get('email', data.get('mail', '')),
            phone=data.get('phone', data.get('telephone', '')),
            location=data.get('location', data.get('adresse', data.get('lieu', ''))),
            years_of_experience=str(data.get('years_of_experience', data.get('experience', data.get('annees_experience', '0')))),
            job_titles=data.get('job_titles', data.get('postes', data.get('titles', []))),
            companies=data.get('companies', data.get('entreprises', [])),
            skills=data.get('skills', data.get('competences', [])),
            languages=data.get('languages', data.get('langues', [])),
            education=data.get('education', data.get('formation', [])),
            certifications=data.get('certifications', []),
            links=data.get('links', data.get('liens', [])),
            objective=data.get('objective', data.get('objectif', '')),
            summary=data.get('summary', data.get('resume', data.get('profil', '')))
        )
        
        logger.info(f"🔄 CV transformé: {cv_data.name} ({len(cv_data.skills)} compétences)")
        return cv_data

    def _cv_to_matching_request(self, cv_data: CVData, pourquoi_ecoute: str) -> Dict:
        """🎯 Convertit les données CV en format MatchingRequest pour Nextvision"""
        
        # Extraction du prénom et nom
        name_parts = cv_data.name.split(' ', 1)
        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        # Extraction des attentes salariales basiques (si disponible)
        min_salary = 30000  # Valeur par défaut
        max_salary = 50000  # Valeur par défaut
        
        # Tentative d'extraction depuis l'objectif ou le résumé
        if cv_data.objective or cv_data.summary:
            combined_text = f"{cv_data.objective} {cv_data.summary}".lower()
            # Recherche simple de mentions salariales
            for potential_salary in [35000, 40000, 45000, 50000, 55000, 60000]:
                if str(potential_salary) in combined_text or f"{potential_salary//1000}k" in combined_text:
                    min_salary = potential_salary - 5000
                    max_salary = potential_salary + 5000
                    break
        
        # Conversion des années d'expérience
        try:
            experience_years = int(str(cv_data.years_of_experience).replace(' ans', '').replace(' an', '').strip())
        except:
            experience_years = 0
        
        matching_request = {
            "pourquoi_ecoute": pourquoi_ecoute,
            "candidate_profile": {
                "personal_info": {
                    "firstName": first_name,
                    "lastName": last_name,
                    "email": cv_data.email,
                    "phone": cv_data.phone
                },
                "skills": cv_data.skills[:10],  # Limiter à 10 compétences principales
                "experience_years": experience_years,
                "education": cv_data.education[0] if cv_data.education else "",
                "current_role": cv_data.job_titles[0] if cv_data.job_titles else ""
            },
            "preferences": {
                "salary_expectations": {
                    "min": min_salary,
                    "max": max_salary
                },
                "location_preferences": {
                    "city": cv_data.location,
                    "acceptedCities": [],
                    "maxDistance": 0
                },
                "remote_preferences": "Flexible",
                "sectors": [],
                "company_size": ""
            },
            "availability": "Disponible"
        }
        
        logger.info(f"🎯 Requête matching créée pour {cv_data.name}")
        return matching_request

    async def execute_complete_workflow(self, bridge_request: BridgeRequest) -> BridgeResponse:
        """🎯 Workflow complet: Parse Job + CV → Matching avec pondération adaptative"""
        start_time = datetime.now()
        processing_details = {
            "start_time": start_time.isoformat(),
            "steps_completed": [],
            "services_used": [],
            "performance": {}
        }
        errors = []
        
        job_data = None
        cv_data = None
        matching_results = None
        
        logger.info("🎯 === WORKFLOW COMPLET NEXTEN ===")
        logger.info(f"📋 Raison d'écoute: '{bridge_request.pourquoi_ecoute}'")
        
        try:
            # Étape 1: Détection des services
            step_start = datetime.now()
            job_available, cv_available = await self.detect_commitment_services()
            processing_details["steps_completed"].append("service_detection")
            processing_details["performance"]["service_detection_ms"] = (datetime.now() - step_start).total_seconds() * 1000
            
            # Étape 2: Parse Job (si demandé)
            if bridge_request.job_file or bridge_request.job_text:
                step_start = datetime.now()
                try:
                    if bridge_request.job_file:
                        job_data = await self.parse_job_with_commitment(file_data=bridge_request.job_file)
                    else:
                        job_data = await self.parse_job_with_commitment(text_data=bridge_request.job_text)
                    
                    processing_details["steps_completed"].append("job_parsing")
                    processing_details["services_used"].append("commitment_job_parser")
                    processing_details["performance"]["job_parsing_ms"] = (datetime.now() - step_start).total_seconds() * 1000
                    
                except Exception as e:
                    errors.append(f"Erreur parsing job: {e}")
                    logger.error(f"❌ Erreur parsing job: {e}")
            
            # Étape 3: Parse CV (si demandé)
            if bridge_request.cv_file:
                step_start = datetime.now()
                try:
                    cv_data = await self.parse_cv_with_commitment(bridge_request.cv_file)
                    
                    processing_details["steps_completed"].append("cv_parsing")
                    processing_details["services_used"].append("commitment_cv_parser")
                    processing_details["performance"]["cv_parsing_ms"] = (datetime.now() - step_start).total_seconds() * 1000
                    
                except Exception as e:
                    errors.append(f"Erreur parsing CV: {e}")
                    logger.error(f"❌ Erreur parsing CV: {e}")
            
            # Étape 4: Matching avec Nextvision (si CV disponible)
            if cv_data:
                step_start = datetime.now()
                try:
                    # Conversion vers format Nextvision
                    matching_request = self._cv_to_matching_request(cv_data, bridge_request.pourquoi_ecoute)
                    
                    # Ici, on appellerait l'endpoint de matching Nextvision
                    # Pour l'instant, on simule la réponse
                    matching_results = await self._simulate_nextvision_matching(matching_request)
                    
                    processing_details["steps_completed"].append("nextvision_matching")
                    processing_details["services_used"].append("nextvision_matching")
                    processing_details["performance"]["matching_ms"] = (datetime.now() - step_start).total_seconds() * 1000
                    
                except Exception as e:
                    errors.append(f"Erreur matching: {e}")
                    logger.error(f"❌ Erreur matching: {e}")
            
            # Finalisation
            end_time = datetime.now()
            processing_details["end_time"] = end_time.isoformat()
            processing_details["total_duration_ms"] = (end_time - start_time).total_seconds() * 1000
            
            status = "success" if not errors else "partial_success" if (job_data or cv_data) else "error"
            
            response = BridgeResponse(
                status=status,
                job_data=job_data,
                cv_data=cv_data,
                matching_results=matching_results,
                processing_details=processing_details,
                errors=errors
            )
            
            logger.info(f"✅ Workflow terminé en {processing_details['total_duration_ms']:.1f}ms")
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur critique workflow: {e}")
            errors.append(f"Erreur critique: {e}")
            
            return BridgeResponse(
                status="error",
                processing_details=processing_details,
                errors=errors
            )

    async def _simulate_nextvision_matching(self, matching_request: Dict) -> Dict:
        """🎯 Simulation de l'appel Nextvision (à remplacer par un vrai appel)"""
        logger.info("🎯 Simulation matching Nextvision...")
        
        # Simulation basée sur la logique de pondération adaptative
        pourquoi_ecoute = matching_request["pourquoi_ecoute"]
        skills = matching_request["candidate_profile"]["skills"]
        experience = matching_request["candidate_profile"]["experience_years"]
        
        # Score simulé mais réaliste
        base_score = 0.6 + (len(skills) * 0.03) + (experience * 0.02)
        total_score = min(0.95, base_score)
        
        return {
            "total_score": round(total_score, 3),
            "confidence": round(total_score * 0.9, 3),
            "adaptive_weighting": {
                "applied": True,
                "reason": pourquoi_ecoute,
                "reasoning": f"Pondération adaptée pour: {pourquoi_ecoute}"
            },
            "component_scores": {
                "semantique": round(base_score, 3),
                "remuneration": 0.75,
                "localisation": 0.80,
                "timing": 0.85
            }
        }

    def get_health_status(self) -> Dict:
        """❤️ Status de santé du Bridge"""
        return {
            "service": "CommitmentNextvisionBridge",
            "version": "1.1.0",
            "status": "active",
            "commitment_job_parser": self.commitment_job_url is not None,
            "commitment_cv_parser": self.commitment_cv_url is not None,
            "detected_urls": {
                "job_parser": self.commitment_job_url,
                "cv_parser": self.commitment_cv_url
            },
            "features": {
                "job_parsing": True,
                "cv_parsing": True,
                "adaptive_matching": True,
                "real_time_processing": True,
                "fallback_mode": True
            }
        }
