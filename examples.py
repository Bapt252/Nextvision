#!/usr/bin/env python3
"""
🎯 Exemples d'utilisation du système NEXTEN complet
Démonstration des workflows révolutionnaires avec pondération adaptative

Author: NEXTEN Team  
Version: 1.0.0

Usage:
    python examples.py                    # Tous les exemples
    python examples.py --health           # Health check seulement
    python examples.py --workflow         # Workflow complet
    python examples.py --weights          # Comparaison pondérations
"""

import requests
import json
import argparse
from pathlib import Path
import sys
import time

# Configuration
NEXTVISION_BASE_URL = "http://localhost:8000"
INTEGRATION_BASE = f"{NEXTVISION_BASE_URL}/api/v1/integration"

class NEXTENClient:
    """🎯 Client pour interagir avec l'écosystème NEXTEN"""
    
    def __init__(self, base_url: str = NEXTVISION_BASE_URL):
        self.base_url = base_url
        self.integration_url = f"{base_url}/api/v1/integration"
        
    def health_check(self):
        """❤️ Vérification de santé de l'écosystème"""
        try:
            response = requests.get(f"{self.integration_url}/health", timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e), "status": "unhealthy"}
    
    def get_ecosystem_status(self):
        """📊 Status complet de l'écosystème NEXTEN"""
        try:
            response = requests.get(f"{self.integration_url}/status", timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def parse_job_text(self, job_text: str):
        """📋 Parse uniquement une offre d'emploi"""
        try:
            response = requests.post(
                f"{self.integration_url}/parse-job-from-commitment",
                data={"job_text": job_text},
                timeout=30
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def preview_adaptive_weights(self, pourquoi_ecoute: str):
        """🔍 Prévisualisation des poids adaptatifs"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/weights/preview",
                params={"pourquoi_ecoute": pourquoi_ecoute},
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def print_header(title: str):
    """🎨 Affiche un en-tête stylé"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

def print_success(message: str):
    """✅ Affiche un message de succès"""
    print(f"✅ {message}")

def print_error(message: str):
    """❌ Affiche un message d'erreur"""
    print(f"❌ {message}")

def print_info(message: str):
    """📋 Affiche une information"""
    print(f"📋 {message}")

def exemple_health_monitoring():
    """🎯 Exemple: Monitoring de l'écosystème"""
    print_header("MONITORING ÉCOSYSTÈME NEXTEN")
    
    client = NEXTENClient()
    
    # Health check
    print_info("Vérification de santé...")
    health = client.health_check()
    
    if health.get("status") == "healthy":
        print_success(f"Écosystème NEXTEN opérationnel !")
        
        if 'commitment_services' in health:
            services = health['commitment_services']
            print(f"   📋 Job Parser: {'✅ Disponible' if services['job_parser']['available'] else '❌ Indisponible'}")
            print(f"   📄 CV Parser: {'✅ Disponible' if services['cv_parser']['available'] else '❌ Indisponible'}")
        
        if 'integration_capabilities' in health:
            capabilities = health['integration_capabilities']
            print(f"   🌉 Workflow complet: {'✅ Possible' if capabilities['complete_workflow'] else '❌ Impossible'}")
    else:
        print_error(f"Problème détecté: {health.get('error', 'Status unhealthy')}")
        return False
    
    # Status détaillé
    print_info("Récupération du status détaillé...")
    status = client.get_ecosystem_status()
    
    if 'nexten_ecosystem' in status:
        ecosystem = status['nexten_ecosystem']
        print_success(f"{ecosystem['name']} - {ecosystem['version']}")
        print(f"💡 Innovation: {ecosystem['innovation']}")
        
        if 'competitive_advantages' in status:
            print("\n🚀 Avantages compétitifs:")
            for advantage in status['competitive_advantages']:
                print(f"   • {advantage}")
    
    return True

def exemple_comparaison_ponderation():
    """🎯 Exemple: Comparaison des pondérations adaptatives"""
    print_header("COMPARAISON PONDÉRATIONS ADAPTATIVES")
    
    client = NEXTENClient()
    
    raisons_test = [
        "Rémunération trop faible",
        "Poste ne coïncide pas avec poste proposé", 
        "Poste trop loin de mon domicile",
        "Manque de flexibilité",
        "Manque de perspectives d'évolution"
    ]
    
    print("📊 Innovation révolutionnaire: Pondération Adaptative Contextuelle\n")
    
    for i, raison in enumerate(raisons_test, 1):
        print(f"{i}. 📋 Raison: {raison}")
        
        result = client.preview_adaptive_weights(raison)
        
        if 'reasoning' in result:
            print(f"   💡 Stratégie: {result['reasoning']}")
            
            if result['adaptation_applied'] and result['weight_changes']:
                print("   📈 Adaptations principales:")
                for component, change in result['weight_changes'].items():
                    if abs(change['change_percent']) >= 10:  # Changements significatifs
                        direction = "↗️" if change['change_percent'] > 0 else "↘️"
                        print(f"     {direction} {component}: {change['change_percent']:+.1f}%")
            else:
                print("   📊 Pondération standard appliquée")
        else:
            print(f"   ❌ Erreur: {result.get('error')}")
        
        print()

def exemple_parsing_job():
    """🎯 Exemple: Parsing d'offre d'emploi avec Commitment-"""
    print_header("PARSING OFFRE D'EMPLOI VIA COMMITMENT-")
    
    client = NEXTENClient()
    
    # Offre d'emploi d'exemple
    job_text = """
    Senior Data Scientist - FinanceAI Corp
    
    FinanceAI Corp, leader européen en intelligence artificielle pour la finance, 
    recherche un(e) Senior Data Scientist pour rejoindre notre équipe R&D.
    
    📍 Localisation: Lyon, France (Télétravail hybride)
    💼 Type: CDI
    💰 Package: 65k€ - 80k€ + variable
    
    🎯 Missions:
    • Développement d'algorithmes de trading algorithmique
    • Analyse prédictive des marchés financiers
    • Optimisation des modèles ML en production
    • Collaboration avec les équipes quantitatives
    
    🛠️ Stack technique:
    • Python (pandas, scikit-learn, TensorFlow)
    • SQL avancé, PostgreSQL
    • Apache Spark, Kafka
    • AWS (SageMaker, EC2, S3)
    • MLFlow, Kubernetes
    
    ✅ Profil recherché:
    • 5+ ans d'expérience en Data Science
    • PhD ou Master en mathématiques/informatique/physique
    • Expérience finance/trading un plus
    • Anglais courant
    
    🎁 Avantages:
    • Stock-options
    • 2 jours télétravail/semaine
    • Budget formation 5k€/an
    • Salle de sport, conciergerie
    """
    
    print_info("Envoi de l'offre d'emploi au Job Parser GPT de Commitment-...")
    start_time = time.time()
    
    result = client.parse_job_text(job_text)
    
    processing_time = round((time.time() - start_time) * 1000)
    
    if result.get('status') == 'success':
        job_data = result['job_data']
        metadata = result['parsing_metadata']
        
        print_success(f"Parsing réussi en {processing_time}ms")
        print(f"🤖 Source: {metadata['source']} (GPT: {metadata['gpt_powered']})")
        
        print(f"\n📋 Offre parsée:")
        print(f"   📌 Titre: {job_data['title']}")
        print(f"   🏢 Entreprise: {job_data['company']}")
        print(f"   📍 Lieu: {job_data['location']}")
        print(f"   💼 Contrat: {job_data['contract_type']}")
        print(f"   💰 Salaire: {job_data['salary_range']}")
        
        print(f"\n🛠️ Compétences requises ({len(job_data['required_skills'])}):")
        for skill in job_data['required_skills'][:8]:  # Top 8
            print(f"   • {skill}")
        
        if len(job_data['benefits']) > 0:
            print(f"\n🎁 Avantages:")
            for benefit in job_data['benefits'][:5]:  # Top 5
                print(f"   • {benefit}")
    else:
        print_error(f"Erreur parsing: {result.get('error')}")

def exemple_workflow_demo():
    """🎯 Exemple: Démonstration workflow (sans fichiers)"""
    print_header("DÉMONSTRATION WORKFLOW NEXTEN")
    
    print("🎯 Le workflow NEXTEN révolutionnaire comprend:")
    print("   1. 📋 Parse Job avec Commitment- Job Parser GPT")
    print("   2. 📄 Parse CV avec Commitment- CV Parser GPT")  
    print("   3. 🎯 Matching avec pondération adaptative Nextvision")
    print("   4. 📊 Résultats unifiés avec explications")
    
    print("\n💡 Pour tester le workflow complet avec vos fichiers:")
    print("   curl -X POST 'http://localhost:8000/api/v1/integration/complete-workflow' \\")
    print("     -H 'Content-Type: multipart/form-data' \\")
    print("     -F 'pourquoi_ecoute=Rémunération trop faible' \\")
    print("     -F 'job_text=Développeur Full Stack - 45k€' \\")
    print("     -F 'cv_file=@votre_cv.pdf'")
    
    print("\n🌉 Innovation Bridge:")
    print("   ✅ Zéro redondance de code")
    print("   ✅ Réutilise 100% de l'existant Commitment-")
    print("   ✅ Pondération adaptative unique au monde")
    print("   ✅ Architecture évolutive et performante")

def main():
    """🎯 Fonction principale"""
    parser = argparse.ArgumentParser(description='🎯 Exemples NEXTEN')
    parser.add_argument('--health', action='store_true', help='Health check seulement')
    parser.add_argument('--workflow', action='store_true', help='Demo workflow')
    parser.add_argument('--weights', action='store_true', help='Comparaison pondérations')
    parser.add_argument('--parsing', action='store_true', help='Exemple parsing job')
    
    args = parser.parse_args()
    
    print("🎯 === DÉMONSTRATION NEXTEN - ÉCOSYSTÈME RÉVOLUTIONNAIRE ===")
    print("🚀 Premier système au monde avec pondération adaptative contextuelle")
    
    try:
        if args.health or (not any([args.workflow, args.weights, args.parsing])):
            if not exemple_health_monitoring():
                print("\n💡 Assurez-vous que Nextvision est démarré (python main.py)")
                sys.exit(1)
        
        if args.weights or (not any([args.health, args.workflow, args.parsing])):
            exemple_comparaison_ponderation()
        
        if args.parsing or (not any([args.health, args.workflow, args.weights])):
            exemple_parsing_job()
        
        if args.workflow or (not any([args.health, args.weights, args.parsing])):
            exemple_workflow_demo()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Interruption utilisateur")
    except Exception as e:
        print_error(f"Erreur lors de la démonstration: {e}")
        print("\n💡 Assurez-vous que:")
        print("   • Nextvision est démarré (python main.py)")
        print("   • Les services Commitment- sont disponibles")
        print("   • La configuration réseau est correcte")
        sys.exit(1)
    
    print("\n🎉 === FIN DE LA DÉMONSTRATION ===")
    print("🌉 NEXTEN Bridge - Intégration zéro redondance réussie !")
    print("📚 Documentation complète: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
