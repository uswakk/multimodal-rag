from typing import List, Dict, Any


def build_prompt(query: str, text_chunks: List[Dict[str, Any]]) -> str:
    """
    Builds a clean prompt for the LLM using retrieved context + user query.
    This is PURE string processing (no model loading).
    """

    # -----------------------------
    # 1. Format context chunks
    # -----------------------------
    context = ""

    for i, chunk in enumerate(text_chunks):
        # Expecting chunk like: {"text": "...", "source": "..."}
        chunk_text = chunk.get("text", "")

        context += f"[Chunk {i+1}]\n{chunk_text}\n\n"

    # -----------------------------
    # 2. Build final prompt
    # -----------------------------
    prompt = f"""
You are a helpful AI assistant.

Use the following context to answer the question.
If the answer is not in the context, say you don't know.

---------------- CONTEXT ----------------
{context}
----------------------------------------

Question: {query}

Answer clearly and concisely:
""".strip()

    return prompt