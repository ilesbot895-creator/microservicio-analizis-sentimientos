# Optimizaciones de Memoria para Render (512 MB RAM)

Este documento describe las optimizaciones implementadas para reducir el uso de memoria RAM y permitir que el servicio funcione en el plan gratuito de Render (512 MB).

## Problema

`pysentimiento` utiliza modelos Transformer (BERT-like) que pueden consumir 300-500+ MB de RAM solo para cargar el modelo, más las dependencias (PyTorch, transformers, etc.), lo que puede exceder fácilmente el límite de 512 MB de Render.

## Optimizaciones Implementadas

### 1. Configuración de Uvicorn
- **Un solo worker** (`--workers 1`): Reduce el uso de memoria al evitar múltiples procesos
- **Loop asyncio**: Más eficiente en memoria que otros loops
- **Sin reload**: Evita procesos hijos que duplicarían el uso de memoria

### 2. Configuración de PyTorch
- **CPU only**: Deshabilitado CUDA completamente (`CUDA_VISIBLE_DEVICES=""`)
- **Gradientes deshabilitados**: `torch.set_grad_enabled(False)` para inference
- **Threads limitados**: `torch.set_num_threads(1)` y `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`
- **Modo evaluación**: Modelo en modo `eval()` con `requires_grad=False` en todos los parámetros

### 3. Variables de Entorno
```bash
PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:128"
TOKENIZERS_PARALLELISM="false"
CUDA_VISIBLE_DEVICES=""
OMP_NUM_THREADS="1"
MKL_NUM_THREADS="1"
```

### 4. Gestión de Memoria
- **Lazy loading**: El modelo se carga solo en la primera petición
- **Garbage collection**: Limpieza explícita después de cargar el modelo y procesar peticiones
- **Singleton pattern**: El modelo se carga una sola vez y se reutiliza

### 5. Carga Eficiente del Modelo
- El modelo se carga solo cuando se necesita (primera petición)
- Se asegura que esté en modo CPU y evaluación
- Se desactivan los gradientes para ahorrar memoria

## Uso de Memoria Esperado

Con estas optimizaciones, el uso de memoria debería ser aproximadamente:
- **FastAPI/Uvicorn**: ~50-80 MB
- **Modelo pysentimiento**: ~200-350 MB (dependiendo del modelo)
- **PyTorch/Transformers**: ~50-100 MB
- **Sistema operativo y otros**: ~50-80 MB
- **Total estimado**: ~350-610 MB

**Nota**: El uso real puede variar. Si aún excede 512 MB, considera:
1. Usar un modelo más pequeño (si pysentimiento lo permite)
2. Usar cuantización del modelo (si está disponible)
3. Actualizar a un plan de pago de Render

## Configuración en Render

### Start Command:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1 --loop asyncio
```

O usar el script `start.sh` que ya incluye todas las variables de entorno optimizadas.

## Monitoreo

Puedes monitorear el uso de memoria en Render desde el dashboard. Si ves que se acerca a 512 MB, las optimizaciones están funcionando correctamente.

## Notas Adicionales

- La primera petición puede tardar unos segundos mientras se carga el modelo
- Las peticiones subsiguientes serán más rápidas ya que el modelo ya está cargado
- El servicio está optimizado para CPU, por lo que las respuestas pueden ser un poco más lentas que con GPU, pero funcionará dentro del límite de memoria

