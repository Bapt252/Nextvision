#!/usr/bin/env python3
"""
Analyseur Avancé & Monitoring pour Nextvision v2.0
Analyses comparatives, monitoring en temps réel, et optimisations
"""

import json
import time
import asyncio
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import threading
import queue
import psutil
import matplotlib.pyplot as plt
from collections import deque, defaultdict
import logging
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configuration avancée
MONITORING_INTERVAL = 5  # secondes
MAX_HISTORY_SIZE = 1000
ALERT_THRESHOLDS = {
    'avg_response_time': 2.0,  # secondes
    'error_rate': 0.05,  # 5%
    'score_variance': 0.3,
    'memory_usage': 0.8  # 80%
}

@dataclass
class PerformanceMetrics:
    """Métriques de performance en temps réel"""
    timestamp: datetime
    response_time: float
    score: Optional[float] = None
    error_count: int = 0
    success_count: int = 0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    api_status: str = "unknown"

@dataclass
class ComparisonScenario:
    """Scénario de comparaison pour A/B testing"""
    name: str
    description: str
    candidate_profiles: List[Dict[str, Any]]
    company_profiles: List[Dict[str, Any]]
    expected_score_range: Tuple[float, float]
    test_count: int = 100

class RealTimeMonitor:
    """Moniteur temps réel de l'API Nextvision"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.metrics_history = deque(maxlen=MAX_HISTORY_SIZE)
        self.alerts_log = []
        self.is_monitoring = False
        self.monitor_thread = None
        self.metrics_queue = queue.Queue()
        
        # Configuration logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def start_monitoring(self):
        """Démarre le monitoring en arrière-plan"""
        if self.is_monitoring:
            self.logger.warning("Le monitoring est déjà actif")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("🔍 Monitoring démarré")
    
    def stop_monitoring(self):
        """Arrête le monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("🛑 Monitoring arrêté")
    
    def _monitor_loop(self):
        """Boucle principale de monitoring"""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                self._check_alerts(metrics)
                time.sleep(MONITORING_INTERVAL)
            except Exception as e:
                self.logger.error(f"Erreur monitoring: {e}")
                time.sleep(MONITORING_INTERVAL)
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """Collecte les métriques système et API"""
        start_time = time.time()
        
        # Test de santé API
        try:
            response = requests.get(f"{self.api_url}/docs", timeout=5)
            api_status = "healthy" if response.status_code == 200 else "unhealthy"
            response_time = time.time() - start_time
        except:
            api_status = "unreachable"
            response_time = float('inf')
        
        # Métriques système
        memory_usage = psutil.virtual_memory().percent / 100
        cpu_usage = psutil.cpu_percent(interval=1) / 100
        
        return PerformanceMetrics(
            timestamp=datetime.now(),
            response_time=response_time,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            api_status=api_status
        )
    
    def _check_alerts(self, metrics: PerformanceMetrics):
        """Vérifie les seuils d'alerte"""
        alerts = []
        
        if metrics.response_time > ALERT_THRESHOLDS['avg_response_time']:
            alerts.append(f"⚠️ Temps de réponse élevé: {metrics.response_time:.3f}s")
        
        if metrics.memory_usage > ALERT_THRESHOLDS['memory_usage']:
            alerts.append(f"⚠️ Utilisation mémoire élevée: {metrics.memory_usage:.1%}")
        
        if metrics.api_status != "healthy":
            alerts.append(f"❌ API indisponible: {metrics.api_status}")
        
        for alert in alerts:
            self.logger.warning(alert)
            self.alerts_log.append({
                'timestamp': metrics.timestamp,
                'message': alert,
                'metrics': metrics
            })
    
    def get_current_status(self) -> Dict[str, Any]:
        """Retourne le statut actuel"""
        if not self.metrics_history:
            return {"status": "no_data"}
        
        recent_metrics = list(self.metrics_history)[-10:]  # 10 dernières mesures
        
        return {
            "status": "monitoring" if self.is_monitoring else "stopped",
            "last_update": recent_metrics[-1].timestamp.isoformat(),
            "avg_response_time": np.mean([m.response_time for m in recent_metrics if m.response_time != float('inf')]),
            "api_status": recent_metrics[-1].api_status,
            "memory_usage": recent_metrics[-1].memory_usage,
            "cpu_usage": recent_metrics[-1].cpu_usage,
            "alerts_count": len(self.alerts_log),
            "monitoring_duration": len(self.metrics_history) * MONITORING_INTERVAL
        }
    
    def export_monitoring_data(self, output_file: str):
        """Exporte les données de monitoring"""
        data = []
        for metric in self.metrics_history:
            data.append({
                'timestamp': metric.timestamp.isoformat(),
                'response_time': metric.response_time,
                'memory_usage': metric.memory_usage,
                'cpu_usage': metric.cpu_usage,
                'api_status': metric.api_status
            })
        
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
        self.logger.info(f"📊 Données exportées vers {output_file}")

class ScenarioComparator:
    """Comparateur de scénarios pour A/B testing"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.scenarios = {}
        self.comparison_results = {}
    
    def add_scenario(self, scenario: ComparisonScenario):
        """Ajoute un scénario de test"""
        self.scenarios[scenario.name] = scenario
    
    def create_default_scenarios(self):
        """Crée des scénarios de test par défaut"""
        # Scénario 1: Candidats motivés par le salaire
        salary_focused = ComparisonScenario(
            name="salary_focused",
            description="Candidats motivés principalement par le salaire",
            candidate_profiles=[{
                'listening_reason': 'better_salary',
                'salary_expectation': 60000,
                'location_flexibility': 'same_region',
                'experience_level': 'intermediate'
            }] * 20,
            company_profiles=[{
                'urgency_level': 'high',
                'budget_flexibility': 'flexible',
                'experience_requirement': 'intermediate_min'
            }] * 20,
            expected_score_range=(0.7, 0.9),
            test_count=50
        )
        
        # Scénario 2: Startups urgentes
        startup_urgent = ComparisonScenario(
            name="startup_urgent",
            description="Startups avec besoins urgents",
            candidate_profiles=[{
                'listening_reason': 'new_challenge',
                'salary_expectation': 50000,
                'location_flexibility': 'nationwide',
                'experience_level': 'senior',
                'work_mode_preference': 'hybrid',
                'availability': 'immediate'
            }] * 20,
            company_profiles=[{
                'urgency_level': 'immediate',
                'budget_flexibility': 'very_flexible',
                'experience_requirement': 'senior_only',
                'company_stage': 'startup',
                'team_size': 'small_team'
            }] * 20,
            expected_score_range=(0.8, 0.95),
            test_count=50
        )
        
        # Scénario 3: Reconversion professionnelle
        career_change = ComparisonScenario(
            name="career_change",
            description="Candidats en reconversion avec entreprises flexibles",
            candidate_profiles=[{
                'listening_reason': 'career_change',
                'salary_expectation': 40000,
                'location_flexibility': 'same_city',
                'experience_level': 'junior',
                'availability': '3_months'
            }] * 20,
            company_profiles=[{
                'urgency_level': 'medium',
                'budget_flexibility': 'strict',
                'experience_requirement': 'junior_ok',
                'company_stage': 'established'
            }] * 20,
            expected_score_range=(0.5, 0.75),
            test_count=50
        )
        
        # Ajout des scénarios
        for scenario in [salary_focused, startup_urgent, career_change]:
            self.add_scenario(scenario)
    
    def run_scenario_comparison(self, cv_file: str, fdp_file: str) -> Dict[str, Any]:
        """Execute la comparaison de tous les scénarios"""
        results = {}
        
        for scenario_name, scenario in self.scenarios.items():
            print(f"🧪 Test du scénario: {scenario.description}")
            
            scenario_results = []
            
            # Test de chaque combinaison profil candidat/entreprise
            for i in range(min(len(scenario.candidate_profiles), len(scenario.company_profiles))):
                candidate_profile = scenario.candidate_profiles[i]
                company_profile = scenario.company_profiles[i]
                
                try:
                    result = self._test_single_combination(
                        cv_file, fdp_file, candidate_profile, company_profile
                    )
                    scenario_results.append(result)
                except Exception as e:
                    print(f"❌ Erreur test {scenario_name}: {e}")
                    continue
            
            # Analyse des résultats du scénario
            if scenario_results:
                scores = [r['score'] for r in scenario_results if r['status'] == 'success']
                times = [r['execution_time'] for r in scenario_results if r['status'] == 'success']
                
                results[scenario_name] = {
                    'description': scenario.description,
                    'total_tests': len(scenario_results),
                    'successful_tests': len(scores),
                    'avg_score': np.mean(scores) if scores else 0,
                    'std_score': np.std(scores) if scores else 0,
                    'avg_time': np.mean(times) if times else 0,
                    'score_range': (min(scores), max(scores)) if scores else (0, 0),
                    'expected_range': scenario.expected_score_range,
                    'meets_expectations': self._check_expectations(scores, scenario.expected_score_range),
                    'raw_results': scenario_results
                }
            
        self.comparison_results = results
        return results
    
    def _test_single_combination(self, cv_file: str, fdp_file: str, 
                                candidate_profile: Dict, company_profile: Dict) -> Dict[str, Any]:
        """Test une combinaison unique"""
        start_time = time.time()
        
        try:
            with open(cv_file, 'rb') as cv_f, open(fdp_file, 'rb') as fdp_f:
                files = {
                    'cv_file': (Path(cv_file).name, cv_f, 'application/pdf'),
                    'fdp_file': (Path(fdp_file).name, fdp_f, 'application/pdf')
                }
                
                data = {
                    'candidate_questionnaire': json.dumps(candidate_profile),
                    'company_questionnaire': json.dumps(company_profile)
                }
                
                response = requests.post(
                    f"{self.api_url}/api/v2/matching/bidirectional",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'status': 'success',
                    'score': result.get('final_score', 0),
                    'execution_time': execution_time,
                    'components': result.get('score_components', {}),
                    'candidate_profile': candidate_profile,
                    'company_profile': company_profile
                }
            else:
                return {
                    'status': 'error',
                    'error': f"HTTP {response.status_code}",
                    'execution_time': execution_time
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'execution_time': time.time() - start_time
            }
    
    def _check_expectations(self, scores: List[float], expected_range: Tuple[float, float]) -> bool:
        """Vérifie si les scores respectent les attentes"""
        if not scores:
            return False
        
        avg_score = np.mean(scores)
        return expected_range[0] <= avg_score <= expected_range[1]
    
    def generate_comparison_report(self) -> str:
        """Génère un rapport de comparaison"""
        if not self.comparison_results:
            return "❌ Aucune comparaison effectuée"
        
        report = f"""
🧪 RAPPORT DE COMPARAISON SCÉNARIOS NEXTVISION v2.0
{'='*60}

"""
        
        for scenario_name, results in self.comparison_results.items():
            status_icon = "✅" if results['meets_expectations'] else "⚠️"
            
            report += f"""
{status_icon} SCÉNARIO: {scenario_name.upper()}
Description: {results['description']}
─────────────────────────────────────────────────────────────
• Tests réussis: {results['successful_tests']}/{results['total_tests']}
• Score moyen: {results['avg_score']:.3f} ± {results['std_score']:.3f}
• Range observé: {results['score_range'][0]:.3f} - {results['score_range'][1]:.3f}
• Range attendu: {results['expected_range'][0]:.3f} - {results['expected_range'][1]:.3f}
• Temps moyen: {results['avg_time']:.3f}s
• Attentes respectées: {'Oui' if results['meets_expectations'] else 'Non'}

"""
        
        # Analyse comparative
        report += f"""
📊 ANALYSE COMPARATIVE:
─────────────────────────────────────────────────────────────
"""
        
        # Classement par score moyen
        ranked_scenarios = sorted(
            self.comparison_results.items(), 
            key=lambda x: x[1]['avg_score'], 
            reverse=True
        )
        
        report += "🏆 CLASSEMENT PAR SCORE MOYEN:\n"
        for i, (name, results) in enumerate(ranked_scenarios, 1):
            report += f"{i}. {name}: {results['avg_score']:.3f}\n"
        
        # Recommandations
        report += f"\n💡 RECOMMANDATIONS:\n"
        
        best_scenario = ranked_scenarios[0]
        worst_scenario = ranked_scenarios[-1]
        
        report += f"✅ Meilleur scénario: {best_scenario[0]} (score: {best_scenario[1]['avg_score']:.3f})\n"
        report += f"❌ Scénario à améliorer: {worst_scenario[0]} (score: {worst_scenario[1]['avg_score']:.3f})\n"
        
        # Analyse de la variance
        avg_variance = np.mean([r['std_score'] for r in self.comparison_results.values()])
        if avg_variance > 0.2:
            report += f"⚠️ Variance élevée détectée ({avg_variance:.3f}) - vérifier la cohérence\n"
        else:
            report += f"✅ Variance acceptable ({avg_variance:.3f}) - algorithme stable\n"
        
        return report

class AdvancedAnalytics:
    """Analytics avancées pour optimisation"""
    
    @staticmethod
    def detect_score_anomalies(scores: List[float], threshold: float = 2.0) -> List[int]:
        """Détecte les anomalies dans les scores using Z-score"""
        if len(scores) < 3:
            return []
        
        z_scores = np.abs(stats.zscore(scores))
        anomaly_indices = np.where(z_scores > threshold)[0]
        return anomaly_indices.tolist()
    
    @staticmethod
    def analyze_score_patterns(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse les patterns dans les scores"""
        df = pd.DataFrame(results)
        
        if df.empty or 'score' not in df.columns:
            return {"error": "Données insuffisantes"}
        
        scores = df['score'].values
        
        # Tests statistiques
        normality_test = stats.shapiro(scores) if len(scores) > 3 else None
        
        # Autocorrélation (pour détecter des patterns temporels)
        autocorr = np.corrcoef(scores[:-1], scores[1:])[0, 1] if len(scores) > 1 else 0
        
        # Analyse de tendance
        x = np.arange(len(scores))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, scores)
        
        return {
            "total_scores": len(scores),
            "mean": float(np.mean(scores)),
            "std": float(np.std(scores)),
            "skewness": float(stats.skew(scores)),
            "kurtosis": float(stats.kurtosis(scores)),
            "normality_p_value": float(normality_test.pvalue) if normality_test else None,
            "autocorrelation": float(autocorr),
            "trend_slope": float(slope),
            "trend_significance": float(p_value),
            "anomalies_count": len(AdvancedAnalytics.detect_score_anomalies(scores)),
            "percentiles": {
                "p10": float(np.percentile(scores, 10)),
                "p25": float(np.percentile(scores, 25)),
                "p50": float(np.percentile(scores, 50)),
                "p75": float(np.percentile(scores, 75)),
                "p90": float(np.percentile(scores, 90))
            }
        }
    
    @staticmethod
    def performance_regression_analysis(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse de régression des performances"""
        df = pd.DataFrame(results)
        
        if df.empty or len(df) < 10:
            return {"error": "Données insuffisantes pour régression"}
        
        # Variables pour régression
        X = np.column_stack([
            np.arange(len(df)),  # ordre temporel
            df['execution_time'].fillna(df['execution_time'].mean()),
        ])
        y = df['score'].values
        
        # Régression linéaire multiple
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score
        
        reg = LinearRegression()
        reg.fit(X, y)
        y_pred = reg.predict(X)
        
        return {
            "r2_score": float(r2_score(y, y_pred)),
            "coefficients": {
                "temporal_trend": float(reg.coef_[0]),
                "execution_time_impact": float(reg.coef_[1]),
                "intercept": float(reg.intercept_)
            },
            "performance_correlation": float(np.corrcoef(df['execution_time'], df['score'])[0, 1])
        }

def main():
    """Interface principale pour analyses avancées"""
    print("🔬 NEXTVISION v2.0 - ANALYSEUR AVANCÉ & MONITORING")
    print("=" * 60)
    
    while True:
        print("\n🎯 MENU PRINCIPAL:")
        print("1. 📊 Démarrer monitoring temps réel")
        print("2. 🧪 Comparaison de scénarios")
        print("3. 📈 Analytics avancées sur résultats existants")
        print("4. 🔍 Statut monitoring actuel")
        print("5. 🚪 Quitter")
        
        choice = input("\nVotre choix (1-5): ").strip()
        
        if choice == "1":
            monitor = RealTimeMonitor()
            monitor.start_monitoring()
            
            print("🔍 Monitoring démarré. Appuyez sur Entrée pour arrêter...")
            input()
            
            monitor.stop_monitoring()
            
            # Option export
            export_choice = input("Exporter les données? (y/N): ").strip().lower()
            if export_choice == 'y':
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"monitoring_data_{timestamp}.csv"
                monitor.export_monitoring_data(output_file)
        
        elif choice == "2":
            # Sélection des fichiers de test
            cv_file = input("Chemin vers un fichier CV de test: ").strip()
            fdp_file = input("Chemin vers un fichier FDP de test: ").strip()
            
            if not Path(cv_file).exists() or not Path(fdp_file).exists():
                print("❌ Fichiers non trouvés")
                continue
            
            comparator = ScenarioComparator()
            comparator.create_default_scenarios()
            
            print("🧪 Démarrage de la comparaison...")
            results = comparator.run_scenario_comparison(cv_file, fdp_file)
            
            print("\n" + comparator.generate_comparison_report())
            
            # Sauvegarde
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f"scenario_comparison_{timestamp}.json", 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"📁 Résultats sauvegardés: scenario_comparison_{timestamp}.json")
        
        elif choice == "3":
            # Analytics sur fichiers existants
            import glob
            result_files = glob.glob("nextvision_test_results/raw_results_*.json")
            
            if not result_files:
                print("❌ Aucun fichier de résultats trouvé")
                continue
            
            latest_file = max(result_files, key=lambda x: Path(x).stat().st_mtime)
            print(f"📁 Analyse du fichier: {latest_file}")
            
            with open(latest_file, 'r') as f:
                raw_results = json.load(f)
            
            successful_results = [r for r in raw_results if r.get('status') == 'success']
            
            if not successful_results:
                print("❌ Aucun résultat réussi à analyser")
                continue
            
            # Analytics patterns
            pattern_analysis = AdvancedAnalytics.analyze_score_patterns(successful_results)
            print("\n🔍 ANALYSE DES PATTERNS:")
            print(json.dumps(pattern_analysis, indent=2))
            
            # Analytics performance
            perf_analysis = AdvancedAnalytics.performance_regression_analysis(successful_results)
            print("\n⚡ ANALYSE DE RÉGRESSION:")
            print(json.dumps(perf_analysis, indent=2))
            
            # Détection d'anomalies
            scores = [r['score'] for r in successful_results]
            anomalies = AdvancedAnalytics.detect_score_anomalies(scores)
            print(f"\n🚨 ANOMALIES DÉTECTÉES: {len(anomalies)} sur {len(scores)} tests")
            
        elif choice == "4":
            # Statut monitoring (nécessite instance active)
            print("💡 Pour voir le statut, démarrez d'abord le monitoring (option 1)")
        
        elif choice == "5":
            print("👋 Au revoir!")
            break
        
        else:
            print("❌ Choix invalide")

if __name__ == "__main__":
    main()