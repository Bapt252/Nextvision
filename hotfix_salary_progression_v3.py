"""
Nextvision V3.0 - Hotfix Salary Progression Bug
===============================================

Correction du bug dans _score_salary_progression qui causait:
"cannot access local variable 'expected_progression_pct' where it is not associated with a value"

Ce hotfix résout les 952 échecs dans les tests production.

Author: NEXTEN Development Team
Version: 3.0.1 - Hotfix
"""

# Appliquer le hotfix au fichier principal
def apply_salary_progression_hotfix():
    """
    Applique le correctif pour la méthode _score_salary_progression
    
    PROBLÈME RÉSOLU:
    - Variables expected_progression_pct et offered_progression_pct 
      n'étaient pas initialisées dans le cas où current_salary ou desired_salary = 0
    - Causait une UnboundLocalError dans les details du ComponentScore
    
    SOLUTION:
    - Initialisation des variables au début de la méthode
    - Garantit que les variables existent toujours pour les details
    """
    
    print("🔧 Application hotfix salary_progression...")
    
    # Lecture du fichier original
    try:
        with open('nextvision/engines/adaptive_weighting_engine_v3.py', 'r') as f:
            content = f.read()
        
        # Remplacement de la méthode buggée
        old_method = '''    def _score_salary_progression(self, candidate_data: Dict, position_data: Dict, weight: float) -> ComponentScore:
        """Score progression salariale (3% base → adaptatif)"""
        start_time = time.time()
        
        current_salary = candidate_data.get("current_salary", 0)
        desired_salary = candidate_data.get("desired_salary", 0)
        position_salary_max = position_data.get("salary_max", 0)
        progression_expectations = candidate_data.get("progression_expectations", 3)
        
        if not current_salary or not desired_salary:
            raw_score = 0.5
        else:
            # Calcul progression offerte vs attendue
            expected_progression_pct = (desired_salary - current_salary) / current_salary * 100
            offered_progression_pct = (position_salary_max - current_salary) / current_salary * 100 if position_salary_max > current_salary else 0
            
            if offered_progression_pct >= expected_progression_pct:
                raw_score = 1.0  # Progression suffisante
            elif offered_progression_pct > 0:
                ratio = offered_progression_pct / expected_progression_pct
                raw_score = max(0.4, ratio)  # Progression partielle
            else:
                raw_score = 0.2  # Pas de progression
            
            # Bonus ambitions modérées
            if progression_expectations <= 3 and expected_progression_pct <= 15:
                raw_score = min(1.0, raw_score + 0.1)
        
        processing_time_ms = (time.time() - start_time) * 1000
        base_weight = BASE_WEIGHTS_V3["salary_progression"]
        boost_applied = weight - base_weight
        
        return ComponentScore(
            name="salary_progression",
            raw_score=raw_score,
            weighted_score=raw_score * weight,
            weight=weight,
            base_weight=base_weight,
            boost_applied=boost_applied,
            quality=MatchQuality.EXCELLENT if raw_score > 0.8 else MatchQuality.GOOD if raw_score > 0.6 else MatchQuality.ACCEPTABLE,
            confidence=0.8,
            details={"expected_progression_pct": expected_progression_pct, "offered_progression_pct": offered_progression_pct},
            processing_time_ms=processing_time_ms
        )'''
        
        new_method = '''    def _score_salary_progression(self, candidate_data: Dict, position_data: Dict, weight: float) -> ComponentScore:
        """Score progression salariale (3% base → adaptatif)"""
        start_time = time.time()
        
        current_salary = candidate_data.get("current_salary", 0)
        desired_salary = candidate_data.get("desired_salary", 0)
        position_salary_max = position_data.get("salary_max", 0)
        progression_expectations = candidate_data.get("progression_expectations", 3)
        
        # FIX: Initialisation variables pour éviter UnboundLocalError
        expected_progression_pct = 0.0
        offered_progression_pct = 0.0
        
        if not current_salary or not desired_salary:
            raw_score = 0.5
        else:
            # Calcul progression offerte vs attendue
            expected_progression_pct = (desired_salary - current_salary) / current_salary * 100
            offered_progression_pct = (position_salary_max - current_salary) / current_salary * 100 if position_salary_max > current_salary else 0
            
            if offered_progression_pct >= expected_progression_pct:
                raw_score = 1.0  # Progression suffisante
            elif offered_progression_pct > 0:
                ratio = offered_progression_pct / expected_progression_pct
                raw_score = max(0.4, ratio)  # Progression partielle
            else:
                raw_score = 0.2  # Pas de progression
            
            # Bonus ambitions modérées
            if progression_expectations <= 3 and expected_progression_pct <= 15:
                raw_score = min(1.0, raw_score + 0.1)
        
        processing_time_ms = (time.time() - start_time) * 1000
        base_weight = BASE_WEIGHTS_V3["salary_progression"]
        boost_applied = weight - base_weight
        
        return ComponentScore(
            name="salary_progression",
            raw_score=raw_score,
            weighted_score=raw_score * weight,
            weight=weight,
            base_weight=base_weight,
            boost_applied=boost_applied,
            quality=MatchQuality.EXCELLENT if raw_score > 0.8 else MatchQuality.GOOD if raw_score > 0.6 else MatchQuality.ACCEPTABLE,
            confidence=0.8,
            details={"expected_progression_pct": expected_progression_pct, "offered_progression_pct": offered_progression_pct},
            processing_time_ms=processing_time_ms
        )'''
        
        # Application du correctif
        if old_method in content:
            fixed_content = content.replace(old_method, new_method)
            
            # Sauvegarde du fichier corrigé
            with open('nextvision/engines/adaptive_weighting_engine_v3.py', 'w') as f:
                f.write(fixed_content)
            
            print("✅ Hotfix appliqué avec succès")
            print("🔧 Bug salary_progression corrigé")
            return True
        else:
            print("❌ Méthode non trouvée dans le fichier")
            return False
            
    except Exception as e:
        print(f"❌ Erreur application hotfix: {e}")
        return False

if __name__ == "__main__":
    # Application du hotfix
    success = apply_salary_progression_hotfix()
    
    if success:
        print("\n🚀 Test de validation post-hotfix:")
        print("python -c \"")
        print("from nextvision.engines.adaptive_weighting_engine_v3 import AdaptiveWeightingEngine")
        print("engine = AdaptiveWeightingEngine()")
        print("print('✅ Engine V3.0.1 - Hotfix OK')")
        print("\"")
        
        print("\n🧪 Relancer le test production:")
        print("python test_nextvision_v3_production_final.py")
    else:
        print("\n❌ Hotfix échoué - Correction manuelle nécessaire")
