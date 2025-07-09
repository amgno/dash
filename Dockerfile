FROM python:3.11-slim

# Installa dipendenze di sistema necessarie per psutil
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Crea directory di lavoro
WORKDIR /app

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice dell'applicazione
COPY app.py .
COPY templates/ templates/
COPY static/ static/

# Crea un utente non-root per sicurezza
RUN useradd -m -u 1000 vpsmonitor && \
    chown -R vpsmonitor:vpsmonitor /app
USER vpsmonitor

# Espone la porta 8080
EXPOSE 8080

# Variabili d'ambiente per Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080

# Comando di avvio
CMD ["python", "app.py"] 