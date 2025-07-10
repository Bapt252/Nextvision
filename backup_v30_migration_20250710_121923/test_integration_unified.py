#!/usr/bin/env python3
"""
🧪 TEST INTÉGRATION UNIFIÉ NEXTVISION V3.0
Script de test unique pour valider l'intégration complète

Author: Assistant Claude  
Version: 1.0.0-unified
"""

import sys
import time
import importlib
from pathlib import Path

def test_critical_imports():
    """Test des imports critiques"""
    
    critical_imports = [
        ("nextvision.services.google_maps_service", "GoogleMapsService"),
        ("nextvision.services.transport_calculator", "TransportCalculator"), 
        ("nextvision.models.transport_models", "TravelMode"),
        ("nextvision.models.extended_matching_models_v3", "ExtendedMatchingProfile"),
        ("nextvision.logging.logger", "get_logger")
    ]
    
    success_count = 0
    total_count = len(critical_imports)
    
    print("🧪 === TEST IMPORTS CRITIQUES ===")
    
    for module_name, class_name in critical_imports:
        try:
            module = importlib.import_module(module_name)
            
            if hasattr(module, class_name):
                print(f"✅ {module_name}.{class_name}")
                success_count += 1
            else:
                print(f"❌ {module_name}.{class_name} - Classe manquante")
        
        except ImportError as e:
            print(f"❌ {module_name} - Import Error: {e}")
        except Exception as e:
            print(f"❌ {module_name} - Erreur: {e}")
    
    return success_count, total_count

def test_enhanced_bridge():
    """Test Enhanced Bridge simplifié"""
    
    print("\n🌉 === TEST ENHANCED BRIDGE ===")
    
    try:
        from nextvision.services.enhanced_commitment_bridge_v3_simplified import SimplifiedBridgeFactory
        
        bridge = SimplifiedBridgeFactory.create_bridge()
        stats = bridge.get_stats()
        
        print(f"✅ Bridge Type: {stats['bridge_type']}")
        print(f"✅ Version: {stats['version']}")
        print(f"✅ Integration Score: {stats['integration_score']}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Bridge Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Bridge Error: {e}")
        return False

def calculate_integration_score(import_success: int, import_total: int, bridge_success: bool) -> float:
    """Calcul score d'intégration unifié"""
    
    # Score imports (60% du total)
    import_score = (import_success / import_total) * 60
    
    # Score bridge (40% du total)  
    bridge_score = 40 if bridge_success else 0
    
    total_score = import_score + bridge_score
    
    return round(total_score, 1)

def main():
    """Test principal d'intégration"""
    
    print("🚀 === TEST INTÉGRATION NEXTVISION V3.0 UNIFIÉ ===")
    print("=" * 55)
    
    start_time = time.time()
    
    # Test imports
    import_success, import_total = test_critical_imports()
    
    # Test bridge
    bridge_success = test_enhanced_bridge()
    
    # Calcul score final
    integration_score = calculate_integration_score(import_success, import_total, bridge_success)
    
    # Rapport final
    duration = time.time() - start_time
    
    print(f"\n📊 === RÉSULTATS FINAUX ===")
    print(f"⏱️ Durée: {duration:.2f}s")
    print(f"📦 Imports: {import_success}/{import_total} ({import_success/import_total*100:.1f}%)")
    print(f"🌉 Bridge: {'✅ OK' if bridge_success else '❌ KO'}")
    print(f"🎯 SCORE INTÉGRATION: {integration_score}%")
    
    if integration_score >= 80:
        print("🎉 INTÉGRATION RÉUSSIE!")
    elif integration_score >= 60:
        print("⚠️ Intégration partielle - corrections mineures nécessaires")
    else:
        print("❌ Intégration problématique - corrections majeures requises")
    
    print("=" * 55)
    
    return integration_score

if __name__ == "__main__":
    score = main()
    sys.exit(0 if score >= 80 else 1)
