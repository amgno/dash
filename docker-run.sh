#!/bin/bash

# Script per eseguire VPS Monitor in Docker con accesso al sistema host
# Usage: ./docker-run.sh

IMAGE_NAME="vps-monitor"
IMAGE_TAG="latest"
CONTAINER_NAME="vps-monitor"

echo "🐳 Avvio VPS Monitor Docker..."
echo "=============================="

# Controlla se Docker è installato
if ! command -v docker &> /dev/null; then
    echo "❌ Docker non trovato! Installa Docker prima di continuare"
    exit 1
fi

# Controlla se l'immagine esiste
if ! docker images | grep -q "$IMAGE_NAME.*$IMAGE_TAG"; then
    echo "❌ Immagine $IMAGE_NAME:$IMAGE_TAG non trovata!"
    echo "   Esegui './docker-build.sh' prima"
    exit 1
fi

# Ferma e rimuove container esistente se presente
if docker ps -a | grep -q "$CONTAINER_NAME"; then
    echo "🛑 Rimuovo container esistente..."
    docker stop $CONTAINER_NAME >/dev/null 2>&1
    docker rm $CONTAINER_NAME >/dev/null 2>&1
fi

echo "🚀 Avvio container con accesso al sistema host..."
echo "   🌐 URL: http://localhost:8080"
echo ""

# Esegue il container con tutti i mount necessari per il sistema host
docker run -d \
    --name $CONTAINER_NAME \
    --privileged \
    --pid host \
    --net host \
    -p 8080:8080 \
    -v /proc:/host/proc:ro \
    -v /sys:/host/sys:ro \
    -v /:/host:ro \
    -v /dev:/host/dev:ro \
    -v /var/run/docker.sock:/var/run/docker.sock:ro \
    -e HOST_PROC=/host/proc \
    -e HOST_SYS=/host/sys \
    -e HOST_ETC=/host/etc \
    -e HOST_DEV=/host/dev \
    --restart unless-stopped \
    $IMAGE_NAME:$IMAGE_TAG

if [ $? -eq 0 ]; then
    echo "✅ Container avviato con successo!"
    echo ""
    echo "📊 Status container:"
    docker ps | grep $CONTAINER_NAME
    echo ""
    echo "📋 Log in tempo reale:"
    echo "   docker logs -f $CONTAINER_NAME"
    echo ""
    echo "🛑 Per fermarlo:"
    echo "   ./docker-stop.sh"
    echo "   docker stop $CONTAINER_NAME"
    
    # Mostra i primi log
    echo ""
    echo "📄 Primi log del container:"
    echo "------------------------"
    sleep 2
    docker logs $CONTAINER_NAME
else
    echo "❌ Errore nell'avvio del container!"
    exit 1
fi 