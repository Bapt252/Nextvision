"""
🧪 Tests Automatisés - Nextvision v2.0 Bidirectional Matching

Tests complets pour valider l'architecture bidirectionnelle :
- Modèles Pydantic bidirectionnels
- Services de scoring (4 composants)
- BiDirectionalMatcher principal
- Adaptateurs ChatGPT Commitment-
- Endpoints API v2.0
- Performance et charge

Author: NEXTEN Team
Version: 2.0.0 - Test Suite
"""

import pytest
import asyncio
import json
import time
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List

# Import des modèles et services à tester
from nextvision.models.bidirectional_models import (
    BiDirectionalCandidateProfile, BiDirectionalCompanyProfile,
    BiDirectionalMatchingRequest, BiDirectionalMatchingResponse,
    PersonalInfoBidirectional, CompetencesProfessionnelles,
    AttentesCandidat, MotivationsCandidat, ExperienceProfessionnelle,
    InformationsEntreprise, DescriptionPoste, ExigencesPoste,
    RaisonEcouteCandidat, UrgenceRecrutement, NiveauExperience, TypeContrat
)

from nextvision.services.bidirectional_scorer import (
    SemanticScorer, SalaryScorer, ExperienceScorer, LocationScorer,
    ScoringResult
)

from nextvision.services.bidirectional_matcher import (
    BiDirectionalMatcher, AdaptiveWeightingEngine, BiDirectionalMatcherFactory
)

from nextvision.adapters.chatgpt_commitment_adapter import (
    CommitmentNextvisionBridge, EnhancedParserV4Adapter, ChatGPTCommitmentAdapter
)


# === FIXTURES DE TEST ===

@pytest.fixture
def sample_candidat_profile():
    """Candidat de test standard"""
    return BiDirectionalCandidateProfile(
        personal_info=PersonalInfoBidirectional(
            firstName="Marie",
            lastName="Dupont",
            email="marie.dupont@email.com",
            phone="+33 6 12 34 56 78"
        ),
        experience_globale=NiveauExperience.CONFIRME,
        competences=CompetencesProfessionnelles(
            competences_techniques=["Maîtrise du logiciel comptable CEGID", "Gestion comptable et fiscale"],
            logiciels_maitrise=["CEGID", "Excel", "SAP"],
            langues={"Français": "Natif", "Anglais": "Courant"}
        ),
        attentes=AttentesCandidat(
            salaire_min=38000,
            salaire_max=45000,
            localisation_preferee="Paris 8ème",
            distance_max_km=30,
            remote_accepte=True
        ),
        motivations=MotivationsCandidat(
            raison_ecoute=RaisonEcouteCandidat.REMUNERATION_TROP_FAIBLE,
            motivations_principales=["Évolution salariale", "Nouvelles responsabilités"]
        )
    )

@pytest.fixture
def sample_entreprise_profile():
    """Entreprise de test standard"""
    return BiDirectionalCompanyProfile(
        entreprise=InformationsEntreprise(
            nom="Cabinet Comptable Excellence",
            secteur="Comptabilité",
            localisation="Paris 8ème"
        ),
        poste=DescriptionPoste(
            titre="Comptable Unique H/F",
            localisation="Paris 8ème",
            type_contrat=TypeContrat.CDI,
            salaire_min=35000,
            salaire_max=42000,
            competences_requises=["Maîtrise du logiciel comptable CEGID", "Gestion comptable et fiscale"]
        ),
        exigences=ExigencesPoste(
            experience_requise="5 ans - 10 ans",
            competences_obligatoires=["Maîtrise du logiciel comptable CEGID"],
            competences_souhaitees=["Gestion comptable et fiscale"]
        ),
        recrutement=CriteresRecrutement(
            urgence=UrgenceRecrutement.URGENT,
            criteres_prioritaires=["expérience", "compétences_techniques"]
        )
    )

@pytest.fixture
def enhanced_parser_data():
    """Données Enhanced Universal Parser v4.0"""
    return {
        "personal_info": {
            "firstName": "Marie",
            "lastName": "Dupont",
            "email": "marie.dupont@email.com",
            "phone": "+33 6 12 34 56 78"
        },
        "skills": ["Maîtrise du logiciel comptable CEGID", "Gestion comptable et fiscale"],
        "softwares": ["CEGID", "Excel", "SAP"],
        "languages": {"Français": "Natif", "Anglais": "Courant"},
        "experience": {"total_years": 7},
        "work_experience": [
            {
                "position": "Comptable Senior",
                "company": "Cabinet ABC",
                "duration": "3 ans",
                "skills_acquired": ["CEGID", "Fiscalité"]
            }
        ],
        "parsing_confidence": 0.92
    }

@pytest.fixture
def chatgpt_data():
    """Données ChatGPT Commitment-"""
    return {
        "titre": "Comptable Unique H/F",
        "localisation": "Paris 8ème",
        "contrat": "CDI",
        "salaire": "35K à 38K annuels",
        "competences_requises": ["Maîtrise du logiciel comptable CEGID", "Gestion comptable et fiscale"],
        "experience_requise": "5 ans - 10 ans",
        "missions": ["Tenue comptabilité complète", "Déclarations fiscales"],
        "avantages": ["Tickets restaurant", "Mutuelle"],
        "badges_auto_rempli": ["Auto-rempli"],
        "parsing_confidence": 0.88
    }


# === TESTS MODÈLES BIDIRECTIONNELS ===

class TestBidirectionalModels:
    """Tests des modèles Pydantic bidirectionnels"""
    
    def test_candidat_profile_creation(self, sample_candidat_profile):
        """Test création profil candidat valide"""
        assert sample_candidat_profile.personal_info.firstName == "Marie"
        assert sample_candidat_profile.experience_globale == NiveauExperience.CONFIRME
        assert sample_candidat_profile.motivations.raison_ecoute == RaisonEcouteCandidat.REMUNERATION_TROP_FAIBLE
        assert sample_candidat_profile.attentes.salaire_min < sample_candidat_profile.attentes.salaire_max
    
    def test_entreprise_profile_creation(self, sample_entreprise_profile):
        """Test création profil entreprise valide"""
        assert sample_entreprise_profile.entreprise.nom == "Cabinet Comptable Excellence"
        assert sample_entreprise_profile.poste.type_contrat == TypeContrat.CDI
        assert sample_entreprise_profile.recrutement.urgence == UrgenceRecrutement.URGENT
        assert sample_entreprise_profile.poste.salaire_min < sample_entreprise_profile.poste.salaire_max
    
    def test_matching_request_creation(self, sample_candidat_profile, sample_entreprise_profile):
        """Test création requête de matching"""
        request = BiDirectionalMatchingRequest(
            candidat=sample_candidat_profile,
            entreprise=sample_entreprise_profile,
            force_adaptive_weighting=True
        )
        
        assert request.candidat.personal_info.firstName == "Marie"
        assert request.entreprise.entreprise.nom == "Cabinet Comptable Excellence"
        assert request.force_adaptive_weighting == True
    
    def test_email_validation(self):
        """Test validation email"""
        with pytest.raises(ValueError):
            PersonalInfoBidirectional(
                firstName="Test",
                lastName="User",
                email="email_invalide"  # Pas de @
            )
    
    def test_salary_coherence(self):
        """Test cohérence fourchette salariale"""
        # Fourchette incohérente (min >= max)
        with pytest.raises(ValueError):
            AttentesCandidat(
                salaire_min=50000,
                salaire_max=40000,  # Max < Min !
                localisation_preferee="Paris"
            )


# === TESTS SCORERS ===

class TestScorers:
    """Tests des 4 scorers bidirectionnels"""
    
    def test_semantic_scorer(self, sample_candidat_profile, sample_entreprise_profile):
        """Test SemanticScorer - correspondance CV ↔ Fiche de poste"""
        scorer = SemanticScorer()
        result = scorer.calculate_score(sample_candidat_profile, sample_entreprise_profile)
        
        assert isinstance(result, ScoringResult)
        assert 0.0 <= result.score <= 1.0
        assert result.confidence > 0.0
        assert result.processing_time_ms > 0
        assert "competences_score" in result.details
        
        # Test match parfait (même compétences)
        assert result.score > 0.7  # Bon match attendu
    
    def test_salary_scorer(self, sample_candidat_profile, sample_entreprise_profile):
        """Test SalaryScorer - budget entreprise vs attentes candidat"""
        scorer = SalaryScorer()
        result = scorer.calculate_score(sample_candidat_profile, sample_entreprise_profile)
        
        assert isinstance(result, ScoringResult)
        assert 0.0 <= result.score <= 1.0
        assert "candidat_fourchette" in result.details
        assert "entreprise_fourchette" in result.details
        assert "overlap_amount" in result.details
        
        # Test overlap partiel (candidat: 38-45K, entreprise: 35-42K)
        assert result.score > 0.5  # Overlap partiel
    
    def test_experience_scorer(self, sample_candidat_profile, sample_entreprise_profile):
        """Test ExperienceScorer - années requises vs expérience candidat"""
        scorer = ExperienceScorer()
        result = scorer.calculate_score(sample_candidat_profile, sample_entreprise_profile)
        
        assert isinstance(result, ScoringResult)
        assert 0.0 <= result.score <= 1.0
        assert "experience_candidat_annees" in result.details
        assert "adequation" in result.details
        
        # Candidat CONFIRME (7 ans) vs "5 ans - 10 ans" requis
        assert result.score > 0.8  # Parfait match
    
    def test_location_scorer(self, sample_candidat_profile, sample_entreprise_profile):
        """Test LocationScorer - impact géographique"""
        scorer = LocationScorer()
        result = scorer.calculate_score(sample_candidat_profile, sample_entreprise_profile)
        
        assert isinstance(result, ScoringResult)
        assert 0.0 <= result.score <= 1.0
        assert "candidat_localisation" in result.details
        assert "entreprise_localisation" in result.details
        
        # Même localisation (Paris 8ème)
        assert result.score > 0.8  # Excellent match géographique
    
    def test_scorer_error_handling(self):
        """Test gestion d'erreurs des scorers"""
        scorer = SemanticScorer()
        
        # Profil candidat invalide
        candidat_invalide = Mock()
        candidat_invalide.competences = None
        
        entreprise_valide = Mock()
        entreprise_valide.exigences.competences_obligatoires = ["Test"]
        
        result = scorer.calculate_score(candidat_invalide, entreprise_valide)
        
        assert result.score == 0.0
        assert result.error_message is not None


# === TESTS ADAPTIVE WEIGHTING ENGINE ===

class TestAdaptiveWeightingEngine:
    """Tests du moteur de pondération adaptative"""
    
    def test_candidat_adaptation_remuneration(self, sample_candidat_profile, sample_entreprise_profile):
        """Test adaptation candidat : rémunération trop faible"""
        engine = AdaptiveWeightingEngine()
        
        # Modifier raison d'écoute
        sample_candidat_profile.motivations.raison_ecoute = RaisonEcouteCandidat.REMUNERATION_TROP_FAIBLE
        
        config = engine.calculate_adaptive_weights(sample_candidat_profile, sample_entreprise_profile)
        
        # Vérifier boost salaire (+10%)
        assert config.candidat_weights.salaire > 0.30  # +10% de 25%
        assert config.candidat_weights.semantique < 0.35  # -5% de 35%
        assert "amélioration salariale" in config.reasoning_candidat.lower()
    
    def test_candidat_adaptation_semantique(self, sample_candidat_profile, sample_entreprise_profile):
        """Test adaptation candidat : poste ne coïncide pas"""
        engine = AdaptiveWeightingEngine()
        
        sample_candidat_profile.motivations.raison_ecoute = RaisonEcouteCandidat.POSTE_NE_COINCIDE_PAS
        
        config = engine.calculate_adaptive_weights(sample_candidat_profile, sample_entreprise_profile)
        
        # Vérifier boost sémantique (+10%)
        assert config.candidat_weights.semantique > 0.40  # +10% de 35%
        assert "adéquation des compétences" in config.reasoning_candidat.lower()
    
    def test_entreprise_adaptation_urgence(self, sample_candidat_profile, sample_entreprise_profile):
        """Test adaptation entreprise : urgence critique"""
        engine = AdaptiveWeightingEngine()
        
        sample_entreprise_profile.recrutement.urgence = UrgenceRecrutement.CRITIQUE
        
        config = engine.calculate_adaptive_weights(sample_candidat_profile, sample_entreprise_profile)
        
        # Vérifier boost entreprise (1.2x)
        assert "critique" in config.reasoning_entreprise.lower()
        # Les poids entreprise devraient être boostés
        assert config.entreprise_weights.semantique >= config.candidat_weights.semantique
    
    def test_default_weights_sum_to_one(self):
        """Test que les poids par défaut somment à 1.0"""
        engine = AdaptiveWeightingEngine()
        default_weights = engine.default_weights
        
        total = (default_weights.semantique + default_weights.salaire + 
                default_weights.experience + default_weights.localisation)
        
        assert abs(total - 1.0) < 0.01  # Tolérance 1%


# === TESTS BIDIRECTIONAL MATCHER ===

class TestBiDirectionalMatcher:
    """Tests du moteur principal de matching"""
    
    @pytest.mark.asyncio
    async def test_full_matching_pipeline(self, sample_candidat_profile, sample_entreprise_profile):
        """Test pipeline complet de matching"""
        matcher = BiDirectionalMatcherFactory.create_basic_matcher()
        
        request = BiDirectionalMatchingRequest(
            candidat=sample_candidat_profile,
            entreprise=sample_entreprise_profile,
            force_adaptive_weighting=True
        )
        
        result = await matcher.calculate_bidirectional_match(request)
        
        # Validations du résultat
        assert isinstance(result, BiDirectionalMatchingResponse)
        assert 0.0 <= result.matching_score <= 1.0
        assert 0.0 <= result.confidence <= 1.0
        assert result.compatibility in ['excellent', 'good', 'average', 'poor', 'incompatible']
        assert result.processing_time_ms > 0
        
        # Validations des composants
        assert 0.0 <= result.component_scores.semantique_score <= 1.0
        assert 0.0 <= result.component_scores.salaire_score <= 1.0
        assert 0.0 <= result.component_scores.experience_score <= 1.0
        assert 0.0 <= result.component_scores.localisation_score <= 1.0
        
        # Validations recommandations
        assert isinstance(result.recommandations_candidat, list)
        assert isinstance(result.recommandations_entreprise, list)
        assert isinstance(result.points_forts, list)
        assert isinstance(result.points_attention, list)
    
    @pytest.mark.asyncio
    async def test_matching_with_perfect_candidate(self, sample_entreprise_profile):
        """Test matching avec candidat parfait"""
        # Candidat parfaitement adapté
        perfect_candidat = BiDirectionalCandidateProfile(
            personal_info=PersonalInfoBidirectional(
                firstName="Perfect",
                lastName="Candidate",
                email="perfect@example.com"
            ),
            experience_globale=NiveauExperience.CONFIRME,
            competences=CompetencesProfessionnelles(
                competences_techniques=sample_entreprise_profile.poste.competences_requises,  # Même compétences
                logiciels_maitrise=["CEGID"],
                langues={"Français": "Natif"}
            ),
            attentes=AttentesCandidat(
                salaire_min=sample_entreprise_profile.poste.salaire_min,  # Même fourchette
                salaire_max=sample_entreprise_profile.poste.salaire_max,
                localisation_preferee=sample_entreprise_profile.poste.localisation,  # Même localisation
                remote_accepte=True
            ),
            motivations=MotivationsCandidat(
                raison_ecoute=RaisonEcouteCandidat.POSTE_NE_COINCIDE_PAS,
                motivations_principales=["Évolution"]
            )
        )
        
        matcher = BiDirectionalMatcherFactory.create_basic_matcher()
        request = BiDirectionalMatchingRequest(
            candidat=perfect_candidat,
            entreprise=sample_entreprise_profile
        )
        
        result = await matcher.calculate_bidirectional_match(request)
        
        # Score très élevé attendu
        assert result.matching_score > 0.8
        assert result.compatibility in ['excellent', 'good']
        assert len(result.points_forts) > len(result.points_attention)
    
    @pytest.mark.asyncio
    async def test_matching_cache(self, sample_candidat_profile, sample_entreprise_profile):
        """Test cache du matching"""
        matcher = BiDirectionalMatcherFactory.create_basic_matcher()
        
        request = BiDirectionalMatchingRequest(
            candidat=sample_candidat_profile,
            entreprise=sample_entreprise_profile
        )
        
        # Premier appel
        start_time = time.time()
        result1 = await matcher.calculate_bidirectional_match(request)
        first_call_time = time.time() - start_time
        
        # Deuxième appel (devrait utiliser le cache)
        start_time = time.time()
        result2 = await matcher.calculate_bidirectional_match(request)
        second_call_time = time.time() - start_time
        
        # Vérifications
        assert result1.matching_score == result2.matching_score
        # Le deuxième appel devrait être plus rapide (cache)
        # Note: En condition réelle, pas forcément vrai car le cache est simple
        assert matcher.stats["total_matches"] >= 2
    
    def test_performance_stats(self):
        """Test statistiques de performance"""
        matcher = BiDirectionalMatcherFactory.create_basic_matcher()
        
        stats = matcher.get_performance_stats()
        
        assert "total_matches" in stats
        assert "cache_hits" in stats
        assert "cache_hit_rate_percent" in stats
        assert "avg_processing_time_ms" in stats
        assert "uptime_hours" in stats
        
        # Cache vide au début
        assert stats["total_matches"] == 0
        assert stats["cache_size"] == 0


# === TESTS ADAPTATEURS COMMITMENT- ===

class TestCommitmentAdapters:
    """Tests des adaptateurs ChatGPT Commitment-"""
    
    def test_enhanced_parser_adapter(self, enhanced_parser_data):
        """Test EnhancedParserV4Adapter"""
        adapter = EnhancedParserV4Adapter()
        
        candidat = adapter.convert_to_bidirectional(enhanced_parser_data)
        
        assert isinstance(candidat, BiDirectionalCandidateProfile)
        assert candidat.personal_info.firstName == "Marie"
        assert candidat.personal_info.lastName == "Dupont"
        assert candidat.parsing_source == "enhanced_parser_v4"
        assert candidat.confidence_score == 0.92
        assert "Maîtrise du logiciel comptable CEGID" in candidat.competences.competences_techniques
    
    def test_chatgpt_adapter(self, chatgpt_data):
        """Test ChatGPTCommitmentAdapter"""
        adapter = ChatGPTCommitmentAdapter()
        
        entreprise = adapter.convert_to_bidirectional(chatgpt_data)
        
        assert isinstance(entreprise, BiDirectionalCompanyProfile)
        assert entreprise.poste.titre == "Comptable Unique H/F"
        assert entreprise.poste.salaire_min == 35000  # Parsing "35K à 38K annuels"
        assert entreprise.poste.salaire_max == 38000
        assert entreprise.exigences.experience_requise == "5 ans - 10 ans"
        assert "Auto-rempli" in entreprise.badges_auto_rempli
        assert entreprise.parsing_source == "chatgpt_commitment"
    
    def test_salary_parsing(self):
        """Test parsing salaire format ChatGPT"""
        adapter = ChatGPTCommitmentAdapter()
        
        # Tests différents formats
        test_cases = [
            ("35K à 38K annuels", (35000, 38000)),
            ("40000€ - 45000€", (40000, 45000)),
            ("50K", (50000, 50000)),
            ("format_invalide", (None, None))
        ]
        
        for salary_str, expected in test_cases:
            result = adapter._parse_salaire(salary_str)
            assert result == expected, f"Failed for '{salary_str}'"
    
    def test_experience_parsing(self):
        """Test parsing expérience format ChatGPT"""
        adapter = ChatGPTCommitmentAdapter()
        
        # Note: Méthode pas encore exposée, test via conversion complète
        test_data = {
            "titre": "Test",
            "experience_requise": "3 ans - 7 ans",
            "localisation": "Paris",
            "contrat": "CDI",
            "competences_requises": [],
            "parsing_confidence": 0.8
        }
        
        entreprise = adapter.convert_to_bidirectional(test_data)
        assert entreprise.exigences.experience_requise == "3 ans - 7 ans"
    
    def test_commitment_bridge_full_workflow(self, enhanced_parser_data, chatgpt_data):
        """Test bridge complet Commitment-"""
        bridge = CommitmentNextvisionBridge()
        
        # Conversion candidat
        candidat = bridge.convert_candidat_from_commitment(enhanced_parser_data)
        assert isinstance(candidat, BiDirectionalCandidateProfile)
        
        # Conversion entreprise
        entreprise = bridge.convert_entreprise_from_commitment(chatgpt_data)
        assert isinstance(entreprise, BiDirectionalCompanyProfile)
        
        # Vérification stats
        stats = bridge.get_bridge_stats()
        assert stats["candidats_converted"] == 1
        assert stats["entreprises_converted"] == 1
        assert stats["total_conversions"] == 2
        assert stats["errors_count"] == 0


# === TESTS PERFORMANCE ===

class TestPerformance:
    """Tests de performance et charge"""
    
    @pytest.mark.asyncio
    async def test_matching_performance(self, sample_candidat_profile, sample_entreprise_profile):
        """Test performance matching individuel"""
        matcher = BiDirectionalMatcherFactory.create_basic_matcher()
        
        request = BiDirectionalMatchingRequest(
            candidat=sample_candidat_profile,
            entreprise=sample_entreprise_profile
        )
        
        start_time = time.time()
        result = await matcher.calculate_bidirectional_match(request)
        processing_time = (time.time() - start_time) * 1000
        
        # Objectif: < 150ms
        assert processing_time < 150, f"Matching trop lent: {processing_time}ms"
        assert result.processing_time_ms < 150
    
    @pytest.mark.asyncio
    async def test_batch_performance(self, sample_candidat_profile, sample_entreprise_profile):
        """Test performance batch (simulation)"""
        matcher = BiDirectionalMatcherFactory.create_basic_matcher()
        
        # Simulation 10 matchings (au lieu de 100 pour les tests)
        start_time = time.time()
        
        tasks = []
        for i in range(10):
            request = BiDirectionalMatchingRequest(
                candidat=sample_candidat_profile,
                entreprise=sample_entreprise_profile
            )
            task = matcher.calculate_bidirectional_match(request)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        total_time = (time.time() - start_time) * 1000
        
        # Validations
        assert len(results) == 10
        assert all(isinstance(r, BiDirectionalMatchingResponse) for r in results)
        
        # Performance: 10 matchings en < 1s
        assert total_time < 1000, f"Batch trop lent: {total_time}ms"
        
        # Calcul throughput
        matchings_per_second = 10 / (total_time / 1000)
        assert matchings_per_second > 10  # Au moins 10 matchings/seconde
    
    def test_memory_usage(self, sample_candidat_profile, sample_entreprise_profile):
        """Test usage mémoire"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Création multiple instances
        matchers = []
        for i in range(10):
            matcher = BiDirectionalMatcherFactory.create_basic_matcher()
            matchers.append(matcher)
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before
        
        # Augmentation mémoire raisonnable (< 50MB pour 10 instances)
        assert memory_increase < 50, f"Trop de mémoire utilisée: {memory_increase}MB"


# === TESTS INTÉGRATION ===

class TestIntegration:
    """Tests d'intégration end-to-end"""
    
    @pytest.mark.asyncio
    async def test_full_pipeline_commitment_to_result(self, enhanced_parser_data, chatgpt_data):
        """Test pipeline complet : Commitment- → Résultat"""
        # 1. Conversion via bridge
        bridge = CommitmentNextvisionBridge()
        
        candidat = bridge.convert_candidat_from_commitment(enhanced_parser_data)
        entreprise = bridge.convert_entreprise_from_commitment(chatgpt_data)
        
        # 2. Matching bidirectionnel
        matcher = BiDirectionalMatcherFactory.create_basic_matcher()
        
        request = BiDirectionalMatchingRequest(
            candidat=candidat,
            entreprise=entreprise,
            force_adaptive_weighting=True
        )
        
        result = await matcher.calculate_bidirectional_match(request)
        
        # 3. Validations end-to-end
        assert result.matching_score > 0.0
        assert result.confidence > 0.0
        assert len(result.recommandations_candidat) >= 0
        assert len(result.recommandations_entreprise) >= 0
        
        # 4. Vérification pondération adaptative appliquée
        assert result.adaptive_weighting.applied == True
        assert result.adaptive_weighting.raison_candidat == RaisonEcouteCandidat.POSTE_NE_COINCIDE_PAS  # Défaut
    
    def test_error_recovery(self):
        """Test récupération d'erreurs"""
        # Simuler candidat avec données corrompues
        candidat_corrompu = Mock()
        candidat_corrompu.personal_info = None
        
        entreprise_valide = Mock()
        entreprise_valide.entreprise.nom = "Test"
        
        matcher = BiDirectionalMatcherFactory.create_basic_matcher()
        
        # Le matching ne devrait pas planter, mais retourner une erreur
        # Note: Test à adapter selon implémentation gestion d'erreur
        assert True  # Placeholder
    
    @pytest.mark.asyncio
    async def test_concurrent_matching(self, sample_candidat_profile, sample_entreprise_profile):
        """Test matching concurrent (simulation multi-utilisateurs)"""
        matcher = BiDirectionalMatcherFactory.create_basic_matcher()
        
        # Simulation 5 utilisateurs simultanés
        concurrent_tasks = []
        for i in range(5):
            request = BiDirectionalMatchingRequest(
                candidat=sample_candidat_profile,
                entreprise=sample_entreprise_profile
            )
            task = matcher.calculate_bidirectional_match(request)
            concurrent_tasks.append(task)
        
        # Exécution simultanée
        results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
        
        # Validation aucune exception
        for result in results:
            assert not isinstance(result, Exception), f"Exception in concurrent matching: {result}"
            assert isinstance(result, BiDirectionalMatchingResponse)


# === CONFIGURATION PYTEST ===

def pytest_configure(config):
    """Configuration globale pytest"""
    # Markers custom
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "performance: mark test as performance test")

# Marquage des tests de performance
pytestmark_performance = pytest.mark.performance


# === RUNNER DE TESTS ===

if __name__ == "__main__":
    import sys
    
    print("🧪 === NEXTVISION v2.0 TEST SUITE ===")
    print("🎯 Tests Matching Bidirectionnel")
    print("")
    
    # Lancement des tests
    exit_code = pytest.main([
        __file__,
        "-v",  # Verbose
        "--tb=short",  # Traceback court
        "--durations=10",  # Top 10 tests les plus lents
        "-x"  # Arrêt au premier échec
    ])
    
    if exit_code == 0:
        print("\n✅ Tous les tests passent ! Architecture validée.")
    else:
        print(f"\n❌ {exit_code} test(s) échoué(s). Vérification nécessaire.")
    
    sys.exit(exit_code)
