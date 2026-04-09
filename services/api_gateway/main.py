from fastapi import FastAPI
import requests

app = FastAPI()

RETRIEVAL_URL = "http://localhost:8004/query"
GENERATION_URL = "http://localhost:8005/generate"

@app.post("/ask")
def ask_question(query: str):
    # 1. Retrieve evidence
    retrieval_resp = requests.post(RETRIEVAL_URL, json={"query": query, "top_k": 5}).json()
    text_chunks = retrieval_resp.get("results", [])

    # 2. Send to generation
    gen_resp = requests.post(GENERATION_URL, json={"query": query, "text_chunks": text_chunks}).json()

    return {"answer": gen_resp["answer"]}