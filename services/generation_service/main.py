from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from llm_client import generate_answer
from prompt_builder import build_prompt, _is_generic_query

app = FastAPI()

class QueryRequest(BaseModel):
    query: str
    text_chunks: List[dict]

@app.post("/generate")
def generate(request: QueryRequest):
    prompt = build_prompt(request.query, request.text_chunks)
    answer = generate_answer(prompt)
    sources = [{"source": chunk.get("source", "Unknown"), "page": chunk.get("page")} for chunk in request.text_chunks]
    return {
        "answer": answer,
        "sources": sources
    }