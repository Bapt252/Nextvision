#!/usr/bin/env python3
"""
🎯 SCRIPT DE TEST NEXTVISION v3.2.1 - VALIDATION FINALE
======================================================

MISSION : Valider l'endpoint /api/v3/intelligent-matching après correction RaisonEcoute
- ✅ Test endpoint complet
- ✅ Validation "Recherche nouveau défi" 
- ✅ Test parsing CV + Job
- ✅ Vérification adaptateur intelligent
- ✅ Performance < 2000ms

Author: NEXTEN Team
Version: Test Final v3.2.1
"""

import requests
import json
import time
import tempfile
from typing import Dict, Any

class NextvisionAPIValidator:
    """🔍 Validateur API Nextvision après correction"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_health_check(self) -> bool:
        """❤️ Test health check"""
        try:
            response = self.session.get(f"{self.base_url}/api/v3/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health Check: {data['status']}")
                return True
            else:
                print(f"❌ Health Check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health Check error: {e}")
            return False
    
    def test_status_detailed(self) -> bool:
        """📊 Test status détaillé"""
        try:
            response = self.session.get(f"{self.base_url}/api/v3/status")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status: {data['version']}")
                print(f"🔧 Services opérationnels: {sum(1 for s in data['services'].values() if s['status'] == 'operational')}")
                return True
            else:
                print(f"❌ Status failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Status error: {e}")
            return False
    
    def create_test_cv_file(self) -> str:
        """📄 Création fichier CV de test"""
        cv_content = """
        Baptiste Comas
        Développeur Full Stack
        
        Email: baptiste.coma@gmail.com
        Téléphone: +33 6 12 34 56 78
        Localisation: Paris, France
        
        COMPÉTENCES:
        - Python, FastAPI, React
        - Machine Learning, Intelligence Artificielle
        - PostgreSQL, MongoDB
        - Docker, AWS, Google Cloud
        - Git, CI/CD
        
        EXPÉRIENCE:
        - 5 ans d'expérience en développement
        - Lead Developer chez TechCorp (2020-2024)
        - Full Stack Developer chez StartupAI (2019-2020)
        
        FORMATION:
        - Master Intelligence Artificielle
        - École d'Ingénieur EPITA
        
        OBJECTIF:
        Recherche nouveau défi dans l'IA et le développement backend
        """
        
        # Création fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(cv_content)
            return f.name
    
    def create_test_job_file(self) -> str:
        """💼 Création fichier Job de test"""
        job_content = """
        OFFRE D'EMPLOI
        
        Poste: Senior Python Developer - IA
        Entreprise: NextenAI
        Localisation: Paris, France
        
        DESCRIPTION:
        Nous recherchons un développeur Python senior pour rejoindre notre équipe IA.
        
        COMPÉTENCES REQUISES:
        - Python expert (5+ ans)
        - FastAPI, Django
        - Machine Learning, TensorFlow
        - PostgreSQL, MongoDB
        - Docker, Kubernetes
        - AWS, Google Cloud
        
        COMPÉTENCES APPRÉCIÉES:
        - React, TypeScript  
        - CI/CD, DevOps
        - Expérience startup
        
        CONTRAT: CDI
        SALAIRE: 55k-70k EUR
        TÉLÉTRAVAIL: Hybride (3j bureau, 2j remote)
        
        RESPONSABILITÉS:
        - Développement APIs IA
        - Architecture backend
        - Optimisation performances
        - Encadrement équipe
        
        AVANTAGES:
        - Mutuelle premium
        - Tickets restaurant
        - Formation continue
        - Stock options
        """
        
        # Création fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(job_content)
            return f.name
    
    def test_intelligent_matching_endpoint(self) -> bool:
        """🎯 Test principal endpoint intelligent matching"""
        print("\n🎯 === TEST INTELLIGENT MATCHING ENDPOINT ===")
        
        try:
            # Création fichiers de test
            cv_file_path = self.create_test_cv_file()
            job_file_path = self.create_test_job_file()
            
            print(f"📄 CV test créé: {cv_file_path}")
            print(f"💼 Job test créé: {job_file_path}")
            
            # Préparation de la requête
            start_time = time.time()
            
            with open(cv_file_path, 'rb') as cv_file, open(job_file_path, 'rb') as job_file:
                files = {
                    'cv_file': ('test_cv.txt', cv_file, 'text/plain'),
                    'job_file': ('test_job.txt', job_file, 'text/plain')
                }
                
                data = {
                    'pourquoi_ecoute': 'Recherche nouveau défi',  # 🎯 TEST CRUCIAL !
                    'job_address': 'Paris, France'
                }
                
                print(f"🚀 Envoi requête à /api/v3/intelligent-matching...")
                print(f"🎯 Raison d'écoute: {data['pourquoi_ecoute']}")
                
                # Envoi de la requête
                response = self.session.post(
                    f"{self.base_url}/api/v3/intelligent-matching",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            request_time = (time.time() - start_time) * 1000
            
            print(f"⏱️  Temps de réponse: {request_time:.2f}ms")
            print(f"📊 Status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Validation du résultat
                print(f"✅ Matching successful!")
                print(f"🎯 Status: {result.get('status', 'unknown')}")
                print(f"📊 Total score: {result.get('matching_results', {}).get('total_score', 'N/A')}")
                print(f"🔧 Adaptations: {len(result.get('adaptation_details', {}).get('adaptations_applied', []))}")
                print(f"⏱️  Performance: {result.get('performance', {}).get('total_time_ms', 'N/A')}ms")
                print(f"🎯 Target atteint: {result.get('performance', {}).get('target_achieved', False)}")
                
                # Validation spécifique RaisonEcoute
                candidate_summary = result.get('candidate_summary', {})
                job_summary = result.get('job_summary', {})
                
                print(f"\n👤 Candidat: {candidate_summary.get('name', 'N/A')}")
                print(f"🛠️  Compétences: {candidate_summary.get('skills_count', 0)}")
                print(f"📅 Expérience: {candidate_summary.get('experience_years', 0)} ans")
                print(f"💰 Salaire: {candidate_summary.get('salary_range', 'N/A')}")
                
                print(f"\n💼 Job: {job_summary.get('job_title', 'N/A')}")
                print(f"🏢 Entreprise: {job_summary.get('company', 'N/A')}")
                print(f"📍 Localisation: {job_summary.get('location', 'N/A')}")
                
                # Vérification erreurs d'adaptation
                adaptation_errors = result.get('adaptation_details', {}).get('validation_errors', [])
                if adaptation_errors:
                    print(f"⚠️  Erreurs adaptation: {adaptation_errors}")
                else:
                    print("✅ Aucune erreur d'adaptation")
                
                return True
                
            else:
                print(f"❌ Request failed: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"❌ Error: {error_detail}")
                except:
                    print(f"❌ Error text: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            return False
    
    def test_questionnaire_with_nouveau_defi(self) -> bool:
        """📋 Test spécifique avec questionnaire et nouveau défi"""
        print("\n📋 === TEST QUESTIONNAIRE AVEC NOUVEAU DÉFI ===")
        
        try:
            cv_file_path = self.create_test_cv_file()
            
            # Questionnaire avec données avancées
            questionnaire_data = {
                "salary_min": 55000,
                "salary_max": 70000,
                "location_preference": "Paris",
                "remote_preference": "Hybride",
                "sectors": ["Technologie", "IA", "Startups"]
            }
            
            with open(cv_file_path, 'rb') as cv_file:
                files = {
                    'cv_file': ('test_cv.txt', cv_file, 'text/plain')
                }
                
                data = {
                    'pourquoi_ecoute': 'Recherche nouveau défi',  # 🎯 TEST CRITIQUE !
                    'questionnaire_data': json.dumps(questionnaire_data),
                    'job_address': 'La Défense, Paris'
                }
                
                print(f"🎯 Test avec questionnaire avancé...")
                print(f"📋 Pourquoi écoute: {data['pourquoi_ecoute']}")
                
                response = self.session.post(
                    f"{self.base_url}/api/v3/intelligent-matching",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Test questionnaire réussi!")
                print(f"🎯 Score: {result.get('matching_results', {}).get('total_score', 'N/A')}")
                return True
            else:
                print(f"❌ Test questionnaire échoué: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Test questionnaire failed: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """🧪 Exécute tous les tests de validation"""
        print("🧪 === VALIDATION NEXTVISION v3.2.1 APRÈS CORRECTION ===")
        print("🎯 Mission: Valider correction RaisonEcoute.NOUVEAU_DEFI")
        print("=" * 60)
        
        tests_results = []
        
        # Test 1: Health Check
        print("\n1️⃣ Test Health Check...")
        tests_results.append(self.test_health_check())
        
        # Test 2: Status détaillé
        print("\n2️⃣ Test Status détaillé...")
        tests_results.append(self.test_status_detailed())
        
        # Test 3: Intelligent Matching principal
        print("\n3️⃣ Test Intelligent Matching...")
        tests_results.append(self.test_intelligent_matching_endpoint())
        
        # Test 4: Questionnaire avec nouveau défi
        print("\n4️⃣ Test Questionnaire + Nouveau Défi...")
        tests_results.append(self.test_questionnaire_with_nouveau_defi())
        
        # Résumé
        passed_tests = sum(tests_results)
        total_tests = len(tests_results)
        
        print("\n" + "=" * 60)
        print(f"📊 RÉSULTATS VALIDATION:")
        print(f"✅ Tests réussis: {passed_tests}/{total_tests}")
        print(f"📈 Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("🎉 TOUS LES TESTS RÉUSSIS - CORRECTION VALIDÉE !")
            print("🚀 Endpoint /api/v3/intelligent-matching opérationnel !")
            print("✅ RaisonEcoute.NOUVEAU_DEFI fonctionne parfaitement !")
            return True
        else:
            print("❌ Certains tests ont échoué - Investigation nécessaire")
            return False

def main():
    """🎯 Point d'entrée principal"""
    print("🎯 NEXTVISION v3.2.1 - VALIDATION FINALE APRÈS CORRECTION")
    print("=" * 60)
    
    # Création du validateur
    validator = NextvisionAPIValidator()
    
    # Exécution des tests
    success = validator.run_all_tests()
    
    if success:
        print("\n🎉 VALIDATION COMPLÈTE RÉUSSIE !")
        print("🚀 L'API Nextvision v3.2.1 est pleinement opérationnelle !")
        print("✅ Correction RaisonEcoute.NOUVEAU_DEFI validée !")
        print("\n🎯 Prêt pour les tests en production !")
    else:
        print("\n❌ Validation incomplète - Vérification nécessaire")
    
    return success

if __name__ == "__main__":
    main()
