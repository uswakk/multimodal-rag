def build_prompt(query, text_chunks):

    context = "\n\n".join([
        f"[Page {c['page']}] {c['text']}"
        for c in text_chunks
    ])

    prompt = f"""
You are a document QA assistant.

Use ONLY the provided context.

Context:
{context}

Question:
{query}

Instructions:
- Answer clearly
- Cite page numbers
- If not found, say "Not enough information"
"""

    return prompt