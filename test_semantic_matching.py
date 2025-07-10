#!/usr/bin/env python3
"""
Script de Test Sémantique Nextvision V3.1
==========================================

Script pour tester et optimiser le matching sémantique via GPT
Exécution: python test_semantic_matching.py

Baptiste Comas - Nextvision V3.1 Semantic Testing
"""

import json
import time
import logging
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import sys
import os

# Ajout du chemin des modules GPT
sys.path.append('gpt_modules')

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('semantic_testing')

@dataclass
class TestResult:
    """Résultat d'un test de matching sémantique"""
    test_name: str
    candidate_name: str
    job_title: str
    expected_score_range: Tuple[float, float]
    actual_score: float
    semantic_score: float
    hierarchical_score: float
    performance_ms: float
    success: bool
    details: Dict[str, Any]

class SemanticTestSuite:
    """Suite de tests pour le matching sémantique"""
    
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key
        self.results: List[TestResult] = []
        
        # Import conditionnel d'OpenAI
        self.openai_client = None
        if openai_api_key:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=openai_api_key)
                logger.info("✅ Client OpenAI configuré")
            except ImportError:
                logger.warning("⚠️ Module openai non installé")
            except Exception as e:
                logger.error(f"❌ Erreur configuration OpenAI: {e}")
        
        # Import des modules Nextvision
        try:
            from cv_parser import CVParserGPT
            from job_parser import JobParserGPT
            from integration import GPTNextvisionIntegrator
            
            self.cv_parser = CVParserGPT(self.openai_client)
            self.job_parser = JobParserGPT(self.openai_client)
            self.integrator = GPTNextvisionIntegrator(
                cv_parser=self.cv_parser,
                job_parser=self.job_parser
            )
            logger.info("✅ Modules Nextvision chargés")
            
        except ImportError as e:
            logger.error(f"❌ Erreur import modules: {e}")
            sys.exit(1)

    def create_test_profiles(self) -> Dict[str, Dict]:
        """Crée les profils de test diversifiés"""
        
        # Profils CV de test
        cv_profiles = {
            "charlotte_darmon": {
                "nom_complet": "Charlotte DARMON",
                "titre_poste": "Directrice Administrative et Financière",
                "niveau_hierarchique": "EXECUTIVE",
                "experience_years": 15,
                "salaire_actuel": 80000,
                "salaire_souhaite": 90000,
                "competences": [
                    "Direction financière", "Contrôle de gestion", "Audit interne",
                    "Consolidation", "Stratégie financière", "Management d'équipe",
                    "IFRS", "Fiscalité", "Trésorerie", "Budget prévisionnel"
                ],
                "secteur_activite": "Finance"
            },
            
            "dev_react_senior": {
                "nom_complet": "Thomas DUBOIS",
                "titre_poste": "Développeur Full-Stack Senior",
                "niveau_hierarchique": "SENIOR",
                "experience_years": 6,
                "salaire_actuel": 55000,
                "salaire_souhaite": 65000,
                "competences": [
                    "React.js", "Node.js", "JavaScript", "TypeScript",
                    "MongoDB", "Express.js", "Git", "Docker",
                    "Jest", "Redux", "REST API", "GraphQL"
                ],
                "secteur_activite": "Tech"
            },
            
            "comptable_junior": {
                "nom_complet": "Marie MARTIN",
                "titre_poste": "Comptable",
                "niveau_hierarchique": "JUNIOR",
                "experience_years": 3,
                "salaire_actuel": 32000,
                "salaire_souhaite": 38000,
                "competences": [
                    "Saisie comptable", "Rapprochements bancaires", "TVA",
                    "Excel", "Sage Comptabilité", "Factures", "Déclarations"
                ],
                "secteur_activite": "Comptabilité"
            },
            
            "manager_finance": {
                "nom_complet": "Jean BERNARD",
                "titre_poste": "Manager Contrôle de Gestion",
                "niveau_hierarchique": "MANAGER",
                "experience_years": 10,
                "salaire_actuel": 65000,
                "salaire_souhaite": 75000,
                "competences": [
                    "Contrôle de gestion", "Budget", "Reporting",
                    "Management équipe", "SAP", "Excel avancé",
                    "Tableau de bord", "Analyse financière"
                ],
                "secteur_activite": "Finance"
            },
            
            "reconversion_dev": {
                "nom_complet": "Sophie GARCIA",
                "titre_poste": "Développeuse Junior (Reconversion)",
                "niveau_hierarchique": "ENTRY",
                "experience_years": 1,
                "salaire_actuel": 28000,
                "salaire_souhaite": 35000,
                "competences": [
                    "Python", "Django", "HTML", "CSS", "JavaScript",
                    "Git", "SQL", "Bootstrap", "Formation intensive"
                ],
                "secteur_activite": "Tech"
            }
        }
        
        # Fiches de poste de test
        job_profiles = {
            "comptable_entry": {
                "titre_poste": "Comptable",
                "niveau_hierarchique": "ENTRY",
                "experience_requise_min": 2,
                "experience_requise_max": 5,
                "salaire_min": 30000,
                "salaire_max": 35000,
                "competences_requises": [
                    "Saisie comptable", "Rapprochements bancaires", "TVA",
                    "Paie simple", "Excel", "Rigueur"
                ],
                "secteur_activite": "Comptabilité"
            },
            
            "dev_react_senior": {
                "titre_poste": "Développeur React Senior",
                "niveau_hierarchique": "SENIOR",
                "experience_requise_min": 5,
                "experience_requise_max": 8,
                "salaire_min": 55000,
                "salaire_max": 70000,
                "competences_requises": [
                    "React.js", "JavaScript", "TypeScript", "Redux",
                    "REST API", "Git", "Tests unitaires"
                ],
                "competences_souhaitees": [
                    "Node.js", "GraphQL", "Docker", "AWS"
                ],
                "secteur_activite": "Tech"
            },
            
            "daf_executive": {
                "titre_poste": "Directeur Administratif et Financier",
                "niveau_hierarchique": "EXECUTIVE",
                "experience_requise_min": 12,
                "experience_requise_max": 20,
                "salaire_min": 85000,
                "salaire_max": 110000,
                "competences_requises": [
                    "Direction financière", "Consolidation", "IFRS", "Management",
                    "Stratégie financière", "Audit interne", "Contrôle de gestion"
                ],
                "secteur_activite": "Finance"
            },
            
            "dev_junior_python": {
                "titre_poste": "Développeur Python Junior",
                "niveau_hierarchique": "JUNIOR",
                "experience_requise_min": 2,
                "experience_requise_max": 3,
                "salaire_min": 35000,
                "salaire_max": 42000,
                "competences_requises": [
                    "Python", "Django", "SQL", "Git", "Linux"
                ],
                "competences_souhaitees": [
                    "REST API", "Docker", "Tests unitaires"
                ],
                "secteur_activite": "Tech"
            },
            
            "manager_finance": {
                "titre_poste": "Manager Contrôle de Gestion",
                "niveau_hierarchique": "MANAGER",
                "experience_requise_min": 8,
                "experience_requise_max": 12,
                "salaire_min": 60000,
                "salaire_max": 75000,
                "competences_requises": [
                    "Contrôle de gestion", "Budget", "Reporting",
                    "Management", "Excel avancé", "SAP"
                ],
                "secteur_activite": "Finance"
            }
        }
        
        return {"cv_profiles": cv_profiles, "job_profiles": job_profiles}

    def convert_to_nextvision_format(self, profile_type: str, profile_data: Dict) -> Dict:
        """Convertit les profils de test au format Nextvision"""
        
        if profile_type == "cv":
            return {
                "personal_info": {
                    "name": profile_data["nom_complet"],
                    "email": f"{profile_data['nom_complet'].lower().replace(' ', '.')}@test.com",
                    "phone": "+33 6 00 00 00 00",
                    "address": "Paris, France"
                },
                "professional_info": {
                    "current_title": profile_data["titre_poste"],
                    "hierarchical_level": profile_data["niveau_hierarchique"],
                    "experience_years": profile_data["experience_years"],
                    "current_salary": profile_data["salaire_actuel"],
                    "expected_salary": profile_data["salaire_souhaite"],
                    "sector": profile_data["secteur_activite"]
                },
                "skills": {
                    "technical_skills": profile_data["competences"],
                    "software": [],
                    "languages": [{"langue": "Français", "niveau": "Natif"}]
                },
                "metadata": {
                    "parser_version": "test_v1.0",
                    "hierarchical_level": profile_data["niveau_hierarchique"]
                }
            }
        
        elif profile_type == "job":
            return {
                "job_info": {
                    "title": profile_data["titre_poste"],
                    "company": "Test Company",
                    "sector": profile_data["secteur_activite"],
                    "location": "Paris, France"
                },
                "requirements": {
                    "hierarchical_level": profile_data["niveau_hierarchique"],
                    "experience_min": profile_data["experience_requise_min"],
                    "experience_max": profile_data["experience_requise_max"],
                    "salary_min": profile_data["salaire_min"],
                    "salary_max": profile_data["salaire_max"],
                    "required_skills": profile_data["competences_requises"],
                    "preferred_skills": profile_data.get("competences_souhaitees", [])
                },
                "metadata": {
                    "parser_version": "test_v1.0",
                    "hierarchical_level": profile_data["niveau_hierarchique"]
                }
            }

    def run_semantic_test(self, cv_key: str, job_key: str, expected_range: Tuple[float, float]) -> TestResult:
        """Exécute un test de matching sémantique spécifique"""
        
        logger.info(f"🧪 Test: {cv_key} vs {job_key}")
        
        profiles = self.create_test_profiles()
        cv_profile = profiles["cv_profiles"][cv_key]
        job_profile = profiles["job_profiles"][job_key]
        
        # Conversion au format Nextvision
        candidate_data = self.convert_to_nextvision_format("cv", cv_profile)
        job_data = self.convert_to_nextvision_format("job", job_profile)
        
        # Exécution du matching
        start_time = time.time()
        result = self.integrator.perform_complete_matching(candidate_data, job_data)
        elapsed_time = (time.time() - start_time) * 1000
        
        # Évaluation du succès
        success = (
            expected_range[0] <= result.total_score <= expected_range[1] and
            result.performance_ms < 100
        )
        
        test_result = TestResult(
            test_name=f"{cv_key}_vs_{job_key}",
            candidate_name=cv_profile["nom_complet"],
            job_title=job_profile["titre_poste"],
            expected_score_range=expected_range,
            actual_score=result.total_score,
            semantic_score=result.scores_breakdown.get('semantic', 0),
            hierarchical_score=result.scores_breakdown.get('hierarchical', 0),
            performance_ms=elapsed_time,
            success=success,
            details={
                "scores_breakdown": result.scores_breakdown,
                "alerts": result.alerts,
                "recommendation": result.recommendation,
                "hierarchical_compatibility": result.hierarchical_compatibility
            }
        )
        
        self.results.append(test_result)
        
        # Log du résultat
        status_emoji = "✅" if success else "❌"
        logger.info(f"{status_emoji} Score: {result.total_score:.3f} (attendu: {expected_range[0]:.2f}-{expected_range[1]:.2f})")
        logger.info(f"   Sémantique: {result.scores_breakdown.get('semantic', 0):.3f}")
        logger.info(f"   Performance: {elapsed_time:.1f}ms")
        
        return test_result

    def run_full_test_suite(self) -> Dict[str, Any]:
        """Exécute la suite complète de tests sémantiques"""
        
        logger.info("🚀 DÉBUT SUITE DE TESTS SÉMANTIQUES")
        logger.info("=" * 50)
        
        # Test cases avec ranges de scores attendus
        test_cases = [
            # Cas validés (Charlotte DARMON)
            ("charlotte_darmon", "comptable_entry", (0.2, 0.4)),  # Incompatible
            ("charlotte_darmon", "daf_executive", (0.8, 1.0)),    # Excellent match
            
            # Tests développement
            ("dev_react_senior", "dev_react_senior", (0.8, 1.0)), # Perfect match
            ("dev_react_senior", "dev_junior_python", (0.3, 0.5)), # Surqualifié
            ("reconversion_dev", "dev_junior_python", (0.6, 0.8)), # Bonne reconversion
            
            # Tests finance/comptabilité
            ("comptable_junior", "comptable_entry", (0.7, 0.9)),   # Bon match
            ("comptable_junior", "daf_executive", (0.1, 0.3)),     # Sous-qualifié
            ("manager_finance", "manager_finance", (0.9, 1.0)),    # Perfect match
            
            # Tests croisés (incompatibilités)
            ("dev_react_senior", "comptable_entry", (0.1, 0.3)),   # Secteurs différents
            ("comptable_junior", "dev_react_senior", (0.1, 0.3)),  # Secteurs différents
        ]
        
        # Exécution des tests
        total_tests = len(test_cases)
        successful_tests = 0
        
        for i, (cv_key, job_key, expected_range) in enumerate(test_cases, 1):
            logger.info(f"\n📋 Test {i}/{total_tests}")
            test_result = self.run_semantic_test(cv_key, job_key, expected_range)
            
            if test_result.success:
                successful_tests += 1
        
        # Analyse des résultats
        success_rate = (successful_tests / total_tests) * 100
        
        # Statistiques par composant
        semantic_scores = [r.semantic_score for r in self.results]
        avg_semantic = sum(semantic_scores) / len(semantic_scores)
        
        performance_times = [r.performance_ms for r in self.results]
        avg_performance = sum(performance_times) / len(performance_times)
        
        logger.info("\n" + "=" * 50)
        logger.info("📊 RÉSULTATS DE LA SUITE DE TESTS")
        logger.info("=" * 50)
        logger.info(f"✅ Tests réussis: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
        logger.info(f"📈 Score sémantique moyen: {avg_semantic:.3f}")
        logger.info(f"⚡ Performance moyenne: {avg_performance:.1f}ms")
        
        # Identification des problèmes
        failed_tests = [r for r in self.results if not r.success]
        if failed_tests:
            logger.info(f"\n❌ {len(failed_tests)} tests échoués:")
            for test in failed_tests:
                logger.info(f"   - {test.test_name}: {test.actual_score:.3f} "
                          f"(attendu: {test.expected_score_range[0]:.2f}-{test.expected_score_range[1]:.2f})")
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "avg_semantic_score": avg_semantic,
            "avg_performance_ms": avg_performance,
            "results": self.results,
            "failed_tests": failed_tests
        }

    def analyze_semantic_weaknesses(self) -> Dict[str, Any]:
        """Analyse les faiblesses du système sémantique actuel"""
        
        logger.info("\n🔍 ANALYSE DES FAIBLESSES SÉMANTIQUES")
        logger.info("=" * 40)
        
        weaknesses = {
            "low_semantic_scores": [],
            "false_positives": [],
            "false_negatives": [],
            "performance_issues": []
        }
        
        for result in self.results:
            # Scores sémantiques trop bas
            if result.semantic_score < 0.3 and result.expected_score_range[1] > 0.7:
                weaknesses["false_negatives"].append(result)
            
            # Scores sémantiques trop hauts
            if result.semantic_score > 0.7 and result.expected_score_range[1] < 0.4:
                weaknesses["false_positives"].append(result)
            
            # Problèmes de performance
            if result.performance_ms > 50:
                weaknesses["performance_issues"].append(result)
        
        # Recommendations
        recommendations = []
        
        if weaknesses["false_positives"]:
            recommendations.append("Implémenter la détection d'incompatibilités sectorielles")
        
        if weaknesses["false_negatives"]:
            recommendations.append("Ajouter un dictionnaire de synonymes")
        
        if len([r for r in self.results if r.semantic_score < 0.4]) > len(self.results) * 0.3:
            recommendations.append("Revoir l'algorithme de matching des compétences")
        
        logger.info(f"🔧 Recommandations d'amélioration:")
        for i, rec in enumerate(recommendations, 1):
            logger.info(f"   {i}. {rec}")
        
        return {
            "weaknesses": weaknesses,
            "recommendations": recommendations
        }

    def generate_test_report(self) -> str:
        """Génère un rapport de test complet"""
        
        report = []
        report.append("# RAPPORT DE TEST SÉMANTIQUE NEXTVISION V3.1")
        report.append("=" * 50)
        report.append(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Version: {self.integrator.version}")
        report.append("")
        
        # Résumé
        total = len(self.results)
        success = len([r for r in self.results if r.success])
        report.append(f"## RÉSUMÉ")
        report.append(f"- Tests exécutés: {total}")
        report.append(f"- Tests réussis: {success} ({(success/total*100):.1f}%)")
        report.append(f"- Performance moyenne: {sum(r.performance_ms for r in self.results)/total:.1f}ms")
        report.append("")
        
        # Détails par test
        report.append("## DÉTAILS DES TESTS")
        for result in self.results:
            status = "✅ SUCCÈS" if result.success else "❌ ÉCHEC"
            report.append(f"### {result.test_name} - {status}")
            report.append(f"- Candidat: {result.candidate_name}")
            report.append(f"- Poste: {result.job_title}")
            report.append(f"- Score total: {result.actual_score:.3f} (attendu: {result.expected_score_range[0]:.2f}-{result.expected_score_range[1]:.2f})")
            report.append(f"- Score sémantique: {result.semantic_score:.3f}")
            report.append(f"- Performance: {result.performance_ms:.1f}ms")
            report.append("")
        
        return "\n".join(report)

def main():
    """Fonction principale"""
    
    print("🚀 NEXTVISION V3.1 - TEST SÉMANTIQUE")
    print("=" * 40)
    
    # Configuration OpenAI (optionnelle)
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("⚠️ OPENAI_API_KEY non configurée - utilisation des profils de fallback")
    
    # Initialisation de la suite de tests
    test_suite = SemanticTestSuite(openai_key)
    
    try:
        # Exécution des tests
        results = test_suite.run_full_test_suite()
        
        # Analyse des faiblesses
        analysis = test_suite.analyze_semantic_weaknesses()
        
        # Génération du rapport
        report = test_suite.generate_test_report()
        
        # Sauvegarde du rapport
        with open(f"semantic_test_report_{int(time.time())}.md", "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"\n📝 Rapport sauvegardé: semantic_test_report_{int(time.time())}.md")
        
        # Recommandations finales
        if results["success_rate"] >= 80:
            print("�� SUCCÈS: Système sémantique fonctionnel")
        else:
            print("⚠️ AMÉLIORATIONS NÉCESSAIRES")
            for rec in analysis["recommendations"]:
                print(f"   - {rec}")
    
    except Exception as e:
        logger.error(f"❌ Erreur lors des tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
