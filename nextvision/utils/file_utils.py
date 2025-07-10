"""
🔧 Nextvision File Utils - Utilitaires de gestion de fichiers
Utilitaires pour la gestion des fichiers dans le projet Nextvision

Author: Nextvision Team
Version: 1.0.0
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
import tempfile


class FileUtils:
    """Utilitaires de gestion de fichiers pour Nextvision"""
    
    def __init__(self):
        self.temp_dir = None
    
    def create_temp_directory(self) -> str:
        """Crée un répertoire temporaire"""
        if not self.temp_dir:
            self.temp_dir = tempfile.mkdtemp(prefix="nextvision_")
        return self.temp_dir
    
    def cleanup_temp_directory(self):
        """Nettoie le répertoire temporaire"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
    
    def validate_file_path(self, file_path: str) -> bool:
        """Valide qu'un chemin de fichier existe et est accessible"""
        try:
            path = Path(file_path)
            return path.exists() and path.is_file()
        except:
            return False
    
    def get_file_size(self, file_path: str) -> Optional[int]:
        """Retourne la taille d'un fichier en octets"""
        try:
            return os.path.getsize(file_path)
        except:
            return None
    
    def get_file_extension(self, file_path: str) -> str:
        """Retourne l'extension d'un fichier"""
        return Path(file_path).suffix.lower()
    
    def is_supported_format(self, file_path: str, supported_formats: List[str]) -> bool:
        """Vérifie si le format de fichier est supporté"""
        extension = self.get_file_extension(file_path)
        return extension in [fmt.lower() for fmt in supported_formats]
    
    def copy_file(self, source: str, destination: str) -> bool:
        """Copie un fichier"""
        try:
            shutil.copy2(source, destination)
            return True
        except:
            return False
    
    def move_file(self, source: str, destination: str) -> bool:
        """Déplace un fichier"""
        try:
            shutil.move(source, destination)
            return True
        except:
            return False
    
    def delete_file(self, file_path: str) -> bool:
        """Supprime un fichier"""
        try:
            os.remove(file_path)
            return True
        except:
            return False
    
    def read_file(self, file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """Lit le contenu d'un fichier texte"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except:
            return None
    
    def write_file(self, file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """Écrit du contenu dans un fichier"""
        try:
            # Créer le répertoire parent si nécessaire
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except:
            return False
    
    def list_files(self, directory: str, pattern: str = "*") -> List[str]:
        """Liste les fichiers dans un répertoire"""
        try:
            path = Path(directory)
            if path.is_dir():
                return [str(f) for f in path.glob(pattern) if f.is_file()]
            return []
        except:
            return []
    
    def ensure_directory(self, directory: str) -> bool:
        """S'assure qu'un répertoire existe (le crée si nécessaire)"""
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            return True
        except:
            return False
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Retourne les informations sur un fichier"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {}
            
            stat = path.stat()
            return {
                'name': path.name,
                'size': stat.st_size,
                'extension': path.suffix.lower(),
                'modified_time': stat.st_mtime,
                'is_file': path.is_file(),
                'is_directory': path.is_dir(),
                'exists': True
            }
        except:
            return {'exists': False}
    
    def __del__(self):
        """Nettoyage automatique"""
        self.cleanup_temp_directory()


# Instance globale pour faciliter l'usage
file_utils = FileUtils()
