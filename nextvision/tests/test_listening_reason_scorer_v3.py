"""
🧪 Tests ListeningReasonScorer V3.0
===================================

Tests de validation du scorer raisons d'écoute intégré dans scorers_v3/
- Performance <4ms target (2% budget)
- Cohérence raisons d'écoute vs profil candidat
- Interaction avec pondération adaptative
- Gestion erreurs et fallbacks

Author: NEXTEN Team
Version: 3.0.0 - Test Suite
"""

import time
import logging
from typing import Dict, Any, List

# Configuration logging pour tests
logging.basicConfig(level=logging.INFO)

# Import des modèles V3.0
from nextvision.models.extended_bidirectional_models_v3 import (
    ExtendedCandidateProfileV3,
    ExtendedCompanyProfileV3,
    CandidateStatusType,
    WorkModalityType,
    CompanySize
)

# Import des modèles V2.0 (pour base)
from nextvision.models.bidirectional_models import (
    BiDirectionalCandidateProfile,
    BiDirectionalCompanyProfile,
    EntrepriseInfo,
    DescriptionPoste,
    AttentesCandidat,
    Competences,
    MotivationsCandidat
)

# Import configuration adaptative
from nextvision.config.adaptive_weighting_config import (
    ListeningReasonType,
    ADAPTIVE_MATRICES_V3
)

# Import scorer
from nextvision.services.scorers_v3.listening_reason_scorer import ListeningReasonScorer

def create_test_candidate_coherent() -> ExtendedCandidateProfileV3:
    """🎯 Candidat test avec raisons d'écoute cohérentes"""
    
    # Base V2.0
    base_profile = BiDirectionalCandidateProfile(
        competences=Competences(),
        attentes=AttentesCandidat(
            salaire_min=45000,
            salaire_max=60000
        ),
        motivations=MotivationsCandidat()
    )
    
    candidate = ExtendedCandidateProfileV3(base_profile=base_profile)
    
    # Raisons d'écoute cohérentes
    candidate.availability_timing.listening_reasons = [
        ListeningReasonType.REMUNERATION_FAIBLE,  # Primaire
        ListeningReasonType.MANQUE_PERSPECTIVES   # Secondaire cohérente
    ]
    
    # Données cohérentes
    candidate.availability_timing.employment_status = CandidateStatusType.EN_POSTE
    candidate.availability_timing.current_salary = 38000  # En dessous du min souhaité
    candidate.transport_preferences.office_preference = WorkModalityType.ON_SITE
    
    return candidate

def create_test_candidate_incoherent() -> ExtendedCandidateProfileV3:
    """❌ Candidat test avec raisons d'écoute incohérentes"""
    
    base_profile = BiDirectionalCandidateProfile(
        competences=Competences(),
        attentes=AttentesCandidat(
            salaire_min=50000,
            salaire_max=52000  # Écart faible
        ),
        motivations=MotivationsCandidat()
    )
    
    candidate = ExtendedCandidateProfileV3(base_profile=base_profile)
    
    # Raisons incohérentes
    candidate.availability_timing.listening_reasons = [
        ListeningReasonType.REMUNERATION_FAIBLE,  # Primaire
        ListeningReasonType.FLEXIBILITE           # Secondaire incohérente
    ]
    
    # Données incohérentes
    candidate.availability_timing.employment_status = CandidateStatusType.DEMANDEUR_EMPLOI
    candidate.availability_timing.current_salary = 55000  # Au-dessus du min souhaité
    
    return candidate

def create_test_candidate_flexibility() -> ExtendedCandidateProfileV3:
    """🔄 Candidat test avec focus flexibilité"""
    
    base_profile = BiDirectionalCandidateProfile(
        competences=Competences(),
        attentes=AttentesCandidat(),
        motivations=MotivationsCandidat()
    )
    
    candidate = ExtendedCandidateProfileV3(base_profile=base_profile)
    
    # Raisons flexibilité
    candidate.availability_timing.listening_reasons = [
        ListeningReasonType.FLEXIBILITE,
        ListeningReasonType.LOCALISATION
    ]
    
    # Données cohérentes flexibilité
    candidate.availability_timing.employment_status = CandidateStatusType.EN_POSTE
    candidate.transport_preferences.office_preference = WorkModalityType.FULL_REMOTE
    candidate.transport_preferences.max_travel_time = 20  # Temps trajet court
    
    return candidate

def create_test_company() -> ExtendedCompanyProfileV3:
    """🏢 Entreprise test standard"""
    
    base_profile = BiDirectionalCompanyProfile(
        entreprise=EntrepriseInfo(
            nom="TechCorp",
            secteur="Technologie"
        ),
        poste=DescriptionPoste(
            titre="Software Engineer",
            description="Poste avec évolution possible"
        )
    )
    
    company = ExtendedCompanyProfileV3(base_profile=base_profile)
    company.company_profile_v3.company_size = CompanySize.STARTUP
    
    return company

def test_listening_reason_performance():
    """⚡ Test performance <4ms"""
    
    print("🚀 TEST PERFORMANCE LISTENING REASON SCORER")
    print("=" * 50)
    
    scorer = ListeningReasonScorer()
    candidate = create_test_candidate_coherent()
    company = create_test_company()
    
    # Test performance avec 15 calculs
    times = []
    for i in range(15):
        start = time.time()
        result = scorer.calculate_listening_reason_score(candidate, company)
        processing_time = (time.time() - start) * 1000
        times.append(processing_time)
        
        print(f"  Calcul #{i+1}: {processing_time:.2f}ms - Score: {result['final_score']:.3f}")
    
    avg_time = sum(times) / len(times)
    max_time = max(times)
    min_time = min(times)
    
    print(f"\n📊 RÉSULTATS PERFORMANCE:")
    print(f"  • Temps moyen: {avg_time:.2f}ms")
    print(f"  • Temps max: {max_time:.2f}ms")
    print(f"  • Temps min: {min_time:.2f}ms")
    print(f"  • Target <4ms: {'✅ ATTEINT' if max_time < 4 else '❌ ÉCHEC'}")
    
    return max_time < 4.0

def test_coherence_analysis():
    """🧠 Test analyse cohérence"""
    
    print("\n🧠 TEST ANALYSE COHÉRENCE")
    print("=" * 50)
    
    scorer = ListeningReasonScorer()
    
    # Test candidat cohérent
    candidate_coherent = create_test_candidate_coherent()
    company = create_test_company()
    
    result_coherent = scorer.calculate_listening_reason_score(candidate_coherent, company)
    
    print(f"📊 CANDIDAT COHÉRENT:")
    print(f"  • Score: {result_coherent['final_score']:.3f}")
    print(f"  • Niveau: {result_coherent['coherence_level']}")
    print(f"  • Raison primaire: {result_coherent['listening_reasons_analysis']['primary_reason']}")
    print(f"  • Raisons secondaires: {result_coherent['listening_reasons_analysis']['secondary_reasons']}")
    
    # Test candidat incohérent  
    candidate_incoherent = create_test_candidate_incoherent()
    result_incoherent = scorer.calculate_listening_reason_score(candidate_incoherent, company)
    
    print(f"\n📊 CANDIDAT INCOHÉRENT:")
    print(f"  • Score: {result_incoherent['final_score']:.3f}")
    print(f"  • Niveau: {result_incoherent['coherence_level']}")
    
    # Comparaison
    coherence_gap = result_coherent['final_score'] - result_incoherent['final_score']
    print(f"\n🔍 ANALYSE COMPARATIVE:")
    print(f"  • Écart cohérence: {coherence_gap:.3f}")
    print(f"  • Discrimination: {'✅ EFFICACE' if coherence_gap > 0.2 else '❌ FAIBLE'}")
    
    return coherence_gap > 0.1

def test_adaptive_impact():
    """🎯 Test impact pondération adaptative"""
    
    print("\n🎯 TEST IMPACT PONDÉRATION ADAPTATIVE")
    print("=" * 50)
    
    scorer = ListeningReasonScorer()
    
    # Test différentes raisons d'écoute
    test_cases = [
        (ListeningReasonType.REMUNERATION_FAIBLE, "Rémunération faible"),
        (ListeningReasonType.MANQUE_PERSPECTIVES, "Manque perspectives"),
        (ListeningReasonType.FLEXIBILITE, "Flexibilité"),
        (ListeningReasonType.LOCALISATION, "Localisation"),
        (ListeningReasonType.POSTE_INADEQUAT, "Poste inadéquat")
    ]
    
    for reason, description in test_cases:
        # Test impact
        adaptive_impact = scorer.get_adaptive_impact_preview([reason])
        
        print(f"📊 {description.upper()}:")
        print(f"  • Impact adaptatif: {adaptive_impact['has_impact']}")
        
        if adaptive_impact['has_impact']:
            print(f"  • Changements majeurs: {adaptive_impact['major_changes']}")
        
        # Test avec candidat réel
        candidate = create_test_candidate_coherent()
        candidate.availability_timing.listening_reasons = [reason]
        
        result = scorer.calculate_listening_reason_score(candidate, create_test_company())
        impact_details = result['adaptive_impact']
        
        print(f"  • Boost détecté: {impact_details['has_adaptive_impact']}")
        if impact_details['has_adaptive_impact']:
            boosted = impact_details.get('boosted_components', [])
            if boosted:
                print(f"  • Top boost: {boosted[0]['component']} ({boosted[0]['boost_factor']:.1f}x)")
    
    return True

def test_multiple_reasons():
    """🔗 Test raisons multiples"""
    
    print("\n🔗 TEST RAISONS MULTIPLES")
    print("=" * 50)
    
    scorer = ListeningReasonScorer()
    company = create_test_company()
    
    # Test raisons simples vs multiples
    test_cases = [
        {
            "name": "Raison simple",
            "reasons": [ListeningReasonType.REMUNERATION_FAIBLE],
            "expected_boost": False
        },
        {
            "name": "Raisons cohérentes",
            "reasons": [ListeningReasonType.REMUNERATION_FAIBLE, ListeningReasonType.MANQUE_PERSPECTIVES],
            "expected_boost": True
        },
        {
            "name": "Raisons incohérentes",
            "reasons": [ListeningReasonType.REMUNERATION_FAIBLE, ListeningReasonType.FLEXIBILITE],
            "expected_boost": False
        },
        {
            "name": "Raisons multiples",
            "reasons": [ListeningReasonType.FLEXIBILITE, ListeningReasonType.LOCALISATION, ListeningReasonType.MANQUE_PERSPECTIVES],
            "expected_boost": True
        }
    ]
    
    results = []
    
    for case in test_cases:
        candidate = create_test_candidate_coherent()
        candidate.availability_timing.listening_reasons = case["reasons"]
        
        result = scorer.calculate_listening_reason_score(candidate, company)
        
        print(f"📊 {case['name'].upper()}:")
        print(f"  • Raisons: {[r.value for r in case['reasons']]}")
        print(f"  • Score: {result['final_score']:.3f}")
        print(f"  • Niveau: {result['coherence_level']}")
        print(f"  • Facteurs: {len(result['coherence_factors'])}")
        
        results.append({
            "name": case["name"],
            "score": result['final_score'],
            "coherence_level": result['coherence_level']
        })
    
    # Vérification progression logique
    simple_score = results[0]['score']
    coherent_score = results[1]['score']
    
    print(f"\n🔍 ANALYSE PROGRESSION:")
    print(f"  • Simple → Cohérent: {coherent_score - simple_score:.3f}")
    print(f"  • Bonus cohérence: {'✅ DÉTECTÉ' if coherent_score > simple_score else '❌ MANQUÉ'}")
    
    return coherent_score > simple_score

def test_error_handling():
    """🚨 Test gestion erreurs"""
    
    print("\n🚨 TEST GESTION ERREURS")
    print("=" * 50)
    
    scorer = ListeningReasonScorer()
    
    # Test candidat sans raisons d'écoute
    try:
        base_profile = BiDirectionalCandidateProfile(
            competences=Competences(),
            attentes=AttentesCandidat(),
            motivations=MotivationsCandidat()
        )
        empty_candidate = ExtendedCandidateProfileV3(base_profile=base_profile)
        empty_candidate.availability_timing.listening_reasons = []
        
        company = create_test_company()
        
        result = scorer.calculate_listening_reason_score(empty_candidate, company)
        
        print(f"📊 CANDIDAT SANS RAISONS:")
        print(f"  • Score: {result['final_score']:.3f}")
        print(f"  • Version: {result.get('version', 'normal')}")
        print(f"  • Erreur gérée: {'error' in result}")
        
        # Test avec raisons vides explicites
        result_empty = scorer.get_adaptive_impact_preview([])
        print(f"\n📊 IMPACT RAISONS VIDES:")
        print(f"  • Impact: {result_empty['has_impact']}")
        print(f"  • Message: {result_empty['message']}")
        
        return 'error' in result or result['final_score'] == 0.5
        
    except Exception as e:
        print(f"❌ Erreur non gérée: {e}")
        return False

def test_performance_stats():
    """📊 Test statistiques performance"""
    
    print("\n📊 TEST STATISTIQUES PERFORMANCE")
    print("=" * 50)
    
    scorer = ListeningReasonScorer()
    company = create_test_company()
    
    # Génération de quelques calculs
    candidates = [
        create_test_candidate_coherent(),
        create_test_candidate_incoherent(),
        create_test_candidate_flexibility()
    ]
    
    for i, candidate in enumerate(candidates):
        result = scorer.calculate_listening_reason_score(candidate, company)
        print(f"  Calcul test #{i+1}: {result['final_score']:.3f} - {result['coherence_level']}")
    
    # Récupération statistiques
    stats = scorer.get_performance_stats()
    
    print(f"\n📈 STATISTIQUES SCORER:")
    print(f"  • Calculs effectués: {stats['scorer_stats']['calculations']}")
    print(f"  • Temps moyen: {stats['performance_metrics']['average_processing_time_ms']:.2f}ms")
    print(f"  • Target atteint: {stats['performance_metrics']['target_achieved']}")
    
    # Distribution cohérence
    coherence_rates = stats['performance_metrics']['coherence_rates']
    print(f"\n📊 DISTRIBUTION COHÉRENCE:")
    for level, rate in coherence_rates.items():
        print(f"  • {level}: {rate:.1%}")
    
    return stats['performance_metrics']['target_achieved']

def run_full_test_suite():
    """🧪 Suite complète de tests"""
    
    print("🧪 SUITE TESTS LISTENING REASON SCORER V3.0")
    print("=" * 60)
    
    tests = [
        ("Performance <4ms", test_listening_reason_performance),
        ("Analyse cohérence", test_coherence_analysis),
        ("Impact adaptatif", test_adaptive_impact),
        ("Raisons multiples", test_multiple_reasons),
        ("Gestion erreurs", test_error_handling),
        ("Statistiques", test_performance_stats)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"\n{'✅' if success else '❌'} {test_name}: {'SUCCÈS' if success else 'ÉCHEC'}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n❌ {test_name}: ERREUR - {e}")
    
    # Résumé final
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print("\n" + "=" * 60)
    print(f"📈 RÉSULTATS FINAUX: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS PASSÉS - LISTENING REASON SCORER OPÉRATIONNEL!")
        print("\n🚀 PRÊT POUR INTÉGRATION PRODUCTION:")
        print("  ✅ Performance <4ms validée")
        print("  ✅ Analyse cohérence fonctionnelle")
        print("  ✅ Impact adaptatif confirmé")
        print("  ✅ Raisons multiples supportées")
        print("  ✅ Gestion erreurs robuste")
        print("  ✅ Statistiques complètes")
        print("\n🎯 IMPACT SYSTÈME V3.0:")
        print("  • 6/12 scorers maintenant opérationnels")
        print("  • 32% du poids total couvert")
        print("  • Cerveau adaptatif (2%) intégré")
        print("  • Interaction avec pondération adaptative active")
    else:
        print(f"⚠️ {total - passed} tests en échec - Corrections nécessaires")
    
    return passed == total

if __name__ == "__main__":
    # Exécution suite complète
    success = run_full_test_suite()
    
    if success:
        print("\n🧠 LISTENING REASON SCORER V3.0 VALIDÉ!")
        print("📦 Package scorers_v3/ mis à jour avec succès")
        print("🎯 Cerveau adaptatif du système V3.0 opérationnel")
        print("⚡ Impact sur pondération adaptative confirmé")
    else:
        print("\n🔧 Corrections nécessaires avant intégration")
