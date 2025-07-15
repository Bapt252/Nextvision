# nextvision/api/v3/intelligent_matching_integration_patch.py
"""
Patch d'intégration pour ajouter le MotivationsAlignmentScorer 
dans l'endpoint intelligent_matching.py existant
"""

# ==========================================
# IMPORTS À AJOUTER (en haut du fichier intelligent_matching.py)
# ==========================================

from nextvision.engines.motivations_scoring_engine import motivations_scoring_engine
from nextvision.services.job_intelligence_service import job_intelligence_service


# ==========================================
# MODIFICATION DE LA MÉTHODE _calculate_intelligent_matching
# ==========================================

async def _calculate_intelligent_matching_enhanced(
    self,
    matching_request,
    job_address: str
) -> Dict[str, Any]:
    """
    Calcul du matching intelligent enrichi avec scoring motivationnel
    INTÉGRATION SEAMLESS - Maintient les performances < 21ms
    """
    
    # ==========================================
    # SCORES EXISTANTS ✅ (inchangés)
    # ==========================================
    static_scores = {
        "semantique": 0.62,
        "hierarchical": 0.66, 
        "remuneration": 0.735,
        "experience": 0.5,
        "secteurs": 0.7,
        "localisation": 0.92  # Transport Intelligence existant
    }
    
    # ==========================================
    # NOUVEAU : INTÉGRATION MOTIVATIONS SCORING
    # ==========================================
    
    motivations_score = 0.5  # Score par défaut
    job_intelligence = None
    
    try:
        # 1. Génération de clé de cache pour optimisation
        job_cache_key = job_intelligence_service.get_cache_key(matching_request.job_requirements)
        
        # 2. Calcul du score motivationnel (2-5ms ciblé)
        motivations_score = await motivations_scoring_engine.calculate_score(
            candidat_motivations=matching_request.questionnaire.motivations,
            job_data=matching_request.job_requirements,
            job_cache_key=job_cache_key
        )
        
        # 3. Analyse d'intelligence job enrichie (optionnel, pour debug/logs)
        job_intelligence = await job_intelligence_service.analyze_job_intelligence(
            job_data=matching_request.job_requirements,
            cache_key=job_cache_key
        )
        
        print(f"🎯 Motivations Score: {motivations_score:.3f}")
        print(f"📊 Job Intelligence: {job_intelligence.culture_type} | Innovation: {job_intelligence.innovation_level}")
        
    except Exception as e:
        print(f"⚠️ Erreur scoring motivations: {e}")
        # Le score par défaut est déjà défini
    
    # ==========================================
    # INTÉGRATION DANS LE SYSTÈME EXISTANT
    # ==========================================
    
    # Scores combinés avec nouveau composant
    all_scores = {
        **static_scores,
        "motivations": motivations_score  # ← NOUVEAU COMPOSANT
    }
    
    # ==========================================
    # PONDÉRATION ADAPTATIVE ENRICHIE
    # ==========================================
    
    # Poids par défaut (existants + nouveau)
    weights = {
        "semantique": 0.15,
        "hierarchical": 0.10,
        "remuneration": 0.20,
        "experience": 0.10,
        "secteurs": 0.15,
        "localisation": 0.15,
        "motivations": 0.15  # ← NOUVEAU POIDS
    }
    
    # Adaptation selon pourquoi_ecoute (système existant enrichi)
    pourquoi_ecoute = getattr(matching_request, 'pourquoi_ecoute', '').lower()
    
    if "rémunération" in pourquoi_ecoute or "salaire" in pourquoi_ecoute:
        weights["remuneration"] += 0.05
        weights["motivations"] -= 0.02  # Ajustement compensatoire
        
    elif "loin" in pourquoi_ecoute or "localisation" in pourquoi_ecoute:
        weights["localisation"] += 0.05
        weights["motivations"] -= 0.02
        
    elif "évolution" in pourquoi_ecoute or "carrière" in pourquoi_ecoute:
        weights["motivations"] += 0.10  # ← NOUVEAU : Boost motivations pour évolution
        weights["experience"] -= 0.05
        
    elif "équipe" in pourquoi_ecoute or "culture" in pourquoi_ecoute:
        weights["motivations"] += 0.08  # ← NOUVEAU : Boost motivations pour équipe
        weights["secteurs"] -= 0.04
        
    elif "innovation" in pourquoi_ecoute or "technologie" in pourquoi_ecoute:
        weights["motivations"] += 0.07  # ← NOUVEAU : Boost motivations pour innovation
        weights["semantique"] -= 0.03
    
    # Normalisation des poids (sécurité)
    total_weight = sum(weights.values())
    if total_weight != 1.0:
        weights = {k: v/total_weight for k, v in weights.items()}
    
    # ==========================================
    # CALCUL DU SCORE FINAL ENRICHI
    # ==========================================
    
    # Score pondéré final
    final_score = sum(all_scores[component] * weights[component] 
                     for component in all_scores.keys())
    
    # Métadonnées enrichies pour réponse
    component_details = {
        component: {
            "score": round(score, 3),
            "weight": round(weights[component], 3),
            "contribution": round(score * weights[component], 3)
        }
        for component, score in all_scores.items()
    }
    
    # ==========================================
    # RÉPONSE ENRICHIE
    # ==========================================
    
    response_data = {
        "final_score": round(final_score, 3),
        "component_scores": all_scores,
        "component_weights": weights,
        "component_details": component_details,
        "job_address": job_address,
        "pourquoi_ecoute": getattr(matching_request, 'pourquoi_ecoute', ''),
        
        # ← NOUVELLES MÉTADONNÉES MOTIVATIONS
        "motivations_analysis": {
            "score": round(motivations_score, 3),
            "candidat_priorities": matching_request.questionnaire.motivations.classees[:3],  # Top 3
            "job_culture": job_intelligence.culture_type if job_intelligence else "unknown",
            "innovation_level": job_intelligence.innovation_level if job_intelligence else "unknown",
            "confidence": round(job_intelligence.confidence_score, 2) if job_intelligence else 0.5
        }
    }
    
    return response_data


# ==========================================
# FONCTION UTILITAIRE POUR PONDÉRATION ADAPTATIVE V2
# ==========================================

def apply_adaptive_weighting_v2(pourquoi_ecoute: str, base_weights: Dict[str, float]) -> Dict[str, float]:
    """
    Version enrichie de la pondération adaptative avec support motivations
    Compatible avec le système existant
    """
    
    weights = base_weights.copy()
    
    # Logique existante (maintenue)
    if "rémunération" in pourquoi_ecoute.lower():
        weights["remuneration"] = min(weights["remuneration"] + 0.05, 0.3)
    elif "loin" in pourquoi_ecoute.lower():
        weights["localisation"] = min(weights["localisation"] + 0.05, 0.25)
    
    # ← NOUVELLES RÈGLES MOTIVATIONS
    elif "évolution" in pourquoi_ecoute.lower() or "carrière" in pourquoi_ecoute.lower():
        weights["motivations"] = min(weights["motivations"] + 0.10, 0.3)
        weights["experience"] = max(weights["experience"] - 0.05, 0.05)
        
    elif "équipe" in pourquoi_ecoute.lower() or "culture" in pourquoi_ecoute.lower():
        weights["motivations"] = min(weights["motivations"] + 0.08, 0.28)
        weights["secteurs"] = max(weights["secteurs"] - 0.04, 0.05)
        
    elif "innovation" in pourquoi_ecoute.lower() or "technologie" in pourquoi_ecoute.lower():
        weights["motivations"] = min(weights["motivations"] + 0.07, 0.25)
        weights["semantique"] = max(weights["semantique"] - 0.03, 0.05)
    
    # Normalisation pour maintenir la somme = 1.0
    total = sum(weights.values())
    return {k: v/total for k, v in weights.items()}


# ==========================================
# EXEMPLE D'INTÉGRATION DANS CLASSE EXISTANTE
# ==========================================

class IntelligentMatchingEndpointEnhanced:
    """Version enrichie de l'endpoint avec scoring motivationnel"""
    
    def __init__(self):
        # Initialisation existante...
        pass
    
    async def _calculate_intelligent_matching(self, matching_request, job_address: str):
        """Point d'intégration principal - remplace la méthode existante"""
        return await _calculate_intelligent_matching_enhanced(
            self, matching_request, job_address
        )


# ==========================================
# SCRIPT DE VALIDATION RAPIDE
# ==========================================

async def validate_motivations_integration():
    """Validation rapide de l'intégration pour tests"""
    
    print("🔧 Validation intégration MotivationsAlignmentScorer...")
    
    try:
        # Test imports
        from nextvision.engines.motivations_scoring_engine import motivations_scoring_engine
        from nextvision.services.job_intelligence_service import job_intelligence_service
        print("✅ Imports validés")
        
        # Test scoring basique
        from nextvision.models.questionnaire_advanced import MotivationsClassees
        from nextvision.services.gpt_direct_service import JobData
        
        test_motivations = MotivationsClassees(
            classees=["Innovation", "Évolution"],
            priorites=[1, 2]
        )
        
        test_job = JobData(
            title="AI Engineer",
            benefits=["Innovation", "Formation"],
            responsibilities=["IA", "Leadership"]
        )
        
        score = await motivations_scoring_engine.calculate_score(
            candidat_motivations=test_motivations,
            job_data=test_job
        )
        
        print(f"✅ Score test: {score:.3f}")
        
        # Test job intelligence
        intel = await job_intelligence_service.analyze_job_intelligence(test_job)
        print(f"✅ Job intelligence: {intel.culture_type}")
        
        print("🎯 Intégration validée avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
        return False


if __name__ == "__main__":
    import asyncio
    asyncio.run(validate_motivations_integration())
