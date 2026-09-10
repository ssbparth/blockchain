import json
import requests
from config import OLLAMA_URL, OLLAMA_MODEL

url = f"{OLLAMA_URL}/api/chat"
payload = {
    "model": OLLAMA_MODEL,
    "messages": [{"role": "user", "content": "hi"}],
    "stream": True
}
print(f"Sending to {url} with model {OLLAMA_MODEL}")
response = requests.post(url, json=payload, stream=True)
for line in response.iter_lines():
    if line:
        data = json.loads(line)
        print(data.get("message", {}).get("content", ""), end="")
        if data.get("done"):
            print("\nDONE")
            break
