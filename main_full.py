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
    from sqlalchemy.orm import Session
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
