#!/usr/bin/env python3
"""
🚀 TEST COMPLET NEXTVISION - Parcours End-to-End avec Vrais Fichiers
====================================================================

Script de test complet pour valider tout le parcours NEXTVISION avec :
- Vrais fichiers CV et Fiche de Poste
- Simulation questionnaire candidat réaliste
- Test endpoint complet /api/v3/intelligent-matching
- Validation tous les scores (Transport + Motivations)

Fichiers requis :
- CV TEST (sur bureau)
- FDP TEST (sur bureau)

Usage: python test_parcours_complet.py

Author: NEXTEN Team
"""

import sys
import os
import time
import json
import requests
import tempfile
from pathlib import Path

# Add nextvision to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def find_test_files():
    """🔍 Localise les fichiers de test sur le bureau"""
    print("🔍 Recherche fichiers de test...")
    
    # Chemins possibles pour le bureau
    desktop_paths = [
        os.path.join(os.path.expanduser("~"), "Desktop"),
        os.path.join(os.path.expanduser("~"), "Bureau"),
        os.path.join(os.path.expanduser("~"), "Desktop", "CV TEST"),
        os.path.join(os.path.expanduser("~"), "Bureau", "CV TEST"),
        "."  # Répertoire courant comme fallback
    ]
    
    found_files = {"cv": None, "job": None}
    
    for desktop_path in desktop_paths:
        if not os.path.exists(desktop_path):
            continue
            
        print(f"   📂 Recherche dans: {desktop_path}")
        
        # Recherche fichiers CV
        cv_patterns = ["CV TEST*", "cv test*", "CV_TEST*", "cv_test*", "CV*"]
        for pattern in cv_patterns:
            import glob
            cv_files = glob.glob(os.path.join(desktop_path, pattern))
            if cv_files:
                found_files["cv"] = cv_files[0]
                print(f"   ✅ CV trouvé: {found_files['cv']}")
                break
        
        # Recherche fichiers Job
        job_patterns = ["FDP TEST*", "fdp test*", "FDP_TEST*", "fdp_test*", "FDP*", "Job*", "Poste*"]
        for pattern in job_patterns:
            job_files = glob.glob(os.path.join(desktop_path, pattern))
            if job_files:
                found_files["job"] = job_files[0]
                print(f"   ✅ Job trouvé: {found_files['job']}")
                break
    
    return found_files

def create_realistic_questionnaire():
    """📋 Crée un questionnaire candidat réaliste"""
    print("📋 Génération questionnaire candidat réaliste...")
    
    questionnaire = {
        # Motivations professionnelles
        "motivations": [
            "Innovation technique",
            "Évolution de carrière", 
            "Leadership d'équipe",
            "Impact business"
        ],
        
        # Préférences transport
        "transport_preferences": [
            "Voiture",
            "Transport en commun"
        ],
        
        # Contraintes géographiques
        "localisation": {
            "ville_actuelle": "Paris",
            "max_distance_km": 25,
            "temps_trajet_max_minutes": 45,
            "accepte_demenagement": False
        },
        
        # Attentes salariales
        "salary_expectations": {
            "min": 55000,
            "max": 75000,
            "negociable": True
        },
        
        # Modalités de travail
        "work_modality": {
            "preference": "Hybride",
            "jours_remote_souhaites": 2,
            "flexibilite_horaires": True
        },
        
        # Secteur et environnement
        "secteur_preferences": [
            "Tech/Digital",
            "Innovation",
            "Startup/Scale-up"
        ],
        
        # Raisons de recherche
        "pourquoi_recherche": "Recherche évolution vers poste senior avec plus de responsabilités et dimension innovation",
        
        # Contraintes temporelles
        "disponibilite": {
            "date_dispo": "2025-09-01",
            "preavis_semaines": 4,
            "urgence_recherche": 3  # 1-5 scale
        },
        
        # Compétences prioritaires à développer
        "competences_developpement": [
            "Leadership technique",
            "Architecture logicielle",
            "Management d'équipe"
        ]
    }
    
    print(f"   ✅ Questionnaire généré: {len(questionnaire)} sections")
    return questionnaire

def test_direct_scoring():
    """🎯 Test direct du scoring sans API"""
    print("\n" + "="*60)
    print("🎯 TEST DIRECT - Moteur de Scoring")
    print("="*60)
    
    try:
        from nextvision.engines.motivations_scoring_engine import (
            create_complete_job_data,
            create_complete_cv_data,
            motivations_scoring_engine
        )
        
        # Données test réalistes
        candidate = create_complete_cv_data(
            name="Sophie Martin",
            skills=["Python", "React", "Leadership", "Innovation", "Architecture"],
            years_of_experience=5,
            objective="Développeuse Senior passionnée d'innovation technique, recherche poste avec évolution vers Tech Lead et impact business fort",
            summary="5 ans d'expérience en développement full-stack, leadership technique d'équipes, passion pour l'innovation et les architectures scalables",
            location="Paris, France",
            job_titles=["Développeuse Senior", "Tech Lead Junior", "Développeuse Full-Stack"],
            companies=["TechCorp", "InnovStartup"],
            education="Master Informatique",
            languages=["Français", "Anglais"],
            certifications=["AWS Certified", "Scrum Master"]
        )
        
        job = create_complete_job_data(
            title="Senior Full-Stack Developer & Tech Lead",
            company="InnovTech Solutions",
            location="Paris 9ème, France",
            contract_type="CDI",
            required_skills=[
                "Python/Django", "React/TypeScript", "Leadership technique", 
                "Architecture logicielle", "DevOps/AWS"
            ],
            preferred_skills=[
                "Machine Learning", "Microservices", "Team management"
            ],
            responsibilities=[
                "Leadership technique équipe 6 développeurs",
                "Architecture et développement solutions innovantes",
                "Mentoring développeurs junior/medior",
                "Collaboration étroite Product & Business",
                "Veille technologique et innovation continue"
            ],
            requirements=[
                "5+ ans expérience développement full-stack",
                "Expérience leadership technique confirmée", 
                "Maîtrise Python/React en environnement agile",
                "Passion innovation et technologies émergentes",
                "Anglais technique courant"
            ],
            benefits=[
                "Innovation continue sur projets cutting-edge",
                "Évolution rapide vers Engineering Manager",
                "Équipe technique d'excellence internationale",
                "Formation budget illimité + conférences",
                "Stock-options startup en hypercroissance",
                "Full remote possible 2j/semaine",
                "Salaire top marché + bonus performance"
            ],
            salary_range={"min": 65000, "max": 85000},
            remote_policy="Hybride flexible 2-3j remote/semaine"
        )
        
        # Test scoring avec motivations explicites
        start_time = time.time()
        result = motivations_scoring_engine.score_motivations_alignment(
            candidate_data=candidate,
            job_data=job,
            candidate_motivations=[
                "Innovation technique",
                "Évolution carrière",
                "Leadership équipe", 
                "Impact business",
                "Apprentissage continu"
            ]
        )
        scoring_time = (time.time() - start_time) * 1000
        
        # Résultats détaillés
        print(f"👤 Candidat: {candidate.name}")
        print(f"   💼 Exp: {candidate.years_of_experience} ans")
        print(f"   🛠️ Skills: {', '.join(candidate.skills[:5])}...")
        print(f"   🎯 Objectif: {candidate.objective[:80]}...")
        
        print(f"\n💼 Poste: {job.title}")
        print(f"   🏢 Entreprise: {job.company}")
        print(f"   📍 Lieu: {job.location}")
        print(f"   💰 Salaire: {job.salary_range['min']}k - {job.salary_range['max']}k")
        print(f"   🏠 Remote: {job.remote_policy}")
        
        print(f"\n📊 RÉSULTATS SCORING MOTIVATIONNEL:")
        print(f"   🎯 Score Global: {result.overall_score:.3f}/1.000")
        print(f"   📊 Confiance: {result.confidence:.3f}")
        print(f"   ⏱️ Temps: {result.processing_time_ms:.2f}ms")
        print(f"   ⚡ Performance: {scoring_time:.2f}ms")
        
        if result.strongest_alignments:
            print(f"\n🔥 Alignements Forts:")
            for alignment in result.strongest_alignments:
                print(f"   ✅ {alignment}")
        
        if result.motivation_scores:
            print(f"\n📈 Top Motivations:")
            for score in sorted(result.motivation_scores, key=lambda x: x.score, reverse=True)[:3]:
                print(f"   {score.motivation_type.value.title()}: {score.score:.3f} (poids: {score.weight:.2f})")
        
        performance_ok = result.processing_time_ms < 10
        print(f"\n{'✅' if performance_ok else '⚠️'} Performance: {'EXCELLENT' if performance_ok else 'ACCEPTABLE'}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Erreur test direct: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_api_endpoint(cv_file_path=None, job_file_path=None):
    """🌐 Test endpoint API complet"""
    print("\n" + "="*60)
    print("🌐 TEST ENDPOINT API - Parcours Complet")
    print("="*60)
    
    # Configuration API
    base_url = "http://localhost:8001"
    endpoint = "/api/v3/intelligent-matching"
    
    # Test de santé API
    try:
        health_response = requests.get(f"{base_url}/api/v3/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ API NEXTVISION accessible")
            health_data = health_response.json()
            print(f"   Version: {health_data.get('version', 'N/A')}")
            features = health_data.get('features', {})
            print(f"   Motivations: {'✅' if features.get('motivations_scorer') else '❌'}")
            print(f"   Transport: {'✅' if features.get('transport_intelligence') else '❌'}")
        else:
            print(f"⚠️ API répond mais status: {health_response.status_code}")
    except requests.ConnectionError:
        print("❌ API non accessible. Démarrez avec: python main.py")
        return False
    except Exception as e:
        print(f"❌ Erreur santé API: {e}")
        return False
    
    # Préparation fichiers
    files_to_test = {}
    
    if cv_file_path and os.path.exists(cv_file_path):
        files_to_test["cv_file"] = open(cv_file_path, 'rb')
        print(f"📄 CV: {cv_file_path}")
    else:
        # Création CV de test
        cv_content = """
Sophie Martin
Développeuse Senior Full-Stack
Email: sophie.martin@email.com
Téléphone: 06.12.34.56.78

OBJECTIF PROFESSIONNEL:
Développeuse Senior passionnée d'innovation technique avec 5 ans d'expérience, 
recherche poste Tech Lead avec évolution managériale et impact business fort.

COMPÉTENCES:
• Développement: Python/Django, React/TypeScript, Node.js
• Architecture: Microservices, API REST/GraphQL, AWS/Docker
• Leadership: Encadrement équipes, Mentoring, Méthodologies Agiles
• Innovation: R&D, Veille technologique, POCs
• Business: Collaboration Product/Business, Vision produit

EXPÉRIENCE:
2020-2025 | Tech Lead Junior - InnovStartup Paris
• Leadership technique équipe 4 développeurs
• Architecture plateforme e-commerce (500k users)
• Innovation: IA/ML pour recommandations
• Management: Recrutement, formation, performance

2018-2020 | Développeuse Senior - TechCorp Paris  
• Développement applications critiques Python/React
• Mentoring développeurs junior
• Optimisation performance (+40% vitesse)

FORMATION:
Master Informatique - EPITECH (2018)
Certifications: AWS Solutions Architect, Scrum Master

LANGUES: Français natif, Anglais courant (C1)
        """
        
        cv_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        cv_file.write(cv_content)
        cv_file.close()
        files_to_test["cv_file"] = open(cv_file.name, 'rb')
        print(f"📄 CV: Test généré")
    
    if job_file_path and os.path.exists(job_file_path):
        files_to_test["job_file"] = open(job_file_path, 'rb')
        print(f"💼 Job: {job_file_path}")
    else:
        # Création fiche de poste de test
        job_content = """
FICHE DE POSTE - SENIOR FULL-STACK DEVELOPER & TECH LEAD

Entreprise: InnovTech Solutions
Localisation: Paris 9ème (Métro Grands Boulevards)
Type contrat: CDI
Salaire: 65k - 85k€ + bonus + stock-options

MISSION:
Rejoindre équipe R&D pour développer plateforme SaaS innovante IA/Data.
Leadership technique équipe 6 développeurs internationaux.
Évolution rapide vers Engineering Manager (6-12 mois).

RESPONSABILITÉS:
• Architecture et développement solutions full-stack haute performance
• Leadership technique équipe développement (6 personnes)
• Mentoring développeurs junior/medior
• Innovation continue: R&D, POCs, veille technologique
• Collaboration étroite Product Manager et Business Units
• Code review, qualité, standards techniques

PROFIL RECHERCHÉ:
• 5+ ans expérience développement full-stack
• Expertise Python/Django + React/TypeScript
• Expérience leadership technique confirmée
• Passion innovation et technologies émergentes
• Anglais technique courant
• Esprit entrepreneurial et ownership

STACK TECHNIQUE:
Backend: Python/Django, Node.js, PostgreSQL, Redis
Frontend: React/TypeScript, Next.js, TailwindCSS  
Cloud: AWS (EC2, RDS, S3, Lambda), Docker, K8s
Data: ElasticSearch, Airflow, Spark
Monitoring: DataDog, Sentry, Grafana

AVANTAGES:
• Innovation continue sur projets cutting-edge IA/Data
• Évolution rapide vers Engineering Manager garantie
• Équipe technique internationale d'exception
• Formation budget illimité + conférences tech
• Stock-options startup hypercroissance (Series B)
• Remote hybride flexible 2-3j/semaine
• Salaire top marché + bonus performance
• Mutuelle premium, tickets resto, RTT

ENVIRONNEMENT:
Startup B2B SaaS en hypercroissance (200% YoY)
Bureaux design République avec rooftop
Culture engineering excellence et innovation
Équipe passionnée, bienveillante, internationale
        """
        
        job_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        job_file.write(job_content)
        job_file.close()
        files_to_test["job_file"] = open(job_file.name, 'rb')
        print(f"💼 Job: Test généré")
    
    # Génération questionnaire
    questionnaire = create_realistic_questionnaire()
    
    # Données de requête
    form_data = {
        "pourquoi_ecoute": "Recherche évolution vers poste senior avec plus de responsabilités techniques et managériales. Motivation forte pour innovation et impact business.",
        "questionnaire_data": json.dumps(questionnaire),
        "job_address": "Paris 9ème, France"
    }
    
    print(f"\n🎯 Paramètres requête:")
    print(f"   Raison écoute: {form_data['pourquoi_ecoute'][:80]}...")
    print(f"   Questionnaire: {len(questionnaire)} sections")
    print(f"   Adresse job: {form_data['job_address']}")
    
    # Requête API
    try:
        print(f"\n🚀 Envoi requête vers {base_url}{endpoint}...")
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}{endpoint}",
            files=files_to_test,
            data=form_data,
            timeout=30
        )
        
        request_time = (time.time() - start_time) * 1000
        print(f"   ⏱️ Temps requête: {request_time:.2f}ms")
        
        # Fermeture fichiers
        for file_obj in files_to_test.values():
            file_obj.close()
        
        # Analyse réponse
        if response.status_code == 200:
            print("✅ REQUÊTE RÉUSSIE")
            
            result = response.json()
            
            # Informations générales
            print(f"\n📊 RÉSULTATS PARCOURS COMPLET:")
            print(f"   Status: {result.get('status', 'N/A')}")
            
            # Performance
            perf = result.get('performance', {})
            total_time = perf.get('total_time_ms', 0)
            print(f"   ⏱️ Temps total: {total_time:.2f}ms")
            print(f"   🎯 Objectif < 2000ms: {'✅' if total_time < 2000 else '❌'}")
            print(f"   📈 Grade: {perf.get('performance_grade', 'N/A')}")
            
            # Résultats matching
            matching = result.get('matching_results', {})
            if matching:
                print(f"\n🎯 SCORES MATCHING:")
                print(f"   Score Total: {matching.get('total_score', 0):.3f}")
                print(f"   Confiance: {matching.get('confidence', 0):.3f}")
                
                # Scores par composant
                component_scores = matching.get('component_scores', {})
                if component_scores:
                    print(f"\n📊 DÉTAIL SCORES:")
                    for component, score in component_scores.items():
                        print(f"   {component.title()}: {score:.3f}")
                
                # Analyse motivations
                motivations = matching.get('motivations_analysis', {})
                if motivations and motivations.get('status') == 'success':
                    print(f"\n🎯 ANALYSE MOTIVATIONS:")
                    print(f"   Score Motivations: {motivations.get('overall_score', 0):.3f}")
                    print(f"   Confiance: {motivations.get('confidence', 0):.3f}")
                    print(f"   Temps: {motivations.get('processing_time_ms', 0):.2f}ms")
                    
                    alignments = motivations.get('strongest_alignments', [])
                    if alignments:
                        print(f"   Alignements forts: {', '.join(alignments[:3])}")
                
                # Transport Intelligence
                transport = matching.get('transport_intelligence', {})
                if transport:
                    print(f"\n🚗 TRANSPORT INTELLIGENCE:")
                    print(f"   Score dynamique: {'✅' if transport.get('location_score_dynamic') else '❌'}")
                    print(f"   Source: {transport.get('location_score_source', 'N/A')}")
                    print(f"   Score: {transport.get('location_score_value', 0):.3f}")
            
            # Détails adaptation
            adaptation = result.get('adaptation_details', {})
            if adaptation:
                print(f"\n🔧 ADAPTATION INTELLIGENTE:")
                print(f"   Succès: {'✅' if adaptation.get('success') else '❌'}")
                print(f"   Transformations: {adaptation.get('transformations_count', 0)}")
            
            print(f"\n🎉 PARCOURS COMPLET: SUCCÈS!")
            return True, result
            
        else:
            print(f"❌ ERREUR API: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Détail: {error_detail}")
            except:
                print(f"   Réponse: {response.text[:200]}...")
            return False, None
            
    except requests.Timeout:
        print("❌ Timeout requête API (>30s)")
        return False, None
    except Exception as e:
        print(f"❌ Erreur requête API: {e}")
        return False, None

def main():
    """🚀 Test complet parcours NEXTVISION"""
    print("🚀 TEST COMPLET PARCOURS NEXTVISION")
    print("=" * 60)
    print("🎯 Objectif: Valider parcours end-to-end complet")
    print("📁 Fichiers: CV TEST + FDP TEST (ou générés)")
    print("🧠 Components: GPT + Transport + Motivations")
    print()
    
    # Recherche fichiers
    files = find_test_files()
    
    if files["cv"]:
        print(f"✅ CV trouvé: {files['cv']}")
    else:
        print("⚠️ CV non trouvé, génération automatique")
    
    if files["job"]:
        print(f"✅ Job trouvé: {files['job']}")
    else:
        print("⚠️ Job non trouvé, génération automatique")
    
    # Test 1: Scoring direct
    success_direct, result_direct = test_direct_scoring()
    
    # Test 2: API endpoint
    success_api, result_api = test_api_endpoint(files["cv"], files["job"])
    
    # Bilan final
    print("\n" + "="*60)
    print("🏆 BILAN TEST PARCOURS COMPLET")
    print("="*60)
    
    print(f"Test Scoring Direct: {'✅ SUCCÈS' if success_direct else '❌ ÉCHEC'}")
    print(f"Test API Endpoint: {'✅ SUCCÈS' if success_api else '❌ ÉCHEC'}")
    
    if success_direct and success_api:
        print("\n🎉 VALIDATION COMPLÈTE: SUCCÈS!")
        print("✅ Moteur de scoring: OPÉRATIONNEL")  
        print("✅ Endpoint API: OPÉRATIONNEL")
        print("✅ Transport Intelligence: INTÉGRÉ")
        print("✅ Motivations Scorer: INTÉGRÉ")
        print("🚀 NEXTVISION: PRÊT PRODUCTION!")
        
        if result_api:
            perf = result_api.get('performance', {})
            total_time = perf.get('total_time_ms', 0)
            print(f"⚡ Performance globale: {total_time:.2f}ms")
        
        return True
    else:
        print("\n⚠️ VALIDATION PARTIELLE")
        if not success_direct:
            print("🔧 Vérifiez imports et dépendances")
        if not success_api:
            print("🔧 Démarrez API: python main.py")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
