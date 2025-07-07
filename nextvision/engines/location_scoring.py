"""
📍 Nextvision - Engine Location Scoring Avancé (Prompt 2)
Enrichissement du composant localisation (6/7) avec intelligence géospatiale

Author: NEXTEN Team
Version: 2.0.0 - Google Maps Intelligence
Integration: Pondération adaptative existante + Transport Intelligence
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from ..services.transport_calculator import TransportCalculator
from ..models.transport_models import (
    LocationScore, TransportCompatibility, ConfigTransport,
    TravelMode, GeocodeResult
)
from ..models.questionnaire_advanced import QuestionnaireComplet, RaisonEcoute

logger = logging.getLogger(__name__)

class LocationScoringEngine:
    """📍 Engine de scoring géospatial enrichi (composant 6/7)"""
    
    def __init__(self, transport_calculator: TransportCalculator):
        self.transport_calculator = transport_calculator
        
        # Pondération adaptative (intégration avec système existant)
        self.adaptive_weights = {
            # Score localisation boosté selon raison d'écoute
            RaisonEcoute.POSTE_TROP_LOIN: 2.0,       # Double poids si distance problème
            RaisonEcoute.MANQUE_FLEXIBILITE: 1.5,    # Bonus si flexibilité importante
            RaisonEcoute.REMUNERATION_FAIBLE: 1.0,   # Poids normal
            RaisonEcoute.POSTE_INADEQUAT: 0.8,       # Moins important si problème matching
            RaisonEcoute.MANQUE_PERSPECTIVES: 0.8    # Moins important si problème évolution
        }
        
        # Configuration scoring avancé
        self.scoring_weights = {
            "time": 0.4,      # Temps trajet (priorité max)
            "cost": 0.2,      # Coût transport
            "comfort": 0.2,   # Confort mode transport
            "reliability": 0.2 # Fiabilité (trafic, météo)
        }
        
        # Métriques performance
        self.scoring_count = 0
        self.average_scoring_time = 0.0
    
    async def calculate_enriched_location_score(
        self,
        candidat_questionnaire: QuestionnaireComplet,
        job_address: str,
        job_context: Optional[Dict] = None
    ) -> LocationScore:
        """📍 Calcule score localisation enrichi avec transport intelligence"""
        
        start_time = datetime.now()
        self.scoring_count += 1
        
        try:
            # 1. Configuration transport depuis questionnaire
            transport_config = self._create_transport_config(candidat_questionnaire)
            
            # 2. Calcul compatibilité transport
            compatibility = await self.transport_calculator.calculate_transport_compatibility(
                transport_config, job_address
            )
            
            # 3. Score localisation de base
            location_score = await self.transport_calculator.calculate_location_score(
                compatibility
            )
            
            # 4. Enrichissements avancés
            await self._enrich_location_score(
                location_score, candidat_questionnaire, job_context
            )
            
            # 5. Pondération adaptative selon raison d'écoute
            final_score = self._apply_adaptive_weighting(
                location_score, candidat_questionnaire.timing.pourquoi_a_lecoute
            )
            
            # 6. Explications détaillées
            self._add_detailed_explanations(location_score, candidat_questionnaire)
            
            # 7. Métriques performance
            calculation_time = (datetime.now() - start_time).total_seconds()
            self.average_scoring_time = (
                (self.average_scoring_time * (self.scoring_count - 1) + calculation_time) 
                / self.scoring_count
            )
            
            logger.debug(
                f"Score localisation: {final_score:.2f} "
                f"(temps: {calculation_time:.2f}s)"
            )
            
            return location_score
            
        except Exception as e:
            logger.error(f"Erreur scoring localisation {job_address}: {e}")
            
            # Score fallback neutre
            return self._create_fallback_location_score(job_address)
    
    async def batch_calculate_location_scores(
        self,
        candidat_questionnaire: QuestionnaireComplet,
        job_addresses: List[str],
        job_contexts: Optional[List[Dict]] = None
    ) -> Dict[str, LocationScore]:
        """🚀 Calcul batch scores localisation pour performance"""
        
        logger.info(f"Batch scoring localisation: {len(job_addresses)} jobs")
        
        # Préparation contextes
        if job_contexts is None:
            job_contexts = [{}] * len(job_addresses)
        
        # Configuration transport une seule fois
        transport_config = self._create_transport_config(candidat_questionnaire)
        
        # Calcul batch compatibilités
        compatibilities = await self.transport_calculator.batch_calculate_job_compatibility(
            transport_config, job_addresses
        )
        
        # Calcul scores en parallèle
        scores = {}
        
        for job_addr, job_context in zip(job_addresses, job_contexts):
            if job_addr in compatibilities:
                compatibility = compatibilities[job_addr]
                
                # Score localisation
                location_score = await self.transport_calculator.calculate_location_score(
                    compatibility
                )
                
                # Enrichissements
                await self._enrich_location_score(
                    location_score, candidat_questionnaire, job_context
                )
                
                # Pondération adaptative
                final_score = self._apply_adaptive_weighting(
                    location_score, candidat_questionnaire.timing.pourquoi_a_lecoute
                )
                
                # Explications
                self._add_detailed_explanations(location_score, candidat_questionnaire)
                
                scores[job_addr] = location_score
            else:
                # Fallback
                scores[job_addr] = self._create_fallback_location_score(job_addr)
        
        logger.info(f"Batch scoring terminé: {len(scores)} scores calculés")
        return scores
    
    async def _enrich_location_score(
        self,
        location_score: LocationScore,
        candidat_questionnaire: QuestionnaireComplet,
        job_context: Optional[Dict] = None
    ):
        """🔧 Enrichit le score avec facteurs avancés"""
        
        compatibility = location_score.transport_compatibility
        
        # Enrichissement 1: Coût transport estimé
        await self._calculate_transport_cost_score(location_score)
        
        # Enrichissement 2: Score confort selon mode transport
        self._calculate_comfort_score(location_score, candidat_questionnaire)
        
        # Enrichissement 3: Fiabilité selon trafic et météo
        self._calculate_reliability_score(location_score)
        
        # Enrichissement 4: Bonus télétravail
        self._apply_telework_bonus(location_score, candidat_questionnaire)
        
        # Enrichissement 5: Facteurs contextuels job
        if job_context:
            self._apply_job_context_adjustments(location_score, job_context)
        
        # Recalcul score final avec enrichissements
        location_score.calculate_score()
    
    async def _calculate_transport_cost_score(self, location_score: LocationScore):
        """💰 Calcule score coût transport"""
        
        compatibility = location_score.transport_compatibility
        
        if not compatibility.recommended_mode or compatibility.recommended_mode not in compatibility.routes:
            location_score.cost_score = 0.5  # Neutre si pas de données
            return
        
        recommended_route = compatibility.routes[compatibility.recommended_mode]
        distance_km = recommended_route.distance_km
        
        # Estimation coûts par mode (€/mois pour 22 jours)
        monthly_costs = {
            TravelMode.DRIVING: distance_km * 2 * 22 * 0.35,  # 0.35€/km (essence + usure)
            TravelMode.TRANSIT: 75,  # Forfait Navigo moyen
            TravelMode.BICYCLING: 10,  # Entretien vélo
            TravelMode.WALKING: 0    # Gratuit
        }
        
        estimated_cost = monthly_costs.get(compatibility.recommended_mode, 50)
        
        # Score inversé: moins cher = meilleur score
        # 0€ = 1.0, 150€ = 0.5, 300€+ = 0.0
        location_score.cost_score = max(0.0, min(1.0, (150 - estimated_cost) / 150))
        
        location_score.explanations.append(
            f"💰 Coût estimé: {estimated_cost:.0f}€/mois → score {location_score.cost_score:.2f}"
        )
    
    def _calculate_comfort_score(
        self, 
        location_score: LocationScore, 
        candidat_questionnaire: QuestionnaireComplet
    ):
        """😌 Calcule score confort selon mode et préférences"""
        
        compatibility = location_score.transport_compatibility
        
        if not compatibility.recommended_mode:
            location_score.comfort_score = 0.5
            return
        
        # Scores confort de base par mode
        base_comfort = {
            TravelMode.DRIVING: 0.9,     # Confortable mais stress trafic
            TravelMode.TRANSIT: 0.7,     # Moyen (foule, correspondances)
            TravelMode.BICYCLING: 0.6,   # Effort physique mais agréable
            TravelMode.WALKING: 0.4      # Effort si distance > 30min
        }
        
        base_score = base_comfort.get(compatibility.recommended_mode, 0.5)
        
        # Ajustements selon route
        if compatibility.recommended_mode in compatibility.routes:
            route = compatibility.routes[compatibility.recommended_mode]
            
            # Pénalité si trajet très long
            if route.duration_minutes > 60:
                base_score *= 0.8
            elif route.duration_minutes > 45:
                base_score *= 0.9
            
            # Pénalité correspondances multiples (transport public)
            if compatibility.recommended_mode == TravelMode.TRANSIT:
                if len(route.steps) > 3:  # Plus de 3 étapes = correspondances
                    base_score *= 0.8
        
        location_score.comfort_score = base_score
        
        location_score.explanations.append(
            f"😌 Confort {compatibility.recommended_mode.value}: score {base_score:.2f}"
        )
    
    def _calculate_reliability_score(self, location_score: LocationScore):
        """🔄 Calcule score fiabilité (trafic, ponctualité)"""
        
        compatibility = location_score.transport_compatibility
        
        if not compatibility.recommended_mode or compatibility.recommended_mode not in compatibility.routes:
            location_score.reliability_score = 0.7
            return
        
        route = compatibility.routes[compatibility.recommended_mode]
        
        # Score de base par mode
        base_reliability = {
            TravelMode.WALKING: 0.95,    # Très fiable
            TravelMode.BICYCLING: 0.85,  # Fiable sauf météo
            TravelMode.TRANSIT: 0.75,    # Moyennement fiable (grèves, retards)
            TravelMode.DRIVING: 0.70     # Variable selon trafic
        }
        
        reliability_score = base_reliability.get(compatibility.recommended_mode, 0.7)
        
        # Ajustement selon trafic
        if route.traffic:
            if route.traffic.delay_minutes > 15:
                reliability_score *= 0.6  # Trafic très dense
            elif route.traffic.delay_minutes > 10:
                reliability_score *= 0.8  # Trafic dense
            elif route.traffic.delay_minutes < 5:
                reliability_score *= 1.1  # Trafic fluide
        
        location_score.reliability_score = min(1.0, reliability_score)
        
        delay_info = ""
        if route.traffic and route.traffic.delay_minutes > 5:
            delay_info = f" (+{route.traffic.delay_minutes}min trafic)"
        
        location_score.explanations.append(
            f"🔄 Fiabilité {compatibility.recommended_mode.value}{delay_info}: "
            f"score {location_score.reliability_score:.2f}"
        )
    
    def _apply_telework_bonus(
        self, 
        location_score: LocationScore, 
        candidat_questionnaire: QuestionnaireComplet
    ):
        """🏠 Applique bonus télétravail"""
        
        # TODO: Extraire info télétravail du questionnaire
        # Pour l'instant, valeur par défaut
        telework_days = 2  # jours par semaine
        
        if telework_days > 0:
            # Bonus selon nombre de jours télétravail
            telework_factor = 1 + (telework_days / 5) * 0.2  # Max 20% bonus
            
            # Application du bonus à tous les scores
            location_score.time_score *= telework_factor
            location_score.cost_score *= telework_factor
            location_score.comfort_score *= telework_factor
            
            # Limitation à 1.0
            location_score.time_score = min(1.0, location_score.time_score)
            location_score.cost_score = min(1.0, location_score.cost_score)
            location_score.comfort_score = min(1.0, location_score.comfort_score)
            
            location_score.explanations.append(
                f"🏠 Bonus télétravail {telework_days}j/semaine: +{(telework_factor-1)*100:.0f}%"
            )
    
    def _apply_job_context_adjustments(
        self, 
        location_score: LocationScore, 
        job_context: Dict
    ):
        """🏢 Ajustements selon contexte job"""
        
        # Ajustement 1: Flexibilité horaires
        if job_context.get("horaires_flexibles", False):
            location_score.reliability_score *= 1.2  # Moins d'impact trafic
            location_score.explanations.append("⏰ Bonus horaires flexibles")
        
        # Ajustement 2: Parking fourni
        if job_context.get("parking_fourni", False):
            if location_score.transport_compatibility.recommended_mode == TravelMode.DRIVING:
                location_score.comfort_score *= 1.1
                location_score.cost_score *= 1.1  # Économie parking
                location_score.explanations.append("🅿️ Bonus parking fourni")
        
        # Ajustement 3: Remboursement transport
        transport_reimbursement = job_context.get("remboursement_transport", 0)
        if transport_reimbursement > 0:
            # Amélioration score coût
            bonus = min(0.3, transport_reimbursement / 100)  # Max 30% bonus
            location_score.cost_score = min(1.0, location_score.cost_score + bonus)
            location_score.explanations.append(
                f"💳 Remboursement transport {transport_reimbursement}%"
            )
    
    def _apply_adaptive_weighting(
        self, 
        location_score: LocationScore, 
        raison_ecoute: RaisonEcoute
    ) -> float:
        """🎯 Applique pondération adaptative selon raison d'écoute"""
        
        # Poids adaptatif selon raison d'écoute
        adaptive_weight = self.adaptive_weights.get(raison_ecoute, 1.0)
        
        # Application de la pondération
        boosted_score = location_score.final_score * adaptive_weight
        
        # Normalisation (score max = 1.0)
        location_score.final_score = min(1.0, boosted_score)
        
        if adaptive_weight != 1.0:
            location_score.explanations.append(
                f"🎯 Pondération adaptative '{raison_ecoute.value}': "
                f"×{adaptive_weight} → score final {location_score.final_score:.2f}"
            )
        
        return location_score.final_score
    
    def _add_detailed_explanations(
        self, 
        location_score: LocationScore, 
        candidat_questionnaire: QuestionnaireComplet
    ):
        """📝 Ajoute explications détaillées"""
        
        compatibility = location_score.transport_compatibility
        
        # Résumé transport
        if compatibility.best_route_info:
            location_score.explanations.insert(0, f"🗺️ Trajet: {compatibility.best_route_info}")
        
        # Modes alternatifs
        if len(compatibility.compatible_modes) > 1:
            alternative_modes = [
                mode.value for mode in compatibility.compatible_modes 
                if mode != compatibility.recommended_mode
            ]
            if alternative_modes:
                location_score.explanations.append(
                    f"🔄 Alternatives: {', '.join(alternative_modes)}"
                )
        
        # Raison d'écoute contexte
        raison = candidat_questionnaire.timing.pourquoi_a_lecoute
        if raison == RaisonEcoute.POSTE_TROP_LOIN:
            location_score.explanations.append(
                "📍 Priorité localisation selon votre recherche"
            )
    
    def _create_transport_config(self, candidat_questionnaire: QuestionnaireComplet) -> ConfigTransport:
        """⚙️ Crée configuration transport depuis questionnaire"""
        
        # TODO: Extraire adresse du questionnaire
        adresse_domicile = "13 rue du champ de mars 75007 Paris"
        
        config = ConfigTransport(
            adresse_domicile=adresse_domicile,
            transport_preferences=candidat_questionnaire.transport,
            telework_days_per_week=2,  # TODO: depuis questionnaire
            telework_flexibility=True
        )
        
        return config
    
    def _create_fallback_location_score(self, job_address: str) -> LocationScore:
        """🚨 Score localisation fallback"""
        
        from ..models.transport_models import GeocodeResult
        from ..models.questionnaire_advanced import TransportPreferences, MoyenTransport
        
        # Locations fallback
        fallback_location = GeocodeResult(
            address=job_address,
            formatted_address=job_address,
            latitude=48.8566,
            longitude=2.3522,
            quality="failed",
            place_id="fallback",
            components={}
        )
        
        # Compatibilité fallback
        fallback_preferences = TransportPreferences(
            moyens_selectionnes=[MoyenTransport.VOITURE],
            temps_max={"voiture": 45}
        )
        
        compatibility = TransportCompatibility(
            candidat_preferences=fallback_preferences,
            job_location=fallback_location,
            candidat_location=fallback_location,
            routes={}
        )
        
        # Score neutre
        location_score = LocationScore(
            base_distance_km=10.0,  # Distance moyenne Paris
            transport_compatibility=compatibility,
            time_score=0.6,
            cost_score=0.6,
            comfort_score=0.6,
            reliability_score=0.6,
            final_score=0.6,
            explanations=["⚠️ Score localisation en mode dégradé"]
        )
        
        return location_score
    
    def get_performance_stats(self) -> Dict:
        """📊 Statistiques performance scoring"""
        
        return {
            "total_scoring_operations": self.scoring_count,
            "average_scoring_time_seconds": self.average_scoring_time,
            "adaptive_weights_config": {
                raison.value: weight 
                for raison, weight in self.adaptive_weights.items()
            },
            "scoring_weights_config": self.scoring_weights
        }

class LocationScoreExplainer:
    """📖 Expliqueur détaillé des scores localisation"""
    
    @staticmethod
    def explain_score_components(location_score: LocationScore) -> Dict:
        """📋 Explication détaillée des composants du score"""
        
        return {
            "score_final": location_score.final_score,
            "components": {
                "temps_trajet": {
                    "score": location_score.time_score,
                    "poids": 0.4,
                    "contribution": location_score.time_score * 0.4
                },
                "cout_transport": {
                    "score": location_score.cost_score,
                    "poids": 0.2,
                    "contribution": location_score.cost_score * 0.2
                },
                "confort": {
                    "score": location_score.comfort_score,
                    "poids": 0.2,
                    "contribution": location_score.comfort_score * 0.2
                },
                "fiabilite": {
                    "score": location_score.reliability_score,
                    "poids": 0.2,
                    "contribution": location_score.reliability_score * 0.2
                }
            },
            "explications": location_score.explanations,
            "transport_info": {
                "mode_recommande": location_score.transport_compatibility.recommended_mode.value if location_score.transport_compatibility.recommended_mode else None,
                "meilleur_trajet": location_score.transport_compatibility.best_route_info,
                "modes_compatibles": [mode.value for mode in location_score.transport_compatibility.compatible_modes]
            }
        }
