from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from text_retriever import search_text
from image_retriever import search_images
from fusion import fuse_results

app = FastAPI()

class QueryRequest(BaseModel):
    query: str
    top_k: int = 10

@app.post("/query")
def query(request: QueryRequest):
    try:
        query = request.query

        # Step 1: search text
        text_results = search_text(query, request.top_k)

        # Step 2: search images
        image_results = search_images(query, request.top_k)

        # Step 3: fuse
        fused = fuse_results(text_results, image_results)

        return {
            "query": request.query,
            "results": fused
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(exc)}")