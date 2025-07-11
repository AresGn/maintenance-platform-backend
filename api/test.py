from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Test API")

# CORS simple
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Test API is working!"}

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Health check passed"}

# Export pour Vercel
handler = app
