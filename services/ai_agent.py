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


# ---------------------------------------------------------
# SYSTEM PROMPT
# ---------------------------------------------------------

try:
    with open("verichain_ai_context.md", "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()

except FileNotFoundError:
    SYSTEM_PROMPT = (
        "You are Verichain AI, a concise assistant for a blockchain "
        "identity and digital asset platform. "
        "Answer briefly and directly. "
        "Do not show internal reasoning."
    )


# ---------------------------------------------------------
# TOOLS
# ---------------------------------------------------------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_identity",
            "description": "Fetch a user's on-chain identity profile using their wallet address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "wallet_address": {
                        "type": "string",
                        "description": "The Ethereum wallet address (0x...)"
                    }
                },
                "required": ["wallet_address"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_assets",
            "description": "Fetch all digital assets owned by a user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "wallet_address": {
                        "type": "string",
                        "description": "The Ethereum wallet address (0x...)"
                    }
                },
                "required": ["wallet_address"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_guardians",
            "description": "Get trusted recovery guardians configured for a wallet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "wallet_address": {
                        "type": "string",
                        "description": "The Ethereum wallet address"
                    }
                },
                "required": ["wallet_address"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_recovery_status",
            "description": "Check the status of a recovery request.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recovery_id": {
                        "type": "integer",
                        "description": "The recovery request ID"
                    }
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
                    "wallet_address": {
                        "type": "string"
                    },
                    "profile_uri": {
                        "type": "string"
                    }
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
                    "wallet_address": {
                        "type": "string"
                    },
                    "asset_type": {
                        "type": "string",
                        "description": "Example: gold, crypto, nft, certificate"
                    },
                    "asset_name": {
                        "type": "string"
                    },
                    "quantity": {
                        "type": "integer"
                    },
                    "metadata_uri": {
                        "type": "string"
                    }
                },
                "required": [
                    "wallet_address",
                    "asset_type",
                    "asset_name",
                    "quantity"
                ]
            }
        }
    }
]


# ---------------------------------------------------------
# TOOL EXECUTION
# ---------------------------------------------------------

def execute_tool(name: str, args: dict):

    print(f"[AI_SERVICE] Executing tool: {name}")

    t0 = time.time()

    try:

        if name == "get_identity":
            result = get_user_profile_on_chain(
                args["wallet_address"]
            )

        elif name == "get_assets":
            result = get_owner_assets_from_chain(
                args["wallet_address"]
            )

        elif name == "get_guardians":
            result = get_guardians_from_chain(
                args["wallet_address"]
            )

        elif name == "get_recovery_status":
            result = get_recovery_status_on_chain(
                args["recovery_id"]
            )

        elif name == "register_identity":
            result = register_user_on_chain(
                args["wallet_address"],
                args.get("profile_uri", "")
            )

        elif name == "mint_asset":
            result = mint_asset_on_chain(
                args["wallet_address"],
                args["asset_type"],
                args["asset_name"],
                args.get("quantity", 1),
                args.get("metadata_uri", "")
            )

        else:
            result = {
                "error": "Unknown tool"
            }

    except Exception as e:

        print(
            f"[AI_SERVICE] Tool {name} failed: {e}"
        )

        result = {
            "error": str(e)
        }

    print(
        f"[AI_SERVICE] Tool {name} finished in "
        f"{time.time() - t0:.2f}s"
    )

    return result


# ---------------------------------------------------------
# CLEAN QWEN THINKING
# ---------------------------------------------------------

def clean_reasoning(text: str) -> str:

    if not text:
        return ""

    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL
    )

    text = re.sub(
        r"<thought>.*?</thought>",
        "",
        text,
        flags=re.DOTALL
    )

    return text.strip()


# ---------------------------------------------------------
# TOOL DETECTION
# ---------------------------------------------------------

def needs_tools(message: str) -> bool:

    keywords = [
        "asset",
        "nft",
        "gold",
        "document",
        "identity",
        "profile",
        "wallet",
        "recover",
        "guardian",
        "audit",
        "log",
        "mint",
        "upload",
        "check",
        "status",
        "show",
        "get",
        "0x"
    ]

    msg_lower = message.lower()

    return any(
        keyword in msg_lower
        for keyword in keywords
    )


# ---------------------------------------------------------
# MAIN CHAT FUNCTION
# ---------------------------------------------------------

async def chat_with_ollama(messages: list):

    t_start = time.time()

    print("\n[AI_SERVICE] --- NEW CHAT REQUEST ---")

    # -----------------------------------------------------
    # SYSTEM MESSAGE
    # -----------------------------------------------------

    if not messages or messages[0].get("role") != "system":

        system_message = {
            "role": "system",
            "content": SYSTEM_PROMPT
        }

    else:

        system_message = messages[0]


    # -----------------------------------------------------
    # KEEP ONLY RECENT CHAT HISTORY
    # This prevents huge prompts from slowing Qwen down.
    # -----------------------------------------------------

    history = [
        message
        for message in messages
        if message.get("role") != "system"
    ]

    history = history[-5:]

    messages = [system_message] + history


    # -----------------------------------------------------
    # FIND LAST USER MESSAGE
    # -----------------------------------------------------

    last_user_msg = ""

    for message in reversed(messages):

        if message.get("role") == "user":

            last_user_msg = message.get(
                "content",
                ""
            )

            break


    use_tools = needs_tools(last_user_msg)

    print(
        f"[AI_SERVICE] Tool selection: {use_tools}"
    )

    print(
        f"[AI_SERVICE] Using model: {OLLAMA_MODEL}"
    )


    # -----------------------------------------------------
    # OLLAMA PAYLOAD
    # -----------------------------------------------------

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,

        # Return complete JSON response
        "stream": False,

        # IMPORTANT FOR QWEN3
        # Stops extended thinking for normal chat.
        "think": False,

        # Keep model loaded so every request doesn't
        # need to reload it from RAM.
        "keep_alive": "10m",

        "options": {
            "temperature": 0.2,

            # Keep responses short and fast.
            "num_predict": 80,

            # Smaller context = faster inference.
            "num_ctx": 2048
        }
    }


    # -----------------------------------------------------
    # ONLY SEND TOOLS WHEN NEEDED
    # -----------------------------------------------------

    if use_tools:

        payload["tools"] = TOOLS


    url = f"{OLLAMA_URL}/api/chat"


    # -----------------------------------------------------
    # CALL OLLAMA
    # -----------------------------------------------------

    print(
        "[AI_SERVICE] Calling Ollama..."
    )

    t_request = time.time()

    try:

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.post(
                url,
                json=payload
            )

            response.raise_for_status()

            data = response.json()


    except httpx.TimeoutException:

        print(
            "[AI_SERVICE] Ollama request timed out."
        )

        return (
            "The AI is taking too long to respond. "
            "Please try again."
        )


    except Exception as e:

        print(
            f"[AI_SERVICE] Ollama error: {e}"
        )

        raise


    print(
        f"[AI_SERVICE] Ollama responded in "
        f"{time.time() - t_request:.2f}s"
    )


    # -----------------------------------------------------
    # READ RESPONSE
    # -----------------------------------------------------

    message = data.get(
        "message",
        {}
    )


    # -----------------------------------------------------
    # TOOL CALLS
    # -----------------------------------------------------

    tool_calls = message.get(
        "tool_calls"
    )


    # -----------------------------------------------------
    # NORMAL CHAT
    # -----------------------------------------------------

    if not tool_calls:

        final_text = clean_reasoning(
            message.get(
                "content",
                ""
            )
        )

        print(
            f"[AI_SERVICE] Completed in "
            f"{time.time() - t_start:.2f}s"
        )

        return final_text


    # -----------------------------------------------------
    # EXECUTE TOOLS
    # -----------------------------------------------------

    print(
        f"[AI_SERVICE] Executing "
        f"{len(tool_calls)} tool(s)..."
    )


    messages.append(message)


    for tool_call in tool_calls:

        function = tool_call.get(
            "function",
            {}
        )

        name = function.get(
            "name"
        )

        args = function.get(
            "arguments",
            {}
        )


        # Some Ollama versions may return arguments
        # as a JSON string.
        if isinstance(args, str):

            try:
                args = json.loads(args)

            except json.JSONDecodeError:

                args = {}


        result = execute_tool(
            name,
            args
        )


        messages.append({
            "role": "tool",
            "name": name,
            "content": json.dumps(
                result,
                default=str
            )
        })


    # -----------------------------------------------------
    # FOLLOW-UP AFTER TOOL
    # -----------------------------------------------------

    follow_up_payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "think": False,
        "keep_alive": "10m",

        "options": {
            "temperature": 0.2,
            "num_predict": 100,
            "num_ctx": 2048
        }
    }


    print(
        "[AI_SERVICE] Generating final tool response..."
    )


    try:

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response2 = await client.post(
                url,
                json=follow_up_payload
            )

            response2.raise_for_status()

            data2 = response2.json()


    except httpx.TimeoutException:

        print(
            "[AI_SERVICE] Tool follow-up timed out."
        )

        return (
            "The blockchain data was retrieved, "
            "but the AI response took too long."
        )


    message2 = data2.get(
        "message",
        {}
    )


    final_text = clean_reasoning(
        message2.get(
            "content",
            ""
        )
    )


    print(
        f"[AI_SERVICE] Completed with tools in "
        f"{time.time() - t_start:.2f}s"
    )


    return final_text