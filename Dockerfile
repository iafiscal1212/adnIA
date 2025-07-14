# Dockerfile optimizado para GPU en Google Cloud Run

# Usamos una imagen base oficial de NVIDIA con CUDA 12.1.1
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# Evitar que los instaladores pidan confirmación interactiva
ENV DEBIAN_FRONTEND=noninteractive

# Instalar Python 3.11, pip y otras dependencias del sistema
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    python3.11-dev \
    gcc \
    g++ \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Establecer python3.11 como el python por defecto
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Establecer directorio de trabajo
WORKDIR /app

# Copiar el archivo de requerimientos primero para aprovechar el caché de Docker
COPY requirements.txt .

# Instalar las dependencias de Python
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto en el que Gunicorn escuchará
EXPOSE 8080

# Comando para ejecutar la aplicación
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "--timeout", "0", "app:app"]
