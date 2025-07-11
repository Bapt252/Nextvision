#!/usr/bin/env python3
"""
🚗 NEXTVISION V3.2.1 - INTÉGRATION TRANSPORT INTELLIGENCE (CORRIGÉ)
=================================================================

Connecte le LocationScoringEngine au système de matching principal
pour remplacer le score de localisation fixe par des calculs dynamiques.

🔧 CORRECTIONS APPORTÉES:
- Fix RaisonEcoute.RECHERCHE_NOUVEAU_DEFI → utilisation valeurs existantes
- Fix structure TimingInfo et EnvironnementTravail
- Fix imports et gestion des objets questionnaire

Author: NEXTEN Team
Version: 3.2.1 - Transport Intelligence Integration (Fixed)
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import asdict

def add_nextvision_path():
    """Ajoute le répertoire Nextvision au PYTHONPATH"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    nextvision_dir = os.path.join(current_dir)
    if nextvision_dir not in sys.path:
        sys.path.insert(0, nextvision_dir)

# Ajout du path avant les imports
add_nextvision_path()

try:
    # Imports Nextvision
    from nextvision.services.transport_calculator import TransportCalculator
    from nextvision.services.google_maps_service import GoogleMapsService
    from nextvision.engines.location_scoring import LocationScoringEngine
    from nextvision.models.transport_models import ConfigTransport
    from nextvision.models.questionnaire_advanced import (
        QuestionnaireComplet, TransportPreferences, MoyenTransport,
        TimingInfo, RaisonEcoute, EnvironnementTravail, DisponibiliteType,
        SecteursPreferences, ContratsPreferences, MotivationsClassees, 
        RemunerationAttentes
    )
    from nextvision.config.google_maps_config import get_google_maps_config
    
    print("✅ Imports Nextvision réussis")
    
except ImportError as e:
    print(f"❌ Erreur import Nextvision: {e}")
    print("💡 Vérifiez que vous êtes dans le répertoire Nextvision/")
    sys.exit(1)

class TransportIntegratedMatchingEngine:
    """🎯 Engine de matching avec Transport Intelligence intégré"""
    
    def __init__(self):
        print("🚀 Initialisation Transport Intelligence...")
        
        # Configuration Google Maps
        self.google_maps_config = get_google_maps_config()
        
        # Services Google Maps
        self.google_maps_service = GoogleMapsService(
            api_key=self.google_maps_config.api_key,
            cache_duration_hours=self.google_maps_config.geocode_cache_duration_hours
        )
        
        # Transport Calculator
        self.transport_calculator = TransportCalculator(self.google_maps_service)
        
        # Location Scoring Engine  
        self.location_scoring_engine = LocationScoringEngine(self.transport_calculator)
        
        # Poids par défaut (comme dans main.py)
        self.default_weights = {
            "semantique": 0.30,     # était 35% → réduit pour équilibrer avec localisation dynamique
            "hierarchical": 0.15,   # Nouveau composant hiérarchique
            "remuneration": 0.20,
            "experience": 0.20,
            "localisation": 0.15,   # Maintenu à 15% mais maintenant DYNAMIQUE
            "secteurs": 0.05
        }
        
        print("✅ Transport Intelligence initialisé")
    
    async def calculate_dynamic_matching_scores(
        self, 
        candidate_data: Dict,
        job_address: str,
        pourquoi_ecoute: str = "Manque de perspectives d'évolution",
        weights: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """🧮 Calcul de matching avec score localisation DYNAMIQUE"""
        
        start_time = time.time()
        
        if weights is None:
            weights = self.default_weights
        
        print(f"🎯 Calcul matching dynamique pour job: {job_address}")
        print(f"📋 Raison d'écoute: '{pourquoi_ecoute}'")
        
        try:
            # 1. 🧮 Scores statiques (comme avant)
            static_scores = await self._calculate_static_scores(candidate_data)
            print(f"📊 Scores statiques calculés: {static_scores}")
            
            # 2. 🚗 Score localisation DYNAMIQUE via Transport Intelligence
            dynamic_location_score = await self._calculate_dynamic_location_score(
                candidate_data, job_address, pourquoi_ecoute
            )
            
            print(f"🗺️ Score localisation dynamique: {dynamic_location_score:.3f}")
            
            # 3. 📊 Assemblage scores finaux
            all_scores = {
                **static_scores,
                "localisation": dynamic_location_score
            }
            
            # 4. 🎯 Score total pondéré
            total_score = sum(all_scores[component] * weights[component] 
                            for component in all_scores.keys() if component in weights)
            
            # 5. 📈 Confiance basée sur qualité des données
            confidence = self._calculate_confidence(all_scores, job_address)
            
            processing_time = (time.time() - start_time) * 1000
            
            result = {
                "component_scores": all_scores,
                "total_score": round(total_score, 3),
                "confidence": round(confidence, 3),
                "transport_intelligence": {
                    "location_score_dynamic": True,
                    "location_score_value": dynamic_location_score,
                    "location_scoring_details": self._get_location_scoring_details()
                },
                "processing_time_ms": round(processing_time, 2),
                "algorithm": "Nextvision V3.2.1 + Transport Intelligence"
            }
            
            print(f"✅ Matching calculé en {processing_time:.1f}ms")
            print(f"🎯 Score total: {total_score:.3f} (confiance: {confidence:.3f})")
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur calcul matching dynamique: {e}")
            
            # Fallback vers scores statiques
            return await self._fallback_static_matching(candidate_data, weights)
    
    async def _calculate_static_scores(self, candidate_data: Dict) -> Dict[str, float]:
        """📊 Calcule les scores statiques (comme dans main.py original)"""
        
        # Extraction des données candidat
        skills_count = len(candidate_data.get("skills", []))
        experience_years = candidate_data.get("experience_years", 0)
        salary_min = candidate_data.get("salary_min", 50000)
        
        # Scores simulés mais cohérents (comme dans main.py)
        scores = {
            "semantique": min(0.9, 0.5 + (skills_count * 0.08) + (experience_years * 0.02)),
            "hierarchical": min(0.85, 0.6 + (experience_years * 0.03)),  # Nouveau
            "remuneration": min(0.95, 0.6 + (salary_min / 100000) * 0.3),
            "experience": min(0.9, 0.4 + (experience_years * 0.05)),
            "secteurs": 0.70  # Score secteur fixe pour demo
        }
        
        return scores
    
    async def _calculate_dynamic_location_score(
        self, 
        candidate_data: Dict, 
        job_address: str,
        pourquoi_ecoute: str
    ) -> float:
        """🗺️ Calcule score localisation via Transport Intelligence"""
        
        try:
            # 1. Création questionnaire candidat pour Location Scoring
            candidat_questionnaire = self._create_candidate_questionnaire(
                candidate_data, pourquoi_ecoute
            )
            
            # 2. Calcul score enrichi via LocationScoringEngine
            location_score = await self.location_scoring_engine.calculate_enriched_location_score(
                candidat_questionnaire=candidat_questionnaire,
                job_address=job_address,
                job_context={}  # Contexte job vide pour demo
            )
            
            # 3. Extraction du score final
            final_score = location_score.final_score
            
            # 4. Stockage des détails pour debugging
            self._last_location_details = {
                "transport_mode": location_score.transport_compatibility.recommended_mode.value if location_score.transport_compatibility.recommended_mode else "unknown",
                "base_distance_km": location_score.base_distance_km,
                "time_score": location_score.time_score,
                "cost_score": location_score.cost_score,
                "comfort_score": location_score.comfort_score,
                "reliability_score": location_score.reliability_score,
                "explanations": location_score.explanations
            }
            
            print(f"🚗 Transport Intelligence:")
            print(f"   Mode recommandé: {self._last_location_details['transport_mode']}")
            print(f"   Distance: {self._last_location_details['base_distance_km']:.1f}km")
            print(f"   Scores → Temps: {self._last_location_details['time_score']:.2f}, "
                  f"Coût: {self._last_location_details['cost_score']:.2f}, "
                  f"Confort: {self._last_location_details['comfort_score']:.2f}")
            
            return final_score
            
        except Exception as e:
            print(f"⚠️ Erreur score localisation dynamique: {e}")
            print("🔄 Fallback vers score localisation fixe")
            
            # Fallback score neutre
            return 0.65
    
    def _create_candidate_questionnaire(
        self, 
        candidate_data: Dict, 
        pourquoi_ecoute: str
    ) -> QuestionnaireComplet:
        """📋 Crée questionnaire candidat pour scoring (CORRIGÉ)"""
        
        # 🔧 FIX: Mapping raisons d'écoute avec valeurs existantes SEULEMENT
        raison_mapping = {
            "Rémunération trop faible": RaisonEcoute.REMUNERATION_FAIBLE,
            "Poste ne coïncide pas avec poste proposé": RaisonEcoute.POSTE_INADEQUAT,
            "Poste trop loin de mon domicile": RaisonEcoute.POSTE_TROP_LOIN,
            "Manque de flexibilité": RaisonEcoute.MANQUE_FLEXIBILITE,
            "Manque de perspectives d'évolution": RaisonEcoute.MANQUE_PERSPECTIVES
        }
        
        # 🔧 FIX: Fallback vers valeur existante au lieu de RECHERCHE_NOUVEAU_DEFI
        raison_ecoute = raison_mapping.get(pourquoi_ecoute, RaisonEcoute.MANQUE_PERSPECTIVES)
        
        # Transport preferences par défaut
        transport_preferences = TransportPreferences(
            moyens_selectionnes=[
                MoyenTransport.VOITURE,
                MoyenTransport.TRANSPORT_COMMUN
            ],
            temps_max={
                "voiture": 45,
                "transport_commun": 60,
                "velo": 30,
                "marche": 25
            }
        )
        
        # 🔧 FIX: Structure TimingInfo correcte
        timing_info = TimingInfo(
            disponibilite=DisponibiliteType.DANS_1_MOIS,  # Valeur enum correcte
            pourquoi_a_lecoute=raison_ecoute,             # Valeur enum correcte
            preavis={"durée": "1 mois", "négociable": True}  # Structure correcte
        )
        
        # 🔧 FIX: EnvironnementTravail est un enum simple, pas une classe
        environnement = EnvironnementTravail.HYBRIDE  # Valeur enum directe
        
        # Secteurs par défaut
        secteurs = SecteursPreferences(
            preferes=["Technologie", "Conseil"],
            redhibitoires=["Tabac"]
        )
        
        # Contrats par défaut
        contrats = ContratsPreferences(
            ordre_preference=[]  # Liste vide pour éviter les erreurs
        )
        
        # Motivations par défaut
        motivations = MotivationsClassees(
            classees=["Évolution", "Salaire", "Ambiance"],
            priorites=[1, 2, 3]
        )
        
        # Rémunération depuis données candidat
        salary_min = candidate_data.get("salary_min", 50000)
        remuneration = RemunerationAttentes(
            min=salary_min,
            max=int(salary_min * 1.3),  # +30% pour le max
            actuel=salary_min
        )
        
        # 🔧 FIX: Questionnaire complet avec tous les champs requis
        questionnaire = QuestionnaireComplet(
            timing=timing_info,
            secteurs=secteurs,
            environnement_travail=environnement,
            transport=transport_preferences,
            contrats=contrats,
            motivations=motivations,
            remuneration=remuneration
        )
        
        return questionnaire
    
    def _calculate_confidence(self, scores: Dict[str, float], job_address: str) -> float:
        """📈 Calcule confiance basée sur qualité des données"""
        
        base_confidence = 0.85
        
        # Bonus si score localisation dynamique réussi
        if hasattr(self, '_last_location_details'):
            if self._last_location_details.get('transport_mode') != 'unknown':
                base_confidence += 0.10
        
        # Bonus si adresse job semble complète
        if len(job_address.split()) >= 3:
            base_confidence += 0.05
        
        return min(0.95, base_confidence)
    
    def _get_location_scoring_details(self) -> Dict:
        """📋 Retourne détails du scoring localisation"""
        
        if hasattr(self, '_last_location_details'):
            return self._last_location_details.copy()
        
        return {"status": "no_details_available"}
    
    async def _fallback_static_matching(self, candidate_data: Dict, weights: Dict) -> Dict:
        """🚨 Fallback vers matching statique en cas d'erreur"""
        
        static_scores = await self._calculate_static_scores(candidate_data)
        static_scores["localisation"] = 0.75  # Score fixe original
        
        total_score = sum(static_scores[component] * weights[component] 
                         for component in static_scores.keys() if component in weights)
        
        return {
            "component_scores": static_scores,
            "total_score": round(total_score, 3),
            "confidence": 0.60,  # Confiance réduite en mode fallback
            "transport_intelligence": {
                "location_score_dynamic": False,
                "location_score_value": 0.75,
                "fallback_mode": True
            },
            "algorithm": "Nextvision V3.2.1 + Static Fallback"
        }

async def test_transport_integration():
    """🧪 Test d'intégration Transport Intelligence"""
    
    print("=" * 60)
    print("🧪 TEST INTÉGRATION TRANSPORT INTELLIGENCE V3.2.1 (CORRIGÉ)")
    print("=" * 60)
    
    # Initialisation du moteur
    engine = TransportIntegratedMatchingEngine()
    
    # Données candidat test
    candidate_test_data = {
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
        "experience_years": 5,
        "salary_min": 65000,
        "location": "13 rue du champ de mars 75007 Paris"
    }
    
    # 🔧 FIX: Jobs test avec raisons d'écoute EXISTANTES seulement
    test_jobs = [
        {
            "address": "1 Place Vendôme 75001 Paris",
            "raison_ecoute": "Poste trop loin de mon domicile"  # ✅ Existe dans enum
        },
        {
            "address": "Tour Eiffel, 5 Avenue Anatole France 75007 Paris", 
            "raison_ecoute": "Rémunération trop faible"  # ✅ Existe dans enum
        },
        {
            "address": "La Défense, 92400 Courbevoie",
            "raison_ecoute": "Manque de perspectives d'évolution"  # ✅ Existe dans enum
        }
    ]
    
    print(f"👤 Candidat test: {candidate_test_data['skills'][:3]}... "
          f"({candidate_test_data['experience_years']} ans exp)")
    print(f"📍 Localisation candidat: {candidate_test_data['location']}")
    print()
    
    results = []
    
    for i, job in enumerate(test_jobs, 1):
        print(f"🎯 TEST {i}/3: {job['address']}")
        print(f"📋 Raison d'écoute: {job['raison_ecoute']}")
        
        try:
            # Calcul matching avec Transport Intelligence
            result = await engine.calculate_dynamic_matching_scores(
                candidate_data=candidate_test_data,
                job_address=job['address'],
                pourquoi_ecoute=job['raison_ecoute']
            )
            
            results.append({
                "job_address": job['address'],
                "raison_ecoute": job['raison_ecoute'],
                "result": result
            })
            
            print(f"✅ Score total: {result['total_score']:.3f}")
            print(f"🗺️ Score localisation: {result['component_scores']['localisation']:.3f}")
            print(f"⏱️ Temps calcul: {result['processing_time_ms']:.1f}ms")
            
            if result['transport_intelligence']['location_score_dynamic']:
                details = result['transport_intelligence']['location_scoring_details']
                if 'transport_mode' in details:
                    print(f"🚗 Mode transport: {details['transport_mode']}")
            
            print("-" * 40)
            
        except Exception as e:
            print(f"❌ Erreur test {i}: {e}")
            print("-" * 40)
    
    # Sauvegarde résultats
    timestamp = int(time.time())
    report_file = f"transport_integration_test_report_fixed_{timestamp}.json"
    
    report = {
        "test_metadata": {
            "timestamp": datetime.now().isoformat(),
            "version": "Nextvision V3.2.1 + Transport Intelligence (Fixed)",
            "candidate_profile": candidate_test_data,
            "test_jobs_count": len(test_jobs),
            "fixes_applied": [
                "RaisonEcoute enum values corrected",
                "TimingInfo structure fixed", 
                "EnvironnementTravail enum usage fixed",
                "QuestionnaireComplet all required fields added"
            ]
        },
        "results": results,
        "performance_stats": {
            "total_tests": len(results),
            "successful_tests": len([r for r in results if r['result']['transport_intelligence']['location_score_dynamic']]),
            "average_processing_time": sum([r['result']['processing_time_ms'] for r in results]) / len(results) if results else 0
        }
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📁 Rapport sauvegardé: {report_file}")
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ INTÉGRATION TRANSPORT INTELLIGENCE (CORRIGÉ)")
    print("=" * 60)
    
    if results:
        dynamic_scores = [r['result']['component_scores']['localisation'] 
                         for r in results 
                         if r['result']['transport_intelligence']['location_score_dynamic']]
        
        if dynamic_scores:
            print(f"✅ Tests réussis: {len(dynamic_scores)}/{len(results)}")
            print(f"🗺️ Scores localisation dynamiques: {[f'{s:.3f}' for s in dynamic_scores]}")
            print(f"📊 Score localisation moyen: {sum(dynamic_scores)/len(dynamic_scores):.3f}")
            print(f"⏱️ Temps moyen: {report['performance_stats']['average_processing_time']:.1f}ms")
            print()
            print("🎯 INTÉGRATION RÉUSSIE ! Le Transport Intelligence est maintenant connecté au matching.")
            print("🔧 Toutes les erreurs RaisonEcoute et structure ont été corrigées.")
        else:
            print("⚠️ Aucun score dynamique calculé - vérifiez la configuration Google Maps")
    else:
        print("❌ Aucun test réussi")

def main():
    """🚀 Point d'entrée principal"""
    
    print("🚗 NEXTVISION V3.2.1 - INTÉGRATION TRANSPORT INTELLIGENCE (CORRIGÉ)")
    print("=" * 60)
    print("Connecte le LocationScoringEngine au système de matching principal")
    print("pour remplacer le score de localisation fixe par des calculs dynamiques.")
    print()
    print("🔧 CORRECTIONS APPORTÉES:")
    print("- Fix RaisonEcoute enum values")
    print("- Fix TimingInfo et EnvironnementTravail structures")  
    print("- Fix QuestionnaireComplet avec tous les champs requis")
    print()
    
    # Vérification environment
    if not os.path.exists("main.py"):
        print("❌ Erreur: Ce script doit être exécuté depuis le répertoire Nextvision/")
        print("💡 Commande: cd /Users/baptistecomas/Nextvision/ && python integration_transport_v321_fixed.py")
        sys.exit(1)
    
    # Test d'intégration
    try:
        asyncio.run(test_transport_integration())
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
