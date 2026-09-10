import asyncio
import sys
sys.stdout.reconfigure(encoding='utf-8')

from services.ai_agent import chat_with_ollama

async def run_tests():
    print("=== TEST A: 'hi' ===")
    res1 = await chat_with_ollama([{"role": "user", "content": "hi"}])
    print(f"RESULT: {res1}\n")

    print("=== TEST B: 'What is Verichain?' ===")
    res2 = await chat_with_ollama([{"role": "user", "content": "What is Verichain?"}])
    print(f"RESULT: {res2}\n")

    print("=== TEST C: 'Show me my assets for 0x123...' ===")
    res3 = await chat_with_ollama([{"role": "user", "content": "Show me my assets for 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"}])
    print(f"RESULT: {res3}\n")

if __name__ == "__main__":
    asyncio.run(run_tests())
