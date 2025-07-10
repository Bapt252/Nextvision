#!/usr/bin/env python3
"""🚀 CORRECTION ULTRA-RAPIDE NEXTVISION V3.0"""

import os
import sys
from pathlib import Path

def main():
    print("🚀 CORRECTION ULTRA-RAPIDE NEXTVISION V3.0")
    print("=" * 50)
    
    # 1. Correction Enhanced Bridge (import circulaire)
    enhanced_bridge = Path("nextvision/services/enhanced_commitment_bridge_v3_integrated.py")
    if enhanced_bridge.exists():
        with open(enhanced_bridge, 'r') as f:
            content = f.read()
        
        # Fixes critiques pour import circulaire
        content = content.replace(
            "class EnhancedCommitmentBridgeV3Integrated(OriginalBridgeV3):",
            "class EnhancedCommitmentBridgeV3Integrated:"
        )
        content = content.replace(
            "super().__init__()",
            """# Import local pour éviter import circulaire
        from nextvision.services.enhanced_commitment_bridge_v3 import EnhancedCommitmentBridgeV3
        self.enhanced_bridge_v3 = EnhancedCommitmentBridgeV3()"""
        )
        content = content.replace(
            "await super().convert_candidat_enhanced_v3(",
            "await self.enhanced_bridge_v3.convert_candidat_enhanced_v3("
        )
        content = content.replace(
            "await super().convert_entreprise_enhanced_v3(",
            "await self.enhanced_bridge_v3.convert_entreprise_enhanced_v3("
        )
        
        with open(enhanced_bridge, 'w') as f:
            f.write(content)
        print("✅ Enhanced Bridge corrigé")
    
    # 2. Correction TravelMode → TravelMode dans tous les fichiers
    python_files = list(Path(".").rglob("*.py"))
    corrections = 0
    
    for file_path in python_files:
        if any(skip in str(file_path) for skip in ["backup", "__pycache__", ".git"]):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            
            # Fixes TravelMode
            content = content.replace("TravelMode", "TravelMode")
            content = content.replace("from nextvision.models.transport_models import TravelMode", 
                                    "from nextvision.models.transport_models import TravelMode")
            
            # Fixes imports services
            content = content.replace("from nextvision.services.google_maps_service import", 
                                    "from nextvision.services.google_maps_service import")
            content = content.replace("from nextvision.services.transport_calculator import", 
                                    "from nextvision.services.transport_calculator import")
            content = content.replace("from nextvision.services.scorers_v3.location_transport_scorer_v3 import", 
                                    "from nextvision.services.scorers_v3.location_transport_scorer_v3 import")
            
            if content != original:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                corrections += 1
        except:
            pass
    
    print(f"✅ {corrections} fichiers corrigés")
    
    # 3. Test rapide
    sys.path.insert(0, str(Path(".").absolute()))
    
    success_count = 0
    try:
        from nextvision.models.transport_models import TravelMode
        print("✅ TravelMode importé")
        success_count += 1
    except Exception as e:
        print(f"❌ TravelMode: {e}")
    
    try:
        from nextvision.services.google_maps_service import GoogleMapsService
        print("✅ GoogleMapsService importé")
        success_count += 1
    except Exception as e:
        print(f"❌ GoogleMapsService: {e}")
    
    try:
        from nextvision.services.transport_calculator import TransportCalculator
        print("✅ TransportCalculator importé")
        success_count += 1
    except Exception as e:
        print(f"❌ TransportCalculator: {e}")
    
    score = (success_count / 3) * 100
    print(f"\n📊 SCORE ESTIMÉ: {score:.1f}%")
    
    if score >= 80:
        print("🎉 OBJECTIF 80% ATTEINT!")
        sys.exit(0)
    elif score >= 60:
        print("⚠️ Proche de l'objectif")
        sys.exit(1)
    else:
        print("❌ Corrections supplémentaires nécessaires")
        sys.exit(2)

if __name__ == "__main__":
    main()
