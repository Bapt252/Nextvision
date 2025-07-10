"""
Logger simple pour Nextvision V3.0
"""

import logging
import sys
from typing import Optional

def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Récupère un logger configuré pour Nextvision
    
    Args:
        name: Nom du logger
        level: Niveau de logging (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Logger configuré
    """
    
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Configuration du handler
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Niveau de logging
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(numeric_level)
    
    return logger

# Logger par défaut
default_logger = get_logger("nextvision")
