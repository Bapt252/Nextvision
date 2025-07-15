#!/usr/bin/env python3
"""
Script de démonstration - MotivationsAlignmentScorer
Exemples pratiques d'utilisation du nouveau système de scoring motivationnel
"""

import asyncio
import time
from typing import Dict, Any

# Imports MotivationsAlignmentScorer
from nextvision.engines.motivations_scoring_engine import motivations_scoring_engine
from nextvision.services.job_intelligence_service import job_intelligence_service
from nextvision.models.questionnaire_advanced import MotivationsClassees, QuestionnaireComplet
from nextvision.services.gpt_direct_service import JobData


class MotivationsScoringDemo:
    """Démonstration complète du système de scoring motivationnel"""
    
    def __init__(self):
        self.demo_results = []
    
    async def run_complete_demo(self):
        """Exécute tous les exemples de démonstration"""
        
        print("🎯 DÉMONSTRATION MOTIVATIONSALIGNMENTSCORER")
        print("=" * 60)
        
        # 1. Exemple basique
        await self._demo_basic_scoring()
        
        # 2. Profils candidats variés
        await self._demo_candidate_profiles()
        
        # 3. Types de jobs différents
        await self._demo_job_types()
        
        # 4. Analyse intelligence job
        await self._demo_job_intelligence()
        
        # 5. Performance et cache
        await self._demo_performance_cache()
        
        # 6. Intégration endpoint simulée
        await self._demo_endpoint_integration()
        
        print("\n" + "=" * 60)
        print("🎉 Démonstration terminée avec succès!")
        
        return self.demo_results
    
    async def _demo_basic_scoring(self):
        """Démonstration du scoring basique"""
        
        print("\n📋 1. SCORING BASIQUE")
        print("-" * 30)
        
        # Candidat exemple
        motivations = MotivationsClassees(
            classees=["Innovation", "Évolution", "Équipe", "Salaire"],
            priorites=[1, 2, 3, 4]
        )
        
        # Job exemple
        job = JobData(
            title="Senior AI Engineer",
            company="TechCorp Innovation",
            benefits=["Formation continue", "R&D budget", "Équipe agile", "Stock options"],
            responsibilities=["Développement IA", "Leadership technique", "Innovation produit"]
        )
        
        # Calcul du score
        start_time = time.perf_counter()
        score = await motivations_scoring_engine.calculate_score(
            candidat_motivations=motivations,
            job_data=job
        )
        execution_time = (time.perf_counter() - start_time) * 1000
        
        print(f"Candidat motivations: {motivations.classees}")
        print(f"Job: {job.title} chez {job.company}")
        print(f"Score d'alignement: {score:.3f}")
        print(f"Temps d'exécution: {execution_time:.2f}ms")
        
        self.demo_results.append({
            "demo": "basic_scoring",
            "score": score,
            "execution_time_ms": execution_time
        })
    
    async def _demo_candidate_profiles(self):
        """Démonstration avec différents profils candidats"""
        
        print("\n👥 2. PROFILS CANDIDATS VARIÉS")
        print("-" * 30)
        
        # Job de référence
        reference_job = JobData(
            title="Full Stack Developer",
            company="TechStartup",
            benefits=["Télétravail hybride", "Formation", "Stock options", "Équipe jeune"],
            responsibilities=["Développement web", "Collaboration équipe", "Innovation continue"]
        )
        
        # Profils candidats variés
        profiles = [
            {
                "name": "Candidat Innovation",
                "motivations": MotivationsClassees(
                    classees=["Innovation", "Technologie", "Évolution"],
                    priorites=[1, 2, 3]
                )
            },
            {
                "name": "Candidat Équilibre",
                "motivations": MotivationsClassees(
                    classees=["Flexibilité", "Équipe", "Work-Life Balance"],
                    priorites=[1, 2, 3]
                )
            },
            {
                "name": "Candidat Évolution",
                "motivations": MotivationsClassees(
                    classees=["Évolution", "Leadership", "Responsabilités"],
                    priorites=[1, 2, 3]
                )
            },
            {
                "name": "Candidat Rémunération",
                "motivations": MotivationsClassees(
                    classees=["Salaire", "Avantages", "Sécurité"],
                    priorites=[1, 2, 3]
                )
            }
        ]
        
        for profile in profiles:
            score = await motivations_scoring_engine.calculate_score(
                candidat_motivations=profile["motivations"],
                job_data=reference_job
            )
            
            print(f"{profile['name']}: {score:.3f}")
            print(f"  Priorités: {profile['motivations'].classees}")
            
            self.demo_results.append({
                "demo": "candidate_profiles",
                "profile": profile["name"],
                "score": score
            })
    
    async def _demo_job_types(self):
        """Démonstration avec différents types de jobs"""
        
        print("\n💼 3. TYPES DE JOBS VARIÉS")
        print("-" * 30)
        
        # Candidat de référence (orienté innovation)
        reference_candidate = MotivationsClassees(
            classees=["Innovation", "Évolution", "Technologie"],
            priorites=[1, 2, 3]
        )
        
        # Types de jobs
        jobs = [
            {
                "name": "Startup Innovation",
                "job": JobData(
                    title="AI Research Engineer",
                    company="InnovLab",
                    benefits=["R&D libre", "Conférences", "Équipe recherche"],
                    responsibilities=["Recherche IA", "Brevets", "Innovation disruptive"]
                )
            },
            {
                "name": "Corporate Stable",
                "job": JobData(
                    title="Senior Developer",
                    company="BigCorp",
                    benefits=["Salaire élevé", "Sécurité emploi", "Formation"],
                    responsibilities=["Maintenance", "Processus établis", "Documentation"]
                )
            },
            {
                "name": "Scale-up Tech",
                "job": JobData(
                    title="Tech Lead",
                    company="GrowthTech",
                    benefits=["Leadership", "Croissance rapide", "Innovation"],
                    responsibilities=["Architecture", "Équipe", "Évolution produit"]
                )
            }
        ]
        
        for job_info in jobs:
            score = await motivations_scoring_engine.calculate_score(
                candidat_motivations=reference_candidate,
                job_data=job_info["job"]
            )
            
            print(f"{job_info['name']}: {score:.3f}")
            print(f"  {job_info['job'].title} chez {job_info['job'].company}")
            
            self.demo_results.append({
                "demo": "job_types",
                "job_type": job_info["name"],
                "score": score
            })
    
    async def _demo_job_intelligence(self):
        """Démonstration de l'analyse d'intelligence job"""
        
        print("\n🧠 4. ANALYSE INTELLIGENCE JOB")
        print("-" * 30)
        
        # Job complexe pour analyse
        complex_job = JobData(
            title="Principal AI Engineer",
            company="TechUnicorn",
            benefits=[
                "Télétravail 100%", "Formation illimitée", "Stock options importantes",
                "Budget R&D personnel", "Conférences internationales"
            ],
            responsibilities=[
                "Architecture IA scalable", "Leadership technique équipe 15 personnes",
                "Innovation breakthrough", "Collaboration C-level", "Veille technologique"
            ]
        )
        
        # Analyse intelligence
        intelligence = await job_intelligence_service.analyze_job_intelligence(
            job_data=complex_job,
            cache_key="demo_complex_job"
        )
        
        print(f"Job: {complex_job.title}")
        print(f"Culture détectée: {intelligence.culture_type}")
        print(f"Niveau innovation: {intelligence.innovation_level}")
        print(f"Potentiel croissance: {intelligence.growth_potential:.2f}")
        print(f"Flexibilité télétravail: {intelligence.remote_flexibility:.2f}")
        print(f"Potentiel leadership: {intelligence.leadership_potential:.2f}")
        print(f"Opportunités apprentissage: {len(intelligence.learning_opportunities)}")
        print(f"Score confiance: {intelligence.confidence_score:.2f}")
        print(f"Temps traitement: {intelligence.processing_time_ms:.2f}ms")
        
        if intelligence.learning_opportunities:
            print(f"Opportunités: {', '.join(intelligence.learning_opportunities[:3])}")
        
        self.demo_results.append({
            "demo": "job_intelligence",
            "culture_type": intelligence.culture_type,
            "innovation_level": intelligence.innovation_level,
            "confidence": intelligence.confidence_score
        })
    
    async def _demo_performance_cache(self):
        """Démonstration des performances et du cache"""
        
        print("\n⚡ 5. PERFORMANCE ET CACHE")
        print("-" * 30)
        
        # Job et candidat pour tests
        test_job = JobData(
            title="Software Engineer",
            benefits=["Formation", "Équipe"],
            responsibilities=["Développement", "Collaboration"]
        )
        
        test_motivations = MotivationsClassees(
            classees=["Innovation", "Équipe"],
            priorites=[1, 2]
        )
        
        # Test sans cache (premier appel)
        print("Test sans cache:")
        times_no_cache = []
        for i in range(5):
            start = time.perf_counter()
            score = await motivations_scoring_engine.calculate_score(
                candidat_motivations=test_motivations,
                job_data=test_job,
                job_cache_key=f"perf_test_{i}"
            )
            execution_time = (time.perf_counter() - start) * 1000
            times_no_cache.append(execution_time)
        
        avg_no_cache = sum(times_no_cache) / len(times_no_cache)
        print(f"  Temps moyen: {avg_no_cache:.2f}ms")
        
        # Test avec cache (appels répétés)
        print("Test avec cache:")
        times_cache = []
        for i in range(5):
            start = time.perf_counter()
            score = await motivations_scoring_engine.calculate_score(
                candidat_motivations=test_motivations,
                job_data=test_job,
                job_cache_key="perf_test_0"  # Même clé = cache hit
            )
            execution_time = (time.perf_counter() - start) * 1000
            times_cache.append(execution_time)
        
        avg_cache = sum(times_cache) / len(times_cache)
        improvement = avg_no_cache / avg_cache if avg_cache > 0 else 0
        
        print(f"  Temps moyen: {avg_cache:.2f}ms")
        print(f"  Amélioration: {improvement:.1f}x")
        
        self.demo_results.append({
            "demo": "performance_cache",
            "avg_no_cache_ms": avg_no_cache,
            "avg_cache_ms": avg_cache,
            "improvement_factor": improvement
        })
    
    async def _demo_endpoint_integration(self):
        """Simulation d'intégration dans l'endpoint intelligent_matching"""
        
        print("\n🔗 6. SIMULATION ENDPOINT INTÉGRATION")
        print("-" * 30)
        
        # Simulation requête complète
        mock_request = {
            "questionnaire": QuestionnaireComplet(
                motivations=MotivationsClassees(
                    classees=["Innovation", "Évolution", "Équipe"],
                    priorites=[1, 2, 3]
                )
            ),
            "job_requirements": JobData(
                title="Senior AI Engineer",
                company="TechCorp",
                benefits=["Formation continue", "Innovation labs", "Équipe agile"],
                responsibilities=["Développement IA", "Leadership", "R&D"]
            ),
            "pourquoi_ecoute": "Recherche nouveau défi innovation"
        }
        
        # Simulation du calcul complet
        start_time = time.perf_counter()
        
        # Scores existants (simulation)
        static_scores = {
            "semantique": 0.62,
            "hierarchical": 0.66,
            "remuneration": 0.735,
            "experience": 0.5,
            "secteurs": 0.7,
            "localisation": 0.92
        }
        
        # Nouveau score motivations
        motivations_score = await motivations_scoring_engine.calculate_score(
            candidat_motivations=mock_request["questionnaire"].motivations,
            job_data=mock_request["job_requirements"]
        )
        
        # Analyse job intelligence
        job_intel = await job_intelligence_service.analyze_job_intelligence(
            job_data=mock_request["job_requirements"]
        )
        
        # Scores combinés
        all_scores = {**static_scores, "motivations": motivations_score}
        
        # Pondération adaptative (simulation)
        weights = {
            "semantique": 0.12,      # -3% pour innovation
            "hierarchical": 0.10,
            "remuneration": 0.15,    # -5% pour innovation
            "experience": 0.10,
            "secteurs": 0.15,
            "localisation": 0.15,
            "motivations": 0.23      # +8% pour innovation
        }
        
        # Score final
        final_score = sum(all_scores[comp] * weights[comp] for comp in all_scores.keys())
        
        total_time = (time.perf_counter() - start_time) * 1000
        
        print(f"Requête: {mock_request['job_requirements'].title}")
        print(f"Pourquoi écoute: {mock_request['pourquoi_ecoute']}")
        print(f"Score motivations: {motivations_score:.3f}")
        print(f"Job culture: {job_intel.culture_type}")
        print(f"Score final: {final_score:.3f}")
        print(f"Temps total: {total_time:.2f}ms")
        print(f"Objectif < 21ms: {'✅ PASS' if total_time < 21 else '⚠️ WARN'}")
        
        # Simulation réponse enrichie
        response = {
            "final_score": round(final_score, 3),
            "component_scores": all_scores,
            "motivations_analysis": {
                "score": round(motivations_score, 3),
                "candidat_priorities": mock_request["questionnaire"].motivations.classees,
                "job_culture": job_intel.culture_type,
                "innovation_level": job_intel.innovation_level,
                "confidence": round(job_intel.confidence_score, 2)
            }
        }
        
        print(f"\nRéponse enrichie preview:")
        print(f"  component_scores.motivations: {response['component_scores']['motivations']}")
        print(f"  motivations_analysis.job_culture: {response['motivations_analysis']['job_culture']}")
        
        self.demo_results.append({
            "demo": "endpoint_integration",
            "final_score": final_score,
            "total_time_ms": total_time,
            "performance_target_met": total_time < 21
        })


async def run_demo():
    """Point d'entrée principal pour la démonstration"""
    
    demo = MotivationsScoringDemo()
    results = await demo.run_complete_demo()
    
    # Affichage résumé
    print(f"\n📊 RÉSUMÉ DÉMONSTRATION")
    print(f"Total démos exécutées: {len(results)}")
    
    # Vérification performance
    perf_results = [r for r in results if "execution_time_ms" in r or "total_time_ms" in r]
    if perf_results:
        avg_time = sum(r.get("execution_time_ms", r.get("total_time_ms", 0)) for r in perf_results) / len(perf_results)
        print(f"Temps moyen d'exécution: {avg_time:.2f}ms")
    
    print(f"🎯 Démonstration MotivationsAlignmentScorer terminée avec succès!")
    
    return results


if __name__ == "__main__":
    print("🚀 Lancement démonstration MotivationsAlignmentScorer...")
    results = asyncio.run(run_demo())
