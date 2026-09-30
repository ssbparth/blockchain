import requests
import logging
from config import PINATA_JWT

logger = logging.getLogger(__name__)

IPFS_REQUEST_TIMEOUT = 30


def upload_to_ipfs(file_name: str, file_content: dict):
    """
    Upload JSON metadata to Pinata IPFS.
    """
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
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=IPFS_REQUEST_TIMEOUT
        )

    except requests.Timeout:
        logger.error(f"IPFS JSON upload timeout for {file_name}")
        raise Exception("IPFS upload timed out")

    except requests.RequestException as e:
        logger.error(f"IPFS JSON upload failed for {file_name}: {e}")
        raise Exception(f"IPFS upload failed: {e}")

    if response.status_code == 200:
        ipfs_hash = response.json()["IpfsHash"]

        logger.info(
            f"Successfully uploaded {file_name} to IPFS: {ipfs_hash}"
        )

        return f"ipfs://{ipfs_hash}"

    logger.error(
        f"IPFS upload failed for {file_name}: "
        f"{response.status_code} - {response.text}"
    )

    raise Exception(
        f"IPFS upload failed: "
        f"{response.status_code} - {response.text}"
    )


def upload_file_to_ipfs(
    file_name: str,
    file_content: bytes,
    content_type: str = "application/octet-stream"
):
    """
    Upload an actual file (PDF/document) to Pinata IPFS.
    """
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

    headers = {
        "Authorization": f"Bearer {PINATA_JWT}"
    }

    files = {
        "file": (
            file_name,
            file_content,
            content_type
        )
    }

    pinata_metadata = {
        "name": file_name
    }

    try:
        response = requests.post(
            url,
            files=files,
            data={
                "pinataMetadata": str(pinata_metadata)
            },
            headers=headers,
            timeout=IPFS_REQUEST_TIMEOUT
        )

    except requests.Timeout:
        logger.error(f"IPFS file upload timeout for {file_name}")
        raise Exception("IPFS file upload timed out")

    except requests.RequestException as e:
        logger.error(f"IPFS file upload failed for {file_name}: {e}")
        raise Exception(f"IPFS file upload failed: {e}")

    if response.status_code == 200:
        ipfs_hash = response.json()["IpfsHash"]

        logger.info(
            f"Successfully uploaded file {file_name} to IPFS: {ipfs_hash}"
        )

        return f"ipfs://{ipfs_hash}"

    logger.error(
        f"IPFS file upload failed for {file_name}: "
        f"{response.status_code} - {response.text}"
    )

    raise Exception(
        f"IPFS file upload failed: "
        f"{response.status_code} - {response.text}"
    )


def pin_json_to_ipfs(file_content: dict, file_name: str):
    return upload_to_ipfs(file_name, file_content)