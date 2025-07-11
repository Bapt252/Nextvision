#!/usr/bin/env python3
"""
🚀 NEXTVISION V3.2.1 - LANCEUR DE TESTS COMPLET

Orchestration complète des tests end-to-end :
1. Diagnostic pré-tests automatique
2. Validation système
3. Lancement des tests e2e
4. Génération rapport consolidé
5. Recommandations post-tests

Version: 3.2.1
Date: 2025-07-11
Auteur: Assistant Claude
"""

import sys
import subprocess
import json
import asyncio
from datetime import datetime
from pathlib import Path
import argparse

class TestLauncher:
    """Lanceur orchestré des tests Nextvision V3.2.1"""
    
    def __init__(self, args):
        self.args = args
        self.results = {
            "diagnostic": None,
            "e2e_tests": None,
            "summary": None
        }
        
    def print_banner(self):
        """Affiche la bannière de lancement"""
        print("🚀 NEXTVISION V3.2.1 - VALIDATION COMPLÈTE")
        print("=" * 60)
        print("Tests End-to-End avec Diagnostic Automatique")
        print("Validation complète du parcours utilisateur")
        print("=" * 60)
        print()
    
    def run_diagnostic(self) -> bool:
        """Lance le diagnostic pré-tests"""
        print("🔍 ÉTAPE 1/3: Diagnostic Système")
        print("-" * 40)
        
        try:
            # Lancement du diagnostic
            result = subprocess.run([
                sys.executable, "diagnostic_pre_tests.py"
            ], capture_output=True, text=True, timeout=120)
            
            # Récupération du code de sortie
            diagnostic_success = result.returncode == 0
            
            # Affichage des résultats
            if result.stdout:
                print(result.stdout)
            
            if result.stderr and not diagnostic_success:
                print("Erreurs détectées:")
                print(result.stderr)
            
            # Chargement du rapport JSON si disponible
            try:
                diagnostic_files = list(Path(".").glob("diagnostic_report_*.json"))
                if diagnostic_files:
                    latest_file = max(diagnostic_files, key=lambda f: f.stat().st_mtime)
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        self.results["diagnostic"] = json.load(f)
                        
            except Exception as e:
                print(f"⚠️  Impossible de charger le rapport diagnostic: {e}")
            
            if diagnostic_success:
                print("✅ Diagnostic terminé avec succès!")
                return True
            else:
                print("❌ Diagnostic a détecté des problèmes critiques")
                if not self.args.force:
                    print("💡 Utiliser --force pour continuer malgré les erreurs")
                    return False
                else:
                    print("⚠️  Continuation forcée malgré les erreurs")
                    return True
                    
        except subprocess.TimeoutExpired:
            print("❌ Timeout du diagnostic (>2 minutes)")
            return False
        except Exception as e:
            print(f"❌ Erreur lors du diagnostic: {e}")
            return False
    
    async def run_e2e_tests(self) -> bool:
        """Lance les tests end-to-end"""
        print("\n🧪 ÉTAPE 2/3: Tests End-to-End")
        print("-" * 40)
        
        try:
            # Lancement des tests e2e
            if self.args.quick:
                print("⚡ Mode rapide activé - Tests essentiels uniquement")
                # Pour le mode rapide, on pourrait modifier le script e2e
                # ou créer une version allégée
            
            result = subprocess.run([
                sys.executable, "test_e2e_nextvision_v321.py"
            ], capture_output=True, text=True, timeout=600)  # 10 minutes max
            
            # Récupération du code de sortie
            tests_success = result.returncode == 0
            
            # Affichage des résultats
            if result.stdout:
                print(result.stdout)
            
            if result.stderr and not tests_success:
                print("Erreurs pendant les tests:")
                print(result.stderr)
            
            # Chargement du rapport JSON si disponible
            try:
                e2e_files = list(Path(".").glob("nextvision_e2e_report_*.json"))
                if e2e_files:
                    latest_file = max(e2e_files, key=lambda f: f.stat().st_mtime)
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        self.results["e2e_tests"] = json.load(f)
                        
            except Exception as e:
                print(f"⚠️  Impossible de charger le rapport e2e: {e}")
            
            if tests_success:
                print("✅ Tests end-to-end terminés avec succès!")
                return True
            else:
                print("❌ Certains tests end-to-end ont échoué")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Timeout des tests e2e (>10 minutes)")
            return False
        except Exception as e:
            print(f"❌ Erreur lors des tests e2e: {e}")
            return False
    
    def generate_consolidated_report(self):
        """Génère un rapport consolidé"""
        print("\n📊 ÉTAPE 3/3: Rapport Consolidé")
        print("-" * 40)
        
        # Analyse des résultats
        diagnostic_data = self.results.get("diagnostic", {})
        e2e_data = self.results.get("e2e_tests", {})
        
        # Extraction des métriques clés
        diagnostic_summary = diagnostic_data.get("summary", {})
        e2e_summary = e2e_data.get("summary", {})
        
        # Calcul du score global
        diagnostic_score = diagnostic_summary.get("success_rate", 0)
        e2e_score = e2e_summary.get("success_rate", 0)
        global_score = (diagnostic_score + e2e_score) / 2 if diagnostic_score and e2e_score else 0
        
        # Statut global
        if global_score >= 0.9:
            global_status = "EXCELLENT"
            status_emoji = "🎉"
        elif global_score >= 0.8:
            global_status = "BON"
            status_emoji = "✅"
        elif global_score >= 0.6:
            global_status = "ACCEPTABLE"
            status_emoji = "⚠️"
        else:
            global_status = "CRITIQUE"
            status_emoji = "❌"
        
        # Génération du rapport
        consolidated_report = {
            "validation_summary": {
                "timestamp": datetime.now().isoformat(),
                "global_score": global_score,
                "global_status": global_status,
                "diagnostic_success_rate": diagnostic_score,
                "e2e_success_rate": e2e_score,
                "ready_for_production": global_score >= 0.8
            },
            "diagnostic_results": diagnostic_data,
            "e2e_test_results": e2e_data,
            "final_recommendations": self._generate_final_recommendations()
        }
        
        # Sauvegarde du rapport consolidé
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"nextvision_validation_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(consolidated_report, f, indent=2, ensure_ascii=False)
        
        # Affichage du résumé
        print(f"{status_emoji} STATUT GLOBAL: {global_status}")
        print(f"Score de validation: {global_score:.1%}")
        print(f"Diagnostic: {diagnostic_score:.1%}")
        print(f"Tests E2E: {e2e_score:.1%}")
        
        if consolidated_report["validation_summary"]["ready_for_production"]:
            print("\n🎯 NEXTVISION V3.2.1 EST PRÊT POUR LA PRODUCTION ! 🎯")
        else:
            print(f"\n⚠️  Optimisations nécessaires avant production")
        
        print(f"\n💾 Rapport complet: {report_file}")
        
        # Affichage des recommandations
        print("\n📋 RECOMMANDATIONS FINALES:")
        for rec in consolidated_report["final_recommendations"]:
            print(f"  • {rec}")
        
        self.results["summary"] = consolidated_report
        
        return global_score >= 0.8
    
    def _generate_final_recommendations(self):
        """Génère les recommandations finales"""
        recommendations = []
        
        diagnostic_data = self.results.get("diagnostic", {})
        e2e_data = self.results.get("e2e_tests", {})
        
        # Analyse du diagnostic
        if diagnostic_data:
            diagnostic_summary = diagnostic_data.get("summary", {})
            if diagnostic_summary.get("success_rate", 0) < 0.8:
                recommendations.append("Corriger les problèmes détectés lors du diagnostic système")
            
            critical_failures = diagnostic_summary.get("critical_failures", [])
            if critical_failures:
                recommendations.append(f"Résoudre les échecs critiques: {', '.join(critical_failures)}")
        
        # Analyse des tests e2e
        if e2e_data:
            e2e_summary = e2e_data.get("summary", {})
            if e2e_summary.get("success_rate", 0) < 0.8:
                recommendations.append("Investiguer les échecs des tests end-to-end")
            
            # Recommandations spécifiques basées sur les tests
            test_results = e2e_data.get("test_results", [])
            for test in test_results:
                if not test.get("success"):
                    test_name = test.get("test_name", "")
                    if "Charlotte DARMON" in test_name or "Hierarchical" in test_name:
                        recommendations.append("Vérifier le système hiérarchique V3.2.1")
                    elif "Google Maps" in test_name:
                        recommendations.append("Vérifier la configuration Google Maps API")
                    elif "Transport" in test_name:
                        recommendations.append("Optimiser le module Transport Intelligence")
                    elif "Performance" in test_name:
                        recommendations.append("Optimiser les performances système")
        
        # Recommandations générales
        if not recommendations:
            recommendations.extend([
                "Système validé - Prêt pour la mise en production",
                "Surveiller les performances en production",
                "Mettre en place le monitoring automatique",
                "Documenter les procédures de déploiement"
            ])
        else:
            recommendations.append("Relancer les tests après corrections")
            recommendations.append("Vérifier la documentation de déploiement")
        
        return recommendations
    
    def run(self) -> int:
        """Lance la validation complète"""
        self.print_banner()
        
        # Étape 1: Diagnostic
        if not self.args.skip_diagnostic:
            diagnostic_success = self.run_diagnostic()
            if not diagnostic_success and not self.args.force:
                print("\n❌ Arrêt en raison d'échecs du diagnostic")
                print("💡 Utiliser --force pour continuer ou corriger les problèmes")
                return 1
        else:
            print("⏭️  Diagnostic ignoré (--skip-diagnostic)")
        
        # Étape 2: Tests E2E
        if not self.args.skip_e2e:
            e2e_success = asyncio.run(self.run_e2e_tests())
        else:
            print("⏭️  Tests E2E ignorés (--skip-e2e)")
            e2e_success = True
        
        # Étape 3: Rapport consolidé
        final_success = self.generate_consolidated_report()
        
        # Code de sortie
        if final_success:
            print("\n🎉 VALIDATION NEXTVISION V3.2.1 RÉUSSIE !")
            return 0
        else:
            print("\n⚠️  Validation incomplète - Voir les recommandations")
            return 1


def main():
    """Fonction principale avec arguments"""
    parser = argparse.ArgumentParser(
        description="Lanceur de tests complet Nextvision V3.2.1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python launch_complete_tests.py                 # Validation complète
  python launch_complete_tests.py --quick         # Tests rapides
  python launch_complete_tests.py --force         # Continue malgré les erreurs
  python launch_complete_tests.py --skip-diagnostic  # Ignore le diagnostic
  python launch_complete_tests.py --skip-e2e      # Ignore les tests e2e
        """
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Mode rapide - Tests essentiels uniquement'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Continue même si le diagnostic détecte des problèmes'
    )
    
    parser.add_argument(
        '--skip-diagnostic',
        action='store_true',
        help='Ignore le diagnostic pré-tests'
    )
    
    parser.add_argument(
        '--skip-e2e',
        action='store_true',
        help='Ignore les tests end-to-end'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Affichage verbeux'
    )
    
    args = parser.parse_args()
    
    # Validation des arguments
    if args.skip_diagnostic and args.skip_e2e:
        print("❌ Erreur: Impossible d'ignorer à la fois le diagnostic ET les tests e2e")
        return 2
    
    try:
        launcher = TestLauncher(args)
        return launcher.run()
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrompus par l'utilisateur")
        return 2
    except Exception as e:
        print(f"\n❌ Erreur critique: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 3


if __name__ == "__main__":
    exit(main())
