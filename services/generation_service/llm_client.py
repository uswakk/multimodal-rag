import requests

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
MODEL_NAME = "qwen3-vl:2b"

def generate_answer(prompt: str):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
    )

    if response.status_code != 200:
        raise Exception(f"HTTP {response.status_code}: {response.text}")

    result = response.json()
    return result.get("response", "No response generated")