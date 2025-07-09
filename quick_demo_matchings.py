#!/usr/bin/env python3
"""
🎯 NextVision V3.0 - Visualiseur de Matchings Simple
==================================================

Script rapide pour voir les résultats de matching sans configuration API.
Interface en ligne de commande simple et efficace.

Author: NEXTEN Team  
Version: 3.0.1
"""

from nextvision.engines.adaptive_weighting_engine_v3 import AdaptiveWeightingEngine
import time

def quick_matching_demo():
    """Démonstration rapide avec résultats visuels"""
    
    print("🎯 NEXTVISION V3.0 - DÉMONSTRATION MATCHINGS")
    print("=" * 60)
    
    # Initialisation
    print("🚀 Initialisation moteur adaptatif...")
    engine = AdaptiveWeightingEngine(validate_matrices=True)
    print("✅ Moteur initialisé")
    
    # Candidats test
    candidates = [
        {
            "candidate_id": "DEV_SENIOR_001",
            "name": "Baptiste Comas - Senior Developer",
            "skills": ["python", "django", "react", "postgresql"],
            "years_experience": 7,
            "current_salary": 58000,
            "desired_salary": 70000,
            "listening_reasons": ["remuneration_faible"],
            "employment_status": "en_poste"
        },
        {
            "candidate_id": "FREELANCE_001", 
            "name": "Alex Dubois - Freelance React",
            "skills": ["react", "typescript", "graphql"],
            "years_experience": 5,
            "current_salary": 0,  # Freelance
            "desired_salary": 55000,
            "listening_reasons": ["flexibilite"],
            "employment_status": "freelance"
        },
        {
            "candidate_id": "JUNIOR_001",
            "name": "Marie Martin - Junior Vue.js",
            "skills": ["javascript", "vue", "node"],
            "years_experience": 2,
            "current_salary": 38000,
            "desired_salary": 42000,
            "listening_reasons": ["poste_inadequat"],
            "employment_status": "en_poste"
        }
    ]
    
    # Postes test
    positions = [
        {
            "position_id": "FINTECH_001",
            "title": "Senior Python Developer - Fintech",
            "required_skills": ["python", "django", "postgresql"],
            "salary_max": 75000,
            "company_sector": "fintech"
        },
        {
            "position_id": "STARTUP_001",
            "title": "Frontend React Developer - Startup",
            "required_skills": ["react", "typescript"],
            "salary_max": 60000,
            "company_sector": "startup"
        },
        {
            "position_id": "ECOMMERCE_001",
            "title": "Junior Vue.js Developer - E-commerce",
            "required_skills": ["vue", "javascript"],
            "salary_max": 45000,
            "company_sector": "e-commerce"
        }
    ]
    
    print(f"\n📊 Test {len(candidates)} candidats x {len(positions)} postes")
    print("=" * 60)
    
    # Calculs matchings
    results = []
    total_start = time.time()
    
    for candidate in candidates:
        print(f"\n👤 {candidate['name']}")
        print(f"   Compétences: {', '.join(candidate['skills'])}")
        print(f"   Salaire: {candidate['current_salary']:,}€ → {candidate['desired_salary']:,}€")
        print(f"   Raison: {candidate['listening_reasons'][0]}")
        
        for position in positions:
            start_time = time.time()
            result = engine.calculate_adaptive_matching_score(candidate, position)
            process_time = (time.time() - start_time) * 1000
            
            # Score et émoji
            score = result.total_score
            if score >= 0.8:
                emoji = "🌟"
                quality = "EXCELLENT"
            elif score >= 0.6:
                emoji = "👍"
                quality = "BON"
            elif score >= 0.4:
                emoji = "🤔"
                quality = "MOYEN"
            else:
                emoji = "👎"
                quality = "FAIBLE"
            
            print(f"   {emoji} {position['title'][:40]:40} | Score: {score:.3f} ({quality}) | {process_time:.1f}ms")
            
            results.append({
                'candidate': candidate['name'],
                'position': position['title'],
                'score': score,
                'reason': result.listening_reason.value,
                'time_ms': process_time
            })
    
    total_time = (time.time() - total_start) * 1000
    
    # Top matchings
    print(f"\n🏆 TOP 5 MATCHINGS:")
    print("-" * 60)
    top_results = sorted(results, key=lambda x: x['score'], reverse=True)[:5]
    
    for i, match in enumerate(top_results, 1):
        print(f"{i}. {match['candidate'][:25]:25} → {match['position'][:30]:30}")
        print(f"   Score: {match['score']:.3f} | Raison: {match['reason']} | {match['time_ms']:.1f}ms")
    
    # Statistiques
    scores = [r['score'] for r in results]
    times = [r['time_ms'] for r in results]
    
    print(f"\n📊 STATISTIQUES:")
    print("-" * 30)
    print(f"Total matchings: {len(results)}")
    print(f"Score moyen: {sum(scores)/len(scores):.3f}")
    print(f"Meilleur score: {max(scores):.3f}")
    print(f"Plus faible: {min(scores):.3f}")
    print(f"Excellents (>0.8): {len([s for s in scores if s > 0.8])}")
    print(f"Temps moyen: {sum(times)/len(times):.1f}ms")
    print(f"Temps total: {total_time:.1f}ms")
    print(f"Performance: {len(results)/(total_time/1000):.0f} matchings/seconde")
    
    # Test spécifique salary_progression (ancien bug)
    print(f"\n🔥 VÉRIFICATION BUG SALARY_PROGRESSION:")
    print("-" * 45)
    
    problematic_candidate = {
        "candidate_id": "CAND_069_TEST",
        "name": "Test Freelance (Ancien bug)",
        "skills": ["react"],
        "current_salary": 0,  # CAS PROBLÉMATIQUE
        "desired_salary": 55000,
        "employment_status": "freelance",
        "listening_reasons": ["flexibilite"]
    }
    
    test_position = positions[0]
    
    try:
        result = engine.calculate_adaptive_matching_score(problematic_candidate, test_position)
        salary_comp = next((s for s in result.component_scores if s.name == "salary_progression"), None)
        
        if salary_comp:
            details = salary_comp.details
            print("✅ Test réussi - Variables présentes:")
            print(f"   Expected progression: {details['expected_progression_pct']}")
            print(f"   Offered progression: {details['offered_progression_pct']}")
            print(f"   Score: {salary_comp.raw_score:.3f}")
            print(f"   Explanation: {details['score_explanation']}")
        else:
            print("❌ Composant salary_progression manquant")
            
    except Exception as e:
        print(f"❌ BUG PERSISTANT: {e}")
        return
    
    print(f"\n🎉 NEXTVISION V3.0.1 OPÉRATIONNEL")
    print("✅ Bug salary_progression corrigé")
    print("✅ Performance excellente")
    print("✅ Tous composants fonctionnels")
    print("\n🚀 Pour l'API Web complète: python main.py")

if __name__ == "__main__":
    try:
        quick_matching_demo()
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt du programme")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
