#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 NEXTVISION GPT INTEGRATION v3.1 - VERSION MINIMALE
Intégration sans conflit de modules
"""

import os
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Imports locaux
try:
    from services.nextvision_gpt_parser_minimal import NextvisionGPTParser, ParsedProfile
    from services.nextvision_job_parser_minimal import NextvisionJobParser, ParsedJobPosting
    GPT_PARSERS_AVAILABLE = True
except ImportError:
    GPT_PARSERS_AVAILABLE = False

# Imports modules Nextvision existants (optionnels)
try:
    from services.hierarchical_detector import HierarchicalDetector
    from services.enhanced_commitment_bridge_v3_hierarchical import EnhancedCommitmentBridgeV3
    NEXTVISION_MODULES_AVAILABLE = True
except ImportError:
    NEXTVISION_MODULES_AVAILABLE = False

@dataclass
class MatchingResult:
    """Résultat de matching entre candidat et poste"""
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
    """Intégrateur principal GPT Nextvision v3.1 - version minimale"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.integration_version = "3.1.0"
        
        # Initialisation des parsers
        if GPT_PARSERS_AVAILABLE:
            self.cv_parser = NextvisionGPTParser(openai_api_key)
            self.job_parser = NextvisionJobParser(openai_api_key)
            print("✅ Parsers GPT minimaux initialisés")
        else:
            self.cv_parser = None
            self.job_parser = None
            print("❌ Parsers GPT non disponibles")
        
        # Initialisation modules Nextvision (optionnels)
        if NEXTVISION_MODULES_AVAILABLE:
            try:
                self.hierarchical_detector = HierarchicalDetector()
                self.commitment_bridge = EnhancedCommitmentBridgeV3()
                print("✅ Modules Nextvision V3.1 chargés")
            except Exception as e:
                print(f"⚠️ Erreur modules Nextvision: {e}")
                self.hierarchical_detector = None
                self.commitment_bridge = None
        else:
            self.hierarchical_detector = None
            self.commitment_bridge = None
            print("⚠️ Modules Nextvision non disponibles - mode standalone")
        
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
        
        try:
            # Calcul des scores par composant
            
            # 1. Score sémantique (30%) - Simulation basée sur compétences
            candidate_skills = []
            for skill_category in candidate_profile.competences_detaillees.values():
                if isinstance(skill_category, list):
                    candidate_skills.extend(skill_category)
            
            job_skills = []
            for skill_category in job_posting.competences_requises.values():
                if isinstance(skill_category, list):
                    job_skills.extend(skill_category)
            
            if candidate_skills and job_skills:
                common_skills = set(candidate_skills) & set(job_skills)
                semantic_score = min(len(common_skills) / len(job_skills), 1.0)
            else:
                semantic_score = 0.6  # Score neutre si pas d'info
            
            # 2. Score hiérarchique (15%) - CRITIQUE pour Charlotte DARMON
            candidate_level = candidate_profile.analyse_cv.get('niveau_hierarchique', 'MID')
            job_level = job_posting.informations_poste.get('niveau_hierarchique', 'MID')
            
            hierarchy_order = ['ENTRY', 'ASSOCIATE', 'MID', 'SENIOR', 'MANAGER', 'EXECUTIVE']
            
            try:
                candidate_index = hierarchy_order.index(candidate_level)
                job_index = hierarchy_order.index(job_level)
                
                diff = abs(candidate_index - job_index)
                if diff == 0:
                    hierarchical_score = 1.0
                elif diff == 1:
                    hierarchical_score = 0.8
                elif diff == 2:
                    hierarchical_score = 0.6
                else:
                    hierarchical_score = 0.3
                
                hierarchical_compatible = diff <= 2
                
                # CAS CHARLOTTE DARMON : si surqualification majeure (diff > 2)
                if candidate_index > job_index + 2:
                    hierarchical_compatible = False
                    hierarchical_score = 0.2  # Score très bas pour surqualification
                    
            except ValueError:
                hierarchical_score = 0.5
                hierarchical_compatible = True
            
            # 3. Score salarial (20%) - Simulation
            salary_score = 0.8  # Simulation - bonne compatibilité
            
            # 4. Score expérience (20%) - Simulation basée sur années
            experience_score = 0.85  # Simulation
            
            # 5. Score localisation (15%) - Simulation
            candidate_location = candidate_profile.informations_personnelles.get('ville', '')
            job_location = job_posting.conditions_travail.get('lieu_travail', '')
            
            if candidate_location and job_location:
                if candidate_location.lower() in job_location.lower() or job_location.lower() in candidate_location.lower():
                    location_score = 1.0
                else:
                    location_score = 0.4  # Mobilité possible
            else:
                location_score = 0.6
            
            # 6. Score secteur (5%) - NOUVEAU V3.1
            candidate_sectors = candidate_profile.analyse_cv.get('secteurs_experiences', [])
            job_sector = job_posting.secteur_activite.get('secteur_final', '')
            
            if not candidate_sectors or not job_sector:
                sector_score = 0.6  # Neutre si pas d'info
            else:
                # Vérifier secteurs préférés/rédhibitoires
                sector_prefs = candidate_profile.informations_complementaires.get('secteurs_preferences', {})
                preferes = sector_prefs.get('preferes', [])
                redhibitoires = sector_prefs.get('redhibitoires', [])
                
                if job_sector in redhibitoires:
                    sector_score = 0.0  # Rédhibitoire
                elif job_sector in preferes:
                    sector_score = 1.0  # Préféré
                elif job_sector in candidate_sectors:
                    sector_score = 0.8  # Expérience dans le secteur
                else:
                    sector_score = 0.5  # Neutre
            
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
            
            # Alerte surqualification hiérarchique (cas Charlotte DARMON)
            if not hierarchical_compatible:
                alerts.append("CRITICAL_MISMATCH: Surqualification hiérarchique détectée")
            
            # Alerte secteur rédhibitoire
            if sector_score == 0.0:
                alerts.append("CRITICAL_MISMATCH: Secteur rédhibitoire pour le candidat")
            
            # Alerte score global faible
            if overall_score < 0.3:
                alerts.append("LOW_COMPATIBILITY: Score global très faible")
            
            # Recommandation basée sur score et alertes
            if "CRITICAL_MISMATCH" in str(alerts):
                recommendation = "REJETÉ: Incompatibilités critiques détectées"
            elif overall_score >= 0.8:
                recommendation = "RECOMMANDÉ: Excellente compatibilité"
            elif overall_score >= 0.6:
                recommendation = "À CONSIDÉRER: Bonne compatibilité"
            elif overall_score >= 0.4:
                recommendation = "MOYEN: Compatibilité modérée, entretien recommandé"
            else:
                recommendation = "FAIBLE: Compatibilité insuffisante"
            
            result = MatchingResult(
                candidate_id=candidate_profile.parsing_metadata.get('file_path', candidate_profile.informations_personnelles.get('nom_complet', 'unknown')),
                job_id=job_posting.parsing_metadata.get('job_id', job_posting.informations_poste.get('intitule', 'unknown')),
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
            
        except Exception as e:
            print(f"❌ Erreur matching: {e}")
            raise

    def get_integration_statistics(self) -> Dict[str, Any]:
        """Statistiques complètes d'intégration"""
        return {
            'integration_version': self.integration_version,
            'modules_available': {
                'nextvision_core': NEXTVISION_MODULES_AVAILABLE,
                'gpt_parsers': GPT_PARSERS_AVAILABLE
            },
            'weights_v31': self.weights_v31,
            'parsers_initialized': {
                'cv_parser': self.cv_parser is not None,
                'job_parser': self.job_parser is not None
            }
        }

def main():
    """Test d'intégration minimal"""
    print("🚀 Test NextvisionGPTIntegration Minimal v3.1")
    integration = NextvisionGPTIntegration()
    stats = integration.get_integration_statistics()
    print(f"📊 Statistiques: {stats}")
    print("✅ Intégration minimale initialisée !")

if __name__ == "__main__":
    main()
