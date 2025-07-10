#!/usr/bin/env python3
"""
📦 Installation des dépendances pour Nextvision V3.0 Testing Suite
Installe et vérifie toutes les dépendances nécessaires

Author: Assistant
Version: 1.0
"""

import subprocess
import sys
import os
from pathlib import Path

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
    """Affiche la bannière d'installation"""
    print(f"""{Colors.BOLD}{Colors.CYAN}
📦 ===============================================
   NEXTVISION V3.0 - INSTALLATION DÉPENDANCES
📦 ==============================================={Colors.END}

{Colors.BLUE}🎯 Installation des dépendances pour la Testing Suite
🧪 Prépare l'environnement pour tester avec vos données réelles{Colors.END}
""")

def check_python_version():
    """Vérifie la version Python"""
    print(f"{Colors.YELLOW}🐍 Vérification version Python...{Colors.END}")
    
    version = sys.version_info
    if version >= (3, 8):
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} : {Colors.GREEN}Compatible{Colors.END}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor} : {Colors.RED}Trop ancien{Colors.END}")
        print(f"   💡 Requis : Python 3.8+")
        return False

def install_dependencies():
    """Installe les dépendances nécessaires"""
    print(f"{Colors.YELLOW}📦 Installation des dépendances...{Colors.END}")
    
    # Dépendances requises pour la testing suite
    testing_deps = [
        'requests',
        'aiohttp',
        'asyncio',
        'pathlib',
        'json',
        'mimetypes'
    ]
    
    # Dépendances principales (si pas déjà installées)
    main_deps = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'python-multipart'
    ]
    
    all_deps = testing_deps + main_deps
    
    print(f"   🔄 Installation en cours...")
    
    try:
        # Installer les dépendances une par une
        for dep in main_deps:
            try:
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', dep
                ], check=True, capture_output=True)
                print(f"   ✅ {dep} : {Colors.GREEN}Installé{Colors.END}")
            except subprocess.CalledProcessError:
                print(f"   ⚠️  {dep} : {Colors.YELLOW}Déjà installé ou erreur{Colors.END}")
        
        print(f"   🎉 Installation terminée !")
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur installation : {Colors.RED}{e}{Colors.END}")
        return False

def verify_installation():
    """Vérifie que tout est installé correctement"""
    print(f"{Colors.YELLOW}🔍 Vérification installation...{Colors.END}")
    
    test_imports = [
        ('requests', 'requests'),
        ('aiohttp', 'aiohttp'),
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('pydantic', 'pydantic')
    ]
    
    all_ok = True
    
    for module_name, import_name in test_imports:
        try:
            __import__(import_name)
            print(f"   ✅ {module_name} : {Colors.GREEN}OK{Colors.END}")
        except ImportError:
            print(f"   ❌ {module_name} : {Colors.RED}ÉCHEC{Colors.END}")
            all_ok = False
    
    return all_ok

def check_environment_setup():
    """Vérifie la configuration de l'environnement"""
    print(f"{Colors.YELLOW}🔧 Vérification environnement...{Colors.END}")
    
    # Vérifier l'environnement virtuel
    if sys.prefix != sys.base_prefix:
        env_name = os.path.basename(sys.prefix)
        print(f"   ✅ Environnement virtuel : {Colors.GREEN}{env_name}{Colors.END}")
    else:
        print(f"   ⚠️  Environnement virtuel : {Colors.YELLOW}Non détecté{Colors.END}")
        print(f"   💡 Recommandé : Créer un environnement virtuel")
    
    # Vérifier les variables d'environnement
    openai_key = os.getenv('OPENAI_API_KEY')
    gmaps_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    if openai_key:
        print(f"   ✅ OPENAI_API_KEY : {Colors.GREEN}Configuré{Colors.END}")
    else:
        print(f"   ⚠️  OPENAI_API_KEY : {Colors.YELLOW}Non configuré{Colors.END}")
        print(f"   💡 Requis pour le parsing des CVs/FDPs")
    
    if gmaps_key:
        print(f"   ✅ GOOGLE_MAPS_API_KEY : {Colors.GREEN}Configuré{Colors.END}")
    else:
        print(f"   ⚠️  GOOGLE_MAPS_API_KEY : {Colors.YELLOW}Non configuré{Colors.END}")
        print(f"   💡 Optionnel pour Transport Intelligence")

def create_test_folders():
    """Crée les dossiers de test"""
    print(f"{Colors.YELLOW}📁 Création dossiers de test...{Colors.END}")
    
    desktop_path = Path.home() / "Desktop"
    cv_folder = desktop_path / "CV TEST"
    fdp_folder = desktop_path / "FDP TEST"
    
    cv_folder.mkdir(exist_ok=True)
    fdp_folder.mkdir(exist_ok=True)
    
    print(f"   ✅ Dossier CV créé : {Colors.GREEN}{cv_folder}{Colors.END}")
    print(f"   ✅ Dossier FDP créé : {Colors.GREEN}{fdp_folder}{Colors.END}")

def show_next_steps():
    """Affiche les prochaines étapes"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}🚀 === PROCHAINES ÉTAPES ==={Colors.END}")
    print()
    print(f"{Colors.BOLD}1. Configurez vos variables d'environnement :{Colors.END}")
    print(f"   {Colors.CYAN}export OPENAI_API_KEY='your_key_here'{Colors.END}")
    print(f"   {Colors.CYAN}export GOOGLE_MAPS_API_KEY='your_key_here'{Colors.END}")
    print()
    print(f"{Colors.BOLD}2. Ajoutez vos fichiers de test :{Colors.END}")
    print(f"   • CVs dans : {Colors.CYAN}~/Desktop/CV TEST/{Colors.END}")
    print(f"   • FDPs dans : {Colors.CYAN}~/Desktop/FDP TEST/{Colors.END}")
    print()
    print(f"{Colors.BOLD}3. Lancez la testing suite :{Colors.END}")
    print(f"   {Colors.CYAN}python nextvision_master_script.py{Colors.END}")
    print()
    print(f"{Colors.BOLD}Ou générez des données d'exemple :{Colors.END}")
    print(f"   {Colors.CYAN}python sample_data_generator.py{Colors.END}")

def main():
    """Point d'entrée principal"""
    print_banner()
    
    # Vérifications et installations
    steps = [
        ("Version Python", check_python_version),
        ("Installation dépendances", install_dependencies),
        ("Vérification installation", verify_installation),
        ("Configuration environnement", check_environment_setup),
        ("Création dossiers test", create_test_folders)
    ]
    
    results = []
    
    for step_name, step_func in steps:
        print(f"\n{Colors.BOLD}🔄 {step_name}...{Colors.END}")
        result = step_func()
        results.append(result)
        
        if result is False:
            print(f"   ❌ {step_name} : {Colors.RED}ÉCHEC{Colors.END}")
        else:
            print(f"   ✅ {step_name} : {Colors.GREEN}OK{Colors.END}")
    
    # Résumé
    print(f"\n{Colors.BOLD}{Colors.CYAN}📊 === RÉSUMÉ INSTALLATION ==={Colors.END}")
    success_count = sum(1 for r in results if r is True)
    total_count = len(results)
    
    if success_count == total_count:
        print(f"   🎉 Installation complète : {Colors.GREEN}RÉUSSIE{Colors.END}")
        print(f"   ✅ Prêt à tester Nextvision V3.0 !")
    else:
        print(f"   ⚠️  Installation partielle : {Colors.YELLOW}{success_count}/{total_count}{Colors.END}")
        print(f"   💡 Corrigez les problèmes avant de continuer")
    
    show_next_steps()

if __name__ == "__main__":
    main()
