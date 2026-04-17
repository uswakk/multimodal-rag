from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from embedder import embed_text
from qdrant_database import create_collection, store_embeddings

app = FastAPI()

COLLECTION_NAME = "documents"


class TextRequest(BaseModel):
    texts: List[str]
    metadata: List[dict]


@app.post("/embed")
def embed(request: TextRequest):
    # Step 1 — Generate embeddings
    embeddings = embed_text(request.texts)

    # Step 2 — Create collection
    create_collection(COLLECTION_NAME, len(embeddings[0]))

    # Step 3 — Merge text + metadata + embeddings
    text_data = []
    for i in range(len(request.texts)):
        text_data.append({
            "text": request.texts[i],
            "embedding": embeddings[i],
            **request.metadata[i]
        })

    # Step 4 — Store in Qdrant
    store_embeddings(COLLECTION_NAME, text_data)

    return {"message": "Embeddings stored in Qdrant"}