import os
import requests

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost")
OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")
OLLAMA_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate"
MODEL_NAME = "qwen3-vl:2b"

def generate_answer(prompt: str):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": 2048,
                "num_predict": 1024,
                "temperature": 0.3
            }
        }
    )

    if response.status_code != 200:
        raise Exception(f"HTTP {response.status_code}: {response.text}")

    result = response.json()
    return result.get("response", "No response generated")