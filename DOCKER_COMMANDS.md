# Comandos Docker - PySentiment

## 🐳 Comandos para Ejecutar Docker

### 1. Construir la imagen Docker
```bash
docker build -t pysentiment .
```

### 2. Ejecutar el contenedor
```bash
docker run -p 8000:8000 pysentiment
```

### 3. Ejecutar en segundo plano (detached)
```bash
docker run -d -p 8000:8000 --name pysentiment-api pysentiment
```

### 4. Ejecutar con docker-compose (recomendado)
```bash
docker-compose up
```

### 5. Ejecutar con docker-compose en segundo plano
```bash
docker-compose up -d
```

### 6. Ver logs del contenedor
```bash
# Si usas docker run
docker logs pysentiment-api

# Si usas docker-compose
docker-compose logs -f
```

### 7. Detener el contenedor
```bash
# Si usas docker run
docker stop pysentiment-api
docker rm pysentiment-api

# Si usas docker-compose
docker-compose down
```

### 8. Reconstruir la imagen (después de cambios)
```bash
docker-compose build --no-cache
docker-compose up
```

### 9. Ejecutar con puerto personalizado
```bash
docker run -p 8080:8000 -e PORT=8000 pysentiment
```

### 10. Ver contenedores en ejecución
```bash
docker ps
```

### 11. Ver todas las imágenes
```bash
docker images
```

### 12. Eliminar la imagen
```bash
docker rmi pysentiment
```

## 🚀 Acceso al Servicio

Una vez ejecutado, el servicio estará disponible en:
- **Landing Page**: http://localhost:8000
- **API**: http://localhost:8000/analyze-sentiment
- **Health Check**: http://localhost:8000/health

## 📋 Verificar que está funcionando

### Ver la landing page:
```bash
curl http://localhost:8000
```

### Health check:
```bash
curl http://localhost:8000/health
```

### Probar la API:
```bash
curl -X POST "http://localhost:8000/analyze-sentiment" \
  -H "Content-Type: application/json" \
  -d '{"review_text": "Me encantó este producto, es excelente!"}'
```

## ⚙️ Configuración

### Variables de Entorno Importantes:
- `PORT`: Puerto del servicio (default: 8000)
- `CUDA_VISIBLE_DEVICES`: Vacío para forzar CPU
- `OMP_NUM_THREADS`: 1 para reducir memoria
- `MKL_NUM_THREADS`: 1 para reducir memoria

### Límites de Memoria:
El docker-compose.yml está configurado con:
- **Memoria máxima**: 512MB (Render free tier)
- **Memoria reservada**: 400MB
- **CPU**: Sin GPU (solo CPU)

## 🔧 Troubleshooting

### Error: Puerto ya en uso
```bash
# Ver qué proceso usa el puerto 8000
netstat -ano | findstr :8000

# O usar otro puerto
docker run -p 8080:8000 pysentiment
```

### Error: Out of memory
- Verifica que tengas al menos 512MB de RAM disponible
- Reduce el límite en docker-compose.yml si es necesario

### Error: No se encuentra el Dockerfile
- Asegúrate de estar en el directorio correcto
- Verifica que el Dockerfile exista: `ls -la Dockerfile`

### Reconstruir desde cero:
```bash
docker-compose down
docker rmi pysentiment
docker-compose build --no-cache
docker-compose up
```

## 📦 Deployment

### Render (con Docker):
1. Conecta tu repositorio
2. Selecciona "Docker" como método de build
3. Render detectará automáticamente el Dockerfile
4. La variable `PORT` se configura automáticamente

### Railway:
1. Conecta tu repositorio
2. Railway detectará el Dockerfile automáticamente
3. El puerto se configura automáticamente

### Verificar que usa CPU (no GPU):
El Dockerfile tiene configurado:
- `CUDA_VISIBLE_DEVICES=""` - Deshabilita GPU
- `FORCE_CPU=1` - Fuerza uso de CPU
- Todas las variables de entorno están configuradas para CPU

