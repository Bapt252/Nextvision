#!/usr/bin/env python3
"""
⚡ Test rapide des imports critiques - Validation immédiate
"""

def test_critical_imports():
    print("🔧 Test des imports critiques corrigés...")
    
    # Test 1: BidirectionalScorer (était manquant)
    try:
        from nextvision.services.bidirectional_scorer import BidirectionalScorer
        print("✅ BidirectionalScorer: OK")
    except Exception as e:
        print(f"❌ BidirectionalScorer: {e}")
        return False
    
    # Test 2: MotivationsScorerV3 (alias était manquant)
    try:
        from nextvision.services.motivations_scorer_v3 import MotivationsScorerV3
        print("✅ MotivationsScorerV3: OK")
    except Exception as e:
        print(f"❌ MotivationsScorerV3: {e}")
        return False
    
    # Test 3: Import depuis services/__init__.py
    try:
        from nextvision.services import BidirectionalScorer, MotivationsScorerV3
        print("✅ Import depuis services.__init__: OK")
    except Exception as e:
        print(f"❌ Import depuis services.__init__: {e}")
        return False
    
    print("🎉 Tous les imports critiques fonctionnent !")
    return True

if __name__ == "__main__":
    success = test_critical_imports()
    if success:
        print("\n🚀 PRÊT POUR TEST COUVERTURE >70% !")
    else:
        print("\n⚠️ Corrections supplémentaires nécessaires")
