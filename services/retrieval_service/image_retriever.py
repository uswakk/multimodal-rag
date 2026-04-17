from qdrant_client import QdrantClient
from transformers import CLIPProcessor, CLIPModel
import torch
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
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

COLLECTION_NAME = "image_embeddings"

def search_images(query: str, top_k: int = 5):

    inputs = processor(text=[query], return_tensors="pt")

    with torch.no_grad():
        text_features = model.get_text_features(**inputs)

    query_vector = text_features[0].cpu().numpy().tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    )

    formatted = []

    for r in results.points:
        formatted.append({
            "type": "image",
            "score": r.score,
            "image_path": r.payload.get("image_path"),
            "page": r.payload.get("page"),
            "source": r.payload.get("source")
        })

    return formatted