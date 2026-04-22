from sentence_transformers import SentenceTransformer

# Load model once (IMPORTANT)
# Upgraded from BAAI/bge-small-en-v1.5 (384-dim) to BAAI/bge-base-en-v1.5 (768-dim)
model = SentenceTransformer("BAAI/bge-base-en-v1.5")


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