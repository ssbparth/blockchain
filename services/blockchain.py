from web3 import Web3
from config import RPC_URL, CONTRACT_ADDRESS, PRIVATE_KEY, ABI_PATH
import json

def get_web3():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    return w3

def get_contract(w3):
    with open(ABI_PATH) as f:
        abi = json.load(f)
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_ADDRESS),
        abi=abi
    )
    return contract

def is_connected():
    w3 = get_web3()
    return w3.is_connected()