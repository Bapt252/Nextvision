"""
🎯 Modèles Analyse Sectorielle NEXTEN
Analyse avancée compatibilité secteurs candidat/offres avec scoring intelligent

Author: NEXTEN Team
Version: 1.0.0
Integration: Commitment- → Nextvision Bridge
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime
from enum import Enum
import re

class CategorieSecteurEnum(str, Enum):
    """🏭 Catégories macro de secteurs"""
    TECHNOLOGIE = "Technologie"
    FINANCE = "Finance"
    SANTE = "Santé"
    EDUCATION = "Éducation"
    COMMERCE = "Commerce"
    INDUSTRIE = "Industrie"
    SERVICES = "Services"
    MEDIA = "Médias & Communication"
    ENERGIE = "Énergie"
    TRANSPORT = "Transport & Logistique"
    IMMOBILIER = "Immobilier"
    AGRICULTURE = "Agriculture"
    TOURISME = "Tourisme & Hôtellerie"
    LUXE = "Luxe"
    JURIDIQUE = "Juridique"
    CONSULTING = "Conseil"
    RECHERCHE = "Recherche & Développement"
    ASSOCIATIF = "Associatif & ONG"
    PUBLIC = "Secteur Public"
    STARTUP = "Startups & Innovation"

class NiveauAffiniteEnum(str, Enum):
    """❤️ Niveaux d'affinité sectorielle"""
    PASSION = "Passion"
    TRES_INTERESSE = "Très intéressé"
    INTERESSE = "Intéressé"
    NEUTRE = "Neutre"
    PEU_INTERESSE = "Peu intéressé"
    REDHIBITOIRE = "Rédhibitoire"

class TypeExperienceEnum(str, Enum):
    """💼 Types d'expérience sectorielle"""
    EXPERIENCE_DIRECTE = "Expérience directe"
    EXPERIENCE_CONNEXE = "Expérience connexe"
    PROJET_PERSONNEL = "Projet personnel"
    FORMATION = "Formation spécialisée"
    STAGE = "Stage"
    MISSION_COURTE = "Mission courte"
    VEILLE_ACTIVE = "Veille active"
    AUCUNE = "Aucune expérience"

class SecteurDetaille(BaseModel):
    """🏢 Secteur détaillé avec métadonnées"""
    nom: str = Field(..., description="Nom du secteur")
    categorie: CategorieSecteurEnum = Field(..., description="Catégorie macro")
    sous_secteurs: List[str] = Field(default_factory=list, description="Sous-secteurs spécifiques")
    
    # Métadonnées économiques
    taille_marche: Optional[str] = Field(None, description="Taille du marché (Petite/Moyenne/Grande)")
    croissance_tendance: Optional[str] = Field(None, description="Tendance de croissance")
    niveau_innovation: Optional[int] = Field(None, ge=1, le=5, description="Niveau d'innovation (1-5)")
    
    # Compétences typiques
    competences_transverses: List[str] = Field(default_factory=list, description="Compétences transversales typiques")
    technologies_courantes: List[str] = Field(default_factory=list, description="Technologies couramment utilisées")
    
    # Conditions de travail typiques
    culture_type: Optional[str] = Field(None, description="Type de culture d'entreprise typique")
    rythme_travail: Optional[str] = Field(None, description="Rythme de travail typique")
    
    @validator('niveau_innovation')
    def validate_innovation(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Niveau innovation doit être entre 1 et 5')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "nom": "Technologies de l'information",
                "categorie": "Technologie",
                "sous_secteurs": ["Développement logiciel", "Infrastructure IT", "Cybersécurité", "Data Science"],
                "taille_marche": "Grande",
                "croissance_tendance": "Forte croissance",
                "niveau_innovation": 5,
                "competences_transverses": ["Résolution de problèmes", "Esprit analytique", "Apprentissage continu"],
                "technologies_courantes": ["Python", "JavaScript", "Cloud", "DevOps"],
                "culture_type": "Innovation et agilité",
                "rythme_travail": "Soutenu avec flexibilité"
            }
        }

class ExperienceSectorielle(BaseModel):
    """🎯 Expérience dans un secteur spécifique"""
    secteur: str = Field(..., description="Nom du secteur")
    type_experience: TypeExperienceEnum = Field(..., description="Type d'expérience")
    duree_mois: int = Field(default=0, ge=0, description="Durée en mois")
    niveau_exposition: int = Field(..., ge=1, le=5, description="Niveau d'exposition (1=faible, 5=forte)")
    
    # Détails de l'expérience
    entreprises: List[str] = Field(default_factory=list, description="Entreprises dans ce secteur")
    projets_notables: List[str] = Field(default_factory=list, description="Projets notables")
    competences_acquises: List[str] = Field(default_factory=list, description="Compétences acquises spécifiques")
    
    # Évaluation
    satisfaction_experience: Optional[int] = Field(None, ge=1, le=5, description="Satisfaction (1-5)")
    apprentissages_cles: List[str] = Field(default_factory=list, description="Apprentissages clés")
    defis_rencontres: List[str] = Field(default_factory=list, description="Défis rencontrés")
    
    # Perspective future
    souhait_continuer: bool = Field(default=True, description="Souhait de continuer dans ce secteur")
    domaines_approfondissement: List[str] = Field(default_factory=list, description="Domaines à approfondir")
    
    @validator('niveau_exposition', 'satisfaction_experience')
    def validate_scores(cls, v, field):
        if v is not None and (v < 1 or v > 5):
            raise ValueError(f'{field.name} doit être entre 1 et 5')
        return v
    
    def calculer_score_experience(self) -> float:
        """📊 Calcule un score d'expérience pour ce secteur"""
        score = 0.0
        
        # Type d'expérience (40%)
        type_scores = {
            TypeExperienceEnum.EXPERIENCE_DIRECTE: 1.0,
            TypeExperienceEnum.EXPERIENCE_CONNEXE: 0.7,
            TypeExperienceEnum.STAGE: 0.5,
            TypeExperienceEnum.MISSION_COURTE: 0.4,
            TypeExperienceEnum.PROJET_PERSONNEL: 0.3,
            TypeExperienceEnum.FORMATION: 0.2,
            TypeExperienceEnum.VEILLE_ACTIVE: 0.1,
            TypeExperienceEnum.AUCUNE: 0.0
        }
        score += type_scores.get(self.type_experience, 0.0) * 0.4
        
        # Durée (20%)
        if self.duree_mois > 0:
            duree_score = min(1.0, self.duree_mois / 36)  # 3 ans = score max
            score += duree_score * 0.2
        
        # Niveau d'exposition (20%)
        score += (self.niveau_exposition - 1) / 4 * 0.2  # Normalisation 1-5 vers 0-1
        
        # Satisfaction (10%)
        if self.satisfaction_experience:
            score += (self.satisfaction_experience - 1) / 4 * 0.1
        
        # Richesse de l'expérience (10%)
        richesse = len(self.competences_acquises) + len(self.projets_notables)
        richesse_score = min(1.0, richesse / 10)
        score += richesse_score * 0.1
        
        return round(score, 3)
    
    class Config:
        json_schema_extra = {
            "example": {
                "secteur": "Technologies de l'information",
                "type_experience": "Expérience directe",
                "duree_mois": 60,
                "niveau_exposition": 5,
                "entreprises": ["TechCorp", "InnovIT"],
                "projets_notables": ["Migration cloud AWS", "API microservices"],
                "competences_acquises": ["Architecture cloud", "DevOps", "Kubernetes"],
                "satisfaction_experience": 4,
                "souhait_continuer": True,
                "domaines_approfondissement": ["IA/ML", "Cybersécurité"]
            }
        }

class PreferenceSectorielle(BaseModel):
    """❤️ Préférence pour un secteur avec justification"""
    secteur: str = Field(..., description="Nom du secteur")
    niveau_affinite: NiveauAffiniteEnum = Field(..., description="Niveau d'affinité")
    priorite: int = Field(..., ge=1, le=20, description="Priorité (1=le plus important)")
    
    # Justification de la préférence
    raisons_attraction: List[str] = Field(default_factory=list, description="Raisons d'attraction")
    raisons_rejet: List[str] = Field(default_factory=list, description="Raisons de rejet (si négatif)")
    
    # Conditions spécifiques
    sous_secteurs_preferes: List[str] = Field(default_factory=list, description="Sous-secteurs préférés")
    taille_entreprise_souhaitee: List[str] = Field(default_factory=list, description="Tailles d'entreprise souhaitées")
    types_postes_vises: List[str] = Field(default_factory=list, description="Types de postes visés")
    
    # Flexibilité
    ouvert_decouverte: bool = Field(default=False, description="Ouvert à la découverte de ce secteur")
    conditions_acceptation: List[str] = Field(default_factory=list, description="Conditions pour accepter ce secteur")
    
    @validator('priorite')
    def validate_priorite(cls, v):
        if v < 1 or v > 20:
            raise ValueError('Priorité doit être entre 1 et 20')
        return v
    
    def calculer_score_affinite(self) -> float:
        """❤️ Calcule un score d'affinité numérique"""
        affinite_scores = {
            NiveauAffiniteEnum.PASSION: 1.0,
            NiveauAffiniteEnum.TRES_INTERESSE: 0.8,
            NiveauAffiniteEnum.INTERESSE: 0.6,
            NiveauAffiniteEnum.NEUTRE: 0.4,
            NiveauAffiniteEnum.PEU_INTERESSE: 0.2,
            NiveauAffiniteEnum.REDHIBITOIRE: 0.0
        }
        
        base_score = affinite_scores.get(self.niveau_affinite, 0.4)
        
        # Bonus pour spécificité des préférences
        if self.sous_secteurs_preferes:
            base_score += 0.1
        if self.types_postes_vises:
            base_score += 0.1
        if self.ouvert_decouverte and self.niveau_affinite == NiveauAffiniteEnum.NEUTRE:
            base_score += 0.2
        
        return min(1.0, base_score)
    
    class Config:
        json_schema_extra = {
            "example": {
                "secteur": "Technologies de l'information",
                "niveau_affinite": "Passion",
                "priorite": 1,
                "raisons_attraction": [
                    "Innovation constante",
                    "Impact sur la société",
                    "Opportunités d'apprentissage",
                    "Évolutions de carrière"
                ],
                "sous_secteurs_preferes": ["IA/ML", "Développement web", "DevOps"],
                "taille_entreprise_souhaitee": ["Startup", "PME"],
                "types_postes_vises": ["Lead Developer", "Architect", "CTO"],
                "ouvert_decouverte": True
            }
        }

class AnalyseSectorielleCandidatte(BaseModel):
    """🎯 Analyse sectorielle complète d'un candidat"""
    
    # Préférences déclarées
    preferences_sectorielles: List[PreferenceSectorielle] = Field(..., description="Préférences sectorielles déclarées")
    secteurs_redhibitoires: List[str] = Field(default_factory=list, description="Secteurs absolument refusés")
    
    # Expériences sectorielles
    experiences_sectorielles: List[ExperienceSectorielle] = Field(default_factory=list, description="Expériences par secteur")
    
    # Analyse calculée
    secteurs_affinite_forte: List[str] = Field(default_factory=list, description="Secteurs à forte affinité (calculé)")
    secteurs_expertise: List[str] = Field(default_factory=list, description="Secteurs d'expertise (calculé)")
    secteurs_decouverte: List[str] = Field(default_factory=list, description="Secteurs ouverts à découverte")
    
    # Scores globaux
    score_adaptabilite_sectorielle: Optional[float] = Field(None, ge=0, le=1, description="Score d'adaptabilité globale")
    score_specialisation: Optional[float] = Field(None, ge=0, le=1, description="Score de spécialisation")
    
    # Métadonnées
    derniere_analyse: datetime = Field(default_factory=datetime.now, description="Date dernière analyse")
    
    def analyser_compatibilite_secteurs(self) -> Dict[str, float]:
        """🔍 Analyse la compatibilité avec chaque secteur"""
        compatibilites = {}
        
        # Traitement des préférences déclarées
        for pref in self.preferences_sectorielles:
            score_affinite = pref.calculer_score_affinite()
            # Bonus priorité (plus la priorité est faible, plus le bonus est élevé)
            bonus_priorite = max(0, (21 - pref.priorite) / 20 * 0.2)
            compatibilites[pref.secteur] = min(1.0, score_affinite + bonus_priorite)
        
        # Traitement des expériences
        for exp in self.experiences_sectorielles:
            score_exp = exp.calculer_score_experience()
            if exp.secteur in compatibilites:
                # Combinaison préférence + expérience
                score_pref = compatibilites[exp.secteur]
                compatibilites[exp.secteur] = score_pref * 0.6 + score_exp * 0.4
            else:
                # Seulement basé sur l'expérience
                compatibilites[exp.secteur] = score_exp * 0.8  # Pénalité car pas de préférence déclarée
        
        # Secteurs rédhibitoires
        for secteur in self.secteurs_redhibitoires:
            compatibilites[secteur] = 0.0
        
        return compatibilites
    
    def identifier_secteurs_prioritaires(self, top_n: int = 5) -> List[Tuple[str, float]]:
        """⭐ Identifie les secteurs prioritaires pour le candidat"""
        compatibilites = self.analyser_compatibilite_secteurs()
        
        # Tri par score décroissant
        secteurs_tries = sorted(compatibilites.items(), key=lambda x: x[1], reverse=True)
        
        return secteurs_tries[:top_n]
    
    def calculer_score_adaptabilite(self) -> float:
        """🔄 Calcule le score d'adaptabilité sectorielle"""
        
        # Nombre de secteurs avec affinité positive
        secteurs_positifs = len([p for p in self.preferences_sectorielles 
                               if p.niveau_affinite in [NiveauAffiniteEnum.INTERESSE, 
                                                       NiveauAffiniteEnum.TRES_INTERESSE, 
                                                       NiveauAffiniteEnum.PASSION]])
        
        # Diversité des expériences
        nb_secteurs_experience = len(set([exp.secteur for exp in self.experiences_sectorielles]))
        
        # Ouverture à la découverte
        secteurs_ouverts = len([p for p in self.preferences_sectorielles if p.ouvert_decouverte])
        
        # Score basé sur la diversité et l'ouverture
        score = 0.0
        
        # Diversité des préférences (40%)
        if secteurs_positifs >= 5:
            score += 0.4
        elif secteurs_positifs >= 3:
            score += 0.3
        elif secteurs_positifs >= 2:
            score += 0.2
        
        # Diversité des expériences (30%)
        if nb_secteurs_experience >= 3:
            score += 0.3
        elif nb_secteurs_experience >= 2:
            score += 0.2
        elif nb_secteurs_experience >= 1:
            score += 0.1
        
        # Ouverture découverte (20%)
        if secteurs_ouverts >= 3:
            score += 0.2
        elif secteurs_ouverts >= 1:
            score += 0.1
        
        # Ratio secteurs non-rédhibitoires (10%)
        total_preferences = len(self.preferences_sectorielles)
        if total_preferences > 0:
            ratio_non_redhibitoire = (total_preferences - len(self.secteurs_redhibitoires)) / total_preferences
            score += ratio_non_redhibitoire * 0.1
        
        self.score_adaptabilite_sectorielle = round(score, 3)
        return self.score_adaptabilite_sectorielle
    
    def calculer_score_specialisation(self) -> float:
        """🎯 Calcule le score de spécialisation sectorielle"""
        
        if not self.experiences_sectorielles:
            self.score_specialisation = 0.0
            return 0.0
        
        # Secteur avec le plus d'expérience
        experiences_par_secteur = {}
        for exp in self.experiences_sectorielles:
            if exp.secteur not in experiences_par_secteur:
                experiences_par_secteur[exp.secteur] = []
            experiences_par_secteur[exp.secteur].append(exp)
        
        # Score du secteur principal
        secteur_principal = max(experiences_par_secteur.keys(), 
                              key=lambda s: sum(e.duree_mois for e in experiences_par_secteur[s]))
        
        experiences_principales = experiences_par_secteur[secteur_principal]
        duree_totale = sum(exp.duree_mois for exp in experiences_principales)
        niveau_moyen = sum(exp.niveau_exposition for exp in experiences_principales) / len(experiences_principales)
        
        # Score basé sur durée et niveau
        score_duree = min(1.0, duree_totale / 60)  # 5 ans = score max
        score_niveau = (niveau_moyen - 1) / 4  # Normalisation 1-5 vers 0-1
        
        score_specialisation = score_duree * 0.6 + score_niveau * 0.4
        
        self.score_specialisation = round(score_specialisation, 3)
        return self.score_specialisation
    
    def generer_recommandations_sectorielles(self) -> Dict[str, List[str]]:
        """💡 Génère des recommandations sectorielles personnalisées"""
        
        compatibilites = self.analyser_compatibilite_secteurs()
        secteurs_prioritaires = self.identifier_secteurs_prioritaires(3)
        
        recommandations = {
            "secteurs_prioritaires": [s[0] for s in secteurs_prioritaires],
            "points_forts": [],
            "axes_developpement": [],
            "opportunites_decouverte": []
        }
        
        # Points forts
        if self.score_specialisation and self.score_specialisation > 0.7:
            recommandations["points_forts"].append("Forte spécialisation sectorielle")
        
        if self.score_adaptabilite_sectorielle and self.score_adaptabilite_sectorielle > 0.7:
            recommandations["points_forts"].append("Grande adaptabilité intersectorielle")
        
        secteurs_expertise = [exp.secteur for exp in self.experiences_sectorielles 
                             if exp.calculer_score_experience() > 0.8]
        if secteurs_expertise:
            recommandations["points_forts"].append(f"Expertise confirmée: {', '.join(secteurs_expertise[:2])}")
        
        # Axes de développement
        if len(self.experiences_sectorielles) <= 1:
            recommandations["axes_developpement"].append("Diversifier l'expérience sectorielle")
        
        if len(self.secteurs_redhibitoires) > 3:
            recommandations["axes_developpement"].append("Considérer l'ouverture à de nouveaux secteurs")
        
        # Opportunités de découverte
        secteurs_ouverts = [p.secteur for p in self.preferences_sectorielles if p.ouvert_decouverte]
        if secteurs_ouverts:
            recommandations["opportunites_decouverte"] = secteurs_ouverts[:3]
        
        return recommandations
    
    def analyse_complete(self) -> Dict[str, Any]:
        """🎯 Effectue l'analyse sectorielle complète"""
        
        # Calculs des scores
        compatibilites = self.analyser_compatibilite_secteurs()
        secteurs_prioritaires = self.identifier_secteurs_prioritaires(5)
        score_adaptabilite = self.calculer_score_adaptabilite()
        score_specialisation = self.calculer_score_specialisation()
        recommandations = self.generer_recommandations_sectorielles()
        
        # Mise à jour des listes calculées
        self.secteurs_affinite_forte = [s for s, score in compatibilites.items() if score >= 0.7]
        self.secteurs_expertise = [exp.secteur for exp in self.experiences_sectorielles 
                                 if exp.calculer_score_experience() >= 0.8]
        self.secteurs_decouverte = [p.secteur for p in self.preferences_sectorielles if p.ouvert_decouverte]
        
        return {
            "scores": {
                "adaptabilite_sectorielle": score_adaptabilite,
                "specialisation": score_specialisation
            },
            "compatibilites_secteurs": compatibilites,
            "secteurs_prioritaires": secteurs_prioritaires,
            "secteurs_affinite_forte": self.secteurs_affinite_forte,
            "secteurs_expertise": self.secteurs_expertise,
            "secteurs_decouverte": self.secteurs_decouverte,
            "recommandations": recommandations,
            "resume": {
                "nb_secteurs_experience": len(set([exp.secteur for exp in self.experiences_sectorielles])),
                "nb_secteurs_preferes": len([p for p in self.preferences_sectorielles 
                                           if p.niveau_affinite in [NiveauAffiniteEnum.INTERESSE, 
                                                                  NiveauAffiniteEnum.TRES_INTERESSE, 
                                                                  NiveauAffiniteEnum.PASSION]]),
                "nb_secteurs_redhibitoires": len(self.secteurs_redhibitoires),
                "secteur_principal_experience": max([exp.secteur for exp in self.experiences_sectorielles], 
                                                  key=lambda s: sum(e.duree_mois for e in self.experiences_sectorielles if e.secteur == s)) if self.experiences_sectorielles else None
            }
        }
    
    class Config:
        json_schema_extra = {
            "example": {
                "preferences_sectorielles": [
                    {
                        "secteur": "Technologies de l'information",
                        "niveau_affinite": "Passion",
                        "priorite": 1,
                        "raisons_attraction": ["Innovation", "Impact"]
                    }
                ],
                "secteurs_redhibitoires": ["Agriculture", "Industrie lourde"],
                "experiences_sectorielles": [
                    {
                        "secteur": "Technologies de l'information",
                        "type_experience": "Expérience directe",
                        "duree_mois": 60,
                        "niveau_exposition": 5
                    }
                ]
            }
        }

# Dictionnaire des secteurs standards pour mapping automatique
SECTEURS_STANDARDS = {
    "tech": "Technologies de l'information",
    "it": "Technologies de l'information", 
    "informatique": "Technologies de l'information",
    "fintech": "Finance",
    "banque": "Finance",
    "assurance": "Finance",
    "sante": "Santé",
    "medical": "Santé",
    "pharma": "Santé",
    "education": "Éducation",
    "formation": "Éducation",
    "ecommerce": "Commerce",
    "retail": "Commerce",
    "vente": "Commerce",
    "industrie": "Industrie",
    "manufacturing": "Industrie",
    "automobile": "Industrie",
    "conseil": "Conseil",
    "consulting": "Conseil",
    "media": "Médias & Communication",
    "communication": "Médias & Communication",
    "marketing": "Médias & Communication",
    "energie": "Énergie",
    "environnement": "Énergie",
    "transport": "Transport & Logistique",
    "logistique": "Transport & Logistique",
    "immobilier": "Immobilier",
    "construction": "Immobilier",
    "agriculture": "Agriculture",
    "agroalimentaire": "Agriculture",
    "tourisme": "Tourisme & Hôtellerie",
    "hotellerie": "Tourisme & Hôtellerie",
    "luxe": "Luxe",
    "mode": "Luxe",
    "juridique": "Juridique",
    "droit": "Juridique",
    "recherche": "Recherche & Développement",
    "rd": "Recherche & Développement",
    "associatif": "Associatif & ONG",
    "ong": "Associatif & ONG",
    "public": "Secteur Public",
    "administration": "Secteur Public",
    "startup": "Startups & Innovation"
}

def normaliser_secteur(secteur_brut: str) -> str:
    """🔄 Normalise un nom de secteur vers la nomenclature standard"""
    secteur_clean = secteur_brut.lower().strip()
    
    # Recherche directe
    if secteur_clean in SECTEURS_STANDARDS:
        return SECTEURS_STANDARDS[secteur_clean]
    
    # Recherche par mots-clés
    for keyword, secteur_standard in SECTEURS_STANDARDS.items():
        if keyword in secteur_clean:
            return secteur_standard
    
    # Si pas trouvé, capitalisation basique
    return secteur_brut.title()

def suggerer_secteurs_similaires(secteur: str, limite: int = 3) -> List[str]:
    """🔍 Suggère des secteurs similaires basés sur des mots-clés"""
    secteur_clean = secteur.lower()
    suggestions = []
    
    # Mapping de similarités
    similarites = {
        "tech": ["finance", "conseil", "startup"],
        "finance": ["tech", "conseil", "assurance"],
        "sante": ["pharma", "recherche", "medical"],
        "conseil": ["tech", "finance", "management"],
        "commerce": ["marketing", "luxe", "retail"],
        "industrie": ["energie", "automobile", "construction"],
        "media": ["marketing", "communication", "luxe"],
        "education": ["recherche", "formation", "public"],
        "startup": ["tech", "finance", "innovation"]
    }
    
    # Recherche des secteurs similaires
    secteur_normalise = normaliser_secteur(secteur)
    for key, similaires in similarites.items():
        if key in secteur_clean:
            for similaire in similaires:
                secteur_suggere = normaliser_secteur(similaire)
                if secteur_suggere != secteur_normalise and secteur_suggere not in suggestions:
                    suggestions.append(secteur_suggere)
    
    return suggestions[:limite]
