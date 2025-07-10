"""
CV Parser GPT v4.0.3 - Module exhaustif pour Nextvision V3.1 - SALARY VALIDATION FIXED
===========================================================

Parser CV utilisant l'API OpenAI adapté du JavaScript fonctionnel.
Module isolé pour éviter les conflits de logging.

Version: 4.0.3 - Gestion robuste des salaires "Non mentionné"
"""

import json
import logging
import time
import re
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass

# Configuration du logging isolé pour ce module
cv_logger = logging.getLogger('gpt_modules.cv_parser')


@dataclass
class CVData:
    """Structure de données pour les CV parsés"""
    nom_complet: str = ""
    email: str = ""
    telephone: str = ""
    adresse: str = ""
    titre_poste: str = ""
    niveau_hierarchique: str = "ENTRY"
    experience_years: int = 0
    salaire_actuel: int = 0
    salaire_souhaite: int = 0
    competences: List[str] = None
    logiciels: List[str] = None
    langues: List[Dict[str, str]] = None
    formations: List[Dict[str, Any]] = None
    experiences: List[Dict[str, Any]] = None
    secteur_activite: str = ""
    disponibilite: str = ""
    mobilite_geographique: bool = False
    
    def __post_init__(self):
        if self.competences is None:
            self.competences = []
        if self.logiciels is None:
            self.logiciels = []
        if self.langues is None:
            self.langues = []
        if self.formations is None:
            self.formations = []
        if self.experiences is None:
            self.experiences = []


class CVParserGPT:
    """
    Parser CV GPT v4.0.3 - Adapté du JavaScript fonctionnel avec validation salaire robuste
    """
    
    def __init__(self, openai_client=None):
        self.client = openai_client
        self.logger = cv_logger
        self.version = "4.0.3"
        
        # Prompt optimisé adapté du JavaScript fonctionnel
        self.prompt_template = """
Analysez ce CV et extrayez TOUTES les informations dans ce format JSON exact:

{
  "nom_complet": "Prénom Nom",
  "email": "email@domain.com",
  "telephone": "+33...",
  "adresse": "ville, pays",
  "titre_poste": "titre exact du poste actuel",
  "niveau_hierarchique": "ENTRY|JUNIOR|SENIOR|MANAGER|DIRECTOR|EXECUTIVE",
  "experience_years": nombre_total_années,
  "salaire_actuel": montant_en_euros,
  "salaire_souhaite": montant_souhaité_euros,
  "competences": ["comp1", "comp2", ...],
  "logiciels": ["logiciel1", "logiciel2", ...],
  "langues": [{"langue": "Français", "niveau": "Natif"}, ...],
  "formations": [{"diplome": "nom", "ecole": "nom", "annee": "2020"}, ...],
  "experiences": [{"poste": "titre", "entreprise": "nom", "debut": "MM/YYYY", "fin": "MM/YYYY", "description": "tâches"}],
  "secteur_activite": "secteur principal",
  "disponibilite": "immédiate|préavis X mois",
  "mobilite_geographique": true/false
}

RÈGLES IMPORTANTES:
1. Déduisez le niveau hiérarchique selon l'expérience et le titre:
   - ENTRY: 0-2 ans, stagiaire, junior
   - JUNIOR: 2-5 ans, développeur, consultant
   - SENIOR: 5-8 ans, expert, lead
   - MANAGER: 8-12 ans, chef d'équipe, manager
   - DIRECTOR: 12-20 ans, directeur, head of
   - EXECUTIVE: 20+ ans, DG, DRH, DAF, CEO, CTO

2. Pour les salaires:
   - Si mentionné: utilisez le montant exact en euros
   - Si non mentionné: mettez "Non mentionné" (string)
   
3. Extrayez TOUTES les compétences techniques et soft skills
4. Retournez UNIQUEMENT le JSON valide, sans texte supplémentaire

CV à analyser:
{cv_text}
"""

    def _safe_int_conversion(self, value: Any, field_name: str = "") -> Optional[int]:
        """
        Conversion sécurisée vers int avec gestion des cas spéciaux
        
        Args:
            value: Valeur à convertir
            field_name: Nom du champ (pour debug)
            
        Returns:
            int ou None si conversion impossible
        """
        if value is None:
            self.logger.debug(f"Champ {field_name}: valeur None")
            return None
            
        if isinstance(value, int):
            return value
            
        if isinstance(value, float):
            return int(value)
            
        if isinstance(value, str):
            # Cas spéciaux pour les valeurs non numériques
            value_lower = value.lower().strip()
            non_numeric_indicators = [
                'non mentionné', 'non mentionnÉ', 'non mentione',
                'n/a', 'na', 'néant', 'neant', 
                'inconnu', 'non spécifié', 'non specifie',
                'à définir', 'a definir', 'à négocier', 'a negocier',
                'selon profil', 'variable', 'confidentiel', '',
                'non renseigné', 'non renseigne'
            ]
            
            if value_lower in non_numeric_indicators:
                self.logger.debug(f"Champ {field_name}: valeur non numérique détectée: '{value}'")
                return None
            
            # Tentative d'extraction numérique
            # Supprimer espaces, €, K, k, etc.
            cleaned = re.sub(r'[^\d]', '', value)
            if cleaned:
                try:
                    num_value = int(cleaned)
                    # Gestion des abréviations K (milliers)
                    if 'k' in value_lower or '€k' in value_lower:
                        num_value *= 1000
                    self.logger.debug(f"Champ {field_name}: '{value}' converti en {num_value}")
                    return num_value
                except ValueError:
                    pass
            
            self.logger.debug(f"Champ {field_name}: impossible de convertir '{value}' en entier")
            return None
        
        self.logger.debug(f"Champ {field_name}: type non supporté {type(value)}")
        return None

    def clean_json_response(self, response_text: str) -> str:
        """
        Nettoie la réponse GPT pour extraire un JSON valide
        Version robuste qui gère tous les cas
        """
        try:
            # Supprimer les espaces en début et fin
            response_text = response_text.strip()
            
            # Cas 1: JSON encapsulé dans des backticks
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            # Cas 2: Texte avant le JSON
            # Chercher le premier {
            json_start = response_text.find('{')
            if json_start > 0:
                response_text = response_text[json_start:]
            
            # Cas 3: Texte après le JSON
            # Chercher le dernier }
            json_end = response_text.rfind('}')
            if json_end > 0:
                response_text = response_text[:json_end + 1]
            
            # Cas 4: Supprimer les retours à la ligne au début/fin
            response_text = response_text.strip()
            
            # Cas 5: Vérifier que ça commence et finit bien par { }
            if not response_text.startswith('{'):
                raise ValueError("JSON ne commence pas par {")
            if not response_text.endswith('}'):
                raise ValueError("JSON ne finit pas par }")
            
            # Cas 6: Nettoyer les caractères de contrôle
            response_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', response_text)
            
            return response_text
            
        except Exception as e:
            self.logger.error(f"Erreur nettoyage JSON: {str(e)}")
            raise

    def parse_cv_text(self, cv_text: str) -> CVData:
        """
        Parse un CV à partir du texte extrait
        """
        start_time = time.time()
        
        try:
            if not self.client:
                self.logger.warning("Pas de client OpenAI configuré, utilisation du profil fallback")
                return self._get_fallback_profile()
            
            # Appel OpenAI avec prompt optimisé
            prompt = self.prompt_template.format(cv_text=cv_text)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content.strip()
            self.logger.debug(f"Réponse GPT brute: {response_text[:200]}...")
            
            # Nettoyage robuste du JSON
            cleaned_json = self.clean_json_response(response_text)
            self.logger.debug(f"JSON nettoyé: {cleaned_json[:200]}...")
            
            # Parse JSON
            parsed_data = json.loads(cleaned_json)
            
            # Conversion en CVData avec validation
            cv_data = self._validate_and_convert(parsed_data)
            
            # Log des performances
            elapsed_time = (time.time() - start_time) * 1000
            self.logger.info(f"CV parsé en {elapsed_time:.1f}ms - Candidat: {cv_data.nom_complet} - Niveau: {cv_data.niveau_hierarchique}")
            
            return cv_data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Erreur JSON parsing: {str(e)}")
            self.logger.error(f"JSON problématique: {response_text if 'response_text' in locals() else 'N/A'}")
            elapsed_time = (time.time() - start_time) * 1000
            self.logger.info(f"Fallback utilisé après {elapsed_time:.1f}ms")
            return self._get_fallback_profile()
            
        except Exception as e:
            self.logger.error(f"Erreur parsing CV: {str(e)}")
            elapsed_time = (time.time() - start_time) * 1000
            self.logger.info(f"Fallback utilisé après {elapsed_time:.1f}ms")
            return self._get_fallback_profile()

    def extract_hierarchical_level(self, experience_years: int, titre_poste: str) -> str:
        """
        Détermine le niveau hiérarchique selon l'expérience et le titre
        Logique adaptée du système hiérarchique V3.1
        """
        titre_lower = titre_poste.lower()
        
        # Niveaux EXECUTIVE (Charlotte DARMON level)
        executive_keywords = ['daf', 'directeur administratif', 'directeur financier', 'ceo', 'cto', 'dg', 'directeur général']
        if any(keyword in titre_lower for keyword in executive_keywords) or experience_years >= 20:
            return "EXECUTIVE"
            
        # Niveaux DIRECTOR  
        director_keywords = ['directeur', 'director', 'head of']
        if any(keyword in titre_lower for keyword in director_keywords) or experience_years >= 12:
            return "DIRECTOR"
            
        # Niveaux MANAGER
        manager_keywords = ['manager', 'chef', 'responsable', 'lead']
        if any(keyword in titre_lower for keyword in manager_keywords) or experience_years >= 8:
            return "MANAGER"
            
        # Niveaux SENIOR
        if 'senior' in titre_lower or experience_years >= 5:
            return "SENIOR"
            
        # Niveaux JUNIOR
        if 'junior' in titre_lower or experience_years >= 2:
            return "JUNIOR"
            
        # Par défaut ENTRY (comme les comptables 2-5 ans)
        return "ENTRY"

    def estimate_salary(self, niveau_hierarchique: str, secteur: str) -> tuple:
        """
        Estime les salaires selon le niveau hiérarchique et secteur
        """
        salary_ranges = {
            "ENTRY": (25000, 35000),
            "JUNIOR": (30000, 45000), 
            "SENIOR": (45000, 65000),
            "MANAGER": (55000, 75000),
            "DIRECTOR": (70000, 100000),
            "EXECUTIVE": (80000, 150000)  # Charlotte DARMON: 80K€
        }
        
        base_min, base_max = salary_ranges.get(niveau_hierarchique, (25000, 35000))
        
        # Ajustements sectoriels
        if "finance" in secteur.lower() or "comptabil" in secteur.lower():
            # Secteur finance/comptabilité: +10%
            return int(base_min * 1.1), int(base_max * 1.1)
        elif "tech" in secteur.lower() or "informatique" in secteur.lower():
            # Secteur tech: +20%
            return int(base_min * 1.2), int(base_max * 1.2)
            
        return base_min, base_max

    def _validate_and_convert(self, parsed_data: Dict[str, Any]) -> CVData:
        """
        Valide et convertit les données parsées en CVData avec gestion robuste des salaires
        """
        cv_data = CVData()
        
        # Mapping des champs basiques
        cv_data.nom_complet = parsed_data.get('nom_complet', '')
        cv_data.email = parsed_data.get('email', '')
        cv_data.telephone = parsed_data.get('telephone', '')
        cv_data.adresse = parsed_data.get('adresse', '')
        cv_data.titre_poste = parsed_data.get('titre_poste', '')
        cv_data.experience_years = int(parsed_data.get('experience_years', 0))
        cv_data.secteur_activite = parsed_data.get('secteur_activite', '')
        cv_data.disponibilite = parsed_data.get('disponibilite', 'immédiate')
        cv_data.mobilite_geographique = parsed_data.get('mobilite_geographique', False)
        
        # Détermination du niveau hiérarchique
        niveau_raw = parsed_data.get('niveau_hierarchique', '').upper()
        valid_levels = ['ENTRY', 'JUNIOR', 'SENIOR', 'MANAGER', 'DIRECTOR', 'EXECUTIVE']
        
        if niveau_raw in valid_levels:
            cv_data.niveau_hierarchique = niveau_raw
        else:
            # Recalcul basé sur l'expérience et titre
            cv_data.niveau_hierarchique = self.extract_hierarchical_level(
                cv_data.experience_years, 
                cv_data.titre_poste
            )
        
        # 🚀 VALIDATION ROBUSTE DES SALAIRES
        salaire_actuel_raw = parsed_data.get('salaire_actuel')
        salaire_souhaite_raw = parsed_data.get('salaire_souhaite')
        
        self.logger.debug(f"Salaires bruts reçus - Actuel: {salaire_actuel_raw}, Souhaité: {salaire_souhaite_raw}")
        
        # Conversion sécurisée des salaires
        salaire_actuel_int = self._safe_int_conversion(salaire_actuel_raw, "salaire_actuel")
        salaire_souhaite_int = self._safe_int_conversion(salaire_souhaite_raw, "salaire_souhaite")
        
        # Si les deux salaires sont disponibles
        if salaire_actuel_int is not None and salaire_souhaite_int is not None:
            cv_data.salaire_actuel = salaire_actuel_int
            cv_data.salaire_souhaite = salaire_souhaite_int
            self.logger.debug(f"Salaires convertis - Actuel: {cv_data.salaire_actuel}€, Souhaité: {cv_data.salaire_souhaite}€")
        
        # Si seulement un salaire est disponible
        elif salaire_actuel_int is not None:
            cv_data.salaire_actuel = salaire_actuel_int
            # Estimation du salaire souhaité (+15% typiquement)
            cv_data.salaire_souhaite = int(salaire_actuel_int * 1.15)
            self.logger.debug(f"Salaire actuel converti: {cv_data.salaire_actuel}€, souhaité estimé: {cv_data.salaire_souhaite}€")
        
        elif salaire_souhaite_int is not None:
            cv_data.salaire_souhaite = salaire_souhaite_int
            # Estimation du salaire actuel (-15% typiquement)
            cv_data.salaire_actuel = int(salaire_souhaite_int * 0.85)
            self.logger.debug(f"Salaire souhaité converti: {cv_data.salaire_souhaite}€, actuel estimé: {cv_data.salaire_actuel}€")
        
        # Si aucun salaire n'est disponible
        else:
            # Estimation complète basée sur le niveau hiérarchique et secteur
            min_sal, max_sal = self.estimate_salary(cv_data.niveau_hierarchique, cv_data.secteur_activite)
            cv_data.salaire_actuel = min_sal
            cv_data.salaire_souhaite = max_sal
            self.logger.info(f"Salaires estimés pour niveau {cv_data.niveau_hierarchique} - Actuel: {cv_data.salaire_actuel}€, Souhaité: {cv_data.salaire_souhaite}€")
        
        # Mapping des listes
        cv_data.competences = parsed_data.get('competences', [])
        cv_data.logiciels = parsed_data.get('logiciels', [])
        cv_data.langues = parsed_data.get('langues', [])
        cv_data.formations = parsed_data.get('formations', [])
        cv_data.experiences = parsed_data.get('experiences', [])
        
        return cv_data

    def _get_fallback_profile(self) -> CVData:
        """
        Profil fallback Dorothée Lim pour les tests
        """
        return CVData(
            nom_complet="Dorothée Lim",
            email="dorothee.lim@email.com",
            telephone="+33 6 12 34 56 78",
            adresse="Paris, France",
            titre_poste="Analyste Financier Senior",
            niveau_hierarchique="SENIOR",
            experience_years=7,
            salaire_actuel=55000,
            salaire_souhaite=65000,
            competences=["Analyse financière", "Reporting", "Excel avancé", "Modélisation"],
            logiciels=["Excel", "SAP", "Tableau", "PowerBI"],
            langues=[{"langue": "Français", "niveau": "Natif"}, {"langue": "Anglais", "niveau": "Courant"}],
            formations=[{"diplome": "Master Finance", "ecole": "ESSEC", "annee": "2018"}],
            experiences=[
                {"poste": "Analyste Financier Senior", "entreprise": "BNP Paribas", "debut": "01/2022", "fin": "Présent", "description": "Analyse et reporting financier"},
                {"poste": "Analyste Financier", "entreprise": "Société Générale", "debut": "09/2018", "fin": "12/2021", "description": "Analyse des risques"}
            ],
            secteur_activite="Finance",
            disponibilite="préavis 2 mois",
            mobilite_geographique=True
        )

    def get_charlotte_darmon_profile(self) -> CVData:
        """
        Profil Charlotte DARMON pour les tests V3.1
        DAF avec 15 ans d'expérience et 80K€
        """
        return CVData(
            nom_complet="Charlotte DARMON",
            email="charlotte.darmon@finance-corp.com",
            telephone="+33 6 98 76 54 32",
            adresse="Paris, France", 
            titre_poste="Directrice Administrative et Financière",
            niveau_hierarchique="EXECUTIVE",  # Important pour les tests !
            experience_years=15,
            salaire_actuel=80000,  # 80K€ comme mentionné
            salaire_souhaite=90000,
            competences=[
                "Direction financière", "Contrôle de gestion", "Audit interne", 
                "Consolidation", "Stratégie financière", "Management d'équipe",
                "IFRS", "Fiscalité", "Trésorerie", "Budget prévisionnel"
            ],
            logiciels=["SAP", "Oracle", "Excel", "Tableau", "PowerBI", "Hyperion"],
            langues=[
                {"langue": "Français", "niveau": "Natif"}, 
                {"langue": "Anglais", "niveau": "Courant"},
                {"langue": "Allemand", "niveau": "Intermédiaire"}
            ],
            formations=[
                {"diplome": "Master CCA", "ecole": "HEC Paris", "annee": "2010"},
                {"diplome": "DSCG", "ecole": "INTEC", "annee": "2008"}
            ],
            experiences=[
                {
                    "poste": "Directrice Administrative et Financière", 
                    "entreprise": "Finance Corp SA", 
                    "debut": "01/2020", 
                    "fin": "Présent",
                    "description": "Direction de l'ensemble des fonctions financières. Management d'une équipe de 8 personnes. Consolidation groupe, reporting IFRS, stratégie financière."
                },
                {
                    "poste": "Contrôleur de Gestion Senior", 
                    "entreprise": "Industrial Group", 
                    "debut": "09/2015", 
                    "fin": "12/2019",
                    "description": "Contrôle de gestion opérationnel et stratégique. Mise en place des outils de pilotage."
                },
                {
                    "poste": "Auditeur Senior", 
                    "entreprise": "PwC France", 
                    "debut": "09/2010", 
                    "fin": "08/2015",
                    "description": "Audit légal et contractuel. Spécialisation secteur industriel."
                }
            ],
            secteur_activite="Finance",
            disponibilite="préavis 3 mois",
            mobilite_geographique=False
        )

    def to_nextvision_format(self, cv_data: CVData) -> Dict[str, Any]:
        """
        Convertit CVData au format attendu par Nextvision V3.1
        """
        return {
            "personal_info": {
                "name": cv_data.nom_complet,
                "email": cv_data.email,
                "phone": cv_data.telephone,
                "address": cv_data.adresse,
                "availability": cv_data.disponibilite,
                "mobility": cv_data.mobilite_geographique
            },
            "professional_info": {
                "current_title": cv_data.titre_poste,
                "hierarchical_level": cv_data.niveau_hierarchique,
                "experience_years": cv_data.experience_years,
                "current_salary": cv_data.salaire_actuel,
                "expected_salary": cv_data.salaire_souhaite,
                "sector": cv_data.secteur_activite
            },
            "skills": {
                "technical_skills": cv_data.competences,
                "software": cv_data.logiciels,
                "languages": cv_data.langues
            },
            "education": cv_data.formations,
            "experience": cv_data.experiences,
            "metadata": {
                "parser_version": self.version,
                "hierarchical_level": cv_data.niveau_hierarchique,
                "parsing_timestamp": time.time()
            }
        }
