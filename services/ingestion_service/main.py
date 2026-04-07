from fastapi import FastAPI, UploadFile, File
import os
from pdf_parser import extract_pdf_data

app = FastAPI()

UPLOAD_DIR = "data/raw_pdfs"
IMAGE_DIR = "data/images"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF and process it
    """

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save uploaded file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Extract data
    text_data, image_paths = extract_pdf_data(file_path, IMAGE_DIR)

    return {
        "message": "PDF processed successfully",
        "pages": len(text_data),
        "images_saved": len(image_paths)
    }