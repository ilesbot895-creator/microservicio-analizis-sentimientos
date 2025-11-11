# Dockerfile optimizado para bajo consumo de memoria (Render 512MB)
# Usa Python slim (más ligero que la imagen estándar)
FROM python:3.11-slim

# Configurar variables de entorno para optimizar memoria y FORZAR CPU
# También configuramos el caché de Hugging Face para usar local_storage
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:128" \
    TOKENIZERS_PARALLELISM="false" \
    CUDA_VISIBLE_DEVICES="" \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    PYTORCH_NO_CUDA_MEMORY_CACHING=1 \
    FORCE_CPU=1 \
    HF_HOME=/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/app/.cache/huggingface/transformers \
    HF_DATASETS_CACHE=/app/.cache/huggingface/datasets

# Instalar solo dependencias del sistema esenciales
# build-essential es necesario para compilar algunas dependencias de Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements primero para aprovechar el cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python sin cache para reducir tamaño
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 3. ¡PRE-DESCARGA EL MODELO! (La clave para evitar errores 429)
# Crear directorio de caché de Hugging Face y pre-descargar el modelo durante el build
# Esto evita que el modelo se descargue en runtime y previene errores 429 (rate limiting)
# Las variables de entorno HF_HOME, TRANSFORMERS_CACHE ya están configuradas arriba
RUN mkdir -p /app/.cache/huggingface && \
    python -c "from pysentimiento import create_analyzer; analyzer = create_analyzer(task='sentiment', lang='es'); print('✅ Modelo pre-descargado exitosamente en /app/.cache/huggingface')"

# Copiar el resto de la aplicación
COPY . .

# Exponer el puerto (default 8000, pero se puede cambiar con PORT)
EXPOSE 8000

# Comando de inicio optimizado para bajo consumo de memoria
# FORZA uso de CPU (no GPU) con todas las variables de entorno
# Usa la variable PORT del entorno, o 8000 por defecto
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --loop asyncio"

