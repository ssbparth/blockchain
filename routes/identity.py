from fastapi import APIRouter, HTTPException, Path
from models.schemas import IdentityCreate
from services.ipfs import pin_json_to_ipfs
from services.blockchain import get_user_profile_on_chain, register_user_on_chain, is_connected
from web3 import Web3

router = APIRouter()

@router.post("/create")
def create_identity(data: IdentityCreate):
    if not is_connected():
        raise HTTPException(status_code=503, detail="Blockchain node not connected")
        
    profile_data = {
        "name": data.name,
        "email": data.email,
        "wallet": data.wallet_address
    }
    
    try:
        # 1. Upload to IPFS
        ipfs_uri = pin_json_to_ipfs(profile_data, f"profile_{data.wallet_address}")
        
        # 2. Register on Blockchain
        tx_result = register_user_on_chain(data.wallet_address, ipfs_uri)
        
        return {
            "message": "Identity created successfully",
            "profile_ipfs": ipfs_uri,
            **tx_result
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create identity: {str(e)}")

@router.get("/status")
def get_identity_status(wallet: str):
    if not is_connected():
        raise HTTPException(status_code=503, detail="Blockchain node not connected")
    try:
        checksum = Web3.to_checksum_address(wallet)
        profile = get_user_profile_on_chain(checksum)
        return {"wallet": checksum, "profile": profile}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail="Invalid wallet address")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
