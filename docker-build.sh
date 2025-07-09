#!/bin/bash

# Script per build dell'immagine Docker VPS Monitor
# Usage: ./docker-build.sh

IMAGE_NAME="vps-monitor"
IMAGE_TAG="latest"

echo "🐳 Build Docker VPS Monitor..."
echo "================================"

# Controlla se Docker è installato
if ! command -v docker &> /dev/null; then
    echo "❌ Docker non trovato! Installa Docker prima di continuare"
    exit 1
fi

# Controlla se Dockerfile esiste
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile non trovato!"
    exit 1
fi

# Controlla se requirements.txt esiste
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt non trovato!"
    exit 1
fi

echo "📦 Building immagine Docker..."
echo "   Nome: $IMAGE_NAME:$IMAGE_TAG"
echo ""

# Build dell'immagine
docker build -t $IMAGE_NAME:$IMAGE_TAG . 

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build completato con successo!"
    echo ""
    echo "📊 Informazioni immagine:"
    docker images $IMAGE_NAME:$IMAGE_TAG
    echo ""
    echo "🚀 Comandi utili:"
    echo "   ./docker-run.sh      - Avvia container"
    echo "   ./docker-compose.sh  - Avvia con docker-compose" 
    echo "   docker run -p 8080:8080 $IMAGE_NAME:$IMAGE_TAG"
else
    echo ""
    echo "❌ Errore durante il build!"
    exit 1
fi 