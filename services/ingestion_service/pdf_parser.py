import fitz
import os
from chunker import chunk_text


def is_valid_chunk(text):
    """
    Filter out garbage chunks that are mostly numeric or too short.
    """
    if not text or len(text.strip()) < 10:
        return False

    # Remove chunks that are mostly numeric (tables, coordinates, etc.)
    words = text.split()
    if len(words) < 3:
        return False

    # Count numeric characters
    numeric_chars = sum(c.isdigit() for c in text)
    if numeric_chars > len(text) * 0.5:  # More than 50% numeric
        return False

    return True


def extract_clean_text(page):
    """
    Extract clean text from PDF page using block-level extraction.
    Filters out tables, coordinates, and other garbage.
    """
    clean_blocks = []

    # Use block extraction for better control
    blocks = page.get_text("blocks")

    for block in blocks:
        if len(block) < 5:  # Ensure block has content
            continue

        text = block[4].strip()  # Text content is at index 4

        # Skip very short blocks
        if len(text) < 5:
            continue

        # Skip blocks that are mostly numeric (tables, coordinates)
        if sum(c.isdigit() for c in text) > len(text) * 0.7:
            continue

        # Skip blocks with too many special characters (likely OCR artifacts)
        special_chars = sum(not c.isalnum() and not c.isspace() for c in text)
        if special_chars > len(text) * 0.3:
            continue

        clean_blocks.append(text)

    return "\n".join(clean_blocks)


def extract_pdf_data(pdf_path: str, image_output_dir: str):
    """
    Extracts text chunks and image data (with page numbers) from a PDF.
    """
    doc = fitz.open(pdf_path)

    text_data = []
    image_data = []

    os.makedirs(image_output_dir, exist_ok=True)
    pdf_name = os.path.basename(pdf_path).split(".")[0]

    for page_number in range(len(doc)):
        page = doc[page_number]
        current_page_num = page_number + 1

        # --- 1. Extract Image (From every page) ---
        try:
            pix = page.get_pixmap()
            image_filename = f"{pdf_name}_page_{current_page_num}.png"
            image_path = os.path.join(image_output_dir, image_filename)
            pix.save(image_path)

            image_data.append({
                "image_path": image_path,
                "page": current_page_num,
                "source": pdf_name
            })
        except Exception as e:
            print(f"Warning: Could not extract image from page {current_page_num}: {e}")

        # --- 2. Extract Clean Text ---
        text = extract_clean_text(page)
        if not text:
            continue

        chunks = chunk_text(text)
        # Filter out invalid chunks
        valid_chunks = [chunk for chunk in chunks if is_valid_chunk(chunk)]

        for i, chunk in enumerate(valid_chunks):
            text_data.append({
                "page": current_page_num,
                "chunk_id": i,
                "text": chunk,
                "source": pdf_name
            })

    return text_data, image_data