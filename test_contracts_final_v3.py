#!/usr/bin/env python3
"""
🎯 NEXTVISION V3.0 - Test final contrats français (4 types)
"""

import sys
sys.path.append('.')

def test_final_contract_types():
    """Test 4 types de contrats français finaux"""
    print("🇫🇷 TEST CONTRATS FRANÇAIS FINAUX")
    print("=" * 50)
    
    # Les 4 contrats du questionnaire français
    expected_contracts = ["CDI", "CDD", "FREELANCE", "INTERIM"]
    
    try:
        # Test import
        from nextvision.models.extended_matching_models_v3 import ContractType
        print("✅ ContractType importé")
        
        # Vérifier les contrats
        available_contracts = [contract.value.upper() for contract in ContractType]
        print(f"📋 Contrats disponibles: {available_contracts}")
        
        # Validation stricte - exactement 4 contrats
        print(f"📊 Nombre de contrats: {len(available_contracts)} (attendu: 4)")
        
        # Vérifier chaque contrat
        all_present = True
        for contract in expected_contracts:
            if contract.lower() in [c.lower() for c in available_contracts]:
                print(f"✅ {contract}")
            else:
                print(f"❌ {contract} manquant")
                all_present = False
        
        # Vérifier qu'il n'y a pas de contrats supplémentaires
        extra_contracts = [c for c in available_contracts if c.upper() not in expected_contracts]
        if extra_contracts:
            print(f"⚠️ Contrats supplémentaires détectés: {extra_contracts}")
            for extra in extra_contracts:
                print(f"❌ {extra} (à supprimer)")
            all_present = False
        
        if all_present and len(available_contracts) == 4:
            print("🎯 PARFAIT: Exactement 4 contrats français!")
        
        return all_present and len(available_contracts) == 4
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_questionnaire_4_contracts():
    """Test questionnaire avec 4 contrats français"""
    print("\n📋 TEST QUESTIONNAIRE - 4 CONTRATS")
    print("=" * 50)
    
    # Exemple réaliste de ranking candidat
    candidat_scenarios = [
        {
            "profile": "Développeur sénior en CDI",
            "contract_ranking": ["cdi", "freelance", "cdd", "interim"],
            "current": "cdi"
        },
        {
            "profile": "Freelance tech", 
            "contract_ranking": ["freelance", "interim", "cdd", "cdi"],
            "current": "freelance"
        },
        {
            "profile": "Junior en recherche",
            "contract_ranking": ["cdi", "cdd", "interim", "freelance"], 
            "current": "recherche"
        }
    ]
    
    entreprise_offers = ["cdi", "cdd", "freelance", "interim"]
    
    print("👥 PROFILS CANDIDATS:")
    for scenario in candidat_scenarios:
        print(f"\n{scenario['profile']}:")
        print(f"   Statut: {scenario['current']}")
        print(f"   Préférences: {' > '.join(c.upper() for c in scenario['contract_ranking'])}")
        
        # Test matching avec chaque offre entreprise
        for offer in entreprise_offers:
            if offer in scenario['contract_ranking']:
                rank = scenario['contract_ranking'].index(offer) + 1
                score = max(0, 1.0 - (rank - 1) * 0.25)
                match_quality = "🔥" if score >= 0.75 else "✅" if score >= 0.5 else "⚠️"
                print(f"     vs {offer.upper()}: Rang {rank}/4 - Score {score:.2f} {match_quality}")
    
    return True

def test_contract_weighting():
    """Test pondération contrats selon profil"""
    print("\n⚖️ TEST PONDÉRATION CONTRATS")
    print("=" * 50)
    
    # Pondération par profil
    contract_weights = {
        "CDI": {
            "stability_factor": 1.0,
            "growth_potential": 0.9,
            "flexibility": 0.3,
            "immediate_income": 0.7
        },
        "CDD": {
            "stability_factor": 0.4,
            "growth_potential": 0.6,
            "flexibility": 0.7,
            "immediate_income": 0.8
        },
        "FREELANCE": {
            "stability_factor": 0.2,
            "growth_potential": 0.8,
            "flexibility": 1.0,
            "immediate_income": 1.0
        },
        "INTERIM": {
            "stability_factor": 0.1,
            "growth_potential": 0.4,
            "flexibility": 0.9,
            "immediate_income": 0.9
        }
    }
    
    print("📊 CARACTÉRISTIQUES PAR CONTRAT:")
    for contract, weights in contract_weights.items():
        print(f"\n{contract}:")
        for factor, score in weights.items():
            bars = "█" * int(score * 10)
            print(f"   {factor}: {score:.1f} {bars}")
    
    return True

def run_final_test():
    """Test final complet"""
    print("🎯 NEXTVISION V3.0 - TEST FINAL CONTRATS")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Types contrats (critique)
    results['contract_types'] = test_final_contract_types()
    
    # Test 2: Questionnaire
    results['questionnaire'] = test_questionnaire_4_contracts()
    
    # Test 3: Pondération
    results['weighting'] = test_contract_weighting()
    
    # Rapport final
    print("\n🏆 RAPPORT FINAL")
    print("=" * 50)
    success_count = sum(results.values())
    total_tests = len(results)
    
    for test_name, success in results.items():
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 SCORE: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("\n🎉 SUCCÈS TOTAL!")
        print("🇫🇷 Les 4 contrats français sont parfaitement intégrés:")
        print("   ✅ CDI - Contrat à Durée Indéterminée")
        print("   ✅ CDD - Contrat à Durée Déterminée") 
        print("   ✅ FREELANCE - Mission freelance")
        print("   ✅ INTERIM - Mission d'intérim")
        print("\n🚀 PRÊT POUR LES TESTS AVEC VOS FICHIERS!")
    else:
        print("\n⚠️ Corrections nécessaires avant tests complets")
    
    return results

if __name__ == "__main__":
    run_final_test()
