from services.ai_agent import chat_with_ollama
import time
import sys

# bypass unicode errors
sys.stdout.reconfigure(encoding='utf-8')

print("--- TEST 1: Simple Message 'hi' ---")
t0 = time.time()
res = chat_with_ollama([{"role": "user", "content": "hi"}])
print(f"Result: {res}")
print(f"Time: {time.time() - t0:.2f}s\n")

print("--- TEST 2: Complex Message 'Show me my assets for 0x123...' ---")
t0 = time.time()
res = chat_with_ollama([{"role": "user", "content": "Show me my assets for 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"}])
print(f"Result: {res}")
print(f"Time: {time.time() - t0:.2f}s\n")
