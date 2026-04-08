from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.models import PointStruct

client = QdrantClient(
    url="http://localhost:6333"
)

def create_collection(collection_name: str, vector_size: int):
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE
        ),
        optimizer_config={
            "indexing_threshold": 0  # 🔥 FORCE INDEXING
        }
    )

def store_embeddings(collection_name: str, text_data: list):
    points = []

    for idx, item in enumerate(text_data):
        points.append(
            PointStruct(
                id=idx,
                vector=item["embedding"],
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