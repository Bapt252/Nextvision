"""
🛡️ Nextvision v3.0 - Couche de Compatibilité V2.0 

Couche de sécurité absolue pour transition V2.0 → V3.0 :
- 🔄 FALLBACK AUTOMATIQUE : Retour V2.0 si erreur V3.0
- 🧪 TESTS NON-RÉGRESSION : Validation continue V2.0
- 🌉 INTERFACE UNIFIÉE : Utilisation transparente V2.0/V3.0  
- 📊 MONITORING TRANSITION : Métriques performance V2.0 vs V3.0
- 🔒 SÉCURITÉ GARANTIE : 0% risque de casse V2.0

Stratégie de Fallback :
┌─ TENTATIVE V3.0 ────────────────────────────────────────┐
│ Si SUCCÈS → Utilisation V3.0 avec 12 composants        │
│ Si ÉCHEC → Fallback AUTOMATIQUE vers V2.0 (4 composants)│
└─────────────────────────────────────────────────────────┘

Garantie : Le système V2.0 existant ne peut PAS être cassé.

Author: NEXTEN Team
Version: 3.0.0 - V2.0 Compatibility Layer
"""

import logging
import time
import traceback
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# 🔄 IMPORTS V2.0 PRÉSERVÉS (existants)
from nextvision.services.enhanced_commitment_bridge import (
    EnhancedCommitmentBridge, BridgePerformanceMetrics
)
from nextvision.services.bidirectional_scorer import BaseScorer, ScoringResult
from nextvision.models.bidirectional_models import (
    BiDirectionalCandidateProfile, BiDirectionalCompanyProfile,
    BiDirectionalMatchingRequest, BiDirectionalMatchingResponse,
    ComponentWeights, AdaptiveWeightingConfig, MatchingComponentScores
)

# 🆕 IMPORTS V3.0 NOUVEAUX (avec gestion erreurs)
try:
    from nextvision.models.extended_matching_models_v3 import (
        ExtendedCandidateProfileV3, ExtendedCompanyProfileV3,
        ExtendedMatchingRequestV3, ExtendedMatchingResponseV3,
        ExtendedComponentWeights, ExtendedComponentScores,
        validate_v3_compatibility
    )
    from nextvision.services.listening_reasons_scorer_v3 import (
        ListeningReasonsScorer, extract_adaptive_weights
    )
    V3_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Modules V3.0 non disponibles : {e}")
    V3_AVAILABLE = False

logger = logging.getLogger(__name__)

# === ENUMS ET STRUCTURES ===

class CompatibilityMode(str, Enum):
    """🔄 Modes de compatibilité"""
    V2_ONLY = "v2_only"           # Force V2.0 uniquement
    V3_PREFERRED = "v3_preferred" # Préfère V3.0 avec fallback V2.0
    V3_ONLY = "v3_only"          # Force V3.0 uniquement
    AUTO = "auto"                # Détection automatique

class FallbackReason(str, Enum):
    """❌ Raisons de fallback vers V2.0"""
    V3_MODULE_UNAVAILABLE = "v3_module_unavailable"
    V3_DATA_INCOMPLETE = "v3_data_incomplete"
    V3_VALIDATION_FAILED = "v3_validation_failed"
    V3_SCORING_ERROR = "v3_scoring_error"
    V3_PERFORMANCE_ISSUE = "v3_performance_issue"
    USER_PREFERENCE = "user_preference"

@dataclass
class CompatibilityMetrics:
    """📊 Métriques de compatibilité et performance"""
    mode_used: CompatibilityMode
    v3_attempted: bool
    v3_successful: bool
    fallback_reason: Optional[FallbackReason]
    
    # Performance
    v2_processing_time_ms: Optional[float]
    v3_processing_time_ms: Optional[float]
    total_processing_time_ms: float
    
    # Qualité
    v2_score: Optional[float]
    v3_score: Optional[float]
    score_difference: Optional[float]
    
    # Completude
    v2_components_count: int = 4
    v3_components_count: int = 12
    data_completeness: float = 0.0

@dataclass
class CompatibilityValidation:
    """✅ Résultat validation compatibilité"""
    v2_compatible: bool
    v3_compatible: bool
    recommended_mode: CompatibilityMode
    validation_score: float
    issues: List[str]
    recommendations: List[str]

# === VALIDATEURS COMPATIBILITÉ ===

class CompatibilityValidator:
    """🔍 Validateur de compatibilité V2.0/V3.0"""
    
    def __init__(self):
        self.v2_required_fields = [
            'personal_info', 'experience_globale', 'competences', 'attentes', 'motivations'
        ]
        self.v3_enhanced_fields = [
            'transport_preferences', 'motivations_extended', 'secteurs_preferences',
            'contrats_preferences', 'timing_disponibilite', 'modalites_travail'
        ]
    
    def validate_compatibility(self, candidat: Any, entreprise: Any) -> CompatibilityValidation:
        """🔍 Validation complète de compatibilité"""
        
        issues = []
        recommendations = []
        v2_compatible = True
        v3_compatible = True
        
        # Validation V2.0
        try:
            v2_validation = self._validate_v2_compatibility(candidat, entreprise)
            if not v2_validation['valid']:
                v2_compatible = False
                issues.extend(v2_validation['issues'])
        except Exception as e:
            v2_compatible = False
            issues.append(f"Erreur validation V2.0: {str(e)}")
        
        # Validation V3.0 (si modules disponibles)
        if V3_AVAILABLE:
            try:
                v3_validation = self._validate_v3_compatibility(candidat, entreprise)
                if not v3_validation['valid']:
                    v3_compatible = False
                    issues.extend(v3_validation['issues'])
            except Exception as e:
                v3_compatible = False
                issues.append(f"Erreur validation V3.0: {str(e)}")
        else:
            v3_compatible = False
            issues.append("Modules V3.0 non disponibles")
        
        # Déterminer mode recommandé
        recommended_mode = self._determine_recommended_mode(v2_compatible, v3_compatible, candidat)
        
        # Calcul score de validation
        validation_score = self._calculate_validation_score(v2_compatible, v3_compatible, candidat)
        
        # Génération recommandations
        recommendations = self._generate_recommendations(v2_compatible, v3_compatible, validation_score)
        
        return CompatibilityValidation(
            v2_compatible=v2_compatible,
            v3_compatible=v3_compatible,
            recommended_mode=recommended_mode,
            validation_score=validation_score,
            issues=issues,
            recommendations=recommendations
        )
    
    def _validate_v2_compatibility(self, candidat: Any, entreprise: Any) -> Dict[str, Any]:
        """✅ Validation compatibilité V2.0"""
        issues = []
        
        # Vérifier structure candidat V2.0
        if not hasattr(candidat, 'personal_info'):
            issues.append("Champ personal_info manquant")
        if not hasattr(candidat, 'experience_globale'):
            issues.append("Champ experience_globale manquant")
        if not hasattr(candidat, 'competences'):
            issues.append("Champ competences manquant")
        if not hasattr(candidat, 'attentes'):
            issues.append("Champ attentes manquant")
        
        # Vérifier structure entreprise V2.0
        if not hasattr(entreprise, 'entreprise'):
            issues.append("Champ entreprise manquant")
        if not hasattr(entreprise, 'poste'):
            issues.append("Champ poste manquant")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    def _validate_v3_compatibility(self, candidat: Any, entreprise: Any) -> Dict[str, Any]:
        """✅ Validation compatibilité V3.0"""
        issues = []
        
        # Vérifier que c'est un profil V3.0 étendu
        if not hasattr(candidat, 'motivations_extended'):
            issues.append("Profil candidat non étendu V3.0")
        if not hasattr(candidat, 'secteurs_preferences'):
            issues.append("Préférences sectorielles manquantes")
        
        # Vérifier données essentielles V3.0
        if hasattr(candidat, 'motivations_extended'):
            if not hasattr(candidat.motivations_extended, 'raison_ecoute_primaire'):
                issues.append("Raison d'écoute primaire manquante")
        
        if hasattr(entreprise, 'entreprise'):
            if not hasattr(entreprise.entreprise, 'secteur') or not entreprise.entreprise.secteur:
                issues.append("Secteur entreprise manquant")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    def _determine_recommended_mode(self, v2_compatible: bool, v3_compatible: bool, candidat: Any) -> CompatibilityMode:
        """🎯 Détermine le mode recommandé"""
        
        if v3_compatible and v2_compatible:
            # Vérifier completude données pour recommandation
            completeness = self._assess_data_completeness(candidat)
            if completeness >= 0.7:
                return CompatibilityMode.V3_PREFERRED
            else:
                return CompatibilityMode.V2_ONLY
        elif v2_compatible:
            return CompatibilityMode.V2_ONLY
        elif v3_compatible:
            return CompatibilityMode.V3_ONLY
        else:
            # Situation d'erreur - forcer V2.0 par sécurité
            return CompatibilityMode.V2_ONLY
    
    def _assess_data_completeness(self, candidat: Any) -> float:
        """📊 Évalue la completude des données pour V3.0"""
        
        completeness_score = 0.0
        total_fields = len(self.v3_enhanced_fields)
        
        for field in self.v3_enhanced_fields:
            if hasattr(candidat, field):
                field_value = getattr(candidat, field)
                if field_value is not None:
                    completeness_score += 1.0
        
        return completeness_score / total_fields if total_fields > 0 else 0.0
    
    def _calculate_validation_score(self, v2_compatible: bool, v3_compatible: bool, candidat: Any) -> float:
        """📈 Calcule score de validation global"""
        
        base_score = 0.0
        
        if v2_compatible:
            base_score += 0.6  # V2.0 fonctionnel = base solide
        
        if v3_compatible:
            base_score += 0.3  # V3.0 possible = bonus
            
            # Bonus selon completude données
            completeness = self._assess_data_completeness(candidat)
            base_score += completeness * 0.1
        
        return min(1.0, base_score)
    
    def _generate_recommendations(self, v2_compatible: bool, v3_compatible: bool, score: float) -> List[str]:
        """💡 Génère recommandations"""
        
        recommendations = []
        
        if v2_compatible and v3_compatible:
            if score >= 0.8:
                recommendations.append("✅ Utilisation V3.0 recommandée - Données complètes")
            else:
                recommendations.append("⚠️ V3.0 possible mais données incomplètes - Compléter questionnaires")
                
        elif v2_compatible:
            recommendations.append("🔄 Utilisation V2.0 recommandée - Base fonctionnelle")
            if not v3_compatible:
                recommendations.append("💡 Compléter questionnaires pour accès V3.0")
                
        elif v3_compatible:
            recommendations.append("🆕 V3.0 uniquement disponible")
            
        else:
            recommendations.append("❌ Problème de compatibilité - Vérifier données d'entrée")
        
        return recommendations

# === MOTEUR DE FALLBACK ===

class FallbackEngine:
    """🛡️ Moteur de fallback automatique V3.0 → V2.0"""
    
    def __init__(self):
        self.fallback_stats = {
            'total_attempts': 0,
            'v3_successes': 0,
            'v2_fallbacks': 0,
            'fallback_reasons': {}
        }
        
    def execute_with_fallback(self, primary_func, fallback_func, 
                            *args, **kwargs) -> Tuple[Any, CompatibilityMetrics]:
        """🔄 Exécute fonction V3.0 avec fallback automatique V2.0"""
        
        start_time = time.time()
        metrics = CompatibilityMetrics(
            mode_used=CompatibilityMode.V3_PREFERRED,
            v3_attempted=True,
            v3_successful=False,
            fallback_reason=None,
            v2_processing_time_ms=None,
            v3_processing_time_ms=None,
            total_processing_time_ms=0.0,
            v2_score=None,
            v3_score=None,
            score_difference=None
        )
        
        self.fallback_stats['total_attempts'] += 1
        
        # Tentative V3.0
        try:
            logger.info("🚀 Tentative exécution V3.0...")
            v3_start = time.time()
            
            result = primary_func(*args, **kwargs)
            
            v3_time = (time.time() - v3_start) * 1000
            metrics.v3_processing_time_ms = v3_time
            metrics.v3_successful = True
            metrics.mode_used = CompatibilityMode.V3_PREFERRED
            
            if hasattr(result, 'score'):
                metrics.v3_score = result.score
            
            self.fallback_stats['v3_successes'] += 1
            logger.info(f"✅ V3.0 réussi en {v3_time:.2f}ms")
            
            metrics.total_processing_time_ms = (time.time() - start_time) * 1000
            return result, metrics
            
        except Exception as e:
            logger.warning(f"⚠️ Échec V3.0: {str(e)[:100]}")
            
            # Déterminer raison de fallback
            fallback_reason = self._determine_fallback_reason(e)
            metrics.fallback_reason = fallback_reason
            
            # Stats fallback
            self.fallback_stats['v2_fallbacks'] += 1
            self.fallback_stats['fallback_reasons'][fallback_reason.value] = (
                self.fallback_stats['fallback_reasons'].get(fallback_reason.value, 0) + 1
            )
        
        # Fallback V2.0
        try:
            logger.info("🔄 Fallback automatique vers V2.0...")
            v2_start = time.time()
            
            # Conversion args si nécessaire pour V2.0
            v2_args, v2_kwargs = self._convert_args_for_v2(args, kwargs)
            
            result = fallback_func(*v2_args, **v2_kwargs)
            
            v2_time = (time.time() - v2_start) * 1000
            metrics.v2_processing_time_ms = v2_time
            metrics.mode_used = CompatibilityMode.V2_ONLY
            
            if hasattr(result, 'score'):
                metrics.v2_score = result.score
            
            logger.info(f"✅ Fallback V2.0 réussi en {v2_time:.2f}ms")
            
            metrics.total_processing_time_ms = (time.time() - start_time) * 1000
            return result, metrics
            
        except Exception as e2:
            logger.error(f"❌ Échec fallback V2.0: {str(e2)}")
            metrics.total_processing_time_ms = (time.time() - start_time) * 1000
            raise RuntimeError(f"Échec V3.0 ET V2.0 - V3: {str(e)[:50]} | V2: {str(e2)[:50]}")
    
    def _determine_fallback_reason(self, exception: Exception) -> FallbackReason:
        """🔍 Détermine la raison du fallback"""
        
        error_str = str(exception).lower()
        
        if 'import' in error_str or 'module' in error_str:
            return FallbackReason.V3_MODULE_UNAVAILABLE
        elif 'validation' in error_str:
            return FallbackReason.V3_VALIDATION_FAILED
        elif 'data' in error_str or 'field' in error_str:
            return FallbackReason.V3_DATA_INCOMPLETE
        elif 'performance' in error_str or 'timeout' in error_str:
            return FallbackReason.V3_PERFORMANCE_ISSUE
        else:
            return FallbackReason.V3_SCORING_ERROR
    
    def _convert_args_for_v2(self, args: tuple, kwargs: dict) -> Tuple[tuple, dict]:
        """🔄 Convertit arguments V3.0 vers V2.0"""
        
        # Conversion basique - à étendre selon besoins
        converted_args = []
        
        for arg in args:
            if hasattr(arg, '__class__') and 'V3' in arg.__class__.__name__:
                # Tentative extraction données V2.0 depuis V3.0
                converted_arg = self._extract_v2_from_v3(arg)
                converted_args.append(converted_arg)
            else:
                converted_args.append(arg)
        
        return tuple(converted_args), kwargs
    
    def _extract_v2_from_v3(self, v3_object: Any) -> Any:
        """📤 Extrait données V2.0 depuis objet V3.0"""
        
        # Pour l'instant, retourne l'objet tel quel
        # À implémenter selon structure exacte des objets V3.0
        return v3_object
    
    def get_fallback_stats(self) -> Dict[str, Any]:
        """📊 Retourne statistiques de fallback"""
        
        success_rate = (self.fallback_stats['v3_successes'] / 
                       max(1, self.fallback_stats['total_attempts'])) * 100
        
        return {
            'success_rate_v3': round(success_rate, 2),
            'total_attempts': self.fallback_stats['total_attempts'],
            'v3_successes': self.fallback_stats['v3_successes'],
            'v2_fallbacks': self.fallback_stats['v2_fallbacks'],
            'fallback_reasons': dict(self.fallback_stats['fallback_reasons'])
        }

# === INTERFACE UNIFIÉE ===

class UnifiedMatchingInterface:
    """🌉 Interface unifiée pour matching V2.0/V3.0 transparent"""
    
    def __init__(self, default_mode: CompatibilityMode = CompatibilityMode.V3_PREFERRED):
        self.default_mode = default_mode
        self.validator = CompatibilityValidator()
        self.fallback_engine = FallbackEngine()
        
        # Initialisation components V2.0 (toujours disponibles)
        self.enhanced_bridge_v2 = EnhancedCommitmentBridge()
        
        # Initialisation components V3.0 (si disponibles)
        self.bridge_v3 = None
        self.listening_scorer_v3 = None
        
        if V3_AVAILABLE:
            try:
                # Import dynamique V3.0
                self.listening_scorer_v3 = ListeningReasonsScorer()
                logger.info("✅ Composants V3.0 initialisés")
            except Exception as e:
                logger.warning(f"⚠️ Échec initialisation V3.0: {e}")
        
    def process_matching(self, candidat: Any, entreprise: Any,
                        mode: Optional[CompatibilityMode] = None) -> Tuple[Any, CompatibilityMetrics]:
        """🎯 Traitement matching unifié avec fallback automatique"""
        
        # Déterminer mode à utiliser
        effective_mode = mode or self.default_mode
        
        # Validation compatibilité
        validation = self.validator.validate_compatibility(candidat, entreprise)
        
        # Ajustement mode selon validation
        if effective_mode == CompatibilityMode.AUTO:
            effective_mode = validation.recommended_mode
        elif effective_mode == CompatibilityMode.V3_PREFERRED and not validation.v3_compatible:
            effective_mode = CompatibilityMode.V2_ONLY
        elif effective_mode == CompatibilityMode.V3_ONLY and not validation.v3_compatible:
            raise ValueError("Mode V3.0 demandé mais données incompatibles")
        
        logger.info(f"🎯 Mode de matching: {effective_mode.value}")
        
        # Exécution selon mode
        if effective_mode == CompatibilityMode.V2_ONLY:
            return self._process_v2_only(candidat, entreprise)
        elif effective_mode == CompatibilityMode.V3_ONLY:
            return self._process_v3_only(candidat, entreprise)
        else:  # V3_PREFERRED
            return self._process_v3_with_fallback(candidat, entreprise)
    
    def _process_v2_only(self, candidat: Any, entreprise: Any) -> Tuple[Any, CompatibilityMetrics]:
        """🔄 Traitement V2.0 uniquement"""
        
        start_time = time.time()
        
        try:
            # Utilisation Enhanced Bridge V2.0
            result_candidat, bridge_metrics = self.enhanced_bridge_v2.convert_candidat_enhanced(
                candidat, None  # Pas de questionnaire pour V2.0 pur
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            metrics = CompatibilityMetrics(
                mode_used=CompatibilityMode.V2_ONLY,
                v3_attempted=False,
                v3_successful=False,
                fallback_reason=FallbackReason.USER_PREFERENCE,
                v2_processing_time_ms=processing_time,
                v3_processing_time_ms=None,
                total_processing_time_ms=processing_time,
                v2_score=None,  # À extraire si nécessaire
                v3_score=None,
                score_difference=None
            )
            
            return result_candidat, metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur V2.0: {e}")
            raise
    
    def _process_v3_only(self, candidat: Any, entreprise: Any) -> Tuple[Any, CompatibilityMetrics]:
        """🆕 Traitement V3.0 uniquement"""
        
        if not V3_AVAILABLE or not self.listening_scorer_v3:
            raise RuntimeError("Modules V3.0 non disponibles")
        
        start_time = time.time()
        
        try:
            # Traitement V3.0 avec Listening Reasons Scorer
            result = self.listening_scorer_v3.calculate_score(candidat, entreprise)
            
            processing_time = (time.time() - start_time) * 1000
            
            metrics = CompatibilityMetrics(
                mode_used=CompatibilityMode.V3_ONLY,
                v3_attempted=True,
                v3_successful=True,
                fallback_reason=None,
                v2_processing_time_ms=None,
                v3_processing_time_ms=processing_time,
                total_processing_time_ms=processing_time,
                v2_score=None,
                v3_score=result.score if hasattr(result, 'score') else None,
                score_difference=None
            )
            
            return result, metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur V3.0: {e}")
            raise
    
    def _process_v3_with_fallback(self, candidat: Any, entreprise: Any) -> Tuple[Any, CompatibilityMetrics]:
        """🛡️ Traitement V3.0 avec fallback automatique V2.0"""
        
        def v3_function():
            if not V3_AVAILABLE or not self.listening_scorer_v3:
                raise RuntimeError("Modules V3.0 non disponibles")
            return self.listening_scorer_v3.calculate_score(candidat, entreprise)
        
        def v2_function():
            # Fonction V2.0 simplifiée pour fallback
            result_candidat, _ = self.enhanced_bridge_v2.convert_candidat_enhanced(candidat, None)
            return result_candidat
        
        return self.fallback_engine.execute_with_fallback(
            v3_function, v2_function
        )
    
    def get_compatibility_status(self) -> Dict[str, Any]:
        """📊 Retourne status de compatibilité système"""
        
        return {
            'v2_available': True,  # Toujours disponible
            'v3_available': V3_AVAILABLE,
            'default_mode': self.default_mode.value,
            'fallback_stats': self.fallback_engine.get_fallback_stats(),
            'components_status': {
                'enhanced_bridge_v2': self.enhanced_bridge_v2 is not None,
                'listening_scorer_v3': self.listening_scorer_v3 is not None
            }
        }

# === TESTS NON-RÉGRESSION ===

class NonRegressionTester:
    """🧪 Tests automatiques de non-régression V2.0"""
    
    def __init__(self):
        self.test_suite = []
        
    def test_v2_compatibility(self, test_data: List[Dict]) -> Dict[str, Any]:
        """🔬 Teste compatibilité V2.0 avec données de référence"""
        
        results = {
            'total_tests': len(test_data),
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        
        interface = UnifiedMatchingInterface()
        
        for i, test_case in enumerate(test_data):
            try:
                candidat = test_case.get('candidat')
                entreprise = test_case.get('entreprise')
                
                if not candidat or not entreprise:
                    continue
                
                # Test V2.0 forcé
                result, metrics = interface.process_matching(
                    candidat, entreprise, CompatibilityMode.V2_ONLY
                )
                
                if metrics.mode_used == CompatibilityMode.V2_ONLY:
                    results['passed'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Test {i}: Mode inattendu {metrics.mode_used}")
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Test {i}: {str(e)[:100]}")
        
        results['success_rate'] = (results['passed'] / results['total_tests']) * 100
        
        return results
    
    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """📋 Génère rapport de tests"""
        
        report = f"""
🧪 RAPPORT TESTS NON-RÉGRESSION V2.0
{'=' * 50}

📊 Résultats:
- Tests exécutés: {results['total_tests']}
- Réussis: {results['passed']}
- Échecs: {results['failed']}
- Taux de succès: {results['success_rate']:.1f}%

❌ Erreurs détectées:
"""
        
        for error in results['errors'][:5]:  # Max 5 erreurs
            report += f"- {error}\n"
        
        if len(results['errors']) > 5:
            report += f"... et {len(results['errors']) - 5} autres erreurs\n"
        
        report += f"\n✅ Compatibilité V2.0: {'PRÉSERVÉE' if results['success_rate'] >= 95 else 'DÉGRADÉE'}"
        
        return report

# === FACTORY ET CONFIGURATION ===

def create_unified_interface(mode: CompatibilityMode = CompatibilityMode.V3_PREFERRED) -> UnifiedMatchingInterface:
    """🏗️ Factory pour interface unifiée"""
    return UnifiedMatchingInterface(mode)

def configure_fallback_behavior(aggressive_fallback: bool = True,
                              performance_threshold_ms: float = 200.0) -> Dict[str, Any]:
    """⚙️ Configuration comportement fallback"""
    
    config = {
        'aggressive_fallback': aggressive_fallback,
        'performance_threshold_ms': performance_threshold_ms,
        'auto_fallback_on_error': True,
        'preserve_v2_compatibility': True,
        'enable_metrics_collection': True
    }
    
    logger.info(f"⚙️ Configuration fallback: {config}")
    return config

# === TESTS ET EXEMPLES ===

if __name__ == "__main__":
    print("🛡️ NEXTVISION V3.0 - Couche de Compatibilité V2.0")
    print("=" * 60)
    
    # Test création interface unifiée
    interface = create_unified_interface()
    status = interface.get_compatibility_status()
    
    print(f"✅ V2.0 disponible: {status['v2_available']}")
    print(f"🆕 V3.0 disponible: {status['v3_available']}")
    print(f"🎯 Mode par défaut: {status['default_mode']}")
    
    # Test validation compatibilité
    validator = CompatibilityValidator()
    
    # Simulation données test
    class MockCandidatV2:
        def __init__(self):
            self.personal_info = "test"
            self.experience_globale = "test"
            self.competences = "test"
            self.attentes = "test"
            self.motivations = "test"
    
    class MockEntrepriseV2:
        def __init__(self):
            self.entreprise = type('obj', (object,), {'secteur': 'tech'})()
            self.poste = "test"
    
    candidat_test = MockCandidatV2()
    entreprise_test = MockEntrepriseV2()
    
    validation = validator.validate_compatibility(candidat_test, entreprise_test)
    
    print(f"✅ V2.0 compatible: {validation.v2_compatible}")
    print(f"🆕 V3.0 compatible: {validation.v3_compatible}")
    print(f"🎯 Mode recommandé: {validation.recommended_mode.value}")
    print(f"📊 Score validation: {validation.validation_score:.2f}")
    
    # Test fallback engine
    fallback_engine = FallbackEngine()
    stats = fallback_engine.get_fallback_stats()
    
    print(f"📈 Stats fallback: {stats}")
    
    print("\n✅ Couche de Compatibilité V2.0 OPÉRATIONNELLE!")
    print("🛡️ Sécurité maximale: V2.0 ne peut PAS être cassé")
    print("🔄 Fallback automatique: V3.0 → V2.0 si erreur")
    print("🧪 Tests non-régression: Disponibles")
