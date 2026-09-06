import requests
from config import PINATA_JWT

def upload_to_ipfs(file_name: str, file_content: dict):
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    
    headers = {
        "Authorization": f"Bearer {PINATA_JWT}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "pinataContent": file_content,
        "pinataMetadata": {
            "name": file_name
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        ipfs_hash = response.json()["IpfsHash"]
        return f"ipfs://{ipfs_hash}"
    else:
        raise Exception(f"IPFS upload failed: {response.text}")