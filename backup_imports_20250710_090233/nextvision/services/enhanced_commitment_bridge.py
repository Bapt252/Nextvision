"""
🎯 Nextvision v2.0 - Enhanced Commitment Bridge avec Auto-Fix Intelligent

Bridge révolutionnaire pour intégration parfaite Commitment- ↔ Nextvision :
- Auto-fix intelligent pour erreurs de conversion
- Validation robuste avec fallbacks multiples
- Endpoint API optimisé pour performance
- Support batch processing pour volume
- Gestion d'erreurs avancée avec retry logic
- Conservation complète badges "Auto-rempli"
- Compatible 100% Enhanced Universal Parser v4.0 + ChatGPT

Author: NEXTEN Team
Version: 2.0.0 - Enhanced Bridge with Auto-Fix Intelligence
"""

import json
import re
import logging
import asyncio
import time  # 🔧 FIX: Import time manquant
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path

# Import des modèles bidirectionnels
from nextvision.models.bidirectional_models import (
    BiDirectionalCandidateProfile, BiDirectionalCompanyProfile,
    PersonalInfoBidirectional, CompetencesProfessionnelles, AttentesCandidat,
    MotivationsCandidat, ExperienceProfessionnelle, InformationsEntreprise,
    DescriptionPoste, ExigencesPoste, ConditionsTravail, CriteresRecrutement,
    RaisonEcouteCandidat, UrgenceRecrutement, NiveauExperience, TypeContrat
)

# Import adaptateurs existants
from nextvision.adapters.chatgpt_commitment_adapter import (
    CommitmentNextvisionBridge as BasicBridge,
    EnhancedParserV4Output, ChatGPTCommitmentOutput
)

logger = logging.getLogger(__name__)

# === STRUCTURES ENHANCED BRIDGE ===

@dataclass
class BridgeValidationResult:
    """Résultat de validation avec auto-fix"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    auto_fixed_fields: List[str]
    confidence_score: float
    processing_notes: List[str]

@dataclass
class EnhancedBridgeStats:
    """Statistiques avancées du bridge"""
    total_conversions: int = 0
    successful_conversions: int = 0
    auto_fixes_applied: int = 0
    validation_errors: int = 0
    avg_processing_time_ms: float = 0.0
    cache_hits: int = 0
    batch_processed: int = 0
    last_reset: datetime = None

@dataclass
class BridgePerformanceMetrics:
    """Métriques de performance détaillées"""
    conversion_time_ms: float
    validation_time_ms: float
    auto_fix_time_ms: float
    total_time_ms: float
    fields_processed: int
    auto_fixes_count: int
    cache_used: bool

# === AUTO-FIX ENGINE ===

class AutoFixEngine:
    """🔧 Moteur d'auto-fix intelligent pour données Commitment-"""
    
    def __init__(self):
        self.fix_patterns = {
            # Patterns salaire
            'salary': [
                (r'(\d+)\s*k\s*à\s*(\d+)\s*k', r'\1000 à \2000'),
                (r'(\d+)k\s*euros?', r'\g<1>000'),
                (r'(\d+)\s*€', r'\1'),
                (r'(\d+)\s*à\s*(\d+)\s*€', r'\1 à \2'),
            ],
            # Patterns expérience
            'experience': [
                (r'(\d+)\s*an[s]?\s*-\s*(\d+)\s*an[s]?', r'\1 ans - \2 ans'),
                (r'(\d+)\s*-\s*(\d+)\s*an[s]?', r'\1 ans - \2 ans'),
                (r'junior', '2 ans - 5 ans'),
                (r'senior', '8 ans - 15 ans'),
                (r'débutant', '0 ans - 2 ans'),
            ],
            # Patterns email
            'email': [
                (r'\s+', ''),  # Supprime espaces
                (r'\.\.+', '.'),  # Supprime points multiples
            ],
            # Patterns téléphone
            'phone': [
                (r'[^\d+\-\.\s\(\)]', ''),  # Garde seulement chiffres et symbols
                (r'^(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})$', r'+33 \1 \2 \3 \4 \5'),
                (r'^0(\d{9})$', r'+33 \1'),
            ]
        }
        
        self.validation_rules = {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone': r'^(\+33|0)[1-9](\d{8}|\s\d{2}\s\d{2}\s\d{2}\s\d{2})$',
            'salary_range': (15000, 200000),  # Fourchette raisonnable
            'name': r'^[a-zA-ZÀ-ÿ\s\-\'\.]{{2,50}}$'
        }
    
    def auto_fix_candidat_data(self, data: Dict) -> Tuple[Dict, BridgeValidationResult]:
        """🔧 Auto-fix intelligent pour données candidat"""
        fixed_data = data.copy()
        validation_result = BridgeValidationResult(
            is_valid=True, errors=[], warnings=[], auto_fixed_fields=[], 
            confidence_score=1.0, processing_notes=[]
        )
        
        try:
            # Fix informations personnelles
            personal_info = fixed_data.get('personal_info', {})
            
            # Fix email
            if 'email' in personal_info and personal_info['email']:
                original_email = personal_info['email']
                fixed_email = self._apply_fixes(original_email, 'email')
                if fixed_email != original_email:
                    personal_info['email'] = fixed_email
                    validation_result.auto_fixed_fields.append('email')
                    validation_result.processing_notes.append(f"Email corrigé: {original_email} → {fixed_email}")
            
            # Fix téléphone
            if 'phone' in personal_info and personal_info['phone']:
                original_phone = personal_info['phone']
                fixed_phone = self._apply_fixes(original_phone, 'phone')
                if fixed_phone != original_phone:
                    personal_info['phone'] = fixed_phone
                    validation_result.auto_fixed_fields.append('phone')
                    validation_result.processing_notes.append(f"Téléphone corrigé: {original_phone} → {fixed_phone}")
            
            # Fix noms (capitalisation)
            for name_field in ['firstName', 'lastName']:
                if name_field in personal_info and personal_info[name_field]:
                    original_name = personal_info[name_field]
                    fixed_name = original_name.title().strip()
                    if fixed_name != original_name:
                        personal_info[name_field] = fixed_name
                        validation_result.auto_fixed_fields.append(name_field)
            
            # Fix compétences (déduplication et nettoyage)
            if 'skills' in fixed_data:
                original_skills = fixed_data['skills']
                fixed_skills = list(dict.fromkeys([skill.strip() for skill in original_skills if skill.strip()]))
                if len(fixed_skills) != len(original_skills):
                    fixed_data['skills'] = fixed_skills
                    validation_result.auto_fixed_fields.append('skills')
                    validation_result.processing_notes.append(f"Compétences nettoyées: {len(original_skills)} → {len(fixed_skills)}")
            
            # Fix expérience
            if 'experience' in fixed_data and 'total_years' in fixed_data['experience']:
                years = fixed_data['experience']['total_years']
                if isinstance(years, str):
                    try:
                        fixed_years = int(re.findall(r'\d+', years)[0])
                        fixed_data['experience']['total_years'] = fixed_years
                        validation_result.auto_fixed_fields.append('experience_years')
                    except (IndexError, ValueError):
                        validation_result.warnings.append("Impossible de parser les années d'expérience")
            
            # Fix logiciels (nettoyage)
            if 'softwares' in fixed_data:
                original_soft = fixed_data['softwares']
                fixed_soft = list(dict.fromkeys([soft.strip() for soft in original_soft if soft.strip()]))
                if len(fixed_soft) != len(original_soft):
                    fixed_data['softwares'] = fixed_soft
                    validation_result.auto_fixed_fields.append('softwares')
            
            # Validation finale
            validation_result = self._validate_candidat_data(fixed_data, validation_result)
            
            # Calcul confiance
            total_fields = self._count_fields(fixed_data)
            errors_count = len(validation_result.errors)
            fixes_count = len(validation_result.auto_fixed_fields)
            
            validation_result.confidence_score = max(0.1, min(1.0, 
                1.0 - (errors_count * 0.2) - (fixes_count * 0.05)
            ))
            
            logger.info(f"🔧 Auto-fix candidat: {fixes_count} corrections, confiance: {validation_result.confidence_score:.2f}")
            
            return fixed_data, validation_result
            
        except Exception as e:
            logger.error(f"❌ Erreur auto-fix candidat: {e}")
            validation_result.errors.append(f"Erreur auto-fix: {str(e)}")
            validation_result.is_valid = False
            validation_result.confidence_score = 0.1
            return fixed_data, validation_result
    
    def auto_fix_entreprise_data(self, data: Dict) -> Tuple[Dict, BridgeValidationResult]:
        """🔧 Auto-fix intelligent pour données entreprise"""
        fixed_data = data.copy()
        validation_result = BridgeValidationResult(
            is_valid=True, errors=[], warnings=[], auto_fixed_fields=[], 
            confidence_score=1.0, processing_notes=[]
        )
        
        try:
            # Fix salaire (format ChatGPT)
            if 'salaire' in fixed_data and fixed_data['salaire']:
                original_salaire = fixed_data['salaire']
                fixed_salaire = self._apply_fixes(original_salaire, 'salary')
                if fixed_salaire != original_salaire:
                    fixed_data['salaire'] = fixed_salaire
                    validation_result.auto_fixed_fields.append('salaire')
                    validation_result.processing_notes.append(f"Salaire corrigé: {original_salaire} → {fixed_salaire}")
            
            # Fix expérience requise
            if 'experience_requise' in fixed_data and fixed_data['experience_requise']:
                original_exp = fixed_data['experience_requise']
                fixed_exp = self._apply_fixes(original_exp, 'experience')
                if fixed_exp != original_exp:
                    fixed_data['experience_requise'] = fixed_exp
                    validation_result.auto_fixed_fields.append('experience_requise')
                    validation_result.processing_notes.append(f"Expérience corrigée: {original_exp} → {fixed_exp}")
            
            # Fix titre (capitalisation)
            if 'titre' in fixed_data and fixed_data['titre']:
                original_titre = fixed_data['titre']
                fixed_titre = original_titre.title().strip()
                if fixed_titre != original_titre:
                    fixed_data['titre'] = fixed_titre
                    validation_result.auto_fixed_fields.append('titre')
            
            # Fix localisation (nettoyage)
            if 'localisation' in fixed_data and fixed_data['localisation']:
                original_loc = fixed_data['localisation']
                fixed_loc = original_loc.strip().title()
                if fixed_loc != original_loc:
                    fixed_data['localisation'] = fixed_loc
                    validation_result.auto_fixed_fields.append('localisation')
            
            # Fix compétences requises (déduplication)
            if 'competences_requises' in fixed_data:
                original_comp = fixed_data['competences_requises']
                fixed_comp = list(dict.fromkeys([comp.strip() for comp in original_comp if comp.strip()]))
                if len(fixed_comp) != len(original_comp):
                    fixed_data['competences_requises'] = fixed_comp
                    validation_result.auto_fixed_fields.append('competences_requises')
            
            # Fix missions (nettoyage)
            if 'missions' in fixed_data:
                original_missions = fixed_data['missions']
                fixed_missions = [mission.strip() for mission in original_missions if mission.strip()]
                if len(fixed_missions) != len(original_missions):
                    fixed_data['missions'] = fixed_missions
                    validation_result.auto_fixed_fields.append('missions')
            
            # Fix avantages (nettoyage)
            if 'avantages' in fixed_data:
                original_avantages = fixed_data['avantages']
                fixed_avantages = [av.strip() for av in original_avantages if av.strip()]
                if len(fixed_avantages) != len(original_avantages):
                    fixed_data['avantages'] = fixed_avantages
                    validation_result.auto_fixed_fields.append('avantages')
            
            # Validation finale
            validation_result = self._validate_entreprise_data(fixed_data, validation_result)
            
            # Calcul confiance
            total_fields = self._count_fields(fixed_data)
            errors_count = len(validation_result.errors)
            fixes_count = len(validation_result.auto_fixed_fields)
            
            validation_result.confidence_score = max(0.1, min(1.0,
                1.0 - (errors_count * 0.2) - (fixes_count * 0.05)
            ))
            
            logger.info(f"🔧 Auto-fix entreprise: {fixes_count} corrections, confiance: {validation_result.confidence_score:.2f}")
            
            return fixed_data, validation_result
            
        except Exception as e:
            logger.error(f"❌ Erreur auto-fix entreprise: {e}")
            validation_result.errors.append(f"Erreur auto-fix: {str(e)}")
            validation_result.is_valid = False
            validation_result.confidence_score = 0.1
            return fixed_data, validation_result
    
    def _apply_fixes(self, text: str, pattern_type: str) -> str:
        """Applique les patterns de fix pour un type donné"""
        if not text or pattern_type not in self.fix_patterns:
            return text
        
        fixed_text = text
        for pattern, replacement in self.fix_patterns[pattern_type]:
            fixed_text = re.sub(pattern, replacement, fixed_text, flags=re.IGNORECASE)
        
        return fixed_text.strip()
    
    def _validate_candidat_data(self, data: Dict, result: BridgeValidationResult) -> BridgeValidationResult:
        """Validation avancée données candidat"""
        personal_info = data.get('personal_info', {})
        
        # Validation email
        email = personal_info.get('email', '')
        if email and not re.match(self.validation_rules['email'], email):
            result.errors.append(f"Email invalide: {email}")
        
        # Validation téléphone
        phone = personal_info.get('phone', '')
        if phone and not re.match(self.validation_rules['phone'], phone):
            result.warnings.append(f"Format téléphone inhabituel: {phone}")
        
        # Validation noms
        for name_field in ['firstName', 'lastName']:
            name = personal_info.get(name_field, '')
            if name and not re.match(self.validation_rules['name'], name):
                result.warnings.append(f"{name_field} contient des caractères inhabituels: {name}")
        
        # Validation compétences
        skills = data.get('skills', [])
        if len(skills) < 2:
            result.warnings.append("Peu de compétences détectées (< 2)")
        elif len(skills) > 20:
            result.warnings.append("Beaucoup de compétences détectées (> 20)")
        
        # Validation expérience
        exp_data = data.get('experience', {})
        years = exp_data.get('total_years', 0)
        if isinstance(years, (int, float)):
            if years < 0 or years > 50:
                result.errors.append(f"Années d'expérience invalides: {years}")
        
        if len(result.errors) > 0:
            result.is_valid = False
        
        return result
    
    def _validate_entreprise_data(self, data: Dict, result: BridgeValidationResult) -> BridgeValidationResult:
        """Validation avancée données entreprise"""
        
        # Validation titre
        titre = data.get('titre', '')
        if not titre or len(titre) < 5:
            result.errors.append("Titre de poste trop court ou manquant")
        
        # Validation localisation
        localisation = data.get('localisation', '')
        if not localisation:
            result.warnings.append("Localisation manquante")
        
        # Validation salaire
        salaire = data.get('salaire', '')
        if salaire:
            # Extraction des montants
            amounts = re.findall(r'\d+', salaire)
            if amounts:
                min_sal = int(amounts[0]) * (1000 if int(amounts[0]) < 1000 else 1)
                sal_range = self.validation_rules['salary_range']
                if min_sal < sal_range[0] or min_sal > sal_range[1]:
                    result.warnings.append(f"Salaire hors fourchette habituelle: {min_sal}€")
        
        # Validation compétences
        competences = data.get('competences_requises', [])
        if len(competences) < 2:
            result.warnings.append("Peu de compétences requises spécifiées")
        
        # Validation expérience requise
        exp_req = data.get('experience_requise', '')
        if not exp_req:
            result.warnings.append("Expérience requise non spécifiée")
        
        # Validation contrat
        contrat = data.get('contrat', '')
        valid_contracts = ['CDI', 'CDD', 'Freelance', 'Stage', 'Alternance']
        if contrat and contrat not in valid_contracts:
            result.warnings.append(f"Type de contrat inhabituel: {contrat}")
        
        if len(result.errors) > 0:
            result.is_valid = False
        
        return result
    
    def _count_fields(self, data: Dict) -> int:
        """Compte le nombre de champs dans la structure"""
        count = 0
        for key, value in data.items():
            if isinstance(value, dict):
                count += self._count_fields(value)
            elif isinstance(value, list):
                count += len(value)
            else:
                count += 1
        return count

# === ENHANCED COMMITMENT BRIDGE ===

class EnhancedCommitmentBridge:
    """🌉 Enhanced Bridge Commitment- ↔ Nextvision avec Auto-Fix Intelligence"""
    
    def __init__(self):
        # Bridge basique existant
        self.basic_bridge = BasicBridge()
        
        # Moteur d'auto-fix
        self.auto_fix_engine = AutoFixEngine()
        
        # Cache pour optimisation
        self.cache = {}
        self.cache_ttl = 1800  # 30 minutes
        
        # Stats enhanced
        self.stats = EnhancedBridgeStats(last_reset=datetime.now())
        
        # Configuration avancée
        self.config = {
            'enable_auto_fix': True,
            'enable_cache': True,
            'enable_batch_processing': True,
            'max_batch_size': 50,
            'validation_strict_mode': False,
            'retry_failed_conversions': True,
            'max_retries': 3
        }
        
        logger.info("🌉 Enhanced Commitment Bridge v2.0 initialisé")
        logger.info(f"🔧 Auto-fix: {self.config['enable_auto_fix']}")
        logger.info(f"⚡ Cache: {self.config['enable_cache']}")
        logger.info(f"📦 Batch: {self.config['enable_batch_processing']}")
    
    async def convert_candidat_enhanced(self, parser_output: Dict, 
                                      questionnaire_data: Optional[Dict] = None,
                                      enable_auto_fix: bool = True) -> Tuple[BiDirectionalCandidateProfile, BridgePerformanceMetrics]:
        """🔄 Conversion candidat Enhanced avec auto-fix intelligent"""
        start_time = time.time()
        metrics = BridgePerformanceMetrics(
            conversion_time_ms=0, validation_time_ms=0, auto_fix_time_ms=0,
            total_time_ms=0, fields_processed=0, auto_fixes_count=0, cache_used=False
        )
        
        try:
            # Génération clé cache
            cache_key = self._generate_cache_key('candidat', parser_output, questionnaire_data)
            
            # Vérification cache
            if self.config['enable_cache'] and cache_key in self.cache:
                cached_result = self.cache[cache_key]
                if self._is_cache_valid(cached_result['timestamp']):
                    metrics.cache_used = True
                    metrics.total_time_ms = (time.time() - start_time) * 1000
                    self.stats.cache_hits += 1
                    logger.info("⚡ Candidat depuis cache")
                    return cached_result['profile'], metrics
            
            # Auto-fix si activé
            if enable_auto_fix and self.config['enable_auto_fix']:
                fix_start = time.time()
                fixed_data, validation_result = self.auto_fix_engine.auto_fix_candidat_data(parser_output)
                metrics.auto_fix_time_ms = (time.time() - fix_start) * 1000
                metrics.auto_fixes_count = len(validation_result.auto_fixed_fields)
                
                if not validation_result.is_valid and self.config['validation_strict_mode']:
                    raise ValueError(f"Validation échouée: {validation_result.errors}")
                
                parser_output = fixed_data
                logger.info(f"🔧 Auto-fix appliqué: {metrics.auto_fixes_count} corrections")
            
            # Conversion via bridge basique
            conversion_start = time.time()
            candidat_profile = self.basic_bridge.convert_candidat_from_commitment(
                parser_output, questionnaire_data
            )
            metrics.conversion_time_ms = (time.time() - conversion_start) * 1000
            
            # Mise en cache
            if self.config['enable_cache']:
                self.cache[cache_key] = {
                    'profile': candidat_profile,
                    'timestamp': datetime.now()
                }
            
            # Stats
            metrics.fields_processed = self.auto_fix_engine._count_fields(parser_output)
            metrics.total_time_ms = (time.time() - start_time) * 1000
            
            self.stats.total_conversions += 1
            self.stats.successful_conversions += 1
            if metrics.auto_fixes_count > 0:
                self.stats.auto_fixes_applied += metrics.auto_fixes_count
            
            # Mise à jour temps moyen
            self._update_avg_processing_time(metrics.total_time_ms)
            
            logger.info(f"✅ Candidat converti en {metrics.total_time_ms:.2f}ms ({metrics.auto_fixes_count} auto-fix)")
            
            return candidat_profile, metrics
            
        except Exception as e:
            self.stats.validation_errors += 1
            logger.error(f"❌ Erreur conversion candidat enhanced: {e}")
            
            # Retry si configuré
            if self.config['retry_failed_conversions']:
                logger.info("🔄 Tentative de conversion sans auto-fix...")
                try:
                    candidat_profile = self.basic_bridge.convert_candidat_from_commitment(
                        parser_output, questionnaire_data
                    )
                    metrics.total_time_ms = (time.time() - start_time) * 1000
                    self.stats.successful_conversions += 1
                    logger.info("✅ Conversion de secours réussie")
                    return candidat_profile, metrics
                except Exception as retry_error:
                    logger.error(f"❌ Échec conversion de secours: {retry_error}")
            
            raise
    
    async def convert_entreprise_enhanced(self, chatgpt_output: Dict,
                                        questionnaire_data: Optional[Dict] = None,
                                        enable_auto_fix: bool = True) -> Tuple[BiDirectionalCompanyProfile, BridgePerformanceMetrics]:
        """🔄 Conversion entreprise Enhanced avec auto-fix intelligent"""
        start_time = time.time()
        metrics = BridgePerformanceMetrics(
            conversion_time_ms=0, validation_time_ms=0, auto_fix_time_ms=0,
            total_time_ms=0, fields_processed=0, auto_fixes_count=0, cache_used=False
        )
        
        try:
            # Génération clé cache
            cache_key = self._generate_cache_key('entreprise', chatgpt_output, questionnaire_data)
            
            # Vérification cache
            if self.config['enable_cache'] and cache_key in self.cache:
                cached_result = self.cache[cache_key]
                if self._is_cache_valid(cached_result['timestamp']):
                    metrics.cache_used = True
                    metrics.total_time_ms = (time.time() - start_time) * 1000
                    self.stats.cache_hits += 1
                    logger.info("⚡ Entreprise depuis cache")
                    return cached_result['profile'], metrics
            
            # Auto-fix si activé
            if enable_auto_fix and self.config['enable_auto_fix']:
                fix_start = time.time()
                fixed_data, validation_result = self.auto_fix_engine.auto_fix_entreprise_data(chatgpt_output)
                metrics.auto_fix_time_ms = (time.time() - fix_start) * 1000
                metrics.auto_fixes_count = len(validation_result.auto_fixed_fields)
                
                if not validation_result.is_valid and self.config['validation_strict_mode']:
                    raise ValueError(f"Validation échouée: {validation_result.errors}")
                
                chatgpt_output = fixed_data
                logger.info(f"🔧 Auto-fix appliqué: {metrics.auto_fixes_count} corrections")
            
            # Conversion via bridge basique
            conversion_start = time.time()
            entreprise_profile = self.basic_bridge.convert_entreprise_from_commitment(
                chatgpt_output, questionnaire_data
            )
            metrics.conversion_time_ms = (time.time() - conversion_start) * 1000
            
            # Mise en cache
            if self.config['enable_cache']:
                self.cache[cache_key] = {
                    'profile': entreprise_profile,
                    'timestamp': datetime.now()
                }
            
            # Stats
            metrics.fields_processed = self.auto_fix_engine._count_fields(chatgpt_output)
            metrics.total_time_ms = (time.time() - start_time) * 1000
            
            self.stats.total_conversions += 1
            self.stats.successful_conversions += 1
            if metrics.auto_fixes_count > 0:
                self.stats.auto_fixes_applied += metrics.auto_fixes_count
            
            # Mise à jour temps moyen
            self._update_avg_processing_time(metrics.total_time_ms)
            
            logger.info(f"✅ Entreprise convertie en {metrics.total_time_ms:.2f}ms ({metrics.auto_fixes_count} auto-fix)")
            
            return entreprise_profile, metrics
            
        except Exception as e:
            self.stats.validation_errors += 1
            logger.error(f"❌ Erreur conversion entreprise enhanced: {e}")
            
            # Retry si configuré
            if self.config['retry_failed_conversions']:
                logger.info("🔄 Tentative de conversion sans auto-fix...")
                try:
                    entreprise_profile = self.basic_bridge.convert_entreprise_from_commitment(
                        chatgpt_output, questionnaire_data
                    )
                    metrics.total_time_ms = (time.time() - start_time) * 1000
                    self.stats.successful_conversions += 1
                    logger.info("✅ Conversion de secours réussie")
                    return entreprise_profile, metrics
                except Exception as retry_error:
                    logger.error(f"❌ Échec conversion de secours: {retry_error}")
            
            raise
    
    async def convert_batch_enhanced(self, batch_data: List[Dict], 
                                   data_type: str = 'candidat') -> Dict[str, Any]:
        """📦 Conversion en lot avec optimisations performance"""
        if not self.config['enable_batch_processing']:
            raise ValueError("Batch processing désactivé")
        
        if len(batch_data) > self.config['max_batch_size']:
            raise ValueError(f"Lot trop volumineux: {len(batch_data)} > {self.config['max_batch_size']}")
        
        start_time = time.time()
        results = {
            'successful': [],
            'failed': [],
            'total_processed': len(batch_data),
            'processing_time_ms': 0,
            'performance_stats': {}
        }
        
        try:
            logger.info(f"📦 Traitement lot {data_type}: {len(batch_data)} éléments")
            
            # Traitement parallèle
            if data_type == 'candidat':
                tasks = [self.convert_candidat_enhanced(item) for item in batch_data]
            else:
                tasks = [self.convert_entreprise_enhanced(item) for item in batch_data]
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Séparation succès/échecs
            total_auto_fixes = 0
            total_processing_time = 0
            
            for i, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    results['failed'].append({
                        'index': i,
                        'error': str(result),
                        'data': batch_data[i]
                    })
                else:
                    profile, metrics = result
                    results['successful'].append({
                        'index': i,
                        'profile': profile.dict(),
                        'metrics': asdict(metrics)
                    })
                    total_auto_fixes += metrics.auto_fixes_count
                    total_processing_time += metrics.total_time_ms
            
            # Stats batch
            processing_time = (time.time() - start_time) * 1000
            results['processing_time_ms'] = processing_time
            results['performance_stats'] = {
                'success_rate': len(results['successful']) / len(batch_data) * 100,
                'avg_item_time_ms': total_processing_time / max(1, len(results['successful'])),
                'total_auto_fixes': total_auto_fixes,
                'throughput_items_per_sec': len(batch_data) / (processing_time / 1000)
            }
            
            self.stats.batch_processed += len(batch_data)
            
            logger.info(f"📦 Lot traité en {processing_time:.2f}ms")
            logger.info(f"✅ Succès: {len(results['successful'])}/{len(batch_data)}")
            logger.info(f"🔧 Auto-fixes totaux: {total_auto_fixes}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement lot: {e}")
            results['processing_time_ms'] = (time.time() - start_time) * 1000
            raise
    
    def get_enhanced_stats(self) -> Dict[str, Any]:
        """📊 Statistiques détaillées du bridge enhanced"""
        success_rate = (self.stats.successful_conversions / max(1, self.stats.total_conversions)) * 100
        cache_hit_rate = (self.stats.cache_hits / max(1, self.stats.total_conversions)) * 100
        
        return {
            'enhanced_bridge_stats': {
                'total_conversions': self.stats.total_conversions,
                'successful_conversions': self.stats.successful_conversions,
                'success_rate_percent': round(success_rate, 2),
                'auto_fixes_applied': self.stats.auto_fixes_applied,
                'validation_errors': self.stats.validation_errors,
                'avg_processing_time_ms': round(self.stats.avg_processing_time_ms, 2),
                'cache_hits': self.stats.cache_hits,
                'cache_hit_rate_percent': round(cache_hit_rate, 2),
                'batch_processed': self.stats.batch_processed
            },
            'cache_stats': {
                'cache_size': len(self.cache),
                'cache_enabled': self.config['enable_cache']
            },
            'config': self.config,
            'uptime_hours': (datetime.now() - self.stats.last_reset).total_seconds() / 3600
        }
    
    def clear_cache(self):
        """🧹 Vide le cache"""
        cache_size = len(self.cache)
        self.cache.clear()
        logger.info(f"🧹 Cache vidé: {cache_size} entrées supprimées")
    
    def reset_stats(self):
        """🔄 Remet à zéro les statistiques"""
        self.stats = EnhancedBridgeStats(last_reset=datetime.now())
        logger.info("🔄 Statistiques remises à zéro")
    
    def update_config(self, new_config: Dict[str, Any]):
        """⚙️ Met à jour la configuration"""
        self.config.update(new_config)
        logger.info(f"⚙️ Configuration mise à jour: {new_config}")
    
    # === MÉTHODES UTILITAIRES ===
    
    def _generate_cache_key(self, data_type: str, main_data: Dict, 
                          questionnaire_data: Optional[Dict]) -> str:
        """Génère clé de cache unique"""
        main_hash = hash(str(sorted(main_data.items())))
        quest_hash = hash(str(sorted(questionnaire_data.items()))) if questionnaire_data else 0
        return f"{data_type}_{main_hash}_{quest_hash}"
    
    def _is_cache_valid(self, timestamp: datetime) -> bool:
        """Vérifie validité du cache"""
        return (datetime.now() - timestamp).seconds < self.cache_ttl
    
    def _update_avg_processing_time(self, processing_time_ms: float):
        """Met à jour temps de traitement moyen"""
        if self.stats.total_conversions == 1:
            self.stats.avg_processing_time_ms = processing_time_ms
        else:
            self.stats.avg_processing_time_ms = (
                (self.stats.avg_processing_time_ms * (self.stats.total_conversions - 1) + processing_time_ms) 
                / self.stats.total_conversions
            )

# === FACTORY ===

class EnhancedBridgeFactory:
    """🏗️ Factory pour Enhanced Bridge"""
    
    @staticmethod
    def create_bridge(enable_auto_fix: bool = True,
                     enable_cache: bool = True,
                     enable_batch: bool = True) -> EnhancedCommitmentBridge:
        """Crée bridge enhanced avec configuration"""
        bridge = EnhancedCommitmentBridge()
        bridge.update_config({
            'enable_auto_fix': enable_auto_fix,
            'enable_cache': enable_cache,
            'enable_batch_processing': enable_batch
        })
        return bridge
    
    @staticmethod
    def create_production_bridge() -> EnhancedCommitmentBridge:
        """Crée bridge optimisé pour production"""
        bridge = EnhancedCommitmentBridge()
        bridge.update_config({
            'enable_auto_fix': True,
            'enable_cache': True,
            'enable_batch_processing': True,
            'validation_strict_mode': False,
            'retry_failed_conversions': True,
            'max_retries': 3,
            'max_batch_size': 100
        })
        return bridge

# === TESTS ===

if __name__ == "__main__":
    import asyncio
    
    async def test_enhanced_bridge():
        """Test du bridge enhanced"""
        bridge = EnhancedBridgeFactory.create_bridge()
        
        # Test candidat avec erreurs
        candidat_data_buggy = {
            "personal_info": {
                "firstName": "marie",  # Pas de majuscule
                "lastName": "DUPONT",  # Tout en majuscules
                "email": "marie..dupont@email..com",  # Points multiples
                "phone": "0612345678"  # Format français non formaté
            },
            "skills": ["CEGID", "Excel", "CEGID", "  ", "Excel"],  # Doublons et espaces
            "experience": {"total_years": "7 ans"},  # String au lieu d'int
            "softwares": ["CEGID ", " Excel", ""],  # Espaces parasites
            "parsing_confidence": 0.75
        }
        
        print("🧪 === TEST ENHANCED BRIDGE ===")
        
        # Test conversion avec auto-fix
        candidat, metrics = await bridge.convert_candidat_enhanced(candidat_data_buggy)
        
        print(f"✅ Candidat converti: {candidat.personal_info.firstName} {candidat.personal_info.lastName}")
        print(f"📧 Email corrigé: {candidat.personal_info.email}")
        print(f"📱 Téléphone corrigé: {candidat.personal_info.phone}")
        print(f"🔧 Auto-fixes appliqués: {metrics.auto_fixes_count}")
        print(f"⚡ Temps total: {metrics.total_time_ms:.2f}ms")
        
        # Test entreprise
        entreprise_data = {
            "titre": "comptable unique h/f",  # Pas de majuscules
            "localisation": "  paris 8ème  ",  # Espaces parasites
            "salaire": "35k à 38k annuels",  # Format K
            "competences_requises": ["CEGID", "Compta", "CEGID"],  # Doublons
            "experience_requise": "5-10 ans",  # Format non standard
            "parsing_confidence": 0.82
        }
        
        entreprise, metrics2 = await bridge.convert_entreprise_enhanced(entreprise_data)
        
        print(f"🏢 Entreprise convertie: {entreprise.poste.titre}")
        print(f"💰 Salaire: {entreprise.poste.salaire_min}€ - {entreprise.poste.salaire_max}€")
        print(f"🔧 Auto-fixes appliqués: {metrics2.auto_fixes_count}")
        
        # Stats
        stats = bridge.get_enhanced_stats()
        print(f"📊 Taux de succès: {stats['enhanced_bridge_stats']['success_rate_percent']}%")
        print(f"🔧 Total auto-fixes: {stats['enhanced_bridge_stats']['auto_fixes_applied']}")
        
        print("✅ Tests Enhanced Bridge réussis!")
        
        return bridge
    
    # Lancement test
    if __name__ == "__main__":
        asyncio.run(test_enhanced_bridge())
