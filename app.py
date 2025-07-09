from flask import Flask, render_template, jsonify
import psutil
import shutil
import time
import socket
import subprocess
import os
from datetime import datetime, timedelta

# Configurazione per Docker: accesso alle metriche del sistema host
def configure_psutil_for_host():
    """Configura psutil per leggere le metriche del sistema host quando in Docker"""
    host_proc = os.environ.get('HOST_PROC', '/proc')
    
    # Rileva se siamo in un container Docker
    in_docker = os.path.exists('/.dockerenv') or os.environ.get('HOST_PROC') is not None
    
    if in_docker and host_proc != '/proc' and os.path.exists(host_proc):
        # Configura psutil per usare i path del sistema host
        psutil.PROCFS_PATH = host_proc
        print(f"🐳 Docker mode: usando {host_proc} per metriche del sistema host")
        return True
    else:
        print("🖥️  Bare metal mode: usando /proc nativo")
        return False

# Inizializza configurazione psutil
IS_DOCKER = configure_psutil_for_host()

app = Flask(__name__)

def get_system_stats():
    """Raccoglie le statistiche del sistema VPS"""
    
    # CPU Usage
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # Memory Usage (compatibile con Monitoraggio Attività macOS)
    memory = psutil.virtual_memory()
    memory_total_gb = memory.total / (1024**3)
    memory_percent = memory.percent
    memory_used_gb = (memory_percent / 100) * memory_total_gb
    
    # Disk Usage (gestisce Docker host mount)
    if IS_DOCKER and os.path.exists('/host'):
        # In Docker, usa il mount del sistema host
        disk = shutil.disk_usage('/host')
    else:
        # Bare metal o Docker senza host mount
        disk = shutil.disk_usage('/')
    
    disk_used_gb = (disk.total - disk.free) / (1024**3)
    disk_total_gb = disk.total / (1024**3)
    disk_percent = (disk_used_gb / disk_total_gb) * 100
    
    # Network Stats
    net_io = psutil.net_io_counters()
    
    # System uptime
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    uptime = str(timedelta(seconds=int(uptime_seconds)))
    
    # Load Average
    load_avg = os.getloadavg()
    
    # Number of processes
    num_processes = len(psutil.pids())
    
    # Network speed (simulate transfer rate)
    bytes_sent = net_io.bytes_sent / (1024**3)  # GB
    bytes_recv = net_io.bytes_recv / (1024**3)  # GB
    
    return {
        'cpu_percent': cpu_percent,
        'memory_percent': memory_percent,
        'memory_used_gb': round(memory_used_gb, 2),
        'memory_total_gb': round(memory_total_gb, 2),
        'disk_percent': round(disk_percent, 1),
        'disk_used_gb': round(disk_used_gb, 2),
        'disk_total_gb': round(disk_total_gb, 2),
        'uptime': uptime,
        'load_avg': round(load_avg[0], 2),
        'num_processes': num_processes,
        'bytes_sent': round(bytes_sent, 2),
        'bytes_recv': round(bytes_recv, 2),
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }

@app.route('/')
def index():
    """Pagina principale"""
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """API endpoint per le statistiche in tempo reale"""
    return jsonify(get_system_stats())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 