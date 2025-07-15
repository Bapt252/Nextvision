#!/usr/bin/env python3
"""
🔧 NEXTVISION V3.2.1 - PATCH RAPIDE ERREUR RAISONECOUTE
========================================================

Corrige l'erreur "RaisonEcoute has no attribute RECHERCHE_NOUVEAU_DEFI"
dans le script integration_transport_v321.py

Author: NEXTEN Team
Version: 3.2.1 - Hotfix
"""

import os
import sys

def fix_integration_script():
    """🔧 Corrige l'erreur RaisonEcoute dans integration_transport_v321.py"""
    
    script_file = "integration_transport_v321.py"
    
    if not os.path.exists(script_file):
        print(f"❌ Fichier {script_file} non trouvé")
        return False
    
    # Lecture du fichier
    try:
        with open(script_file, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"📖 Lecture de {script_file} réussie")
    except Exception as e:
        print(f"❌ Erreur lecture: {e}")
        return False
    
    # Correction 1: Remplacer RECHERCHE_NOUVEAU_DEFI par POSTE_INADEQUAT
    old_line = "raison_ecoute = raison_mapping.get(pourquoi_ecoute, RaisonEcoute.RECHERCHE_NOUVEAU_DEFI)"
    new_line = "raison_ecoute = raison_mapping.get(pourquoi_ecoute, RaisonEcoute.POSTE_INADEQUAT)"
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        print("✅ Correction RECHERCHE_NOUVEAU_DEFI → POSTE_INADEQUAT")
    else:
        print("⚠️ Ligne à corriger non trouvée (peut-être déjà corrigée?)")
    
    # Sauvegarde
    try:
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ {script_file} corrigé avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur écriture: {e}")
        return False

def main():
    """🚀 Point d'entrée principal"""
    
    print("🔧 NEXTVISION V3.2.1 - PATCH RAPIDE ERREUR RAISONECOUTE")
    print("=" * 60)
    print("Corrige l'erreur 'RaisonEcoute has no attribute RECHERCHE_NOUVEAU_DEFI'")
    print()
    
    # Vérification environnement
    if not os.path.exists("integration_transport_v321.py"):
        print("❌ Erreur: Ce patch doit être exécuté depuis le répertoire Nextvision/")
        print("💡 Assurez-vous d'être dans le bon répertoire")
        sys.exit(1)
    
    # Application du patch
    if fix_integration_script():
        print()
        print("🎯 PATCH APPLIQUÉ AVEC SUCCÈS !")
        print("=" * 40)
        print("✅ Erreur RaisonEcoute corrigée")
        print("🧪 Relancez maintenant le test:")
        print("python integration_transport_v321.py")
        print()
        print("CHANGEMENT EFFECTUÉ:")
        print("• RaisonEcoute.RECHERCHE_NOUVEAU_DEFI → RaisonEcoute.POSTE_INADEQUAT")
    else:
        print()
        print("❌ Échec de l'application du patch")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
