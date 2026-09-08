from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import identity, assets, roles

app = FastAPI(
    title="Blockchain Digital Asset & Identity Platform",
    description="Backend API interfacing with Ethereum/EVM smart contracts and IPFS (Pinata)",
    version="1.0.0"
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(identity.router, prefix="/identity", tags=["Identity"])
app.include_router(assets.router, prefix="/assets", tags=["Assets"])
app.include_router(roles.router, prefix="/roles", tags=["Roles"])

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Blockchain backend is running"}