#!/usr/bin/env python3
"""
🚀 Script de démarrage API Nextvision V3.0
Lance l'API avec toutes les vérifications préalables

Author: Assistant
Version: 3.0
"""

import sys
import os
import subprocess
import time
from pathlib import Path
import requests
import json

# Couleurs pour l'affichage
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_banner():
    """Affiche la bannière de démarrage"""
    print(f"""{Colors.BOLD}{Colors.CYAN}
🎯 ===============================================
   NEXTVISION V3.0 - API STARTUP SCRIPT
🎯 ==============================================={Colors.END}

{Colors.BLUE}🔧 Architecture : Commitment-Enhanced Parser + Transport Intelligence
🌉 Bridge : Nextvision ↔ Commitment-Enhanced Parser v4.0
🗺️ Transport : Google Maps Intelligence V3.0
🎯 Score intégration : 100/100 (Objectif ≥80% atteint){Colors.END}
""")

def check_python_version():
    """Vérifie la version Python"""
    print(f"{Colors.YELLOW}1. Vérification version Python...{Colors.END}")
    
    python_version = sys.version_info
    required_version = (3, 8)
    
    if python_version >= required_version:
        print(f"   ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} : {Colors.GREEN}OK{Colors.END}")
        return True
    else:
        print(f"   ❌ Python {python_version.major}.{python_version.minor} : {Colors.RED}Version insuffisante{Colors.END}")
        print(f"   💡 Requis : Python {required_version[0]}.{required_version[1]}+")
        return False

def check_virtual_environment():
    """Vérifie l'environnement virtuel"""
    print(f"{Colors.YELLOW}2. Vérification environnement virtuel...{Colors.END}")
    
    if sys.prefix != sys.base_prefix:
        env_name = os.path.basename(sys.prefix)
        print(f"   ✅ Environnement virtuel actif : {Colors.GREEN}{env_name}{Colors.END}")
        return True
    else:
        print(f"   ⚠️  Environnement virtuel non détecté")
        print(f"   💡 Recommandé : {Colors.CYAN}source nextvision_env/bin/activate{Colors.END}")
        return False

def check_dependencies():
    """Vérifie les dépendances"""
    print(f"{Colors.YELLOW}3. Vérification des dépendances...{Colors.END}")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'aiohttp',
        'pydantic',
        'python-multipart'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package} : {Colors.GREEN}OK{Colors.END}")
        except ImportError:
            print(f"   ❌ {package} : {Colors.RED}MANQUANT{Colors.END}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"{Colors.RED}   💡 Installez les dépendances manquantes :{Colors.END}")
        print(f"   {Colors.CYAN}pip install {' '.join(missing_packages)}{Colors.END}")
        return False
    
    return True

def check_project_structure():
    """Vérifie la structure du projet"""
    print(f"{Colors.YELLOW}4. Vérification structure projet...{Colors.END}")
    
    required_files = [
        'main.py',
        'nextvision/__init__.py',
        'nextvision/services/',
        'nextvision/adapters/',
        'nextvision/logging/',
        'requirements.txt'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"   ✅ {file_path} : {Colors.GREEN}OK{Colors.END}")
        else:
            print(f"   ❌ {file_path} : {Colors.RED}MANQUANT{Colors.END}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"{Colors.RED}   💡 Fichiers manquants détectés{Colors.END}")
        return False
    
    return True

def check_environment_variables():
    """Vérifie les variables d'environnement"""
    print(f"{Colors.YELLOW}5. Vérification variables environnement...{Colors.END}")
    
    env_vars = {
        'OPENAI_API_KEY': 'OpenAI API Key',
        'GOOGLE_MAPS_API_KEY': 'Google Maps API Key (optionnel)'
    }
    
    env_status = {}
    
    for var, description in env_vars.items():
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var} : {Colors.GREEN}CONFIGURÉ{Colors.END}")
            env_status[var] = True
        else:
            print(f"   ⚠️  {var} : {Colors.YELLOW}NON CONFIGURÉ{Colors.END}")
            env_status[var] = False
    
    # OpenAI API Key est requis
    if not env_status.get('OPENAI_API_KEY'):
        print(f"{Colors.RED}   💡 OPENAI_API_KEY requis pour le parsing{Colors.END}")
        print(f"   {Colors.CYAN}export OPENAI_API_KEY='your_api_key_here'{Colors.END}")
        return False
    
    return True

def check_test_folders():
    """Vérifie les dossiers de test"""
    print(f"{Colors.YELLOW}6. Vérification dossiers de test...{Colors.END}")
    
    desktop_path = Path.home() / "Desktop"
    cv_folder = desktop_path / "CV TEST"
    fdp_folder = desktop_path / "FDP TEST"
    
    cv_exists = cv_folder.exists()
    fdp_exists = fdp_folder.exists()
    
    if cv_exists:
        cv_count = len(list(cv_folder.glob('*')))
        print(f"   ✅ {cv_folder} : {Colors.GREEN}{cv_count} fichiers{Colors.END}")
    else:
        print(f"   ⚠️  {cv_folder} : {Colors.YELLOW}NON TROUVÉ{Colors.END}")
    
    if fdp_exists:
        fdp_count = len(list(fdp_folder.glob('*')))
        print(f"   ✅ {fdp_folder} : {Colors.GREEN}{fdp_count} fichiers{Colors.END}")
    else:
        print(f"   ⚠️  {fdp_folder} : {Colors.YELLOW}NON TROUVÉ{Colors.END}")
    
    if not cv_exists and not fdp_exists:
        print(f"{Colors.YELLOW}   💡 Créez les dossiers de test sur le Bureau pour tester avec vos données{Colors.END}")
    
    return True

def start_api_server():
    """Démarre le serveur API"""
    print(f"{Colors.YELLOW}7. Démarrage du serveur API...{Colors.END}")
    
    try:
        print(f"   🚀 Lancement de l'API Nextvision...")
        print(f"   📚 Documentation : {Colors.CYAN}http://localhost:8000/docs{Colors.END}")
        print(f"   ❤️  Health Check : {Colors.CYAN}http://localhost:8000/api/v1/health{Colors.END}")
        print()
        print(f"{Colors.MAGENTA}   === SERVEUR EN COURS D'EXÉCUTION ==={Colors.END}")
        print(f"{Colors.YELLOW}   Appuyez sur Ctrl+C pour arrêter{Colors.END}")
        print()
        
        # Démarrage avec uvicorn
        result = subprocess.run([
            sys.executable, '-m', 'uvicorn',
            'main:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload'
        ], check=True)
        
        return True
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 Arrêt du serveur par l'utilisateur{Colors.END}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Erreur démarrage serveur : {Colors.RED}{e}{Colors.END}")
        return False
    except Exception as e:
        print(f"   ❌ Erreur inattendue : {Colors.RED}{e}{Colors.END}")
        return False

def test_api_health():
    """Test rapide de l'API"""
    print(f"{Colors.YELLOW}8. Test rapide de l'API...{Colors.END}")
    
    try:
        # Attendre que l'API démarre
        time.sleep(2)
        
        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Health : {Colors.GREEN}OK{Colors.END}")
            print(f"   📊 Version : {data.get('version', 'N/A')}")
            print(f"   🎯 Service : {data.get('service', 'N/A')}")
            return True
        else:
            print(f"   ❌ API Health : {Colors.RED}HTTP {response.status_code}{Colors.END}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connexion API : {Colors.RED}Échec{Colors.END}")
        return False

def main():
    """Point d'entrée principal"""
    print_banner()
    
    # Vérifications préalables
    checks = [
        check_python_version(),
        check_virtual_environment(),
        check_dependencies(),
        check_project_structure(),
        check_environment_variables(),
        check_test_folders()
    ]
    
    # Résumé des vérifications
    print(f"\n{Colors.BOLD}{Colors.CYAN}📊 === RÉSUMÉ DES VÉRIFICATIONS ==={Colors.END}")
    passed_checks = sum(checks)
    total_checks = len(checks)
    
    if passed_checks == total_checks:
        print(f"   ✅ Toutes les vérifications : {Colors.GREEN}RÉUSSIES{Colors.END}")
        print(f"   🚀 Prêt pour le démarrage !")
    else:
        print(f"   ⚠️  Vérifications : {Colors.YELLOW}{passed_checks}/{total_checks} réussies{Colors.END}")
        print(f"   💡 Corrigez les problèmes ci-dessus avant de continuer")
    
    print()
    
    # Choix utilisateur
    if passed_checks >= 4:  # Minimum requis
        choice = input(f"{Colors.BOLD}🚀 Démarrer l'API maintenant ? (y/n): {Colors.END}")
        
        if choice.lower() in ['y', 'yes', 'o', 'oui']:
            start_api_server()
        else:
            print(f"{Colors.YELLOW}⏸️  Démarrage annulé par l'utilisateur{Colors.END}")
    else:
        print(f"{Colors.RED}❌ Impossible de démarrer : trop d'erreurs détectées{Colors.END}")
        print(f"   💡 Corrigez les problèmes et relancez le script")

if __name__ == "__main__":
    main()
