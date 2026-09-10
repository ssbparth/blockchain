import json
import logging
from web3 import Web3
from config import RPC_URL, CONTRACT_ADDRESS, PRIVATE_KEY, ABI_PATH

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
    try:
        w3 = get_web3()
        return w3.is_connected()
    except Exception as e:
        logger.error(f"RPC connection failed: {e}")
        return False

def _build_and_send_tx(w3, tx_fn):
    if not PRIVATE_KEY:
        raise ValueError("PRIVATE_KEY is not configured in environment")
    
    account = w3.eth.account.from_key(PRIVATE_KEY)
    sender_address = account.address
    nonce = w3.eth.get_transaction_count(sender_address, 'pending')
    
    base_fee = w3.eth.get_block('latest').get('baseFeePerGas', w3.to_wei('20', 'gwei'))
    max_priority_fee = w3.to_wei('2', 'gwei')
    max_fee = base_fee * 2 + max_priority_fee
    
    tx_dict = tx_fn.build_transaction({
        'from': sender_address,
        'nonce': nonce,
        'maxFeePerGas': max_fee,
        'maxPriorityFeePerGas': max_priority_fee,
    })
    
    try:
        gas_estimate = w3.eth.estimate_gas(tx_dict)
        tx_dict['gas'] = int(gas_estimate * 1.2)
    except Exception as e:
        raise ValueError(f"Transaction will revert: {str(e)}")
    
    signed_tx = w3.eth.account.sign_transaction(tx_dict, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    
    if receipt.status == 0:
        raise Exception(f"Transaction reverted on-chain. TX Hash: {tx_hash.hex()}")
        
    return receipt, tx_hash.hex()

def mint_asset_on_chain(owner_address: str, asset_type: str, asset_name: str, quantity: int, metadata_uri: str):
    w3 = get_web3()
    contract = get_contract(w3)
    checksum_owner = Web3.to_checksum_address(owner_address)
    
    tx_call = contract.functions.mintAsset(checksum_owner, asset_type, asset_name, quantity, metadata_uri)
    receipt, tx_hash = _build_and_send_tx(w3, tx_call)
    
    asset_id = None
    try:
        events = contract.events.AssetMinted().process_receipt(receipt)
        if events:
            asset_id = events[0]['args']['id']
    except Exception as e:
        logger.warning(f"Failed to parse AssetMinted event: {e}")

    return {
        "status": "confirmed",
        "tx_hash": tx_hash,
        "block_number": receipt.blockNumber,
        "gas_used": receipt.gasUsed,
        "asset_id": asset_id
    }

def revoke_asset_on_chain(asset_id: int):
    w3 = get_web3()
    contract = get_contract(w3)
    tx_call = contract.functions.revokeAsset(asset_id)
    receipt, tx_hash = _build_and_send_tx(w3, tx_call)
    return {"status": "confirmed", "tx_hash": tx_hash, "asset_id": asset_id}

def get_owner_assets_from_chain(owner_address: str):
    w3 = get_web3()
    contract = get_contract(w3)
    checksum_owner = Web3.to_checksum_address(owner_address)
    asset_ids = contract.functions.getOwnerAssets(checksum_owner).call()
    assets = []
    for aid in asset_ids:
        raw_asset = contract.functions.assets(aid).call()
        assets.append({
            "id": raw_asset[0], "asset_type": raw_asset[1], "asset_name": raw_asset[2],
            "quantity": raw_asset[3], "metadata_uri": raw_asset[4], "owner": raw_asset[5], "is_valid": raw_asset[6]
        })
    return assets

def get_asset_by_id(asset_id: int):
    w3 = get_web3()
    contract = get_contract(w3)
    raw_asset = contract.functions.assets(asset_id).call()
    if raw_asset[0] == 0: return None
    return {
        "id": raw_asset[0], "asset_type": raw_asset[1], "asset_name": raw_asset[2],
        "quantity": raw_asset[3], "metadata_uri": raw_asset[4], "owner": raw_asset[5], "is_valid": raw_asset[6]
    }

def add_admin_on_chain(admin_address: str):
    w3 = get_web3()
    contract = get_contract(w3)
    checksum_admin = Web3.to_checksum_address(admin_address)
    tx_call = contract.functions.addAdmin(checksum_admin)
    receipt, tx_hash = _build_and_send_tx(w3, tx_call)
    return {"status": "confirmed", "tx_hash": tx_hash, "admin_address": checksum_admin}

def check_admin_status(wallet_address: str):
    w3 = get_web3()
    contract = get_contract(w3)
    checksum = Web3.to_checksum_address(wallet_address)
    is_admin = contract.functions.admins(checksum).call()
    super_admin = contract.functions.superAdmin().call()
    return {
        "wallet_address": checksum,
        "is_admin": is_admin or (checksum.lower() == super_admin.lower()),
        "is_super_admin": (checksum.lower() == super_admin.lower())
    }

def add_guardian_on_chain(guardian_address: str):
    w3 = get_web3()
    contract = get_contract(w3)
    checksum_guardian = Web3.to_checksum_address(guardian_address)
    tx_call = contract.functions.addGuardian(checksum_guardian)
    receipt, tx_hash = _build_and_send_tx(w3, tx_call)
    return {"status": "confirmed", "tx_hash": tx_hash}

def remove_guardian_on_chain(guardian_address: str):
    w3 = get_web3()
    contract = get_contract(w3)
    checksum_guardian = Web3.to_checksum_address(guardian_address)
    tx_call = contract.functions.removeGuardian(checksum_guardian)
    receipt, tx_hash = _build_and_send_tx(w3, tx_call)
    return {"status": "confirmed", "tx_hash": tx_hash}

def get_guardians_from_chain(wallet_address: str):
    w3 = get_web3()
    contract = get_contract(w3)
    checksum = Web3.to_checksum_address(wallet_address)
    identity = contract.functions.getIdentity(checksum).call()
    guardians = contract.functions.getGuardians(identity).call()
    threshold = contract.functions.getRecoveryThreshold(identity).call()
    return {"identity": identity, "guardians": guardians, "threshold": threshold}

def request_recovery_on_chain(identity_address: str, new_owner_address: str):
    w3 = get_web3()
    contract = get_contract(w3)
    checksum_id = Web3.to_checksum_address(identity_address)
    checksum_new = Web3.to_checksum_address(new_owner_address)
    tx_call = contract.functions.requestRecovery(checksum_id, checksum_new)
    receipt, tx_hash = _build_and_send_tx(w3, tx_call)
    recovery_id = contract.functions.activeRecoveryId(checksum_id).call()
    return {"status": "confirmed", "tx_hash": tx_hash, "recovery_id": recovery_id}

def approve_recovery_on_chain(recovery_id: int):
    w3 = get_web3()
    contract = get_contract(w3)
    tx_call = contract.functions.approveRecovery(recovery_id)
    receipt, tx_hash = _build_and_send_tx(w3, tx_call)
    return {"status": "confirmed", "tx_hash": tx_hash}

def execute_recovery_on_chain(recovery_id: int):
    w3 = get_web3()
    contract = get_contract(w3)
    tx_call = contract.functions.executeRecovery(recovery_id)
    receipt, tx_hash = _build_and_send_tx(w3, tx_call)
    return {"status": "confirmed", "tx_hash": tx_hash}

def cancel_recovery_on_chain(recovery_id: int):
    w3 = get_web3()
    contract = get_contract(w3)
    tx_call = contract.functions.cancelRecovery(recovery_id)
    receipt, tx_hash = _build_and_send_tx(w3, tx_call)
    return {"status": "confirmed", "tx_hash": tx_hash}

def get_recovery_status_on_chain(recovery_id: int):
    w3 = get_web3()
    contract = get_contract(w3)
    req = contract.functions.recoveryRequests(recovery_id).call()
    status_map = {0: "None", 1: "Pending", 2: "Executed", 3: "Cancelled"}
    return {
        "recovery_id": req[0], "identity": req[1], "proposed_new_owner": req[2],
        "approval_count": req[3], "status": status_map.get(req[4], "Unknown")
    }

def register_user_on_chain(wallet_address: str, profile_uri: str):
    w3 = get_web3()
    contract = get_contract(w3)
    checksum = Web3.to_checksum_address(wallet_address)
    tx_call = contract.functions.registerUser(checksum, profile_uri)
    receipt, tx_hash = _build_and_send_tx(w3, tx_call)
    return {"status": "confirmed" if receipt.status == 1 else "reverted", "tx_hash": tx_hash}

def get_user_profile_on_chain(wallet_address: str):
    w3 = get_web3()
    contract = get_contract(w3)
    checksum = Web3.to_checksum_address(wallet_address)
    profile = contract.functions.getUserProfile(checksum).call()
    return {
        "wallet": profile[0],
        "profile_uri": profile[1],
        "is_registered": profile[2]
    }

def log_audit_on_chain(action: str, details: str):
    w3 = get_web3()
    contract = get_contract(w3)
    tx_call = contract.functions.logAudit(action, details)
    receipt, tx_hash = _build_and_send_tx(w3, tx_call)
    return {"status": "confirmed" if receipt.status == 1 else "reverted", "tx_hash": tx_hash}
