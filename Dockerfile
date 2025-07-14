# Dockerfile para ADNIA en Google Cloud Platform
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p uploads temp

# Configurar variables de entorno
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Exponer el puerto
EXPOSE 8080

# Comando para ejecutar la aplicación, optimizado para Cloud Run
# Se recomienda 1 worker y gestionar la concurrencia a nivel de instancia.
# Threads puede ser ajustado según la naturaleza de la carga (I/O vs CPU bound).
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "--timeout", "0", "app:app"]

