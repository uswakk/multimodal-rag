import os
import time
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = "image_embeddings"


def get_client(retries: int = 10, delay: float = 1.0):
    for attempt in range(1, retries + 1):
        try:
            client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
            client.get_collections()
            return client
        except Exception as exc:
            if attempt == retries:
                raise
            print(f"Qdrant connection attempt {attempt}/{retries} failed: {exc}")
            time.sleep(delay)


def create_collection(vector_size=512):
    client = get_client()
    collections = client.get_collections().collections

    if any(c.name == COLLECTION_NAME for c in collections):
        print(f"Collection '{COLLECTION_NAME}' already exists. Skipping recreation.")
        return

    print(f"Creating collection '{COLLECTION_NAME}'...")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
    )


def upload_embeddings(embeddings, image_paths, metadata):
    client = get_client()
    import numpy as np
    import uuid
    points = []

    for i, emb in enumerate(embeddings):
        vector = np.array(emb).flatten().tolist()
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "type": "image",
                    "image_path": image_paths[i],
                    "page": metadata[i]["page"],
                    "source": metadata[i]["source"]
                }
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)
