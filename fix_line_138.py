#!/usr/bin/env python3
"""🎯 CORRECTION LIGNE 138 SPÉCIFIQUE"""

from pathlib import Path

def fix_specific_line_138():
    """Corrige spécifiquement la ligne 138"""
    print("🎯 Correction ligne 138 spécifique...")
    
    bridge_file = Path("nextvision/services/enhanced_commitment_bridge_v3_integrated.py")
    if not bridge_file.exists():
        print("⚠️ Fichier Enhanced Bridge non trouvé")
        return False
    
    with open(bridge_file, 'r') as f:
        lines = f.readlines()
    
    print(f"📄 Fichier a {len(lines)} lignes")
    
    # Examiner autour de la ligne 138
    if len(lines) >= 138:
        print(f"🔍 Ligne 138: {lines[137].strip()}")
        
        # Chercher la fonction contenant la ligne 138
        function_start = None
        for i in range(137, -1, -1):
            if lines[i].strip().startswith('def ') and not 'async def' in lines[i]:
                function_start = i
                function_name = lines[i].strip().split('(')[0].replace('def ', '')
                print(f"📍 Fonction trouvée: {function_name} à la ligne {i + 1}")
                break
        
        # Rendre la fonction async
        if function_start is not None:
            if 'async def' not in lines[function_start]:
                lines[function_start] = lines[function_start].replace('def ', 'async def ')
                print(f"✅ Fonction rendue async: ligne {function_start + 1}")
            
            # Sauvegarder
            with open(bridge_file, 'w') as f:
                f.writelines(lines)
            
            print("💾 Fichier sauvegardé")
            return True
    else:
        print("❌ Fichier trop court, ligne 138 non trouvée")
        return False

def main():
    print("🎯 CORRECTION LIGNE 138 NEXTVISION V3.0")
    print("=" * 50)
    
    success = fix_specific_line_138()
    return success

if __name__ == "__main__":
    main()
