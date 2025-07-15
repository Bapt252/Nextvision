"""
🎯 NEXTVISION - MotivationsAlignmentScorer Compatible JobData
============================================================

Moteur de scoring motivationnel haute performance compatible avec la structure 
JobData du GPT Direct Service et intégrable dans l'endpoint principal.

Performance: < 5ms ciblé
Cache intelligent: 100 entrées
Compatibilité: JobData structure complète

Version: 1.0.0 - Production Ready
Author: NEXTEN Team
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Import des structures NEXTVISION
try:
    from nextvision.services.gpt_direct_service import JobData, CVData
except ImportError:
    # Fallback si import échoue
    from typing import NamedTuple
    
    class JobData(NamedTuple):
        title: str
        company: str
        location: str
        contract_type: str
        required_skills: List[str]
        preferred_skills: List[str]
        responsibilities: List[str]
        requirements: List[str]
        benefits: List[str]
        salary_range: Dict[str, int]
        remote_policy: str
    
    class CVData(NamedTuple):
        name: str
        email: str
        phone: str
        skills: List[str]
        years_of_experience: int
        education: str
        job_titles: List[str]
        companies: List[str]
        location: str
        summary: str
        objective: str
        languages: List[str]
        certifications: List[str]

logger = logging.getLogger(__name__)

class MotivationType(str, Enum):
    """Types de motivations professionnelles détectées"""
    INNOVATION = "innovation"
    EVOLUTION = "evolution" 
    EQUIPE = "equipe"
    SALAIRE = "salaire"
    FLEXIBILITE = "flexibilite"
    AUTONOMIE = "autonomie"
    IMPACT = "impact"
    APPRENTISSAGE = "apprentissage"

@dataclass
class MotivationScore:
    """Score d'une motivation spécifique"""
    motivation_type: MotivationType
    score: float  # 0.0 à 1.0
    confidence: float
    evidence_found: List[str]
    missing_elements: List[str]
    weight: float  # Poids de cette motivation

@dataclass
class MotivationsResult:
    """Résultat complet du scoring motivationnel"""
    overall_score: float
    confidence: float
    motivation_scores: List[MotivationScore]
    strongest_alignments: List[str]
    improvement_suggestions: List[str]
    processing_time_ms: float

class JobIntelligenceService:
    """🧠 Service d'intelligence job pour analyse culturelle et opportunités"""
    
    def __init__(self):
        self.cultural_keywords = {
            "startup": ["startup", "innovation", "agile", "entrepreneurial", "disruptive", "scale-up"],
            "tech": ["tech", "digital", "software", "ai", "machine learning", "data"],
            "corporate": ["corporate", "enterprise", "multinational", "established", "structured"]
        }
        
        self.evolution_signals = [
            "career development", "growth opportunities", "promotion", "leadership",
            "progression", "advancement", "évolution", "développement", "carrière"
        ]
        
        self.flexibility_signals = [
            "remote", "flexible", "work-life balance", "télétravail", "hybride",
            "horaires flexibles", "autonomy", "flexible hours"
        ]
    
    def analyze_culture(self, job_data: JobData) -> Dict[str, float]:
        """Analyse la culture d'entreprise"""
        text_content = f"{job_data.title} {' '.join(job_data.responsibilities)} {' '.join(job_data.benefits)}".lower()
        
        culture_scores = {}
        for culture_type, keywords in self.cultural_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_content) / len(keywords)
            culture_scores[culture_type] = min(1.0, score * 2)  # Amplify signal
        
        return culture_scores
    
    def extract_evolution_signals(self, job_data: JobData) -> Tuple[float, List[str]]:
        """Extrait les signaux d'évolution/progression"""
        text_content = f"{' '.join(job_data.responsibilities)} {' '.join(job_data.benefits)}".lower()
        
        found_signals = []
        for signal in self.evolution_signals:
            if signal in text_content:
                found_signals.append(signal)
        
        evolution_score = min(1.0, len(found_signals) / 5)  # Normalize sur 5 signaux max
        return evolution_score, found_signals
    
    def extract_flexibility_signals(self, job_data: JobData) -> Tuple[float, List[str]]:
        """Extrait les signaux de flexibilité"""
        text_content = f"{job_data.remote_policy} {' '.join(job_data.benefits)}".lower()
        
        found_signals = []
        
        # Analyse remote policy
        if "remote" in job_data.remote_policy.lower():
            found_signals.append("remote_work")
        if "hybride" in job_data.remote_policy.lower() or "hybrid" in job_data.remote_policy.lower():
            found_signals.append("hybrid_work")
        
        # Analyse autres signaux
        for signal in self.flexibility_signals:
            if signal in text_content:
                found_signals.append(signal)
        
        flexibility_score = min(1.0, len(found_signals) / 4)  # Normalize sur 4 signaux max
        return flexibility_score, found_signals
    
    def calculate_confidence(self, job_data: JobData) -> float:
        """Calcule le niveau de confiance de l'analyse"""
        confidence = 0.7  # Base
        
        # Boost si beaucoup de détails
        if len(job_data.responsibilities) >= 3:
            confidence += 0.1
        if len(job_data.benefits) >= 2:
            confidence += 0.1
        if len(job_data.required_skills) >= 3:
            confidence += 0.1
        
        return min(0.95, confidence)

class MotivationsAlignmentScorer:
    """🎯 Scorer principal d'alignement motivationnel - Compatible JobData"""
    
    def __init__(self):
        self.job_intelligence = JobIntelligenceService()
        
        # Mots-clés par type de motivation
        self.motivation_keywords = {
            MotivationType.INNOVATION: [
                "innovation", "créativité", "nouveau", "disruptif", "pionnier",
                "cutting-edge", "breakthrough", "R&D", "recherche"
            ],
            MotivationType.EVOLUTION: [
                "évolution", "carrière", "promotion", "leadership", "management",
                "développement", "progression", "advancement", "growth"
            ],
            MotivationType.EQUIPE: [
                "équipe", "collaboration", "team", "collectif", "ensemble",
                "coopération", "partenariat", "mentoring", "coaching"
            ],
            MotivationType.SALAIRE: [
                "salaire", "rémunération", "bonus", "prime", "avantages",
                "benefits", "package", "compensation", "financier"
            ],
            MotivationType.FLEXIBILITE: [
                "flexibilité", "télétravail", "remote", "horaires", "équilibre",
                "work-life balance", "autonomie", "souplesse", "adaptation"
            ],
            MotivationType.AUTONOMIE: [
                "autonomie", "indépendance", "liberté", "responsabilité",
                "initiative", "ownership", "self-management", "empowerment"
            ],
            MotivationType.IMPACT: [
                "impact", "mission", "sens", "contribution", "différence",
                "changement", "social", "environnemental", "purpose"
            ],
            MotivationType.APPRENTISSAGE: [
                "apprentissage", "formation", "développement", "compétences",
                "learning", "skills", "knowledge", "expertise", "certification"
            ]
        }
        
        # Cache pour optimisation performance
        self._cache = {}
        self._cache_size = 100
    
    def score_motivations_alignment(self, 
                                   candidate_data: CVData,
                                   job_data: JobData,
                                   candidate_motivations: Optional[List[str]] = None) -> MotivationsResult:
        """
        🎯 Score principal d'alignement motivationnel
        
        Args:
            candidate_data: Données candidat (CV)
            job_data: Données job complètes (TOUS les champs JobData requis)
            candidate_motivations: Motivations explicites du candidat (optionnel)
        
        Returns:
            MotivationsResult avec score détaillé
        """
        start_time = time.time()
        
        try:
            # Génération clé cache
            cache_key = self._generate_cache_key(candidate_data, job_data)
            if cache_key in self._cache:
                logger.info("✅ Cache hit for motivations scoring")
                cached_result = self._cache[cache_key]
                cached_result.processing_time_ms = (time.time() - start_time) * 1000
                return cached_result
            
            # Détection motivations candidat
            detected_motivations = self._detect_candidate_motivations(candidate_data, candidate_motivations)
            
            # Analyse job opportunities
            job_opportunities = self._analyze_job_opportunities(job_data)
            
            # Scoring par motivation
            motivation_scores = []
            total_weighted_score = 0.0
            total_weight = 0.0
            
            for motivation, weight in detected_motivations.items():
                score_result = self._score_single_motivation(
                    motivation, weight, job_opportunities, job_data
                )
                motivation_scores.append(score_result)
                
                total_weighted_score += score_result.score * weight
                total_weight += weight
            
            # Score global
            overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.5
            
            # Confiance globale
            confidence = self.job_intelligence.calculate_confidence(job_data)
            
            # Génération insights
            strongest_alignments = self._find_strongest_alignments(motivation_scores)
            improvement_suggestions = self._generate_improvement_suggestions(motivation_scores, job_data)
            
            # Résultat final
            result = MotivationsResult(
                overall_score=overall_score,
                confidence=confidence,
                motivation_scores=motivation_scores,
                strongest_alignments=strongest_alignments,
                improvement_suggestions=improvement_suggestions,
                processing_time_ms=(time.time() - start_time) * 1000
            )
            
            # Mise en cache (si objectif performance atteint)
            if result.processing_time_ms < 10 and len(self._cache) < self._cache_size:
                self._cache[cache_key] = result
            
            logger.info(f"✅ Motivations scoring completed: {overall_score:.3f} (confidence: {confidence:.3f}, {result.processing_time_ms:.2f}ms)")
            return result
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            logger.error(f"❌ Error in motivations scoring: {e}")
            
            # Fallback result
            return MotivationsResult(
                overall_score=0.5,
                confidence=0.3,
                motivation_scores=[],
                strongest_alignments=["Analysis partially failed"],
                improvement_suggestions=["Please retry with more detailed job description"],
                processing_time_ms=processing_time
            )
    
    def _detect_candidate_motivations(self, 
                                     candidate_data: CVData, 
                                     explicit_motivations: Optional[List[str]] = None) -> Dict[MotivationType, float]:
        """Détecte les motivations principales du candidat"""
        motivations = {}
        
        # Si motivations explicites fournies
        if explicit_motivations:
            for motivation_text in explicit_motivations:
                motivation_type = self._map_text_to_motivation(motivation_text.lower())
                if motivation_type:
                    motivations[motivation_type] = 0.9  # Poids élevé pour motivations explicites
        
        # Détection via analyse CV
        cv_text = f"{candidate_data.objective} {candidate_data.summary}".lower()
        
        for motivation_type, keywords in self.motivation_keywords.items():
            keyword_matches = sum(1 for keyword in keywords if keyword in cv_text)
            if keyword_matches > 0:
                weight = min(0.8, keyword_matches / len(keywords) * 2)  # Max 0.8 pour détection auto
                motivations[motivation_type] = max(motivations.get(motivation_type, 0), weight)
        
        # Motivations par défaut si rien détecté
        if not motivations:
            motivations = {
                MotivationType.EVOLUTION: 0.6,
                MotivationType.APPRENTISSAGE: 0.5,
                MotivationType.SALAIRE: 0.4
            }
        
        return motivations
    
    def _analyze_job_opportunities(self, job_data: JobData) -> Dict[MotivationType, float]:
        """Analyse les opportunités offertes par le job"""
        opportunities = {}
        
        # Analyse texte complet du job
        job_text = f"""
        {job_data.title} {' '.join(job_data.responsibilities)} 
        {' '.join(job_data.benefits)} {' '.join(job_data.requirements)}
        """.lower()
        
        # Score par type de motivation
        for motivation_type, keywords in self.motivation_keywords.items():
            keyword_matches = sum(1 for keyword in keywords if keyword in job_text)
            opportunities[motivation_type] = min(1.0, keyword_matches / len(keywords) * 2)
        
        # Analyse spécialisée
        culture_analysis = self.job_intelligence.analyze_culture(job_data)
        
        # Boost selon culture détectée
        if culture_analysis.get("startup", 0) > 0.5:
            opportunities[MotivationType.INNOVATION] = max(opportunities[MotivationType.INNOVATION], 0.8)
            opportunities[MotivationType.AUTONOMIE] = max(opportunities[MotivationType.AUTONOMIE], 0.7)
        
        if culture_analysis.get("tech", 0) > 0.5:
            opportunities[MotivationType.APPRENTISSAGE] = max(opportunities[MotivationType.APPRENTISSAGE], 0.7)
            opportunities[MotivationType.INNOVATION] = max(opportunities[MotivationType.INNOVATION], 0.6)
        
        # Analyse évolution
        evolution_score, _ = self.job_intelligence.extract_evolution_signals(job_data)
        opportunities[MotivationType.EVOLUTION] = max(opportunities[MotivationType.EVOLUTION], evolution_score)
        
        # Analyse flexibilité
        flexibility_score, _ = self.job_intelligence.extract_flexibility_signals(job_data)
        opportunities[MotivationType.FLEXIBILITE] = max(opportunities[MotivationType.FLEXIBILITE], flexibility_score)
        
        return opportunities
    
    def _score_single_motivation(self, 
                                motivation_type: MotivationType,
                                candidate_weight: float,
                                job_opportunities: Dict[MotivationType, float],
                                job_data: JobData) -> MotivationScore:
        """Score une motivation spécifique"""
        
        job_opportunity_score = job_opportunities.get(motivation_type, 0.0)
        
        # Score base : alignement opportunité vs motivation candidat
        base_score = job_opportunity_score
        
        # Ajustements selon type de motivation
        if motivation_type == MotivationType.SALAIRE:
            # Boost si salary_range attractif
            if job_data.salary_range and job_data.salary_range.get("max", 0) > 60000:
                base_score = min(1.0, base_score + 0.2)
        
        elif motivation_type == MotivationType.FLEXIBILITE:
            # Boost selon remote policy
            if "remote" in job_data.remote_policy.lower():
                base_score = min(1.0, base_score + 0.3)
            elif "hybride" in job_data.remote_policy.lower():
                base_score = min(1.0, base_score + 0.2)
        
        # Evidence trouvée
        evidence_found = []
        missing_elements = []
        
        keywords = self.motivation_keywords[motivation_type]
        job_text = f"{job_data.title} {' '.join(job_data.responsibilities)} {' '.join(job_data.benefits)}".lower()
        
        for keyword in keywords:
            if keyword in job_text:
                evidence_found.append(keyword)
            else:
                missing_elements.append(keyword)
        
        # Confiance basée sur évidence
        confidence = min(0.9, len(evidence_found) / len(keywords) + 0.3)
        
        return MotivationScore(
            motivation_type=motivation_type,
            score=base_score,
            confidence=confidence,
            evidence_found=evidence_found[:5],  # Top 5
            missing_elements=missing_elements[:3],  # Top 3 manquants
            weight=candidate_weight
        )
    
    def _find_strongest_alignments(self, motivation_scores: List[MotivationScore]) -> List[str]:
        """Trouve les alignements les plus forts"""
        strong_alignments = []
        
        for score in motivation_scores:
            if score.score >= 0.7 and score.confidence >= 0.6:
                strong_alignments.append(
                    f"{score.motivation_type.value.title()}: {score.score:.1%} match"
                )
        
        return strong_alignments[:3]  # Top 3
    
    def _generate_improvement_suggestions(self, 
                                        motivation_scores: List[MotivationScore],
                                        job_data: JobData) -> List[str]:
        """Génère des suggestions d'amélioration"""
        suggestions = []
        
        # Analyse scores faibles
        weak_scores = [s for s in motivation_scores if s.score < 0.4 and s.weight > 0.5]
        
        for weak_score in weak_scores[:2]:  # Top 2 problèmes
            motivation = weak_score.motivation_type.value
            
            if weak_score.motivation_type == MotivationType.EVOLUTION:
                suggestions.append(f"Détailler les opportunités d'évolution de carrière pour améliorer l'attrait {motivation}")
            elif weak_score.motivation_type == MotivationType.FLEXIBILITE:
                suggestions.append(f"Clarifier la politique de télétravail et flexibilité horaires")
            elif weak_score.motivation_type == MotivationType.INNOVATION:
                suggestions.append(f"Mettre en avant les projets innovants et technologies utilisées")
            else:
                suggestions.append(f"Renforcer les éléments liés à {motivation} dans la description")
        
        return suggestions
    
    def _map_text_to_motivation(self, motivation_text: str) -> Optional[MotivationType]:
        """Map texte libre vers type de motivation"""
        text_lower = motivation_text.lower()
        
        mapping = {
            "innovation": MotivationType.INNOVATION,
            "évolution": MotivationType.EVOLUTION,
            "evolution": MotivationType.EVOLUTION,
            "carrière": MotivationType.EVOLUTION,
            "équipe": MotivationType.EQUIPE,
            "team": MotivationType.EQUIPE,
            "salaire": MotivationType.SALAIRE,
            "rémunération": MotivationType.SALAIRE,
            "flexibilité": MotivationType.FLEXIBILITE,
            "flexibility": MotivationType.FLEXIBILITE,
            "autonomie": MotivationType.AUTONOMIE,
            "autonomy": MotivationType.AUTONOMIE,
            "impact": MotivationType.IMPACT,
            "apprentissage": MotivationType.APPRENTISSAGE,
            "learning": MotivationType.APPRENTISSAGE
        }
        
        for key, motivation_type in mapping.items():
            if key in text_lower:
                return motivation_type
        
        return None
    
    def _generate_cache_key(self, candidate_data: CVData, job_data: JobData) -> str:
        """Génère clé de cache"""
        candidate_hash = hash(f"{candidate_data.name}{candidate_data.objective}{len(candidate_data.skills)}")
        job_hash = hash(f"{job_data.title}{job_data.company}{len(job_data.responsibilities)}")
        return f"motivations_{candidate_hash}_{job_hash}"

# === FONCTIONS UTILITAIRES PUBLIQUES ===

def create_motivations_scorer() -> MotivationsAlignmentScorer:
    """Factory pour créer le scorer de motivations"""
    return MotivationsAlignmentScorer()

def create_complete_job_data(title: str, company: str, 
                           required_skills: List[str] = None,
                           benefits: List[str] = None,
                           **kwargs) -> JobData:
    """
    🏗️ Utilitaire pour créer JobData complète facilement
    
    Résout le problème: TypeError missing 7 required positional arguments
    """
    
    defaults = {
        "location": "Paris, France",
        "contract_type": "CDI",
        "required_skills": required_skills or [],
        "preferred_skills": [],
        "responsibilities": [f"Missions liées au poste {title}"],
        "requirements": ["Expérience pertinente"],
        "benefits": benefits or ["Télétravail partiel", "Formation"],
        "salary_range": {"min": 45000, "max": 65000},
        "remote_policy": "Hybride"
    }
    
    # Merge avec kwargs fournis
    defaults.update(kwargs)
    
    return JobData(
        title=title,
        company=company,
        **defaults
    )

def create_complete_cv_data(name: str, skills: List[str] = None, **kwargs) -> CVData:
    """🏗️ Utilitaire pour créer CVData complète facilement"""
    
    defaults = {
        "email": f"{name.lower().replace(' ', '.')}@email.com",
        "phone": "",
        "skills": skills or [],
        "years_of_experience": 3,
        "education": "Formation supérieure",
        "job_titles": ["Poste actuel"],
        "companies": ["Entreprise"],
        "location": "Paris, France", 
        "summary": f"Profil professionnel de {name}",
        "objective": "Recherche nouvelle opportunité",
        "languages": ["Français"],
        "certifications": []
    }
    
    # Merge avec kwargs fournis
    defaults.update(kwargs)
    
    return CVData(
        name=name,
        **defaults
    )

# === VARIABLES PUBLIQUES ===

# Instance globale réutilisable
motivations_scoring_engine = MotivationsAlignmentScorer()

__all__ = [
    "MotivationsAlignmentScorer",
    "MotivationType", 
    "MotivationScore",
    "MotivationsResult",
    "JobIntelligenceService",
    "create_motivations_scorer",
    "create_complete_job_data",
    "create_complete_cv_data",
    "motivations_scoring_engine"
]

if __name__ == "__main__":
    print("🎯 NEXTVISION - MotivationsAlignmentScorer Engine")
    print("=" * 55)
    
    # Test rapide avec données complètes
    try:
        # Création données test avec utilitaires
        candidate = create_complete_cv_data(
            name="Test Candidat",
            skills=["Python", "Leadership", "Innovation"],
            objective="Recherche poste avec évolution et innovation technique"
        )
        
        job = create_complete_job_data(
            title="Senior AI Engineer", 
            company="TechCorp Innovation",
            required_skills=["Python", "AI", "Leadership"],
            benefits=["Innovation continue", "Évolution rapide", "Télétravail"],
            responsibilities=["Développement IA", "Leadership équipe", "Innovation produits"],
            salary_range={"min": 65000, "max": 80000},
            remote_policy="Hybride 3j/semaine"
        )
        
        # Test scoring
        scorer = create_motivations_scorer()
        result = scorer.score_motivations_alignment(
            candidate_data=candidate,
            job_data=job,
            candidate_motivations=["Innovation", "Évolution", "Leadership équipe"]
        )
        
        print(f"✅ Test Score: {result.overall_score:.3f}")
        print(f"📊 Confiance: {result.confidence:.3f}")
        print(f"⏱️ Temps: {result.processing_time_ms:.2f}ms")
        print(f"🎯 Alignements: {len(result.strongest_alignments)}")
        print()
        print("✅ MotivationsAlignmentScorer OPÉRATIONNEL!")
        print("🚀 Prêt pour intégration dans endpoint /api/v3/intelligent-matching")
        
    except Exception as e:
        print(f"❌ Test échoué: {e}")
        print("🔧 Vérifiez les imports et dépendances")
