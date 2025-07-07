"""
🎯 Nextvision v2.0 - Services de Scoring Bidirectionnel

Implémentation des 4 composants business prioritaires :
- Sémantique (35%) : Correspondance CV ↔ Fiche de poste 
- Salaire (25%) : Budget entreprise vs attentes candidat
- Expérience (20%) : Années d'expérience requises
- Localisation (15%) : Impact géographique avec Google Maps Intelligence

Architecture adaptative bidirectionnelle selon :
- Côté candidat : raison d'écoute (pourquoi_ecoute)
- Côté entreprise : urgence de recrutement

Author: NEXTEN Team
Version: 2.0.0 - Bidirectional Scoring
"""

from typing import Dict, List, Tuple, Optional
import logging
import time
import re
from dataclasses import dataclass
from datetime import datetime

# Import des modèles bidirectionnels
from nextvision.models.bidirectional_models import (
    BiDirectionalCandidateProfile, BiDirectionalCompanyProfile,
    BiDirectionalMatchingRequest, BiDirectionalMatchingResponse,
    ComponentWeights, AdaptiveWeightingConfig, MatchingComponentScores,
    RaisonEcouteCandidat, UrgenceRecrutement, NiveauExperience
)

# Import des services Google Maps existants
from nextvision.services.google_maps_service import GoogleMapsService
from nextvision.engines.location_scoring import LocationScoringEngine
from nextvision.services.transport_calculator import TransportCalculator

logger = logging.getLogger(__name__)

# === SCORING INTERFACES ===

@dataclass
class ScoringResult:
    """Résultat de scoring standardisé"""
    score: float  # 0.0 à 1.0
    details: Dict
    confidence: float
    processing_time_ms: float
    error_message: Optional[str] = None

class BaseScorer:
    """Interface de base pour tous les scorers"""
    
    def __init__(self, weight: float = 1.0):
        self.weight = weight
        self.name = self.__class__.__name__
    
    def calculate_score(self, candidat: BiDirectionalCandidateProfile, 
                       entreprise: BiDirectionalCompanyProfile) -> ScoringResult:
        """Méthode abstraite à implémenter par chaque scorer"""
        raise NotImplementedError

# === 1. SEMANTIC SCORER (35% - COMPOSANT LE PLUS IMPORTANT) ===

class SemanticScorer(BaseScorer):
    """🧠 Scoring sémantique : Correspondance CV ↔ Fiche de poste"""
    
    def __init__(self, weight: float = 0.35):
        super().__init__(weight)
        # Dictionnaire de synonymes pour matching intelligent
        self.synonymes_competences = {
            "comptabilité": ["comptable", "gestion comptable", "finance", "fiscalité"],
            "cegid": ["sage", "erp comptable", "logiciel comptable"],
            "python": ["programmation python", "développement python", "coding python"],
            "javascript": ["js", "développement web", "frontend", "nodejs"],
            "management": ["encadrement", "leadership", "gestion équipe"],
        }
    
    def calculate_score(self, candidat: BiDirectionalCandidateProfile, 
                       entreprise: BiDirectionalCompanyProfile) -> ScoringResult:
        """Calcule correspondance sémantique candidat ↔ entreprise"""
        start_time = time.time()
        
        try:
            # 1. Matching compétences techniques (40% du score sémantique)
            competences_score = self._match_competences(
                candidat.competences.competences_techniques,
                entreprise.exigences.competences_obligatoires + entreprise.exigences.competences_souhaitees
            )
            
            # 2. Matching titre/poste (30% du score sémantique)
            poste_score = self._match_poste_title(
                candidat.experiences_detaillees,
                entreprise.poste.titre
            )
            
            # 3. Matching secteur d'activité (20% du score sémantique)
            secteur_score = self._match_secteur(
                candidat.attentes.secteurs_preferes,
                entreprise.entreprise.secteur
            )
            
            # 4. Matching logiciels/outils (10% du score sémantique)
            logiciels_score = self._match_logiciels(
                candidat.competences.logiciels_maitrise,
                entreprise.poste.competences_requises
            )
            
            # Score sémantique final pondéré
            semantic_score = (
                competences_score * 0.40 +
                poste_score * 0.30 +
                secteur_score * 0.20 +
                logiciels_score * 0.10
            )
            
            details = {
                "competences_score": competences_score,
                "poste_score": poste_score,
                "secteur_score": secteur_score,
                "logiciels_score": logiciels_score,
                "competences_matchees": self._get_matched_competences(candidat, entreprise),
                "competences_manquantes": self._get_missing_competences(candidat, entreprise)
            }
            
            processing_time = (time.time() - start_time) * 1000
            confidence = min(0.95, semantic_score * 1.1)  # Confiance basée sur le score
            
            logger.info(f"🧠 Semantic Score: {semantic_score:.3f} (confiance: {confidence:.3f})")
            
            return ScoringResult(
                score=semantic_score,
                details=details,
                confidence=confidence,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur SemanticScorer: {e}")
            return ScoringResult(
                score=0.0,
                details={"error": str(e)},
                confidence=0.0,
                processing_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e)
            )
    
    def _match_competences(self, competences_candidat: List[str], competences_requises: List[str]) -> float:
        """Matching intelligent des compétences avec synonymes"""
        if not competences_requises:
            return 1.0
        
        matches = 0
        for comp_requise in competences_requises:
            if self._is_competence_match(comp_requise, competences_candidat):
                matches += 1
        
        return min(1.0, matches / len(competences_requises))
    
    def _is_competence_match(self, competence_requise: str, competences_candidat: List[str]) -> bool:
        """Vérifie si une compétence match (exact ou synonyme)"""
        comp_requise_lower = competence_requise.lower()
        
        for comp_candidat in competences_candidat:
            comp_candidat_lower = comp_candidat.lower()
            
            # Match exact
            if comp_requise_lower in comp_candidat_lower or comp_candidat_lower in comp_requise_lower:
                return True
            
            # Match via synonymes
            for mot_cle, synonymes in self.synonymes_competences.items():
                if mot_cle in comp_requise_lower:
                    for synonyme in synonymes:
                        if synonyme in comp_candidat_lower:
                            return True
        
        return False
    
    def _match_poste_title(self, experiences: List, titre_poste: str) -> float:
        """Match titre de poste avec expériences"""
        if not experiences:
            return 0.5  # Score neutre si pas d'expérience
        
        titre_lower = titre_poste.lower()
        best_match = 0.0
        
        for exp in experiences:
            poste_lower = exp.poste.lower()
            # Score basé sur les mots communs
            mots_titre = set(titre_lower.split())
            mots_poste = set(poste_lower.split())
            communs = len(mots_titre.intersection(mots_poste))
            score = communs / max(len(mots_titre), len(mots_poste))
            best_match = max(best_match, score)
        
        return min(1.0, best_match)
    
    def _match_secteur(self, secteurs_candidat: List[str], secteur_entreprise: str) -> float:
        """Match secteur d'activité"""
        if not secteurs_candidat:
            return 0.7  # Score neutre si pas de préférence secteur
        
        secteur_lower = secteur_entreprise.lower()
        for secteur_pref in secteurs_candidat:
            if secteur_pref.lower() in secteur_lower or secteur_lower in secteur_pref.lower():
                return 1.0
        
        return 0.3  # Pénalité si secteur non préféré
    
    def _match_logiciels(self, logiciels_candidat: List[str], competences_poste: List[str]) -> float:
        """Match logiciels/outils maîtrisés"""
        if not competences_poste:
            return 1.0
        
        matches = 0
        for comp_poste in competences_poste:
            for logiciel in logiciels_candidat:
                if logiciel.lower() in comp_poste.lower():
                    matches += 1
                    break
        
        return min(1.0, matches / len(competences_poste)) if competences_poste else 1.0
    
    def _get_matched_competences(self, candidat: BiDirectionalCandidateProfile, 
                                entreprise: BiDirectionalCompanyProfile) -> List[str]:
        """Retourne les compétences qui matchent"""
        matched = []
        for comp_req in entreprise.exigences.competences_obligatoires:
            if self._is_competence_match(comp_req, candidat.competences.competences_techniques):
                matched.append(comp_req)
        return matched
    
    def _get_missing_competences(self, candidat: BiDirectionalCandidateProfile,
                                entreprise: BiDirectionalCompanyProfile) -> List[str]:
        """Retourne les compétences manquantes"""
        missing = []
        for comp_req in entreprise.exigences.competences_obligatoires:
            if not self._is_competence_match(comp_req, candidat.competences.competences_techniques):
                missing.append(comp_req)
        return missing

# === 2. SALARY SCORER (25% - TRÈS IMPORTANT CÔTÉ BUDGET) ===

class SalaryScorer(BaseScorer):
    """💰 Scoring salariale : Budget entreprise vs attentes candidat"""
    
    def __init__(self, weight: float = 0.25):
        super().__init__(weight)
    
    def calculate_score(self, candidat: BiDirectionalCandidateProfile,
                       entreprise: BiDirectionalCompanyProfile) -> ScoringResult:
        """Calcule compatibilité salariale bidirectionnelle"""
        start_time = time.time()
        
        try:
            candidat_min = candidat.attentes.salaire_min
            candidat_max = candidat.attentes.salaire_max
            entreprise_min = entreprise.poste.salaire_min or 0
            entreprise_max = entreprise.poste.salaire_max or 999999
            
            # 1. Compatibilité de base (60% du score)
            compatibilite_score = self._calculate_salary_compatibility(
                candidat_min, candidat_max, entreprise_min, entreprise_max
            )
            
            # 2. Positionnement dans la fourchette (25% du score)
            positionnement_score = self._calculate_positioning_score(
                candidat_min, candidat_max, entreprise_min, entreprise_max
            )
            
            # 3. Négociabilité (15% du score)
            negociabilite_score = self._calculate_negotiability_score(
                candidat, entreprise
            )
            
            # Score salarial final
            salary_score = (
                compatibilite_score * 0.60 +
                positionnement_score * 0.25 +
                negociabilite_score * 0.15
            )
            
            details = {
                "candidat_fourchette": f"{candidat_min}€ - {candidat_max}€",
                "entreprise_fourchette": f"{entreprise_min}€ - {entreprise_max}€",
                "compatibilite_score": compatibilite_score,
                "positionnement_score": positionnement_score,
                "negociabilite_score": negociabilite_score,
                "overlap_amount": self._calculate_overlap(candidat_min, candidat_max, entreprise_min, entreprise_max),
                "recommendation": self._get_salary_recommendation(candidat_min, candidat_max, entreprise_min, entreprise_max)
            }
            
            processing_time = (time.time() - start_time) * 1000
            confidence = 0.9 if compatibilite_score > 0.7 else 0.6
            
            logger.info(f"💰 Salary Score: {salary_score:.3f} (confiance: {confidence:.3f})")
            
            return ScoringResult(
                score=salary_score,
                details=details,
                confidence=confidence,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur SalaryScorer: {e}")
            return ScoringResult(
                score=0.0,
                details={"error": str(e)},
                confidence=0.0,
                processing_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e)
            )
    
    def _calculate_salary_compatibility(self, c_min: int, c_max: int, e_min: int, e_max: int) -> float:
        """Calcule compatibilité de base des fourchettes"""
        if e_max >= c_min and e_min <= c_max:
            # Il y a un overlap
            overlap = min(c_max, e_max) - max(c_min, e_min)
            candidat_range = c_max - c_min
            entreprise_range = e_max - e_min
            avg_range = (candidat_range + entreprise_range) / 2
            return min(1.0, overlap / avg_range)
        else:
            # Pas d'overlap - calculer distance
            if c_min > e_max:
                gap = c_min - e_max
                return max(0.0, 1.0 - (gap / c_min))
            else:
                gap = e_min - c_max
                return max(0.0, 1.0 - (gap / e_min))
    
    def _calculate_positioning_score(self, c_min: int, c_max: int, e_min: int, e_max: int) -> float:
        """Score basé sur positionnement dans les fourchettes"""
        if e_max < c_min:
            return 0.0  # Entreprise trop basse
        
        if e_min > c_max:
            return 0.2  # Entreprise trop haute mais négociable
        
        # Calcul position moyenne candidat vs entreprise
        candidat_mid = (c_min + c_max) / 2
        entreprise_mid = (e_min + e_max) / 2
        
        if abs(candidat_mid - entreprise_mid) / candidat_mid < 0.1:
            return 1.0  # Très bon alignement
        elif abs(candidat_mid - entreprise_mid) / candidat_mid < 0.2:
            return 0.8  # Bon alignement
        else:
            return 0.5  # Alignement moyen
    
    def _calculate_negotiability_score(self, candidat: BiDirectionalCandidateProfile,
                                     entreprise: BiDirectionalCompanyProfile) -> float:
        """Score de négociabilité basé sur contexte"""
        score = 0.5  # Base neutre
        
        # Boost si urgence entreprise élevée
        if entreprise.recrutement.urgence == UrgenceRecrutement.CRITIQUE:
            score += 0.3
        elif entreprise.recrutement.urgence == UrgenceRecrutement.URGENT:
            score += 0.2
        
        # Boost si candidat expérimenté
        if candidat.experience_globale in [NiveauExperience.CONFIRME, NiveauExperience.SENIOR]:
            score += 0.2
        
        return min(1.0, score)
    
    def _calculate_overlap(self, c_min: int, c_max: int, e_min: int, e_max: int) -> int:
        """Calcule montant de l'overlap en euros"""
        if e_max >= c_min and e_min <= c_max:
            return min(c_max, e_max) - max(c_min, e_min)
        return 0
    
    def _get_salary_recommendation(self, c_min: int, c_max: int, e_min: int, e_max: int) -> str:
        """Recommandation salariale"""
        overlap = self._calculate_overlap(c_min, c_max, e_min, e_max)
        
        if overlap > 0:
            mid_overlap = (max(c_min, e_min) + min(c_max, e_max)) / 2
            return f"Proposer {int(mid_overlap)}€ (zone de convergence)"
        elif c_min > e_max:
            return f"Augmenter budget entreprise d'au moins {c_min - e_max}€"
        else:
            return f"Négocier à la baisse candidat de {e_min - c_max}€ max"

# === 3. EXPERIENCE SCORER (20% - ANNÉES REQUISES) ===

class ExperienceScorer(BaseScorer):
    """📈 Scoring expérience : Années requises vs expérience candidat"""
    
    def __init__(self, weight: float = 0.20):
        super().__init__(weight)
    
    def calculate_score(self, candidat: BiDirectionalCandidateProfile,
                       entreprise: BiDirectionalCompanyProfile) -> ScoringResult:
        """Calcule adéquation expérience candidat vs exigences"""
        start_time = time.time()
        
        try:
            # 1. Parse de l'expérience requise (format "5 ans - 10 ans")
            exp_min_req, exp_max_req = self._parse_experience_requise(entreprise.exigences.experience_requise)
            
            # 2. Extraction années d'expérience candidat
            exp_candidat = self._get_candidat_experience_years(candidat)
            
            # 3. Calcul score de base (70% du score)
            base_score = self._calculate_experience_match(exp_candidat, exp_min_req, exp_max_req)
            
            # 4. Bonus qualité expérience (20% du score)
            qualite_score = self._calculate_experience_quality(candidat, entreprise)
            
            # 5. Bonus progression carrière (10% du score)
            progression_score = self._calculate_career_progression(candidat)
            
            # Score expérience final
            experience_score = (
                base_score * 0.70 +
                qualite_score * 0.20 +
                progression_score * 0.10
            )
            
            details = {
                "experience_candidat_annees": exp_candidat,
                "experience_requise": entreprise.exigences.experience_requise,
                "experience_min_requise": exp_min_req,
                "experience_max_requise": exp_max_req,
                "base_score": base_score,
                "qualite_score": qualite_score,
                "progression_score": progression_score,
                "niveau_candidat": candidat.experience_globale.value,
                "adequation": self._get_experience_adequation(exp_candidat, exp_min_req, exp_max_req)
            }
            
            processing_time = (time.time() - start_time) * 1000
            confidence = 0.9 if base_score > 0.8 else 0.7
            
            logger.info(f"📈 Experience Score: {experience_score:.3f} (confiance: {confidence:.3f})")
            
            return ScoringResult(
                score=experience_score,
                details=details,
                confidence=confidence,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur ExperienceScorer: {e}")
            return ScoringResult(
                score=0.0,
                details={"error": str(e)},
                confidence=0.0,
                processing_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e)
            )
    
    def _parse_experience_requise(self, exp_requise: str) -> Tuple[int, int]:
        """Parse format ChatGPT '5 ans - 10 ans' vers (5, 10)"""
        try:
            # Regex pour capturer les nombres
            pattern = r'(\d+)\s*ans?\s*-\s*(\d+)\s*ans?'
            match = re.search(pattern, exp_requise.lower())
            
            if match:
                return int(match.group(1)), int(match.group(2))
            
            # Fallback: essayer de trouver un seul nombre
            single_pattern = r'(\d+)\s*ans?'
            single_match = re.search(single_pattern, exp_requise.lower())
            if single_match:
                years = int(single_match.group(1))
                return years, years + 2  # Fourchette par défaut
            
            # Valeur par défaut
            return 2, 10
            
        except Exception:
            return 2, 10  # Fourchette large par défaut
    
    def _get_candidat_experience_years(self, candidat: BiDirectionalCandidateProfile) -> int:
        """Extrait années d'expérience du candidat"""
        # Mapping des niveaux vers années
        niveau_mapping = {
            NiveauExperience.DEBUTANT: 1,
            NiveauExperience.JUNIOR: 3,
            NiveauExperience.CONFIRME: 7,
            NiveauExperience.SENIOR: 12
        }
        
        base_years = niveau_mapping.get(candidat.experience_globale, 3)
        
        # Ajustement basé sur les expériences détaillées
        if candidat.experiences_detaillees:
            total_experience = 0
            for exp in candidat.experiences_detaillees:
                # Parse durée si disponible
                duree_years = self._parse_duree_experience(exp.duree)
                total_experience += duree_years
            
            if total_experience > 0:
                return min(total_experience, base_years + 2)  # Cap réaliste
        
        return base_years
    
    def _parse_duree_experience(self, duree: str) -> int:
        """Parse durée d'expérience vers années"""
        try:
            # Patterns pour différents formats
            if 'an' in duree.lower():
                years_match = re.search(r'(\d+)\s*ans?', duree.lower())
                if years_match:
                    return int(years_match.group(1))
            
            if 'mois' in duree.lower():
                months_match = re.search(r'(\d+)\s*mois', duree.lower())
                if months_match:
                    return max(1, int(months_match.group(1)) // 12)
            
            return 1  # Défaut 1 an
        except:
            return 1
    
    def _calculate_experience_match(self, exp_candidat: int, exp_min: int, exp_max: int) -> float:
        """Calcule adéquation expérience"""
        if exp_min <= exp_candidat <= exp_max:
            return 1.0  # Parfait match
        
        if exp_candidat < exp_min:
            # Sous-qualifié
            gap = exp_min - exp_candidat
            if gap <= 1:
                return 0.8  # Acceptable avec 1 an de moins
            elif gap <= 2:
                return 0.6  # Possible avec formation
            else:
                return max(0.2, 1.0 - (gap / exp_min))
        
        else:
            # Sur-qualifié
            excess = exp_candidat - exp_max
            if excess <= 2:
                return 0.9  # Léger sur-qualifié acceptable
            elif excess <= 5:
                return 0.7  # Sur-qualifié mais gérable
            else:
                return 0.5  # Très sur-qualifié - risque de fuite
    
    def _calculate_experience_quality(self, candidat: BiDirectionalCandidateProfile,
                                    entreprise: BiDirectionalCompanyProfile) -> float:
        """Score qualité de l'expérience"""
        if not candidat.experiences_detaillees:
            return 0.5
        
        quality_score = 0.0
        
        for exp in candidat.experiences_detaillees:
            # Bonus si expérience dans secteur similaire
            if entreprise.entreprise.secteur.lower() in exp.entreprise.lower():
                quality_score += 0.3
            
            # Bonus si titre de poste similaire
            if any(mot in exp.poste.lower() for mot in entreprise.poste.titre.lower().split()):
                quality_score += 0.2
            
            # Bonus si compétences acquises pertinentes
            competences_pertinentes = 0
            for comp in exp.competences_acquises:
                if any(comp.lower() in req.lower() for req in entreprise.exigences.competences_obligatoires):
                    competences_pertinentes += 1
            
            if competences_pertinentes > 0:
                quality_score += min(0.3, competences_pertinentes * 0.1)
        
        return min(1.0, quality_score)
    
    def _calculate_career_progression(self, candidat: BiDirectionalCandidateProfile) -> float:
        """Score progression de carrière"""
        if len(candidat.experiences_detaillees) < 2:
            return 0.5
        
        # Simple heuristique basée sur évolution des titres
        progression_indicators = ['senior', 'lead', 'chef', 'manager', 'directeur']
        has_progression = False
        
        for exp in candidat.experiences_detaillees:
            if any(indicator in exp.poste.lower() for indicator in progression_indicators):
                has_progression = True
                break
        
        return 0.8 if has_progression else 0.5
    
    def _get_experience_adequation(self, exp_candidat: int, exp_min: int, exp_max: int) -> str:
        """Retourne évaluation textuelle de l'adéquation"""
        if exp_min <= exp_candidat <= exp_max:
            return "Parfaitement adapté"
        elif exp_candidat < exp_min:
            gap = exp_min - exp_candidat
            if gap <= 1:
                return "Légèrement sous-qualifié (acceptable)"
            else:
                return f"Sous-qualifié de {gap} ans"
        else:
            excess = exp_candidat - exp_max
            if excess <= 2:
                return "Légèrement sur-qualifié"
            else:
                return f"Sur-qualifié de {excess} ans"

# === 4. LOCATION SCORER (15% - GOOGLE MAPS INTELLIGENCE) ===

class LocationScorer(BaseScorer):
    """📍 Scoring localisation : Impact géographique avec Google Maps Intelligence"""
    
    def __init__(self, weight: float = 0.15, google_maps_service: GoogleMapsService = None,
                 location_scoring_engine: LocationScoringEngine = None):
        super().__init__(weight)
        self.google_maps_service = google_maps_service
        self.location_scoring_engine = location_scoring_engine
    
    def calculate_score(self, candidat: BiDirectionalCandidateProfile,
                       entreprise: BiDirectionalCompanyProfile) -> ScoringResult:
        """Calcule score localisation avec Google Maps Intelligence"""
        start_time = time.time()
        
        try:
            if self.location_scoring_engine and self.google_maps_service:
                # Utilisation du système Google Maps existant
                return self._calculate_with_google_maps(candidat, entreprise, start_time)
            else:
                # Fallback sur calcul simplifié
                return self._calculate_simplified_location(candidat, entreprise, start_time)
                
        except Exception as e:
            logger.error(f"❌ Erreur LocationScorer: {e}")
            return ScoringResult(
                score=0.5,  # Score neutre en cas d'erreur
                details={"error": str(e), "mode": "fallback"},
                confidence=0.3,
                processing_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e)
            )
    
    def _calculate_with_google_maps(self, candidat: BiDirectionalCandidateProfile,
                                   entreprise: BiDirectionalCompanyProfile,
                                   start_time: float) -> ScoringResult:
        """Calcul avec Google Maps Intelligence (à implémenter)"""
        # TODO: Intégrer avec le LocationScoringEngine existant
        # Pour l'instant, fallback sur méthode simplifiée
        return self._calculate_simplified_location(candidat, entreprise, start_time)
    
    def _calculate_simplified_location(self, candidat: BiDirectionalCandidateProfile,
                                     entreprise: BiDirectionalCompanyProfile,
                                     start_time: float) -> ScoringResult:
        """Calcul localisation simplifié"""
        
        # 1. Comparaison ville/arrondissement (60% du score)
        ville_score = self._compare_cities(
            candidat.attentes.localisation_preferee,
            entreprise.poste.localisation
        )
        
        # 2. Distance approximative (25% du score)
        distance_score = self._estimate_distance_score(
            candidat.attentes.localisation_preferee,
            entreprise.poste.localisation,
            candidat.attentes.distance_max_km
        )
        
        # 3. Remote compatibility (15% du score)
        remote_score = self._calculate_remote_compatibility(candidat, entreprise)
        
        # Score localisation final
        location_score = (
            ville_score * 0.60 +
            distance_score * 0.25 +
            remote_score * 0.15
        )
        
        details = {
            "candidat_localisation": candidat.attentes.localisation_preferee,
            "entreprise_localisation": entreprise.poste.localisation,
            "distance_max_km": candidat.attentes.distance_max_km,
            "ville_score": ville_score,
            "distance_score": distance_score,
            "remote_score": remote_score,
            "remote_candidat": candidat.attentes.remote_accepte,
            "remote_entreprise": entreprise.conditions.remote_possible
        }
        
        processing_time = (time.time() - start_time) * 1000
        confidence = 0.7  # Confiance moyenne pour calcul simplifié
        
        logger.info(f"📍 Location Score: {location_score:.3f} (mode simplifié)")
        
        return ScoringResult(
            score=location_score,
            details=details,
            confidence=confidence,
            processing_time_ms=processing_time
        )
    
    def _compare_cities(self, loc_candidat: str, loc_entreprise: str) -> float:
        """Compare localisation candidat vs entreprise"""
        candidat_lower = loc_candidat.lower()
        entreprise_lower = loc_entreprise.lower()
        
        # Match exact
        if candidat_lower == entreprise_lower:
            return 1.0
        
        # Match partiel (même ville/arrondissement)
        candidat_words = set(candidat_lower.split())
        entreprise_words = set(entreprise_lower.split())
        
        common_words = candidat_words.intersection(entreprise_words)
        if common_words:
            return 0.8
        
        # Cas spéciaux Paris
        if 'paris' in candidat_lower and 'paris' in entreprise_lower:
            return 0.7  # Même ville mais arrondissements différents
        
        return 0.3  # Villes différentes
    
    def _estimate_distance_score(self, loc_candidat: str, loc_entreprise: str, max_km: int) -> float:
        """Estimation score distance (sans Google Maps)"""
        if self._compare_cities(loc_candidat, loc_entreprise) >= 0.8:
            return 1.0  # Même zone
        
        # Heuristiques basiques
        if 'paris' in loc_candidat.lower() and 'paris' in loc_entreprise.lower():
            return 0.8  # Intra-Paris
        
        if max_km >= 50:
            return 0.7  # Candidat flexible
        elif max_km >= 30:
            return 0.5  # Moyennement flexible
        else:
            return 0.3  # Peu flexible
    
    def _calculate_remote_compatibility(self, candidat: BiDirectionalCandidateProfile,
                                      entreprise: BiDirectionalCompanyProfile) -> float:
        """Score compatibilité télétravail"""
        candidat_remote = candidat.attentes.remote_accepte
        entreprise_remote = entreprise.conditions.remote_possible
        
        if candidat_remote and entreprise_remote:
            return 1.0  # Parfait match
        elif not candidat_remote and not entreprise_remote:
            return 1.0  # Accord sur présentiel
        elif entreprise_remote and not candidat_remote:
            return 0.8  # Entreprise propose mais candidat préfère présentiel
        else:
            return 0.3  # Candidat veut remote mais entreprise ne propose pas

# === SUITE DANS LA PARTIE 2 DU FICHIER ===
