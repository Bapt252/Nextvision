#!/usr/bin/env python3
"""
🎯 Enhancement Contract Scoring - Cas exclusifs
"""

contract_scoring_enhancement = '''

class ContractFlexibilityScorer:
    """🎯 Scorer avancé flexibilité contractuelle V3.0"""
    
    def score_contract_match(self, candidate_prefs: List[str], company_offer: str, 
                           exclusive_search: bool = False) -> Dict[str, float]:
        """
        Score matching contrats avec gestion cas exclusifs
        
        Args:
            candidate_prefs: Classement préférences candidat ["cdi", "freelance", ...]
            company_offer: Offre entreprise "cdi"
            exclusive_search: True si candidat ne veut QUE ce type
        """
        
        if exclusive_search:
            # Candidat recherche EXCLUSIVEMENT un type
            if company_offer in candidate_prefs:
                return {
                    "score": 1.0,
                    "match_type": "perfect_exclusive",
                    "confidence": 0.95,
                    "reason": f"Candidat recherche exclusivement {company_offer.upper()}"
                }
            else:
                return {
                    "score": 0.0,
                    "match_type": "incompatible",
                    "confidence": 0.95,
                    "reason": f"Candidat refuse {company_offer.upper()}"
                }
        
        else:
            # Classement normal avec dégressivité
            if company_offer in candidate_prefs:
                rank = candidate_prefs.index(company_offer) + 1
                base_score = max(0, 1.0 - (rank - 1) * 0.25)
                
                # Bonus si contrat préféré
                bonus = 0.1 if rank == 1 else 0
                final_score = min(1.0, base_score + bonus)
                
                return {
                    "score": final_score,
                    "match_type": "ranked_preference",
                    "rank": rank,
                    "total_options": len(candidate_prefs),
                    "confidence": 0.8,
                    "reason": f"{company_offer.upper()} est rang {rank}/{len(candidate_prefs)}"
                }
            else:
                return {
                    "score": 0.2,  # Score minimal pour contrat non listé
                    "match_type": "not_preferred",
                    "confidence": 0.3,
                    "reason": f"{company_offer.upper()} pas dans préférences"
                }

    def detect_exclusive_search(self, candidate_data: Dict) -> Tuple[bool, List[str]]:
        """Détecte si candidat recherche exclusivement certains contrats"""
        
        # Indicateurs recherche exclusive
        exclusive_indicators = {
            "only_cdi": ["stabilité", "sécurité", "évolution", "long terme"],
            "only_freelance": ["liberté", "indépendance", "missions courtes", "tarif jour"],
            "only_interim": ["flexibilité", "découverte", "missions variées"],
            "only_cdd": ["projet défini", "durée limitée", "pas engagement"]
        }
        
        candidate_motivations = candidate_data.get("motivations_text", "").lower()
        contract_prefs = candidate_data.get("contract_ranking", [])
        
        # Si 1 seul contrat en préférence = exclusif
        if len(contract_prefs) == 1:
            return True, contract_prefs
        
        # Analyse motivations pour détecter exclusivité
        for contract_type, keywords in exclusive_indicators.items():
            if any(keyword in candidate_motivations for keyword in keywords):
                if len(contract_prefs) <= 2:  # Peu d'options = probablement exclusif
                    return True, contract_prefs[:1]
        
        return False, contract_prefs

'''

# Ajouter au fichier models
with open('nextvision/models/extended_matching_models_v3.py', 'a') as f:
    f.write(contract_scoring_enhancement)

print("✅ Contract Scoring avancé ajouté!")
print("🎯 Gestion cas exclusifs: CDI only, Freelance only, etc.")
