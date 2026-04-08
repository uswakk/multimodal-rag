from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from .embedder import embed_text

app = FastAPI()


class TextRequest(BaseModel):
    texts: List[str]


@app.post("/embed")
def embed(request: TextRequest):
    embeddings = embed_text(request.texts)

    return {
        "embeddings": embeddings.tolist()
    }