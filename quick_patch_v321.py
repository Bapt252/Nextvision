#!/usr/bin/env python3
"""
Patch Rapide V3.2.1 - Correction Immédiate
===========================================

Correction rapide et ciblée pour les 3 cas d'incompatibilité restants
Sans modification majeure de l'architecture existante

Usage: python quick_patch_v321.py

Baptiste Comas - Nextvision Quick Fix
"""

import sys
import time
import logging

# Ajout du chemin des modules
sys.path.append('gpt_modules')

logger = logging.getLogger('quick_patch')

def apply_sectoral_penalty_patch():
    """Applique un patch rapide pour les incompatibilités sectorielles"""
    
    # Import des modules existants
    from integration import GPTNextvisionIntegrator
    
    # Sauvegarde de la méthode originale
    original_perform_matching = GPTNextvisionIntegrator.perform_complete_matching
    
    def patched_perform_complete_matching(self, candidate_data, job_data):
        """Version patchée avec pénalité sectorielle"""
        
        # Exécution normale
        result = original_perform_matching(self, candidate_data, job_data)
        
        # Extraction des secteurs
        candidate_sector = candidate_data.get('professional_info', {}).get('sector', '').lower()
        job_sector = job_data.get('job_info', {}).get('sector', '').lower()
        
        # Détection d'incompatibilité critique
        tech_keywords = ["tech", "informatique", "développement"]
        finance_keywords = ["finance", "comptabilité", "compta"]
        
        candidate_tech = any(keyword in candidate_sector for keyword in tech_keywords)
        candidate_finance = any(keyword in candidate_sector for keyword in finance_keywords)
        
        job_tech = any(keyword in job_sector for keyword in tech_keywords)
        job_finance = any(keyword in job_sector for keyword in finance_keywords)
        
        # Application de la pénalité si incompatibilité détectée
        penalty_applied = False
        
        if (candidate_tech and job_finance) or (candidate_finance and job_tech):
            # Incompatibilité Tech <-> Finance/Comptabilité
            if "comptabil" in job_sector or "comptabil" in candidate_sector:
                penalty = 0.5  # 50% de pénalité pour comptabilité
            else:
                penalty = 0.6  # 60% de pénalité pour finance
            
            # Application de la pénalité
            original_score = result.total_score
            result.total_score = original_score * penalty
            
            # Ajout de l'alerte
            sectoral_alert = f"SECTORAL_MISMATCH: {candidate_sector} vs {job_sector} (pénalité: {penalty:.1f})"
            result.alerts.append(sectoral_alert)
            
            # Mise à jour de la recommandation
            if result.total_score < 0.3:
                result.recommendation = "NO_MATCH_SECTORAL"
            
            penalty_applied = True
            
            # Log pour debugging
            self.logger.info(f"Pénalité sectorielle appliquée: {original_score:.3f} → {result.total_score:.3f}")
        
        return result
    
    # Remplacement de la méthode
    GPTNextvisionIntegrator.perform_complete_matching = patched_perform_complete_matching
    
    return penalty_applied

def quick_test():
    """Test rapide du patch"""
    
    print("🔧 APPLICATION PATCH RAPIDE V3.2.1")
    print("=" * 40)
    
    # Application du patch
    patch_applied = apply_sectoral_penalty_patch()
    
    if patch_applied:
        print("✅ Patch appliqué avec succès")
    else:
        print("⚠️ Patch en attente de test")
    
    # Test avec la suite existante
    try:
        from test_semantic_matching import SemanticTestSuite
        import os
        
        # Configuration
        test_suite = SemanticTestSuite(os.getenv('OPENAI_API_KEY'))
        
        # Test des 3 cas problématiques
        print("\n📋 Test des cas critiques:")
        
        critical_tests = [
            ("dev_react_senior", "dev_junior_python", (0.30, 0.50), "Surqualification"),
            ("dev_react_senior", "comptable_entry", (0.10, 0.30), "Tech vs Comptabilité"),
            ("comptable_junior", "dev_react_senior", (0.10, 0.30), "Comptabilité vs Tech")
        ]
        
        improvements = 0
        for cv_key, job_key, expected_range, description in critical_tests:
            result = test_suite.run_semantic_test(cv_key, job_key, expected_range)
            
            status = "✅" if result.success else "❌"
            print(f"   {description}: {result.actual_score:.3f} {status}")
            
            if "SECTORAL_MISMATCH" in str(result.details.get('alerts', [])):
                print(f"      🎯 Pénalité sectorielle appliquée")
            
            if result.success:
                improvements += 1
        
        # Test Charlotte DARMON (validation)
        print(f"\n🔍 Validation Charlotte DARMON:")
        charlotte_result = test_suite.run_semantic_test("charlotte_darmon", "comptable_entry", (0.20, 0.40))
        charlotte_ok = charlotte_result.success and abs(charlotte_result.actual_score - 0.335) < 0.05
        
        status = "✅" if charlotte_ok else "❌"
        print(f"   Score: {charlotte_result.actual_score:.3f} {status}")
        
        # Résultat final
        print(f"\n📊 RÉSULTATS PATCH V3.2.1:")
        print(f"   Cas critiques corrigés: {improvements}/3")
        print(f"   Charlotte DARMON: {'✅ Maintenu' if charlotte_ok else '❌ Impacté'}")
        
        if improvements >= 2 and charlotte_ok:
            print("\n🎯 PATCH RÉUSSI")
            print("   Incompatibilités sectorielles corrigées")
        elif charlotte_ok:
            print(f"\n⚠️ AMÉLIORATION PARTIELLE")
            print(f"   {improvements}/3 cas corrigés, Charlotte maintenu")
        else:
            print(f"\n❌ PATCH À RÉVISER")
            print(f"   Charlotte DARMON impacté")
        
        return improvements >= 2 and charlotte_ok
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    
    # Configuration logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        success = quick_test()
        
        if success:
            print("\n💾 Pour sauvegarder le patch:")
            print("   Le patch est appliqué en mémoire")
            print("   Intégrer les modifications dans integration.py")
        else:
            print("\n🔧 Ajustements supplémentaires nécessaires")
            
    except Exception as e:
        print(f"❌ Erreur patch: {e}")
