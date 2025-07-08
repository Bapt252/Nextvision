#!/usr/bin/env python3
"""Test Enhanced Bridge v2.0 avec Fichiers Réels CV et FDP"""

import asyncio
import aiohttp
import json
import time
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://localhost:8000"
DESKTOP_PATH = Path.home() / "Desktop"
CV_FOLDER = DESKTOP_PATH / "CV TEST"
FDP_FOLDER = DESKTOP_PATH / "FDP TEST"

# Extensions de fichiers supportées
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt'}

class RealFilesTestSuite:
    """🧪 Suite de tests avec fichiers réels CV et FDP"""
    
    def __init__(self):
        self.session = None
        self.results = {
            "files_discovered": {"cvs": [], "fdps": []},
            "parsing_simulated": {"cvs": [], "fdps": []},
            "enhanced_conversions": {"cvs": [], "fdps": []},
            "performance_summary": {},
            "errors": []
        }
        self.start_time = time.time()
    
    async def run_real_files_test(self) -> Dict[str, Any]:
        """🚀 Lance le test complet avec fichiers réels"""
        print("🧪 === TEST ENHANCED BRIDGE v2.0 - FICHIERS RÉELS ===")
        print("📁 Analyse des dossiers CV TEST et FDP TEST")
        print("")
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            try:
                # 1. Découverte des fichiers
                await self._discover_files()
                
                # 2. Simulation parsing (Enhanced Universal Parser v4.0 + ChatGPT)
                await self._simulate_parsing()
                
                # 3. Test conversions Enhanced Bridge
                await self._test_enhanced_conversions()
                
                # 4. Génération rapport final
                return self._generate_final_report()
                
            except Exception as e:
                logger.error(f"❌ Erreur critique: {e}")
                self.results["errors"].append(f"Erreur critique: {str(e)}")
                return self.results
    
    async def _discover_files(self):
        """📁 Découverte des fichiers CV et FDP"""
        print("📁 1. Découverte des fichiers...")
        
        # Vérification dossiers
        if not CV_FOLDER.exists():
            error_msg = f"❌ Dossier CV TEST non trouvé: {CV_FOLDER}"
            print(error_msg)
            self.results["errors"].append(error_msg)
        
        if not FDP_FOLDER.exists():
            error_msg = f"❌ Dossier FDP TEST non trouvé: {FDP_FOLDER}"
            print(error_msg)
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
        
        self.results["files_discovered"]["cvs"] = [str(f) for f in cv_files]
        self.results["files_discovered"]["fdps"] = [str(f) for f in fdp_files]
        
        print(f"  📄 CVs trouvés: {len(cv_files)}")
        for cv in cv_files[:5]:  # Afficher les 5 premiers
            print(f"    • {cv.name}")
        if len(cv_files) > 5:
            print(f"    • ... et {len(cv_files) - 5} autres")
        
        print(f"  📋 FDPs trouvées: {len(fdp_files)}")
        for fdp in fdp_files[:5]:  # Afficher les 5 premiers
            print(f"    • {fdp.name}")
        if len(fdp_files) > 5:
            print(f"    • ... et {len(fdp_files) - 5} autres")
        
        if len(cv_files) == 0 and len(fdp_files) == 0:
            error_msg = "❌ Aucun fichier trouvé dans CV TEST ou FDP TEST"
            print(error_msg)
            self.results["errors"].append(error_msg)
    
    async def _simulate_parsing(self):
        """🔄 Simulation du parsing Enhanced Universal Parser v4.0 + ChatGPT"""
        print("🔄 2. Simulation parsing des fichiers...")
        
        cv_files = self.results["files_discovered"]["cvs"]
        fdp_files = self.results["files_discovered"]["fdps"]
        
        # Simulation parsing CVs (Enhanced Universal Parser v4.0)
        print(f"  🤖 Simulation parsing {len(cv_files)} CVs...")
        for i, cv_path in enumerate(cv_files[:10]):  # Limiter à 10 pour le test
            cv_name = Path(cv_path).name
            
            # Simulation données Enhanced Universal Parser v4.0
            simulated_cv = self._generate_simulated_cv_data(cv_name, i)
            self.results["parsing_simulated"]["cvs"].append({
                "file_path": cv_path,
                "file_name": cv_name,
                "parsed_data": simulated_cv,
                "parsing_confidence": simulated_cv["parsing_confidence"]
            })
            
            print(f"    ✅ {cv_name} → Confiance: {simulated_cv['parsing_confidence']:.2f}")
        
        # Simulation parsing FDPs (ChatGPT)
        print(f"  🧠 Simulation parsing {len(fdp_files)} FDPs...")
        for i, fdp_path in enumerate(fdp_files[:10]):  # Limiter à 10 pour le test
            fdp_name = Path(fdp_path).name
            
            # Simulation données ChatGPT
            simulated_fdp = self._generate_simulated_fdp_data(fdp_name, i)
            self.results["parsing_simulated"]["fdps"].append({
                "file_path": fdp_path,
                "file_name": fdp_name,
                "parsed_data": simulated_fdp,
                "parsing_confidence": simulated_fdp["parsing_confidence"]
            })
            
            print(f"    ✅ {fdp_name} → Confiance: {simulated_fdp['parsing_confidence']:.2f}")
    
    async def _test_enhanced_conversions(self):
        """🔧 Test conversions Enhanced Bridge"""
        print("🔧 3. Test conversions Enhanced Bridge...")
        
        # Test conversion CVs
        cvs_parsed = self.results["parsing_simulated"]["cvs"]
        for cv_data in cvs_parsed[:5]:  # Tester les 5 premiers
            try:
                start_time = time.time()
                
                payload = {
                    "candidat_data": cv_data["parsed_data"],
                    "candidat_questionnaire": {
                        "raison_ecoute": "Recherche nouveau défi",
                        "salary_min": 35000,
                        "salary_max": 55000,
                        "preferred_location": "Paris"
                    }
                }
                
                async with self.session.post(
                    f"{API_BASE_URL}/api/v2/conversion/commitment/enhanced",
                    json=payload
                ) as resp:
                    processing_time = (time.time() - start_time) * 1000
                    
                    if resp.status == 200:
                        result = await resp.json()
                        metrics = result.get("performance_metrics", {}).get("candidat", {})
                        
                        conversion_result = {
                            "file_name": cv_data["file_name"],
                            "status": "✅ Success",
                            "processing_time_ms": processing_time,
                            "auto_fixes": metrics.get("auto_fixes_count", 0),
                            "conversion_success": True
                        }
                        
                        print(f"    ✅ {cv_data['file_name']}: {processing_time:.2f}ms, {metrics.get('auto_fixes_count', 0)} auto-fixes")
                        
                    else:
                        conversion_result = {
                            "file_name": cv_data["file_name"],
                            "status": f"❌ Error {resp.status}",
                            "conversion_success": False
                        }
                        print(f"    ❌ {cv_data['file_name']}: Error {resp.status}")
                
                self.results["enhanced_conversions"]["cvs"].append(conversion_result)
                
            except Exception as e:
                error_result = {
                    "file_name": cv_data["file_name"],
                    "status": f"❌ Exception: {str(e)}",
                    "conversion_success": False
                }
                self.results["enhanced_conversions"]["cvs"].append(error_result)
                print(f"    ❌ {cv_data['file_name']}: Exception {e}")
    
    def _generate_simulated_cv_data(self, file_name: str, index: int) -> Dict:
        """Génère données CV simulées basées sur le nom de fichier"""
        # Extraction patterns du nom de fichier
        name_lower = file_name.lower()
        
        # Simulation basique basée sur patterns
        if "marie" in name_lower or "martin" in name_lower:
            firstName = "Marie" if "marie" in name_lower else "Martin"
            lastName = "Dupont"
            skills = ["Comptabilité", "CEGID", "Excel", "Gestion"]
            experience_years = 5 + (index % 8)
        elif "jean" in name_lower or "dev" in name_lower or "tech" in name_lower:
            firstName = "Jean"
            lastName = "Durand"
            skills = ["Python", "JavaScript", "React", "FastAPI"]
            experience_years = 3 + (index % 6)
        else:
            firstName = f"Candidat{index + 1}"
            lastName = "Test"
            skills = ["Communication", "Microsoft Office", "Gestion de projet"]
            experience_years = 2 + (index % 10)
        
        return {
            "personal_info": {
                "firstName": firstName,
                "lastName": lastName,
                "email": f"{firstName.lower()}.{lastName.lower()}@email.com",
                "phone": f"+33 6 {20 + index:02d} {30 + index:02d} {40 + index:02d} {50 + index:02d}"
            },
            "skills": skills,
            "softwares": ["Excel", "Word", "Outlook"],
            "languages": {"Français": "Natif", "Anglais": "Courant"},
            "experience": {"total_years": experience_years},
            "work_experience": [
                {
                    "position": f"Poste Senior {index + 1}",
                    "company": f"Entreprise {index + 1}",
                    "duration": f"{experience_years // 2} ans",
                    "skills_acquired": skills[:2]
                }
            ],
            "parsing_confidence": 0.85 + (index % 3) * 0.05
        }
    
    def _generate_simulated_fdp_data(self, file_name: str, index: int) -> Dict:
        """Génère données FDP simulées basées sur le nom de fichier"""
        name_lower = file_name.lower()
        
        # Simulation basique basée sur patterns
        if "comptable" in name_lower or "compta" in name_lower:
            titre = "Comptable Senior H/F"
            competences = ["Maîtrise CEGID", "Comptabilité générale", "Fiscalité"]
            salaire = "38K à 45K annuels"
            experience = "5 ans - 8 ans"
        elif "dev" in name_lower or "tech" in name_lower or "info" in name_lower:
            titre = "Développeur Full-Stack Senior"
            competences = ["Python", "React", "FastAPI", "Docker"]
            salaire = "45K à 60K annuels"
            experience = "3 ans - 7 ans"
        else:
            titre = f"Poste {index + 1} H/F"
            competences = ["Compétence 1", "Compétence 2", "Compétence 3"]
            salaire = f"{30 + index * 2}K à {35 + index * 3}K annuels"
            experience = f"{2 + index % 5} ans - {5 + index % 8} ans"
        
        return {
            "titre": titre,
            "localisation": f"Paris {8 + (index % 12)}ème",
            "contrat": "CDI",
            "salaire": salaire,
            "competences_requises": competences,
            "experience_requise": experience,
            "missions": [
                f"Mission principale {index + 1}",
                f"Responsabilité {index + 1}",
                f"Objectif {index + 1}"
            ],
            "avantages": ["Tickets restaurant", "Mutuelle", "RTT"],
            "badges_auto_rempli": ["Auto-rempli"],
            "fiche_poste_originale": f"Fiche de poste détaillée pour {titre}...",
            "parsing_confidence": 0.80 + (index % 4) * 0.05
        }
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """📊 Génère le rapport final"""
        total_time = time.time() - self.start_time
        
        # Calcul statistiques
        cvs_found = len(self.results["files_discovered"]["cvs"])
        fdps_found = len(self.results["files_discovered"]["fdps"])
        cvs_converted = len([c for c in self.results["enhanced_conversions"]["cvs"] if c.get("conversion_success")])
        
        self.results["performance_summary"] = {
            "total_execution_time_sec": round(total_time, 2),
            "files_discovered": {
                "cvs": cvs_found,
                "fdps": fdps_found,
                "total": cvs_found + fdps_found
            },
            "conversions_enhanced": {
                "cvs_successful": cvs_converted,
                "total_successful": cvs_converted
            }
        }
        
        print("")
        print("📊 === RAPPORT FINAL - FICHIERS RÉELS ===")
        print(f"⏱️ Temps total: {total_time:.2f}s")
        print(f"📁 Fichiers découverts: {cvs_found} CVs + {fdps_found} FDPs")
        print(f"🔧 Conversions Enhanced: {cvs_converted} succès")
        print("")
        
        if self.results["errors"]:
            print("⚠️ ERREURS DÉTECTÉES:")
            for error in self.results["errors"]:
                print(f"  • {error}")
        else:
            print("✅ Aucune erreur critique détectée")
        
        return self.results

async def main():
    """🚀 Point d'entrée principal"""
    test_suite = RealFilesTestSuite()
    
    try:
        # Vérification API disponible
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/v1/health") as resp:
                if resp.status != 200:
                    print(f"❌ API Nextvision non disponible sur {API_BASE_URL}")
                    print("   Assurez-vous que l'API tourne avec: python main_v2_enhanced.py")
                    return
        
        # Lancement tests
        results = await test_suite.run_real_files_test()
        
        # Sauvegarde rapport
        report_file = Path(f"enhanced_bridge_real_files_report_{int(time.time())}.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📄 Rapport sauvegardé: {report_file}")
        
        return results
        
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        return {"status": "critical_error", "error": str(e)}

if __name__ == "__main__":
    # Lancement des tests avec fichiers réels
    asyncio.run(main())
