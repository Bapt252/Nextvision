"""
GPT Nextvision Integration Module V3.1
=====================================

Module d'intégration entre les parsers GPT et le système Nextvision V3.1.
Coordonne l'ensemble du pipeline de matching avec les nouvelles pondérations.

Version: 1.0.0
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

# Configuration du logging isolé pour ce module
integration_logger = logging.getLogger('gpt_modules.integration')


@dataclass
class MatchResult:
    """Résultat de matching avec détails des scores"""
    candidate_name: str
    job_title: str
    total_score: float
    scores_breakdown: Dict[str, float]
    hierarchical_compatibility: str
    alerts: List[str]
    performance_ms: float
    recommendation: str


class GPTNextvisionIntegrator:
    """
    Intégrateur principal GPT <-> Nextvision V3.1
    """
    
    def __init__(self, cv_parser=None, job_parser=None, hierarchical_detector=None, enhanced_bridge=None):
        self.cv_parser = cv_parser
        self.job_parser = job_parser
        self.hierarchical_detector = hierarchical_detector
        self.enhanced_bridge = enhanced_bridge
        self.logger = integration_logger
        self.version = "1.0.0"
        
        # Pondérations V3.1 avec NOUVEAU secteur (5%)
        self.weights_v31 = {
            'semantic': 0.30,      # 30% - Compatibilité sémantique
            'hierarchical': 0.15,  # 15% - Niveau hiérarchique  
            'salary': 0.20,        # 20% - Compatibilité salariale
            'experience': 0.20,    # 20% - Années d'expérience
            'location': 0.15,      # 15% - Localisation
            'sector': 0.05         # 5% - NOUVEAU: Secteur d'activité
        }
        
        # Seuils de validation
        self.critical_mismatch_threshold = 0.4  # Charlotte vs comptable < 0.4
        self.hierarchical_gap_threshold = 2     # Plus de 2 niveaux d'écart
        self.performance_target_ms = 100       # < 100ms maintenue

    def calculate_sector_score(self, candidate_sector: str, job_sector: str) -> float:
        """
        NOUVEAU: Calcule la compatibilité secteur (5% du score total)
        """
        if not candidate_sector or not job_sector:
            return 0.5  # Score neutre si données manquantes
            
        candidate_lower = candidate_sector.lower()
        job_lower = job_sector.lower()
        
        # Correspondance exacte
        if candidate_lower == job_lower:
            return 1.0
            
        # Correspondances sectorielles proches
        finance_keywords = ['finance', 'comptabilité', 'audit', 'contrôle', 'gestion']
        tech_keywords = ['tech', 'informatique', 'digital', 'logiciel', 'développement']
        conseil_keywords = ['conseil', 'consulting', 'stratégie', 'audit']
        
        candidate_finance = any(keyword in candidate_lower for keyword in finance_keywords)
        job_finance = any(keyword in job_lower for keyword in finance_keywords)
        
        candidate_tech = any(keyword in candidate_lower for keyword in tech_keywords)
        job_tech = any(keyword in job_lower for keyword in tech_keywords)
        
        candidate_conseil = any(keyword in candidate_lower for keyword in conseil_keywords)
        job_conseil = any(keyword in job_lower for keyword in conseil_keywords)
        
        # Bonus pour secteurs proches
        if (candidate_finance and job_finance) or (candidate_tech and job_tech) or (candidate_conseil and job_conseil):
            return 0.8
            
        # Finance vers conseil (secteurs compatibles)
        if (candidate_finance and job_conseil) or (candidate_conseil and job_finance):
            return 0.6
            
        # Score par défaut pour secteurs différents
        return 0.3

    def calculate_hierarchical_score(self, candidate_level: str, job_level: str) -> tuple:
        """
        Calcule le score hiérarchique et détecte les incompatibilités critiques
        """
        hierarchy_order = {
            'ENTRY': 0,
            'JUNIOR': 1, 
            'SENIOR': 2,
            'MANAGER': 3,
            'DIRECTOR': 4,
            'EXECUTIVE': 5
        }
        
        candidate_rank = hierarchy_order.get(candidate_level, 0)
        job_rank = hierarchy_order.get(job_level, 0)
        
        level_gap = abs(candidate_rank - job_rank)
        
        # Correspondance parfaite
        if level_gap == 0:
            return 1.0, "PERFECT_MATCH"
            
        # Correspondance acceptable (1 niveau d'écart)
        elif level_gap == 1:
            return 0.8, "GOOD_MATCH"
            
        # Correspondance possible (2 niveaux d'écart)
        elif level_gap == 2:
            return 0.5, "ACCEPTABLE_MATCH"
            
        # INCOMPATIBILITÉ CRITIQUE (3+ niveaux d'écart)
        # Cas Charlotte DARMON (EXECUTIVE) vs Comptable (ENTRY): 5 niveaux d'écart
        else:
            if candidate_rank > job_rank:
                return 0.1, "CRITICAL_OVERQUALIFIED"
            else:
                return 0.1, "CRITICAL_UNDERQUALIFIED"

    def calculate_salary_score(self, candidate_current: int, candidate_expected: int, 
                             job_min: int, job_max: int) -> float:
        """
        Calcule la compatibilité salariale
        """
        if not all([candidate_current, candidate_expected, job_min, job_max]):
            return 0.5  # Score neutre si données manquantes
            
        # Utilise le salaire souhaité du candidat comme référence
        target_salary = candidate_expected
        job_mid = (job_min + job_max) / 2
        
        # Correspondance parfaite (±10%)
        if abs(target_salary - job_mid) / job_mid <= 0.1:
            return 1.0
            
        # Correspondance bonne (±20%)
        elif abs(target_salary - job_mid) / job_mid <= 0.2:
            return 0.8
            
        # Correspondance acceptable (±30%)
        elif abs(target_salary - job_mid) / job_mid <= 0.3:
            return 0.6
            
        # Problème salarial majeur
        else:
            return 0.2

    def calculate_experience_score(self, candidate_years: int, job_min: int, job_max: int) -> float:
        """
        Calcule la compatibilité d'expérience
        """
        if not candidate_years or not job_min:
            return 0.5
            
        # Dans la fourchette demandée
        if job_min <= candidate_years <= job_max:
            return 1.0
            
        # Légèrement en dessous (acceptable)
        elif candidate_years >= job_min * 0.8:
            return 0.8
            
        # Expérience supérieure (surqualifié mais acceptable)
        elif candidate_years > job_max:
            # Surqualification modérée acceptable
            if candidate_years <= job_max * 1.5:
                return 0.7
            # Surqualification excessive (comme Charlotte vs comptable)
            else:
                return 0.3
                
        # Expérience insuffisante
        else:
            return 0.2

    def perform_complete_matching(self, candidate_data: Dict, job_data: Dict) -> MatchResult:
        """
        Effectue un matching complet avec le système V3.1
        """
        start_time = time.time()
        
        try:
            # Extraction des niveaux hiérarchiques
            candidate_level = candidate_data.get('professional_info', {}).get('hierarchical_level', 'ENTRY')
            job_level = job_data.get('requirements', {}).get('hierarchical_level', 'ENTRY')
            
            # Calcul des scores individuels
            scores = {}
            alerts = []
            
            # 1. Score hiérarchique (15%) - CRITIQUE pour Charlotte vs Comptable
            hierarchical_score, hierarchical_status = self.calculate_hierarchical_score(
                candidate_level, job_level
            )
            scores['hierarchical'] = hierarchical_score
            
            if hierarchical_status.startswith('CRITICAL'):
                alerts.append(f"CRITICAL_MISMATCH: Incompatibilité hiérarchique ({candidate_level} vs {job_level})")
            
            # 2. Score salarial (20%)
            salary_score = self.calculate_salary_score(
                candidate_data.get('professional_info', {}).get('current_salary', 0),
                candidate_data.get('professional_info', {}).get('expected_salary', 0),
                job_data.get('requirements', {}).get('salary_min', 0),
                job_data.get('requirements', {}).get('salary_max', 0)
            )
            scores['salary'] = salary_score
            
            # 3. Score expérience (20%)
            experience_score = self.calculate_experience_score(
                candidate_data.get('professional_info', {}).get('experience_years', 0),
                job_data.get('requirements', {}).get('experience_min', 0),
                job_data.get('requirements', {}).get('experience_max', 0)
            )
            scores['experience'] = experience_score
            
            # 4. NOUVEAU: Score secteur (5%)
            sector_score = self.calculate_sector_score(
                candidate_data.get('professional_info', {}).get('sector', ''),
                job_data.get('job_info', {}).get('sector', '')
            )
            scores['sector'] = sector_score
            
            # 5. Score sémantique (30%) - Simplifié pour les tests
            # En production, utiliserait le système d'embeddings existant
            semantic_score = 0.7  # Score par défaut pour les tests
            scores['semantic'] = semantic_score
            
            # 6. Score localisation (15%) - Simplifié
            location_score = 0.8  # Score par défaut pour les tests
            scores['location'] = location_score
            
            # Calcul du score total avec pondérations V3.1
            total_score = (
                scores['semantic'] * self.weights_v31['semantic'] +
                scores['hierarchical'] * self.weights_v31['hierarchical'] +
                scores['salary'] * self.weights_v31['salary'] +
                scores['experience'] * self.weights_v31['experience'] +
                scores['location'] * self.weights_v31['location'] +
                scores['sector'] * self.weights_v31['sector']
            )
            
            # Détection des alertes critiques
            if total_score < self.critical_mismatch_threshold:
                alerts.append(f"CRITICAL_MISMATCH: Score total {total_score:.3f} < {self.critical_mismatch_threshold}")
                
            # Recommandation
            if total_score >= 0.8:
                recommendation = "EXCELLENT_MATCH"
            elif total_score >= 0.6:
                recommendation = "GOOD_MATCH"
            elif total_score >= 0.4:
                recommendation = "POSSIBLE_MATCH"
            else:
                recommendation = "NO_MATCH"
                
            # Performance
            elapsed_time = (time.time() - start_time) * 1000
            
            if elapsed_time > self.performance_target_ms:
                alerts.append(f"PERFORMANCE_WARNING: {elapsed_time:.1f}ms > {self.performance_target_ms}ms")
            
            return MatchResult(
                candidate_name=candidate_data.get('personal_info', {}).get('name', ''),
                job_title=job_data.get('job_info', {}).get('title', ''),
                total_score=total_score,
                scores_breakdown=scores,
                hierarchical_compatibility=hierarchical_status,
                alerts=alerts,
                performance_ms=elapsed_time,
                recommendation=recommendation
            )
            
        except Exception as e:
            self.logger.error(f"Erreur lors du matching: {str(e)}")
            elapsed_time = (time.time() - start_time) * 1000
            
            return MatchResult(
                candidate_name="ERROR",
                job_title="ERROR", 
                total_score=0.0,
                scores_breakdown={},
                hierarchical_compatibility="ERROR",
                alerts=[f"SYSTEM_ERROR: {str(e)}"],
                performance_ms=elapsed_time,
                recommendation="ERROR"
            )

    def test_charlotte_darmon_vs_comptable(self) -> Dict[str, Any]:
        """
        Test spécifique Charlotte DARMON vs poste comptable
        DOIT valider les 5 objectifs mentionnés dans le contexte
        """
        self.logger.info("🧪 DÉBUT TEST CHARLOTTE DARMON VS COMPTABLE")
        
        # Récupération des profils de test
        if self.cv_parser:
            charlotte_data = self.cv_parser.to_nextvision_format(
                self.cv_parser.get_charlotte_darmon_profile()
            )
        else:
            # Profil Charlotte en cas de parser non disponible
            charlotte_data = {
                "personal_info": {"name": "Charlotte DARMON"},
                "professional_info": {
                    "hierarchical_level": "EXECUTIVE",
                    "experience_years": 15,
                    "current_salary": 80000,
                    "expected_salary": 90000,
                    "sector": "Finance"
                }
            }
        
        if self.job_parser:
            comptable_data = self.job_parser.to_nextvision_format(
                self.job_parser.get_comptable_entry_job()
            )
        else:
            # Poste comptable en cas de parser non disponible
            comptable_data = {
                "job_info": {"title": "Comptable", "sector": "Comptabilité"},
                "requirements": {
                    "hierarchical_level": "ENTRY",
                    "experience_min": 2,
                    "experience_max": 5,
                    "salary_min": 30000,
                    "salary_max": 35000
                }
            }
        
        # Exécution du matching
        result = self.perform_complete_matching(charlotte_data, comptable_data)
        
        # Validation des 5 objectifs
        objectives = {
            "1_score_abaisse": result.total_score < 0.4,
            "2_incompatibilite_hierarchique": "CRITICAL" in result.hierarchical_compatibility,
            "3_alerte_critical_mismatch": any("CRITICAL_MISMATCH" in alert for alert in result.alerts),
            "4_performance_maintenue": result.performance_ms < 100,
            "5_secteur_integre": 'sector' in result.scores_breakdown
        }
        
        # Rapport détaillé
        rapport = {
            "test_name": "Charlotte DARMON vs Comptable ENTRY",
            "timestamp": time.time(),
            "result": result,
            "objectives_validation": objectives,
            "success": all(objectives.values()),
            "weights_used": self.weights_v31,
            "system_version": {
                "integration": self.version,
                "cv_parser": getattr(self.cv_parser, 'version', 'N/A'),
                "job_parser": getattr(self.job_parser, 'version', 'N/A')
            }
        }
        
        # Log du résultat
        success_emoji = "✅" if rapport["success"] else "❌"
        self.logger.info(f"{success_emoji} TEST TERMINÉ - Score: {result.total_score:.3f} - Objectifs: {sum(objectives.values())}/5")
        
        return rapport

    def integration_status(self) -> Dict[str, Any]:
        """
        Statut de l'intégration GPT <-> Nextvision V3.1
        """
        return {
            "integration_version": self.version,
            "weights_v31": self.weights_v31,
            "thresholds": {
                "critical_mismatch": self.critical_mismatch_threshold,
                "hierarchical_gap": self.hierarchical_gap_threshold,
                "performance_target_ms": self.performance_target_ms
            },
            "parsers_status": {
                "cv_parser": "Available" if self.cv_parser else "Not configured",
                "job_parser": "Available" if self.job_parser else "Not configured",
                "hierarchical_detector": "Available" if self.hierarchical_detector else "Not configured",
                "enhanced_bridge": "Available" if self.enhanced_bridge else "Not configured"
            },
            "features": [
                "Système hiérarchique V3.1 intégré",
                "Nouveau scoring secteur (5%)",
                "Détection CRITICAL_MISMATCH",
                "Performance < 100ms maintenue",
                "Parsers GPT isolés (conflict-free)"
            ]
        }


# Fonctions utilitaires pour les tests rapides
def quick_test_charlotte_vs_comptable():
    """
    Test rapide Charlotte vs Comptable sans dépendances externes
    """
    from .cv_parser import CVParserGPT
    from .job_parser import JobParserGPT
    
    # Initialisation des parsers
    cv_parser = CVParserGPT()
    job_parser = JobParserGPT()
    
    # Initialisation de l'intégrateur
    integrator = GPTNextvisionIntegrator(
        cv_parser=cv_parser,
        job_parser=job_parser
    )
    
    # Exécution du test
    return integrator.test_charlotte_darmon_vs_comptable()


if __name__ == "__main__":
    # Test autonome
    print("🚀 Test autonome de l'intégration GPT V3.1")
    result = quick_test_charlotte_vs_comptable()
    print(f"Résultat: {result['success']}")
    print(f"Score: {result['result'].total_score:.3f}")
    print(f"Objectifs validés: {sum(result['objectives_validation'].values())}/5")
