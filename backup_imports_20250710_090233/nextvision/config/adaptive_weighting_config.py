"""
Nextvision V3.0 - Configuration Pondération Adaptative
=====================================================

Configuration centralisée des matrices de pondération selon raison d'écoute candidat.
Correction des matrices pour totaliser exactement 1.000000 (validation Pydantic).

PROBLÈME RÉSOLU:
- POSTE_INADEQUAT: 1.040000 → 1.000000 ✅
- MANQUE_PERSPECTIVES: 1.020000 → 1.000000 ✅ 
- REMUNERATION_FAIBLE: 1.000000 ✅ (déjà OK)

Author: NEXTEN Development Team
Version: 3.0 - Fixed
"""

from typing import Dict, List
from enum import Enum
from dataclasses import dataclass, field
import json

# ================================
# ÉNUMÉRATIONS
# ================================

class ListeningReasonType(Enum):
    """Types de raisons d'écoute pour pondération adaptative"""
    REMUNERATION_FAIBLE = "remuneration_faible"
    POSTE_INADEQUAT = "poste_inadequat" 
    LOCALISATION = "localisation"
    FLEXIBILITE = "flexibilite"
    MANQUE_PERSPECTIVES = "perspectives"  # Mapping avec contexte fourni
    AUTRE = "autre"

# ================================
# PONDÉRATIONS DE BASE V3.0
# ================================

BASE_WEIGHTS_V3 = {
    "semantic": 0.24,           # 24% - V2.0 ajusté
    "salary": 0.19,             # 19% - V2.0 ajusté  
    "experience": 0.14,         # 14% - V2.0 ajusté
    "location": 0.09,           # 9% - V2.0 ajusté
    "motivations": 0.08,        # 8% - Nouveau V3.0
    "sector_compatibility": 0.06, # 6% - Nouveau V3.0
    "contract_flexibility": 0.05, # 5% - Nouveau V3.0
    "timing_compatibility": 0.04, # 4% - Nouveau V3.0
    "work_modality": 0.04,      # 4% - Nouveau V3.0
    "salary_progression": 0.03, # 3% - Nouveau V3.0
    "listening_reason": 0.02,   # 2% - Nouveau V3.0
    "candidate_status": 0.02    # 2% - Nouveau V3.0
}

# Vérification : sum = 1.00 ✅

# ================================
# MATRICES D'ADAPTATION CORRIGÉES
# ================================

ADAPTIVE_MATRICES_V3 = {
    
    # ✅ MATRICE OK - Totale: 1.000000
    ListeningReasonType.REMUNERATION_FAIBLE: {
        "salary": 0.32,                 # Boost +68% (19% → 32%)
        "salary_progression": 0.05,     # Boost +67% (3% → 5%)
        "semantic": 0.20,               # Réduit (24% → 20%)
        "experience": 0.13,             # Stable
        "location": 0.09,               # Stable
        "motivations": 0.07,            # Réduit
        "sector_compatibility": 0.05,   # Réduit
        "contract_flexibility": 0.04,   # Stable
        "timing_compatibility": 0.03,   # Stable
        "work_modality": 0.02,          # Réduit
        "listening_reason": 0.00,       # Impact systémique déjà appliqué
        "candidate_status": 0.00        # Impact systémique déjà appliqué
    },
    
    # 🔧 MATRICE CORRIGÉE - Était: 1.040000 → Maintenant: 1.000000 ✅
    ListeningReasonType.POSTE_INADEQUAT: {
        "semantic": 0.30,               # Boost +25% (24% → 30%) - Réduit de 35% pour corriger
        "sector_compatibility": 0.10,   # Boost +67% (6% → 10%)
        "motivations": 0.14,            # Boost modéré
        "salary": 0.16,                 # Légèrement réduit
        "experience": 0.12,             # Stable
        "location": 0.08,               # Stable
        "contract_flexibility": 0.04,   # Stable
        "timing_compatibility": 0.03,   # Stable
        "work_modality": 0.02,          # Réduit
        "salary_progression": 0.01,     # Minimal
        "listening_reason": 0.00,       # Impact systémique déjà appliqué
        "candidate_status": 0.00        # Impact systémique déjà appliqué
    },
    
    # 🔧 MATRICE CORRIGÉE - Était: 1.020000 → Maintenant: 1.000000 ✅
    ListeningReasonType.MANQUE_PERSPECTIVES: {
        "experience": 0.22,             # Boost +57% (14% → 22%) - Réduit de 25% pour corriger
        "motivations": 0.14,            # Boost +75% (8% → 14%)
        "semantic": 0.20,               # Léger boost
        "salary": 0.16,                 # Stable
        "sector_compatibility": 0.08,   # Boost
        "location": 0.08,               # Stable
        "salary_progression": 0.05,     # Boost
        "contract_flexibility": 0.03,   # Stable
        "timing_compatibility": 0.02,   # Réduit
        "work_modality": 0.02,          # Réduit
        "listening_reason": 0.00,       # Impact systémique déjà appliqué
        "candidate_status": 0.00        # Impact systémique déjà appliqué
    },
    
    # ✅ MATRICE LOCALISATION - Totale: 1.000000
    ListeningReasonType.LOCALISATION: {
        "location": 0.25,               # Boost majeur
        "work_modality": 0.08,          # Boost télétravail/hybrid
        "semantic": 0.20,               # Stable
        "salary": 0.16,                 # Légèrement réduit
        "experience": 0.12,             # Stable
        "motivations": 0.07,            # Réduit
        "sector_compatibility": 0.05,   # Réduit
        "contract_flexibility": 0.03,   # Réduit
        "timing_compatibility": 0.02,   # Réduit
        "salary_progression": 0.02,     # Minimal
        "listening_reason": 0.00,       # Impact systémique déjà appliqué
        "candidate_status": 0.00        # Impact systémique déjà appliqué
    },
    
    # ✅ MATRICE FLEXIBILITÉ - Totale: 1.000000
    ListeningReasonType.FLEXIBILITE: {
        "work_modality": 0.10,          # Boost majeur télétravail
        "contract_flexibility": 0.09,   # Boost freelance/CDD
        "timing_compatibility": 0.07,   # Boost disponibilité
        "semantic": 0.22,               # Légèrement réduit
        "salary": 0.16,                 # Réduit
        "location": 0.12,               # Stable
        "motivations": 0.10,            # Stable
        "experience": 0.11,             # Légèrement réduit
        "sector_compatibility": 0.03,   # Minimal
        "salary_progression": 0.00,     # Pas prioritaire
        "listening_reason": 0.00,       # Impact systémique déjà appliqué
        "candidate_status": 0.00        # Impact systémique déjà appliqué
    }
}

# ================================
# VALIDATION ET UTILITAIRES
# ================================

def validate_matrix_sum(matrix: Dict[str, float], matrix_name: str) -> bool:
    """Valide qu'une matrice totalise exactement 1.000000"""
    total = sum(matrix.values())
    is_valid = abs(total - 1.0) < 0.000001  # Tolérance float
    
    if not is_valid:
        print(f"❌ ERREUR {matrix_name}: Somme = {total:.6f} (attendu: 1.000000)")
    else:
        print(f"✅ OK {matrix_name}: Somme = {total:.6f}")
    
    return is_valid

def validate_all_matrices() -> Dict[str, bool]:
    """Valide toutes les matrices d'adaptation"""
    results = {}
    
    print("🧮 VALIDATION MATRICES V3.0")
    print("=" * 40)
    
    # Validation matrice de base
    base_valid = validate_matrix_sum(BASE_WEIGHTS_V3, "BASE_WEIGHTS")
    results["BASE_WEIGHTS"] = base_valid
    
    # Validation matrices adaptatives
    for reason_type, matrix in ADAPTIVE_MATRICES_V3.items():
        matrix_name = reason_type.value.upper()
        matrix_valid = validate_matrix_sum(matrix, matrix_name)
        results[matrix_name] = matrix_valid
    
    print("=" * 40)
    all_valid = all(results.values())
    status = "✅ TOUTES VALIDÉES" if all_valid else "❌ ERREURS DÉTECTÉES"
    print(f"RÉSULTAT GLOBAL: {status}")
    
    return results

def get_adaptive_weights(listening_reason: ListeningReasonType) -> Dict[str, float]:
    """Retourne les poids adaptatifs pour une raison d'écoute donnée"""
    
    if listening_reason in ADAPTIVE_MATRICES_V3:
        return ADAPTIVE_MATRICES_V3[listening_reason].copy()
    
    # Fallback sur poids de base si raison inconnue
    return BASE_WEIGHTS_V3.copy()

def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """Normalise des poids pour qu'ils totalisent exactement 1.0"""
    total = sum(weights.values())
    if total == 0:
        return weights
    
    return {key: value / total for key, value in weights.items()}

def get_boost_analysis(base_weights: Dict[str, float], 
                      adaptive_weights: Dict[str, float]) -> Dict[str, Dict[str, float]]:
    """Analyse les boosts appliqués par rapport aux poids de base"""
    
    analysis = {}
    for component in base_weights:
        base_weight = base_weights[component]
        adaptive_weight = adaptive_weights.get(component, 0)
        
        if base_weight > 0:
            boost_percentage = ((adaptive_weight - base_weight) / base_weight) * 100
        else:
            boost_percentage = 0 if adaptive_weight == 0 else float('inf')
        
        analysis[component] = {
            "base": base_weight,
            "adaptive": adaptive_weight,
            "boost_percentage": boost_percentage,
            "absolute_change": adaptive_weight - base_weight
        }
    
    return analysis

# ================================
# CLASSE PRINCIPALE
# ================================

@dataclass
class AdaptiveWeightingConfigV3:
    """Configuration pondération adaptative V3.0 - Matrices corrigées"""
    
    base_weights: Dict[str, float] = field(default_factory=lambda: BASE_WEIGHTS_V3.copy())
    adaptive_matrices: Dict[ListeningReasonType, Dict[str, float]] = field(
        default_factory=lambda: ADAPTIVE_MATRICES_V3.copy()
    )
    
    def __post_init__(self):
        """Validation automatique à l'initialisation"""
        self.validate_configuration()
    
    def validate_configuration(self) -> bool:
        """Valide l'ensemble de la configuration"""
        results = validate_all_matrices()
        return all(results.values())
    
    def get_weights_for_reason(self, reason: ListeningReasonType) -> Dict[str, float]:
        """Retourne les poids pour une raison d'écoute spécifique"""
        return get_adaptive_weights(reason)
    
    def analyze_impact(self, reason: ListeningReasonType) -> Dict[str, Dict[str, float]]:
        """Analyse l'impact d'une raison d'écoute sur les pondérations"""
        adaptive_weights = self.get_weights_for_reason(reason)
        return get_boost_analysis(self.base_weights, adaptive_weights)

# ================================
# TESTS ET DÉMONSTRATION
# ================================

if __name__ == "__main__":
    print("🚀 NEXTVISION V3.0 - Configuration Pondération Adaptative")
    print("=" * 60)
    
    # Test validation matrices
    validation_results = validate_all_matrices()
    
    # Test classe principale
    print("\n🧠 TEST CLASSE ADAPTATIVE")
    config = AdaptiveWeightingConfigV3()
    
    # Test raison problématique corrigée
    print("\n📊 ANALYSE POSTE_INADEQUAT (anciennement 1.040000)")
    reason = ListeningReasonType.POSTE_INADEQUAT
    weights = config.get_weights_for_reason(reason)
    total = sum(weights.values())
    print(f"Nouvelle somme: {total:.6f} ✅")
    
    # Analyse impact
    impact = config.analyze_impact(reason)
    print("\nPrincipaux boosts:")
    for component, data in impact.items():
        if data["boost_percentage"] > 10:
            print(f"  - {component}: +{data['boost_percentage']:.1f}% ({data['base']:.3f} → {data['adaptive']:.3f})")
    
    print("\n📊 ANALYSE MANQUE_PERSPECTIVES (anciennement 1.020000)")
    reason2 = ListeningReasonType.MANQUE_PERSPECTIVES
    weights2 = config.get_weights_for_reason(reason2)
    total2 = sum(weights2.values())
    print(f"Nouvelle somme: {total2:.6f} ✅")
    
    # Statut final
    print("\n" + "=" * 60)
    if all(validation_results.values()):
        print("🎯 SUCCÈS: Toutes les matrices totalisent 1.000000")
        print("🎯 PRÊT: Validation Pydantic OK")
        print("🎯 SCORE: 3/3 modèles V3.0 ✅")
    else:
        print("❌ ÉCHEC: Des matrices sont encore incorrectes")
    
    print("=" * 60)
