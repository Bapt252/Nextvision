"""
📜 Modèles Préférences Contrats NEXTEN
Gestion avancée types contrats avec scoring et flexibilité candidat/offre

Author: NEXTEN Team
Version: 1.0.0
Integration: Commitment- → Nextvision Bridge
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, date
from enum import Enum

# Import des énumérations communes
from .questionnaire_advanced import TypeContratEnum

class StatutJuridiqueEnum(str, Enum):
    """⚖️ Statuts juridiques pour freelance/indépendant"""
    SALARIE = "Salarié"
    MICRO_ENTREPRISE = "Micro-entreprise"
    SASU = "SASU"
    EURL = "EURL"
    PORTAGE_SALARIAL = "Portage salarial"
    COOPERATIVES = "Coopératives"
    ASSOCIATION = "Association"

class AvantageContratEnum(str, Enum):
    """🎁 Types d'avantages par type de contrat"""
    SECURITE_EMPLOI = "Sécurité de l'emploi"
    FLEXIBILITE = "Flexibilité"
    REMUNERATION_ELEVEE = "Rémunération élevée"
    EXPERIENCE_VARIEE = "Expérience variée"
    AUTONOMIE = "Autonomie"
    FORMATION = "Formation/Évolution"
    AVANTAGES_SOCIAUX = "Avantages sociaux"
    RESEAUTAGE = "Réseautage"
    INNOVATION = "Innovation/Projets"

class RisqueContratEnum(str, Enum):
    """⚠️ Risques par type de contrat"""
    INSECURITE = "Insécurité financière"
    ABSENCE_EVOLUTION = "Absence d'évolution"
    CHARGES_ADMINISTRATIVES = "Charges administratives"
    ISOLATION = "Isolation professionnelle"
    SURCHARGE_TRAVAIL = "Surcharge de travail"
    PAS_FORMATION = "Pas de formation"
    PAS_CONGES_PAYES = "Pas de congés payés"
    INSTABILITE = "Instabilité missions"

class ContractPreference(BaseModel):
    """📜 Préférence pour un type de contrat"""
    type_contrat: TypeContratEnum = Field(..., description="Type de contrat")
    priorite: int = Field(..., ge=1, le=10, description="Priorité (1=préféré, 10=moins préféré)")
    acceptabilite: float = Field(..., ge=0, le=1, description="Score d'acceptabilité (0=refusé, 1=idéal)")
    
    # Conditions spécifiques
    duree_min_mois: Optional[int] = Field(None, ge=1, description="Durée minimum en mois (pour CDD/missions)")
    duree_max_mois: Optional[int] = Field(None, ge=1, description="Durée maximum en mois")
    remuneration_min: Optional[int] = Field(None, ge=0, description="Rémunération minimum (€/an ou €/jour)")
    remuneration_max: Optional[int] = Field(None, ge=0, description="Rémunération maximum acceptable")
    
    # Flexibilités acceptées
    teletravail_requis: Optional[bool] = Field(None, description="Télétravail requis pour ce type")
    deplacement_acceptable: bool = Field(default=True, description="Déplacements acceptables")
    horaires_flexibles: bool = Field(default=False, description="Horaires flexibles requis")
    
    # Justifications
    avantages_recherches: List[AvantageContratEnum] = Field(default_factory=list, description="Avantages recherchés")
    risques_acceptes: List[RisqueContratEnum] = Field(default_factory=list, description="Risques acceptés")
    conditions_specifiques: List[str] = Field(default_factory=list, description="Conditions spécifiques")
    
    # Expérience passée
    deja_experimente: bool = Field(default=False, description="Déjà expérimenté ce type de contrat")
    satisfaction_passee: Optional[int] = Field(None, ge=1, le=5, description="Satisfaction passée (1-5)")
    
    @validator('priorite')
    def validate_priorite(cls, v):
        if v < 1 or v > 10:
            raise ValueError('Priorité doit être entre 1 et 10')
        return v
    
    @validator('satisfaction_passee')
    def validate_satisfaction(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Satisfaction doit être entre 1 et 5')
        return v
    
    @validator('duree_max_mois')
    def validate_duree_coherence(cls, v, values):
        if v and 'duree_min_mois' in values and values['duree_min_mois']:
            if v < values['duree_min_mois']:
                raise ValueError('Durée maximum ne peut être inférieure à la durée minimum')
        return v
    
    @validator('remuneration_max')
    def validate_remuneration_coherence(cls, v, values):
        if v and 'remuneration_min' in values and values['remuneration_min']:
            if v < values['remuneration_min']:
                raise ValueError('Rémunération maximum ne peut être inférieure au minimum')
        return v
    
    def calculer_score_attractivite(self) -> float:
        """⭐ Calcule le score d'attractivité de ce type de contrat pour le candidat"""
        score = self.acceptabilite
        
        # Bonus pour expérience positive passée
        if self.deja_experimente and self.satisfaction_passee:
            bonus_experience = (self.satisfaction_passee - 1) / 4 * 0.2  # Jusqu'à +20%
            score += bonus_experience
        
        # Bonus pour priorité élevée
        bonus_priorite = max(0, (11 - self.priorite) / 10 * 0.15)  # Jusqu'à +15%
        score += bonus_priorite
        
        # Bonus pour spécificité des conditions
        if self.conditions_specifiques:
            score += 0.05
        
        return min(1.0, score)
    
    class Config:
        json_schema_extra = {
            "example": {
                "type_contrat": "CDI",
                "priorite": 1,
                "acceptabilite": 1.0,
                "duree_min_mois": None,
                "remuneration_min": 45000,
                "remuneration_max": 65000,
                "teletravail_requis": False,
                "horaires_flexibles": True,
                "avantages_recherches": ["Sécurité de l'emploi", "Formation/Évolution"],
                "risques_acceptes": [],
                "deja_experimente": True,
                "satisfaction_passee": 4,
                "conditions_specifiques": ["Équipe technique mature", "Projets innovants"]
            }
        }

class FlexibiliteContractuelle(BaseModel):
    """🔄 Flexibilité contractuelle du candidat"""
    
    # Polyvalence contractuelle
    accepte_transitions: bool = Field(default=True, description="Accepte transitions entre types contrats")
    periode_essai_extended: bool = Field(default=False, description="Accepte période d'essai étendue")
    clause_non_concurrence: bool = Field(default=False, description="Accepte clause de non-concurrence")
    
    # Négociations possibles
    remuneration_variable: bool = Field(default=False, description="Accepte part variable importante")
    stock_options_lieu_salaire: bool = Field(default=False, description="Stock-options en lieu de salaire")
    avantages_lieu_salaire: bool = Field(default=True, description="Avantages en nature lieu salaire")
    
    # Adaptations temporelles
    debut_differe_acceptable: bool = Field(default=True, description="Début différé acceptable")
    duree_flexible: bool = Field(default=True, description="Durée de contrat flexible")
    renouvellement_automatique: bool = Field(default=False, description="Renouvellement automatique souhaité")
    
    # Conditions particulières
    multi_employeur: bool = Field(default=False, description="Multi-employeur acceptable (temps partagé)")
    mission_ponctuelle: bool = Field(default=False, description="Missions ponctuelles acceptables")
    formation_integree: bool = Field(default=True, description="Formation intégrée au contrat souhaitée")
    
    # Limites
    exclusions_absolues: List[TypeContratEnum] = Field(default_factory=list, description="Types de contrats absolument refusés")
    duree_engagement_max: Optional[int] = Field(None, description="Durée d'engagement maximum (mois)")
    
    def calculer_score_flexibilite(self) -> float:
        """🔄 Calcule un score de flexibilité contractuelle"""
        score = 0.0
        
        # Adaptabilité (40%)
        if self.accepte_transitions:
            score += 0.15
        if self.duree_flexible:
            score += 0.10
        if self.debut_differe_acceptable:
            score += 0.10
        if self.formation_integree:
            score += 0.05
        
        # Ouverture négociation (30%)
        if self.remuneration_variable:
            score += 0.10
        if self.avantages_lieu_salaire:
            score += 0.10
        if self.stock_options_lieu_salaire:
            score += 0.10
        
        # Polyvalence (20%)
        if self.multi_employeur:
            score += 0.10
        if self.mission_ponctuelle:
            score += 0.10
        
        # Clauses acceptées (10%)
        if self.periode_essai_extended:
            score += 0.05
        if self.clause_non_concurrence:
            score += 0.05
        
        # Pénalités pour exclusions
        if len(self.exclusions_absolues) > 3:
            score -= 0.20
        elif len(self.exclusions_absolues) > 1:
            score -= 0.10
        
        return max(0.0, min(1.0, score))
    
    class Config:
        json_schema_extra = {
            "example": {
                "accepte_transitions": True,
                "periode_essai_extended": False,
                "clause_non_concurrence": False,
                "remuneration_variable": True,
                "avantages_lieu_salaire": True,
                "debut_differe_acceptable": True,
                "duree_flexible": True,
                "multi_employeur": False,
                "mission_ponctuelle": True,
                "formation_integree": True,
                "exclusions_absolues": ["Stage"],
                "duree_engagement_max": 60
            }
        }

class FreelanceConfig(BaseModel):
    """💼 Configuration spécifique freelance/indépendant"""
    
    statut_juridique_prefere: Optional[StatutJuridiqueEnum] = Field(None, description="Statut juridique préféré")
    tjm_minimum: Optional[int] = Field(None, ge=50, description="TJM minimum (€)")
    tjm_souhaite: Optional[int] = Field(None, ge=50, description="TJM souhaité (€)")
    
    # Modalités de mission
    duree_mission_min: int = Field(default=1, ge=1, description="Durée mission minimum (mois)")
    duree_mission_max: int = Field(default=12, ge=1, description="Durée mission maximum (mois)")
    preavis_mission: int = Field(default=15, ge=1, description="Préavis fin de mission (jours)")
    
    # Conditions commerciales
    facture_mensuelle: bool = Field(default=True, description="Facturation mensuelle")
    acompte_requis: bool = Field(default=False, description="Acompte requis")
    frais_mission_rembourses: bool = Field(default=True, description="Frais de mission remboursés")
    
    # Organisation
    travail_site_client: bool = Field(default=True, description="Travail sur site client acceptable")
    materiel_fourni: bool = Field(default=False, description="Matériel fourni par client requis")
    management_client: bool = Field(default=True, description="Management par client acceptable")
    
    # Spécialisations
    secteurs_specialises: List[str] = Field(default_factory=list, description="Secteurs de spécialisation")
    competences_phares: List[str] = Field(default_factory=list, description="Compétences phares vendues")
    certifications_valeur: List[str] = Field(default_factory=list, description="Certifications à valeur ajoutée")
    
    # Réseau et développement
    reseau_freelances: bool = Field(default=False, description="Réseau de freelances partenaires")
    portage_acceptable: bool = Field(default=True, description="Portage salarial acceptable")
    exclusivite_acceptable: bool = Field(default=False, description="Exclusivité temporaire acceptable")
    
    @validator('tjm_souhaite')
    def validate_tjm_coherence(cls, v, values):
        if v and 'tjm_minimum' in values and values['tjm_minimum']:
            if v < values['tjm_minimum']:
                raise ValueError('TJM souhaité ne peut être inférieur au TJM minimum')
        return v
    
    @validator('duree_mission_max')
    def validate_duree_mission_coherence(cls, v, values):
        if 'duree_mission_min' in values and values['duree_mission_min']:
            if v < values['duree_mission_min']:
                raise ValueError('Durée mission maximum ne peut être inférieure au minimum')
        return v
    
    def calculer_tjm_recommande(self, salaire_equivalent: int) -> int:
        """💰 Calcule le TJM recommandé basé sur un salaire équivalent"""
        # Formule : (Salaire annuel / 12) / 20 jours * facteur charges (1.6-2.0)
        tjm_base = (salaire_equivalent / 12) / 20
        facteur_charges = 1.8  # Facteur moyen pour charges + marge
        tjm_recommande = int(tjm_base * facteur_charges)
        
        return max(tjm_recommande, self.tjm_minimum or 0)
    
    def estimer_ca_annuel(self, taux_activite: float = 0.8) -> Dict[str, int]:
        """📊 Estime le chiffre d'affaires annuel"""
        if not self.tjm_minimum or not self.tjm_souhaite:
            return {"ca_minimum": 0, "ca_souhaite": 0, "ca_realiste": 0}
        
        jours_travailles_an = int(220 * taux_activite)  # 220 jours ouvrés * taux activité
        
        ca_minimum = self.tjm_minimum * jours_travailles_an
        ca_souhaite = self.tjm_souhaite * jours_travailles_an
        ca_realiste = int((self.tjm_minimum + self.tjm_souhaite) / 2 * jours_travailles_an)
        
        return {
            "ca_minimum": ca_minimum,
            "ca_souhaite": ca_souhaite, 
            "ca_realiste": ca_realiste,
            "jours_travailles": jours_travailles_an,
            "taux_activite": taux_activite
        }
    
    class Config:
        json_schema_extra = {
            "example": {
                "statut_juridique_prefere": "Micro-entreprise",
                "tjm_minimum": 400,
                "tjm_souhaite": 550,
                "duree_mission_min": 3,
                "duree_mission_max": 12,
                "preavis_mission": 15,
                "facture_mensuelle": True,
                "frais_mission_rembourses": True,
                "travail_site_client": True,
                "management_client": True,
                "secteurs_specialises": ["Technologies de l'information", "Finance"],
                "competences_phares": ["Python", "Architecture cloud", "DevOps"],
                "portage_acceptable": True
            }
        }

class AnalysePreferencesContrats(BaseModel):
    """📋 Analyse complète des préférences contractuelles"""
    
    # Préférences par type de contrat
    preferences_contrats: List[ContractPreference] = Field(..., description="Préférences par type de contrat")
    flexibilite_contractuelle: FlexibiliteContractuelle = Field(..., description="Flexibilité contractuelle")
    config_freelance: Optional[FreelanceConfig] = Field(None, description="Configuration freelance (si applicable)")
    
    # Analyse calculée
    type_contrat_ideal: Optional[TypeContratEnum] = Field(None, description="Type de contrat idéal (calculé)")
    score_adaptabilite_contractuelle: Optional[float] = Field(None, ge=0, le=1, description="Score adaptabilité")
    risque_acceptation_global: Optional[float] = Field(None, ge=0, le=1, description="Score de prise de risque")
    
    # Métadonnées
    derniere_analyse: datetime = Field(default_factory=datetime.now, description="Date dernière analyse")
    
    @validator('preferences_contrats')
    def validate_preferences_uniques(cls, v):
        """Valide que chaque type de contrat n'apparaît qu'une fois"""
        types = [p.type_contrat for p in v]
        if len(types) != len(set(types)):
            raise ValueError('Chaque type de contrat ne peut apparaître qu\'une seule fois')
        return v
    
    @validator('preferences_contrats')
    def validate_priorites_uniques(cls, v):
        """Valide que chaque priorité n'apparaît qu'une fois"""
        priorites = [p.priorite for p in v]
        if len(priorites) != len(set(priorites)):
            raise ValueError('Chaque priorité doit être unique')
        return v
    
    def identifier_contrat_ideal(self) -> TypeContratEnum:
        """🎯 Identifie le type de contrat idéal"""
        if not self.preferences_contrats:
            return TypeContratEnum.CDI  # Défaut
        
        # Tri par score d'attractivité
        preferences_triees = sorted(
            self.preferences_contrats,
            key=lambda p: p.calculer_score_attractivite(),
            reverse=True
        )
        
        contrat_ideal = preferences_triees[0].type_contrat
        self.type_contrat_ideal = contrat_ideal
        return contrat_ideal
    
    def calculer_score_adaptabilite_contractuelle(self) -> float:
        """🔄 Calcule le score d'adaptabilité contractuelle"""
        
        # Nombre de types acceptables (acceptabilité > 0.5)
        types_acceptables = len([p for p in self.preferences_contrats if p.acceptabilite >= 0.5])
        
        # Score de flexibilité
        score_flexibilite = self.flexibilite_contractuelle.calculer_score_flexibilite()
        
        # Diversité d'expérience
        types_experimentes = len([p for p in self.preferences_contrats if p.deja_experimente])
        
        # Calcul score global
        score = 0.0
        
        # Nombre de types acceptables (40%)
        if types_acceptables >= 5:
            score += 0.4
        elif types_acceptables >= 3:
            score += 0.3
        elif types_acceptables >= 2:
            score += 0.2
        
        # Flexibilité contractuelle (35%)
        score += score_flexibilite * 0.35
        
        # Expérience diversifiée (25%)
        if types_experimentes >= 3:
            score += 0.25
        elif types_experimentes >= 2:
            score += 0.15
        elif types_experimentes >= 1:
            score += 0.10
        
        self.score_adaptabilite_contractuelle = round(score, 3)
        return self.score_adaptabilite_contractuelle
    
    def calculer_score_prise_risque(self) -> float:
        """⚡ Calcule le score de prise de risque contractuelle"""
        
        score_risque = 0.0
        
        # Analyse des préférences pour contrats risqués
        contrats_risques = [TypeContratEnum.FREELANCE, TypeContratEnum.CDD, TypeContratEnum.INTERIM]
        
        for pref in self.preferences_contrats:
            if pref.type_contrat in contrats_risques:
                # Plus la priorité est élevée (faible numéro) et l'acceptabilité forte, plus le score augmente
                score_type = (11 - pref.priorite) / 10 * pref.acceptabilite
                score_risque += score_type / len(contrats_risques)
        
        # Bonus pour configuration freelance détaillée
        if self.config_freelance and self.config_freelance.tjm_minimum:
            score_risque += 0.2
        
        # Bonus pour acceptation de conditions risquées
        if self.flexibilite_contractuelle.remuneration_variable:
            score_risque += 0.1
        if self.flexibilite_contractuelle.stock_options_lieu_salaire:
            score_risque += 0.1
        if self.flexibilite_contractuelle.multi_employeur:
            score_risque += 0.1
        
        self.risque_acceptation_global = round(min(1.0, score_risque), 3)
        return self.risque_acceptation_global
    
    def analyser_compatibilite_offre(self, type_contrat_offre: TypeContratEnum, 
                                   duree_mois: Optional[int] = None,
                                   remuneration: Optional[int] = None) -> Dict[str, any]:
        """🎯 Analyse la compatibilité avec une offre spécifique"""
        
        # Recherche de la préférence pour ce type de contrat
        preference_trouvee = None
        for pref in self.preferences_contrats:
            if pref.type_contrat == type_contrat_offre:
                preference_trouvee = pref
                break
        
        if not preference_trouvee:
            return {
                "compatible": False,
                "score_compatibilite": 0.0,
                "raison": f"Type de contrat {type_contrat_offre} non accepté"
            }
        
        score_base = preference_trouvee.acceptabilite
        alertes = []
        bonus = 0.0
        
        # Vérification durée
        if duree_mois and preference_trouvee.duree_min_mois:
            if duree_mois < preference_trouvee.duree_min_mois:
                alertes.append(f"Durée ({duree_mois} mois) inférieure au minimum ({preference_trouvee.duree_min_mois} mois)")
                score_base *= 0.7
        
        if duree_mois and preference_trouvee.duree_max_mois:
            if duree_mois > preference_trouvee.duree_max_mois:
                alertes.append(f"Durée ({duree_mois} mois) supérieure au maximum ({preference_trouvee.duree_max_mois} mois)")
                score_base *= 0.8
        
        # Vérification rémunération
        if remuneration and preference_trouvee.remuneration_min:
            if remuneration < preference_trouvee.remuneration_min:
                alertes.append(f"Rémunération ({remuneration}€) inférieure au minimum ({preference_trouvee.remuneration_min}€)")
                score_base *= 0.6
            elif remuneration >= preference_trouvee.remuneration_min * 1.2:
                bonus += 0.1  # Bonus si rémunération > 120% du minimum
        
        # Bonus pour expérience positive passée
        if preference_trouvee.deja_experimente and preference_trouvee.satisfaction_passee and preference_trouvee.satisfaction_passee >= 4:
            bonus += 0.1
        
        # Bonus pour priorité élevée
        if preference_trouvee.priorite <= 3:
            bonus += 0.05
        
        score_final = min(1.0, score_base + bonus)
        compatible = score_final >= 0.5 and not any("inférieure au minimum" in alerte for alerte in alertes)
        
        return {
            "compatible": compatible,
            "score_compatibilite": round(score_final, 3),
            "priorite_candidat": preference_trouvee.priorite,
            "acceptabilite_base": preference_trouvee.acceptabilite,
            "alertes": alertes,
            "bonus_appliques": round(bonus, 3),
            "recommandations": self._generer_recommandations_offre(preference_trouvee, type_contrat_offre)
        }
    
    def _generer_recommandations_offre(self, preference: ContractPreference, 
                                     type_contrat: TypeContratEnum) -> List[str]:
        """💡 Génère des recommandations pour l'offre"""
        recommandations = []
        
        if preference.teletravail_requis:
            recommandations.append("Vérifier la politique de télétravail")
        
        if preference.horaires_flexibles:
            recommandations.append("Mettre en avant la flexibilité horaire")
        
        if preference.avantages_recherches:
            avantages_str = ", ".join([a.value for a in preference.avantages_recherches[:2]])
            recommandations.append(f"Souligner les avantages: {avantages_str}")
        
        if preference.deja_experimente and preference.satisfaction_passee and preference.satisfaction_passee >= 4:
            recommandations.append("Candidat à l'aise avec ce type de contrat")
        
        if type_contrat == TypeContratEnum.FREELANCE and self.config_freelance:
            recommandations.append(f"TJM souhaité: {self.config_freelance.tjm_souhaite}€")
        
        return recommandations
    
    def generer_profil_contractuel(self) -> Dict[str, any]:
        """📊 Génère un profil contractuel complet"""
        
        contrat_ideal = self.identifier_contrat_ideal()
        score_adaptabilite = self.calculer_score_adaptabilite_contractuelle()
        score_risque = self.calculer_score_prise_risque()
        
        # Top 3 des préférences
        top_preferences = sorted(self.preferences_contrats, 
                               key=lambda p: p.calculer_score_attractivite(), 
                               reverse=True)[:3]
        
        # Profil type
        if score_risque >= 0.7:
            profil_type = "Entrepreneur/Risque élevé"
        elif score_adaptabilite >= 0.7:
            profil_type = "Adaptable/Polyvalent"
        elif contrat_ideal == TypeContratEnum.CDI:
            profil_type = "Stabilité/Sécurité"
        else:
            profil_type = "Mixte"
        
        return {
            "profil_type": profil_type,
            "contrat_ideal": contrat_ideal,
            "top_3_preferences": [
                {
                    "type": pref.type_contrat,
                    "score": pref.calculer_score_attractivite(),
                    "priorite": pref.priorite
                } for pref in top_preferences
            ],
            "scores": {
                "adaptabilite_contractuelle": score_adaptabilite,
                "prise_risque": score_risque,
                "flexibilite": self.flexibilite_contractuelle.calculer_score_flexibilite()
            },
            "caracteristiques": {
                "types_acceptables": len([p for p in self.preferences_contrats if p.acceptabilite >= 0.5]),
                "types_experimentes": len([p for p in self.preferences_contrats if p.deja_experimente]),
                "exclusions_absolues": len(self.flexibilite_contractuelle.exclusions_absolues),
                "config_freelance": self.config_freelance is not None
            },
            "recommandations_recruteurs": self._generer_recommandations_recruteurs(profil_type, score_adaptabilite)
        }
    
    def _generer_recommandations_recruteurs(self, profil_type: str, score_adaptabilite: float) -> List[str]:
        """💼 Génère des recommandations pour les recruteurs"""
        recommandations = []
        
        if profil_type == "Entrepreneur/Risque élevé":
            recommandations.extend([
                "Proposer des missions d'expertise ou projets innovants",
                "Mettre en avant l'autonomie et la responsabilité",
                "Considérer des packages rémunération variable"
            ])
        elif profil_type == "Adaptable/Polyvalent":
            recommandations.extend([
                "Candidat flexible sur le type de contrat",
                "Possibilité d'évolution contractuelle dans l'entreprise",
                "Adapté aux structures en transformation"
            ])
        elif profil_type == "Stabilité/Sécurité":
            recommandations.extend([
                "Mettre en avant la sécurité de l'emploi",
                "Souligner les perspectives d'évolution interne",
                "Privilégier CDI avec période d'essai standard"
            ])
        
        if score_adaptabilite >= 0.8:
            recommandations.append("Très haute adaptabilité - candidat fiable pour tous types de missions")
        
        return recommandations
    
    class Config:
        json_schema_extra = {
            "example": {
                "preferences_contrats": [
                    {
                        "type_contrat": "CDI",
                        "priorite": 1,
                        "acceptabilite": 1.0,
                        "remuneration_min": 45000
                    },
                    {
                        "type_contrat": "Freelance",
                        "priorite": 2,
                        "acceptabilite": 0.8,
                        "remuneration_min": 400
                    }
                ],
                "flexibilite_contractuelle": {
                    "accepte_transitions": True,
                    "duree_flexible": True,
                    "remuneration_variable": True
                },
                "config_freelance": {
                    "tjm_minimum": 400,
                    "tjm_souhaite": 550,
                    "duree_mission_min": 3
                }
            }
        }
