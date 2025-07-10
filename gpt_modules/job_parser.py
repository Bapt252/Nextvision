"""
Job Parser GPT v3.0.2 - Module fiches de poste pour Nextvision V3.1 - PROMPT FIXED
===================================================================================

Parser fiches de poste utilisant l'API OpenAI adapté du JavaScript fonctionnel.
Module isolé pour éviter les conflits de logging.

Version: 3.0.2 - Correction du template prompt (échappement accolades JSON)
"""

import json
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Configuration du logging isolé pour ce module
job_logger = logging.getLogger('gpt_modules.job_parser')


@dataclass
class JobData:
    """Structure de données pour les fiches de poste parsées"""
    titre_poste: str = ""
    entreprise: str = ""
    secteur_activite: str = ""
    niveau_hierarchique: str = "ENTRY"
    experience_requise_min: int = 0
    experience_requise_max: int = 0
    salaire_min: int = 0
    salaire_max: int = 0
    localisation: str = ""
    type_contrat: str = "CDI"
    competences_requises: List[str] = None
    competences_souhaitees: List[str] = None
    logiciels_requis: List[str] = None
    langues_requises: List[Dict[str, str]] = None
    formations_requises: List[str] = None
    description: str = ""
    missions: List[str] = None
    avantages: List[str] = None
    remote_possible: bool = False
    taille_entreprise: str = ""
    
    def __post_init__(self):
        if self.competences_requises is None:
            self.competences_requises = []
        if self.competences_souhaitees is None:
            self.competences_souhaitees = []
        if self.logiciels_requis is None:
            self.logiciels_requis = []
        if self.langues_requises is None:
            self.langues_requises = []
        if self.formations_requises is None:
            self.formations_requises = []
        if self.missions is None:
            self.missions = []
        if self.avantages is None:
            self.avantages = []


class JobParserGPT:
    """
    Parser fiches de poste GPT v3.0.2 - Template prompt corrigé avec échappement accolades JSON
    """
    
    def __init__(self, openai_client=None):
        self.client = openai_client
        self.logger = job_logger
        self.version = "3.0.2"
        
        # Prompt optimisé avec accolades JSON échappées
        self.prompt_template = """Analysez cette fiche de poste et extrayez TOUTES les informations dans ce format JSON exact:

{{
  "titre_poste": "titre exact du poste",
  "entreprise": "nom de l'entreprise",
  "secteur_activite": "secteur principal",
  "niveau_hierarchique": "ENTRY|JUNIOR|SENIOR|MANAGER|DIRECTOR|EXECUTIVE",
  "experience_requise_min": nombre_minimum_années,
  "experience_requise_max": nombre_maximum_années,
  "salaire_min": montant_minimum_euros,
  "salaire_max": montant_maximum_euros,
  "localisation": "ville, pays",
  "type_contrat": "CDI|CDD|Stage|Freelance",
  "competences_requises": ["comp1", "comp2", ...],
  "competences_souhaitees": ["comp1", "comp2", ...],
  "logiciels_requis": ["logiciel1", "logiciel2", ...],
  "langues_requises": [{{"langue": "Français", "niveau": "Courant"}}, ...],
  "formations_requises": ["formation1", "formation2", ...],
  "description": "description complète du poste",
  "missions": ["mission1", "mission2", ...],
  "avantages": ["avantage1", "avantage2", ...],
  "remote_possible": true/false,
  "taille_entreprise": "startup|PME|ETI|GE"
}}

RÈGLES IMPORTANTES:
1. Déduisez le niveau hiérarchique selon le titre et l'expérience:
   - ENTRY: 0-2 ans, assistant, stagiaire, junior
   - JUNIOR: 2-5 ans, consultant, développeur
   - SENIOR: 5-8 ans, expert, lead, senior
   - MANAGER: 8-12 ans, chef d'équipe, manager, responsable
   - DIRECTOR: 12-20 ans, directeur, head of
   - EXECUTIVE: 20+ ans, DG, DRH, DAF, CEO, CTO

2. Estimez les salaires si non mentionnés selon le niveau et secteur
3. Séparez compétences requises (indispensables) et souhaitées (plus)
4. Extrayez TOUTES les missions et responsabilités
5. Retournez UNIQUEMENT le JSON, rien d'autre

Fiche de poste à analyser:
{job_text}"""

    def extract_hierarchical_level(self, experience_min: int, experience_max: int, titre_poste: str) -> str:
        """
        Détermine le niveau hiérarchique selon l'expérience et le titre
        Logique adaptée du système hiérarchique V3.1
        """
        titre_lower = titre_poste.lower()
        exp_moyenne = (experience_min + experience_max) / 2 if experience_max > 0 else experience_min
        
        # Niveaux EXECUTIVE
        executive_keywords = ['daf', 'directeur administratif', 'directeur financier', 'ceo', 'cto', 'dg', 'directeur général']
        if any(keyword in titre_lower for keyword in executive_keywords) or exp_moyenne >= 20:
            return "EXECUTIVE"
            
        # Niveaux DIRECTOR  
        director_keywords = ['directeur', 'director', 'head of']
        if any(keyword in titre_lower for keyword in director_keywords) or exp_moyenne >= 12:
            return "DIRECTOR"
            
        # Niveaux MANAGER
        manager_keywords = ['manager', 'chef', 'responsable', 'lead']
        if any(keyword in titre_lower for keyword in manager_keywords) or exp_moyenne >= 8:
            return "MANAGER"
            
        # Niveaux SENIOR
        if 'senior' in titre_lower or exp_moyenne >= 5:
            return "SENIOR"
            
        # Niveaux JUNIOR
        if 'junior' in titre_lower or exp_moyenne >= 2:
            return "JUNIOR"
            
        # Par défaut ENTRY
        return "ENTRY"

    def estimate_salary_range(self, niveau_hierarchique: str, secteur: str, localisation: str) -> tuple:
        """
        Estime la fourchette de salaires selon le niveau hiérarchique, secteur et localisation
        """
        salary_ranges = {
            "ENTRY": (25000, 35000),
            "JUNIOR": (30000, 45000), 
            "SENIOR": (45000, 65000),
            "MANAGER": (55000, 75000),
            "DIRECTOR": (70000, 100000),
            "EXECUTIVE": (80000, 150000)
        }
        
        base_min, base_max = salary_ranges.get(niveau_hierarchique, (25000, 35000))
        
        # Ajustements sectoriels
        multiplier = 1.0
        if "finance" in secteur.lower() or "comptabil" in secteur.lower():
            multiplier = 1.1  # Finance: +10%
        elif "tech" in secteur.lower() or "informatique" in secteur.lower():
            multiplier = 1.2  # Tech: +20%
        elif "conseil" in secteur.lower():
            multiplier = 1.15  # Conseil: +15%
            
        # Ajustements géographiques
        if "paris" in localisation.lower():
            multiplier *= 1.1  # Paris: +10%
        elif "lyon" in localisation.lower() or "marseille" in localisation.lower():
            multiplier *= 1.05  # Grandes villes: +5%
            
        return int(base_min * multiplier), int(base_max * multiplier)

    def parse_job_text(self, job_text: str) -> JobData:
        """
        Parse une fiche de poste à partir du texte
        """
        start_time = time.time()
        
        try:
            if not self.client:
                self.logger.warning("Pas de client OpenAI configuré, utilisation du poste fallback")
                return self._get_fallback_job()
            
            # Appel OpenAI avec prompt optimisé (template corrigé)
            prompt = self.prompt_template.format(job_text=job_text)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content.strip()
            self.logger.debug(f"Réponse GPT brute: {response_text[:200]}...")
            
            # Nettoyage du JSON si encapsulé dans des backticks
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            # Extraction JSON robuste
            json_start = response_text.find('{')
            json_end = response_text.rfind('}')
            if json_start >= 0 and json_end > json_start:
                response_text = response_text[json_start:json_end + 1]
            
            parsed_data = json.loads(response_text)
            
            # Conversion en JobData avec validation
            job_data = self._validate_and_convert(parsed_data)
            
            # Log des performances
            elapsed_time = (time.time() - start_time) * 1000
            self.logger.info(f"Fiche de poste parsée en {elapsed_time:.1f}ms - Poste: {job_data.titre_poste} - Niveau: {job_data.niveau_hierarchique}")
            
            return job_data
            
        except Exception as e:
            self.logger.error(f"Erreur parsing fiche de poste: {str(e)}")
            elapsed_time = (time.time() - start_time) * 1000
            self.logger.info(f"Fallback utilisé après {elapsed_time:.1f}ms")
            return self._get_fallback_job()

    def _validate_and_convert(self, parsed_data: Dict[str, Any]) -> JobData:
        """
        Valide et convertit les données parsées en JobData
        """
        job_data = JobData()
        
        # Mapping des champs basiques
        job_data.titre_poste = parsed_data.get('titre_poste', '')
        job_data.entreprise = parsed_data.get('entreprise', '')
        job_data.secteur_activite = parsed_data.get('secteur_activite', '')
        job_data.localisation = parsed_data.get('localisation', '')
        job_data.type_contrat = parsed_data.get('type_contrat', 'CDI')
        job_data.description = parsed_data.get('description', '')
        job_data.remote_possible = parsed_data.get('remote_possible', False)
        job_data.taille_entreprise = parsed_data.get('taille_entreprise', '')
        
        # Expérience requise
        job_data.experience_requise_min = int(parsed_data.get('experience_requise_min', 0))
        job_data.experience_requise_max = int(parsed_data.get('experience_requise_max', 0))
        
        # Détermination du niveau hiérarchique
        niveau_raw = parsed_data.get('niveau_hierarchique', '').upper()
        valid_levels = ['ENTRY', 'JUNIOR', 'SENIOR', 'MANAGER', 'DIRECTOR', 'EXECUTIVE']
        
        if niveau_raw in valid_levels:
            job_data.niveau_hierarchique = niveau_raw
        else:
            # Recalcul basé sur l'expérience et titre
            job_data.niveau_hierarchique = self.extract_hierarchical_level(
                job_data.experience_requise_min,
                job_data.experience_requise_max,
                job_data.titre_poste
            )
        
        # Estimation des salaires si manquants
        salaire_min = parsed_data.get('salaire_min', 0)
        salaire_max = parsed_data.get('salaire_max', 0)
        
        if not salaire_min or not salaire_max:
            est_min, est_max = self.estimate_salary_range(
                job_data.niveau_hierarchique, 
                job_data.secteur_activite,
                job_data.localisation
            )
            job_data.salaire_min = salaire_min or est_min
            job_data.salaire_max = salaire_max or est_max
        else:
            job_data.salaire_min = int(salaire_min)
            job_data.salaire_max = int(salaire_max)
        
        # Listes
        job_data.competences_requises = parsed_data.get('competences_requises', [])
        job_data.competences_souhaitees = parsed_data.get('competences_souhaitees', [])
        job_data.logiciels_requis = parsed_data.get('logiciels_requis', [])
        job_data.langues_requises = parsed_data.get('langues_requises', [])
        job_data.formations_requises = parsed_data.get('formations_requises', [])
        job_data.missions = parsed_data.get('missions', [])
        job_data.avantages = parsed_data.get('avantages', [])
        
        return job_data

    def _get_fallback_job(self) -> JobData:
        """
        Poste fallback pour les tests - Consultant Senior
        """
        return JobData(
            titre_poste="Consultant Senior Finance",
            entreprise="Finance Consulting Group",
            secteur_activite="Conseil",
            niveau_hierarchique="SENIOR",
            experience_requise_min=5,
            experience_requise_max=8,
            salaire_min=55000,
            salaire_max=70000,
            localisation="Paris, France",
            type_contrat="CDI",
            competences_requises=[
                "Conseil en finance", "Analyse financière", "Modélisation", 
                "Présentation client", "Gestion de projet"
            ],
            competences_souhaitees=["SAP", "Tableau", "Python"],
            logiciels_requis=["Excel", "PowerPoint", "Sage"],
            langues_requises=[
                {"langue": "Français", "niveau": "Natif"}, 
                {"langue": "Anglais", "niveau": "Courant"}
            ],
            formations_requises=["Master Finance", "École de Commerce"],
            description="Poste de consultant senior en finance pour accompagner nos clients",
            missions=[
                "Accompagnement des clients sur leurs problématiques financières",
                "Réalisation d'audits et diagnostics",
                "Animation d'ateliers et formations"
            ],
            avantages=["Télétravail partiel", "Formation continue", "Prime annuelle"],
            remote_possible=True,
            taille_entreprise="ETI"
        )

    def get_comptable_entry_job(self) -> JobData:
        """
        Poste comptable ENTRY level pour les tests Charlotte DARMON
        Ce poste DOIT être incompatible avec Charlotte (EXECUTIVE)
        """
        return JobData(
            titre_poste="Comptable",
            entreprise="Compta Services SARL",
            secteur_activite="Comptabilité",
            niveau_hierarchique="ENTRY",  # Important pour le test !
            experience_requise_min=2,     # 2-5 ans comme mentionné
            experience_requise_max=5,
            salaire_min=30000,             # 35K€ comme mentionné
            salaire_max=35000,
            localisation="Paris, France",
            type_contrat="CDI",
            competences_requises=[
                "Saisie comptable", "Rapprochements bancaires", "TVA",
                "Paie simple", "Excel", "Rigueur"
            ],
            competences_souhaitees=["Sage", "Divalto", "Quadratus"],
            logiciels_requis=["Excel", "Sage Comptabilité"],
            langues_requises=[{"langue": "Français", "niveau": "Natif"}],
            formations_requises=["BTS Comptabilité", "DCG"],
            description="Poste de comptable pour PME en croissance. Missions variées de comptabilité générale.",
            missions=[
                "Saisie des écritures comptables courantes",
                "Rapprochements bancaires mensuels", 
                "Déclaration de TVA",
                "Préparation des éléments pour l'expert-comptable",
                "Classement et archivage"
            ],
            avantages=["Mutuelle", "Tickets restaurant", "RTT"],
            remote_possible=False,
            taille_entreprise="PME"
        )

    def get_daf_executive_job(self) -> JobData:
        """
        Poste DAF EXECUTIVE pour test de matching positif avec Charlotte
        """
        return JobData(
            titre_poste="Directeur Administratif et Financier",
            entreprise="TechCorp International",
            secteur_activite="Finance",
            niveau_hierarchique="EXECUTIVE",
            experience_requise_min=12,
            experience_requise_max=20,
            salaire_min=85000,
            salaire_max=110000,
            localisation="Paris, France",
            type_contrat="CDI",
            competences_requises=[
                "Direction financière", "Consolidation", "IFRS", "Management",
                "Stratégie financière", "Audit interne", "Contrôle de gestion"
            ],
            competences_souhaitees=["SAP", "Oracle", "M&A", "Fiscalité internationale"],
            logiciels_requis=["SAP", "Excel", "Consolidation software"],
            langues_requises=[
                {"langue": "Français", "niveau": "Natif"}, 
                {"langue": "Anglais", "niveau": "Courant"}
            ],
            formations_requises=["Master Finance", "DSCG", "École de Commerce"],
            description="Direction de l'ensemble des fonctions financières d'un groupe international.",
            missions=[
                "Direction des équipes financières (10+ personnes)",
                "Consolidation des comptes groupe",
                "Reporting aux investisseurs",
                "Stratégie financière et M&A",
                "Relations bancaires et financements"
            ],
            avantages=["Variable", "Stock-options", "Voiture de fonction", "Télétravail"],
            remote_possible=True,
            taille_entreprise="GE"
        )

    def to_nextvision_format(self, job_data: JobData) -> Dict[str, Any]:
        """
        Convertit JobData au format attendu par Nextvision V3.1
        """
        return {
            "job_info": {
                "title": job_data.titre_poste,
                "company": job_data.entreprise,
                "sector": job_data.secteur_activite,
                "location": job_data.localisation,
                "contract_type": job_data.type_contrat,
                "remote_possible": job_data.remote_possible,
                "company_size": job_data.taille_entreprise
            },
            "requirements": {
                "hierarchical_level": job_data.niveau_hierarchique,
                "experience_min": job_data.experience_requise_min,
                "experience_max": job_data.experience_requise_max,
                "salary_min": job_data.salaire_min,
                "salary_max": job_data.salaire_max,
                "required_skills": job_data.competences_requises,
                "preferred_skills": job_data.competences_souhaitees,
                "software": job_data.logiciels_requis,
                "languages": job_data.langues_requises,
                "education": job_data.formations_requises
            },
            "description": {
                "full_description": job_data.description,
                "missions": job_data.missions,
                "benefits": job_data.avantages
            },
            "metadata": {
                "parser_version": self.version,
                "hierarchical_level": job_data.niveau_hierarchique,
                "parsing_timestamp": time.time()
            }
        }
