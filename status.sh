#!/bin/bash

# Script per controllare lo status di VPS Monitor
# Usage: ./status.sh

PID_FILE="vps_monitor.pid"
LOG_FILE="vps_monitor.log"

echo "📊 Status VPS Monitor"
echo "===================="

# Controlla se il file PID esiste
if [ ! -f "$PID_FILE" ]; then
    echo "🔴 Status: FERMATO"
    echo "   (File PID non trovato)"
else
    PID=$(cat $PID_FILE)
    
    # Controlla se il processo è attivo
    if ps -p $PID > /dev/null 2>&1; then
        echo "🟢 Status: ATTIVO"
        echo "   📋 PID: $PID"
        echo "   🌐 URL: http://localhost:8080"
        
        # Mostra informazioni sul processo
        echo "   ⏱️  Avviato: $(ps -o lstart= -p $PID)"
        echo "   🧠 Memoria: $(ps -o rss= -p $PID | awk '{print $1/1024 " MB"}')"
        echo "   ⚡ CPU: $(ps -o %cpu= -p $PID)%"
        
        # Controlla se la porta è in ascolto
        if netstat -tln 2>/dev/null | grep -q ":8080 "; then
            echo "   🔌 Porta 8080: IN ASCOLTO"
        else
            echo "   ⚠️  Porta 8080: NON IN ASCOLTO"
        fi
        
    else
        echo "🔴 Status: FERMATO"
        echo "   ⚠️  File PID presente ma processo non attivo"
        echo "   🧹 Usa './stop.sh' per pulire"
    fi
fi

# Informazioni sui file di log
echo ""
echo "📁 File di Log:"
if [ -f "$LOG_FILE" ]; then
    LOG_SIZE=$(wc -c < "$LOG_FILE" 2>/dev/null)
    LOG_LINES=$(wc -l < "$LOG_FILE" 2>/dev/null)
    echo "   📄 $LOG_FILE ($(numfmt --to=iec $LOG_SIZE), $LOG_LINES righe)"
    
    # Mostra le ultime righe del log se esistono
    if [ "$LOG_LINES" -gt 0 ]; then
        echo ""
        echo "📋 Ultime 5 righe del log:"
        echo "------------------------"
        tail -5 "$LOG_FILE"
    fi
else
    echo "   ❌ Nessun file di log trovato"
fi

echo ""
echo "🔧 Comandi disponibili:"
echo "   ./start.sh   - Avvia il servizio"
echo "   ./stop.sh    - Ferma il servizio" 
echo "   ./restart.sh - Riavvia il servizio"
echo "   ./status.sh  - Mostra questo status" 