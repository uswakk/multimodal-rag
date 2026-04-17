import os
import time
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")


def get_client(retries: int = 10, delay: float = 1.0):
    for attempt in range(1, retries + 1):
        try:
            client = QdrantClient(url=QDRANT_URL)
            client.get_collections()
            return client
        except Exception as exc:
            if attempt == retries:
                raise
            print(f"Qdrant connection attempt {attempt}/{retries} failed: {exc}")
            time.sleep(delay)


def create_collection(collection_name: str, vector_size: int):
    client = get_client()
    collections = client.get_collections().collections
    if any(c.name == collection_name for c in collections):
        print(f"Collection '{collection_name}' already exists. Skipping recreation.")
        return

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE
        )
    )


def store_embeddings(collection_name: str, text_data: list):
    client = get_client()
    import uuid
    points = []

    for item in text_data:
        vector_data = item["embedding"].tolist() if hasattr(item["embedding"], "tolist") else item["embedding"]
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector_data,
                payload={
                    "text": item["text"],
                    "page": item["page"],
                    "chunk_id": item["chunk_id"],
                    "source": item["source"]
                }
            )
        )

    client.upsert(
        collection_name=collection_name,
        points=points
    )