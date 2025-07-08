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