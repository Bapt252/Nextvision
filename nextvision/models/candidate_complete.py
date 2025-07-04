"""
👤 Modèles Candidat Complet NEXTEN
Structure candidat enrichie combinant CV parsé + questionnaire détaillé Commitment-

Author: NEXTEN Team  
Version: 1.0.0
Integration: Commitment- → Nextvision Bridge
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from enum import Enum

# Import des modèles questionnaire avancés
from .questionnaire_advanced import (
    QuestionnaireCompletAdvanced,
    PourquoiEcouteEnum,
    MotivationEnum
)

class NiveauEnum(str, Enum):
    """📊 Niveaux de compétence/expérience"""
    DEBUTANT = "Débutant"
    INTERMEDIAIRE = "Intermédiaire"
    AVANCE = "Avancé"
    EXPERT = "Expert"
    MAITRE = "Maître"

class TypeFormationEnum(str, Enum):
    """🎓 Types de formations"""
    BAC = "Baccalauréat"
    BTS = "BTS"
    DUT = "DUT"
    LICENCE = "Licence"
    MASTER = "Master"
    DOCTORAT = "Doctorat"
    INGENIEUR = "École d'ingénieur"
    COMMERCE = "École de commerce"
    CERTIFICATION = "Certification professionnelle"
    FORMATION_COURTE = "Formation courte"
    AUTODIDACTE = "Autodidacte"

class StatutActiviteEnum(str, Enum):
    """💼 Statut d'activité actuel"""
    EMPLOI_CDI = "En emploi CDI"
    EMPLOI_CDD = "En emploi CDD"
    EMPLOI_INTERIM = "En emploi intérim"
    FREELANCE = "Freelance"
    CHOMAGE = "En recherche d'emploi"
    ETUDIANT = "Étudiant"
    STAGE = "En stage"
    CREATION_ENTREPRISE = "Création d'entreprise"
    FORMATION = "En formation"
    RECONVERSION = "En reconversion"

class CompetenceTechnique(BaseModel):
    """🔧 Compétence technique détaillée"""
    nom: str = Field(..., description="Nom de la compétence")
    niveau: NiveauEnum = Field(..., description="Niveau de maîtrise")
    annees_experience: int = Field(default=0, ge=0, description="Années d'expérience avec cette compétence")
    derniere_utilisation: Optional[str] = Field(None, description="Dernière utilisation (ex: '2024', 'Actuellement')")
    certifications: List[str] = Field(default_factory=list, description="Certifications liées")
    projets_references: List[str] = Field(default_factory=list, description="Projets de référence")
    veille_active: bool = Field(default=False, description="Veille technologique active")
    
    @validator('annees_experience')
    def validate_experience(cls, v):
        if v < 0 or v > 50:
            raise ValueError('Années d\'expérience doit être entre 0 et 50')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "nom": "Python",
                "niveau": "Avancé",
                "annees_experience": 5,
                "derniere_utilisation": "Actuellement",
                "certifications": ["Python Institute PCAP", "AWS Python Developer"],
                "projets_references": ["API FastAPI e-commerce", "ML Pipeline production"],
                "veille_active": True
            }
        }

class ExperienceProfessionnelle(BaseModel):
    """💼 Expérience professionnelle enrichie"""
    poste: str = Field(..., description="Intitulé du poste")
    entreprise: str = Field(..., description="Nom de l'entreprise")
    secteur: Optional[str] = Field(None, description="Secteur d'activité")
    taille_entreprise: Optional[str] = Field(None, description="Taille entreprise (TPE, PME, ETI, GE)")
    duree_mois: int = Field(..., ge=0, description="Durée en mois")
    date_debut: Optional[str] = Field(None, description="Date de début (YYYY-MM)")
    date_fin: Optional[str] = Field(None, description="Date de fin (YYYY-MM ou 'En cours')")
    
    # Détails techniques
    missions_principales: List[str] = Field(default_factory=list, description="Missions principales")
    technologies_utilisees: List[str] = Field(default_factory=list, description="Technologies utilisées")
    realisations_quantifiees: List[str] = Field(default_factory=list, description="Réalisations avec métriques")
    
    # Management et responsabilités
    taille_equipe: Optional[int] = Field(None, ge=0, description="Taille équipe managée")
    budget_gere: Optional[int] = Field(None, ge=0, description="Budget géré (€)")
    
    # Évaluation
    score_pertinence: Optional[float] = Field(None, ge=0, le=1, description="Score de pertinence pour le profil")
    
    @validator('duree_mois')
    def validate_duree(cls, v):
        if v < 0 or v > 600:  # 50 ans max
            raise ValueError('Durée doit être entre 0 et 600 mois')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "poste": "Développeur Senior Python",
                "entreprise": "TechCorp",
                "secteur": "Technologies de l'information",
                "taille_entreprise": "PME",
                "duree_mois": 36,
                "date_debut": "2021-01",
                "date_fin": "En cours",
                "missions_principales": [
                    "Développement APIs REST avec FastAPI",
                    "Architecture microservices",
                    "Mentorat équipe junior"
                ],
                "technologies_utilisees": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
                "realisations_quantifiees": [
                    "Réduction temps réponse API de 40%",
                    "Migration 5M+ utilisateurs sans incident"
                ],
                "taille_equipe": 4,
                "score_pertinence": 0.95
            }
        }

class FormationAcademique(BaseModel):
    """🎓 Formation académique détaillée"""
    diplome: str = Field(..., description="Nom du diplôme")
    type_formation: TypeFormationEnum = Field(..., description="Type de formation")
    etablissement: str = Field(..., description="Établissement")
    specialite: Optional[str] = Field(None, description="Spécialité/Mention")
    annee_obtention: int = Field(..., description="Année d'obtention")
    mention: Optional[str] = Field(None, description="Mention obtenue")
    
    # Détails académiques
    matieres_principales: List[str] = Field(default_factory=list, description="Matières principales étudiées")
    projets_academiques: List[str] = Field(default_factory=list, description="Projets académiques notables")
    stages_inclus: List[str] = Field(default_factory=list, description="Stages intégrés à la formation")
    
    # Évaluation
    pertinence_metier: Optional[float] = Field(None, ge=0, le=1, description="Pertinence pour le métier visé")
    
    @validator('annee_obtention')
    def validate_annee(cls, v):
        current_year = datetime.now().year
        if v < 1950 or v > current_year + 5:
            raise ValueError(f'Année obtention doit être entre 1950 et {current_year + 5}')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "diplome": "Master Informatique - Génie Logiciel",
                "type_formation": "Master",
                "etablissement": "Université Paris-Saclay",
                "specialite": "Intelligence Artificielle",
                "annee_obtention": 2020,
                "mention": "Bien",
                "matieres_principales": ["Machine Learning", "Bases de données", "Génie logiciel"],
                "projets_academiques": ["Système de recommandation e-commerce", "Chatbot NLP"],
                "pertinence_metier": 0.9
            }
        }

class LangueCompetence(BaseModel):
    """🗣️ Compétence linguistique"""
    langue: str = Field(..., description="Nom de la langue")
    niveau_oral: NiveauEnum = Field(..., description="Niveau oral")
    niveau_ecrit: NiveauEnum = Field(..., description="Niveau écrit")
    certification: Optional[str] = Field(None, description="Certification (TOEIC, DELF, etc.)")
    score_certification: Optional[int] = Field(None, description="Score de certification")
    usage_professionnel: bool = Field(default=False, description="Utilisée dans contexte professionnel")
    
    class Config:
        json_schema_extra = {
            "example": {
                "langue": "Anglais",
                "niveau_oral": "Avancé",
                "niveau_ecrit": "Avancé", 
                "certification": "TOEIC",
                "score_certification": 920,
                "usage_professionnel": True
            }
        }

class CVDataEnriched(BaseModel):
    """📄 Données CV enrichies issues du parsing Commitment-"""
    
    # Informations personnelles
    nom_complet: str = Field(..., description="Nom complet")
    email: EmailStr = Field(..., description="Email")
    telephone: Optional[str] = Field(None, description="Numéro de téléphone")
    adresse: Optional[str] = Field(None, description="Adresse complète")
    ville: Optional[str] = Field(None, description="Ville de résidence")
    code_postal: Optional[str] = Field(None, description="Code postal")
    
    # Statut professionnel
    statut_activite: StatutActiviteEnum = Field(..., description="Statut d'activité actuel")
    poste_actuel: Optional[str] = Field(None, description="Poste occupé actuellement")
    entreprise_actuelle: Optional[str] = Field(None, description="Entreprise actuelle")
    salaire_actuel: Optional[int] = Field(None, ge=0, description="Salaire actuel brut annuel (€)")
    
    # Expérience professionnelle
    experiences: List[ExperienceProfessionnelle] = Field(default_factory=list, description="Expériences professionnelles")
    annees_experience_totale: int = Field(default=0, ge=0, description="Années d'expérience totales")
    
    # Formation
    formations: List[FormationAcademique] = Field(default_factory=list, description="Formations académiques")
    niveau_etudes_max: Optional[TypeFormationEnum] = Field(None, description="Plus haut niveau d'études")
    
    # Compétences
    competences_techniques: List[CompetenceTechnique] = Field(default_factory=list, description="Compétences techniques détaillées")
    competences_transversales: List[str] = Field(default_factory=list, description="Compétences transversales/soft skills")
    langues: List[LangueCompetence] = Field(default_factory=list, description="Compétences linguistiques")
    
    # Certifications et projets
    certifications_pro: List[str] = Field(default_factory=list, description="Certifications professionnelles")
    projets_personnels: List[str] = Field(default_factory=list, description="Projets personnels notables")
    publications: List[str] = Field(default_factory=list, description="Publications/Articles")
    
    # Liens et présence en ligne
    linkedin_url: Optional[str] = Field(None, description="URL LinkedIn")
    github_url: Optional[str] = Field(None, description="URL GitHub")
    portfolio_url: Optional[str] = Field(None, description="URL Portfolio")
    autres_liens: List[Dict[str, str]] = Field(default_factory=list, description="Autres liens professionnels")
    
    # Résumé et objectifs
    resume_professionnel: Optional[str] = Field(None, description="Résumé professionnel")
    objectif_carriere: Optional[str] = Field(None, description="Objectif de carrière")
    
    # Métadonnées parsing
    source_parsing: str = Field(default="commitment_cv_parser", description="Source du parsing")
    date_parsing: datetime = Field(default_factory=datetime.now, description="Date du parsing")
    score_qualite_cv: Optional[float] = Field(None, ge=0, le=1, description="Score qualité du CV")
    
    @validator('annees_experience_totale')
    def validate_experience_totale(cls, v, values):
        if v > 50:
            raise ValueError('Expérience totale ne peut dépasser 50 ans')
        return v
    
    def calculer_score_qualite(self) -> float:
        """📊 Calcule un score de qualité du CV basé sur la complétude"""
        score = 0.0
        max_score = 10.0
        
        # Informations de base (2 points)
        if self.email and self.nom_complet:
            score += 2.0
        
        # Expérience (2 points)
        if self.experiences:
            score += 1.0
            if self.annees_experience_totale >= 2:
                score += 1.0
        
        # Formation (1 point)
        if self.formations:
            score += 1.0
        
        # Compétences techniques (2 points)
        if self.competences_techniques:
            score += 1.0
            if len(self.competences_techniques) >= 5:
                score += 1.0
        
        # Compétences transversales (1 point)
        if self.competences_transversales:
            score += 1.0
        
        # Langues (1 point)
        if self.langues:
            score += 1.0
        
        # Présence en ligne (1 point)
        if self.linkedin_url or self.github_url or self.portfolio_url:
            score += 1.0
        
        self.score_qualite_cv = score / max_score
        return self.score_qualite_cv
    
    class Config:
        json_schema_extra = {
            "example": {
                "nom_complet": "Jean Dupont",
                "email": "jean.dupont@email.com",
                "telephone": "+33 6 12 34 56 78",
                "ville": "Paris",
                "statut_activite": "En emploi CDI",
                "poste_actuel": "Développeur Senior Python",
                "entreprise_actuelle": "TechCorp",
                "salaire_actuel": 52000,
                "annees_experience_totale": 7,
                "competences_techniques": [
                    {
                        "nom": "Python",
                        "niveau": "Avancé",
                        "annees_experience": 5
                    }
                ],
                "formations": [
                    {
                        "diplome": "Master Informatique",
                        "type_formation": "Master",
                        "etablissement": "Université Paris-Saclay",
                        "annee_obtention": 2018
                    }
                ]
            }
        }

class CandidatCompletNexfen(BaseModel):
    """🎯 Modèle candidat complet NEXTEN - CV + Questionnaire enrichi"""
    
    # Données sources
    cv_data: CVDataEnriched = Field(..., description="Données CV enrichies")
    questionnaire_data: QuestionnaireCompletAdvanced = Field(..., description="Questionnaire complet")
    
    # Métadonnées d'intégration
    candidate_id: Optional[str] = Field(None, description="ID unique candidat")
    source_commitment: str = Field(default="https://github.com/Bapt252/Commitment-", description="Source Commitment-")
    date_integration: datetime = Field(default_factory=datetime.now, description="Date d'intégration")
    
    # Scores d'analyse
    score_coherence: Optional[float] = Field(None, ge=0, le=1, description="Score cohérence CV/questionnaire")
    score_employabilite: Optional[float] = Field(None, ge=0, le=1, description="Score employabilité global")
    facteur_motivation: Optional[float] = Field(None, ge=0, le=1, description="Facteur motivation adaptative")
    
    # Flags d'analyse
    alerte_incoherences: List[str] = Field(default_factory=list, description="Alertes d'incohérences détectées")
    points_forts: List[str] = Field(default_factory=list, description="Points forts identifiés")
    axes_amelioration: List[str] = Field(default_factory=list, description="Axes d'amélioration")
    
    def analyser_coherence_cv_questionnaire(self) -> float:
        """🔍 Analyse la cohérence entre CV et questionnaire"""
        coherence_score = 1.0
        alertes = []
        
        # Vérification salaire actuel vs attentes
        if (self.cv_data.salaire_actuel and 
            self.questionnaire_data.remuneration.get('min', 0) > 0):
            
            salaire_actuel = self.cv_data.salaire_actuel
            salaire_min_souhaite = self.questionnaire_data.remuneration['min']
            
            if salaire_min_souhaite <= salaire_actuel * 0.9:  # Baisse > 10%
                alertes.append("Attente salariale inférieure au salaire actuel")
                coherence_score -= 0.2
            elif salaire_min_souhaite > salaire_actuel * 1.5:  # Hausse > 50%
                alertes.append("Attente salariale très ambitieuse (+50%)")
                coherence_score -= 0.1
        
        # Vérification motivation vs raison d'écoute
        pourquoi_ecoute = self.questionnaire_data.timing.pourquoi_a_lecoute
        motivations = [m.motivation for m in self.questionnaire_data.motivations.motivations_classees[:3]]
        
        # Mapping cohérence raison/motivations
        coherence_mapping = {
            PourquoiEcouteEnum.REMUNERATION_FAIBLE: [MotivationEnum.SALAIRE],
            PourquoiEcouteEnum.MANQUE_PERSPECTIVES: [MotivationEnum.EVOLUTION, MotivationEnum.APPRENTISSAGE],
            PourquoiEcouteEnum.MANQUE_FLEXIBILITE: [MotivationEnum.FLEXIBILITE, MotivationEnum.EQUILIBRE_VIE]
        }
        
        if pourquoi_ecoute in coherence_mapping:
            motivations_attendues = coherence_mapping[pourquoi_ecoute]
            if not any(m in motivations for m in motivations_attendues):
                alertes.append(f"Motivations incohérentes avec raison d'écoute: {pourquoi_ecoute}")
                coherence_score -= 0.15
        
        # Vérification expérience vs niveau formations
        if self.cv_data.annees_experience_totale > 10 and self.cv_data.niveau_etudes_max in [TypeFormationEnum.BAC, TypeFormationEnum.BTS]:
            alertes.append("Forte expérience avec niveau d'études relativement faible")
            # Pas de pénalité - c'est légitime
        
        self.alerte_incoherences = alertes
        self.score_coherence = max(0.0, coherence_score)
        return self.score_coherence
    
    def calculer_score_employabilite(self) -> float:
        """💼 Calcule un score d'employabilité global"""
        score = 0.0
        
        # Compétences techniques (30%)
        if self.cv_data.competences_techniques:
            score_competences = min(1.0, len(self.cv_data.competences_techniques) / 10)
            score += score_competences * 0.3
        
        # Expérience (25%)
        exp_score = min(1.0, self.cv_data.annees_experience_totale / 10)
        score += exp_score * 0.25
        
        # Formation (15%)
        if self.cv_data.formations:
            formation_score = 0.5
            if self.cv_data.niveau_etudes_max in [TypeFormationEnum.MASTER, TypeFormationEnum.INGENIEUR, TypeFormationEnum.DOCTORAT]:
                formation_score = 1.0
            elif self.cv_data.niveau_etudes_max in [TypeFormationEnum.LICENCE, TypeFormationEnum.COMMERCE]:
                formation_score = 0.8
            score += formation_score * 0.15
        
        # Langues (10%)
        if self.cv_data.langues:
            score += min(1.0, len(self.cv_data.langues) / 3) * 0.1
        
        # Motivation/Adaptabilité (20%)
        if self.questionnaire_data.motivations.motivations_classees:
            motivation_score = len(self.questionnaire_data.motivations.motivations_classees) / 5
            score += min(1.0, motivation_score) * 0.2
        
        self.score_employabilite = score
        return score
    
    def identifier_points_forts(self) -> List[str]:
        """⭐ Identifie les points forts du candidat"""
        points_forts = []
        
        # Expérience
        if self.cv_data.annees_experience_totale >= 5:
            points_forts.append(f"Expérience solide ({self.cv_data.annees_experience_totale} ans)")
        
        # Compétences techniques
        if len(self.cv_data.competences_techniques) >= 8:
            points_forts.append("Large palette de compétences techniques")
        
        # Formation
        if self.cv_data.niveau_etudes_max in [TypeFormationEnum.MASTER, TypeFormationEnum.INGENIEUR, TypeFormationEnum.DOCTORAT]:
            points_forts.append("Formation de haut niveau")
        
        # Langues
        langues_avancees = [l for l in self.cv_data.langues if l.niveau_oral in [NiveauEnum.AVANCE, NiveauEnum.EXPERT]]
        if len(langues_avancees) >= 2:
            points_forts.append("Profil international (multilingue)")
        
        # Motivation
        if len(self.questionnaire_data.motivations.motivations_classees) >= 5:
            points_forts.append("Motivations clairement définies")
        
        # Flexibilité transport
        if len(self.questionnaire_data.transport.moyens_selectionnes) >= 3:
            points_forts.append("Grande flexibilité de transport")
        
        self.points_forts = points_forts
        return points_forts
    
    def analyse_complete(self) -> Dict[str, Any]:
        """🎯 Effectue l'analyse complète du candidat"""
        
        # Calculs des scores
        score_coherence = self.analyser_coherence_cv_questionnaire()
        score_employabilite = self.calculer_score_employabilite()
        score_qualite_cv = self.cv_data.calculer_score_qualite()
        score_completude_questionnaire = self.questionnaire_data.calculer_score_completude()
        
        # Identification des points forts
        points_forts = self.identifier_points_forts()
        
        # Calcul facteur motivation adaptatif
        raison_ecoute = self.questionnaire_data.timing.pourquoi_a_lecoute
        motivation_principale = self.questionnaire_data.motivations.motivations_classees[0].motivation if self.questionnaire_data.motivations.motivations_classees else None
        
        # Facteur motivation basé sur la cohérence raison/motivation principale
        facteur_motivation = 0.8  # Base
        if motivation_principale:
            if raison_ecoute == PourquoiEcouteEnum.REMUNERATION_FAIBLE and motivation_principale == MotivationEnum.SALAIRE:
                facteur_motivation = 0.95
            elif raison_ecoute == PourquoiEcouteEnum.MANQUE_PERSPECTIVES and motivation_principale == MotivationEnum.EVOLUTION:
                facteur_motivation = 0.9
        
        self.facteur_motivation = facteur_motivation
        
        return {
            "scores": {
                "coherence_cv_questionnaire": score_coherence,
                "employabilite": score_employabilite,
                "qualite_cv": score_qualite_cv,
                "completude_questionnaire": score_completude_questionnaire,
                "facteur_motivation": facteur_motivation
            },
            "points_forts": points_forts,
            "alertes": self.alerte_incoherences,
            "resume_candidat": {
                "nom": self.cv_data.nom_complet,
                "experience": f"{self.cv_data.annees_experience_totale} ans",
                "competences_count": len(self.cv_data.competences_techniques),
                "formation_max": self.cv_data.niveau_etudes_max,
                "raison_ecoute": raison_ecoute,
                "motivation_principale": motivation_principale
            }
        }
    
    class Config:
        json_schema_extra = {
            "example": {
                "cv_data": {
                    "nom_complet": "Jean Dupont",
                    "email": "jean.dupont@email.com",
                    "statut_activite": "En emploi CDI",
                    "annees_experience_totale": 7
                },
                "questionnaire_data": {
                    "timing": {
                        "disponibilite": "Dans 2 mois",
                        "pourquoi_a_lecoute": "Rémunération trop faible"
                    },
                    "remuneration": {
                        "min": 45000,
                        "max": 60000
                    }
                }
            }
        }
