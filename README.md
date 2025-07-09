# VPS Monitor - Sistema di Monitoraggio

Un sistema di monitoraggio per VPS Ubuntu che replica esattamente l'interfaccia mostrata nell'immagine di riferimento, visualizzando le statistiche del sistema in tempo reale.

## Caratteristiche

- **Interfaccia identica** all'immagine di riferimento
- **Monitoraggio in tempo reale** delle statistiche del sistema
- **Cross-platform**: Compatibile con Linux, Ubuntu, macOS e Windows
- **Design responsive** con tema scuro
- **Aggiornamento automatico** ogni 2 secondi
- **Controlli interattivi** (Refresh, Pause, Close)
- **Avvio semplificato**: File batch per Windows (.bat) e script per Linux (.sh)

## Statistiche Monitorate

- **CPU Usage**: Indicatore circolare che mostra l'utilizzo della CPU
- **Memory Volume**: Progress bar per l'utilizzo della memoria RAM
- **Uptime**: Tempo di attività del sistema
- **Network I/O**: Velocità di trasferimento dati di rete
- **System Details**: Numero di processi e carico del sistema
- **Disk Usage**: Utilizzo dello spazio su disco

## Installazione

### Prerequisiti
- **Modalità Bare Metal**: Python 3.7+ e Sistema Ubuntu/Linux/Windows
- **Modalità Docker**: Docker e Docker Compose

### Setup

#### Modalità 1: Bare Metal (Esecuzione Diretta)

##### 🪟 Windows

1. **Assicurati di avere Python installato**:
   - Scarica Python da: https://www.python.org/downloads/
   - ⚠️ **IMPORTANTE**: Durante l'installazione, seleziona "Add Python to PATH"

2. **Avvia automaticamente** (installa dipendenze e avvia):
   ```cmd
   # Doppio click su start.bat oppure da Command Prompt:
   start.bat
   ```

3. **Avvio rapido** (se le dipendenze sono già installate):
   ```cmd
   # Doppio click su run.bat oppure da Command Prompt:
   run.bat
   ```

4. **Avvio manuale** (da Command Prompt):
   ```cmd
   pip install -r requirements.txt
   python app.py
   ```

##### 🐧 Linux/Ubuntu

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
# Oppure usa gli script helper
chmod +x *.sh
./start.sh    # Avvia in background
./status.sh   # Controlla lo status
```

#### Modalità 2: Docker (🐳 Consigliato per VPS)

**Vantaggi Docker:**
- ✅ **Sistema Host**: Accesso completo alle metriche del sistema **bare metal**
- ✅ **Isolamento**: App sicura e isolata
- ✅ **Facilità**: Deploy con un comando
- ✅ **Portabilità**: Funziona ovunque

1. **Setup con Docker Compose (Raccomandato)**:
```bash
# Rendi eseguibili gli script
chmod +x *.sh

# Build e avvio in un comando
./docker-compose.sh up

# Altri comandi utili
./docker-compose.sh logs    # Visualizza log
./docker-compose.sh status  # Status completo
./docker-compose.sh down    # Ferma tutto
```

2. **Setup Docker Manuale**:
```bash
./docker-build.sh   # Compila l'immagine
./docker-run.sh     # Avvia container con accesso host
./docker-stop.sh    # Ferma e opzionalmente rimuove
```

3. **Comandi Docker Nativi**:
```bash
# Build
docker build -t vps-monitor .

# Run con accesso al sistema host
docker run -d --name vps-monitor \
  --privileged --pid host --net host \
  -v /proc:/host/proc:ro \
  -v /sys:/host/sys:ro \
  -v /:/host:ro \
  -e HOST_PROC=/host/proc \
  vps-monitor
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
├── start.bat          # 🪟 Avvio Windows con installazione dipendenze
├── run.bat            # 🪟 Avvio rapido Windows
├── start.sh           # 🐧 Script Linux per avvio in background
├── status.sh          # 🐧 Script Linux per controllo status
├── docker-*.sh        # 🐳 Script Docker per deployment
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

### 🪟 Problemi Windows

#### Python non riconosciuto
```cmd
# Errore: 'python' is not recognized as an internal or external command
# Soluzione: Reinstalla Python selezionando "Add Python to PATH"
# Oppure usa: py app.py invece di python app.py
```

#### Pip non disponibile
```cmd
# Errore: 'pip' is not recognized
# Soluzione: Prova con py -m pip install -r requirements.txt
```

#### Impossibile accedere alle metriche di sistema
- Su Windows, alcune metriche come il load average sono simulate
- Assicurati di eseguire come amministratore se necessario per accesso completo alle statistiche

### 🐧 Problemi Linux/Ubuntu

#### Errore "ModuleNotFoundError: No module named 'psutil'"
```bash
pip install psutil
```

### 🌐 Problemi Generali

#### La porta 8080 è già in uso
Cambia la porta nell'ultima riga di `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=9000)  # Usa porta 9000
```

### Docker: Container non riesce ad accedere alle metriche del sistema
Assicurati di usare i mount corretti:
```bash
# Usa gli script forniti che includono tutti i mount necessari
./docker-run.sh

# Oppure aggiungi manualmente i mount del sistema host
docker run --privileged --pid host \
  -v /proc:/host/proc:ro \
  -v /sys:/host/sys:ro \
  -v /:/host:ro \
  -e HOST_PROC=/host/proc \
  vps-monitor
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