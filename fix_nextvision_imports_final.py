#!/usr/bin/env python3
"""
🔧 SCRIPT DE CORRECTION IMPORTS NEXTVISION V3.0 - FINAL
Résout spécifiquement les imports circulaires et chemins incorrects côté Nextvision

🎯 OBJECTIF: Passer de 57.1% à 80%+ d'intégration
⚠️ SCOPE: Corrections UNIQUEMENT dans le backend Nextvision
❌ NE TOUCHE PAS: Repository Commitment- (qui fonctionne déjà)

Author: Assistant Claude  
Version: 3.0.0-final
"""

import os
import re
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import shutil
import time
from datetime import datetime

class NextvisionImportFixer:
    """🔧 Correcteur d'imports Nextvision V3.0"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.nextvision_path = self.project_root / "nextvision"
        self.corrections_made = 0
        self.files_processed = 0
        self.errors_found = []
        
        # Mapping des corrections d'imports
        self.import_corrections = {
            # Corrections de chemins services
            "from nextvision.google_maps_service import": "from nextvision.services.google_maps_service import",
            "import nextvision.google_maps_service": "import nextvision.services.google_maps_service",
            "nextvision.google_maps_service.": "nextvision.services.google_maps_service.",
            
            "from nextvision.location_transport_scorer_v3 import": "from nextvision.services.scorers_v3.location_transport_scorer_v3 import",
            "import nextvision.location_transport_scorer_v3": "import nextvision.services.scorers_v3.location_transport_scorer_v3",
            "nextvision.location_transport_scorer_v3.": "nextvision.services.scorers_v3.location_transport_scorer_v3.",
            
            "from nextvision.transport_calculator import": "from nextvision.services.transport_calculator import",
            "import nextvision.transport_calculator": "import nextvision.services.transport_calculator",
            
            # Corrections modèles transport
            "TransportMethod": "TravelMode",
            "from nextvision.models.transport_models import TransportMethod": "from nextvision.models.transport_models import TravelMode",
            
            # Corrections parsing bridge
            "from nextvision.parsing.commitment_bridge_optimized import": "from nextvision.services.parsing.commitment_bridge_optimized import",
            "from nextvision.commitment_bridge_optimized import": "from nextvision.services.parsing.commitment_bridge_optimized import",
            
            # Corrections scorer
            "from nextvision.scorers_v3.location_transport_scorer_v3 import": "from nextvision.services.scorers_v3.location_transport_scorer_v3 import",
        }
        
        # Fichiers critiques à corriger
        self.critical_files = [
            "nextvision/services/enhanced_commitment_bridge_v3_integrated.py",
            "nextvision/services/enhanced_commitment_bridge_v3.py",
            "nextvision/services/google_maps_service.py",
            "nextvision/services/transport_calculator.py",
            "nextvision/services/scorers_v3/location_transport_scorer_v3.py",
            "test_integration_simple.py",
            "test_nextvision_commitment_integration.py"
        ]
        
        print(f"🔧 Correcteur d'imports Nextvision initialisé")
        print(f"📁 Répertoire projet: {self.project_root.absolute()}")
        print(f"🎯 Fichiers critiques: {len(self.critical_files)}")

    def create_backup(self) -> str:
        """Crée une sauvegarde avant corrections"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.project_root / f"backup_imports_{timestamp}"
        
        try:
            if self.nextvision_path.exists():
                shutil.copytree(self.nextvision_path, backup_dir / "nextvision")
                print(f"✅ Sauvegarde créée: {backup_dir}")
                return str(backup_dir)
            else:
                print("⚠️ Dossier nextvision non trouvé - pas de sauvegarde")
                return ""
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            return ""

    def fix_circular_import_enhanced_bridge(self) -> bool:
        """Corrige l'import circulaire dans enhanced_commitment_bridge_v3_integrated.py"""
        
        file_path = self.nextvision_path / "services" / "enhanced_commitment_bridge_v3_integrated.py"
        
        if not file_path.exists():
            print(f"⚠️ Fichier non trouvé: {file_path}")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Corrections spécifiques pour éviter l'import circulaire
            corrections = [
                # Déplacer imports problématiques vers imports locaux
                (
                    "# Import Enhanced Bridge V3.0 original\nfrom nextvision.services.enhanced_commitment_bridge_v3 import (\n    EnhancedCommitmentBridgeV3 as OriginalBridgeV3,\n    BridgeV3Stats, BridgeV3Metrics, AutoFixEngineV3,\n    EnhancedBridgeV3Factory\n)",
                    "# Import Enhanced Bridge V3.0 original sera fait localement pour éviter import circulaire"
                ),
                
                # Corriger l'héritage pour éviter import circulaire
                (
                    "class EnhancedCommitmentBridgeV3Integrated(OriginalBridgeV3):",
                    "class EnhancedCommitmentBridgeV3Integrated:"
                ),
                
                # Ajouter import local dans __init__
                (
                    "        # Initialisation Enhanced Bridge V3.0\n        super().__init__()",
                    "        # Import local pour éviter import circulaire\n        from nextvision.services.enhanced_commitment_bridge_v3 import EnhancedCommitmentBridgeV3\n        \n        # Composition au lieu d'héritage\n        self.enhanced_bridge_v3 = EnhancedCommitmentBridgeV3()"
                ),
                
                # Corriger les appels super() en appels directs
                (
                    "await super().convert_candidat_enhanced_v3(",
                    "await self.enhanced_bridge_v3.convert_candidat_enhanced_v3("
                ),
                
                (
                    "await super().convert_entreprise_enhanced_v3(",
                    "await self.enhanced_bridge_v3.convert_entreprise_enhanced_v3("
                ),
                
                # Corriger les appels aux stats
                (
                    "super().get_enhanced_stats_v3()",
                    "self.enhanced_bridge_v3.get_enhanced_stats_v3()"
                ),
                
                (
                    "super().reset_stats_v3()",
                    "self.enhanced_bridge_v3.reset_stats_v3()"
                )
            ]
            
            # Application des corrections
            for old, new in corrections:
                if old in content:
                    content = content.replace(old, new)
                    self.corrections_made += 1
                    print(f"  ✅ Correction appliquée: import circulaire")
            
            # Sauvegarde si modifications
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Import circulaire corrigé: {file_path.name}")
                return True
            else:
                print(f"ℹ️ Aucune correction nécessaire: {file_path.name}")
                return True
                
        except Exception as e:
            error_msg = f"Erreur correction import circulaire {file_path.name}: {e}"
            self.errors_found.append(error_msg)
            print(f"❌ {error_msg}")
            return False

    def fix_file_imports(self, file_path: Path) -> bool:
        """Corrige les imports dans un fichier"""
        
        if not file_path.exists():
            print(f"⚠️ Fichier non trouvé: {file_path}")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            corrections_in_file = 0
            
            # Application des corrections d'imports
            for old_import, new_import in self.import_corrections.items():
                if old_import in content:
                    content = content.replace(old_import, new_import)
                    corrections_in_file += 1
                    print(f"  ✅ {old_import} → {new_import}")
            
            # Corrections spécifiques par fichier
            if file_path.name == "google_maps_service.py":
                # Corrections spécifiques Google Maps
                if "from nextvision.models.transport_models import TransportMethod" in content:
                    content = content.replace(
                        "from nextvision.models.transport_models import TransportMethod",
                        "from nextvision.models.transport_models import TravelMode"
                    )
                    corrections_in_file += 1
            
            elif file_path.name == "transport_calculator.py":
                # Corrections Transport Calculator
                if "TransportMethod.DRIVING" in content:
                    content = content.replace("TransportMethod.DRIVING", "TravelMode.DRIVING")
                    corrections_in_file += 1
                if "TransportMethod.TRANSIT" in content:
                    content = content.replace("TransportMethod.TRANSIT", "TravelMode.TRANSIT")
                    corrections_in_file += 1
            
            # Sauvegarde si modifications
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.corrections_made += corrections_in_file
                print(f"✅ {corrections_in_file} corrections appliquées: {file_path.name}")
                return True
            else:
                print(f"ℹ️ Aucune correction nécessaire: {file_path.name}")
                return True
                
        except Exception as e:
            error_msg = f"Erreur correction {file_path.name}: {e}"
            self.errors_found.append(error_msg)
            print(f"❌ {error_msg}")
            return False

    def fix_init_files(self) -> bool:
        """Met à jour les fichiers __init__.py pour les imports corrects"""
        
        init_files = [
            self.nextvision_path / "services" / "__init__.py",
            self.nextvision_path / "services" / "parsing" / "__init__.py", 
            self.nextvision_path / "services" / "scorers_v3" / "__init__.py"
        ]
        
        success = True
        
        for init_file in init_files:
            if init_file.exists():
                try:
                    with open(init_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Ajout imports manquants si nécessaire
                    if "services/__init__.py" in str(init_file):
                        required_imports = [
                            "from .google_maps_service import GoogleMapsService",
                            "from .transport_calculator import TransportCalculator",
                            "from .enhanced_commitment_bridge_v3_integrated import EnhancedCommitmentBridgeV3Integrated"
                        ]
                        
                        for import_line in required_imports:
                            if import_line not in content:
                                content += f"\n{import_line}"
                                self.corrections_made += 1
                        
                        with open(init_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        print(f"✅ __init__.py mis à jour: {init_file.parent.name}")
                        
                except Exception as e:
                    error_msg = f"Erreur __init__.py {init_file}: {e}"
                    self.errors_found.append(error_msg)
                    print(f"❌ {error_msg}")
                    success = False
        
        return success

    def validate_python_syntax(self, file_path: Path) -> bool:
        """Valide la syntaxe Python d'un fichier"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), str(file_path), 'exec')
            return True
        except SyntaxError as e:
            print(f"❌ Erreur syntaxe {file_path.name}: ligne {e.lineno}")
            return False
        except Exception as e:
            print(f"⚠️ Erreur validation {file_path.name}: {e}")
            return False

    def run_integration_test(self) -> Tuple[bool, float]:
        """Lance le test d'intégration simple pour vérifier le score"""
        
        test_file = self.project_root / "test_integration_simple.py"
        
        if not test_file.exists():
            print("⚠️ Fichier test_integration_simple.py non trouvé")
            return False, 0.0
        
        try:
            print("🧪 Lancement test d'intégration...")
            
            # Lancement du test
            result = subprocess.run([
                sys.executable, str(test_file)
            ], capture_output=True, text=True, timeout=120)
            
            # Analyse du résultat
            if result.returncode == 0:
                print("✅ Tests d'intégration réussis")
                # Extraction du taux de réussite depuis la sortie
                output = result.stdout
                success_rate = self._extract_success_rate(output)
                return True, success_rate
            else:
                print(f"⚠️ Tests partiellement réussis (code: {result.returncode})")
                output = result.stdout
                success_rate = self._extract_success_rate(output)
                return False, success_rate
                
        except subprocess.TimeoutExpired:
            print("⏱️ Test timeout - possibles problèmes d'imports")
            return False, 0.0
        except Exception as e:
            print(f"❌ Erreur test intégration: {e}")
            return False, 0.0

    def _extract_success_rate(self, output: str) -> float:
        """Extrait le taux de réussite de la sortie du test"""
        try:
            # Recherche du taux de réussite
            match = re.search(r'Taux de réussite: (\d+\.?\d*)%', output)
            if match:
                return float(match.group(1))
            
            # Fallback: compter les succès/échecs
            success_count = output.count('✅ Test')
            total_count = output.count('TEST:')
            
            if total_count > 0:
                return (success_count / total_count) * 100
            
            return 50.0  # Estimation par défaut
            
        except Exception:
            return 50.0

    def fix_all_imports(self) -> bool:
        """Lance toutes les corrections d'imports"""
        
        print("🚀 DÉMARRAGE CORRECTION IMPORTS NEXTVISION V3.0")
        print("=" * 60)
        
        start_time = time.time()
        
        # Sauvegarde
        backup_dir = self.create_backup()
        
        # Étape 1: Correction import circulaire critique
        print("\n🔧 ÉTAPE 1: Correction import circulaire Enhanced Bridge")
        print("-" * 50)
        success_circular = self.fix_circular_import_enhanced_bridge()
        
        # Étape 2: Correction des chemins d'imports
        print("\n🔧 ÉTAPE 2: Correction chemins d'imports")
        print("-" * 50)
        
        files_success = 0
        for file_rel_path in self.critical_files:
            file_path = self.project_root / file_rel_path
            print(f"\n🔍 Traitement: {file_rel_path}")
            
            if self.fix_file_imports(file_path):
                files_success += 1
            self.files_processed += 1
        
        # Étape 3: Mise à jour __init__.py
        print("\n🔧 ÉTAPE 3: Mise à jour fichiers __init__.py")
        print("-" * 50)
        init_success = self.fix_init_files()
        
        # Étape 4: Validation syntaxe
        print("\n🔧 ÉTAPE 4: Validation syntaxe Python")
        print("-" * 50)
        
        syntax_errors = 0
        for file_rel_path in self.critical_files:
            file_path = self.project_root / file_rel_path
            if file_path.exists():
                if not self.validate_python_syntax(file_path):
                    syntax_errors += 1
        
        # Étape 5: Test d'intégration
        print("\n🧪 ÉTAPE 5: Test d'intégration")
        print("-" * 50)
        test_success, success_rate = self.run_integration_test()
        
        # Rapport final
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("📊 RAPPORT FINAL CORRECTION IMPORTS")
        print("=" * 60)
        
        print(f"⏱️ Durée: {duration:.2f}s")
        print(f"📁 Fichiers traités: {self.files_processed}")
        print(f"🔧 Corrections appliquées: {self.corrections_made}")
        print(f"❌ Erreurs syntaxe: {syntax_errors}")
        print(f"🧪 Score intégration: {success_rate:.1f}%")
        
        # Statut global
        overall_success = (
            success_circular and 
            files_success >= len(self.critical_files) * 0.8 and
            syntax_errors == 0 and
            success_rate >= 80.0
        )
        
        if overall_success:
            print("\n🎉 CORRECTION RÉUSSIE!")
            print("✅ Imports circulaires résolus")
            print("✅ Chemins d'imports corrigés") 
            print("✅ Syntaxe Python validée")
            print(f"✅ Score intégration: {success_rate:.1f}% (>= 80%)")
            print("\n🚀 Prochaines étapes:")
            print("1. Lancer: python3 test_nextvision_commitment_integration.py")
            print("2. Tests avancés: python3 demo_nextvision_v3_complete.py")
            
        else:
            print("\n⚠️ CORRECTION PARTIELLE")
            if not success_circular:
                print("❌ Import circulaire non résolu")
            if files_success < len(self.critical_files) * 0.8:
                print(f"❌ Trop de fichiers échoués: {files_success}/{len(self.critical_files)}")
            if syntax_errors > 0:
                print(f"❌ Erreurs syntaxe: {syntax_errors}")
            if success_rate < 80.0:
                print(f"❌ Score intégration insuffisant: {success_rate:.1f}% (< 80%)")
            
            print("\n🔧 Actions recommandées:")
            print("1. Vérifier les erreurs ci-dessus")
            print("2. Corriger manuellement si nécessaire")
            print("3. Relancer: python3 fix_nextvision_imports_final.py")
        
        if self.errors_found:
            print(f"\n❌ ERREURS DÉTECTÉES ({len(self.errors_found)}):")
            for error in self.errors_found:
                print(f"   • {error}")
        
        if backup_dir:
            print(f"\n💾 Sauvegarde disponible: {backup_dir}")
        
        print("=" * 60)
        
        return overall_success

def main():
    """Point d'entrée principal"""
    
    # Vérification environnement
    if not Path("nextvision").exists():
        print("❌ Dossier 'nextvision' non trouvé.")
        print("Assurez-vous d'être dans le répertoire racine du projet Nextvision.")
        sys.exit(1)
    
    # Lancement correction
    fixer = NextvisionImportFixer()
    
    try:
        success = fixer.fix_all_imports()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Correction interrompue par l'utilisateur")
        sys.exit(2)
    except Exception as e:
        print(f"\n❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)

if __name__ == "__main__":
    main()
