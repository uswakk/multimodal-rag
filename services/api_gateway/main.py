from fastapi import FastAPI
import requests
import time

app = FastAPI()

RETRIEVAL_URL = "http://retrieval_service:8000/query"
GENERATION_URL = "http://generation_service:8000/generate"

@app.post("/ask")
def ask_question(request: dict):

    query = request["query"]
    start_time = time.time()

    print(f"[API Gateway] Processing query: '{query}'")

    # --- STEP 1: Retrieve ---
    retrieval_start = time.time()
    retrieval_response = requests.post(
        RETRIEVAL_URL,
        json={"query": query, "top_k": 2}
    )
    retrieval_time = time.time() - retrieval_start
    print(f"[API Gateway] Retrieval completed in {retrieval_time:.2f}s")

    if retrieval_response.status_code != 200:
        print(f"[API Gateway] Retrieval failed with status {retrieval_response.status_code}")
        return {"error": "Retrieval failed"}

    text_chunks = retrieval_response.json()["results"]
    print(f"[API Gateway] Retrieved {len(text_chunks)} chunks")

    # --- STEP 2: Generate ---
    generation_start = time.time()
    generation_response = requests.post(
        GENERATION_URL,
        json={
            "query": query,
            "text_chunks": text_chunks
        }
    )
    generation_time = time.time() - generation_start
    print(f"[API Gateway] Generation completed in {generation_time:.2f}s")

    if generation_response.status_code != 200:
        print(f"[API Gateway] Generation failed with status {generation_response.status_code}")
        return {"error": "Generation failed"}

    generation_data = generation_response.json()

    total_time = time.time() - start_time
    print(f"[API Gateway] Total processing time: {total_time:.2f}s")

    return {
        "query": query,
        "answer": generation_data.get("answer"),
        "sources": generation_data.get("sources", [])
    }