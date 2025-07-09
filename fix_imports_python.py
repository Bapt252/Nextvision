#!/usr/bin/env python3
"""
🔧 NEXTVISION INTEGRATION FIXER
Script Python pour corriger automatiquement les problèmes d'imports et dépendances

Author: Assistant Claude
Version: 1.0.0
"""

import os
import sys
import re
import subprocess
import importlib.util
from pathlib import Path
from typing import List, Dict, Optional, Tuple

def print_status(message: str):
    print(f"🔧 [INFO] {message}")

def print_success(message: str):
    print(f"✅ [SUCCESS] {message}")

def print_warning(message: str):
    print(f"⚠️ [WARNING] {message}")

def print_error(message: str):
    print(f"❌ [ERROR] {message}")

class NextvisionIntegrationFixer:
    """Outil de correction automatique pour l'intégration Nextvision"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).absolute()
        self.python_files: List[Path] = []
        self.import_errors: List[Dict] = []
        self.fixes_applied: List[str] = []
        
    def scan_python_files(self):
        """Scan tous les fichiers Python du projet"""
        print_status("Scan des fichiers Python...")
        
        self.python_files = list(self.project_root.rglob("*.py"))
        print_success(f"{len(self.python_files)} fichiers Python trouvés")
        
    def check_dependencies(self) -> Dict[str, bool]:
        """Vérifie les dépendances critiques"""
        print_status("Vérification des dépendances critiques...")
        
        critical_deps = {
            'requests': False,
            'aiohttp': False,
            'pydantic': False,
            'fastapi': False,
            'playwright': False,
            'asyncio': True  # Built-in
        }
        
        for dep_name in critical_deps:
            if dep_name == 'asyncio':
                continue  # Built-in
                
            spec = importlib.util.find_spec(dep_name)
            critical_deps[dep_name] = spec is not None
            
            if critical_deps[dep_name]:
                print_success(f"✅ {dep_name} installé")
            else:
                print_error(f"❌ {dep_name} manquant")
        
        return critical_deps
    
    def install_missing_dependencies(self, missing_deps: List[str]):
        """Installe les dépendances manquantes"""
        if not missing_deps:
            print_success("Toutes les dépendances sont installées")
            return
            
        print_status(f"Installation de {len(missing_deps)} dépendances manquantes...")
        
        for dep in missing_deps:
            try:
                print_status(f"Installation de {dep}...")
                subprocess.run([
                    sys.executable, "-m", "pip", "install", dep
                ], check=True, capture_output=True)
                print_success(f"✅ {dep} installé")
                self.fixes_applied.append(f"Installé dépendance: {dep}")
            except subprocess.CalledProcessError as e:
                print_error(f"Échec installation {dep}: {e}")
    
    def fix_transport_method_imports(self):
        """Corrige les imports TransportMethod → TravelMode"""
        print_status("Correction des imports TransportMethod...")
        
        files_fixed = 0
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Pattern 1: Import direct de TransportMethod
                content = re.sub(
                    r'from nextvision\.models\.extended_matching_models_v3 import.*TransportMethod',
                    'from nextvision.models.transport_models import TravelMode',
                    content
                )
                
                # Pattern 2: Usage de TransportMethod dans le code
                content = re.sub(
                    r'\bTransportMethod\b',
                    'TravelMode',
                    content
                )
                
                # Pattern 3: Imports multiples avec TransportMethod
                content = re.sub(
                    r'from nextvision\.models\.extended_matching_models_v3 import \((.*?)TransportMethod(.*?)\)',
                    r'from nextvision.models.extended_matching_models_v3 import (\1\2)\nfrom nextvision.models.transport_models import TravelMode',
                    content,
                    flags=re.DOTALL
                )
                
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print_success(f"✅ Corrigé TransportMethod dans: {py_file.name}")
                    files_fixed += 1
                    self.fixes_applied.append(f"Corrigé TransportMethod: {py_file}")
                    
            except Exception as e:
                print_error(f"Erreur correction {py_file}: {e}")
        
        if files_fixed > 0:
            print_success(f"TransportMethod corrigé dans {files_fixed} fichiers")
        else:
            print_success("Aucun import TransportMethod trouvé à corriger")
    
    def fix_absolute_imports(self):
        """Corrige les imports relatifs en imports absolus"""
        print_status("Correction des imports relatifs...")
        
        files_fixed = 0
        
        for py_file in self.python_files:
            if "nextvision" not in str(py_file):
                continue  # Skip non-nextvision files
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Correction imports relatifs vers absolus
                relative_patterns = [
                    (r'from \.([a-zA-Z_][a-zA-Z0-9_]*) import', r'from nextvision.\1 import'),
                    (r'from \.\.([a-zA-Z_][a-zA-Z0-9_]*) import', r'from nextvision.\1 import'),
                    (r'from \.\.\.([a-zA-Z_][a-zA-Z0-9_]*) import', r'from nextvision.\1 import'),
                ]
                
                for pattern, replacement in relative_patterns:
                    content = re.sub(pattern, replacement, content)
                
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print_success(f"✅ Corrigé imports relatifs dans: {py_file.name}")
                    files_fixed += 1
                    self.fixes_applied.append(f"Corrigé imports relatifs: {py_file}")
                    
            except Exception as e:
                print_error(f"Erreur correction imports {py_file}: {e}")
        
        if files_fixed > 0:
            print_success(f"Imports relatifs corrigés dans {files_fixed} fichiers")
        else:
            print_success("Aucun import relatif trouvé à corriger")
    
    def create_missing_init_files(self):
        """Crée les fichiers __init__.py manquants"""
        print_status("Vérification fichiers __init__.py...")
        
        required_init_dirs = [
            "nextvision",
            "nextvision/models",
            "nextvision/services", 
            "nextvision/services/parsing",
            "nextvision/services/scorers_v3",
            "nextvision/engines",
            "nextvision/utils",
            "nextvision/core",
            "nextvision/api"
        ]
        
        created_files = 0
        
        for dir_path in required_init_dirs:
            full_path = self.project_root / dir_path
            init_file = full_path / "__init__.py"
            
            if full_path.exists() and not init_file.exists():
                try:
                    with open(init_file, 'w', encoding='utf-8') as f:
                        f.write(f'"""\n{dir_path} module\n"""\n')
                    
                    print_success(f"✅ Créé: {init_file}")
                    created_files += 1
                    self.fixes_applied.append(f"Créé __init__.py: {init_file}")
                    
                except Exception as e:
                    print_error(f"Erreur création {init_file}: {e}")
        
        if created_files > 0:
            print_success(f"{created_files} fichiers __init__.py créés")
        else:
            print_success("Tous les __init__.py requis sont présents")
    
    def test_critical_imports(self) -> Dict[str, bool]:
        """Teste les imports critiques pour l'intégration"""
        print_status("Test des imports critiques...")
        
        critical_imports = {
            'requests': 'import requests',
            'TravelMode': 'from nextvision.models.transport_models import TravelMode',
            'Enhanced Bridge': 'from nextvision.services.enhanced_commitment_bridge_v3_integrated import EnhancedCommitmentBridgeV3Integrated',
            'Parsing Bridge': 'from nextvision.services.parsing.commitment_bridge_optimized import CommitmentParsingBridge',
            'Extended Models': 'from nextvision.models.extended_matching_models_v3 import ExtendedMatchingProfile'
        }
        
        results = {}
        
        for name, import_stmt in critical_imports.items():
            try:
                exec(import_stmt)
                results[name] = True
                print_success(f"✅ {name} import OK")
            except Exception as e:
                results[name] = False
                print_warning(f"⚠️ {name} import échoué: {e}")
        
        return results
    
    def create_requirements_integration(self):
        """Crée un requirements.txt spécifique pour l'intégration"""
        print_status("Création requirements-integration.txt...")
        
        integration_requirements = """# NEXTVISION V3.0 + COMMITMENT- INTEGRATION REQUIREMENTS

# === CORE DEPENDENCIES ===
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
python-dotenv>=1.0.0

# === HTTP & ASYNC ===
requests>=2.31.0
aiohttp>=3.9.0
httpx>=0.25.0
aiofiles>=23.2.1
asyncio-throttle>=1.0.2

# === PARSING & AUTOMATION ===
playwright>=1.40.0
python-multipart>=0.0.6

# === GOOGLE MAPS INTELLIGENCE ===
geopy>=2.4.0
shapely>=2.0.2
numpy>=1.24.0

# === DATA PROCESSING ===
dataclasses-json>=0.6.1
orjson>=3.9.9

# === CACHE & PERFORMANCE ===
redis>=5.0.0
aioredis>=2.0.1
pickle-mixin>=1.0.2

# === TESTING ===
pytest>=7.4.3
pytest-asyncio>=0.21.1
pytest-mock>=3.12.0

# === LOGGING & MONITORING ===
structlog>=23.2.0

# === SECURITY ===
cryptography>=41.0.7

# === CONFIGURATION ===
pyyaml>=6.0.1
toml>=0.10.2

# === DEVELOPMENT ===
typing-extensions>=4.8.0
"""
        
        try:
            with open(self.project_root / "requirements-integration.txt", 'w', encoding='utf-8') as f:
                f.write(integration_requirements)
            
            print_success("✅ requirements-integration.txt créé")
            self.fixes_applied.append("Créé requirements-integration.txt")
            
        except Exception as e:
            print_error(f"Erreur création requirements-integration.txt: {e}")
    
    def setup_python_path(self):
        """Configure le PYTHONPATH pour l'intégration"""
        print_status("Configuration PYTHONPATH...")
        
        current_path = str(self.project_root)
        
        # Ajouter au PYTHONPATH pour cette session
        if current_path not in sys.path:
            sys.path.insert(0, current_path)
            print_success(f"✅ {current_path} ajouté au PYTHONPATH")
            self.fixes_applied.append(f"PYTHONPATH configuré: {current_path}")
    
    def run_full_fix(self):
        """Lance la correction complète"""
        print_status("🚀 LANCEMENT CORRECTION COMPLÈTE INTÉGRATION")
        print_status("=" * 60)
        
        # 1. Scan fichiers
        self.scan_python_files()
        
        # 2. Setup Python path
        self.setup_python_path()
        
        # 3. Vérification dépendances
        deps_status = self.check_dependencies()
        missing_deps = [dep for dep, installed in deps_status.items() if not installed]
        
        # 4. Installation dépendances manquantes
        if missing_deps:
            self.install_missing_dependencies(missing_deps)
        
        # 5. Création __init__.py manquants
        self.create_missing_init_files()
        
        # 6. Correction imports TransportMethod
        self.fix_transport_method_imports()
        
        # 7. Correction imports relatifs
        self.fix_absolute_imports()
        
        # 8. Création requirements intégration
        self.create_requirements_integration()
        
        # 9. Test imports critiques
        import_results = self.test_critical_imports()
        
        # 10. Résumé
        self.print_summary(import_results)
        
        return len(self.fixes_applied), import_results
    
    def print_summary(self, import_results: Dict[str, bool]):
        """Affiche le résumé des corrections"""
        print_status("\n" + "=" * 60)
        print_status("📊 RÉSUMÉ CORRECTION INTÉGRATION")
        print_status("=" * 60)
        
        print_success(f"✅ {len(self.fixes_applied)} corrections appliquées:")
        for fix in self.fixes_applied:
            print(f"   • {fix}")
        
        print_status(f"\n📋 Status imports critiques:")
        success_count = sum(import_results.values())
        total_count = len(import_results)
        
        for name, success in import_results.items():
            status = "✅" if success else "❌"
            print(f"   {status} {name}")
        
        print_status(f"\n🎯 Score d'intégration: {success_count}/{total_count}")
        
        if success_count == total_count:
            print_success("\n🎉 INTÉGRATION PARFAITEMENT CORRIGÉE!")
            print_status("Prochaines étapes:")
            print("   1. Configurer les API keys dans .env")
            print("   2. Lancer: python3 test_nextvision_commitment_integration.py")
        elif success_count >= total_count * 0.8:
            print_warning("\n⚠️ INTÉGRATION MAJORITAIREMENT CORRIGÉE")
            print_status("Quelques imports peuvent nécessiter une configuration supplémentaire")
        else:
            print_error("\n❌ INTÉGRATION PARTIELLEMENT CORRIGÉE")
            print_status("Vérifier la configuration et les dépendances manquantes")

def main():
    """Point d'entrée principal"""
    print("🔧 NEXTVISION INTEGRATION FIXER")
    print("=" * 50)
    
    # Détection du répertoire du projet
    project_root = os.getcwd()
    if "nextvision" in os.listdir(project_root):
        print_success(f"Projet Nextvision détecté dans: {project_root}")
    else:
        print_error("Projet Nextvision non détecté dans le répertoire courant")
        print_status("Assurez-vous d'être dans le répertoire racine de Nextvision")
        sys.exit(1)
    
    # Lancement correction
    fixer = NextvisionIntegrationFixer(project_root)
    
    try:
        fixes_count, import_results = fixer.run_full_fix()
        
        # Code de sortie basé sur le succès
        success_rate = sum(import_results.values()) / len(import_results)
        
        if success_rate >= 0.9:
            sys.exit(0)  # Succès complet
        elif success_rate >= 0.7:
            sys.exit(1)  # Succès partiel
        else:
            sys.exit(2)  # Échec
            
    except Exception as e:
        print_error(f"Erreur critique: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()
