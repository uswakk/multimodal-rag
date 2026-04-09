FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install fastapi uvicorn torch torchvision pillow transformers qdrant-client

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]