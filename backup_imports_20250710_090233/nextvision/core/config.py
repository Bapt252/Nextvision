"""
🔧 Nextvision Configuration
Gestion centralisée de la configuration avec pondération adaptative

Author: NEXTEN Team
Version: 1.0.0
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """⚙️ Configuration Settings"""
    
    # 🚀 Application Settings
    APP_NAME: str = "Nextvision"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    SECRET_KEY: str = Field(default="dev-secret-key")
    
    # 🗄️ Database Configuration
    DATABASE_URL: str = Field(default="postgresql://nextvision:nextvision123@localhost:5432/nextvision")
    
    # 🔴 Redis Configuration  
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # 🤖 External APIs
    OPENAI_API_KEY: str = Field(default="")
    GOOGLE_MAPS_API_KEY: str = Field(default="")
    
    # 🌐 Frontend Integration
    COMMITMENT_FRONTEND_URL: str = Field(default="https://bapt252.github.io/Commitment-")
    
    # 🔐 CORS
    ALLOWED_ORIGINS: List[str] = Field(default=["*"])
    
    # 🎯 Pondération par défaut
    DEFAULT_WEIGHTS: dict = Field(default={
        "semantique": 0.35,
        "remuneration": 0.20,
        "timing": 0.15,
        "localisation": 0.10,
        "secteurs": 0.10,
        "environnement": 0.05,
        "motivations": 0.05
    })
    
    def get_adaptive_weights(self, pourquoi_ecoute: str) -> dict:
        """
        🎯 Pondération Adaptative Contextuelle
        RÉVOLUTION: Ajustement intelligent selon le contexte
        """
        base_weights = self.DEFAULT_WEIGHTS.copy()
        
        adaptations = {
            "Rémunération trop faible": {
                "remuneration": 0.30,  # +10%
                "semantique": 0.30     # -5%
            },
            "Poste ne coïncide pas avec poste proposé": {
                "semantique": 0.45,    # +10%
                "remuneration": 0.15   # -5%
            },
            "Poste trop loin de mon domicile": {
                "localisation": 0.20,  # +10%
                "semantique": 0.30     # -5%
            },
            "Manque de flexibilité": {
                "environnement": 0.15, # +10%
                "motivations": 0.10    # +5%
            },
            "Manque de perspectives d'évolution": {
                "motivations": 0.15,   # +10%
                "semantique": 0.30     # -5%
            }
        }
        
        if pourquoi_ecoute in adaptations:
            base_weights.update(adaptations[pourquoi_ecoute])
        
        return base_weights
    
    class Config:
        env_file = ".env"

# Instance globale
settings = Settings()
