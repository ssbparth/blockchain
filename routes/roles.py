from fastapi import APIRouter, HTTPException
from models.schemas import RoleAssign
from services.blockchain import is_connected

router = APIRouter()

@router.post("/assign")
def assign_role(data: RoleAssign):
    if not is_connected():
        raise HTTPException(status_code=500, detail="Blockchain not connected")
    return {
        "message": "Role assigned",
        "wallet": data.wallet_address,
        "role": data.role
    }

@router.get("/get/{wallet_address}")
def get_role(wallet_address: str):
    return {
        "wallet": wallet_address,
        "role": "viewer"
    }