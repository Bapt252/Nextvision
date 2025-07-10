"""
🌉 Enhanced Commitment Bridge V3.1 Hiérarchique
Intègre la détection de niveau hiérarchique pour améliorer le matching
Résout le problème Charlotte DARMON (DAF matchée sur postes comptables)

Author: Assistant Claude
Version: 3.1.0
Date: 2025-07-10
"""

import logging
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime

# Import des modèles nécessaires
from nextvision.models.bidirectional_models import (
    BiDirectionalCandidateProfile, BiDirectionalCompanyProfile,
    PersonalInfoBidirectional, CompetencesProfessionnelles, AttentesCandidat,
    MotivationsCandidat, InformationsEntreprise, DescriptionPoste,
    ExigencesPoste, ConditionsTravail, CriteresRecrutement,
    NiveauExperience, TypeContrat, RaisonEcouteCandidat, UrgenceRecrutement
)

# Import des modèles transport
from nextvision.models.transport_models import TravelMode

# Import du système hiérarchique
from nextvision.services.hierarchical_detector import HierarchicalScoring, HierarchicalLevel

# Import du bridge existant pour héritage
from nextvision.services.enhanced_commitment_bridge_v3_simplified import (
    EnhancedCommitmentBridgeV3Simplified, BridgeMetrics
)

logger = logging.getLogger(__name__)

class HierarchicalBridgeMetrics(BridgeMetrics):
    """📊 Métriques étendues avec informations hiérarchiques"""
    
    def __init__(self):
        super().__init__()
        self.hierarchical_score = 0.0
        self.candidate_level = None
        self.job_level = None
        self.compatibility_level = ""
        self.hierarchical_warnings = []

class EnhancedCommitmentBridgeV3Hierarchical(EnhancedCommitmentBridgeV3Simplified):
    """🌉 Bridge V3.1 avec détection hiérarchique intégrée"""
    
    def __init__(self):
        super().__init__()
        self.version = "3.1.0-hierarchical"
        self.hierarchical_scorer = HierarchicalScoring()
        
        # Nouvelles pondérations incluant la hiérarchie
        self.scoring_weights = {
            'semantic': 0.30,      # était 0.35
            'salary': 0.20,        # était 0.25  
            'experience': 0.20,    # était 0.25
            'location': 0.15,      # inchangé
            'hierarchical': 0.15   # nouveau composant
        }
        
        # Statistiques étendues
        self.stats.update({
            "hierarchical_matches": 0,
            "hierarchical_mismatches": 0,
            "avg_hierarchical_score": 0.0
        })
        
        logger.info("🌉 Enhanced Bridge V3.1 Hiérarchique initialisé")
    
    async def enhanced_matching_with_hierarchy(
        self, 
        candidate_data: Dict[str, Any], 
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🎯 Matching principal avec détection hiérarchique
        Compatible avec l'interface existante mais ajoute la composante hiérarchique
        """
        
        start_time = datetime.now()
        
        try:
            # 1. Scores existants (utilisation des méthodes héritées)
            semantic_score = self._calculate_semantic_score(candidate_data, job_data)
            salary_score = self._calculate_salary_score(candidate_data, job_data)
            experience_score = self._calculate_experience_score(candidate_data, job_data)
            location_score = self._calculate_location_score(candidate_data, job_data)
            
            # 2. NOUVEAU: Score hiérarchique
            hierarchical_analysis = self.hierarchical_scorer.calculate_hierarchical_score(
                candidate_data.get('parsed_content', ''),
                job_data.get('parsed_content', '')
            )
            hierarchical_score = hierarchical_analysis['hierarchical_score']
            
            # 3. Calcul du score total avec nouvelle pondération
            total_score = (
                semantic_score * self.scoring_weights['semantic'] +
                salary_score * self.scoring_weights['salary'] +
                experience_score * self.scoring_weights['experience'] +
                location_score * self.scoring_weights['location'] +
                hierarchical_score * self.scoring_weights['hierarchical']
            )
            
            # 4. Détermination de la compatibilité avec alertes hiérarchiques
            compatibility = self._determine_compatibility_with_hierarchy(
                total_score, hierarchical_analysis
            )
            
            # 5. Génération des alertes
            alerts = self._generate_hierarchical_alerts(hierarchical_analysis)
            
            # 6. Calcul du temps de traitement
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # 7. Mise à jour des statistiques
            self._update_hierarchical_stats(hierarchical_score, hierarchical_analysis)
            
            # 8. Confiance basée sur sémantique + hiérarchie
            confidence = min((semantic_score + hierarchical_score) / 2, 1.0)
            
            result = {
                'total_score': total_score,
                'compatibility': compatibility,
                'confidence': confidence,
                'components': {
                    'semantic': semantic_score,
                    'salary': salary_score,
                    'experience': experience_score,
                    'location': location_score,
                    'hierarchical': hierarchical_score  # Nouveau
                },
                'hierarchical_details': {
                    'candidate_level': hierarchical_analysis['candidate_level'],
                    'job_level': hierarchical_analysis['job_level'],
                    'compatibility_level': hierarchical_analysis['compatibility_level'],
                    'salary_warning': hierarchical_analysis.get('salary_warning'),
                    'management_indicators': hierarchical_analysis['detailed_analysis']['management_indicators'],
                    'candidate_experience': hierarchical_analysis.get('candidate_experience')
                },
                'alerts': alerts,
                'processing_time': processing_time,
                'version': self.version
            }
            
            logger.info(
                f"✅ Matching hiérarchique terminé: score {total_score:.3f}, "
                f"hiérarchie {hierarchical_score:.3f}, "
                f"compatibilité '{compatibility}', "
                f"temps {processing_time:.1f}ms"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur matching hiérarchique: {e}")
            # Fallback vers système existant
            return await self._fallback_to_standard_matching(candidate_data, job_data)
    
    def _calculate_semantic_score(self, candidate_data: Dict[str, Any], job_data: Dict[str, Any]) -> float:
        """🔤 Calcul score sémantique (hérité et adapté)"""
        # Pour l'instant, simulation basée sur vos résultats
        # TODO: Intégrer avec votre système sémantique existant
        candidate_skills = candidate_data.get('skills', [])
        job_requirements = job_data.get('competences_requises', [])
        
        if not candidate_skills or not job_requirements:
            return 0.6  # Score par défaut
        
        # Simulation d'un matching sémantique simple
        common_skills = set(str(skill).lower() for skill in candidate_skills) & \
                       set(str(req).lower() for req in job_requirements)
        
        if len(job_requirements) > 0:
            semantic_score = len(common_skills) / len(job_requirements)
            return min(semantic_score * 1.5, 1.0)  # Boost pour correspondances exactes
        
        return 0.6
    
    def _calculate_salary_score(self, candidate_data: Dict[str, Any], job_data: Dict[str, Any]) -> float:
        """💰 Calcul score salarial (hérité et adapté)"""
        candidate_salary = candidate_data.get('salary', {})
        job_salary = job_data.get('salary_range', (35000, 50000))
        
        candidate_min = candidate_salary.get('expected', 40000)
        job_max = job_salary[1] if isinstance(job_salary, tuple) else 50000
        
        if candidate_min <= job_max:
            return 1.0
        elif candidate_min <= job_max * 1.2:  # 20% de tolérance
            return 0.7
        elif candidate_min <= job_max * 1.5:  # 50% de tolérance
            return 0.4
        else:
            return 0.1
    
    def _calculate_experience_score(self, candidate_data: Dict[str, Any], job_data: Dict[str, Any]) -> float:
        """📈 Calcul score expérience (hérité et adapté)"""
        candidate_exp = candidate_data.get('experience', {}).get('total_years', 3)
        job_exp_required = job_data.get('experience_requise', '2-5 ans')
        
        # Parsing simple des exigences d'expérience
        if '0-2' in job_exp_required or 'junior' in job_exp_required.lower():
            required_min, required_max = 0, 2
        elif '2-5' in job_exp_required:
            required_min, required_max = 2, 5
        elif '5-10' in job_exp_required or 'senior' in job_exp_required.lower():
            required_min, required_max = 5, 10
        else:
            required_min, required_max = 3, 7  # Par défaut
        
        if required_min <= candidate_exp <= required_max:
            return 1.0
        elif required_min <= candidate_exp <= required_max * 1.5:
            return 0.8
        elif candidate_exp >= required_min * 0.7:
            return 0.6
        else:
            return 0.3
    
    def _calculate_location_score(self, candidate_data: Dict[str, Any], job_data: Dict[str, Any]) -> float:
        """📍 Calcul score localisation (hérité et adapté)"""
        # Simulation simple - TODO: intégrer avec Transport Intelligence V3.0
        candidate_location = candidate_data.get('location', {}).get('city', 'Paris')
        job_location = job_data.get('localisation', 'Paris')
        
        if candidate_location.lower() == job_location.lower():
            return 1.0
        elif 'paris' in candidate_location.lower() and 'paris' in job_location.lower():
            return 0.9
        else:
            return 0.6  # Accepte mobilité/remote
    
    def _determine_compatibility_with_hierarchy(
        self, 
        total_score: float, 
        hierarchical_analysis: Dict[str, Any]
    ) -> str:
        """🎯 Détermine la compatibilité en tenant compte du niveau hiérarchique"""
        
        base_compatibility = self._get_base_compatibility(total_score)
        hierarchical_score = hierarchical_analysis['hierarchical_score']
        
        # Dégradation si problème hiérarchique majeur
        if hierarchical_score < 0.3:
            if base_compatibility in ["excellent", "very_good"]:
                logger.warning(
                    f"🔻 Dégradation compatibilité pour inadéquation hiérarchique: "
                    f"{hierarchical_analysis['candidate_level']} → {hierarchical_analysis['job_level']}"
                )
                return "average"  # Dégradation forcée
            elif base_compatibility == "good":
                return "poor"
        
        # Amélioration si excellent match hiérarchique
        if hierarchical_score > 0.9 and total_score > 0.7:
            logger.info("🔺 Amélioration compatibilité pour excellent match hiérarchique")
            return "excellent"
        
        return base_compatibility
    
    def _generate_hierarchical_alerts(self, hierarchical_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """⚠️ Génère des alertes basées sur l'analyse hiérarchique"""
        
        alerts = []
        
        # Alerte surqualification critique (comme Charlotte DARMON)
        if hierarchical_analysis['hierarchical_score'] < 0.3:
            alerts.append({
                'type': 'CRITICAL_MISMATCH',
                'message': f"Inadéquation hiérarchique critique: {hierarchical_analysis['candidate_level']} → {hierarchical_analysis['job_level']}",
                'impact': 'HIGH',
                'recommendation': 'Chercher un poste correspondant au niveau du candidat',
                'score_impact': f"Score réduit de {0.15 * (0.3 - hierarchical_analysis['hierarchical_score']):.2f}"
            })
        
        # Alerte sur-qualification modérée
        elif hierarchical_analysis['hierarchical_score'] < 0.6:
            alerts.append({
                'type': 'OVERQUALIFICATION',
                'message': f"Candidat potentiellement surqualifié: {hierarchical_analysis['compatibility_level']}",
                'impact': 'MEDIUM',
                'recommendation': 'Vérifier les motivations du candidat pour ce niveau de poste',
                'score_impact': f"Score réduit de {0.15 * (0.6 - hierarchical_analysis['hierarchical_score']):.2f}"
            })
        
        # Alerte écart salarial
        if hierarchical_analysis.get('salary_warning'):
            alerts.append({
                'type': 'SALARY_MISMATCH',
                'message': hierarchical_analysis['salary_warning'],
                'impact': 'HIGH',
                'recommendation': 'Revoir la grille salariale ou chercher un candidat dans la fourchette'
            })
        
        # Alerte excellent match hiérarchique
        if hierarchical_analysis['hierarchical_score'] > 0.9:
            alerts.append({
                'type': 'EXCELLENT_MATCH',
                'message': f"Excellent alignement hiérarchique: {hierarchical_analysis['compatibility_level']}",
                'impact': 'POSITIVE',
                'recommendation': 'Candidat prioritaire pour ce poste'
            })
        
        return alerts
    
    def _get_base_compatibility(self, score: float) -> str:
        """📊 Compatibilité de base selon le score (logique existante)"""
        if score >= 0.8:
            return "excellent"
        elif score >= 0.7:
            return "very_good"
        elif score >= 0.6:
            return "good"
        elif score >= 0.5:
            return "average"
        else:
            return "poor"
    
    def _update_hierarchical_stats(self, hierarchical_score: float, hierarchical_analysis: Dict[str, Any]):
        """📈 Mise à jour des statistiques hiérarchiques"""
        
        if hierarchical_score >= 0.7:
            self.stats["hierarchical_matches"] += 1
        else:
            self.stats["hierarchical_mismatches"] += 1
        
        # Calcul moyenne glissante
        total_matches = self.stats["hierarchical_matches"] + self.stats["hierarchical_mismatches"]
        if total_matches > 1:
            current_avg = self.stats["avg_hierarchical_score"]
            self.stats["avg_hierarchical_score"] = (
                (current_avg * (total_matches - 1) + hierarchical_score) / total_matches
            )
        else:
            self.stats["avg_hierarchical_score"] = hierarchical_score
    
    async def _fallback_to_standard_matching(
        self, 
        candidate_data: Dict[str, Any], 
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """🚨 Fallback vers le système standard en cas d'erreur"""
        
        logger.warning("🔄 Fallback vers matching standard (sans hiérarchie)")
        
        # Utilise les pondérations anciennes
        semantic_score = self._calculate_semantic_score(candidate_data, job_data)
        salary_score = self._calculate_salary_score(candidate_data, job_data)
        experience_score = self._calculate_experience_score(candidate_data, job_data)
        location_score = self._calculate_location_score(candidate_data, job_data)
        
        # Pondérations V3.0 standards
        total_score = (
            semantic_score * 0.35 +
            salary_score * 0.25 +
            experience_score * 0.25 +
            location_score * 0.15
        )
        
        return {
            'total_score': total_score,
            'compatibility': self._get_base_compatibility(total_score),
            'confidence': semantic_score,
            'components': {
                'semantic': semantic_score,
                'salary': salary_score,
                'experience': experience_score,
                'location': location_score,
                'hierarchical': 0.0  # Non calculé
            },
            'hierarchical_details': {
                'candidate_level': 'UNKNOWN',
                'job_level': 'UNKNOWN',
                'compatibility_level': 'Non analysé',
                'error': 'Fallback mode - hiérarchie non analysée'
            },
            'alerts': [{
                'type': 'FALLBACK_MODE',
                'message': 'Analyse hiérarchique indisponible - matching standard utilisé',
                'impact': 'MEDIUM'
            }],
            'processing_time': 1.0,
            'version': f"{self.version}-fallback"
        }
    
    def get_hierarchical_stats(self) -> Dict[str, Any]:
        """📊 Statistiques spécifiques au système hiérarchique"""
        
        base_stats = self.get_stats()
        
        hierarchical_stats = {
            'hierarchical_system': {
                'total_analyses': self.stats["hierarchical_matches"] + self.stats["hierarchical_mismatches"],
                'good_matches': self.stats["hierarchical_matches"],
                'mismatches': self.stats["hierarchical_mismatches"],
                'average_score': self.stats["avg_hierarchical_score"],
                'mismatch_rate': (
                    self.stats["hierarchical_mismatches"] / 
                    max(1, self.stats["hierarchical_matches"] + self.stats["hierarchical_mismatches"])
                )
            },
            'scoring_weights': self.scoring_weights,
            'version': self.version
        }
        
        return {**base_stats, **hierarchical_stats}

class HierarchicalBridgeFactory:
    """🏗️ Factory pour création bridge hiérarchique"""
    
    @staticmethod
    def create_hierarchical_bridge() -> EnhancedCommitmentBridgeV3Hierarchical:
        """Création bridge V3.1 hiérarchique"""
        return EnhancedCommitmentBridgeV3Hierarchical()
    
    @staticmethod
    def create_standard_bridge() -> EnhancedCommitmentBridgeV3Simplified:
        """Création bridge V3.0 standard (fallback)"""
        return EnhancedCommitmentBridgeV3Simplified()
