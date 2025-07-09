#!/usr/bin/env python3
"""
🚀 Demo Transport Intelligence V3.0 - Script de test simple
Usage: python demo_transport_intelligence.py

PROMPT 5 - Test du système révolutionné avec adresses réelles Paris
"""

import asyncio
import os
import logging
from typing import Dict, Any

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def demo_transport_intelligence_v3():
    """🧪 Démonstration Transport Intelligence V3.0"""
    
    print("🚀 DEMO TRANSPORT INTELLIGENCE V3.0 - NEXTVISION")
    print("=" * 60)
    
    # Check si clé API Google Maps disponible
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    if not google_maps_api_key:
        print("⚠️  DEMO MODE - SIMULATION")
        print("   Pour tests réels, définissez GOOGLE_MAPS_API_KEY")
        print("   export GOOGLE_MAPS_API_KEY='your_api_key_here'")
        print()
        
        # Simulation résultats pour démonstration
        await demo_simulation_mode()
        return
    
    try:
        # Import des services (vérification disponibilité)
        print("🔧 Initialisation services Transport Intelligence...")
        
        # NOTE: Adaptez ces imports selon votre structure exacte
        from nextvision.services.google_maps_service import GoogleMapsService
        from nextvision.services.transport_calculator import TransportCalculator  
        from nextvision.engines.transport_intelligence_engine import TransportIntelligenceEngine
        
        # Initialisation
        google_maps_service = GoogleMapsService(api_key=google_maps_api_key)
        transport_calculator = TransportCalculator(google_maps_service)
        engine = TransportIntelligenceEngine(google_maps_service, transport_calculator)
        
        print("✅ Services initialisés avec succès")
        print()
        
        # Test scénario réel Paris
        await demo_real_paris_scenario(engine)
        
        # Tests batch
        await demo_batch_processing(engine)
        
        # Tests validation Paris
        await demo_paris_validation(engine)
        
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        print("💡 Vérifiez que tous les modules sont dans le PYTHONPATH")
        await demo_simulation_mode()
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
        await demo_simulation_mode()

async def demo_simulation_mode():
    """🎭 Mode simulation pour démonstration sans API"""
    
    print("🎭 MODE SIMULATION - Démonstration fonctionnalités")
    print()
    
    # Simulation données d'entrée
    candidat_address = "25 avenue des Champs-Élysées, 75008 Paris"
    entreprise_address = "1 Place de la Défense, 92400 Courbevoie"
    transport_methods = ["public-transport", "vehicle", "bike", "walking"]
    travel_times = {
        "public-transport": 30,
        "vehicle": 25, 
        "bike": 20,
        "walking": 15
    }
    context = {
        "remote_days_per_week": 2,
        "parking_provided": True,
        "flexible_hours": True
    }
    
    print(f"📍 SCÉNARIO TEST:")
    print(f"   Candidat: {candidat_address}")
    print(f"   Entreprise: {entreprise_address}")
    print(f"   Modes transport: {transport_methods}")
    print(f"   Temps acceptés: {travel_times}")
    print(f"   Contexte: {context}")
    print()
    
    # Simulation résultat Transport Intelligence V3.0
    simulated_result = {
        "final_score": 0.842,
        "compatibility_analysis": {
            "compatible_modes": ["public-transport", "vehicle"],
            "incompatible_modes": ["bike", "walking"],
            "compatibility_rate": 0.5,
            "compatibility_details": {
                "public-transport": {
                    "actual_time_minutes": 28,
                    "time_limit_minutes": 30,
                    "is_compatible": True,
                    "time_efficiency": 1.07
                },
                "vehicle": {
                    "actual_time_minutes": 22,
                    "time_limit_minutes": 25,
                    "is_compatible": True,
                    "time_efficiency": 1.14
                },
                "bike": {
                    "actual_time_minutes": 45,
                    "time_limit_minutes": 20,
                    "is_compatible": False,
                    "time_efficiency": 0.44
                },
                "walking": {
                    "actual_time_minutes": 78,
                    "time_limit_minutes": 15,
                    "is_compatible": False,
                    "time_efficiency": 0.19
                }
            }
        },
        "best_transport_option": {
            "mode": "public-transport",
            "duration_minutes": 28,
            "distance_km": 12.3,
            "has_traffic_delays": False
        },
        "score_breakdown": {
            "final_score": 0.842,
            "time_compatibility_score": 0.50,
            "flexibility_bonus": 0.15,
            "efficiency_score": 0.89,
            "reliability_score": 0.85
        },
        "explanations": [
            "🎯 Score transport: 0.84/1.0 (2/4 modes compatibles)",
            "✅ public-transport: 28min ≤ 30min (efficacité: 107%)",
            "✅ vehicle: 22min ≤ 25min (efficacité: 114%)",
            "❌ bike: 45min > 20min",
            "❌ walking: 78min > 15min",
            "🔄 Bonus flexibilité: +15% (×1.15 pour 2 modes)",
            "🌟 Recommandé: public-transport"
        ],
        "recommendations": [
            "✅ Bonne compatibilité transport - candidat viable",
            "🔄 Candidate flexible - plusieurs options transport",
            "🏠 Télétravail 2j/semaine peut compenser trajets"
        ],
        "version": "3.0.0-simulation",
        "scorer": "LocationTransportScorerV3"
    }
    
    print("🚀 RÉSULTAT TRANSPORT INTELLIGENCE V3.0:")
    print(f"   📊 Score final: {simulated_result['final_score']:.3f}/1.0")
    print(f"   ✅ Modes compatibles: {simulated_result['compatibility_analysis']['compatible_modes']}")
    print(f"   🌟 Meilleure option: {simulated_result['best_transport_option']['mode']}")
    print(f"   ⏱️  Durée recommandée: {simulated_result['best_transport_option']['duration_minutes']}min")
    print()
    
    print("📝 EXPLICATIONS DÉTAILLÉES:")
    for explanation in simulated_result['explanations']:
        print(f"   {explanation}")
    print()
    
    print("💡 RECOMMANDATIONS:")
    for recommendation in simulated_result['recommendations']:
        print(f"   {recommendation}")
    print()
    
    print("🔧 ARCHITECTURE V3.0 RÉVOLUTIONNÉE:")
    print("   ✅ LocationTransportScorerV3 (NOUVEAU)")
    print("   ✅ TransportIntelligenceEngine (NOUVEAU)")
    print("   ✅ Intégration GoogleMapsService (EXPLOITÉ)")
    print("   ✅ Cache intelligent + fallbacks")
    print("   ✅ Support nouvelles données questionnaire")
    print()

async def demo_real_paris_scenario(engine):
    """🗺️ Test scénario réel Paris avec API Google Maps"""
    
    print("🗺️ TEST SCÉNARIO RÉEL PARIS")
    print()
    
    try:
        result = await engine.calculate_intelligent_location_score(
            candidat_address="25 avenue des Champs-Élysées, 75008 Paris",
            entreprise_address="1 Place de la Défense, 92400 Courbevoie",
            transport_methods=["public-transport", "vehicle", "bike", "walking"],
            travel_times={"public-transport": 30, "vehicle": 25, "bike": 20, "walking": 15},
            context={"remote_days_per_week": 2, "parking_provided": True}
        )
        
        print(f"✅ Score calculé: {result['final_score']:.3f}")
        print(f"   Modes compatibles: {result['compatibility_analysis']['compatible_modes']}")
        print(f"   Meilleure option: {result['best_transport_option']['mode']}")
        print()
        
    except Exception as e:
        print(f"❌ Erreur test réel: {e}")
        print()

async def demo_batch_processing(engine):
    """🚀 Démonstration batch processing"""
    
    print("🚀 TEST BATCH PROCESSING")
    print()
    
    jobs_data = [
        {
            "address": "Place de l'Opéra, 75009 Paris",
            "transport_methods": ["public-transport", "vehicle"],
            "travel_times": {"public-transport": 30, "vehicle": 25},
            "context": {"parking_provided": False}
        },
        {
            "address": "Gare de Lyon, 75012 Paris",
            "transport_methods": ["public-transport", "bike", "walking"],
            "travel_times": {"public-transport": 40, "bike": 20, "walking": 45},
            "context": {"flexible_hours": True}
        }
    ]
    
    try:
        batch_results = await engine.batch_calculate_intelligent_scores(
            candidat_address="Place de la République, 75011 Paris",
            jobs_data=jobs_data
        )
        
        print("✅ Batch processing terminé:")
        for job_address, score_data in batch_results["scores"].items():
            print(f"   {job_address}: {score_data['final_score']:.3f}")
        print()
        
    except Exception as e:
        print(f"❌ Erreur batch: {e}")
        print()

async def demo_paris_validation(engine):
    """🧪 Démonstration tests validation Paris"""
    
    print("🧪 TESTS VALIDATION PARIS")
    print()
    
    try:
        # Tests intégrés dans l'engine
        test_results = await engine.run_paris_validation_tests()
        
        summary = test_results["summary"]
        success_rate = summary["successful_tests"] / summary["total_tests"] * 100
        
        print(f"✅ Tests validation terminés:")
        print(f"   Tests exécutés: {summary['total_tests']}")
        print(f"   Taux succès: {success_rate:.1f}%")
        print(f"   Score moyen: {summary['average_score']:.3f}")
        print()
        
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
        print()

def main():
    """🎯 Point d'entrée principal"""
    
    try:
        asyncio.run(demo_transport_intelligence_v3())
    except KeyboardInterrupt:
        print("\n👋 Demo interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur demo: {e}")
    
    print("\n🎉 Fin de la démonstration Transport Intelligence V3.0")
    print("📋 Voir documentation: nextvision/docs/TRANSPORT_INTELLIGENCE_V3_DOCUMENTATION.md")

if __name__ == "__main__":
    main()
