#!/usr/bin/env python3
"""
🎯 CORRECTION DIRECTE FICHIER - enhanced_commitment_bridge_v3_integrated.py
Correction ciblée du problème d'indentation ligne 30 et imports circulaires

Author: Claude Assistant
Version: 1.0.0 - Correction Directe
"""

import os
import sys
from pathlib import Path
import shutil

def backup_file(file_path):
    """Crée une sauvegarde du fichier"""
    backup_path = f"{file_path}.backup"
    shutil.copy2(file_path, backup_path)
    print(f"📁 Sauvegarde créée: {backup_path}")

def fix_enhanced_bridge_file():
    """Corrige directement le fichier enhanced_commitment_bridge_v3_integrated.py"""
    
    file_path = Path("nextvision/services/enhanced_commitment_bridge_v3_integrated.py")
    
    if not file_path.exists():
        print(f"❌ Fichier non trouvé: {file_path}")
        return False
    
    print(f"🔧 Correction du fichier: {file_path}")
    
    # Sauvegarde
    backup_file(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # === CORRECTION 1: Remplacer l'héritage par composition ===
        print("🔄 Remplacement héritage par composition...")
        
        # Remplacer la déclaration de classe
        content = content.replace(
            "class EnhancedCommitmentBridgeV3Integrated(OriginalBridgeV3):",
            "class EnhancedCommitmentBridgeV3Integrated:"
        )
        
        # Remplacer l'import problématique par un import lazy
        content = content.replace(
            """# Import Enhanced Bridge V3.0 original
from nextvision.services.enhanced_commitment_bridge_v3 import (
    EnhancedCommitmentBridgeV3 as OriginalBridgeV3,
    BridgeV3Stats, BridgeV3Metrics, AutoFixEngineV3,
    EnhancedBridgeV3Factory
)""",
            """# Import Enhanced Bridge V3.0 - Lazy import to avoid circular dependency
# from nextvision.services.enhanced_commitment_bridge_v3 import (...)
# Will be imported dynamically in __init__"""
        )
        
        # Remplacer super().__init__() par composition
        content = content.replace(
            "        # Initialisation Enhanced Bridge V3.0\n        super().__init__()",
            """        # Initialisation Enhanced Bridge V3.0 via composition
        from nextvision.services.enhanced_commitment_bridge_v3 import (
            EnhancedCommitmentBridgeV3, BridgeV3Stats, BridgeV3Metrics, 
            AutoFixEngineV3, EnhancedBridgeV3Factory
        )
        self._enhanced_bridge_v3 = EnhancedCommitmentBridgeV3()"""
        )
        
        # Remplacer tous les appels super() par délégation
        content = content.replace(
            "await super().convert_candidat_enhanced_v3(",
            "await self._enhanced_bridge_v3.convert_candidat_enhanced_v3("
        )
        
        content = content.replace(
            "await super().convert_entreprise_enhanced_v3(",
            "await self._enhanced_bridge_v3.convert_entreprise_enhanced_v3("
        )
        
        content = content.replace(
            "super().get_enhanced_stats_v3()",
            "self._enhanced_bridge_v3.get_enhanced_stats_v3()"
        )
        
        content = content.replace(
            "super().reset_stats_v3()",
            "self._enhanced_bridge_v3.reset_stats_v3()"
        )
        
        # === CORRECTION 2: Ajout des imports manquants en haut ===
        print("📋 Ajout imports manquants...")
        
        # Ajouter les imports nécessaires après les imports existants
        imports_to_add = """
# Import des types pour éviter les erreurs
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nextvision.services.enhanced_commitment_bridge_v3 import (
        BridgeV3Stats, BridgeV3Metrics, AutoFixEngineV3, EnhancedBridgeV3Factory
    )
"""
        
        # Ajouter après les imports existants (avant logger = get_logger)
        content = content.replace(
            "from nextvision.logging.logger import get_logger\n\nlogger = get_logger(__name__)",
            f"from nextvision.logging.logger import get_logger{imports_to_add}\nlogger = get_logger(__name__)"
        )
        
        # === CORRECTION 3: Correction des classes de base ===
        print("🏗️ Correction classes de base...")
        
        # Remplacer l'héritage dans IntegratedBridgeStats
        content = content.replace(
            "class IntegratedBridgeStats(BridgeV3Stats):",
            """class IntegratedBridgeStats:
    \"\"\"Statistiques Bridge V3.0 intégré avec parsing réel\"\"\"
    
    def __init__(self, last_reset=None):
        # Statistiques de base
        self.last_reset = last_reset or datetime.now()
        self.total_conversions = 0
        self.successful_conversions = 0
        self.failed_conversions = 0"""
        )
        
        # Remplacer l'héritage dans IntegratedBridgeMetrics
        content = content.replace(
            "class IntegratedBridgeMetrics(BridgeV3Metrics):",
            """class IntegratedBridgeMetrics:
    \"\"\"Métriques Bridge V3.0 intégré\"\"\"
    
    def __init__(self, conversion_time_ms=0, validation_time_ms=0, auto_fix_time_ms=0,
                 total_time_ms=0, fields_processed=0, auto_fixes_count=0, cache_used=False,
                 commitment_parsing_time_ms=0, commitment_confidence=0.0,
                 commitment_fields_extracted=0, commitment_strategy_used="unknown",
                 format_conversion_time_ms=0, data_enrichment_time_ms=0,
                 transport_preparation_time_ms=0, data_quality_score=0.0,
                 integration_success=False):
        
        # Métriques de base
        self.conversion_time_ms = conversion_time_ms
        self.validation_time_ms = validation_time_ms  
        self.auto_fix_time_ms = auto_fix_time_ms
        self.total_time_ms = total_time_ms
        self.fields_processed = fields_processed
        self.auto_fixes_count = auto_fixes_count
        self.cache_used = cache_used"""
        )
        
        print("✅ Corrections appliquées")
        
        # Écrire le fichier corrigé
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fichier corrigé et sauvegardé")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {e}")
        return False

def test_syntax():
    """Teste la syntaxe du fichier corrigé"""
    
    file_path = "nextvision/services/enhanced_commitment_bridge_v3_integrated.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Test de compilation
        compile(content, file_path, 'exec')
        print("✅ Syntaxe du fichier corrigée - pas d'erreurs de compilation")
        return True
        
    except SyntaxError as e:
        print(f"❌ Erreur de syntaxe ligne {e.lineno}: {e.msg}")
        print(f"   Texte: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def test_imports():
    """Teste les imports après correction"""
    
    print("🧪 Test des imports après correction...")
    
    # Ajouter le projet au path
    project_root = Path.cwd()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    try:
        # Test import du module corrigé
        import nextvision.services.enhanced_commitment_bridge_v3_integrated
        print("✅ Import enhanced_commitment_bridge_v3_integrated réussi")
        
        # Test import de la classe
        from nextvision.services.enhanced_commitment_bridge_v3_integrated import EnhancedCommitmentBridgeV3Integrated
        print("✅ Import classe EnhancedCommitmentBridgeV3Integrated réussi")
        
        # Test instanciation
        bridge = EnhancedCommitmentBridgeV3Integrated(enable_real_parsing=False)
        print("✅ Instanciation de la classe réussie")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur import: {e}")
        return False

def main():
    """Point d'entrée principal"""
    
    print("🎯 CORRECTION DIRECTE - enhanced_commitment_bridge_v3_integrated.py")
    print("Résolution problème indentation ligne 30 et imports circulaires")
    print()
    
    success = True
    
    # 1. Correction du fichier
    if not fix_enhanced_bridge_file():
        success = False
    
    # 2. Test syntaxe
    if not test_syntax():
        success = False
    
    # 3. Test imports
    if not test_imports():
        success = False
    
    print("\n" + "="*60)
    print("📊 RÉSULTAT CORRECTION DIRECTE")
    print("="*60)
    
    if success:
        print("🎉 CORRECTION RÉUSSIE!")
        print("✅ Fichier enhanced_commitment_bridge_v3_integrated.py corrigé")
        print("✅ Imports circulaires résolus (héritage → composition)")
        print("✅ Syntaxe Python validée")
        print("✅ Module importable")
        
        print("\n📋 PROCHAINES ÉTAPES:")
        print("1. Lancer: python3 test_integration_simple.py")
        print("2. Score d'intégration attendu: ≥ 80%")
        
        return True
        
    else:
        print("❌ CORRECTION PARTIELLEMENT ÉCHOUÉE")
        print("📋 ACTIONS:")
        print("1. Vérifier la sauvegarde (.backup)")
        print("2. Relancer la correction si nécessaire")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
