#!/usr/bin/env python3
"""
🧪 Test rapide intégration Nextvision + Commitment-
"""

import sys
import asyncio
sys.path.append('.')

async def test_quick_integration():
    print("🧪 === TEST RAPIDE INTÉGRATION ===")
    
    try:
        # Test 1: Imports
        print("1. Test imports...")
        from nextvision.models.transport_models import TravelMode
        from nextvision.services.enhanced_commitment_bridge_v3_integrated import IntegratedBridgeFactory
        print("✅ Imports OK")
        
        # Test 2: Création bridge
        print("2. Test bridge...")
        bridge = IntegratedBridgeFactory.create_development_integrated_bridge()
        print("✅ Bridge créé")
        
        # Test 3: Health check
        print("3. Test health...")
        health = bridge.get_integration_health()
        print(f"✅ Health: {health['status']}")
        
        # Test 4: Candidat simple
        print("4. Test candidat...")
        candidat_result, metrics = await bridge.convert_candidat_enhanced_integrated(
            parser_output=None,
            cv_file_path=None,
            questionnaire_data={"test": "data"},
            enable_real_parsing=False
        )
        print("✅ Candidat créé")
        
        await bridge.close()
        print("\n🎉 INTÉGRATION FONCTIONNELLE!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_quick_integration())
    sys.exit(0 if success else 1)
