import fitz
import os
from .chunker import chunk_text


def extract_pdf_data(pdf_path: str, image_output_dir: str):

    doc = fitz.open(pdf_path)

    text_data = []
    image_paths = []

    os.makedirs(image_output_dir, exist_ok=True)

    pdf_name = os.path.basename(pdf_path).split(".")[0]

    for page_number in range(len(doc)):
        page = doc[page_number]

        # --- Extract Text ---
        text = page.get_text().strip()

        if not text:
            continue

        chunks = chunk_text(text)

        for i, chunk in enumerate(chunks):
            text_data.append({
                "page": page_number + 1,
                "chunk_id": i,
                "text": chunk,
                "source": pdf_name
            })

        # --- Extract Image ---
        pix = page.get_pixmap()
        image_path = os.path.join(
            image_output_dir,
            f"{pdf_name}_page_{page_number+1}.png"
        )
        pix.save(image_path)

        image_paths.append(image_path)

    return text_data, image_paths