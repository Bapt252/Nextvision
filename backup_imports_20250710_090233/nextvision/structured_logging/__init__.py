"""
🔧 Nextvision Structured Logging - Système de logging structuré
Module de logging avancé pour Nextvision

Author: Nextvision Team
Version: 1.0.0
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

class StructuredLogger:
    """Logger structuré pour Nextvision"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Configuration handler si pas déjà fait
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_structured(self, level: str, message: str, **kwargs):
        """Log avec structure JSON"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'level': level,
            **kwargs
        }
        
        if level.upper() == 'ERROR':
            self.logger.error(json.dumps(log_data))
        elif level.upper() == 'WARNING':
            self.logger.warning(json.dumps(log_data))
        elif level.upper() == 'DEBUG':
            self.logger.debug(json.dumps(log_data))
        else:
            self.logger.info(json.dumps(log_data))
    
    def info(self, message: str, **kwargs):
        """Log info structuré"""
        self.log_structured('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning structuré"""
        self.log_structured('WARNING', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error structuré"""
        self.log_structured('ERROR', message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug structuré"""
        self.log_structured('DEBUG', message, **kwargs)

def get_structured_logger(name: str) -> StructuredLogger:
    """Récupère un logger structuré"""
    return StructuredLogger(name)

# Export principal
__all__ = ['StructuredLogger', 'get_structured_logger']
