"""
🎯 Nextvision V3.0 - SectorCompatibilityScorer (6% Weight)
=========================================================

Score la compatibilité secteur candidat vs entreprise avec logique métier intelligente
- Analyse secteurs préférés/rédhibitoires depuis motivations_ranking
- Cartographie secteurs connexes et transitions naturelles
- Gestion ouverture changement carrière et priorisation secteur vs poste
- Bonus/malus selon taille entreprise et stade de croissance
- Performance optimisée <11ms (6% du budget 175ms)

Author: NEXTEN Team
Version: 3.0.0 - Sector Intelligence
"""

import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum

from nextvision.models.extended_bidirectional_models_v3 import (
    ExtendedCandidateProfileV3,
    ExtendedCompanyProfileV3,
    CompanySize
)

logger = logging.getLogger(__name__)

class SectorCompatibilityLevel(str, Enum):
    """Niveaux de compatibilité secteur"""
    PERFECT = "perfect"
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    INCOMPATIBLE = "incompatible"

class SectorCompatibilityScorer:
    """
    🎯 Sector Compatibility Scorer V3.0 - Intelligence Sectorielle
    
    Évalue la compatibilité secteur avec logique métier avancée :
    - Score 1.0 : Secteur entreprise dans secteurs préférés
    - Score 0.0 : Secteur entreprise dans secteurs rédhibitoires  
    - Score modulé : Secteurs connexes selon cartographie intelligente
    - Bonus/malus : Taille entreprise, croissance, ouverture changement
    - Performance <11ms avec cache optimisé
    """
    
    def __init__(self):
        self.name = "SectorCompatibilityScorer"
        self.version = "3.0.0"
        
        # Cartographie secteurs connexes (optimisée performance)
        self.sector_connections = {
            # Technologie & Digital
            "technologie": {
                "direct_connections": ["informatique", "digital", "tech", "numérique", "software"],
                "natural_transitions": ["fintech", "edtech", "healthtech", "e-commerce"],
                "distant_connections": ["conseil", "finance", "télécommunications"],
                "connection_strength": 0.9
            },
            "informatique": {
                "direct_connections": ["technologie", "digital", "software", "tech"],
                "natural_transitions": ["cybersécurité", "intelligence artificielle", "data"],
                "distant_connections": ["finance", "industrie", "conseil"],
                "connection_strength": 0.9
            },
            "fintech": {
                "direct_connections": ["finance", "technologie", "banque"],
                "natural_transitions": ["assurance", "investissement", "crypto"],
                "distant_connections": ["immobilier", "conseil"],
                "connection_strength": 0.8
            },
            
            # Finance & Services
            "finance": {
                "direct_connections": ["banque", "assurance", "investissement"],
                "natural_transitions": ["fintech", "immobilier", "conseil"],
                "distant_connections": ["technologie", "audit"],
                "connection_strength": 0.8
            },
            "banque": {
                "direct_connections": ["finance", "assurance", "investissement"],
                "natural_transitions": ["fintech", "immobilier", "crédit"],
                "distant_connections": ["conseil", "audit"],
                "connection_strength": 0.8
            },
            "assurance": {
                "direct_connections": ["finance", "banque", "mutuelle"],
                "natural_transitions": ["insurtech", "santé", "immobilier"],
                "distant_connections": ["conseil", "audit"],
                "connection_strength": 0.7
            },
            
            # Conseil & Services aux entreprises
            "conseil": {
                "direct_connections": ["consulting", "audit", "services"],
                "natural_transitions": ["finance", "technologie", "management"],
                "distant_connections": ["industrie", "santé", "immobilier"],
                "connection_strength": 0.7
            },
            "audit": {
                "direct_connections": ["conseil", "finance", "comptabilité"],
                "natural_transitions": ["compliance", "risk", "consulting"],
                "distant_connections": ["banque", "assurance"],
                "connection_strength": 0.7
            },
            
            # Santé & Bien-être
            "santé": {
                "direct_connections": ["médical", "pharmaceutique", "biotechnologie"],
                "natural_transitions": ["healthtech", "assurance", "recherche"],
                "distant_connections": ["technologie", "conseil"],
                "connection_strength": 0.6
            },
            "pharmaceutique": {
                "direct_connections": ["santé", "biotechnologie", "recherche"],
                "natural_transitions": ["médical", "chimie", "healthtech"],
                "distant_connections": ["technologie", "industrie"],
                "connection_strength": 0.6
            },
            
            # Industrie & Manufacturing
            "industrie": {
                "direct_connections": ["manufacturing", "automobile", "énergie"],
                "natural_transitions": ["technologie", "logistique", "innovation"],
                "distant_connections": ["conseil", "finance"],
                "connection_strength": 0.6
            },
            "automobile": {
                "direct_connections": ["industrie", "manufacturing", "transport"],
                "natural_transitions": ["technologie", "électrique", "mobilité"],
                "distant_connections": ["énergie", "assurance"],
                "connection_strength": 0.6
            },
            
            # Commerce & Distribution
            "e-commerce": {
                "direct_connections": ["commerce", "retail", "digital"],
                "natural_transitions": ["technologie", "marketing", "logistique"],
                "distant_connections": ["finance", "media"],
                "connection_strength": 0.7
            },
            "retail": {
                "direct_connections": ["commerce", "distribution", "vente"],
                "natural_transitions": ["e-commerce", "marketing", "digital"],
                "distant_connections": ["finance", "immobilier"],
                "connection_strength": 0.6
            },
            
            # Média & Communication
            "media": {
                "direct_connections": ["communication", "marketing", "digital"],
                "natural_transitions": ["technologie", "e-commerce", "publicité"],
                "distant_connections": ["conseil", "finance"],
                "connection_strength": 0.6
            },
            "marketing": {
                "direct_connections": ["communication", "publicité", "digital"],
                "natural_transitions": ["e-commerce", "media", "technologie"],
                "distant_connections": ["conseil", "retail"],
                "connection_strength": 0.6
            },
            
            # Secteurs publics & Sociaux
            "public": {
                "direct_connections": ["administration", "gouvernement", "collectivités"],
                "natural_transitions": ["éducation", "santé", "social"],
                "distant_connections": ["conseil", "technologie"],
                "connection_strength": 0.5
            },
            "éducation": {
                "direct_connections": ["formation", "université", "recherche"],
                "natural_transitions": ["edtech", "public", "conseil"],
                "distant_connections": ["technologie", "santé"],
                "connection_strength": 0.5
            }
        }
        
        # Normalisation secteurs (aliases)
        self.sector_aliases = {
            "tech": "technologie",
            "it": "informatique",
            "digital": "technologie",
            "numérique": "technologie",
            "software": "informatique",
            "banking": "banque",
            "insurance": "assurance",
            "consulting": "conseil",
            "healthcare": "santé",
            "pharma": "pharmaceutique",
            "automotive": "automobile",
            "manufacturing": "industrie",
            "ecommerce": "e-commerce",
            "online": "e-commerce",
            "advertising": "marketing",
            "gouvernement": "public",
            "administration": "public",
            "education": "éducation",
            "training": "formation"
        }
        
        # Bonus/malus selon taille entreprise
        self.size_modifiers = {
            CompanySize.STARTUP: {
                "risk_tolerance_bonus": 0.1,
                "innovation_bonus": 0.15,
                "stability_malus": -0.05,
                "description": "Startup - Innovation & flexibilité"
            },
            CompanySize.PME: {
                "growth_bonus": 0.05,
                "proximity_bonus": 0.1,
                "stability_malus": 0.0,
                "description": "PME - Équilibre croissance/stabilité"
            },
            CompanySize.ETI: {
                "stability_bonus": 0.1,
                "structure_bonus": 0.05,
                "innovation_malus": -0.05,
                "description": "ETI - Stabilité & structure"
            },
            CompanySize.GRAND_GROUPE: {
                "stability_bonus": 0.15,
                "resources_bonus": 0.1,
                "flexibility_malus": -0.1,
                "description": "Grand groupe - Ressources & stabilité"
            },
            CompanySize.ADMINISTRATION: {
                "stability_bonus": 0.2,
                "security_bonus": 0.1,
                "innovation_malus": -0.15,
                "description": "Administration - Sécurité & stabilité"
            }
        }
        
        # Cache pour performance
        self._sector_analysis_cache = {}
        
        # Métriques
        self.stats = {
            "calculations": 0,
            "cache_hits": 0,
            "average_processing_time": 0.0,
            "compatibility_distribution": {level.value: 0 for level in SectorCompatibilityLevel}
        }
    
    def calculate_sector_compatibility_score(
        self,
        candidate: ExtendedCandidateProfileV3,
        company: ExtendedCompanyProfileV3,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        🎯 Calcule score compatibilité secteur avec logique métier intelligente
        
        Target: <11ms (6% du budget 175ms)
        """
        start_time = datetime.now()
        self.stats["calculations"] += 1
        
        try:
            # 1. Extraction rapide données secteur
            sector_data = self._extract_sector_data(candidate, company)
            
            if not sector_data["company_sector"]:
                return self._create_fallback_score("Secteur entreprise non défini")
            
            # 2. Analyse compatibilité secteur (avec cache)
            compatibility_analysis = self._analyze_sector_compatibility(sector_data)
            
            # 3. Calcul score de base
            base_score = self._calculate_base_sector_score(compatibility_analysis)
            
            # 4. Application modifiers (taille, croissance, ouverture)
            adjusted_score = self._apply_sector_modifiers(
                base_score, compatibility_analysis, sector_data
            )
            
            # 5. Enrichissement résultat
            result = self._enrich_sector_result(
                adjusted_score, compatibility_analysis, sector_data, context
            )
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            result["processing_time_ms"] = processing_time
            
            # Mise à jour stats
            self._update_stats(processing_time, compatibility_analysis["compatibility_level"])
            
            logger.info(
                f"🎯 SectorCompatibilityScorer: {adjusted_score:.3f} "
                f"({compatibility_analysis['compatibility_level']}, {processing_time:.1f}ms)"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur SectorCompatibilityScorer: {e}")
            return self._create_fallback_score(f"Erreur: {str(e)}")
    
    def _extract_sector_data(
        self,
        candidate: ExtendedCandidateProfileV3,
        company: ExtendedCompanyProfileV3
    ) -> Dict[str, Any]:
        """📊 Extraction données secteur candidat/entreprise"""
        
        # Secteurs candidat
        preferred_sectors = candidate.motivations_ranking.secteurs_preferes or []
        prohibited_sectors = candidate.motivations_ranking.secteurs_redhibitoires or []
        
        # Normalisation secteurs candidat
        normalized_preferred = [self._normalize_sector(s) for s in preferred_sectors]
        normalized_prohibited = [self._normalize_sector(s) for s in prohibited_sectors]
        
        # Secteur entreprise (V3.0 prioritaire, fallback V2.0)
        company_sector = company.company_profile_v3.company_sector
        if not company_sector:
            company_sector = company.base_profile.entreprise.secteur or ""
        
        company_sector = self._normalize_sector(company_sector)
        
        # Métadonnées candidat
        career_change_openness = candidate.motivations_ranking.career_change_openness
        sector_priority_vs_role = candidate.motivations_ranking.sector_priority_vs_role
        
        # Métadonnées entreprise
        company_size = company.company_profile_v3.company_size
        growth_stage = company.company_profile_v3.growth_stage
        
        return {
            "preferred_sectors": normalized_preferred,
            "prohibited_sectors": normalized_prohibited,
            "company_sector": company_sector,
            "career_change_openness": career_change_openness,
            "sector_priority_vs_role": sector_priority_vs_role,
            "company_size": company_size,
            "growth_stage": growth_stage,
            "raw_preferred": preferred_sectors,
            "raw_prohibited": prohibited_sectors
        }
    
    def _normalize_sector(self, sector: str) -> str:
        """🔄 Normalisation secteur avec aliases"""
        
        if not sector:
            return ""
        
        sector_lower = sector.lower().strip()
        
        # Vérification aliases
        if sector_lower in self.sector_aliases:
            return self.sector_aliases[sector_lower]
        
        # Recherche partielle dans aliases
        for alias, normalized in self.sector_aliases.items():
            if alias in sector_lower or sector_lower in alias:
                return normalized
        
        return sector_lower
    
    def _analyze_sector_compatibility(self, sector_data: Dict[str, Any]) -> Dict[str, Any]:
        """🔍 Analyse compatibilité secteur (avec cache)"""
        
        company_sector = sector_data["company_sector"]
        preferred_sectors = sector_data["preferred_sectors"]
        prohibited_sectors = sector_data["prohibited_sectors"]
        
        # Cache key
        cache_key = f"{company_sector}|{','.join(preferred_sectors)}|{','.join(prohibited_sectors)}"
        
        if cache_key in self._sector_analysis_cache:
            self.stats["cache_hits"] += 1
            return self._sector_analysis_cache[cache_key]
        
        # Analyse compatibilité
        compatibility_analysis = {
            "match_type": "unknown",
            "compatibility_level": SectorCompatibilityLevel.ACCEPTABLE,
            "connection_strength": 0.5,
            "compatibility_factors": [],
            "concerns": []
        }
        
        # 1. Vérification secteurs rédhibitoires (priorité absolue)
        if company_sector in prohibited_sectors:
            compatibility_analysis.update({
                "match_type": "prohibited",
                "compatibility_level": SectorCompatibilityLevel.INCOMPATIBLE,
                "connection_strength": 0.0,
                "compatibility_factors": [],
                "concerns": [f"Secteur {company_sector} dans secteurs rédhibitoires"]
            })
        
        # 2. Vérification secteurs préférés (score parfait)
        elif company_sector in preferred_sectors:
            compatibility_analysis.update({
                "match_type": "preferred",
                "compatibility_level": SectorCompatibilityLevel.PERFECT,
                "connection_strength": 1.0,
                "compatibility_factors": [f"Secteur {company_sector} dans secteurs préférés"],
                "concerns": []
            })
        
        # 3. Analyse connexions sectorielles
        else:
            connection_analysis = self._analyze_sector_connections(
                company_sector, preferred_sectors, prohibited_sectors
            )
            compatibility_analysis.update(connection_analysis)
        
        # Mise en cache
        self._sector_analysis_cache[cache_key] = compatibility_analysis
        
        return compatibility_analysis
    
    def _analyze_sector_connections(
        self,
        company_sector: str,
        preferred_sectors: List[str],
        prohibited_sectors: List[str]
    ) -> Dict[str, Any]:
        """🔗 Analyse connexions sectorielles"""
        
        max_connection_strength = 0.0
        best_connection_type = "none"
        compatibility_factors = []
        concerns = []
        
        # Analyse connexions avec secteurs préférés
        for preferred in preferred_sectors:
            connection_strength = self._calculate_connection_strength(company_sector, preferred)
            
            if connection_strength > max_connection_strength:
                max_connection_strength = connection_strength
                
                if connection_strength >= 0.8:
                    best_connection_type = "direct_connection"
                elif connection_strength >= 0.6:
                    best_connection_type = "natural_transition"
                elif connection_strength >= 0.4:
                    best_connection_type = "distant_connection"
                else:
                    best_connection_type = "weak_connection"
        
        # Génération facteurs et préoccupations
        if max_connection_strength >= 0.8:
            compatibility_factors.append(f"Connexion directe détectée avec secteurs préférés")
        elif max_connection_strength >= 0.6:
            compatibility_factors.append(f"Transition naturelle possible vers secteurs préférés")
        elif max_connection_strength >= 0.4:
            compatibility_factors.append(f"Connexion distante avec secteurs préférés")
        else:
            concerns.append(f"Secteur {company_sector} éloigné des préférences candidat")
        
        # Vérification proximité secteurs rédhibitoires
        for prohibited in prohibited_sectors:
            prohibition_risk = self._calculate_connection_strength(company_sector, prohibited)
            if prohibition_risk >= 0.6:
                concerns.append(f"Secteur proche de {prohibited} (rédhibitoire)")
                max_connection_strength *= 0.7  # Pénalité
        
        # Détermination niveau compatibilité
        if max_connection_strength >= 0.8:
            compatibility_level = SectorCompatibilityLevel.EXCELLENT
        elif max_connection_strength >= 0.6:
            compatibility_level = SectorCompatibilityLevel.GOOD
        elif max_connection_strength >= 0.4:
            compatibility_level = SectorCompatibilityLevel.ACCEPTABLE
        elif max_connection_strength >= 0.2:
            compatibility_level = SectorCompatibilityLevel.POOR
        else:
            compatibility_level = SectorCompatibilityLevel.POOR
        
        return {
            "match_type": best_connection_type,
            "compatibility_level": compatibility_level,
            "connection_strength": max_connection_strength,
            "compatibility_factors": compatibility_factors,
            "concerns": concerns
        }
    
    def _calculate_connection_strength(self, sector1: str, sector2: str) -> float:
        """🔢 Calcul force connexion entre 2 secteurs"""
        
        if sector1 == sector2:
            return 1.0
        
        # Vérification bidirectionnelle
        for primary, secondary in [(sector1, sector2), (sector2, sector1)]:
            if primary in self.sector_connections:
                connections = self.sector_connections[primary]
                base_strength = connections.get("connection_strength", 0.5)
                
                if secondary in connections.get("direct_connections", []):
                    return base_strength * 1.0
                elif secondary in connections.get("natural_transitions", []):
                    return base_strength * 0.8
                elif secondary in connections.get("distant_connections", []):
                    return base_strength * 0.6
        
        # Aucune connexion explicite
        return 0.1
    
    def _calculate_base_sector_score(self, compatibility_analysis: Dict[str, Any]) -> float:
        """🧮 Calcul score de base secteur"""
        
        match_type = compatibility_analysis["match_type"]
        connection_strength = compatibility_analysis["connection_strength"]
        
        # Scores selon type de match
        if match_type == "prohibited":
            return 0.0
        elif match_type == "preferred":
            return 1.0
        elif match_type == "direct_connection":
            return 0.85
        elif match_type == "natural_transition":
            return 0.70
        elif match_type == "distant_connection":
            return 0.55
        else:
            # Score basé sur force connexion
            return min(0.5, connection_strength)
    
    def _apply_sector_modifiers(
        self,
        base_score: float,
        compatibility_analysis: Dict[str, Any],
        sector_data: Dict[str, Any]
    ) -> float:
        """🔧 Application modifiers secteur"""
        
        adjusted_score = base_score
        
        # 1. Modifier ouverture changement carrière
        career_openness = sector_data["career_change_openness"]
        if career_openness >= 4:  # Très ouvert
            adjusted_score *= 1.15
        elif career_openness >= 3:  # Moyennement ouvert
            adjusted_score *= 1.05
        elif career_openness <= 2:  # Peu ouvert
            adjusted_score *= 0.9
        
        # 2. Modifier priorité secteur vs poste
        sector_priority = sector_data["sector_priority_vs_role"]
        if sector_priority >= 4:  # Secteur très important
            # Renforce le score si bon, pénalise si mauvais
            if base_score >= 0.7:
                adjusted_score *= 1.1
            elif base_score <= 0.3:
                adjusted_score *= 0.8
        elif sector_priority <= 2:  # Secteur moins important
            # Atténue l'impact (bon ou mauvais)
            adjusted_score = 0.5 + (adjusted_score - 0.5) * 0.7
        
        # 3. Modifier selon taille entreprise
        company_size = sector_data["company_size"]
        if company_size in self.size_modifiers:
            modifiers = self.size_modifiers[company_size]
            
            # Application des bonus/malus
            for modifier_type, value in modifiers.items():
                if modifier_type.endswith("_bonus") and value > 0:
                    adjusted_score = min(1.0, adjusted_score + value)
                elif modifier_type.endswith("_malus") and value < 0:
                    adjusted_score = max(0.0, adjusted_score + value)
        
        # 4. Modifier selon stade croissance
        growth_stage = sector_data["growth_stage"]
        if growth_stage == "growth" and career_openness >= 3:
            adjusted_score *= 1.05  # Bonus croissance si ouvert
        elif growth_stage == "restructuring":
            adjusted_score *= 0.95  # Malus restructuration
        
        return min(1.0, max(0.0, adjusted_score))
    
    def _enrich_sector_result(
        self,
        final_score: float,
        compatibility_analysis: Dict[str, Any],
        sector_data: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """🔧 Enrichissement résultat secteur"""
        
        # Recommandations intelligentes
        recommendations = self._generate_sector_recommendations(
            final_score, compatibility_analysis, sector_data
        )
        
        # Analyse détaillée
        detailed_analysis = self._generate_detailed_sector_analysis(
            compatibility_analysis, sector_data
        )
        
        return {
            "final_score": final_score,
            "compatibility_level": compatibility_analysis["compatibility_level"].value,
            "sector_analysis": {
                "company_sector": sector_data["company_sector"],
                "preferred_sectors": sector_data["raw_preferred"],
                "prohibited_sectors": sector_data["raw_prohibited"],
                "match_type": compatibility_analysis["match_type"],
                "connection_strength": compatibility_analysis["connection_strength"],
                "career_change_openness": sector_data["career_change_openness"],
                "sector_priority_vs_role": sector_data["sector_priority_vs_role"]
            },
            "compatibility_factors": compatibility_analysis["compatibility_factors"],
            "concerns": compatibility_analysis["concerns"],
            "detailed_analysis": detailed_analysis,
            "recommendations": recommendations,
            "calculated_at": datetime.now().isoformat(),
            "version": self.version,
            "scorer": self.name
        }
    
    def _generate_sector_recommendations(
        self,
        final_score: float,
        compatibility_analysis: Dict[str, Any],
        sector_data: Dict[str, Any]
    ) -> List[str]:
        """💡 Génération recommandations secteur"""
        
        recommendations = []
        
        # Recommandations globales
        if compatibility_analysis["compatibility_level"] == SectorCompatibilityLevel.PERFECT:
            recommendations.append("🎯 Secteur parfaitement aligné - Argument majeur")
        elif compatibility_analysis["compatibility_level"] == SectorCompatibilityLevel.EXCELLENT:
            recommendations.append("🌟 Excellente compatibilité sectorielle")
        elif compatibility_analysis["compatibility_level"] == SectorCompatibilityLevel.GOOD:
            recommendations.append("✅ Bonne compatibilité - Transition naturelle")
        elif compatibility_analysis["compatibility_level"] == SectorCompatibilityLevel.ACCEPTABLE:
            recommendations.append("⚠️ Compatibilité modérée - Valoriser transférabilité")
        elif compatibility_analysis["compatibility_level"] == SectorCompatibilityLevel.POOR:
            recommendations.append("🔍 Compatibilité faible - Creuser motivations")
        else:
            recommendations.append("❌ Secteur incompatible - Risque de refus")
        
        # Recommandations spécifiques
        match_type = compatibility_analysis["match_type"]
        
        if match_type == "preferred":
            recommendations.append("💼 Mettre en avant l'alignement secteur candidat")
        elif match_type == "direct_connection":
            recommendations.append("🔗 Souligner les connexions sectorielles")
        elif match_type == "natural_transition":
            recommendations.append("🚀 Présenter comme évolution naturelle")
        elif match_type == "prohibited":
            recommendations.append("🚫 Abandon recommandé - Secteur rédhibitoire")
        
        # Recommandations selon ouverture changement
        career_openness = sector_data["career_change_openness"]
        if career_openness >= 4:
            recommendations.append("🔄 Candidat ouvert - Exploiter opportunités transverses")
        elif career_openness <= 2:
            recommendations.append("⚠️ Candidat peu ouvert - Rester proche secteur actuel")
        
        # Recommandations selon priorité secteur
        sector_priority = sector_data["sector_priority_vs_role"]
        if sector_priority >= 4:
            recommendations.append("🎯 Secteur critique - Argumenter solidement")
        elif sector_priority <= 2:
            recommendations.append("💡 Secteur moins critique - Focaliser sur poste")
        
        return recommendations
    
    def _generate_detailed_sector_analysis(
        self,
        compatibility_analysis: Dict[str, Any],
        sector_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """📊 Analyse détaillée secteur"""
        
        return {
            "sector_mapping": {
                "company_sector_normalized": sector_data["company_sector"],
                "preferred_sectors_normalized": sector_data["preferred_sectors"],
                "prohibited_sectors_normalized": sector_data["prohibited_sectors"]
            },
            "compatibility_metrics": {
                "connection_strength": compatibility_analysis["connection_strength"],
                "match_type": compatibility_analysis["match_type"],
                "risk_level": "high" if compatibility_analysis["compatibility_level"] in [
                    SectorCompatibilityLevel.POOR, SectorCompatibilityLevel.INCOMPATIBLE
                ] else "low"
            },
            "candidate_profile": {
                "career_change_openness": sector_data["career_change_openness"],
                "sector_priority_vs_role": sector_data["sector_priority_vs_role"],
                "flexibility_index": sector_data["career_change_openness"] / 5.0
            },
            "company_context": {
                "company_size": sector_data["company_size"].value,
                "growth_stage": sector_data["growth_stage"],
                "size_modifier": self.size_modifiers.get(sector_data["company_size"], {}).get("description", "")
            }
        }
    
    def _create_fallback_score(self, reason: str) -> Dict[str, Any]:
        """🚨 Score fallback en cas d'erreur"""
        
        logger.warning(f"Fallback SectorCompatibilityScorer: {reason}")
        
        return {
            "final_score": 0.5,  # Score neutre
            "compatibility_level": SectorCompatibilityLevel.ACCEPTABLE.value,
            "sector_analysis": {
                "company_sector": None,
                "preferred_sectors": [],
                "prohibited_sectors": [],
                "match_type": "unknown",
                "connection_strength": 0.5,
                "career_change_openness": 3,
                "sector_priority_vs_role": 3
            },
            "compatibility_factors": [],
            "concerns": [f"Mode dégradé: {reason}"],
            "detailed_analysis": {},
            "recommendations": [
                f"⚠️ {reason}",
                "🛠️ Vérifier manuellement la compatibilité sectorielle"
            ],
            "calculated_at": datetime.now().isoformat(),
            "version": f"{self.version}-fallback",
            "scorer": self.name,
            "error": reason
        }
    
    def _update_stats(self, processing_time: float, compatibility_level: SectorCompatibilityLevel):
        """📊 Mise à jour statistiques"""
        
        # Moyenne temps de traitement
        total = self.stats["calculations"]
        current_avg = self.stats["average_processing_time"]
        self.stats["average_processing_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        # Distribution compatibilité
        self.stats["compatibility_distribution"][compatibility_level.value] += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """📈 Statistiques performance"""
        
        compatibility_rates = {}
        if self.stats["calculations"] > 0:
            for level, count in self.stats["compatibility_distribution"].items():
                compatibility_rates[level] = count / self.stats["calculations"]
        
        cache_hit_rate = 0.0
        if self.stats["calculations"] > 0:
            cache_hit_rate = self.stats["cache_hits"] / self.stats["calculations"]
        
        return {
            "scorer_stats": self.stats.copy(),
            "performance_metrics": {
                "average_processing_time_ms": self.stats["average_processing_time"],
                "target_achieved": self.stats["average_processing_time"] < 11.0,
                "cache_hit_rate": cache_hit_rate,
                "compatibility_rates": compatibility_rates
            },
            "cache_size": len(self._sector_analysis_cache)
        }
    
    def get_sector_connections_preview(self, sector: str) -> Dict[str, Any]:
        """🔍 Aperçu connexions secteur"""
        
        normalized_sector = self._normalize_sector(sector)
        
        if normalized_sector in self.sector_connections:
            connections = self.sector_connections[normalized_sector]
            return {
                "sector": normalized_sector,
                "has_connections": True,
                "direct_connections": connections.get("direct_connections", []),
                "natural_transitions": connections.get("natural_transitions", []),
                "distant_connections": connections.get("distant_connections", []),
                "connection_strength": connections.get("connection_strength", 0.5)
            }
        else:
            return {
                "sector": normalized_sector,
                "has_connections": False,
                "message": f"Pas de connexions définies pour {normalized_sector}"
            }
    
    def clear_cache(self):
        """🧹 Nettoyage cache"""
        self._sector_analysis_cache.clear()
