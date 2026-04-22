from typing import List, Dict, Any


GENERIC_QUERY_PHRASES = [
    "what is in this document",
    "what is in this file",
    "what is this document",
    "what is this file",
    "what is in this",
    "what does this document say",
    "what does this file say",
    "what's in this document",
    "what's in this file",
    "summarize",
    "give me a summary",
]


def _is_generic_query(query: str) -> bool:
    q = (query or "").strip().lower()
    if not q:
        return True
    # short queries are often underspecified
    if len(q.split()) <= 3:
        return True
    for phrase in GENERIC_QUERY_PHRASES:
        if phrase in q:
            return True
    return False


def build_prompt(query: str, text_chunks: List[Dict[str, Any]], relevance_threshold: float = 0.25) -> str:
    """
    Builds a clean prompt for the LLM using retrieved context + user query.
    Adds heuristics to handle vague/generic queries and low-relevance retrievals.
    """

    # -----------------------------
    # 1. Format context chunks with source information
    # -----------------------------
    context = ""
    max_score = None

    for i, chunk in enumerate(text_chunks):
        # Expecting chunk like: {"text": "...", "source": "...", "page": "...", "score": 0.8}
        chunk_text = chunk.get("text", "")
        source = chunk.get("source", "Unknown source")
        page = chunk.get("page")
        score = chunk.get("score")

        if score is not None:
            try:
                s = float(score)
                max_score = s if (max_score is None or s > max_score) else max_score
            except Exception:
                pass

        source_info = f"[Source: {source}"
        if page is not None:
            source_info += f", Page: {page}"
        if score is not None:
            try:
                source_info += f", Score: {float(score):.3f}"
            except Exception:
                pass
        source_info += "]"

        context += f"[Chunk {i+1}] {source_info}\n{chunk_text}\n\n"

    # -----------------------------
    # 2. Decide prompt style based on query and retrieved relevance
    # -----------------------------
    is_generic = _is_generic_query(query)
    low_relevance = (max_score is not None and max_score < relevance_threshold)

    if is_generic:
        # Summarization-style prompt for document-level questions
        prompt = f"""
You are a helpful AI assistant.

The user asked a broad/generic question about a document and likely expects a high-level summary.
Using ONLY the context below, produce a concise summary (3-8 bullet points) of the content. Do not hallucinate. If the context is insufficient to summarize, state "I don't know based on the provided context." When summarizing, cite the source(s) used for each bullet if available.

---------------- CONTEXT ----------------
{context}
----------------------------------------

Task: Summarize the document(s) above clearly and concisely. Include source citations.
""".strip()

        return prompt

    # If not generic but retrieval seems low-quality, ask for clarification rather than guessing
    if low_relevance and (not context.strip()):
        prompt = f"""
You are a helpful AI assistant.

The user asked: {query}

You do not have enough relevant context to answer this question. Do not guess. Ask the user a clarifying question to better understand what they want (for example: do you want a summary, specific facts, or a page reference?). Keep the clarifying question short.
""".strip()

        return prompt

    # Default: standard QA prompt with clear directives
    prompt = f"""
You are a helpful AI assistant.

Use the following context to answer the question.
Use only information present in the context. If the answer is not in the context, say "I don't know based on the provided context." When answering, cite the source(s) you used.

---------------- CONTEXT ----------------
{context}
----------------------------------------

Question: {query}

Answer clearly and concisely, citing your sources:
""".strip()

    return prompt