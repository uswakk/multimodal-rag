import os
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.models import PointStruct

client = QdrantClient(
    url=os.getenv("QDRANT_URL", "http://localhost:6333")
)

def create_collection(collection_name: str, vector_size: int):
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