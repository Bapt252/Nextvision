"""
🔄 Utilitaires Enrichissement Données NEXTEN
Transformation et enrichissement données Commitment- vers modèles avancés Nextvision

Author: NEXTEN Team
Version: 1.0.0
Integration: Commitment- → Nextvision Bridge
"""

import re
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, date
from dataclasses import dataclass
import json

# Imports des modèles
from ..models.questionnaire_advanced import (
    QuestionnaireCompletAdvanced,
    TimingDisponibilite,
    PreferencesSectorielles,
    ConfigTransport,
    PreferencesContrats,
    RankingMotivations,
    MotivationClassee,
    PourquoiEcouteEnum,
    DisponibiliteEnum,
    EnvironnementTravailEnum,
    TypeContratEnum,
    MoyenTransportEnum,
    MotivationEnum
)
from ..models.candidate_complete import (
    CandidatCompletNexfen,
    CVDataEnriched,
    CompetenceTechnique,
    ExperienceProfessionnelle,
    FormationAcademique,
    LangueCompetence,
    NiveauEnum,
    TypeFormationEnum,
    StatutActiviteEnum
)
from ..models.job_complete import (
    JobDataAdvanced,
    CompetenceRequise,
    MissionPrincipale,
    AvantagesSociaux,
    EnvironnementEntreprise,
    LocalisationPoste,
    ProcessusRecrutement,
    TailleEntrepriseEnum,
    TypeRecrutementEnum,
    NiveauRequis,
    FlexibiliteTravailEnum
)
from ..models.sectoral_analysis import normaliser_secteur, suggerer_secteurs_similaires

# Configuration du logging
logger = logging.getLogger(__name__)

@dataclass
class EnrichmentConfig:
    """⚙️ Configuration pour l'enrichissement des données"""
    auto_complete_missing: bool = True
    use_smart_defaults: bool = True
    normalize_sectors: bool = True
    extract_skills_from_text: bool = True
    infer_experience_levels: bool = True
    calculate_scores: bool = True
    log_transformations: bool = True

class CommitmentDataEnricher:
    """🔄 Enrichisseur de données Commitment- vers modèles avancés"""
    
    def __init__(self, config: Optional[EnrichmentConfig] = None):
        """Initialise l'enrichisseur avec la configuration"""
        self.config = config or EnrichmentConfig()
        self.transformation_log = []
        
        # Dictionnaires de mapping pour normalisation
        self.skills_mapping = self._init_skills_mapping()
        self.sectors_mapping = self._init_sectors_mapping()
        self.companies_database = self._init_companies_database()
        
        logger.info("🔄 CommitmentDataEnricher initialisé")
    
    def enrich_candidate_from_commitment(
        self, 
        cv_data_raw: Dict[str, Any], 
        questionnaire_data_raw: Dict[str, Any]
    ) -> CandidatCompletNexfen:
        """👤 Enrichit les données candidat depuis Commitment-"""
        
        logger.info("👤 Début enrichissement candidat Commitment-")
        start_time = datetime.now()
        
        try:
            # Enrichissement CV
            cv_enriched = self._enrich_cv_data(cv_data_raw)
            
            # Enrichissement questionnaire
            questionnaire_enriched = self._enrich_questionnaire_data(questionnaire_data_raw)
            
            # Création du candidat complet
            candidat_complet = CandidatCompletNexfen(
                cv_data=cv_enriched,
                questionnaire_data=questionnaire_enriched,
                source_commitment="https://github.com/Bapt252/Commitment-",
                date_integration=datetime.now()
            )
            
            # Analyse de cohérence automatique
            if self.config.calculate_scores:
                candidat_complet.analyser_coherence_cv_questionnaire()
                candidat_complet.calculer_score_employabilite()
                candidat_complet.identifier_points_forts()
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            self._log_transformation("candidate_enrichment", {
                "processing_time_ms": processing_time,
                "cv_skills_count": len(cv_enriched.competences_techniques),
                "experiences_count": len(cv_enriched.experiences),
                "questionnaire_completeness": questionnaire_enriched.calculer_score_completude()
            })
            
            logger.info(f"✅ Candidat enrichi en {processing_time:.1f}ms")
            return candidat_complet
            
        except Exception as e:
            logger.error(f"❌ Erreur enrichissement candidat: {e}")
            raise
    
    def enrich_job_from_commitment(
        self, 
        job_data_raw: Dict[str, Any],
        company_info: Optional[Dict[str, Any]] = None
    ) -> JobDataAdvanced:
        """💼 Enrichit les données job depuis Commitment-"""
        
        logger.info("💼 Début enrichissement job Commitment-")
        start_time = datetime.now()
        
        try:
            # Enrichissement des données job
            job_enriched = self._enrich_job_data(job_data_raw, company_info)
            
            # Calcul du score d'attractivité
            if self.config.calculate_scores:
                job_enriched.calculer_score_attractivite()
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            self._log_transformation("job_enrichment", {
                "processing_time_ms": processing_time,
                "competences_required_count": len(job_enriched.competences_requises),
                "missions_count": len(job_enriched.missions_principales),
                "attractivity_score": job_enriched.score_attractivite
            })
            
            logger.info(f"✅ Job enrichi en {processing_time:.1f}ms")
            return job_enriched
            
        except Exception as e:
            logger.error(f"❌ Erreur enrichissement job: {e}")
            raise
    
    def _enrich_cv_data(self, cv_raw: Dict[str, Any]) -> CVDataEnriched:
        """📄 Enrichit les données CV"""
        
        # Informations personnelles avec normalisation
        nom_complet = cv_raw.get('name', cv_raw.get('nom_complet', ''))
        email = cv_raw.get('email', '')
        telephone = cv_raw.get('phone', cv_raw.get('telephone', ''))
        
        # Normalisation adresse
        adresse_complete = cv_raw.get('location', cv_raw.get('adresse', ''))
        ville, code_postal = self._extract_city_postal_code(adresse_complete)
        
        # Statut professionnel avec inférence
        statut_activite = self._infer_activity_status(cv_raw)
        
        # Enrichissement expériences
        experiences_enriched = self._enrich_experiences(cv_raw.get('experiences', []))
        
        # Calcul années d'expérience totales
        annees_experience_totale = self._calculate_total_experience(experiences_enriched)
        
        # Enrichissement formations
        formations_enriched = self._enrich_formations(cv_raw.get('education', cv_raw.get('formations', [])))
        
        # Niveau d'études maximum
        niveau_etudes_max = self._determine_max_education_level(formations_enriched)
        
        # Enrichissement compétences techniques
        competences_techniques = self._enrich_technical_skills(
            cv_raw.get('skills', cv_raw.get('competences', [])),
            experiences_enriched
        )
        
        # Compétences transversales
        competences_transversales = self._extract_soft_skills(cv_raw)
        
        # Langues
        langues = self._enrich_languages(cv_raw.get('languages', cv_raw.get('langues', [])))
        
        # Liens et présence en ligne
        linkedin_url = self._extract_linkedin(cv_raw.get('links', []))
        github_url = self._extract_github(cv_raw.get('links', []))
        
        # Création CV enrichi
        cv_enriched = CVDataEnriched(
            nom_complet=nom_complet,
            email=email,
            telephone=telephone,
            adresse=adresse_complete,
            ville=ville,
            code_postal=code_postal,
            statut_activite=statut_activite,
            poste_actuel=cv_raw.get('current_role', ''),
            entreprise_actuelle=cv_raw.get('current_company', ''),
            salaire_actuel=cv_raw.get('current_salary', None),
            experiences=experiences_enriched,
            annees_experience_totale=annees_experience_totale,
            formations=formations_enriched,
            niveau_etudes_max=niveau_etudes_max,
            competences_techniques=competences_techniques,
            competences_transversales=competences_transversales,
            langues=langues,
            certifications_pro=cv_raw.get('certifications', []),
            projets_personnels=cv_raw.get('projects', []),
            linkedin_url=linkedin_url,
            github_url=github_url,
            resume_professionnel=cv_raw.get('summary', cv_raw.get('resume', '')),
            objectif_carriere=cv_raw.get('objective', '')
        )
        
        return cv_enriched
    
    def _enrich_questionnaire_data(self, questionnaire_raw: Dict[str, Any]) -> QuestionnaireCompletAdvanced:
        """📋 Enrichit les données questionnaire"""
        
        # Timing et disponibilité
        timing = self._enrich_timing_data(questionnaire_raw.get('timing', {}))
        
        # Secteurs avec normalisation
        secteurs = self._enrich_sectoral_preferences(questionnaire_raw.get('secteurs', {}))
        
        # Environnement de travail
        environnement_travail = self._map_environment_type(
            questionnaire_raw.get('environnement_travail', 'Bureau partagé')
        )
        
        # Transport
        transport = self._enrich_transport_config(questionnaire_raw.get('transport', {}))
        
        # Contrats
        contrats = self._enrich_contract_preferences(questionnaire_raw.get('contrats', {}))
        
        # Motivations
        motivations = self._enrich_motivations_ranking(questionnaire_raw.get('motivations', {}))
        
        # Rémunération
        remuneration = questionnaire_raw.get('remuneration', {'min': 30000, 'max': 50000})
        
        questionnaire_enriched = QuestionnaireCompletAdvanced(
            timing=timing,
            secteurs=secteurs,
            environnement_travail=environnement_travail,
            transport=transport,
            contrats=contrats,
            motivations=motivations,
            remuneration=remuneration
        )
        
        return questionnaire_enriched
    
    def _enrich_job_data(self, job_raw: Dict[str, Any], company_info: Optional[Dict[str, Any]] = None) -> JobDataAdvanced:
        """💼 Enrichit les données job"""
        
        # Informations de base
        titre_poste = job_raw.get('title', job_raw.get('titre', ''))
        entreprise = job_raw.get('company', job_raw.get('entreprise', ''))
        type_contrat = self._map_contract_type(job_raw.get('contract_type', 'CDI'))
        
        # Localisation enrichie
        localisation = self._enrich_job_location(job_raw.get('location_details', {}), job_raw.get('location', ''))
        
        # Environnement de travail
        environnement_travail = self._map_environment_type(job_raw.get('work_environment', 'Bureau partagé'))
        
        # Environnement d'entreprise
        environnement_entreprise = self._enrich_company_environment(job_raw, company_info)
        
        # Rémunération
        salaire_min, salaire_max = self._extract_salary_range(job_raw.get('salary_range', job_raw.get('salary', '')))
        
        # Avantages sociaux
        avantages_sociaux = self._enrich_benefits(job_raw.get('benefits', []))
        
        # Missions principales
        missions_principales = self._enrich_job_missions(job_raw.get('responsibilities', []))
        
        # Compétences requises
        competences_requises = self._enrich_required_skills(job_raw.get('required_skills', []))
        
        # Compétences souhaitées
        competences_souhaitees = self._enrich_required_skills(job_raw.get('preferred_skills', []))
        
        # Niveau d'expérience
        niveau_experience = self._map_experience_level(job_raw.get('experience_level', 'Confirmé'))
        
        # Type de recrutement
        type_recrutement = self._infer_recruitment_type(job_raw)
        
        # Processus de recrutement
        processus_recrutement = self._enrich_recruitment_process(job_raw.get('recruitment_process', {}))
        
        job_enriched = JobDataAdvanced(
            titre_poste=titre_poste,
            entreprise=entreprise,
            type_contrat=type_contrat,
            localisation=localisation,
            environnement_travail=environnement_travail,
            environnement_entreprise=environnement_entreprise,
            salaire_min=salaire_min,
            salaire_max=salaire_max,
            avantages_sociaux=avantages_sociaux,
            missions_principales=missions_principales,
            competences_requises=competences_requises,
            competences_souhaitees=competences_souhaitees,
            niveau_experience=niveau_experience,
            type_recrutement=type_recrutement,
            processus_recrutement=processus_recrutement,
            date_publication=datetime.now(),
            source_parsing="commitment_job_parser"
        )
        
        return job_enriched
    
    # Méthodes d'enrichissement spécifiques
    
    def _enrich_technical_skills(self, skills_raw: List[str], experiences: List[ExperienceProfessionnelle]) -> List[CompetenceTechnique]:
        """🔧 Enrichit les compétences techniques"""
        
        competences = []
        
        for skill in skills_raw:
            # Normalisation du nom
            skill_normalized = self._normalize_skill_name(skill)
            
            # Inférence du niveau basé sur l'expérience
            niveau = self._infer_skill_level(skill_normalized, experiences)
            
            # Années d'expérience avec cette compétence
            annees_exp = self._calculate_skill_experience_years(skill_normalized, experiences)
            
            # Dernière utilisation
            derniere_utilisation = self._get_last_skill_usage(skill_normalized, experiences)
            
            competence = CompetenceTechnique(
                nom=skill_normalized,
                niveau=niveau,
                annees_experience=annees_exp,
                derniere_utilisation=derniere_utilisation,
                veille_active=self._infer_tech_watch(skill_normalized)
            )
            
            competences.append(competence)
        
        return competences
    
    def _enrich_experiences(self, experiences_raw: List[Dict[str, Any]]) -> List[ExperienceProfessionnelle]:
        """💼 Enrichit les expériences professionnelles"""
        
        experiences = []
        
        for exp_raw in experiences_raw:
            # Extraction des données de base
            poste = exp_raw.get('title', exp_raw.get('poste', ''))
            entreprise = exp_raw.get('company', exp_raw.get('entreprise', ''))
            
            # Calcul de la durée
            duree_mois = self._calculate_experience_duration(exp_raw)
            
            # Secteur avec normalisation
            secteur = None
            if 'sector' in exp_raw or 'secteur' in exp_raw:
                secteur = normaliser_secteur(exp_raw.get('sector', exp_raw.get('secteur', '')))
            else:
                # Inférence du secteur depuis l'entreprise
                secteur = self._infer_sector_from_company(entreprise)
            
            # Taille d'entreprise
            taille_entreprise = self._infer_company_size(entreprise, exp_raw)
            
            # Technologies utilisées
            technologies = self._extract_technologies_from_description(
                exp_raw.get('description', exp_raw.get('missions', ''))
            )
            
            experience = ExperienceProfessionnelle(
                poste=poste,
                entreprise=entreprise,
                secteur=secteur,
                taille_entreprise=taille_entreprise,
                duree_mois=duree_mois,
                date_debut=exp_raw.get('start_date', exp_raw.get('date_debut')),
                date_fin=exp_raw.get('end_date', exp_raw.get('date_fin', 'En cours')),
                missions_principales=self._extract_missions_from_description(
                    exp_raw.get('description', exp_raw.get('missions', ''))
                ),
                technologies_utilisees=technologies
            )
            
            experiences.append(experience)
        
        return experiences
    
    def _enrich_timing_data(self, timing_raw: Dict[str, Any]) -> TimingDisponibilite:
        """⏰ Enrichit les données de timing"""
        
        # Mapping de disponibilité
        disponibilite_str = timing_raw.get('disponibilite', 'Dans 2 mois')
        disponibilite = self._map_availability(disponibilite_str)
        
        # Raison d'écoute
        pourquoi_ecoute_str = timing_raw.get('pourquoi_a_lecoute', 'Évolution professionnelle')
        pourquoi_a_lecoute = self._map_listening_reason(pourquoi_ecoute_str)
        
        timing = TimingDisponibilite(
            disponibilite=disponibilite,
            pourquoi_a_lecoute=pourquoi_a_lecoute,
            preavis=timing_raw.get('preavis'),
            date_souhaitee=self._parse_date(timing_raw.get('date_souhaitee')),
            contraintes_specifiques=timing_raw.get('contraintes_specifiques')
        )
        
        return timing
    
    def _enrich_transport_config(self, transport_raw: Dict[str, Any]) -> ConfigTransport:
        """🚗 Enrichit la configuration transport"""
        
        # Moyens de transport
        moyens_str = transport_raw.get('moyens_selectionnes', ['Voiture'])
        moyens_selectionnes = [self._map_transport_method(m) for m in moyens_str]
        
        # Temps maximum par moyen
        temps_max = transport_raw.get('temps_max', {})
        if not temps_max and moyens_selectionnes:
            # Valeurs par défaut intelligentes
            temps_max = {}
            for moyen in moyens_selectionnes:
                if moyen.value.lower() == 'voiture':
                    temps_max['voiture'] = 30
                elif 'transport' in moyen.value.lower():
                    temps_max['transport_commun'] = 45
                elif moyen.value.lower() == 'vélo':
                    temps_max['velo'] = 20
        
        transport = ConfigTransport(
            moyens_selectionnes=moyens_selectionnes,
            temps_max=temps_max,
            distance_max_km=transport_raw.get('distance_max_km'),
            couts_max_mensuel=transport_raw.get('couts_max_mensuel'),
            flexibilite_horaires=transport_raw.get('flexibilite_horaires', False)
        )
        
        return transport
    
    def _enrich_motivations_ranking(self, motivations_raw: Dict[str, Any]) -> RankingMotivations:
        """🎯 Enrichit le classement des motivations"""
        
        motivations_classees = []
        classees_data = motivations_raw.get('motivations_classees', [])
        
        if not classees_data:
            # Création par défaut basée sur des motivations standards
            default_motivations = [
                {"motivation": "Évolution", "priorite": 1, "poids": 0.3},
                {"motivation": "Salaire", "priorite": 2, "poids": 0.25},
                {"motivation": "Flexibilité", "priorite": 3, "poids": 0.2}
            ]
            classees_data = default_motivations
        
        for i, motivation_data in enumerate(classees_data):
            motivation_enum = self._map_motivation(motivation_data.get('motivation', 'Évolution'))
            
            motivation_classee = MotivationClassee(
                motivation=motivation_enum,
                priorite=motivation_data.get('priorite', i + 1),
                poids=motivation_data.get('poids', 1.0 / len(classees_data)),
                description_personnalisee=motivation_data.get('description_personnalisee')
            )
            
            motivations_classees.append(motivation_classee)
        
        ranking = RankingMotivations(
            motivations_classees=motivations_classees,
            facteur_adaptabilite=motivations_raw.get('facteur_adaptabilite', 0.8)
        )
        
        # Normalisation des poids
        ranking.normaliser_poids()
        
        return ranking
    
    # Méthodes utilitaires de mapping et normalisation
    
    def _normalize_skill_name(self, skill: str) -> str:
        """🔤 Normalise le nom d'une compétence"""
        skill_clean = skill.strip().title()
        return self.skills_mapping.get(skill_clean.lower(), skill_clean)
    
    def _map_contract_type(self, contract_str: str) -> TypeContratEnum:
        """📜 Mappe le type de contrat"""
        contract_mapping = {
            'cdi': TypeContratEnum.CDI,
            'cdd': TypeContratEnum.CDD,
            'interim': TypeContratEnum.INTERIM,
            'freelance': TypeContratEnum.FREELANCE,
            'stage': TypeContratEnum.STAGE,
            'apprentissage': TypeContratEnum.APPRENTISSAGE
        }
        
        return contract_mapping.get(contract_str.lower(), TypeContratEnum.CDI)
    
    def _map_environment_type(self, env_str: str) -> EnvironnementTravailEnum:
        """🏢 Mappe le type d'environnement"""
        env_mapping = {
            'bureau individuel': EnvironnementTravailEnum.BUREAU_INDIVIDUEL,
            'bureau partagé': EnvironnementTravailEnum.BUREAU_PARTAGE,
            'open space': EnvironnementTravailEnum.OPEN_SPACE,
            'télétravail': EnvironnementTravailEnum.DOMICILE,
            'hybride': EnvironnementTravailEnum.HYBRIDE,
            'coworking': EnvironnementTravailEnum.COWORKING
        }
        
        return env_mapping.get(env_str.lower(), EnvironnementTravailEnum.BUREAU_PARTAGE)
    
    def _map_motivation(self, motivation_str: str) -> MotivationEnum:
        """🎯 Mappe une motivation"""
        motivation_mapping = {
            'évolution': MotivationEnum.EVOLUTION,
            'salaire': MotivationEnum.SALAIRE,
            'flexibilité': MotivationEnum.FLEXIBILITE,
            'ambiance': MotivationEnum.AMBIANCE,
            'apprentissage': MotivationEnum.APPRENTISSAGE,
            'reconnaissance': MotivationEnum.RECONNAISSANCE,
            'autonomie': MotivationEnum.AUTONOMIE,
            'équilibre': MotivationEnum.EQUILIBRE_VIE,
            'sécurité': MotivationEnum.SECURITE,
            'innovation': MotivationEnum.INNOVATION
        }
        
        return motivation_mapping.get(motivation_str.lower(), MotivationEnum.EVOLUTION)
    
    def _infer_skill_level(self, skill: str, experiences: List[ExperienceProfessionnelle]) -> NiveauEnum:
        """📊 Infère le niveau d'une compétence"""
        
        # Recherche de la compétence dans les expériences
        total_months = 0
        for exp in experiences:
            if skill.lower() in [tech.lower() for tech in exp.technologies_utilisees]:
                total_months += exp.duree_mois
        
        # Mapping basé sur l'expérience
        if total_months >= 60:  # 5+ ans
            return NiveauEnum.EXPERT
        elif total_months >= 36:  # 3+ ans
            return NiveauEnum.AVANCE
        elif total_months >= 12:  # 1+ an
            return NiveauEnum.INTERMEDIAIRE
        else:
            return NiveauEnum.DEBUTANT
    
    def _calculate_total_experience(self, experiences: List[ExperienceProfessionnelle]) -> int:
        """📊 Calcule les années d'expérience totales"""
        total_months = sum(exp.duree_mois for exp in experiences)
        return total_months // 12
    
    def _extract_salary_range(self, salary_str: str) -> Tuple[Optional[int], Optional[int]]:
        """💰 Extrait la fourchette salariale"""
        if not salary_str:
            return None, None
        
        # Pattern pour extraire les salaires
        pattern = r'(\d{2,6})\s*(?:k|000)?.*?(?:à|-).*?(\d{2,6})\s*(?:k|000)?'
        match = re.search(pattern, salary_str.lower())
        
        if match:
            min_sal = int(match.group(1))
            max_sal = int(match.group(2))
            
            # Ajustement si exprimé en k
            if 'k' in salary_str.lower() or min_sal < 100:
                min_sal *= 1000
                max_sal *= 1000
            
            return min_sal, max_sal
        
        # Pattern pour un seul salaire
        single_pattern = r'(\d{2,6})\s*(?:k|000)?'
        single_match = re.search(single_pattern, salary_str.lower())
        
        if single_match:
            salary = int(single_match.group(1))
            if 'k' in salary_str.lower() or salary < 100:
                salary *= 1000
            
            # Estimation d'une fourchette ±10%
            return int(salary * 0.9), int(salary * 1.1)
        
        return None, None
    
    # Méthodes d'initialisation des dictionnaires
    
    def _init_skills_mapping(self) -> Dict[str, str]:
        """🔧 Initialise le mapping des compétences"""
        return {
            'js': 'JavaScript',
            'ts': 'TypeScript',
            'py': 'Python',
            'react': 'React',
            'vue': 'Vue.js',
            'angular': 'Angular',
            'node': 'Node.js',
            'nodejs': 'Node.js',
            'postgresql': 'PostgreSQL',
            'postgres': 'PostgreSQL',
            'mysql': 'MySQL',
            'mongodb': 'MongoDB',
            'docker': 'Docker',
            'kubernetes': 'Kubernetes',
            'k8s': 'Kubernetes',
            'aws': 'AWS',
            'azure': 'Azure',
            'gcp': 'Google Cloud',
            'ci/cd': 'CI/CD',
            'devops': 'DevOps'
        }
    
    def _init_sectors_mapping(self) -> Dict[str, str]:
        """🏭 Initialise le mapping des secteurs"""
        return {
            'it': 'Technologies de l\'information',
            'tech': 'Technologies de l\'information',
            'informatique': 'Technologies de l\'information',
            'fintech': 'Finance',
            'finance': 'Finance',
            'banque': 'Finance',
            'santé': 'Santé',
            'medical': 'Santé',
            'éducation': 'Éducation',
            'formation': 'Éducation',
            'commerce': 'Commerce',
            'retail': 'Commerce',
            'industrie': 'Industrie',
            'conseil': 'Conseil',
            'consulting': 'Conseil'
        }
    
    def _init_companies_database(self) -> Dict[str, Dict[str, Any]]:
        """🏢 Initialise la base de données des entreprises"""
        return {
            'google': {'sector': 'Technologies de l\'information', 'size': 'GE'},
            'microsoft': {'sector': 'Technologies de l\'information', 'size': 'GE'},
            'amazon': {'sector': 'Technologies de l\'information', 'size': 'GE'},
            'apple': {'sector': 'Technologies de l\'information', 'size': 'GE'},
            'meta': {'sector': 'Technologies de l\'information', 'size': 'GE'},
            'bnp paribas': {'sector': 'Finance', 'size': 'GE'},
            'société générale': {'sector': 'Finance', 'size': 'GE'},
            'crédit agricole': {'sector': 'Finance', 'size': 'GE'},
            'airbus': {'sector': 'Industrie', 'size': 'GE'},
            'thales': {'sector': 'Industrie', 'size': 'GE'},
            'sanofi': {'sector': 'Santé', 'size': 'GE'},
            'l\'oréal': {'sector': 'Luxe', 'size': 'GE'}
        }
    
    # Méthodes utilitaires diverses
    
    def _log_transformation(self, operation: str, details: Dict[str, Any]):
        """📝 Log une transformation effectuée"""
        if self.config.log_transformations:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "operation": operation,
                "details": details
            }
            self.transformation_log.append(log_entry)
    
    def get_transformation_summary(self) -> Dict[str, Any]:
        """📊 Retourne un résumé des transformations effectuées"""
        return {
            "total_transformations": len(self.transformation_log),
            "operations_by_type": self._count_operations_by_type(),
            "average_processing_time": self._calculate_average_processing_time(),
            "last_transformation": self.transformation_log[-1] if self.transformation_log else None
        }
    
    def _count_operations_by_type(self) -> Dict[str, int]:
        """📊 Compte les opérations par type"""
        counts = {}
        for log_entry in self.transformation_log:
            operation = log_entry["operation"]
            counts[operation] = counts.get(operation, 0) + 1
        return counts
    
    def _calculate_average_processing_time(self) -> float:
        """⏱️ Calcule le temps de traitement moyen"""
        times = []
        for log_entry in self.transformation_log:
            if "processing_time_ms" in log_entry["details"]:
                times.append(log_entry["details"]["processing_time_ms"])
        
        return sum(times) / len(times) if times else 0.0

# Instance globale de l'enrichisseur
data_enricher = CommitmentDataEnricher()

# Fonctions utilitaires pour l'utilisation directe
def enrich_candidate_from_commitment(cv_data: Dict[str, Any], questionnaire_data: Dict[str, Any]) -> CandidatCompletNexfen:
    """👤 Fonction utilitaire pour enrichir un candidat"""
    return data_enricher.enrich_candidate_from_commitment(cv_data, questionnaire_data)

def enrich_job_from_commitment(job_data: Dict[str, Any], company_info: Optional[Dict[str, Any]] = None) -> JobDataAdvanced:
    """💼 Fonction utilitaire pour enrichir un job"""
    return data_enricher.enrich_job_from_commitment(job_data, company_info)

def get_enrichment_stats() -> Dict[str, Any]:
    """📊 Fonction utilitaire pour obtenir les statistiques d'enrichissement"""
    return data_enricher.get_transformation_summary()
