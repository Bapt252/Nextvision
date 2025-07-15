# nextvision/services/job_intelligence_service.py
"""
Service d'intelligence job pour analyse motivationnelle enrichie
Complément au MotivationsAlignmentScorer
Performance optimisée pour l'intégration NEXTVISION
"""

from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel
import asyncio
import json
import hashlib

from nextvision.services.gpt_direct_service import JobData, CVData


class JobIntelligenceSignals(BaseModel):
    """Signaux d'intelligence extraits du job pour enrichir le matching"""
    
    # Signaux culturels
    culture_type: str = "standard"  # startup, corporate, scale-up, traditional
    innovation_level: str = "medium"  # low, medium, high, cutting-edge
    team_size_indication: str = "unknown"  # small, medium, large, enterprise
    
    # Signaux d'évolution
    growth_potential: float = 0.5  # 0-1
    learning_opportunities: List[str] = []
    leadership_potential: float = 0.5  # 0-1
    
    # Signaux de flexibilité
    remote_flexibility: float = 0.5  # 0-1
    work_life_balance: float = 0.5  # 0-1
    autonomy_level: float = 0.5  # 0-1
    
    # Méta-données
    confidence_score: float = 0.5  # Confiance dans l'analyse
    processing_time_ms: float = 0.0


class JobIntelligenceService:
    """
    Service d'analyse intelligente des jobs pour enrichir le scoring motivationnel
    """
    
    def __init__(self):
        self.analysis_cache: Dict[str, JobIntelligenceSignals] = {}
        
        # Patterns pré-définis pour analyse rapide
        self.culture_patterns = {
            "startup": [
                "startup", "scale-up", "création", "innovation", "disruption",
                "agile", "lean", "mvp", "product-market fit", "growth hacking"
            ],
            "corporate": [
                "multinational", "groupe", "filiale", "siège", "corporate",
                "processus", "procédures", "compliance", "audit", "gouvernance"
            ],
            "tech": [
                "tech", "digital", "ia", "ai", "machine learning", "data science",
                "cloud", "devops", "microservices", "api", "saas"
            ]
        }
        
        self.growth_indicators = [
            "formation", "développement", "évolution", "carrière", "promotion",
            "mentoring", "coaching", "certification", "expertise", "leadership",
            "responsabilités", "management", "équipe"
        ]
        
        self.flexibility_indicators = [
            "télétravail", "remote", "hybride", "flexible", "autonomie",
            "horaires", "souplesse", "work-life", "balance", "congés"
        ]
    
    async def analyze_job_intelligence(
        self,
        job_data: JobData,
        cache_key: Optional[str] = None
    ) -> JobIntelligenceSignals:
        """
        Analyse intelligente du job pour extraction de signaux enrichis
        
        Args:
            job_data: Données du job à analyser
            cache_key: Clé de cache pour optimisation
            
        Returns:
            Signaux d'intelligence extraits
        """
        import time
        start_time = time.perf_counter()
        
        # Vérification cache
        if cache_key and cache_key in self.analysis_cache:
            cached_result = self.analysis_cache[cache_key]
            cached_result.processing_time_ms = (time.perf_counter() - start_time) * 1000
            return cached_result
        
        # Extraction du texte complet
        full_text = self._extract_full_job_text(job_data).lower()
        
        # Analyse des signaux
        signals = JobIntelligenceSignals()
        
        # 1. Analyse culturelle
        signals.culture_type = self._analyze_culture_type(full_text)
        signals.innovation_level = self._analyze_innovation_level(full_text)
        signals.team_size_indication = self._analyze_team_size(full_text)
        
        # 2. Analyse d'évolution
        signals.growth_potential = self._analyze_growth_potential(full_text)
        signals.learning_opportunities = self._extract_learning_opportunities(full_text)
        signals.leadership_potential = self._analyze_leadership_potential(full_text)
        
        # 3. Analyse de flexibilité
        signals.remote_flexibility = self._analyze_remote_flexibility(full_text)
        signals.work_life_balance = self._analyze_work_life_balance(full_text)
        signals.autonomy_level = self._analyze_autonomy_level(full_text)
        
        # 4. Score de confiance
        signals.confidence_score = self._calculate_confidence_score(full_text, signals)
        
        # Temps de traitement
        signals.processing_time_ms = (time.perf_counter() - start_time) * 1000
        
        # Cache pour optimisation
        if cache_key:
            self.analysis_cache[cache_key] = signals
        
        return signals
    
    def _extract_full_job_text(self, job_data: JobData) -> str:
        """Extrait tout le texte disponible du job"""
        text_parts = []
        
        if hasattr(job_data, 'title'):
            text_parts.append(str(job_data.title))
        if hasattr(job_data, 'company'):
            text_parts.append(str(job_data.company))
        if hasattr(job_data, 'description'):
            text_parts.append(str(job_data.description))
        if hasattr(job_data, 'benefits') and job_data.benefits:
            text_parts.extend(job_data.benefits)
        if hasattr(job_data, 'responsibilities') and job_data.responsibilities:
            text_parts.extend(job_data.responsibilities)
        if hasattr(job_data, 'requirements'):
            text_parts.append(str(job_data.requirements))
        
        return " ".join(text_parts)
    
    def _analyze_culture_type(self, text: str) -> str:
        """Détermine le type de culture d'entreprise"""
        scores = {}
        
        for culture, patterns in self.culture_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text)
            scores[culture] = score
        
        if scores["startup"] > scores.get("corporate", 0):
            return "startup"
        elif scores["tech"] > 2:
            return "tech"
        elif scores["corporate"] > 0:
            return "corporate"
        else:
            return "standard"
    
    def _analyze_innovation_level(self, text: str) -> str:
        """Évalue le niveau d'innovation"""
        innovation_keywords = [
            "innovation", "ia", "ai", "machine learning", "r&d", "recherche",
            "cutting-edge", "disruptif", "transformation", "digital", "tech"
        ]
        
        count = sum(1 for keyword in innovation_keywords if keyword in text)
        
        if count >= 4:
            return "cutting-edge"
        elif count >= 2:
            return "high"
        elif count >= 1:
            return "medium"
        else:
            return "low"
    
    def _analyze_team_size(self, text: str) -> str:
        """Estime la taille de l'équipe"""
        small_indicators = ["startup", "small team", "petite équipe", "agile"]
        large_indicators = ["multinational", "groupe", "enterprise", "siège"]
        
        small_count = sum(1 for indicator in small_indicators if indicator in text)
        large_count = sum(1 for indicator in large_indicators if indicator in text)
        
        if large_count > small_count:
            return "large"
        elif small_count > 0:
            return "small"
        else:
            return "medium"
    
    def _analyze_growth_potential(self, text: str) -> float:
        """Calcule le potentiel d'évolution (0-1)"""
        count = sum(1 for indicator in self.growth_indicators if indicator in text)
        return min(count / len(self.growth_indicators) * 2, 1.0)
    
    def _extract_learning_opportunities(self, text: str) -> List[str]:
        """Extrait les opportunités d'apprentissage"""
        opportunities = []
        
        learning_keywords = {
            "formation": "Formation continue",
            "certification": "Certifications",
            "mentoring": "Mentoring",
            "coaching": "Coaching",
            "expertise": "Développement expertise",
            "technologies": "Nouvelles technologies",
            "projets": "Projets innovants"
        }
        
        for keyword, opportunity in learning_keywords.items():
            if keyword in text:
                opportunities.append(opportunity)
        
        return opportunities
    
    def _analyze_leadership_potential(self, text: str) -> float:
        """Évalue le potentiel de leadership (0-1)"""
        leadership_keywords = [
            "management", "équipe", "responsabilités", "leadership",
            "encadrement", "coordination", "pilotage", "direction"
        ]
        
        count = sum(1 for keyword in leadership_keywords if keyword in text)
        return min(count / len(leadership_keywords) * 2, 1.0)
    
    def _analyze_remote_flexibility(self, text: str) -> float:
        """Évalue la flexibilité télétravail (0-1)"""
        remote_keywords = ["télétravail", "remote", "hybride", "distance"]
        count = sum(1 for keyword in remote_keywords if keyword in text)
        
        # Boost si explicitement mentionné
        if "100% télétravail" in text or "full remote" in text:
            return 1.0
        elif count > 0:
            return 0.7
        else:
            return 0.3
    
    def _analyze_work_life_balance(self, text: str) -> float:
        """Évalue l'équilibre vie-travail (0-1)"""
        balance_keywords = [
            "work-life", "équilibre", "congés", "vacances", "souplesse",
            "horaires flexibles", "rtt", "temps partiel"
        ]
        
        count = sum(1 for keyword in balance_keywords if keyword in text)
        return min(count / len(balance_keywords) * 3, 1.0)
    
    def _analyze_autonomy_level(self, text: str) -> float:
        """Évalue le niveau d'autonomie (0-1)"""
        autonomy_keywords = [
            "autonomie", "indépendant", "initiative", "créativité",
            "liberté", "flexible", "self-managed"
        ]
        
        count = sum(1 for keyword in autonomy_keywords if keyword in text)
        return min(count / len(autonomy_keywords) * 2, 1.0)
    
    def _calculate_confidence_score(
        self,
        text: str,
        signals: JobIntelligenceSignals
    ) -> float:
        """Calcule un score de confiance dans l'analyse"""
        
        # Facteurs de confiance
        text_length_factor = min(len(text.split()) / 100, 1.0)  # Plus de texte = plus de confiance
        signals_count = sum([
            1 if signals.culture_type != "standard" else 0,
            1 if signals.innovation_level != "medium" else 0,
            1 if len(signals.learning_opportunities) > 0 else 0,
            1 if signals.growth_potential > 0.3 else 0,
            1 if signals.remote_flexibility != 0.3 else 0
        ])
        
        signals_factor = signals_count / 5.0
        
        return (text_length_factor + signals_factor) / 2
    
    def get_cache_key(self, job_data: JobData) -> str:
        """Génère une clé de cache unique pour le job"""
        job_text = self._extract_full_job_text(job_data)
        return hashlib.md5(job_text.encode()).hexdigest()[:16]
    
    def clear_cache(self):
        """Vide le cache pour libérer la mémoire"""
        self.analysis_cache.clear()


# Instance globale pour réutilisation
job_intelligence_service = JobIntelligenceService()
