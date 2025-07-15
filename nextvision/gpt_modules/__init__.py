"""
🚀 NEXTVISION GPT MODULES v3.1
Package des modules GPT isolés
"""

from .cv_parser import NextvisionGPTParser, ParsedProfile
from .job_parser import NextvisionJobParser, ParsedJobPosting
from .integration import NextvisionGPTIntegration, MatchingResult

__all__ = [
    'NextvisionGPTParser', 'ParsedProfile',
    'NextvisionJobParser', 'ParsedJobPosting', 
    'NextvisionGPTIntegration', 'MatchingResult'
]

__version__ = "3.1.0"
