#!/usr/bin/env python3
"""
🚀 TEST RAPIDE OPTIMISATIONS PHASE 1 - NEXTVISION
=================================================

Test des optimisations Phase 1 : 48s → 25s
✅ GPT-3.5-turbo vs GPT-4
✅ Parallélisation CV + Job
✅ Prompts optimisés

Usage: python test_phase1_optimizations.py
"""

import asyncio
import time
import logging
from typing import Optional

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data
TEST_CV_CONTENT = """
MOHAMED OUADHANE
Développeur Full Stack Senior
Email: mohamed.ouadhane@email.com
Téléphone: +33 6 12 34 56 78
Localisation: Paris, France

EXPÉRIENCE PROFESSIONNELLE
Développeur Full Stack Senior | TechCorp (2020-2024)
- Développement applications web React/Node.js
- Architecture microservices AWS
- Lead technique équipe de 5 développeurs
- Gestion projets agiles

Développeur Backend | StartupInnovante (2018-2020)
- API REST Python/Django
- Base de données PostgreSQL
- DevOps CI/CD

COMPÉTENCES TECHNIQUES
- Frontend: React, Vue.js, TypeScript, HTML5, CSS3
- Backend: Node.js, Python, Django, Express.js
- Base de données: PostgreSQL, MongoDB, Redis
- Cloud: AWS, Docker, Kubernetes
- Outils: Git, Jenkins, JIRA

FORMATION
Master Informatique | EPITECH (2016-2018)
Licence Informatique | Université Paris 7 (2013-2016)

LANGUES
- Français: Natif
- Anglais: Courant
- Arabe: Natif

OBJECTIF
Recherche un poste de Lead Developer dans une entreprise innovante pour évoluer vers l'architecture logicielle.
"""

TEST_JOB_CONTENT = """
BCOM HR - Fiche de poste Assistant Facturation

POSTE : Assistant Facturation H/F
ENTREPRISE : BCOM HR Solutions
LOCALISATION : Paris 15ème, France
TYPE DE CONTRAT : CDI
SALAIRE : 35 000€ - 42 000€ brut annuel

DESCRIPTION DU POSTE
Nous recherchons un Assistant Facturation pour rejoindre notre équipe comptable.
Vous serez responsable de la gestion complète du processus de facturation.

MISSIONS PRINCIPALES
- Établissement et envoi des factures clients
- Suivi des paiements et relances
- Réconciliation comptable
- Gestion des litiges clients
- Reporting mensuel

COMPÉTENCES REQUISES
- Bac+2 minimum en comptabilité/gestion
- Maîtrise des outils bureautiques (Excel, Word)
- Connaissance logiciel de facturation (SAP, Sage)
- Rigueur et organisation
- Excellent relationnel client

COMPÉTENCES APPRÉCIÉES
- Expérience en facturation (2+ ans)
- Anglais professionnel
- Connaissance ERP

AVANTAGES
- Tickets restaurant
- Mutuelle entreprise
- RTT
- Télétravail 2 jours/semaine
- Formation continue

TÉLÉTRAVAIL : Hybride (3 jours bureau / 2 jours télétravail)
"""

async def test_original_vs_optimized():
    """Test comparaison performance original vs optimisé"""
    
    print("🚀 === TEST OPTIMISATIONS PHASE 1 ===")
    print(f"📊 Objectif : 48s → 25s (48% amélioration)")
    print("")
    
    try:
        # Import service optimisé
        from nextvision.services.gpt_direct_service_optimized import (
            parse_both_parallel_optimized,
            get_gpt_service_optimized_status
        )
        
        # Status service optimisé
        status = get_gpt_service_optimized_status()
        print("📊 SERVICE OPTIMISÉ :")
        print(f"   • Version: {status['version']}")
        print(f"   • Modèle: {status['optimizations']['gpt_model']}")
        print(f"   • Parallélisation: {status['optimizations']['parallel_processing']}")
        print(f"   • Réduction tokens: {status['optimizations']['token_reduction']}")
        print(f"   • Objectif: {status['performance']['target_improvement']}")
        print("")
        
        # Test parsing parallèle optimisé
        print("🚀 Test parsing parallèle optimisé...")
        start_time = time.time()
        
        cv_data, job_data = await parse_both_parallel_optimized(
            cv_content=TEST_CV_CONTENT,
            job_content=TEST_JOB_CONTENT
        )
        
        end_time = time.time()
        processing_time = (end_time - start_time) * 1000
        
        print(f"✅ RÉSULTATS PARSING OPTIMISÉ :")
        print(f"   • Temps total: {processing_time:.2f}ms")
        print(f"   • CV parsé: {cv_data.name}")
        print(f"   • Job parsé: {job_data.title if job_data else 'None'}")
        print(f"   • Compétences CV: {len(cv_data.skills)} détectées")
        print(f"   • Expérience: {cv_data.years_of_experience} ans")
        
        if job_data:
            print(f"   • Compétences Job: {len(job_data.required_skills)} requises")
            print(f"   • Salaire: {job_data.salary_range}")
        
        print("")
        
        # Estimation vs baseline
        estimated_baseline = 45000  # 45s baseline estimé
        improvement_ms = estimated_baseline - processing_time
        improvement_percent = (improvement_ms / estimated_baseline) * 100
        
        print("📊 COMPARAISON PERFORMANCE :")
        print(f"   • Baseline estimé: {estimated_baseline:.0f}ms")
        print(f"   • Optimisé mesuré: {processing_time:.2f}ms")
        print(f"   • Gain absolu: {improvement_ms:.2f}ms")
        print(f"   • Amélioration: {improvement_percent:.1f}%")
        
        # Validation objectifs
        target_25s = processing_time < 25000
        target_15s = processing_time < 15000
        
        if target_15s:
            print("🎯 OBJECTIF FINAL ATTEINT : < 15s !")
        elif target_25s:
            print("🎯 OBJECTIF PHASE 1 ATTEINT : < 25s !")
        else:
            print("⚠️  Objectif Phase 1 non atteint (> 25s)")
        
        print("")
        
        return {
            "processing_time_ms": processing_time,
            "improvement_percent": improvement_percent,
            "target_25s_achieved": target_25s,
            "target_15s_achieved": target_15s,
            "cv_data": cv_data,
            "job_data": job_data
        }
        
    except ImportError as e:
        print(f"❌ Erreur import service optimisé: {e}")
        print("💡 Vérifier que le service optimisé est bien déployé")
        return None
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return None

async def test_individual_components():
    """Test composants individuels optimisés"""
    
    print("🔍 === TEST COMPOSANTS INDIVIDUELS ===")
    
    try:
        from nextvision.services.gpt_direct_service_optimized import (
            parse_cv_direct_optimized,
            parse_job_direct_optimized
        )
        
        # Test CV seul
        print("📄 Test CV optimisé...")
        cv_start = time.time()
        cv_data = await parse_cv_direct_optimized(TEST_CV_CONTENT)
        cv_time = (time.time() - cv_start) * 1000
        print(f"   ✅ CV: {cv_time:.2f}ms - {cv_data.name}")
        
        # Test Job seul
        print("💼 Test Job optimisé...")
        job_start = time.time()
        job_data = await parse_job_direct_optimized(TEST_JOB_CONTENT)
        job_time = (time.time() - job_start) * 1000
        print(f"   ✅ Job: {job_time:.2f}ms - {job_data.title}")
        
        # Comparaison séquentiel vs parallèle
        sequential_total = cv_time + job_time
        print("")
        print("📊 COMPARAISON SÉQUENTIEL vs PARALLÈLE :")
        print(f"   • CV seul: {cv_time:.2f}ms")
        print(f"   • Job seul: {job_time:.2f}ms")
        print(f"   • Total séquentiel: {sequential_total:.2f}ms")
        print(f"   • Parallèle attendu: ~{max(cv_time, job_time):.2f}ms")
        print(f"   • Gain parallélisation: ~{sequential_total - max(cv_time, job_time):.2f}ms")
        
        return {
            "cv_time_ms": cv_time,
            "job_time_ms": job_time,
            "sequential_total_ms": sequential_total,
            "parallel_estimate_ms": max(cv_time, job_time)
        }
        
    except Exception as e:
        print(f"❌ Erreur test composants: {e}")
        return None

async def main():
    """Test principal optimisations Phase 1"""
    
    print("🚀 NEXTVISION - TEST OPTIMISATIONS PHASE 1")
    print("=" * 50)
    print("")
    
    # Test parallélisation optimisée
    parallel_results = await test_original_vs_optimized()
    
    print("")
    
    # Test composants individuels
    component_results = await test_individual_components()
    
    print("")
    print("🎯 === RÉSUMÉ TESTS ===")
    
    if parallel_results:
        print(f"✅ Parsing parallèle: {parallel_results['processing_time_ms']:.2f}ms")
        print(f"✅ Amélioration estimée: {parallel_results['improvement_percent']:.1f}%")
        print(f"✅ Objectif Phase 1 (<25s): {'🎯 ATTEINT' if parallel_results['target_25s_achieved'] else '❌ Non atteint'}")
        print(f"✅ Objectif Final (<15s): {'🎯 ATTEINT' if parallel_results['target_15s_achieved'] else '⏳ En cours'}")
    
    if component_results:
        print(f"✅ Gain parallélisation: ~{component_results['sequential_total_ms'] - component_results['parallel_estimate_ms']:.2f}ms")
    
    print("")
    print("🎯 PROCHAINES ÉTAPES :")
    print("   1. Tester avec API complète via endpoint optimisé")
    print("   2. Valider résultats en conditions réelles")
    print("   3. Mesurer coûts API (90% réduction attendue)")
    print("   4. Si OK : Migration vers endpoint principal")
    
    print("")
    print("✅ Tests optimisations Phase 1 terminés !")

if __name__ == "__main__":
    asyncio.run(main())
