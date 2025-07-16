#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 NEXTVISION - Test OpenAI v1.x Integration
Script de test pour vérifier la compatibilité OpenAI v1.x
"""

import os
import sys
import json
import time
from pathlib import Path

# Ajout du chemin du projet
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_openai_import():
    """Test l'import OpenAI v1.x"""
    print("🧪 TEST IMPORT OPENAI v1.x")
    print("=" * 50)
    
    try:
        # Test import OpenAI
        from openai import OpenAI
        print("✅ OpenAI v1.x importé avec succès")
        
        # Test version si disponible
        import openai
        if hasattr(openai, '__version__'):
            print(f"📦 Version OpenAI: {openai.__version__}")
        else:
            print("📦 Version OpenAI: Non disponible")
            
        # Test création client (sans clé API)
        try:
            client = OpenAI(api_key="test-key")
            print("✅ Client OpenAI créé avec succès")
        except Exception as e:
            print(f"⚠️ Création client: {e}")
            
        return True
        
    except ImportError as e:
        print(f"❌ Erreur import OpenAI: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

def test_gpt_modules():
    """Test les modules GPT"""
    print("\n🧪 TEST MODULES GPT")
    print("=" * 50)
    
    try:
        # Test CV Parser
        from nextvision.gpt_modules.cv_parser import NextvisionGPTParser
        cv_parser = NextvisionGPTParser()
        print("✅ CV Parser initialisé")
        
        # Test Job Parser
        from nextvision.gpt_modules.job_parser import NextvisionJobParser
        job_parser = NextvisionJobParser()
        print("✅ Job Parser initialisé")
        
        # Test Integration
        from nextvision.gpt_modules.integration import NextvisionGPTIntegration
        integration = NextvisionGPTIntegration()
        print("✅ Integration initialisée")
        
        return True, cv_parser, job_parser, integration
        
    except Exception as e:
        print(f"❌ Erreur modules GPT: {e}")
        return False, None, None, None

def test_parsing_functionality(cv_parser, job_parser):
    """Test la fonctionnalité de parsing"""
    print("\n🧪 TEST PARSING FUNCTIONALITY")
    print("=" * 50)
    
    try:
        # Test CV parsing
        test_cv = """
        Dorothée Lim
        Assistante de Direction
        17 ans d'expérience
        Hermès International
        """
        
        profile = cv_parser.parse_cv(test_cv)
        print(f"✅ CV parsé: {profile.informations_personnelles['nom_complet']}")
        
        # Test Job parsing
        test_job = """
        Recherche Assistante de Direction
        CDI - Paris
        5-10 ans d'expérience
        """
        
        job_posting = job_parser.parse_job(test_job)
        print(f"✅ Job parsé: {job_posting.informations_poste['intitule']}")
        
        return True, profile, job_posting
        
    except Exception as e:
        print(f"❌ Erreur parsing: {e}")
        return False, None, None

def test_matching_functionality(integration, profile, job_posting):
    """Test la fonctionnalité de matching"""
    print("\n🧪 TEST MATCHING FUNCTIONALITY")
    print("=" * 50)
    
    try:
        # Test matching
        result = integration.compute_enhanced_matching(profile, job_posting)
        
        print(f"✅ Matching réussi:")
        print(f"   📊 Score: {result.overall_score}")
        print(f"   🎯 Recommandation: {result.recommendation}")
        print(f"   ⚠️ Alertes: {len(result.alerts)}")
        
        # Affichage des statistiques
        stats = integration.get_integration_statistics()
        print(f"   📈 Statistiques: {stats['status']}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Erreur matching: {e}")
        return False, None

def test_openai_availability():
    """Test la disponibilité OpenAI"""
    print("\n🧪 TEST DISPONIBILITÉ OPENAI")
    print("=" * 50)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"✅ Clé API OpenAI détectée: {api_key[:8]}...")
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            print("✅ Client OpenAI initialisé avec clé API")
            return True
        except Exception as e:
            print(f"⚠️ Erreur initialisation client: {e}")
            return False
    else:
        print("⚠️ Clé API OpenAI non configurée")
        print("   Variable d'environnement OPENAI_API_KEY manquante")
        return False

def generate_test_report():
    """Génère un rapport de test complet"""
    print("\n🚀 RAPPORT DE TEST NEXTVISION OpenAI v1.x")
    print("=" * 70)
    
    # Tests
    openai_import_ok = test_openai_import()
    modules_ok, cv_parser, job_parser, integration = test_gpt_modules()
    
    if modules_ok:
        parsing_ok, profile, job_posting = test_parsing_functionality(cv_parser, job_parser)
        
        if parsing_ok:
            matching_ok, result = test_matching_functionality(integration, profile, job_posting)
        else:
            matching_ok = False
    else:
        parsing_ok = False
        matching_ok = False
    
    openai_available = test_openai_availability()
    
    # Résumé
    print("\n📊 RÉSUMÉ DU TEST")
    print("=" * 70)
    
    status_icon = lambda ok: "✅" if ok else "❌"
    
    print(f"{status_icon(openai_import_ok)} Import OpenAI v1.x")
    print(f"{status_icon(modules_ok)} Modules GPT")
    print(f"{status_icon(parsing_ok)} Parsing CV/Job")
    print(f"{status_icon(matching_ok)} Matching")
    print(f"{status_icon(openai_available)} OpenAI API disponible")
    
    # Status global
    all_ok = all([openai_import_ok, modules_ok, parsing_ok, matching_ok])
    
    if all_ok:
        print("\n🎉 SUCCÈS : Nextvision OpenAI v1.x prêt !")
        if openai_available:
            print("✅ Mode OpenAI complet activé")
        else:
            print("⚠️ Mode fallback activé (clé API manquante)")
    else:
        print("\n❌ ÉCHEC : Problèmes détectés")
        
    print("\n🚀 Pour démarrer Nextvision :")
    print("   cd /Users/baptistecomas/Nextvision")
    print("   pip install -r requirements.txt")
    print("   python main.py")
    
    return all_ok

def main():
    """Point d'entrée principal"""
    try:
        success = generate_test_report()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
