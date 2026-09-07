# 🔗 Blockchain Identity Platform — Backend

> Built for **SIH 2026** | FastAPI + Web3 + IPFS

A blockchain-powered backend that lets users own their digital identity and assets — certificates, gold, stocks, crypto — as tamper-proof NFTs. No central database. No single point of failure.

---

## 🚨 The Problem

Most organizations store identity and ownership records in one central database.
- If it gets hacked → everyone's data is exposed
- If admin makes a mistake → records can be changed with no trace
- Proving you own something → slow, manual, easy to fake

## ✅ Our Solution

Every identity and asset lives on a blockchain — permanent, verifiable, unfakeable.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🪪 Digital Identity (DID) | Every user gets a unique decentralized identity linked to their wallet |
| 🏅 NFT-Based Assets | Gold, stocks, crypto, certificates — all as tamper-proof NFTs |
| 🔐 Admin-Only Minting | Only approved admins can issue assets — no fakes possible |
| 👥 Role-Based Access | Admin, Issuer, Verifier, Viewer roles |
| 📜 Audit Trail | Every action permanently recorded on blockchain |
| 📦 IPFS Storage | Asset metadata stored on decentralized storage via Pinata |

---

## 🛠️ Tech Stack

- **Backend** — FastAPI (Python)
- **Blockchain** — web3.py + Polygon Testnet
- **Storage** — IPFS via Pinata
- **Smart Contracts** — Solidity + Hardhat

---

## ⚙️ Setup Instructions

### 1. Clone the repo
git clone https://github.com/ssbparth/blockchain
cd blockchain


### 2. Create virtual environment
python -m venv venv
venv\Scripts\activate



### 3. Install dependencies
pip install fastapi web3 uvicorn python-dotenv requests


### 4. Create `.env` file
RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=your_deployed_contract_address
PRIVATE_KEY=your_wallet_private_key
ABI_PATH=abi.json
PINATA_API_KEY=your_pinata_api_key
PINATA_SECRET=your_pinata_secret
PINATA_JWT=your_pinata_jwt


### 5. Run the server
uvicorn main:app --reload


### 6. Open API Docs
http://127.0.0.1:8000/docs

---

## 📡 API Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/health` | Server status |
| GET | `/identity/status` | Blockchain connection check |
| POST | `/identity/create` | Create a new digital identity |
| POST | `/assets/mint` | Mint a digital asset NFT |
| GET | `/assets/get/{wallet_address}` | Get all assets of a user |
| POST | `/roles/assign` | Assign admin/user role |
| GET | `/roles/get/{wallet_address}` | Get role of a user |

---

## 🔗 Related Repos

- [Smart Contracts](https://github.com/ssbparth/blockchain-contracts) — Solidity contracts + Hardhat
