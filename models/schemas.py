from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class IdentityCreate(BaseModel):
    wallet_address: str = Field(..., description="Ethereum wallet address (0x...)")
    name: str
    email: Optional[str] = None

class AssetMint(BaseModel):
    wallet_address: str = Field(..., description="Recipient wallet address")
    asset_name: str = Field(..., description="Name of the asset")
    asset_type: str = Field(..., description="Category: gold, stock, crypto, etc.")
    quantity: int = Field(..., ge=1, description="Integer quantity of the asset")
    unit: Optional[str] = Field("units", description="Unit of measurement, e.g. grams, shares")
    additional_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Arbitrary key-value metadata to pin to IPFS")
    metadata_uri: Optional[str] = Field(None, description="Optional pre-existing IPFS URI or link")

class AssetRevoke(BaseModel):
    asset_id: int = Field(..., ge=1, description="ID of the asset to revoke")

class RoleAssign(BaseModel):
    wallet_address: str = Field(..., description="Target wallet address")
    role: str = Field("admin", description="Role to assign (e.g. admin)")

class AssetResponse(BaseModel):
    id: int
    asset_type: str
    asset_name: str
    quantity: int
    metadata_uri: str
    owner: str
    is_valid: bool