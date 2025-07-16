#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 NEXTVISION GPT INTEGRATION v3.2 - OpenAI v1.x Compatible
Intégration complète avec support OpenAI v1.x complet
"""

import os
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# OpenAI v1.x Import avec gestion d'erreurs
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
    print("✅ OpenAI v1.x available for integration")
except ImportError as e:
    OPENAI_AVAILABLE = False
    print(f"⚠️ OpenAI not available for integration - using fallback: {e}")

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
    """Intégrateur principal GPT Nextvision v3.2 - OpenAI v1.x compatible"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.integration_version = "3.2.0"
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        # Initialisation du client OpenAI v1.x pour l'intégration
        self.openai_client = None
        if OPENAI_AVAILABLE and self.openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                print("✅ OpenAI v1.x integration client initialized")
            except Exception as e:
                print(f"⚠️ OpenAI integration client initialization failed: {e}")
                self.openai_client = None
        
        # Initialisation des parsers OpenAI v1.x compatibles
        self.cv_parser = NextvisionGPTParser(openai_api_key)
        self.job_parser = NextvisionJobParser(openai_api_key)
        print("✅ OpenAI v1.x compatible parsers initialized")
        
        # Pondérations V3.2 avec amélioration secteur
        self.weights_v32 = {
            'semantic': 0.25,      # 25% - Compatibilité sémantique
            'hierarchical': 0.20,  # 20% - Niveau hiérarchique (augmenté)
            'salary': 0.18,        # 18% - Compatibilité salariale
            'experience': 0.20,    # 20% - Années d'expérience
            'location': 0.12,      # 12% - Localisation
            'sector': 0.05         # 5% - Secteur d'activité
        }
        
        # Statistiques d'intégration
        self.integration_stats = {
            'total_matchings': 0,
            'openai_enhanced_matchings': 0,
            'fallback_matchings': 0,
            'openai_available': OPENAI_AVAILABLE,
            'client_initialized': self.openai_client is not None
        }
        
        print(f"🚀 NextvisionGPTIntegration v{self.integration_version} initialized")
        print(f"📊 OpenAI Status: {'✅ Available' if self.openai_client else '⚠️ Fallback Mode'}")

    def enhance_matching_with_openai(self, candidate_profile: ParsedProfile, job_posting: ParsedJobPosting) -> Optional[Dict[str, Any]]:
        """Améliore le matching avec OpenAI v1.x"""
        if not self.openai_client:
            return None
        
        try:
            # Contexte pour l'amélioration du matching
            context = {
                'candidate_name': candidate_profile.informations_personnelles.get('nom_complet', 'Unknown'),
                'candidate_level': candidate_profile.analyse_cv.get('niveau_hierarchique', 'MID'),
                'candidate_sectors': candidate_profile.analyse_cv.get('secteurs_experiences', []),
                'candidate_experience': candidate_profile.analyse_cv.get('anciennete_professionnelle', 'Unknown'),
                'job_title': job_posting.informations_poste.get('intitule', 'Unknown'),
                'job_level': job_posting.informations_poste.get('niveau_hierarchique', 'MID'),
                'job_sector': job_posting.secteur_activite.get('secteur_final', 'Unknown'),
                'job_experience': job_posting.informations_poste.get('experience_requise', 'Unknown')
            }
            
            prompt = f"""
            Analysez cette compatibilité candidat-poste et donnez un score détaillé:
            
            CANDIDAT:
            - Nom: {context['candidate_name']}
            - Niveau: {context['candidate_level']}
            - Secteurs: {context['candidate_sectors']}
            - Expérience: {context['candidate_experience']}
            
            POSTE:
            - Intitulé: {context['job_title']}
            - Niveau: {context['job_level']}
            - Secteur: {context['job_sector']}
            - Expérience requise: {context['job_experience']}
            
            Analysez les points suivants et donnez un score 0-1 pour chaque:
            1. Compatibilité sémantique (compétences vs besoins)
            2. Compatibilité hiérarchique (niveaux correspondants)
            3. Compatibilité salariale (attentes vs offre)
            4. Compatibilité expérience (années vs requis)
            5. Compatibilité localisation (mobilité vs lieu)
            6. Compatibilité secteur (secteurs vs poste)
            
            Répondez avec ce JSON:
            {{
                "semantic_score": float,
                "hierarchical_score": float,
                "salary_score": float,
                "experience_score": float,
                "location_score": float,
                "sector_score": float,
                "analysis": "Analyse détaillée de la compatibilité",
                "recommendations": ["Recommandation 1", "Recommandation 2"]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Vous êtes un expert en matching RH. Analysez objectivement la compatibilité."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            import json
            enhanced_data = json.loads(response.choices[0].message.content)
            enhanced_data['openai_enhanced'] = True
            enhanced_data['model_used'] = 'gpt-3.5-turbo'
            
            self.integration_stats['openai_enhanced_matchings'] += 1
            return enhanced_data
            
        except Exception as e:
            print(f"❌ OpenAI enhancement error: {e}")
            return None

    def compute_enhanced_matching(self, candidate_profile: ParsedProfile, job_posting: ParsedJobPosting) -> MatchingResult:
        """Matching amélioré V3.2 avec OpenAI v1.x"""
        print("🎯 MATCHING AMÉLIORÉ V3.2 - OpenAI v1.x")
        self.integration_stats['total_matchings'] += 1
        
        # Tentative d'amélioration avec OpenAI v1.x
        openai_enhancement = self.enhance_matching_with_openai(candidate_profile, job_posting)
        
        if openai_enhancement:
            # Utilise les scores OpenAI
            score_breakdown = {
                'semantic': openai_enhancement.get('semantic_score', 0.6),
                'hierarchical': openai_enhancement.get('hierarchical_score', 0.5),
                'salary': openai_enhancement.get('salary_score', 0.7),
                'experience': openai_enhancement.get('experience_score', 0.8),
                'location': openai_enhancement.get('location_score', 1.0),
                'sector': openai_enhancement.get('sector_score', 0.5)
            }
            analysis_source = "OpenAI v1.x Enhanced"
        else:
            # Fallback aux scores par défaut
            self.integration_stats['fallback_matchings'] += 1
            
            # Score hiérarchique amélioré
            candidate_level = candidate_profile.analyse_cv.get('niveau_hierarchique', 'MID')
            job_level = job_posting.informations_poste.get('niveau_hierarchique', 'MID')
            
            hierarchy_order = ['ENTRY', 'ASSOCIATE', 'MID', 'SENIOR', 'MANAGER', 'EXECUTIVE']
            
            try:
                candidate_index = hierarchy_order.index(candidate_level)
                job_index = hierarchy_order.index(job_level)
                
                diff = abs(candidate_index - job_index)
                
                # Cas de surqualification majeure
                if candidate_index > job_index + 2:
                    hierarchical_score = 0.2
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
            
            # Score secteur amélioré
            candidate_sectors = candidate_profile.analyse_cv.get('secteurs_experiences', [])
            job_sector = job_posting.secteur_activite.get('secteur_final', '')
            
            if job_sector in candidate_sectors:
                sector_score = 0.9
            elif any(sector in job_sector for sector in candidate_sectors):
                sector_score = 0.7
            else:
                sector_score = 0.5
            
            score_breakdown = {
                'semantic': 0.6,
                'hierarchical': hierarchical_score,
                'salary': 0.7,
                'experience': 0.8,
                'location': 1.0,
                'sector': sector_score
            }
            analysis_source = "Fallback Analysis"
        
        # Calcul du score global pondéré V3.2
        overall_score = sum(score * self.weights_v32[component] for component, score in score_breakdown.items())
        
        # Détermination de la compatibilité hiérarchique
        hierarchical_compatible = score_breakdown['hierarchical'] >= 0.5
        
        # Génération des alertes
        alerts = []
        if not hierarchical_compatible:
            alerts.append("CRITICAL_MISMATCH: Incompatibilité hiérarchique détectée")
        
        if score_breakdown['sector'] < 0.6:
            alerts.append("SECTOR_MISMATCH: Secteur d'activité différent")
        
        if overall_score < 0.3:
            alerts.append("LOW_COMPATIBILITY: Score global très faible")
        
        # Recommandation améliorée
        if "CRITICAL_MISMATCH" in str(alerts):
            recommendation = "REJETÉ: Incompatibilités critiques détectées"
        elif overall_score >= 0.8:
            recommendation = "FORTEMENT RECOMMANDÉ: Excellente compatibilité"
        elif overall_score >= 0.65:
            recommendation = "RECOMMANDÉ: Bonne compatibilité"
        elif overall_score >= 0.45:
            recommendation = "À CONSIDÉRER: Compatibilité modérée"
        else:
            recommendation = "FAIBLE: Compatibilité insuffisante"
        
        # Métadonnées enrichies
        metadata = {
            'weights_used': self.weights_v32,
            'matching_timestamp': time.time(),
            'integration_version': self.integration_version,
            'analysis_source': analysis_source,
            'openai_available': OPENAI_AVAILABLE,
            'client_initialized': self.openai_client is not None
        }
        
        if openai_enhancement:
            metadata.update({
                'openai_analysis': openai_enhancement.get('analysis', ''),
                'openai_recommendations': openai_enhancement.get('recommendations', [])
            })
        
        result = MatchingResult(
            candidate_id=candidate_profile.informations_personnelles.get('nom_complet', 'unknown'),
            job_id=job_posting.informations_poste.get('intitule', 'unknown'),
            overall_score=round(overall_score, 3),
            score_breakdown=score_breakdown,
            hierarchical_compatibility=hierarchical_compatible,
            sector_compatibility=score_breakdown['sector'],
            alerts=alerts,
            recommendation=recommendation,
            metadata=metadata
        )
        
        print(f"✅ Matching V3.2 terminé - Score: {overall_score:.3f} ({analysis_source})")
        return result

    def get_integration_statistics(self) -> Dict[str, Any]:
        """Statistiques détaillées de l'intégration"""
        total = self.integration_stats['total_matchings']
        openai_rate = (self.integration_stats['openai_enhanced_matchings'] / total * 100) if total > 0 else 0
        
        return {
            **self.integration_stats,
            'integration_version': self.integration_version,
            'weights_v32': self.weights_v32,
            'openai_enhancement_rate': round(openai_rate, 2),
            'cv_parser_stats': self.cv_parser.get_parsing_statistics(),
            'job_parser_stats': self.job_parser.get_parsing_statistics(),
            'status': 'OpenAI v1.x Enhanced' if self.openai_client else 'Fallback Mode Compatible'
        }

def main():
    """Test de l'intégration OpenAI v1.x"""
    print("🚀 Test Intégration OpenAI v1.x")
    integration = NextvisionGPTIntegration()
    
    # Test avec profils factices
    cv_content = "Dorothée Lim, Assistante de Direction, 17 ans d'expérience..."
    job_content = "Recherche Assistante de Direction, CDI, Paris..."
    
    profile = integration.cv_parser.parse_cv(cv_content)
    job_posting = integration.job_parser.parse_job(job_content)
    
    result = integration.compute_enhanced_matching(profile, job_posting)
    
    print(f"✅ Matching: {result.candidate_id} vs {result.job_id}")
    print(f"📊 Score: {result.overall_score} - {result.recommendation}")
    print(f"📈 Statistiques: {integration.get_integration_statistics()}")

if __name__ == "__main__":
    main()
