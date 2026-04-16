FROM python:3.10-slim

WORKDIR /app

# Prevent Python buffering + reduce size
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install minimal system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies (CPU ONLY)
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of code
COPY . .

# Run service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]