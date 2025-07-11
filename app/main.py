from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.auth import router as auth_router
from .api.sites import router as sites_router
from .api.production_lines import router as production_lines_router
from .api.equipment import router as equipment_router

app = FastAPI(
    title="Maintenance Platform API",
    description="API pour la plateforme de maintenance industrielle",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes d'authentification
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])

# Inclure les routes pour les équipements
app.include_router(sites_router, prefix="/api/v1/sites", tags=["sites"])
app.include_router(production_lines_router, prefix="/api/v1/production-lines", tags=["production-lines"])
app.include_router(equipment_router, prefix="/api/v1/equipment", tags=["equipment"])

# Inclure les routes pour la maintenance
from app.api.v1.maintenance import router as maintenance_router
app.include_router(maintenance_router, prefix="/api/v1/maintenance", tags=["maintenance"])

@app.get("/")
async def root():
    return {"message": "API Maintenance Platform"}

@app.get("/health")
async def health():
    return {"status": "ok"}
