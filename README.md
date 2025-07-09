# VPS Monitor - Sistema di Monitoraggio

Un sistema di monitoraggio per VPS Ubuntu che replica esattamente l'interfaccia mostrata nell'immagine di riferimento, visualizzando le statistiche del sistema in tempo reale.

## Caratteristiche

- **Interfaccia identica** all'immagine di riferimento
- **Monitoraggio in tempo reale** delle statistiche del sistema
- **Design responsive** con tema scuro
- **Aggiornamento automatico** ogni 2 secondi
- **Controlli interattivi** (Refresh, Pause, Close)

## Statistiche Monitorate

- **CPU Usage**: Indicatore circolare che mostra l'utilizzo della CPU
- **Memory Volume**: Progress bar per l'utilizzo della memoria RAM
- **Uptime**: Tempo di attività del sistema
- **Network I/O**: Velocità di trasferimento dati di rete
- **System Details**: Numero di processi e carico del sistema
- **Disk Usage**: Utilizzo dello spazio su disco

## Installazione

### Prerequisiti
- Python 3.7 o superiore
- Sistema operativo Ubuntu/Linux

### Setup

1. **Clona o scarica il progetto**:
```bash
cd /path/to/project
```

2. **Installa le dipendenze**:
```bash
pip install -r requirements.txt
```

3. **Avvia l'applicazione**:
```bash
python app.py
```

4. **Accedi al monitor**:
Apri il browser e vai su: `http://localhost:8080`

## Utilizzo

### Accesso Locale
```
http://localhost:8080
```

### Accesso Remoto (VPS)
Se installi su una VPS, sostituisci `localhost` con l'IP della tua VPS:
```
http://YOUR_VPS_IP:8080
```

**Importante**: Assicurati che la porta 8080 sia aperta nel firewall della VPS.

### Controlli

- **REFRESH**: Aggiorna manualmente le statistiche
- **PAUSE/RESUME**: Mette in pausa/riprende il monitoraggio automatico
- **CLOSE WINDOW**: Chiude l'applicazione (con conferma)

## Configurazione Firewall (VPS)

Per accedere al monitor da remoto, apri la porta 8080:

```bash
# Ubuntu/Debian con ufw
sudo ufw allow 8080

# CentOS/RHEL con firewalld
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

## Deployment per Produzione

Per un ambiente di produzione, si consiglia di utilizzare un server WSGI come Gunicorn:

```bash
# Installa Gunicorn
pip install gunicorn

# Avvia con Gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

## Tecnologie Utilizzate

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Monitoraggio**: psutil (libreria Python)
- **Styling**: CSS Grid, Flexbox, Animazioni CSS

## API Endpoints

- `GET /`: Pagina principale del monitor
- `GET /api/stats`: Endpoint JSON con le statistiche del sistema

## Struttura del Progetto

```
vps-monitor/
├── app.py              # Applicazione Flask principale
├── requirements.txt    # Dipendenze Python
├── README.md          # Documentazione
├── templates/
│   └── index.html     # Template HTML principale
└── static/
    ├── css/
    │   └── style.css  # Stili CSS
    └── js/
        └── app.js     # JavaScript per aggiornamenti in tempo reale
```

## Personalizzazione

### Modificare l'intervallo di aggiornamento
Nel file `static/js/app.js`, modifica la riga:
```javascript
refreshInterval = setInterval(updateStats, 2000); // 2000ms = 2 secondi
```

### Aggiungere nuove metriche
1. Modifica la funzione `get_system_stats()` in `app.py`
2. Aggiorna il template HTML e il JavaScript per visualizzare i nuovi dati

## Risoluzione Problemi

### Errore "ModuleNotFoundError: No module named 'psutil'"
```bash
pip install psutil
```

### La porta 8080 è già in uso
Cambia la porta nell'ultima riga di `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=9000)  # Usa porta 9000
```

### Problemi di permessi su Linux
Alcuni dati di sistema potrebbero richiedere privilegi elevati:
```bash
sudo python app.py
```

## Sicurezza

⚠️ **Attenzione**: Questo monitor mostra informazioni sensibili del sistema. In produzione:

1. Implementa autenticazione/autorizzazione
2. Usa HTTPS
3. Limita l'accesso a indirizzi IP specifici
4. Considera l'uso di un reverse proxy (nginx)

## Licenza

Progetto open source per uso educativo e personale. 