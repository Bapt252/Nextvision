"""
🚀 Exemples d'utilisation Nextvision V3.0 - Scorers Enhanced
Guide pratique d'implémentation des nouveaux scorers

Author: NEXTEN Team
Version: 3.0.0 - Usage Examples
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any

# Import des scorers V3.0
from nextvision.services.scorers_v3 import (
    AvailabilityTimingScorer,
    ContractTypesScorer,
    WorkEnvironmentScorer,
    LocationTransportScorerV3
)

# Import du scorer enhanced
from nextvision.services.enhanced_bidirectional_scorer_v3 import (
    EnhancedBidirectionalScorerV3
)

# Import des modèles
from nextvision.models.extended_bidirectional_models_v3 import (
    ExtendedCandidateProfileV3,
    ExtendedCompanyProfileV3,
    ExtendedMatchingRequestV3,
    AvailabilityTimingV3,
    TransportPreferencesV3,
    MotivationsRankingV3,
    CompanyProfileV3,
    RecruitmentProcessV3,
    JobBenefitsV3,
    CandidateStatusType,
    WorkModalityType,
    TypeContrat,
    UrgenceRecrutement,
    CompanySize,
    ListeningReasonType
)

# Import des modèles V2.0 (base)
from nextvision.models.bidirectional_models import (
    BiDirectionalCandidateProfile,
    BiDirectionalCompanyProfile,
    NiveauExperience
)

# Import des services
from nextvision.services.google_maps_service import GoogleMapsService
from nextvision.services.transport_calculator import TransportCalculator

print("🚀 NEXTVISION V3.0 - EXEMPLES D'UTILISATION")
print("=" * 60)

# ============================================
# EXEMPLE 1: UTILISATION INDIVIDUELLE DES SCORERS
# ============================================

async def example_individual_scorers():
    """📊 Exemple 1: Utilisation individuelle des scorers"""
    
    print("\n📊 EXEMPLE 1: SCORERS INDIVIDUELS")
    print("-" * 40)
    
    # Création candidat exemple
    candidate = create_sample_candidate()
    
    # Création entreprise exemple
    company = create_sample_company()
    
    # 1. AvailabilityTimingScorer
    print("\n🕐 1. AvailabilityTimingScorer")
    timing_scorer = AvailabilityTimingScorer()
    
    timing_result = timing_scorer.calculate_availability_timing_score(
        candidate, company
    )
    
    print(f"   Score: {timing_result['final_score']:.2f}")
    print(f"   Niveau: {timing_result['compatibility_level']}")
    print(f"   Candidat: {timing_result['timing_analysis']['candidate_availability']}")
    print(f"   Entreprise: {timing_result['timing_analysis']['urgency_level']}")
    
    # 2. ContractTypesScorer
    print("\n📋 2. ContractTypesScorer")
    contract_scorer = ContractTypesScorer()
    
    contract_result = contract_scorer.calculate_contract_types_score(
        candidate, company
    )
    
    print(f"   Score: {contract_result['final_score']:.2f}")
    print(f"   Niveau: {contract_result['compatibility_level']}")
    print(f"   Position ranking: {contract_result['contract_analysis']['position_in_ranking']}")
    print(f"   Contrat offert: {contract_result['contract_analysis']['offered_contract']}")
    
    # 3. WorkEnvironmentScorer
    print("\n🏢 3. WorkEnvironmentScorer")
    environment_scorer = WorkEnvironmentScorer()
    
    environment_result = environment_scorer.calculate_work_environment_score(
        candidate, company
    )
    
    print(f"   Score: {environment_result['final_score']:.2f}")
    print(f"   Niveau: {environment_result['compatibility_level']}")
    print(f"   Candidat: {environment_result['environment_analysis']['candidate_office_preference']}")
    print(f"   Entreprise: {environment_result['environment_analysis']['company_remote_policy']}")
    
    # Affichage recommandations
    print("\n💡 Recommandations timing:")
    for rec in timing_result['recommendations'][:2]:
        print(f"   - {rec}")
    
    print("\n💡 Recommandations contrat:")
    for rec in contract_result['recommendations'][:2]:
        print(f"   - {rec}")
    
    print("\n💡 Recommandations environnement:")
    for rec in environment_result['recommendations'][:2]:
        print(f"   - {rec}")

# ============================================
# EXEMPLE 2: UTILISATION ENHANCED SCORER V3.0
# ============================================

async def example_enhanced_scorer():
    """🚀 Exemple 2: Enhanced Scorer V3.0 complet"""
    
    print("\n🚀 EXEMPLE 2: ENHANCED SCORER V3.0")
    print("-" * 40)
    
    # Services (mock pour exemple)
    google_maps_service = None  # Mock
    transport_calculator = None  # Mock
    
    # Création Enhanced Scorer
    enhanced_scorer = EnhancedBidirectionalScorerV3(
        google_maps_service, transport_calculator
    )
    
    # Création candidat et entreprise
    candidate = create_sample_candidate()
    company = create_sample_company()
    
    # Création requête matching
    request = ExtendedMatchingRequestV3(
        candidate=candidate,
        company=company,
        use_adaptive_weighting=True,
        use_google_maps_intelligence=False,  # Désactivé pour l'exemple
        exploit_questionnaire_data=True
    )
    
    print("⏱️  Calcul score bidirectionnel enhanced...")
    
    # Calcul score complet
    response = await enhanced_scorer.calculate_enhanced_bidirectional_score(request)
    
    print(f"\n✅ RÉSULTATS ENHANCED:")
    print(f"   Score final: {response.matching_score:.3f}")
    print(f"   Confiance: {response.confidence:.3f}")
    print(f"   Compatibilité: {response.compatibility}")
    print(f"   Temps traitement: {response.performance_monitoring.total_processing_time_ms:.1f}ms")
    print(f"   Target atteint: {response.performance_monitoring.target_achieved}")
    
    print(f"\n📊 SCORES DÉTAILLÉS:")
    print(f"   Sémantique: {response.component_scores.semantic_score:.2f}")
    print(f"   Salaire: {response.component_scores.salary_score:.2f}")
    print(f"   Expérience: {response.component_scores.experience_score:.2f}")
    print(f"   Localisation: {response.component_scores.location_score:.2f}")
    print(f"   Timing: {response.component_scores.timing_compatibility_score:.2f}")
    print(f"   Contrat: {response.component_scores.contract_flexibility_score:.2f}")
    print(f"   Environnement: {response.component_scores.work_modality_score:.2f}")
    
    print(f"\n⚖️  POIDS APPLIQUÉS:")
    print(f"   Pondération adaptative: {response.adaptive_weighting_applied}")
    if response.listening_reason_detected:
        print(f"   Raison détectée: {response.listening_reason_detected.value}")
    
    print(f"\n🎯 POINTS FORTS:")
    for point in response.points_forts_match:
        print(f"   - {point}")
    
    print(f"\n⚠️  POINTS ATTENTION:")
    for point in response.points_attention:
        print(f"   - {point}")
    
    print(f"\n📈 EXPLOITATION QUESTIONNAIRE:")
    print(f"   Taux exploitation: {response.questionnaire_exploitation_rate:.1%}")
    print(f"   Impact features V3.0: {response.v3_features_impact}")

# ============================================
# EXEMPLE 3: BATCH PROCESSING
# ============================================

async def example_batch_processing():
    """⚡ Exemple 3: Traitement batch multiple candidats"""
    
    print("\n⚡ EXEMPLE 3: TRAITEMENT BATCH")
    print("-" * 40)
    
    # Création entreprise unique
    company = create_sample_company()
    
    # Création plusieurs candidats
    candidates = [
        create_sample_candidate("Candidat A - Remote", WorkModalityType.FULL_REMOTE),
        create_sample_candidate("Candidat B - Hybrid", WorkModalityType.HYBRID),
        create_sample_candidate("Candidat C - On-site", WorkModalityType.ON_SITE)
    ]
    
    enhanced_scorer = EnhancedBidirectionalScorerV3()
    
    print(f"🔄 Traitement {len(candidates)} candidats...")
    
    results = []
    
    for i, candidate in enumerate(candidates):
        request = ExtendedMatchingRequestV3(
            candidate=candidate,
            company=company,
            use_adaptive_weighting=True,
            use_google_maps_intelligence=False
        )
        
        response = await enhanced_scorer.calculate_enhanced_bidirectional_score(request)
        results.append((f"Candidat {chr(65+i)}", response))
        
        print(f"   ✅ Candidat {chr(65+i)}: {response.matching_score:.3f} ({response.compatibility})")
    
    # Classement
    print(f"\n🏆 CLASSEMENT FINAL:")
    sorted_results = sorted(results, key=lambda x: x[1].matching_score, reverse=True)
    
    for rank, (name, response) in enumerate(sorted_results, 1):
        print(f"   {rank}. {name}: {response.matching_score:.3f}")
        print(f"      Environnement: {response.component_scores.work_modality_score:.2f}")
        print(f"      Timing: {response.component_scores.timing_compatibility_score:.2f}")
        print(f"      Contrat: {response.component_scores.contract_flexibility_score:.2f}")

# ============================================
# EXEMPLE 4: MONITORING ET PERFORMANCE
# ============================================

async def example_monitoring_performance():
    """📊 Exemple 4: Monitoring et performance"""
    
    print("\n📊 EXEMPLE 4: MONITORING PERFORMANCE")
    print("-" * 40)
    
    # Création scorers
    timing_scorer = AvailabilityTimingScorer()
    contract_scorer = ContractTypesScorer()
    environment_scorer = WorkEnvironmentScorer()
    enhanced_scorer = EnhancedBidirectionalScorerV3()
    
    # Simulation calculs multiples
    candidate = create_sample_candidate()
    company = create_sample_company()
    
    print("🔄 Simulation 20 calculs...")
    
    for i in range(20):
        # Calculs individuels
        timing_scorer.calculate_availability_timing_score(candidate, company)
        contract_scorer.calculate_contract_types_score(candidate, company)
        environment_scorer.calculate_work_environment_score(candidate, company)
        
        # Calcul enhanced
        request = ExtendedMatchingRequestV3(
            candidate=candidate,
            company=company,
            use_google_maps_intelligence=False
        )
        await enhanced_scorer.calculate_enhanced_bidirectional_score(request)
    
    # Statistiques
    print(f"\n📈 STATISTIQUES PERFORMANCE:")
    
    timing_stats = timing_scorer.get_performance_stats()
    print(f"   Timing Scorer:")
    print(f"     Calculs: {timing_stats['scorer_stats']['total_calculations']}")
    print(f"     Score moyen: {timing_stats['performance_metrics']['average_score']:.2f}")
    print(f"     Matches parfaits: {timing_stats['performance_metrics']['perfect_match_rate']:.1%}")
    
    contract_stats = contract_scorer.get_performance_stats()
    print(f"   Contract Scorer:")
    print(f"     Calculs: {contract_stats['scorer_stats']['total_calculations']}")
    print(f"     Score moyen: {contract_stats['performance_metrics']['average_score']:.2f}")
    print(f"     Contrats préférés: {contract_stats['performance_metrics']['most_preferred_contracts']}")
    
    environment_stats = environment_scorer.get_performance_stats()
    print(f"   Environment Scorer:")
    print(f"     Calculs: {environment_stats['scorer_stats']['total_calculations']}")
    print(f"     Score moyen: {environment_stats['performance_metrics']['average_score']:.2f}")
    print(f"     Distribution remote: {environment_stats['performance_metrics']['remote_preference_distribution']}")
    
    enhanced_stats = enhanced_scorer.get_global_performance_stats()
    print(f"   Enhanced Scorer:")
    print(f"     Calculs: {enhanced_stats['enhanced_scorer_stats']['total_calculations']}")
    print(f"     Taux succès: {enhanced_stats['performance_metrics']['success_rate']:.1%}")
    print(f"     Target atteint: {enhanced_stats['performance_metrics']['target_achievement_rate']:.1%}")
    print(f"     Temps moyen: {enhanced_stats['performance_metrics']['average_processing_time']:.1f}ms")

# ============================================
# EXEMPLE 5: GESTION D'ERREURS ET FALLBACKS
# ============================================

async def example_error_handling():
    """🛡️ Exemple 5: Gestion d'erreurs et fallbacks"""
    
    print("\n🛡️ EXEMPLE 5: GESTION D'ERREURS")
    print("-" * 40)
    
    # Création scorer
    timing_scorer = AvailabilityTimingScorer()
    
    # Candidat invalide (simulation erreur)
    invalid_candidate = None
    company = create_sample_company()
    
    print("⚠️  Test avec candidat invalide...")
    
    # Le scorer doit gérer l'erreur gracieusement
    result = timing_scorer.calculate_availability_timing_score(
        invalid_candidate, company
    )
    
    print(f"   Score fallback: {result['final_score']:.2f}")
    print(f"   Erreur: {result.get('error', 'Aucune')}")
    print(f"   Version: {result['version']}")
    
    # Test Enhanced Scorer avec erreur
    print("\n⚠️  Test Enhanced Scorer avec erreur...")
    
    enhanced_scorer = EnhancedBidirectionalScorerV3()
    
    try:
        request = ExtendedMatchingRequestV3(
            candidate=invalid_candidate,
            company=company
        )
        response = await enhanced_scorer.calculate_enhanced_bidirectional_score(request)
        
        print(f"   Score fallback: {response.matching_score:.2f}")
        print(f"   Compatibilité: {response.compatibility}")
        print(f"   Recommandations: {response.recommandations_candidat}")
        
    except Exception as e:
        print(f"   Erreur gérée: {e}")

# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def create_sample_candidate(name: str = "Candidat Test", 
                          office_pref: WorkModalityType = WorkModalityType.HYBRID) -> ExtendedCandidateProfileV3:
    """🧑‍💼 Création candidat exemple"""
    
    # Profil base V2.0
    base_profile = BiDirectionalCandidateProfile(
        nom="Dupont",
        prenom="Jean",
        experience_globale=NiveauExperience.CONFIRME,
        attentes=type('Attentes', (), {
            'salaire_min': 45000,
            'salaire_max': 60000,
            'localisation_preferee': 'Paris',
            'secteurs_preferes': ['Tech', 'Finance'],
            'distance_max_km': 30,
            'remote_accepte': True
        })(),
        competences=type('Competences', (), {
            'competences_techniques': ['Python', 'JavaScript', 'SQL'],
            'logiciels_maitrise': ['Git', 'Docker', 'AWS']
        })(),
        experiences_detaillees=[],
        motivations=type('Motivations', (), {
            'raison_ecoute': None
        })()
    )
    
    # Extensions V3.0
    transport_preferences = TransportPreferencesV3(
        transport_methods=['vehicle', 'public-transport'],
        max_travel_time=35,
        contract_ranking=[TypeContrat.CDI, TypeContrat.FREELANCE, TypeContrat.CDD],
        office_preference=office_pref,
        flexible_hours_important=True,
        parking_required=False,
        public_transport_accessibility=4
    )
    
    availability_timing = AvailabilityTimingV3(
        timing="2mois",
        employment_status=CandidateStatusType.EN_POSTE,
        notice_period_weeks=8,
        start_date_flexibility=3,
        recruitment_discretion_required=True,
        current_salary=50000,
        listening_reasons=[ListeningReasonType.EVOLUTION_CARRIERE]
    )
    
    return ExtendedCandidateProfileV3(
        base_profile=base_profile,
        transport_preferences=transport_preferences,
        availability_timing=availability_timing,
        motivations_ranking=MotivationsRankingV3(),
        remote_work_experience=True,
        management_experience=False,
        questionnaire_completion_rate=0.85,
        v3_features_enabled=True
    )

def create_sample_company() -> ExtendedCompanyProfileV3:
    """🏢 Création entreprise exemple"""
    
    # Profil base V2.0
    base_profile = BiDirectionalCompanyProfile(
        entreprise=type('Entreprise', (), {
            'nom': 'TechCorp',
            'secteur': 'Technology',
            'taille': 'PME'
        })(),
        poste=type('Poste', (), {
            'titre': 'Développeur Senior',
            'salaire_min': 50000,
            'salaire_max': 70000,
            'localisation': 'Paris 10ème',
            'competences_requises': ['Python', 'JavaScript']
        })(),
        exigences=type('Exigences', (), {
            'experience_requise': '3-5 ans',
            'competences_obligatoires': ['Python', 'SQL'],
            'competences_souhaitees': ['React', 'Docker']
        })(),
        conditions=type('Conditions', (), {
            'remote_possible': True
        })(),
        recrutement=type('Recrutement', (), {
            'urgence': UrgenceRecrutement.NORMAL,
            'contexte_urgence': 'Expansion équipe'
        })()
    )
    
    # Extensions V3.0
    company_profile_v3 = CompanyProfileV3(
        company_sector='Technology',
        company_size=CompanySize.PME,
        company_culture=['Innovation', 'Autonomie', 'Collaboration'],
        growth_stage='growth',
        team_size_hiring_for=8
    )
    
    recruitment_process = RecruitmentProcessV3(
        recruitment_delays='2-3 mois',
        notice_management='Flexible selon profil',
        interview_stages=3,
        remote_interview_possible=True,
        trial_period_duration=3
    )
    
    job_benefits = JobBenefitsV3(
        contract_nature=TypeContrat.CDI,
        job_benefits=['Mutuelle', 'Tickets restaurant', 'CE', 'Parking'],
        remote_policy=WorkModalityType.HYBRID,
        bonus_structure='Variable',
        career_progression_timeline='2-3 ans'
    )
    
    return ExtendedCompanyProfileV3(
        base_profile=base_profile,
        company_profile_v3=company_profile_v3,
        recruitment_process=recruitment_process,
        job_benefits=job_benefits,
        questionnaire_completion_rate=0.80,
        v3_features_enabled=True
    )

# ============================================
# EXÉCUTION EXEMPLES
# ============================================

async def run_all_examples():
    """🚀 Exécution de tous les exemples"""
    
    try:
        await example_individual_scorers()
        await example_enhanced_scorer()
        await example_batch_processing()
        await example_monitoring_performance()
        await example_error_handling()
        
        print("\n" + "=" * 60)
        print("✅ TOUS LES EXEMPLES EXÉCUTÉS AVEC SUCCÈS")
        print("🎯 Scorers V3.0 prêts pour production")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erreur dans les exemples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Exécution asynchrone
    asyncio.run(run_all_examples())
