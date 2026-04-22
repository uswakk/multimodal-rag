from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import os
import time
import re

# ----------------------------
# Retry connection to Qdrant
# ----------------------------
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

# Strong embedding model
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

COLLECTION_NAME = "documents"

# ----------------------------
# 🧹 CLEANING FUNCTION
# ----------------------------
def is_valid_chunk(text: str) -> bool:
    """
    Removes garbage chunks like:
    - numbers only
    - references
    - short meaningless text
    """
    if len(text.strip()) < 50:
        return False

    # Too many digits → probably table
    digit_ratio = sum(c.isdigit() for c in text) / len(text)
    if digit_ratio > 0.4:
        return False

    # Remove references section
    if "doi" in text.lower() or "arxiv" in text.lower():
        return False

    return True


# ----------------------------
# 🔍 QUERY EXPANSION
# ----------------------------
def expand_query(query: str) -> str:
    """
    Makes vague queries more specific
    """
    query = query.lower()

    if "what is" in query:
        return query + " definition explanation overview"

    if "key findings" in query or "summary" in query:
        return query + " main contributions results conclusions"

    return query


# ----------------------------
# 🔍 MAIN SEARCH
# ----------------------------
def search_text(query: str, top_k: int = 10):

    # Expand vague queries
    expanded_query = expand_query(query)

    # Embed
    query_vector = model.encode(expanded_query).tolist()

    # Fetch more candidates (important for reranking)
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k * 3   # get more → filter later
    )

    formatted = []

    for r in results.points:
        text = r.payload.get("text", "")

        # Filter bad chunks
        if not is_valid_chunk(text):
            continue

        formatted.append({
            "type": "text",
            "score": r.score,
            "text": text,
            "page": r.payload.get("page"),
            "source": r.payload.get("source")
        })

    # Return best k after filtering
    return formatted[:top_k]