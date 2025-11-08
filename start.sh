#!/bin/bash
# Script de inicio para Render
# Asegura que uvicorn use el host y puerto correctos

uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

