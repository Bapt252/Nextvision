# test_commitment_integration.py
"""
Script de test sécurisé pour valider l'intégration Commitment-
OBJECTIF: Tester sans impacter le système Nextvision existant
"""

import asyncio
import sys
import json
from pathlib import Path
import tempfile
from datetime import datetime

# Import du bridge sécurisé
try:
    from nextvision.services.parsing.commitment_bridge import CommitmentParsingBridge
except ImportError:
    print("❌ Erreur: Impossible d'importer CommitmentParsingBridge")
    print("💡 Assurez-vous que le fichier commitment_bridge.py est dans nextvision/services/parsing/")
    sys.exit(1)

class CommitmentIntegrationTester:
    """Testeur sécurisé pour l'intégration Commitment-"""
    
    def __init__(self):
        self.bridge = CommitmentParsingBridge({
            "safe_mode": True,
            "fallback_enabled": True,
            "test_mode": True
        })
        self.test_results = []
    
    async def run_safety_tests(self):
        """Suite de tests de sécurité complète"""
        
        print("🧪 " + "="*60)
        print("🔗 TESTS DE SÉCURITÉ COMMITMENT INTEGRATION")
        print("🧪 " + "="*60)
        print()
        
        # Test 1: Health Check
        await self._test_health_check()
        
        # Test 2: Connexion parsers
        await self._test_parser_connectivity()
        
        # Test 3: Fallback safety
        await self._test_fallback_safety()
        
        # Test 4: Error handling
        await self._test_error_handling()
        
        # Test 5: Real file parsing (si fichiers disponibles)
        await self._test_real_file_parsing()
        
        # Résumé des tests
        self._print_test_summary()
    
    async def _test_health_check(self):
        """Test 1: Vérification de santé"""
        print("🔍 Test 1: Health Check...")
        
        try:
            health = await self.bridge.health_check()
            
            if health["bridge_status"] == "healthy":
                print("  ✅ Bridge en bonne santé")
                print(f"  📊 CV Parser: {'✅' if health['cv_parser_available'] else '❌'}")
                print(f"  📊 Job Parser: {'✅' if health['job_parser_available'] else '❌'}")
                self.test_results.append(("Health Check", True, "Bridge opérationnel"))
            else:
                print(f"  ⚠️ Bridge status: {health['bridge_status']}")
                print(f"  📝 Error: {health.get('error', 'Unknown')}")
                self.test_results.append(("Health Check", False, health.get('error', 'Unknown')))
                
        except Exception as e:
            print(f"  ❌ Health check failed: {e}")
            self.test_results.append(("Health Check", False, str(e)))
        
        print()
    
    async def _test_parser_connectivity(self):
        """Test 2: Connectivité vers parsers Commitment-"""
        print("🌐 Test 2: Connectivité Parsers...")
        
        try:
            # Test simple de connectivité
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Test CV parser
                try:
                    await page.goto(self.bridge.cv_parser_url, timeout=15000)
                    cv_title = await page.title()
                    print(f"  ✅ CV Parser accessible: {cv_title[:50]}...")
                    cv_ok = True
                except Exception as e:
                    print(f"  ❌ CV Parser inaccessible: {e}")
                    cv_ok = False
                
                # Test Job parser  
                try:
                    await page.goto(self.bridge.job_parser_url, timeout=15000)
                    job_title = await page.title()
                    print(f"  ✅ Job Parser accessible: {job_title[:50]}...")
                    job_ok = True
                except Exception as e:
                    print(f"  ❌ Job Parser inaccessible: {e}")
                    job_ok = False
                
                await browser.close()
            
            self.test_results.append(("CV Parser Connectivity", cv_ok, "Accessible" if cv_ok else "Inaccessible"))
            self.test_results.append(("Job Parser Connectivity", job_ok, "Accessible" if job_ok else "Inaccessible"))
            
        except ImportError:
            print("  ⚠️ Playwright non installé - test de connectivité ignoré")
            print("  💡 Installez avec: pip install playwright && playwright install")
            self.test_results.append(("Parser Connectivity", False, "Playwright non installé"))
        except Exception as e:
            print(f"  ❌ Erreur connectivité: {e}")
            self.test_results.append(("Parser Connectivity", False, str(e)))
        
        print()
    
    async def _test_fallback_safety(self):
        """Test 3: Sécurité du fallback"""
        print("🛡️ Test 3: Sécurité Fallback...")
        
        # Test avec fichier inexistant
        fake_file = "fichier_totalement_inexistant.pdf"
        
        try:
            result = await self.bridge.parse_cv_safe(fake_file)
            
            if result.get("source") == "fallback_simulation":
                print("  ✅ Fallback CV activé automatiquement")
                print(f"  📊 Données simulées générées: {len(str(result))} caractères")
                fallback_cv_ok = True
            else:
                print(f"  ⚠️ Fallback CV inattendu: {result.get('source')}")
                fallback_cv_ok = False
            
            # Test fallback job
            result_job = await self.bridge.parse_job_safe(fake_file)
            
            if result_job.get("source") == "fallback_simulation":
                print("  ✅ Fallback Job activé automatiquement")
                fallback_job_ok = True
            else:
                print(f"  ⚠️ Fallback Job inattendu: {result_job.get('source')}")
                fallback_job_ok = False
            
            self.test_results.append(("Fallback CV Safety", fallback_cv_ok, "Fonctionnel"))
            self.test_results.append(("Fallback Job Safety", fallback_job_ok, "Fonctionnel"))
            
        except Exception as e:
            print(f"  ❌ Erreur fallback: {e}")
            self.test_results.append(("Fallback Safety", False, str(e)))
        
        print()
    
    async def _test_error_handling(self):
        """Test 4: Gestion d'erreurs"""
        print("⚡ Test 4: Gestion d'Erreurs...")
        
        # Test avec différents cas d'erreur
        error_cases = [
            ("", "Fichier vide"),
            ("/path/invalid/file.pdf", "Chemin invalide"),
            ("not_a_file", "Pas un fichier")
        ]
        
        all_handled = True
        
        for test_file, description in error_cases:
            try:
                result = await self.bridge.parse_cv_safe(test_file)
                
                if not result.get("success", True):
                    print(f"  ✅ {description}: Erreur gérée proprement")
                else:
                    print(f"  ⚠️ {description}: Devrait échouer mais a réussi")
                    all_handled = False
                    
            except Exception as e:
                print(f"  ❌ {description}: Exception non gérée: {e}")
                all_handled = False
        
        self.test_results.append(("Error Handling", all_handled, "Gestion propre des erreurs"))
        print()
    
    async def _test_real_file_parsing(self):
        """Test 5: Parsing avec vrais fichiers (si disponibles)"""
        print("📄 Test 5: Parsing Fichiers Réels...")
        
        # Chercher des fichiers de test dans différents emplacements
        test_locations = [
            "tests/data/",
            "test_data/", 
            "data/",
            "./",
            "../tests/data/"
        ]
        
        test_files = []
        
        for location in test_locations:
            path = Path(location)
            if path.exists():
                # Chercher fichiers PDF
                test_files.extend(path.glob("*.pdf"))
                test_files.extend(path.glob("*cv*.pdf"))
                test_files.extend(path.glob("*job*.pdf"))
                test_files.extend(path.glob("*test*.pdf"))
        
        if not test_files:
            print("  ⚠️ Aucun fichier de test trouvé")
            print("  💡 Placez des fichiers PDF dans tests/data/ pour tests complets")
            
            # Créer un fichier de test basique
            await self._create_test_file()
            self.test_results.append(("Real File Parsing", False, "Aucun fichier de test"))
        else:
            print(f"  📁 {len(test_files)} fichiers de test trouvés")
            
            # Tester avec le premier fichier trouvé
            test_file = str(test_files[0])
            print(f"  🔍 Test avec: {Path(test_file).name}")
            
            try:
                result = await self.bridge.parse_cv_safe(test_file)
                
                if result.get("success"):
                    source = result.get("source", "unknown")
                    print(f"  ✅ Parsing réussi via: {source}")
                    
                    if "data" in result:
                        data = result["data"]
                        if "data" in data:  # Structure Commitment-
                            inner_data = data["data"]
                            exp_count = len(inner_data.get("work_experience", []))
                            print(f"  📊 Expériences extraites: {exp_count}")
                        else:
                            print(f"  📊 Données extraites: {len(str(data))} caractères")
                    
                    real_parsing_ok = True
                else:
                    print(f"  ❌ Parsing échoué: {result.get('error')}")
                    real_parsing_ok = False
                
                self.test_results.append(("Real File Parsing", real_parsing_ok, f"Via {source}" if real_parsing_ok else "Échec"))
                
            except Exception as e:
                print(f"  ❌ Erreur parsing réel: {e}")
                self.test_results.append(("Real File Parsing", False, str(e)))
        
        print()
    
    async def _create_test_file(self):
        """Créer un fichier de test basique"""
        print("  📝 Création fichier de test basique...")
        
        try:
            test_dir = Path("tests/data")
            test_dir.mkdir(parents=True, exist_ok=True)
            
            # Créer un fichier texte simulant un CV
            test_cv_content = """
CV Test - Jean Dupont
Email: jean.dupont@example.com
Téléphone: 01 23 45 67 89

EXPÉRIENCE PROFESSIONNELLE

2020-2023: Développeur Full Stack
Entreprise Tech, Paris
- Développement applications web
- Technologies: JavaScript, Python, React

2018-2020: Développeur Junior  
StartUp Innovation, Lyon
- Maintenance applications
- Formation aux nouvelles technologies

FORMATION

2018: Master Informatique
Université de Lyon

COMPÉTENCES
- JavaScript, Python, React
- Base de données SQL
- Git, Docker
            """
            
            test_file = test_dir / "cv_test.txt"
            test_file.write_text(test_cv_content, encoding='utf-8')
            
            print(f"  ✅ Fichier de test créé: {test_file}")
            
        except Exception as e:
            print(f"  ⚠️ Impossible de créer fichier de test: {e}")
    
    def _print_test_summary(self):
        """Afficher le résumé des tests"""
        print("📊 " + "="*60)
        print("�� RÉSUMÉ DES TESTS DE SÉCURITÉ")
        print("📊 " + "="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, success, _ in self.test_results if success)
        
        print(f"\n🎯 Tests passés: {passed_tests}/{total_tests}")
        
        if passed_tests == total_tests:
            print("✅ TOUS LES TESTS PASSÉS - INTÉGRATION SÉCURISÉE !")
        elif passed_tests >= total_tests * 0.8:
            print("⚠️ MAJORITÉ DES TESTS PASSÉS - INTÉGRATION ACCEPTABLE")
        else:
            print("❌ PLUSIEURS TESTS ÉCHOUÉS - RÉVISION NÉCESSAIRE")
        
        print("\n📋 Détail des tests:")
        for test_name, success, details in self.test_results:
            status = "✅" if success else "❌"
            print(f"  {status} {test_name}: {details}")
        
        # Statistiques du bridge
        stats = self.bridge.get_stats()
        print(f"\n📈 Statistiques Bridge:")
        print(f"  • Taux de succès: {stats['success_rate']:.1f}%")
        print(f"  • Taux de fallback: {stats['fallback_rate']:.1f}%")
        print(f"  • Parsing CV: {stats['cv_parses']}")
        print(f"  • Parsing Jobs: {stats['job_parses']}")
        
        print("\n🔧 Recommandations:")
        if passed_tests == total_tests:
            print("  ✅ Le bridge est prêt pour l'intégration avec Enhanced Bridge V3.0")
            print("  🚀 Vous pouvez procéder à l'étape suivante en toute sécurité")
        else:
            print("  ⚠️ Résoudre les problèmes identifiés avant intégration")
            if stats['fallback_rate'] > 50:
                print("  💡 Vérifiez la connectivité vers Commitment- parsers")
        
        print("\n🎉 Tests de sécurité terminés !")

# Interface de test simple
async def main():
    """Point d'entrée principal"""
    
    print(f"🕒 Début des tests: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Vérifier les dépendances
    try:
        import playwright
        print("✅ Playwright disponible")
    except ImportError:
        print("⚠️ Playwright non installé")
        print("💡 Pour des tests complets, installez: pip install playwright && playwright install")
    
    # Lancer les tests
    tester = CommitmentIntegrationTester()
    await tester.run_safety_tests()

# Tests en mode script
if __name__ == "__main__":
    print("🔗 COMMITMENT INTEGRATION - TESTS DE SÉCURITÉ")
    print("=" * 60)
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrompus par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur critique dans les tests: {e}")
        sys.exit(1)
