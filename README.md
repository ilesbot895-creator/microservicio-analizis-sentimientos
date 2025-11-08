# Microservicio de Análisis de Sentimientos

API mínima para evaluar el sentimiento de reseñas en español usando pysentimiento.

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución Local

```bash
python main.py
```

O directamente con uvicorn:

```bash
uvicorn main:app --reload
```

## Despliegue en Render

### Configuración en Render:

1. **Build Command:**
   ```
   pip install -r requirements.txt
   ```

2. **Start Command:**
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

   **Importante:** Debes usar este comando exacto con `--host 0.0.0.0` y `--port $PORT` para que Render pueda detectar el puerto correctamente.

## Endpoints

- `POST /analyze-sentiment` - Analizar el sentimiento de una reseña
- `GET /health` - Health check del servicio

## Uso

```bash
curl -X POST "http://localhost:8000/analyze-sentiment" \
  -H "Content-Type: application/json" \
  -d '{"review_text": "Me encantó este producto, es excelente!"}'
```

