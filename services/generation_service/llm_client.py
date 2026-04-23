import os
import base64
import requests

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost")
OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")
OLLAMA_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate"
MODEL_NAME = "qwen3-vl:2b"

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def generate_answer(prompt: str, image_paths: list = []):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_ctx": 4096,        # increase context for images
            "num_predict": 1024,
            "temperature": 0.7
        }
    }

    # Attach images if any
    if image_paths:
        images = []
        for path in image_paths:
            try:
                images.append(encode_image(path))
            except Exception as e:
                print(f"Could not load image {path}: {e}")
        if images:
            payload["images"] = images

    response = requests.post(OLLAMA_URL, json=payload)

    if response.status_code != 200:
        raise Exception(f"HTTP {response.status_code}: {response.text}")

    result = response.json()
    raw = result.get("response", "")

    import re
    cleaned = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
    return cleaned if cleaned else "I was unable to generate an answer."