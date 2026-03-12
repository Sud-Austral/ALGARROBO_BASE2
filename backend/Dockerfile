# Backend Dockerfile
FROM python:3.11-slim

# Install system dependencies for LibreOffice and Tesseract
RUN apt-get update && apt-get install -y \
    libreoffice-writer \
    libreoffice-calc \
    tesseract-ocr \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV SOFFICE_PATH=/usr/bin/soffice

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app21:app"]
