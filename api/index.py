from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.sites import router as sites_router
from app.api.production_lines import router as production_lines_router
from app.api.equipment import router as equipment_router

app = FastAPI(
    title="Maintenance Platform API",
    description="API pour la plateforme de maintenance industrielle",
    version="1.0.0"
)

# Configuration CORS pour Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez votre domaine frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(sites_router, prefix="/api/sites", tags=["sites"])
app.include_router(production_lines_router, prefix="/api/production-lines", tags=["production-lines"])
app.include_router(equipment_router, prefix="/api/equipment", tags=["equipment"])

@app.get("/")
async def root():
    return {"message": "Maintenance Platform API is running on Vercel!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

# Export pour Vercel
handler = app
