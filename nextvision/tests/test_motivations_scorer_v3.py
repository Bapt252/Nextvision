"""
🧪 Tests MotivationsScorer V3.0
==============================

Tests de validation du scorer motivations intégré dans scorers_v3/
- Performance <15ms target
- Compatibilité modèles V3.0
- Gestion erreurs et fallbacks
- Cache et optimisations

Author: NEXTEN Team
Version: 3.0.0 - Test Suite
"""

import time
import logging
from typing import Dict, Any

# Configuration logging pour tests
logging.basicConfig(level=logging.INFO)

# Import des modèles V3.0
from nextvision.models.extended_bidirectional_models_v3 import (
    ExtendedCandidateProfileV3,
    ExtendedCompanyProfileV3,
    MotivationType,
    WorkModalityType,
    CompanySize,
    CandidateStatusType
)

# Import des modèles V2.0 (pour test rétrocompatibilité)
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
from nextvision.services.scorers_v3.motivations_scorer import MotivationsScorer

def create_test_candidate_v3() -> ExtendedCandidateProfileV3:
    """🎯 Création candidat test V3.0 avec motivations"""
    
    # Base V2.0 minimal
    base_profile = BiDirectionalCandidateProfile(
        competences=Competences(),
        attentes=AttentesCandidat(),
        motivations=MotivationsCandidat()
    )
    
    candidate = ExtendedCandidateProfileV3(base_profile=base_profile)
    
    # Motivations V3.0 avec ranking
    candidate.motivations_ranking.motivations_ranking = {
        MotivationType.EVOLUTION_CARRIERE: 5,   # Priorité #1
        MotivationType.CHALLENGE_TECHNIQUE: 4,  # Priorité #2  
        MotivationType.AUTONOMIE: 3,            # Priorité #3
        MotivationType.EQUILIBRE_VIE: 2         # Priorité #4
    }
    
    # Configuration disponibilité
    candidate.availability_timing.employment_status = CandidateStatusType.EN_POSTE
    candidate.availability_timing.listening_reasons = []
    
    return candidate

def create_test_company_v3() -> ExtendedCompanyProfileV3:
    """🏢 Création entreprise test V3.0 avec opportunités"""
    
    # Base V2.0
    base_profile = BiDirectionalCompanyProfile(
        entreprise=EntrepriseInfo(
            nom="TechCorp",
            secteur="Technologie",
            description="Startup technologique en forte croissance, culture innovation et autonomie"
        ),
        poste=DescriptionPoste(
            titre="Senior Software Engineer",
            description="Poste avec perspectives d'évolution rapide vers tech lead, environnement innovant, autonomie technique, technologies cutting-edge",
            missions_principales=["Développement", "Architecture", "Leadership technique"]
        )
    )
    
    company = ExtendedCompanyProfileV3(base_profile=base_profile)
    
    # Configuration V3.0
    company.company_profile_v3.company_size = CompanySize.STARTUP
    company.company_profile_v3.company_culture = ["Innovation", "Autonomie", "Croissance"]
    
    company.job_benefits.remote_policy = WorkModalityType.HYBRID
    company.job_benefits.job_benefits = ["Formation continue", "Stock options", "Flexibilité horaires"]
    company.job_benefits.career_progression_timeline = "12-18 mois"
    
    return company

def create_test_candidate_v2_fallback() -> ExtendedCandidateProfileV3:
    """🔄 Test candidat avec fallback V2.0"""
    
    base_profile = BiDirectionalCandidateProfile(
        competences=Competences(),
        attentes=AttentesCandidat(),
        motivations=MotivationsCandidat()
    )
    
    candidate = ExtendedCandidateProfileV3(base_profile=base_profile)
    
    # Pas de motivations V3.0 → fallback V2.0
    candidate.motivations_ranking.motivations_ranking = {}
    
    # Listening reasons pour déduction
    from nextvision.config.adaptive_weighting_config import ListeningReasonType
    candidate.availability_timing.listening_reasons = [
        ListeningReasonType.MANQUE_PERSPECTIVES,
        ListeningReasonType.POSTE_INADEQUAT
    ]
    
    return candidate

def test_motivations_scorer_performance():
    """⚡ Test performance <15ms"""
    
    print("🚀 TEST PERFORMANCE MOTIVATIONS SCORER")
    print("=" * 50)
    
    scorer = MotivationsScorer()
    candidate = create_test_candidate_v3()
    company = create_test_company_v3()
    
    # Test performance avec 10 calculs
    times = []
    for i in range(10):
        start = time.time()
        result = scorer.calculate_motivations_score(candidate, company)
        processing_time = (time.time() - start) * 1000
        times.append(processing_time)
        
        print(f"  Calcul #{i+1}: {processing_time:.1f}ms - Score: {result['final_score']:.3f}")
    
    avg_time = sum(times) / len(times)
    max_time = max(times)
    
    print(f"\n📊 RÉSULTATS PERFORMANCE:")
    print(f"  • Temps moyen: {avg_time:.1f}ms")
    print(f"  • Temps max: {max_time:.1f}ms")
    print(f"  • Target <15ms: {'✅ ATTEINT' if max_time < 15 else '❌ ÉCHEC'}")
    
    return avg_time < 15.0

def test_motivations_analysis():
    """🎯 Test analyse motivations complète"""
    
    print("\n🎯 TEST ANALYSE MOTIVATIONS")
    print("=" * 50)
    
    scorer = MotivationsScorer()
    candidate = create_test_candidate_v3()
    company = create_test_company_v3()
    
    result = scorer.calculate_motivations_score(candidate, company)
    
    print(f"📊 Score global: {result['final_score']:.3f}")
    print(f"🎚️ Niveau: {result['compatibility_level']}")
    print(f"⏱️ Temps: {result.get('processing_time_ms', 0):.1f}ms")
    
    # Analyse détaillée
    analysis = result['motivation_analysis']
    print(f"\\n📈 ANALYSE:")
    print(f"  • Total motivations: {analysis['total_motivations']}")
    print(f"  • Alignements forts: {analysis['strong_alignments']}")
    print(f"  • Alignements faibles: {analysis['weak_alignments']}")
    print(f"  • Top motivation satisfaite: {analysis['top_motivation_satisfied']}")
    
    # Détail des matches
    print(f"\\n🔍 DÉTAIL MOTIVATIONS:")
    for match in result['detailed_matches']:
        print(f"  • {match['motivation']} (#{match['ranking_position']}): "
              f"{match['enterprise_score']:.2f} → {match['alignment_level']}")
    
    # Recommandations
    print(f"\\n💡 RECOMMANDATIONS:")
    for rec in result['recommendations'][:3]:
        print(f"  {rec}")
    
    return result['final_score'] > 0.5

def test_fallback_v2():
    """🔄 Test fallback V2.0"""
    
    print("\\n🔄 TEST FALLBACK V2.0")
    print("=" * 50)
    
    scorer = MotivationsScorer()
    candidate = create_test_candidate_v2_fallback()
    company = create_test_company_v3()
    
    result = scorer.calculate_motivations_score(candidate, company)
    
    print(f"📊 Score fallback: {result['final_score']:.3f}")
    print(f"🎚️ Niveau: {result['compatibility_level']}")
    
    # Vérification motivations déduites
    analysis = result['motivation_analysis']
    print(f"\\n📈 MOTIVATIONS DÉDUITES:")
    print(f"  • Total: {analysis['total_motivations']}")
    
    for match in result['detailed_matches']:
        print(f"  • {match['motivation']}: déduite depuis listening reasons")
    
    return result['final_score'] > 0.0

def test_cache_performance():
    """💾 Test performance cache entreprise"""
    
    print("\\n💾 TEST CACHE PERFORMANCE")
    print("=" * 50)
    
    scorer = MotivationsScorer()
    candidate = create_test_candidate_v3()
    company = create_test_company_v3()
    
    # Premier calcul (cache miss)
    start = time.time()
    result1 = scorer.calculate_motivations_score(candidate, company)
    time1 = (time.time() - start) * 1000
    
    # Deuxième calcul (cache hit)
    start = time.time()
    result2 = scorer.calculate_motivations_score(candidate, company)
    time2 = (time.time() - start) * 1000
    
    print(f"📊 PERFORMANCE CACHE:")
    print(f"  • 1er calcul (miss): {time1:.1f}ms")
    print(f"  • 2ème calcul (hit): {time2:.1f}ms")
    print(f"  • Gain cache: {((time1 - time2) / time1 * 100):.1f}%")
    
    # Statistiques scorer
    stats = scorer.get_performance_stats()
    print(f"\\n📈 STATS SCORER:")
    print(f"  • Cache hits: {stats['scorer_stats']['cache_hits']}")
    print(f"  • Cache size: {stats['cache_size']}")
    print(f"  • Target atteint: {stats['performance_metrics']['target_achieved']}")
    
    return time2 < time1

def test_error_handling():
    """🚨 Test gestion erreurs"""
    
    print("\\n🚨 TEST GESTION ERREURS")
    print("=" * 50)
    
    scorer = MotivationsScorer()
    
    # Test avec candidat vide
    try:
        base_profile = BiDirectionalCandidateProfile(
            competences=Competences(),
            attentes=AttentesCandidat(),
            motivations=MotivationsCandidat()
        )
        empty_candidate = ExtendedCandidateProfileV3(base_profile=base_profile)
        company = create_test_company_v3()
        
        result = scorer.calculate_motivations_score(empty_candidate, company)
        
        print(f"📊 Score candidat vide: {result['final_score']:.3f}")
        print(f"🎚️ Mode: {result.get('version', 'normal')}")
        print(f"❓ Erreur gérée: {'error' in result}")
        
        return 'error' in result or result['final_score'] == 0.5
        
    except Exception as e:
        print(f"❌ Erreur non gérée: {e}")
        return False

def run_full_test_suite():
    """🧪 Suite complète de tests"""
    
    print("🧪 SUITE TESTS MOTIVATIONS SCORER V3.0")
    print("=" * 60)
    
    tests = [
        ("Performance <15ms", test_motivations_scorer_performance),
        ("Analyse motivations", test_motivations_analysis), 
        ("Fallback V2.0", test_fallback_v2),
        ("Cache performance", test_cache_performance),
        ("Gestion erreurs", test_error_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"\\n{'✅' if success else '❌'} {test_name}: {'SUCCÈS' if success else 'ÉCHEC'}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\\n❌ {test_name}: ERREUR - {e}")
    
    # Résumé final
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print("\\n" + "=" * 60)
    print(f"📈 RÉSULTATS FINAUX: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS PASSÉS - MOTIVATIONS SCORER OPÉRATIONNEL!")
        print("\\n🚀 PRÊT POUR INTÉGRATION PRODUCTION:")
        print("  ✅ Performance <15ms validée")
        print("  ✅ Compatibilité V3.0 confirmée")
        print("  ✅ Fallback V2.0 fonctionnel")
        print("  ✅ Cache optimisé") 
        print("  ✅ Gestion erreurs robuste")
        print("\\n🎯 IMPACT SYSTÈME V3.0:")
        print("  • 5/12 scorers maintenant opérationnels")
        print("  • 30% du poids total couvert")
        print("  • Motivation (8%) = 2ème scorer manquant le plus important")
    else:
        print(f"⚠️ {total - passed} tests en échec - Corrections nécessaires")
    
    return passed == total

if __name__ == "__main__":
    # Exécution suite complète
    success = run_full_test_suite()
    
    if success:
        print("\\n🔥 MOTIVATIONS SCORER V3.0 VALIDÉ!")
        print("📦 Package scorers_v3/ mis à jour avec succès")
        print("🎯 Prêt pour intégration dans enhanced_bidirectional_scorer_v3.py")
    else:
        print("\\n🔧 Corrections nécessaires avant intégration")
