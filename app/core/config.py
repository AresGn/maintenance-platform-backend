# Configuration de l'application
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Base de données
    DATABASE_URL: str = "postgresql://neondb_owner:npg_Wwj4xevgCb3K@ep-lingering-cell-a8y9d337-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"

    # Sécurité JWT
    SECRET_KEY: str = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJPbmxpbmUgSldUIEJ1aWxkZXIiLCJpYXQiOjE3NTExMDAyNTksImV4cCI6MTc4MjYzNjI1OSwiYXVkIjoid3d3LmV4YW1wbGUuY29tIiwic3ViIjoianJvY2tldEBleGFtcGxlLmNvbSIsIkdpdmVuTmFtZSI6IkpvaG5ueSIsIlN1cm5hbWUiOiJSb2NrZXQiLCJFbWFpbCI6Impyb2NrZXRAZXhhbXBsZS5jb20iLCJSb2xlIjpbIk1hbmFnZXIiLCJQcm9qZWN0IEFkbWluaXN0cmF0b3IiXX0.vxuF-cOriJjHq68QCnh9hzfsnmX55WUq86NZleCXJPI"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Variables optionnelles
    REFRESH_TOKEN_EXPIRE_DAYS: Optional[int] = 7
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = None
    MAIL_PORT: Optional[int] = 587
    MAIL_SERVER: Optional[str] = None
    REDIS_URL: Optional[str] = None
    ENVIRONMENT: Optional[str] = "development"
    DEBUG: Optional[bool] = True

    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://maintenanceplatform-frontend.vercel.app"
    ]

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignorer les variables supplémentaires

settings = Settings()
