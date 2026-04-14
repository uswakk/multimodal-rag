from fastapi import FastAPI
import requests

app = FastAPI()

RETRIEVAL_URL = "http://localhost:8004/query"
GENERATION_URL = "http://localhost:8005/generate"


@app.post("/ask")
def ask_question(request: dict):

    query = request["query"]

    # --- STEP 1: Retrieve ---
    retrieval_response = requests.post(
        RETRIEVAL_URL,
        json={"query": query, "top_k": 3}
    )

    if retrieval_response.status_code != 200:
        return {"error": "Retrieval failed"}

    text_chunks = retrieval_response.json()["results"]

    # --- STEP 2: Generate ---
    generation_response = requests.post(
        GENERATION_URL,
        json={
            "query": query,
            "text_chunks": text_chunks
        }
    )

    if generation_response.status_code != 200:
        return {"error": "Generation failed"}

    return {
        "query": query,
        "answer": generation_response.json()["answer"],
        "sources": text_chunks
    }