# Multimodal RAG Pipeline

An intelligent document intelligence system using Text & Vision RAG. Powers retrieval-augmented generation with Qdrant vector database and Ollama LLMs.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Ollama](https://ollama.com/) (running locally)
- [Node.js](https://nodejs.org/) (for frontend)

## 🚀 Quick Start

### 1. Start Ollama Model
Ensure Ollama is running and pull the vision model:
```bash
ollama pull qwen3-vl:2b
```

### 2. Start Backend (Docker)
From the root directory, build and start the 7 microservices:
```bash
docker-compose up --build -d
```
All services will be available:
- **API Gateway**: [http://localhost:8006](http://localhost:8006) (Docs: [/docs](http://localhost:8006/docs))
- **Qdrant Dashboard**: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

### 3. Start Frontend
Navigate to the frontend directory, install dependencies, and run:
```bash
cd frontend
npm install
npm run dev
```
Open your browser at [http://localhost:5173](http://localhost:5173).

## 🛠 Model Testing & Timing
To test the LLM connectivity and generation speed locally:
```bash
cd services/generation_service
python testing_model.py
```
*Note: If running on CPU, the first token may take several minutes to generate.*

## 🐳 Docker Services Architecture
- `api_gateway`: Entry point for all requests.
- `ingestion_service`: Handles document uploads.
- `text_indexing_service`: Chunks and indexes text via SigLIP/BGE.
- `visual_indexing_service`: Extracts and indexes images from PDFs.
- `retrieval_service`: Unified multimodal retrieval.
- `generation_service`: Bridges to Ollama for final answer generation.
- `qdrant`: Vector database for all embeddings.
