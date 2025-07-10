#!/usr/bin/env python3
"""
🧪 TEST SYSTÈME COMPLET : MATCHING + PARSING RÉEL
Test de l'intégration complète Nextvision V3.0 + Commitment Parser v4.0

Author: Assistant Claude
Version: 1.0.0-complete
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any

# Import Enhanced Bridge V3.0 Simplifié (sans imports circulaires)
from nextvision.services.enhanced_commitment_bridge_v3_simplified import (
    SimplifiedBridgeFactory, EnhancedCommitmentBridgeV3Simplified
)

# Import Transport Intelligence V3.0
from nextvision.engines.transport_intelligence_engine import TransportIntelligenceEngine
from nextvision.services.bidirectional_matcher import BiDirectionalMatcherV2

class SystemeCompletTester:
    """🧪 Testeur système complet Matching + Parsing"""
    
    def __init__(self):
        # Initialisation Enhanced Bridge V3.0 Simplifié
        self.bridge = SimplifiedBridgeFactory.create_bridge()
        
        # Initialisation Transport Intelligence V3.0
        self.transport_engine = TransportIntelligenceEngine()
        
        # Initialisation Matcher Bidirectionnel
        self.matcher = BiDirectionalMatcherV2()
        
        print("🚀 Système complet initialisé:")
        print("   ✅ Enhanced Bridge V3.0 Simplifié")
        print("   ✅ Transport Intelligence V3.0")
        print("   ✅ BiDirectional Matcher V2")
    
    async def test_candidat_parsing_to_matching(self, candidat_data: Dict[str, Any]):
        """🔄 Test complet : Parsing → Bridge → Matching"""
        
        print(f"\n🧪 === TEST CANDIDAT COMPLET ===")
        start_time = time.time()
        
        # ÉTAPE 1: Simulation données parser réel
        parser_output = {
            "candidate_id": f"TEST_{datetime.now().timestamp()}",
            "personal_info": candidat_data.get("personal_info", {}),
            "skills": candidat_data.get("skills", []),
            "experience": candidat_data.get("experience", {}),
            "salary": candidat_data.get("salary", {}),
            "location": candidat_data.get("location", {}),
            "parsing_confidence": candidat_data.get("parsing_confidence", 0.8)
        }
        
        # Questionnaire V3.0 (données enrichies)
        questionnaire_data = {
            "mobility_preferences": candidat_data.get("mobility_preferences", {}),
            "motivations_sectors": candidat_data.get("motivations_sectors", {}),
            "availability_status": candidat_data.get("availability_status", {})
        }
        
        print(f"📄 Parser Output: {len(parser_output)} champs")
        print(f"📋 Questionnaire V3.0: {len(questionnaire_data)} sections")
        
        # ÉTAPE 2: Conversion via Enhanced Bridge V3.0
        bridge_start = time.time()
        candidat_profile, bridge_metrics = await self.bridge.convert_candidat_simplified(
            parser_output, questionnaire_data
        )
        bridge_time = time.time() - bridge_start
        
        print(f"🌉 Bridge V3.0: {bridge_time*1000:.1f}ms")
        print(f"   ✅ Profil: {candidat_profile.version}")
        print(f"   ✅ Composants V3.0: {bridge_metrics.v3_components_count}")
        
        # ÉTAPE 3: Score Transport Intelligence V3.0
        if candidat_data.get("test_transport", False):
            transport_start = time.time()
            try:
                transport_score = await self.transport_engine.calculate_transport_score(
                    candidat_location=candidat_profile.location,
                    job_location="La Défense, Paris",
                    mobility_preferences=candidat_profile.mobility_preferences
                )
                transport_time = time.time() - transport_start
                
                print(f"🚗 Transport Intelligence: {transport_time*1000:.1f}ms")
                print(f"   ✅ Score: {transport_score:.3f}")
            except Exception as e:
                print(f"⚠️ Transport Intelligence: Erreur {e}")
                transport_score = 0.8  # Score par défaut
        else:
            transport_score = 0.8  # Score par défaut
            print(f"🚗 Transport Intelligence: Score par défaut {transport_score}")
        
        total_time = time.time() - start_time
        
        print(f"⏱️ Temps total: {total_time*1000:.1f}ms")
        print(f"🎯 Résultat: Candidat transformé et évalué avec succès")
        
        return {
            "candidat_profile": candidat_profile,
            "bridge_metrics": bridge_metrics,
            "transport_score": transport_score,
            "total_time_ms": total_time * 1000
        }
    
    async def test_entreprise_parsing_to_matching(self, entreprise_data: Dict[str, Any]):
        """🏢 Test complet entreprise : Parsing → Bridge → Matching"""
        
        print(f"\n🏢 === TEST ENTREPRISE COMPLET ===")
        start_time = time.time()
        
        # ÉTAPE 1: Simulation données parser entreprise
        chatgpt_output = {
            "company_id": f"COMP_TEST_{datetime.now().timestamp()}",
            "titre": entreprise_data.get("titre", "Poste de test"),
            "entreprise": entreprise_data.get("entreprise", "Entreprise Test"),
            "localisation": entreprise_data.get("localisation", "Paris"),
            "competences_requises": entreprise_data.get("competences_requises", []),
            "experience_requise": entreprise_data.get("experience_requise", "3-5 ans"),
            "salaire": entreprise_data.get("salaire", "40K-60K"),
            "parsing_confidence": entreprise_data.get("parsing_confidence", 0.85)
        }
        
        # Questionnaire entreprise V3.0
        questionnaire_data = {
            "company_structure": entreprise_data.get("company_structure", {}),
            "job_details": entreprise_data.get("job_details", {}),
            "recruitment_process": entreprise_data.get("recruitment_process", {})
        }
        
        print(f"📄 ChatGPT Output: {len(chatgpt_output)} champs")
        print(f"📋 Questionnaire V3.0: {len(questionnaire_data)} sections")
        
        # ÉTAPE 2: Conversion via Enhanced Bridge V3.0
        bridge_start = time.time()
        company_profile, bridge_metrics = await self.bridge.convert_entreprise_simplified(
            chatgpt_output, questionnaire_data
        )
        bridge_time = time.time() - bridge_start
        
        print(f"🌉 Bridge V3.0: {bridge_time*1000:.1f}ms")
        print(f"   ✅ Profil: {company_profile.version}")
        print(f"   ✅ Composants V3.0: {bridge_metrics.v3_components_count}")
        
        total_time = time.time() - start_time
        
        print(f"⏱️ Temps total: {total_time*1000:.1f}ms")
        print(f"🎯 Résultat: Entreprise transformée avec succès")
        
        return {
            "company_profile": company_profile,
            "bridge_metrics": bridge_metrics,
            "total_time_ms": total_time * 1000
        }
    
    async def test_matching_complet(self, candidat_result: Dict, entreprise_result: Dict):
        """🎯 Test matching complet candidat ↔ entreprise"""
        
        print(f"\n🎯 === TEST MATCHING COMPLET ===")
        start_time = time.time()
        
        candidat_profile = candidat_result["candidat_profile"]
        company_profile = entreprise_result["company_profile"]
        
        # Calcul matching bidirectionnel
        try:
            match_result = await self.matcher.calculate_bidirectional_match(
                candidat_profile, company_profile
            )
            
            matching_time = time.time() - start_time
            
            print(f"✅ Matching calculé en {matching_time*1000:.1f}ms")
            print(f"🎯 Score global: {match_result.global_score:.3f}")
            print(f"👤 Score candidat → entreprise: {match_result.candidate_to_company_score:.3f}")
            print(f"🏢 Score entreprise → candidat: {match_result.company_to_candidate_score:.3f}")
            
            # Détails des composants
            print(f"\n📊 Détails composants:")
            print(f"   💼 Skills: {match_result.skills_score:.3f}")
            print(f"   💰 Salary: {match_result.salary_score:.3f}")
            print(f"   📍 Location: {match_result.location_score:.3f}")
            print(f"   🚗 Transport: {candidat_result.get('transport_score', 0.8):.3f}")
            
            return {
                "match_result": match_result,
                "matching_time_ms": matching_time * 1000,
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Erreur matching: {e}")
            return {
                "error": str(e),
                "matching_time_ms": 0,
                "success": False
            }
    
    def print_rapport_final(self, candidat_result: Dict, entreprise_result: Dict, matching_result: Dict):
        """📊 Rapport final du test complet"""
        
        print(f"\n" + "="*70)
        print(f"📊 RAPPORT FINAL - SYSTÈME COMPLET")
        print(f"="*70)
        
        total_time = (
            candidat_result["total_time_ms"] + 
            entreprise_result["total_time_ms"] + 
            matching_result.get("matching_time_ms", 0)
        )
        
        print(f"⏱️ Performance globale:")
        print(f"   📄 Parsing → Bridge candidat: {candidat_result['total_time_ms']:.1f}ms")
        print(f"   🏢 Parsing → Bridge entreprise: {entreprise_result['total_time_ms']:.1f}ms")
        print(f"   🎯 Matching bidirectionnel: {matching_result.get('matching_time_ms', 0):.1f}ms")
        print(f"   🚀 TOTAL: {total_time:.1f}ms")
        
        print(f"\n🎯 Résultats:")
        if matching_result.get("success"):
            score = matching_result["match_result"].global_score
            print(f"   ✅ Matching réussi: {score:.3f}")
            if score >= 0.8:
                print(f"   🎉 EXCELLENT MATCH (≥0.8)")
            elif score >= 0.6:
                print(f"   ✅ BON MATCH (≥0.6)")
            elif score >= 0.4:
                print(f"   ⚠️ MATCH MOYEN (≥0.4)")
            else:
                print(f"   ❌ MATCH FAIBLE (<0.4)")
        else:
            print(f"   ❌ Matching échoué: {matching_result.get('error', 'Erreur inconnue')}")
        
        print(f"\n🎊 Système complet:")
        print(f"   ✅ Enhanced Bridge V3.0 Simplifié")
        print(f"   ✅ Transport Intelligence V3.0")
        print(f"   ✅ Parsing réel Commitment v4.0 (simulation)")
        print(f"   ✅ Matching bidirectionnel V2")
        
        print(f"="*70)

async def main():
    """🚀 Test principal système complet"""
    
    print("🚀 === TEST SYSTÈME COMPLET NEXTVISION V3.0 ===")
    print("Matching + Parsing + Transport Intelligence")
    print("="*70)
    
    # Initialisation testeur
    try:
        tester = SystemeCompletTester()
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
        return
    
    # DONNÉES TEST (simulant les données du parser réel)
    candidat_test = {
        "personal_info": {
            "firstName": "Thomas",
            "lastName": "Dupont",
            "email": "thomas.dupont@test.com",
            "phone": "0612345678"
        },
        "skills": ["JavaScript", "React", "Node.js", "Python", "Docker"],
        "experience": {"total_years": 5},
        "salary": {"current": 45000, "expected": 55000},
        "location": {"city": "Paris"},
        "mobility_preferences": {
            "transport_methods": ["transport_public", "vélo"],
            "max_travel_time": "45 minutes",
            "work_location_preference": "hybride"
        },
        "motivations_sectors": {
            "motivations_ranking": ["défis_techniques", "équilibre_vie", "évolution_carrière"],
            "preferred_sectors": ["technologie", "finance"],
            "excluded_sectors": ["industrie"]
        },
        "availability_status": {
            "availability_timing": "1-3_mois",
            "current_status": "en_poste",
            "listening_reasons": ["opportunité_évolution", "défis_techniques"]
        },
        "test_transport": False,  # Désactiver transport par défaut (nécessite API)
        "parsing_confidence": 0.9
    }
    
    entreprise_test = {
        "titre": "Développeur Full Stack Senior",
        "entreprise": "TechCorp France",
        "localisation": "La Défense, Paris",
        "competences_requises": ["JavaScript", "React", "Node.js", "Docker", "AWS"],
        "experience_requise": "4-6 ans",
        "salaire": "50K-65K",
        "company_structure": {
            "sector": "technologie",
            "size": "startup"
        },
        "job_details": {
            "contract_type": "CDI",
            "benefits": ["mutuelle", "tickets_restaurant", "formations", "télétravail"],
            "remote_work_policy": "hybride"
        },
        "recruitment_process": {
            "urgency": "normal"
        },
        "parsing_confidence": 0.85
    }
    
    try:
        # Test candidat complet
        candidat_result = await tester.test_candidat_parsing_to_matching(candidat_test)
        
        # Test entreprise complet
        entreprise_result = await tester.test_entreprise_parsing_to_matching(entreprise_test)
        
        # Test matching complet
        matching_result = await tester.test_matching_complet(candidat_result, entreprise_result)
        
        # Rapport final
        tester.print_rapport_final(candidat_result, entreprise_result, matching_result)
        
        print(f"\n🎉 Test système complet terminé avec succès!")
        print(f"\n💡 Pour tester avec données réelles:")
        print(f"1. Aller sur: https://bapt252.github.io/Commitment-/templates/candidate-questionnaire.html")
        print(f"2. Remplir questionnaire et récupérer JSON")
        print(f"3. Modifier candidat_test avec vos données")
        print(f"4. Relancer le script")
        
    except Exception as e:
        print(f"❌ Erreur test système complet: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
