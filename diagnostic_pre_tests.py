#!/usr/bin/env python3
"""
🔍 NEXTVISION V3.2.1 - DIAGNOSTIC PRÉ-TESTS

Vérifie que le système est prêt pour les tests end-to-end :
- API Nextvision accessible
- Variables d'environnement configurées
- Dépendances Python installées
- Google Maps API fonctionnelle
- Bridge Commitment- connecté

Version: 3.2.1
Date: 2025-07-11
Auteur: Assistant Claude
"""

import os
import sys
import json
import asyncio
import subprocess
import importlib
import requests
from datetime import datetime
from typing import Dict, List, Any, Tuple
import time

class SystemDiagnostic:
    """Diagnostic système pour Nextvision V3.2.1"""
    
    def __init__(self):
        self.checks = []
        self.warnings = []
        self.errors = []
        self.base_url = "http://localhost:8001"
        
    def log_result(self, check_name: str, success: bool, message: str, details: str = None):
        """Enregistre le résultat d'un check"""
        result = {
            "check": check_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.checks.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {check_name}: {message}")
        
        if details and not success:
            print(f"   Details: {details}")
    
    def check_python_version(self) -> bool:
        """Vérifie la version Python"""
        try:
            version = sys.version_info
            required_major, required_minor = 3, 8
            
            if version.major == required_major and version.minor >= required_minor:
                self.log_result(
                    "Python Version",
                    True,
                    f"Python {version.major}.{version.minor}.{version.micro} ✓"
                )
                return True
            else:
                self.log_result(
                    "Python Version",
                    False,
                    f"Python {version.major}.{version.minor}.{version.micro} (requis: ≥{required_major}.{required_minor})",
                    "Mettre à jour Python pour éviter les problèmes de compatibilité"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Python Version",
                False,
                "Impossible de vérifier la version Python",
                str(e)
            )
            return False
    
    def check_required_packages(self) -> bool:
        """Vérifie les packages Python requis"""
        required_packages = [
            ('aiohttp', 'Requêtes HTTP asynchrones'),
            ('requests', 'Requêtes HTTP basiques'),
            ('asyncio', 'Programmation asynchrone'),
            ('json', 'Manipulation JSON'),
            ('logging', 'Système de logs'),
            ('statistics', 'Calculs statistiques'),
            ('datetime', 'Gestion des dates'),
            ('pathlib', 'Manipulation des chemins'),
            ('typing', 'Annotations de type')
        ]
        
        missing_packages = []
        
        for package, description in required_packages:
            try:
                importlib.import_module(package)
            except ImportError:
                missing_packages.append((package, description))
        
        if not missing_packages:
            self.log_result(
                "Required Packages",
                True,
                f"Tous les packages requis sont installés ({len(required_packages)} vérifiés)"
            )
            return True
        else:
            missing_list = ", ".join([pkg for pkg, _ in missing_packages])
            self.log_result(
                "Required Packages",
                False,
                f"Packages manquants: {missing_list}",
                "Installer avec: pip install " + " ".join([pkg for pkg, _ in missing_packages])
            )
            return False
    
    def check_environment_variables(self) -> bool:
        """Vérifie les variables d'environnement essentielles"""
        required_env_vars = [
            ('OPENAI_API_KEY', 'Clé API OpenAI pour le parsing GPT'),
            ('GOOGLE_MAPS_API_KEY', 'Clé API Google Maps pour géocodage'),
        ]
        
        optional_env_vars = [
            ('REDIS_URL', 'URL Redis pour le cache'),
            ('DATABASE_URL', 'URL base de données'),
            ('ENVIRONMENT', 'Environnement (dev/prod)')
        ]
        
        missing_required = []
        missing_optional = []
        
        for var_name, description in required_env_vars:
            if not os.getenv(var_name):
                missing_required.append((var_name, description))
        
        for var_name, description in optional_env_vars:
            if not os.getenv(var_name):
                missing_optional.append((var_name, description))
        
        if not missing_required:
            self.log_result(
                "Environment Variables",
                True,
                f"Variables requises présentes ({len(required_env_vars)} vérifiées)"
            )
            
            if missing_optional:
                optional_list = ", ".join([var for var, _ in missing_optional])
                print(f"   ⚠️  Variables optionnelles manquantes: {optional_list}")
            
            return True
        else:
            missing_list = ", ".join([var for var, _ in missing_required])
            self.log_result(
                "Environment Variables",
                False,
                f"Variables requises manquantes: {missing_list}",
                "Configurer dans .env ou variables système"
            )
            return False
    
    def check_api_connectivity(self) -> bool:
        """Vérifie la connectivité de l'API Nextvision"""
        try:
            # Test de connectivité simple
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=10)
            
            if response.status_code == 200:
                self.log_result(
                    "API Connectivity",
                    True,
                    f"API Nextvision accessible sur {self.base_url}"
                )
                return True
            else:
                self.log_result(
                    "API Connectivity",
                    False,
                    f"API répond avec le code {response.status_code}",
                    f"Vérifier que l'API Nextvision est démarrée sur {self.base_url}"
                )
                return False
                
        except requests.exceptions.ConnectionError:
            self.log_result(
                "API Connectivity",
                False,
                "Impossible de connecter à l'API Nextvision",
                f"Démarrer l'API ou vérifier l'URL: {self.base_url}"
            )
            return False
        except requests.exceptions.Timeout:
            self.log_result(
                "API Connectivity",
                False,
                "Timeout lors de la connexion à l'API",
                "L'API met trop de temps à répondre"
            )
            return False
        except Exception as e:
            self.log_result(
                "API Connectivity",
                False,
                "Erreur inattendue lors de la connexion",
                str(e)
            )
            return False
    
    def check_api_endpoints(self) -> bool:
        """Vérifie les endpoints critiques de l'API"""
        critical_endpoints = [
            ("/api/v1/health", "Health check principal"),
            ("/api/v2/maps/health", "Google Maps service"),
            ("/api/v1/integration/health", "Bridge Commitment-"),
            ("/docs", "Documentation API")
        ]
        
        working_endpoints = 0
        
        for endpoint, description in critical_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code in [200, 404]:  # 404 acceptable pour /docs
                    working_endpoints += 1
                    print(f"   ✅ {endpoint} - {description}")
                else:
                    print(f"   ❌ {endpoint} - Code {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {endpoint} - Erreur: {str(e)[:50]}...")
        
        success = working_endpoints >= len(critical_endpoints) - 1  # Au moins 3/4
        
        self.log_result(
            "API Endpoints",
            success,
            f"{working_endpoints}/{len(critical_endpoints)} endpoints fonctionnels",
            "Certains services peuvent être indisponibles" if not success else None
        )
        
        return success
    
    def check_google_maps_api(self) -> bool:
        """Vérifie l'API Google Maps"""
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        
        if not api_key:
            self.log_result(
                "Google Maps API",
                False,
                "Clé API Google Maps non configurée",
                "Définir GOOGLE_MAPS_API_KEY dans l'environnement"
            )
            return False
        
        try:
            # Test simple de géocodage
            test_url = f"https://maps.googleapis.com/maps/api/geocode/json?address=Paris&key={api_key}"
            response = requests.get(test_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'OK':
                    self.log_result(
                        "Google Maps API",
                        True,
                        "Clé API Google Maps valide et fonctionnelle"
                    )
                    return True
                else:
                    self.log_result(
                        "Google Maps API",
                        False,
                        f"API Google Maps erreur: {data.get('status')}",
                        "Vérifier les quotas et restrictions de la clé API"
                    )
                    return False
            else:
                self.log_result(
                    "Google Maps API",
                    False,
                    f"Erreur HTTP {response.status_code} de Google Maps",
                    "Problème de connectivité ou clé API invalide"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Google Maps API",
                False,
                "Impossible de tester l'API Google Maps",
                str(e)
            )
            return False
    
    def check_openai_api(self) -> bool:
        """Vérifie l'API OpenAI"""
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            self.log_result(
                "OpenAI API",
                False,
                "Clé API OpenAI non configurée",
                "Définir OPENAI_API_KEY dans l'environnement"
            )
            return False
        
        if not api_key.startswith('sk-'):
            self.log_result(
                "OpenAI API",
                False,
                "Format de clé API OpenAI invalide",
                "La clé doit commencer par 'sk-'"
            )
            return False
        
        try:
            # Test simple avec l'API OpenAI
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://api.openai.com/v1/models',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_result(
                    "OpenAI API",
                    True,
                    "Clé API OpenAI valide et fonctionnelle"
                )
                return True
            else:
                self.log_result(
                    "OpenAI API",
                    False,
                    f"API OpenAI erreur: HTTP {response.status_code}",
                    "Vérifier la validité de la clé API"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "OpenAI API",
                False,
                "Impossible de tester l'API OpenAI",
                str(e)
            )
            return False
    
    def check_disk_space(self) -> bool:
        """Vérifie l'espace disque disponible"""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            
            free_gb = free // (1024**3)
            total_gb = total // (1024**3)
            
            if free_gb >= 1:  # Au moins 1GB libre
                self.log_result(
                    "Disk Space",
                    True,
                    f"{free_gb}GB libre sur {total_gb}GB total"
                )
                return True
            else:
                self.log_result(
                    "Disk Space",
                    False,
                    f"Seulement {free_gb}GB libre sur {total_gb}GB",
                    "Libérer de l'espace disque pour les logs et rapports"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Disk Space",
                False,
                "Impossible de vérifier l'espace disque",
                str(e)
            )
            return False
    
    def check_network_performance(self) -> bool:
        """Vérifie les performances réseau"""
        try:
            start_time = time.time()
            response = requests.get("https://httpbin.org/delay/1", timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response_time < 3000:  # Moins de 3 secondes
                self.log_result(
                    "Network Performance",
                    True,
                    f"Latence réseau: {response_time:.0f}ms"
                )
                return True
            else:
                self.log_result(
                    "Network Performance",
                    False,
                    f"Latence réseau élevée: {response_time:.0f}ms",
                    "Connexion réseau lente détectée"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Network Performance",
                False,
                "Impossible de tester les performances réseau",
                str(e)
            )
            return False
    
    def run_all_diagnostics(self) -> Dict[str, Any]:
        """Exécute tous les diagnostics"""
        print("🔍 DIAGNOSTIC SYSTÈME NEXTVISION V3.2.1")
        print("=" * 50)
        
        # Liste des diagnostics à exécuter
        diagnostics = [
            ("Python Version", self.check_python_version),
            ("Required Packages", self.check_required_packages),
            ("Environment Variables", self.check_environment_variables),
            ("API Connectivity", self.check_api_connectivity),
            ("API Endpoints", self.check_api_endpoints),
            ("Google Maps API", self.check_google_maps_api),
            ("OpenAI API", self.check_openai_api),
            ("Disk Space", self.check_disk_space),
            ("Network Performance", self.check_network_performance)
        ]
        
        successful_checks = 0
        critical_failures = []
        
        for check_name, check_func in diagnostics:
            try:
                success = check_func()
                if success:
                    successful_checks += 1
                else:
                    # Identifier les échecs critiques
                    if check_name in ["API Connectivity", "Environment Variables", "Python Version"]:
                        critical_failures.append(check_name)
                        
            except Exception as e:
                self.log_result(
                    check_name,
                    False,
                    f"Diagnostic échoué: {str(e)}",
                    "Erreur inattendue lors du diagnostic"
                )
                critical_failures.append(check_name)
        
        # Génération du rapport
        total_checks = len(diagnostics)
        success_rate = successful_checks / total_checks
        
        print("\n" + "=" * 50)
        print("📊 RÉSULTATS DU DIAGNOSTIC")
        print("=" * 50)
        print(f"Checks réussis: {successful_checks}/{total_checks}")
        print(f"Taux de réussite: {success_rate:.1%}")
        
        if critical_failures:
            print(f"\n❌ ÉCHECS CRITIQUES: {', '.join(critical_failures)}")
            print("⚠️  Les tests end-to-end risquent d'échouer")
        
        if success_rate >= 0.8:
            print("\n✅ SYSTÈME PRÊT pour les tests end-to-end")
            ready_for_tests = True
        elif success_rate >= 0.6:
            print("\n⚠️  SYSTÈME PARTIELLEMENT PRÊT - Tests possibles avec limitations")
            ready_for_tests = True
        else:
            print("\n❌ SYSTÈME NON PRÊT - Corriger les problèmes avant de lancer les tests")
            ready_for_tests = False
        
        # Recommandations
        print("\n📋 RECOMMANDATIONS:")
        if not ready_for_tests:
            print("  1. Corriger les échecs critiques")
            print("  2. Relancer le diagnostic")
            print("  3. Puis exécuter les tests end-to-end")
        else:
            print("  1. Démarrer l'API Nextvision si ce n'est pas fait")
            print("  2. Exécuter: python test_e2e_nextvision_v321.py")
            print("  3. Analyser les résultats des tests")
        
        return {
            "summary": {
                "total_checks": total_checks,
                "successful_checks": successful_checks,
                "failed_checks": total_checks - successful_checks,
                "success_rate": success_rate,
                "ready_for_tests": ready_for_tests,
                "critical_failures": critical_failures,
                "timestamp": datetime.now().isoformat()
            },
            "detailed_checks": self.checks,
            "recommendations": self._generate_specific_recommendations()
        }
    
    def _generate_specific_recommendations(self) -> List[str]:
        """Génère des recommandations spécifiques"""
        recommendations = []
        
        failed_checks = [check for check in self.checks if not check['success']]
        
        for check in failed_checks:
            check_name = check['check']
            
            if "Python Version" in check_name:
                recommendations.append("Installer Python 3.8+ : https://python.org/downloads")
            elif "Required Packages" in check_name:
                recommendations.append("Installer les dépendances : pip install -r requirements.txt")
            elif "Environment Variables" in check_name:
                recommendations.append("Configurer les variables : cp .env.example .env")
            elif "API Connectivity" in check_name:
                recommendations.append("Démarrer l'API : python main.py")
            elif "Google Maps API" in check_name:
                recommendations.append("Configurer GOOGLE_MAPS_API_KEY dans .env")
            elif "OpenAI API" in check_name:
                recommendations.append("Configurer OPENAI_API_KEY dans .env")
            elif "Disk Space" in check_name:
                recommendations.append("Libérer de l'espace disque")
            elif "Network Performance" in check_name:
                recommendations.append("Vérifier la connexion internet")
        
        return recommendations


def main():
    """Fonction principale"""
    diagnostic = SystemDiagnostic()
    report = diagnostic.run_all_diagnostics()
    
    # Sauvegarde du rapport
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"diagnostic_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Rapport détaillé sauvegardé: {report_file}")
    
    # Code de sortie
    exit_code = 0 if report['summary']['ready_for_tests'] else 1
    print(f"\n🎯 Diagnostic terminé avec le code: {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Diagnostic interrompu par l'utilisateur")
        exit(2)
    except Exception as e:
        print(f"\n❌ Erreur critique: {str(e)}")
        exit(3)
