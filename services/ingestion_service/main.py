from fastapi import FastAPI, UploadFile, File
import os
import requests
from .pdf_parser import extract_pdf_data
from fastapi.responses import HTMLResponse

app = FastAPI()

UPLOAD_DIR = "data/raw_pdfs"
IMAGE_DIR = "data/images"

EMBEDDING_SERVICE_URL = "http://localhost:8002/embed"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF → extract text + images → send chunks to embedding service
    """

    try:
        # --- Save file ---
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        # --- Extract text + images ---
        text_data, image_paths = extract_pdf_data(file_path, IMAGE_DIR)

        # --- Extract only text for embedding ---
        texts = [item["text"] for item in text_data]

        # --- Call embedding service ---
        response = requests.post(
            EMBEDDING_SERVICE_URL,
            json={"texts": texts}
        )

        # Check if request failed
        if response.status_code != 200:
            return {
                "error": "Embedding service failed",
                "details": response.text
            }

        embeddings = response.json()["embeddings"]

        # --- Attach embeddings back ---
        for i, item in enumerate(text_data):
            item["embedding"] = embeddings[i]

        # --- Return summary (not full data to avoid overload) ---
        return {
            "message": "PDF processed successfully",
            "pages_processed": len(set([item["page"] for item in text_data])),
            "total_chunks": len(text_data),
            "images_saved": len(image_paths)
        }

    except Exception as e:
        return {
            "error": str(e)
        }