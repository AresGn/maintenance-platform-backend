# Configuration de la base de données
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .config import settings

# Créer l'engine de base de données
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # Mettre à True pour voir les requêtes SQL
)

# Créer la session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dépendance pour obtenir une session de base de données
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
