# nextvision/engines/motivations_scoring_engine.py
"""
Moteur de scoring d'alignement motivationnel
Intégration seamless avec l'architecture NEXTVISION v3.2.1
Performance cible: 2-5ms ajoutés au pipeline existant
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import asyncio
import time
from dataclasses import dataclass

from nextvision.models.questionnaire_advanced import MotivationsClassees
from nextvision.services.gpt_direct_service import JobData


@dataclass
class MotivationWeight:
    """Poids et importance des différentes motivations"""
    evolution: float = 0.25
    salaire: float = 0.20
    equipe: float = 0.25
    innovation: float = 0.20
    flexibilite: float = 0.10


class JobMotivationSignals(BaseModel):
    """Signaux motivationnels extraits du job"""
    evolution_signals: List[str] = []
    salaire_signals: List[str] = []
    equipe_signals: List[str] = []
    innovation_signals: List[str] = []
    flexibilite_signals: List[str] = []
    
    evolution_score: float = 0.0
    salaire_score: float = 0.0
    equipe_score: float = 0.0
    innovation_score: float = 0.0
    flexibilite_score: float = 0.0


class MotivationsAlignmentScorer:
    """
    Calculateur d'alignement motivationnel optimisé pour l'architecture NEXTVISION
    """
    
    def __init__(self):
        self.motivation_weights = MotivationWeight()
        
        # Cache pour optimiser les performances répétitives
        self._job_signals_cache: Dict[str, JobMotivationSignals] = {}
        
        # Mots-clés optimisés pour détection rapide (sans GPT)
        self.keywords_map = {
            "evolution": [
                "évolution", "carrière", "promotion", "leadership", "management", 
                "senior", "lead", "responsabilités", "formation", "développement",
                "mentoring", "expertise", "croissance", "progression"
            ],
            "salaire": [
                "salaire", "rémunération", "bonus", "prime", "stock", "equity",
                "avantages", "benefits", "package", "intéressement", "participation"
            ],
            "equipe": [
                "équipe", "team", "collaboration", "collectif", "cohésion",
                "startup", "scale-up", "culture", "valeurs", "ambiance", "spirit"
            ],
            "innovation": [
                "innovation", "ia", "ai", "technologie", "r&d", "recherche",
                "développement", "cutting-edge", "state-of-the-art", "disruption",
                "transformation", "digital", "tech"
            ],
            "flexibilite": [
                "télétravail", "remote", "flexible", "hybride", "horaires",
                "autonomie", "liberté", "work-life", "balance", "souplesse"
            ]
        }
    
    async def calculate_score(
        self,
        candidat_motivations: MotivationsClassees,
        job_data: JobData,
        job_cache_key: Optional[str] = None
    ) -> float:
        """
        Calcule le score d'alignement motivationnel entre candidat et job
        
        Args:
            candidat_motivations: Motivations du candidat avec priorités
            job_data: Données du job (benefits, responsibilities, etc.)
            job_cache_key: Clé de cache pour optimiser les performances
            
        Returns:
            Score d'alignement entre 0.0 et 1.0
        """
        start_time = time.perf_counter()
        
        # 1. Extraction des signaux motivationnels du job (avec cache)
        job_signals = await self._extract_job_motivation_signals(job_data, job_cache_key)
        
        # 2. Calcul de l'alignement avec les priorités candidat
        alignment_score = self._calculate_alignment_score(candidat_motivations, job_signals)
        
        # 3. Normalisation et ajustement final
        final_score = self._normalize_score(alignment_score)
        
        execution_time = (time.perf_counter() - start_time) * 1000
        print(f"🎯 MotivationsAlignmentScorer: {execution_time:.2f}ms")
        
        return final_score
    
    async def _extract_job_motivation_signals(
        self,
        job_data: JobData,
        cache_key: Optional[str] = None
    ) -> JobMotivationSignals:
        """Extrait les signaux motivationnels du job avec cache optimisé"""
        
        # Vérification cache
        if cache_key and cache_key in self._job_signals_cache:
            return self._job_signals_cache[cache_key]
        
        signals = JobMotivationSignals()
        
        # Texte combiné pour analyse rapide
        combined_text = ""
        if hasattr(job_data, 'benefits') and job_data.benefits:
            combined_text += " ".join(job_data.benefits).lower()
        if hasattr(job_data, 'responsibilities') and job_data.responsibilities:
            combined_text += " " + " ".join(job_data.responsibilities).lower()
        if hasattr(job_data, 'description'):
            combined_text += " " + str(job_data.description).lower()
        
        # Détection rapide par mots-clés (plus rapide que GPT)
        for motivation, keywords in self.keywords_map.items():
            matches = []
            score = 0.0
            
            for keyword in keywords:
                if keyword in combined_text:
                    matches.append(keyword)
                    score += 1.0
            
            # Normalisation du score (0-1) basé sur la fréquence
            normalized_score = min(score / len(keywords) * 3, 1.0)  # Max boost x3
            
            # Attribution des résultats
            if motivation == "evolution":
                signals.evolution_signals = matches
                signals.evolution_score = normalized_score
            elif motivation == "salaire":
                signals.salaire_signals = matches
                signals.salaire_score = normalized_score
            elif motivation == "equipe":
                signals.equipe_signals = matches
                signals.equipe_score = normalized_score
            elif motivation == "innovation":
                signals.innovation_signals = matches
                signals.innovation_score = normalized_score
            elif motivation == "flexibilite":
                signals.flexibilite_signals = matches
                signals.flexibilite_score = normalized_score
        
        # Cache pour performances
        if cache_key:
            self._job_signals_cache[cache_key] = signals
        
        return signals
    
    def _calculate_alignment_score(
        self,
        candidat_motivations: MotivationsClassees,
        job_signals: JobMotivationSignals
    ) -> float:
        """Calcule l'alignement basé sur les priorités candidat et signaux job"""
        
        total_score = 0.0
        total_weight = 0.0
        
        # Mapping des motivations candidat vers les scores job
        motivation_mapping = {
            "évolution": job_signals.evolution_score,
            "evolution": job_signals.evolution_score,
            "salaire": job_signals.salaire_score,
            "rémunération": job_signals.salaire_score,
            "équipe": job_signals.equipe_score,
            "equipe": job_signals.equipe_score,
            "team": job_signals.equipe_score,
            "innovation": job_signals.innovation_score,
            "technologie": job_signals.innovation_score,
            "flexibilité": job_signals.flexibilite_score,
            "flexibilite": job_signals.flexibilite_score,
            "télétravail": job_signals.flexibilite_score,
        }
        
        # Calcul pondéré basé sur les priorités candidat
        for i, motivation in enumerate(candidat_motivations.classees):
            motivation_clean = motivation.lower().strip()
            
            # Poids inversé (priorité 1 = poids max)
            priority_rank = candidat_motivations.priorites[i] if i < len(candidat_motivations.priorites) else i + 1
            weight = 1.0 / priority_rank  # Priorité 1 = poids 1.0, Priorité 2 = poids 0.5, etc.
            
            # Score job pour cette motivation
            job_score = motivation_mapping.get(motivation_clean, 0.0)
            
            total_score += weight * job_score
            total_weight += weight
        
        # Moyenne pondérée
        if total_weight > 0:
            return total_score / total_weight
        
        return 0.0
    
    def _normalize_score(self, raw_score: float) -> float:
        """Normalise le score final pour s'aligner sur les autres composants NEXTVISION"""
        
        # Ajustement pour être cohérent avec les autres scores (0.5-0.95 typique)
        normalized = max(0.0, min(1.0, raw_score))
        
        # Transformation pour distribution plus réaliste
        if normalized < 0.2:
            return 0.2 + normalized * 0.3  # Boost minimum à 0.2
        elif normalized > 0.8:
            return 0.8 + (normalized - 0.8) * 0.75  # Limitation haute à 0.95
        else:
            return normalized
    
    def clear_cache(self):
        """Vide le cache pour libérer la mémoire"""
        self._job_signals_cache.clear()


# Instance globale pour réutilisation (performance)
motivations_scoring_engine = MotivationsAlignmentScorer()
