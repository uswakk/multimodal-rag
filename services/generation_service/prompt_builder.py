from typing import List, Dict, Any


CHAT_PHRASES = [
    "hi", "hello", "hey", "how are you",
    "good morning", "good evening"
]



GENERIC_QUERY_PHRASES = [
    "what is in this document",
    "what is this document",
    "what does this say",
    "summarize this",
    "give me a summary",
    "overview of this",
]

GENERIC_QUERY_PHRASES = [
    "what is in this document",
    "what is this document",
    "what does this say",
    "summarize this",
    "give me a summary",
    "overview of this",
]

def _is_generic_query(query: str) -> bool:
    q = (query or "").strip().lower()
    if not q:
        return True
    # Don't treat short factual questions as generic
    for phrase in GENERIC_QUERY_PHRASES:
        if phrase in q:
            return True
    return False

def _is_chat_query(query: str) -> bool:
    q = (query or "").strip().lower()
    return any(phrase in q for phrase in CHAT_PHRASES)

def build_prompt(query: str, text_chunks: List[Dict[str, Any]], relevance_threshold: float = 0.25) -> str:

    # -----------------------------
    # 1. Format context
    # -----------------------------
    context = ""
    max_score = 0

    for i, chunk in enumerate(text_chunks):
        chunk_text = chunk.get("text", "")
        source = chunk.get("source", "Unknown")
        page = chunk.get("page")
        score = float(chunk.get("score", 0))

        max_score = max(max_score, score)

        context += f"""
[Chunk {i+1}]
Source: {source} | Page: {page} | Score: {score:.2f}
{chunk_text}
""".strip() + "\n\n"

    has_context = len(context.strip()) > 0
    low_relevance = max_score < relevance_threshold

    # -----------------------------
    # CASE 1: Chat / Greeting
    # -----------------------------
    if _is_chat_query(query):
        return f"""
You are a friendly AI assistant.

The user said: "{query}"

Respond naturally and conversationally.
Do not mention documents or context.
""".strip()

    # -----------------------------
    # CASE 2: Generic query → summary
    # -----------------------------
    if _is_generic_query(query) and has_context:
        return f"""
You are a helpful AI assistant.

The user is asking for a general understanding.

Using the context below:
- Provide a concise summary (5–8 bullet points)
- Focus on key ideas
- Use context primarily, but you may fill small gaps with general knowledge

---------------- CONTEXT ----------------
{context}
----------------------------------------
""".strip()

    # -----------------------------
    # CASE 3: Weak retrieval
    # -----------------------------
    if not has_context or low_relevance:
        return f"""
        You are a knowledgeable AI assistant.

        The user asked: "{query}"

        No relevant document context was found. Answer using your general knowledge.
        Be concise and factual. Do not mention documents or context.
        """.strip()

    # -----------------------------
    # CASE 4: Normal QA (best case)
    # -----------------------------
    return f"""
You are a helpful AI assistant.

Answer the question using the context below.

Guidelines:
- Use context as the primary source
- You may use general knowledge to improve clarity
- If unsure, say "I don't know based on the provided context"
- Keep answers clear and concise

---------------- CONTEXT ----------------
{context}
----------------------------------------

Question: {query}

Answer:
""".strip()