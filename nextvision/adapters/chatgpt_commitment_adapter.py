"""
🎯 Nextvision v2.0 - Adaptateur ChatGPT Commitment-

Adaptateur pour exploiter le système de parsing IA existant de Commitment- :
- Enhanced Universal Parser v4.0 (côté candidat - CVs)
- Système ChatGPT (côté entreprise - fiches de poste)
- Conversion vers format bidirectionnel Nextvision
- Conservation des badges "Auto-rempli" et métadonnées parsing

Author: NEXTEN Team
Version: 2.0.0 - ChatGPT Integration
"""

import json
import re
import nextvision_logging as logging
import time  # 🔧 FIX: Import time manquant pour time.time()
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from dataclasses import dataclass

# Import des modèles bidirectionnels
from nextvision.models.bidirectional_models import (
    BiDirectionalCandidateProfile, BiDirectionalCompanyProfile,
    PersonalInfoBidirectional, CompetencesProfessionnelles, AttentesCandidat,
    MotivationsCandidat, ExperienceProfessionnelle, InformationsEntreprise,
    DescriptionPoste, ExigencesPoste, ConditionsTravail, CriteresRecrutement,
    RaisonEcouteCandidat, UrgenceRecrutement, NiveauExperience, TypeContrat,
    ChatGPTCommitmentFormat
)

logger = logging.getLogger(__name__)

# === STRUCTURES DE DONNÉES COMMITMENT- ===

@dataclass
class EnhancedParserV4Output:
    """Structure de sortie Enhanced Universal Parser v4.0 (candidat)"""
    personal_info: Dict
    skills: List[str]
    experience: Dict
    education: Optional[str]
    languages: Dict[str, str]
    softwares: List[str]
    work_experience: List[Dict]
    parsing_confidence: float
    extraction_time_ms: float

@dataclass  
class ChatGPTCommitmentOutput:
    """Structure de sortie système ChatGPT Commitment- (entreprise)"""
    titre: str
    localisation: str
    contrat: str  # Format: "CDI"
    salaire: str  # Format: "35K à 38K annuels"
    competences_requises: List[str]  # Format: ["Maîtrise du logiciel comptable CEGID", "Gestion comptable et fiscale"]
    experience_requise: str  # Format: "5 ans - 10 ans"
    missions: List[str]
    avantages: List[str]
    badges_auto_rempli: List[str]  # ["Auto-rempli"]
    fiche_poste_originale: str
    parsing_confidence: float
    extraction_time_ms: float

# === ADAPTATEUR CANDIDAT (Enhanced Universal Parser v4.0) ===

class EnhancedParserV4Adapter:
    """🔄 Adaptateur Enhanced Universal Parser v4.0 → Bidirectionnel"""
    
    def __init__(self):
        self.name = "Enhanced Universal Parser v4.0 Adapter"
        
        # Mapping niveaux d'expérience
        self.experience_mapping = {
            "0-2": NiveauExperience.DEBUTANT,
            "2-5": NiveauExperience.JUNIOR, 
            "5-10": NiveauExperience.CONFIRME,
            "10+": NiveauExperience.SENIOR
        }
    
    def convert_to_bidirectional(self, parser_output: Union[Dict, EnhancedParserV4Output],
                               questionnaire_data: Optional[Dict] = None) -> BiDirectionalCandidateProfile:
        """🔄 Conversion Enhanced Parser → Bidirectionnel"""
        
        try:
            # Normalisation input
            if isinstance(parser_output, dict):
                data = parser_output
            else:
                data = parser_output.__dict__
            
            logger.info("🔄 Conversion Enhanced Universal Parser v4.0 → Bidirectionnel")
            
            # 1. Informations personnelles
            personal_info = self._extract_personal_info(data.get("personal_info", {}))
            
            # 2. Expérience et compétences
            experience_globale = self._extract_experience_level(data.get("experience", {}))
            experiences_detaillees = self._extract_detailed_experience(data.get("work_experience", []))
            competences = self._extract_competences(data)
            
            # 3. Attentes (depuis questionnaire ou valeurs par défaut)
            attentes = self._extract_attentes(questionnaire_data)
            
            # 4. Motivations (depuis questionnaire ou par défaut)
            motivations = self._extract_motivations(questionnaire_data)
            
            # 5. Construction profil bidirectionnel
            candidat_profile = BiDirectionalCandidateProfile(
                personal_info=personal_info,
                experience_globale=experience_globale,
                experiences_detaillees=experiences_detaillees,
                competences=competences,
                formation=data.get("education"),
                attentes=attentes,
                motivations=motivations,
                parsing_source="enhanced_parser_v4",
                parsed_at=datetime.now(),
                confidence_score=data.get("parsing_confidence", 0.8)
            )
            
            logger.info(f"✅ Candidat converti: {personal_info.firstName} {personal_info.lastName}")
            logger.info(f"📊 Confiance parsing: {data.get('parsing_confidence', 0.8)}")
            
            return candidat_profile
            
        except Exception as e:
            logger.error(f"❌ Erreur conversion Enhanced Parser: {e}")
            raise
    
    def _extract_personal_info(self, personal_data: Dict) -> PersonalInfoBidirectional:
        """Extraction informations personnelles"""
        return PersonalInfoBidirectional(
            firstName=personal_data.get("firstName", ""),
            lastName=personal_data.get("lastName", ""),
            email=personal_data.get("email", ""),
            phone=personal_data.get("phone"),
            age=personal_data.get("age"),
            linkedin_url=personal_data.get("linkedin_url")
        )
    
    def _extract_experience_level(self, experience_data: Dict) -> NiveauExperience:
        """Extraction niveau d'expérience global"""
        years = experience_data.get("total_years", 0)
        
        if years <= 2:
            return NiveauExperience.DEBUTANT
        elif years <= 5:
            return NiveauExperience.JUNIOR
        elif years <= 10:
            return NiveauExperience.CONFIRME
        else:
            return NiveauExperience.SENIOR
    
    def _extract_detailed_experience(self, work_experience: List[Dict]) -> List[ExperienceProfessionnelle]:
        """Extraction expériences détaillées"""
        experiences = []
        
        for exp in work_experience:
            experience = ExperienceProfessionnelle(
                poste=exp.get("position", ""),
                entreprise=exp.get("company", ""),
                duree=exp.get("duration", ""),
                description=exp.get("description"),
                competences_acquises=exp.get("skills_acquired", [])
            )
            experiences.append(experience)
        
        return experiences
    
    def _extract_competences(self, data: Dict) -> CompetencesProfessionnelles:
        """Extraction compétences professionnelles"""
        return CompetencesProfessionnelles(
            competences_techniques=data.get("skills", []),
            logiciels_maitrise=data.get("softwares", []),
            langues=data.get("languages", {}),
            certifications=data.get("certifications", [])
        )
    
    def _extract_attentes(self, questionnaire_data: Optional[Dict]) -> AttentesCandidat:
        """Extraction attentes depuis questionnaire ou défaut"""
        if questionnaire_data:
            return AttentesCandidat(
                salaire_min=questionnaire_data.get("salary_min", 30000),
                salaire_max=questionnaire_data.get("salary_max", 50000),
                salaire_actuel=questionnaire_data.get("current_salary"),
                localisation_preferee=questionnaire_data.get("preferred_location", "Paris"),
                distance_max_km=questionnaire_data.get("max_distance", 30),
                remote_accepte=questionnaire_data.get("remote_ok", False),
                secteurs_preferes=questionnaire_data.get("preferred_sectors", []),
                types_contrat=[TypeContrat.CDI]
            )
        else:
            # Valeurs par défaut raisonnables
            return AttentesCandidat(
                salaire_min=30000,
                salaire_max=50000,
                localisation_preferee="Paris",
                distance_max_km=30,
                remote_accepte=False,
                secteurs_preferes=[],
                types_contrat=[TypeContrat.CDI]
            )
    
    def _extract_motivations(self, questionnaire_data: Optional[Dict]) -> MotivationsCandidat:
        """Extraction motivations depuis questionnaire ou défaut"""
        if questionnaire_data and "raison_ecoute" in questionnaire_data:
            raison_str = questionnaire_data["raison_ecoute"]
            # Conversion string → enum
            for raison in RaisonEcouteCandidat:
                if raison.value.lower() in raison_str.lower():
                    raison_ecoute = raison
                    break
            else:
                raison_ecoute = RaisonEcouteCandidat.POSTE_NE_COINCIDE_PAS  # Défaut
        else:
            raison_ecoute = RaisonEcouteCandidat.POSTE_NE_COINCIDE_PAS  # Défaut
        
        return MotivationsCandidat(
            raison_ecoute=raison_ecoute,
            motivations_principales=questionnaire_data.get("motivations", []) if questionnaire_data else [],
            elements_bloquants_actuels=questionnaire_data.get("blockers", []) if questionnaire_data else [],
            objectifs_carriere=questionnaire_data.get("career_goals") if questionnaire_data else None
        )

# === ADAPTATEUR ENTREPRISE (Système ChatGPT Commitment-) ===

class ChatGPTCommitmentAdapter:
    """🔄 Adaptateur Système ChatGPT Commitment- → Bidirectionnel"""
    
    def __init__(self):
        self.name = "ChatGPT Commitment- Adapter"
        
        # Patterns de parsing pour formats spécifiques
        self.salary_pattern = r'(\d+)K?\s*(?:à|-)?\s*(\d+)K?\s*(?:annuels?|€|euros?)?'
        self.experience_pattern = r'(\d+)\s*ans?\s*-?\s*(\d+)?\s*ans?'
        
        # Mapping types de contrat
        self.contrat_mapping = {
            "CDI": TypeContrat.CDI,
            "CDD": TypeContrat.CDD,
            "Freelance": TypeContrat.FREELANCE,
            "Stage": TypeContrat.STAGE,
            "Alternance": TypeContrat.ALTERNANCE
        }
        
        # Mapping urgence recrutement
        self.urgence_mapping = {
            "critique": UrgenceRecrutement.CRITIQUE,
            "urgent": UrgenceRecrutement.URGENT,
            "normal": UrgenceRecrutement.NORMAL,
            "long terme": UrgenceRecrutement.LONG_TERME
        }
    
    def convert_to_bidirectional(self, chatgpt_output: Union[Dict, ChatGPTCommitmentOutput],
                               questionnaire_data: Optional[Dict] = None) -> BiDirectionalCompanyProfile:
        """🔄 Conversion ChatGPT Commitment- → Bidirectionnel"""
        
        try:
            # Normalisation input
            if isinstance(chatgpt_output, dict):
                data = chatgpt_output
            else:
                data = chatgpt_output.__dict__
            
            logger.info("🔄 Conversion ChatGPT Commitment- → Bidirectionnel")
            logger.info(f"📋 Poste: {data.get('titre', 'N/A')}")
            
            # 1. Informations entreprise
            entreprise = self._extract_entreprise_info(data, questionnaire_data)
            
            # 2. Description du poste (parsing ChatGPT)
            poste = self._extract_poste_description(data)
            
            # 3. Exigences et compétences
            exigences = self._extract_exigences(data)
            
            # 4. Conditions de travail
            conditions = self._extract_conditions(data, questionnaire_data)
            
            # 5. Critères de recrutement
            recrutement = self._extract_criteres_recrutement(questionnaire_data)
            
            # 6. Construction profil bidirectionnel
            entreprise_profile = BiDirectionalCompanyProfile(
                entreprise=entreprise,
                poste=poste,
                exigences=exigences,
                conditions=conditions,
                recrutement=recrutement,
                parsing_source="chatgpt_commitment",
                fiche_poste_originale=data.get("fiche_poste_originale"),
                badges_auto_rempli=data.get("badges_auto_rempli", ["Auto-rempli"]),
                parsed_at=datetime.now(),
                confidence_score=data.get("parsing_confidence", 0.85)
            )
            
            logger.info(f"✅ Entreprise convertie: {entreprise.nom} - {poste.titre}")
            logger.info(f"📊 Confiance parsing: {data.get('parsing_confidence', 0.85)}")
            logger.info(f"🏷️ Badges: {data.get('badges_auto_rempli', ['Auto-rempli'])}")
            
            return entreprise_profile
            
        except Exception as e:
            logger.error(f"❌ Erreur conversion ChatGPT Commitment-: {e}")
            raise
    
    def _extract_entreprise_info(self, data: Dict, questionnaire_data: Optional[Dict]) -> InformationsEntreprise:
        """Extraction informations entreprise"""
        
        # Extraction depuis questionnaire si disponible
        if questionnaire_data:
            nom = questionnaire_data.get("company_name", "Entreprise")
            secteur = questionnaire_data.get("sector", "Non spécifié")
            taille = questionnaire_data.get("company_size")
            description = questionnaire_data.get("company_description")
            site_web = questionnaire_data.get("website")
        else:
            # Fallback sur données parsing
            nom = "Entreprise"  # À extraire du contexte
            secteur = self._infer_secteur(data)
        
        return InformationsEntreprise(
            nom=nom,
            secteur=secteur,
            taille=taille if questionnaire_data else None,
            localisation=data.get("localisation", ""),
            description=description if questionnaire_data else None,
            site_web=site_web if questionnaire_data else None
        )
    
    def _extract_poste_description(self, data: Dict) -> DescriptionPoste:
        """Extraction description poste avec parsing ChatGPT"""
        
        # Parsing salaire format "35K à 38K annuels"
        salaire_min, salaire_max = self._parse_salaire(data.get("salaire", ""))
        
        # Type de contrat
        type_contrat = self.contrat_mapping.get(data.get("contrat", "CDI"), TypeContrat.CDI)
        
        return DescriptionPoste(
            titre=data.get("titre", ""),
            localisation=data.get("localisation", ""),
            type_contrat=type_contrat,
            salaire_min=salaire_min,
            salaire_max=salaire_max,
            description=data.get("description"),
            missions_principales=data.get("missions", []),
            competences_requises=data.get("competences_requises", [])
        )
    
    def _extract_exigences(self, data: Dict) -> ExigencesPoste:
        """Extraction exigences poste"""
        return ExigencesPoste(
            experience_requise=data.get("experience_requise", ""),
            competences_obligatoires=data.get("competences_requises", [])[:3],  # Top 3 obligatoires
            competences_souhaitees=data.get("competences_requises", [])[3:],    # Autres souhaitées
            formations_requises=data.get("formations", []),
            langues_requises=data.get("langues", {})
        )
    
    def _extract_conditions(self, data: Dict, questionnaire_data: Optional[Dict]) -> ConditionsTravail:
        """Extraction conditions de travail"""
        return ConditionsTravail(
            horaires=questionnaire_data.get("horaires") if questionnaire_data else None,
            remote_possible=questionnaire_data.get("remote_possible", False) if questionnaire_data else False,
            avantages=data.get("avantages", []),
            environnement_travail=questionnaire_data.get("work_environment") if questionnaire_data else None
        )
    
    def _extract_criteres_recrutement(self, questionnaire_data: Optional[Dict]) -> CriteresRecrutement:
        """Extraction critères de recrutement"""
        if questionnaire_data:
            urgence_str = questionnaire_data.get("urgence", "normal").lower()
            urgence = self.urgence_mapping.get(urgence_str, UrgenceRecrutement.NORMAL)
            
            return CriteresRecrutement(
                urgence=urgence,
                criteres_prioritaires=questionnaire_data.get("priority_criteria", []),
                criteres_eliminatoires=questionnaire_data.get("eliminatory_criteria", []),
                nombre_postes=questionnaire_data.get("positions_count", 1)
            )
        else:
            return CriteresRecrutement(
                urgence=UrgenceRecrutement.NORMAL,
                criteres_prioritaires=["competences_techniques", "experience"],
                criteres_eliminatoires=[],
                nombre_postes=1
            )
    
    def _parse_salaire(self, salaire_str: str) -> tuple[Optional[int], Optional[int]]:
        """Parse format salaire ChatGPT '35K à 38K annuels' → (35000, 38000)"""
        if not salaire_str:
            return None, None
        
        try:
            match = re.search(self.salary_pattern, salaire_str, re.IGNORECASE)
            if match:
                min_sal = int(match.group(1))
                max_sal = int(match.group(2)) if match.group(2) else min_sal
                
                # Conversion K → euros si nécessaire
                if min_sal < 1000:  # Probablement en K
                    min_sal *= 1000
                if max_sal < 1000:
                    max_sal *= 1000
                
                return min_sal, max_sal
            
            # Fallback : essayer de trouver un nombre unique
            single_match = re.search(r'(\d+)K?', salaire_str)
            if single_match:
                salary = int(single_match.group(1))
                if salary < 1000:
                    salary *= 1000
                return salary, salary
            
            return None, None
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur parsing salaire '{salaire_str}': {e}")
            return None, None
    
    def _infer_secteur(self, data: Dict) -> str:
        """Inférence secteur depuis données poste"""
        titre = data.get("titre", "").lower()
        competences = " ".join(data.get("competences_requises", [])).lower()
        
        # Patterns sectoriels
        if any(word in titre + competences for word in ["comptable", "cegid", "fiscal", "comptabilité"]):
            return "Comptabilité"
        elif any(word in titre + competences for word in ["développeur", "python", "javascript", "web"]):
            return "Informatique"
        elif any(word in titre + competences for word in ["marketing", "communication", "digital"]):
            return "Marketing"
        elif any(word in titre + competences for word in ["vente", "commercial", "client"]):
            return "Commercial"
        else:
            return "Autre"

# === FACTORY ADAPTER BIDIRECTIONNEL ===

class BiDirectionalAdapterFactory:
    """🏗️ Factory pour création des adaptateurs"""
    
    @staticmethod
    def create_enhanced_parser_adapter() -> EnhancedParserV4Adapter:
        """Crée adaptateur Enhanced Universal Parser v4.0"""
        return EnhancedParserV4Adapter()
    
    @staticmethod
    def create_chatgpt_commitment_adapter() -> ChatGPTCommitmentAdapter:
        """Crée adaptateur ChatGPT Commitment-"""
        return ChatGPTCommitmentAdapter()
    
    @staticmethod
    def create_full_pipeline():
        """Crée pipeline complet de conversion"""
        return {
            "candidat_adapter": EnhancedParserV4Adapter(),
            "entreprise_adapter": ChatGPTCommitmentAdapter()
        }

# === SERVICE D'ORCHESTRATION ===

class CommitmentNextvisionBridge:
    """🌉 Bridge principal Commitment- ↔ Nextvision"""
    
    def __init__(self):
        self.candidat_adapter = EnhancedParserV4Adapter()
        self.entreprise_adapter = ChatGPTCommitmentAdapter()
        
        # Stats bridge
        self.stats = {
            "candidats_converted": 0,
            "entreprises_converted": 0,
            "total_processing_time": 0.0,
            "errors_count": 0
        }
    
    def convert_candidat_from_commitment(self, parser_output: Dict,
                                       questionnaire_data: Optional[Dict] = None) -> BiDirectionalCandidateProfile:
        """🔄 Conversion candidat Enhanced Parser → Bidirectionnel"""
        start_time = time.time()  # ✅ time maintenant importé
        
        try:
            candidat = self.candidat_adapter.convert_to_bidirectional(parser_output, questionnaire_data)
            
            processing_time = time.time() - start_time  # ✅ time maintenant importé
            self.stats["candidats_converted"] += 1
            self.stats["total_processing_time"] += processing_time
            
            logger.info(f"✅ Candidat converti en {processing_time*1000:.2f}ms")
            return candidat
            
        except Exception as e:
            self.stats["errors_count"] += 1
            logger.error(f"❌ Erreur conversion candidat: {e}")
            raise
    
    def convert_entreprise_from_commitment(self, chatgpt_output: Dict,
                                         questionnaire_data: Optional[Dict] = None) -> BiDirectionalCompanyProfile:
        """🔄 Conversion entreprise ChatGPT → Bidirectionnel"""
        start_time = time.time()  # ✅ time maintenant importé
        
        try:
            entreprise = self.entreprise_adapter.convert_to_bidirectional(chatgpt_output, questionnaire_data)
            
            processing_time = time.time() - start_time  # ✅ time maintenant importé
            self.stats["entreprises_converted"] += 1
            self.stats["total_processing_time"] += processing_time
            
            logger.info(f"✅ Entreprise convertie en {processing_time*1000:.2f}ms")
            return entreprise
            
        except Exception as e:
            self.stats["errors_count"] += 1
            logger.error(f"❌ Erreur conversion entreprise: {e}")
            raise
    
    def get_bridge_stats(self) -> Dict:
        """📊 Statistiques du bridge"""
        total_conversions = self.stats["candidats_converted"] + self.stats["entreprises_converted"]
        avg_time = self.stats["total_processing_time"] / max(1, total_conversions)
        
        return {
            "candidats_converted": self.stats["candidats_converted"],
            "entreprises_converted": self.stats["entreprises_converted"],
            "total_conversions": total_conversions,
            "average_conversion_time_ms": round(avg_time * 1000, 2),
            "errors_count": self.stats["errors_count"],
            "success_rate_percent": round((total_conversions / max(1, total_conversions + self.stats["errors_count"])) * 100, 2)
        }

# === TESTS & VALIDATION ===

if __name__ == "__main__":
    # Test avec données exemple
    
    # Test candidat Enhanced Parser
    enhanced_parser_data = {
        "personal_info": {
            "firstName": "Marie",
            "lastName": "Dupont",
            "email": "marie.dupont@email.com",
            "phone": "+33 6 12 34 56 78"
        },
        "skills": ["Maîtrise du logiciel comptable CEGID", "Gestion comptable et fiscale"],
        "softwares": ["CEGID", "Excel", "SAP"],
        "languages": {"Français": "Natif", "Anglais": "Courant"},
        "experience": {"total_years": 7},
        "work_experience": [
            {
                "position": "Comptable Senior",
                "company": "Cabinet ABC",
                "duration": "3 ans",
                "skills_acquired": ["CEGID", "Fiscalité"]
            }
        ],
        "parsing_confidence": 0.92
    }
    
    # Test entreprise ChatGPT
    chatgpt_data = {
        "titre": "Comptable Unique H/F",
        "localisation": "Paris 8ème",
        "contrat": "CDI",
        "salaire": "35K à 38K annuels",
        "competences_requises": ["Maîtrise du logiciel comptable CEGID", "Gestion comptable et fiscale"],
        "experience_requise": "5 ans - 10 ans",
        "missions": ["Tenue comptabilité complète", "Déclarations fiscales"],
        "avantages": ["Tickets restaurant", "Mutuelle"],
        "badges_auto_rempli": ["Auto-rempli"],
        "parsing_confidence": 0.88
    }
    
    # Test bridge
    bridge = CommitmentNextvisionBridge()
    
    print("🌉 === TEST BRIDGE COMMITMENT- ↔ NEXTVISION ===")
    
    # Test candidat
    candidat = bridge.convert_candidat_from_commitment(enhanced_parser_data)
    print(f"👤 Candidat: {candidat.personal_info.firstName} {candidat.personal_info.lastName}")
    print(f"🎯 Raison écoute: {candidat.motivations.raison_ecoute.value}")
    
    # Test entreprise
    entreprise = bridge.convert_entreprise_from_commitment(chatgpt_data)
    print(f"🏢 Entreprise: {entreprise.entreprise.nom} - {entreprise.poste.titre}")
    print(f"⚡ Urgence: {entreprise.recrutement.urgence.value}")
    
    # Stats
    stats = bridge.get_bridge_stats()
    print(f"📊 Stats bridge: {stats}")
    
    print("✅ Tests bridge réussis!")
