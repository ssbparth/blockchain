import os
from dotenv import load_dotenv

load_dotenv()

# Required environment variables for production
REQUIRED_VARS = [
    "RPC_URL",
    "CONTRACT_ADDRESS",
    "PRIVATE_KEY",
    "PINATA_JWT"
]

# Validate required environment variables
missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
if missing:
    raise RuntimeError(
        f"Missing required environment variables: {', '.join(missing)}. "
        f"Please check your .env file or environment configuration."
    )

RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:8545")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
ABI_PATH = os.getenv("ABI_PATH", "abi.json")
PINATA_API_KEY = os.getenv("PINATA_API_KEY", "")
PINATA_SECRET = os.getenv("PINATA_SECRET", "")
PINATA_JWT = os.getenv("PINATA_JWT", "")