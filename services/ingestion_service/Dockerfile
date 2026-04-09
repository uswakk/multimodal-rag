FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for pymupdf/fitz if necessary (slim needs some)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir fastapi uvicorn requests pymupdf

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
