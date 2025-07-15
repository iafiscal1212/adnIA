# Dockerfile (Ajustado para unstructured)
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y \
    tesseract-ocr tesseract-ocr-spa libtesseract-dev poppler-utils libpoppler-dev libmagic-dev libjpeg-dev zlib1g-dev build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu  # Fix para unstructured si falla

FROM python:3.12-slim
COPY --from=builder /usr/local /usr/local
COPY --from=builder /usr/bin/tesseract /usr/bin/tesseract

WORKDIR /app
COPY . .
EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "--timeout", "300", "app:app"]
