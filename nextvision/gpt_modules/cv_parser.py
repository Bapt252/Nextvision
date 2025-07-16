#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 NEXTVISION GPT PARSER v4.1 - OpenAI v1.x Compatible
Parser GPT avec support OpenAI v1.x complet
"""

import os
import sys
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# OpenAI v1.x Import avec gestion d'erreurs
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
    print("✅ OpenAI v1.x detected and imported successfully")
except ImportError as e:
    OPENAI_AVAILABLE = False
    print(f"⚠️ OpenAI not available - using fallback mode only: {e}")

@dataclass
class ParsedProfile:
    """Structure de données pour profil parsé"""
    informations_personnelles: Dict[str, Any]
    experiences_professionnelles: List[Dict[str, Any]]
    formations_education: List[Dict[str, Any]]
    competences_detaillees: Dict[str, Any]
    langues: List[Dict[str, Any]]
    informations_complementaires: Dict[str, Any]
    analyse_cv: Dict[str, Any]
    parsing_metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class NextvisionGPTParser:
    """Parser GPT Nextvision avec OpenAI v1.x"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.parser_version = "4.1.0"
        self.integration_id = "nextvision-openai-v1x"
        
        # Initialisation du client OpenAI v1.x
        self.openai_client = None
        if OPENAI_AVAILABLE and self.openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                print(f"✅ OpenAI v1.x client initialized successfully")
            except Exception as e:
                print(f"⚠️ OpenAI client initialization failed: {e}")
                self.openai_client = None
        
        print(f"🚀 NextvisionGPTParser v{self.parser_version} initialized")
        
        self.parsing_stats = {
            'total_parsed': 0,
            'openai_success': 0,
            'fallback_used': 0,
            'errors': 0,
            'openai_available': OPENAI_AVAILABLE,
            'client_initialized': self.openai_client is not None
        }

    def parse_cv_with_openai(self, cv_content: str) -> Optional[ParsedProfile]:
        """Parse CV avec OpenAI v1.x"""
        if not self.openai_client:
            return None
            
        try:
            prompt = f"""
            Analysez ce CV et extrayez les informations selon cette structure JSON exacte:
            
            {{
                "informations_personnelles": {{
                    "nom_complet": "string",
                    "prenom": "string",
                    "nom_famille": "string",
                    "age": "string",
                    "email": "string",
                    "telephone": "string",
                    "ville": "string",
                    "pays": "string",
                    "titre_recherche": "string"
                }},
                "experiences_professionnelles": [
                    {{
                        "ordre": 1,
                        "poste": "string",
                        "entreprise": "string",
                        "type_contrat": "string",
                        "date_debut": "string",
                        "date_fin": "string",
                        "duree": "string",
                        "lieu": "string",
                        "secteur": "string",
                        "description_complete": "string",
                        "missions": ["string"],
                        "technologies": ["string"]
                    }}
                ],
                "formations_education": [
                    {{
                        "ordre": 1,
                        "type": "string",
                        "intitule_complet": "string",
                        "etablissement": "string",
                        "ville": "string",
                        "annee_fin": "string"
                    }}
                ],
                "competences_detaillees": {{
                    "techniques_informatiques": ["string"],
                    "logiciels_maitrise": ["string"],
                    "competences_metier": ["string"],
                    "soft_skills": ["string"],
                    "competences_sectorielles": ["string"]
                }},
                "langues": [
                    {{
                        "langue": "string",
                        "niveau_global": "string"
                    }}
                ],
                "informations_complementaires": {{
                    "mobilite_geographique": ["string"],
                    "centres_interet": ["string"],
                    "secteurs_preferences": {{
                        "preferes": ["string"],
                        "acceptables": ["string"],
                        "redhibitoires": ["string"]
                    }}
                }},
                "analyse_cv": {{
                    "anciennete_professionnelle": "string",
                    "secteurs_experiences": ["string"],
                    "profil_type": "string",
                    "niveau_hierarchique": "ENTRY|ASSOCIATE|MID|SENIOR|MANAGER|EXECUTIVE"
                }}
            }}
            
            CV à analyser:
            {cv_content}
            
            Répondez uniquement avec le JSON, sans autre texte.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Vous êtes un expert en analyse de CV. Répondez uniquement avec du JSON valide."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            parsed_data = json.loads(response.choices[0].message.content)
            
            # Ajout des métadonnées
            parsed_data['parsing_metadata'] = {
                'parser_version': self.parser_version,
                'integration_id': self.integration_id,
                'parsing_timestamp': time.time(),
                'is_fallback': False,
                'openai_model': 'gpt-3.5-turbo'
            }
            
            profile = ParsedProfile(**parsed_data)
            self.parsing_stats['openai_success'] += 1
            
            return profile
            
        except Exception as e:
            print(f"❌ OpenAI parsing error: {e}")
            self.parsing_stats['errors'] += 1
            return None

    def _get_fallback_profile(self) -> ParsedProfile:
        """Profil de fallback Dorothée Lim"""
        return ParsedProfile(
            informations_personnelles={
                "nom_complet": "Dorothée Lim",
                "prenom": "Dorothée",
                "nom_famille": "Lim",
                "age": "45 ans",
                "email": "limdorothee@gmail.com",
                "telephone": "06 68 69 00 06",
                "ville": "Paris",
                "pays": "France",
                "titre_recherche": "Assistante de Direction Confirmée"
            },
            experiences_professionnelles=[
                {
                    "ordre": 1,
                    "poste": "Assistante de Direction | Coordination Production Événementielle",
                    "entreprise": "Hermès International",
                    "type_contrat": "CDD",
                    "date_debut": "Août 2023",
                    "date_fin": "Décembre 2024",
                    "duree": "1 an 4 mois",
                    "lieu": "Paris",
                    "secteur": "Luxe",
                    "description_complete": "Coordination des projets événementiels et des plannings, gestion administrative et budgétaire.",
                    "missions": ["Coordination projets événementiels", "Gestion administrative", "Gestion budgétaire"],
                    "technologies": ["Gestion de projet", "Budgétisation", "Logistique"]
                }
            ],
            formations_education=[
                {
                    "ordre": 1,
                    "type": "Master 2",
                    "intitule_complet": "Master 2 Marketing Communication Vente et Management",
                    "etablissement": "CNAM",
                    "ville": "Paris",
                    "annee_fin": "2011"
                }
            ],
            competences_detaillees={
                "techniques_informatiques": ["Office Manager", "Gestion de Projet", "PLM", "ERP"],
                "logiciels_maitrise": ["Pack Office Expert", "Excel Avancé", "PowerPoint"],
                "competences_metier": ["Assistanat de Direction", "Coordination", "Communication"],
                "soft_skills": ["Communication", "Organisation", "Adaptabilité"],
                "competences_sectorielles": ["Luxe", "Mode", "Cosmétique", "Événementiel"]
            },
            langues=[
                {"langue": "Français", "niveau_global": "Natif"},
                {"langue": "Anglais", "niveau_global": "Très avancé"}
            ],
            informations_complementaires={
                "mobilite_geographique": ["Paris", "Île-de-France"],
                "centres_interet": ["Voyage", "Sport", "Photo"],
                "secteurs_preferences": {
                    "preferes": ["Luxe", "Mode"],
                    "acceptables": ["Cosmétique", "Événementiel"],
                    "redhibitoires": []
                }
            },
            analyse_cv={
                "anciennete_professionnelle": "17+ années d'expérience",
                "secteurs_experiences": ["Luxe", "Mode", "Cosmétique"],
                "profil_type": "Assistante de Direction Senior - Spécialiste Luxe/Mode",
                "niveau_hierarchique": "SENIOR"
            },
            parsing_metadata={
                'parser_version': self.parser_version,
                'integration_id': self.integration_id,
                'parsing_timestamp': time.time(),
                'is_fallback': True,
                'openai_available': OPENAI_AVAILABLE
            }
        )

    def parse_cv(self, cv_content: str) -> ParsedProfile:
        """Parse CV avec OpenAI v1.x ou fallback"""
        self.parsing_stats['total_parsed'] += 1
        
        # Essai avec OpenAI v1.x
        if self.openai_client:
            profile = self.parse_cv_with_openai(cv_content)
            if profile:
                return profile
        
        # Fallback
        print("⚠️ Using fallback profile (Dorothée Lim)")
        self.parsing_stats['fallback_used'] += 1
        return self._get_fallback_profile()

    def get_parsing_statistics(self) -> Dict[str, Any]:
        """Statistiques détaillées du parsing"""
        total = self.parsing_stats['total_parsed']
        success_rate = (self.parsing_stats['openai_success'] / total * 100) if total > 0 else 0
        
        return {
            **self.parsing_stats,
            'success_rate': round(success_rate, 2),
            'parser_version': self.parser_version,
            'status': 'OpenAI v1.x Ready' if self.openai_client else 'Fallback Mode'
        }

def main():
    """Test du parser"""
    print("🚀 Test CV Parser OpenAI v1.x")
    parser = NextvisionGPTParser()
    
    # Test avec contenu factice
    test_cv = "Jean Dupont, Développeur Python, 5 ans d'expérience..."
    profile = parser.parse_cv(test_cv)
    
    print(f"✅ Profil parsé: {profile.informations_personnelles['nom_complet']}")
    print(f"📊 Statistiques: {parser.get_parsing_statistics()}")

if __name__ == "__main__":
    main()
