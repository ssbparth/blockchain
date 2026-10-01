from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest
from services.ai_agent import chat_with_ollama
import traceback

router = APIRouter()

@router.post("/chat")
async def ai_chat(data: ChatRequest):
    try:
        messages = [{"role": m.role, "content": m.content} for m in data.messages]
        response_text = await chat_with_ollama(messages)
        return {"response": response_text}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI Agent error: {str(e)}")

@router.get("/status")
async def ai_status():
    import httpx
    from config import OLLAMA_URL
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get(f"{OLLAMA_URL}/api/tags")
            res.raise_for_status()
            return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Ollama offline")
