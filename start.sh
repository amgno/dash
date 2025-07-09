#!/bin/bash

# Script per avviare VPS Monitor
# Usage: ./start.sh

PID_FILE="vps_monitor.pid"
LOG_FILE="vps_monitor.log"
APP_FILE="app.py"

echo "🚀 Avvio VPS Monitor..."

# Controlla se l'app è già in esecuzione
if [ -f "$PID_FILE" ]; then
    PID=$(cat $PID_FILE)
    if ps -p $PID > /dev/null 2>&1; then
        echo "❌ VPS Monitor è già in esecuzione (PID: $PID)"
        echo "   Usa './stop.sh' per fermarlo prima"
        exit 1
    else
        echo "🧹 Rimuovo file PID obsoleto..."
        rm -f $PID_FILE
    fi
fi

# Controlla se il file app.py esiste
if [ ! -f "$APP_FILE" ]; then
    echo "❌ File $APP_FILE non trovato!"
    exit 1
fi

# Controlla se Python è installato
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 non trovato! Installa Python3 prima di continuare"
    exit 1
fi

# Installa dipendenze se requirements.txt esiste
if [ -f "requirements.txt" ]; then
    echo "📦 Installo dipendenze..."
    python3 -m pip install -r requirements.txt --quiet
fi

# Avvia l'applicazione in background
echo "🌟 Avvio server su http://localhost:8080..."
nohup python3 $APP_FILE > $LOG_FILE 2>&1 &

# Salva il PID
echo $! > $PID_FILE

# Attendi un momento per verificare l'avvio
sleep 2

# Verifica che il processo sia ancora attivo
if ps -p $(cat $PID_FILE) > /dev/null 2>&1; then
    echo "✅ VPS Monitor avviato con successo!"
    echo "   🌐 Visita: http://localhost:8080"
    echo "   📋 PID: $(cat $PID_FILE)"
    echo "   📄 Log: $LOG_FILE"
    echo ""
    echo "🛑 Per fermarlo: ./stop.sh"
else
    echo "❌ Errore nell'avvio! Controlla il log:"
    cat $LOG_FILE
    rm -f $PID_FILE
    exit 1
fi 