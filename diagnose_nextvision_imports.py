#!/usr/bin/env python3
"""
🔍 DIAGNOSTIC RAPIDE IMPORTS NEXTVISION V3.0
Identifie précisément les problèmes d'imports avant correction

🎯 OBJECTIF: Diagnostic complet en < 30 secondes
✅ FOCUS: Identification problèmes spécifiques

Author: Assistant Claude
Version: 1.0.0-diagnostic
"""

import os
import sys
import re
import traceback
from pathlib import Path
from typing import Dict, List, Set, Tuple
import time

class NextvisionImportDiagnostic:
    """🔍 Diagnostic rapide des imports Nextvision"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.nextvision_path = self.project_root / "nextvision"
        
        self.issues_found: List[Dict] = []
        self.import_map: Dict[str, List[str]] = {}
        self.circular_imports: List[Tuple[str, str]] = []
        self.missing_files: List[str] = []
        self.syntax_errors: List[Tuple[str, str]] = []
        
        print(f"🔍 Diagnostic imports Nextvision initialisé")

    def scan_import_statements(self, file_path: Path) -> List[str]:
        """Extrait tous les imports d'un fichier"""
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Patterns d'imports
            patterns = [
                r'^from\s+(nextvision\.[^\s]+)\s+import',
                r'^import\s+(nextvision\.[^\s]+)',
                r'^\s*from\s+(nextvision\.[^\s]+)\s+import',
                r'^\s*import\s+(nextvision\.[^\s]+)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                imports.extend(matches)
            
            return imports
            
        except Exception as e:
            self.syntax_errors.append((str(file_path), str(e)))
            return []

    def detect_incorrect_paths(self) -> List[Dict]:
        """Détecte les chemins d'imports incorrects"""
        
        incorrect_patterns = [
            # Patterns incorrects → Patterns corrects
            {
                'pattern': r'nextvision\.google_maps_service',
                'correct': 'nextvision.services.google_maps_service',
                'description': 'Google Maps Service chemin incorrect'
            },
            {
                'pattern': r'nextvision\.location_transport_scorer_v3',
                'correct': 'nextvision.services.scorers_v3.location_transport_scorer_v3',
                'description': 'Location Transport Scorer chemin incorrect'
            },
            {
                'pattern': r'nextvision\.transport_calculator',
                'correct': 'nextvision.services.transport_calculator',
                'description': 'Transport Calculator chemin incorrect'
            },
            {
                'pattern': r'nextvision\.commitment_bridge_optimized',
                'correct': 'nextvision.services.parsing.commitment_bridge_optimized',
                'description': 'Commitment Bridge chemin incorrect'
            },
            {
                'pattern': r'TransportMethod',
                'correct': 'TravelMode',
                'description': 'Ancien modèle TransportMethod utilisé'
            }
        ]
        
        issues = []
        
        # Scan tous les fichiers Python
        python_files = list(self.project_root.glob("**/*.py"))
        
        for file_path in python_files:
            if "backup" in str(file_path):  # Ignore backups
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern_info in incorrect_patterns:
                    pattern = pattern_info['pattern']
                    if re.search(pattern, content):
                        issues.append({
                            'type': 'incorrect_path',
                            'file': str(file_path.relative_to(self.project_root)),
                            'pattern': pattern,
                            'correct': pattern_info['correct'],
                            'description': pattern_info['description'],
                            'severity': 'high'
                        })
            
            except Exception:
                continue
        
        return issues

    def detect_circular_imports(self) -> List[Dict]:
        """Détecte les imports circulaires potentiels"""
        
        # Fichiers à risque d'imports circulaires
        critical_files = [
            "nextvision/services/enhanced_commitment_bridge_v3_integrated.py",
            "nextvision/services/enhanced_commitment_bridge_v3.py",
        ]
        
        issues = []
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                continue
            
            imports = self.scan_import_statements(full_path)
            
            # Détection patterns circulaires
            for import_stmt in imports:
                if "enhanced_commitment_bridge" in import_stmt:
                    # Import circulaire potentiel détecté
                    issues.append({
                        'type': 'circular_import',
                        'file': file_path,
                        'import': import_stmt,
                        'description': 'Import circulaire Enhanced Bridge détecté',
                        'severity': 'critical'
                    })
        
        return issues

    def detect_missing_files(self) -> List[Dict]:
        """Détecte les fichiers manquants référencés"""
        
        expected_files = [
            "nextvision/services/google_maps_service.py",
            "nextvision/services/transport_calculator.py",
            "nextvision/services/scorers_v3/location_transport_scorer_v3.py",
            "nextvision/services/parsing/commitment_bridge_optimized.py",
            "nextvision/services/enhanced_commitment_bridge_v3.py",
            "nextvision/services/enhanced_commitment_bridge_v3_integrated.py",
            "nextvision/models/transport_models.py",
            "nextvision/models/extended_matching_models_v3.py"
        ]
        
        issues = []
        
        for file_path in expected_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                issues.append({
                    'type': 'missing_file',
                    'file': file_path,
                    'description': f'Fichier critique manquant: {file_path}',
                    'severity': 'high'
                })
        
        return issues

    def test_quick_imports(self) -> List[Dict]:
        """Test rapide des imports critiques"""
        
        critical_imports = [
            ("nextvision.services.google_maps_service", "GoogleMapsService"),
            ("nextvision.services.transport_calculator", "TransportCalculator"),
            ("nextvision.services.scorers_v3.location_transport_scorer_v3", "LocationTransportScorerV3"),
            ("nextvision.models.transport_models", "TravelMode"),
        ]
        
        issues = []
        
        # Ajout chemin projet
        project_str = str(self.project_root.absolute())
        if project_str not in sys.path:
            sys.path.insert(0, project_str)
        
        for module_name, class_name in critical_imports:
            try:
                # Test import
                import importlib
                module = importlib.import_module(module_name)
                
                # Test classe
                if not hasattr(module, class_name):
                    issues.append({
                        'type': 'import_error',
                        'module': module_name,
                        'description': f'Classe {class_name} manquante dans {module_name}',
                        'severity': 'high'
                    })
                
            except ImportError as e:
                issues.append({
                    'type': 'import_error',
                    'module': module_name,
                    'error': str(e),
                    'description': f'Impossible d\'importer {module_name}: {e}',
                    'severity': 'critical'
                })
            except Exception as e:
                issues.append({
                    'type': 'import_error',
                    'module': module_name,
                    'error': str(e),
                    'description': f'Erreur inattendue {module_name}: {e}',
                    'severity': 'medium'
                })
        
        return issues

    def run_comprehensive_diagnostic(self) -> Dict:
        """Lance un diagnostic complet"""
        
        print("🚀 LANCEMENT DIAGNOSTIC COMPLET")
        print("=" * 50)
        
        start_time = time.time()
        
        # Diagnostic par catégorie
        print("🔍 Analyse chemins incorrects...")
        incorrect_paths = self.detect_incorrect_paths()
        
        print("🔄 Détection imports circulaires...")
        circular_imports = self.detect_circular_imports()
        
        print("📁 Vérification fichiers manquants...")
        missing_files = self.detect_missing_files()
        
        print("📦 Test imports rapides...")
        import_errors = self.test_quick_imports()
        
        # Compilation résultats
        all_issues = incorrect_paths + circular_imports + missing_files + import_errors
        
        # Classement par sévérité
        critical_issues = [i for i in all_issues if i.get('severity') == 'critical']
        high_issues = [i for i in all_issues if i.get('severity') == 'high']
        medium_issues = [i for i in all_issues if i.get('severity') == 'medium']
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Rapport
        print(f"\n⏱️ Diagnostic terminé en {duration:.2f}s")
        print(f"🔍 Issues détectées: {len(all_issues)}")
        
        return {
            'duration': duration,
            'total_issues': len(all_issues),
            'critical_issues': critical_issues,
            'high_issues': high_issues,
            'medium_issues': medium_issues,
            'all_issues': all_issues
        }

    def print_diagnostic_report(self, results: Dict):
        """Affiche le rapport de diagnostic"""
        
        print("\n" + "=" * 60)
        print("📊 RAPPORT DIAGNOSTIC NEXTVISION V3.0")
        print("=" * 60)
        
        critical = results['critical_issues']
        high = results['high_issues']
        medium = results['medium_issues']
        total = results['total_issues']
        
        print(f"📋 Issues total: {total}")
        print(f"🚨 Critiques: {len(critical)}")
        print(f"⚠️ Importantes: {len(high)}")
        print(f"ℹ️ Moyennes: {len(medium)}")
        
        # Issues critiques
        if critical:
            print(f"\n🚨 ISSUES CRITIQUES ({len(critical)}):")
            for i, issue in enumerate(critical, 1):
                print(f"{i}. {issue['description']}")
                if 'file' in issue:
                    print(f"   📁 Fichier: {issue['file']}")
                if 'error' in issue:
                    print(f"   ❌ Erreur: {issue['error']}")
        
        # Issues importantes
        if high:
            print(f"\n⚠️ ISSUES IMPORTANTES ({len(high)}):")
            for i, issue in enumerate(high[:5], 1):  # Top 5
                print(f"{i}. {issue['description']}")
                if 'file' in issue:
                    print(f"   📁 Fichier: {issue['file']}")
                if 'correct' in issue:
                    print(f"   ✅ Correction: {issue['correct']}")
            if len(high) > 5:
                print(f"   ... et {len(high) - 5} autres issues importantes")
        
        # Recommandations
        print(f"\n🎯 RECOMMANDATIONS:")
        
        if len(critical) > 0:
            print("1. 🚨 URGENT: Résoudre les issues critiques d'abord")
            print("   • Imports circulaires bloquent l'intégration")
            print("   • Lancer: python3 fix_nextvision_imports_final.py")
        
        if len(high) > 0:
            print("2. ⚠️ IMPORTANT: Corriger les chemins d'imports")
            print("   • Plusieurs modules utilisent d'anciens chemins")
            print("   • Remplacer TransportMethod par TravelMode")
        
        if len(medium) > 0:
            print("3. ℹ️ OPTIMISATION: Issues moyennes à corriger ensuite")
        
        print("\n📋 PROCHAINES ÉTAPES:")
        if total == 0:
            print("✅ Aucun problème détecté - intégration semble OK")
            print("🧪 Lancer: python3 validate_nextvision_integration.py")
        elif len(critical) + len(high) <= 5:
            print("🔧 Peu d'issues - correction rapide possible")
            print("1. Lancer: python3 fix_nextvision_imports_final.py")
            print("2. Valider: python3 validate_nextvision_integration.py")
        else:
            print("🛠️ Nombreuses issues - correction systématique nécessaire")
            print("1. Corriger imports: python3 fix_nextvision_imports_final.py")
            print("2. Vérifier structure: dossiers/fichiers manquants")
            print("3. Relancer diagnostic: python3 diagnose_nextvision_imports.py")
        
        # Score estimé
        if total == 0:
            estimated_score = 95.0
        elif len(critical) == 0 and len(high) <= 2:
            estimated_score = 85.0
        elif len(critical) <= 1 and len(high) <= 5:
            estimated_score = 70.0
        elif len(critical) <= 2:
            estimated_score = 55.0
        else:
            estimated_score = 30.0
        
        print(f"\n📊 SCORE INTÉGRATION ESTIMÉ: {estimated_score:.1f}%")
        
        if estimated_score >= 80:
            print("🎉 Intégration probablement fonctionnelle")
        elif estimated_score >= 60:
            print("⚠️ Intégration partielle - corrections mineures nécessaires")
        else:
            print("❌ Intégration problématique - corrections majeures nécessaires")
        
        print("=" * 60)

def main():
    """Point d'entrée principal"""
    
    # Vérification environnement
    if not Path("nextvision").exists():
        print("❌ Dossier 'nextvision' non trouvé.")
        print("Exécutez ce script depuis le répertoire racine du projet Nextvision.")
        sys.exit(1)
    
    # Lancement diagnostic
    diagnostic = NextvisionImportDiagnostic()
    
    try:
        results = diagnostic.run_comprehensive_diagnostic()
        diagnostic.print_diagnostic_report(results)
        
        # Code de sortie basé sur la sévérité
        critical_count = len(results['critical_issues'])
        high_count = len(results['high_issues'])
        
        if critical_count == 0 and high_count == 0:
            sys.exit(0)  # Aucun problème
        elif critical_count == 0 and high_count <= 3:
            sys.exit(1)  # Problèmes mineurs
        elif critical_count <= 1:
            sys.exit(2)  # Problèmes modérés
        else:
            sys.exit(3)  # Problèmes majeurs
            
    except KeyboardInterrupt:
        print("\n⚠️ Diagnostic interrompu par l'utilisateur")
        sys.exit(4)
    except Exception as e:
        print(f"\n❌ Erreur diagnostic: {e}")
        traceback.print_exc()
        sys.exit(5)

if __name__ == "__main__":
    main()
