# 🚀 Railway Master Dockerfile (Backend Liviano)
# -----------------------------------------------
# Optimizado para:
# - Carga ultra-rápida (Multi-stage build)
# - Extracción liviana (.doc con antiword y .jpg con tesseract)
# - Persistencia en volumen /data

# ETAPA 1: Builder (Compilación de librerías pesadas)
FROM python:3.11-slim as builder
WORKDIR /build

# Instalamos herramientas de compilación básicas
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalamos requerimientos en una carpeta temporal /install
# (Solo jala el archivo de la subcarpeta backend_railway)
COPY backend_railway/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ETAPA 2: Runtime (Imagen de ejecución final)
FROM python:3.11-slim
WORKDIR /app

# 1. Instalamos solo dependencias de ejecución esenciales
# Antiword (<1MB) para .doc antiguos
# Tesseract + Español unicamente para OCR liviano
# libpq5 para la conexión a base de datos PostgreSQL
RUN apt-get update && apt-get install -y \
    antiword \
    tesseract-ocr \
    tesseract-ocr-spa \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# 2. Copiamos los paquetes de Python ya instalados del builder (ahorra tiempo masivo)
COPY --from=builder /install /usr/local

# 3. Copiamos TODO el contenido de backend_railway al contenedor raíz
COPY backend_railway/ .

# 4. Variables de entorno globales del contenedor
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 5. Puerto dinámico Railway e inicio del servidor
# (Inyectamos $PORT automáticamente con gunicorn)
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT app21:app"]
