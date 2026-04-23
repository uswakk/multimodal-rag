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


def _is_chat_query(query: str) -> bool:
    q = (query or "").strip().lower()
    return any(phrase in q for phrase in CHAT_PHRASES)


def _is_generic_query(query: str) -> bool:
    q = (query or "").strip().lower()
    if not q:
        return True
    for phrase in GENERIC_QUERY_PHRASES:
        if phrase in q:
            return True
    return False


def _is_visual_query(query: str) -> bool:
    visual_keywords = [
        "color", "colour", "look", "image", "picture", "photo",
        "show", "visible", "wearing", "dressed", "appearance",
        "shape", "diagram", "chart", "graph", "figure", "illustration"
    ]
    q = query.lower()
    return any(kw in q for kw in visual_keywords)


def build_prompt(
    query: str,
    text_chunks: List[Dict[str, Any]],
    image_chunks: List[Dict[str, Any]] = [],
    relevance_threshold: float = 0.25
) -> str:

    # -----------------------------
    # 1. Format text context
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
    has_images = len(image_chunks) > 0
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
    # CASE 2: Visual query with images
    # -----------------------------
    if has_images and (has_images or _is_visual_query(query)):
        image_note = f"{len(image_chunks)} relevant image(s) from the document are attached."
        context_section = f"""
Additional text context from the document:
---------------- CONTEXT ----------------
{context}
----------------------------------------
""".strip() if has_context else ""

        return f"""
You are a helpful AI assistant with vision capabilities.

The user is asking about something visual in a document.
{image_note}

Instructions:
- Look at the attached image(s) carefully
- Answer based on what is visually present in the image(s)
- If the answer is clearly visible, describe it precisely (e.g. colors, shapes, labels)
- If the image does not contain enough information, say so honestly
- Do not guess or hallucinate details not visible in the image

{context_section}

Question: {query}

Answer:
""".strip()

    # -----------------------------
    # CASE 3: Generic query → summary
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
    # CASE 4: Weak retrieval → general knowledge
    # -----------------------------
    if not has_context or low_relevance:
        return f"""
You are a knowledgeable AI assistant.

The user asked: "{query}"

No relevant document context was found. Answer using your general knowledge.
Be concise and factual. Do not mention documents or context.
""".strip()

    # -----------------------------
    # CASE 5: Normal QA (best case)
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