#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 NEXTVISION JOB PARSER v3.0 - VERSION MINIMALE
Parser Job sans conflit de modules
"""

import os
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class ParsedJobPosting:
    """Structure de données pour fiche de poste parsée"""
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
    """Parser intelligent pour fiches de poste - version minimale"""
    
    SECTEURS_ACTIVITE = {
        'tech': 'Technologies de l\'information',
        'finance': 'Finance et banque',
        'health': 'Santé et médical',
        'education': 'Education et formation',
        'commerce': 'Commerce et retail',
        'industry': 'Industrie et manufacture',
        'energy': 'Energie et environnement',
        'transport': 'Transport et logistique',
        'construction': 'Immobilier et construction',
        'media': 'Médias et communication',
        'luxury': 'Luxe et mode',
        'agriculture': 'Agriculture et agroalimentaire',
        'services': 'Services aux entreprises',
        'culture': 'Culture et divertissement',
        'sport': 'Sport et loisirs'
    }
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.parser_version = "3.0.1"
        print(f"�� NextvisionJobParser v{self.parser_version} initialisé")

    def _get_fallback_job_posting(self) -> ParsedJobPosting:
        """Fiche de poste de fallback pour démonstration"""
        return ParsedJobPosting(
            informations_poste={
                "intitule": "Développeur Full-Stack Senior",
                "mission_principale": "Développement et maintenance d'applications web complexes",
                "responsabilites": [
                    "Développement frontend et backend",
                    "Architecture technique des projets",
                    "Encadrement d'équipe junior",
                    "Relation client et spécifications"
                ],
                "niveau_poste": "senior",
                "niveau_hierarchique": "SENIOR",
                "equipe": "Équipe de 8 développeurs",
                "reporting": "CTO",
                "contexte": "Renforcement équipe suite croissance"
            },
            informations_entreprise={
                "nom": "TechCorp Innovation",
                "secteur_principal": "tech",
                "taille": "PME (150 employés)",
                "localisation": "Paris",
                "culture": "Startup scale-up dynamique",
                "valeurs": ["Innovation", "Agilité", "Transparence"],
                "avantages_entreprise": ["Participation", "Formation continue", "Flexibilité"]
            },
            competences_requises={
                "techniques": ["JavaScript", "React", "Node.js", "Python", "SQL"],
                "logiciels": ["Git", "Docker", "AWS", "VS Code"],
                "methodologies": ["Agile", "Scrum", "DevOps", "CI/CD"],
                "certifications": ["AWS Certified", "Scrum Master"],
                "soft_skills": ["Leadership", "Communication", "Résolution problèmes"],
                "langues": [
                    {"langue": "Français", "niveau_requis": "Natif", "obligatoire": True},
                    {"langue": "Anglais", "niveau_requis": "Courant", "obligatoire": True}
                ]
            },
            conditions_travail={
                "type_contrat": "CDI",
                "duree_contrat": "",
                "salaire_min": "55",
                "salaire_max": "70",
                "variable": "Participation aux bénéfices",
                "avantages": ["Mutuelle", "RTT", "Tickets restaurant", "Télétravail"],
                "lieu_travail": "Paris 9ème",
                "mobilite_requise": "Occasionnelle",
                "horaires": "Flexibles 9h-18h",
                "teletravail": "3 jours/semaine",
                "date_prise_poste": "Dès que possible"
            },
            profil_recherche={
                "experience_min": "5",
                "experience_max": "10",
                "formation": "Bac+5 Informatique",
                "specialisation": "Développement web",
                "profil_type": "Développeur senior polyvalent",
                "competences_cles": ["Full-stack", "Leadership", "Architecture"],
                "qualites_personnelles": ["Autonomie", "Créativité", "Esprit d'équipe"],
                "deal_breakers": ["Pas d'expérience web", "Pas de leadership"]
            },
            secteur_activite={
                "secteur_detecte": "tech",
                "secteur_final": "tech",
                "sous_secteur": "Développement logiciel",
                "mots_cles_secteur": ["développement", "web", "application", "tech"],
                "compatibilite_secteurs": ["tech", "services", "media"],
                "nextvision_integration": {
                    'secteur_weight': 0.05,
                    'secteur_code': "tech",
                    'secteur_label': "Technologies de l'information",
                    'compatibility_score': 1.0
                }
            },
            parsing_metadata={
                'parser_version': self.parser_version,
                'parsing_timestamp': time.time(),
                'is_fallback': True,
                'openai_used': False
            }
        )

    def parse_job_posting_exhaustive(self, job_text: str, company_sector: Optional[str] = None) -> ParsedJobPosting:
        """Parse exhaustif d'une fiche de poste - version fallback"""
        print(f"🚀 Parsing job posting (fallback): {len(job_text)} caractères")
        job_posting = self._get_fallback_job_posting()
        
        # Adapter le secteur si fourni
        if company_sector and company_sector in self.SECTEURS_ACTIVITE:
            job_posting.secteur_activite.update({
                "secteur_final": company_sector,
                "secteur_entreprise": company_sector
            })
        
        return job_posting

def main():
    """Test du job parser minimal"""
    print("🚀 Test NextvisionJobParser Minimal v3.0")
    parser = NextvisionJobParser()
    job = parser._get_fallback_job_posting()
    print(f"✅ Job posting chargé: {job.informations_poste['intitule']}")

if __name__ == "__main__":
    main()
