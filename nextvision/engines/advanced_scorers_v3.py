"""
Nextvision V3.0 - Scorers Avancés
=================================

Scorers spécialisés pour les nouveaux composants V3.0:
- SectorCompatibilityScorer (6% poids)
- TimingCompatibilityScorer (4% poids)  
- WorkModalityScorer (4% poids)

Finalisation prompt 4 - Nextvision V3.0 100% terminé.

Author: NEXTEN Development Team
Version: 3.0 - Final
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import datetime
from dateutil.parser import parse as parse_date
import re


class MatchQuality(Enum):
    """Qualité du matching pour les scorers"""
    PERFECT = "perfect"
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    INCOMPATIBLE = "incompatible"


@dataclass
class ScoringResult:
    """Résultat standardisé des scorers V3.0"""
    score: float  # 0.0 à 1.0
    quality: MatchQuality
    confidence: float  # 0.0 à 1.0
    details: Dict[str, Any]
    reason: str
    boost_factors: List[str] = None
    penalty_factors: List[str] = None


class SectorCompatibilityScorer:
    """🎯 Scorer compatibilité sectorielle V3.0 (6% poids)"""
    
    def __init__(self):
        # Secteurs avec proximité/transfert de compétences
        self.sector_proximity = {
            "fintech": ["banque", "assurance", "finance", "trading"],
            "edtech": ["education", "formation", "e-learning", "university"],
            "healthtech": ["sante", "medical", "pharmaceutical", "biotech"],
            "retailtech": ["retail", "e-commerce", "distribution", "luxury"],
            "proptech": ["immobilier", "construction", "architecture"],
            "mobility": ["transport", "automobile", "logistics", "delivery"],
            "energie": ["utilities", "renewable", "oil", "gas"],
            "telecom": ["media", "entertainment", "broadcasting"],
            "consulting": ["audit", "strategy", "transformation", "management"],
            "startup": ["innovation", "venture", "growth", "scale-up"]
        }
        
        # Secteurs avec barrières d'entrée élevées
        self.restricted_sectors = {
            "defense": ["military", "aerospace", "security"],
            "nuclear": ["energy", "nuclear", "radioactive"],
            "pharmaceutical": ["drug", "medical", "clinical", "fda"],
            "banking": ["finance", "regulatory", "compliance", "risk"]
        }
    
    def score_sector_compatibility(self, candidate_prefs: Dict[str, Any], 
                                 company_sector: str) -> ScoringResult:
        """
        Score la compatibilité sectorielle candidat/entreprise
        
        Args:
            candidate_prefs: {
                "preferred_sectors": ["fintech", "startup"],
                "avoided_sectors": ["defense", "tobacco"],
                "current_sector": "banking",
                "openness_to_change": 4,  # 1-5 scale
                "sector_experience": {"finance": 3, "tech": 2}  # années
            }
            company_sector: "fintech"
        """
        
        preferred = candidate_prefs.get("preferred_sectors", [])
        avoided = candidate_prefs.get("avoided_sectors", [])
        current_sector = candidate_prefs.get("current_sector", "")
        openness = candidate_prefs.get("openness_to_change", 3)
        experience = candidate_prefs.get("sector_experience", {})
        
        # 🚫 EXCLUSION TOTALE - Secteurs évités
        if self._is_sector_avoided(company_sector, avoided):
            return ScoringResult(
                score=0.0,
                quality=MatchQuality.INCOMPATIBLE,
                confidence=0.95,
                details={"reason": "sector_avoided", "avoided_sectors": avoided},
                reason=f"Secteur {company_sector} explicitement évité par candidat",
                penalty_factors=["sector_blacklist"]
            )
        
        # ✅ MATCH PARFAIT - Secteur préféré
        if self._is_sector_preferred(company_sector, preferred):
            bonus = self._calculate_experience_bonus(company_sector, experience)
            final_score = min(1.0, 0.95 + bonus)
            
            return ScoringResult(
                score=final_score,
                quality=MatchQuality.PERFECT,
                confidence=0.9,
                details={
                    "match_type": "preferred_sector",
                    "experience_bonus": bonus,
                    "sector_rank": preferred.index(company_sector) + 1 if company_sector in preferred else None
                },
                reason=f"Secteur {company_sector} dans préférences candidat",
                boost_factors=["preferred_sector", "experience_bonus"] if bonus > 0 else ["preferred_sector"]
            )
        
        # 🔄 SECTEUR ACTUEL - Bonus stabilité
        if self._is_same_sector(company_sector, current_sector):
            stability_bonus = 0.1 if openness <= 3 else 0.05  # Moins ouvert = valorise stabilité
            experience_bonus = self._calculate_experience_bonus(company_sector, experience)
            final_score = min(1.0, 0.85 + stability_bonus + experience_bonus)
            
            return ScoringResult(
                score=final_score,
                quality=MatchQuality.EXCELLENT,
                confidence=0.85,
                details={
                    "match_type": "current_sector",
                    "stability_bonus": stability_bonus,
                    "experience_bonus": experience_bonus
                },
                reason=f"Candidat déjà dans secteur {company_sector}",
                boost_factors=["sector_continuity", "experience_match"]
            )
        
        # 🔗 SECTEURS CONNEXES - Transfert compétences
        proximity_score = self._calculate_sector_proximity(current_sector, company_sector)
        if proximity_score > 0.5:
            # Candidat ouvert au changement valorisé
            openness_modifier = (openness - 3) * 0.1  # -0.2 à +0.2
            final_score = min(1.0, proximity_score + openness_modifier)
            
            return ScoringResult(
                score=final_score,
                quality=MatchQuality.GOOD if final_score > 0.7 else MatchQuality.ACCEPTABLE,
                confidence=0.7,
                details={
                    "match_type": "sector_proximity",
                    "proximity_score": proximity_score,
                    "openness_modifier": openness_modifier,
                    "transferable_skills": True
                },
                reason=f"Secteurs {current_sector} → {company_sector} connexes",
                boost_factors=["sector_proximity"] if openness > 3 else []
            )
        
        # 🆕 NOUVEAU SECTEUR - Dépend ouverture candidat
        if openness >= 4:  # Candidat ouvert
            base_score = 0.6 + (openness - 3) * 0.1
            entry_barrier = self._calculate_entry_barrier(company_sector)
            final_score = max(0.2, base_score - entry_barrier)
            
            return ScoringResult(
                score=final_score,
                quality=MatchQuality.ACCEPTABLE if final_score > 0.5 else MatchQuality.POOR,
                confidence=0.5,
                details={
                    "match_type": "sector_transition",
                    "candidate_openness": openness,
                    "entry_barrier": entry_barrier
                },
                reason=f"Candidat ouvert à transition vers {company_sector}",
                boost_factors=["high_openness"] if openness == 5 else []
            )
        
        else:  # Candidat fermé au changement
            return ScoringResult(
                score=0.3,
                quality=MatchQuality.POOR,
                confidence=0.6,
                details={
                    "match_type": "difficult_transition",
                    "candidate_openness": openness,
                    "risk_level": "high"
                },
                reason=f"Candidat peu ouvert transition {current_sector} → {company_sector}",
                penalty_factors=["low_openness", "sector_mismatch"]
            )
    
    def _is_sector_avoided(self, company_sector: str, avoided_sectors: List[str]) -> bool:
        """Vérifie si secteur entreprise est évité par candidat"""
        company_lower = company_sector.lower()
        for avoided in avoided_sectors:
            if avoided.lower() in company_lower or company_lower in avoided.lower():
                return True
        return False
    
    def _is_sector_preferred(self, company_sector: str, preferred_sectors: List[str]) -> bool:
        """Vérifie si secteur entreprise est préféré par candidat"""
        company_lower = company_sector.lower()
        for preferred in preferred_sectors:
            if preferred.lower() in company_lower or company_lower in preferred.lower():
                return True
        return False
    
    def _is_same_sector(self, company_sector: str, current_sector: str) -> bool:
        """Vérifie si même secteur (avec variations nom)"""
        if not current_sector:
            return False
        return company_sector.lower() in current_sector.lower() or current_sector.lower() in company_sector.lower()
    
    def _calculate_sector_proximity(self, current_sector: str, target_sector: str) -> float:
        """Calcule proximité entre secteurs (0.0 à 1.0)"""
        if not current_sector:
            return 0.0
        
        current_lower = current_sector.lower()
        target_lower = target_sector.lower()
        
        # Recherche dans mapping proximité
        for main_sector, related_sectors in self.sector_proximity.items():
            if main_sector in target_lower:
                for related in related_sectors:
                    if related in current_lower:
                        return 0.8  # Forte proximité
            
            if main_sector in current_lower:
                for related in related_sectors:
                    if related in target_lower:
                        return 0.8
        
        # Proximité par mots-clés communs
        current_words = set(current_lower.split())
        target_words = set(target_lower.split())
        common_words = current_words.intersection(target_words)
        
        if common_words:
            return min(0.7, len(common_words) * 0.2)
        
        return 0.0
    
    def _calculate_entry_barrier(self, sector: str) -> float:
        """Calcule barrière d'entrée secteur (0.0 à 0.5)"""
        sector_lower = sector.lower()
        
        # Secteurs avec barrières élevées
        for restricted, keywords in self.restricted_sectors.items():
            for keyword in keywords:
                if keyword in sector_lower:
                    return 0.4  # Barrière élevée
        
        # Tech/Digital : barrières moyennes
        if any(word in sector_lower for word in ["tech", "digital", "software", "it"]):
            return 0.1
        
        # Services : barrières faibles
        if any(word in sector_lower for word in ["consulting", "service", "conseil"]):
            return 0.05
        
        return 0.2  # Barrière moyenne par défaut
    
    def _calculate_experience_bonus(self, sector: str, experience: Dict[str, int]) -> float:
        """Calcule bonus expérience secteur (0.0 à 0.1)"""
        sector_lower = sector.lower()
        
        for exp_sector, years in experience.items():
            if exp_sector.lower() in sector_lower or sector_lower in exp_sector.lower():
                return min(0.1, years * 0.02)  # +2% par année, max 10%
        
        return 0.0


class TimingCompatibilityScorer:
    """⏰ Scorer compatibilité timing V3.0 (4% poids)"""
    
    def score_timing_compatibility(self, candidate_timing: Dict[str, Any], 
                                 company_timing: Dict[str, Any]) -> ScoringResult:
        """
        Score la compatibilité des timings candidat/entreprise
        
        Args:
            candidate_timing: {
                "availability_date": "2025-08-15",
                "notice_period_weeks": 8,
                "flexibility_weeks": 2,
                "urgency_level": 3  # 1-5 scale
            }
            company_timing: {
                "desired_start_date": "2025-08-01", 
                "recruitment_urgency": 4,  # 1-5 scale
                "max_wait_weeks": 6,
                "project_deadline": "2025-12-01"
            }
        """
        
        try:
            # Parsing dates
            candidate_available = self._parse_date(candidate_timing.get("availability_date"))
            company_desired = self._parse_date(company_timing.get("desired_start_date"))
            project_deadline = self._parse_date(company_timing.get("project_deadline"))
            
            if not candidate_available or not company_desired:
                return self._default_timing_score("missing_dates")
            
            # Calcul gap temporel
            gap_days = (candidate_available - company_desired).days
            gap_weeks = gap_days / 7
            
            notice_weeks = candidate_timing.get("notice_period_weeks", 0)
            flexibility_weeks = candidate_timing.get("flexibility_weeks", 0)
            max_wait_weeks = company_timing.get("max_wait_weeks", 4)
            
            candidate_urgency = candidate_timing.get("urgency_level", 3)
            company_urgency = company_timing.get("recruitment_urgency", 3)
            
            # 🎯 TIMING PARFAIT - Disponibilité immédiate/flexible
            if abs(gap_days) <= 7:  # Moins d'une semaine d'écart
                urgency_bonus = self._calculate_urgency_bonus(candidate_urgency, company_urgency)
                final_score = min(1.0, 0.95 + urgency_bonus)
                
                return ScoringResult(
                    score=final_score,
                    quality=MatchQuality.PERFECT,
                    confidence=0.9,
                    details={
                        "gap_days": gap_days,
                        "match_type": "perfect_timing",
                        "urgency_bonus": urgency_bonus
                    },
                    reason="Timing candidat/entreprise parfaitement aligné",
                    boost_factors=["perfect_timing"] + (["urgency_match"] if urgency_bonus > 0 else [])
                )
            
            # ✅ TIMING EXCELLENT - Dans flexibilité
            total_flexibility = flexibility_weeks + max_wait_weeks
            if abs(gap_weeks) <= total_flexibility:
                flexibility_score = 1.0 - (abs(gap_weeks) / total_flexibility) * 0.3
                urgency_modifier = self._calculate_urgency_modifier(candidate_urgency, company_urgency)
                final_score = min(1.0, flexibility_score + urgency_modifier)
                
                return ScoringResult(
                    score=final_score,
                    quality=MatchQuality.EXCELLENT if final_score > 0.8 else MatchQuality.GOOD,
                    confidence=0.8,
                    details={
                        "gap_weeks": gap_weeks,
                        "total_flexibility": total_flexibility,
                        "flexibility_score": flexibility_score,
                        "urgency_modifier": urgency_modifier
                    },
                    reason=f"Timing compatible avec {gap_weeks:.1f} semaines d'écart",
                    boost_factors=["within_flexibility"] if urgency_modifier > 0 else []
                )
            
            # 🔄 PRÉAVIS À NÉGOCIER - Candidat en poste
            if notice_weeks > 0 and gap_weeks > max_wait_weeks:
                notice_penalty = min(0.4, (gap_weeks - max_wait_weeks) * 0.05)
                deadline_pressure = self._calculate_deadline_pressure(candidate_available, project_deadline)
                final_score = max(0.2, 0.7 - notice_penalty - deadline_pressure)
                
                penalty_factors = ["long_notice_period"]
                if deadline_pressure > 0.1:
                    penalty_factors.append("deadline_pressure")
                
                return ScoringResult(
                    score=final_score,
                    quality=MatchQuality.ACCEPTABLE if final_score > 0.5 else MatchQuality.POOR,
                    confidence=0.6,
                    details={
                        "gap_weeks": gap_weeks,
                        "notice_weeks": notice_weeks,
                        "notice_penalty": notice_penalty,
                        "deadline_pressure": deadline_pressure,
                        "negotiation_required": True
                    },
                    reason=f"Préavis {notice_weeks} semaines nécessite négociation",
                    penalty_factors=penalty_factors
                )
            
            # ⚠️ TIMING DIFFICILE - Écart important
            if gap_weeks > max_wait_weeks * 2:
                return ScoringResult(
                    score=0.3,
                    quality=MatchQuality.POOR,
                    confidence=0.7,
                    details={
                        "gap_weeks": gap_weeks,
                        "max_wait_weeks": max_wait_weeks,
                        "feasibility": "low"
                    },
                    reason=f"Écart timing trop important: {gap_weeks:.1f} semaines",
                    penalty_factors=["major_timing_gap", "low_feasibility"]
                )
            
            # 🤝 TIMING NÉGOCIABLE - Avec effort
            negotiation_score = max(0.4, 0.8 - abs(gap_weeks) * 0.1)
            urgency_factor = (candidate_urgency + company_urgency) / 10  # 0.2 à 1.0
            final_score = min(0.8, negotiation_score + urgency_factor * 0.1)
            
            return ScoringResult(
                score=final_score,
                quality=MatchQuality.ACCEPTABLE,
                confidence=0.5,
                details={
                    "gap_weeks": gap_weeks,
                    "negotiation_score": negotiation_score,
                    "urgency_factor": urgency_factor,
                    "requires_negotiation": True
                },
                reason=f"Timing négociable avec effort mutuel",
                boost_factors=["high_mutual_urgency"] if urgency_factor > 0.8 else []
            )
        
        except Exception as e:
            return self._default_timing_score(f"error: {str(e)}")
    
    def _parse_date(self, date_str: str) -> Optional[datetime.datetime]:
        """Parse date string en datetime"""
        if not date_str:
            return None
        try:
            return parse_date(date_str)
        except:
            return None
    
    def _calculate_urgency_bonus(self, candidate_urgency: int, company_urgency: int) -> float:
        """Calcule bonus si urgences alignées (0.0 à 0.1)"""
        if candidate_urgency >= 4 and company_urgency >= 4:
            return 0.1  # Bonus maximal si tous deux urgents
        elif abs(candidate_urgency - company_urgency) <= 1:
            return 0.05  # Bonus modéré si urgences proches
        return 0.0
    
    def _calculate_urgency_modifier(self, candidate_urgency: int, company_urgency: int) -> float:
        """Calcule modificateur urgence (-0.1 à +0.1)"""
        urgency_gap = abs(candidate_urgency - company_urgency)
        if urgency_gap == 0:
            return 0.1  # Bonus parfait alignement
        elif urgency_gap == 1:
            return 0.05  # Bonus léger
        elif urgency_gap >= 3:
            return -0.1  # Pénalité écart important
        return 0.0
    
    def _calculate_deadline_pressure(self, start_date: datetime.datetime, 
                                   deadline_date: Optional[datetime.datetime]) -> float:
        """Calcule pression deadline projet (0.0 à 0.3)"""
        if not deadline_date:
            return 0.0
        
        project_duration_weeks = (deadline_date - start_date).days / 7
        
        if project_duration_weeks < 8:  # Moins de 2 mois
            return 0.3  # Pression maximale
        elif project_duration_weeks < 16:  # Moins de 4 mois
            return 0.2  # Pression élevée
        elif project_duration_weeks < 24:  # Moins de 6 mois
            return 0.1  # Pression modérée
        
        return 0.0  # Pas de pression
    
    def _default_timing_score(self, reason: str) -> ScoringResult:
        """Score par défaut en cas d'erreur/données manquantes"""
        return ScoringResult(
            score=0.5,
            quality=MatchQuality.ACCEPTABLE,
            confidence=0.3,
            details={"reason": reason, "default_score": True},
            reason=f"Score timing par défaut: {reason}",
            penalty_factors=["missing_data"]
        )


class WorkModalityScorer:
    """🏠 Scorer modalités de travail V3.0 (4% poids)"""
    
    def __init__(self):
        # Mapping compatibilité modalités (candidat → entreprise)
        self.modality_compatibility = {
            "full_remote": {
                "full_remote": 1.0,
                "hybrid": 0.7,      # Acceptable mais pas optimal
                "on_site": 0.1      # Très difficile
            },
            "hybrid": {
                "full_remote": 0.9,  # Bonus flexibilité
                "hybrid": 1.0,
                "on_site": 0.6      # Acceptable si proche
            },
            "on_site": {
                "full_remote": 0.3,  # Difficile transition
                "hybrid": 0.8,       # Bon compromis
                "on_site": 1.0
            },
            "flexible": {  # Candidat adaptable
                "full_remote": 0.9,
                "hybrid": 0.95,
                "on_site": 0.85
            }
        }
    
    def score_work_modality(self, candidate_prefs: Dict[str, Any], 
                          company_policy: Dict[str, Any]) -> ScoringResult:
        """
        Score compatibilité modalités travail candidat/entreprise
        
        Args:
            candidate_prefs: {
                "preferred_modality": "hybrid",
                "remote_days_per_week": 3,
                "max_commute_minutes": 45,
                "flexibility_level": 4,  # 1-5 scale
                "home_office_setup": True,
                "motivations": ["work_life_balance", "productivity"]
            }
            company_policy: {
                "work_modality": "hybrid",
                "remote_days_allowed": 2,
                "office_days_required": 3,
                "commute_distance_km": 25,
                "flexibility_level": 3,
                "team_collaboration_requirements": ["meetings", "workshops"]
            }
        """
        
        candidate_modality = candidate_prefs.get("preferred_modality", "hybrid")
        company_modality = company_policy.get("work_modality", "hybrid")
        
        # Score base compatibilité modalités
        base_score = self.modality_compatibility.get(candidate_modality, {}).get(company_modality, 0.5)
        
        # ✅ MATCH PARFAIT - Modalités identiques
        if candidate_modality == company_modality:
            return self._score_perfect_modality_match(candidate_prefs, company_policy, base_score)
        
        # 🔄 HYBRID COMPATIBILITY - Détail jours remote/présentiel
        elif candidate_modality == "hybrid" or company_modality == "hybrid":
            return self._score_hybrid_compatibility(candidate_prefs, company_policy, base_score)
        
        # 🏠 REMOTE vs ON_SITE - Vérification faisabilité
        elif (candidate_modality == "full_remote" and company_modality == "on_site") or \
             (candidate_modality == "on_site" and company_modality == "full_remote"):
            return self._score_extreme_modality_gap(candidate_prefs, company_policy, base_score)
        
        # 🤝 AUTRES CAS - Évaluation standard
        else:
            return self._score_standard_modality(candidate_prefs, company_policy, base_score)
    
    def _score_perfect_modality_match(self, candidate_prefs: Dict, company_policy: Dict, base_score: float) -> ScoringResult:
        """Score modalités identiques avec détails"""
        
        modality = candidate_prefs.get("preferred_modality")
        
        # Bonus pour setup/équipement compatible
        setup_bonus = 0.0
        boost_factors = ["perfect_modality_match"]
        
        if modality == "full_remote":
            if candidate_prefs.get("home_office_setup", False):
                setup_bonus += 0.05
                boost_factors.append("home_office_ready")
        
        elif modality == "hybrid":
            candidate_remote_days = candidate_prefs.get("remote_days_per_week", 2)
            company_remote_days = company_policy.get("remote_days_allowed", 2)
            
            if candidate_remote_days <= company_remote_days:
                setup_bonus += 0.05
                boost_factors.append("remote_days_aligned")
        
        # Bonus motivations alignées
        motivations = candidate_prefs.get("motivations", [])
        if "work_life_balance" in motivations and modality in ["full_remote", "hybrid"]:
            setup_bonus += 0.03
            boost_factors.append("work_life_balance")
        
        final_score = min(1.0, base_score + setup_bonus)
        
        return ScoringResult(
            score=final_score,
            quality=MatchQuality.PERFECT,
            confidence=0.9,
            details={
                "modality": modality,
                "setup_bonus": setup_bonus,
                "perfect_match": True
            },
            reason=f"Modalité {modality} parfaitement alignée",
            boost_factors=boost_factors
        )
    
    def _score_hybrid_compatibility(self, candidate_prefs: Dict, company_policy: Dict, base_score: float) -> ScoringResult:
        """Score compatibilité détaillée mode hybrid"""
        
        candidate_remote_days = candidate_prefs.get("remote_days_per_week", 2)
        company_remote_days = company_policy.get("remote_days_allowed", 2)
        candidate_commute_max = candidate_prefs.get("max_commute_minutes", 45)
        company_commute_km = company_policy.get("commute_distance_km", 20)
        
        # Estimation temps trajet (35km/h moyenne urbaine)
        company_commute_minutes = company_commute_km * 1.7  # Approximation
        
        # Score jours remote/présentiel
        remote_days_gap = abs(candidate_remote_days - company_remote_days)
        remote_score = max(0.5, 1.0 - remote_days_gap * 0.2)
        
        # Score trajet domicile-bureau
        commute_score = 1.0
        commute_penalty = 0.0
        
        if company_commute_minutes > candidate_commute_max:
            commute_penalty = min(0.4, (company_commute_minutes - candidate_commute_max) / candidate_commute_max * 0.5)
            commute_score = max(0.3, 1.0 - commute_penalty)
        
        # Score final pondéré
        final_score = min(1.0, base_score * 0.6 + remote_score * 0.25 + commute_score * 0.15)
        
        # Qualité selon score
        if final_score >= 0.8:
            quality = MatchQuality.EXCELLENT
        elif final_score >= 0.6:
            quality = MatchQuality.GOOD
        else:
            quality = MatchQuality.ACCEPTABLE
        
        penalty_factors = []
        if remote_days_gap > 1:
            penalty_factors.append("remote_days_mismatch")
        if commute_penalty > 0.2:
            penalty_factors.append("long_commute")
        
        return ScoringResult(
            score=final_score,
            quality=quality,
            confidence=0.8,
            details={
                "candidate_remote_days": candidate_remote_days,
                "company_remote_days": company_remote_days,
                "remote_days_gap": remote_days_gap,
                "commute_minutes": company_commute_minutes,
                "commute_penalty": commute_penalty,
                "remote_score": remote_score,
                "commute_score": commute_score
            },
            reason=f"Compatibilité hybrid: {candidate_remote_days}j remote vs {company_remote_days}j autorisés",
            penalty_factors=penalty_factors if penalty_factors else None
        )
    
    def _score_extreme_modality_gap(self, candidate_prefs: Dict, company_policy: Dict, base_score: float) -> ScoringResult:
        """Score écart extrême modalités (remote vs on_site)"""
        
        candidate_modality = candidate_prefs.get("preferred_modality")
        company_modality = company_policy.get("work_modality")
        candidate_flexibility = candidate_prefs.get("flexibility_level", 3)
        
        # Facteurs d'ajustement
        flexibility_modifier = (candidate_flexibility - 3) * 0.1  # -0.2 à +0.2
        
        # Cas spéciaux qui peuvent sauver le match
        rescue_factors = []
        rescue_bonus = 0.0
        
        if candidate_modality == "full_remote" and company_modality == "on_site":
            # Candidat remote peut accepter on_site si très motivé
            motivations = candidate_prefs.get("motivations", [])
            if "team_collaboration" in motivations:
                rescue_bonus += 0.2
                rescue_factors.append("values_collaboration")
            
            if candidate_flexibility >= 4:
                rescue_bonus += 0.1
                rescue_factors.append("high_flexibility")
        
        elif candidate_modality == "on_site" and company_modality == "full_remote":
            # Candidat présentiel peut s'adapter au remote
            if candidate_prefs.get("home_office_setup", False):
                rescue_bonus += 0.2
                rescue_factors.append("remote_ready")
            
            if "autonomy" in candidate_prefs.get("motivations", []):
                rescue_bonus += 0.1
                rescue_factors.append("autonomy_motivated")
        
        final_score = max(0.1, min(0.8, base_score + flexibility_modifier + rescue_bonus))
        
        if final_score >= 0.5:
            quality = MatchQuality.ACCEPTABLE
            reason = f"Écart modalité importante mais faisable avec adaptation"
        else:
            quality = MatchQuality.POOR
            reason = f"Écart modalité {candidate_modality} vs {company_modality} très difficile"
        
        return ScoringResult(
            score=final_score,
            quality=quality,
            confidence=0.6,
            details={
                "candidate_modality": candidate_modality,
                "company_modality": company_modality,
                "flexibility_modifier": flexibility_modifier,
                "rescue_bonus": rescue_bonus,
                "rescue_factors": rescue_factors
            },
            reason=reason,
            boost_factors=rescue_factors if rescue_factors else None,
            penalty_factors=["major_modality_gap"]
        )
    
    def _score_standard_modality(self, candidate_prefs: Dict, company_policy: Dict, base_score: float) -> ScoringResult:
        """Score standard autres cas modalités"""
        
        candidate_flexibility = candidate_prefs.get("flexibility_level", 3)
        company_flexibility = company_policy.get("flexibility_level", 3)
        
        # Bonus flexibilité mutuelle
        flexibility_bonus = 0.0
        if candidate_flexibility >= 4 and company_flexibility >= 4:
            flexibility_bonus = 0.1
        elif candidate_flexibility >= 4 or company_flexibility >= 4:
            flexibility_bonus = 0.05
        
        final_score = min(1.0, base_score + flexibility_bonus)
        
        # Détermination qualité
        if final_score >= 0.8:
            quality = MatchQuality.EXCELLENT
        elif final_score >= 0.6:
            quality = MatchQuality.GOOD
        elif final_score >= 0.4:
            quality = MatchQuality.ACCEPTABLE
        else:
            quality = MatchQuality.POOR
        
        return ScoringResult(
            score=final_score,
            quality=quality,
            confidence=0.7,
            details={
                "base_score": base_score,
                "flexibility_bonus": flexibility_bonus,
                "candidate_flexibility": candidate_flexibility,
                "company_flexibility": company_flexibility
            },
            reason="Modalités compatibles avec ajustements",
            boost_factors=["mutual_flexibility"] if flexibility_bonus > 0 else None
        )


# ================================
# UTILITAIRES ET TESTS
# ================================

def test_all_scorers():
    """Test rapide des 3 scorers V3.0"""
    
    print("🧪 TEST SCORERS V3.0 - Finalisation Nextvision")
    print("=" * 50)
    
    # Test SectorCompatibilityScorer
    print("\n1️⃣ TEST SECTOR COMPATIBILITY")
    sector_scorer = SectorCompatibilityScorer()
    
    candidate_sector = {
        "preferred_sectors": ["fintech", "startup"],
        "avoided_sectors": ["defense"],
        "current_sector": "banking",
        "openness_to_change": 4,
        "sector_experience": {"finance": 3}
    }
    
    result = sector_scorer.score_sector_compatibility(candidate_sector, "fintech")
    print(f"Score fintech: {result.score:.2f} | Quality: {result.quality.value}")
    print(f"Reason: {result.reason}")
    
    # Test TimingCompatibilityScorer
    print("\n2️⃣ TEST TIMING COMPATIBILITY")
    timing_scorer = TimingCompatibilityScorer()
    
    candidate_timing = {
        "availability_date": "2025-08-15",
        "notice_period_weeks": 6,
        "flexibility_weeks": 2,
        "urgency_level": 4
    }
    
    company_timing = {
        "desired_start_date": "2025-08-01",
        "recruitment_urgency": 4,
        "max_wait_weeks": 8
    }
    
    result = timing_scorer.score_timing_compatibility(candidate_timing, company_timing)
    print(f"Score timing: {result.score:.2f} | Quality: {result.quality.value}")
    print(f"Reason: {result.reason}")
    
    # Test WorkModalityScorer
    print("\n3️⃣ TEST WORK MODALITY")
    modality_scorer = WorkModalityScorer()
    
    candidate_modality = {
        "preferred_modality": "hybrid",
        "remote_days_per_week": 3,
        "max_commute_minutes": 45,
        "flexibility_level": 4,
        "motivations": ["work_life_balance"]
    }
    
    company_modality = {
        "work_modality": "hybrid",
        "remote_days_allowed": 2,
        "commute_distance_km": 20,
        "flexibility_level": 3
    }
    
    result = modality_scorer.score_work_modality(candidate_modality, company_modality)
    print(f"Score modality: {result.score:.2f} | Quality: {result.quality.value}")
    print(f"Reason: {result.reason}")
    
    print("\n✅ TESTS SCORERS V3.0 TERMINÉS")
    print("🎯 NEXTVISION V3.0 - 3/4 SCORERS CRÉÉS")


if __name__ == "__main__":
    test_all_scorers()
