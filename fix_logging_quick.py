#!/usr/bin/env python3
"""
🔧 Quick Fix pour les imports logging Nextvision
Remplace nextvision_logging par logging standard
"""

import os
import re

def fix_logging_imports():
    """Corrige les imports logging dans tout le projet"""
    
    print("🔧 Correction des imports logging...")
    
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
            
            # Vérifier si le fichier contient l'import problématique
            if "import nextvision_logging as logging" in content:
                print(f"📝 Correction: {file_path}")
                
                # Remplacer l'import
                content = content.replace(
                    "import nextvision_logging as logging",
                    "import logging"
                )
                
                # Écrire le fichier corrigé
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixed_count += 1
                
        except Exception as e:
            print(f"❌ Erreur avec {file_path}: {e}")
    
    print(f"✅ {fixed_count} fichiers corrigés")

if __name__ == "__main__":
    fix_logging_imports()
    print("🎉 Correction terminée !")
