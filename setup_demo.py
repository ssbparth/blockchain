import os
import sys
sys.path.append('C:\\Users\\KOMAL PATIL\\blockchain-backend')

from services.blockchain import get_web3, get_contract, register_user_on_chain, add_admin_on_chain, mint_asset_on_chain

wallet = '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'
print(f'Setting up Demo Wallet {wallet} on-chain...')

try:
    print('1. Registering Identity...')
    register_user_on_chain(wallet, 'ipfs://demo-profile')
    print('Identity registered!')
except Exception as e:
    print(f'Register Identity failed (maybe already registered?): {e}')

try:
    print('2. Assigning Admin Role...')
    add_admin_on_chain(wallet)
    print('Admin Role assigned!')
except Exception as e:
    print(f'Admin assign failed: {e}')

try:
    print('3. Minting sample NFT...')
    res = mint_asset_on_chain(wallet, 'NFT / Digital Asset', 'Demo Badge', 1, 'ipfs://metadata')
    print(f'Minted! Asset ID: {res.get("asset_id")}')
except Exception as e:
    print(f'Mint failed: {e}')

print('Demo setup complete.')
