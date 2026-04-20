from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from llm_client import generate_answer
from prompt_builder import build_prompt

app = FastAPI()

class QueryRequest(BaseModel):
    query: str
    text_chunks: List[dict]

@app.post("/generate")
def generate(request: QueryRequest):

    prompt = build_prompt(request.query, request.text_chunks)

    answer = generate_answer(prompt)

    # Extract unique sources from the text chunks
    sources = []
    seen = set()
    for chunk in request.text_chunks:
        source = chunk.get("source", "Unknown")
        if source not in seen:
            sources.append({
                "source": source,
                "page": chunk.get("page")
            })
            seen.add(source)

    return {
        "answer": answer,
        "sources": sources
    }