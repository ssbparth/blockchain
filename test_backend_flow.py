from fastapi.testclient import TestClient
from main import app
from web3 import Web3
from services.blockchain import check_admin_status
import time

client = TestClient(app)

def test_mint_retrieve_revoke():
    print("Testing Complete Mint Flow...")
    
    # 1. Test Mint
    test_wallet = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266" # Account 0
    mint_payload = {
        "wallet_address": test_wallet,
        "asset_name": "Test Asset 1",
        "asset_type": "stock",
        "quantity": 100,
        "unit": "shares",
        "additional_metadata": {},
        "metadata_uri": "ipfs://test1"
    }
    
    response = client.post("/assets/mint", json=mint_payload)
    if response.status_code != 200:
        print("Mint Failed:", response.json())
        return
        
    data = response.json()
    print("Mint Success:", data)
    asset_id = data.get("asset_id")
    
    # 2. Retrieve Asset
    response = client.get(f"/assets/get/{test_wallet}")
    data = response.json()
    print("Retrieve Success:", data)
    
    found = False
    for a in data["assets"]:
        if a["id"] == asset_id:
            found = True
            break
            
    if not found:
        print("Asset not found in retrieve!")
        
    # 3. Revoke
    response = client.post("/assets/revoke", json={"asset_id": asset_id})
    print("Revoke Success:", response.json())
    
    # 4. Verify Revoke
    response = client.get(f"/assets/{asset_id}")
    print("Asset Status After Revoke:", response.json())

test_mint_retrieve_revoke()
