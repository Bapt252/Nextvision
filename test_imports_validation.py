#!/usr/bin/env python3

"""
🚀 Nextvision V3.0 - Test de Validation des Imports
===================================================

Script de test pour valider que tous les modules Nextvision
peuvent être importés correctement par coverage et pytest.

🎯 OBJECTIF:
- Tester l'import de tous les modules critiques
- Valider que coverage peut les détecter
- Diagnostiquer les erreurs d'import

Usage:
    python test_imports_validation.py
    python test_imports_validation.py --verbose
    python test_imports_validation.py --coverage-test

Author: NEXTEN Team - Coverage Fix
Version: 3.0.0
"""

import sys
import os
import traceback
import importlib
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

# Modules critiques à tester
CRITICAL_MODULES = [
    'nextvision',
    'nextvision.services',
    'nextvision.services.enhanced_bidirectional_scorer_v3',
    'nextvision.services.bidirectional_scorer',
    'nextvision.services.motivations_scorer_v3',
    'nextvision.services.listening_reasons_scorer_v3',
    'nextvision.services.professional_motivations_scorer_v3',
    'nextvision.services.scorers_v3',
    'nextvision.services.scorers_v3.location_transport_scorer_v3',
    'nextvision.services.google_maps_service',
    'nextvision.services.transport_calculator'
]

# Classes critiques à tester
CRITICAL_CLASSES = {
    'nextvision.services.enhanced_bidirectional_scorer_v3': 'EnhancedBidirectionalScorerV3',
    'nextvision.services.bidirectional_scorer': 'BidirectionalScorer',
    'nextvision.services.motivations_scorer_v3': 'MotivationsScorerV3',
    'nextvision.services.listening_reasons_scorer_v3': 'ListeningReasonsScorerV3',
    'nextvision.services.professional_motivations_scorer_v3': 'ProfessionalMotivationsScorerV3',
    'nextvision.services.scorers_v3.location_transport_scorer_v3': 'LocationTransportScorerV3',
    'nextvision.services.google_maps_service': 'GoogleMapsService',
    'nextvision.services.transport_calculator': 'TransportCalculator'
}

# Configuration couleurs
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def print_header():
    """Affiche l'en-tête du script."""
    print(f"{Colors.BLUE}{Colors.BOLD}🚀 NEXTVISION V3.0 - VALIDATION DES IMPORTS{Colors.END}")
    print(f"{Colors.BLUE}{'=' * 50}{Colors.END}")
    print(f"{Colors.CYAN}📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print(f"{Colors.CYAN}📂 Répertoire: {os.getcwd()}{Colors.END}")
    print()

def print_success(message):
    """Affiche un message de succès."""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    """Affiche un message d'erreur."""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    """Affiche un message d'avertissement."""
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.END}")

def print_info(message):
    """Affiche un message d'information."""
    print(f"{Colors.CYAN}📋 {message}{Colors.END}")

def print_section(title):
    """Affiche un titre de section."""
    print(f"\n{Colors.PURPLE}{Colors.BOLD}{title}{Colors.END}")
    print(f"{Colors.PURPLE}{'=' * len(title)}{Colors.END}")

# ============================================================================
# TESTS D'IMPORT
# ============================================================================

def test_basic_imports(verbose=False):
    """Teste les imports de base."""
    print_section("🔍 TEST DES IMPORTS DE BASE")
    
    success_count = 0
    error_count = 0
    
    for module_name in CRITICAL_MODULES:
        try:
            # Tentative d'import
            module = importlib.import_module(module_name)
            
            if verbose:
                print_success(f"Import réussi: {module_name}")
                if hasattr(module, '__version__'):
                    print(f"    Version: {module.__version__}")
                if hasattr(module, '__all__'):
                    print(f"    Exports: {len(module.__all__)} éléments")
            
            success_count += 1
            
        except Exception as e:
            print_error(f"Échec import: {module_name}")
            if verbose:
                print(f"    Erreur: {str(e)}")
                print(f"    Type: {type(e).__name__}")
            error_count += 1
    
    print(f"\n📊 Résultats imports de base:")
    print(f"   ✅ Réussis: {success_count}")
    print(f"   ❌ Échecs: {error_count}")
    
    return error_count == 0

def test_class_imports(verbose=False):
    """Teste les imports des classes critiques."""
    print_section("🎯 TEST DES IMPORTS DE CLASSES")
    
    success_count = 0
    error_count = 0
    
    for module_name, class_name in CRITICAL_CLASSES.items():
        try:
            # Import du module
            module = importlib.import_module(module_name)
            
            # Vérification de la classe
            if hasattr(module, class_name):
                cls = getattr(module, class_name)
                
                if verbose:
                    print_success(f"Classe disponible: {module_name}.{class_name}")
                    if hasattr(cls, '__doc__') and cls.__doc__:
                        doc_preview = cls.__doc__.split('\n')[0][:60]
                        print(f"    Description: {doc_preview}...")
                
                success_count += 1
            else:
                print_error(f"Classe manquante: {module_name}.{class_name}")
                error_count += 1
                
        except Exception as e:
            print_error(f"Erreur classe: {module_name}.{class_name}")
            if verbose:
                print(f"    Erreur: {str(e)}")
            error_count += 1
    
    print(f"\n📊 Résultats imports de classes:")
    print(f"   ✅ Réussis: {success_count}")
    print(f"   ❌ Échecs: {error_count}")
    
    return error_count == 0

def test_package_structure():
    """Teste la structure des packages."""
    print_section("📦 TEST DE LA STRUCTURE DES PACKAGES")
    
    # Test de l'existence des fichiers __init__.py critiques
    critical_inits = [
        'nextvision/__init__.py',
        'nextvision/services/__init__.py', 
        'nextvision/services/scorers_v3/__init__.py'
    ]
    
    missing_inits = []
    
    for init_file in critical_inits:
        if os.path.exists(init_file):
            print_success(f"__init__.py trouvé: {init_file}")
        else:
            print_error(f"__init__.py manquant: {init_file}")
            missing_inits.append(init_file)
    
    # Test de l'existence des modules critiques
    critical_files = [
        'nextvision/services/enhanced_bidirectional_scorer_v3.py',
        'nextvision/services/bidirectional_scorer.py',
        'nextvision/services/scorers_v3/location_transport_scorer_v3.py'
    ]
    
    missing_files = []
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            print_success(f"Module trouvé: {file_path}")
        else:
            print_error(f"Module manquant: {file_path}")
            missing_files.append(file_path)
    
    all_ok = len(missing_inits) == 0 and len(missing_files) == 0
    
    print(f"\n📊 Structure des packages:")
    print(f"   📁 __init__.py manquants: {len(missing_inits)}")
    print(f"   📄 Modules manquants: {len(missing_files)}")
    
    return all_ok

def test_coverage_compatibility():
    """Teste la compatibilité avec coverage."""
    print_section("📊 TEST DE COMPATIBILITÉ COVERAGE")
    
    try:
        # Test d'import de coverage
        import coverage
        print_success("Module coverage disponible")
        
        # Test de création d'une instance coverage
        cov = coverage.Coverage()
        print_success("Instance coverage créée")
        
        # Test d'import avec coverage actif
        cov.start()
        
        try:
            import nextvision.services.enhanced_bidirectional_scorer_v3
            print_success("Import réussi avec coverage actif")
            coverage_ok = True
        except Exception as e:
            print_error(f"Échec import avec coverage: {e}")
            coverage_ok = False
        finally:
            cov.stop()
        
        return coverage_ok
        
    except ImportError:
        print_warning("Module coverage non disponible")
        return False
    except Exception as e:
        print_error(f"Erreur test coverage: {e}")
        return False

# ============================================================================
# DIAGNOSTIC AVANCÉ
# ============================================================================

def diagnose_import_errors():
    """Diagnostique détaillé des erreurs d'import."""
    print_section("🔬 DIAGNOSTIC DÉTAILLÉ DES ERREURS")
    
    for module_name in CRITICAL_MODULES:
        try:
            importlib.import_module(module_name)
        except Exception as e:
            print_error(f"Module: {module_name}")
            print(f"   Erreur: {str(e)}")
            print(f"   Type: {type(e).__name__}")
            
            # Traceback complet pour debugging
            if '--verbose' in sys.argv:
                print("   Traceback complet:")
                traceback.print_exc()
            print()

def generate_report(results):
    """Génère un rapport de test."""
    print_section("📋 RAPPORT FINAL")
    
    all_passed = all(results.values())
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Résultat global: {'✅ TOUS LES TESTS PASSÉS' if all_passed else '❌ ÉCHECS DÉTECTÉS'}")
    
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 Nextvision est prêt pour la couverture de code !{Colors.END}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}💥 Corrections nécessaires avant couverture{Colors.END}")
    
    return all_passed

# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

def main():
    """Fonction principale du script."""
    print_header()
    
    # Configuration
    verbose = '--verbose' in sys.argv
    coverage_test = '--coverage-test' in sys.argv
    
    # Exécution des tests
    results = {}
    
    results['Structure'] = test_package_structure()
    results['Imports de base'] = test_basic_imports(verbose)
    results['Imports de classes'] = test_class_imports(verbose)
    
    if coverage_test:
        results['Compatibilité coverage'] = test_coverage_compatibility()
    
    # Diagnostic en cas d'erreurs
    if not all(results.values()):
        diagnose_import_errors()
    
    # Génération du rapport final
    success = generate_report(results)
    
    # Code de sortie
    sys.exit(0 if success else 1)

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    if '--help' in sys.argv or '-h' in sys.argv:
        print("🚀 Nextvision V3.0 - Test de Validation des Imports")
        print("")
        print("Usage:")
        print("  python test_imports_validation.py [OPTIONS]")
        print("")
        print("Options:")
        print("  --verbose       Affichage détaillé")
        print("  --coverage-test Test compatibilité coverage")
        print("  --help, -h      Affiche cette aide")
        print("")
        sys.exit(0)
    
    main()