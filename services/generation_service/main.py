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

    # If there are no retrieved chunks, ask for clarification (never return empty)
    if not request.text_chunks:
        return {
            "answer": "Can you be more specific with the query, or please name the document you are referring to",
            "sources": []
        }

    # If the user asked a generic question and there are multiple documents, ask which one
    if _is_generic_query(request.query) and len(sources) > 1:
        doc_names = ", ".join([s.get("source", "Unknown") for s in sources])
        return {
            "answer": f"Your query could refer to multiple documents: {doc_names}. Can you be more specific with the query, or please name the document you are referring to",
            "sources": sources
        }

    # Build prompt and call LLM
    prompt = build_prompt(request.query, request.text_chunks)
    answer = generate_answer(prompt)

    # Never return an empty string — replace empties with a clarifying prompt
    if not (answer and str(answer).strip()):
        answer = "Can you be more specific with the query, or please name the document you are referring to"

    return {
        "answer": answer,
        "sources": sources
    }