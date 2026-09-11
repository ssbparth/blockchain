from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from routes import identity, assets, roles, recovery, audit, ai

app = FastAPI(
    title="Blockchain Digital Asset & Identity Platform",
    description="Backend API interfacing with Ethereum/EVM smart contracts and IPFS (Pinata)",
    version="1.0.0"
)

# CORS configuration - restrict origins in production
# Set ALLOWED_ORIGINS env var as comma-separated list (e.g., "https://app.example.com,http://localhost:3000")
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173").split(",")

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(identity.router, prefix="/identity", tags=["Identity"])
app.include_router(assets.router, prefix="/assets", tags=["Assets"])
app.include_router(roles.router, prefix="/roles", tags=["Roles"])
app.include_router(recovery.router, prefix="/recovery", tags=["Recovery"])
app.include_router(audit.router, prefix="/audit", tags=["Audit Logging"])
app.include_router(ai.router, prefix="/ai", tags=["AI Agent"])

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Blockchain backend is running"}




