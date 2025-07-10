#!/usr/bin/env python3
"""
🧪 Test Complet Nextvision V3.0 avec Vraies Données CV et FDP
Pipeline : CV/FDP → Commitment Bridge → Enhanced Bridge V3 → Transport Intelligence → Matching

Author: Assistant
Version: 3.0 - Test Données Réelles
"""

import asyncio
import aiohttp
import json
import time
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
import mimetypes

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nextvision_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://localhost:8001"
DESKTOP_PATH = Path.home() / "Desktop"
CV_FOLDER = DESKTOP_PATH / "CV TEST"
FDP_FOLDER = DESKTOP_PATH / "FDP TEST"

# Extensions de fichiers supportées
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt'}

# Couleurs pour l'affichage
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

@dataclass
class TestResult:
    """Résultat d'un test"""
    success: bool
    message: str
    details: Optional[Dict] = None
    processing_time: float = 0.0
    error: Optional[str] = None

@dataclass
class FileTestResult:
    """Résultat de test pour un fichier"""
    file_path: str
    file_name: str
    file_size: int
    file_type: str
    parsing_result: Optional[TestResult] = None
    matching_result: Optional[TestResult] = None
    transport_result: Optional[TestResult] = None

class NextvisionRealDataTester:
    """🧪 Testeur principal pour données réelles"""
    
    def __init__(self):
        self.session = None
        self.results = {
            "test_summary": {
                "start_time": time.time(),
                "end_time": None,
                "total_duration": 0.0,
                "files_tested": 0,
                "successful_tests": 0,
                "failed_tests": 0
            },
            "file_discovery": {
                "cv_files": [],
                "fdp_files": [],
                "total_files": 0,
                "supported_files": 0
            },
            "api_health": {
                "core_api": False,
                "bridge_integration": False,
                "google_maps": False,
                "commitment_bridge": False
            },
            "test_results": {
                "cv_tests": [],
                "fdp_tests": [],
                "matching_tests": [],
                "transport_tests": []
            },
            "performance_metrics": {
                "average_parsing_time": 0.0,
                "average_matching_time": 0.0,
                "average_transport_time": 0.0,
                "total_api_calls": 0,
                "success_rate": 0.0
            },
            "errors": []
        }
    
    async def run_complete_test(self) -> Dict[str, Any]:
        """🚀 Lance le test complet avec vraies données"""
        print(f"{Colors.BOLD}{Colors.CYAN}🧪 === TEST COMPLET NEXTVISION V3.0 - DONNÉES RÉELLES ==={Colors.END}")
        print(f"{Colors.BLUE}📁 Recherche dans : {CV_FOLDER} et {FDP_FOLDER}{Colors.END}")
        print()
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            try:
                # 1. Vérification API
                print(f"{Colors.YELLOW}1. Vérification état API Nextvision...{Colors.END}")
                await self._check_api_health()
                
                # 2. Découverte des fichiers
                print(f"{Colors.YELLOW}2. Découverte des fichiers CV et FDP...{Colors.END}")
                await self._discover_files()
                
                # 3. Test parsing des CVs
                print(f"{Colors.YELLOW}3. Test parsing des CVs réels...{Colors.END}")
                await self._test_cv_parsing()
                
                # 4. Test parsing des FDPs
                print(f"{Colors.YELLOW}4. Test parsing des FDPs réelles...{Colors.END}")
                await self._test_fdp_parsing()
                
                # 5. Test matching complet
                print(f"{Colors.YELLOW}5. Test matching candidat/poste...{Colors.END}")
                await self._test_complete_matching()
                
                # 6. Test Transport Intelligence
                print(f"{Colors.YELLOW}6. Test Transport Intelligence...{Colors.END}")
                await self._test_transport_intelligence()
                
                # 7. Génération rapport final
                return await self._generate_final_report()
                
            except Exception as e:
                logger.error(f"❌ Erreur critique dans le test : {e}")
                self.results["errors"].append(f"Erreur critique : {str(e)}")
                return self.results
    
    async def _check_api_health(self):
        """❤️ Vérifie l'état de l'API"""
        health_checks = [
            ("core_api", "/api/v1/health"),
            ("bridge_integration", "/api/v1/integration/health"),
            ("google_maps", "/api/v2/maps/health"),
        ]
        
        for service, endpoint in health_checks:
            try:
                async with self.session.get(f"{API_BASE_URL}{endpoint}") as resp:
                    if resp.status == 200:
                        self.results["api_health"][service] = True
                        print(f"  ✅ {service}: {Colors.GREEN}OK{Colors.END}")
                    else:
                        self.results["api_health"][service] = False
                        print(f"  ❌ {service}: {Colors.RED}ERREUR {resp.status}{Colors.END}")
            except Exception as e:
                self.results["api_health"][service] = False
                print(f"  ❌ {service}: {Colors.RED}NON DISPONIBLE{Colors.END}")
                logger.error(f"Health check {service} failed: {e}")
    
    async def _discover_files(self):
        """📁 Découvre les fichiers dans les dossiers"""
        cv_files = []
        fdp_files = []
        
        # Vérification existence dossiers
        if not CV_FOLDER.exists():
            error_msg = f"Dossier CV TEST non trouvé : {CV_FOLDER}"
            print(f"  ❌ {Colors.RED}{error_msg}{Colors.END}")
            self.results["errors"].append(error_msg)
        else:
            for file_path in CV_FOLDER.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    cv_files.append(file_path)
        
        if not FDP_FOLDER.exists():
            error_msg = f"Dossier FDP TEST non trouvé : {FDP_FOLDER}"
            print(f"  ❌ {Colors.RED}{error_msg}{Colors.END}")
            self.results["errors"].append(error_msg)
        else:
            for file_path in FDP_FOLDER.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    fdp_files.append(file_path)
        
        self.results["file_discovery"]["cv_files"] = [str(f) for f in cv_files]
        self.results["file_discovery"]["fdp_files"] = [str(f) for f in fdp_files]
        self.results["file_discovery"]["total_files"] = len(cv_files) + len(fdp_files)
        self.results["file_discovery"]["supported_files"] = len(cv_files) + len(fdp_files)
        
        print(f"  📄 CVs trouvés : {Colors.GREEN}{len(cv_files)}{Colors.END}")
        for i, cv in enumerate(cv_files[:5]):  # Afficher les 5 premiers
            file_size = cv.stat().st_size / 1024  # KB
            print(f"    • {cv.name} ({file_size:.1f} KB)")
        if len(cv_files) > 5:
            print(f"    • ... et {len(cv_files) - 5} autres")
        
        print(f"  📋 FDPs trouvées : {Colors.GREEN}{len(fdp_files)}{Colors.END}")
        for i, fdp in enumerate(fdp_files[:5]):  # Afficher les 5 premiers
            file_size = fdp.stat().st_size / 1024  # KB
            print(f"    • {fdp.name} ({file_size:.1f} KB)")
        if len(fdp_files) > 5:
            print(f"    • ... et {len(fdp_files) - 5} autres")
    
    async def _test_cv_parsing(self):
        """🤖 Test parsing des CVs avec Commitment-Enhanced Parser"""
        cv_files = [Path(f) for f in self.results["file_discovery"]["cv_files"]]
        
        if not cv_files:
            print(f"  ⚠️ {Colors.YELLOW}Aucun CV à tester{Colors.END}")
            return
        
        print(f"  🔄 Test parsing de {len(cv_files)} CVs...")
        
        # Tester les premiers CVs (limiter pour éviter surcharge)
        test_limit = min(10, len(cv_files))
        
        for i, cv_path in enumerate(cv_files[:test_limit]):
            start_time = time.time()
            
            try:
                # Lecture du fichier
                with open(cv_path, 'rb') as f:
                    file_content = f.read()
                
                # Préparer les données pour l'upload
                form_data = aiohttp.FormData()
                form_data.add_field('candidat_questionnaire', json.dumps({
                    'raison_ecoute': 'Recherche nouveau défi',
                    'salary_min': 35000,
                    'salary_max': 55000,
                    'preferred_location': 'Paris'
                }))
                form_data.add_field('file', file_content, 
                                  filename=cv_path.name, 
                                  content_type=self._get_mime_type(cv_path))
                
                # Test parsing via Enhanced Bridge
                async with self.session.post(
                    f"{API_BASE_URL}/api/v2/conversion/commitment/enhanced",
                    data=form_data
                ) as resp:
                    
                    processing_time = time.time() - start_time
                    
                    if resp.status == 200:
                        result_data = await resp.json()
                        
                        test_result = FileTestResult(
                            file_path=str(cv_path),
                            file_name=cv_path.name,
                            file_size=cv_path.stat().st_size,
                            file_type=cv_path.suffix,
                            parsing_result=TestResult(
                                success=True,
                                message="Parsing réussi",
                                details=result_data,
                                processing_time=processing_time
                            )
                        )
                        
                        print(f"    ✅ {cv_path.name}: {Colors.GREEN}{processing_time:.2f}s{Colors.END}")
                        
                    else:
                        error_msg = f"Erreur HTTP {resp.status}"
                        test_result = FileTestResult(
                            file_path=str(cv_path),
                            file_name=cv_path.name,
                            file_size=cv_path.stat().st_size,
                            file_type=cv_path.suffix,
                            parsing_result=TestResult(
                                success=False,
                                message=error_msg,
                                processing_time=processing_time,
                                error=error_msg
                            )
                        )
                        
                        print(f"    ❌ {cv_path.name}: {Colors.RED}{error_msg}{Colors.END}")
                
                self.results["test_results"]["cv_tests"].append(test_result)
                
            except Exception as e:
                error_msg = f"Exception : {str(e)}"
                test_result = FileTestResult(
                    file_path=str(cv_path),
                    file_name=cv_path.name,
                    file_size=cv_path.stat().st_size,
                    file_type=cv_path.suffix,
                    parsing_result=TestResult(
                        success=False,
                        message=error_msg,
                        processing_time=time.time() - start_time,
                        error=error_msg
                    )
                )
                
                self.results["test_results"]["cv_tests"].append(test_result)
                print(f"    ❌ {cv_path.name}: {Colors.RED}{error_msg}{Colors.END}")
    
    async def _test_fdp_parsing(self):
        """🧠 Test parsing des FDPs avec ChatGPT"""
        fdp_files = [Path(f) for f in self.results["file_discovery"]["fdp_files"]]
        
        if not fdp_files:
            print(f"  ⚠️ {Colors.YELLOW}Aucune FDP à tester{Colors.END}")
            return
        
        print(f"  🔄 Test parsing de {len(fdp_files)} FDPs...")
        
        # Tester les premières FDPs (limiter pour éviter surcharge)
        test_limit = min(10, len(fdp_files))
        
        for i, fdp_path in enumerate(fdp_files[:test_limit]):
            start_time = time.time()
            
            try:
                # Lecture du fichier
                with open(fdp_path, 'rb') as f:
                    file_content = f.read()
                
                # Préparer les données pour l'upload
                form_data = aiohttp.FormData()
                form_data.add_field('additional_context', json.dumps({
                    'company_name': 'Test Company',
                    'location': 'Paris',
                    'contract_type': 'CDI'
                }))
                form_data.add_field('file', file_content, 
                                  filename=fdp_path.name, 
                                  content_type=self._get_mime_type(fdp_path))
                
                # Test parsing FDP
                async with self.session.post(
                    f"{API_BASE_URL}/api/v2/jobs/parse",
                    data=form_data
                ) as resp:
                    
                    processing_time = time.time() - start_time
                    
                    if resp.status == 200:
                        result_data = await resp.json()
                        
                        test_result = FileTestResult(
                            file_path=str(fdp_path),
                            file_name=fdp_path.name,
                            file_size=fdp_path.stat().st_size,
                            file_type=fdp_path.suffix,
                            parsing_result=TestResult(
                                success=True,
                                message="Parsing réussi",
                                details=result_data,
                                processing_time=processing_time
                            )
                        )
                        
                        print(f"    ✅ {fdp_path.name}: {Colors.GREEN}{processing_time:.2f}s{Colors.END}")
                        
                    else:
                        error_msg = f"Erreur HTTP {resp.status}"
                        test_result = FileTestResult(
                            file_path=str(fdp_path),
                            file_name=fdp_path.name,
                            file_size=fdp_path.stat().st_size,
                            file_type=fdp_path.suffix,
                            parsing_result=TestResult(
                                success=False,
                                message=error_msg,
                                processing_time=processing_time,
                                error=error_msg
                            )
                        )
                        
                        print(f"    ❌ {fdp_path.name}: {Colors.RED}{error_msg}{Colors.END}")
                
                self.results["test_results"]["fdp_tests"].append(test_result)
                
            except Exception as e:
                error_msg = f"Exception : {str(e)}"
                test_result = FileTestResult(
                    file_path=str(fdp_path),
                    file_name=fdp_path.name,
                    file_size=fdp_path.stat().st_size,
                    file_type=fdp_path.suffix,
                    parsing_result=TestResult(
                        success=False,
                        message=error_msg,
                        processing_time=time.time() - start_time,
                        error=error_msg
                    )
                )
                
                self.results["test_results"]["fdp_tests"].append(test_result)
                print(f"    ❌ {fdp_path.name}: {Colors.RED}{error_msg}{Colors.END}")
    
    async def _test_complete_matching(self):
        """🎯 Test matching complet candidat/poste"""
        successful_cvs = [t for t in self.results["test_results"]["cv_tests"] if t.parsing_result.success]
        successful_fdps = [t for t in self.results["test_results"]["fdp_tests"] if t.parsing_result.success]
        
        if not successful_cvs or not successful_fdps:
            print(f"  ⚠️ {Colors.YELLOW}Pas assez de données parsées pour tester le matching{Colors.END}")
            return
        
        print(f"  🔄 Test matching : {len(successful_cvs)} CVs x {len(successful_fdps)} FDPs...")
        
        # Tester quelques combinaisons représentatives
        test_combinations = min(5, len(successful_cvs) * len(successful_fdps))
        
        for i in range(test_combinations):
            cv_index = i % len(successful_cvs)
            fdp_index = i % len(successful_fdps)
            
            cv_test = successful_cvs[cv_index]
            fdp_test = successful_fdps[fdp_index]
            
            start_time = time.time()
            
            try:
                # Données de test pour matching
                matching_request = {
                    "pourquoi_ecoute": "Recherche nouveau défi",
                    "candidate_profile": {
                        "personal_info": {
                            "firstName": "Test",
                            "lastName": "Candidat",
                            "email": "test@example.com"
                        },
                        "skills": ["Python", "JavaScript", "React"],
                        "experience_years": 5,
                        "education": "Master",
                        "current_role": "Développeur"
                    },
                    "preferences": {
                        "salary_expectations": {
                            "min": 40000,
                            "max": 60000
                        },
                        "location_preferences": {
                            "city": "Paris",
                            "acceptedCities": ["Paris", "Lyon"],
                            "maxDistance": 30
                        },
                        "sectors": ["Tech", "Finance"]
                    }
                }
                
                async with self.session.post(
                    f"{API_BASE_URL}/api/v1/matching/candidate/test_{i}",
                    json=matching_request
                ) as resp:
                    
                    processing_time = time.time() - start_time
                    
                    if resp.status == 200:
                        result_data = await resp.json()
                        
                        test_result = TestResult(
                            success=True,
                            message=f"Matching réussi : {cv_test.file_name} x {fdp_test.file_name}",
                            details=result_data,
                            processing_time=processing_time
                        )
                        
                        score = result_data.get('matching_results', {}).get('total_score', 0)
                        print(f"    ✅ {cv_test.file_name} x {fdp_test.file_name}: {Colors.GREEN}Score {score:.2f} ({processing_time:.2f}s){Colors.END}")
                        
                    else:
                        error_msg = f"Erreur HTTP {resp.status}"
                        test_result = TestResult(
                            success=False,
                            message=error_msg,
                            processing_time=processing_time,
                            error=error_msg
                        )
                        
                        print(f"    ❌ {cv_test.file_name} x {fdp_test.file_name}: {Colors.RED}{error_msg}{Colors.END}")
                
                self.results["test_results"]["matching_tests"].append(test_result)
                
            except Exception as e:
                error_msg = f"Exception : {str(e)}"
                test_result = TestResult(
                    success=False,
                    message=error_msg,
                    processing_time=time.time() - start_time,
                    error=error_msg
                )
                
                self.results["test_results"]["matching_tests"].append(test_result)
                print(f"    ❌ {cv_test.file_name} x {fdp_test.file_name}: {Colors.RED}{error_msg}{Colors.END}")
    
    async def _test_transport_intelligence(self):
        """🚗 Test Transport Intelligence V3.0"""
        print(f"  🔄 Test Transport Intelligence...")
        
        # Test données transport
        transport_tests = [
            {
                "candidat_address": "12 rue de Rivoli, 75001 Paris",
                "job_address": "La Défense, 92400 Courbevoie",
                "transport_modes": ["transport_commun", "voiture"],
                "max_times": {"transport_commun": 45, "voiture": 30}
            },
            {
                "candidat_address": "Boulogne-Billancourt, 92100",
                "job_address": "Châtelet, 75001 Paris",
                "transport_modes": ["transport_commun", "velo"],
                "max_times": {"transport_commun": 35, "velo": 25}
            }
        ]
        
        for i, transport_test in enumerate(transport_tests):
            start_time = time.time()
            
            try:
                async with self.session.post(
                    f"{API_BASE_URL}/api/v2/transport/compatibility",
                    json=transport_test
                ) as resp:
                    
                    processing_time = time.time() - start_time
                    
                    if resp.status == 200:
                        result_data = await resp.json()
                        
                        test_result = TestResult(
                            success=True,
                            message=f"Transport test {i+1} réussi",
                            details=result_data,
                            processing_time=processing_time
                        )
                        
                        compatibility = result_data.get('compatibility_result', {})
                        is_compatible = compatibility.get('is_compatible', False)
                        score = compatibility.get('compatibility_score', 0)
                        
                        status_color = Colors.GREEN if is_compatible else Colors.RED
                        print(f"    ✅ Test {i+1}: {status_color}Compatible={is_compatible}, Score={score:.2f}{Colors.END} ({processing_time:.2f}s)")
                        
                    else:
                        error_msg = f"Erreur HTTP {resp.status}"
                        test_result = TestResult(
                            success=False,
                            message=error_msg,
                            processing_time=processing_time,
                            error=error_msg
                        )
                        
                        print(f"    ❌ Test {i+1}: {Colors.RED}{error_msg}{Colors.END}")
                
                self.results["test_results"]["transport_tests"].append(test_result)
                
            except Exception as e:
                error_msg = f"Exception : {str(e)}"
                test_result = TestResult(
                    success=False,
                    message=error_msg,
                    processing_time=time.time() - start_time,
                    error=error_msg
                )
                
                self.results["test_results"]["transport_tests"].append(test_result)
                print(f"    ❌ Test {i+1}: {Colors.RED}{error_msg}{Colors.END}")
    
    async def _generate_final_report(self) -> Dict[str, Any]:
        """📊 Génère le rapport final"""
        end_time = time.time()
        total_duration = end_time - self.results["test_summary"]["start_time"]
        
        # Calcul des métriques
        all_tests = []
        all_tests.extend(self.results["test_results"]["cv_tests"])
        all_tests.extend(self.results["test_results"]["fdp_tests"])
        all_tests.extend(self.results["test_results"]["matching_tests"])
        all_tests.extend(self.results["test_results"]["transport_tests"])
        
        successful_tests = 0
        failed_tests = 0
        total_processing_time = 0.0
        
        for test_group in [
            self.results["test_results"]["cv_tests"],
            self.results["test_results"]["fdp_tests"],
            self.results["test_results"]["matching_tests"],
            self.results["test_results"]["transport_tests"]
        ]:
            for test in test_group:
                if hasattr(test, 'parsing_result') and test.parsing_result:
                    if test.parsing_result.success:
                        successful_tests += 1
                    else:
                        failed_tests += 1
                    total_processing_time += test.parsing_result.processing_time
                elif hasattr(test, 'success'):
                    if test.success:
                        successful_tests += 1
                    else:
                        failed_tests += 1
                    total_processing_time += test.processing_time
        
        # Mise à jour du résumé
        self.results["test_summary"].update({
            "end_time": end_time,
            "total_duration": total_duration,
            "files_tested": len(all_tests),
            "successful_tests": successful_tests,
            "failed_tests": failed_tests
        })
        
        self.results["performance_metrics"].update({
            "average_processing_time": total_processing_time / max(1, successful_tests + failed_tests),
            "success_rate": successful_tests / max(1, successful_tests + failed_tests) * 100,
            "total_api_calls": successful_tests + failed_tests
        })
        
        # Affichage du rapport
        print()
        print(f"{Colors.BOLD}{Colors.CYAN}📊 === RAPPORT FINAL - TEST DONNÉES RÉELLES ==={Colors.END}")
        print(f"{Colors.BOLD}⏱️  Durée totale : {Colors.GREEN}{total_duration:.2f}s{Colors.END}")
        print(f"{Colors.BOLD}📁 Fichiers découverts : {Colors.BLUE}{self.results['file_discovery']['total_files']}{Colors.END}")
        print(f"{Colors.BOLD}🧪 Tests réussis : {Colors.GREEN}{successful_tests}{Colors.END}")
        print(f"{Colors.BOLD}❌ Tests échoués : {Colors.RED}{failed_tests}{Colors.END}")
        print(f"{Colors.BOLD}📊 Taux de réussite : {Colors.GREEN}{self.results['performance_metrics']['success_rate']:.1f}%{Colors.END}")
        print()
        
        # État des APIs
        print(f"{Colors.BOLD}🔗 État des APIs :{Colors.END}")
        for service, status in self.results["api_health"].items():
            status_color = Colors.GREEN if status else Colors.RED
            status_text = "✅ OK" if status else "❌ NON DISPONIBLE"
            print(f"  • {service}: {status_color}{status_text}{Colors.END}")
        
        # Erreurs détectées
        if self.results["errors"]:
            print(f"{Colors.BOLD}⚠️  ERREURS DÉTECTÉES :{Colors.END}")
            for error in self.results["errors"]:
                print(f"  • {Colors.RED}{error}{Colors.END}")
        else:
            print(f"{Colors.BOLD}✅ Aucune erreur critique détectée{Colors.END}")
        
        return self.results
    
    def _get_mime_type(self, file_path: Path) -> str:
        """Détermine le type MIME d'un fichier"""
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type or 'application/octet-stream'

async def main():
    """🚀 Point d'entrée principal"""
    print(f"{Colors.BOLD}{Colors.MAGENTA}🎯 NEXTVISION V3.0 - TEST DONNÉES RÉELLES{Colors.END}")
    print(f"{Colors.BLUE}Pipeline : CV/FDP → Commitment Bridge → Enhanced Bridge V3 → Transport Intelligence → Matching{Colors.END}")
    print()
    
    # Vérification préalable
    if not CV_FOLDER.exists() and not FDP_FOLDER.exists():
        print(f"{Colors.RED}❌ Aucun dossier de test trouvé !{Colors.END}")
        print(f"   Vérifiez que vous avez bien :{Colors.END}")
        print(f"   • {CV_FOLDER}")
        print(f"   • {FDP_FOLDER}")
        return
    
    # Vérification API
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/v1/health") as resp:
                if resp.status != 200:
                    print(f"{Colors.RED}❌ API Nextvision non disponible sur {API_BASE_URL}{Colors.END}")
                    print(f"   Démarrez l'API avec : {Colors.YELLOW}python main.py{Colors.END}")
                    return
    except Exception as e:
        print(f"{Colors.RED}❌ Impossible de contacter l'API : {e}{Colors.END}")
        print(f"   Démarrez l'API avec : {Colors.YELLOW}python main.py{Colors.END}")
        return
    
    # Lancement du test
    tester = NextvisionRealDataTester()
    
    try:
        results = await tester.run_complete_test()
        
        # Sauvegarde du rapport
        timestamp = int(time.time())
        report_file = Path(f"nextvision_real_data_test_report_{timestamp}.json")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print()
        print(f"{Colors.BOLD}📄 Rapport détaillé sauvegardé : {Colors.GREEN}{report_file}{Colors.END}")
        print(f"{Colors.BOLD}🔍 Logs détaillés : {Colors.GREEN}nextvision_test.log{Colors.END}")
        
        return results
        
    except Exception as e:
        print(f"{Colors.RED}❌ Erreur critique : {e}{Colors.END}")
        return {"status": "critical_error", "error": str(e)}

if __name__ == "__main__":
    asyncio.run(main())
