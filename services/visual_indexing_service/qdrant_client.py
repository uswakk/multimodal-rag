import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(
    host=os.getenv("QDRANT_HOST", "localhost"),
    port=int(os.getenv("QDRANT_PORT", 6333))
)

COLLECTION_NAME = "image_embeddings"

def create_collection(vector_size=512):
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
    import numpy as np
    import uuid
    from qdrant_client.models import PointStruct
    points = []

    for i, emb in enumerate(embeddings):
        # Flatten to 1D regardless of nesting depth, then convert to Python floats
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