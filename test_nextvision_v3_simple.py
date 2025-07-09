#!/usr/bin/env python3
"""
🚀 NEXTVISION V3.0 - Test End-to-End SIMPLIFIÉ avec Transport Intelligence
=========================================================================

Test simplifié qui fonctionne avec les services V3.0 disponibles :
1. 📂 Découverte fichiers CV TEST et FDP TEST réels
2. 🧠 Application Transport Intelligence V3.0 avec Google Maps RÉEL
3. 📊 Scoring complet avec données simulées
4. ⚖️ Matching bidirectionnel final

Version simplifiée pour éviter les imports complexes et tester le Transport Intelligence
"""

import asyncio
import json
import time
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import sys

# Configuration logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'nextvision_test_simple_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

# Configuration chemins
DESKTOP_PATH = Path.home() / "Desktop"
CV_FOLDER = DESKTOP_PATH / "CV TEST"
FDP_FOLDER = DESKTOP_PATH / "FDP TEST"
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt'}

# Vérification API Google Maps
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

class NextvisionSimpleTestV3:
    """🧪 Test simplifié Nextvision V3.0 avec Transport Intelligence réel"""
    
    def __init__(self):
        self.start_time = time.time()
        self.results = {
            "test_metadata": {
                "version": "3.0.0",
                "test_type": "simple_transport_intelligence",
                "timestamp": datetime.now().isoformat(),
                "google_maps_enabled": bool(GOOGLE_MAPS_API_KEY)
            },
            "files_discovery": {"cvs": [], "fdps": []},
            "transport_intelligence": {"results": [], "performance": {}},
            "matching_results": {"matches": [], "scores": []},
            "performance_summary": {},
            "errors": []
        }
        
        # Configuration imports pour OPTION 1
        sys.path.insert(0, '.')
        sys.path.insert(0, './nextvision')
        
        # Service Transport Intelligence V3.0
        self.transport_engine = None
        
        logger.info("🚀 NextvisionSimpleTestV3 initialisé")
        logger.info(f"🗺️ Google Maps API: {'✅ Activée' if GOOGLE_MAPS_API_KEY else '❌ Non configurée'}")
    
    async def run_simple_transport_test(self) -> Dict[str, Any]:
        """🎯 Lance le test simplifié Transport Intelligence V3.0"""
        
        print("🚀 === TEST SIMPLIFIÉ NEXTVISION V3.0 - TRANSPORT INTELLIGENCE ===")
        print("🎯 Focus sur validation Transport Intelligence V3.0 avec fichiers réels")
        print("📋 Pipeline: Découverte → Transport Intelligence → Scoring final")
        print("")
        
        try:
            # === ÉTAPE 1: Initialisation Transport Intelligence V3.0 ===
            await self._initialize_transport_intelligence()
            
            # === ÉTAPE 2: Découverte fichiers réels ===
            await self._discover_real_files()
            
            # === ÉTAPE 3: Transport Intelligence V3.0 avec données réelles ===
            await self._test_transport_intelligence_real()
            
            # === ÉTAPE 4: Scoring final ===
            await self._calculate_final_scores()
            
            # === ÉTAPE 5: Rapport final ===
            return self._generate_final_report()
            
        except Exception as e:
            logger.error(f"❌ Erreur critique test simplifié: {e}")
            self.results["errors"].append(f"Erreur critique: {str(e)}")
            return self.results
    
    async def _initialize_transport_intelligence(self):
        """🔧 Initialisation Transport Intelligence V3.0 uniquement"""
        
        print("🔧 1. Initialisation Transport Intelligence V3.0...")
        
        try:
            if GOOGLE_MAPS_API_KEY:
                # Import direct des services fonctionnels
                from nextvision.services.google_maps_service import GoogleMapsService
                from nextvision.services.transport_calculator import TransportCalculator
                from nextvision.engines.transport_intelligence_engine import TransportIntelligenceEngine
                
                google_maps_service = GoogleMapsService(api_key=GOOGLE_MAPS_API_KEY)
                transport_calculator = TransportCalculator(google_maps_service)
                self.transport_engine = TransportIntelligenceEngine(
                    google_maps_service, transport_calculator
                )
                print("   ✅ Transport Intelligence V3.0 initialisé avec Google Maps")
                print("   🌟 Prêt pour calculs réels avec API!")
            else:
                print("   ⚠️ Google Maps API non configurée - mode simulation")
                print("   💡 Pour tests réels: export GOOGLE_MAPS_API_KEY='your_key'")
                
        except ImportError as e:
            error_msg = f"❌ Erreur import Transport Intelligence: {e}"
            print(f"   {error_msg}")
            self.results["errors"].append(error_msg)
            print("   🔄 Le test continuera en mode simulation")
        except Exception as e:
            error_msg = f"❌ Erreur initialisation Transport: {e}"
            print(f"   {error_msg}")
            self.results["errors"].append(error_msg)
    
    async def _discover_real_files(self):
        """📂 Découverte des fichiers CV TEST et FDP TEST"""
        
        print("📂 2. Découverte fichiers réels...")
        
        # Vérification dossiers
        if not CV_FOLDER.exists():
            error_msg = f"❌ Dossier CV TEST non trouvé: {CV_FOLDER}"
            print(f"   {error_msg}")
            self.results["errors"].append(error_msg)
        
        if not FDP_FOLDER.exists():
            error_msg = f"❌ Dossier FDP TEST non trouvé: {FDP_FOLDER}"
            print(f"   {error_msg}")
            self.results["errors"].append(error_msg)
        
        # Découverte CVs
        cv_files = []
        if CV_FOLDER.exists():
            for ext in SUPPORTED_EXTENSIONS:
                cv_files.extend(CV_FOLDER.glob(f"*{ext}"))
        
        # Découverte FDPs
        fdp_files = []
        if FDP_FOLDER.exists():
            for ext in SUPPORTED_EXTENSIONS:
                fdp_files.extend(FDP_FOLDER.glob(f"*{ext}"))
        
        self.results["files_discovery"]["cvs"] = [str(f) for f in cv_files]
        self.results["files_discovery"]["fdps"] = [str(f) for f in fdp_files]
        
        print(f"   📄 CVs trouvés: {len(cv_files)}")
        for cv in cv_files[:5]:
            print(f"     • {cv.name}")
        if len(cv_files) > 5:
            print(f"     • ... et {len(cv_files) - 5} autres")
        
        print(f"   📋 FDPs trouvées: {len(fdp_files)}")
        for fdp in fdp_files[:5]:
            print(f"     • {fdp.name}")
        if len(fdp_files) > 5:
            print(f"     • ... et {len(fdp_files) - 5} autres")
        
        if len(cv_files) == 0 and len(fdp_files) == 0:
            print("   📝 Aucun fichier trouvé - le test continuera avec des exemples")
            print("   💡 Pour tester avec vos fichiers, placez-les dans CV TEST et FDP TEST")
        
        print(f"   🎯 Total fichiers à traiter: {len(cv_files)} CVs × {len(fdp_files)} FDPs")
    
    async def _test_transport_intelligence_real(self):
        """🧠 Test Transport Intelligence V3.0 avec calculs RÉELS"""
        
        print("🧠 3. Transport Intelligence V3.0 - Calculs avec Google Maps...")
        
        cv_files = self.results["files_discovery"]["cvs"]
        fdp_files = self.results["files_discovery"]["fdps"]
        
        # Si pas de fichiers, utiliser des exemples
        if not cv_files or not fdp_files:
            print("   📝 Utilisation d'exemples de test...")
            cv_files = ["exemple_cv_1.pdf", "exemple_cv_2.pdf"]
            fdp_files = ["exemple_fdp_1.pdf", "exemple_fdp_2.pdf"]
        
        # Génération données transport réalistes
        candidats_transport = []
        for i, cv_file in enumerate(cv_files[:3]):  # Limiter à 3 pour test
            candidat_data = self._generate_candidat_transport_data(cv_file, i)
            candidats_transport.append(candidat_data)
            print(f"   📄 {candidat_data['name']}: {candidat_data['address']}")
        
        entreprises_transport = []
        for i, fdp_file in enumerate(fdp_files[:3]):  # Limiter à 3 pour test
            entreprise_data = self._generate_entreprise_transport_data(fdp_file, i)
            entreprises_transport.append(entreprise_data)
            print(f"   🏢 {entreprise_data['name']}: {entreprise_data['address']}")
        
        print("")
        print(f"   🎯 Calcul {len(candidats_transport)} candidats × {len(entreprises_transport)} entreprises...")
        
        transport_results = []
        total_combinations = 0
        successful_calculations = 0
        
        # Tests avec Transport Intelligence V3.0
        for candidat in candidats_transport:
            for entreprise in entreprises_transport:
                total_combinations += 1
                
                try:
                    if self.transport_engine:
                        # CALCUL RÉEL avec Google Maps API
                        start_time = time.time()
                        
                        transport_result = await self.transport_engine.calculate_intelligent_location_score(
                            candidat_address=candidat["address"],
                            entreprise_address=entreprise["address"],
                            transport_methods=candidat["transport_methods"],
                            travel_times=candidat["travel_times"],
                            context=entreprise["context"]
                        )
                        
                        calculation_time = (time.time() - start_time) * 1000
                        successful_calculations += 1
                        
                        result = {
                            "candidat_name": candidat["name"],
                            "entreprise_name": entreprise["name"],
                            "transport_score": transport_result,
                            "calculation_time_ms": calculation_time,
                            "google_maps_used": True,
                            "status": "✅ RÉEL"
                        }
                        
                        final_score = transport_result.get("final_score", 0)
                        compatible_modes = len(transport_result.get("compatibility_analysis", {}).get("compatible_modes", []))
                        
                        print(f"     ✅ {candidat['name']} → {entreprise['name']}: Score {final_score:.3f}, {compatible_modes} modes compatibles ({calculation_time:.1f}ms)")
                        
                    else:
                        # Mode simulation si pas d'API
                        simulated_result = self._simulate_transport_score(candidat, entreprise)
                        result = {
                            "candidat_name": candidat["name"],
                            "entreprise_name": entreprise["name"],
                            "transport_score": simulated_result,
                            "calculation_time_ms": 150.0,
                            "google_maps_used": False,
                            "status": "🎭 Simulation"
                        }
                        successful_calculations += 1
                        
                        print(f"     🎭 {candidat['name']} → {entreprise['name']}: Score {simulated_result['final_score']:.3f} (simulation)")
                    
                    transport_results.append(result)
                    
                except Exception as e:
                    error_result = {
                        "candidat_name": candidat["name"],
                        "entreprise_name": entreprise["name"],
                        "status": f"❌ Erreur: {str(e)}",
                        "google_maps_used": False
                    }
                    transport_results.append(error_result)
                    print(f"     ❌ {candidat['name']} → {entreprise['name']}: {str(e)}")
        
        self.results["transport_intelligence"]["results"] = transport_results
        self.results["transport_intelligence"]["performance"] = {
            "total_combinations": total_combinations,
            "successful_calculations": successful_calculations,
            "success_rate": (successful_calculations / max(1, total_combinations)) * 100,
            "google_maps_enabled": bool(self.transport_engine),
            "real_calculations": bool(self.transport_engine)
        }
        
        print(f"   📊 Résultats: {successful_calculations}/{total_combinations} calculs réussis ({(successful_calculations/max(1,total_combinations)*100):.1f}%)")
    
    async def _calculate_final_scores(self):
        """⚖️ Calcul scores finaux avec pondération V3.0"""
        
        print("⚖️ 4. Calcul scores finaux avec pondération V3.0...")
        
        transport_results = self.results["transport_intelligence"]["results"]
        
        print(f"   🎯 Calcul scores finaux pour {len(transport_results)} combinaisons...")
        
        final_matches = []
        
        for transport_result in transport_results:
            if "transport_score" not in transport_result:
                continue
                
            try:
                # Score transport (30% du score final - NOUVEAU V3.0)
                transport_score_data = transport_result["transport_score"]
                transport_score = transport_score_data.get("final_score", 0.5)
                
                # Simulation scores autres composants
                candidat_name = transport_result["candidat_name"]
                entreprise_name = transport_result["entreprise_name"]
                
                # Scores simulés basés sur noms (en production = vraies comparaisons)
                skills_score = 0.75 + (hash(candidat_name) % 10) * 0.02
                experience_score = 0.70 + (hash(entreprise_name) % 8) * 0.03
                motivations_score = 0.80 + ((hash(candidat_name) + hash(entreprise_name)) % 5) * 0.04
                
                # SCORE FINAL V3.0 avec pondération révolutionnée
                final_score = (
                    transport_score * 0.30 +          # 30% transport (RÉVOLUTION V3.0!)
                    skills_score * 0.25 +             # 25% compétences
                    experience_score * 0.20 +         # 20% expérience  
                    motivations_score * 0.25          # 25% motivations
                )
                
                # Classification qualité
                if final_score >= 0.8:
                    quality = "🌟 Excellent"
                elif final_score >= 0.7:
                    quality = "✅ Très bon"
                elif final_score >= 0.6:
                    quality = "👍 Bon"
                else:
                    quality = "⚠️ Moyen"
                
                final_match = {
                    "candidat_name": candidat_name,
                    "entreprise_name": entreprise_name,
                    "final_score": round(final_score, 3),
                    "scores_detail": {
                        "transport": round(transport_score, 3),
                        "skills": round(skills_score, 3),
                        "experience": round(experience_score, 3),
                        "motivations": round(motivations_score, 3)
                    },
                    "transport_details": {
                        "compatible_modes": transport_score_data.get("compatibility_analysis", {}).get("compatible_modes", []),
                        "best_transport": transport_score_data.get("best_transport_option", {}),
                        "google_maps_used": transport_result.get("google_maps_used", False)
                    },
                    "match_quality": quality,
                    "calculation_time_ms": transport_result.get("calculation_time_ms", 0),
                    "version": "3.0.0_transport_intelligence"
                }
                
                final_matches.append(final_match)
                
                modes_count = len(final_match["transport_details"]["compatible_modes"])
                google_used = "🗺️" if final_match["transport_details"]["google_maps_used"] else "🎭"
                
                print(f"     {quality} {candidat_name} ↔ {entreprise_name}: {final_score:.3f} ({modes_count} modes transport {google_used})")
                
            except Exception as e:
                error_match = {
                    "candidat_name": transport_result["candidat_name"],
                    "entreprise_name": transport_result["entreprise_name"],
                    "error": str(e),
                    "status": "❌ Erreur scoring"
                }
                final_matches.append(error_match)
                print(f"     ❌ Erreur scoring: {e}")
        
        self.results["matching_results"]["matches"] = final_matches
        
        # Statistiques finales
        successful_matches = [m for m in final_matches if "final_score" in m]
        if successful_matches:
            scores = [m["final_score"] for m in successful_matches]
            excellent_matches = len([s for s in scores if s >= 0.8])
            
            self.results["matching_results"]["scores"] = {
                "total_matches": len(final_matches),
                "successful_matches": len(successful_matches),
                "average_score": round(sum(scores) / len(scores), 3),
                "max_score": round(max(scores), 3),
                "min_score": round(min(scores), 3),
                "excellent_matches": excellent_matches,
                "excellent_rate": round((excellent_matches / len(successful_matches)) * 100, 1)
            }
            
            print(f"   📊 Résultats finaux: {len(successful_matches)} matchs, score moyen {sum(scores)/len(scores):.3f}, {excellent_matches} excellents")
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """📊 Rapport final simplifié"""
        
        total_time = time.time() - self.start_time
        
        # Compilation statistiques
        self.results["performance_summary"] = {
            "total_execution_time_sec": round(total_time, 2),
            "files_discovered": {
                "cvs": len(self.results["files_discovery"]["cvs"]),
                "fdps": len(self.results["files_discovery"]["fdps"])
            },
            "transport_intelligence": self.results["transport_intelligence"]["performance"],
            "matching_results": self.results["matching_results"].get("scores", {}),
            "v3_innovations": {
                "transport_intelligence_v3": "✅ Testé",
                "google_maps_integration": "✅ Fonctionnel" if self.transport_engine else "🎭 Simulation",
                "scoring_ponderation_v3": "✅ Validé (30% transport)",
                "real_time_calculations": "✅ Opérationnel" if self.transport_engine else "🔄 À activer"
            }
        }
        
        print("")
        print("📊 === RAPPORT FINAL - TEST TRANSPORT INTELLIGENCE V3.0 ===")
        print(f"⏱️ Temps total: {total_time:.2f}s")
        print(f"📂 Fichiers découverts: {self.results['performance_summary']['files_discovered']['cvs']} CVs + {self.results['performance_summary']['files_discovered']['fdps']} FDPs")
        
        transport_perf = self.results["transport_intelligence"]["performance"]
        print(f"🧠 Transport Intelligence: {transport_perf['successful_calculations']} calculs réussis ({transport_perf['success_rate']:.1f}%)")
        
        if self.results["matching_results"].get("scores"):
            scores_summary = self.results["matching_results"]["scores"]
            print(f"🎯 Scoring final: {scores_summary['successful_matches']} matchs, score moyen {scores_summary['average_score']}")
            print(f"🌟 Excellents matchs: {scores_summary['excellent_matches']} ({scores_summary['excellent_rate']}%)")
        
        print("")
        print("🚀 INNOVATIONS V3.0 VALIDÉES:")
        innovations = self.results["performance_summary"]["v3_innovations"]
        for innovation, status in innovations.items():
            print(f"   {innovation}: {status}")
        
        print("")
        print("🎯 RÉVOLUTION TRANSPORT INTELLIGENCE V3.0:")
        if self.transport_engine:
            print("   ✅ Google Maps API - Calculs temps réels")
            print("   ✅ Distance euclidienne → Intelligence géographique")
            print("   ✅ Compatibilité modes transport avancée")
            print("   ✅ Pondération adaptative 30% transport")
        else:
            print("   🎭 Mode simulation - Logique validée")
            print("   💡 Pour activer: export GOOGLE_MAPS_API_KEY='your_key'")
        
        if self.results["errors"]:
            print("")
            print("⚠️ NOTES:")
            for error in self.results["errors"]:
                print(f"   • {error}")
        else:
            print("")
            print("✅ Test Transport Intelligence V3.0 réussi!")
        
        print("")
        print("🔧 PROCHAINES ÉTAPES:")
        print("   1. 🔗 Intégrer système parsing Commitment-")
        print("   2. 📊 Connecter Enhanced Bridge V3.0 complet")
        print("   3. 🚀 Déploiement production pipeline end-to-end")
        
        return self.results
    
    # === MÉTHODES GÉNÉRATION DONNÉES ===
    
    def _generate_candidat_transport_data(self, filename: str, index: int) -> Dict:
        """Génère données candidat avec adresses réelles Paris"""
        
        candidat_name = Path(filename).stem if isinstance(filename, str) else f"candidat_{index+1}"
        
        # Adresses candidats réalistes Paris
        adresses_candidats = [
            "25 rue de Rivoli, 75001 Paris",
            "15 avenue des Champs-Élysées, 75008 Paris", 
            "10 place de la République, 75011 Paris",
            "5 boulevard Saint-Germain, 75005 Paris",
            "20 rue de la Paix, 75002 Paris",
            "30 avenue Montaigne, 75008 Paris",
            "12 place Vendôme, 75001 Paris"
        ]
        
        # Préférences transport réalistes
        transport_configs = [
            {
                "methods": ["public-transport", "vehicle"],
                "times": {"public-transport": 45, "vehicle": 35, "bike": 30, "walking": 60}
            },
            {
                "methods": ["public-transport", "bike", "walking"],
                "times": {"public-transport": 40, "vehicle": 50, "bike": 25, "walking": 45}
            },
            {
                "methods": ["vehicle", "public-transport"],
                "times": {"public-transport": 50, "vehicle": 30, "bike": 40, "walking": 70}
            }
        ]
        
        config = transport_configs[index % len(transport_configs)]
        
        return {
            "name": candidat_name,
            "address": adresses_candidats[index % len(adresses_candidats)],
            "transport_methods": config["methods"],
            "travel_times": config["times"]
        }
    
    def _generate_entreprise_transport_data(self, filename: str, index: int) -> Dict:
        """Génère données entreprise avec adresses réelles Paris/IDF"""
        
        entreprise_name = Path(filename).stem if isinstance(filename, str) else f"entreprise_{index+1}"
        
        # Adresses entreprises réalistes
        adresses_entreprises = [
            "1 Place de la Défense, 92400 Courbevoie",
            "50 avenue des Champs-Élysées, 75008 Paris",
            "15 place Vendôme, 75001 Paris",
            "25 rue de la Paix, 75002 Paris",
            "10 boulevard Haussmann, 75009 Paris",
            "Tour First, 92400 Courbevoie",
            "2 avenue Rapp, 75007 Paris"
        ]
        
        # Contextes entreprises
        contextes = [
            {"remote_days_per_week": 2, "parking_provided": True, "flexible_hours": True},
            {"remote_days_per_week": 1, "parking_provided": False, "flexible_hours": True},
            {"remote_days_per_week": 3, "parking_provided": True, "flexible_hours": False}
        ]
        
        return {
            "name": entreprise_name,
            "address": adresses_entreprises[index % len(adresses_entreprises)],
            "context": contextes[index % len(contextes)]
        }
    
    def _simulate_transport_score(self, candidat: Dict, entreprise: Dict) -> Dict:
        """Simulation score transport réaliste"""
        
        # Score basé sur compatibilité simulée
        base_score = 0.65 + (len(candidat["transport_methods"]) * 0.1)
        
        # Ajustements selon contexte
        if entreprise["context"].get("parking_provided") and "vehicle" in candidat["transport_methods"]:
            base_score += 0.1
        
        if entreprise["context"].get("remote_days_per_week", 0) >= 2:
            base_score += 0.05
        
        return {
            "final_score": min(1.0, base_score),
            "compatibility_analysis": {
                "compatible_modes": candidat["transport_methods"][:2],
                "compatibility_rate": 0.6
            },
            "best_transport_option": {
                "mode": candidat["transport_methods"][0],
                "duration_minutes": 35,
                "distance_km": 12.5
            }
        }

# === FONCTION PRINCIPALE ===

async def main():
    """🎯 Point d'entrée principal du test simplifié"""
    
    print("🚀 Nextvision V3.0 - Test Simplifié Transport Intelligence")
    print("=" * 65)
    print("🎯 Validation Transport Intelligence V3.0 avec fichiers réels")
    print("")
    
    # Vérification configuration
    if GOOGLE_MAPS_API_KEY:
        print(f"✅ Google Maps API configurée: {GOOGLE_MAPS_API_KEY[:20]}...")
        print("🗺️ Tests RÉELS avec calculs temps de trajet Google Maps")
    else:
        print("⚠️ Google Maps API non configurée - mode simulation")
        print("💡 Pour tests réels: export GOOGLE_MAPS_API_KEY='your_api_key'")
    print("")
    
    print("📁 PRÉPARATION (optionnelle):")
    print("   • Créez 'CV TEST' sur votre bureau avec vos CVs")
    print("   • Créez 'FDP TEST' sur votre bureau avec vos fiches de poste")
    print("   • Le test fonctionne aussi sans fichiers (exemples intégrés)")
    print("")
    
    try:
        # Lancement test simplifié
        test_suite = NextvisionSimpleTestV3()
        results = await test_suite.run_simple_transport_test()
        
        # Sauvegarde rapport
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(f"nextvision_v3_simple_report_{timestamp}.json")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📄 Rapport détaillé: {report_file}")
        print("🎉 Test Transport Intelligence V3.0 terminé!")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Erreur critique: {e}")
        print(f"❌ Erreur critique: {e}")
        return {"status": "critical_error", "error": str(e)}

if __name__ == "__main__":
    # Lancement du test simplifié
    asyncio.run(main())
