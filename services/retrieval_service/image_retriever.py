from qdrant_client import QdrantClient
from transformers import CLIPProcessor, CLIPModel
import torch

client = QdrantClient(host="localhost", port=6333)

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

COLLECTION_NAME = "image_embeddings"

def search_images(query: str, top_k: int = 5):

    inputs = processor(text=[query], return_tensors="pt")

    with torch.no_grad():
        text_features = model.get_text_features(**inputs)

    query_vector = text_features[0].cpu().numpy().tolist()

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )

    formatted = []

    for r in results:
        formatted.append({
            "type": "image",
            "score": r.score,
            "image_path": r.payload.get("image_path"),
            "page": r.payload.get("page"),
            "source": r.payload.get("source")
        })

    return formatted