import requests
import logging
from config import PINATA_JWT

logger = logging.getLogger(__name__)

# Default timeout for Pinata API requests (seconds)
IPFS_REQUEST_TIMEOUT = 30

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
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=IPFS_REQUEST_TIMEOUT)
    except requests.Timeout:
        logger.error(f"IPFS upload timeout for {file_name}")
        raise Exception("IPFS upload timed out")
    except requests.RequestException as e:
        logger.error(f"IPFS upload request failed for {file_name}: {e}")
        raise Exception(f"IPFS upload failed: {e}")
    
    if response.status_code == 200:
        ipfs_hash = response.json()["IpfsHash"]
        logger.info(f"Successfully uploaded {file_name} to IPFS: {ipfs_hash}")
        return f"ipfs://{ipfs_hash}"
    else:
        logger.error(f"IPFS upload failed for {file_name}: {response.status_code} - {response.text}")
        raise Exception(f"IPFS upload failed: {response.status_code} - {response.text}")