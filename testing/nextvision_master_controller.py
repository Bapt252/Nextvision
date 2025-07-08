#!/usr/bin/env python3
"""
Contrôleur Principal Nextvision v2.0
Interface unifiée pour tous les tests et analyses
"""

import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import threading
import psutil

# Configuration globale
API_URL = "http://localhost:8000"
CV_DIR = "/Users/baptistecomas/Desktop/CV TEST"
FDP_DIR = "/Users/baptistecomas/Desktop/FDP TEST"
RESULTS_BASE_DIR = "nextvision_test_results"

class NextvisionController:
    """Contrôleur principal pour orchestrer tous les tests Nextvision"""
    
    def __init__(self):
        self.api_url = API_URL
        self.cv_dir = Path(CV_DIR)
        self.fdp_dir = Path(FDP_DIR)
        self.results_dir = Path(RESULTS_BASE_DIR)
        self.results_dir.mkdir(exist_ok=True)
        
        self.api_process = None
        self.monitoring_active = False
        
    def check_api_status(self) -> Dict[str, Any]:
        """Vérifie le statut de l'API"""
        try:
            response = requests.get(f"{self.api_url}/docs", timeout=5)
            if response.status_code == 200:
                return {
                    "status": "running",
                    "url": self.api_url,
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {"status": "error", "code": response.status_code}
        except requests.exceptions.ConnectionError:
            return {"status": "not_running"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_environment(self) -> Dict[str, Any]:
        """Vérifie l'environnement de test"""
        env_status = {
            "cv_directory": {
                "exists": self.cv_dir.exists(),
                "count": len(list(self.cv_dir.glob("*.pdf"))) if self.cv_dir.exists() else 0
            },
            "fdp_directory": {
                "exists": self.fdp_dir.exists(),
                "count": len(list(self.fdp_dir.glob("*.pdf"))) if self.fdp_dir.exists() else 0
            },
            "results_directory": {
                "exists": self.results_dir.exists(),
                "previous_tests": len(list(self.results_dir.glob("*.json")))
            },
            "system": {
                "python_version": sys.version,
                "memory_gb": round(psutil.virtual_memory().total / (1024**3), 1),
                "cpu_count": psutil.cpu_count(),
                "disk_free_gb": round(psutil.disk_usage('/').free / (1024**3), 1)
            }
        }
        
        return env_status
    
    def start_api_server(self) -> bool:
        """Démarre le serveur API si pas déjà en cours"""
        api_status = self.check_api_status()
        
        if api_status["status"] == "running":
            print("✅ API déjà en cours d'exécution")
            return True
        
        print("🚀 Démarrage du serveur API...")
        
        # Commande pour démarrer l'API
        try:
            # Change vers le répertoire du projet
            project_dir = Path.cwd()  # Assuming we're in the right directory
            
            # Démarrage de l'API en arrière-plan
            self.api_process = subprocess.Popen(
                ["uvicorn", "main_v2:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Attendre que l'API soit prête
            max_wait = 30
            for _ in range(max_wait):
                time.sleep(1)
                if self.check_api_status()["status"] == "running":
                    print("✅ API démarrée avec succès")
                    return True
            
            print("❌ Timeout - API n'a pas démarré dans les 30s")
            self.stop_api_server()
            return False
            
        except Exception as e:
            print(f"❌ Erreur démarrage API: {e}")
            return False
    
    def stop_api_server(self):
        """Arrête le serveur API"""
        if self.api_process:
            self.api_process.terminate()
            self.api_process.wait()
            self.api_process = None
            print("🛑 Serveur API arrêté")
    
    def run_mass_test(self, max_combinations: int = None) -> str:
        """Lance le test massif"""
        if not self.start_api_server():
            return "❌ Impossible de démarrer l'API"
        
        print(f"🎯 Lancement du test massif...")
        print(f"📊 Combinaisons max: {max_combinations or 'toutes'}")
        
        try:
            # Import et exécution du test massif
            from nextvision_mass_testing import MassTestRunner, ResultsAnalyzer
            
            runner = MassTestRunner()
            results = runner.run_mass_test(max_combinations)
            
            if results:
                analyzer = ResultsAnalyzer(results)
                raw_file, report_file = analyzer.save_results(self.results_dir)
                
                return f"✅ Test terminé - Résultats: {raw_file}"
            else:
                return "❌ Aucun résultat généré"
                
        except Exception as e:
            return f"❌ Erreur test massif: {e}"
    
    def run_visualization(self) -> str:
        """Génère les visualisations"""
        try:
            # Recherche du dernier fichier de résultats
            result_files = list(self.results_dir.glob("raw_results_*.json"))
            
            if not result_files:
                return "❌ Aucun fichier de résultats trouvé"
            
            latest_file = max(result_files, key=lambda x: x.stat().st_mtime)
            
            # Import et exécution du visualiseur
            from nextvision_visualizer import NextvisionVisualizer
            
            visualizer = NextvisionVisualizer(str(latest_file))
            visualizer.generate_dashboard()
            
            return f"✅ Visualisations générées - Fichier: {latest_file.name}"
            
        except Exception as e:
            return f"❌ Erreur visualisation: {e}"
    
    def run_scenario_comparison(self) -> str:
        """Lance la comparaison de scénarios"""
        if not self.start_api_server():
            return "❌ Impossible de démarrer l'API"
        
        try:
            # Sélection de fichiers de test
            cv_files = list(self.cv_dir.glob("*.pdf"))
            fdp_files = list(self.fdp_dir.glob("*.pdf"))
            
            if not cv_files or not fdp_files:
                return "❌ Aucun fichier CV ou FDP trouvé"
            
            # Utilisation des premiers fichiers trouvés
            cv_file = str(cv_files[0])
            fdp_file = str(fdp_files[0])
            
            from nextvision_advanced_analyzer import ScenarioComparator
            
            comparator = ScenarioComparator()
            comparator.create_default_scenarios()
            
            results = comparator.run_scenario_comparison(cv_file, fdp_file)
            
            # Sauvegarde
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.results_dir / f"scenario_comparison_{timestamp}.json"
            
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            return f"✅ Comparaison terminée - Résultats: {output_file.name}"
            
        except Exception as e:
            return f"❌ Erreur comparaison: {e}"
    
    def start_monitoring(self) -> str:
        """Démarre le monitoring temps réel"""
        if not self.start_api_server():
            return "❌ Impossible de démarrer l'API"
        
        try:
            from nextvision_advanced_analyzer import RealTimeMonitor
            
            monitor = RealTimeMonitor()
            monitor.start_monitoring()
            
            self.monitoring_active = True
            
            return "✅ Monitoring démarré - Utilisez 'stop_monitoring' pour arrêter"
            
        except Exception as e:
            return f"❌ Erreur monitoring: {e}"
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retourne le statut complet du système"""
        return {
            "timestamp": datetime.now().isoformat(),
            "api": self.check_api_status(),
            "environment": self.check_environment(),
            "monitoring": self.monitoring_active,
            "recent_tests": self._get_recent_tests()
        }
    
    def _get_recent_tests(self) -> List[Dict[str, Any]]:
        """Récupère les tests récents"""
        recent_tests = []
        
        # Fichiers de résultats bruts
        for file in sorted(self.results_dir.glob("raw_results_*.json"), 
                          key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                
                successful = len([r for r in data if r.get('status') == 'success'])
                total = len(data)
                
                recent_tests.append({
                    "file": file.name,
                    "timestamp": datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                    "tests": f"{successful}/{total}",
                    "success_rate": f"{(successful/total*100):.1f}%" if total > 0 else "0%"
                })
            except:
                continue
        
        return recent_tests
    
    def cleanup(self):
        """Nettoyage avant fermeture"""
        self.stop_api_server()
        print("🧹 Nettoyage terminé")

def print_banner():
    """Affiche la bannière de démarrage"""
    banner = """
    ████████╗███████╗███████╗████████╗    ███╗   ██╗███████╗██╗  ██╗████████╗██╗   ██╗██╗███████╗██╗ ██████╗ ███╗   ██╗
    ╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝    ████╗  ██║██╔════╝╚██╗██╔╝╚══██╔══╝██║   ██║██║██╔════╝██║██╔═══██╗████╗  ██║
       ██║   █████╗  ███████╗   ██║       ██╔██╗ ██║█████╗   ╚███╔╝    ██║   ██║   ██║██║███████╗██║██║   ██║██╔██╗ ██║
       ██║   ██╔══╝  ╚════██║   ██║       ██║╚██╗██║██╔══╝   ██╔██╗    ██║   ╚██╗ ██╔╝██║╚════██║██║██║   ██║██║╚██╗██║
       ██║   ███████╗███████║   ██║       ██║ ╚████║███████╗██╔╝ ██╗   ██║    ╚████╔╝ ██║███████║██║╚██████╔╝██║ ╚████║
       ╚═╝   ╚══════╝╚══════╝   ╚═╝       ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝   ╚═╝     ╚═══╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
    
    🚀 NEXTVISION v2.0 - SYSTÈME DE TEST MASSIF
    ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    """
    print(banner)

def main():
    """Interface principale"""
    print_banner()
    
    controller = NextvisionController()
    
    try:
        while True:
            # Affichage du statut système
            status = controller.get_system_status()
            api_status = status["api"]["status"]
            api_icon = "🟢" if api_status == "running" else "🔴"
            
            print(f"\n{api_icon} API: {api_status}")
            print(f"📁 CVs: {status['environment']['cv_directory']['count']}")
            print(f"📋 FDPs: {status['environment']['fdp_directory']['count']}")
            print(f"📊 Tests précédents: {status['environment']['results_directory']['previous_tests']}")
            
            if status["recent_tests"]:
                latest_test = status["recent_tests"][0]
                print(f"🕒 Dernier test: {latest_test['tests']} ({latest_test['success_rate']})")
            
            print("\n" + "="*70)
            print("🎯 MENU PRINCIPAL NEXTVISION v2.0")
            print("="*70)
            print("1. 🧪 Lancer Test Massif (personnalisé)")
            print("2. 🎯 Test Massif Rapide (100 combinaisons)")
            print("3. 🎯 Test Massif Complet (toutes combinaisons)")
            print("4. 📊 Générer Visualisations")
            print("5. 🧪 Comparaison Scénarios")
            print("6. 📈 Monitoring Temps Réel")
            print("7. 📋 Analytics Avancées")
            print("8. 🔧 Statut Détaillé Système")
            print("9. 🔄 Redémarrer API")
            print("0. 🚪 Quitter")
            
            choice = input("\n👉 Votre choix (0-9): ").strip()
            
            if choice == "1":
                try:
                    max_combinations = int(input("Nombre max de combinaisons: "))
                    print("🚀 Démarrage du test personnalisé...")
                    result = controller.run_mass_test(max_combinations)
                    print(f"\n📊 RÉSULTAT: {result}")
                except ValueError:
                    print("❌ Nombre invalide")
            
            elif choice == "2":
                print("🚀 Démarrage du test rapide (100 combinaisons)...")
                result = controller.run_mass_test(100)
                print(f"\n📊 RÉSULTAT: {result}")
            
            elif choice == "3":
                confirm = input("⚠️ Test complet (~2,346 combinaisons). Continuer? (y/N): ")
                if confirm.lower() == 'y':
                    print("🚀 Démarrage du test complet...")
                    result = controller.run_mass_test()
                    print(f"\n📊 RÉSULTAT: {result}")
            
            elif choice == "4":
                print("🎨 Génération des visualisations...")
                result = controller.run_visualization()
                print(f"\n📊 RÉSULTAT: {result}")
            
            elif choice == "5":
                print("🧪 Démarrage comparaison scénarios...")
                result = controller.run_scenario_comparison()
                print(f"\n📊 RÉSULTAT: {result}")
            
            elif choice == "6":
                print("📈 Démarrage monitoring...")
                result = controller.start_monitoring()
                print(f"\n📊 RÉSULTAT: {result}")
                
                if "✅" in result:
                    input("\n⏸️ Appuyez sur Entrée pour arrêter le monitoring...")
                    controller.monitoring_active = False
                    print("🛑 Monitoring arrêté")
            
            elif choice == "7":
                print("📈 Ouverture des analytics avancées...")
                try:
                    from nextvision_advanced_analyzer import main as advanced_main
                    advanced_main()
                except Exception as e:
                    print(f"❌ Erreur analytics: {e}")
            
            elif choice == "8":
                print("\n" + "="*50)
                print("🔍 STATUT DÉTAILLÉ DU SYSTÈME")
                print("="*50)
                
                detailed_status = controller.get_system_status()
                
                # API Status
                api_info = detailed_status["api"]
                print(f"\n🌐 API:")
                print(f"   Status: {api_info['status']}")
                if api_info["status"] == "running":
                    print(f"   URL: {controller.api_url}")
                    print(f"   Temps réponse: {api_info.get('response_time', 'N/A')}s")
                
                # Environment
                env = detailed_status["environment"]
                print(f"\n📁 ENVIRONNEMENT:")
                print(f"   CVs disponibles: {env['cv_directory']['count']}")
                print(f"   FDPs disponibles: {env['fdp_directory']['count']}")
                print(f"   Tests précédents: {env['results_directory']['previous_tests']}")
                
                # System
                sys_info = env["system"]
                print(f"\n💻 SYSTÈME:")
                print(f"   Python: {sys_info['python_version'].split()[0]}")
                print(f"   RAM: {sys_info['memory_gb']} GB")
                print(f"   CPU: {sys_info['cpu_count']} cores")
                print(f"   Disque libre: {sys_info['disk_free_gb']} GB")
                
                # Tests récents
                if detailed_status["recent_tests"]:
                    print(f"\n📊 TESTS RÉCENTS:")
                    for test in detailed_status["recent_tests"][:3]:
                        print(f"   • {test['file']}: {test['tests']} ({test['success_rate']})")
                
                input("\nAppuyez sur Entrée pour continuer...")
            
            elif choice == "9":
                print("🔄 Redémarrage de l'API...")
                controller.stop_api_server()
                time.sleep(2)
                if controller.start_api_server():
                    print("✅ API redémarrée avec succès")
                else:
                    print("❌ Échec redémarrage API")
            
            elif choice == "0":
                print("👋 Fermeture de Nextvision Test Suite...")
                break
            
            else:
                print("❌ Choix invalide")
            
            if choice not in ["0", "7"]:  # Pas de pause pour analytics ou quitter
                input("\n⏸️ Appuyez sur Entrée pour continuer...")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Interruption détectée...")
    
    finally:
        controller.cleanup()
        print("🎉 Merci d'avoir utilisé Nextvision Test Suite!")

if __name__ == "__main__":
    main()