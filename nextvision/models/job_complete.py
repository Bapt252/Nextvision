"""
💼 Modèles Job Complet NEXTEN
Structure job enrichie combinant parsing GPT + environnement entreprise détaillé

Author: NEXTEN Team
Version: 1.0.0  
Integration: Commitment- → Nextvision Bridge
"""

from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, date
from enum import Enum

# Import des énumérations communes
from .questionnaire_advanced import (
    TypeContratEnum,
    EnvironnementTravailEnum,
    MoyenTransportEnum
)

class TailleEntrepriseEnum(str, Enum):
    """🏢 Tailles d'entreprise"""
    TPE = "TPE (0-9 salariés)"
    PME = "PME (10-249 salariés)"
    ETI = "ETI (250-4999 salariés)"
    GE = "Grande Entreprise (5000+ salariés)"
    STARTUP = "Startup"
    SCALE_UP = "Scale-up"
    MULTINATIONAL = "Multinationale"

class TypeRecrutementEnum(str, Enum):
    """🎯 Types de recrutement"""
    CREATION_POSTE = "Création de poste"
    REMPLACEMENT = "Remplacement"
    RENFORT_EQUIPE = "Renfort d'équipe"
    EVOLUTION_INTERNE = "Évolution interne"
    PROJET_SPECIFIQUE = "Projet spécifique"
    SAISONNIER = "Saisonnier"

class NiveauRequis(str, Enum):
    """📊 Niveaux requis"""
    DEBUTANT = "Débutant"
    JUNIOR = "Junior (1-3 ans)"
    CONFIRME = "Confirmé (3-7 ans)"
    SENIOR = "Senior (7-15 ans)"
    EXPERT = "Expert (15+ ans)"
    MANAGER = "Manager"
    DIRECTOR = "Directeur"

class FlexibiliteTravailEnum(str, Enum):
    """🏠 Types de flexibilité travail"""
    PRESENTIEL_OBLIGATOIRE = "100% présentiel"
    HYBRIDE_1J = "Hybride 1j télétravail/semaine"
    HYBRIDE_2J = "Hybride 2j télétravail/semaine"
    HYBRIDE_3J = "Hybride 3j télétravail/semaine"
    MAJORITAIREMENT_REMOTE = "Majoritairement remote"
    FULL_REMOTE = "100% remote"
    FLEXIBLE = "Flexible selon projets"

class CompetenceRequise(BaseModel):
    """🔧 Compétence requise pour le poste"""
    nom: str = Field(..., description="Nom de la compétence")
    niveau_requis: NiveauRequis = Field(..., description="Niveau requis")
    obligatoire: bool = Field(default=True, description="Compétence obligatoire ou souhaitable")
    experience_min_mois: int = Field(default=0, ge=0, description="Expérience minimum en mois")
    certifications_souhaitees: List[str] = Field(default_factory=list, description="Certifications souhaitées")
    outils_associes: List[str] = Field(default_factory=list, description="Outils/technologies associés")
    contexte_utilisation: Optional[str] = Field(None, description="Contexte d'utilisation")
    
    @validator('experience_min_mois')
    def validate_experience(cls, v):
        if v < 0 or v > 600:  # 50 ans max
            raise ValueError('Expérience doit être entre 0 et 600 mois')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "nom": "Python",
                "niveau_requis": "Confirmé (3-7 ans)",
                "obligatoire": True,
                "experience_min_mois": 36,
                "certifications_souhaitees": ["Python Institute PCAP"],
                "outils_associes": ["Django", "FastAPI", "Flask"],
                "contexte_utilisation": "Développement APIs REST et microservices"
            }
        }

class MissionPrincipale(BaseModel):
    """📋 Mission principale du poste"""
    titre: str = Field(..., description="Titre de la mission")
    description: str = Field(..., description="Description détaillée")
    pourcentage_temps: Optional[int] = Field(None, ge=0, le=100, description="% temps consacré à cette mission")
    competences_cles: List[str] = Field(default_factory=list, description="Compétences clés pour cette mission")
    livrables_attendus: List[str] = Field(default_factory=list, description="Livrables attendus")
    
    class Config:
        json_schema_extra = {
            "example": {
                "titre": "Développement architecture microservices",
                "description": "Conception et développement d'APIs REST scalables",
                "pourcentage_temps": 60,
                "competences_cles": ["Python", "FastAPI", "PostgreSQL", "Docker"],
                "livrables_attendus": ["Architecture technique", "APIs documentées", "Tests automatisés"]
            }
        }

class AvantagesSociaux(BaseModel):
    """🎁 Avantages sociaux détaillés"""
    mutuelle_entreprise: bool = Field(default=False, description="Mutuelle prise en charge")
    tickets_restaurant: Optional[int] = Field(None, description="Montant tickets restaurant (€)")
    prime_transport: Optional[int] = Field(None, description="Prime transport mensuelle (€)")
    prime_performance: bool = Field(default=False, description="Prime sur objectifs")
    
    # Congés et temps
    conges_payes: int = Field(default=25, description="Jours de congés payés")
    rtt: Optional[int] = Field(None, description="Jours RTT")
    conges_anciennete: bool = Field(default=False, description="Congés d'ancienneté")
    
    # Formations et développement
    budget_formation_annuel: Optional[int] = Field(None, description="Budget formation annuel (€)")
    conference_tech: bool = Field(default=False, description="Participation conférences techniques")
    certifications_prises_charge: bool = Field(default=False, description="Certifications prises en charge")
    
    # Équipements
    laptop_fourni: bool = Field(default=True, description="Laptop fourni")
    mobile_professionnel: bool = Field(default=False, description="Mobile professionnel")
    ecrans_supplementaires: bool = Field(default=False, description="Écrans supplémentaires")
    
    # Autres avantages
    salle_sport: bool = Field(default=False, description="Salle de sport/Accès partenaire")
    stock_options: bool = Field(default=False, description="Stock options/BSPCE")
    voiture_fonction: bool = Field(default=False, description="Voiture de fonction")
    autres_avantages: List[str] = Field(default_factory=list, description="Autres avantages spécifiques")
    
    def calculer_score_avantages(self) -> float:
        """📊 Calcule un score d'attractivité des avantages"""
        score = 0.0
        
        # Avantages financiers (40%)
        if self.tickets_restaurant and self.tickets_restaurant >= 8:
            score += 0.1
        if self.prime_transport and self.prime_transport >= 50:
            score += 0.1
        if self.prime_performance:
            score += 0.1
        if self.stock_options:
            score += 0.1
        
        # Temps et flexibilité (30%)
        if self.conges_payes >= 30:
            score += 0.1
        if self.rtt and self.rtt >= 10:
            score += 0.1
        if self.conges_anciennete:
            score += 0.1
        
        # Formation et développement (20%)
        if self.budget_formation_annuel and self.budget_formation_annuel >= 2000:
            score += 0.1
        if self.certifications_prises_charge:
            score += 0.05
        if self.conference_tech:
            score += 0.05
        
        # Équipements et confort (10%)
        if self.laptop_fourni:
            score += 0.03
        if self.ecrans_supplementaires:
            score += 0.02
        if self.salle_sport:
            score += 0.05
        
        return min(1.0, score)
    
    class Config:
        json_schema_extra = {
            "example": {
                "mutuelle_entreprise": True,
                "tickets_restaurant": 10,
                "prime_transport": 75,
                "prime_performance": True,
                "conges_payes": 28,
                "rtt": 12,
                "budget_formation_annuel": 3000,
                "certifications_prises_charge": True,
                "laptop_fourni": True,
                "ecrans_supplementaires": True,
                "autres_avantages": ["Parking gratuit", "Café illimité", "Team building trimestriels"]
            }
        }

class EnvironnementEntreprise(BaseModel):
    """🏢 Environnement et culture d'entreprise"""
    taille_entreprise: TailleEntrepriseEnum = Field(..., description="Taille de l'entreprise")
    secteur_activite: str = Field(..., description="Secteur d'activité principal")
    taille_equipe: Optional[int] = Field(None, ge=1, description="Taille de l'équipe de travail")
    manager_direct: Optional[str] = Field(None, description="Poste du manager direct")
    
    # Culture et valeurs
    valeurs_entreprise: List[str] = Field(default_factory=list, description="Valeurs de l'entreprise")
    culture_collaborative: bool = Field(default=True, description="Culture collaborative")
    innovation_encouragee: bool = Field(default=False, description="Innovation encouragée")
    autonomie_niveau: Optional[str] = Field(None, description="Niveau d'autonomie accordé")
    
    # Environnement technique
    stack_technique_principale: List[str] = Field(default_factory=list, description="Stack technique principale")
    methodologie_dev: List[str] = Field(default_factory=list, description="Méthodologies de développement")
    outils_collaboration: List[str] = Field(default_factory=list, description="Outils de collaboration")
    
    # Perspectives d'évolution
    evolution_interne_possible: bool = Field(default=True, description="Évolution interne possible")
    plans_carriere_definis: bool = Field(default=False, description="Plans de carrière définis")
    mobilite_internationale: bool = Field(default=False, description="Mobilité internationale possible")
    
    # Diversité et inclusion
    politique_diversite: bool = Field(default=False, description="Politique diversité active")
    equilibre_vie_pro_perso: Optional[str] = Field(None, description="Approche équilibre vie pro/perso")
    
    class Config:
        json_schema_extra = {
            "example": {
                "taille_entreprise": "PME (10-249 salariés)",
                "secteur_activite": "Technologies de l'information",
                "taille_equipe": 8,
                "manager_direct": "Lead Developer",
                "valeurs_entreprise": ["Innovation", "Transparence", "Bienveillance"],
                "culture_collaborative": True,
                "innovation_encouragee": True,
                "autonomie_niveau": "Élevée",
                "stack_technique_principale": ["Python", "React", "PostgreSQL", "AWS"],
                "methodologie_dev": ["Agile", "Scrum", "CI/CD"],
                "evolution_interne_possible": True,
                "plans_carriere_definis": True
            }
        }

class LocalisationPoste(BaseModel):
    """📍 Localisation et mobilité du poste"""
    ville_principale: str = Field(..., description="Ville principale de travail")
    code_postal: Optional[str] = Field(None, description="Code postal")
    adresse_complete: Optional[str] = Field(None, description="Adresse complète")
    
    # Transport et accessibilité
    acces_transport_public: bool = Field(default=False, description="Accessible en transport public")
    lignes_transport: List[str] = Field(default_factory=list, description="Lignes de transport proches")
    parking_disponible: bool = Field(default=False, description="Parking disponible")
    parking_gratuit: bool = Field(default=False, description="Parking gratuit")
    
    # Flexibilité géographique
    flexibilite_travail: FlexibiliteTravailEnum = Field(..., description="Flexibilité télétravail")
    deplacements_frequents: bool = Field(default=False, description="Déplacements fréquents requis")
    pourcentage_deplacement: Optional[int] = Field(None, ge=0, le=100, description="% de déplacements")
    zones_deplacement: List[str] = Field(default_factory=list, description="Zones géographiques de déplacement")
    
    # Sites multiples
    plusieurs_sites: bool = Field(default=False, description="Travail sur plusieurs sites")
    sites_additionnels: List[str] = Field(default_factory=list, description="Sites additionnels")
    
    def calculer_score_accessibilite(self) -> float:
        """🚗 Calcule un score d'accessibilité du poste"""
        score = 0.0
        
        # Transport public (40%)
        if self.acces_transport_public:
            score += 0.3
            if len(self.lignes_transport) >= 2:
                score += 0.1
        
        # Parking (30%)
        if self.parking_disponible:
            score += 0.2
            if self.parking_gratuit:
                score += 0.1
        
        # Flexibilité (30%)
        if self.flexibilite_travail in [FlexibiliteTravailEnum.HYBRIDE_2J, FlexibiliteTravailEnum.HYBRIDE_3J]:
            score += 0.2
        elif self.flexibilite_travail in [FlexibiliteTravailEnum.FULL_REMOTE, FlexibiliteTravailEnum.MAJORITAIREMENT_REMOTE]:
            score += 0.3
        
        return min(1.0, score)
    
    class Config:
        json_schema_extra = {
            "example": {
                "ville_principale": "Paris",
                "code_postal": "75008",
                "acces_transport_public": True,
                "lignes_transport": ["Métro ligne 1", "RER A", "Bus 73"],
                "parking_disponible": True,
                "parking_gratuit": False,
                "flexibilite_travail": "Hybride 2j télétravail/semaine",
                "deplacements_frequents": False,
                "pourcentage_deplacement": 10
            }
        }

class ProcessusRecrutement(BaseModel):
    """🎯 Processus de recrutement détaillé"""
    etapes_process: List[str] = Field(..., description="Étapes du processus")
    duree_process_semaines: Optional[int] = Field(None, ge=1, description="Durée estimée en semaines")
    
    # Types d'entretiens
    entretien_rh: bool = Field(default=True, description="Entretien RH")
    entretien_technique: bool = Field(default=False, description="Entretien technique")
    test_technique: bool = Field(default=False, description="Test technique")
    mise_en_situation: bool = Field(default=False, description="Mise en situation")
    rencontre_equipe: bool = Field(default=False, description="Rencontre avec l'équipe")
    
    # Délais et feedback
    feedback_sous_jours: Optional[int] = Field(None, ge=1, description="Délai de feedback (jours)")
    prise_poste_souhaitee: Optional[date] = Field(None, description="Date de prise de poste souhaitée")
    urgence_recrutement: bool = Field(default=False, description="Recrutement urgent")
    
    # Informations complémentaires
    contact_recruteur: Optional[str] = Field(None, description="Contact recruteur")
    questions_frequentes: List[str] = Field(default_factory=list, description="Questions fréquentes du process")
    conseils_candidat: List[str] = Field(default_factory=list, description="Conseils aux candidats")
    
    class Config:
        json_schema_extra = {
            "example": {
                "etapes_process": [
                    "Entretien RH (30min)",
                    "Test technique (2h)",
                    "Entretien technique avec le lead (1h)",
                    "Rencontre équipe (30min)",
                    "Décision finale"
                ],
                "duree_process_semaines": 3,
                "entretien_rh": True,
                "entretien_technique": True,
                "test_technique": True,
                "rencontre_equipe": True,
                "feedback_sous_jours": 5,
                "urgence_recrutement": False,
                "conseils_candidat": [
                    "Préparer des exemples concrets de projets",
                    "Maîtriser notre stack technique",
                    "Montrer sa motivation pour le produit"
                ]
            }
        }

class JobDataAdvanced(BaseModel):
    """💼 Données job avancées issues du parsing Commitment- + enrichissement"""
    
    # Informations de base (issues du parsing GPT)
    titre_poste: str = Field(..., description="Titre du poste")
    entreprise: str = Field(..., description="Nom de l'entreprise")
    type_contrat: TypeContratEnum = Field(..., description="Type de contrat")
    
    # Localisation et environnement
    localisation: LocalisationPoste = Field(..., description="Localisation détaillée")
    environnement_travail: EnvironnementTravailEnum = Field(..., description="Environnement de travail")
    environnement_entreprise: EnvironnementEntreprise = Field(..., description="Environnement d'entreprise")
    
    # Rémunération et avantages
    salaire_min: Optional[int] = Field(None, ge=0, description="Salaire minimum (€ brut annuel)")
    salaire_max: Optional[int] = Field(None, ge=0, description="Salaire maximum (€ brut annuel)")
    salaire_indicatif: Optional[str] = Field(None, description="Indication salariale textuelle")
    avantages_sociaux: AvantagesSociaux = Field(..., description="Avantages sociaux détaillés")
    
    # Missions et compétences
    missions_principales: List[MissionPrincipale] = Field(..., description="Missions principales du poste")
    competences_requises: List[CompetenceRequise] = Field(..., description="Compétences requises détaillées")
    competences_souhaitees: List[CompetenceRequise] = Field(default_factory=list, description="Compétences souhaitées")
    
    # Profil recherché
    niveau_experience: NiveauRequis = Field(..., description="Niveau d'expérience requis")
    formation_souhaitee: Optional[str] = Field(None, description="Formation souhaitée")
    langues_requises: List[str] = Field(default_factory=list, description="Langues requises")
    
    # Recrutement
    type_recrutement: TypeRecrutementEnum = Field(..., description="Type de recrutement")
    processus_recrutement: ProcessusRecrutement = Field(..., description="Processus de recrutement")
    
    # Métadonnées
    date_publication: Optional[datetime] = Field(None, description="Date de publication de l'offre")
    date_limite_candidature: Optional[date] = Field(None, description="Date limite de candidature")
    reference_interne: Optional[str] = Field(None, description="Référence interne de l'offre")
    source_parsing: str = Field(default="commitment_job_parser", description="Source du parsing")
    date_parsing: datetime = Field(default_factory=datetime.now, description="Date du parsing")
    
    # Scores calculés
    score_attractivite: Optional[float] = Field(None, ge=0, le=1, description="Score d'attractivité global")
    score_competitivite_salaire: Optional[float] = Field(None, ge=0, le=1, description="Score compétitivité salariale")
    
    @validator('salaire_max')
    def validate_salaire_coherence(cls, v, values):
        """Valide la cohérence salaire min/max"""
        if v and 'salaire_min' in values and values['salaire_min']:
            if v < values['salaire_min']:
                raise ValueError('Salaire maximum ne peut être inférieur au minimum')
        return v
    
    def calculer_score_attractivite(self) -> float:
        """⭐ Calcule un score d'attractivité global de l'offre"""
        score = 0.0
        
        # Rémunération (25%)
        if self.salaire_min and self.salaire_max:
            salaire_moyen = (self.salaire_min + self.salaire_max) / 2
            # Score basé sur le niveau par rapport au marché (simplification)
            if salaire_moyen >= 50000:
                score += 0.25
            elif salaire_moyen >= 40000:
                score += 0.20
            elif salaire_moyen >= 30000:
                score += 0.15
            else:
                score += 0.10
        
        # Avantages sociaux (20%)
        score += self.avantages_sociaux.calculer_score_avantages() * 0.20
        
        # Environnement entreprise (20%)
        env_score = 0.0
        if self.environnement_entreprise.evolution_interne_possible:
            env_score += 0.3
        if self.environnement_entreprise.innovation_encouragee:
            env_score += 0.3
        if len(self.environnement_entreprise.valeurs_entreprise) >= 3:
            env_score += 0.2
        if self.environnement_entreprise.plans_carriere_definis:
            env_score += 0.2
        score += env_score * 0.20
        
        # Flexibilité et localisation (15%)
        score += self.localisation.calculer_score_accessibilite() * 0.15
        
        # Processus de recrutement (10%)
        process_score = 0.0
        if self.processus_recrutement.duree_process_semaines and self.processus_recrutement.duree_process_semaines <= 4:
            process_score += 0.5
        if self.processus_recrutement.feedback_sous_jours and self.processus_recrutement.feedback_sous_jours <= 7:
            process_score += 0.3
        if len(self.processus_recrutement.conseils_candidat) > 0:
            process_score += 0.2
        score += process_score * 0.10
        
        # Clarté des missions (10%)
        missions_score = min(1.0, len(self.missions_principales) / 3)
        score += missions_score * 0.10
        
        self.score_attractivite = min(1.0, score)
        return self.score_attractivite
    
    def analyser_adequation_competences(self, competences_candidat: List[str]) -> Dict[str, Any]:
        """🎯 Analyse l'adéquation entre les compétences requises et celles du candidat"""
        
        competences_obligatoires = [c.nom.lower() for c in self.competences_requises if c.obligatoire]
        competences_souhaitees_noms = [c.nom.lower() for c in self.competences_souhaitees]
        competences_candidat_lower = [c.lower() for c in competences_candidat]
        
        # Matching compétences obligatoires
        obligatoires_matchees = [c for c in competences_obligatoires if c in competences_candidat_lower]
        taux_match_obligatoires = len(obligatoires_matchees) / len(competences_obligatoires) if competences_obligatoires else 1.0
        
        # Matching compétences souhaitées
        souhaitees_matchees = [c for c in competences_souhaitees_noms if c in competences_candidat_lower]
        taux_match_souhaitees = len(souhaitees_matchees) / len(competences_souhaitees_noms) if competences_souhaitees_noms else 0.0
        
        # Score global compétences
        score_competences = taux_match_obligatoires * 0.7 + taux_match_souhaitees * 0.3
        
        # Compétences manquantes critiques
        obligatoires_manquantes = [c for c in competences_obligatoires if c not in competences_candidat_lower]
        
        return {
            "score_adequation_competences": round(score_competences, 3),
            "taux_match_obligatoires": round(taux_match_obligatoires, 3),
            "taux_match_souhaitees": round(taux_match_souhaitees, 3),
            "competences_obligatoires_matchees": obligatoires_matchees,
            "competences_souhaitees_matchees": souhaitees_matchees,
            "competences_manquantes_critiques": obligatoires_manquantes,
            "total_competences_requises": len(competences_obligatoires),
            "total_competences_matchees": len(obligatoires_matchees) + len(souhaitees_matchees)
        }
    
    class Config:
        json_schema_extra = {
            "example": {
                "titre_poste": "Développeur Python Senior",
                "entreprise": "TechCorp Innovation",
                "type_contrat": "CDI",
                "localisation": {
                    "ville_principale": "Paris",
                    "flexibilite_travail": "Hybride 2j télétravail/semaine",
                    "acces_transport_public": True
                },
                "environnement_travail": "Bureau partagé",
                "salaire_min": 50000,
                "salaire_max": 65000,
                "niveau_experience": "Confirmé (3-7 ans)",
                "type_recrutement": "Renfort d'équipe",
                "competences_requises": [
                    {
                        "nom": "Python",
                        "niveau_requis": "Confirmé (3-7 ans)",
                        "obligatoire": True,
                        "experience_min_mois": 36
                    }
                ]
            }
        }
