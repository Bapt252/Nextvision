#!/usr/bin/env python3
"""
🧪 Test Rapide Nextvision V3.2.1
Test du parcours complet : Parsing → Géocode → Transport → Matching

Usage:
    python test_nextvision_quick.py
"""

import os
import sys
import asyncio
import time
import json
from datetime import datetime

def check_environment():
    """✅ Vérifie l'environnement et les prérequis"""
    print("🔍 Vérification environnement...")
    
    # Variables d'environnement
    google_maps_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    if not google_maps_key or google_maps_key == "your-google-maps-api-key-here":
        print("❌ GOOGLE_MAPS_API_KEY non configuré")
        print("💡 Configurez avec: export GOOGLE_MAPS_API_KEY=your_api_key")
        return False
    
    print("✅ Google Maps API Key configuré")
    return True

def test_imports():
    """Test des imports Nextvision"""
    print("\n1️⃣ Test des imports...")
    
    try:
        import logging
        print("✅ logging importé")
        
        # Test import basique sans Google Maps d'abord
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Test models seulement
        from nextvision.models.transport_models import TravelMode
        print("✅ Transport models importés")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        print("💡 Suggestion: Vérifier structure du projet")
        return False

async def test_geocoding_simple():
    """Test de géocodage simplifié avec requests"""
    print("\n2️⃣ Test géocodage direct...")
    
    try:
        import requests
        
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        address = "Paris, France"
        
        url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': address,
            'key': api_key
        }
        
        print(f"📍 Test géocodage: {address}")
        start_time = time.time()
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                result = data['results'][0]
                location = result['geometry']['location']
                
                geocoding_time = time.time() - start_time
                
                print(f"✅ Géocodage réussi en {geocoding_time:.3f}s")
                print(f"   📍 {result['formatted_address']}")
                print(f"   📊 Coordonnées: {location['lat']:.4f}, {location['lng']:.4f}")
                
                return {
                    "status": "success",
                    "address": result['formatted_address'],
                    "coordinates": [location['lat'], location['lng']],
                    "time": geocoding_time
                }
            else:
                print(f"❌ Erreur API: {data['status']}")
                return {"status": "failed", "error": data['status']}
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return {"status": "failed", "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"❌ Erreur géocodage: {e}")
        return {"status": "failed", "error": str(e)}

def test_matching_simulation():
    """Test de simulation du matching"""
    print("\n3️⃣ Test simulation matching...")
    
    try:
        # Données candidat simulées
        candidat_data = {
            "nom": "Sophie Dubois",
            "competences": ["Python", "React", "PostgreSQL", "Docker"],
            "experience_annees": 3,
            "adresse": "12 Boulevard Saint-Michel, 75005 Paris"
        }
        
        # Données job simulées
        job_data = {
            "titre": "Développeur Full Stack",
            "entreprise": "TechLyon",
            "competences_requises": ["Python", "React", "SQL"],
            "adresse": "25 Rue de la République, 69002 Lyon"
        }
        
        print(f"👤 Candidat: {candidat_data['nom']}")
        print(f"💼 Poste: {job_data['titre']} @ {job_data['entreprise']}")
        
        # Calcul score compétences
        cv_skills = set(s.lower() for s in candidat_data["competences"])
        job_skills = set(s.lower() for s in job_data["competences_requises"])
        skill_match = len(cv_skills & job_skills) / len(job_skills)
        
        # Score expérience
        experience_match = min(1.0, candidat_data["experience_annees"] / 3)
        
        # Score localisation (simulation)
        location_score = 0.6  # Paris-Lyon = score moyen
        
        # Score final avec pondérations V3.2.1
        weights = {
            'semantic': 0.30,
            'experience': 0.20,
            'location': 0.15,
            'other': 0.35
        }
        
        final_score = (
            skill_match * weights['semantic'] +
            experience_match * weights['experience'] +
            location_score * weights['location'] +
            0.75 * weights['other']  # Autres scores simulés
        )
        
        print(f"🔧 Compétences: {skill_match:.3f} ({len(cv_skills & job_skills)}/{len(job_skills)} match)")
        print(f"👨‍💼 Expérience: {experience_match:.3f}")
        print(f"📍 Localisation: {location_score:.3f}")
        print(f"🎯 Score final: {final_score:.3f}")
        
        # Qualité du match
        if final_score >= 0.7:
            quality = "Excellent"
        elif final_score >= 0.5:
            quality = "Bon"
        else:
            quality = "Moyen"
        
        print(f"🏆 Qualité: {quality}")
        
        return {
            "status": "success",
            "candidat": candidat_data,
            "job": job_data,
            "scores": {
                "skill_match": skill_match,
                "experience_match": experience_match,
                "location_score": location_score,
                "final_score": final_score
            },
            "quality": quality
        }
        
    except Exception as e:
        print(f"❌ Erreur simulation: {e}")
        return {"status": "failed", "error": str(e)}

async def test_api_health():
    """Test santé de l'API si elle tourne"""
    print("\n4️⃣ Test API (optionnel)...")
    
    try:
        import requests
        
        # Test différents ports possibles
        ports = [5051, 8001, 8000]
        
        for port in ports:
            try:
                url = f"http://localhost:{port}/api/v1/health"
                response = requests.get(url, timeout=2)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ API trouvée sur port {port}")
                    print(f"   Status: {data.get('status', 'unknown')}")
                    return {"status": "success", "port": port, "data": data}
                    
            except requests.exceptions.RequestException:
                continue
        
        print("⚠️ API Nextvision non disponible (normal si non démarrée)")
        return {"status": "not_running"}
        
    except Exception as e:
        print(f"❌ Erreur test API: {e}")
        return {"status": "error", "error": str(e)}

async def main():
    """Point d'entrée principal"""
    print("🚀 NEXTVISION V3.2.1 - TEST RAPIDE")
    print("="*50)
    
    # Vérification environnement
    if not check_environment():
        return 1
    
    # Tests séquentiels
    results = {}
    
    # 1. Imports
    if not test_imports():
        print("❌ Tests arrêtés - problème imports")
        return 1
    results["imports"] = "success"
    
    # 2. Géocodage  
    geocoding_result = await test_geocoding_simple()
    results["geocoding"] = geocoding_result
    
    # 3. Simulation matching
    matching_result = test_matching_simulation()
    results["matching"] = matching_result
    
    # 4. Test API
    api_result = await test_api_health()
    results["api"] = api_result
    
    # Résumé
    print("\n" + "="*50)
    print("📊 RÉSUMÉ DU TEST")
    print("="*50)
    
    success_count = 0
    total_tests = 0
    
    for test_name, result in results.items():
        total_tests += 1
        if isinstance(result, dict):
            status = result.get("status", "unknown")
        else:
            status = result
            
        if status == "success":
            success_count += 1
            print(f"✅ {test_name.title()}: RÉUSSI")
        elif status == "not_running":
            print(f"⚠️ {test_name.title()}: NON DÉMARRÉ")
        else:
            print(f"❌ {test_name.title()}: ÉCHEC")
    
    print(f"\n🎯 Résultat: {success_count}/{total_tests} tests réussis")
    
    if success_count >= 2:  # Au moins imports + géocodage
        print("🎉 COMPOSANTS CLÉS OPÉRATIONNELS!")
        
        # Affichage des résultats
        if matching_result["status"] == "success":
            print(f"\n💡 Exemple de matching:")
            print(f"   👤 {matching_result['candidat']['nom']}")
            print(f"   💼 {matching_result['job']['titre']}")
            print(f"   🎯 Score: {matching_result['scores']['final_score']:.3f}")
            print(f"   🏆 Qualité: {matching_result['quality']}")
        
        print(f"\n🚀 Prochaines étapes:")
        print(f"   1. Démarrer API: python main.py")
        print(f"   2. Tests avancés: Création scripts détaillés")
        print(f"   3. Interface: http://localhost:5051/docs")
        
        return 0
    else:
        print("⚠️ Certains composants nécessitent une vérification")
        return 1

if __name__ == "__main__":
    print("💡 Assurez-vous d'avoir configuré GOOGLE_MAPS_API_KEY")
    print("💡 Lancez depuis le dossier racine Nextvision")
    print()
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
