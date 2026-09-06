from pydantic import BaseModel

class IdentityCreate(BaseModel):
    wallet_address: str
    name: str
    email: str

class AssetMint(BaseModel):
    wallet_address: str
    asset_name: str
    asset_type: str  # "gold", "stock", "crypto"
    quantity: float
    unit: str  # "grams", "shares", "tokens"
    metadata_uri: str

class RoleAssign(BaseModel):
    wallet_address: str
    role: str