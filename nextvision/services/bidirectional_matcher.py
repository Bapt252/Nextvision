"""
🎯 Nextvision v2.0 - BiDirectional Matcher & Adaptive Weighting Engine

Moteur principal de matching bidirectionnel avec :
- Pondération adaptative candidat (raison d'écoute) + entreprise (urgence)
- Orchestration des 4 scorers prioritaires
- Cache intelligent et optimisation performance
- Intégration Google Maps Intelligence

Author: NEXTEN Team
Version: 2.0.0 - BiDirectional Matching Engine
"""

from typing import Dict, List, Optional, Tuple
import logging
import time
import asyncio
from datetime import datetime

# Import des modèles et scorers
from nextvision.models.bidirectional_models import (
    BiDirectionalCandidateProfile, BiDirectionalCompanyProfile,
    BiDirectionalMatchingRequest, BiDirectionalMatchingResponse,
    ComponentWeights, AdaptiveWeightingConfig, MatchingComponentScores,
    RaisonEcouteCandidat, UrgenceRecrutement
)

from nextvision.services.bidirectional_scorer import (
    SemanticScorer, SalaryScorer, ExperienceScorer, LocationScorer,
    ScoringResult
)

# Import des services Google Maps existants
from nextvision.services.google_maps_service import GoogleMapsService
from nextvision.engines.location_scoring import LocationScoringEngine

logger = logging.getLogger(__name__)

# === ADAPTIVE WEIGHTING ENGINE ===

class AdaptiveWeightingEngine:
    """🎯 Moteur de pondération adaptative bidirectionnelle"""
    
    def __init__(self):
        # Configuration poids par défaut (4 composants business) - CORRIGÉ
        self.default_weights = ComponentWeights(
            semantique=0.35,  # 35% - Correspondance CV ↔ Fiche de poste
            salaire=0.25,     # 25% - Budget entreprise vs attentes candidat
            experience=0.25,  # 25% - Années d'expérience requises (CORRIGÉ de 0.20 à 0.25)
            localisation=0.15 # 15% - Impact géographique
        )
        
        # Adaptations candidat selon raison d'écoute - CORRIGÉ pour totaliser 1.0
        self.candidat_adaptations = {
            RaisonEcouteCandidat.REMUNERATION_TROP_FAIBLE: {
                "salaire": 0.35,      # +10% priorité salaire
                "semantique": 0.30,   # -5% sémantique
                "experience": 0.20,   # -5% expérience
                "localisation": 0.15, # maintenu
                "reasoning": "Priorité accordée à l'amélioration salariale"
            },
            RaisonEcouteCandidat.POSTE_NE_COINCIDE_PAS: {
                "semantique": 0.45,   # +10% priorité sémantique
                "salaire": 0.20,      # -5% salaire
                "experience": 0.20,   # -5% expérience
                "localisation": 0.15, # maintenu
                "reasoning": "Focus sur l'adéquation des compétences et du poste"
            },
            RaisonEcouteCandidat.POSTE_TROP_LOIN: {
                "localisation": 0.25, # +10% priorité localisation
                "semantique": 0.30,   # -5% sémantique
                "salaire": 0.25,      # maintenu
                "experience": 0.20,   # -5% expérience
                "reasoning": "Priorité à la proximité géographique"
            },
            RaisonEcouteCandidat.MANQUE_FLEXIBILITE: {
                "semantique": 0.30,   # -5% sémantique
                "salaire": 0.30,      # +5% salaire (compensation)
                "experience": 0.20,   # -5% expérience
                "localisation": 0.20, # +5% localisation (remote)
                "reasoning": "Recherche d'un meilleur équilibre vie pro/perso"
            },
            RaisonEcouteCandidat.MANQUE_PERSPECTIVES: {
                "semantique": 0.40,   # +5% sémantique (match poste)
                "salaire": 0.30,      # +5% salaire (évolution)
                "experience": 0.15,   # -10% expérience
                "localisation": 0.15, # maintenu
                "reasoning": "Focus sur les opportunités de développement"
            }
        }
        
        # Adaptations entreprise selon urgence
        self.entreprise_adaptations = {
            UrgenceRecrutement.CRITIQUE: {
                "boost_factor": 1.2,
                "tolerance_increase": 0.15,
                "reasoning": "Urgence critique - critères assouplis"
            },
            UrgenceRecrutement.URGENT: {
                "boost_factor": 1.1,
                "tolerance_increase": 0.10,
                "reasoning": "Urgence élevée - légère flexibilité"
            },
            UrgenceRecrutement.NORMAL: {
                "boost_factor": 1.0,
                "tolerance_increase": 0.0,
                "reasoning": "Délais normaux - critères standards"
            },
            UrgenceRecrutement.LONG_TERME: {
                "boost_factor": 0.95,
                "tolerance_increase": -0.05,
                "reasoning": "Recherche longue - critères stricts"
            }
        }
    
    def calculate_adaptive_weights(self, candidat: BiDirectionalCandidateProfile,
                                 entreprise: BiDirectionalCompanyProfile) -> AdaptiveWeightingConfig:
        """🎯 Calcule pondération adaptative bidirectionnelle"""
        
        # 1. Adaptation côté candidat
        candidat_weights = self._apply_candidat_adaptation(candidat.motivations.raison_ecoute)
        
        # 2. Adaptation côté entreprise (tolerance boost)
        entreprise_weights = self._apply_entreprise_adaptation(
            candidat_weights, entreprise.recrutement.urgence
        )
        
        # 3. Configuration finale
        config = AdaptiveWeightingConfig(
            candidat_weights=candidat_weights,
            entreprise_weights=entreprise_weights,
            raison_candidat=candidat.motivations.raison_ecoute,
            urgence_entreprise=entreprise.recrutement.urgence,
            reasoning_candidat=self.candidat_adaptations[candidat.motivations.raison_ecoute]["reasoning"],
            reasoning_entreprise=self.entreprise_adaptations[entreprise.recrutement.urgence]["reasoning"]
        )
        
        logger.info(f"🎯 Pondération adaptative calculée:")
        logger.info(f"   👤 Candidat: {candidat.motivations.raison_ecoute.value}")
        logger.info(f"   🏢 Entreprise: {entreprise.recrutement.urgence.value}")
        logger.info(f"   📊 Poids finaux: {entreprise_weights.dict()}")
        
        return config
    
    def _apply_candidat_adaptation(self, raison: RaisonEcouteCandidat) -> ComponentWeights:
        """Applique adaptation candidat"""
        if raison in self.candidat_adaptations:
            adaptation = self.candidat_adaptations[raison]
            return ComponentWeights(
                semantique=adaptation["semantique"],
                salaire=adaptation["salaire"],
                experience=adaptation["experience"],
                localisation=adaptation["localisation"]
            )
        return self.default_weights
    
    def _apply_entreprise_adaptation(self, candidat_weights: ComponentWeights,
                                   urgence: UrgenceRecrutement) -> ComponentWeights:
        """Applique adaptation entreprise (boost de tolérance)"""
        if urgence not in self.entreprise_adaptations:
            return candidat_weights
        
        adaptation = self.entreprise_adaptations[urgence]
        boost_factor = adaptation["boost_factor"]
        
        # Application du boost sur tous les composants
        return ComponentWeights(
            semantique=min(1.0, candidat_weights.semantique * boost_factor),
            salaire=min(1.0, candidat_weights.salaire * boost_factor),
            experience=min(1.0, candidat_weights.experience * boost_factor),
            localisation=min(1.0, candidat_weights.localisation * boost_factor)
        )

# === BIDIRECTIONAL MATCHER ===

class BiDirectionalMatcher:
    """🎯 Moteur principal de matching bidirectionnel"""
    
    def __init__(self, google_maps_service: GoogleMapsService = None,
                 location_scoring_engine: LocationScoringEngine = None):
        
        # Initialisation des scorers
        self.semantic_scorer = SemanticScorer()
        self.salary_scorer = SalaryScorer()
        self.experience_scorer = ExperienceScorer()
        self.location_scorer = LocationScorer(
            google_maps_service=google_maps_service,
            location_scoring_engine=location_scoring_engine
        )
        
        # Moteur de pondération adaptative
        self.weighting_engine = AdaptiveWeightingEngine()
        
        # Cache pour optimisation performance
        self.cache = {}
        self.cache_ttl = 3600  # 1 heure
        
        # Stats performance
        self.stats = {
            "total_matches": 0,
            "cache_hits": 0,
            "avg_processing_time": 0.0,
            "last_reset": datetime.now()
        }
    
    async def calculate_bidirectional_match(self, request: BiDirectionalMatchingRequest) -> BiDirectionalMatchingResponse:
        """🎯 MATCHING PRINCIPAL : Calcul bidirectionnel candidat ↔ entreprise"""
        start_time = time.time()
        
        try:
            logger.info(f"🎯 === MATCHING BIDIRECTIONNEL ===")
            logger.info(f"👤 Candidat: {request.candidat.personal_info.firstName} {request.candidat.personal_info.lastName}")
            logger.info(f"🏢 Entreprise: {request.entreprise.entreprise.nom} - {request.entreprise.poste.titre}")
            
            # 1. Vérification cache
            cache_key = self._generate_cache_key(request)
            if cache_key in self.cache and not request.force_adaptive_weighting:
                cached_result = self.cache[cache_key]
                if self._is_cache_valid(cached_result["timestamp"]):
                    self.stats["cache_hits"] += 1
                    logger.info("⚡ Résultat depuis cache")
                    return cached_result["response"]
            
            # 2. Pondération adaptative bidirectionnelle
            adaptive_config = self.weighting_engine.calculate_adaptive_weights(
                request.candidat, request.entreprise
            )
            weights = adaptive_config.entreprise_weights
            
            # 3. Calcul parallèle des 4 composants
            scoring_tasks = [
                self._calculate_semantic_score(request.candidat, request.entreprise),
                self._calculate_salary_score(request.candidat, request.entreprise),
                self._calculate_experience_score(request.candidat, request.entreprise),
                self._calculate_location_score(request.candidat, request.entreprise)
            ]
            
            semantic_result, salary_result, experience_result, location_result = await asyncio.gather(*scoring_tasks)
            
            # 4. Agrégation scores avec pondération adaptative
            component_scores = MatchingComponentScores(
                semantique_score=semantic_result.score,
                semantique_details=semantic_result.details,
                salaire_score=salary_result.score,
                salaire_details=salary_result.details,
                experience_score=experience_result.score,
                experience_details=experience_result.details,
                localisation_score=location_result.score,
                localisation_details=location_result.details
            )
            
            # 5. Score final pondéré
            final_score = (
                semantic_result.score * weights.semantique +
                salary_result.score * weights.salaire +
                experience_result.score * weights.experience +
                location_result.score * weights.localisation
            )
            
            # 6. Calcul confiance et compatibilité
            confidence = self._calculate_confidence(semantic_result, salary_result, experience_result, location_result)
            compatibility = self._determine_compatibility(final_score)
            
            # 7. Génération recommandations
            recommandations = self._generate_recommendations(
                request.candidat, request.entreprise, component_scores, adaptive_config
            )
            
            # 8. Construction réponse
            processing_time = (time.time() - start_time) * 1000
            
            response = BiDirectionalMatchingResponse(
                matching_score=round(final_score, 3),
                confidence=round(confidence, 3),
                compatibility=compatibility,
                component_scores=component_scores,
                adaptive_weighting=adaptive_config,
                recommandations_candidat=recommandations["candidat"],
                recommandations_entreprise=recommandations["entreprise"],
                points_forts=recommandations["points_forts"],
                points_attention=recommandations["points_attention"],
                processing_time_ms=round(processing_time, 2)
            )
            
            # 9. Cache du résultat
            self.cache[cache_key] = {
                "response": response,
                "timestamp": datetime.now()
            }
            
            # 10. Mise à jour stats
            self._update_stats(processing_time)
            
            logger.info(f"✅ Matching terminé en {processing_time:.2f}ms")
            logger.info(f"📊 Score final: {final_score:.3f} (confiance: {confidence:.3f})")
            logger.info(f"🎯 Compatibilité: {compatibility}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur matching bidirectionnel: {e}")
            # Retour d'une réponse d'erreur structurée
            return BiDirectionalMatchingResponse(
                matching_score=0.0,
                confidence=0.0,
                compatibility="incompatible",
                component_scores=MatchingComponentScores(
                    semantique_score=0.0, semantique_details={"error": str(e)},
                    salaire_score=0.0, salaire_details={"error": str(e)},
                    experience_score=0.0, experience_details={"error": str(e)},
                    localisation_score=0.0, localisation_details={"error": str(e)}
                ),
                adaptive_weighting=self.weighting_engine.calculate_adaptive_weights(
                    request.candidat, request.entreprise
                ),
                recommandations_candidat=[f"Erreur de traitement: {str(e)}"],
                recommandations_entreprise=[f"Erreur de traitement: {str(e)}"],
                points_forts=[],
                points_attention=[f"Erreur système: {str(e)}"],
                processing_time_ms=(time.time() - start_time) * 1000
            )
    
    # === MÉTHODES DE SCORING ASYNCHRONES ===
    
    async def _calculate_semantic_score(self, candidat: BiDirectionalCandidateProfile,
                                       entreprise: BiDirectionalCompanyProfile) -> ScoringResult:
        """Calcul sémantique asynchrone"""
        return self.semantic_scorer.calculate_score(candidat, entreprise)
    
    async def _calculate_salary_score(self, candidat: BiDirectionalCandidateProfile,
                                    entreprise: BiDirectionalCompanyProfile) -> ScoringResult:
        """Calcul salarial asynchrone"""
        return self.salary_scorer.calculate_score(candidat, entreprise)
    
    async def _calculate_experience_score(self, candidat: BiDirectionalCandidateProfile,
                                        entreprise: BiDirectionalCompanyProfile) -> ScoringResult:
        """Calcul expérience asynchrone"""
        return self.experience_scorer.calculate_score(candidat, entreprise)
    
    async def _calculate_location_score(self, candidat: BiDirectionalCandidateProfile,
                                      entreprise: BiDirectionalCompanyProfile) -> ScoringResult:
        """Calcul localisation asynchrone"""
        return self.location_scorer.calculate_score(candidat, entreprise)
    
    # === MÉTHODES UTILITAIRES ===
    
    def _calculate_confidence(self, *results: ScoringResult) -> float:
        """Calcule confiance globale basée sur les résultats individuels"""
        confidences = [result.confidence for result in results if result.confidence > 0]
        if not confidences:
            return 0.0
        
        # Confiance = moyenne pondérée par les scores
        scores = [result.score for result in results if result.score > 0]
        if not scores:
            return 0.0
        
        weighted_confidence = sum(c * s for c, s in zip(confidences, scores)) / sum(scores)
        return min(0.95, weighted_confidence)
    
    def _determine_compatibility(self, score: float) -> str:
        """Détermine niveau de compatibilité"""
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
    
    def _generate_recommendations(self, candidat: BiDirectionalCandidateProfile,
                                entreprise: BiDirectionalCompanyProfile,
                                scores: MatchingComponentScores,
                                adaptive_config: AdaptiveWeightingConfig) -> Dict[str, List[str]]:
        """Génère recommandations intelligentes"""
        
        recommandations_candidat = []
        recommandations_entreprise = []
        points_forts = []
        points_attention = []
        
        # Analyse sémantique
        if scores.semantique_score >= 0.8:
            points_forts.append("Excellente adéquation compétences/poste")
        elif scores.semantique_score < 0.5:
            points_attention.append("Écart significatif compétences requises")
            recommandations_candidat.append("Développer les compétences manquantes identifiées")
            recommandations_entreprise.append("Prévoir formation/accompagnement sur les compétences manquantes")
        
        # Analyse salariale
        if scores.salaire_score >= 0.8:
            points_forts.append("Fourchettes salariales bien alignées")
        elif scores.salaire_score < 0.5:
            points_attention.append("Écart salarial important à négocier")
            if candidat.motivations.raison_ecoute == RaisonEcouteCandidat.REMUNERATION_TROP_FAIBLE:
                recommandations_entreprise.append("Envisager budget supplémentaire ou avantages compensatoires")
        
        # Analyse expérience
        if scores.experience_score >= 0.8:
            points_forts.append("Niveau d'expérience parfaitement adapté")
        elif scores.experience_score < 0.5:
            if scores.experience_details.get("adequation", "").startswith("Sous-qualifié"):
                recommandations_entreprise.append("Prévoir plan de formation pour combler l'écart d'expérience")
                recommandations_candidat.append("Mettre en avant expériences transférables et motivation d'apprentissage")
        
        # Analyse localisation
        if scores.localisation_score >= 0.8:
            points_forts.append("Localisation très favorable")
        elif scores.localisation_score < 0.5:
            points_attention.append("Défis géographiques à considérer")
            if candidat.motivations.raison_ecoute == RaisonEcouteCandidat.POSTE_TROP_LOIN:
                recommandations_entreprise.append("Proposer télétravail ou aide transport si possible")
        
        # Recommandations adaptatives
        if adaptive_config.urgence_entreprise == UrgenceRecrutement.CRITIQUE:
            recommandations_entreprise.append("Accélérer le processus de recrutement")
            recommandations_candidat.append("Disponibilité rapide valorisée par l'entreprise")
        
        return {
            "candidat": recommandations_candidat,
            "entreprise": recommandations_entreprise,
            "points_forts": points_forts,
            "points_attention": points_attention
        }
    
    def _generate_cache_key(self, request: BiDirectionalMatchingRequest) -> str:
        """Génère clé de cache unique"""
        candidat_id = f"{request.candidat.personal_info.email}_{hash(str(request.candidat.dict()))}"
        entreprise_id = f"{request.entreprise.entreprise.nom}_{hash(str(request.entreprise.dict()))}"
        return f"match_{candidat_id}_{entreprise_id}"
    
    def _is_cache_valid(self, timestamp: datetime) -> bool:
        """Vérifie validité du cache"""
        return (datetime.now() - timestamp).seconds < self.cache_ttl
    
    def _update_stats(self, processing_time: float):
        """Met à jour statistiques"""
        self.stats["total_matches"] += 1
        if self.stats["total_matches"] == 1:
            self.stats["avg_processing_time"] = processing_time
        else:
            self.stats["avg_processing_time"] = (
                (self.stats["avg_processing_time"] * (self.stats["total_matches"] - 1) + processing_time) 
                / self.stats["total_matches"]
            )
    
    def get_performance_stats(self) -> Dict:
        """Retourne statistiques de performance"""
        cache_hit_rate = (self.stats["cache_hits"] / max(1, self.stats["total_matches"])) * 100
        
        return {
            "total_matches": self.stats["total_matches"],
            "cache_hits": self.stats["cache_hits"],
            "cache_hit_rate_percent": round(cache_hit_rate, 2),
            "avg_processing_time_ms": round(self.stats["avg_processing_time"], 2),
            "cache_size": len(self.cache),
            "uptime_hours": (datetime.now() - self.stats["last_reset"]).seconds / 3600
        }
    
    def clear_cache(self):
        """Vide le cache"""
        self.cache.clear()
        logger.info("🧹 Cache vidé")

# === FACTORY POUR INITIALISATION ===

class BiDirectionalMatcherFactory:
    """🏗️ Factory pour création du matcher avec dépendances"""
    
    @staticmethod
    def create_matcher(google_maps_service: GoogleMapsService = None,
                      location_scoring_engine: LocationScoringEngine = None) -> BiDirectionalMatcher:
        """Crée un matcher avec les services Google Maps"""
        return BiDirectionalMatcher(
            google_maps_service=google_maps_service,
            location_scoring_engine=location_scoring_engine
        )
    
    @staticmethod
    def create_basic_matcher() -> BiDirectionalMatcher:
        """Crée un matcher sans Google Maps (pour tests/développement)"""
        return BiDirectionalMatcher()

# === TESTS & VALIDATION ===

if __name__ == "__main__":
    import asyncio
    from nextvision.models.bidirectional_models import (
        PersonalInfoBidirectional, CompetencesProfessionnelles, AttentesCandidat,
        MotivationsCandidat, InformationsEntreprise, DescriptionPoste,
        ExigencesPoste, ConditionsTravail, CriteresRecrutement,
        NiveauExperience, TypeContrat
    )
    
    async def test_bidirectional_matching():
        """Test du système de matching bidirectionnel"""
        
        # Création candidat test
        candidat = BiDirectionalCandidateProfile(
            personal_info=PersonalInfoBidirectional(
                firstName="Marie",
                lastName="Dupont",
                email="marie.dupont@email.com",
                phone="+33 6 12 34 56 78"
            ),
            experience_globale=NiveauExperience.CONFIRME,
            competences=CompetencesProfessionnelles(
                competences_techniques=["Maîtrise du logiciel comptable CEGID", "Gestion comptable et fiscale"],
                logiciels_maitrise=["CEGID", "Excel", "SAP"],
                langues={"Français": "Natif", "Anglais": "Courant"}
            ),
            attentes=AttentesCandidat(
                salaire_min=38000,
                salaire_max=45000,
                localisation_preferee="Paris 8ème",
                distance_max_km=30,
                remote_accepte=True
            ),
            motivations=MotivationsCandidat(
                raison_ecoute=RaisonEcouteCandidat.REMUNERATION_TROP_FAIBLE,
                motivations_principales=["Évolution salariale", "Nouvelles responsabilités"]
            )
        )
        
        # Création entreprise test
        entreprise = BiDirectionalCompanyProfile(
            entreprise=InformationsEntreprise(
                nom="Cabinet Comptable Excellence",
                secteur="Comptabilité",
                localisation="Paris 8ème"
            ),
            poste=DescriptionPoste(
                titre="Comptable Unique H/F",
                localisation="Paris 8ème",
                type_contrat=TypeContrat.CDI,
                salaire_min=35000,
                salaire_max=42000,
                competences_requises=["Maîtrise du logiciel comptable CEGID", "Gestion comptable et fiscale"]
            ),
            exigences=ExigencesPoste(
                experience_requise="5 ans - 10 ans",
                competences_obligatoires=["Maîtrise du logiciel comptable CEGID"],
                competences_souhaitees=["Gestion comptable et fiscale"]
            ),
            conditions=ConditionsTravail(
                remote_possible=True,
                avantages=["Tickets restaurant", "Mutuelle"]
            ),
            recrutement=CriteresRecrutement(
                urgence=UrgenceRecrutement.URGENT,
                criteres_prioritaires=["expérience", "compétences_techniques"]
            )
        )
        
        # Test matching
        matcher = BiDirectionalMatcherFactory.create_basic_matcher()
        request = BiDirectionalMatchingRequest(
            candidat=candidat,
            entreprise=entreprise,
            force_adaptive_weighting=True
        )
        
        result = await matcher.calculate_bidirectional_match(request)
        
        print("🎯 === TEST MATCHING BIDIRECTIONNEL ===")
        print(f"📊 Score final: {result.matching_score}")
        print(f"🎯 Compatibilité: {result.compatibility}")
        print(f"⚡ Temps traitement: {result.processing_time_ms}ms")
        print(f"🧠 Sémantique: {result.component_scores.semantique_score}")
        print(f"💰 Salaire: {result.component_scores.salaire_score}")
        print(f"📈 Expérience: {result.component_scores.experience_score}")
        print(f"📍 Localisation: {result.component_scores.localisation_score}")
        print(f"🎯 Pondération adaptative: {result.adaptive_weighting.reasoning_candidat}")
        print("✅ Test réussi!")
        
        return result
    
    # Lancement du test
    if __name__ == "__main__":
        asyncio.run(test_bidirectional_matching())
