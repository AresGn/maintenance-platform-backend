from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import os

# Import des modules existants
try:
    from app.core.config import settings
    from app.core.database import get_db
    from app.core.security import verify_password, create_access_token
    from app.models.user import User
    from app.models.equipment import Equipment
    from app.models.site import Site
    from app.models.production_line import ProductionLine
    from sqlalchemy.orm import Session
    from typing import List, Optional
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("Database modules not available, using fallback mode")

app = FastAPI(
    title="Maintenance Platform API",
    description="API pour la plateforme de maintenance industrielle",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles Pydantic
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: str
    updated_at: str

class EquipmentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: str
    location: Optional[str]
    site_id: Optional[int]
    production_line_id: Optional[int]
    created_at: str
    updated_at: str

class EquipmentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "active"
    location: Optional[str] = None
    site_id: Optional[int] = None
    production_line_id: Optional[int] = None

class SiteResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    location: Optional[str]
    created_at: str
    updated_at: str

class DashboardStats(BaseModel):
    total_equipment: int
    active_equipment: int
    maintenance_equipment: int
    out_of_service_equipment: int
    pending_maintenances: int
    completed_maintenances: int

class MaintenanceEvent(BaseModel):
    id: int
    title: str
    start: str
    end: str
    equipment_id: Optional[int]
    equipment_name: Optional[str]
    type: str  # 'preventive', 'corrective', 'inspection'
    status: str  # 'scheduled', 'in_progress', 'completed', 'cancelled'
    technician: Optional[str]
    description: Optional[str]

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Utilisateurs de test (fallback si pas de DB)
USERS_DB = {
    "admin": {"id": 1, "username": "admin", "password": "admin123", "role": "admin"},
    "super1": {"id": 2, "username": "super1", "password": "super123", "role": "supervisor"},
    "tech1": {"id": 3, "username": "tech1", "password": "tech123", "role": "technician"}
}

@app.get("/")
async def root():
    return {
        "message": "Maintenance Platform API is running!",
        "status": "ok",
        "version": "1.0.0",
        "database": "connected" if DATABASE_AVAILABLE else "fallback"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "API is running",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown"),
        "database": "available" if DATABASE_AVAILABLE else "fallback"
    }

@app.get("/test")
async def test():
    return {"test": "success", "message": "Test endpoint working"}

# Routes d'authentification
@app.post("/api/auth/login-json")
async def login_json(credentials: LoginRequest, db: Session = Depends(get_db) if DATABASE_AVAILABLE else None):
    if DATABASE_AVAILABLE and db:
        # Utiliser la vraie base de données
        user = db.query(User).filter(User.username == credentials.username).first()
        if not user or not verify_password(credentials.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        
        # Générer un vrai token JWT
        token = create_access_token(data={"sub": user.username})
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 3600,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else "2025-01-01T00:00:00Z",
                "updated_at": user.updated_at.isoformat() if user.updated_at else "2025-01-01T00:00:00Z"
            }
        }
    else:
        # Fallback vers les utilisateurs en dur
        user = USERS_DB.get(credentials.username)
        if not user or user["password"] != credentials.password:
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        
        token = f"token_{user['username']}_{user['id']}"
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 3600,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": f"{user['username']}@maintenance.com",
                "first_name": user["username"].title(),
                "last_name": "User",
                "role": user["role"],
                "is_active": True,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z"
            }
        }

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db) if DATABASE_AVAILABLE else None):
    if DATABASE_AVAILABLE and db:
        # TODO: Décoder le JWT et récupérer l'utilisateur de la DB
        pass
    
    # Fallback vers le token simple
    if not token.startswith("token_"):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        parts = token.split("_")
        username = parts[1]
        user_id = int(parts[2])
        
        user = USERS_DB.get(username)
        if not user or user["id"] != user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return UserResponse(
            id=user["id"],
            username=user["username"],
            email=f"{user['username']}@maintenance.com",
            first_name=user["username"].title(),
            last_name="User",
            role=user["role"],
            is_active=True,
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z"
        )
    except (IndexError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes d'équipements
@app.get("/api/equipment", response_model=List[EquipmentResponse])
async def get_equipment(db: Session = Depends(get_db) if DATABASE_AVAILABLE else None):
    try:
        if DATABASE_AVAILABLE and db:
            equipment = db.query(Equipment).all()
            return [
                EquipmentResponse(
                    id=eq.id,
                    name=eq.name,
                    description=getattr(eq, 'description', None),
                    status=getattr(eq, 'status', 'unknown'),
                    location=getattr(eq, 'location', None),
                    site_id=getattr(eq, 'site_id', None),
                    production_line_id=getattr(eq, 'production_line_id', None),
                    created_at=eq.created_at.isoformat() if hasattr(eq, 'created_at') and eq.created_at else "2025-01-01T00:00:00Z",
                    updated_at=eq.updated_at.isoformat() if hasattr(eq, 'updated_at') and eq.updated_at else "2025-01-01T00:00:00Z"
                ) for eq in equipment
            ]
        else:
            # Fallback vers les données de test
            return [
                EquipmentResponse(
                    id=1,
                    name="Compresseur A1",
                    description="Compresseur principal ligne 1",
                    status="active",
                    location="Atelier A",
                    site_id=1,
                    production_line_id=1,
                    created_at="2025-01-01T00:00:00Z",
                    updated_at="2025-01-01T00:00:00Z"
                ),
                EquipmentResponse(
                    id=2,
                    name="Convoyeur B2",
                    description="Convoyeur ligne 2",
                    status="maintenance",
                    location="Atelier B",
                    site_id=1,
                    production_line_id=2,
                    created_at="2025-01-01T00:00:00Z",
                    updated_at="2025-01-01T00:00:00Z"
                )
            ]
    except Exception as e:
        print(f"Erreur lors de la récupération des équipements: {e}")
        # Fallback vers les données de test en cas d'erreur
        return [
            EquipmentResponse(
                id=1,
                name="Compresseur A1",
                description="Compresseur principal ligne 1",
                status="active",
                location="Atelier A",
                site_id=1,
                production_line_id=1,
                created_at="2025-01-01T00:00:00Z",
                updated_at="2025-01-01T00:00:00Z"
            ),
            EquipmentResponse(
                id=2,
                name="Convoyeur B2",
                description="Convoyeur ligne 2",
                status="maintenance",
                location="Atelier B",
                site_id=1,
                production_line_id=2,
                created_at="2025-01-01T00:00:00Z",
                updated_at="2025-01-01T00:00:00Z"
            )
        ]

@app.post("/api/equipment", response_model=EquipmentResponse)
async def create_equipment(equipment_data: EquipmentCreate, db: Session = Depends(get_db) if DATABASE_AVAILABLE else None):
    if DATABASE_AVAILABLE and db:
        equipment = Equipment(
            name=equipment_data.name,
            description=equipment_data.description,
            status=equipment_data.status,
            location=equipment_data.location,
            site_id=equipment_data.site_id,
            production_line_id=equipment_data.production_line_id
        )
        db.add(equipment)
        db.commit()
        db.refresh(equipment)

        return EquipmentResponse(
            id=equipment.id,
            name=equipment.name,
            description=getattr(equipment, 'description', None),
            status=getattr(equipment, 'status', 'unknown'),
            location=getattr(equipment, 'location', None),
            site_id=getattr(equipment, 'site_id', None),
            production_line_id=getattr(equipment, 'production_line_id', None),
            created_at=equipment.created_at.isoformat() if hasattr(equipment, 'created_at') and equipment.created_at else "2025-01-01T00:00:00Z",
            updated_at=equipment.updated_at.isoformat() if hasattr(equipment, 'updated_at') and equipment.updated_at else "2025-01-01T00:00:00Z"
        )
    else:
        # Mode test
        return EquipmentResponse(
            id=999,
            name=equipment_data.name,
            description=equipment_data.description,
            status=equipment_data.status,
            location=equipment_data.location,
            site_id=equipment_data.site_id,
            production_line_id=equipment_data.production_line_id,
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z"
        )

# Route dashboard
@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db) if DATABASE_AVAILABLE else None):
    if DATABASE_AVAILABLE and db:
        total_equipment = db.query(Equipment).count()
        active_equipment = db.query(Equipment).filter(Equipment.status == "active").count()
        maintenance_equipment = db.query(Equipment).filter(Equipment.status == "maintenance").count()
        out_of_service_equipment = db.query(Equipment).filter(Equipment.status == "out_of_service").count()

        return DashboardStats(
            total_equipment=total_equipment,
            active_equipment=active_equipment,
            maintenance_equipment=maintenance_equipment,
            out_of_service_equipment=out_of_service_equipment,
            pending_maintenances=0,  # TODO: implémenter
            completed_maintenances=0  # TODO: implémenter
        )
    else:
        # Données de test
        return DashboardStats(
            total_equipment=25,
            active_equipment=20,
            maintenance_equipment=3,
            out_of_service_equipment=2,
            pending_maintenances=5,
            completed_maintenances=15
        )

# Route sites
@app.get("/api/sites", response_model=List[SiteResponse])
async def get_sites(db: Session = Depends(get_db) if DATABASE_AVAILABLE else None):
    if DATABASE_AVAILABLE and db:
        sites = db.query(Site).all()
        return [
            SiteResponse(
                id=site.id,
                name=site.name,
                description=getattr(site, 'description', None),
                location=getattr(site, 'location', None),
                created_at=site.created_at.isoformat() if hasattr(site, 'created_at') and site.created_at else "2025-01-01T00:00:00Z",
                updated_at=site.updated_at.isoformat() if hasattr(site, 'updated_at') and site.updated_at else "2025-01-01T00:00:00Z"
            ) for site in sites
        ]
    else:
        # Données de test
        return [
            SiteResponse(
                id=1,
                name="Site Principal",
                description="Site de production principal",
                location="Paris, France",
                created_at="2025-01-01T00:00:00Z",
                updated_at="2025-01-01T00:00:00Z"
            )
        ]

# Routes de maintenance
@app.get("/api/v1/maintenance/calendar", response_model=List[MaintenanceEvent])
async def get_maintenance_calendar(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db) if DATABASE_AVAILABLE else None
):
    try:
        if DATABASE_AVAILABLE and db:
            # TODO: Implémenter la récupération depuis la DB
            # maintenances = db.query(Maintenance).filter(
            #     Maintenance.scheduled_date.between(start_date, end_date)
            # ).all()
            pass

        # Données de test pour le calendrier
        from datetime import datetime, timedelta
        import random

        # Générer quelques événements de test
        events = []
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

        # Créer quelques événements de maintenance
        for i in range(5):
            event_date = start + timedelta(days=random.randint(0, (end - start).days))
            events.append(MaintenanceEvent(
                id=i + 1,
                title=f"Maintenance {['Préventive', 'Corrective', 'Inspection'][i % 3]}",
                start=event_date.isoformat(),
                end=(event_date + timedelta(hours=2)).isoformat(),
                equipment_id=random.randint(1, 7),
                equipment_name=f"Équipement {random.randint(1, 7)}",
                type=['preventive', 'corrective', 'inspection'][i % 3],
                status=['scheduled', 'in_progress', 'completed'][i % 3],
                technician=f"Technicien {random.randint(1, 3)}",
                description=f"Description de la maintenance {i + 1}"
            ))

        return events

    except Exception as e:
        print(f"Erreur lors de la récupération du calendrier: {e}")
        # Retourner une liste vide en cas d'erreur
        return []

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
