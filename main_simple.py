"""
🎯 Nextvision - Main FastAPI Application
Algorithme de matching IA adaptatif pour NEXTEN
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="🎯 Nextvision API",
    description="Algorithme de matching IA adaptatif pour NEXTEN",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": "Nextvision",
        "description": "Algorithme de matching IA adaptatif pour NEXTEN",
        "version": "1.0.0",
        "status": "active",
        "frontend_integration": "https://github.com/Bapt252/Commitment-",
        "docs": "/docs"
    }

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Nextvision",
        "version": "1.0.0",
        "timestamp": "2025-07-04T00:00:00Z"
    }

@app.post("/api/v1/matching/candidate/{candidate_id}")
async def match_candidate(candidate_id: str, request_data: dict = None):
    """🎯 Endpoint de matching adaptatif"""
    return {
        "candidate_id": candidate_id,
        "status": "success",
        "message": "Matching endpoint ready - Pondération adaptative disponible",
        "note": "Connecter avec le frontend Commitment- pour tests complets"
    }

if __name__ == "__main__":
    print("🚀 Démarrage Nextvision API...")
    print("📚 Documentation: http://localhost:8000/docs")
    print("❤️ Health Check: http://localhost:8000/api/v1/health")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
