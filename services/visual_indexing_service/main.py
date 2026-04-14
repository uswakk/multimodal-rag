import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from image_embedder import embed_images
from qdrant_client import upload_embeddings, create_collection

app = FastAPI()

# Initialize collection at startup (non-fatal if Qdrant isn't up yet)
try:
    create_collection()
except Exception as e:
    print(f"WARNING: Could not initialize Qdrant collection at startup: {e}")
    print("Requests will fail until Qdrant is available.")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    import json
    print("\n--- VALIDATION ERROR ---")
    print(f"Body: {await request.body()}")
    print(f"Error details: {json.dumps(exc.errors(), indent=2)}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(await request.body())},
    )

class ImageRequest(BaseModel):
    image_paths: List[str]
    metadata: List[dict]

@app.post("/embed-images")
def embed_images_endpoint(request: ImageRequest):
    print("\n--- NEW EMBEDDING REQUEST ---")
    print("STEP 1: Request received")
    
    # --- Verify paths ---
    for path in request.image_paths:
        print(f"STEP 2: Checking image path: {path}")
        if not os.path.exists(path):
            error_msg = f"Image file not found at: {os.path.abspath(path)}"
            print(f"ERROR: {error_msg}")
            raise HTTPException(status_code=404, detail=error_msg)

    print("STEP 3: Before embedding")
    try:
        embeddings = embed_images(request.image_paths)
        print("STEP 4: After embedding")
    except Exception as e:
        error_msg = f"Model embedding failed: {str(e)}"
        print(f"ERROR: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

    print("STEP 5: Before Qdrant insert")
    try:
        upload_embeddings(embeddings, request.image_paths, request.metadata)
        print("STEP 6: Done")
    except Exception as e:
        error_msg = f"Qdrant storage failed: {str(e)}"
        print(f"ERROR: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

    return {
        "status": "success",
        "message": "Image embeddings stored successfully",
        "count": len(embeddings)
    }