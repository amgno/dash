#!/bin/bash

# Script per fermare VPS Monitor
# Usage: ./stop.sh

PID_FILE="vps_monitor.pid"
LOG_FILE="vps_monitor.log"

echo "🛑 Fermo VPS Monitor..."

# Controlla se il file PID esiste
if [ ! -f "$PID_FILE" ]; then
    echo "❌ VPS Monitor non sembra essere in esecuzione"
    echo "   (File PID non trovato: $PID_FILE)"
    exit 1
fi

# Legge il PID dal file
PID=$(cat $PID_FILE)

# Controlla se il processo è attivo
if ! ps -p $PID > /dev/null 2>&1; then
    echo "❌ Processo con PID $PID non trovato"
    echo "🧹 Pulisco file PID obsoleto..."
    rm -f $PID_FILE
    exit 1
fi

echo "📋 Trovato processo VPS Monitor (PID: $PID)"

# Prova a fermare con SIGTERM (graceful shutdown)
echo "🚦 Invio segnale TERM..."
kill -TERM $PID

# Attende 5 secondi per il graceful shutdown
for i in {1..5}; do
    if ! ps -p $PID > /dev/null 2>&1; then
        break
    fi
    echo "   Attendo... ($i/5)"
    sleep 1
done

# Se il processo è ancora attivo, forza la chiusura
if ps -p $PID > /dev/null 2>&1; then
    echo "⚠️  Processo ancora attivo, forzo la chiusura..."
    kill -KILL $PID
    sleep 1
    
    # Verifica finale
    if ps -p $PID > /dev/null 2>&1; then
        echo "❌ Impossibile fermare il processo $PID"
        exit 1
    fi
fi

# Cleanup file PID
rm -f $PID_FILE

# Mostra statistiche finali
if [ -f "$LOG_FILE" ]; then
    LOG_SIZE=$(wc -c < "$LOG_FILE")
    echo "📄 Log file: $LOG_FILE ($(numfmt --to=iec $LOG_SIZE))"
fi

echo "✅ VPS Monitor fermato con successo!"
echo ""
echo "🔄 Per riavviarlo: ./start.sh" 