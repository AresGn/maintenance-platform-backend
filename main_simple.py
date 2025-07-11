from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import os

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

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Utilisateurs de test (en dur pour commencer)
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
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "API is running",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown")
    }

@app.get("/test")
async def test():
    return {"test": "success", "message": "Test endpoint working"}

# Routes d'authentification
@app.post("/api/auth/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = USERS_DB.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Générer un token simple (en production, utilisez JWT)
    token = f"token_{user['username']}_{user['id']}"
    return {"access_token": token, "token_type": "bearer"}

# Route alternative pour le frontend (accepte JSON)
@app.post("/api/auth/login-json")
async def login_json(credentials: LoginRequest):
    user = USERS_DB.get(credentials.username)
    if not user or user["password"] != credentials.password:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    # Générer un token simple
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
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Décoder le token simple (en production, utilisez JWT)
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
            role=user["role"]
        )
    except (IndexError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
