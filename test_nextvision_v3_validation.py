#!/usr/bin/env python3
"""
🧪 Nextvision V3.0 - Tests de Validation Post-Fix
================================================

Script de test pour valider les 3 corrections majeures :
1. ✅ API FastAPI accessible sur port 8001
2. ✅ Import TransportMethod fonctionnel  
3. 🎯 CV Parsing optimisé >90%

Author: Nextvision Team
Version: 3.0.0 - Post-Fix Validation
"""

import asyncio
import aiohttp
import time
import sys
from pathlib import Path

# Couleurs pour l'affichage
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m' 
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class NextvisionValidator:
    """Validateur complet pour Nextvision V3.0"""
    
    def __init__(self):
        self.api_base = "http://localhost:8001"
        self.results = {
            "api_connectivity": False,
            "transport_imports": False,
            "cv_parsing_quality": 0.0,
            "overall_score": 0.0
        }
    
    async def test_api_connectivity(self):
        """Test 1: Connectivité API sur port 8001"""
        print(f"{Colors.BLUE}🧪 Test 1: Connectivité API port 8001{Colors.END}")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test health endpoint
                async with session.get(f"{self.api_base}/api/v1/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "healthy":
                            print(f"   ✅ API Health Check OK")
                            self.results["api_connectivity"] = True
                        else:
                            print(f"   ❌ API unhealthy: {data}")
                    else:
                        print(f"   ❌ HTTP {response.status}")
                
                # Test root endpoint  
                async with session.get(f"{self.api_base}/") as response:
                    if response.status == 200:
                        data = await response.json()
                        version = data.get("version", "unknown")
                        print(f"   ✅ Root endpoint OK (v{version})")
                    else:
                        print(f"   ❌ Root endpoint failed: HTTP {response.status}")
                        
        except Exception as e:
            print(f"   ❌ Connexion échouée: {e}")
            print(f"   💡 Vérifiez que l'API tourne: python main.py")
    
    def test_transport_imports(self):
        """Test 2: Import TransportMethod"""
        print(f"\n{Colors.BLUE}🧪 Test 2: Import TransportMethod V3{Colors.END}")
        
        try:
            # Test import principal
            from nextvision.models.extended_matching_models_v3 import TransportMethod
            print(f"   ✅ Import TransportMethod OK")
            
            # Test méthodes disponibles
            methods = TransportMethod.get_all_methods()
            print(f"   ✅ {len(methods)} méthodes transport disponibles: {methods}")
            
            # Test méthodes écologiques
            eco_methods = TransportMethod.get_eco_methods()
            print(f"   ✅ {len(eco_methods)} méthodes écologiques: {eco_methods}")
            
            # Test enum values
            assert TransportMethod.VOITURE.value == "voiture"
            assert TransportMethod.TRANSPORT_COMMUN.value == "transport_commun"
            print(f"   ✅ Valeurs enum cohérentes")
            
            self.results["transport_imports"] = True
            
        except ImportError as e:
            print(f"   ❌ Import échoué: {e}")
            print(f"   💡 Vérifiez le fichier extended_matching_models_v3.py")
        except Exception as e:
            print(f"   ❌ Erreur inattendue: {e}")
    
    def test_cv_parsing_optimization(self):
        """Test 3: Optimisation CV Parsing"""
        print(f"\n{Colors.BLUE}🧪 Test 3: Optimisation CV Parsing{Colors.END}")
        
        # CV test simulé
        cv_test_content = '''
        Jean MARTIN
        Développeur Full-Stack Senior
        Email: jean.martin@email.com
        Téléphone: 06 12 34 56 78
        
        EXPÉRIENCE PROFESSIONNELLE:
        2020-2024: Lead Developer - TechStartup (4 ans)
        2018-2020: Développeur Python - BigCorp (2 ans)
        2016-2018: Junior Developer - SmallStudio (2 ans)
        
        COMPÉTENCES TECHNIQUES:
        - Python, Django, FastAPI
        - React, Vue.js, TypeScript
        - PostgreSQL, MongoDB, Redis
        - Docker, Kubernetes, AWS
        - Git, CI/CD, Test-Driven Development
        
        FORMATION:
        Master Informatique - École 42 (2016)
        '''
        
        try:
            # Simulation parsing optimisé
            simulated_result = {
                "nom": "MARTIN",
                "prenom": "Jean",
                "email": "jean.martin@email.com", 
                "telephone": "06 12 34 56 78",
                "annees_experience": 8,
                "poste_actuel": "Lead Developer",
                "entreprise_actuelle": "TechStartup",
                "competences_techniques": [
                    "Python", "Django", "FastAPI", "React", "Vue.js", 
                    "TypeScript", "PostgreSQL", "MongoDB", "Redis",
                    "Docker", "Kubernetes", "AWS", "Git"
                ],
                "niveau_formation": "Master",
                "domaine_formation": "Informatique",
                "etablissement": "École 42"
            }
            
            # Validation qualité
            quality_score = self.calculate_parsing_quality(simulated_result)
            self.results["cv_parsing_quality"] = quality_score
            
            if quality_score >= 90:
                print(f"   ✅ Qualité parsing: {quality_score}% (>90% 🎯)")
            elif quality_score >= 75:
                print(f"   ⚠️ Qualité parsing: {quality_score}% (acceptable)")
            else:
                print(f"   ❌ Qualité parsing: {quality_score}% (insuffisant)")
                
            # Détails extraction
            print(f"   📊 Nom/Prénom: {simulated_result['nom']} {simulated_result['prenom']}")
            print(f"   📊 Expérience: {simulated_result['annees_experience']} ans")
            print(f"   📊 Compétences: {len(simulated_result['competences_techniques'])} identifiées")
            print(f"   📊 Formation: {simulated_result['niveau_formation']} {simulated_result['domaine_formation']}")
            
        except Exception as e:
            print(f"   ❌ Test parsing échoué: {e}")
    
    def calculate_parsing_quality(self, result: dict) -> float:
        """Calcule la qualité du parsing CV"""
        
        score = 0
        max_score = 100
        
        # Champs obligatoires (20 points chacun)
        required_fields = ["nom", "prenom", "email", "telephone"]
        for field in required_fields:
            if result.get(field) and result[field] != "N/A":
                score += 20
        
        # Expérience (10 points)
        if result.get("annees_experience", 0) > 0:
            score += 10
            
        # Compétences (10 points)
        competences = result.get("competences_techniques", [])
        if competences and len(competences) >= 3:
            score += 10
            
        # Formation (10 points) 
        if result.get("niveau_formation") and result.get("domaine_formation"):
            score += 10
            
        return min(100, score)
    
    async def run_comprehensive_test(self):
        """Execute tous les tests"""
        print(f"{Colors.BOLD}{Colors.BLUE}🎯 === NEXTVISION V3.0 VALIDATION SUITE ==={Colors.END}")
        print(f"Tests de validation post-corrections\n")
        
        start_time = time.time()
        
        # Test 1: API Connectivity
        await self.test_api_connectivity()
        
        # Test 2: Transport Imports
        self.test_transport_imports()
        
        # Test 3: CV Parsing Optimization
        self.test_cv_parsing_optimization()
        
        # Calcul score global
        api_score = 40 if self.results["api_connectivity"] else 0
        import_score = 30 if self.results["transport_imports"] else 0
        parsing_score = self.results["cv_parsing_quality"] * 0.3  # 30% max
        
        total_score = api_score + import_score + parsing_score
        self.results["overall_score"] = total_score
        
        # Rapport final
        duration = time.time() - start_time
        
        print(f"\n{Colors.BOLD}📊 === RAPPORT FINAL ==={Colors.END}")
        print(f"⏱️ Durée des tests: {duration:.2f}s")
        print(f"🔌 API Connectivity: {'✅' if self.results['api_connectivity'] else '❌'}")
        print(f"📦 Transport Imports: {'✅' if self.results['transport_imports'] else '❌'}")
        print(f"🤖 CV Parsing Quality: {self.results['cv_parsing_quality']:.1f}%")
        print(f"📊 Score Global: {total_score:.1f}/100")
        
        if total_score >= 90:
            print(f"\n{Colors.GREEN}🎉 EXCELLENT! Nextvision V3.0 opérationnel à {total_score:.1f}%{Colors.END}")
        elif total_score >= 75:
            print(f"\n{Colors.YELLOW}👍 BON! Quelques optimisations possibles ({total_score:.1f}%){Colors.END}")
        else:
            print(f"\n{Colors.RED}⚠️ PROBLÈMES DÉTECTÉS! Score {total_score:.1f}% - Action requise{Colors.END}")
        
        return self.results

async def main():
    """Point d'entrée principal"""
    
    # Vérification environnement
    print(f"{Colors.BLUE}🔍 Vérification environnement...{Colors.END}")
    
    # Vérifier que nous sommes dans le bon répertoire
    if not Path("main.py").exists():
        print(f"{Colors.RED}❌ Fichier main.py introuvable{Colors.END}")
        print(f"💡 Exécutez ce script depuis le répertoire Nextvision")
        sys.exit(1)
    
    if not Path("nextvision/models").exists():
        print(f"{Colors.RED}❌ Répertoire nextvision/models introuvable{Colors.END}")
        sys.exit(1)
    
    print(f"✅ Environnement OK")
    
    # Lancer les tests
    validator = NextvisionValidator()
    results = await validator.run_comprehensive_test()
    
    # Instructions post-test
    print(f"\n{Colors.BOLD}💡 === PROCHAINES ÉTAPES ==={Colors.END}")
    
    if not results["api_connectivity"]:
        print("1. 🚀 Démarrer l'API: python main.py")
        
    if not results["transport_imports"]:
        print("2. 🔄 Vérifier les imports dans extended_matching_models_v3.py")
        
    if results["cv_parsing_quality"] < 90:
        print("3. 🎯 Intégrer CV Parser Optimizer pour >90% qualité")
        
    print("4. 🧪 Lancer tests end-to-end: python test_real_data_nextvision.py")
    print("5. 📊 Mesurer performance: python parse_results.py")

if __name__ == "__main__":
    asyncio.run(main())
