from fastapi import APIRouter, HTTPException
from models.schemas import AssetMint
from services.blockchain import is_connected

router = APIRouter()

@router.post("/mint")
def mint_asset(data: AssetMint):
    if not is_connected():
        raise HTTPException(status_code=500, detail="Blockchain not connected")
    return {
        "message": "Asset minting queued",
        "wallet": data.wallet_address,
        "asset_name": data.asset_name,
        "asset_type": data.asset_type
    }

@router.get("/get/{wallet_address}")
def get_assets(wallet_address: str):
    return {
        "wallet": wallet_address,
        "assets": []
    }