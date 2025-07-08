    def _score_salary_progression(self, candidate_data: Dict, position_data: Dict, weight: float) -> ComponentScore:
        """
        Score progression salariale (3% base → adaptatif)
        ULTRA-DEFENSIVE FIX: Approche simple et infaillible
        """
        start_time = time.time()
        
        # VARIABLES TOUJOURS DÉFINIES DÈS LE DÉBUT - AUCUNE EXCEPTION POSSIBLE
        raw_score = 0.5
        expected_progression_pct = 0.0
        offered_progression_pct = 0.0
        score_explanation = "initialized"
        
        # EXTRACTION DONNÉES SÉCURISÉE
        try:
            current_salary = candidate_data.get("current_salary", 0)
            desired_salary = candidate_data.get("desired_salary", 0) 
            position_salary_min = position_data.get("salary_min", 0)
            position_salary_max = position_data.get("salary_max", 0)
            progression_expectations = candidate_data.get("progression_expectations", 3)
            employment_status = candidate_data.get("employment_status", "en_poste")
            
            # CONVERSION SÉCURISÉE - GESTION None/str/int
            if current_salary is None or current_salary == "" or current_salary == "None":
                current_salary = 0
            if desired_salary is None or desired_salary == "" or desired_salary == "None":
                desired_salary = 0
            if position_salary_min is None or position_salary_min == "" or position_salary_min == "None":
                position_salary_min = 0
            if position_salary_max is None or position_salary_max == "" or position_salary_max == "None":
                position_salary_max = 0
            
            # CONVERSION EN FLOAT SÉCURISÉE
            current_salary = float(current_salary) if current_salary else 0.0
            desired_salary = float(desired_salary) if desired_salary else 0.0
            position_salary_min = float(position_salary_min) if position_salary_min else 0.0
            position_salary_max = float(position_salary_max) if position_salary_max else 0.0
            
            # LOGIQUE SIMPLIFIÉE - DEUX CAS PRINCIPAUX SEULEMENT
            if current_salary <= 0:
                # CAS 1: PAS DE SALAIRE ACTUEL (freelance, demandeur emploi, etc.)
                score_explanation = "no_current_salary"
                
                if desired_salary > 0 and position_salary_max > 0:
                    if desired_salary <= position_salary_max:
                        raw_score = 0.8  # Alignement correct
                        score_explanation = "desired_salary_compatible"
                    else:
                        raw_score = 0.4  # Trop élevé
                        score_explanation = "desired_salary_too_high"
                    
                    # Bonus demandeur emploi
                    if employment_status == "demandeur_emploi":
                        raw_score = min(1.0, raw_score + 0.1)
                        score_explanation += "_unemployed_bonus"
                else:
                    raw_score = 0.5
                    score_explanation = "insufficient_salary_data"
                
                # PAS DE CALCUL DE PROGRESSION - variables restent à 0.0
            
            else:
                # CAS 2: AVEC SALAIRE ACTUEL - calcul progression simple
                score_explanation = "with_current_salary"
                
                if desired_salary > 0 and position_salary_max > 0:
                    # Calcul progression - division sécurisée car current_salary > 0
                    expected_progression_pct = ((desired_salary - current_salary) / current_salary) * 100
                    
                    if position_salary_max > current_salary:
                        offered_progression_pct = ((position_salary_max - current_salary) / current_salary) * 100
                    else:
                        offered_progression_pct = 0.0
                    
                    # Score progression
                    if offered_progression_pct >= expected_progression_pct:
                        raw_score = 1.0
                        score_explanation = "progression_satisfied"
                    elif offered_progression_pct > 0:
                        raw_score = 0.7
                        score_explanation = "partial_progression"
                    else:
                        raw_score = 0.3
                        score_explanation = "no_progression_offered"
                else:
                    raw_score = 0.5
                    score_explanation = "incomplete_progression_data"
            
        except Exception as e:
            # FALLBACK TOTAL EN CAS D'ERREUR INATTENDUE
            raw_score = 0.5
            expected_progression_pct = 0.0
            offered_progression_pct = 0.0
            score_explanation = f"error_fallback_{str(e)[:20]}"
        
        # CONSTRUCTION RÉSULTAT - VARIABLES GARANTIES DÉFINIES
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
            details={
                "expected_progression_pct": expected_progression_pct,
                "offered_progression_pct": offered_progression_pct,
                "current_salary": current_salary if 'current_salary' in locals() else 0,
                "desired_salary": desired_salary if 'desired_salary' in locals() else 0,
                "employment_status": employment_status if 'employment_status' in locals() else "unknown",
                "score_explanation": score_explanation
            },
            processing_time_ms=processing_time_ms
        )