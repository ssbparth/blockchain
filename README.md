# Blockchain Identity Platform - Backend

FastAPI backend for a blockchain-based digital asset ownership platform.

## Tech Stack
- FastAPI (Python)
- web3.py
- IPFS (Pinata)
- Hardhat (Smart Contracts)
- Polygon Testnet

## Setup

1. Install dependencies:
pip install fastapi web3 uvicorn python-dotenv requests

2. Create .env file:
RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=your_contract_address
PRIVATE_KEY=your_private_key
PINATA_API_KEY=your_pinata_key
PINATA_SECRET=your_pinata_secret
PINATA_JWT=your_pinata_jwt

3. Run server:
uvicorn main:app --reload

## API Routes
- GET /health - Server status
- GET /identity/status - Blockchain connection
- POST /identity/create - Create digital identity
- POST /assets/mint - Mint digital asset NFT
- GET /assets/get/{wallet_address} - Get user assets
- POST /roles/assign - Assign admin/user role
- GET /roles/get/{wallet_address} - Get user role
