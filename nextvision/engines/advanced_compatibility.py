"""
🎯 Engine Compatibilité Avancée NEXTEN
Moteur de matching intelligent secteurs + contrats + environnement + motivations

Author: NEXTEN Team
Version: 1.0.0
Integration: Commitment- → Nextvision Bridge
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
import logging
import asyncio
from dataclasses import dataclass

# Imports des modèles avancés
from ..models.candidate_complete import CandidatCompletNexfen, CVDataEnriched
from ..models.job_complete import JobDataAdvanced
from ..models.questionnaire_advanced import QuestionnaireCompletAdvanced, PourquoiEcouteEnum
from ..models.sectoral_analysis import AnalyseSectorielleCandidatte, normaliser_secteur
from ..models.contract_preferences import AnalysePreferencesContrats
from ..models.motivation_ranking import ProfilMotivationnel

# Configuration du logging
logger = logging.getLogger(__name__)

@dataclass
class CompatibilityWeights:
    """⚖️ Poids pour le calcul de compatibilité"""
    semantique: float = 0.25
    sectoriel: float = 0.20
    contractuel: float = 0.15
    motivationnel: float = 0.15
    remuneration: float = 0.10
    localisation: float = 0.08
    environnement: float = 0.07

class AdvancedCompatibilityEngine:
    """🎯 Moteur de compatibilité avancée NEXTEN"""
    
    def __init__(self, weights: Optional[CompatibilityWeights] = None):
        """Initialise le moteur avec les poids de compatibilité"""
        self.weights = weights or CompatibilityWeights()
        self.cache_compatibility = {}
        self.performance_metrics = {
            "calculations_count": 0,
            "cache_hits": 0,
            "average_calculation_time": 0.0
        }
        
        logger.info("🎯 AdvancedCompatibilityEngine initialisé")
    
    def apply_adaptive_weighting(self, raison_ecoute: PourquoiEcouteEnum) -> CompatibilityWeights:
        """🔄 Applique la pondération adaptative selon la raison d'écoute"""
        
        weights = CompatibilityWeights()
        
        # Pondération adaptative selon la raison d'écoute
        if raison_ecoute == PourquoiEcouteEnum.REMUNERATION_FAIBLE:
            weights.remuneration = 0.30  # +20%
            weights.motivationnel = 0.20  # +5%
            weights.semantique = 0.20     # -5%
            
        elif raison_ecoute == PourquoiEcouteEnum.POSTE_INADEQUAT:
            weights.semantique = 0.35     # +10%
            weights.sectoriel = 0.25      # +5%
            weights.motivationnel = 0.10  # -5%
            
        elif raison_ecoute == PourquoiEcouteEnum.TROP_LOIN:
            weights.localisation = 0.25   # +17%
            weights.environnement = 0.15  # +8%
            weights.semantique = 0.20     # -5%
            
        elif raison_ecoute == PourquoiEcouteEnum.MANQUE_FLEXIBILITE:
            weights.environnement = 0.20  # +13%
            weights.contractuel = 0.25    # +10%
            weights.motivationnel = 0.20  # +5%
            
        elif raison_ecoute == PourquoiEcouteEnum.MANQUE_PERSPECTIVES:
            weights.motivationnel = 0.25  # +10%
            weights.sectoriel = 0.25      # +5%
            weights.semantique = 0.20     # -5%
            
        logger.info(f"🔄 Pondération adaptative appliquée pour: {raison_ecoute}")
        return weights
    
    async def calculate_advanced_compatibility(
        self, 
        candidat: CandidatCompletNexfen,
        job: JobDataAdvanced,
        use_adaptive_weighting: bool = True
    ) -> Dict[str, Any]:
        """🎯 Calcule la compatibilité avancée candidat/job"""
        
        start_time = datetime.now()
        cache_key = f"{hash(str(candidat.dict()))}_{hash(str(job.dict()))}"
        
        # Vérification cache
        if cache_key in self.cache_compatibility:
            self.performance_metrics["cache_hits"] += 1
            logger.debug("💾 Résultat de compatibilité récupéré du cache")
            return self.cache_compatibility[cache_key]
        
        # Sélection des poids
        if use_adaptive_weighting:
            weights = self.apply_adaptive_weighting(candidat.questionnaire_data.timing.pourquoi_a_lecoute)
        else:
            weights = self.weights
        
        # Calculs de compatibilité par composant
        compatibility_scores = await self._calculate_all_compatibility_components(candidat, job)
        
        # Calcul du score global pondéré
        global_score = self._calculate_weighted_global_score(compatibility_scores, weights)
        
        # Analyse des forces et faiblesses
        strengths, weaknesses = self._analyze_strengths_weaknesses(compatibility_scores, weights)
        
        # Recommandations d'amélioration
        recommendations = self._generate_improvement_recommendations(
            candidat, job, compatibility_scores, weaknesses
        )
        
        # Prédiction de réussite
        success_prediction = self._predict_job_success(candidat, job, compatibility_scores)
        
        # Construction du résultat
        result = {
            "global_score": round(global_score, 3),
            "confidence": self._calculate_confidence_score(compatibility_scores),
            "components": compatibility_scores,
            "weights_used": {
                "semantique": weights.semantique,
                "sectoriel": weights.sectoriel,
                "contractuel": weights.contractuel,
                "motivationnel": weights.motivationnel,
                "remuneration": weights.remuneration,
                "localisation": weights.localisation,
                "environnement": weights.environnement
            },
            "adaptive_weighting": {
                "applied": use_adaptive_weighting,
                "reason": candidat.questionnaire_data.timing.pourquoi_a_lecoute if use_adaptive_weighting else None
            },
            "analysis": {
                "strengths": strengths,
                "weaknesses": weaknesses,
                "recommendations": recommendations,
                "success_prediction": success_prediction
            },
            "metadata": {
                "calculation_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
                "engine_version": "1.0.0",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Mise en cache
        self.cache_compatibility[cache_key] = result
        
        # Métriques de performance
        self.performance_metrics["calculations_count"] += 1
        self._update_performance_metrics(result["metadata"]["calculation_time_ms"])
        
        logger.info(f"✅ Compatibilité calculée: {global_score:.3f} (confiance: {result['confidence']:.3f})")
        return result
    
    async def _calculate_all_compatibility_components(
        self, 
        candidat: CandidatCompletNexfen, 
        job: JobDataAdvanced
    ) -> Dict[str, float]:
        """🧮 Calcule tous les composants de compatibilité"""
        
        # Exécution asynchrone des calculs
        tasks = [
            self._calculate_semantic_compatibility(candidat.cv_data, job),
            self._calculate_sectoral_compatibility(candidat, job),
            self._calculate_contractual_compatibility(candidat, job),
            self._calculate_motivational_compatibility(candidat, job),
            self._calculate_salary_compatibility(candidat, job),
            self._calculate_location_compatibility(candidat, job),
            self._calculate_environment_compatibility(candidat, job)
        ]
        
        results = await asyncio.gather(*tasks)
        
        return {
            "semantique": results[0],
            "sectoriel": results[1],
            "contractuel": results[2],
            "motivationnel": results[3],
            "remuneration": results[4],
            "localisation": results[5],
            "environnement": results[6]
        }
    
    async def _calculate_semantic_compatibility(self, cv: CVDataEnriched, job: JobDataAdvanced) -> float:
        """🔤 Compatibilité sémantique compétences/job"""
        
        if not cv.competences_techniques or not job.competences_requises:
            return 0.3  # Score faible si manque de données
        
        # Extraction des compétences candidat
        competences_candidat = [comp.nom.lower() for comp in cv.competences_techniques]
        
        # Analyse avec la méthode du job
        adequation = job.analyser_adequation_competences(competences_candidat)
        
        # Score basé sur le matching obligatoire + souhaitable
        score_base = adequation["score_adequation_competences"]
        
        # Bonus pour expérience dans les compétences clés
        competences_avec_experience = [
            comp for comp in cv.competences_techniques 
            if comp.annees_experience >= 2 and comp.nom.lower() in [c.nom.lower() for c in job.competences_requises]
        ]
        
        bonus_experience = min(0.2, len(competences_avec_experience) / len(job.competences_requises) * 0.2)
        
        # Bonus pour niveau d'expérience global
        annees_exp_total = cv.annees_experience_totale
        if annees_exp_total >= 5:
            bonus_seniorite = 0.1
        elif annees_exp_total >= 2:
            bonus_seniorite = 0.05
        else:
            bonus_seniorite = 0.0
        
        score_final = min(1.0, score_base + bonus_experience + bonus_seniorite)
        return round(score_final, 3)
    
    async def _calculate_sectoral_compatibility(self, candidat: CandidatCompletNexfen, job: JobDataAdvanced) -> float:
        """🏭 Compatibilité sectorielle"""
        
        # Normalisation du secteur de l'offre
        secteur_job = normaliser_secteur(job.environnement_entreprise.secteur_activite)
        
        # Analyse sectorielle du candidat (simulation basée sur ses préférences)
        secteurs_candidat = candidat.questionnaire_data.secteurs.preferes
        secteurs_redhibitoires = candidat.questionnaire_data.secteurs.redhibitoires
        
        # Vérification secteur rédhibitoire
        if secteur_job in secteurs_redhibitoires:
            return 0.0
        
        # Matching direct avec secteurs préférés
        if secteur_job in secteurs_candidat:
            # Position dans les préférences (bonus si en tête)
            try:
                position = secteurs_candidat.index(secteur_job) + 1
                score_preference = max(0.7, 1.0 - (position - 1) * 0.1)
            except ValueError:
                score_preference = 0.8
        else:
            # Pas dans les préférences mais pas rédhibitoire
            score_preference = 0.4
        
        # Bonus pour expérience dans le secteur
        experiences_secteur = [
            exp for exp in candidat.cv_data.experiences 
            if exp.secteur and normaliser_secteur(exp.secteur) == secteur_job
        ]
        
        if experiences_secteur:
            duree_totale_mois = sum(exp.duree_mois for exp in experiences_secteur)
            bonus_experience = min(0.3, duree_totale_mois / 36 * 0.3)  # 3 ans = bonus max
        else:
            bonus_experience = 0.0
        
        score_final = min(1.0, score_preference + bonus_experience)
        return round(score_final, 3)
    
    async def _calculate_contractual_compatibility(self, candidat: CandidatCompletNexfen, job: JobDataAdvanced) -> float:
        """📜 Compatibilité contractuelle"""
        
        # Analyse basée sur les préférences de contrat du questionnaire
        contrats_candidat = candidat.questionnaire_data.contrats.ordre_preference
        type_contrat_job = job.type_contrat
        
        # Position du type de contrat dans les préférences
        try:
            position = contrats_candidat.index(type_contrat_job) + 1
            score_base = max(0.3, 1.0 - (position - 1) * 0.15)
        except ValueError:
            # Type de contrat pas dans les préférences
            score_base = 0.2
        
        # Bonus pour conditions spécifiques
        bonus_conditions = 0.0
        
        # Vérification durée (pour CDD/missions)
        if type_contrat_job.value in ["CDD", "Intérim"] and candidat.questionnaire_data.contrats.duree_min_cdd:
            # Durée minimale acceptable (simulation - dans un vrai cas, on l'aurait dans job)
            duree_estimee_mois = 12  # Simulation
            if duree_estimee_mois >= candidat.questionnaire_data.contrats.duree_min_cdd:
                bonus_conditions += 0.1
        
        # Bonus pour ouverture freelance si applicable
        if type_contrat_job.value == "Freelance" and candidat.questionnaire_data.contrats.freelance_acceptable:
            bonus_conditions += 0.2
        
        score_final = min(1.0, score_base + bonus_conditions)
        return round(score_final, 3)
    
    async def _calculate_motivational_compatibility(self, candidat: CandidatCompletNexfen, job: JobDataAdvanced) -> float:
        """🎯 Compatibilité motivationnelle"""
        
        # Construction des caractéristiques de l'offre pour l'évaluation motivationnelle
        caracteristiques_offre = {
            "salaire_propose": (job.salaire_min + job.salaire_max) / 2 if job.salaire_min and job.salaire_max else None,
            "salaire_min_candidat": candidat.questionnaire_data.remuneration.get("min", 0),
            "perspectives_evolution": job.environnement_entreprise.evolution_interne_possible,
            "teletravail_jours": self._extract_telework_days(job.localisation.flexibilite_travail),
            "budget_formation": job.avantages_sociaux.budget_formation_annuel,
            "culture_entreprise": " ".join(job.environnement_entreprise.valeurs_entreprise)
        }
        
        # Simulation du profil motivationnel à partir du questionnaire
        profil_motivationnel = self._build_motivational_profile_from_questionnaire(candidat.questionnaire_data)
        
        # Évaluation de l'adéquation
        evaluation = profil_motivationnel.evaluer_adequation_offre_complete(caracteristiques_offre)
        
        return evaluation["score_adequation_global"]
    
    async def _calculate_salary_compatibility(self, candidat: CandidatCompletNexfen, job: JobDataAdvanced) -> float:
        """💰 Compatibilité salariale"""
        
        attentes_candidat = candidat.questionnaire_data.remuneration
        salaire_min_candidat = attentes_candidat.get("min", 0)
        salaire_max_candidat = attentes_candidat.get("max", 999999)
        
        if not job.salaire_min or not job.salaire_max:
            return 0.5  # Score neutre si pas d'info salariale
        
        salaire_moyen_offre = (job.salaire_min + job.salaire_max) / 2
        
        # Calcul de compatibilité
        if salaire_moyen_offre >= salaire_max_candidat:
            return 1.0  # Salaire au-dessus des attentes max
        elif salaire_moyen_offre >= salaire_min_candidat:
            # Proportionnel entre min et max candidat
            ratio = (salaire_moyen_offre - salaire_min_candidat) / (salaire_max_candidat - salaire_min_candidat)
            return round(0.6 + ratio * 0.4, 3)  # Score entre 0.6 et 1.0
        else:
            # Sous les attentes minimales
            ratio_deficit = salaire_moyen_offre / salaire_min_candidat
            return round(max(0.0, ratio_deficit * 0.5), 3)  # Score proportionnel au déficit
    
    async def _calculate_location_compatibility(self, candidat: CandidatCompletNexfen, job: JobDataAdvanced) -> float:
        """📍 Compatibilité géographique"""
        
        # Transport du candidat
        moyens_transport = candidat.questionnaire_data.transport.moyens_selectionnes
        temps_max = candidat.questionnaire_data.transport.temps_max
        
        # Localisation du job
        ville_job = job.localisation.ville_principale
        
        # Score basé sur le télétravail
        jours_teletravail = self._extract_telework_days(job.localisation.flexibilite_travail)
        
        if jours_teletravail >= 4:  # Majoritairement remote
            return 0.9
        elif jours_teletravail >= 2:  # Hybride
            score_base = 0.7
        else:  # Présentiel
            score_base = 0.4
        
        # Bonus pour transport compatible
        bonus_transport = 0.0
        
        if job.localisation.acces_transport_public and "Transport en commun" in [m.value for m in moyens_transport]:
            bonus_transport += 0.15
        
        if job.localisation.parking_disponible and "Voiture" in [m.value for m in moyens_transport]:
            bonus_transport += 0.1
            if job.localisation.parking_gratuit:
                bonus_transport += 0.05
        
        score_final = min(1.0, score_base + bonus_transport)
        return round(score_final, 3)
    
    async def _calculate_environment_compatibility(self, candidat: CandidatCompletNexfen, job: JobDataAdvanced) -> float:
        """🏢 Compatibilité environnementale"""
        
        env_prefere_candidat = candidat.questionnaire_data.environnement_travail
        env_job = job.environnement_travail
        
        # Matching direct environnement
        if env_prefere_candidat == env_job:
            score_base = 1.0
        elif (env_prefere_candidat.value in ["Hybride (bureau + télétravail)", "Télétravail à domicile"] and 
              job.localisation.flexibilite_travail.value in ["Hybride", "Full remote"]):
            score_base = 0.9  # Flexibilité compatible
        else:
            score_base = 0.4  # Environnement différent mais adaptable
        
        # Bonus pour culture d'entreprise
        bonus_culture = 0.0
        if job.environnement_entreprise.culture_collaborative:
            bonus_culture += 0.05
        if job.environnement_entreprise.innovation_encouragee:
            bonus_culture += 0.05
        if len(job.environnement_entreprise.valeurs_entreprise) >= 3:
            bonus_culture += 0.05
        
        score_final = min(1.0, score_base + bonus_culture)
        return round(score_final, 3)
    
    def _calculate_weighted_global_score(self, scores: Dict[str, float], weights: CompatibilityWeights) -> float:
        """⚖️ Calcule le score global pondéré"""
        
        global_score = (
            scores["semantique"] * weights.semantique +
            scores["sectoriel"] * weights.sectoriel +
            scores["contractuel"] * weights.contractuel +
            scores["motivationnel"] * weights.motivationnel +
            scores["remuneration"] * weights.remuneration +
            scores["localisation"] * weights.localisation +
            scores["environnement"] * weights.environnement
        )
        
        return round(global_score, 3)
    
    def _calculate_confidence_score(self, scores: Dict[str, float]) -> float:
        """🎯 Calcule un score de confiance basé sur la cohérence des scores"""
        
        # Variance des scores (moins de variance = plus de confiance)
        scores_values = list(scores.values())
        mean_score = sum(scores_values) / len(scores_values)
        variance = sum((score - mean_score) ** 2 for score in scores_values) / len(scores_values)
        
        # Score de confiance inversement proportionnel à la variance
        confidence = max(0.5, 1.0 - variance * 2)
        
        # Bonus si la plupart des scores sont élevés
        high_scores = len([s for s in scores_values if s >= 0.7])
        if high_scores >= len(scores_values) * 0.6:
            confidence += 0.1
        
        return round(min(1.0, confidence), 3)
    
    def _analyze_strengths_weaknesses(self, scores: Dict[str, float], weights: CompatibilityWeights) -> Tuple[List[str], List[str]]:
        """💪 Analyse les forces et faiblesses"""
        
        strengths = []
        weaknesses = []
        
        # Analyse par composant
        for component, score in scores.items():
            weight = getattr(weights, component)
            weighted_impact = score * weight
            
            if score >= 0.8:
                strengths.append(f"Excellent {component.replace('_', ' ')} ({score:.2f})")
            elif score >= 0.6:
                strengths.append(f"Bon {component.replace('_', ' ')} ({score:.2f})")
            elif score <= 0.4:
                weaknesses.append(f"Faible {component.replace('_', ' ')} ({score:.2f})")
            elif weighted_impact <= 0.05:  # Impact pondéré faible
                weaknesses.append(f"{component.replace('_', ' ').title()} à améliorer ({score:.2f})")
        
        return strengths, weaknesses
    
    def _generate_improvement_recommendations(
        self, 
        candidat: CandidatCompletNexfen, 
        job: JobDataAdvanced, 
        scores: Dict[str, float], 
        weaknesses: List[str]
    ) -> List[str]:
        """💡 Génère des recommandations d'amélioration"""
        
        recommendations = []
        
        # Recommandations basées sur les faiblesses
        if scores["semantique"] <= 0.5:
            recommendations.append("Développer les compétences techniques clés du poste")
        
        if scores["sectoriel"] <= 0.5:
            recommendations.append("Acquérir de l'expérience dans le secteur d'activité")
        
        if scores["motivationnel"] <= 0.5:
            recommendations.append("Revoir l'alignement des motivations avec l'offre")
        
        if scores["remuneration"] <= 0.5:
            recommendations.append("Négocier le package de rémunération global")
        
        if scores["localisation"] <= 0.5:
            recommendations.append("Explorer les options de télétravail ou transport")
        
        # Recommandations pour maximiser les forces
        best_score = max(scores.values())
        best_component = max(scores, key=scores.get)
        
        if best_score >= 0.8:
            recommendations.append(f"Capitaliser sur l'excellent {best_component.replace('_', ' ')}")
        
        return recommendations
    
    def _predict_job_success(self, candidat: CandidatCompletNexfen, job: JobDataAdvanced, scores: Dict[str, float]) -> Dict[str, Any]:
        """🔮 Prédit la réussite potentielle dans le poste"""
        
        # Score de réussite basé sur les composants clés
        success_factors = {
            "competences_techniques": scores["semantique"] * 0.3,
            "motivation_adequation": scores["motivationnel"] * 0.25,
            "experience_sectorielle": scores["sectoriel"] * 0.2,
            "environnement_adapte": scores["environnement"] * 0.15,
            "satisfaction_conditions": (scores["remuneration"] + scores["contractuel"]) / 2 * 0.1
        }
        
        success_score = sum(success_factors.values())
        
        # Niveau de confiance
        if success_score >= 0.8:
            prediction_level = "Très élevée"
            risk_factors = []
        elif success_score >= 0.6:
            prediction_level = "Élevée"
            risk_factors = ["Quelques ajustements nécessaires"]
        elif success_score >= 0.4:
            prediction_level = "Modérée"
            risk_factors = ["Risques d'inadéquation à surveiller"]
        else:
            prediction_level = "Faible"
            risk_factors = ["Inadéquation importante sur plusieurs aspects"]
        
        return {
            "success_probability": round(success_score, 3),
            "prediction_level": prediction_level,
            "key_success_factors": success_factors,
            "risk_factors": risk_factors,
            "recommendation": self._get_global_recommendation(success_score)
        }
    
    def _get_global_recommendation(self, success_score: float) -> str:
        """📋 Recommandation globale basée sur le score de réussite"""
        
        if success_score >= 0.8:
            return "Candidat fortement recommandé - Excellent match"
        elif success_score >= 0.6:
            return "Candidat recommandé - Bon potentiel avec ajustements mineurs"
        elif success_score >= 0.4:
            return "Candidat à considérer - Nécessite des ajustements importants"
        else:
            return "Candidat non recommandé - Inadéquation trop importante"
    
    # Méthodes utilitaires
    
    def _extract_telework_days(self, flexibility_type) -> int:
        """🏠 Extrait le nombre de jours de télétravail"""
        flexibility_str = str(flexibility_type)
        
        if "100% remote" in flexibility_str or "Full remote" in flexibility_str:
            return 5
        elif "3j télétravail" in flexibility_str:
            return 3
        elif "2j télétravail" in flexibility_str:
            return 2
        elif "1j télétravail" in flexibility_str:
            return 1
        else:
            return 0
    
    def _build_motivational_profile_from_questionnaire(self, questionnaire: QuestionnaireCompletAdvanced) -> ProfilMotivationnel:
        """🎯 Construit un profil motivationnel à partir du questionnaire"""
        
        # Import ici pour éviter les imports circulaires
        from ..models.motivation_ranking import MotivationDetaillee, ProfilMotivationnel, IntensiteMotivationEnum
        
        motivations_detaillees = []
        
        for i, motivation_classee in enumerate(questionnaire.motivations.motivations_classees):
            motivation_detail = MotivationDetaillee(
                motivation=motivation_classee.motivation,
                intensite=IntensiteMotivationEnum.IMPORTANTE,  # Par défaut
                priorite=motivation_classee.priorite,
                poids=motivation_classee.poids,
                description_personnalisee=motivation_classee.description_personnalisee,
                negociable=True  # Par défaut
            )
            motivations_detaillees.append(motivation_detail)
        
        profil = ProfilMotivationnel(
            motivations_classees=motivations_detaillees
        )
        
        # Analyse de cohérence avec la raison d'écoute
        profil.analyser_coherence_raison_ecoute(questionnaire.timing.pourquoi_a_lecoute)
        
        return profil
    
    def _update_performance_metrics(self, calculation_time: float):
        """📊 Met à jour les métriques de performance"""
        count = self.performance_metrics["calculations_count"]
        current_avg = self.performance_metrics["average_calculation_time"]
        
        # Calcul de la nouvelle moyenne
        new_avg = ((current_avg * (count - 1)) + calculation_time) / count
        self.performance_metrics["average_calculation_time"] = round(new_avg, 2)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """📈 Retourne les statistiques de performance"""
        return {
            "calculations_performed": self.performance_metrics["calculations_count"],
            "cache_hits": self.performance_metrics["cache_hits"],
            "cache_hit_rate": round(
                self.performance_metrics["cache_hits"] / max(1, self.performance_metrics["calculations_count"]) * 100, 2
            ),
            "average_calculation_time_ms": self.performance_metrics["average_calculation_time"],
            "cache_size": len(self.cache_compatibility)
        }
    
    def clear_cache(self):
        """🗑️ Vide le cache de compatibilité"""
        self.cache_compatibility.clear()
        logger.info("💾 Cache de compatibilité vidé")

# Instance globale du moteur
compatibility_engine = AdvancedCompatibilityEngine()

# Fonction utilitaire pour l'utilisation directe
async def calculate_compatibility(
    candidat: CandidatCompletNexfen,
    job: JobDataAdvanced,
    use_adaptive_weighting: bool = True
) -> Dict[str, Any]:
    """🎯 Fonction utilitaire pour calculer la compatibilité"""
    return await compatibility_engine.calculate_advanced_compatibility(
        candidat, job, use_adaptive_weighting
    )
