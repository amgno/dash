#!/bin/bash

# Script per fermare VPS Monitor Docker
# Usage: ./docker-stop.sh

CONTAINER_NAME="vps-monitor"

echo "🛑 Fermo VPS Monitor Docker..."
echo "============================="

# Controlla se Docker è installato
if ! command -v docker &> /dev/null; then
    echo "❌ Docker non trovato!"
    exit 1
fi

# Controlla se il container esiste
if ! docker ps -a | grep -q "$CONTAINER_NAME"; then
    echo "❌ Container $CONTAINER_NAME non trovato"
    exit 1
fi

# Controlla se il container è in esecuzione
if docker ps | grep -q "$CONTAINER_NAME"; then
    echo "📋 Fermando container..."
    docker stop $CONTAINER_NAME
    
    if [ $? -eq 0 ]; then
        echo "✅ Container fermato con successo"
    else
        echo "❌ Errore nel fermare il container"
        exit 1
    fi
else
    echo "⚠️  Container già fermato"
fi

# Chiede se rimuovere il container
echo ""
read -p "🗑️  Rimuovere il container? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker rm $CONTAINER_NAME
    
    if [ $? -eq 0 ]; then
        echo "✅ Container rimosso con successo"
    else
        echo "❌ Errore nella rimozione del container"
        exit 1
    fi
else
    echo "📦 Container mantenuto (fermo)"
fi

echo ""
echo "🔄 Per riavviarlo:"
echo "   ./docker-run.sh"
echo "   docker start $CONTAINER_NAME" 