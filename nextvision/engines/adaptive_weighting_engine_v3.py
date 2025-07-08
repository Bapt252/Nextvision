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
                "expected_progression_pct": float(expected_progression_pct) if expected_progression_pct is not None else 0.0,
                "offered_progression_pct": float(offered_progression_pct) if offered_progression_pct is not None else 0.0,
                "current_salary": float(current_salary) if current_salary is not None else 0.0,
                "desired_salary": float(desired_salary) if desired_salary is not None else 0.0,
                "employment_status": str(employment_status) if employment_status is not None else "unknown",
                "score_explanation": str(score_explanation) if score_explanation is not None else "fallback"
            },
            processing_time_ms=processing_time_ms
        )

    def _score_salary_progression(self, candidate_data: Dict, position_data: Dict, weight: float) -> ComponentScore:
        """
        🔥 MÉTHODE CORRIGÉE - Score progression salariale (3% base → adaptatif)
        
        FIX V3.0.1: Initialisation variables pour éviter UnboundLocalError
        - expected_progression_pct et offered_progression_pct toujours initialisées
        - Compatible freelances, demandeurs emploi (current_salary = 0)
        - Gestion robuste tous cas edge
        """
        start_time = time.time()
        
        current_salary = candidate_data.get("current_salary", 0)
        desired_salary = candidate_data.get("desired_salary", 0)
        position_salary_max = position_data.get("salary_max", 0)
        progression_expectations = candidate_data.get("progression_expectations", 3)
        employment_status = candidate_data.get("employment_status", "unknown")
        
        # 🔥 FIX CRITIQUE: Initialisation variables pour éviter UnboundLocalError
        expected_progression_pct = 0.0
        offered_progression_pct = 0.0
        score_explanation = "fallback_default"
        
        # 🎯 CAS 1: Candidat sans salaire actuel (freelance, demandeur emploi, étudiant)
        if not current_salary or current_salary <= 0:
            if employment_status == "freelance":
                # Freelance : évaluation sur TJM équivalent vs salaire proposé
                raw_score = 0.7  # Score neutre, dépend négociation
                score_explanation = "freelance_evaluation"
            elif employment_status == "demandeur_emploi":
                # Demandeur emploi : toute offre est positive
                raw_score = 0.8 if desired_salary <= position_salary_max else 0.6
                score_explanation = "unemployment_opportunity"
            else:
                # Autres cas (étudiant, transition carrière)
                raw_score = 0.6  # Score modéré
                score_explanation = "no_current_salary"
            
            # Pas de calcul progression car pas de salaire de référence
            expected_progression_pct = 0.0
            offered_progression_pct = 0.0
        
        # 🎯 CAS 2: Candidat sans attente salariale définie  
        elif not desired_salary or desired_salary <= 0:
            # Score basé sur niveau salaire proposé vs marché
            if position_salary_max > current_salary:
                raw_score = 0.8  # Amélioration offerte
                offered_progression_pct = (position_salary_max - current_salary) / current_salary * 100
                score_explanation = "positive_progression_offered"
            else:
                raw_score = 0.4  # Pas d'amélioration
                score_explanation = "no_progression_offered"
            
            expected_progression_pct = 0.0  # Pas d'attente définie
        
        # 🎯 CAS 3: Données complètes - Calcul progression standard
        else:
            # Calcul progressions
            expected_progression_pct = (desired_salary - current_salary) / current_salary * 100
            offered_progression_pct = (position_salary_max - current_salary) / current_salary * 100 if position_salary_max > current_salary else 0
            
            # Évaluation match progression
            if offered_progression_pct >= expected_progression_pct:
                raw_score = 1.0  # Progression suffisante ou supérieure
                score_explanation = "progression_exceeds_expectations"
            elif offered_progression_pct > 0:
                # Progression partielle - ratio de satisfaction
                ratio = offered_progression_pct / expected_progression_pct
                raw_score = max(0.4, min(1.0, ratio))
                score_explanation = f"partial_progression_{int(ratio*100)}pct"
            else:
                raw_score = 0.2  # Pas de progression vs attentes
                score_explanation = "no_progression_vs_expectations"
            
            # 🎁 BONUS: Ambitions modérées (réalisme candidat)
            if progression_expectations <= 3 and expected_progression_pct <= 15:
                raw_score = min(1.0, raw_score + 0.1)
                score_explanation += "_realistic_expectations_bonus"
        
        # Calcul métriques finales
        processing_time_ms = (time.time() - start_time) * 1000
        base_weight = 0.03  # BASE_WEIGHTS_V3["salary_progression"] 
        boost_applied = weight - base_weight
        
        # Détermination qualité match
        if raw_score > 0.8:
            quality = MatchQuality.EXCELLENT
        elif raw_score > 0.6:
            quality = MatchQuality.GOOD
        elif raw_score > 0.4:
            quality = MatchQuality.ACCEPTABLE
        else:
            quality = MatchQuality.POOR
        
        return ComponentScore(
            name="salary_progression",
            raw_score=raw_score,
            weighted_score=raw_score * weight,
            weight=weight,
            base_weight=base_weight,
            boost_applied=boost_applied,
            quality=quality,
            confidence=0.8,
            details={
                "expected_progression_pct": float(expected_progression_pct),
                "offered_progression_pct": float(offered_progression_pct),
                "current_salary": float(current_salary) if current_salary else 0.0,
                "desired_salary": float(desired_salary) if desired_salary else 0.0,
                "employment_status": str(employment_status),
                "score_explanation": str(score_explanation)
            },
            processing_time_ms=processing_time_ms
        )