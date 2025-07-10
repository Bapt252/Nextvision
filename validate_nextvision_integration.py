#!/usr/bin/env python3
"""
🔍 SCRIPT DE VALIDATION POST-CORRECTION NEXTVISION V3.0
Valide que les corrections d'imports ont bien résolu les problèmes

🎯 OBJECTIF: Confirmer que le score d'intégration ≥ 80%
✅ FOCUS: Validation spécifique des corrections appliquées

Author: Assistant Claude
Version: 3.0.0-validation
"""

import os
import sys
import importlib
import traceback
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import time
from datetime import datetime

class NextvisionIntegrationValidator:
    """🔍 Validateur d'intégration Nextvision V3.0"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.nextvision_path = self.project_root / "nextvision"
        
        self.validation_results: Dict[str, bool] = {}
        self.import_tests: Dict[str, bool] = {}
        self.performance_metrics: Dict[str, float] = {}
        self.detailed_errors: List[str] = []
        
        # Tests d'imports critiques
        self.critical_imports = {
            "nextvision.services.google_maps_service": "GoogleMapsService",
            "nextvision.services.transport_calculator": "TransportCalculator",
            "nextvision.services.scorers_v3.location_transport_scorer_v3": "LocationTransportScorerV3",
            "nextvision.services.parsing.commitment_bridge_optimized": "CommitmentParsingBridge",
            "nextvision.services.enhanced_commitment_bridge_v3": "EnhancedCommitmentBridgeV3",
            "nextvision.models.transport_models": "TravelMode",
            "nextvision.models.extended_matching_models_v3": "ExtendedMatchingProfile"
        }
        
        print(f"🔍 Validateur d'intégration Nextvision initialisé")
        print(f"📁 Répertoire projet: {self.project_root.absolute()}")

    def validate_project_structure(self) -> bool:
        """Valide la structure du projet"""
        
        print("🏗️ VALIDATION STRUCTURE PROJET")
        print("-" * 40)
        
        required_paths = [
            self.nextvision_path,
            self.nextvision_path / "services",
            self.nextvision_path / "services" / "parsing",
            self.nextvision_path / "services" / "scorers_v3",
            self.nextvision_path / "models",
        ]
        
        missing_paths = []
        for path in required_paths:
            if path.exists():
                print(f"✅ {path.relative_to(self.project_root)}")
            else:
                print(f"❌ {path.relative_to(self.project_root)} (MANQUANT)")
                missing_paths.append(str(path))
        
        # Fichiers critiques
        critical_files = [
            "nextvision/services/enhanced_commitment_bridge_v3_integrated.py",
            "nextvision/services/google_maps_service.py",
            "nextvision/services/transport_calculator.py",
            "nextvision/services/scorers_v3/location_transport_scorer_v3.py",
            "nextvision/services/parsing/commitment_bridge_optimized.py"
        ]
        
        missing_files = []
        for file_path in critical_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} (MANQUANT)")
                missing_files.append(file_path)
        
        structure_valid = len(missing_paths) == 0 and len(missing_files) == 0
        self.validation_results["structure"] = structure_valid
        
        if structure_valid:
            print("✅ Structure projet validée")
        else:
            print(f"❌ Structure incomplète: {len(missing_paths)} dossiers, {len(missing_files)} fichiers manquants")
            
        return structure_valid

    def validate_critical_imports(self) -> bool:
        """Valide les imports critiques"""
        
        print("\n📦 VALIDATION IMPORTS CRITIQUES")
        print("-" * 40)
        
        # Ajout du répertoire projet au Python path
        project_str = str(self.project_root.absolute())
        if project_str not in sys.path:
            sys.path.insert(0, project_str)
        
        successful_imports = 0
        total_imports = len(self.critical_imports)
        
        for module_name, expected_class in self.critical_imports.items():
            try:
                start_time = time.time()
                
                # Import du module
                module = importlib.import_module(module_name)
                
                # Vérification de la classe/objet attendu
                if hasattr(module, expected_class):
                    import_time = (time.time() - start_time) * 1000
                    self.performance_metrics[f"import_{module_name}"] = import_time
                    
                    print(f"✅ {module_name}.{expected_class} ({import_time:.2f}ms)")
                    self.import_tests[module_name] = True
                    successful_imports += 1
                else:
                    print(f"❌ {module_name}: classe '{expected_class}' non trouvée")
                    self.import_tests[module_name] = False
                    self.detailed_errors.append(f"Classe manquante: {module_name}.{expected_class}")
                
            except ImportError as e:
                print(f"❌ {module_name}: erreur import - {e}")
                self.import_tests[module_name] = False
                self.detailed_errors.append(f"Import error {module_name}: {e}")
                
            except Exception as e:
                print(f"❌ {module_name}: erreur inattendue - {e}")
                self.import_tests[module_name] = False
                self.detailed_errors.append(f"Unexpected error {module_name}: {e}")
        
        imports_valid = successful_imports >= total_imports * 0.9  # 90% de réussite minimum
        self.validation_results["imports"] = imports_valid
        
        print(f"\n📊 Résultat imports: {successful_imports}/{total_imports} ({(successful_imports/total_imports)*100:.1f}%)")
        
        return imports_valid

    def validate_no_circular_imports(self) -> bool:
        """Valide l'absence d'imports circulaires"""
        
        print("\n🔄 VALIDATION IMPORTS CIRCULAIRES")
        print("-" * 40)
        
        # Test import du bridge intégré (anciennement problématique)
        try:
            start_time = time.time()
            
            from nextvision.services.enhanced_commitment_bridge_v3_integrated import (
                EnhancedCommitmentBridgeV3Integrated,
                IntegratedBridgeFactory
            )
            
            import_time = (time.time() - start_time) * 1000
            print(f"✅ Enhanced Bridge V3 Intégré importé ({import_time:.2f}ms)")
            
            # Test instanciation
            bridge = IntegratedBridgeFactory.create_development_integrated_bridge()
            print("✅ Bridge intégré instancié")
            
            self.validation_results["circular_imports"] = True
            return True
            
        except ImportError as e:
            print(f"❌ Import circulaire détecté: {e}")
            self.detailed_errors.append(f"Circular import: {e}")
            self.validation_results["circular_imports"] = False
            return False
            
        except Exception as e:
            print(f"❌ Erreur bridge intégré: {e}")
            self.detailed_errors.append(f"Bridge error: {e}")
            self.validation_results["circular_imports"] = False
            return False

    def validate_model_consistency(self) -> bool:
        """Valide la cohérence des modèles (ex: TravelMode vs TravelMode)"""
        
        print("\n🎯 VALIDATION COHÉRENCE MODÈLES")
        print("-" * 40)
        
        try:
            # Test TravelMode (nouveau modèle)
            from nextvision.models.transport_models import TravelMode
            
            # Vérification énums
            expected_modes = ['DRIVING', 'TRANSIT', 'WALKING', 'BICYCLING']
            available_modes = [mode.name for mode in TravelMode]
            
            missing_modes = [mode for mode in expected_modes if mode not in available_modes]
            
            if len(missing_modes) == 0:
                print(f"✅ TravelMode complet: {available_modes}")
                self.validation_results["model_consistency"] = True
                return True
            else:
                print(f"❌ TravelMode incomplet: manque {missing_modes}")
                self.validation_results["model_consistency"] = False
                return False
                
        except ImportError as e:
            print(f"❌ Modèle transport non trouvé: {e}")
            self.detailed_errors.append(f"Transport model: {e}")
            self.validation_results["model_consistency"] = False
            return False

    def validate_service_instantiation(self) -> bool:
        """Valide l'instanciation des services principaux"""
        
        print("\n🛠️ VALIDATION INSTANCIATION SERVICES")
        print("-" * 40)
        
        successful_services = 0
        total_services = 3  # Nombre de services critiques
        
        # Test Google Maps Service
        try:
            from nextvision.services.google_maps_service import GoogleMapsService
            service = GoogleMapsService("test_key")
            print("✅ GoogleMapsService instancié")
            successful_services += 1
        except Exception as e:
            print(f"❌ GoogleMapsService: {e}")
            self.detailed_errors.append(f"GoogleMapsService: {e}")
        
        # Test Transport Calculator
        try:
            from nextvision.services.transport_calculator import TransportCalculator
            calculator = TransportCalculator()
            print("✅ TransportCalculator instancié")
            successful_services += 1
        except Exception as e:
            print(f"❌ TransportCalculator: {e}")
            self.detailed_errors.append(f"TransportCalculator: {e}")
        
        # Test Location Transport Scorer
        try:
            from nextvision.services.scorers_v3.location_transport_scorer_v3 import LocationTransportScorerV3
            scorer = LocationTransportScorerV3()
            print("✅ LocationTransportScorerV3 instancié")
            successful_services += 1
        except Exception as e:
            print(f"❌ LocationTransportScorerV3: {e}")
            self.detailed_errors.append(f"LocationTransportScorerV3: {e}")
        
        services_valid = successful_services >= total_services * 0.8  # 80% de réussite
        self.validation_results["service_instantiation"] = services_valid
        
        print(f"\n📊 Services: {successful_services}/{total_services} ({(successful_services/total_services)*100:.1f}%)")
        
        return services_valid

    def run_integration_test(self) -> Tuple[bool, float]:
        """Lance le test d'intégration officiel"""
        
        print("\n🧪 LANCEMENT TEST INTÉGRATION OFFICIEL")
        print("-" * 40)
        
        test_file = self.project_root / "test_integration_simple.py"
        
        if not test_file.exists():
            print("❌ test_integration_simple.py non trouvé")
            return False, 0.0
        
        try:
            # Lancement test avec timeout
            result = subprocess.run([
                sys.executable, str(test_file)
            ], capture_output=True, text=True, timeout=180)
            
            # Analyse sortie
            output = result.stdout + result.stderr
            
            # Extraction score
            import re
            match = re.search(r'Taux de réussite: (\d+\.?\d*)%', output)
            if match:
                score = float(match.group(1))
            else:
                # Estimation basée sur les succès/échecs
                success_count = output.count('✅')
                total_count = max(output.count('TEST:'), 7)  # 7 tests attendus
                score = (success_count / total_count) * 100 if total_count > 0 else 0
            
            test_success = result.returncode == 0 and score >= 80.0
            
            if test_success:
                print(f"✅ Test intégration réussi: {score:.1f}%")
            else:
                print(f"⚠️ Test intégration partiel: {score:.1f}% (code: {result.returncode})")
                
                # Affichage erreurs si disponibles
                if result.stderr:
                    print("Erreurs détectées:")
                    for line in result.stderr.split('\n')[:5]:  # Premières erreurs
                        if line.strip():
                            print(f"  • {line.strip()}")
            
            self.validation_results["integration_test"] = test_success
            return test_success, score
            
        except subprocess.TimeoutExpired:
            print("⏱️ Test timeout (>3min) - possibles imports bloquants")
            self.validation_results["integration_test"] = False
            return False, 0.0
            
        except Exception as e:
            print(f"❌ Erreur test: {e}")
            self.validation_results["integration_test"] = False
            return False, 0.0

    def calculate_integration_score(self) -> float:
        """Calcule le score d'intégration final"""
        
        # Pondération des validations
        weights = {
            "structure": 0.15,           # 15% - Structure projet
            "imports": 0.25,             # 25% - Imports critiques
            "circular_imports": 0.20,    # 20% - Absence imports circulaires
            "model_consistency": 0.15,   # 15% - Cohérence modèles
            "service_instantiation": 0.15, # 15% - Services instanciables
            "integration_test": 0.10     # 10% - Test intégration
        }
        
        total_score = 0.0
        
        for validation, passed in self.validation_results.items():
            if validation in weights:
                contribution = weights[validation] * (100 if passed else 0)
                total_score += contribution
                print(f"  {validation}: {'✅' if passed else '❌'} ({contribution:.1f} points)")
        
        return total_score

    def generate_action_plan(self, score: float) -> List[str]:
        """Génère un plan d'action basé sur les validations échouées"""
        
        actions = []
        
        if not self.validation_results.get("structure", False):
            actions.append("🏗️ Restaurer structure projet: fichiers/dossiers manquants")
        
        if not self.validation_results.get("imports", False):
            actions.append("📦 Corriger imports critiques: vérifier chemins modules")
            actions.append("🔧 Lancer: python3 fix_nextvision_imports_final.py")
        
        if not self.validation_results.get("circular_imports", False):
            actions.append("🔄 Résoudre imports circulaires: enhanced_commitment_bridge_v3_integrated.py")
            actions.append("🛠️ Transformer héritage en composition")
        
        if not self.validation_results.get("model_consistency", False):
            actions.append("🎯 Corriger modèles: TravelMode → TravelMode")
        
        if not self.validation_results.get("service_instantiation", False):
            actions.append("🛠️ Corriger instanciation services: vérifier dépendances")
        
        if score < 80.0:
            actions.append("🧪 Relancer validation: python3 validate_nextvision_integration.py")
            actions.append("📊 Objectif: atteindre score ≥ 80%")
        
        return actions

    def run_complete_validation(self) -> Tuple[bool, float]:
        """Lance la validation complète"""
        
        print("🔍 VALIDATION COMPLÈTE INTÉGRATION NEXTVISION V3.0")
        print("=" * 60)
        
        start_time = time.time()
        
        # Validation par étapes
        validations = [
            ("Structure Projet", self.validate_project_structure),
            ("Imports Critiques", self.validate_critical_imports),
            ("Imports Circulaires", self.validate_no_circular_imports),
            ("Cohérence Modèles", self.validate_model_consistency),
            ("Instanciation Services", self.validate_service_instantiation)
        ]
        
        # Exécution validations
        for validation_name, validation_func in validations:
            try:
                validation_func()
            except Exception as e:
                print(f"❌ Erreur validation {validation_name}: {e}")
                self.validation_results[validation_name.lower().replace(" ", "_")] = False
                self.detailed_errors.append(f"{validation_name}: {e}")
        
        # Test intégration final
        test_success, test_score = self.run_integration_test()
        
        # Calcul score final
        validation_score = self.calculate_integration_score()
        
        # Score final (moyenne pondérée)
        final_score = (validation_score * 0.7) + (test_score * 0.3)
        
        # Rapport final
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("📊 RAPPORT VALIDATION FINAL")
        print("=" * 60)
        
        print(f"⏱️ Durée validation: {duration:.2f}s")
        print(f"📦 Imports testés: {len(self.critical_imports)}")
        print(f"🛠️ Validations effectuées: {len(self.validation_results)}")
        
        print(f"\n📊 SCORES:")
        print(f"  • Score validation: {validation_score:.1f}%")
        print(f"  • Score test intégration: {test_score:.1f}%")
        print(f"  • Score final: {final_score:.1f}%")
        
        # Détail des validations
        print(f"\n🔍 DÉTAIL VALIDATIONS:")
        self.calculate_integration_score()  # Affiche le détail
        
        # Statut final
        success = final_score >= 80.0
        
        if success:
            print(f"\n🎉 VALIDATION RÉUSSIE! Score: {final_score:.1f}% (≥ 80%)")
            print("✅ Intégration Nextvision V3.0 fonctionnelle")
            print("✅ Imports correctement résolus")
            print("✅ Services instanciables")
            print("\n🚀 Prochaines étapes:")
            print("1. Tests complets: python3 test_nextvision_commitment_integration.py")
            print("2. Démo Transport Intelligence: python3 demo_transport_intelligence.py")
            print("3. Déploiement: python3 deploy_nextvision_v2.sh")
            
        else:
            print(f"\n⚠️ VALIDATION PARTIELLE. Score: {final_score:.1f}% (< 80%)")
            
            # Plan d'action
            actions = self.generate_action_plan(final_score)
            if actions:
                print("\n🔧 PLAN D'ACTION:")
                for i, action in enumerate(actions, 1):
                    print(f"{i}. {action}")
        
        # Erreurs détaillées
        if self.detailed_errors:
            print(f"\n❌ ERREURS DÉTAILLÉES ({len(self.detailed_errors)}):")
            for i, error in enumerate(self.detailed_errors[:10], 1):  # Premières 10
                print(f"{i}. {error}")
            if len(self.detailed_errors) > 10:
                print(f"   ... et {len(self.detailed_errors) - 10} autres erreurs")
        
        print("=" * 60)
        
        return success, final_score

def main():
    """Point d'entrée principal"""
    
    # Vérification environnement
    if not Path("nextvision").exists():
        print("❌ Dossier 'nextvision' non trouvé.")
        print("Exécutez ce script depuis le répertoire racine du projet Nextvision.")
        sys.exit(1)
    
    # Lancement validation
    validator = NextvisionIntegrationValidator()
    
    try:
        success, score = validator.run_complete_validation()
        
        # Code de sortie
        if success:
            sys.exit(0)  # Succès complet
        elif score >= 60.0:
            sys.exit(1)  # Succès partiel
        else:
            sys.exit(2)  # Échec
            
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrompue par l'utilisateur")
        sys.exit(3)
    except Exception as e:
        print(f"\n❌ Erreur critique validation: {e}")
        traceback.print_exc()
        sys.exit(4)

if __name__ == "__main__":
    main()
