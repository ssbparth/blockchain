import json
import logging
from web3 import Web3
from config import RPC_URL, CONTRACT_ADDRESS, PRIVATE_KEY, ABI_PATH

# Cache ABI at module load to avoid repeated file I/O
with open(ABI_PATH) as f:
    _CACHED_ABI = json.load(f)

logger = logging.getLogger(__name__)

def get_web3():
    return Web3(Web3.HTTPProvider(RPC_URL))

def get_contract(w3=None):
    if w3 is None:
        w3 = get_web3()
    if not CONTRACT_ADDRESS:
        raise ValueError("CONTRACT_ADDRESS is not set in configuration")
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_ADDRESS),
        abi=_CACHED_ABI
    )
    return contract

def is_connected():
    """Check if connected to RPC node. Logs specific errors for debugging."""
    try:
        w3 = get_web3()
        return w3.is_connected()
    except ConnectionError as e:
        logger.warning(f"RPC connection failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking RPC connection: {e}")
        return False

def _build_and_send_tx(w3, tx_fn):
    """Helper to build, sign, broadcast and wait for a transaction using backend PRIVATE_KEY."""
    if not PRIVATE_KEY:
        raise ValueError("PRIVATE_KEY is not configured in environment")
    
    account = w3.eth.account.from_key(PRIVATE_KEY)
    sender_address = account.address
    nonce = w3.eth.get_transaction_count(sender_address, 'pending')
    
    # Build transaction with gas estimation and EIP-1559 fees
    try:
        gas_estimate = tx_fn.estimate_gas({'from': sender_address})
        gas_limit = int(gas_estimate * 1.2)  # 20% buffer
    except Exception:
        gas_limit = 300000  # Fallback default
    
    # EIP-1559 fee structure (works on modern networks, falls back on legacy)
    base_fee = w3.eth.get_block('latest').get('baseFeePerGas', w3.to_wei('20', 'gwei'))
    max_priority_fee = w3.to_wei('2', 'gwei')
    max_fee = base_fee * 2 + max_priority_fee
    
    tx_dict = tx_fn.build_transaction({
        'from': sender_address,
        'nonce': nonce,
        'gas': gas_limit,
        'maxFeePerGas': max_fee,
        'maxPriorityFeePerGas': max_priority_fee,
    })
    
    signed_tx = w3.eth.account.sign_transaction(tx_dict, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    return receipt, tx_hash.hex()

def mint_asset_on_chain(owner_address: str, asset_type: str, asset_name: str, quantity: int, metadata_uri: str):
    """Calls mintAsset on DigitalAsset contract."""
    w3 = get_web3()
    contract = get_contract(w3)
    checksum_owner = Web3.to_checksum_address(owner_address)
    
    tx_call = contract.functions.mintAsset(
        checksum_owner,
        asset_type,
        asset_name,
        quantity,
        metadata_uri
    )
    
    receipt, tx_hash = _build_and_send_tx(w3, tx_call)
    
    # Parse AssetMinted event
    asset_id = None
    try:
        events = contract.events.AssetMinted().process_receipt(receipt)
        if events:
            asset_id = events[0]['args']['id']
    except Exception as e:
        logger.warning(f"Failed to parse AssetMinted event from receipt: {e}")

    return {
        "status": "confirmed" if receipt.status == 1 else "reverted",
        "tx_hash": tx_hash,
        "block_number": receipt.blockNumber,
        "gas_used": receipt.gasUsed,
        "asset_id": asset_id
    }

def revoke_asset_on_chain(asset_id: int):
    """Calls revokeAsset on DigitalAsset contract."""
    w3 = get_web3()
    contract = get_contract(w3)
    
    tx_call = contract.functions.revokeAsset(asset_id)
    receipt, tx_hash = _build_and_send_tx(w3, tx_call)
    
    return {
        "status": "confirmed" if receipt.status == 1 else "reverted",
        "tx_hash": tx_hash,
        "block_number": receipt.blockNumber,
        "gas_used": receipt.gasUsed,
        "asset_id": asset_id
    }

def get_owner_assets_from_chain(owner_address: str):
    """Fetches all assets owned by the address from the contract."""
    w3 = get_web3()
    contract = get_contract(w3)
    checksum_owner = Web3.to_checksum_address(owner_address)
    
    asset_ids = contract.functions.getOwnerAssets(checksum_owner).call()
    assets = []
    for aid in asset_ids:
        raw_asset = contract.functions.assets(aid).call()
        # struct: (id, assetType, assetName, quantity, metadataURI, owner, isValid)
        assets.append({
            "id": raw_asset[0],
            "asset_type": raw_asset[1],
            "asset_name": raw_asset[2],
            "quantity": raw_asset[3],
            "metadata_uri": raw_asset[4],
            "owner": raw_asset[5],
            "is_valid": raw_asset[6]
        })
    return assets

def get_asset_by_id(asset_id: int):
    """Fetches a single asset details by ID."""
    w3 = get_web3()
    contract = get_contract(w3)
    raw_asset = contract.functions.assets(asset_id).call()
    if raw_asset[0] == 0:
        return None
    return {
        "id": raw_asset[0],
        "asset_type": raw_asset[1],
        "asset_name": raw_asset[2],
        "quantity": raw_asset[3],
        "metadata_uri": raw_asset[4],
        "owner": raw_asset[5],
        "is_valid": raw_asset[6]
    }

def add_admin_on_chain(admin_address: str):
    """Calls addAdmin on DigitalAsset contract (sender must be superAdmin)."""
    w3 = get_web3()
    contract = get_contract(w3)
    checksum_admin = Web3.to_checksum_address(admin_address)
    
    tx_call = contract.functions.addAdmin(checksum_admin)
    receipt, tx_hash = _build_and_send_tx(w3, tx_call)
    
    return {
        "status": "confirmed" if receipt.status == 1 else "reverted",
        "tx_hash": tx_hash,
        "block_number": receipt.blockNumber,
        "admin_address": checksum_admin
    }

def check_admin_status(wallet_address: str):
    """Checks if address is admin or superAdmin."""
    w3 = get_web3()
    contract = get_contract(w3)
    checksum = Web3.to_checksum_address(wallet_address)
    is_admin = contract.functions.admins(checksum).call()
    super_admin = contract.functions.superAdmin().call()
    return {
        "wallet_address": checksum,
        "is_admin": is_admin or (checksum.lower() == super_admin.lower()),
        "is_super_admin": (checksum.lower() == super_admin.lower()),
        "super_admin": super_admin
    }
