#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 NEXTVISION JOB PARSER v3.0 - VERSION ISOLÉE
"""

import os
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

@dataclass
class ParsedJobPosting:
    informations_poste: Dict[str, Any]
    informations_entreprise: Dict[str, Any]
    competences_requises: Dict[str, Any]
    conditions_travail: Dict[str, Any]
    profil_recherche: Dict[str, Any]
    secteur_activite: Dict[str, Any]
    parsing_metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class NextvisionJobParser:
    """Parser Job isolé"""
    
    SECTEURS_ACTIVITE = {
        'tech': 'Technologies de l\'information',
        'finance': 'Finance et banque',
        'luxury': 'Luxe et mode'
    }
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.parser_version = "3.0.1"
        print(f"🚀 NextvisionJobParser v{self.parser_version} initialisé")

    def _get_fallback_job_posting(self) -> ParsedJobPosting:
        """Job posting de fallback"""
        return ParsedJobPosting(
            informations_poste={
                "intitule": "Développeur Full-Stack Senior",
                "niveau_hierarchique": "SENIOR",
                "responsabilites": ["Développement", "Architecture", "Encadrement"]
            },
            informations_entreprise={
                "nom": "TechCorp",
                "secteur_principal": "tech",
                "taille": "PME"
            },
            competences_requises={
                "techniques": ["JavaScript", "React", "Node.js"],
                "soft_skills": ["Leadership", "Communication"]
            },
            conditions_travail={
                "type_contrat": "CDI",
                "salaire_min": "55",
                "salaire_max": "70",
                "lieu_travail": "Paris"
            },
            profil_recherche={
                "experience_min": "5",
                "formation": "Bac+5"
            },
            secteur_activite={
                "secteur_final": "tech",
                "secteur_detecte": "tech",
                "nextvision_integration": {
                    'secteur_weight': 0.05,
                    'secteur_code': "tech",
                    'compatibility_score': 1.0
                }
            },
            parsing_metadata={
                'parser_version': self.parser_version,
                'parsing_timestamp': time.time(),
                'is_fallback': True
            }
        )

def main():
    print("🚀 Test Job Parser isolé")
    parser = NextvisionJobParser()
    job = parser._get_fallback_job_posting()
    print(f"✅ {job.informations_poste['intitule']}")

if __name__ == "__main__":
    main()
