# sentiment_service.py

import os
import gc

# Configurar PyTorch para usar CPU y optimizar memoria
# Esto reduce significativamente el uso de RAM (optimizado para Render 512MB)
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Deshabilitar CUDA completamente
os.environ["OMP_NUM_THREADS"] = "1"  # Limitar threads de OpenMP
os.environ["MKL_NUM_THREADS"] = "1"  # Limitar threads de MKL

# No importamos pysentimiento a nivel de módulo para evitar cargas pesadas
# (p. ej. transformers) cuando se importa este módulo. Inicializaremos el
# analizador de forma perezosa (lazy) en la primera petición.
sentiment_analyzer = None

def get_analyzer():
    """Devuelve una instancia singleton del analizador, inicializándolo
    en la primera llamada con optimizaciones de memoria."""
    global sentiment_analyzer
    if sentiment_analyzer is None:
        # Importar aquí para evitar cargar transformers al inicio
        import torch
        from pysentimiento import create_analyzer
        
        # Configurar PyTorch para usar menos memoria (optimizado para Render 512MB)
        # Desactivar gradientes en inference (no los necesitamos)
        torch.set_grad_enabled(False)
        
        # Limitar threads de CPU para reducir uso de memoria
        # En Render free tier, es mejor usar menos threads
        torch.set_num_threads(1)
        
        # Inicializar el analizador (costoso) sólo cuando se necesite.
        # CUDA ya está deshabilitado en las variables de entorno del módulo
        # El modelo se carga en CPU automáticamente (CUDA deshabilitado)
        sentiment_analyzer = create_analyzer(task="sentiment", lang="es")
        
        # Asegurar que el modelo esté en modo evaluación (no entrenamiento)
        # Esto reduce el uso de memoria
        if hasattr(sentiment_analyzer, 'model'):
            sentiment_analyzer.model.eval()
            # Forzar modo no training para ahorrar memoria
            for param in sentiment_analyzer.model.parameters():
                param.requires_grad = False
        
        # Forzar limpieza de memoria después de cargar
        gc.collect()
    return sentiment_analyzer

def map_sentiment_to_stars(probabilities: dict, label: str) -> int:
    if label == 'NEU':
        return 3
    if label == 'POS':
        prob_pos = probabilities.get('POS', 0.0)
        if prob_pos > 0.90:
            return 5
        return 4
        
    if label == 'NEG':
        prob_neg = probabilities.get('NEG', 0.0)
        if prob_neg > 0.90:
            return 1
        return 2
        
    return 3


def analyze_review_sentiment(review_text: str) -> dict:
    """Analiza el sentimiento de una reseña con optimizaciones de memoria."""
    # Importamos el preprocesador localmente para no cargarlo en la
    # importación del módulo principal.
    from pysentimiento.preprocessing import preprocess_tweet

    analyzer = get_analyzer()
    processed_text = preprocess_tweet(review_text)
    analysis_result = analyzer.predict(processed_text)
    sentiment_label = analysis_result.output
    sentiment_probabilities = analysis_result.probas
    star_rating = map_sentiment_to_stars(sentiment_probabilities, sentiment_label)
    
    result = {
        "review_data": {
            "text_original": review_text,
            "text_processed": processed_text
        },
        "sentiment_analysis": {
            "label": sentiment_label,  # Ej: "POS", "NEG", "NEU"
            "score_1_to_5": star_rating, # Ej: 5
            "probabilities": {
                "positive": round(sentiment_probabilities.get('POS', 0.0) * 100, 2), # %
                "negative": round(sentiment_probabilities.get('NEG', 0.0) * 100, 2), # %
                "neutral": round(sentiment_probabilities.get('NEU', 0.0) * 100, 2)  # %
            }
        },
        "summary": {
            "puntuacion_estrellas": f"{star_rating}/5 ⭐",
            "polaridad_completa": {
                "POS": "Positiva" if sentiment_label == 'POS' else "No Positiva",
                "NEG": "Negativa" if sentiment_label == 'NEG' else "No Negativa",
                "NEU": "Neutral" if sentiment_label == 'NEU' else "No Neutral"
            }
        }
    }
    
    # Limpiar memoria después de procesar (opcional pero ayuda)
    # Solo hacerlo si el uso de memoria es crítico
    del analysis_result, processed_text
    gc.collect()
    
    return result