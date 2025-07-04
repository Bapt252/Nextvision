"""
🌉 Commitment-Nextvision Bridge Service
Service passerelle pour connecter les parsers de Commitment- à l'algorithme de matching Nextvision

Author: NEXTEN Team
Version: 1.0.0
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
import time
import json

# Configuration du logging
logger = logging.getLogger(__name__)


class CommitmentServiceType(Enum):
    """Types de services Commitment- disponibles"""
    CV_PARSER = "cv_parser"
    JOB_PARSER = "job_parser"


@dataclass
class CommitmentConfig:
    """Configuration pour se connecter aux services Commitment-"""
    base_url: str
    cv_parser_port: int = 3001  # Port par défaut du CV Parser (Node.js)
    job_parser_port: int = 5053  # Port par défaut du Job Parser (Python)
    timeout: int = 30
    api_key: Optional[str] = None
    max_retries: int = 3


class CommitmentNextvisionBridge:
    """
    🌉 Service Bridge Principal
    
    Connecte les parsers de Commitment- (CV + Job) à l'algorithme 
    de pondération adaptative de Nextvision
    """
    
    def __init__(self, config: CommitmentConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        
        # URLs des services
        self.cv_parser_url = f"{config.base_url}:{config.cv_parser_port}"
        self.job_parser_url = f"{config.base_url}:{config.job_parser_port}"
        
        logger.info(f"🌉 Bridge initialisé")
        logger.info(f"📄 CV Parser: {self.cv_parser_url}")
        logger.info(f"💼 Job Parser: {self.job_parser_url}")
    
    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """🔍 Vérification de la santé des services Commitment-"""
        results = {}
        
        # Test CV Parser
        try:
            cv_health = await self._call_cv_parser_health()
            results["cv_parser"] = {
                "status": "healthy" if cv_health else "unhealthy",
                "url": self.cv_parser_url,
                "details": cv_health
            }
        except Exception as e:
            results["cv_parser"] = {
                "status": "error",
                "url": self.cv_parser_url,
                "error": str(e)
            }
        
        # Test Job Parser
        try:
            job_health = await self._call_job_parser_health()
            results["job_parser"] = {
                "status": "healthy" if job_health else "unhealthy", 
                "url": self.job_parser_url,
                "details": job_health
            }
        except Exception as e:
            results["job_parser"] = {
                "status": "error",
                "url": self.job_parser_url,
                "error": str(e)
            }
        
        return {
            "bridge_status": "operational",
            "services": results,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    
    async def _call_cv_parser_health(self) -> Dict[str, Any]:
        """Appel santé CV Parser"""
        url = f"{self.cv_parser_url}/api/v2/parse/cv/stats"
        
        headers = {}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        
        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"CV Parser health check failed: {response.status}")
    
    async def _call_job_parser_health(self) -> Dict[str, Any]:
        """Appel santé Job Parser"""
        url = f"{self.job_parser_url}/health"
        
        headers = {}
        if self.config.api_key:
            headers["X-API-Key"] = self.config.api_key
        
        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Job Parser health check failed: {response.status}")
    
    async def parse_cv_with_commitment(self, cv_file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        📄 Parse CV via Commitment- CV Parser
        
        Args:
            cv_file_data: Données binaires du CV
            filename: Nom du fichier
            
        Returns:
            Dict contenant les données parsées du CV
        """
        logger.info(f"📄 Parsing CV via Commitment-: {filename}")
        
        # Préparer les données multipart
        data = aiohttp.FormData()
        data.add_field('cv', cv_file_data, filename=filename, content_type='application/octet-stream')
        
        headers = {}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        
        url = f"{self.cv_parser_url}/api/v2/parse/cv/upload"
        
        for attempt in range(self.config.max_retries):
            try:
                async with self.session.post(url, data=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"✅ CV parsé avec succès: {filename}")
                        return self._format_cv_data(result)
                    else:
                        error_text = await response.text()
                        raise Exception(f"CV parsing failed: {response.status} - {error_text}")
                        
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    logger.error(f"❌ Échec parsing CV après {self.config.max_retries} tentatives: {e}")
                    raise
                else:
                    logger.warning(f"⚠️ Tentative {attempt + 1} échouée, retry: {e}")
                    await asyncio.sleep(2 ** attempt)  # Backoff exponentiel
    
    async def parse_job_with_commitment(self, job_file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        💼 Parse Job via Commitment- Job Parser
        
        Args:
            job_file_data: Données binaires de l'offre d'emploi
            filename: Nom du fichier
            
        Returns:
            Dict contenant les données parsées de l'offre d'emploi
        """
        logger.info(f"💼 Parsing Job via Commitment-: {filename}")
        
        # Étape 1: Mettre en queue le job
        data = aiohttp.FormData()
        data.add_field('file', job_file_data, filename=filename, content_type='application/octet-stream')
        data.add_field('priority', 'premium')  # Priorité élevée pour le bridge
        
        headers = {}
        if self.config.api_key:
            headers["X-API-Key"] = self.config.api_key
        
        queue_url = f"{self.job_parser_url}/api/queue"
        
        # Mise en queue
        async with self.session.post(queue_url, data=data, headers=headers) as response:
            if response.status == 202:
                queue_result = await response.json()
                job_id = queue_result["job_id"]
                logger.info(f"📋 Job mis en queue: {job_id}")
            else:
                error_text = await response.text()
                raise Exception(f"Job queue failed: {response.status} - {error_text}")
        
        # Étape 2: Attendre le résultat
        result_url = f"{self.job_parser_url}/api/result/{job_id}"
        
        for attempt in range(30):  # Attendre jusqu'à 30 secondes
            await asyncio.sleep(1)
            
            async with self.session.get(result_url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    if result["status"] == "done":
                        logger.info(f"✅ Job parsé avec succès: {filename}")
                        return self._format_job_data(result["result"])
                    elif result["status"] == "failed":
                        raise Exception(f"Job parsing failed: {result.get('error', 'Unknown error')}")
                    elif result["status"] in ["running", "pending"]:
                        continue  # Continuer à attendre
                    
        raise Exception(f"Job parsing timeout after 30 seconds for {filename}")
    
    def _format_cv_data(self, raw_cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """📊 Formate les données CV pour Nextvision"""
        try:
            data = raw_cv_data.get("data", {})
            
            # Extraction des informations personnelles
            personal = data.get("personal", {})
            
            # Extraction des compétences
            skills_data = data.get("skills", {})
            all_skills = []
            if isinstance(skills_data, dict):
                all_skills.extend(skills_data.get("technical", []))
                all_skills.extend(skills_data.get("soft", []))
            
            # Extraction de l'expérience
            experience_data = data.get("experience", [])
            experience_years = 0
            if experience_data:
                # Calculer les années d'expérience approximatives
                experience_years = len(experience_data) * 2  # Estimation simple
            
            # Extraction de l'éducation
            education_data = data.get("education", [])
            education = ""
            if education_data:
                education = education_data[0].get("degree", "") if isinstance(education_data[0], dict) else str(education_data[0])
            
            formatted_data = {
                "personal_info": {
                    "firstName": personal.get("firstName", ""),
                    "lastName": personal.get("lastName", ""),
                    "email": personal.get("email", ""),
                    "phone": personal.get("phone", "")
                },
                "skills": all_skills,
                "experience_years": experience_years,
                "education": education,
                "current_role": experience_data[0].get("position", "") if experience_data else "",
                "raw_data": data  # Garder les données brutes pour debug
            }
            
            logger.info(f"📊 CV formaté: {len(all_skills)} compétences, {experience_years} ans d'expérience")
            return formatted_data
            
        except Exception as e:
            logger.error(f"❌ Erreur formatage CV: {e}")
            # Retourner une structure minimale en cas d'erreur
            return {
                "personal_info": {
                    "firstName": "",
                    "lastName": "",
                    "email": "",
                    "phone": ""
                },
                "skills": [],
                "experience_years": 0,
                "education": "",
                "current_role": "",
                "raw_data": raw_cv_data,
                "formatting_error": str(e)
            }
    
    def _format_job_data(self, raw_job_data: Dict[str, Any]) -> Dict[str, Any]:
        """📊 Formate les données Job pour Nextvision"""
        try:
            # Le format exact dépend de ce que retourne votre Job Parser
            # Adaptation nécessaire selon votre structure de données
            
            formatted_data = {
                "title": raw_job_data.get("title", ""),
                "description": raw_job_data.get("description", ""),
                "required_skills": raw_job_data.get("required_skills", []),
                "location": raw_job_data.get("location", ""),
                "salary_range": raw_job_data.get("salary", {}),
                "company": raw_job_data.get("company", ""),
                "experience_required": raw_job_data.get("experience_required", 0),
                "contract_type": raw_job_data.get("contract_type", ""),
                "remote_possible": raw_job_data.get("remote", False),
                "raw_data": raw_job_data  # Garder les données brutes
            }
            
            logger.info(f"📊 Job formaté: {formatted_data['title']} chez {formatted_data['company']}")
            return formatted_data
            
        except Exception as e:
            logger.error(f"❌ Erreur formatage Job: {e}")
            return {
                "title": "",
                "description": "",
                "required_skills": [],
                "location": "",
                "salary_range": {},
                "company": "",
                "experience_required": 0,
                "contract_type": "",
                "remote_possible": False,
                "raw_data": raw_job_data,
                "formatting_error": str(e)
            }
    
    async def complete_workflow(
        self, 
        cv_file_data: bytes, 
        cv_filename: str,
        job_file_data: bytes,
        job_filename: str,
        pourquoi_ecoute: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🎯 Workflow Complet: Parse CV + Job + Matching avec Pondération Adaptative
        
        C'est l'endpoint principal qui utilise toute la puissance de NEXTEN !
        """
        workflow_start = time.time()
        logger.info(f"🎯 === WORKFLOW COMPLET NEXTEN ===")
        logger.info(f"📄 CV: {cv_filename}")
        logger.info(f"💼 Job: {job_filename}")
        logger.info(f"🎯 Motivation: {pourquoi_ecoute}")
        
        try:
            # Étape 1: Parsing en parallèle (optimisation performance)
            logger.info("⚡ Parsing CV et Job en parallèle...")
            cv_task = self.parse_cv_with_commitment(cv_file_data, cv_filename)
            job_task = self.parse_job_with_commitment(job_file_data, job_filename)
            
            cv_data, job_data = await asyncio.gather(cv_task, job_task)
            
            # Étape 2: Préparation des données pour Nextvision
            from main import get_adaptive_weights, calculate_mock_matching_scores
            from main import MatchingRequest, CandidateProfile, PersonalInfo, Preferences, SalaryExpectations, LocationPreferences
            
            # Construction de la requête de matching
            matching_request = MatchingRequest(
                pourquoi_ecoute=pourquoi_ecoute,
                candidate_profile=CandidateProfile(
                    personal_info=PersonalInfo(**cv_data["personal_info"]),
                    skills=cv_data["skills"],
                    experience_years=cv_data["experience_years"],
                    education=cv_data["education"],
                    current_role=cv_data["current_role"]
                ),
                preferences=Preferences(
                    salary_expectations=SalaryExpectations(**preferences.get("salary_expectations", {"min": 40000, "max": 60000})),
                    location_preferences=LocationPreferences(**preferences.get("location_preferences", {"city": "Paris"})),
                    remote_preferences=preferences.get("remote_preferences", ""),
                    sectors=preferences.get("sectors", []),
                    company_size=preferences.get("company_size", "")
                ),
                availability=preferences.get("availability", "")
            )
            
            # Étape 3: Application de l'algorithme révolutionnaire
            logger.info("🎯 Application de la pondération adaptative...")
            weight_analysis = get_adaptive_weights(pourquoi_ecoute)
            weights = weight_analysis["weights"]
            
            # Étape 4: Calcul du matching
            matching_analysis = calculate_mock_matching_scores(matching_request, weights)
            
            # Étape 5: Résultat complet
            processing_time = round((time.time() - workflow_start) * 1000, 2)
            
            result = {
                "status": "success",
                "workflow": "complete_nexten_matching",
                "processing_time_ms": processing_time,
                
                # Données parsées
                "parsed_data": {
                    "cv": cv_data,
                    "job": job_data
                },
                
                # Résultats du matching
                "matching_results": {
                    "total_score": matching_analysis["total_score"],
                    "confidence": matching_analysis["confidence"],
                    "component_scores": matching_analysis["component_scores"],
                    "weights_used": weights
                },
                
                # Innovation : Pondération adaptative
                "adaptive_weighting": {
                    "applied": weight_analysis["adaptation_applied"],
                    "reason": pourquoi_ecoute,
                    "reasoning": weight_analysis["reasoning"],
                    "weight_changes": self._calculate_weight_changes(weights) if weight_analysis["adaptation_applied"] else None
                },
                
                # Métadonnées
                "metadata": {
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "cv_filename": cv_filename,
                    "job_filename": job_filename,
                    "algorithm": "NEXTEN Adaptive Contextual Weighting",
                    "version": "1.0.0"
                }
            }
            
            logger.info(f"✅ Workflow complet terminé en {processing_time}ms")
            logger.info(f"📊 Score de matching final: {matching_analysis['total_score']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur workflow complet: {e}")
            raise Exception(f"Workflow failed: {str(e)}")
    
    def _calculate_weight_changes(self, adapted_weights: Dict) -> Dict:
        """📊 Calcule les changements de poids"""
        from main import DEFAULT_WEIGHTS
        
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


# 🔧 Factory function pour créer le bridge
def create_commitment_bridge(
    base_url: str = "http://localhost",
    cv_parser_port: int = 3001,
    job_parser_port: int = 5053,
    api_key: Optional[str] = None
) -> CommitmentNextvisionBridge:
    """
    🏭 Factory pour créer un bridge Commitment-Nextvision
    """
    config = CommitmentConfig(
        base_url=base_url,
        cv_parser_port=cv_parser_port,
        job_parser_port=job_parser_port,
        api_key=api_key
    )
    
    return CommitmentNextvisionBridge(config)
