#!/bin/bash

# Script per gestire VPS Monitor con Docker Compose
# Usage: ./docker-compose.sh [up|down|restart|logs|status]

COMPOSE_FILE="docker-compose.yml"

# Funzione per mostrare l'help
show_help() {
    echo "🐳 Gestione VPS Monitor Docker Compose"
    echo "====================================="
    echo ""
    echo "Usage: ./docker-compose.sh [comando]"
    echo ""
    echo "Comandi disponibili:"
    echo "  up       - Avvia i servizi"
    echo "  down     - Ferma i servizi"
    echo "  restart  - Riavvia i servizi"
    echo "  logs     - Mostra i log"
    echo "  status   - Mostra lo status"
    echo "  build    - Ricompila l'immagine"
    echo ""
    echo "Esempi:"
    echo "  ./docker-compose.sh up"
    echo "  ./docker-compose.sh logs"
    echo "  ./docker-compose.sh down"
}

# Controlla se Docker Compose è installato
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose non trovato! Installa docker-compose prima di continuare"
    exit 1
fi

# Controlla se il file docker-compose.yml esiste
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "❌ File $COMPOSE_FILE non trovato!"
    exit 1
fi

# Gestisci i comandi
case "${1:-up}" in
    "up")
        echo "🚀 Avvio VPS Monitor con Docker Compose..."
        echo "=========================================="
        docker-compose up -d
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Servizi avviati con successo!"
            echo "🌐 URL: http://localhost:8080"
            echo ""
            echo "📊 Status servizi:"
            docker-compose ps
        else
            echo "❌ Errore nell'avvio dei servizi!"
            exit 1
        fi
        ;;
        
    "down")
        echo "🛑 Fermo VPS Monitor..."
        docker-compose down
        
        if [ $? -eq 0 ]; then
            echo "✅ Servizi fermati con successo!"
        else
            echo "❌ Errore nel fermare i servizi!"
            exit 1
        fi
        ;;
        
    "restart")
        echo "🔄 Riavvio VPS Monitor..."
        docker-compose restart
        
        if [ $? -eq 0 ]; then
            echo "✅ Servizi riavviati con successo!"
            echo "🌐 URL: http://localhost:8080"
        else
            echo "❌ Errore nel riavvio dei servizi!"
            exit 1
        fi
        ;;
        
    "logs")
        echo "📄 Log VPS Monitor:"
        echo "=================="
        docker-compose logs -f
        ;;
        
    "status")
        echo "📊 Status VPS Monitor Docker Compose"
        echo "==================================="
        docker-compose ps
        echo ""
        echo "📊 Statistiche risorse:"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
        ;;
        
    "build")
        echo "🔨 Ricompilo immagine VPS Monitor..."
        docker-compose build --no-cache
        
        if [ $? -eq 0 ]; then
            echo "✅ Build completato con successo!"
        else
            echo "❌ Errore nel build!"
            exit 1
        fi
        ;;
        
    "help"|"-h"|"--help")
        show_help
        ;;
        
    *)
        echo "❌ Comando sconosciuto: $1"
        echo ""
        show_help
        exit 1
        ;;
esac 