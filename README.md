# Maintenance Platform Backend

Backend API pour la plateforme de maintenance industrielle.

## Déploiement

Ce repository contient uniquement le backend de l'application.

### Vercel
- Configuré pour déployer automatiquement sur Vercel
- Point d'entrée: `api/index.py`
- Configuration: `vercel.json`

### Variables d'environnement requises
```
DATABASE_URL=postgresql://...
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## API Endpoints

- `GET /` - Message de bienvenue
- `GET /health` - Vérification de santé
- `POST /api/auth/login` - Connexion
- `POST /api/auth/register` - Inscription
- `GET /api/auth/me` - Profil utilisateur
