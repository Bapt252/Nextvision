#!/usr/bin/env python3
"""🔧 CORRECTION ERREUR ASYNC NEXTVISION V3.0"""

from pathlib import Path
import re

def fix_async_syntax():
    """Corrige l'erreur await outside async function"""
    print("🔧 Correction erreur async/await...")
    
    bridge_file = Path("nextvision/services/enhanced_commitment_bridge_v3_integrated.py")
    if not bridge_file.exists():
        print("⚠️ Fichier Enhanced Bridge non trouvé")
        return False
    
    with open(bridge_file, 'r') as f:
        content = f.read()
    
    # Identifier les fonctions avec await qui ne sont pas async
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        # Si une ligne contient 'await' et la fonction n'est pas async
        if 'await' in line and not line.strip().startswith('#'):
            # Chercher la définition de fonction correspondante
            func_start = None
            for j in range(i, -1, -1):
                if lines[j].strip().startswith('def ') and not lines[j].strip().startswith('def __'):
                    func_start = j
                    break
            
            # Si on trouve une fonction, la rendre async
            if func_start is not None and 'async def' not in lines[func_start]:
                lines[func_start] = lines[func_start].replace('def ', 'async def ')
                print(f"  ✅ Fonction rendue async: ligne {func_start + 1}")
        
        new_lines.append(line)
    
    # Corrections spécifiques
    content = '\n'.join(new_lines)
    
    # S'assurer que les méthodes principales sont async
    async_methods = [
        'convert_candidat_enhanced_integrated',
        'convert_entreprise_enhanced_integrated'
    ]
    
    for method in async_methods:
        pattern = f'def {method}('
        replacement = f'async def {method}('
        if pattern in content and replacement not in content:
            content = content.replace(pattern, replacement)
            print(f"  ✅ Méthode {method} rendue async")
    
    # Sauvegarder
    with open(bridge_file, 'w') as f:
        f.write(content)
    
    print("✅ Erreurs async corrigées")
    return True

def main():
    print("🔧 CORRECTION ERREUR ASYNC NEXTVISION V3.0")
    print("=" * 50)
    
    success = fix_async_syntax()
    
    if success:
        print("\n✅ Corrections async appliquées")
        print("🧪 Testez maintenant:")
        print("  python3 diagnose_nextvision_imports.py")
    else:
        print("\n❌ Échec correction async")
    
    return success

if __name__ == "__main__":
    main()
