#!/usr/bin/env python3
"""
Script de Mise à Niveau Sémantique V3.2 - Nextvision
====================================================

Script pour appliquer les améliorations sémantiques et tester les résultats
Corrige les 4 problèmes identifiés :
1. Surqualification mal détectée  
2. Matches parfaits sous-évalués
3. Incompatibilités sectorielles 
4. Algorithme de matching trop simpliste

Usage: python upgrade_semantic_v32.py

Baptiste Comas - Nextvision V3.2
"""

import sys
import time
import logging
from typing import Dict, Any
import os

# Ajout du chemin des modules
sys.path.append('gpt_modules')

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('semantic_upgrade')

class SemanticUpgradeManager:
    """Gestionnaire de mise à niveau sémantique"""
    
    def __init__(self):
        self.logger = logger
        self.backup_created = False
        
        # Import des modules existants
        try:
            from integration import GPTNextvisionIntegrator, quick_test_charlotte_vs_comptable
            from cv_parser import CVParserGPT
            from job_parser import JobParserGPT
            
            self.integration_module = GPTNextvisionIntegrator
            self.test_function = quick_test_charlotte_vs_comptable
            
            # Configuration OpenAI si disponible
            openai_client = None
            if os.getenv('OPENAI_API_KEY'):
                try:
                    import openai
                    openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                except:
                    pass
            
            # Initialisation des parsers
            self.cv_parser = CVParserGPT(openai_client)
            self.job_parser = JobParserGPT(openai_client)
            
            logger.info("✅ Modules Nextvision chargés")
            
        except ImportError as e:
            logger.error(f"❌ Erreur import: {e}")
            sys.exit(1)

    def create_enhanced_semantic_method(self):
        """Crée la méthode sémantique améliorée"""
        
        # Dictionnaires intégrés directement
        skills_synonyms = {
            "tech": {
                "javascript": ["js", "ecmascript", "node.js", "frontend", "react", "vue"],
                "python": ["py", "django", "flask", "data science", "backend"],
                "react": ["reactjs", "react.js", "frontend", "spa", "javascript"],
                "node": ["nodejs", "node.js", "backend", "javascript", "express"],
                "api": ["rest", "api rest", "web service", "microservice"],
                "git": ["github", "gitlab", "version control", "versionning"],
                "docker": ["container", "containerisation", "devops"],
                "sql": ["mysql", "postgresql", "database", "bdd"],
                "frontend": ["front-end", "interface", "ui", "client-side"],
                "backend": ["back-end", "serveur", "server-side", "api"]
            },
            "finance": {
                "excel": ["tableur", "spreadsheet", "vba", "modélisation financière"],
                "sap": ["erp", "système de gestion", "sap fi", "sap co"],
                "ifrs": ["normes comptables", "consolidation", "reporting financier"],
                "comptabilité": ["compta", "comptable", "écritures", "saisie"],
                "contrôle": ["contrôle de gestion", "budget", "pilotage"],
                "audit": ["révision", "contrôle interne", "audit interne"],
                "consolidation": ["comptes consolidés", "ifrs", "groupe"],
                "fiscalité": ["fiscal", "impôts", "déclarations", "tva"],
                "trésorerie": ["cash management", "finances", "liquidité"],
                "reporting": ["rapport", "dashboard", "tableau de bord"]
            },
            "general": {
                "management": ["gestion équipe", "encadrement", "leadership"],
                "gestion": ["pilotage", "organisation", "coordination"],
                "projet": ["gestion de projet", "chef de projet", "project management"],
                "analyse": ["analytique", "étude", "investigation"]
            }
        }
        
        sector_incompatibilities = {
            ("tech", "finance"): 0.3,
            ("tech", "comptabilité"): 0.2,
            ("finance", "tech"): 0.3,
            ("comptabilité", "tech"): 0.2,
            ("commercial", "technique"): 0.4,
            ("technique", "commercial"): 0.4
        }
        
        def check_synonyms(skill1: str, skill2: str, sector: str) -> float:
            """Vérifie si deux compétences sont synonymes"""
            sector_synonyms = skills_synonyms.get(sector, {})
            general_synonyms = skills_synonyms.get("general", {})
            all_synonyms = {**sector_synonyms, **general_synonyms}
            
            for key, synonyms in all_synonyms.items():
                if key in skill1:
                    if any(syn in skill2 for syn in synonyms) or skill2 in synonyms:
                        return 0.9
                if key in skill2:
                    if any(syn in skill1 for syn in synonyms) or skill1 in synonyms:
                        return 0.9
                if any(syn in skill1 for syn in synonyms) and any(syn in skill2 for syn in synonyms):
                    return 0.7
            return 0.0
        
        def calculate_sector_penalty(candidate_sector: str, job_sector: str) -> float:
            """Calcule la pénalité sectorielle"""
            if not candidate_sector or not job_sector:
                return 1.0
            
            candidate_lower = candidate_sector.lower()
            job_lower = job_sector.lower()
            
            # Correspondance exacte
            if candidate_lower == job_lower:
                return 1.0
            
            # Vérification des incompatibilités
            sector_pair = (candidate_lower, job_lower)
            if sector_pair in sector_incompatibilities:
                return sector_incompatibilities[sector_pair]
            
            # Secteurs compatibles
            finance_sectors = ["finance", "comptabilité", "audit", "contrôle"]
            tech_sectors = ["tech", "informatique", "développement"]
            
            candidate_finance = any(sector in candidate_lower for sector in finance_sectors)
            job_finance = any(sector in job_lower for sector in finance_sectors)
            candidate_tech = any(sector in candidate_lower for sector in tech_sectors)
            job_tech = any(sector in job_lower for sector in tech_sectors)
            
            if candidate_finance and job_finance:
                return 0.8
            if candidate_tech and job_tech:
                return 0.9
            
            return 0.6
        
        def detect_overqualification(candidate_data: Dict, job_data: Dict) -> float:
            """Détecte la surqualification"""
            candidate_level = candidate_data.get('professional_info', {}).get('hierarchical_level', '')
            job_level = job_data.get('requirements', {}).get('hierarchical_level', '')
            
            hierarchy_order = {
                'ENTRY': 0, 'JUNIOR': 1, 'SENIOR': 2,
                'MANAGER': 3, 'DIRECTOR': 4, 'EXECUTIVE': 5
            }
            
            candidate_rank = hierarchy_order.get(candidate_level, 0)
            job_rank = hierarchy_order.get(job_level, 0)
            level_gap = candidate_rank - job_rank
            
            if level_gap <= 0:
                return 1.0
            elif level_gap == 1:
                return 0.9
            elif level_gap == 2:
                return 0.7
            elif level_gap >= 3:
                return 0.5
            return 1.0
        
        def enhanced_calculate_semantic_score(self, candidate_data: Dict, job_data: Dict) -> float:
            """
            NOUVEAU: Algorithme sémantique amélioré V3.2
            Corrige les 4 problèmes identifiés lors des tests
            """
            try:
                # Extraction des données
                candidate_skills = candidate_data.get('skills', {}).get('technical_skills', [])
                candidate_sector = candidate_data.get('professional_info', {}).get('sector', '').lower()
                
                job_required_skills = job_data.get('requirements', {}).get('required_skills', [])
                job_preferred_skills = job_data.get('requirements', {}).get('preferred_skills', [])
                job_sector = job_data.get('job_info', {}).get('sector', '').lower()
                
                if not candidate_skills or not job_required_skills:
                    return 0.4
                
                # Calcul des matches avec synonymes
                required_matches = 0
                required_confidence_sum = 0.0
                
                for req_skill in job_required_skills:
                    req_skill_lower = req_skill.lower()
                    best_match_confidence = 0.0
                    
                    for cand_skill in candidate_skills:
                        cand_skill_lower = cand_skill.lower()
                        confidence = 0.0
                        
                        # Match exact
                        if req_skill_lower == cand_skill_lower:
                            confidence = 1.0
                        # Match partiel
                        elif req_skill_lower in cand_skill_lower or cand_skill_lower in req_skill_lower:
                            confidence = 0.8
                        # Match synonyme
                        else:
                            confidence = check_synonyms(req_skill_lower, cand_skill_lower, job_sector)
                        
                        best_match_confidence = max(best_match_confidence, confidence)
                    
                    if best_match_confidence > 0.5:  # Seuil de confiance
                        required_matches += 1
                    required_confidence_sum += best_match_confidence
                
                # Calcul des matches préférés
                preferred_matches = 0
                preferred_confidence_sum = 0.0
                
                if job_preferred_skills:
                    for pref_skill in job_preferred_skills:
                        pref_skill_lower = pref_skill.lower()
                        best_match_confidence = 0.0
                        
                        for cand_skill in candidate_skills:
                            cand_skill_lower = cand_skill.lower()
                            confidence = 0.0
                            
                            if pref_skill_lower == cand_skill_lower:
                                confidence = 1.0
                            elif pref_skill_lower in cand_skill_lower or cand_skill_lower in pref_skill_lower:
                                confidence = 0.8
                            else:
                                confidence = check_synonyms(pref_skill_lower, cand_skill_lower, job_sector)
                            
                            best_match_confidence = max(best_match_confidence, confidence)
                        
                        if best_match_confidence > 0.5:
                            preferred_matches += 1
                        preferred_confidence_sum += best_match_confidence
                
                # Score basé sur la couverture ET la confiance
                required_coverage = required_matches / len(job_required_skills)
                required_avg_confidence = required_confidence_sum / len(job_required_skills)
                required_score = (required_coverage * 0.6) + (required_avg_confidence * 0.4)
                
                preferred_score = 0.0
                if job_preferred_skills:
                    preferred_coverage = preferred_matches / len(job_preferred_skills)
                    preferred_avg_confidence = preferred_confidence_sum / len(job_preferred_skills)
                    preferred_score = (preferred_coverage * 0.6) + (preferred_avg_confidence * 0.4)
                
                # Score combiné (75% requis, 25% préféré)
                base_semantic_score = (required_score * 0.75) + (preferred_score * 0.25)
                
                # NOUVEAU: Application des pénalités
                sector_penalty = calculate_sector_penalty(candidate_sector, job_sector)
                overqualification_penalty = detect_overqualification(candidate_data, job_data)
                
                # Score final avec pénalités
                final_score = base_semantic_score * sector_penalty * overqualification_penalty
                
                # Bonus pour matches parfaits (résout le problème des 0.890)
                if required_matches == len(job_required_skills) and required_avg_confidence > 0.9:
                    final_score = min(final_score * 1.1, 1.0)  # Bonus de 10%
                
                # Log amélioré pour debugging
                self.logger.debug(f"Sémantique V3.2: base={base_semantic_score:.3f}, "
                                f"secteur={sector_penalty:.2f}, surqualif={overqualification_penalty:.2f}, "
                                f"final={final_score:.3f}")
                
                return final_score
                
            except Exception as e:
                self.logger.error(f"Erreur sémantique V3.2: {e}")
                return 0.3  # Score de sécurité
        
        return enhanced_calculate_semantic_score

    def apply_upgrade(self):
        """Applique la mise à niveau sémantique"""
        
        logger.info("🚀 DÉBUT MISE À NIVEAU SÉMANTIQUE V3.2")
        logger.info("=" * 50)
        
        # Test AVANT la mise à niveau
        logger.info("📋 Test AVANT mise à niveau (V3.1)")
        integrator_v31 = self.integration_module(
            cv_parser=self.cv_parser,
            job_parser=self.job_parser
        )
        
        result_before = integrator_v31.test_charlotte_darmon_vs_comptable()
        score_before = result_before['result'].total_score
        semantic_before = result_before['result'].scores_breakdown.get('semantic', 0)
        
        logger.info(f"   Score total V3.1: {score_before:.3f}")
        logger.info(f"   Score sémantique V3.1: {semantic_before:.3f}")
        
        # Application de la mise à niveau
        logger.info("\n🔧 Application des améliorations V3.2...")
        
        enhanced_method = self.create_enhanced_semantic_method()
        
        # Remplacement de la méthode
        self.integration_module.calculate_semantic_score = enhanced_method
        
        # Test APRÈS la mise à niveau
        logger.info("\n📋 Test APRÈS mise à niveau (V3.2)")
        integrator_v32 = self.integration_module(
            cv_parser=self.cv_parser,
            job_parser=self.job_parser
        )
        integrator_v32.version = "3.2.0"  # Mise à jour version
        
        result_after = integrator_v32.test_charlotte_darmon_vs_comptable()
        score_after = result_after['result'].total_score
        semantic_after = result_after['result'].scores_breakdown.get('semantic', 0)
        
        logger.info(f"   Score total V3.2: {score_after:.3f}")
        logger.info(f"   Score sémantique V3.2: {semantic_after:.3f}")
        
        # Validation du succès
        charlotte_maintained = abs(score_after - score_before) < 0.05  # Tolérance 5%
        
        logger.info("\n" + "=" * 50)
        logger.info("📊 RÉSULTATS DE LA MISE À NIVEAU")
        logger.info("=" * 50)
        
        if charlotte_maintained:
            logger.info("✅ Test Charlotte DARMON maintenu (objectif principal)")
            logger.info(f"   Écart: {abs(score_after - score_before):.3f}")
        else:
            logger.info("❌ Test Charlotte DARMON impacté")
            logger.info(f"   Écart: {abs(score_after - score_before):.3f}")
        
        logger.info(f"📈 Évolution sémantique: {semantic_before:.3f} → {semantic_after:.3f}")
        
        return {
            "success": charlotte_maintained,
            "score_before": score_before,
            "score_after": score_after,
            "semantic_before": semantic_before,
            "semantic_after": semantic_after,
            "integrator_v32": integrator_v32
        }

    def run_enhanced_tests(self, integrator_v32):
        """Lance les tests avec l'algorithme amélioré"""
        
        logger.info("\n🧪 TESTS AVEC ALGORITHME V3.2")
        logger.info("=" * 40)
        
        # Import du script de test
        try:
            from test_semantic_matching import SemanticTestSuite
            
            # Configuration de la suite de tests avec l'intégrateur V3.2
            test_suite = SemanticTestSuite(os.getenv('OPENAI_API_KEY'))
            test_suite.integrator = integrator_v32  # Utilisation de la V3.2
            
            # Exécution des tests
            results = test_suite.run_full_test_suite()
            
            logger.info(f"✅ Tests réussis V3.2: {results['successful_tests']}/{results['total_tests']} "
                      f"({results['success_rate']:.1f}%)")
            
            # Comparaison avec les résultats précédents (60%)
            improvement = results['success_rate'] - 60.0
            if improvement > 0:
                logger.info(f"📈 AMÉLIORATION: +{improvement:.1f}% par rapport à V3.1")
            else:
                logger.info(f"📉 Régression: {improvement:.1f}% par rapport à V3.1")
            
            return results
            
        except ImportError:
            logger.warning("⚠️ Script de test non trouvé, tests manuels uniquement")
            return None

def main():
    """Fonction principale"""
    
    print("🚀 NEXTVISION V3.2 - MISE À NIVEAU SÉMANTIQUE")
    print("=" * 50)
    
    try:
        # Initialisation du gestionnaire
        upgrade_manager = SemanticUpgradeManager()
        
        # Application de la mise à niveau
        upgrade_result = upgrade_manager.apply_upgrade()
        
        if upgrade_result["success"]:
            print("\n✅ MISE À NIVEAU RÉUSSIE")
            print("Objectif Charlotte DARMON maintenu")
            
            # Tests étendus avec V3.2
            test_results = upgrade_manager.run_enhanced_tests(upgrade_result["integrator_v32"])
            
            if test_results and test_results["success_rate"] >= 80:
                print("🎯 SUCCÈS COMPLET: Système V3.2 opérationnel")
                print(f"   Performance: {test_results['success_rate']:.1f}% de réussite")
            elif test_results:
                print("⚠️ AMÉLIORATION PARTIELLE")
                print(f"   Performance: {test_results['success_rate']:.1f}% de réussite")
                print("   Optimisations supplémentaires recommandées")
            
            # Sauvegarde de la version améliorée
            logger.info("\n💾 Pour sauvegarder définitivement:")
            logger.info("   1. git add gpt_modules/")
            logger.info("   2. git commit -m 'feat: Algorithme sémantique V3.2'")
            logger.info("   3. git push origin feature/gpt-integration-v31")
            
        else:
            print("\n❌ MISE À NIVEAU ÉCHOUÉE")
            print("Objectif Charlotte DARMON non maintenu")
            print("Révision des paramètres nécessaire")
    
    except Exception as e:
        logger.error(f"❌ Erreur lors de la mise à niveau: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
