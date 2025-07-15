#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 NEXTVISION GPT INTEGRATION v3.1 - VERSION ISOLÉE
Intégration complète sans conflit de modules
"""

import os
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Imports locaux isolés
from .cv_parser import NextvisionGPTParser, ParsedProfile
from .job_parser import NextvisionJobParser, ParsedJobPosting

@dataclass
class MatchingResult:
    candidate_id: str
    job_id: str
    overall_score: float
    score_breakdown: Dict[str, float]
    hierarchical_compatibility: bool
    sector_compatibility: float
    alerts: List[str]
    recommendation: str
    metadata: Dict[str, Any]

class NextvisionGPTIntegration:
    """Intégrateur principal GPT Nextvision v3.1 - isolé"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.integration_version = "3.1.0"
        
        # Initialisation des parsers isolés
        self.cv_parser = NextvisionGPTParser(openai_api_key)
        self.job_parser = NextvisionJobParser(openai_api_key)
        print("✅ Parsers GPT isolés initialisés")
        
        # Pondérations V3.1 avec NOUVEAU secteur
        self.weights_v31 = {
            'semantic': 0.30,      # 30% - Compatibilité sémantique
            'hierarchical': 0.15,  # 15% - Niveau hiérarchique  
            'salary': 0.20,        # 20% - Compatibilité salariale
            'experience': 0.20,    # 20% - Années d'expérience
            'location': 0.15,      # 15% - Localisation
            'sector': 0.05         # 5% - NOUVEAU: Secteur d'activité
        }
        
        print(f"🚀 NextvisionGPTIntegration v{self.integration_version} initialisé")

    def compute_enhanced_matching(self, candidate_profile: ParsedProfile, job_posting: ParsedJobPosting) -> MatchingResult:
        """Matching amélioré V3.1 avec secteurs et hiérarchie"""
        print("🎯 MATCHING AMÉLIORÉ V3.1")
        
        # 1. Score sémantique (30%)
        semantic_score = 0.6  # Simulation
        
        # 2. Score hiérarchique (15%) - CRITIQUE pour Charlotte DARMON
        candidate_level = candidate_profile.analyse_cv.get('niveau_hierarchique', 'MID')
        job_level = job_posting.informations_poste.get('niveau_hierarchique', 'MID')
        
        hierarchy_order = ['ENTRY', 'ASSOCIATE', 'MID', 'SENIOR', 'MANAGER', 'EXECUTIVE']
        
        try:
            candidate_index = hierarchy_order.index(candidate_level)
            job_index = hierarchy_order.index(job_level)
            
            diff = abs(candidate_index - job_index)
            
            # CAS CHARLOTTE DARMON : surqualification majeure
            if candidate_index > job_index + 2:
                hierarchical_score = 0.2  # Score très bas
                hierarchical_compatible = False
            elif diff == 0:
                hierarchical_score = 1.0
                hierarchical_compatible = True
            elif diff <= 2:
                hierarchical_score = 0.8 - (diff * 0.1)
                hierarchical_compatible = True
            else:
                hierarchical_score = 0.3
                hierarchical_compatible = False
                
        except ValueError:
            hierarchical_score = 0.5
            hierarchical_compatible = True
        
        # 3. Score salarial (20%)
        salary_score = 0.7
        
        # 4. Score expérience (20%)
        experience_score = 0.8
        
        # 5. Score localisation (15%)
        location_score = 1.0
        
        # 6. Score secteur (5%) - NOUVEAU V3.1
        candidate_sectors = candidate_profile.analyse_cv.get('secteurs_experiences', [])
        job_sector = job_posting.secteur_activite.get('secteur_final', '')
        
        if job_sector in candidate_sectors:
            sector_score = 0.8
        else:
            sector_score = 0.5
        
        # Calcul du score global pondéré V3.1
        score_breakdown = {
            'semantic': semantic_score,
            'hierarchical': hierarchical_score,
            'salary': salary_score,
            'experience': experience_score,
            'location': location_score,
            'sector': sector_score
        }
        
        overall_score = sum(score * self.weights_v31[component] for component, score in score_breakdown.items())
        
        # Génération des alertes
        alerts = []
        if not hierarchical_compatible:
            alerts.append("CRITICAL_MISMATCH: Surqualification hiérarchique détectée")
        
        if overall_score < 0.3:
            alerts.append("LOW_COMPATIBILITY: Score global très faible")
        
        # Recommandation
        if "CRITICAL_MISMATCH" in str(alerts):
            recommendation = "REJETÉ: Incompatibilités critiques détectées"
        elif overall_score >= 0.8:
            recommendation = "RECOMMANDÉ: Excellente compatibilité"
        elif overall_score >= 0.6:
            recommendation = "À CONSIDÉRER: Bonne compatibilité"
        elif overall_score >= 0.4:
            recommendation = "MOYEN: Compatibilité modérée"
        else:
            recommendation = "FAIBLE: Compatibilité insuffisante"
        
        result = MatchingResult(
            candidate_id=candidate_profile.informations_personnelles.get('nom_complet', 'unknown'),
            job_id=job_posting.informations_poste.get('intitule', 'unknown'),
            overall_score=round(overall_score, 3),
            score_breakdown=score_breakdown,
            hierarchical_compatibility=hierarchical_compatible,
            sector_compatibility=sector_score,
            alerts=alerts,
            recommendation=recommendation,
            metadata={
                'weights_used': self.weights_v31,
                'matching_timestamp': time.time(),
                'integration_version': self.integration_version
            }
        )
        
        print(f"✅ Matching terminé - Score: {overall_score:.3f}")
        return result

    def get_integration_statistics(self) -> Dict[str, Any]:
        return {
            'integration_version': self.integration_version,
            'weights_v31': self.weights_v31,
            'parsers_initialized': True
        }

def main():
    print("🚀 Test Intégration isolée")
    integration = NextvisionGPTIntegration()
    stats = integration.get_integration_statistics()
    print(f"📊 {stats}")

if __name__ == "__main__":
    main()
