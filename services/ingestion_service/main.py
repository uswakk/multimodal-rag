from fastapi import FastAPI, UploadFile, File
import os
import requests
from .pdf_parser import extract_pdf_data

app = FastAPI()

UPLOAD_DIR = "data/raw_pdfs"
IMAGE_DIR = "data/images"

EMBEDDING_SERVICE_URL = "http://localhost:8002/embed"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload PDF → extract text + images → send chunks to embedding service → store in Qdrant
    """

    try:
        # --- Save file ---
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        # --- Extract text + images ---
        text_data, image_paths = extract_pdf_data(file_path, IMAGE_DIR)

        # --- Prepare text + metadata ---
        texts = [item["text"] for item in text_data]

        metadata = [
            {
                "page": item["page"],
                "chunk_id": item["chunk_id"],
                "source": item["source"]
            }
            for item in text_data
        ]

        # --- Call embedding + storage service ---
        response = requests.post(
            EMBEDDING_SERVICE_URL,
            json={
                "texts": texts,
                "metadata": metadata
            }
        )

        # --- Handle failure ---
        if response.status_code != 200:
            return {
                "error": "Embedding service failed",
                "details": response.text
            }

        # --- Success response ---
        return {
            "message": "PDF processed and stored in vector DB successfully",
            "pages_processed": len(set([item["page"] for item in text_data])),
            "total_chunks": len(text_data),
            "images_saved": len(image_paths)
        }

    except Exception as e:
        return {
            "error": str(e)
        }