#!/usr/bin/env python3
"""
🎯 DEMO - MotivationsAlignmentScorer CORRIGÉ
===========================================

Démonstration du MotivationsAlignmentScorer avec structure JobData complète.
Résout le problème: TypeError missing 7 required positional arguments

✅ STRUCTURE JOBDATA COMPLÈTE utilisée
✅ Performance testée < 5ms objectif
✅ Prêt pour intégration endpoint

Author: NEXTEN Team
"""

import sys
import os
import time

# Add nextvision to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from nextvision.engines.motivations_scoring_engine import (
        MotivationsAlignmentScorer,
        create_complete_job_data,
        create_complete_cv_data,
        motivations_scoring_engine
    )
    from nextvision.services.gpt_direct_service import JobData, CVData
    print("✅ Imports NEXTVISION successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_basic_alignment():
    """🎯 Test basique d'alignement motivationnel"""
    print("\n" + "="*60)
    print("🎯 TEST BASIC ALIGNMENT - JobData Structure Complète")
    print("="*60)
    
    # ✅ CANDIDATE DATA - Structure complète
    candidate = create_complete_cv_data(
        name="Marie Dubois",
        skills=["Python", "Machine Learning", "Leadership", "Innovation"],
        years_of_experience=5,
        objective="Recherche poste avec forte dimension innovation et évolution technique. Motivation pour leadership d'équipe et impact produit.",
        summary="Senior Developer passionnée d'innovation et de développement d'équipe",
        location="Paris, France"
    )
    
    # ✅ JOB DATA - Structure complète avec TOUS les champs requis
    job = create_complete_job_data(
        title="Senior AI Engineer & Tech Lead",
        company="InnovTech Solutions",
        location="Paris, France",
        contract_type="CDI",
        required_skills=["Python", "AI/ML", "Leadership technique", "Innovation"],
        preferred_skills=["TensorFlow", "Team management", "Product development"],
        responsibilities=[
            "Leadership technique équipe 5 personnes",
            "Développement solutions IA innovantes",
            "Mentoring développeurs junior",
            "Architecture produits disruptifs"
        ],
        requirements=[
            "5+ ans expérience Python/ML",
            "Expérience leadership technique",
            "Passion innovation et disruption"
        ],
        benefits=[
            "Innovation continue sur projets cutting-edge",
            "Évolution rapide vers CTO possible",
            "Équipe technique d'excellence",
            "Formation et conférences budget illimité",
            "Stock-options startup"
        ],
        salary_range={"min": 70000, "max": 90000},
        remote_policy="Hybride 3 jours/semaine télétravail"
    )
    
    print(f"👤 Candidat: {candidate.name}")
    print(f"   Compétences: {', '.join(candidate.skills)}")
    print(f"   Objectif: {candidate.objective[:80]}...")
    print()
    print(f"💼 Job: {job.title} chez {job.company}")
    print(f"   Compétences requises: {', '.join(job.required_skills)}")
    print(f"   Avantages: {len(job.benefits)} éléments")
    print(f"   Salaire: {job.salary_range['min']}k-{job.salary_range['max']}k")
    
    # 🎯 SCORING AVEC MOTIVATIONS EXPLICITES
    start_time = time.time()
    
    scorer = MotivationsAlignmentScorer()
    result = scorer.score_motivations_alignment(
        candidate_data=candidate,
        job_data=job,
        candidate_motivations=[
            "Innovation technique",
            "Évolution carrière", 
            "Leadership équipe",
            "Impact produit"
        ]
    )
    
    processing_time = (time.time() - start_time) * 1000
    
    # RÉSULTATS
    print("\n" + "-"*50)
    print("📊 RÉSULTATS SCORING MOTIVATIONNEL")
    print("-"*50)
    print(f"🎯 Score Global: {result.overall_score:.3f}/1.000")
    print(f"📊 Confiance: {result.confidence:.3f}")
    print(f"⏱️ Temps traitement: {result.processing_time_ms:.2f}ms")
    print(f"⚡ Performance demo: {processing_time:.2f}ms")
    
    if result.strongest_alignments:
        print(f"\n🔥 Alignements forts ({len(result.strongest_alignments)}):")
        for alignment in result.strongest_alignments:
            print(f"   ✅ {alignment}")
    
    if result.motivation_scores:
        print(f"\n📈 Détail par motivation ({len(result.motivation_scores)}):")
        for score in result.motivation_scores[:5]:  # Top 5
            print(f"   {score.motivation_type.value.title()}: {score.score:.3f} (poids: {score.weight:.2f})")
    
    if result.improvement_suggestions:
        print(f"\n💡 Suggestions amélioration:")
        for suggestion in result.improvement_suggestions:
            print(f"   🔧 {suggestion}")
    
    # VALIDATION PERFORMANCE
    performance_ok = result.processing_time_ms < 10  # Objectif < 10ms
    print(f"\n{'✅' if performance_ok else '⚠️'} Performance: {'EXCELLENT' if performance_ok else 'ACCEPTABLE'}")
    
    return result

def test_multiple_profiles():
    """🎯 Test avec plusieurs profils candidats"""
    print("\n" + "="*60)
    print("🎯 TEST MULTIPLE PROFILES")
    print("="*60)
    
    # Job fixe startup IA
    job = create_complete_job_data(
        title="AI Product Manager",
        company="StartupIA",
        required_skills=["Product Management", "AI", "Innovation"],
        benefits=["Innovation disruptive", "Équipe agile", "Télétravail complet"],
        responsibilities=["Gestion produit IA", "Innovation continue", "Team leadership"],
        salary_range={"min": 60000, "max": 75000},
        remote_policy="Full remote possible"
    )
    
    # Profils candidats variés
    profiles = [
        {
            "name": "Alex Innovation", 
            "motivations": ["Innovation", "Autonomie", "Impact"],
            "skills": ["Product", "Innovation", "Leadership"]
        },
        {
            "name": "Sophie Salaire",
            "motivations": ["Salaire", "Sécurité", "Avantages"],
            "skills": ["Product", "Management", "Finance"]
        },
        {
            "name": "Thomas Équipe",
            "motivations": ["Équipe", "Collaboration", "Apprentissage"],
            "skills": ["Product", "Team management", "Coaching"]
        }
    ]
    
    print(f"💼 Job test: {job.title} chez {job.company}")
    print(f"   Remote: {job.remote_policy}")
    print(f"   Avantages clés: {', '.join(job.benefits[:3])}")
    
    results = []
    for profile in profiles:
        candidate = create_complete_cv_data(
            name=profile["name"],
            skills=profile["skills"],
            objective=f"Candidat orienté {', '.join(profile['motivations'])}"
        )
        
        result = motivations_scoring_engine.score_motivations_alignment(
            candidate_data=candidate,
            job_data=job,
            candidate_motivations=profile["motivations"]
        )
        
        results.append((profile["name"], result))
        print(f"\n👤 {profile['name']}: {result.overall_score:.3f} ({result.processing_time_ms:.1f}ms)")
    
    # Classement
    results.sort(key=lambda x: x[1].overall_score, reverse=True)
    print(f"\n🏆 CLASSEMENT FINAL:")
    for i, (name, result) in enumerate(results, 1):
        print(f"   {i}. {name}: {result.overall_score:.3f}")
    
    return results

def test_performance_stress():
    """⚡ Test performance sous stress"""
    print("\n" + "="*60)
    print("⚡ TEST PERFORMANCE STRESS")
    print("="*60)
    
    job = create_complete_job_data(
        title="Software Engineer",
        company="TechCorp",
        required_skills=["Python", "React"],
        benefits=["Formation", "Évolution"]
    )
    
    candidate = create_complete_cv_data(
        name="Test User",
        skills=["Python", "React", "Leadership"]
    )
    
    # Test 10 scorings rapides
    times = []
    for i in range(10):
        start = time.time()
        result = motivations_scoring_engine.score_motivations_alignment(
            candidate_data=candidate,
            job_data=job,
            candidate_motivations=["Innovation", "Évolution"]
        )
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"📊 RÉSULTATS PERFORMANCE (10 runs):")
    print(f"   ⚡ Temps moyen: {avg_time:.2f}ms")
    print(f"   🚀 Temps min: {min_time:.2f}ms")
    print(f"   🐌 Temps max: {max_time:.2f}ms")
    print(f"   🎯 Objectif < 5ms: {'✅ ATTEINT' if avg_time < 5 else '⚠️ PROCHE' if avg_time < 10 else '❌ À OPTIMISER'}")
    
    return avg_time

def main():
    """🚀 Démonstration complète"""
    print("🎯 NEXTVISION - MotivationsAlignmentScorer Demo")
    print("=" * 70)
    print("✅ Structure JobData complète utilisée")
    print("✅ Tous les champs requis fournis")
    print("✅ Performance optimisée")
    
    try:
        # Test 1: Alignement basique
        result1 = test_basic_alignment()
        
        # Test 2: Profils multiples  
        results2 = test_multiple_profiles()
        
        # Test 3: Performance
        avg_time = test_performance_stress()
        
        # BILAN FINAL
        print("\n" + "="*70)
        print("🏆 BILAN DÉMONSTRATION")
        print("="*70)
        print(f"✅ Score principal: {result1.overall_score:.3f}")
        print(f"✅ Performance moyenne: {avg_time:.2f}ms")
        print(f"✅ Tests profils: {len(results2)} candidats")
        print(f"✅ Structure JobData: COMPLÈTE")
        print()
        print("🚀 MotivationsAlignmentScorer OPÉRATIONNEL!")
        print("🔧 Prêt pour intégration dans /api/v3/intelligent-matching")
        print("📈 Structure compatible avec GPT Direct Service")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR DEMO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
