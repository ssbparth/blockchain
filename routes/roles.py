from fastapi import APIRouter, HTTPException
from models.schemas import RoleAssign
from services.blockchain import is_connected, add_admin_on_chain, check_admin_status

router = APIRouter()

@router.post("/assign")
def assign_role(data: RoleAssign):
    if not is_connected():
        raise HTTPException(status_code=503, detail="Blockchain node not connected")
    
    if data.role.lower() not in ["admin"]:
        raise HTTPException(status_code=400, detail="Only 'admin' role can be assigned on-chain")
    
    try:
        result = add_admin_on_chain(data.wallet_address)
        return {
            "message": "Admin role assigned successfully",
            "wallet": result.get("admin_address"),
            "role": "admin",
            "tx_hash": result.get("tx_hash"),
            "status": result.get("status")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Role assignment failed: {str(e)}")

@router.get("/get/{wallet_address}")
def get_role(wallet_address: str):
    if not is_connected():
        raise HTTPException(status_code=503, detail="Blockchain node not connected")
    try:
        status = check_admin_status(wallet_address)
        role = "super_admin" if status.get("is_super_admin") else ("admin" if status.get("is_admin") else "user")
        return {
            "wallet": status.get("wallet_address"),
            "role": role,
            "is_admin": status.get("is_admin"),
            "is_super_admin": status.get("is_super_admin")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch role: {str(e)}")