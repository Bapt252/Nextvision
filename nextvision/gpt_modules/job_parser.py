#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 NEXTVISION JOB PARSER v4.1 - OpenAI v1.x Compatible
Parser d'offres d'emploi avec support OpenAI v1.x complet
"""

import os
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# OpenAI v1.x Import avec gestion d'erreurs
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
    print("✅ OpenAI v1.x detected for job parsing")
except ImportError as e:
    OPENAI_AVAILABLE = False
    print(f"⚠️ OpenAI not available for job parsing - using fallback: {e}")

@dataclass
class ParsedJobPosting:
    """Structure de données pour offre d'emploi parsée"""
    informations_poste: Dict[str, Any]
    description_detaillee: Dict[str, Any]
    competences_requises: Dict[str, Any]
    conditions_emploi: Dict[str, Any]
    informations_entreprise: Dict[str, Any]
    secteur_activite: Dict[str, Any]
    localisation: Dict[str, Any]
    parsing_metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class NextvisionJobParser:
    """Parser d'offres d'emploi avec OpenAI v1.x"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.parser_version = "4.1.0"
        self.integration_id = "nextvision-job-parser-v1x"
        
        # Initialisation du client OpenAI v1.x
        self.openai_client = None
        if OPENAI_AVAILABLE and self.openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                print(f"✅ OpenAI v1.x job parser client initialized")
            except Exception as e:
                print(f"⚠️ OpenAI job parser client initialization failed: {e}")
                self.openai_client = None
        
        print(f"🚀 NextvisionJobParser v{self.parser_version} initialized")
        
        self.parsing_stats = {
            'total_parsed': 0,
            'openai_success': 0,
            'fallback_used': 0,
            'errors': 0,
            'openai_available': OPENAI_AVAILABLE,
            'client_initialized': self.openai_client is not None
        }

    def parse_job_with_openai(self, job_content: str) -> Optional[ParsedJobPosting]:
        """Parse offre d'emploi avec OpenAI v1.x"""
        if not self.openai_client:
            return None
            
        try:
            prompt = f"""
            Analysez cette offre d'emploi et extrayez les informations selon cette structure JSON exacte:
            
            {{
                "informations_poste": {{
                    "intitule": "string",
                    "type_contrat": "string",
                    "niveau_hierarchique": "ENTRY|ASSOCIATE|MID|SENIOR|MANAGER|EXECUTIVE",
                    "experience_requise": "string",
                    "date_publication": "string",
                    "urgence": "string"
                }},
                "description_detaillee": {{
                    "missions_principales": ["string"],
                    "responsabilites": ["string"],
                    "objectifs": ["string"],
                    "environnement_travail": "string"
                }},
                "competences_requises": {{
                    "competences_techniques": ["string"],
                    "competences_metier": ["string"],
                    "soft_skills": ["string"],
                    "formations_diplomes": ["string"],
                    "langues": [
                        {{
                            "langue": "string",
                            "niveau_requis": "string"
                        }}
                    ]
                }},
                "conditions_emploi": {{
                    "salaire_min": "string",
                    "salaire_max": "string",
                    "avantages": ["string"],
                    "horaires": "string",
                    "teletravail": "string"
                }},
                "informations_entreprise": {{
                    "nom_entreprise": "string",
                    "secteur": "string",
                    "taille": "string",
                    "description": "string"
                }},
                "secteur_activite": {{
                    "secteur_principal": "string",
                    "secteur_final": "string",
                    "sous_secteurs": ["string"]
                }},
                "localisation": {{
                    "ville": "string",
                    "region": "string",
                    "pays": "string",
                    "mobilite_requise": "string"
                }}
            }}
            
            Offre d'emploi à analyser:
            {job_content}
            
            Répondez uniquement avec le JSON, sans autre texte.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Vous êtes un expert en analyse d'offres d'emploi. Répondez uniquement avec du JSON valide."},
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
            
            job_posting = ParsedJobPosting(**parsed_data)
            self.parsing_stats['openai_success'] += 1
            
            return job_posting
            
        except Exception as e:
            print(f"❌ OpenAI job parsing error: {e}")
            self.parsing_stats['errors'] += 1
            return None

    def _get_fallback_job_posting(self) -> ParsedJobPosting:
        """Offre d'emploi de fallback"""
        return ParsedJobPosting(
            informations_poste={
                "intitule": "Assistante de Direction",
                "type_contrat": "CDI",
                "niveau_hierarchique": "MID",
                "experience_requise": "5-10 ans",
                "date_publication": "2024-07-16",
                "urgence": "Normale"
            },
            description_detaillee={
                "missions_principales": [
                    "Assistance à la direction générale",
                    "Gestion administrative",
                    "Coordination des projets"
                ],
                "responsabilites": [
                    "Organisation des plannings",
                    "Préparation des réunions",
                    "Suivi des dossiers"
                ],
                "objectifs": [
                    "Optimiser l'efficacité de la direction",
                    "Assurer la coordination des équipes"
                ],
                "environnement_travail": "Siège social, environnement dynamique"
            },
            competences_requises={
                "competences_techniques": ["Pack Office", "Excel avancé", "Outils collaboratifs"],
                "competences_metier": ["Assistanat de direction", "Gestion administrative", "Communication"],
                "soft_skills": ["Organisation", "Discrétion", "Adaptabilité"],
                "formations_diplomes": ["Bac+3 minimum", "Formation assistanat"],
                "langues": [
                    {"langue": "Français", "niveau_requis": "Natif"},
                    {"langue": "Anglais", "niveau_requis": "Intermédiaire"}
                ]
            },
            conditions_emploi={
                "salaire_min": "35000",
                "salaire_max": "45000",
                "avantages": ["Tickets restaurant", "Mutuelle", "CE"],
                "horaires": "35h/semaine",
                "teletravail": "2 jours/semaine"
            },
            informations_entreprise={
                "nom_entreprise": "Entreprise Test",
                "secteur": "Services",
                "taille": "100-500 salariés",
                "description": "Entreprise leader dans son secteur"
            },
            secteur_activite={
                "secteur_principal": "Services",
                "secteur_final": "Services aux entreprises",
                "sous_secteurs": ["Conseil", "Support"]
            },
            localisation={
                "ville": "Paris",
                "region": "Île-de-France",
                "pays": "France",
                "mobilite_requise": "Occasionnelle"
            },
            parsing_metadata={
                'parser_version': self.parser_version,
                'integration_id': self.integration_id,
                'parsing_timestamp': time.time(),
                'is_fallback': True,
                'openai_available': OPENAI_AVAILABLE
            }
        )

    def parse_job(self, job_content: str) -> ParsedJobPosting:
        """Parse offre d'emploi avec OpenAI v1.x ou fallback"""
        self.parsing_stats['total_parsed'] += 1
        
        # Essai avec OpenAI v1.x
        if self.openai_client:
            job_posting = self.parse_job_with_openai(job_content)
            if job_posting:
                return job_posting
        
        # Fallback
        print("⚠️ Using fallback job posting")
        self.parsing_stats['fallback_used'] += 1
        return self._get_fallback_job_posting()

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
    """Test du parser d'emploi"""
    print("🚀 Test Job Parser OpenAI v1.x")
    parser = NextvisionJobParser()
    
    # Test avec contenu factice
    test_job = "Recherche Assistante de Direction, CDI, Paris, 5 ans d'expérience..."
    job_posting = parser.parse_job(test_job)
    
    print(f"✅ Offre parsée: {job_posting.informations_poste['intitule']}")
    print(f"📊 Statistiques: {parser.get_parsing_statistics()}")

if __name__ == "__main__":
    main()
