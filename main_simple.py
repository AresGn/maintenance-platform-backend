from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
