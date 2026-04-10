FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install fastapi uvicorn qdrant-client sentence-transformers transformers torch torchvision

EXPOSE 8004

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
