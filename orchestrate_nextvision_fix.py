#!/usr/bin/env python3
"""
🎯 ORCHESTRATEUR CORRECTION NEXTVISION V3.0
Lance les corrections dans l'ordre optimal pour atteindre 80%+ d'intégration

🚀 WORKFLOW AUTOMATISÉ:
1. Diagnostic initial
2. Corrections ciblées
3. Validation finale
4. Rapport de réussite

Author: Assistant Claude
Version: 3.0.0-orchestrator
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class NextvisionFixOrchestrator:
    """🎯 Orchestrateur de correction Nextvision V3.0"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.start_time = datetime.now()
        
        self.steps_completed: Dict[str, bool] = {}
        self.step_scores: Dict[str, float] = {}
        self.step_durations: Dict[str, float] = {}
        self.overall_progress = 0.0
        
        # Configuration des étapes
        self.workflow_steps = [
            {
                'name': 'diagnostic_initial',
                'script': 'diagnose_nextvision_imports.py',
                'description': 'Diagnostic initial des imports',
                'weight': 0.15,
                'required': True
            },
            {
                'name': 'correction_imports',
                'script': 'fix_nextvision_imports_final.py',
                'description': 'Correction des imports et chemins',
                'weight': 0.45,
                'required': True
            },
            {
                'name': 'validation_complete',
                'script': 'validate_nextvision_integration.py',
                'description': 'Validation complète de l\'intégration',
                'weight': 0.25,
                'required': True
            },
            {
                'name': 'test_integration',
                'script': 'test_integration_simple.py',
                'description': 'Test d\'intégration final',
                'weight': 0.15,
                'required': False
            }
        ]
        
        print(f"🎯 Orchestrateur de correction Nextvision V3.0 initialisé")
        print(f"📁 Répertoire: {self.project_root.absolute()}")
        print(f"🕐 Début: {self.start_time.strftime('%H:%M:%S')}")

    def print_step_header(self, step_num: int, total_steps: int, step_name: str, description: str):
        """Affiche l'en-tête d'une étape"""
        print(f"\n{'='*60}")
        print(f"🔄 ÉTAPE {step_num}/{total_steps}: {step_name.upper()}")
        print(f"📋 {description}")
        print(f"{'='*60}")

    def print_progress_bar(self, progress: float, width: int = 40):
        """Affiche une barre de progression"""
        filled = int(width * progress / 100)
        bar = '█' * filled + '░' * (width - filled)
        print(f"📊 Progression globale: [{bar}] {progress:.1f}%")

    def run_script(self, script_name: str, timeout: int = 300) -> Tuple[bool, int, str, str]:
        """Lance un script et retourne le résultat"""
        
        script_path = self.project_root / script_name
        
        if not script_path.exists():
            return False, -1, "", f"Script {script_name} non trouvé"
        
        try:
            print(f"🚀 Lancement: {script_name}")
            start_time = time.time()
            
            # Lancement du script
            result = subprocess.run([
                sys.executable, str(script_path)
            ], capture_output=True, text=True, timeout=timeout)
            
            duration = time.time() - start_time
            
            print(f"⏱️ Durée: {duration:.2f}s")
            print(f"📤 Code retour: {result.returncode}")
            
            # Affichage sortie si verbose
            if result.stdout:
                print("📋 Sortie:")
                # Afficher seulement les lignes importantes
                lines = result.stdout.split('\n')
                important_lines = [
                    line for line in lines 
                    if any(marker in line for marker in ['✅', '❌', '⚠️', 'Score', 'SUCCÈS', 'ÉCHEC', 'FINAL'])
                ]
                for line in important_lines[-10:]:  # Dernières 10 lignes importantes
                    if line.strip():
                        print(f"  {line}")
            
            if result.stderr and result.returncode != 0:
                print("❌ Erreurs:")
                error_lines = result.stderr.split('\n')[:5]  # Premières 5 erreurs
                for line in error_lines:
                    if line.strip():
                        print(f"  {line}")
            
            return True, result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            print(f"⏱️ Timeout ({timeout}s) - Script bloqué")
            return False, -2, "", "Timeout"
        except Exception as e:
            print(f"❌ Erreur exécution: {e}")
            return False, -3, "", str(e)

    def extract_score_from_output(self, output: str, script_name: str) -> float:
        """Extrait le score depuis la sortie d'un script"""
        
        import re
        
        # Patterns de score selon le script
        score_patterns = [
            r'Score final: (\d+\.?\d*)%',
            r'Score intégration: (\d+\.?\d*)%', 
            r'Taux de réussite: (\d+\.?\d*)%',
            r'SCORE INTÉGRATION ESTIMÉ: (\d+\.?\d*)%'
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, output)
            if match:
                return float(match.group(1))
        
        # Estimation basée sur le code de retour et contenu
        if "RÉUSSIE" in output or "SUCCÈS" in output:
            return 85.0
        elif "PARTIELLE" in output or "partiel" in output:
            return 65.0
        elif "ÉCHEC" in output or "échoué" in output:
            return 30.0
        else:
            return 50.0  # Score neutre

    def analyze_step_result(self, step: Dict, success: bool, return_code: int, 
                          stdout: str, stderr: str) -> Tuple[bool, float]:
        """Analyse le résultat d'une étape"""
        
        step_name = step['name']
        
        # Extraction du score
        score = self.extract_score_from_output(stdout, step['script'])
        
        # Détermination du succès selon l'étape
        if step_name == 'diagnostic_initial':
            # Diagnostic réussi si exécuté, score informatif
            step_success = success and return_code <= 3  # Codes 0-3 acceptables
        elif step_name == 'correction_imports':
            # Correction réussie si code 0 ou score > 70%
            step_success = success and (return_code == 0 or score >= 70.0)
        elif step_name == 'validation_complete':
            # Validation réussie si score >= 80%
            step_success = success and return_code == 0 and score >= 80.0
        elif step_name == 'test_integration':
            # Test réussi si score >= 80%
            step_success = success and score >= 80.0
        else:
            step_success = success and return_code == 0
        
        return step_success, score

    def should_continue_workflow(self, step: Dict, step_success: bool, score: float) -> bool:
        """Détermine si le workflow doit continuer"""
        
        # Étapes obligatoires
        if step['required'] and not step_success:
            return False
        
        # Seuils de continuation
        if step['name'] == 'diagnostic_initial':
            return True  # Toujours continuer après diagnostic
        elif step['name'] == 'correction_imports':
            return score >= 60.0  # Continuer si amélioration significative
        elif step['name'] == 'validation_complete':
            return score >= 75.0  # Continuer pour test final si proche
        
        return True

    def run_complete_workflow(self) -> Tuple[bool, float]:
        """Lance le workflow complet de correction"""
        
        print("🎯 DÉMARRAGE WORKFLOW CORRECTION NEXTVISION V3.0")
        print("=" * 60)
        print(f"📋 Étapes prévues: {len(self.workflow_steps)}")
        print(f"🎯 Objectif: Score ≥ 80% d'intégration")
        print()
        
        total_steps = len(self.workflow_steps)
        workflow_success = True
        final_score = 0.0
        
        # Exécution des étapes
        for i, step in enumerate(self.workflow_steps, 1):
            step_name = step['name']
            step_description = step['description']
            step_weight = step['weight']
            
            # En-tête étape
            self.print_step_header(i, total_steps, step_name, step_description)
            
            # Progression
            current_progress = ((i - 1) / total_steps) * 100
            self.print_progress_bar(current_progress)
            
            # Exécution
            step_start = time.time()
            success, return_code, stdout, stderr = self.run_script(step['script'])
            step_duration = time.time() - step_start
            
            # Analyse résultat
            step_success, step_score = self.analyze_step_result(step, success, return_code, stdout, stderr)
            
            # Enregistrement
            self.steps_completed[step_name] = step_success
            self.step_scores[step_name] = step_score
            self.step_durations[step_name] = step_duration
            
            # Mise à jour score final pondéré
            final_score += step_score * step_weight
            
            # Affichage résultat étape
            if step_success:
                print(f"✅ Étape {i} RÉUSSIE - Score: {step_score:.1f}%")
            else:
                print(f"❌ Étape {i} ÉCHOUÉE - Score: {step_score:.1f}%")
                if step['required']:
                    print(f"🚨 Étape obligatoire échouée - Arrêt workflow")
                    workflow_success = False
                    break
            
            # Vérification continuation
            if not self.should_continue_workflow(step, step_success, step_score):
                print(f"⏹️ Arrêt workflow - Score insuffisant: {step_score:.1f}%")
                workflow_success = False
                break
            
            # Pause entre étapes
            if i < total_steps:
                time.sleep(1)
        
        # Progression finale
        self.print_progress_bar(100.0)
        
        return workflow_success, final_score

    def generate_final_report(self, workflow_success: bool, final_score: float):
        """Génère le rapport final"""
        
        end_time = datetime.now()
        total_duration = end_time - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 RAPPORT FINAL ORCHESTRATEUR")
        print("=" * 60)
        
        print(f"🕐 Début: {self.start_time.strftime('%H:%M:%S')}")
        print(f"🕐 Fin: {end_time.strftime('%H:%M:%S')}")
        print(f"⏱️ Durée totale: {total_duration.total_seconds():.2f}s")
        
        # Résumé étapes
        print(f"\n📋 RÉSUMÉ ÉTAPES:")
        completed_count = sum(self.steps_completed.values())
        total_count = len(self.workflow_steps)
        
        for step in self.workflow_steps:
            step_name = step['name']
            step_desc = step['description']
            
            if step_name in self.steps_completed:
                success = self.steps_completed[step_name]
                score = self.step_scores.get(step_name, 0)
                duration = self.step_durations.get(step_name, 0)
                
                status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
                print(f"  {status} - {step_desc}")
                print(f"    Score: {score:.1f}% | Durée: {duration:.1f}s")
            else:
                print(f"  ⏭️ IGNORÉ - {step_desc}")
        
        # Score final
        print(f"\n📊 SCORE FINAL: {final_score:.1f}%")
        
        # Statut global
        if workflow_success and final_score >= 80.0:
            print("\n🎉 WORKFLOW RÉUSSI!")
            print("✅ Corrections appliquées avec succès")
            print("✅ Score d'intégration ≥ 80% atteint")
            print("✅ Nextvision V3.0 opérationnel")
            
            print("\n🚀 PROCHAINES ÉTAPES RECOMMANDÉES:")
            print("1. Tests avancés: python3 test_nextvision_commitment_integration.py")
            print("2. Démo Transport Intelligence: python3 demo_transport_intelligence.py") 
            print("3. Configuration .env avec vos API keys")
            print("4. Déploiement: bash deploy_nextvision_v2.sh")
            
        elif workflow_success and final_score >= 70.0:
            print("\n⚠️ WORKFLOW PARTIELLEMENT RÉUSSI")
            print(f"✅ Corrections appliquées")
            print(f"⚠️ Score: {final_score:.1f}% (proche de l'objectif 80%)")
            print("🔧 Optimisations mineures nécessaires")
            
            print("\n🔧 ACTIONS RECOMMANDÉES:")
            print("1. Ajustements manuels des derniers imports")
            print("2. Relancer: python3 validate_nextvision_integration.py")
            print("3. Si score > 80%: continuer vers tests avancés")
            
        else:
            print("\n❌ WORKFLOW ÉCHOUÉ")
            print(f"❌ Score final: {final_score:.1f}% (< objectif 80%)")
            
            # Identification des étapes échouées
            failed_steps = [
                step['name'] for step in self.workflow_steps 
                if step['name'] in self.steps_completed and not self.steps_completed[step['name']]
            ]
            
            if failed_steps:
                print(f"🚨 Étapes échouées: {', '.join(failed_steps)}")
            
            print("\n🛠️ ACTIONS CORRECTIVES:")
            print("1. Vérifier les erreurs détaillées ci-dessus")
            print("2. Corriger manuellement si nécessaire")
            print("3. Relancer: python3 orchestrate_nextvision_fix.py")
            print("4. Si problèmes persistent: vérifier structure projet")
        
        # Métriques détaillées
        if self.step_scores:
            print(f"\n📈 ÉVOLUTION SCORES:")
            for step in self.workflow_steps:
                if step['name'] in self.step_scores:
                    score = self.step_scores[step['name']]
                    print(f"  {step['description']}: {score:.1f}%")
        
        print("=" * 60)

def main():
    """Point d'entrée principal"""
    
    # Vérifications préliminaires
    project_root = Path(".")
    if not (project_root / "nextvision").exists():
        print("❌ Dossier 'nextvision' non trouvé.")
        print("Exécutez ce script depuis le répertoire racine du projet Nextvision.")
        sys.exit(1)
    
    # Vérification scripts nécessaires
    required_scripts = [
        "diagnose_nextvision_imports.py",
        "fix_nextvision_imports_final.py", 
        "validate_nextvision_integration.py",
        "test_integration_simple.py"
    ]
    
    missing_scripts = []
    for script in required_scripts:
        if not (project_root / script).exists():
            missing_scripts.append(script)
    
    if missing_scripts:
        print(f"❌ Scripts manquants: {', '.join(missing_scripts)}")
        print("Assurez-vous que tous les scripts de correction sont présents.")
        sys.exit(1)
    
    # Lancement orchestrateur
    orchestrator = NextvisionFixOrchestrator()
    
    try:
        success, final_score = orchestrator.run_complete_workflow()
        orchestrator.generate_final_report(success, final_score)
        
        # Code de sortie basé sur le succès
        if success and final_score >= 80.0:
            sys.exit(0)  # Succès complet
        elif success and final_score >= 70.0:
            sys.exit(1)  # Succès partiel
        else:
            sys.exit(2)  # Échec
            
    except KeyboardInterrupt:
        print("\n⚠️ Workflow interrompu par l'utilisateur")
        sys.exit(3)
    except Exception as e:
        print(f"\n❌ Erreur critique orchestrateur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(4)

if __name__ == "__main__":
    main()
