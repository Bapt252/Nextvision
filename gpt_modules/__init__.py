"""
GPT Modules Package for Nextvision V3.1
=======================================

Ce package contient les modules d'intégration GPT pour Nextvision V3.1.
Modules isolés pour éviter les conflits de logging avec le système principal.

Modules disponibles:
- cv_parser: Parser CV exhaustif (v4.0.1)
- job_parser: Parser fiches de poste (v3.0.1)  
- integration: Module d'intégration avec le système V3.1

Version: 1.0.0
Auteur: Baptiste Comas
Date: 2025-07-10
"""

__version__ = "1.0.0"
__author__ = "Baptiste Comas"

# Imports des modules principaux
from .cv_parser import CVParserGPT
from .job_parser import JobParserGPT
from .integration import GPTNextvisionIntegrator

__all__ = [
    'CVParserGPT',
    'JobParserGPT', 
    'GPTNextvisionIntegrator'
]
