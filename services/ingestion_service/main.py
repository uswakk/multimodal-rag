from fastapi import FastAPI, UploadFile, File
import os
import requests
from pdf_parser import extract_pdf_data

app = FastAPI()

# Use absolute paths that match Docker volume mount
UPLOAD_DIR = "/app/data/raw_pdfs"
IMAGE_DIR = "/app/data/images"

TEXT_SERVICE_URL = os.getenv("TEXT_SERVICE_URL", "http://text_indexing_service:8000/embed")
VISUAL_SERVICE_URL = os.getenv("VISUAL_SERVICE_URL", "http://visual_indexing_service:8000/embed-images")

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

print(f"Ingestion Service started.")
print(f"Target Text Service: {TEXT_SERVICE_URL}")
print(f"Target Visual Service: {VISUAL_SERVICE_URL}")


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
        text_data, image_data = extract_pdf_data(file_path, IMAGE_DIR)

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

        # --- Call embedding services ---
        errors = []
        unique_pages = sorted(list(set([item["page"] for item in text_data])))

        # 1. Text Service
        if texts:
            try:
                text_response = requests.post(
                    TEXT_SERVICE_URL,
                    json={
                        "texts": texts,
                        "metadata": metadata
                    },
                    timeout=60
                )
                if text_response.status_code != 200:
                    errors.append(f"Text service error ({text_response.status_code}): {text_response.text}")
            except requests.exceptions.RequestException as e:
                errors.append(f"Text service connection failed: {str(e)}")

        # 2. Visual Service
        if image_data:
            image_paths = [item["image_path"] for item in image_data]
            image_meta = [
                {"page": item["page"], "source": item["source"]} 
                for item in image_data
            ]
            
            try:
                visual_response = requests.post(
                    VISUAL_SERVICE_URL,
                    json={
                        "image_paths": image_paths,
                        "metadata": image_meta
                    },
                    timeout=60
                )
                if visual_response.status_code != 200:
                    errors.append(f"Visual service error ({visual_response.status_code}): {visual_response.text}")
            except requests.exceptions.RequestException as e:
                errors.append(f"Visual service connection failed: {str(e)}")

        # --- Check for errors ---
        if errors:
            return {
                "status": "partial_failure" if len(errors) < (2 if image_data else 1) else "failure",
                "message": "Some services failed during processing",
                "errors": errors,
                "pages_processed": len(unique_pages),
                "total_chunks": len(text_data),
                "images_saved": len(image_data)
            }

        # --- Success response ---
        return {
            "status": "success",
            "message": "PDF processed and stored in vector DB successfully",
            "pages_processed": len(unique_pages),
            "total_chunks": len(text_data),
            "images_saved": len(image_data)
        }

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {
            "status": "error",
            "error": str(e)
        }