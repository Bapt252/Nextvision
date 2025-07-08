#!/usr/bin/env python3
"""
🎯 NEXTVISION V3.0 - Script de Test Complet
Test avec CV TEST et FDP TEST depuis le bureau
"""

import os
import sys
import time
import json
from pathlib import Path

# Ajout du chemin Nextvision (répertoire actuel)
sys.path.append('.')

# Imports Nextvision V3.0
try:
    from nextvision.services.enhanced_commitment_bridge_v3 import EnhancedBridgeV3Factory
    from nextvision.adapters.questionnaire_parser_v3 import CandidateQuestionnaireParserV3, CompanyQuestionnaireParserV3
    from nextvision.services.listening_reasons_scorer_v3 import ListeningReasonScorer
    from nextvision.services.professional_motivations_scorer_v3 import ProfessionalMotivationsScorer
    from nextvision.engines.v2_compatibility_layer import V2CompatibilityLayer
    print("✅ Imports V3.0 réussis")
except Exception as e:
    print(f"❌ Erreur imports V3.0: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Imports V2.0 pour comparaison
try:
    from nextvision.services.enhanced_commitment_bridge import EnhancedBridgeFactory
    print("✅ Imports V2.0 réussis")
except Exception as e:
    print(f"❌ Erreur imports V2.0: {e}")

def load_test_files():
    """Charge les fichiers de test depuis le bureau"""
    bureau_paths = [
        Path.home() / "Desktop",
        Path.home() / "Bureau", 
        Path.home() / "desktop"
    ]
    
    cv_files = []
    fdp_files = []
    
    for bureau in bureau_paths:
        if bureau.exists():
            print(f"📁 Recherche dans: {bureau}")
            cv_files.extend(list(bureau.glob("*CV*TEST*")))
            cv_files.extend(list(bureau.glob("*cv*test*")))
            cv_files.extend(list(bureau.glob("CV_TEST*")))
            fdp_files.extend(list(bureau.glob("*FDP*TEST*")))
            fdp_files.extend(list(bureau.glob("*fdp*test*")))
            fdp_files.extend(list(bureau.glob("FDP_TEST*")))
    
    print(f"📄 Fichiers CV trouvés: {[f.name for f in cv_files]}")
    print(f"📋 Fichiers FDP trouvés: {[f.name for f in fdp_files]}")
    
    return cv_files, fdp_files

def simulate_questionnaire_data():
    """Simule des données questionnaire pour test V3.0"""
    candidat_data = {
        "transport_methods": ["voiture", "metro"],
        "max_travel_time": 45,
        "contract_ranking": ["cdi", "freelance", "cdd"],
        "office_preference": "hybride",
        "motivations_ranking": ["evolution", "salaire", "flexibilite", "apprentissage"],
        "secteurs_preferes": ["tech", "finance"],
        "secteurs_redhibitoires": ["industrie"],
        "timing": "3_mois",
        "employment_status": "en_poste",
        "listening_reasons": ["inadequate_position", "perspectives"]
    }
    
    entreprise_data = {
        "company_sector": "tech",
        "company_size": "200-500",
        "recruitment_delays": "1_mois",
        "notice_management": "flexible",
        "contract_nature": "cdi",
        "job_benefits": ["formation", "mutuelle", "tickets_resto"],
        "remote_policy": "hybride_3j"
    }
    
    return candidat_data, entreprise_data

def test_v3_bridge_sync():
    """Test Bridge V3.0 en mode synchrone"""
    print("\n🔥 TEST BRIDGE V3.0 (MODE SYNC)")
    print("="*50)
    
    try:
        # Test import des classes
        from nextvision.models.extended_matching_models_v3 import ExtendedMatchingProfile
        print("✅ ExtendedMatchingProfile importé")
        
        # Test parser
        candidat_questionnaire, entreprise_questionnaire = simulate_questionnaire_data()
        
        candidat_parser = CandidateQuestionnaireParserV3()
        parsed_candidat = candidat_parser.parse_questionnaire_data(candidat_questionnaire)
        print(f"✅ Parser candidat: {len(parsed_candidat)} champs")
        
        entreprise_parser = CompanyQuestionnaireParserV3()
        parsed_entreprise = entreprise_parser.parse_questionnaire_data(entreprise_questionnaire)
        print(f"✅ Parser entreprise: {len(parsed_entreprise)} champs")
        
        # Test scorers
        listening_scorer = ListeningReasonScorer()
        weights = listening_scorer.generate_adaptive_weights("inadequate_position")
        print(f"✅ Listening Scorer: {len(weights)} poids générés")
        
        motivations_scorer = ProfessionalMotivationsScorer()
        print("✅ Motivations Scorer initialisé")
        
        return True, parsed_candidat, parsed_entreprise
        
    except Exception as e:
        print(f"❌ Erreur test V3.0: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None

def test_questionnaire_parsing():
    """Test parsing questionnaires V3.0"""
    print("\n📋 TEST PARSING QUESTIONNAIRES V3.0")
    print("="*50)
    
    try:
        candidat_data, entreprise_data = simulate_questionnaire_data()
        
        # Test parser candidat
        candidat_parser = CandidateQuestionnaireParserV3()
        parsed_candidat = candidat_parser.parse_questionnaire_data(candidat_data)
        print(f"✅ Parser candidat: {len(parsed_candidat)} champs extraits")
        for key, value in list(parsed_candidat.items())[:3]:
            print(f"   - {key}: {value}")
        
        # Test parser entreprise
        entreprise_parser = CompanyQuestionnaireParserV3()
        parsed_entreprise = entreprise_parser.parse_questionnaire_data(entreprise_data)
        print(f"✅ Parser entreprise: {len(parsed_entreprise)} champs extraits")
        for key, value in list(parsed_entreprise.items())[:3]:
            print(f"   - {key}: {value}")
        
        # Calcul exploitation
        total_possible = len(candidat_data) + len(entreprise_data)
        total_extrait = len(parsed_candidat) + len(parsed_entreprise)
        exploitation = (total_extrait / total_possible) * 100
        
        print(f"📊 Exploitation questionnaires: {exploitation:.1f}%")
        print(f"🎯 Objectif 95%: {'✅ ATTEINT' if exploitation >= 95 else '❌ À AMÉLIORER'}")
        
        return parsed_candidat, parsed_entreprise, exploitation
        
    except Exception as e:
        print(f"❌ Erreur parsing: {e}")
        import traceback
        traceback.print_exc()
        return None, None, 0

def test_adaptive_weighting():
    """Test pondération adaptative V3.0"""
    print("\n🧠 TEST PONDÉRATION ADAPTATIVE")
    print("="*50)
    
    try:
        scorer = ListeningReasonScorer()
        
        # Test différentes raisons d'écoute
        test_cases = [
            ("inadequate_position", "Position inadéquate"),
            ("perspectives", "Manque de perspectives"),
            ("remuneration", "Problème de rémunération"),
            ("location", "Problème de localisation"),
            ("flexibility", "Manque de flexibilité")
        ]
        
        for reason, description in test_cases:
            weights = scorer.generate_adaptive_weights(reason)
            print(f"📊 {description}:")
            print(f"   Salary: {weights.get('salary', 0.20):.2f}")
            print(f"   Location: {weights.get('location', 0.10):.2f}")
            print(f"   Motivations: {weights.get('professional_motivations', 0.08):.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur pondération: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_complete_test():
    """Exécute la suite complète de tests V3.0"""
    print("🚀 NEXTVISION V3.0 - TESTS COMPLETS")
    print("="*60)
    
    # Chargement fichiers
    cv_files, fdp_files = load_test_files()
    
    # Tests
    results = {}
    
    # Test 1: Parsing questionnaires
    candidat_parsed, entreprise_parsed, exploitation = test_questionnaire_parsing()
    results['questionnaire_exploitation'] = exploitation
    
    # Test 2: Pondération adaptative
    adaptive_ok = test_adaptive_weighting()
    results['adaptive_weighting'] = adaptive_ok
    
    # Test 3: Bridge V3.0
    bridge_ok, candidat_data, entreprise_data = test_v3_bridge_sync()
    results['bridge_v3'] = bridge_ok
    
    # Rapport final
    print("\n📊 RAPPORT FINAL")
    print("="*50)
    print(f"📋 Exploitation questionnaires: {exploitation:.1f}% (objectif: 95%)")
    print(f"🧠 Pondération adaptative: {'✅' if adaptive_ok else '❌'}")
    print(f"🔥 Bridge V3.0: {'✅' if bridge_ok else '❌'}")
    
    # Statut global
    success = exploitation >= 95 and adaptive_ok and bridge_ok
    
    print(f"\n🎯 STATUT GLOBAL: {'✅ SUCCÈS' if success else '❌ À AMÉLIORER'}")
    
    return results

if __name__ == "__main__":
    print("🎯 Lancement des tests Nextvision V3.0...")
    results = run_complete_test()
    print(f"\n🏁 Tests terminés: {results}")
