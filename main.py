from fastapi import FastAPI
from routes import identity, assets, roles

app = FastAPI(title="Blockchain Identity Platform")

app.include_router(identity.router, prefix="/identity", tags=["Identity"])
app.include_router(assets.router, prefix="/assets", tags=["Assets"])
app.include_router(roles.router, prefix="/roles", tags=["Roles"])

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Blockchain backend is running"}