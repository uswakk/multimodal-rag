from sentence_transformers import SentenceTransformer

# Load model once (IMPORTANT)
# Using BAAI/bge-small-en-v1.5 — outputs 384-dim vectors
model = SentenceTransformer("BAAI/bge-small-en-v1.5")


def embed_text(text_list):
    """
    Convert list of text chunks into embeddings
    """

    embeddings = model.encode(text_list)

    return embeddings

if __name__ == "__main__":
    texts = [
        "Machine learning is powerful",
        "AI is transforming industries"
    ]

    embeddings = embed_text(texts)

    print(len(embeddings))
    print(len(embeddings[0]))  # vector size