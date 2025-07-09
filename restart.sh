#!/bin/bash

# Script per riavviare VPS Monitor
# Usage: ./restart.sh

echo "🔄 Riavvio VPS Monitor..."
echo ""

# Ferma il servizio se è in esecuzione
if [ -f "vps_monitor.pid" ]; then
    ./stop.sh
    echo ""
    echo "⏱️  Attendo 2 secondi..."
    sleep 2
fi

# Avvia il servizio
./start.sh 