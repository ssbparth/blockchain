from fastapi import APIRouter, HTTPException
from models.schemas import IdentityCreate
from services.blockchain import get_web3, is_connected

router = APIRouter()

@router.get("/status")
def blockchain_status():
    connected = is_connected()
    return {"connected": connected}

@router.post("/create")
def create_identity(data: IdentityCreate):
    if not is_connected():
        raise HTTPException(status_code=500, detail="Blockchain not connected")
    return {
        "message": "Identity creation queued",
        "wallet": data.wallet_address,
        "name": data.name
    }