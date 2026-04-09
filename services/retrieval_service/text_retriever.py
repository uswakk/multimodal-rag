from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

client = QdrantClient(host="localhost", port=6333)

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