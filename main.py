# main.py

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any
import os

from sentiment_service import analyze_review_sentiment

app = FastAPI(
    title="Microservicio de Análisis de Sentimientos",
    version="1.0.0",
    description="API mínima para evaluar el sentimiento de reseñas en español usando pysentimiento.",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Sirve la página de inicio."""
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    else:
        return HTMLResponse(content="""
        <html>
            <head><title>PySentiment</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0;">
                <div>
                    <h1 style="font-size: 4rem; margin-bottom: 1rem;">PySentiment</h1>
                    <p style="font-size: 1.5rem;">Análisis de Sentimientos en Español</p>
                </div>
            </body>
        </html>
        """)


class Review(BaseModel):
    review_text: str
    
@app.post("/analyze-sentiment", response_model=Dict[str, Any])
async def analyze_sentiment(review: Review):
    result = analyze_review_sentiment(review.review_text)
    
    return result

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Sentiment Analyzer"}


if __name__ == "__main__":
    # Ejecutar con uvicorn cuando se lance directamente: `python main.py`
    import uvicorn
    import os

    # Obtener el puerto de la variable de entorno PORT (para Render, Heroku, etc.)
    # Si no existe, usar 8000 como valor por defecto para desarrollo local
    port = int(os.environ.get("PORT", 8000))
    
    # Detectar si estamos en producción (Render, Heroku, etc.) o en desarrollo local
    # Si existe PORT, estamos en producción y usamos 0.0.0.0 para acceso externo
    # Si no existe PORT, estamos en local y usamos 127.0.0.1
    if os.environ.get("PORT"):
        # Producción: usar 0.0.0.0 para que sea accesible desde fuera
        host = os.environ.get("HOST", "0.0.0.0")
    else:
        # Desarrollo local: usar 127.0.0.1 (localhost)
        host = os.environ.get("HOST", "127.0.0.1")

    # Nota: hemos desactivado la UI de documentación automática en la instancia
    # de FastAPI (docs_url/redoc_url/openapi_url = None), por lo que /docs y
    # /redoc no estarán disponibles.
    # Usamos reload=False para evitar problemas de recarga que importen
    # módulos en procesos hijos (que pueden forzar la carga de dependencias
    # pesadas como transformers tijdens el spawn).
    # Configuración optimizada para usar menos memoria:
    # - workers=1: Un solo worker para reducir uso de RAM
    # - loop="asyncio": Usar el loop de asyncio estándar (más eficiente en memoria)
    # - limit_concurrency: Limitar conexiones concurrentes
    uvicorn.run(
        "main:app", 
        host=host, 
        port=port, 
        reload=False,
        workers=1,  # Un solo worker para reducir memoria (Render free tier)
        loop="asyncio",
        log_level="info"
    )