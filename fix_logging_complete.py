#!/usr/bin/env python3
"""
🔧 Fix Complet pour tous les imports Nextvision
Corrige tous les problèmes d'imports logging
"""

import os
import re

def fix_all_logging_imports():
    """Corrige tous les imports logging dans le projet"""
    
    print("🔧 Correction complète des imports logging...")
    
    # Patterns à corriger
    import_fixes = [
        # Ancien -> Nouveau
        ("import nextvision_logging as logging", "import logging"),
        ("from nextvision.logging.logger import get_logger", "import logging\n\ndef get_logger(name):\n    return logging.getLogger(name)"),
        ("from nextvision.logging import get_logger", "import logging\n\ndef get_logger(name):\n    return logging.getLogger(name)"),
        ("from nextvision_logging import", "from logging import"),
        ("nextvision_logging.getLogger", "logging.getLogger"),
        ("nextvision.logging.logger.get_logger", "logging.getLogger"),
    ]
    
    # Fichiers à corriger
    files_to_fix = []
    
    # Recherche récursive des fichiers Python
    for root, dirs, files in os.walk("nextvision"):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                files_to_fix.append(file_path)
    
    # Ajout des fichiers racine
    root_files = ["main.py", "main_production.py"]
    for file in root_files:
        if os.path.exists(file):
            files_to_fix.append(file)
    
    fixed_count = 0
    
    for file_path in files_to_fix:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Appliquer tous les fixes
            for old_pattern, new_pattern in import_fixes:
                if old_pattern in content:
                    print(f"📝 Correction '{old_pattern}' dans: {file_path}")
                    content = content.replace(old_pattern, new_pattern)
            
            # Corrections spécifiques pour les loggers
            if "get_logger(__name__)" in content and "def get_logger" not in content:
                # Ajouter la fonction get_logger si elle est utilisée mais pas définie
                if "import logging" in content:
                    content = content.replace(
                        "import logging",
                        "import logging\n\ndef get_logger(name):\n    return logging.getLogger(name)"
                    )
            
            # Écrire le fichier si modifié
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_count += 1
                
        except Exception as e:
            print(f"❌ Erreur avec {file_path}: {e}")
    
    print(f"✅ {fixed_count} fichiers corrigés")

def fix_specific_files():
    """Correction spécifique pour les fichiers problématiques"""
    
    # Fix pour enhanced_commitment_bridge_v3_integrated.py
    problem_file = "nextvision/services/enhanced_commitment_bridge_v3_integrated.py"
    
    if os.path.exists(problem_file):
        print(f"🎯 Correction spécifique: {problem_file}")
        
        try:
            with open(problem_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remplacer l'import problématique
            content = content.replace(
                "from nextvision.logging.logger import get_logger",
                "import logging\n\ndef get_logger(name):\n    return logging.getLogger(name)"
            )
            
            with open(problem_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"✅ {problem_file} corrigé")
            
        except Exception as e:
            print(f"❌ Erreur avec {problem_file}: {e}")

def create_minimal_logging_module():
    """Crée un module logging minimal si nécessaire"""
    
    # Créer le dossier logging s'il n'existe pas
    logging_dir = "nextvision/logging"
    if not os.path.exists(logging_dir):
        os.makedirs(logging_dir)
        print(f"📁 Dossier créé: {logging_dir}")
    
    # Créer __init__.py
    init_file = os.path.join(logging_dir, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write("""# Nextvision Logging Module
import logging

def get_logger(name):
    return logging.getLogger(name)
""")
        print(f"✅ Créé: {init_file}")
    
    # Créer logger.py
    logger_file = os.path.join(logging_dir, "logger.py")
    if not os.path.exists(logger_file):
        with open(logger_file, 'w') as f:
            f.write("""# Nextvision Logger
import logging

def get_logger(name):
    return logging.getLogger(name)
""")
        print(f"✅ Créé: {logger_file}")

if __name__ == "__main__":
    print("🚀 CORRECTION COMPLÈTE DES IMPORTS LOGGING")
    print("=" * 50)
    
    # 1. Corrections générales
    fix_all_logging_imports()
    
    # 2. Corrections spécifiques
    fix_specific_files()
    
    # 3. Création module logging minimal
    create_minimal_logging_module()
    
    print("\n🎉 CORRECTION TERMINÉE!")
    print("💡 Essayez maintenant: python main.py")
