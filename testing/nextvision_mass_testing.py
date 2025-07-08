#!/usr/bin/env python3
"""
Système de Test Massif pour Nextvision v2.0
Validateur à grande échelle : 69 CVs × 34 FDPs = 2,346 combinaisons
"""

import os
import json
import time
import random
import requests
import asyncio
import aiohttp
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import logging

# Configuration
API_BASE_URL = "http://localhost:8000"
CV_DIRECTORY = "/Users/baptistecomas/Desktop/CV TEST"
FDP_DIRECTORY = "/Users/baptistecomas/Desktop/FDP TEST"
RESULTS_DIR = "nextvision_test_results"
MAX_CONCURRENT_REQUESTS = 10

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CandidateProfile:
    """Profil candidat simulé avec questionnaire"""
    listening_reason: str  # "career_change", "better_salary", "new_challenge", "layoff", "relocation"
    salary_expectation: int
    location_flexibility: str  # "same_city", "same_region", "nationwide", "international"
    experience_level: str  # "junior", "intermediate", "senior", "expert"
    work_mode_preference: str  # "office", "remote", "hybrid"
    availability: str  # "immediate", "1_month", "3_months", "6_months"

@dataclass
class CompanyProfile:
    """Profil entreprise simulé avec questionnaire"""
    urgency_level: str  # "immediate", "high", "medium", "low"
    budget_flexibility: str  # "strict", "flexible", "very_flexible"
    experience_requirement: str  # "junior_ok", "intermediate_min", "senior_only", "expert_required"
    location_requirement: str  # "strict_office", "hybrid_ok", "remote_ok", "location_flexible"
    team_size: str  # "startup", "small_team", "medium_team", "large_team"
    company_stage: str  # "startup", "scale_up", "established", "enterprise"

class QuestionnaireSimulator:
    """Simulateur de réponses questionnaires réalistes"""
    
    LISTENING_REASONS = {
        "career_change": 0.25,
        "better_salary": 0.30,
        "new_challenge": 0.20,
        "layoff": 0.15,
        "relocation": 0.10
    }
    
    URGENCY_LEVELS = {
        "immediate": 0.20,
        "high": 0.35,
        "medium": 0.30,
        "low": 0.15
    }
    
    def generate_candidate_profile(self) -> CandidateProfile:
        """Génère un profil candidat réaliste"""
        listening_reason = random.choices(
            list(self.LISTENING_REASONS.keys()),
            weights=list(self.LISTENING_REASONS.values())
        )[0]
        
        # Ajustement des attentes selon la raison d'écoute
        if listening_reason == "better_salary":
            salary_base = random.randint(45000, 80000)
            salary_multiplier = random.uniform(1.2, 1.5)
        elif listening_reason == "layoff":
            salary_base = random.randint(35000, 60000)
            salary_multiplier = random.uniform(0.9, 1.1)
        else:
            salary_base = random.randint(40000, 70000)
            salary_multiplier = random.uniform(1.0, 1.3)
        
        return CandidateProfile(
            listening_reason=listening_reason,
            salary_expectation=int(salary_base * salary_multiplier),
            location_flexibility=random.choice([
                "same_city", "same_region", "nationwide", "international"
            ]),
            experience_level=random.choice([
                "junior", "intermediate", "senior", "expert"
            ]),
            work_mode_preference=random.choice([
                "office", "remote", "hybrid"
            ]),
            availability=random.choice([
                "immediate", "1_month", "3_months", "6_months"
            ])
        )
    
    def generate_company_profile(self) -> CompanyProfile:
        """Génère un profil entreprise réaliste"""
        urgency = random.choices(
            list(self.URGENCY_LEVELS.keys()),
            weights=list(self.URGENCY_LEVELS.values())
        )[0]
        
        # Corrélation urgence/flexibilité
        if urgency in ["immediate", "high"]:
            budget_flexibility = random.choice(["flexible", "very_flexible", "strict"])
            location_requirement = random.choice(["hybrid_ok", "remote_ok", "location_flexible"])
        else:
            budget_flexibility = random.choice(["strict", "flexible"])
            location_requirement = random.choice(["strict_office", "hybrid_ok"])
        
        return CompanyProfile(
            urgency_level=urgency,
            budget_flexibility=budget_flexibility,
            experience_requirement=random.choice([
                "junior_ok", "intermediate_min", "senior_only", "expert_required"
            ]),
            location_requirement=location_requirement,
            team_size=random.choice([
                "startup", "small_team", "medium_team", "large_team"
            ]),
            company_stage=random.choice([
                "startup", "scale_up", "established", "enterprise"
            ])
        )

class FileManager:
    """Gestionnaire de fichiers CVs et FDPs"""
    
    def __init__(self, cv_dir: str, fdp_dir: str):
        self.cv_dir = Path(cv_dir)
        self.fdp_dir = Path(fdp_dir)
    
    def get_cv_files(self) -> List[Path]:
        """Récupère tous les fichiers CV"""
        extensions = ['*.pdf', '*.doc', '*.docx']
        files = []
        for ext in extensions:
            files.extend(self.cv_dir.glob(ext))
        return sorted(files)
    
    def get_fdp_files(self) -> List[Path]:
        """Récupère tous les fichiers FDP"""
        extensions = ['*.pdf', '*.doc', '*.docx']
        files = []
        for ext in extensions:
            files.extend(self.fdp_dir.glob(ext))
        return sorted(files)

class APITester:
    """Testeur API avec gestion des performances"""
    
    def __init__(self, base_url: str, max_concurrent: int = 10):
        self.base_url = base_url
        self.max_concurrent = max_concurrent
        self.session = requests.Session()
    
    def test_api_health(self) -> bool:
        """Vérifie si l'API est accessible"""
        try:
            response = self.session.get(f"{self.base_url}/docs")
            return response.status_code == 200
        except:
            return False
    
    def single_match_test(self, cv_file: Path, fdp_file: Path, 
                         candidate_profile: CandidateProfile,
                         company_profile: CompanyProfile) -> Dict[str, Any]:
        """Test de matching unique"""
        start_time = time.time()
        
        try:
            # Préparation des données
            with open(cv_file, 'rb') as cv_f, open(fdp_file, 'rb') as fdp_f:
                files = {
                    'cv_file': (cv_file.name, cv_f, 'application/pdf'),
                    'fdp_file': (fdp_file.name, fdp_f, 'application/pdf')
                }
                
                data = {
                    'candidate_questionnaire': json.dumps(asdict(candidate_profile)),
                    'company_questionnaire': json.dumps(asdict(company_profile))
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/v2/matching/bidirectional",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'status': 'success',
                    'cv_file': cv_file.name,
                    'fdp_file': fdp_file.name,
                    'execution_time': execution_time,
                    'score': result.get('final_score', 0),
                    'components': result.get('score_components', {}),
                    'candidate_profile': asdict(candidate_profile),
                    'company_profile': asdict(company_profile),
                    'raw_response': result
                }
            else:
                return {
                    'status': 'error',
                    'cv_file': cv_file.name,
                    'fdp_file': fdp_file.name,
                    'execution_time': execution_time,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'candidate_profile': asdict(candidate_profile),
                    'company_profile': asdict(company_profile)
                }
                
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'status': 'error',
                'cv_file': cv_file.name,
                'fdp_file': fdp_file.name,
                'execution_time': execution_time,
                'error': str(e),
                'candidate_profile': asdict(candidate_profile),
                'company_profile': asdict(company_profile)
            }

class MassTestRunner:
    """Orchestrateur des tests massifs"""
    
    def __init__(self):
        self.file_manager = FileManager(CV_DIRECTORY, FDP_DIRECTORY)
        self.api_tester = APITester(API_BASE_URL, MAX_CONCURRENT_REQUESTS)
        self.questionnaire_sim = QuestionnaireSimulator()
        self.results = []
        
        # Création du dossier résultats
        self.results_dir = Path(RESULTS_DIR)
        self.results_dir.mkdir(exist_ok=True)
    
    def run_mass_test(self, max_combinations: int = None) -> List[Dict[str, Any]]:
        """Lance le test massif"""
        logger.info("🚀 Démarrage du test massif Nextvision v2.0")
        
        # Vérification API
        if not self.api_tester.test_api_health():
            logger.error("❌ API non accessible sur " + API_BASE_URL)
            return []
        
        logger.info("✅ API accessible")
        
        # Récupération des fichiers
        cv_files = self.file_manager.get_cv_files()
        fdp_files = self.file_manager.get_fdp_files()
        
        logger.info(f"📄 {len(cv_files)} CVs trouvés")
        logger.info(f"📋 {len(fdp_files)} FDPs trouvées")
        
        total_combinations = len(cv_files) * len(fdp_files)
        if max_combinations:
            total_combinations = min(total_combinations, max_combinations)
        
        logger.info(f"🎯 {total_combinations} combinaisons à tester")
        
        # Génération des combinaisons
        combinations = []
        count = 0
        for cv_file in cv_files:
            for fdp_file in fdp_files:
                if max_combinations and count >= max_combinations:
                    break
                
                candidate_profile = self.questionnaire_sim.generate_candidate_profile()
                company_profile = self.questionnaire_sim.generate_company_profile()
                
                combinations.append((cv_file, fdp_file, candidate_profile, company_profile))
                count += 1
            
            if max_combinations and count >= max_combinations:
                break
        
        # Exécution des tests avec ThreadPool
        logger.info("⚡ Démarrage des tests parallèles...")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS) as executor:
            results = list(executor.map(self._execute_single_test, combinations))
        
        total_time = time.time() - start_time
        
        # Filtrage des résultats réussis
        successful_results = [r for r in results if r['status'] == 'success']
        failed_results = [r for r in results if r['status'] == 'error']
        
        logger.info(f"✅ Tests terminés en {total_time:.2f}s")
        logger.info(f"🎉 {len(successful_results)} succès / {len(results)} total")
        logger.info(f"❌ {len(failed_results)} échecs")
        
        if successful_results:
            avg_score = np.mean([r['score'] for r in successful_results])
            avg_time = np.mean([r['execution_time'] for r in successful_results])
            throughput = len(successful_results) / total_time
            
            logger.info(f"📊 Score moyen: {avg_score:.3f}")
            logger.info(f"⏱️  Temps moyen: {avg_time:.3f}s")
            logger.info(f"🚀 Débit: {throughput:.1f} matchs/s")
        
        self.results = results
        return results
    
    def _execute_single_test(self, combination: Tuple) -> Dict[str, Any]:
        """Exécute un test unique"""
        cv_file, fdp_file, candidate_profile, company_profile = combination
        return self.api_tester.single_match_test(cv_file, fdp_file, candidate_profile, company_profile)

class ResultsAnalyzer:
    """Analyseur de résultats avec statistiques avancées"""
    
    def __init__(self, results: List[Dict[str, Any]]):
        self.results = results
        self.successful_results = [r for r in results if r['status'] == 'success']
        self.df = pd.DataFrame(self.successful_results) if self.successful_results else pd.DataFrame()
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Génère un rapport complet"""
        if self.df.empty:
            return {"error": "Aucun résultat réussi à analyser"}
        
        report = {
            "overview": self._generate_overview(),
            "performance_stats": self._analyze_performance(),
            "score_analysis": self._analyze_scores(),
            "questionnaire_impact": self._analyze_questionnaire_impact(),
            "consistency_check": self._check_consistency(),
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_overview(self) -> Dict[str, Any]:
        """Vue d'ensemble des résultats"""
        total_tests = len(self.results)
        successful_tests = len(self.successful_results)
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": f"{success_rate:.2f}%",
            "unique_cvs": self.df['cv_file'].nunique() if not self.df.empty else 0,
            "unique_fdps": self.df['fdp_file'].nunique() if not self.df.empty else 0
        }
    
    def _analyze_performance(self) -> Dict[str, Any]:
        """Analyse des performances"""
        if self.df.empty:
            return {}
        
        execution_times = self.df['execution_time']
        
        return {
            "avg_execution_time": f"{execution_times.mean():.3f}s",
            "min_execution_time": f"{execution_times.min():.3f}s",
            "max_execution_time": f"{execution_times.max():.3f}s",
            "p95_execution_time": f"{execution_times.quantile(0.95):.3f}s",
            "total_processing_time": f"{execution_times.sum():.2f}s"
        }
    
    def _analyze_scores(self) -> Dict[str, Any]:
        """Analyse des scores"""
        if self.df.empty:
            return {}
        
        scores = self.df['score']
        
        return {
            "mean_score": f"{scores.mean():.3f}",
            "median_score": f"{scores.median():.3f}",
            "std_score": f"{scores.std():.3f}",
            "min_score": f"{scores.min():.3f}",
            "max_score": f"{scores.max():.3f}",
            "score_distribution": {
                "excellent (>0.8)": f"{(scores > 0.8).sum()} ({(scores > 0.8).mean()*100:.1f}%)",
                "good (0.6-0.8)": f"{((scores >= 0.6) & (scores <= 0.8)).sum()} ({((scores >= 0.6) & (scores <= 0.8)).mean()*100:.1f}%)",
                "average (0.4-0.6)": f"{((scores >= 0.4) & (scores < 0.6)).sum()} ({((scores >= 0.4) & (scores < 0.6)).mean()*100:.1f}%)",
                "poor (<0.4)": f"{(scores < 0.4).sum()} ({(scores < 0.4).mean()*100:.1f}%)"
            }
        }
    
    def _analyze_questionnaire_impact(self) -> Dict[str, Any]:
        """Analyse l'impact des questionnaires"""
        if self.df.empty:
            return {}
        
        analysis = {}
        
        # Impact des raisons d'écoute candidat
        listening_reasons = self.df['candidate_profile'].apply(lambda x: x['listening_reason'])
        analysis['listening_reason_impact'] = listening_reasons.value_counts().to_dict()
        
        # Impact de l'urgence entreprise
        urgency_levels = self.df['company_profile'].apply(lambda x: x['urgency_level'])
        analysis['urgency_impact'] = urgency_levels.value_counts().to_dict()
        
        # Corrélations score/questionnaire
        for reason in listening_reasons.unique():
            mask = listening_reasons == reason
            avg_score = self.df[mask]['score'].mean()
            analysis[f'avg_score_{reason}'] = f"{avg_score:.3f}"
        
        return analysis
    
    def _check_consistency(self) -> Dict[str, Any]:
        """Vérification de cohérence"""
        if self.df.empty:
            return {}
        
        consistency_checks = {}
        
        # Vérification variance par CV
        cv_variance = self.df.groupby('cv_file')['score'].std().mean()
        consistency_checks['cv_score_variance'] = f"{cv_variance:.3f}"
        
        # Vérification variance par FDP
        fdp_variance = self.df.groupby('fdp_file')['score'].std().mean()
        consistency_checks['fdp_score_variance'] = f"{fdp_variance:.3f}"
        
        # Cohérence temporelle
        time_consistency = self.df['execution_time'].std()
        consistency_checks['time_consistency'] = f"{time_consistency:.3f}"
        
        return consistency_checks
    
    def _generate_recommendations(self) -> List[str]:
        """Génère des recommandations"""
        recommendations = []
        
        if self.df.empty:
            recommendations.append("❌ Aucune donnée à analyser - vérifier la configuration API")
            return recommendations
        
        # Analyse des performances
        avg_time = self.df['execution_time'].mean()
        if avg_time > 1.0:
            recommendations.append(f"⚠️ Temps d'exécution élevé ({avg_time:.3f}s) - optimiser les performances")
        else:
            recommendations.append(f"✅ Performances excellentes ({avg_time:.3f}s par match)")
        
        # Analyse des scores
        avg_score = self.df['score'].mean()
        if avg_score > 0.8:
            recommendations.append(f"✅ Scores excellents (moyenne: {avg_score:.3f})")
        elif avg_score > 0.6:
            recommendations.append(f"⚠️ Scores moyens (moyenne: {avg_score:.3f}) - ajuster les pondérations")
        else:
            recommendations.append(f"❌ Scores faibles (moyenne: {avg_score:.3f}) - revoir l'algorithme")
        
        # Analyse de la variance
        score_std = self.df['score'].std()
        if score_std < 0.1:
            recommendations.append("⚠️ Variance des scores faible - vérifier la diversité des profils")
        elif score_std > 0.3:
            recommendations.append("⚠️ Variance des scores élevée - vérifier la stabilité de l'algorithme")
        else:
            recommendations.append("✅ Variance des scores appropriée")
        
        return recommendations
    
    def save_results(self, output_dir: Path):
        """Sauvegarde les résultats et analyses"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sauvegarde des résultats bruts
        raw_file = output_dir / f"raw_results_{timestamp}.json"
        with open(raw_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Sauvegarde du rapport d'analyse
        report = self.generate_comprehensive_report()
        report_file = output_dir / f"analysis_report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Sauvegarde CSV pour analyse externe
        if not self.df.empty:
            csv_file = output_dir / f"results_{timestamp}.csv"
            self.df.to_csv(csv_file, index=False)
        
        logger.info(f"📊 Résultats sauvegardés dans {output_dir}")
        return raw_file, report_file

def main():
    """Fonction principale de test"""
    print("🚀 NEXTVISION v2.0 - SYSTÈME DE TEST MASSIF")
    print("=" * 50)
    
    # Initialisation
    runner = MassTestRunner()
    
    # Configuration du test
    max_combinations = input("Nombre max de combinaisons (Enter pour toutes): ")
    max_combinations = int(max_combinations) if max_combinations.strip() else None
    
    print(f"\n🎯 Lancement du test avec {max_combinations or 'toutes les'} combinaisons...")
    
    # Exécution
    results = runner.run_mass_test(max_combinations)
    
    if not results:
        print("❌ Aucun résultat - vérifier la configuration")
        return
    
    # Analyse
    print("\n📊 Analyse des résultats...")
    analyzer = ResultsAnalyzer(results)
    report = analyzer.generate_comprehensive_report()
    
    # Affichage du rapport
    print("\n" + "="*50)
    print("📈 RAPPORT D'ANALYSE NEXTVISION v2.0")
    print("="*50)
    
    if "error" in report:
        print(f"❌ {report['error']}")
        return
    
    # Vue d'ensemble
    overview = report['overview']
    print(f"\n📋 VUE D'ENSEMBLE:")
    print(f"   • Tests: {overview['successful_tests']}/{overview['total_tests']} ({overview['success_rate']})")
    print(f"   • CVs uniques: {overview['unique_cvs']}")
    print(f"   • FDPs uniques: {overview['unique_fdps']}")
    
    # Performances
    perf = report['performance_stats']
    print(f"\n⚡ PERFORMANCES:")
    print(f"   • Temps moyen: {perf['avg_execution_time']}")
    print(f"   • P95: {perf['p95_execution_time']}")
    print(f"   • Range: {perf['min_execution_time']} - {perf['max_execution_time']}")
    
    # Scores
    scores = report['score_analysis']
    print(f"\n🎯 SCORES:")
    print(f"   • Moyenne: {scores['mean_score']} (±{scores['std_score']})")
    print(f"   • Range: {scores['min_score']} - {scores['max_score']}")
    print(f"   • Distribution:")
    for level, count in scores['score_distribution'].items():
        print(f"     - {level}: {count}")
    
    # Recommandations
    print(f"\n💡 RECOMMANDATIONS:")
    for rec in report['recommendations']:
        print(f"   {rec}")
    
    # Sauvegarde
    raw_file, report_file = analyzer.save_results(runner.results_dir)
    print(f"\n💾 Résultats sauvegardés:")
    print(f"   • Données brutes: {raw_file}")
    print(f"   • Rapport: {report_file}")
    
    print("\n🎉 Test massif terminé avec succès!")

if __name__ == "__main__":
    main()