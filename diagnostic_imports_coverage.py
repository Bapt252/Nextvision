#!/usr/bin/env python3
"""
🔍 Nextvision V3.0 - Diagnostic Import Coverage Fix
==================================================

Script de diagnostic avancé pour identifier et corriger 
les erreurs d'import qui empêchent d'atteindre 70% de couverture.

Objectif: Passer de 59% à >70% de couverture de code.

Author: NEXTEN Team
Version: 3.0.0 - Final Coverage Fix
"""

import sys
import os
import traceback
import importlib
from typing import Dict, List, Tuple, Any

def test_import_detailed(module_path: str, class_name: str = None) -> Tuple[bool, str, str]:
    """
    🔍 Test import détaillé avec capture d'erreur complète
    
    Returns:
        (success, error_type, full_traceback)
    """
    try:
        # Import du module
        module = importlib.import_module(module_path)
        
        # Test import classe spécifique si demandée
        if class_name:
            if hasattr(module, class_name):
                class_obj = getattr(module, class_name)
                return True, "SUCCESS", f"✅ {module_path}.{class_name} importé avec succès"
            else:
                return False, "CLASS_NOT_FOUND", f"❌ Classe {class_name} non trouvée dans {module_path}"
        
        return True, "SUCCESS", f"✅ Module {module_path} importé avec succès"
        
    except ImportError as e:
        return False, "IMPORT_ERROR", f"❌ ImportError: {str(e)}\n{traceback.format_exc()}"
    except ModuleNotFoundError as e:
        return False, "MODULE_NOT_FOUND", f"❌ ModuleNotFoundError: {str(e)}\n{traceback.format_exc()}"
    except Exception as e:
        return False, "OTHER_ERROR", f"❌ Erreur inattendue: {str(e)}\n{traceback.format_exc()}"

def diagnose_failing_imports() -> Dict[str, Any]:
    """
    🩺 Diagnostic complet des imports qui échouent
    """
    print("🔍 DIAGNOSTIC IMPORTS NEXTVISION V3.0")
    print("=" * 60)
    
    # Modules à tester (selon erreurs rapportées)
    modules_to_test = [
        ("nextvision.services.bidirectional_scorer", "BidirectionalScorer"),
        ("nextvision.services.motivations_scorer_v3", "MotivationsScorerV3"),
        ("nextvision.services.listening_reasons_scorer_v3", "ListeningReasonsScorerV3"),
        ("nextvision.services.professional_motivations_scorer_v3", "ProfessionalMotivationsScorerV3"),
        ("nextvision.services.scorers_v3", None),
        ("nextvision.services.scorers_v3.location_transport_scorer_v3", "LocationTransportScorerV3"),
    ]
    
    results = {}
    failing_modules = []
    
    for module_path, class_name in modules_to_test:
        print(f"\n🔍 Test: {module_path}" + (f".{class_name}" if class_name else ""))
        
        success, error_type, details = test_import_detailed(module_path, class_name)
        
        results[module_path] = {
            "success": success,
            "error_type": error_type,
            "details": details,
            "class_name": class_name
        }
        
        if success:
            print(f"  {details}")
        else:
            print(f"  {details}")
            failing_modules.append((module_path, class_name, error_type))
    
    return {
        "results": results,
        "failing_modules": failing_modules,
        "total_tested": len(modules_to_test),
        "successful": sum(1 for r in results.values() if r["success"]),
        "failed": sum(1 for r in results.values() if not r["success"])
    }

def analyze_dependency_chain(module_path: str) -> List[str]:
    """
    🔗 Analyse chaîne de dépendances pour identifier imports manquants
    """
    dependency_errors = []
    
    try:
        # Tentative import avec capture détaillée
        importlib.import_module(module_path)
        
    except Exception as e:
        error_msg = str(e)
        
        # Extraction modules manquants depuis l'erreur
        if "No module named" in error_msg:
            missing_module = error_msg.split("No module named ")[1].strip("'\"")
            dependency_errors.append(f"Module manquant: {missing_module}")
            
        elif "cannot import name" in error_msg:
            parts = error_msg.split("cannot import name ")[1]
            if " from " in parts:
                missing_name = parts.split(" from ")[0].strip("'\"")
                from_module = parts.split(" from ")[1].strip("'\"")
                dependency_errors.append(f"Import manquant: {missing_name} depuis {from_module}")
        
        # Analyse traceback pour plus de détails
        tb = traceback.format_exc()
        if "nextvision.models" in tb:
            dependency_errors.append("Problème modèles nextvision.models")
        if "nextvision_logging" in tb:
            dependency_errors.append("Problème nextvision_logging")
    
    return dependency_errors

def check_required_models() -> Dict[str, bool]:
    """
    📋 Vérification modèles requis pour imports
    """
    required_models = [
        "nextvision.models.bidirectional_models",
        "nextvision.models.extended_matching_models_v3", 
        "nextvision.models.transport_models",
        "nextvision_logging"
    ]
    
    model_status = {}
    
    for model in required_models:
        try:
            importlib.import_module(model)
            model_status[model] = True
            print(f"✅ {model}")
        except Exception as e:
            model_status[model] = False
            print(f"❌ {model}: {str(e)}")
    
    return model_status

def generate_fixes(diagnosis: Dict[str, Any]) -> List[str]:
    """
    🔧 Génération corrections spécifiques
    """
    fixes = []
    
    failing_modules = diagnosis["failing_modules"]
    
    for module_path, class_name, error_type in failing_modules:
        
        if error_type == "IMPORT_ERROR":
            # Analyser dépendances
            deps = analyze_dependency_chain(module_path)
            if deps:
                fixes.append(f"🔧 {module_path}: Corriger dépendances - {', '.join(deps)}")
            else:
                fixes.append(f"🔧 {module_path}: Vérifier imports internes")
                
        elif error_type == "MODULE_NOT_FOUND":
            fixes.append(f"🔧 {module_path}: Module inexistant - vérifier chemin")
            
        elif error_type == "CLASS_NOT_FOUND":
            fixes.append(f"🔧 {module_path}: Ajouter classe {class_name} ou alias")
    
    # Fixes génériques
    if len(failing_modules) > 2:
        fixes.append("🔧 GÉNÉRAL: Revoir structure imports __init__.py")
        fixes.append("🔧 GÉNÉRAL: Vérifier nextvision_logging disponible")
    
    return fixes

def main():
    """
    🚀 Diagnostic principal
    """
    print("🎯 OBJECTIF: Passer de 59% à >70% de couverture")
    print("🔍 PROBLÈME: Imports échouent malgré classes existantes")
    print()
    
    # 1. Vérification modèles de base
    print("📋 VÉRIFICATION MODÈLES DE BASE:")
    print("-" * 40)
    model_status = check_required_models()
    print()
    
    # 2. Diagnostic imports principaux
    diagnosis = diagnose_failing_imports()
    
    # 3. Résumé
    print("\n📊 RÉSUMÉ DIAGNOSTIC:")
    print("-" * 30)
    print(f"✅ Succès: {diagnosis['successful']}/{diagnosis['total_tested']}")
    print(f"❌ Échecs: {diagnosis['failed']}/{diagnosis['total_tested']}")
    
    # 4. Corrections recommandées
    if diagnosis['failed'] > 0:
        print("\n🔧 CORRECTIONS RECOMMANDÉES:")
        print("-" * 35)
        fixes = generate_fixes(diagnosis)
        for i, fix in enumerate(fixes, 1):
            print(f"{i}. {fix}")
    else:
        print("\n🎉 TOUS LES IMPORTS FONCTIONNENT!")
        print("✅ Le problème de couverture vient d'ailleurs")
    
    print(f"\n🎯 PROCHAINE ÉTAPE:")
    if diagnosis['failed'] > 0:
        print("   → Corriger les imports identifiés ci-dessus")
    else:
        print("   → Vérifier configuration coverage.py")
        print("   → Relancer tests avec --cov-report=term-missing")
    
    return diagnosis['failed'] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
