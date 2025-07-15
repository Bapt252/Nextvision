"""
🔄 ADAPTATEUR INTELLIGENT - NEXTVISION v3.2.1
=====================================================

RÉVOLUTION ARCHITECTURE : Résolution automatique des incompatibilités format
- Parsing Output → Matching Input (automatique)
- CV parsé → CandidateProfile (transformation intelligente)
- Job parsé → JobRequirements (normalisation adaptative)
- Bridge complet : 5 étapes manuelles → 1 étape automatique

Author: NEXTEN Team
Version: 3.2.1
Innovation: Adaptateur format + Transport Intelligence intégré
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, ValidationError
import logging
import time
import json
from datetime import datetime
import re

# Import des modèles Nextvision
from nextvision.models.questionnaire_advanced import (
    QuestionnaireComplet, TimingInfo, RaisonEcoute, 
    TransportPreferences, MoyenTransport, RemunerationAttentes,
    SecteursPreferences, EnvironnementTravail, ContratsPreferences,
    MotivationsClassees, DisponibiliteType
)

logger = logging.getLogger(__name__)

class PersonalInfo(BaseModel):
    """🧑 Informations personnelles standardisées"""
    firstName: str
    lastName: str
    email: str
    phone: Optional[str] = None

class SalaryExpectations(BaseModel):
    """💰 Attentes salariales normalisées"""
    min: int
    max: int
    current: Optional[int] = None

class LocationPreferences(BaseModel):
    """📍 Préférences géographiques"""
    city: str
    acceptedCities: Optional[List[str]] = []
    maxDistance: Optional[int] = 0

class CandidateProfile(BaseModel):
    """👤 Profil candidat unifié pour Matching Engine"""
    personal_info: PersonalInfo
    skills: List[str]
    experience_years: int
    education: Optional[str] = ""
    current_role: Optional[str] = ""

class JobRequirements(BaseModel):
    """💼 Exigences job unifiées pour Matching Engine"""
    title: str
    company: str
    location: str
    required_skills: List[str]
    preferred_skills: Optional[List[str]] = []
    salary_range: Optional[Dict[str, int]] = None
    contract_type: Optional[str] = "CDI"
    remote_policy: Optional[str] = None

class Preferences(BaseModel):
    """⚙️ Préférences candidat pour matching"""
    salary_expectations: SalaryExpectations
    location_preferences: LocationPreferences
    remote_preferences: Optional[str] = ""
    sectors: Optional[List[str]] = []
    company_size: Optional[str] = ""

class MatchingRequest(BaseModel):
    """🎯 Requête de matching complète et unifiée"""
    pourquoi_ecoute: str
    candidate_profile: CandidateProfile
    preferences: Preferences
    job_requirements: Optional[JobRequirements] = None
    questionnaire: Optional[QuestionnaireComplet] = None
    metadata: Optional[Dict[str, Any]] = None

class AdaptationResult(BaseModel):
    """📊 Résultat de l'adaptation avec métadonnées"""
    success: bool
    matching_request: Optional[MatchingRequest] = None
    adaptations_applied: List[str]
    validation_errors: List[str]
    processing_time_ms: float
    metadata: Dict[str, Any]

class ParsingToMatchingAdapter:
    """
    🔄 ADAPTATEUR INTELLIGENT RÉVOLUTIONNAIRE
    ==========================================
    
    **Mission** : Transformer automatiquement les outputs de parsing
                  en inputs parfaitement formatés pour le Matching Engine
    
    **Innovation** :
    - ✅ Résout les incompatibilités CV parsing → CandidateProfile
    - ✅ Résout les incompatibilités Job parsing → JobRequirements  
    - ✅ Crée automatiquement le MatchingRequest complet
    - ✅ Génère questionnaire candidat depuis contexte
    - ✅ Normalise et valide toutes les données
    - ✅ Gestion d'erreurs robuste avec fallbacks intelligents
    
    **Transformation** : Workflow 5 étapes → 1 étape automatique
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.adaptations_applied = []
        self.validation_errors = []
        
    def adapt_cv_to_candidate_profile(self, cv_data: Dict[str, Any]) -> CandidateProfile:
        """
        🤖 Adapte CV parsé → CandidateProfile unifié
        
        Résout automatiquement les incompatibilités de format entre:
        - Output Commitment- CV Parser 
        - Input Nextvision Matching Engine
        """
        self.logger.info("🔄 Adaptation CV → CandidateProfile")
        
        try:
            # === EXTRACTION INFORMATIONS PERSONNELLES ===
            personal_info = self._extract_personal_info(cv_data)
            
            # === EXTRACTION COMPÉTENCES ===
            skills = self._extract_skills(cv_data)
            
            # === EXTRACTION EXPÉRIENCE ===
            experience_years = self._extract_experience_years(cv_data)
            
            # === EXTRACTION FORMATION ===
            education = self._extract_education(cv_data)
            
            # === EXTRACTION POSTE ACTUEL ===
            current_role = self._extract_current_role(cv_data)
            
            candidate_profile = CandidateProfile(
                personal_info=personal_info,
                skills=skills,
                experience_years=experience_years,
                education=education,
                current_role=current_role
            )
            
            self.adaptations_applied.append("cv_to_candidate_profile")
            self.logger.info(f"✅ CandidateProfile créé : {personal_info.firstName} {personal_info.lastName}")
            
            return candidate_profile
            
        except Exception as e:
            self.logger.error(f"❌ Erreur adaptation CV: {str(e)}")
            # Fallback avec données minimales
            return self._create_fallback_candidate_profile(cv_data)
    
    def adapt_job_to_requirements(self, job_data: Dict[str, Any]) -> JobRequirements:
        """
        💼 Adapte Job parsé → JobRequirements unifié
        
        Résout automatiquement les incompatibilités de format entre:
        - Output Commitment- Job Parser
        - Input Nextvision Matching Engine
        """
        self.logger.info("🔄 Adaptation Job → JobRequirements")
        
        try:
            # === EXTRACTION INFORMATIONS JOB ===
            title = self._extract_job_title(job_data)
            company = self._extract_company(job_data)
            location = self._extract_job_location(job_data)
            
            # === EXTRACTION COMPÉTENCES REQUISES ===
            required_skills = self._extract_required_skills(job_data)
            preferred_skills = self._extract_preferred_skills(job_data)
            
            # === EXTRACTION SALAIRE ===
            salary_range = self._extract_salary_range(job_data)
            
            # === EXTRACTION CONTRAT ===
            contract_type = self._extract_contract_type(job_data)
            remote_policy = self._extract_remote_policy(job_data)
            
            job_requirements = JobRequirements(
                title=title,
                company=company,
                location=location,
                required_skills=required_skills,
                preferred_skills=preferred_skills,
                salary_range=salary_range,
                contract_type=contract_type,
                remote_policy=remote_policy
            )
            
            self.adaptations_applied.append("job_to_requirements")
            self.logger.info(f"✅ JobRequirements créé : {title} chez {company}")
            
            return job_requirements
            
        except Exception as e:
            self.logger.error(f"❌ Erreur adaptation Job: {str(e)}")
            # Fallback avec données minimales
            return self._create_fallback_job_requirements(job_data)
    
    def create_questionnaire_from_context(
        self, 
        pourquoi_ecoute: str, 
        candidate_location: str, 
        salary_min: int
    ) -> QuestionnaireComplet:
        """
        📋 Génère automatiquement QuestionnaireComplet depuis contexte
        
        Innovation : Création intelligente du questionnaire candidat
        sans intervention manuelle, basé sur les données disponibles
        """
        self.logger.info("📋 Création questionnaire depuis contexte")
        
        try:
            # === MAPPING RAISONS D'ÉCOUTE ===
            raison_mapping = {
                "Rémunération trop faible": RaisonEcoute.REMUNERATION_FAIBLE,
                "Poste ne coïncide pas avec poste proposé": RaisonEcoute.POSTE_INADEQUAT,
                "Poste trop loin de mon domicile": RaisonEcoute.POSTE_TROP_LOIN,
                "Manque de flexibilité": RaisonEcoute.MANQUE_FLEXIBILITE,
                "Manque de perspectives d'évolution": RaisonEcoute.MANQUE_PERSPECTIVES,
                "Recherche nouveau défi": RaisonEcoute.NOUVEAU_DEFI,
                "Amélioration conditions": RaisonEcoute.AMELIORATION_CONDITIONS
            }
            
            raison_ecoute = raison_mapping.get(pourquoi_ecoute, RaisonEcoute.NOUVEAU_DEFI)
            
            # === QUESTIONNAIRE COMPLET AUTOMATIQUE ===
            questionnaire = QuestionnaireComplet(
                timing=TimingInfo(
                    disponibilite=DisponibiliteType.DANS_1_MOIS,
                    pourquoi_a_lecoute=raison_ecoute,
                    preavis={"durée": "1 mois", "négociable": True}
                ),
                secteurs=SecteursPreferences(
                    preferes=["Technologie", "Innovation"],
                    redhibitoires=[]
                ),
                environnement_travail=EnvironnementTravail.HYBRIDE,
                transport=TransportPreferences(
                    moyens_selectionnes=[MoyenTransport.VOITURE, MoyenTransport.TRANSPORT_COMMUN],
                    temps_max={"voiture": 45, "transport_commun": 60}
                ),
                contrats=ContratsPreferences(
                    ordre_preference=["CDI", "Freelance", "CDD"]
                ),
                motivations=MotivationsClassees(
                    classees=["Évolution", "Salaire", "Équipe", "Innovation"],
                    priorites=[1, 2, 3, 4]
                ),
                remuneration=RemunerationAttentes(
                    min=salary_min,
                    max=int(salary_min * 1.3),
                    actuel=salary_min
                )
            )
            
            self.adaptations_applied.append("questionnaire_from_context")
            self.logger.info(f"✅ Questionnaire créé pour raison: {pourquoi_ecoute}")
            
            return questionnaire
            
        except Exception as e:
            self.logger.error(f"❌ Erreur création questionnaire: {str(e)}")
            # Fallback questionnaire minimal
            return self._create_fallback_questionnaire(salary_min)
    
    def create_complete_matching_request(
        self,
        cv_data: Dict[str, Any],
        job_data: Optional[Dict[str, Any]] = None,
        pourquoi_ecoute: str = "Recherche nouveau défi",
        additional_context: Optional[Dict[str, Any]] = None
    ) -> AdaptationResult:
        """
        🎯 FONCTION PRINCIPALE : Crée MatchingRequest complet automatiquement
        
        **Innovation Révolutionnaire** :
        - Input : CV parsé + Job parsé (formats bruts)
        - Output : MatchingRequest parfaitement formaté pour Matching Engine
        - Zéro intervention manuelle
        - Validation complète automatique
        - Métadonnées enrichies
        
        **Transformation** : 5 étapes → 1 étape
        """
        start_time = time.time()
        
        self.logger.info("🎯 === CRÉATION MATCHING REQUEST UNIFIÉ ===")
        self.logger.info(f"📋 Pourquoi écoute: {pourquoi_ecoute}")
        
        try:
            # === PHASE 1: ADAPTATION CANDIDATE PROFILE ===
            candidate_profile = self.adapt_cv_to_candidate_profile(cv_data)
            
            # === PHASE 2: CRÉATION PRÉFÉRENCES ===
            preferences = self._create_preferences_from_context(
                cv_data, additional_context, pourquoi_ecoute
            )
            
            # === PHASE 3: ADAPTATION JOB REQUIREMENTS (optionnel) ===
            job_requirements = None
            if job_data:
                job_requirements = self.adapt_job_to_requirements(job_data)
            
            # === PHASE 4: CRÉATION QUESTIONNAIRE ===
            questionnaire = self.create_questionnaire_from_context(
                pourquoi_ecoute=pourquoi_ecoute,
                candidate_location=preferences.location_preferences.city,
                salary_min=preferences.salary_expectations.min
            )
            
            # === PHASE 5: ASSEMBLAGE MATCHING REQUEST ===
            matching_request = MatchingRequest(
                pourquoi_ecoute=pourquoi_ecoute,
                candidate_profile=candidate_profile,
                preferences=preferences,
                job_requirements=job_requirements,
                questionnaire=questionnaire,
                metadata={
                    "adapter_version": "3.2.1",
                    "created_at": datetime.now().isoformat(),
                    "adaptations_applied": self.adaptations_applied,
                    "source_cv_fields": list(cv_data.keys()) if cv_data else [],
                    "source_job_fields": list(job_data.keys()) if job_data else []
                }
            )
            
            # === VALIDATION FINALE ===
            validation_errors = self._validate_matching_request(matching_request)
            
            processing_time = (time.time() - start_time) * 1000
            
            # === RÉSULTAT ADAPTATION ===
            result = AdaptationResult(
                success=len(validation_errors) == 0,
                matching_request=matching_request,
                adaptations_applied=self.adaptations_applied,
                validation_errors=validation_errors,
                processing_time_ms=round(processing_time, 2),
                metadata={
                    "adapter_version": "3.2.1",
                    "timestamp": datetime.now().isoformat(),
                    "transformations_count": len(self.adaptations_applied),
                    "candidate_name": f"{candidate_profile.personal_info.firstName} {candidate_profile.personal_info.lastName}",
                    "skills_count": len(candidate_profile.skills),
                    "has_job_data": job_data is not None
                }
            )
            
            if result.success:
                self.logger.info(f"✅ MatchingRequest créé avec succès en {processing_time:.2f}ms")
                self.logger.info(f"🔧 Adaptations appliquées: {len(self.adaptations_applied)}")
            else:
                self.logger.warning(f"⚠️ MatchingRequest créé avec erreurs: {len(validation_errors)}")
            
            return result
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self.logger.error(f"❌ Erreur création MatchingRequest: {str(e)}")
            
            return AdaptationResult(
                success=False,
                matching_request=None,
                adaptations_applied=self.adaptations_applied,
                validation_errors=[f"Erreur critique: {str(e)}"],
                processing_time_ms=round(processing_time, 2),
                metadata={
                    "adapter_version": "3.2.1",
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e),
                    "phase": "creation_complete"
                }
            )
    
    # === MÉTHODES D'EXTRACTION PRIVÉES ===
    
    def _extract_personal_info(self, cv_data: Dict[str, Any]) -> PersonalInfo:
        """🧑 Extraction informations personnelles avec fallbacks intelligents"""
        # Parsing Commitment- peut retourner différents formats
        name = cv_data.get("name", cv_data.get("nom", cv_data.get("personal_info", {}).get("nom", "")))
        email = cv_data.get("email", cv_data.get("personal_info", {}).get("email", ""))
        phone = cv_data.get("phone", cv_data.get("telephone", cv_data.get("personal_info", {}).get("telephone", "")))
        
        # Split nom/prénom intelligent
        if name and " " in name:
            parts = name.strip().split(" ", 1)
            firstName = parts[0]
            lastName = parts[1] if len(parts) > 1 else ""
        else:
            firstName = cv_data.get("prenom", cv_data.get("personal_info", {}).get("prenom", name or "Candidat"))
            lastName = cv_data.get("nom", cv_data.get("personal_info", {}).get("nom", "Test"))
        
        return PersonalInfo(
            firstName=firstName,
            lastName=lastName,
            email=email or "candidat@example.com",
            phone=phone
        )
    
    def _extract_skills(self, cv_data: Dict[str, Any]) -> List[str]:
        """🛠️ Extraction compétences avec normalisation"""
        skills = cv_data.get("skills", cv_data.get("competences", []))
        
        if isinstance(skills, str):
            # Si string, split par virgules ou points-virgules
            skills = [s.strip() for s in re.split(r'[,;]', skills) if s.strip()]
        elif not isinstance(skills, list):
            skills = []
        
        # Normalisation : suppression doublons et vides
        skills = list(set([skill.strip() for skill in skills if skill and skill.strip()]))
        
        # Fallback si aucune compétence
        if not skills:
            skills = ["Compétence générale"]
        
        return skills[:20]  # Limite à 20 compétences max
    
    def _extract_experience_years(self, cv_data: Dict[str, Any]) -> int:
        """📅 Extraction années d'expérience avec calcul intelligent"""
        experience = cv_data.get("years_of_experience", cv_data.get("experience", {}).get("annees_experience", 0))
        
        if isinstance(experience, str):
            # Extraction numérique depuis string
            match = re.search(r'(\d+)', experience)
            experience = int(match.group(1)) if match else 0
        
        return max(0, min(int(experience), 50))  # Entre 0 et 50 ans
    
    def _extract_education(self, cv_data: Dict[str, Any]) -> str:
        """🎓 Extraction formation avec normalisation"""
        education = cv_data.get("education", cv_data.get("formation", ""))
        
        if isinstance(education, list) and education:
            education = education[0] if education else ""
        
        return str(education)[:200]  # Limite 200 caractères
    
    def _extract_current_role(self, cv_data: Dict[str, Any]) -> str:
        """💼 Extraction poste actuel"""
        current_role = cv_data.get("current_role", cv_data.get("poste_actuel", ""))
        
        # Si pas de poste actuel, prendre le premier des job_titles
        if not current_role:
            job_titles = cv_data.get("job_titles", [])
            if job_titles and isinstance(job_titles, list):
                current_role = job_titles[0]
        
        return str(current_role)[:100]  # Limite 100 caractères
    
    def _extract_job_title(self, job_data: Dict[str, Any]) -> str:
        """💼 Extraction titre du poste"""
        return job_data.get("title", job_data.get("titre_poste", "Poste à définir"))
    
    def _extract_company(self, job_data: Dict[str, Any]) -> str:
        """🏢 Extraction entreprise"""
        return job_data.get("company", job_data.get("entreprise", "Entreprise"))
    
    def _extract_job_location(self, job_data: Dict[str, Any]) -> str:
        """📍 Extraction localisation job"""
        return job_data.get("location", job_data.get("localisation", "Paris, France"))
    
    def _extract_required_skills(self, job_data: Dict[str, Any]) -> List[str]:
        """🛠️ Extraction compétences requises job"""
        skills = job_data.get("required_skills", job_data.get("competences_requises", []))
        
        if isinstance(skills, str):
            skills = [s.strip() for s in re.split(r'[,;]', skills) if s.strip()]
        elif not isinstance(skills, list):
            skills = ["Compétences générales"]
        
        return skills[:15]  # Limite à 15
    
    def _extract_preferred_skills(self, job_data: Dict[str, Any]) -> List[str]:
        """⭐ Extraction compétences préférées job"""
        skills = job_data.get("preferred_skills", job_data.get("competences_preferees", []))
        
        if isinstance(skills, str):
            skills = [s.strip() for s in re.split(r'[,;]', skills) if s.strip()]
        elif not isinstance(skills, list):
            skills = []
        
        return skills[:10]  # Limite à 10
    
    def _extract_salary_range(self, job_data: Dict[str, Any]) -> Dict[str, int]:
        """💰 Extraction fourchette salariale job"""
        salary = job_data.get("salary_range", job_data.get("salaire", {}))
        
        if isinstance(salary, str):
            # Extraction depuis string (ex: "45k-55k", "45000-55000")
            match = re.findall(r'(\d+)k?', salary.lower())
            if len(match) >= 2:
                min_sal = int(match[0]) * (1000 if 'k' in salary.lower() else 1)
                max_sal = int(match[1]) * (1000 if 'k' in salary.lower() else 1)
                return {"min": min_sal, "max": max_sal}
        elif isinstance(salary, dict):
            return {
                "min": salary.get("min", 45000),
                "max": salary.get("max", 55000)
            }
        
        # Fallback par défaut
        return {"min": 45000, "max": 55000}
    
    def _extract_contract_type(self, job_data: Dict[str, Any]) -> str:
        """📋 Extraction type de contrat"""
        return job_data.get("contract_type", job_data.get("type_contrat", "CDI"))
    
    def _extract_remote_policy(self, job_data: Dict[str, Any]) -> str:
        """🏠 Extraction politique remote"""
        return job_data.get("remote_policy", job_data.get("politique_remote", "Hybride"))
    
    def _create_preferences_from_context(
        self, 
        cv_data: Dict[str, Any], 
        additional_context: Optional[Dict[str, Any]], 
        pourquoi_ecoute: str
    ) -> Preferences:
        """⚙️ Création préférences depuis contexte CV et additional_context"""
        
        # Extraction localisation candidat
        location = cv_data.get("location", cv_data.get("localisation", "Paris"))
        if "," not in location:
            location = f"{location}, France"
        
        # Estimation salaire depuis contexte ou défaut intelligent
        salary_min = 45000
        salary_max = 55000
        
        if additional_context:
            salary_min = additional_context.get("salary_min", salary_min)
            salary_max = additional_context.get("salary_max", salary_max)
        
        # Adaptation selon raison d'écoute
        if "rémunération" in pourquoi_ecoute.lower():
            salary_min = int(salary_min * 1.2)  # +20% si problème salaire
            salary_max = int(salary_max * 1.3)
        
        return Preferences(
            salary_expectations=SalaryExpectations(
                min=salary_min,
                max=salary_max,
                current=salary_min
            ),
            location_preferences=LocationPreferences(
                city=location.split(",")[0].strip(),
                acceptedCities=[location.split(",")[0].strip()],
                maxDistance=50
            ),
            remote_preferences="Hybride",
            sectors=["Technologie", "Innovation"],
            company_size="Moyenne à grande"
        )
    
    def _create_fallback_candidate_profile(self, cv_data: Dict[str, Any]) -> CandidateProfile:
        """🛡️ Fallback CandidateProfile si adaptation échoue"""
        return CandidateProfile(
            personal_info=PersonalInfo(
                firstName="Candidat",
                lastName="Test", 
                email="candidat@example.com"
            ),
            skills=["Compétence générale"],
            experience_years=2,
            education="Formation",
            current_role="Poste actuel"
        )
    
    def _create_fallback_job_requirements(self, job_data: Dict[str, Any]) -> JobRequirements:
        """🛡️ Fallback JobRequirements si adaptation échoue"""
        return JobRequirements(
            title="Poste à définir",
            company="Entreprise",
            location="Paris, France",
            required_skills=["Compétences générales"],
            salary_range={"min": 45000, "max": 55000}
        )
    
    def _create_fallback_questionnaire(self, salary_min: int) -> QuestionnaireComplet:
        """🛡️ Fallback QuestionnaireComplet minimal"""
        return QuestionnaireComplet(
            timing=TimingInfo(
                disponibilite=DisponibiliteType.DANS_1_MOIS,
                pourquoi_a_lecoute=RaisonEcoute.NOUVEAU_DEFI,
                preavis={"durée": "1 mois", "négociable": True}
            ),
            secteurs=SecteursPreferences(preferes=["Technologie"], redhibitoires=[]),
            environnement_travail=EnvironnementTravail.HYBRIDE,
            transport=TransportPreferences(
                moyens_selectionnes=[MoyenTransport.VOITURE],
                temps_max={"voiture": 45}
            ),
            contrats=ContratsPreferences(ordre_preference=["CDI"]),
            motivations=MotivationsClassees(classees=["Évolution"], priorites=[1]),
            remuneration=RemunerationAttentes(min=salary_min, max=salary_min + 10000, actuel=salary_min)
        )
    
    def _validate_matching_request(self, matching_request: MatchingRequest) -> List[str]:
        """✅ Validation complète MatchingRequest"""
        errors = []
        
        try:
            # Validation Pydantic automatique
            matching_request.dict()
        except ValidationError as e:
            errors.extend([f"Validation Pydantic: {error}" for error in e.errors()])
        
        # Validations métier
        if not matching_request.candidate_profile.skills:
            errors.append("Aucune compétence candidat")
        
        if matching_request.preferences.salary_expectations.min <= 0:
            errors.append("Salaire minimum invalide")
        
        if not matching_request.candidate_profile.personal_info.email:
            errors.append("Email candidat manquant")
        
        return errors

# === FONCTION UTILITAIRE PRINCIPALE ===

def create_unified_matching_request(
    cv_data: Dict[str, Any],
    job_data: Optional[Dict[str, Any]] = None,
    pourquoi_ecoute: str = "Recherche nouveau défi",
    additional_context: Optional[Dict[str, Any]] = None
) -> AdaptationResult:
    """
    🎯 FONCTION PRINCIPALE D'ADAPTATION UNIFIÉE
    
    **Usage** :
    ```python
    from nextvision.adapters.parsing_to_matching_adapter import create_unified_matching_request
    
    # CV et Job parsés par Commitment-
    cv_parsed = {...}  # Output CV Parser
    job_parsed = {...} # Output Job Parser
    
    # Transformation automatique
    result = create_unified_matching_request(
        cv_data=cv_parsed,
        job_data=job_parsed,
        pourquoi_ecoute="Rémunération trop faible"
    )
    
    if result.success:
        matching_request = result.matching_request
        # → Prêt pour Matching Engine !
    ```
    
    **Innovation** : 5 étapes manuelles → 1 fonction automatique
    """
    adapter = ParsingToMatchingAdapter()
    return adapter.create_complete_matching_request(
        cv_data=cv_data,
        job_data=job_data,
        pourquoi_ecoute=pourquoi_ecoute,
        additional_context=additional_context
    )
