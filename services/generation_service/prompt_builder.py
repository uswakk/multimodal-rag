from typing import List, Dict, Any


def build_prompt(query: str, text_chunks: List[Dict[str, Any]]) -> str:
    """
    Builds a clean prompt for the LLM using retrieved context + user query.
    This is PURE string processing (no model loading).
    """

    # -----------------------------
    # 1. Format context chunks with source information
    # -----------------------------
    context = ""

    for i, chunk in enumerate(text_chunks):
        # Expecting chunk like: {"text": "...", "source": "...", "page": "..."}
        chunk_text = chunk.get("text", "")
        source = chunk.get("source", "Unknown source")
        page = chunk.get("page")
        
        source_info = f"[Source: {source}"
        if page is not None:
            source_info += f", Page: {page}"
        source_info += "]"

        context += f"[Chunk {i+1}] {source_info}\n{chunk_text}\n\n"

    # -----------------------------
    # 2. Build final prompt
    # -----------------------------
    prompt = f"""
You are a helpful AI assistant.

Use the following context to answer the question.
If the answer is not in the context, say you don't know.
When answering, cite the source(s) you used.

---------------- CONTEXT ----------------
{context}
----------------------------------------

Question: {query}

Answer clearly and concisely, citing your sources:
""".strip()

    return prompt