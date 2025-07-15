#!/usr/bin/env python3
"""
Patch Persistant V3.2.1 - Application Automatique
=================================================

Modifie directement le fichier integration.py pour appliquer
la correction sectorielle de façon permanente

Baptiste Comas - Nextvision V3.2.1 Final
"""

import os
import re
import shutil
from datetime import datetime

def backup_integration_file():
    """Crée une sauvegarde du fichier integration.py"""
    
    source = "gpt_modules/integration.py"
    backup = f"gpt_modules/integration_backup_{int(datetime.now().timestamp())}.py"
    
    try:
        shutil.copy2(source, backup)
        print(f"✅ Sauvegarde créée: {backup}")
        return backup
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")
        return None

def apply_persistent_patch():
    """Applique le patch directement dans integration.py"""
    
    integration_file = "gpt_modules/integration.py"
    
    try:
        # Lecture du fichier
        with open(integration_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérification si le patch est déjà appliqué
        if "SECTORAL_PENALTY" in content:
            print("⚠️ Patch déjà appliqué")
            return True
        
        # Pattern pour trouver la fin du calcul du score total
        pattern = r'(total_score = \(\s*scores\[\'semantic\'\] \* self\.weights_v31\[\'semantic\'\] \+.*?\s*scores\[\'sector\'\] \* self\.weights_v31\[\'sector\'\]\s*\))'
        
        replacement = r'''\1
            
            # PATCH V3.2.1: Application pénalité sectorielle pour incompatibilités critiques
            candidate_sector = candidate_data.get('professional_info', {}).get('sector', '').lower()
            job_sector = job_data.get('job_info', {}).get('sector', '').lower()
            
            # Détection incompatibilité Tech ↔ Finance/Comptabilité
            tech_keywords = ["tech", "informatique", "développement"]
            finance_keywords = ["finance", "comptabilité", "compta"]
            
            candidate_tech = any(keyword in candidate_sector for keyword in tech_keywords)
            candidate_finance = any(keyword in candidate_sector for keyword in finance_keywords)
            job_tech = any(keyword in job_sector for keyword in tech_keywords)
            job_finance = any(keyword in job_sector for keyword in finance_keywords)
            
            # Application pénalité si incompatibilité détectée
            if (candidate_tech and job_finance) or (candidate_finance and job_tech):
                original_score = total_score
                penalty = 0.5 if "comptabil" in (candidate_sector + job_sector) else 0.6
                total_score = original_score * penalty
                alerts.append(f"SECTORAL_PENALTY: Incompatibilité {candidate_sector} vs {job_sector} (pénalité: {penalty:.1f})")
                self.logger.debug(f"Pénalité sectorielle V3.2.1: {original_score:.3f} → {total_score:.3f}")'''
        
        # Application du patch
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        if new_content == content:
            print("❌ Pattern non trouvé - modification manuelle nécessaire")
            return False
        
        # Sauvegarde du fichier modifié
        with open(integration_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Patch appliqué avec succès dans integration.py")
        return True
        
    except Exception as e:
        print(f"❌ Erreur application patch: {e}")
        return False

def test_persistent_patch():
    """Test du patch persistant"""
    
    print("\n📋 Test du patch persistant:")
    
    try:
        # Import du module modifié
        import sys
        sys.path.insert(0, 'gpt_modules')
        
        # Suppression du module du cache pour forcer le rechargement
        if 'integration' in sys.modules:
            del sys.modules['integration']
        if 'gpt_modules.integration' in sys.modules:
            del sys.modules['gpt_modules.integration']
        
        # Rechargement
        from integration import GPTNextvisionIntegrator
        from cv_parser import CVParserGPT
        from job_parser import JobParserGPT
        
        # Configuration
        import os
        openai_client = None
        if os.getenv('OPENAI_API_KEY'):
            import openai
            openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        cv_parser = CVParserGPT(openai_client)
        job_parser = JobParserGPT(openai_client)
        integrator = GPTNextvisionIntegrator(cv_parser=cv_parser, job_parser=job_parser)
        
        # Test Charlotte
        charlotte_result = integrator.test_charlotte_darmon_vs_comptable()
        charlotte_score = charlotte_result['result'].total_score
        print(f"1. Charlotte vs Comptable: {charlotte_score:.3f}")
        
        # Tests sectoriels avec la suite complète
        from test_semantic_matching import SemanticTestSuite
        test_suite = SemanticTestSuite()
        
        # Test Dev vs Comptable
        dev_result = test_suite.run_semantic_test("dev_react_senior", "comptable_entry", (0.10, 0.30))
        print(f"2. Dev vs Comptable: {dev_result.actual_score:.3f} {'✅' if dev_result.success else '❌'}")
        
        # Test Comptable vs Dev
        comptable_result = test_suite.run_semantic_test("comptable_junior", "dev_react_senior", (0.10, 0.30))
        print(f"3. Comptable vs Dev: {comptable_result.actual_score:.3f} {'✅' if comptable_result.success else '❌'}")
        
        # Vérification des alertes sectorielles
        sectoral_alerts = [alert for alert in dev_result.details.get('alerts', []) if 'SECTORAL_PENALTY' in str(alert)]
        if sectoral_alerts:
            print("   🎯 Pénalité sectorielle détectée dans les alertes")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_full_test_suite():
    """Lance la suite complète de tests avec le patch persistant"""
    
    print("\n🧪 SUITE COMPLÈTE DE TESTS V3.2.1")
    print("=" * 40)
    
    try:
        # Suppression du cache des modules pour forcer le rechargement
        import sys
        modules_to_reload = [m for m in sys.modules.keys() if 'integration' in m or 'test_semantic' in m]
        for module in modules_to_reload:
            if module in sys.modules:
                del sys.modules[module]
        
        # Import de la suite de tests
        from test_semantic_matching import SemanticTestSuite
        
        # Configuration et exécution
        test_suite = SemanticTestSuite(os.getenv('OPENAI_API_KEY'))
        results = test_suite.run_full_test_suite()
        
        print(f"\n📊 RÉSULTATS FINAUX V3.2.1:")
        print(f"   Tests réussis: {results['successful_tests']}/{results['total_tests']}")
        print(f"   Taux de réussite: {results['success_rate']:.1f}%")
        
        # Comparaison avec les versions précédentes
        if results['success_rate'] >= 80:
            print("🏆 OBJECTIF ATTEINT: ≥80% de réussite")
        elif results['success_rate'] >= 70:
            print("🎯 BONNE AMÉLIORATION: ≥70% de réussite")
        else:
            print("⚠️ Amélioration partielle")
        
        improvement_v31 = results['success_rate'] - 60.0  # Baseline V3.1
        print(f"📈 Amélioration vs V3.1: +{improvement_v31:.1f}%")
        
        return results['success_rate'] >= 75
        
    except Exception as e:
        print(f"❌ Erreur suite de tests: {e}")
        return False

def main():
    """Fonction principale"""
    
    print("🔧 PATCH PERSISTANT V3.2.1 - NEXTVISION")
    print("Application définitive des corrections sectorielles")
    print("=" * 55)
    
    try:
        # Sauvegarde
        backup_path = backup_integration_file()
        if not backup_path:
            print("❌ Impossible de créer la sauvegarde")
            return False
        
        # Application du patch
        if not apply_persistent_patch():
            print("❌ Échec de l'application du patch")
            return False
        
        # Test du patch
        if not test_persistent_patch():
            print("❌ Échec du test du patch")
            return False
        
        # Suite complète de tests
        success = run_full_test_suite()
        
        if success:
            print("\n🎉 SUCCÈS COMPLET - NEXTVISION V3.2.1 OPÉRATIONNEL")
            print("   Patch persistant appliqué avec succès")
            print("   Performance ≥75% atteinte")
            print("   Système prêt pour production")
            
            print(f"\n💾 Sauvegarde disponible: {backup_path}")
            print("   En cas de problème: cp backup integration.py")
            
        else:
            print("\n⚠️ AMÉLIORATION PARTIELLE")
            print("   Patch appliqué mais performance <75%")
            print("   Optimisations supplémentaires possibles")
        
        return success
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✅ Patch persistant V3.2.1 terminé avec succès")
    else:
        print("\n❌ Patch persistant nécessite des ajustements")
