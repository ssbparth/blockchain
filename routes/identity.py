from fastapi import APIRouter, HTTPException
from web3 import Web3
from models.schemas import IdentityCreate
from services.blockchain import get_web3, is_connected
from services.ipfs import upload_to_ipfs

router = APIRouter()

@router.get("/status")
def blockchain_status():
    connected = is_connected()
    if connected:
        w3 = get_web3()
        chain_id = w3.eth.chain_id
        latest_block = w3.eth.block_number
        return {
            "connected": True,
            "chain_id": chain_id,
            "latest_block": latest_block
        }
    return {"connected": False, "message": "Cannot reach RPC node"}

@router.post("/create")
def create_identity(data: IdentityCreate):
    if not is_connected():
        raise HTTPException(status_code=503, detail="Blockchain node not connected")
    
    if not Web3.is_address(data.wallet_address):
        raise HTTPException(status_code=400, detail="Invalid Ethereum wallet address")
    
    checksum_wallet = Web3.to_checksum_address(data.wallet_address)
    
    # Optionally pin user profile metadata to IPFS
    ipfs_profile_uri = None
    try:
        profile_data = {
            "name": data.name,
            "email": data.email,
            "wallet": checksum_wallet
        }
        ipfs_profile_uri = upload_to_ipfs(f"identity_{checksum_wallet}.json", profile_data)
    except Exception:
        # Gracefully handle if IPFS pinning fails or is optional
        pass

    return {
        "message": "Identity registered",
        "wallet": checksum_wallet,
        "name": data.name,
        "email": data.email,
        "profile_ipfs": ipfs_profile_uri
    }

@router.get("/balance/{wallet_address}")
def get_balance(wallet_address: str):
    if not is_connected():
        raise HTTPException(status_code=503, detail="Blockchain node not connected")
    
    if not Web3.is_address(wallet_address):
        raise HTTPException(status_code=400, detail="Invalid Ethereum wallet address")
    
    w3 = get_web3()
    checksum = Web3.to_checksum_address(wallet_address)
    balance_wei = w3.eth.get_balance(checksum)
    balance_eth = w3.from_wei(balance_wei, "ether")
    
    return {
        "wallet": checksum,
        "balance_wei": str(balance_wei),
        "balance_eth": float(balance_eth)
    }