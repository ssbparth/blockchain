from fastapi import APIRouter, HTTPException, Path
import logging
from models.schemas import AssetMint, AssetRevoke
from services.blockchain import (
    is_connected,
    mint_asset_on_chain,
    get_owner_assets_from_chain,
    revoke_asset_on_chain,
    get_asset_by_id
)
from services.ipfs import upload_to_ipfs

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/mint")
def mint_asset(data: AssetMint):
    if not is_connected():
        raise HTTPException(status_code=503, detail="Blockchain node not connected")
    
    # 1. Determine or build metadata URI
    metadata_uri = data.metadata_uri
    if not metadata_uri:
        metadata_payload = {
            "name": data.asset_name,
            "type": data.asset_type,
            "quantity": data.quantity,
            "unit": data.unit,
            "recipient": data.wallet_address,
            "attributes": data.additional_metadata or {}
        }
        try:
            metadata_uri = upload_to_ipfs(f"asset_{data.asset_name}.json", metadata_payload)
        except Exception as e:
            logger.error(f"IPFS pinning failed for asset {data.asset_name}: {e}")
            raise HTTPException(status_code=502, detail="IPFS pinning failed")

    # 2. Call smart contract mintAsset
    try:
        tx_result = mint_asset_on_chain(
            owner_address=data.wallet_address,
            asset_type=data.asset_type,
            asset_name=data.asset_name,
            quantity=data.quantity,
            metadata_uri=metadata_uri
        )
        return {
            "message": "Asset minted successfully",
            "asset_id": tx_result.get("asset_id"),
            "tx_hash": tx_result.get("tx_hash"),
            "metadata_uri": metadata_uri,
            "status": tx_result.get("status")
        }
    except Exception as e:
        logger.error(f"Transaction failed for asset {data.asset_name}: {e}")
        raise HTTPException(status_code=400, detail="Transaction failed")

@router.get("/get/{wallet_address}")
def get_assets(wallet_address: str):
    if not is_connected():
        raise HTTPException(status_code=503, detail="Blockchain node not connected")
    try:
        assets = get_owner_assets_from_chain(wallet_address)
        return {
            "wallet": wallet_address,
            "count": len(assets),
            "assets": assets
        }
    except Exception as e:
        logger.error(f"Failed to fetch assets for {wallet_address}: {e}")
        raise HTTPException(status_code=400, detail="Failed to fetch assets")

@router.get("/{asset_id}")
def get_asset(asset_id: int = Path(..., ge=1)):
    if not is_connected():
        raise HTTPException(status_code=503, detail="Blockchain node not connected")
    try:
        asset = get_asset_by_id(asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset with ID {asset_id} not found")
        return asset
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch asset {asset_id}: {e}")
        raise HTTPException(status_code=400, detail="Failed to fetch asset")

@router.post("/revoke")
def revoke_asset(data: AssetRevoke):
    if not is_connected():
        raise HTTPException(status_code=503, detail="Blockchain node not connected")
    try:
        tx_result = revoke_asset_on_chain(data.asset_id)
        return {
            "message": f"Asset {data.asset_id} revoked",
            "tx_hash": tx_result.get("tx_hash"),
            "status": tx_result.get("status")
        }
    except Exception as e:
        logger.error(f"Revocation failed for asset {data.asset_id}: {e}")
        raise HTTPException(status_code=400, detail="Revocation failed")
