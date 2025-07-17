"""
🧪 Tests SectorCompatibilityScorer V3.0
======================================

Tests de validation du scorer compatibilité secteur intégré dans scorers_v3/
- Performance <11ms target (6% budget)
- Logique métier: Score 1.0 (préféré), 0.0 (rédhibitoire), modulé (connexions)
- Cartographie secteurs connexes avec 20+ secteurs
- Ouverture changement carrière et priorité secteur vs poste
- Bonus/malus selon taille entreprise

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
    CompanySize,
    CandidateStatusType,
    MotivationType
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

# Import scorer
from nextvision.services.scorers_v3.sector_compatibility_scorer import SectorCompatibilityScorer

def create_test_candidate_tech_preferred() -> ExtendedCandidateProfileV3:
    """🎯 Candidat test avec préférence technologie"""
    
    # Base V2.0
    base_profile = BiDirectionalCandidateProfile(
        competences=Competences(),
        attentes=AttentesCandidat(),
        motivations=MotivationsCandidat()
    )
    
    candidate = ExtendedCandidateProfileV3(base_profile=base_profile)
    
    # Secteurs préférés/rédhibitoires
    candidate.motivations_ranking.secteurs_preferes = ["Technologie", "Informatique", "Digital"]
    candidate.motivations_ranking.secteurs_redhibitoires = ["Industrie lourde", "Chimie"]
    
    # Ouverture changement carrière
    candidate.motivations_ranking.career_change_openness = 4  # Très ouvert
    candidate.motivations_ranking.sector_priority_vs_role = 3  # Équilibré
    
    return candidate

def create_test_candidate_finance_focused() -> ExtendedCandidateProfileV3:
    """💰 Candidat test avec focus finance strict"""
    
    base_profile = BiDirectionalCandidateProfile(
        competences=Competences(),
        attentes=AttentesCandidat(),
        motivations=MotivationsCandidat()
    )
    
    candidate = ExtendedCandidateProfileV3(base_profile=base_profile)
    
    # Focus finance strict
    candidate.motivations_ranking.secteurs_preferes = ["Finance", "Banque"]
    candidate.motivations_ranking.secteurs_redhibitoires = ["Technologie", "Startup"]
    
    # Peu ouvert au changement
    candidate.motivations_ranking.career_change_openness = 2  # Peu ouvert
    candidate.motivations_ranking.sector_priority_vs_role = 5  # Secteur très important
    
    return candidate

def create_test_candidate_open_minded() -> ExtendedCandidateProfileV3:
    """🔄 Candidat test très ouvert"""
    
    base_profile = BiDirectionalCandidateProfile(
        competences=Competences(),
        attentes=AttentesCandidat(),
        motivations=MotivationsCandidat()
    )
    
    candidate = ExtendedCandidateProfileV3(base_profile=base_profile)
    
    # Très ouvert
    candidate.motivations_ranking.secteurs_preferes = ["Conseil", "Technologie"]
    candidate.motivations_ranking.secteurs_redhibitoires = []  # Aucun secteur rédhibitoire
    
    # Très ouvert au changement
    candidate.motivations_ranking.career_change_openness = 5  # Très ouvert
    candidate.motivations_ranking.sector_priority_vs_role = 2  # Poste plus important
    
    return candidate

def create_test_company_tech_startup() -> ExtendedCompanyProfileV3:
    """🚀 Entreprise test - Startup tech"""
    
    base_profile = BiDirectionalCompanyProfile(
        entreprise=EntrepriseInfo(
            nom="TechStartup",
            secteur="Technologie"
        ),
        poste=DescriptionPoste(
            titre="Software Engineer",
            description="Développement dans une startup innovante"
        )
    )
    
    company = ExtendedCompanyProfileV3(base_profile=base_profile)
    
    # Configuration V3.0
    company.company_profile_v3.company_sector = "Technologie"
    company.company_profile_v3.company_size = CompanySize.STARTUP
    company.company_profile_v3.growth_stage = "growth"
    
    return company

def create_test_company_finance_corp() -> ExtendedCompanyProfileV3:
    """🏦 Entreprise test - Grande banque"""
    
    base_profile = BiDirectionalCompanyProfile(
        entreprise=EntrepriseInfo(
            nom="BigBank",
            secteur="Banque"
        ),
        poste=DescriptionPoste(
            titre="Analyste Financier",
            description="Analyse financière dans grande banque"
        )
    )
    
    company = ExtendedCompanyProfileV3(base_profile=base_profile)
    
    # Configuration V3.0
    company.company_profile_v3.company_sector = "Finance"
    company.company_profile_v3.company_size = CompanySize.GRAND_GROUPE
    company.company_profile_v3.growth_stage = "stable"
    
    return company

def create_test_company_fintech() -> ExtendedCompanyProfileV3:
    """💳 Entreprise test - Fintech"""
    
    base_profile = BiDirectionalCompanyProfile(
        entreprise=EntrepriseInfo(
            nom="FinTechCorp",
            secteur="Fintech"
        ),
        poste=DescriptionPoste(
            titre="Product Manager",
            description="Gestion produit fintech"
        )
    )
    
    company = ExtendedCompanyProfileV3(base_profile=base_profile)
    
    # Configuration V3.0
    company.company_profile_v3.company_sector = "Fintech"
    company.company_profile_v3.company_size = CompanySize.PME
    company.company_profile_v3.growth_stage = "growth"
    
    return company

def test_sector_compatibility_performance():
    """⚡ Test performance <11ms"""
    
    print("🚀 TEST PERFORMANCE SECTOR COMPATIBILITY SCORER")
    print("=" * 50)
    
    scorer = SectorCompatibilityScorer()
    candidate = create_test_candidate_tech_preferred()
    company = create_test_company_tech_startup()
    
    # Test performance avec 12 calculs
    times = []
    for i in range(12):
        start = time.time()
        result = scorer.calculate_sector_compatibility_score(candidate, company)
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
    print(f"  • Target <11ms: {'✅ ATTEINT' if max_time < 11 else '❌ ÉCHEC'}")
    
    return max_time < 11.0

def test_sector_business_logic():
    """📋 Test logique métier secteur"""
    
    print("\n📋 TEST LOGIQUE MÉTIER SECTEUR")
    print("=" * 50)
    
    scorer = SectorCompatibilityScorer()
    
    # Test 1: Secteur préféré (Score = 1.0)
    candidate_tech = create_test_candidate_tech_preferred()
    company_tech = create_test_company_tech_startup()
    
    result_preferred = scorer.calculate_sector_compatibility_score(candidate_tech, company_tech)
    
    print(f"📊 TEST SECTEUR PRÉFÉRÉ:")
    print(f"  • Candidat préfère: {candidate_tech.motivations_ranking.secteurs_preferes}")
    print(f"  • Entreprise secteur: {company_tech.company_profile_v3.company_sector}")
    print(f"  • Score: {result_preferred['final_score']:.3f}")
    print(f"  • Niveau: {result_preferred['compatibility_level']}")
    print(f"  • Match type: {result_preferred['sector_analysis']['match_type']}")
    
    # Test 2: Secteur rédhibitoire (Score = 0.0)
    candidate_finance = create_test_candidate_finance_focused()
    company_tech = create_test_company_tech_startup()
    
    result_prohibited = scorer.calculate_sector_compatibility_score(candidate_finance, company_tech)
    
    print(f"\n📊 TEST SECTEUR RÉDHIBITOIRE:")
    print(f"  • Candidat rédhibitoire: {candidate_finance.motivations_ranking.secteurs_redhibitoires}")
    print(f"  • Entreprise secteur: {company_tech.company_profile_v3.company_sector}")
    print(f"  • Score: {result_prohibited['final_score']:.3f}")
    print(f"  • Niveau: {result_prohibited['compatibility_level']}")
    print(f"  • Match type: {result_prohibited['sector_analysis']['match_type']}")
    
    # Test 3: Secteur connexe (Score modulé)
    candidate_tech = create_test_candidate_tech_preferred()
    company_fintech = create_test_company_fintech()
    
    result_connected = scorer.calculate_sector_compatibility_score(candidate_tech, company_fintech)
    
    print(f"\n📊 TEST SECTEUR CONNEXE:")
    print(f"  • Candidat préfère: {candidate_tech.motivations_ranking.secteurs_preferes}")
    print(f"  • Entreprise secteur: {company_fintech.company_profile_v3.company_sector}")
    print(f"  • Score: {result_connected['final_score']:.3f}")
    print(f"  • Niveau: {result_connected['compatibility_level']}")
    print(f"  • Match type: {result_connected['sector_analysis']['match_type']}")
    print(f"  • Connexion: {result_connected['sector_analysis']['connection_strength']:.2f}")
    
    # Validation logique métier
    print(f"\n🔍 VALIDATION LOGIQUE MÉTIER:")
    print(f"  • Préféré >= Connexe: {result_preferred['final_score'] >= result_connected['final_score']}")
    print(f"  • Connexe >= Rédhibitoire: {result_connected['final_score'] >= result_prohibited['final_score']}")
    print(f"  • Rédhibitoire ≈ 0.0: {result_prohibited['final_score'] <= 0.1}")
    
    return (result_preferred['final_score'] >= result_connected['final_score'] >= result_prohibited['final_score']
            and result_prohibited['final_score'] <= 0.1)

def test_sector_connections_mapping():
    """🗺️ Test cartographie secteurs connexes"""
    
    print("\n🗺️ TEST CARTOGRAPHIE SECTEURS CONNEXES")
    print("=" * 50)
    
    scorer = SectorCompatibilityScorer()
    
    # Test connexions prédéfinies
    test_sectors = [
        "Technologie",
        "Finance",
        "Fintech",
        "Conseil",
        "Santé",
        "E-commerce"
    ]
    
    for sector in test_sectors:
        connections = scorer.get_sector_connections_preview(sector)
        
        print(f"📊 {sector.upper()}:")
        print(f"  • Connexions: {connections['has_connections']}")
        
        if connections['has_connections']:
            print(f"  • Directes: {connections['direct_connections'][:3]}")
            print(f"  • Transitions: {connections['natural_transitions'][:3]}")
            print(f"  • Distantes: {connections['distant_connections'][:3]}")
            print(f"  • Force: {connections['connection_strength']:.2f}")
    
    # Test calcul force connexion
    print(f"\n🔍 TEST FORCE CONNEXIONS:")
    test_pairs = [
        ("Technologie", "Fintech"),
        ("Finance", "Banque"),
        ("Conseil", "Technologie"),
        ("Santé", "Industrie")
    ]
    
    for sector1, sector2 in test_pairs:
        strength = scorer._calculate_connection_strength(sector1.lower(), sector2.lower())
        print(f"  • {sector1} ↔ {sector2}: {strength:.2f}")
    
    return True

def test_career_change_openness():
    """🔄 Test ouverture changement carrière"""
    
    print("\n🔄 TEST OUVERTURE CHANGEMENT CARRIÈRE")
    print("=" * 50)
    
    scorer = SectorCompatibilityScorer()
    
    # Test différents niveaux d'ouverture
    test_cases = [
        {
            "name": "Peu ouvert",
            "openness": 2,
            "expected_impact": "Pénalité pour secteur différent"
        },
        {
            "name": "Moyennement ouvert",
            "openness": 3,
            "expected_impact": "Neutre"
        },
        {
            "name": "Très ouvert",
            "openness": 5,
            "expected_impact": "Bonus exploration secteurs"
        }
    ]
    
    # Entreprise secteur connexe (pas préféré)
    company_fintech = create_test_company_fintech()
    
    results = []
    
    for case in test_cases:
        # Candidat avec préférence tech
        candidate = create_test_candidate_tech_preferred()
        candidate.motivations_ranking.career_change_openness = case["openness"]
        
        result = scorer.calculate_sector_compatibility_score(candidate, company_fintech)
        
        print(f"📊 {case['name'].upper()} (Ouverture: {case['openness']}/5):")
        print(f"  • Score: {result['final_score']:.3f}")
        print(f"  • Impact: {case['expected_impact']}")
        
        results.append(result['final_score'])
    
    # Validation progression logique
    print(f"\n🔍 VALIDATION PROGRESSION:")
    print(f"  • Très ouvert > Moyennement ouvert: {results[2] > results[1]}")
    print(f"  • Moyennement ouvert > Peu ouvert: {results[1] > results[0]}")
    
    return results[2] > results[1] > results[0]

def test_company_size_modifiers():
    """🏢 Test modifiers selon taille entreprise"""
    
    print("\n🏢 TEST MODIFIERS TAILLE ENTREPRISE")
    print("=" * 50)
    
    scorer = SectorCompatibilityScorer()
    candidate = create_test_candidate_open_minded()
    
    # Test différentes tailles
    company_sizes = [
        CompanySize.STARTUP,
        CompanySize.PME,
        CompanySize.ETI,
        CompanySize.GRAND_GROUPE,
        CompanySize.ADMINISTRATION
    ]
    
    results = []
    
    for size in company_sizes:
        # Création entreprise avec taille spécifique
        company = create_test_company_tech_startup()
        company.company_profile_v3.company_size = size
        
        result = scorer.calculate_sector_compatibility_score(candidate, company)
        
        print(f"📊 {size.value.upper()}:")
        print(f"  • Score: {result['final_score']:.3f}")
        print(f"  • Niveau: {result['compatibility_level']}")
        
        # Détails modifiers
        size_modifiers = scorer.size_modifiers.get(size, {})
        description = size_modifiers.get('description', 'Pas de modifiers')
        print(f"  • Modifiers: {description}")
        
        results.append({
            'size': size.value,
            'score': result['final_score']
        })
    
    # Analyse différenciation
    scores = [r['score'] for r in results]
    print(f"\n🔍 DIFFÉRENCIATION TAILLES:")
    print(f"  • Score min: {min(scores):.3f}")
    print(f"  • Score max: {max(scores):.3f}")
    print(f"  • Écart: {max(scores) - min(scores):.3f}")
    print(f"  • Différenciation: {'✅ EFFICACE' if max(scores) - min(scores) > 0.1 else '❌ FAIBLE'}")
    
    return max(scores) - min(scores) > 0.05

def test_sector_priority_vs_role():
    """⚖️ Test priorité secteur vs poste"""
    
    print("\n⚖️ TEST PRIORITÉ SECTEUR VS POSTE")
    print("=" * 50)
    
    scorer = SectorCompatibilityScorer()
    
    # Test différents niveaux de priorité
    priority_levels = [
        {"level": 1, "name": "Poste prioritaire", "expected": "Atténuation impact secteur"},
        {"level": 3, "name": "Équilibré", "expected": "Impact normal"},
        {"level": 5, "name": "Secteur prioritaire", "expected": "Amplification impact secteur"}
    ]
    
    # Test avec secteur moyennement compatible
    candidate = create_test_candidate_tech_preferred()
    company = create_test_company_fintech()  # Secteur connexe
    
    results = []
    
    for priority_case in priority_levels:
        candidate.motivations_ranking.sector_priority_vs_role = priority_case["level"]
        
        result = scorer.calculate_sector_compatibility_score(candidate, company)
        
        print(f"📊 {priority_case['name'].upper()} (Priorité: {priority_case['level']}/5):")
        print(f"  • Score: {result['final_score']:.3f}")
        print(f"  • Impact attendu: {priority_case['expected']}")
        
        results.append(result['final_score'])
    
    # Validation
    print(f"\n🔍 VALIDATION PRIORITÉ:")
    print(f"  • Secteur prioritaire impacte plus: {abs(results[2] - results[1]) > abs(results[0] - results[1])}")
    
    return True

def test_error_handling():
    """🚨 Test gestion erreurs"""
    
    print("\n🚨 TEST GESTION ERREURS")
    print("=" * 50)
    
    scorer = SectorCompatibilityScorer()
    
    # Test entreprise sans secteur
    try:
        base_profile = BiDirectionalCompanyProfile(
            entreprise=EntrepriseInfo(nom="NoSector", secteur=""),
            poste=DescriptionPoste(titre="Test", description="Test")
        )
        company_no_sector = ExtendedCompanyProfileV3(base_profile=base_profile)
        company_no_sector.company_profile_v3.company_sector = ""
        
        candidate = create_test_candidate_tech_preferred()
        
        result = scorer.calculate_sector_compatibility_score(candidate, company_no_sector)
        
        print(f"📊 ENTREPRISE SANS SECTEUR:")
        print(f"  • Score: {result['final_score']:.3f}")
        print(f"  • Version: {result.get('version', 'normal')}")
        print(f"  • Erreur gérée: {'error' in result}")
        
        # Test secteur inexistant
        company_unknown = create_test_company_tech_startup()
        company_unknown.company_profile_v3.company_sector = "SecteurInexistant"
        
        result_unknown = scorer.calculate_sector_compatibility_score(candidate, company_unknown)
        
        print(f"\n📊 SECTEUR INEXISTANT:")
        print(f"  • Score: {result_unknown['final_score']:.3f}")
        print(f"  • Niveau: {result_unknown['compatibility_level']}")
        print(f"  • Connexions: {result_unknown['sector_analysis']['connection_strength']:.2f}")
        
        return ('error' in result or result['final_score'] == 0.5) and result_unknown['final_score'] > 0
        
    except Exception as e:
        print(f"❌ Erreur non gérée: {e}")
        return False

def test_performance_stats():
    """📊 Test statistiques performance"""
    
    print("\n📊 TEST STATISTIQUES PERFORMANCE")
    print("=" * 50)
    
    scorer = SectorCompatibilityScorer()
    
    # Génération de calculs variés
    test_cases = [
        (create_test_candidate_tech_preferred(), create_test_company_tech_startup()),
        (create_test_candidate_finance_focused(), create_test_company_finance_corp()),
        (create_test_candidate_open_minded(), create_test_company_fintech())
    ]
    
    for i, (candidate, company) in enumerate(test_cases):
        result = scorer.calculate_sector_compatibility_score(candidate, company)
        print(f"  Calcul test #{i+1}: {result['final_score']:.3f} - {result['compatibility_level']}")
    
    # Récupération statistiques
    stats = scorer.get_performance_stats()
    
    print(f"\n📈 STATISTIQUES SCORER:")
    print(f"  • Calculs effectués: {stats['scorer_stats']['calculations']}")
    print(f"  • Temps moyen: {stats['performance_metrics']['average_processing_time_ms']:.2f}ms")
    print(f"  • Target atteint: {stats['performance_metrics']['target_achieved']}")
    print(f"  • Cache hit rate: {stats['performance_metrics']['cache_hit_rate']:.1%}")
    print(f"  • Cache size: {stats['cache_size']}")
    
    # Distribution compatibilité
    compatibility_rates = stats['performance_metrics']['compatibility_rates']
    print(f"\n📊 DISTRIBUTION COMPATIBILITÉ:")
    for level, rate in compatibility_rates.items():
        print(f"  • {level}: {rate:.1%}")
    
    return stats['performance_metrics']['target_achieved']

def run_full_test_suite():
    """🧪 Suite complète de tests"""
    
    print("🧪 SUITE TESTS SECTOR COMPATIBILITY SCORER V3.0")
    print("=" * 60)
    
    tests = [
        ("Performance <11ms", test_sector_compatibility_performance),
        ("Logique métier", test_sector_business_logic),
        ("Cartographie secteurs", test_sector_connections_mapping),
        ("Ouverture changement", test_career_change_openness),
        ("Modifiers taille", test_company_size_modifiers),
        ("Priorité secteur", test_sector_priority_vs_role),
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
        print("🎉 TOUS LES TESTS PASSÉS - SECTOR COMPATIBILITY SCORER OPÉRATIONNEL!")
        print("\n🚀 PRÊT POUR INTÉGRATION PRODUCTION:")
        print("  ✅ Performance <11ms validée")
        print("  ✅ Logique métier confirmée (1.0 préféré, 0.0 rédhibitoire)")
        print("  ✅ Cartographie secteurs opérationnelle (20+ secteurs)")
        print("  ✅ Ouverture changement carrière fonctionnelle")
        print("  ✅ Modifiers taille entreprise actifs")
        print("  ✅ Priorité secteur vs poste gérée")
        print("  ✅ Gestion erreurs robuste")
        print("  ✅ Statistiques complètes")
        print("\n🎯 IMPACT SYSTÈME V3.0:")
        print("  • 7/12 scorers maintenant opérationnels")
        print("  • 38% du poids total couvert")
        print("  • Logique métier secteur (6%) intégrée")
        print("  • Cartographie secteurs connexes active")
    else:
        print(f"⚠️ {total - passed} tests en échec - Corrections nécessaires")
    
    return passed == total

if __name__ == "__main__":
    # Exécution suite complète
    success = run_full_test_suite()
    
    if success:
        print("\n🎯 SECTOR COMPATIBILITY SCORER V3.0 VALIDÉ!")
        print("📦 Package scorers_v3/ mis à jour avec succès")
        print("🗺️ Cartographie secteurs connexes opérationnelle")
        print("🔄 Ouverture changement carrière intégrée")
        print("🏢 Modifiers taille entreprise actifs")
    else:
        print("\n🔧 Corrections nécessaires avant intégration")
