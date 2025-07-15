"""
🌉 Enhanced Commitment Bridge V3.0 Simplifié - FIXÉ
Version simplifiée sans imports circulaires pour test système complet

Author: Assistant Claude
Version: 3.0.1-fixed
Date: 2025-07-10
"""

import nextvision_logging as logging
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime

# Import des modèles nécessaires
from nextvision.models.bidirectional_models import (
    BiDirectionalCandidateProfile, BiDirectionalCompanyProfile,
    PersonalInfoBidirectional, CompetencesProfessionnelles, AttentesCandidat,
    MotivationsCandidat, InformationsEntreprise, DescriptionPoste,
    ExigencesPoste, ConditionsTravail, CriteresRecrutement,
    NiveauExperience, TypeContrat, RaisonEcouteCandidat, UrgenceRecrutement
)

# Import des modèles transport (CORRIGÉ)
from nextvision.models.transport_models import TravelMode

logger = logging.getLogger(__name__)

class BridgeMetrics:
    """📊 Métriques de conversion du bridge"""
    
    def __init__(self):
        self.v3_components_count = 0
        self.conversion_time_ms = 0.0
        self.success = True
        self.warnings = []
        self.created_at = datetime.now()

class EnhancedCommitmentBridgeV3Simplified:
    """🌉 Bridge V3.0 Simplifié pour test système complet"""
    
    def __init__(self):
        self.version = "3.0.1-fixed"
        self.stats = {
            "candidat_conversions": 0,
            "entreprise_conversions": 0,
            "total_processing_time": 0.0
        }
        logger.info("🌉 Enhanced Bridge V3.0 Simplifié initialisé")
    
    async def convert_candidat_simplified(
        self, 
        parser_output: Dict[str, Any], 
        questionnaire_data: Dict[str, Any]
    ) -> Tuple[BiDirectionalCandidateProfile, BridgeMetrics]:
        """🔄 Conversion candidat simplifiée pour tests"""
        
        start_time = datetime.now()
        metrics = BridgeMetrics()
        
        try:
            # Création profil candidat de base
            candidat_profile = self._create_basic_candidate_profile(parser_output)
            
            # Enrichissement avec questionnaire V3.0
            self._enrich_candidat_with_questionnaire(candidat_profile, questionnaire_data)
            
            # Métriques
            metrics.conversion_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            metrics.v3_components_count = 5  # personal_info, competences, attentes, motivations, experience
            metrics.success = True
            
            self.stats["candidat_conversions"] += 1
            self.stats["total_processing_time"] += metrics.conversion_time_ms
            
            logger.info(f"✅ Candidat converti en {metrics.conversion_time_ms:.1f}ms")
            
            return candidat_profile, metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur conversion candidat: {e}")
            metrics.success = False
            metrics.warnings.append(f"Conversion échouée: {e}")
            
            # Fallback vers profil minimal
            fallback_profile = self._create_fallback_candidate_profile(parser_output)
            return fallback_profile, metrics
    
    async def convert_entreprise_simplified(
        self, 
        chatgpt_output: Dict[str, Any], 
        questionnaire_data: Dict[str, Any]
    ) -> Tuple[BiDirectionalCompanyProfile, BridgeMetrics]:
        """🏢 Conversion entreprise simplifiée pour tests"""
        
        start_time = datetime.now()
        metrics = BridgeMetrics()
        
        try:
            # Création profil entreprise de base
            company_profile = self._create_basic_company_profile(chatgpt_output)
            
            # Enrichissement avec questionnaire V3.0
            self._enrich_company_with_questionnaire(company_profile, questionnaire_data)
            
            # Métriques
            metrics.conversion_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            metrics.v3_components_count = 5  # entreprise, poste, exigences, conditions, recrutement
            metrics.success = True
            
            self.stats["entreprise_conversions"] += 1
            self.stats["total_processing_time"] += metrics.conversion_time_ms
            
            logger.info(f"✅ Entreprise convertie en {metrics.conversion_time_ms:.1f}ms")
            
            return company_profile, metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur conversion entreprise: {e}")
            metrics.success = False
            metrics.warnings.append(f"Conversion échouée: {e}")
            
            # Fallback vers profil minimal
            fallback_profile = self._create_fallback_company_profile(chatgpt_output)
            return fallback_profile, metrics
    
    def _create_basic_candidate_profile(self, parser_output: Dict[str, Any]) -> BiDirectionalCandidateProfile:
        """👤 Création profil candidat de base"""
        
        personal_info_data = parser_output.get("personal_info", {})
        skills_data = parser_output.get("skills", [])
        experience_data = parser_output.get("experience", {})
        salary_data = parser_output.get("salary", {})
        location_data = parser_output.get("location", {})
        
        # Personal Info
        personal_info = PersonalInfoBidirectional(
            firstName=personal_info_data.get("firstName", "Test"),
            lastName=personal_info_data.get("lastName", "Candidate"),
            email=personal_info_data.get("email", "test@example.com"),
            phone=personal_info_data.get("phone", "0123456789")
        )
        
        # Compétences
        competences = CompetencesProfessionnelles(
            competences_techniques=skills_data if isinstance(skills_data, list) else ["Compétences générales"],
            logiciels_maitrise=skills_data[:3] if isinstance(skills_data, list) and len(skills_data) > 3 else skills_data,
            langues={"Français": "Natif", "Anglais": "Courant"}
        )
        
        # Expérience globale
        total_years = experience_data.get("total_years", 3)
        if total_years <= 2:
            experience_globale = NiveauExperience.JUNIOR
        elif total_years <= 5:
            experience_globale = NiveauExperience.CONFIRME
        else:
            experience_globale = NiveauExperience.SENIOR
        
        # Attentes
        attentes = AttentesCandidat(
            salaire_min=salary_data.get("current", 35000),
            salaire_max=salary_data.get("expected", 50000),
            localisation_preferee=location_data.get("city", "Paris"),
            distance_max_km=30,
            remote_accepte=True
        )
        
        # Motivations (défaut)
        motivations = MotivationsCandidat(
            raison_ecoute=RaisonEcouteCandidat.MANQUE_PERSPECTIVES,
            motivations_principales=["Évolution professionnelle", "Nouveaux défis"]
        )
        
        return BiDirectionalCandidateProfile(
            personal_info=personal_info,
            experience_globale=experience_globale,
            competences=competences,
            attentes=attentes,
            motivations=motivations,
            version="3.0.1-simplified"
        )
    
    def _create_basic_company_profile(self, chatgpt_output: Dict[str, Any]) -> BiDirectionalCompanyProfile:
        """🏢 Création profil entreprise de base"""
        
        # Informations entreprise
        entreprise = InformationsEntreprise(
            nom=chatgpt_output.get("entreprise", "Entreprise Test"),
            secteur=chatgpt_output.get("company_structure", {}).get("sector", "Technologie"),
            localisation=chatgpt_output.get("localisation", "Paris")
        )
        
        # Description poste
        poste = DescriptionPoste(
            titre=chatgpt_output.get("titre", "Poste Test"),
            localisation=chatgpt_output.get("localisation", "Paris"),
            type_contrat=TypeContrat.CDI,
            salaire_min=self._parse_salary_min(chatgpt_output.get("salaire", "40K")),
            salaire_max=self._parse_salary_max(chatgpt_output.get("salaire", "50K")),
            competences_requises=chatgpt_output.get("competences_requises", ["Compétences générales"])
        )
        
        # Exigences
        exigences = ExigencesPoste(
            experience_requise=chatgpt_output.get("experience_requise", "2-5 ans"),
            competences_obligatoires=chatgpt_output.get("competences_requises", ["Compétences générales"])[:3],
            competences_souhaitees=chatgpt_output.get("competences_requises", ["Compétences générales"])[3:6]
        )
        
        # Conditions
        conditions = ConditionsTravail(
            remote_possible=chatgpt_output.get("job_details", {}).get("remote_work_policy") in ["hybride", "remote"],
            avantages=chatgpt_output.get("job_details", {}).get("benefits", ["Mutuelle", "Tickets restaurant"])
        )
        
        # Recrutement
        urgence_str = chatgpt_output.get("recruitment_process", {}).get("urgency", "normal")
        urgence = UrgenceRecrutement.NORMAL
        if urgence_str == "urgent":
            urgence = UrgenceRecrutement.URGENT
        elif urgence_str == "critique":
            urgence = UrgenceRecrutement.CRITIQUE
        
        recrutement = CriteresRecrutement(
            urgence=urgence,
            criteres_prioritaires=["competences", "experience"]
        )
        
        return BiDirectionalCompanyProfile(
            entreprise=entreprise,
            poste=poste,
            exigences=exigences,
            conditions=conditions,
            recrutement=recrutement,
            version="3.0.1-simplified"
        )
    
    def _enrich_candidat_with_questionnaire(
        self, 
        candidat: BiDirectionalCandidateProfile, 
        questionnaire_data: Dict[str, Any]
    ):
        """🔧 Enrichissement candidat avec questionnaire V3.0"""
        
        mobility_prefs = questionnaire_data.get("mobility_preferences", {})
        motivations_sectors = questionnaire_data.get("motivations_sectors", {})
        availability = questionnaire_data.get("availability_status", {})
        
        # Enrichissement attentes avec mobilité
        if mobility_prefs:
            work_location_pref = mobility_prefs.get("work_location_preference", "")
            if work_location_pref == "remote":
                candidat.attentes.remote_accepte = True
            elif work_location_pref == "hybride":
                candidat.attentes.remote_accepte = True
        
        # Enrichissement motivations
        if motivations_sectors:
            listening_reasons = availability.get("listening_reasons", [])
            if "opportunité_évolution" in listening_reasons:
                candidat.motivations.raison_ecoute = RaisonEcouteCandidat.MANQUE_PERSPECTIVES
            elif "salaire" in str(listening_reasons).lower():
                candidat.motivations.raison_ecoute = RaisonEcouteCandidat.REMUNERATION_TROP_FAIBLE
    
    def _enrich_company_with_questionnaire(
        self, 
        company: BiDirectionalCompanyProfile, 
        questionnaire_data: Dict[str, Any]
    ):
        """🔧 Enrichissement entreprise avec questionnaire V3.0"""
        
        job_details = questionnaire_data.get("job_details", {})
        recruitment_process = questionnaire_data.get("recruitment_process", {})
        
        # Enrichissement conditions avec job_details
        if job_details:
            remote_policy = job_details.get("remote_work_policy", "")
            if remote_policy in ["hybride", "remote", "full_remote"]:
                company.conditions.remote_possible = True
            
            benefits = job_details.get("benefits", [])
            if benefits:
                company.conditions.avantages.extend(benefits)
        
        # Enrichissement urgence
        if recruitment_process:
            urgency = recruitment_process.get("urgency", "normal")
            if urgency == "urgent":
                company.recrutement.urgence = UrgenceRecrutement.URGENT
            elif urgency == "critique":
                company.recrutement.urgence = UrgenceRecrutement.CRITIQUE
    
    def _create_fallback_candidate_profile(self, parser_output: Dict[str, Any]) -> BiDirectionalCandidateProfile:
        """🚨 Profil candidat fallback minimal"""
        
        return BiDirectionalCandidateProfile(
            personal_info=PersonalInfoBidirectional(
                firstName="Test",
                lastName="Candidate",
                email="test@example.com",
                phone="0123456789"
            ),
            experience_globale=NiveauExperience.CONFIRME,
            competences=CompetencesProfessionnelles(
                competences_techniques=["Compétences générales"],
                logiciels_maitrise=["Office"],
                langues={"Français": "Natif"}
            ),
            attentes=AttentesCandidat(
                salaire_min=35000,
                salaire_max=50000,
                localisation_preferee="Paris",
                distance_max_km=30,
                remote_accepte=True
            ),
            motivations=MotivationsCandidat(
                raison_ecoute=RaisonEcouteCandidat.MANQUE_PERSPECTIVES,
                motivations_principales=["Évolution professionnelle"]
            ),
            version="3.0.1-fallback"
        )
    
    def _create_fallback_company_profile(self, chatgpt_output: Dict[str, Any]) -> BiDirectionalCompanyProfile:
        """🚨 Profil entreprise fallback minimal"""
        
        return BiDirectionalCompanyProfile(
            entreprise=InformationsEntreprise(
                nom="Entreprise Test",
                secteur="Technologie",
                localisation="Paris"
            ),
            poste=DescriptionPoste(
                titre="Poste Test",
                localisation="Paris",
                type_contrat=TypeContrat.CDI,
                salaire_min=35000,
                salaire_max=50000,
                competences_requises=["Compétences générales"]
            ),
            exigences=ExigencesPoste(
                experience_requise="2-5 ans",
                competences_obligatoires=["Compétences générales"],
                competences_souhaitees=[]
            ),
            conditions=ConditionsTravail(
                remote_possible=True,
                avantages=["Mutuelle"]
            ),
            recrutement=CriteresRecrutement(
                urgence=UrgenceRecrutement.NORMAL,
                criteres_prioritaires=["competences"]
            ),
            version="3.0.1-fallback"
        )
    
    def _parse_salary_min(self, salary_str: str) -> int:
        """💰 Parse salaire minimum"""
        try:
            if "-" in salary_str:
                min_part = salary_str.split("-")[0]
            else:
                min_part = salary_str
            
            # Extraire les chiffres
            numbers = ''.join(filter(str.isdigit, min_part))
            if numbers:
                salary = int(numbers)
                # Si en milliers (ex: "40K" = 40000)
                if "K" in salary_str.upper() and salary < 1000:
                    salary *= 1000
                return salary
            return 35000
        except:
            return 35000
    
    def _parse_salary_max(self, salary_str: str) -> int:
        """💰 Parse salaire maximum"""
        try:
            if "-" in salary_str:
                max_part = salary_str.split("-")[1]
            else:
                max_part = salary_str
            
            # Extraire les chiffres
            numbers = ''.join(filter(str.isdigit, max_part))
            if numbers:
                salary = int(numbers)
                # Si en milliers (ex: "60K" = 60000)
                if "K" in salary_str.upper() and salary < 1000:
                    salary *= 1000
                return salary
            return 50000
        except:
            return 50000
    
    def get_stats(self) -> Dict[str, Any]:
        """📊 Statistiques du bridge"""
        return {
            "version": self.version,
            "stats": self.stats,
            "uptime": datetime.now().isoformat()
        }

class SimplifiedBridgeFactory:
    """🏗️ Factory pour création bridge simplifié"""
    
    @staticmethod
    def create_bridge() -> EnhancedCommitmentBridgeV3Simplified:
        """Création bridge V3.0 simplifié"""
        return EnhancedCommitmentBridgeV3Simplified()
