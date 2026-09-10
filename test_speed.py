import time
import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

url = "http://127.0.0.1:11434/api/chat"
messages = [
    {"role": "system", "content": "You are Verichain AI, an intelligent, friendly, and highly professional assistant."},
    {"role": "user", "content": "hi"}
]

for i in range(3):
    t0 = time.time()
    payload = {"model": "qwen3:4b", "messages": messages, "stream": False}
    resp = requests.post(url, json=payload).json()
    print(f"Run {i+1} took {time.time() - t0:.2f}s - {resp['message']['content']}")
