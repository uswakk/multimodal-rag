import fitz  # PyMuPDF
import os

def extract_pdf_data(pdf_path: str, image_output_dir: str):
    """
    Extract text and images from a PDF.

    Returns:
        text_data: list of dicts with page number + text
        image_paths: list of saved image file paths
    """

    # Open PDF
    doc = fitz.open(pdf_path)

    text_data = []
    image_paths = []

    # Create image directory if not exists
    os.makedirs(image_output_dir, exist_ok=True)

    # Loop through each page
    for page_number in range(len(doc)):
        page = doc[page_number]

        # --- Extract Text ---
        text = page.get_text()

        text_data.append({
            "page": page_number + 1,
            "text": text
        })

        # --- Extract Page Image (VERY IMPORTANT) ---
        pix = page.get_pixmap()
        image_path = os.path.join(image_output_dir, f"page_{page_number+1}.png")
        pix.save(image_path)

        image_paths.append(image_path)

    return text_data, image_paths