# Multimodal RAG
# Commands

## Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

## Start Ingestion Service
venv/Scripts/activate
uvicorn services.ingestion_service.main:app --port 8001 --reload

## Start Text Indexing Service
venv/Scripts/activate
uvicorn services.text_indexing_service.main:app --port 8002 --reload
