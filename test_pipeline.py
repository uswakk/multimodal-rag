import requests
import time
import os

INGESTION_URL = "http://localhost:8001/upload"
GATEWAY_URL = "http://localhost:8000/ask"

def test_pipeline():
    print("=== Multimodal RAG Pipeline Test ===")
    
    # Check if data directory has a sample PDF
    pdf_path = "data/raw_pdfs/2312.00752v2.pdf"
    alt_pdf_path = "data/raw_pdfs/HRM.pdf"
    
    target_pdf = None
    if os.path.exists(pdf_path):
        target_pdf = pdf_path
    elif os.path.exists(alt_pdf_path):
        target_pdf = alt_pdf_path
        
    if not target_pdf:
        print(f"No sample PDF found in data/raw_pdfs/")
        return
        
    print(f"\n1. Testing Ingestion Service (Uploading {target_pdf})")
    try:
        with open(target_pdf, "rb") as f:
            files = {"file": (os.path.basename(target_pdf), f, "application/pdf")}
            response = requests.post(INGESTION_URL, files=files)
            
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        if response.status_code != 200:
            print("Ingestion failed. Stopping test.")
            return
    except Exception as e:
        print(f"Failed to connect to ingestion service: {e}")
        return
        
    print("\nWaiting 5 seconds for indexing to settle...")
    time.sleep(5)
    
    print("\n2. Testing API Gateway (Retrieval + Generation)")
    query = "What is this document about? Summarize its main topic."
    print(f"Query: '{query}'")
    
    try:
        response = requests.post(f"{GATEWAY_URL}?query={query}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Failed to connect to API gateway: {e}")

if __name__ == "__main__":
    test_pipeline()
