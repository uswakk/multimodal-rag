from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from llm_client import generate_answer
from prompt_builder import build_prompt

app = FastAPI()

class QueryRequest(BaseModel):
    query: str
    text_chunks: List[dict]
    image_chunks: List[dict] = []   # new

@app.post("/generate")
def generate(request: QueryRequest):
    # Separate image paths from image chunks
    image_paths = [
        chunk["image_path"]
        for chunk in request.image_chunks
        if chunk.get("image_path")
    ]

    prompt = build_prompt(request.query, request.text_chunks, request.image_chunks)
    answer = generate_answer(prompt, image_paths)

    sources = [
        {"source": c.get("source"), "page": c.get("page")}
        for c in request.text_chunks + request.image_chunks
    ]

    return {"answer": answer, "sources": sources}