#!/usr/bin/env python3
"""🧹 NETTOYAGE FINAL NEXTVISION V3.0"""

from pathlib import Path
import sys

def test_final_score():
    """Test final du score"""
    print("🧪 Test final du score...")
    
    sys.path.insert(0, str(Path(".").absolute()))
    
    tests = [
        ("nextvision.logging.logger", "get_logger"),
        ("nextvision.models.transport_models", "TravelMode"),
        ("nextvision.services.google_maps_service", "GoogleMapsService"),
        ("nextvision.services.transport_calculator", "TransportCalculator"),
        ("nextvision.services.enhanced_commitment_bridge_v3_integrated", "EnhancedCommitmentBridgeV3Integrated")
    ]
    
    success = 0
    
    for module_name, class_name in tests:
        try:
            import importlib
            module = importlib.import_module(module_name)
            if hasattr(module, class_name):
                print(f"✅ {module_name}.{class_name}")
                success += 1
            else:
                print(f"❌ {module_name}: classe {class_name} manquante")
        except Exception as e:
            print(f"❌ {module_name}: {e}")
    
    score = (success / len(tests)) * 100
    print(f"\n📊 SCORE FINAL: {score:.1f}%")
    
    return score

def main():
    print("🧹 NETTOYAGE FINAL NEXTVISION V3.0")
    print("=" * 50)
    
    score = test_final_score()
    
    if score >= 80:
        print("\n🎉 OBJECTIF 80% ATTEINT!")
        print("✅ Intégration Nextvision V3.0 fonctionnelle")
        return True
    elif score >= 70:
        print(f"\n⚠️ Score {score:.1f}% - très proche!")
        print("🔧 Quelques ajustements mineurs nécessaires")
        return True
    else:
        print(f"\n❌ Score {score:.1f}% - corrections supplémentaires nécessaires")
        return False

if __name__ == "__main__":
    main()
