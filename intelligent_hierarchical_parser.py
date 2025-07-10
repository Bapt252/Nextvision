#!/usr/bin/env python3
"""
🧠 INTELLIGENT HIERARCHICAL & FUNCTIONAL PARSER
Système modulaire de détection niveau hiérarchique + domaine fonctionnel

Author: Assistant Claude
Version: 1.0.0-intelligent-parser
"""

import re
from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass

class HierarchicalLevel(str, Enum):
    """🏢 Niveaux hiérarchiques universels"""
    DIRECTION = "Direction"        # C-Level, Directeur, DG, PDG
    MANAGEMENT = "Management"      # Manager, Chef, Responsable, Head
    SENIOR = "Senior"             # Senior, Confirmé, Expert, Lead
    CONFIRME = "Confirmé"         # Confirmé, Autonome
    JUNIOR = "Junior"             # Junior, Assistant, Débutant
    STAGIAIRE = "Stagiaire"       # Stage, Apprenti, Alternant

class FunctionalDomain(str, Enum):
    """💼 Domaines fonctionnels universels"""
    FINANCE = "Finance"           # Comptabilité, Finance, Contrôle
    IT = "IT"                     # Informatique, Tech, Dev
    RH = "RH"                     # Ressources Humaines, Recrutement
    COMMERCIAL = "Commercial"     # Vente, Business Dev, Account
    MARKETING = "Marketing"       # Marketing, Communication, Digital
    JURIDIQUE = "Juridique"       # Droit, Legal, Conformité
    OPERATIONS = "Operations"     # Ops, Production, Logistique
    GENERAL = "General"           # Direction générale, Conseil

@dataclass
class ProfileAnalysis:
    """📊 Résultat analyse profil"""
    hierarchical_level: HierarchicalLevel
    functional_domain: FunctionalDomain
    experience_years: Optional[int] = None
    confidence_level: float = 0.0
    detected_keywords: List[str] = None
    salary_range: Optional[Tuple[int, int]] = None
    management_scope: Optional[str] = None

class IntelligentHierarchicalParser:
    """🧠 Parser intelligent niveau + fonction"""
    
    def __init__(self):
        # Patterns hiérarchiques par ordre de priorité (du plus élevé au plus bas)
        self.hierarchical_patterns = {
            HierarchicalLevel.DIRECTION: {
                "keywords": [
                    # C-Level
                    "CEO", "COO", "CTO", "CFO", "CHRO", "CMO", "CDO", "CSO",
                    "DG", "PDG", "Président", "Présidente",
                    # Direction française
                    "Directeur", "Directrice", "DAF", "RAF", "DRH", "DSI", "DMK",
                    "Directeur Général", "Directrice Générale",
                    "Directeur Administratif", "Directeur Financier",
                    "Directeur des Systèmes", "Directeur Marketing",
                    # International
                    "Director", "VP", "Vice President", "General Manager"
                ],
                "context_patterns": [
                    r"en tant que (directeur|directrice|DG|PDG)",
                    r"(directeur|directrice).*depuis.*(\d+)",
                    r"direction.*équipe.*(\d+)",
                    r"budget.*(\d+).*millions?"
                ],
                "experience_min": 10
            },
            
            HierarchicalLevel.MANAGEMENT: {
                "keywords": [
                    "Manager", "Chef", "Responsable", "Superviseur",
                    "Team Lead", "Head of", "Lead", "Principal",
                    "Chef de projet", "Chef d'équipe", "Chef de service",
                    "Responsable commercial", "Responsable RH", "Responsable IT",
                    "Manager commercial", "Account Manager", "Project Manager",
                    "Encadrement", "Management", "Coordination"
                ],
                "context_patterns": [
                    r"manage.*équipe.*(\d+)",
                    r"encadrement.*(\d+).*personnes?",
                    r"responsable.*(\d+).*collaborateurs?",
                    r"management.*(\d+).*ans"
                ],
                "experience_min": 5
            },
            
            HierarchicalLevel.SENIOR: {
                "keywords": [
                    "Senior", "Confirmé", "Expert", "Spécialisé", "Expérimenté",
                    "Consultant Senior", "Développeur Senior", "Comptable Senior",
                    "Analyste Senior", "Expert-comptable", "Ingénieur Senior",
                    "Senior Developer", "Senior Consultant", "Tech Lead"
                ],
                "context_patterns": [
                    r"senior.*(\d+).*ans",
                    r"expert.*(\d+).*années?",
                    r"spécialisé.*depuis.*(\d+)",
                    r"confirmé.*(\d+).*ans"
                ],
                "experience_min": 3
            },
            
            HierarchicalLevel.CONFIRME: {
                "keywords": [
                    "Autonome", "Indépendant", "Opérationnel",
                    "Comptable", "Développeur", "Consultant", "Analyste",
                    "Technicien", "Gestionnaire", "Coordinateur",
                    "Chargé de", "En charge de"
                ],
                "context_patterns": [
                    r"autonome.*(\d+).*ans",
                    r"expérience.*(\d+).*ans",
                    r"pratique.*(\d+).*années?"
                ],
                "experience_min": 2
            },
            
            HierarchicalLevel.JUNIOR: {
                "keywords": [
                    "Junior", "Débutant", "Assistant", "Adjoint",
                    "Junior Developer", "Assistant comptable", "Chargé d'études",
                    "Analyste junior", "Consultant junior", "Support",
                    "Aide", "Collaborateur", "Employé"
                ],
                "context_patterns": [
                    r"junior.*(\d+).*mois",
                    r"débutant.*(\d+).*an",
                    r"première.*expérience",
                    r"récemment.*diplômé"
                ],
                "experience_min": 0
            },
            
            HierarchicalLevel.STAGIAIRE: {
                "keywords": [
                    "Stagiaire", "Stage", "Apprenti", "Apprentissage", "Alternant",
                    "Alternance", "Étudiant", "En formation", "Trainee", "Intern"
                ],
                "context_patterns": [
                    r"stage.*(\d+).*mois",
                    r"apprentissage.*(\d+)",
                    r"alternance.*(\d+)",
                    r"étudiant.*école"
                ],
                "experience_min": 0
            }
        }
        
        # Patterns fonctionnels
        self.functional_patterns = {
            FunctionalDomain.FINANCE: {
                "keywords": [
                    "Comptabilité", "Finance", "Fiscal", "Contrôle de gestion",
                    "DAF", "RAF", "CFO", "Comptable", "Contrôleur",
                    "CEGID", "SAGE", "SAP FI", "Consolidation", "Audit",
                    "Trésorerie", "Budget", "Reporting financier", "IFRS",
                    "Facturation", "Recouvrement", "Paie", "Social"
                ],
                "context": "finance comptabilité fiscal budget"
            },
            
            FunctionalDomain.IT: {
                "keywords": [
                    "Informatique", "IT", "Tech", "Digital", "DSI", "CTO",
                    "Développeur", "Developer", "Programmeur", "Ingénieur",
                    "DevOps", "Sysadmin", "Réseau", "Sécurité", "Cloud",
                    "Python", "Java", "JavaScript", "React", "Angular", "PHP",
                    "SQL", "MongoDB", "Docker", "Kubernetes", "AWS", "Azure",
                    "Cybersécurité", "Intelligence Artificielle", "IA", "AI"
                ],
                "context": "développement programmation infrastructure réseau"
            },
            
            FunctionalDomain.RH: {
                "keywords": [
                    "Ressources Humaines", "RH", "HR", "CHRO", "DRH",
                    "Recrutement", "Talent", "Formation", "Paie", "Social",
                    "SIRH", "Gestion des compétences", "Évaluation",
                    "Relations sociales", "Droit du travail", "Convention collective",
                    "Sourcing", "Chasse de têtes", "Assessment", "Onboarding"
                ],
                "context": "recrutement formation paie social sirh"
            },
            
            FunctionalDomain.COMMERCIAL: {
                "keywords": [
                    "Commercial", "Vente", "Sales", "Business Development",
                    "Account Manager", "Key Account", "Négociation",
                    "Prospection", "CRM", "Salesforce", "Pipedrive",
                    "Chiffre d'affaires", "Objectifs", "Quota", "Commission",
                    "B2B", "B2C", "Grand compte", "PME", "Lead generation"
                ],
                "context": "vente commercial prospection négociation"
            },
            
            FunctionalDomain.MARKETING: {
                "keywords": [
                    "Marketing", "Communication", "Digital Marketing", "CMO",
                    "Growth", "Performance", "SEO", "SEA", "Social Media",
                    "Content Marketing", "Email Marketing", "Automation",
                    "Google Analytics", "Facebook Ads", "LinkedIn Ads",
                    "Brand", "Branding", "Creative", "Webmarketing",
                    "Influence", "Community Management", "Lead nurturing"
                ],
                "context": "marketing communication digital seo sea"
            },
            
            FunctionalDomain.JURIDIQUE: {
                "keywords": [
                    "Juridique", "Droit", "Legal", "Avocat", "Juriste",
                    "Compliance", "Conformité", "Réglementation", "RGPD",
                    "Contrat", "Négociation", "Contentieux", "Propriété intellectuelle",
                    "Droit des sociétés", "Droit social", "Droit commercial",
                    "Due diligence", "Regulatory", "Risk management"
                ],
                "context": "droit juridique compliance contrat réglementation"
            },
            
            FunctionalDomain.OPERATIONS: {
                "keywords": [
                    "Opérations", "Production", "Logistique", "Supply Chain",
                    "COO", "Directeur des opérations", "Process", "Amélioration continue",
                    "Lean", "Six Sigma", "Qualité", "ISO", "Certification",
                    "Planification", "Ordonnancement", "Stocks", "Approvisionnement",
                    "Transport", "Distribution", "Entrepôt", "WMS", "ERP"
                ],
                "context": "production logistique opérations supply chain"
            },
            
            FunctionalDomain.GENERAL: {
                "keywords": [
                    "Direction Générale", "Stratégie", "Conseil", "Management",
                    "Transformation", "Changement", "Innovation", "Développement",
                    "Business Strategy", "Corporate", "Gouvernance",
                    "Executive", "Leadership", "Vision", "Fusions-acquisitions",
                    "Due diligence", "Private Equity", "Venture Capital"
                ],
                "context": "stratégie direction générale transformation conseil"
            }
        }
        
        # Matrice de compatibilité niveau/poste
        self.compatibility_matrix = {
            # Finance
            ("Comptable Unique", FunctionalDomain.FINANCE): {
                HierarchicalLevel.CONFIRME: 1.0,
                HierarchicalLevel.SENIOR: 0.8,
                HierarchicalLevel.JUNIOR: 0.7,
                HierarchicalLevel.MANAGEMENT: 0.3,  # Surqualifié
                HierarchicalLevel.DIRECTION: 0.1   # Très surqualifié
            },
            ("Responsable Comptable", FunctionalDomain.FINANCE): {
                HierarchicalLevel.MANAGEMENT: 1.0,
                HierarchicalLevel.SENIOR: 0.9,
                HierarchicalLevel.CONFIRME: 0.6,
                HierarchicalLevel.DIRECTION: 0.4,
                HierarchicalLevel.JUNIOR: 0.2
            },
            ("DAF", FunctionalDomain.FINANCE): {
                HierarchicalLevel.DIRECTION: 1.0,
                HierarchicalLevel.MANAGEMENT: 0.7,
                HierarchicalLevel.SENIOR: 0.3,
                HierarchicalLevel.CONFIRME: 0.1,
                HierarchicalLevel.JUNIOR: 0.0
            },
            # IT
            ("Développeur", FunctionalDomain.IT): {
                HierarchicalLevel.CONFIRME: 1.0,
                HierarchicalLevel.SENIOR: 0.9,
                HierarchicalLevel.JUNIOR: 0.8,
                HierarchicalLevel.MANAGEMENT: 0.4,
                HierarchicalLevel.DIRECTION: 0.1
            },
            ("Lead Developer", FunctionalDomain.IT): {
                HierarchicalLevel.SENIOR: 1.0,
                HierarchicalLevel.MANAGEMENT: 0.9,
                HierarchicalLevel.CONFIRME: 0.7,
                HierarchicalLevel.DIRECTION: 0.5,
                HierarchicalLevel.JUNIOR: 0.2
            },
            ("CTO", FunctionalDomain.IT): {
                HierarchicalLevel.DIRECTION: 1.0,
                HierarchicalLevel.MANAGEMENT: 0.6,
                HierarchicalLevel.SENIOR: 0.3,
                HierarchicalLevel.CONFIRME: 0.1,
                HierarchicalLevel.JUNIOR: 0.0
            }
        }
    
    def analyze_profile(self, text: str, filename: str = "") -> ProfileAnalysis:
        """🔍 Analyse complète profil candidat"""
        
        text_lower = text.lower()
        
        # 1. Détection niveau hiérarchique
        hierarchical_level, hierarchical_confidence, hierarchical_keywords = self._detect_hierarchical_level(text_lower)
        
        # 2. Détection domaine fonctionnel
        functional_domain, functional_confidence, functional_keywords = self._detect_functional_domain(text_lower)
        
        # 3. Extraction expérience
        experience_years = self._extract_experience_years(text_lower)
        
        # 4. Extraction salaire
        salary_range = self._extract_salary_range(text_lower)
        
        # 5. Détection management
        management_scope = self._detect_management_scope(text_lower)
        
        # 6. Confiance globale
        global_confidence = (hierarchical_confidence + functional_confidence) / 2
        
        return ProfileAnalysis(
            hierarchical_level=hierarchical_level,
            functional_domain=functional_domain,
            experience_years=experience_years,
            confidence_level=global_confidence,
            detected_keywords=hierarchical_keywords + functional_keywords,
            salary_range=salary_range,
            management_scope=management_scope
        )
    
    def _detect_hierarchical_level(self, text: str) -> Tuple[HierarchicalLevel, float, List[str]]:
        """🏢 Détection niveau hiérarchique"""
        
        scores = {}
        detected_keywords = []
        
        for level, config in self.hierarchical_patterns.items():
            score = 0
            level_keywords = []
            
            # Score par mots-clés
            for keyword in config["keywords"]:
                if keyword.lower() in text:
                    score += 1
                    level_keywords.append(keyword)
            
            # Score par patterns contextuels
            for pattern in config.get("context_patterns", []):
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    score += 2  # Patterns contextuels valent plus
                    level_keywords.extend([m if isinstance(m, str) else m[0] for m in matches])
            
            if score > 0:
                scores[level] = score
                detected_keywords.extend(level_keywords)
        
        if not scores:
            return HierarchicalLevel.CONFIRME, 0.3, []
        
        # Niveau avec le score le plus élevé
        best_level = max(scores.keys(), key=lambda x: scores[x])
        max_score = scores[best_level]
        confidence = min(max_score / 5, 1.0)  # Normalisation
        
        return best_level, confidence, detected_keywords
    
    def _detect_functional_domain(self, text: str) -> Tuple[FunctionalDomain, float, List[str]]:
        """💼 Détection domaine fonctionnel"""
        
        scores = {}
        detected_keywords = []
        
        for domain, config in self.functional_patterns.items():
            score = 0
            domain_keywords = []
            
            # Score par mots-clés
            for keyword in config["keywords"]:
                if keyword.lower() in text:
                    score += 1
                    domain_keywords.append(keyword)
            
            # Bonus contexte
            context_words = config["context"].split()
            context_score = sum(1 for word in context_words if word in text)
            score += context_score * 0.5
            
            if score > 0:
                scores[domain] = score
                detected_keywords.extend(domain_keywords)
        
        if not scores:
            return FunctionalDomain.GENERAL, 0.3, []
        
        # Domaine avec le score le plus élevé
        best_domain = max(scores.keys(), key=lambda x: scores[x])
        max_score = scores[best_domain]
        confidence = min(max_score / 10, 1.0)  # Normalisation
        
        return best_domain, confidence, detected_keywords
    
    def _extract_experience_years(self, text: str) -> Optional[int]:
        """📈 Extraction années d'expérience"""
        
        patterns = [
            r'(\d+)\s*ans?\s*d[\'']expérience',
            r'expérience.*?(\d+)\s*ans?',
            r'depuis\s*(\d+)\s*ans?',
            r'(\d+)\s*années?\s*en',
            r'(\d+)\s*ans?\s*dans',
            r'plus\s*de\s*(\d+)\s*ans?'
        ]
        
        years = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            years.extend([int(match) for match in matches if match.isdigit()])
        
        return max(years) if years else None
    
    def _extract_salary_range(self, text: str) -> Optional[Tuple[int, int]]:
        """💰 Extraction fourchette salariale"""
        
        patterns = [
            r'(\d+)k?\s*[-–]\s*(\d+)k?',  # 45K-60K
            r'(\d+)\s*000\s*[-–]\s*(\d+)\s*000',  # 45000-60000
            r'entre\s*(\d+)k?\s*et\s*(\d+)k?',  # entre 45K et 60K
            r'salaire.*?(\d+)k?.*?(\d+)k?'  # salaire 45K à 60K
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                match = matches[0]
                min_sal = int(match[0]) * (1000 if 'k' in text.lower() else 1)
                max_sal = int(match[1]) * (1000 if 'k' in text.lower() else 1)
                return (min_sal, max_sal)
        
        return None
    
    def _detect_management_scope(self, text: str) -> Optional[str]:
        """👥 Détection périmètre management"""
        
        patterns = [
            r'équipe.*?(\d+).*?personnes?',
            r'manage.*?(\d+).*?collaborateurs?',
            r'encadrement.*?(\d+)',
            r'responsable.*?(\d+).*?personnes?'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return f"{matches[0]} personnes"
        
        return None
    
    def calculate_position_compatibility(self, profile: ProfileAnalysis, 
                                       position_title: str, 
                                       position_domain: FunctionalDomain) -> float:
        """🎯 Calcul compatibilité profil/poste avec pondération hiérarchique"""
        
        # Compatibilité domaine fonctionnel
        domain_compatibility = 1.0 if profile.functional_domain == position_domain else 0.3
        
        # Compatibilité niveau hiérarchique
        matrix_key = (position_title, position_domain)
        if matrix_key in self.compatibility_matrix:
            level_compatibility = self.compatibility_matrix[matrix_key].get(
                profile.hierarchical_level, 0.5
            )
        else:
            # Compatibilité par défaut selon niveau
            level_compatibility = {
                HierarchicalLevel.DIRECTION: 0.2,     # Direction généralement surqualifiée
                HierarchicalLevel.MANAGEMENT: 0.7,
                HierarchicalLevel.SENIOR: 0.9,
                HierarchicalLevel.CONFIRME: 1.0,
                HierarchicalLevel.JUNIOR: 0.8,
                HierarchicalLevel.STAGIAIRE: 0.4
            }.get(profile.hierarchical_level, 0.5)
        
        # Score final pondéré
        final_score = (domain_compatibility * 0.4) + (level_compatibility * 0.6)
        
        return min(final_score, 1.0)

def demo_intelligent_parser():
    """🚀 Démonstration parser intelligent"""
    
    parser = IntelligentHierarchicalParser()
    
    # Exemples de profils
    test_profiles = {
        "Charlotte DARMON (DAF)": """
        Directrice Administrative et Financière avec 15 ans d'expérience
        en direction financière. Expert CEGID et SAGE. Management équipe 8 personnes.
        Responsable budget 50M€. Consolidation, reporting IFRS, contrôle de gestion.
        Salaire actuel 95K-120K.
        """,
        
        "Junior Developer": """
        Développeur junior Python avec 2 ans d'expérience. 
        Compétences React, Node.js, MongoDB. Formation récente école d'ingénieur.
        Recherche poste développeur full-stack. Salaire souhaité 40K-50K.
        """,
        
        "Senior Consultant RH": """
        Consultant senior en ressources humaines, 8 ans d'expérience.
        Expert SIRH, recrutement, formation. Management équipe 4 consultants.
        Spécialisé transformation digitale RH. Salaire 65K-80K.
        """
    }
    
    print("🧠 === DÉMONSTRATION PARSER INTELLIGENT ===")
    print("="*60)
    
    for name, profile_text in test_profiles.items():
        print(f"\n👤 PROFIL: {name}")
        print("-" * 40)
        
        analysis = parser.analyze_profile(profile_text)
        
        print(f"🏢 Niveau hiérarchique: {analysis.hierarchical_level.value}")
        print(f"💼 Domaine fonctionnel: {analysis.functional_domain.value}")
        print(f"📈 Expérience: {analysis.experience_years} ans" if analysis.experience_years else "📈 Expérience: Non détectée")
        print(f"🧠 Confiance: {analysis.confidence_level:.2f}")
        print(f"💰 Salaire: {analysis.salary_range}" if analysis.salary_range else "💰 Salaire: Non détecté")
        print(f"👥 Management: {analysis.management_scope}" if analysis.management_scope else "👥 Management: Non détecté")
        print(f"🔍 Mots-clés: {', '.join(analysis.detected_keywords[:5])}...")
        
        # Test compatibilité avec différents postes
        test_positions = [
            ("Comptable Unique", FunctionalDomain.FINANCE),
            ("DAF", FunctionalDomain.FINANCE),
            ("Développeur", FunctionalDomain.IT),
            ("CTO", FunctionalDomain.IT)
        ]
        
        print(f"\n🎯 COMPATIBILITÉ POSTES:")
        for pos_title, pos_domain in test_positions:
            compatibility = parser.calculate_position_compatibility(analysis, pos_title, pos_domain)
            if compatibility >= 0.7:
                status = "✅ EXCELLENT"
            elif compatibility >= 0.5:
                status = "⚠️ MOYEN"
            else:
                status = "❌ INADAPTÉ"
            
            print(f"   {status} {pos_title}: {compatibility:.2f}")

if __name__ == "__main__":
    demo_intelligent_parser()
