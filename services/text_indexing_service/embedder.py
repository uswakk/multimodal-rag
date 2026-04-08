from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

# Load model once (IMPORTANT)
try:
    model = SentenceTransformer("BAAI/bge-small-en-v1.5")
    logger.info("Sentence transformer model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load sentence transformer model: {str(e)}")
    raise


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