#!/usr/bin/env python3
"""
Test Parsing GPT + Matching Sémantique - Nextvision V3.1
========================================================

Script interactif pour tester :
1. Parsing CV via GPT
2. Parsing fiche de poste via GPT  
3. Matching sémantique complet
4. Comparaison avec profils fallback

Auteur: Baptiste Comas
Date: 2025-07-10
Version: 1.0.0
"""

import sys
import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_gpt_parsing')

def setup_openai_client():
    """
    Configure le client OpenAI
    """
    print("🔑 Configuration du client OpenAI...")
    
    # Vérification de la clé API
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️ Clé OPENAI_API_KEY non trouvée dans les variables d'environnement")
        api_key = input("Entrez votre clé OpenAI (ou 'skip' pour utiliser les profils fallback): ")
        
        if api_key.lower() == 'skip':
            print("📋 Mode fallback activé (pas de parsing GPT en temps réel)")
            return None
    
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        # Test de la connexion
        print("🧪 Test de connexion OpenAI...")
        test_response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Test de connexion - réponds juste 'OK'"}],
            max_tokens=10
        )
        
        if test_response.choices[0].message.content.strip().upper() == 'OK':
            print("✅ Connexion OpenAI réussie !")
            return client
        else:
            print("⚠️ Réponse inattendue d'OpenAI")
            return None
            
    except ImportError:
        print("❌ Module 'openai' non installé. Installez avec: pip install openai")
        return None
    except Exception as e:
        print(f"❌ Erreur connexion OpenAI: {e}")
        return None

def load_gpt_modules():
    """
    Charge les modules GPT
    """
    try:
        # Ajout du chemin si nécessaire
        current_dir = Path(__file__).parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
        
        from gpt_modules import CVParserGPT, JobParserGPT, GPTNextvisionIntegrator
        print("✅ Modules GPT chargés avec succès")
        return CVParserGPT, JobParserGPT, GPTNextvisionIntegrator
        
    except ImportError as e:
        print(f"❌ Erreur chargement modules GPT: {e}")
        return None, None, None

def test_cv_parsing(cv_parser, cv_text: str):
    """
    Test le parsing d'un CV via GPT
    """
    print("\n📋 TEST PARSING CV VIA GPT")
    print("=" * 50)
    
    start_time = time.time()
    
    # Parsing via GPT
    print("🤖 Parsing en cours via GPT-4...")
    cv_data = cv_parser.parse_cv_text(cv_text)
    
    parsing_time = (time.time() - start_time) * 1000
    
    # Affichage des résultats
    print(f"⚡ Temps de parsing: {parsing_time:.1f}ms")
    print(f"👤 Nom: {cv_data.nom_complet}")
    print(f"💼 Titre: {cv_data.titre_poste}")
    print(f"🏆 Niveau: {cv_data.niveau_hierarchique}")
    print(f"📅 Expérience: {cv_data.experience_years} ans")
    print(f"💰 Salaire: {cv_data.salaire_actuel}€ (souhaité: {cv_data.salaire_souhaite}€)")
    print(f"🏢 Secteur: {cv_data.secteur_activite}")
    
    print(f"\n🛠️ Compétences ({len(cv_data.competences)}):")
    for i, comp in enumerate(cv_data.competences[:5], 1):
        print(f"   {i}. {comp}")
    if len(cv_data.competences) > 5:
        print(f"   ... et {len(cv_data.competences) - 5} autres")
    
    print(f"\n💻 Logiciels ({len(cv_data.logiciels)}):")
    for i, log in enumerate(cv_data.logiciels[:5], 1):
        print(f"   {i}. {log}")
    
    return cv_data

def test_job_parsing(job_parser, job_text: str):
    """
    Test le parsing d'une fiche de poste via GPT
    """
    print("\n💼 TEST PARSING FICHE DE POSTE VIA GPT")
    print("=" * 50)
    
    start_time = time.time()
    
    # Parsing via GPT
    print("🤖 Parsing en cours via GPT-4...")
    job_data = job_parser.parse_job_text(job_text)
    
    parsing_time = (time.time() - start_time) * 1000
    
    # Affichage des résultats
    print(f"⚡ Temps de parsing: {parsing_time:.1f}ms")
    print(f"💼 Titre: {job_data.titre_poste}")
    print(f"🏢 Entreprise: {job_data.entreprise}")
    print(f"🏆 Niveau: {job_data.niveau_hierarchique}")
    print(f"📅 Expérience: {job_data.experience_requise_min}-{job_data.experience_requise_max} ans")
    print(f"💰 Salaire: {job_data.salaire_min}-{job_data.salaire_max}€")
    print(f"🏢 Secteur: {job_data.secteur_activite}")
    print(f"📍 Localisation: {job_data.localisation}")
    
    print(f"\n✅ Compétences requises ({len(job_data.competences_requises)}):")
    for i, comp in enumerate(job_data.competences_requises[:5], 1):
        print(f"   {i}. {comp}")
    
    print(f"\n⭐ Compétences souhaitées ({len(job_data.competences_souhaitees)}):")
    for i, comp in enumerate(job_data.competences_souhaitees[:3], 1):
        print(f"   {i}. {comp}")
    
    return job_data

def test_semantic_matching(integrator, cv_data, job_data):
    """
    Test le matching sémantique complet
    """
    print("\n🧠 TEST MATCHING SÉMANTIQUE COMPLET")
    print("=" * 50)
    
    start_time = time.time()
    
    # Conversion au format Nextvision
    cv_nextvision = integrator.cv_parser.to_nextvision_format(cv_data)
    job_nextvision = integrator.job_parser.to_nextvision_format(job_data)
    
    # Matching complet
    print("🔄 Calcul du matching sémantique...")
    result = integrator.perform_complete_matching(cv_nextvision, job_nextvision)
    
    matching_time = (time.time() - start_time) * 1000
    
    # Affichage des résultats
    print(f"⚡ Temps de matching: {matching_time:.1f}ms")
    print(f"🎯 Score total: {result.total_score:.3f}")
    print(f"🏆 Recommandation: {result.recommendation}")
    print(f"🔍 Compatibilité hiérarchique: {result.hierarchical_compatibility}")
    
    print(f"\n📊 Détail des scores:")
    for component, score in result.scores_breakdown.items():
        weight = integrator.weights_v31.get(component, 0)
        contribution = score * weight
        print(f"   - {component.capitalize()}: {score:.3f} (×{weight:.2f} = {contribution:.3f})")
    
    if result.alerts:
        print(f"\n⚠️ Alertes ({len(result.alerts)}):")
        for alert in result.alerts:
            print(f"   - {alert}")
    else:
        print("\n✅ Aucune alerte")
    
    return result

def get_sample_cv():
    """
    Retourne un CV d'exemple pour les tests
    """
    return """
CV - Marie Dubois
Développeuse Full-Stack Senior

Contact:
Email: marie.dubois@email.com
Téléphone: +33 6 12 34 56 78
Adresse: Lyon, France

Expérience Professionnelle:
• Développeuse Full-Stack Senior - TechCorp SA (2020-Présent)
  - Développement d'applications React/Node.js
  - Architecture microservices et APIs REST
  - Management d'une équipe de 3 développeurs junior
  - Technologies: React, Node.js, PostgreSQL, AWS

• Développeuse Web - WebAgency (2018-2020)
  - Développement frontend et backend
  - Intégration APIs tierces
  - Optimisation performances

Formation:
• Master Informatique - INSA Lyon (2018)
• DUT Informatique - IUT Lyon (2016)

Compétences Techniques:
- Langages: JavaScript, TypeScript, Python, SQL
- Frameworks: React, Vue.js, Node.js, Express
- Bases de données: PostgreSQL, MongoDB, Redis
- Cloud: AWS, Docker, Kubernetes
- Outils: Git, Jenkins, Jira

Langues:
- Français: Natif
- Anglais: Courant (TOEIC 880)

Disponibilité: Immédiate
Salaire souhaité: 55 000€
"""

def get_sample_job():
    """
    Retourne une fiche de poste d'exemple pour les tests
    """
    return """
OFFRE D'EMPLOI - Développeur Full-Stack

Entreprise: InnovTech Solutions
Secteur: Technologies de l'information
Localisation: Lyon, France
Type de contrat: CDI

Description du poste:
Nous recherchons un Développeur Full-Stack expérimenté pour rejoindre notre équipe technique dynamique. Vous participerez au développement de nos solutions SaaS innovantes.

Missions principales:
• Développement d'applications web modernes (React/Node.js)
• Conception et implémentation d'APIs REST
• Participation aux choix d'architecture technique
• Code review et mentorat des développeurs junior
• Optimisation des performances et de la sécurité

Profil recherché:
• 4-7 ans d'expérience en développement web
• Maîtrise de JavaScript/TypeScript
• Expérience React et Node.js indispensable
• Connaissance des bases de données relationnelles
• Expérience avec les outils DevOps (Docker, CI/CD)
• Bon niveau d'anglais technique

Compétences appréciées:
• AWS ou autres cloud providers
• Kubernetes
• MongoDB
• Tests unitaires et TDD

Rémunération:
• Salaire: 45 000 - 60 000€ selon expérience
• Tickets restaurant, mutuelle
• Télétravail partiel (2j/semaine)
• Formation continue

Candidature:
Envoyez CV + lettre de motivation à recrutement@innovtech.fr
"""

def main():
    """
    Fonction principale du test
    """
    print("🧠 NEXTVISION V3.1 - TEST PARSING GPT + MATCHING SÉMANTIQUE")
    print("=" * 70)
    
    # Configuration OpenAI
    openai_client = setup_openai_client()
    
    # Chargement des modules GPT
    CVParserGPT, JobParserGPT, GPTNextvisionIntegrator = load_gpt_modules()
    
    if not all([CVParserGPT, JobParserGPT, GPTNextvisionIntegrator]):
        print("❌ Impossible de charger les modules GPT")
        return
    
    # Initialisation des parsers
    print("\n🔧 Initialisation des parsers...")
    cv_parser = CVParserGPT(openai_client=openai_client)
    job_parser = JobParserGPT(openai_client=openai_client)
    integrator = GPTNextvisionIntegrator(cv_parser=cv_parser, job_parser=job_parser)
    
    print(f"✅ Parsers initialisés (mode: {'GPT en temps réel' if openai_client else 'Fallback'})")
    
    # Choix du mode de test
    print("\n📋 MODES DE TEST DISPONIBLES:")
    print("1. Test avec CV/Job d'exemple")
    print("2. Test avec vos propres textes")
    print("3. Test comparatif (GPT vs Fallback)")
    
    choice = input("\nChoisissez un mode (1-3): ").strip()
    
    if choice == "1":
        # Test avec exemples
        print("\n🧪 TEST AVEC EXEMPLES PRÉDÉFINIS")
        cv_text = get_sample_cv()
        job_text = get_sample_job()
        
    elif choice == "2":
        # Test avec textes personnalisés
        print("\n📝 SAISIE DE VOS TEXTES")
        print("\n📋 Collez votre CV (terminez par une ligne vide):")
        cv_lines = []
        while True:
            line = input()
            if not line.strip():
                break
            cv_lines.append(line)
        cv_text = '\n'.join(cv_lines)
        
        print("\n💼 Collez votre fiche de poste (terminez par une ligne vide):")
        job_lines = []
        while True:
            line = input()
            if not line.strip():
                break
            job_lines.append(line)
        job_text = '\n'.join(job_lines)
        
    elif choice == "3":
        # Test comparatif
        print("\n⚖️ TEST COMPARATIF GPT vs FALLBACK")
        if not openai_client:
            print("❌ Client OpenAI requis pour le test comparatif")
            return
        
        cv_text = get_sample_cv()
        job_text = get_sample_job()
        
        # Test avec GPT
        print("\n🤖 === PARSING AVEC GPT ===")
        cv_data_gpt = test_cv_parsing(cv_parser, cv_text)
        job_data_gpt = test_job_parsing(job_parser, job_text)
        result_gpt = test_semantic_matching(integrator, cv_data_gpt, job_data_gpt)
        
        # Test avec fallback
        print("\n📋 === PARSING AVEC FALLBACK ===")
        cv_parser_fallback = CVParserGPT(openai_client=None)
        job_parser_fallback = JobParserGPT(openai_client=None)
        integrator_fallback = GPTNextvisionIntegrator(cv_parser=cv_parser_fallback, job_parser=job_parser_fallback)
        
        cv_data_fallback = cv_parser_fallback._get_fallback_profile()
        job_data_fallback = job_parser_fallback._get_fallback_job()
        result_fallback = test_semantic_matching(integrator_fallback, cv_data_fallback, job_data_fallback)
        
        # Comparaison
        print("\n📊 COMPARAISON GPT vs FALLBACK")
        print("=" * 50)
        print(f"Score GPT: {result_gpt.total_score:.3f}")
        print(f"Score Fallback: {result_fallback.total_score:.3f}")
        print(f"Différence: {abs(result_gpt.total_score - result_fallback.total_score):.3f}")
        
        return
    
    else:
        print("❌ Choix invalide")
        return
    
    # Vérification des textes
    if not cv_text.strip() or not job_text.strip():
        print("❌ CV ou fiche de poste vide")
        return
    
    # Tests de parsing
    cv_data = test_cv_parsing(cv_parser, cv_text)
    job_data = test_job_parsing(job_parser, job_text)
    
    # Test de matching sémantique
    result = test_semantic_matching(integrator, cv_data, job_data)
    
    # Résumé final
    print("\n🎯 RÉSUMÉ DU TEST")
    print("=" * 50)
    print(f"Candidat: {cv_data.nom_complet} ({cv_data.niveau_hierarchique})")
    print(f"Poste: {job_data.titre_poste} ({job_data.niveau_hierarchique})")
    print(f"Score final: {result.total_score:.3f}")
    print(f"Recommandation: {result.recommendation}")
    
    if result.total_score >= 0.8:
        print("🎯 EXCELLENT MATCH - Candidature fortement recommandée !")
    elif result.total_score >= 0.6:
        print("✅ BON MATCH - Candidature intéressante")
    elif result.total_score >= 0.4:
        print("⚠️ MATCH POSSIBLE - À étudier plus en détail")
    else:
        print("❌ PAS DE MATCH - Candidature non recommandée")
    
    # Sauvegarde optionnelle
    save = input("\nSauvegarder les résultats ? (o/N): ").strip().lower()
    if save == 'o':
        timestamp = int(time.time())
        filename = f"test_gpt_parsing_{timestamp}.json"
        
        rapport = {
            "timestamp": timestamp,
            "cv_parsed": {
                "nom": cv_data.nom_complet,
                "niveau": cv_data.niveau_hierarchique,
                "experience": cv_data.experience_years,
                "competences": cv_data.competences
            },
            "job_parsed": {
                "titre": job_data.titre_poste,
                "niveau": job_data.niveau_hierarchique,
                "competences_requises": job_data.competences_requises
            },
            "matching_result": {
                "score_total": result.total_score,
                "scores_detail": result.scores_breakdown,
                "recommendation": result.recommendation
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(rapport, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Résultats sauvegardés: {filename}")

if __name__ == "__main__":
    main()
