"""
🧪 Tests unitaires Nextvision V3.0 - Scorers Timing & Contrats & Environnement
Tests de validation pour les nouveaux scorers V3.0

Author: NEXTEN Team
Version: 3.0.0 - Tests Intelligence
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from typing import Dict, Any

# Import des scorers à tester
from nextvision.services.scorers_v3.availability_timing_scorer import (
    AvailabilityTimingScorer, TimingCompatibilityLevel
)
from nextvision.services.scorers_v3.contract_types_scorer import (
    ContractTypesScorer, ContractCompatibilityLevel
)
from nextvision.services.scorers_v3.work_environment_scorer import (
    WorkEnvironmentScorer, EnvironmentCompatibilityLevel
)

# Import des modèles
from nextvision.models.extended_bidirectional_models_v3 import (
    ExtendedCandidateProfileV3,
    ExtendedCompanyProfileV3,
    AvailabilityTimingV3,
    TransportPreferencesV3,
    JobBenefitsV3,
    CandidateStatusType,
    WorkModalityType,
    TypeContrat,
    UrgenceRecrutement
)

class TestAvailabilityTimingScorer(unittest.TestCase):
    """🕐 Tests AvailabilityTimingScorer"""
    
    def setUp(self):
        """Configuration tests"""
        self.scorer = AvailabilityTimingScorer()
        
        # Mock candidat de base
        self.base_candidate = Mock()
        self.base_candidate.availability_timing = AvailabilityTimingV3(
            timing="2mois",
            employment_status=CandidateStatusType.EN_POSTE,
            notice_period_weeks=8,
            start_date_flexibility=2,
            recruitment_discretion_required=True,
            current_salary=45000
        )
        
        # Mock entreprise de base
        self.base_company = Mock()
        self.base_company.base_profile.recrutement.urgence = UrgenceRecrutement.NORMAL
        self.base_company.recruitment_process.recruitment_delays = "2-3 mois"
        self.base_company.recruitment_process.notice_management = "Flexible selon profil"
        
        # Candidat complet
        self.candidate = Mock(spec=ExtendedCandidateProfileV3)
        self.candidate.availability_timing = self.base_candidate.availability_timing
        self.candidate.base_profile = self.base_candidate
        
        # Entreprise complète
        self.company = Mock(spec=ExtendedCompanyProfileV3)
        self.company.base_profile = self.base_company.base_profile
        self.company.recruitment_process = self.base_company.recruitment_process
    
    def test_perfect_timing_match(self):
        """Test match timing parfait"""
        # Candidat immédiatement disponible
        self.candidate.availability_timing.timing = "immediat"
        self.candidate.availability_timing.employment_status = CandidateStatusType.DEMANDEUR_EMPLOI
        self.candidate.availability_timing.notice_period_weeks = 0
        
        # Entreprise urgente
        self.company.base_profile.recrutement.urgence = UrgenceRecrutement.URGENT
        self.company.recruitment_process.recruitment_delays = "immédiat"
        
        result = self.scorer.calculate_availability_timing_score(
            self.candidate, self.company
        )
        
        self.assertGreaterEqual(result["final_score"], 0.9)
        self.assertEqual(result["compatibility_level"], TimingCompatibilityLevel.PERFECT.value)
        self.assertEqual(result["timing_analysis"]["notice_period_weeks"], 0)
    
    def test_notice_period_management(self):
        """Test gestion préavis"""
        # Candidat en poste avec préavis
        self.candidate.availability_timing.employment_status = CandidateStatusType.EN_POSTE
        self.candidate.availability_timing.notice_period_weeks = 8
        
        # Entreprise tolérante
        self.company.recruitment_process.notice_management = "Flexible et adaptable"
        
        result = self.scorer.calculate_availability_timing_score(
            self.candidate, self.company
        )
        
        self.assertGreaterEqual(result["final_score"], 0.6)
        self.assertEqual(result["timing_analysis"]["notice_period_weeks"], 8)
    
    def test_incompatible_timing(self):
        """Test timing incompatible"""
        # Candidat avec long préavis
        self.candidate.availability_timing.timing = "3mois"
        self.candidate.availability_timing.notice_period_weeks = 12
        
        # Entreprise critique
        self.company.base_profile.recrutement.urgence = UrgenceRecrutement.CRITIQUE
        self.company.recruitment_process.recruitment_delays = "immédiat"
        
        result = self.scorer.calculate_availability_timing_score(
            self.candidate, self.company
        )
        
        self.assertLessEqual(result["final_score"], 0.3)
        self.assertIn("incompatible", result["compatibility_level"].lower())
    
    def test_flexibility_bonus(self):
        """Test bonus flexibilité"""
        # Candidat très flexible
        self.candidate.availability_timing.start_date_flexibility = 6
        self.candidate.availability_timing.employment_status = CandidateStatusType.DEMANDEUR_EMPLOI
        self.candidate.availability_timing.recruitment_discretion_required = False
        
        result = self.scorer.calculate_availability_timing_score(
            self.candidate, self.company
        )
        
        self.assertGreater(result["score_breakdown"]["flexibility_bonus"], 0.0)
    
    def test_conversion_timing_to_weeks(self):
        """Test conversion timing vers semaines"""
        self.assertEqual(self.scorer._convert_timing_to_weeks("immediat"), 0)
        self.assertEqual(self.scorer._convert_timing_to_weeks("1mois"), 4)
        self.assertEqual(self.scorer._convert_timing_to_weeks("2mois"), 8)
        self.assertEqual(self.scorer._convert_timing_to_weeks("3mois"), 12)

class TestContractTypesScorer(unittest.TestCase):
    """📋 Tests ContractTypesScorer"""
    
    def setUp(self):
        """Configuration tests"""
        self.scorer = ContractTypesScorer()
        
        # Mock candidat de base
        self.base_candidate = Mock()
        self.base_candidate.attentes.salaire_min = 40000
        self.base_candidate.attentes.salaire_max = 55000
        self.base_candidate.experience_globale = Mock()
        self.base_candidate.experience_globale.value = "CONFIRME"
        
        # Mock entreprise de base
        self.base_company = Mock()
        self.base_company.poste.salaire_min = 42000
        self.base_company.poste.salaire_max = 60000
        self.base_company.recrutement.urgence = UrgenceRecrutement.NORMAL
        
        # Candidat complet
        self.candidate = Mock(spec=ExtendedCandidateProfileV3)
        self.candidate.base_profile = self.base_candidate
        self.candidate.transport_preferences = TransportPreferencesV3(
            contract_ranking=[TypeContrat.CDI, TypeContrat.FREELANCE, TypeContrat.CDD]
        )
        self.candidate.availability_timing = AvailabilityTimingV3(
            employment_status=CandidateStatusType.EN_POSTE
        )
        
        # Entreprise complète
        self.company = Mock(spec=ExtendedCompanyProfileV3)
        self.company.base_profile = self.base_company
        self.company.job_benefits = JobBenefitsV3(
            contract_nature=TypeContrat.CDI,
            job_benefits=["Mutuelle", "Tickets restaurant", "CE"]
        )
        self.company.recruitment_process = Mock()
        self.company.recruitment_process.trial_period_duration = 2
    
    def test_perfect_contract_match(self):
        """Test match contrat parfait"""
        # Contrat offert = première préférence
        self.company.job_benefits.contract_nature = TypeContrat.CDI
        
        result = self.scorer.calculate_contract_types_score(
            self.candidate, self.company
        )
        
        self.assertGreaterEqual(result["final_score"], 0.8)
        self.assertEqual(result["compatibility_level"], ContractCompatibilityLevel.IDEAL.value)
        self.assertEqual(result["contract_analysis"]["position_in_ranking"], 1)
    
    def test_second_preference_contract(self):
        """Test deuxième préférence contrat"""
        # Contrat offert = deuxième préférence
        self.company.job_benefits.contract_nature = TypeContrat.FREELANCE
        
        result = self.scorer.calculate_contract_types_score(
            self.candidate, self.company
        )
        
        self.assertGreaterEqual(result["final_score"], 0.6)
        self.assertEqual(result["compatibility_level"], ContractCompatibilityLevel.PREFERRED.value)
        self.assertEqual(result["contract_analysis"]["position_in_ranking"], 2)
    
    def test_contract_not_in_ranking(self):
        """Test contrat hors ranking"""
        # Contrat non dans les préférences
        self.company.job_benefits.contract_nature = TypeContrat.INTERIM
        
        result = self.scorer.calculate_contract_types_score(
            self.candidate, self.company
        )
        
        self.assertLessEqual(result["final_score"], 0.4)
        self.assertEqual(result["compatibility_level"], ContractCompatibilityLevel.INCOMPATIBLE.value)
        self.assertGreater(result["contract_analysis"]["position_in_ranking"], 3)
    
    def test_salary_compatibility(self):
        """Test compatibilité salariale"""
        # Fourchettes qui se chevauchent
        self.base_candidate.attentes.salaire_min = 45000
        self.base_candidate.attentes.salaire_max = 55000
        self.base_company.poste.salaire_min = 50000
        self.base_company.poste.salaire_max = 65000
        
        result = self.scorer.calculate_contract_types_score(
            self.candidate, self.company
        )
        
        self.assertGreater(result["score_breakdown"]["salary_compatibility"], 0.6)
    
    def test_flexibility_bonus(self):
        """Test bonus flexibilité"""
        # Candidat flexible + nombreux avantages
        self.candidate.transport_preferences.contract_ranking = [
            TypeContrat.CDI, TypeContrat.FREELANCE, TypeContrat.CDD, TypeContrat.INTERIM
        ]
        self.company.job_benefits.job_benefits = [
            "Mutuelle", "Tickets restaurant", "CE", "Parking", "Salle sport", "Télétravail"
        ]
        
        result = self.scorer.calculate_contract_types_score(
            self.candidate, self.company
        )
        
        self.assertGreater(result["score_breakdown"]["flexibility_bonus"], 0.0)

class TestWorkEnvironmentScorer(unittest.TestCase):
    """🏢 Tests WorkEnvironmentScorer"""
    
    def setUp(self):
        """Configuration tests"""
        self.scorer = WorkEnvironmentScorer()
        
        # Mock candidat de base
        self.base_candidate = Mock()
        
        # Candidat complet
        self.candidate = Mock(spec=ExtendedCandidateProfileV3)
        self.candidate.base_profile = self.base_candidate
        self.candidate.transport_preferences = TransportPreferencesV3(
            office_preference=WorkModalityType.HYBRID,
            max_travel_time=30,
            flexible_hours_important=True,
            parking_required=False,
            public_transport_accessibility=4
        )
        self.candidate.remote_work_experience = True
        self.candidate.management_experience = False
        
        # Entreprise complète
        self.company = Mock(spec=ExtendedCompanyProfileV3)
        self.company.base_profile = Mock()
        self.company.base_profile.poste.localisation = "Paris 9ème"
        self.company.job_benefits = JobBenefitsV3(
            remote_policy=WorkModalityType.HYBRID,
            job_benefits=["Mutuelle", "Tickets restaurant", "Parking"]
        )
        self.company.company_profile_v3 = Mock()
        self.company.company_profile_v3.company_culture = ["Innovation", "Autonomie"]
        self.company.company_profile_v3.team_size_hiring_for = 8
        self.company.company_profile_v3.growth_stage = "growth"
        self.company.company_profile_v3.company_size = Mock()
        self.company.company_profile_v3.company_size.value = "startup"
        self.company.recruitment_process = Mock()
        self.company.recruitment_process.trial_period_duration = 3
    
    def test_perfect_remote_match(self):
        """Test match remote parfait"""
        # Candidat et entreprise en hybrid
        self.candidate.transport_preferences.office_preference = WorkModalityType.HYBRID
        self.company.job_benefits.remote_policy = WorkModalityType.HYBRID
        
        result = self.scorer.calculate_work_environment_score(
            self.candidate, self.company
        )
        
        self.assertGreaterEqual(result["final_score"], 0.7)
        self.assertEqual(
            result["environment_analysis"]["candidate_office_preference"], 
            WorkModalityType.HYBRID.value
        )
        self.assertEqual(
            result["environment_analysis"]["company_remote_policy"], 
            WorkModalityType.HYBRID.value
        )
    
    def test_remote_incompatibility(self):
        """Test incompatibilité remote"""
        # Candidat full remote, entreprise on-site
        self.candidate.transport_preferences.office_preference = WorkModalityType.FULL_REMOTE
        self.company.job_benefits.remote_policy = WorkModalityType.ON_SITE
        
        result = self.scorer.calculate_work_environment_score(
            self.candidate, self.company
        )
        
        self.assertLessEqual(result["final_score"], 0.5)
        self.assertLess(result["score_breakdown"]["remote_compatibility"], 0.3)
    
    def test_schedule_flexibility(self):
        """Test flexibilité horaires"""
        # Candidat a besoin de flexibilité
        self.candidate.transport_preferences.flexible_hours_important = True
        
        result = self.scorer.calculate_work_environment_score(
            self.candidate, self.company
        )
        
        # Startup = généralement plus flexible
        self.assertGreater(result["score_breakdown"]["schedule_flexibility"], 0.6)
    
    def test_commute_analysis(self):
        """Test analyse trajets"""
        # Temps trajet acceptable
        self.candidate.transport_preferences.max_travel_time = 45
        
        result = self.scorer.calculate_work_environment_score(
            self.candidate, self.company
        )
        
        self.assertGreater(result["score_breakdown"]["commute_analysis"], 0.5)
        self.assertLessEqual(
            result["environment_analysis"]["estimated_commute_time"], 
            result["environment_analysis"]["max_acceptable_time"]
        )
    
    def test_culture_alignment(self):
        """Test alignement culture"""
        # Culture autonomie + candidat remote
        self.candidate.transport_preferences.office_preference = WorkModalityType.HYBRID
        self.company.company_profile_v3.company_culture = ["Autonomie", "Innovation"]
        
        result = self.scorer.calculate_work_environment_score(
            self.candidate, self.company
        )
        
        self.assertGreater(result["score_breakdown"]["culture_alignment"], 0.6)
        self.assertIn("autonomie", str(result["environment_analysis"]["culture_alignment_factors"]).lower())
    
    def test_workplace_benefits(self):
        """Test avantages lieu travail"""
        # Candidat ne nécessite pas parking
        self.candidate.transport_preferences.parking_required = False
        
        result = self.scorer.calculate_work_environment_score(
            self.candidate, self.company
        )
        
        self.assertGreaterEqual(result["score_breakdown"]["workplace_benefits"], 0.4)
    
    def test_remote_compatibility_matrix(self):
        """Test matrice compatibilité remote"""
        # Test différentes combinaisons
        test_cases = [
            (WorkModalityType.FULL_REMOTE, WorkModalityType.FULL_REMOTE, 1.0),
            (WorkModalityType.HYBRID, WorkModalityType.HYBRID, 1.0),
            (WorkModalityType.ON_SITE, WorkModalityType.ON_SITE, 1.0),
            (WorkModalityType.FULL_REMOTE, WorkModalityType.ON_SITE, 0.1),
        ]
        
        for candidate_pref, company_policy, expected_min_score in test_cases:
            self.candidate.transport_preferences.office_preference = candidate_pref
            self.company.job_benefits.remote_policy = company_policy
            
            result = self.scorer.calculate_work_environment_score(
                self.candidate, self.company
            )
            
            if expected_min_score >= 0.8:
                self.assertGreaterEqual(result["score_breakdown"]["remote_compatibility"], 0.8)
            elif expected_min_score <= 0.2:
                self.assertLessEqual(result["score_breakdown"]["remote_compatibility"], 0.3)

class TestScorersIntegration(unittest.TestCase):
    """🔗 Tests intégration scorers"""
    
    def setUp(self):
        """Configuration tests intégration"""
        self.timing_scorer = AvailabilityTimingScorer()
        self.contract_scorer = ContractTypesScorer()
        self.environment_scorer = WorkEnvironmentScorer()
        
        # Profils candidat et entreprise complets
        self.candidate = self._create_full_candidate()
        self.company = self._create_full_company()
    
    def _create_full_candidate(self) -> Mock:
        """Création candidat complet pour tests"""
        candidate = Mock(spec=ExtendedCandidateProfileV3)
        
        # Base profile
        candidate.base_profile = Mock()
        candidate.base_profile.attentes.salaire_min = 45000
        candidate.base_profile.attentes.salaire_max = 60000
        candidate.base_profile.experience_globale = Mock()
        candidate.base_profile.experience_globale.value = "CONFIRME"
        
        # Transport preferences
        candidate.transport_preferences = TransportPreferencesV3(
            office_preference=WorkModalityType.HYBRID,
            max_travel_time=35,
            contract_ranking=[TypeContrat.CDI, TypeContrat.FREELANCE],
            flexible_hours_important=True,
            parking_required=False,
            public_transport_accessibility=4
        )
        
        # Availability timing
        candidate.availability_timing = AvailabilityTimingV3(
            timing="2mois",
            employment_status=CandidateStatusType.EN_POSTE,
            notice_period_weeks=8,
            start_date_flexibility=3,
            recruitment_discretion_required=True
        )
        
        # Additional attributes
        candidate.remote_work_experience = True
        candidate.management_experience = False
        
        return candidate
    
    def _create_full_company(self) -> Mock:
        """Création entreprise complète pour tests"""
        company = Mock(spec=ExtendedCompanyProfileV3)
        
        # Base profile
        company.base_profile = Mock()
        company.base_profile.poste.salaire_min = 50000
        company.base_profile.poste.salaire_max = 70000
        company.base_profile.poste.localisation = "Paris 10ème"
        company.base_profile.recrutement.urgence = UrgenceRecrutement.NORMAL
        
        # Job benefits
        company.job_benefits = JobBenefitsV3(
            contract_nature=TypeContrat.CDI,
            remote_policy=WorkModalityType.HYBRID,
            job_benefits=["Mutuelle", "Tickets restaurant", "Parking", "CE"]
        )
        
        # Company profile
        company.company_profile_v3 = Mock()
        company.company_profile_v3.company_culture = ["Innovation", "Autonomie"]
        company.company_profile_v3.team_size_hiring_for = 6
        company.company_profile_v3.growth_stage = "growth"
        company.company_profile_v3.company_size = Mock()
        company.company_profile_v3.company_size.value = "startup"
        
        # Recruitment process
        company.recruitment_process = Mock()
        company.recruitment_process.recruitment_delays = "2-3 mois"
        company.recruitment_process.notice_management = "Flexible selon profil"
        company.recruitment_process.trial_period_duration = 3
        
        return company
    
    def test_all_scorers_execution(self):
        """Test exécution de tous les scorers"""
        # Test chaque scorer individuellement
        timing_result = self.timing_scorer.calculate_availability_timing_score(
            self.candidate, self.company
        )
        
        contract_result = self.contract_scorer.calculate_contract_types_score(
            self.candidate, self.company
        )
        
        environment_result = self.environment_scorer.calculate_work_environment_score(
            self.candidate, self.company
        )
        
        # Validation structure des résultats
        for result in [timing_result, contract_result, environment_result]:
            self.assertIn("final_score", result)
            self.assertIn("compatibility_level", result)
            self.assertIn("score_breakdown", result)
            self.assertIn("explanations", result)
            self.assertIn("recommendations", result)
            self.assertIn("calculated_at", result)
            self.assertIn("version", result)
            self.assertIn("scorer", result)
            
            # Validation valeurs
            self.assertGreaterEqual(result["final_score"], 0.0)
            self.assertLessEqual(result["final_score"], 1.0)
            self.assertIsInstance(result["explanations"], list)
            self.assertIsInstance(result["recommendations"], list)
    
    def test_performance_stats(self):
        """Test statistiques performance"""
        # Exécution multiple pour générer stats
        for i in range(10):
            self.timing_scorer.calculate_availability_timing_score(
                self.candidate, self.company
            )
            self.contract_scorer.calculate_contract_types_score(
                self.candidate, self.company
            )
            self.environment_scorer.calculate_work_environment_score(
                self.candidate, self.company
            )
        
        # Vérification stats
        timing_stats = self.timing_scorer.get_performance_stats()
        contract_stats = self.contract_scorer.get_performance_stats()
        environment_stats = self.environment_scorer.get_performance_stats()
        
        for stats in [timing_stats, contract_stats, environment_stats]:
            self.assertIn("scorer_stats", stats)
            self.assertIn("performance_metrics", stats)
            self.assertIn("configuration", stats)
            self.assertEqual(stats["scorer_stats"]["total_calculations"], 10)
    
    def test_fallback_scenarios(self):
        """Test scénarios de fallback"""
        # Test avec candidat/entreprise invalides
        invalid_candidate = Mock()
        invalid_company = Mock()
        
        # Chaque scorer doit gérer les erreurs gracieusement
        timing_result = self.timing_scorer.calculate_availability_timing_score(
            invalid_candidate, invalid_company
        )
        
        contract_result = self.contract_scorer.calculate_contract_types_score(
            invalid_candidate, invalid_company
        )
        
        environment_result = self.environment_scorer.calculate_work_environment_score(
            invalid_candidate, invalid_company
        )
        
        # Validation fallback
        for result in [timing_result, contract_result, environment_result]:
            self.assertIn("error", result)
            self.assertIn("fallback", result["version"])
            self.assertGreaterEqual(result["final_score"], 0.0)
            self.assertLessEqual(result["final_score"], 1.0)

def run_all_tests():
    """🚀 Exécution de tous les tests"""
    
    print("🧪 NEXTVISION V3.0 - TESTS SCORERS")
    print("=" * 50)
    
    # Suite de tests
    test_suite = unittest.TestSuite()
    
    # Ajout des tests
    test_suite.addTest(unittest.makeSuite(TestAvailabilityTimingScorer))
    test_suite.addTest(unittest.makeSuite(TestContractTypesScorer))
    test_suite.addTest(unittest.makeSuite(TestWorkEnvironmentScorer))
    test_suite.addTest(unittest.makeSuite(TestScorersIntegration))
    
    # Exécution
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Rapport final
    print("\n" + "=" * 50)
    print(f"🎯 RÉSULTATS FINAUX:")
    print(f"✅ Tests réussis: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Échecs: {len(result.failures)}")
    print(f"🚨 Erreurs: {len(result.errors)}")
    print(f"📊 Taux de réussite: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.wasSuccessful():
        print("\n🌟 TOUS LES TESTS PASSENT - SCORERS V3.0 VALIDÉS ✅")
    else:
        print("\n⚠️ CERTAINS TESTS ÉCHOUENT - RÉVISION NÉCESSAIRE")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_all_tests()
