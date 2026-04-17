from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import os
import time

def get_client(retries: int = 10, delay: float = 1.0):
    for attempt in range(1, retries + 1):
        try:
            client = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))
            client.get_collections()
            return client
        except Exception as exc:
            if attempt == retries:
                raise
            print(f"Qdrant connection attempt {attempt}/{retries} failed: {exc}")
            time.sleep(delay)

client = get_client()
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

COLLECTION_NAME = "documents"

def search_text(query: str, top_k: int = 5):

    query_vector = model.encode(query).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    )

    formatted = []

    for r in results.points:
        formatted.append({
            "type": "text",
            "score": r.score,
            "text": r.payload.get("text"),
            "page": r.payload.get("page"),
            "source": r.payload.get("source")
        })

    return formatted