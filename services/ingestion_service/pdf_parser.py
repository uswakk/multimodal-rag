import fitz
import os
from .chunker import chunk_text


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

        # --- 2. Extract Text ---
        text = page.get_text().strip()
        if not text:
            continue

        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            text_data.append({
                "page": current_page_num,
                "chunk_id": i,
                "text": chunk,
                "source": pdf_name
            })

    return text_data, image_data