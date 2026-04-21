import time
import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3-vl:2b"

def stream_answer_with_timing(prompt: str):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True,
        "options": {
            "num_ctx": 2048,
            "num_predict": 1024,
            "temperature": 0.3
        }
    }

    start_time = time.perf_counter()
    first_token_time = None
    full_text = ""

    with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=300) as response:
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

        final_chunk = None

        for line in response.iter_lines():
            if not line:
                continue

            chunk = json.loads(line.decode("utf-8"))
            content = chunk.get("response", "")
            
            if content:
                print(content, end="", flush=True)

            if first_token_time is None and content:
                first_token_time = time.perf_counter()

            full_text += chunk.get("response", "")

            if chunk.get("done") is True:
                final_chunk = chunk
                break

    end_time = time.perf_counter()

    print("\n===== STREAM TIMING =====")
    print(f"Time to first token  : {(first_token_time - start_time):.3f} sec" if first_token_time else "Time to first token  : N/A")
    print(f"Total stream time    : {(end_time - start_time):.3f} sec")

    if final_chunk:
        total_duration = final_chunk.get("total_duration")
        load_duration = final_chunk.get("load_duration")
        prompt_eval_duration = final_chunk.get("prompt_eval_duration")
        eval_duration = final_chunk.get("eval_duration")
        eval_count = final_chunk.get("eval_count")

        if total_duration is not None:
            print(f"Server total_duration: {total_duration / 1_000_000_000:.3f} sec")
        if load_duration is not None:
            print(f"Load duration        : {load_duration / 1_000_000_000:.3f} sec")
        if prompt_eval_duration is not None:
            print(f"Prompt eval duration : {prompt_eval_duration / 1_000_000_000:.3f} sec")
        if eval_duration is not None:
            sec = eval_duration / 1_000_000_000
            print(f"Generation duration  : {sec:.3f} sec")
            if eval_count and sec > 0:
                print(f"Generation speed     : {eval_count / sec:.2f} tok/sec")

    print("=========================\n")
    return full_text


if __name__ == "__main__":
    prompt = "Say Hi"
    answer = stream_answer_with_timing(prompt)
    print("===== MODEL ANSWER =====")
    print(answer)