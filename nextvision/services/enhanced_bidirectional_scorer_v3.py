"""
🚀 Nextvision V3.0 - BidirectionalScorer Enhanced (PROMPT 7)
Intégration des nouveaux scorers timing & contrats & environnement

Ajout des scorers :
- AvailabilityTimingScorer
- ContractTypesScorer  
- WorkEnvironmentScorer

Author: NEXTEN Team
Version: 3.0.0 - Enhanced with new scorers
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

# Import des scorers existants V3.0
from nextvision.services.scorers_v3 import (
    LocationTransportScorerV3,
    AvailabilityTimingScorer,
    ContractTypesScorer,
    WorkEnvironmentScorer
)

# Import des modèles V3.0
from nextvision.models.extended_bidirectional_models_v3 import (
    ExtendedCandidateProfileV3,
    ExtendedCompanyProfileV3,
    ExtendedMatchingRequestV3,
    ExtendedMatchingResponseV3,
    ExtendedComponentScoresV3,
    ExtendedComponentWeightsV3,
    PerformanceMonitoringV3
)

# Import des scorers V2.0 existants (héritage)
from nextvision.services.bidirectional_scorer import (
    SemanticScorer,
    SalaryScorer,
    ExperienceScorer,
    BaseScorer,
    ScoringResult
)

logger = logging.getLogger(__name__)

class EnhancedBidirectionalScorerV3:
    """
    🎯 Scorer Bidirectionnel V3.0 Enhanced
    
    Intègre tous les scorers V3.0 :
    - V2.0 : Semantic, Salary, Experience, Location (mise à jour)
    - V3.0 : Timing, Contract, Environment (nouveaux)
    
    Performance target : <175ms (vs 150ms V2.0)
    """
    
    def __init__(self, google_maps_service=None, transport_calculator=None):
        self.name = "EnhancedBidirectionalScorerV3"
        self.version = "3.0.0"
        
        # Scorers V2.0 (héritage)
        self.semantic_scorer = SemanticScorer(weight=0.24)
        self.salary_scorer = SalaryScorer(weight=0.19)
        self.experience_scorer = ExperienceScorer(weight=0.14)
        
        # Scorers V3.0 (nouveaux)
        self.location_transport_scorer = LocationTransportScorerV3(
            google_maps_service, transport_calculator
        )
        self.availability_timing_scorer = AvailabilityTimingScorer()
        self.contract_types_scorer = ContractTypesScorer()
        self.work_environment_scorer = WorkEnvironmentScorer()
        
        # Configuration performance
        self.performance_config = {
            "target_time_ms": 175,
            "parallel_execution": True,
            "timeout_ms": 5000,
            "fallback_enabled": True
        }
        
        # Métriques globales
        self.global_stats = {
            "total_calculations": 0,
            "successful_calculations": 0,
            "average_processing_time": 0.0,
            "component_performance": {},
            "target_achievements": 0
        }
    
    async def calculate_enhanced_bidirectional_score(
        self,
        request: ExtendedMatchingRequestV3
    ) -> ExtendedMatchingResponseV3:
        """
        🎯 Calcul score bidirectionnel V3.0 Enhanced
        
        Args:
            request: Requête matching V3.0 complète
            
        Returns:
            Réponse matching V3.0 avec tous les scores
        """
        
        start_time = datetime.now()
        self.global_stats["total_calculations"] += 1
        
        try:
            candidate = request.candidate
            company = request.company
            
            logger.info(f"🚀 Début calcul Enhanced V3.0 - {self.name}")
            
            # 1. Calcul scores en parallèle (performance optimisée)
            if request.use_google_maps_intelligence:
                component_scores = await self._calculate_scores_parallel(
                    candidate, company, request
                )
            else:
                component_scores = await self._calculate_scores_sequential(
                    candidate, company, request
                )
            
            # 2. Détermination poids adaptatifs
            applied_weights = self._determine_adaptive_weights(
                candidate, company, request
            )
            
            # 3. Calcul score final pondéré
            final_score = self._calculate_weighted_final_score(
                component_scores, applied_weights
            )
            
            # 4. Évaluation niveau compatibilité
            compatibility_level = self._evaluate_compatibility_level(final_score)
            
            # 5. Génération recommandations enrichies
            recommendations = self._generate_enhanced_recommendations(
                component_scores, applied_weights, candidate, company
            )
            
            # 6. Analyse exploitation questionnaire
            questionnaire_analysis = self._analyze_questionnaire_exploitation(
                candidate, company, component_scores
            )
            
            # 7. Monitoring performance
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            performance_monitoring = self._create_performance_monitoring(
                processing_time, component_scores, request
            )
            
            # 8. Construction réponse V3.0
            response = self._build_enhanced_response(
                final_score, compatibility_level, component_scores, applied_weights,
                recommendations, questionnaire_analysis, performance_monitoring, request
            )
            
            # 9. Mise à jour statistiques
            self._update_global_stats(processing_time, True)
            
            logger.info(
                f"✅ Enhanced V3.0 terminé: {final_score:.3f} "
                f"({compatibility_level}, {processing_time:.1f}ms)"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur Enhanced V3.0: {e}")
            
            # Fallback intelligent
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_global_stats(processing_time, False)
            
            return self._create_fallback_response(request, str(e), processing_time)
    
    async def _calculate_scores_parallel(
        self,
        candidate: ExtendedCandidateProfileV3,
        company: ExtendedCompanyProfileV3,
        request: ExtendedMatchingRequestV3
    ) -> ExtendedComponentScoresV3:
        """🚀 Calcul scores en parallèle (performance optimisée)"""
        
        logger.debug("🔄 Calcul scores parallèle V3.0")
        
        # Tâches parallèles avec timeout
        tasks = [
            self._safe_score_calculation(
                "semantic", 
                lambda: self.semantic_scorer.calculate_score(
                    candidate.base_profile, company.base_profile
                )
            ),
            self._safe_score_calculation(
                "salary",
                lambda: self.salary_scorer.calculate_score(
                    candidate.base_profile, company.base_profile
                )
            ),
            self._safe_score_calculation(
                "experience",
                lambda: self.experience_scorer.calculate_score(
                    candidate.base_profile, company.base_profile
                )
            ),
            self._safe_score_calculation(
                "location_transport",
                lambda: self.location_transport_scorer.calculate_location_transport_score_v3(
                    candidate.base_profile.attentes.localisation_preferee,
                    company.base_profile.poste.localisation,
                    candidate.transport_preferences.transport_methods or ["vehicle", "public-transport"],
                    {"vehicle": candidate.transport_preferences.max_travel_time, 
                     "public-transport": candidate.transport_preferences.max_travel_time}
                )
            ),
            self._safe_score_calculation(
                "availability_timing",
                lambda: self.availability_timing_scorer.calculate_availability_timing_score(
                    candidate, company
                )
            ),
            self._safe_score_calculation(
                "contract_types",
                lambda: self.contract_types_scorer.calculate_contract_types_score(
                    candidate, company
                )
            ),
            self._safe_score_calculation(
                "work_environment",
                lambda: self.work_environment_scorer.calculate_work_environment_score(
                    candidate, company
                )
            )
        ]
        
        # Exécution avec timeout global
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks),
                timeout=self.performance_config["timeout_ms"] / 1000
            )
        except asyncio.TimeoutError:
            logger.warning("⏰ Timeout calcul parallèle - fallback séquentiel")
            return await self._calculate_scores_sequential(candidate, company, request)
        
        # Assemblage scores
        return self._assemble_component_scores(results)
    
    async def _calculate_scores_sequential(
        self,
        candidate: ExtendedCandidateProfileV3,
        company: ExtendedCompanyProfileV3,
        request: ExtendedMatchingRequestV3
    ) -> ExtendedComponentScoresV3:
        """🔄 Calcul scores séquentiel (fallback)"""
        
        logger.debug("🔄 Calcul scores séquentiel V3.0")
        
        scores = {}
        
        # Calcul séquentiel avec gestion erreurs
        try:
            semantic_result = self.semantic_scorer.calculate_score(
                candidate.base_profile, company.base_profile
            )
            scores["semantic"] = semantic_result
        except Exception as e:
            logger.error(f"Erreur semantic: {e}")
            scores["semantic"] = self._create_fallback_score_result("semantic", 0.5)
        
        try:
            salary_result = self.salary_scorer.calculate_score(
                candidate.base_profile, company.base_profile
            )
            scores["salary"] = salary_result
        except Exception as e:
            logger.error(f"Erreur salary: {e}")
            scores["salary"] = self._create_fallback_score_result("salary", 0.6)
        
        try:
            experience_result = self.experience_scorer.calculate_score(
                candidate.base_profile, company.base_profile
            )
            scores["experience"] = experience_result
        except Exception as e:
            logger.error(f"Erreur experience: {e}")
            scores["experience"] = self._create_fallback_score_result("experience", 0.7)
        
        try:
            timing_result = self.availability_timing_scorer.calculate_availability_timing_score(
                candidate, company
            )
            scores["availability_timing"] = timing_result
        except Exception as e:
            logger.error(f"Erreur timing: {e}")
            scores["availability_timing"] = self._create_fallback_score_result("timing", 0.6)
        
        try:
            contract_result = self.contract_types_scorer.calculate_contract_types_score(
                candidate, company
            )
            scores["contract_types"] = contract_result
        except Exception as e:
            logger.error(f"Erreur contract: {e}")
            scores["contract_types"] = self._create_fallback_score_result("contract", 0.6)
        
        try:
            environment_result = self.work_environment_scorer.calculate_work_environment_score(
                candidate, company
            )
            scores["work_environment"] = environment_result
        except Exception as e:
            logger.error(f"Erreur environment: {e}")
            scores["work_environment"] = self._create_fallback_score_result("environment", 0.7)
        
        # Location/Transport (peut être complexe)
        try:
            location_result = await self.location_transport_scorer.calculate_location_transport_score_v3(
                candidate.base_profile.attentes.localisation_preferee,
                company.base_profile.poste.localisation,
                candidate.transport_preferences.transport_methods or ["vehicle"],
                {"vehicle": candidate.transport_preferences.max_travel_time}
            )
            scores["location_transport"] = location_result
        except Exception as e:
            logger.error(f"Erreur location: {e}")
            scores["location_transport"] = self._create_fallback_score_result("location", 0.6)
        
        return self._assemble_component_scores([
            ("semantic", scores["semantic"]),
            ("salary", scores["salary"]),
            ("experience", scores["experience"]),
            ("location_transport", scores["location_transport"]),
            ("availability_timing", scores["availability_timing"]),
            ("contract_types", scores["contract_types"]),
            ("work_environment", scores["work_environment"])
        ])
    
    async def _safe_score_calculation(self, component_name: str, calculation_func) -> tuple:
        """🛡️ Calcul sécurisé avec gestion erreurs"""
        
        try:
            if asyncio.iscoroutinefunction(calculation_func):
                result = await calculation_func()
            else:
                result = calculation_func()
            return (component_name, result)
        except Exception as e:
            logger.error(f"Erreur calcul {component_name}: {e}")
            fallback_score = self._create_fallback_score_result(component_name, 0.5)
            return (component_name, fallback_score)
    
    def _assemble_component_scores(self, results: List[tuple]) -> ExtendedComponentScoresV3:
        """🔧 Assemblage scores composants"""
        
        scores_dict = {}
        details_dict = {}
        
        for component_name, result in results:
            if isinstance(result, ScoringResult):
                # Format V2.0 (ScoringResult)
                scores_dict[component_name] = result.score
                details_dict[component_name] = result.details
            elif isinstance(result, dict):
                # Format V3.0 (dict)
                scores_dict[component_name] = result.get("final_score", 0.5)
                details_dict[component_name] = result
            else:
                # Fallback
                scores_dict[component_name] = 0.5
                details_dict[component_name] = {"error": "Format non reconnu"}
        
        return ExtendedComponentScoresV3(
            semantic_score=scores_dict.get("semantic", 0.5),
            semantic_details=details_dict.get("semantic", {}),
            
            salary_score=scores_dict.get("salary", 0.5),
            salary_details=details_dict.get("salary", {}),
            
            experience_score=scores_dict.get("experience", 0.5),
            experience_details=details_dict.get("experience", {}),
            
            location_score=scores_dict.get("location_transport", 0.5),
            location_details=details_dict.get("location_transport", {}),
            
            # Nouveaux V3.0
            motivations_score=0.7,  # TODO: Implémenter MotivationsScorer
            motivations_details={},
            
            sector_compatibility_score=0.7,  # TODO: Implémenter SectorScorer
            sector_compatibility_details={},
            
            contract_flexibility_score=scores_dict.get("contract_types", 0.5),
            contract_flexibility_details=details_dict.get("contract_types", {}),
            
            timing_compatibility_score=scores_dict.get("availability_timing", 0.5),
            timing_compatibility_details=details_dict.get("availability_timing", {}),
            
            work_modality_score=scores_dict.get("work_environment", 0.5),
            work_modality_details=details_dict.get("work_environment", {}),
            
            salary_progression_score=0.7,  # TODO: Implémenter SalaryProgressionScorer
            salary_progression_details={},
            
            listening_reason_score=0.7,  # TODO: Implémenter ListeningReasonScorer
            listening_reason_details={},
            
            candidate_status_score=0.7,  # TODO: Implémenter CandidateStatusScorer
            candidate_status_details={}
        )
    
    def _determine_adaptive_weights(
        self,
        candidate: ExtendedCandidateProfileV3,
        company: ExtendedCompanyProfileV3,
        request: ExtendedMatchingRequestV3
    ) -> ExtendedComponentWeightsV3:
        """⚖️ Détermination poids adaptatifs"""
        
        if not request.use_adaptive_weighting:
            return ExtendedComponentWeightsV3()  # Poids de base
        
        # Détection raison d'écoute principale
        listening_reasons = candidate.availability_timing.listening_reasons
        
        if listening_reasons:
            # Utiliser première raison pour adaptation
            primary_reason = listening_reasons[0]
            
            # Application matrice adaptative (simplifié)
            if "REMUNERATION" in primary_reason.value:
                return ExtendedComponentWeightsV3(
                    semantic=0.20,      # -4%
                    salary=0.30,        # +11%
                    experience=0.12,    # -2%
                    location=0.08,      # -1%
                    contract_flexibility=0.08,  # +3%
                    timing_compatibility=0.06,  # +2%
                    work_modality=0.04,
                    motivations=0.06,
                    sector_compatibility=0.04,
                    salary_progression=0.02
                )
            
            elif "LOCALISATION" in primary_reason.value:
                return ExtendedComponentWeightsV3(
                    semantic=0.20,      # -4%
                    salary=0.16,        # -3%
                    experience=0.12,    # -2%
                    location=0.18,      # +9%
                    work_modality=0.08, # +4%
                    timing_compatibility=0.05,
                    contract_flexibility=0.04,
                    motivations=0.07,
                    sector_compatibility=0.05,
                    salary_progression=0.03,
                    listening_reason=0.02
                )
        
        # Poids par défaut
        return ExtendedComponentWeightsV3()
    
    def _calculate_weighted_final_score(
        self,
        component_scores: ExtendedComponentScoresV3,
        weights: ExtendedComponentWeightsV3
    ) -> float:
        """🧮 Calcul score final pondéré"""
        
        final_score = (
            component_scores.semantic_score * weights.semantic +
            component_scores.salary_score * weights.salary +
            component_scores.experience_score * weights.experience +
            component_scores.location_score * weights.location +
            component_scores.motivations_score * weights.motivations +
            component_scores.sector_compatibility_score * weights.sector_compatibility +
            component_scores.contract_flexibility_score * weights.contract_flexibility +
            component_scores.timing_compatibility_score * weights.timing_compatibility +
            component_scores.work_modality_score * weights.work_modality +
            component_scores.salary_progression_score * weights.salary_progression +
            component_scores.listening_reason_score * weights.listening_reason +
            component_scores.candidate_status_score * weights.candidate_status
        )
        
        return min(1.0, final_score)
    
    def _evaluate_compatibility_level(self, score: float) -> str:
        """📊 Évaluation niveau compatibilité"""
        
        if score >= 0.85:
            return "excellent"
        elif score >= 0.70:
            return "good"
        elif score >= 0.50:
            return "average"
        elif score >= 0.30:
            return "poor"
        else:
            return "incompatible"
    
    def _generate_enhanced_recommendations(
        self,
        component_scores: ExtendedComponentScoresV3,
        weights: ExtendedComponentWeightsV3,
        candidate: ExtendedCandidateProfileV3,
        company: ExtendedCompanyProfileV3
    ) -> Dict[str, List[str]]:
        """💡 Génération recommandations enrichies"""
        
        recommendations = {
            "recommandations_candidat": [],
            "recommandations_entreprise": [],
            "points_forts_match": [],
            "points_attention": [],
            "deal_breakers": []
        }
        
        # Analyse points forts
        if component_scores.semantic_score >= 0.8:
            recommendations["points_forts_match"].append(
                "🎯 Excellente correspondance compétences/poste"
            )
        
        if component_scores.salary_score >= 0.8:
            recommendations["points_forts_match"].append(
                "💰 Fourchettes salariales très compatibles"
            )
        
        if component_scores.timing_compatibility_score >= 0.8:
            recommendations["points_forts_match"].append(
                "⏰ Timing de disponibilité idéal"
            )
        
        # Analyse points d'attention
        if component_scores.contract_flexibility_score < 0.5:
            recommendations["points_attention"].append(
                "📋 Type de contrat à négocier"
            )
        
        if component_scores.location_score < 0.5:
            recommendations["points_attention"].append(
                "📍 Localisation potentiellement problématique"
            )
        
        # Deal breakers
        if component_scores.salary_score < 0.3:
            recommendations["deal_breakers"].append(
                "💸 Écart salarial majeur - incompatibilité critique"
            )
        
        if component_scores.timing_compatibility_score < 0.2:
            recommendations["deal_breakers"].append(
                "⏱️ Timing incompatible - urgence vs disponibilité"
            )
        
        # Recommandations candidat
        if component_scores.contract_flexibility_score < 0.6:
            recommendations["recommandations_candidat"].append(
                "🔄 Considérer plus de flexibilité sur le type de contrat"
            )
        
        if component_scores.work_modality_score < 0.6:
            recommendations["recommandations_candidat"].append(
                "🏢 Revoir préférences télétravail/présentiel"
            )
        
        # Recommandations entreprise
        if component_scores.salary_score < 0.6:
            recommendations["recommandations_entreprise"].append(
                "💰 Revoir fourchette salariale proposée"
            )
        
        if component_scores.timing_compatibility_score < 0.6:
            recommendations["recommandations_entreprise"].append(
                "⏰ Assouplir délais de recrutement ou gérer préavis"
            )
        
        return recommendations
    
    def _analyze_questionnaire_exploitation(
        self,
        candidate: ExtendedCandidateProfileV3,
        company: ExtendedCompanyProfileV3,
        component_scores: ExtendedComponentScoresV3
    ) -> Dict[str, Any]:
        """📊 Analyse exploitation questionnaire"""
        
        # Calcul taux d'exploitation
        candidate_completion = candidate.questionnaire_completion_rate
        company_completion = company.questionnaire_completion_rate
        
        average_exploitation = (candidate_completion + company_completion) / 2
        
        # Données inutilisées
        unused_data = []
        
        if candidate_completion < 0.8:
            unused_data.append("Données candidat incomplètes")
        
        if company_completion < 0.8:
            unused_data.append("Données entreprise incomplètes")
        
        # Impact features V3.0
        v3_impact = {
            "timing_intelligence": component_scores.timing_compatibility_score - 0.5,
            "contract_intelligence": component_scores.contract_flexibility_score - 0.5,
            "environment_intelligence": component_scores.work_modality_score - 0.5
        }
        
        return {
            "exploitation_rate": average_exploitation,
            "unused_data": unused_data,
            "v3_features_impact": v3_impact
        }
    
    def _create_performance_monitoring(
        self,
        processing_time: float,
        component_scores: ExtendedComponentScoresV3,
        request: ExtendedMatchingRequestV3
    ) -> PerformanceMonitoringV3:
        """📈 Création monitoring performance"""
        
        target_achieved = processing_time <= self.performance_config["target_time_ms"]
        
        # Temps par composant (estimation)
        component_times = {
            "semantic": processing_time * 0.20,
            "salary": processing_time * 0.15,
            "experience": processing_time * 0.15,
            "location": processing_time * 0.25,
            "timing": processing_time * 0.10,
            "contract": processing_time * 0.08,
            "environment": processing_time * 0.07
        }
        
        return PerformanceMonitoringV3(
            total_processing_time_ms=processing_time,
            component_times_ms=component_times,
            adaptive_weighting_time_ms=processing_time * 0.05,
            google_maps_time_ms=processing_time * 0.20 if request.use_google_maps_intelligence else 0.0,
            target_achieved=target_achieved,
            cache_hits=0,  # TODO: Implémenter cache
            cache_misses=0
        )
    
    def _build_enhanced_response(
        self,
        final_score: float,
        compatibility_level: str,
        component_scores: ExtendedComponentScoresV3,
        applied_weights: ExtendedComponentWeightsV3,
        recommendations: Dict[str, List[str]],
        questionnaire_analysis: Dict[str, Any],
        performance_monitoring: PerformanceMonitoringV3,
        request: ExtendedMatchingRequestV3
    ) -> ExtendedMatchingResponseV3:
        """🔧 Construction réponse enrichie"""
        
        # Calcul confiance
        confidence = min(0.95, final_score * 1.1)
        
        # Détection raison d'écoute
        listening_reason = None
        if request.candidate.availability_timing.listening_reasons:
            listening_reason = request.candidate.availability_timing.listening_reasons[0]
        
        return ExtendedMatchingResponseV3(
            matching_score=final_score,
            confidence=confidence,
            compatibility=compatibility_level,
            component_scores=component_scores,
            applied_weights=applied_weights,
            adaptive_weighting_applied=request.use_adaptive_weighting,
            listening_reason_detected=listening_reason,
            weighting_boost_analysis={},
            recommandations_candidat=recommendations["recommandations_candidat"],
            recommandations_entreprise=recommendations["recommandations_entreprise"],
            points_forts_match=recommendations["points_forts_match"],
            points_attention=recommendations["points_attention"],
            deal_breakers=recommendations["deal_breakers"],
            questionnaire_exploitation_rate=questionnaire_analysis["exploitation_rate"],
            unused_questionnaire_data=questionnaire_analysis["unused_data"],
            v3_features_impact=questionnaire_analysis["v3_features_impact"],
            performance_monitoring=performance_monitoring,
            algorithm_version="3.0.0-enhanced",
            v2_compatibility_maintained=True
        )
    
    def _create_fallback_response(
        self,
        request: ExtendedMatchingRequestV3,
        error_message: str,
        processing_time: float
    ) -> ExtendedMatchingResponseV3:
        """🚨 Création réponse fallback"""
        
        logger.warning(f"Création réponse fallback: {error_message}")
        
        # Scores par défaut
        fallback_scores = ExtendedComponentScoresV3(
            semantic_score=0.6,
            salary_score=0.6,
            experience_score=0.6,
            location_score=0.6,
            motivations_score=0.6,
            sector_compatibility_score=0.6,
            contract_flexibility_score=0.6,
            timing_compatibility_score=0.6,
            work_modality_score=0.6,
            salary_progression_score=0.6,
            listening_reason_score=0.6,
            candidate_status_score=0.6
        )
        
        # Poids par défaut
        default_weights = ExtendedComponentWeightsV3()
        
        # Performance monitoring fallback
        performance_monitoring = PerformanceMonitoringV3(
            total_processing_time_ms=processing_time,
            target_achieved=False
        )
        
        return ExtendedMatchingResponseV3(
            matching_score=0.6,
            confidence=0.4,
            compatibility="average",
            component_scores=fallback_scores,
            applied_weights=default_weights,
            adaptive_weighting_applied=False,
            recommandations_candidat=["⚠️ Évaluation en mode dégradé"],
            recommandations_entreprise=["⚠️ Vérification manuelle recommandée"],
            points_forts_match=[],
            points_attention=["🔧 Erreur système - vérifier manuellement"],
            deal_breakers=[],
            questionnaire_exploitation_rate=0.5,
            unused_questionnaire_data=["Données partiellement exploitées"],
            v3_features_impact={"error": error_message},
            performance_monitoring=performance_monitoring,
            algorithm_version="3.0.0-fallback"
        )
    
    def _create_fallback_score_result(self, component_name: str, score: float) -> dict:
        """🛡️ Création résultat score fallback"""
        
        return {
            "final_score": score,
            "score_breakdown": {f"{component_name}_score": score},
            "explanations": [f"⚠️ Mode dégradé - {component_name}"],
            "recommendations": ["🔧 Vérification manuelle recommandée"],
            "calculated_at": datetime.now().isoformat(),
            "version": "3.0.0-fallback",
            "error": f"Erreur calcul {component_name}"
        }
    
    def _update_global_stats(self, processing_time: float, success: bool):
        """📊 Mise à jour statistiques globales"""
        
        if success:
            self.global_stats["successful_calculations"] += 1
            
            if processing_time <= self.performance_config["target_time_ms"]:
                self.global_stats["target_achievements"] += 1
        
        # Mise à jour moyenne
        total = self.global_stats["total_calculations"]
        current_avg = self.global_stats["average_processing_time"]
        
        self.global_stats["average_processing_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )
    
    def get_global_performance_stats(self) -> Dict[str, Any]:
        """📈 Statistiques performance globales"""
        
        total = self.global_stats["total_calculations"]
        success_rate = 0.0
        target_rate = 0.0
        
        if total > 0:
            success_rate = self.global_stats["successful_calculations"] / total
            target_rate = self.global_stats["target_achievements"] / total
        
        return {
            "enhanced_scorer_stats": self.global_stats.copy(),
            "performance_metrics": {
                "success_rate": success_rate,
                "target_achievement_rate": target_rate,
                "average_processing_time": self.global_stats["average_processing_time"]
            },
            "component_scorers": {
                "timing": self.availability_timing_scorer.get_performance_stats(),
                "contract": self.contract_types_scorer.get_performance_stats(),
                "environment": self.work_environment_scorer.get_performance_stats()
            },
            "configuration": self.performance_config
        }
    
    def reset_stats(self):
        """🔄 Reset statistiques"""
        self.global_stats = {
            "total_calculations": 0,
            "successful_calculations": 0,
            "average_processing_time": 0.0,
            "component_performance": {},
            "target_achievements": 0
        }
        
        # Reset stats des scorers individuels
        self.availability_timing_scorer.reset_stats()
        self.contract_types_scorer.reset_stats()
        self.work_environment_scorer.reset_stats()
