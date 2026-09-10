import json
import re
import time
import httpx
from config import OLLAMA_URL, OLLAMA_MODEL
from services.blockchain import (
    get_user_profile_on_chain,
    get_owner_assets_from_chain,
    get_guardians_from_chain,
    get_recovery_status_on_chain,
    mint_asset_on_chain,
    register_user_on_chain
)

print("[AI_SERVICE] Initializing AI agent module...")

try:
    with open("verichain_ai_context.md", "r") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    SYSTEM_PROMPT = "You are Verichain AI. Help the user interact with the blockchain."

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_identity",
            "description": "Fetch a user's on-chain identity profile using their wallet address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "wallet_address": {"type": "string", "description": "The Ethereum wallet address (0x...)"}
                },
                "required": ["wallet_address"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_assets",
            "description": "Fetch all digital assets, NFTs, or documents owned by a user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "wallet_address": {"type": "string", "description": "The Ethereum wallet address (0x...)"}
                },
                "required": ["wallet_address"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_guardians",
            "description": "Get the trusted recovery guardians configured for a wallet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "wallet_address": {"type": "string", "description": "The Ethereum wallet address"}
                },
                "required": ["wallet_address"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_recovery_status",
            "description": "Check the status of a specific recovery request ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recovery_id": {"type": "integer", "description": "The recovery request ID"}
                },
                "required": ["recovery_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "register_identity",
            "description": "Register a new user identity on-chain.",
            "parameters": {
                "type": "object",
                "properties": {
                    "wallet_address": {"type": "string"},
                    "profile_uri": {"type": "string"}
                },
                "required": ["wallet_address", "profile_uri"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mint_asset",
            "description": "Mint a new asset or document to a user's wallet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "wallet_address": {"type": "string"},
                    "asset_type": {"type": "string", "description": "e.g., 'document', 'gold', 'crypto'"},
                    "asset_name": {"type": "string"},
                    "quantity": {"type": "integer"},
                    "metadata_uri": {"type": "string", "description": "IPFS URI if available"}
                },
                "required": ["wallet_address", "asset_type", "asset_name", "quantity"]
            }
        }
    }
]

def execute_tool(name: str, args: dict):
    print(f"[AI_SERVICE] Executing tool: {name}")
    t0 = time.time()
    try:
        if name == "get_identity":
            res = get_user_profile_on_chain(args["wallet_address"])
        elif name == "get_assets":
            res = get_owner_assets_from_chain(args["wallet_address"])
        elif name == "get_guardians":
            res = get_guardians_from_chain(args["wallet_address"])
        elif name == "get_recovery_status":
            res = get_recovery_status_on_chain(args["recovery_id"])
        elif name == "register_identity":
            res = register_user_on_chain(args["wallet_address"], args.get("profile_uri", ""))
        elif name == "mint_asset":
            res = mint_asset_on_chain(
                args["wallet_address"], 
                args["asset_type"], 
                args["asset_name"], 
                args.get("quantity", 1), 
                args.get("metadata_uri", "")
            )
        else:
            res = {"error": "Unknown tool"}
    except Exception as e:
        print(f"[AI_SERVICE] Tool {name} failed: {e}")
        res = {"error": str(e)}
    
    print(f"[AI_SERVICE] Tool {name} finished in {time.time() - t0:.2f}s")
    return res

def clean_reasoning(text: str) -> str:
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'<thought>.*?</thought>', '', text, flags=re.DOTALL)
    return text.strip()

def needs_tools(message: str) -> bool:
    keywords = ["asset", "nft", "gold", "document", "identity", "profile", "wallet", "recover", "guardian", "audit", "log", "mint", "upload", "check", "status", "show", "get", "0x"]
    msg_lower = message.lower()
    return any(k in msg_lower for k in keywords)

async def chat_with_ollama(messages: list):
    t_start = time.time()
    print(f"\n[AI_SERVICE] --- NEW CHAT REQUEST ---")
    print(f"[AI_SERVICE] Request parsing & preparation started...")
    
    if not messages or messages[0].get("role") != "system":
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
        
    url = f"{OLLAMA_URL}/api/chat"
    
    last_user_msg = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last_user_msg = m.get("content", "")
            break

    # 1. Tool Selection Heuristic
    use_tools = needs_tools(last_user_msg)
    print(f"[AI_SERVICE] Context prepared. Tool selection required: {use_tools} (took {time.time() - t_start:.2f}s)")

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False
    }
    if use_tools:
        payload["tools"] = TOOLS

    # 2. Ollama Request
    print(f"[AI_SERVICE] Calling Ollama API...")
    t_req = time.time()
    
    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
    print(f"[AI_SERVICE] Ollama API responded in {time.time() - t_req:.2f}s")
    
    message = data.get("message", {})
    messages.append(message)
    
    tool_calls = message.get("tool_calls")
    
    # 3. Final Response Generation (No tools needed)
    if not tool_calls:
        print(f"[AI_SERVICE] No tool calls requested. Generating final response...")
        final_text = clean_reasoning(message.get("content", ""))
        print(f"[AI_SERVICE] Chat completed successfully in {time.time() - t_start:.2f}s total.")
        return final_text
        
    # 4. Tool Execution
    print(f"[AI_SERVICE] Tool execution requested by AI ({len(tool_calls)} tools)...")
    t_tools = time.time()
    for tc in tool_calls:
        fn = tc.get("function", {})
        name = fn.get("name")
        args = fn.get("arguments", {})
        
        result = execute_tool(name, args)
        
        messages.append({
            "role": "tool",
            "name": name,
            "content": json.dumps(result)
        })
    print(f"[AI_SERVICE] All tools executed in {time.time() - t_tools:.2f}s")
        
    # 5. Follow-up Call
    print(f"[AI_SERVICE] Requesting final summary from Ollama...")
    follow_up_payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False
    }
    
    t_req2 = time.time()
    async with httpx.AsyncClient(timeout=90.0) as client:
        response2 = await client.post(url, json=follow_up_payload)
        response2.raise_for_status()
        data2 = response2.json()
        
    print(f"[AI_SERVICE] Ollama summary received in {time.time() - t_req2:.2f}s")
    
    message2 = data2.get("message", {})
    final_text = clean_reasoning(message2.get("content", ""))
    
    print(f"[AI_SERVICE] Chat completed successfully with tools in {time.time() - t_start:.2f}s total.")
    return final_text
