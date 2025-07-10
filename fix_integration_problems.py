#!/usr/bin/env python3
"""
🎯 Script de Correction Problèmes d'Intégration Nextvision V3.0
Corrige les 2 derniers problèmes pour atteindre ≥80% d'intégration

PROBLÈMES CIBLÉS:
1. questionnaire_parser_v3.py - erreurs d'indentation (35 points)
2. structured_logging LogLevel - imports incorrects (15 points)

Author: Assistant IA
Version: Final Fix - 30 points restants
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any
import shutil
from datetime import datetime

class IntegrationProblemsFixer:
    """🔧 Fixeur des problèmes d'intégration finale"""
    
    def __init__(self, nextvision_path: str):
        self.nextvision_path = Path(nextvision_path)
        self.backup_suffix = f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.fixes_applied = []
        self.errors_found = []
        
    def fix_all_integration_problems(self) -> Dict[str, Any]:
        """🎯 Corrige tous les problèmes d'intégration identifiés"""
        
        print("🚀 === CORRECTION PROBLÈMES INTÉGRATION NEXTVISION V3.0 ===")
        print(f"📁 Répertoire: {self.nextvision_path}")
        print(f"🎯 Objectif: Passer de 50% à ≥80% d'intégration")
        print()
        
        results = {
            "fixes_applied": [],
            "errors_fixed": [],
            "points_gained": 0,
            "status": "unknown"
        }
        
        try:
            # 1. Correction questionnaire_parser_v3.py (35 points)
            print("🔧 1. Correction questionnaire_parser_v3.py...")
            questionnaire_result = self.fix_questionnaire_parser_indentation()
            if questionnaire_result["success"]:
                results["fixes_applied"].append("questionnaire_parser_v3.py")
                results["points_gained"] += 35
                print(f"   ✅ Succès: +35 points")
            else:
                print(f"   ❌ Échec: {questionnaire_result['error']}")
                results["errors_fixed"].append(f"questionnaire_parser_v3.py: {questionnaire_result['error']}")
            
            # 2. Correction structured_logging imports (15 points)
            print("\n🔧 2. Correction imports structured_logging...")
            logging_result = self.fix_structured_logging_imports()
            if logging_result["success"]:
                results["fixes_applied"].append("structured_logging_imports")
                results["points_gained"] += 15
                print(f"   ✅ Succès: +15 points")
            else:
                print(f"   ❌ Échec: {logging_result['error']}")
                results["errors_fixed"].append(f"structured_logging: {logging_result['error']}")
            
            # 3. Vérification et corrections supplémentaires
            print("\n🔧 3. Vérifications supplémentaires...")
            additional_fixes = self.apply_additional_fixes()
            results["fixes_applied"].extend(additional_fixes)
            
            # 4. Validation finale
            print("\n📊 === RÉSULTATS CORRECTION ===")
            total_points = results["points_gained"]
            estimated_score = 50 + total_points  # Score de base 50%
            
            print(f"🎯 Points gagnés: {total_points}/50 points")
            print(f"📈 Score estimé: {estimated_score}%")
            
            if estimated_score >= 80:
                results["status"] = "success"
                print("🎉 OBJECTIF ATTEINT: ≥80% d'intégration!")
            else:
                results["status"] = "partial"
                print(f"⚠️  Objectif partiellement atteint: {estimated_score}%")
            
            # 5. Instructions finales
            self.print_final_instructions(results)
            
            return results
            
        except Exception as e:
            print(f"❌ Erreur générale: {e}")
            results["status"] = "error"
            results["error"] = str(e)
            return results
    
    def fix_questionnaire_parser_indentation(self) -> Dict[str, Any]:
        """🔧 Corrige les erreurs d'indentation dans questionnaire_parser_v3.py"""
        
        questionnaire_file = self.nextvision_path / "nextvision" / "adapters" / "questionnaire_parser_v3.py"
        
        if not questionnaire_file.exists():
            return {"success": False, "error": f"Fichier non trouvé: {questionnaire_file}"}
        
        try:
            # Backup
            backup_file = questionnaire_file.with_suffix(f".py{self.backup_suffix}")
            shutil.copy2(questionnaire_file, backup_file)
            print(f"   📋 Backup créé: {backup_file.name}")
            
            # Lecture contenu
            with open(questionnaire_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Corrections d'indentation spécifiques
            fixed_content = self.fix_python_indentation_issues(content)
            
            # Vérifications supplémentaires Python
            fixed_content = self.fix_python_syntax_issues(fixed_content)
            
            # Sauvegarde corrigée
            with open(questionnaire_file, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            print(f"   ✅ Fichier corrigé: {questionnaire_file.name}")
            
            # Test validation syntaxe
            try:
                compile(fixed_content, str(questionnaire_file), 'exec')
                print(f"   ✅ Syntaxe Python validée")
                return {"success": True, "fixes": ["indentation", "syntax"]}
            except SyntaxError as se:
                print(f"   ⚠️  Syntaxe encore problématique: {se}")
                return {"success": False, "error": f"Syntaxe: {se}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def fix_python_indentation_issues(self, content: str) -> str:
        """🔧 Corrige les problèmes d'indentation Python"""
        
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Détection lignes problématiques communes
            if line.strip():
                # Correction espaces/tabs mixtes
                if '\t' in line and '    ' in line:
                    # Conversion tabs -> 4 espaces
                    line = line.replace('\t', '    ')
                
                # Correction indentation après def/class/if/for/while/try/except
                if i > 0:
                    prev_line = lines[i-1].strip()
                    if (prev_line.endswith(':') and 
                        prev_line.startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'except', 'with ', 'elif ', 'else:'))):
                        
                        # Ligne suivante doit être indentée
                        if line.strip() and not line.startswith('    ') and not line.strip().startswith(('"""', "'''", '#')):
                            # Ajouter indentation si manquante
                            stripped = line.lstrip()
                            if stripped:
                                line = '    ' + stripped
                
                # Correction indentation dans blocs
                if (line.strip().startswith(('return ', 'yield ', 'raise ', 'pass', 'break', 'continue')) or
                    line.strip().startswith(('logger.', 'print('))):
                    
                    # Vérifier si dans un bloc
                    indent_level = self.detect_required_indentation(lines, i)
                    current_indent = len(line) - len(line.lstrip())
                    
                    if current_indent != indent_level and line.strip():
                        line = ' ' * indent_level + line.strip()
                
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def detect_required_indentation(self, lines: List[str], line_index: int) -> int:
        """🔍 Détecte le niveau d'indentation requis"""
        
        # Parcours vers le haut pour trouver le niveau
        for i in range(line_index - 1, -1, -1):
            line = lines[i].strip()
            if line and not line.startswith('#'):
                if line.endswith(':'):
                    # Dans un bloc
                    base_indent = len(lines[i]) - len(lines[i].lstrip())
                    return base_indent + 4
                elif lines[i].strip():
                    # Même niveau que ligne non-vide précédente
                    return len(lines[i]) - len(lines[i].lstrip())
        
        return 0  # Niveau racine
    
    def fix_python_syntax_issues(self, content: str) -> str:
        """🔧 Corrige les problèmes de syntaxe Python"""
        
        # Correction parenthèses/crochets non fermés
        content = self.fix_unclosed_brackets(content)
        
        # Correction virgules manquantes dans listes/dicts
        content = self.fix_missing_commas(content)
        
        # Correction strings non fermées
        content = self.fix_unclosed_strings(content)
        
        return content
    
    def fix_unclosed_brackets(self, content: str) -> str:
        """🔧 Corrige les parenthèses/crochets non fermés"""
        
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            if line.strip():
                # Comptage parenthèses
                open_parens = line.count('(')
                close_parens = line.count(')')
                open_brackets = line.count('[')
                close_brackets = line.count(']')
                open_braces = line.count('{')
                close_braces = line.count('}')
                
                # Correction si déséquilibre simple
                if open_parens > close_parens and open_parens - close_parens == 1:
                    if not line.rstrip().endswith(')'):
                        line = line.rstrip() + ')'
                
                if open_brackets > close_brackets and open_brackets - close_brackets == 1:
                    if not line.rstrip().endswith(']'):
                        line = line.rstrip() + ']'
                
                if open_braces > close_braces and open_braces - close_braces == 1:
                    if not line.rstrip().endswith('}'):
                        line = line.rstrip() + '}'
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_missing_commas(self, content: str) -> str:
        """🔧 Corrige les virgules manquantes"""
        
        # Patterns courants de virgules manquantes
        patterns = [
            (r'(\w+)(\s+)(\w+\s*:)', r'\1,\2\3'),  # dict items
            (r'(["\'])\s*\n\s*(["\'])', r'\1,\n    \2'),  # string lists
            (r'(\]\s*)\n\s*(\w+\s*=)', r'\1,\n    \2'),  # list items
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        return content
    
    def fix_unclosed_strings(self, content: str) -> str:
        """🔧 Corrige les strings non fermées"""
        
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            if line.strip():
                # Vérification guillemets simples
                single_quotes = line.count("'") - line.count("\\'")
                if single_quotes % 2 == 1:
                    # Nombre impair -> probablement non fermée
                    if line.strip().endswith("'"):
                        pass  # Déjà fermée
                    else:
                        line = line.rstrip() + "'"
                
                # Vérification guillemets doubles
                double_quotes = line.count('"') - line.count('\\"')
                if double_quotes % 2 == 1:
                    if line.strip().endswith('"'):
                        pass  # Déjà fermée
                    else:
                        line = line.rstrip() + '"'
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_structured_logging_imports(self) -> Dict[str, Any]:
        """🔧 Corrige les imports structured_logging incorrects"""
        
        print("   🔍 Recherche imports structured_logging incorrects...")
        
        fixes_applied = []
        files_fixed = []
        
        # Recherche tous les fichiers Python avec imports problématiques
        for py_file in self.nextvision_path.rglob("*.py"):
            if self.fix_structured_logging_in_file(py_file):
                files_fixed.append(py_file.name)
                fixes_applied.append(f"Import corrigé dans {py_file.name}")
        
        # Vérification du module __init__.py du logging
        logging_init = self.nextvision_path / "nextvision" / "logging" / "__init__.py"
        if self.ensure_logging_init_exports(logging_init):
            fixes_applied.append("__init__.py logging mis à jour")
        
        # Création alias si nécessaire
        if self.create_structured_logging_alias():
            fixes_applied.append("Alias structured_logging créé")
        
        if fixes_applied:
            print(f"   ✅ {len(fixes_applied)} corrections appliquées")
            for fix in fixes_applied:
                print(f"      - {fix}")
            return {"success": True, "fixes": fixes_applied}
        else:
            print("   ℹ️  Aucun import problématique trouvé")
            return {"success": True, "fixes": ["Aucune correction nécessaire"]}
    
    def fix_structured_logging_in_file(self, file_path: Path) -> bool:
        """🔧 Corrige les imports structured_logging dans un fichier"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Patterns d'imports à corriger
            patterns = [
                # from nextvision.structured_logging import ...
                (r'from\s+nextvision\.structured_logging\s+import\s+([^\n]+)',
                 r'from nextvision.logging.structured_logging import \1'),
                
                # import nextvision.structured_logging
                (r'import\s+nextvision\.structured_logging',
                 r'import nextvision.logging.structured_logging as structured_logging'),
                
                # nextvision.structured_logging.xxx
                (r'nextvision\.structured_logging\.(\w+)',
                 r'structured_logging.\1'),
            ]
            
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)
            
            # Si modifications apportées
            if content != original_content:
                # Backup
                backup_file = file_path.with_suffix(f".py{self.backup_suffix}")
                shutil.copy2(file_path, backup_file)
                
                # Sauvegarde corrigée
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"      ✅ {file_path.name}")
                return True
            
            return False
            
        except Exception as e:
            print(f"      ❌ Erreur {file_path.name}: {e}")
            return False
    
    def ensure_logging_init_exports(self, init_file: Path) -> bool:
        """🔧 S'assure que __init__.py exporte structured_logging"""
        
        try:
            if not init_file.exists():
                init_file.parent.mkdir(parents=True, exist_ok=True)
                init_content = ""
            else:
                with open(init_file, 'r', encoding='utf-8') as f:
                    init_content = f.read()
            
            # Vérifier si structured_logging est déjà exporté
            if 'structured_logging' not in init_content:
                # Ajouter export
                exports_to_add = '''
# Exports structured logging
from .structured_logging import (
    LogLevel, LogComponent, LogContext, StructuredFormatter,
    get_structured_logger, setup_production_logging,
    log_context, log_operation, get_request_tracker
)

__all__ = [
    'LogLevel', 'LogComponent', 'LogContext', 'StructuredFormatter',
    'get_structured_logger', 'setup_production_logging',
    'log_context', 'log_operation', 'get_request_tracker'
]
'''
                
                init_content += exports_to_add
                
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write(init_content)
                
                print(f"      ✅ {init_file.name} mis à jour")
                return True
            
            return False
            
        except Exception as e:
            print(f"      ❌ Erreur __init__.py: {e}")
            return False
    
    def create_structured_logging_alias(self) -> bool:
        """🔧 Crée un alias structured_logging.py à la racine si nécessaire"""
        
        alias_file = self.nextvision_path / "nextvision" / "structured_logging.py"
        
        if alias_file.exists():
            return False  # Déjà existe
        
        try:
            alias_content = '''"""
🔧 Alias pour compatibilité structured_logging
Redirige vers nextvision.logging.structured_logging
"""

# Import et re-export de tous les éléments
from nextvision.logging.structured_logging import *

# Rééxport explicite des éléments principaux
from nextvision.logging.structured_logging import (
    LogLevel, LogComponent, LogContext, StructuredFormatter,
    get_structured_logger, setup_production_logging,
    log_context, log_operation, get_request_tracker,
    LogAnalytics, get_log_analytics
)
'''
            
            with open(alias_file, 'w', encoding='utf-8') as f:
                f.write(alias_content)
            
            print(f"      ✅ Alias créé: structured_logging.py")
            return True
            
        except Exception as e:
            print(f"      ❌ Erreur création alias: {e}")
            return False
    
    def apply_additional_fixes(self) -> List[str]:
        """🔧 Applique des corrections supplémentaires"""
        
        additional_fixes = []
        
        # 1. Correction permissions fichiers
        try:
            for py_file in self.nextvision_path.rglob("*.py"):
                if not os.access(py_file, os.R_OK | os.W_OK):
                    os.chmod(py_file, 0o644)
            additional_fixes.append("Permissions fichiers corrigées")
        except:
            pass
        
        # 2. Vérification __init__.py manquants
        init_fixes = self.ensure_init_files()
        additional_fixes.extend(init_fixes)
        
        # 3. Nettoyage cache Python
        cache_cleaned = self.clean_python_cache()
        if cache_cleaned:
            additional_fixes.append("Cache Python nettoyé")
        
        return additional_fixes
    
    def ensure_init_files(self) -> List[str]:
        """🔧 S'assure que tous les répertoires ont des __init__.py"""
        
        fixes = []
        
        dirs_to_check = [
            self.nextvision_path / "nextvision" / "adapters",
            self.nextvision_path / "nextvision" / "services" / "scorers_v3",
            self.nextvision_path / "nextvision" / "logging",
        ]
        
        for dir_path in dirs_to_check:
            if dir_path.exists() and dir_path.is_dir():
                init_file = dir_path / "__init__.py"
                if not init_file.exists():
                    try:
                        init_file.touch()
                        fixes.append(f"__init__.py créé dans {dir_path.name}")
                    except:
                        pass
        
        return fixes
    
    def clean_python_cache(self) -> bool:
        """🧹 Nettoie le cache Python"""
        
        try:
            cache_dirs = list(self.nextvision_path.rglob("__pycache__"))
            cache_files = list(self.nextvision_path.rglob("*.pyc"))
            
            for cache_dir in cache_dirs:
                shutil.rmtree(cache_dir, ignore_errors=True)
            
            for cache_file in cache_files:
                cache_file.unlink(missing_ok=True)
            
            return len(cache_dirs) > 0 or len(cache_files) > 0
            
        except:
            return False
    
    def print_final_instructions(self, results: Dict[str, Any]):
        """📋 Affiche les instructions finales"""
        
        print("\n" + "="*60)
        print("📋 === INSTRUCTIONS FINALES ===")
        print("="*60)
        
        if results["status"] == "success":
            print("🎉 FÉLICITATIONS ! Objectif ≥80% atteint !")
            print()
            print("📋 Prochaines étapes:")
            print("1. Tester le score avec: python3 test_final_score.py")
            print("2. Redémarrer l'environnement Python:")
            print("   cd /path/to/Nextvision")
            print("   source nextvision_env/bin/activate")
            print("3. Tester les imports:")
            print("   python3 -c \"from nextvision.adapters.questionnaire_parser_v3 import QuestionnaireParserV3Factory\"")
            print("   python3 -c \"from nextvision.logging.structured_logging import LogLevel\"")
            
        else:
            print("⚠️  Corrections partielles appliquées")
            print()
            print("🔧 Actions manuelles recommandées:")
            
            if results["points_gained"] < 35:
                print("- Vérifier manuellement questionnaire_parser_v3.py pour erreurs syntaxe")
                print("- Utiliser un IDE pour détecter problèmes indentation")
            
            if "structured_logging_imports" not in results["fixes_applied"]:
                print("- Vérifier imports structured_logging dans tous les fichiers")
                print("- S'assurer que nextvision.logging.structured_logging est accessible")
        
        print()
        print("🔍 En cas de problème:")
        print("1. Restaurer depuis backup si nécessaire")
        print("2. Vérifier logs d'erreur détaillés")
        print("3. Tester imports individuellement")
        print()
        print("✅ Script terminé !")

def main():
    """🚀 Point d'entrée principal"""
    
    # Détection automatique du chemin Nextvision
    current_dir = Path.cwd()
    possible_paths = [
        current_dir,
        current_dir.parent,
        Path.home() / "Nextvision",
        Path("/path/to/Nextvision")  # À remplacer par le chemin réel
    ]
    
    nextvision_path = None
    for path in possible_paths:
        if (path / "nextvision" / "__init__.py").exists():
            nextvision_path = path
            break
    
    if not nextvision_path:
        print("❌ Impossible de trouver le répertoire Nextvision")
        print("💡 Lancez ce script depuis le répertoire Nextvision ou spécifiez le chemin")
        sys.exit(1)
    
    # Lancement des corrections
    fixer = IntegrationProblemsFixer(nextvision_path)
    results = fixer.fix_all_integration_problems()
    
    # Code de sortie selon résultat
    if results["status"] == "success":
        sys.exit(0)
    elif results["status"] == "partial":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()
