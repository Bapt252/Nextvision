"""
Système de détection de niveau hiérarchique pour Nextvision V3.0
Améliore le parsing pour éviter les inadéquations niveau/poste

🎯 OBJECTIF : Résoudre le problème Charlotte DARMON (DAF matchée sur postes comptables)

Author: Assistant Claude  
Version: 1.0.1
Date: 2025-07-10
"""

import re
from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass

class HierarchicalLevel(Enum):
    """Niveaux hiérarchiques standardisés"""
    EXECUTIVE = 5    # PDG, DG, DAF, DRH
    DIRECTOR = 4     # Directeur, Manager Senior
    MANAGER = 3      # Chef d'équipe, Responsable
    SENIOR = 2       # Senior, Confirmé
    JUNIOR = 1       # Junior, Assistant
    ENTRY = 0        # Stagiaire, Débutant

@dataclass
class HierarchicalMatch:
    """Résultat de l'analyse hiérarchique"""
    detected_level: HierarchicalLevel
    confidence_score: float
    years_experience: Optional[int]
    salary_range: Optional[Tuple[int, int]]
    management_indicators: List[str]
    keywords_found: List[str]

class HierarchicalDetector:
    """Détecteur de niveau hiérarchique dans CV et fiches de poste"""
    
    def __init__(self):
        self.level_patterns = {
            HierarchicalLevel.EXECUTIVE: {
                'titles': [
                    r'\b(?:directeur|directrice)\s+(?:administratif|financier|général|générale)\b',
                    r'\bDAF\b', r'\bDG\b', r'\bPDG\b', r'\bDRH\b', r'\bCEO\b', r'\bCFO\b',
                    r'\b(?:président|présidente)\b', r'\bdirection\s+générale\b'
                ],
                'keywords': [
                    'stratégie', 'gouvernance', 'conseil administration', 'comité direction',
                    'vision stratégique', 'transformation', 'budget global', 'consolidation'
                ],
                'responsibilities': [
                    'pilotage stratégique', 'reporting conseil', 'gestion P&L',
                    'management transversal', 'politique financière'
                ]
            },
            
            HierarchicalLevel.DIRECTOR: {
                'titles': [
                    r'\b(?:directeur|directrice)\s+(?:comptable|financier|opérationnel)\b',
                    r'\bresponsable\s+(?:financier|comptable)\s+(?:groupe|régional)\b',
                    r'\bchef\s+comptable\s+principal\b'
                ],
                'keywords': [
                    'supervision équipe', 'reporting direction', 'budget département',
                    'coordination', 'optimisation processus', 'audit interne'
                ],
                'responsibilities': [
                    'encadrement équipe', 'définition procédures', 'contrôle budgétaire',
                    'reporting mensuel', 'interface direction'
                ]
            },
            
            HierarchicalLevel.MANAGER: {
                'titles': [
                    r'\bresponsable\s+comptable\b', r'\bchef\s+comptable\b',
                    r'\bresponsable\s+paie\b', r'\bresponsable\s+contrôle\s+gestion\b',
                    r'\bmanager\b', r'\bsuperviseur\b'
                ],
                'keywords': [
                    'encadrement', 'formation équipe', 'planning', 'coordination',
                    'validation', 'contrôle', 'reporting hiérarchique'
                ],
                'responsibilities': [
                    'management équipe', 'formation collaborateurs', 'contrôle qualité',
                    'planification', 'reporting'
                ]
            },
            
            HierarchicalLevel.SENIOR: {
                'titles': [
                    r'\bcomptable\s+(?:senior|confirmé|expérimenté)\b',
                    r'\bcomptable\s+principal\b', r'\bcomptable\s+unique\b'
                ],
                'keywords': [
                    'autonomie', 'expertise', 'conseil', 'formation junior',
                    'dossiers complexes', 'client portefeuille'
                ],
                'responsibilities': [
                    'dossiers complexes', 'conseil client', 'formation junior',
                    'expertise technique', 'référent'
                ]
            },
            
            HierarchicalLevel.JUNIOR: {
                'titles': [
                    r'\bcomptable\b', r'\bassistant\s+comptable\b',
                    r'\baide\s+comptable\b', r'\bcomptable\s+général\b'
                ],
                'keywords': [
                    'saisie', 'assistance', 'support', 'apprentissage',
                    'formation', 'suivi', 'exécution'
                ],
                'responsibilities': [
                    'saisie comptable', 'classement', 'assistance',
                    'tâches courantes', 'formation'
                ]
            },
            
            HierarchicalLevel.ENTRY: {
                'titles': [
                    r'\bstagiaire\b', r'\bapprenti\b', r'\bdébutant\b',
                    r'\bjunior\s+débutant\b', r'\bassistant\s+junior\b'
                ],
                'keywords': [
                    'stage', 'apprentissage', 'formation', 'découverte',
                    'initiation', 'accompagnement'
                ],
                'responsibilities': [
                    'tâches simples', 'formation', 'découverte métier',
                    'assistance senior', 'apprentissage'
                ]
            }
        }
        
        self.experience_patterns = [
            r'(\d+)\s+ans?\s+d[\'\s]*expérience',
            r'expérience\s+de\s+(\d+)\s+ans?',
            r'(\d+)\s+années?\s+d[\'\s]*expérience',
            r'plus\s+de\s+(\d+)\s+ans?',
            r'(\d+)\s+ans?\s+en\s+(?:comptabilité|finance|gestion)'
        ]
        
        self.salary_patterns = [
            r'(\d+)(?:\s*000)?\s*€?\s*-\s*(\d+)(?:\s*000)?\s*€?',
            r'entre\s+(\d+)(?:\s*000)?\s*et\s+(\d+)(?:\s*000)?\s*€?',
            r'salaire\s*:?\s*(\d+)(?:\s*000)?\s*€?',
            r'rémunération\s*:?\s*(\d+)(?:\s*000)?\s*€?'
        ]

    def detect_hierarchical_level(self, text: str, is_job_posting: bool = False) -> HierarchicalMatch:
        """
        Détecte le niveau hiérarchique dans un texte (CV ou fiche de poste)
        
        Args:
            text: Texte à analyser
            is_job_posting: True si c'est une fiche de poste, False si c'est un CV
        
        Returns:
            HierarchicalMatch avec le niveau détecté et les indicateurs
        """
        text_lower = text.lower()
        best_match = None
        highest_confidence = 0.0
        
        for level, patterns in self.level_patterns.items():
            confidence, keywords = self._calculate_level_confidence(text_lower, patterns)
            
            if confidence > highest_confidence:
                highest_confidence = confidence
                best_match = level
                matched_keywords = keywords
        
        # Extraction des années d'expérience
        years_exp = self._extract_years_experience(text_lower)
        
        # Extraction de la fourchette salariale
        salary_range = self._extract_salary_range(text_lower)
        
        # Détection des indicateurs de management
        management_indicators = self._detect_management_indicators(text_lower)
        
        # Ajustement du niveau basé sur l'expérience
        if best_match and years_exp:
            best_match = self._adjust_level_by_experience(best_match, years_exp)
            highest_confidence = min(highest_confidence + 0.1, 1.0)
        
        return HierarchicalMatch(
            detected_level=best_match or HierarchicalLevel.JUNIOR,
            confidence_score=highest_confidence,
            years_experience=years_exp,
            salary_range=salary_range,
            management_indicators=management_indicators,
            keywords_found=matched_keywords if best_match else []
        )
    
    def _calculate_level_confidence(self, text: str, patterns: Dict) -> Tuple[float, List[str]]:
        """Calcule le score de confiance pour un niveau donné"""
        total_score = 0.0
        found_keywords = []
        
        # Vérification des titres (poids: 0.5)
        for title_pattern in patterns.get('titles', []):
            if re.search(title_pattern, text, re.IGNORECASE):
                total_score += 0.5
                found_keywords.append(title_pattern)
        
        # Vérification des mots-clés (poids: 0.3)
        keyword_score = 0
        for keyword in patterns.get('keywords', []):
            if keyword in text:
                keyword_score += 1
                found_keywords.append(keyword)
        
        if patterns.get('keywords'):
            total_score += (keyword_score / len(patterns['keywords'])) * 0.3
        
        # Vérification des responsabilités (poids: 0.2)
        resp_score = 0
        for resp in patterns.get('responsibilities', []):
            if resp in text:
                resp_score += 1
                found_keywords.append(resp)
        
        if patterns.get('responsibilities'):
            total_score += (resp_score / len(patterns['responsibilities'])) * 0.2
        
        return min(total_score, 1.0), found_keywords
    
    def _extract_years_experience(self, text: str) -> Optional[int]:
        """Extrait le nombre d'années d'expérience"""
        for pattern in self.experience_patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        return None
    
    def _extract_salary_range(self, text: str) -> Optional[Tuple[int, int]]:
        """Extrait la fourchette salariale"""
        for pattern in self.salary_patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 2:
                    min_sal = int(match.group(1))
                    max_sal = int(match.group(2))
                    # Ajustement pour les salaires en milliers
                    if min_sal < 200:  # Probablement en milliers
                        min_sal *= 1000
                        max_sal *= 1000
                    return (min_sal, max_sal)
                else:
                    salary = int(match.group(1))
                    if salary < 200:  # Probablement en milliers
                        salary *= 1000
                    return (salary, salary)
        return None
    
    def _detect_management_indicators(self, text: str) -> List[str]:
        """Détecte les indicateurs de management"""
        management_keywords = [
            'encadrement', 'management', 'équipe', 'supervision', 'pilotage',
            'coordination', 'formation', 'recrutement', 'évaluation',
            'budget', 'planning', 'objectifs', 'reporting'
        ]
        
        found_indicators = []
        for keyword in management_keywords:
            if keyword in text:
                found_indicators.append(keyword)
        
        return found_indicators
    
    def _adjust_level_by_experience(self, base_level: HierarchicalLevel, years: int) -> HierarchicalLevel:
        """Ajuste le niveau en fonction de l'expérience"""
        if years < 2:
            return min(base_level, HierarchicalLevel.JUNIOR)
        elif years < 5:
            return base_level
        elif years < 10:
            return HierarchicalLevel(min(base_level.value + 1, HierarchicalLevel.EXECUTIVE.value))
        else:  # 10+ ans
            return HierarchicalLevel(min(base_level.value + 2, HierarchicalLevel.EXECUTIVE.value))

class HierarchicalScoring:
    """Système de scoring prenant en compte le niveau hiérarchique"""
    
    def __init__(self):
        self.detector = HierarchicalDetector()
        
        # Matrice de compatibilité hiérarchique (candidat vs poste)
        self.compatibility_matrix = {
            # Candidat EXECUTIVE peut : EXECUTIVE(1.0), DIRECTOR(0.8), MANAGER(0.3)
            HierarchicalLevel.EXECUTIVE: {
                HierarchicalLevel.EXECUTIVE: 1.0,
                HierarchicalLevel.DIRECTOR: 0.8,
                HierarchicalLevel.MANAGER: 0.3,
                HierarchicalLevel.SENIOR: 0.1,
                HierarchicalLevel.JUNIOR: 0.0,
                HierarchicalLevel.ENTRY: 0.0
            },
            # Candidat DIRECTOR peut : EXECUTIVE(0.7), DIRECTOR(1.0), MANAGER(0.9)
            HierarchicalLevel.DIRECTOR: {
                HierarchicalLevel.EXECUTIVE: 0.7,
                HierarchicalLevel.DIRECTOR: 1.0,
                HierarchicalLevel.MANAGER: 0.9,
                HierarchicalLevel.SENIOR: 0.5,
                HierarchicalLevel.JUNIOR: 0.2,
                HierarchicalLevel.ENTRY: 0.0
            },
            # Candidat MANAGER peut : DIRECTOR(0.6), MANAGER(1.0), SENIOR(0.8)
            HierarchicalLevel.MANAGER: {
                HierarchicalLevel.EXECUTIVE: 0.4,
                HierarchicalLevel.DIRECTOR: 0.6,
                HierarchicalLevel.MANAGER: 1.0,
                HierarchicalLevel.SENIOR: 0.8,
                HierarchicalLevel.JUNIOR: 0.6,
                HierarchicalLevel.ENTRY: 0.2
            },
            # Candidat SENIOR peut : MANAGER(0.7), SENIOR(1.0), JUNIOR(0.9)
            HierarchicalLevel.SENIOR: {
                HierarchicalLevel.EXECUTIVE: 0.2,
                HierarchicalLevel.DIRECTOR: 0.4,
                HierarchicalLevel.MANAGER: 0.7,
                HierarchicalLevel.SENIOR: 1.0,
                HierarchicalLevel.JUNIOR: 0.9,
                HierarchicalLevel.ENTRY: 0.5
            },
            # Candidat JUNIOR peut : SENIOR(0.6), JUNIOR(1.0), ENTRY(0.8)
            HierarchicalLevel.JUNIOR: {
                HierarchicalLevel.EXECUTIVE: 0.0,
                HierarchicalLevel.DIRECTOR: 0.1,
                HierarchicalLevel.MANAGER: 0.3,
                HierarchicalLevel.SENIOR: 0.6,
                HierarchicalLevel.JUNIOR: 1.0,
                HierarchicalLevel.ENTRY: 0.8
            },
            # Candidat ENTRY peut : JUNIOR(0.7), ENTRY(1.0)
            HierarchicalLevel.ENTRY: {
                HierarchicalLevel.EXECUTIVE: 0.0,
                HierarchicalLevel.DIRECTOR: 0.0,
                HierarchicalLevel.MANAGER: 0.1,
                HierarchicalLevel.SENIOR: 0.2,
                HierarchicalLevel.JUNIOR: 0.7,
                HierarchicalLevel.ENTRY: 1.0
            }
        }
    
    def calculate_hierarchical_score(self, candidate_cv: str, job_posting: str) -> Dict:
        """
        Calcule le score de compatibilité hiérarchique entre candidat et poste
        
        Returns:
            Dict avec score, niveaux détectés, et analyse détaillée
        """
        # Analyse du CV candidat
        candidate_analysis = self.detector.detect_hierarchical_level(candidate_cv, is_job_posting=False)
        
        # Analyse de la fiche de poste
        job_analysis = self.detector.detect_hierarchical_level(job_posting, is_job_posting=True)
        
        # Calcul de la compatibilité
        compatibility_score = self.compatibility_matrix[candidate_analysis.detected_level][job_analysis.detected_level]
        
        # Ajustement basé sur la confiance
        confidence_factor = (candidate_analysis.confidence_score + job_analysis.confidence_score) / 2
        final_score = compatibility_score * confidence_factor
        
        # Analyse de l'écart salarial si disponible
        salary_warning = self._check_salary_mismatch(candidate_analysis, job_analysis)
        
        return {
            'hierarchical_score': final_score,
            'compatibility_level': self._get_compatibility_description(compatibility_score),
            'candidate_level': candidate_analysis.detected_level.name,
            'job_level': job_analysis.detected_level.name,
            'candidate_confidence': candidate_analysis.confidence_score,
            'job_confidence': job_analysis.confidence_score,
            'candidate_experience': candidate_analysis.years_experience,
            'salary_warning': salary_warning,
            'detailed_analysis': {
                'candidate_keywords': candidate_analysis.keywords_found,
                'job_keywords': job_analysis.keywords_found,
                'management_indicators': candidate_analysis.management_indicators
            }
        }
    
    def _get_compatibility_description(self, score: float) -> str:
        """Retourne une description de la compatibilité"""
        if score >= 0.9:
            return "Excellent match"
        elif score >= 0.7:
            return "Bon match"
        elif score >= 0.5:
            return "Match acceptable"
        elif score >= 0.3:
            return "Match partiel - attention surqualification"
        else:
            return "Incompatible - écart hiérarchique trop important"
    
    def _check_salary_mismatch(self, candidate_analysis: HierarchicalMatch, 
                              job_analysis: HierarchicalMatch) -> Optional[str]:
        """Vérifie les incompatibilités salariales"""
        if candidate_analysis.salary_range and job_analysis.salary_range:
            candidate_min = candidate_analysis.salary_range[0]
            job_max = job_analysis.salary_range[1]
            
            if candidate_min > job_max * 1.2:  # Candidat veut 20% de plus que le max du poste
                return f"Écart salarial important: candidat minimum {candidate_min}€ vs poste maximum {job_max}€"
        
        return None
