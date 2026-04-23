from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import os
import time
import re

# ----------------------------
# Qdrant Connection
# ----------------------------
def get_client(retries=10, delay=1.0):
    for i in range(retries):
        try:
            client = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))
            client.get_collections()
            return client
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(delay)

client = get_client()
# Upgraded from BAAI/bge-small-en-v1.5 (384-dim) to BAAI/bge-base-en-v1.5 (768-dim)
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

COLLECTION_NAME = "documents"

# ----------------------------
# 🔍 INTENT DETECTION
# ----------------------------
def detect_intent(query: str):
    q = query.lower()

    if "what is" in q or len(q.split()) <= 2:
        return "definition"

    if "summary" in q or "key findings" in q:
        return "summary"

    return "general"


# ----------------------------
# 🔍 QUERY EXPANSION
# ----------------------------
def expand_query(query: str, intent: str):
    if intent == "definition":
        return query + " definition explanation introduction overview"

    if intent == "summary":
        return query + " summary key contributions results conclusion abstract"

    return query


# ----------------------------
# 🧹 STRONG FILTER
# ----------------------------
def is_valid_chunk(text: str):
    text = text.strip()
    if len(text) < 30:          # was 40 — only kill truly empty fragments
        return False
    digit_ratio = sum(c.isdigit() for c in text) / len(text)
    if digit_ratio > 0.35:      # was 0.25 — a bit more tolerant
        return False
    # Only reject if it's purely a figure caption, not just mentions "figure"
    if re.match(r"^(figure|fig\.)\s*\d+", text.lower()):
        return False
    if "doi:" in text.lower() or "arxiv:" in text.lower():
        return False
    return True


# ----------------------------
# ⭐ SCORE BOOSTING
# ----------------------------
def boost_score(text: str, score: float, intent: str):

    text_lower = text.lower()

    # Boost definition-like sentences
    if intent == "definition":
        if "is a" in text_lower or "is an" in text_lower:
            score += 0.15
        if "we present" in text_lower:
            score += 0.1

    # Boost summary-like sentences
    if intent == "summary":
        if "we show" in text_lower or "results show" in text_lower:
            score += 0.15
        if "this paper" in text_lower:
            score += 0.1

    return score


# ----------------------------
# 🔍 SEARCH FUNCTION
# ----------------------------
def search_text(query: str, top_k: int = 5):

    intent = detect_intent(query)

    expanded_query = expand_query(query, intent)

    query_vector = model.encode(expanded_query).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k * 5   # fetch more → filter later
    )

    filtered = []

    for r in results.points:
        text = r.payload.get("text", "")

        if not is_valid_chunk(text):
            continue

        score = boost_score(text, r.score, intent)

        filtered.append({
            "type": "text",
            "score": score,
            "text": text,
            "page": r.payload.get("page"),
            "source": r.payload.get("source")
        })

    # Sort AFTER boosting
    filtered.sort(key=lambda x: x["score"], reverse=True)

    return filtered[:top_k]