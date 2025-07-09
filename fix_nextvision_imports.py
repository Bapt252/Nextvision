#!/usr/bin/env python3
"""
🔧 CORRECTION IMPORTS NEXTVISION
Script pour corriger les imports incorrects détectés par les tests

Author: Assistant Claude  
Version: 1.0.0
"""

import os
import re
import glob
from pathlib import Path

def print_status(message: str):
    print(f"🔧 [INFO] {message}")

def print_success(message: str):
    print(f"✅ [SUCCESS] {message}")

def print_error(message: str):
    print(f"❌ [ERROR] {message}")

def fix_imports_in_file(file_path: str) -> bool:
    """Corrige les imports dans un fichier spécifique"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = False
        
        # Correction 1: nextvision.questionnaire_advanced → nextvision.models.questionnaire_advanced
        if 'nextvision.questionnaire_advanced' in content:
            content = content.replace(
                'from nextvision.questionnaire_advanced',
                'from nextvision.models.questionnaire_advanced'
            )
            content = content.replace(
                'import nextvision.questionnaire_advanced',
                'import nextvision.models.questionnaire_advanced'
            )
            changes_made = True
            print_success(f"Corrigé questionnaire_advanced dans: {file_path}")
        
        # Correction 2: Supprimer les imports commitment_bridge (inexistants)
        problematic_imports = [
            'from nextvision.commitment_bridge',
            'import nextvision.commitment_bridge',
            'from nextvision.services.commitment_bridge',
            'import nextvision.services.commitment_bridge'
        ]
        
        for bad_import in problematic_imports:
            if bad_import in content:
                # Supprimer les lignes d'import problématiques
                lines = content.split('\n')
                new_lines = []
                
                for line in lines:
                    if bad_import in line:
                        print_success(f"Supprimé import problématique: {line.strip()}")
                        changes_made = True
                        # Ne pas ajouter cette ligne
                        continue
                    new_lines.append(line)
                
                content = '\n'.join(new_lines)
        
        # Correction 3: Ajout des imports corrects si nécessaire
        if 'Enhanced Bridge' in content or 'EnhancedCommitmentBridge' in content:
            # Si le fichier utilise Enhanced Bridge, s'assurer d'avoir les bons imports
            if 'from nextvision.services.enhanced_commitment_bridge_v3_integrated' not in content:
                # Ajouter l'import correct au début du fichier
                lines = content.split('\n')
                import_added = False
                
                for i, line in enumerate(lines):
                    if line.startswith('from nextvision') or line.startswith('import nextvision'):
                        lines.insert(i, 'from nextvision.services.enhanced_commitment_bridge_v3_integrated import EnhancedCommitmentBridgeV3Integrated, IntegratedBridgeFactory')
                        import_added = True
                        changes_made = True
                        break
                
                if import_added:
                    content = '\n'.join(lines)
                    print_success(f"Ajouté import Enhanced Bridge dans: {file_path}")
        
        # Sauvegarder si des changements ont été faits
        if changes_made and content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print_error(f"Erreur dans {file_path}: {e}")
        return False

def main():
    """Point d'entrée principal"""
    
    print("🔧 CORRECTION IMPORTS NEXTVISION")
    print("=" * 50)
    
    # Rechercher tous les fichiers Python dans le projet
    python_files = []
    
    # Chercher dans nextvision/ et les fichiers racine
    for pattern in ["nextvision/**/*.py", "*.py"]:
        python_files.extend(glob.glob(pattern, recursive=True))
    
    print_status(f"Analyse de {len(python_files)} fichiers Python...")
    
    files_modified = 0
    
    for file_path in python_files:
        # Ignorer les fichiers de test et __pycache__
        if '__pycache__' in file_path or file_path.endswith('.pyc'):
            continue
            
        if fix_imports_in_file(file_path):
            files_modified += 1
    
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ CORRECTION IMPORTS")
    print("=" * 50)
    
    if files_modified > 0:
        print_success(f"✅ {files_modified} fichiers corrigés")
        print_status("Corrections appliquées:")
        print("  • nextvision.questionnaire_advanced → nextvision.models.questionnaire_advanced")
        print("  • Suppression imports commitment_bridge inexistants")
        print("  • Ajout imports Enhanced Bridge corrects")
    else:
        print_status("Aucune correction nécessaire")
    
    print("\n📋 PROCHAINES ÉTAPES:")
    print("1. Relancer: python3 test_integration_simple.py")
    print("2. Score attendu: > 70%")
    print("=" * 50)

if __name__ == "__main__":
    main()
