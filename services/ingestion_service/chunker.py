def chunk_text(text, chunk_size=300, overlap=50):
    """
    Splits text into chunks with overlap.

    Args:
        text (str): full text
        chunk_size (int): number of words per chunk
        overlap (int): number of overlapping words

    Returns:
        List of text chunks
    """

    words = text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size

        chunk = words[start:end]
        chunks.append(" ".join(chunk))

        # Move forward but keep overlap
        start += chunk_size - overlap

    return chunks

