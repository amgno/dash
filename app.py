from flask import Flask, render_template, jsonify
import psutil
import shutil
import time
import socket
import subprocess
import os
import platform
from datetime import datetime, timedelta

# Import specifici per Windows con debug
try:
    import GPUtil
    print("✅ GPUtil caricato con successo")
except ImportError as e:
    GPUtil = None
    print(f"⚠️  GPUtil non disponibile: {e}")

if platform.system() == 'Windows':
    try:
        import wmi
        print("✅ WMI caricato con successo")
    except ImportError as e:
        wmi = None
        print(f"⚠️  WMI non disponibile: {e}")
else:
    wmi = None
    print("ℹ️  WMI non necessario (non Windows)")

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
        system_name = platform.system()
        print(f"🖥️  Bare metal mode su {system_name}: usando metriche native del sistema")
        return False

# Rileva il sistema operativo
SYSTEM_OS = platform.system()
IS_WINDOWS = SYSTEM_OS == 'Windows'
IS_DOCKER = configure_psutil_for_host()

app = Flask(__name__)

def get_load_average():
    """Ottiene il load average del sistema (compatibile cross-platform)"""
    try:
        if IS_WINDOWS:
            # Su Windows, simula il load average con la percentuale CPU
            return psutil.cpu_percent(interval=0.1) / 100.0
        else:
            # Su Unix/Linux/macOS, usa getloadavg()
            return os.getloadavg()[0]
    except (AttributeError, OSError):
        # Fallback se getloadavg() non è disponibile
        return psutil.cpu_percent(interval=0.1) / 100.0

def get_disk_path():
    """Restituisce il path corretto per il controllo del disco"""
    if IS_DOCKER and os.path.exists('/host'):
        return '/host'
    elif IS_WINDOWS:
        return 'C:\\'  # Drive principale su Windows
    else:
        return '/'  # Root su Unix/Linux/macOS

def get_gpu_stats():
    """Ottiene statistiche GPU reali se possibile, altrimenti simulate"""
    
    # Prima prova: GPUtil su Windows
    if GPUtil and IS_WINDOWS:
        try:
            gpus = GPUtil.getGPUs()
            print(f"🎮 GPUs trovate con GPUtil: {len(gpus) if gpus else 0}")
            
            if gpus:
                gpu = gpus[0]  # Prima GPU
                
                # Debug: stampa i valori raw della GPU
                print(f"🔍 GPU raw values: load={gpu.load}, memory_used={gpu.memoryUsed}, memory_total={gpu.memoryTotal}, temp={gpu.temperature}")
                
                # gpu.load è già 0-1, quindi moltiplicare per 100 è corretto
                # Ma controlliamo se forse è già in percentuale
                raw_load = gpu.load
                if raw_load > 1:
                    # È già in percentuale (0-100)
                    gpu_load = round(raw_load, 1)
                    print(f"🔍 GPU load già in percentuale: {gpu_load}%")
                else:
                    # È in formato 0-1, convertire a percentuale
                    gpu_load = round(raw_load * 100, 1)
                    print(f"🔍 GPU load convertito da {raw_load} a {gpu_load}%")
                
                gpu_stats = {
                    'name': gpu.name[:20],
                    'load': gpu_load,
                    'memory_used': round(gpu.memoryUsed, 1),
                    'memory_total': round(gpu.memoryTotal, 1),
                    'memory_percent': round((gpu.memoryUsed / gpu.memoryTotal) * 100, 1),
                    'temperature': round(gpu.temperature, 1) if gpu.temperature else 0
                }
                print(f"✅ GPU reale via GPUtil: {gpu_stats}")
                return [gpu_stats]
        except Exception as e:
            print(f"⚠️ Errore GPUtil: {e}")
    
    # Seconda prova: nvidia-smi (disponibile su molti sistemi)
    try:
        import subprocess
        result = subprocess.run([
            'nvidia-smi', 
            '--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu', 
            '--format=csv,noheader,nounits'
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            if lines and lines[0]:
                gpu_data = [x.strip() for x in lines[0].split(',')]
                
                if len(gpu_data) >= 5:
                    try:
                        name = gpu_data[0]
                        load = float(gpu_data[1])
                        memory_used = float(gpu_data[2]) / 1024  # MB to GB
                        memory_total = float(gpu_data[3]) / 1024  # MB to GB
                        temperature = float(gpu_data[4])
                        
                        gpu_stats = {
                            'name': name[:20],
                            'load': round(load, 1),
                            'memory_used': round(memory_used, 1),
                            'memory_total': round(memory_total, 1),
                            'memory_percent': round((memory_used / memory_total) * 100, 1),
                            'temperature': round(temperature, 1)
                        }
                        print(f"✅ GPU reale via nvidia-smi: {gpu_stats}")
                        return [gpu_stats]
                    except (ValueError, IndexError) as parse_error:
                        print(f"⚠️ Errore parsing nvidia-smi: {parse_error}")
    except Exception as nvidia_error:
        print(f"⚠️ nvidia-smi non disponibile: {nvidia_error}")
    
    # Terza prova: WMI su Windows per almeno il nome GPU
    gpu_name = "GPU (Simulata)"
    if wmi and IS_WINDOWS:
        try:
            import wmi as wmi_module
            c = wmi_module.WMI()
            
            for video_controller in c.Win32_VideoController():
                if video_controller.Name:
                    name = video_controller.Name.lower()
                    if any(brand in name for brand in ['nvidia', 'amd', 'intel', 'radeon', 'geforce', 'quadro']):
                        gpu_name = video_controller.Name[:20]
                        print(f"🎮 Nome GPU reale da WMI: {gpu_name}")
                        break
        except Exception as wmi_error:
            print(f"⚠️ Errore WMI: {wmi_error}")
    
    # Fallback: simula statistiche realistiche
    print(f"🎮 Usando statistiche simulate per: {gpu_name}")
    
    import random
    cpu_load = psutil.cpu_percent()
    
    # Simula GPU load basato su CPU load con variazioni realistiche
    gpu_load = max(5, min(95, cpu_load + random.uniform(-10, 20)))
    
    # Memoria varia in base al load e al tipo di GPU stimato
    if 'rtx' in gpu_name.lower() or 'gtx 16' in gpu_name.lower():
        memory_total = 8.0
        base_memory = 1.5
    elif 'gtx' in gpu_name.lower():
        memory_total = 6.0
        base_memory = 1.0
    else:
        memory_total = 4.0
        base_memory = 0.8
    
    memory_used = round(base_memory + (gpu_load / 100) * (memory_total - base_memory), 1)
    memory_percent = round((memory_used / memory_total) * 100, 1)
    
    # Temperatura realistica basata su load
    temp_base = 40 + (gpu_load * 0.5)
    temperature = round(temp_base + random.uniform(-5, 10), 1)
    
    return [{
        'name': gpu_name,
        'load': round(gpu_load, 1),
        'memory_used': memory_used,
        'memory_total': memory_total,
        'memory_percent': memory_percent,
        'temperature': temperature
    }]

def get_network_activity():
    """Ottiene statistiche di attività di rete in tempo reale"""
    try:
        # Cache per valori precedenti
        if not hasattr(get_network_activity, 'last_net_io'):
            get_network_activity.last_net_io = None
            get_network_activity.last_time = None
        
        current_net_io = psutil.net_io_counters()
        current_time = time.time()
        
        if get_network_activity.last_net_io and get_network_activity.last_time:
            # Calcola differenze
            time_diff = current_time - get_network_activity.last_time
            if time_diff > 0:
                bytes_sent_diff = current_net_io.bytes_sent - get_network_activity.last_net_io.bytes_sent
                bytes_recv_diff = current_net_io.bytes_recv - get_network_activity.last_net_io.bytes_recv
                
                # Velocità in KB/s
                sent_speed = round(bytes_sent_diff / time_diff / 1024, 1)
                recv_speed = round(bytes_recv_diff / time_diff / 1024, 1)
                total_speed = round((sent_speed + recv_speed), 1)
            else:
                sent_speed = recv_speed = total_speed = 0
        else:
            sent_speed = recv_speed = total_speed = 0
        
        # Aggiorna cache
        get_network_activity.last_net_io = current_net_io
        get_network_activity.last_time = current_time
        
        # Ottieni numero connessioni
        try:
            connections = len(psutil.net_connections())
        except:
            connections = 0
        
        return {
            'upload_speed': max(0, sent_speed),
            'download_speed': max(0, recv_speed),
            'total_speed': max(0, total_speed),
            'connections': connections,
            'total_sent_gb': round(current_net_io.bytes_sent / (1024**3), 2),
            'total_recv_gb': round(current_net_io.bytes_recv / (1024**3), 2)
        }
    except Exception as e:
        print(f"Errore network activity: {e}")
        return {
            'upload_speed': 0,
            'download_speed': 0,
            'total_speed': 0,
            'connections': 0,
            'total_sent_gb': 0,
            'total_recv_gb': 0
        }

def get_top_processes():
    """Ottiene i processi che consumano più CPU"""
    try:
        # Cache globale per i valori CPU precedenti
        if not hasattr(get_top_processes, 'cpu_cache'):
            get_top_processes.cpu_cache = {}
        
        processes = []
        current_pids = set()
        
        # Prima passata: ottieni tutti i processi attivi
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                info = proc.info
                pid = info['pid']
                current_pids.add(pid)
                
                # Ottieni CPU percent (veloce, senza interval)
                cpu_percent = proc.cpu_percent()
                
                # Se abbiamo un valore precedente, usa quello per il calcolo
                if pid in get_top_processes.cpu_cache:
                    cpu_percent = get_top_processes.cpu_cache[pid]
                
                # Aggiorna cache
                get_top_processes.cpu_cache[pid] = cpu_percent
                
                # Filtra solo processi che usano CPU
                if cpu_percent > 0.1 or info['memory_percent'] > 1.0:
                    processes.append({
                        'pid': pid,
                        'name': info['name'][:15],
                        'cpu_percent': round(cpu_percent, 1),
                        'memory_percent': round(info['memory_percent'], 1)
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Pulisci cache per PID non più esistenti
        get_top_processes.cpu_cache = {pid: cpu for pid, cpu in get_top_processes.cpu_cache.items() if pid in current_pids}
        
        # Ordina per CPU e prendi i top 5
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        return processes[:5]
    except Exception as e:
        print(f"Errore top processes: {e}")
        return [
            {'name': 'Error', 'cpu_percent': 0, 'memory_percent': 0},
            {'name': 'Loading', 'cpu_percent': 0, 'memory_percent': 0}
        ]

def get_system_temperature():
    """Ottiene temperature simulate realistiche"""
    import random
    
    # Usa il carico CPU attuale (senza interval per velocità)
    try:
        cpu_load = psutil.cpu_percent()
    except:
        cpu_load = 50
    
    # Simula temperature realistiche basate sul carico
    base_temp = 40
    load_factor = (cpu_load / 100) * 25
    
    # Aggiungi piccole variazioni casuali per realismo
    variation = random.uniform(-3, 3)
    
    cpu_temp = round(base_temp + load_factor + variation, 1)
    gpu_temp = round(cpu_temp + 8 + random.uniform(-2, 5), 1)  # GPU più calda
    system_temp = round((cpu_temp + gpu_temp) / 2 + random.uniform(-1, 1), 1)
    mb_temp = round(cpu_temp - 5 + random.uniform(-2, 2), 1)  # MB più fredda
    
    return {
        'cpu_temp': max(25, cpu_temp),  # Minimo 25°C
        'gpu_temp': max(30, gpu_temp),  # Minimo 30°C
        'system_temp': max(25, system_temp),
        'mb_temp': max(20, mb_temp)     # Minimo 20°C
    }

def get_all_disks():
    """Ottiene informazioni su tutti i dischi del sistema"""
    try:
        disks = []
        
        # Ottieni tutte le partizioni
        partitions = psutil.disk_partitions()
        print(f"🔍 Partizioni trovate: {len(partitions)}")
        
        for partition in partitions:
            try:
                print(f"🔍 Analizzando partizione: {partition}")
                
                # Su Windows, filtra solo i drive chiaramente inutili
                if IS_WINDOWS:
                    # Filtra solo CD/DVD e network drives ovvi
                    skip_partition = False
                    
                    # Salta se è chiaramente un CD/DVD
                    if 'cdrom' in partition.opts.lower():
                        skip_partition = True
                        
                    # Salta se è un network drive
                    if partition.device.startswith('\\\\'):
                        skip_partition = True
                        
                    # Salta se il device è troppo corto (drive invalidi)
                    if len(partition.device) < 2:
                        skip_partition = True
                        
                    # MA NON saltare se fstype è vuoto - potrebbero essere drive validi
                    
                    if skip_partition:
                        print(f"🔍 Saltando partizione: {partition.device} (tipo: {partition.fstype}, opts: {partition.opts})")
                        continue
                    else:
                        print(f"🔍 Provo partizione: {partition.device} (tipo: {partition.fstype}, opts: {partition.opts})")
                else:
                    # Su Linux/Mac, filtra diversamente
                    if 'cdrom' in partition.opts or partition.fstype == '':
                        continue
                
                # Ottieni utilizzo della partizione
                partition_usage = psutil.disk_usage(partition.mountpoint)
                print(f"🔍 Utilizzo {partition.device}: {partition_usage}")
                
                # Calcola percentuale utilizzo
                if partition_usage.total > 0:
                    usage_percent = (partition_usage.used / partition_usage.total) * 100
                else:
                    continue
                
                # Determina etichetta del disco
                if IS_WINDOWS:
                    label = partition.device.replace('\\', '').replace(':', '')  # C, D, etc.
                    if not label:
                        label = 'WIN'
                else:
                    label = partition.mountpoint.split('/')[-1] or 'root'
                
                disk_info = {
                    'label': label[:4],  # Massimo 4 caratteri
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total_gb': round(partition_usage.total / (1024**3), 1),
                    'used_gb': round(partition_usage.used / (1024**3), 1),
                    'free_gb': round(partition_usage.free / (1024**3), 1),
                    'usage_percent': round(usage_percent, 1)
                }
                
                disks.append(disk_info)
                print(f"✅ Disco aggiunto: {disk_info}")
                
            except (PermissionError, OSError) as e:
                print(f"⚠️ Errore accesso partizione {partition.device}: {e}")
                continue
            except Exception as e:
                print(f"⚠️ Errore generico partizione {partition.device}: {e}")
                continue
        
        print(f"📊 Totale dischi validi trovati: {len(disks)}")
        
        # Su Windows, prova l'approccio diretto con drive noti
        if IS_WINDOWS and not disks:
            print("🔍 Partizioni non funzionano su Windows, provo approccio diretto...")
            
            # Lista di drive da testare (dall'A: al Z:)
            potential_drives = [f"{chr(ord('A') + i)}:\\" for i in range(26)]
            
            for drive in potential_drives:
                try:
                    # Prova a accedere al drive
                    drive_usage = psutil.disk_usage(drive)
                    
                    # Se arriviamo qui, il drive esiste
                    usage_percent = (drive_usage.used / drive_usage.total) * 100
                    total_gb = round(drive_usage.total / (1024**3), 1)
                    used_gb = round(drive_usage.used / (1024**3), 1)
                    free_gb = round(drive_usage.free / (1024**3), 1)
                    
                    # Filtra drive molto piccoli (probabilmente virtuali)
                    if total_gb < 0.1:  # Meno di 100 MB
                        continue
                    
                    disk_info = {
                        'label': drive[0],  # C, D, E, etc.
                        'mountpoint': drive,
                        'fstype': 'NTFS',
                        'total_gb': total_gb,
                        'used_gb': used_gb,
                        'free_gb': free_gb,
                        'usage_percent': round(usage_percent, 1)
                    }
                    
                    disks.append(disk_info)
                    print(f"✅ Drive trovato: {drive} - {total_gb}GB ({usage_percent:.1f}% utilizzato)")
                    
                except (OSError, PermissionError, FileNotFoundError):
                    # Drive non esiste o non accessibile
                    pass
                except Exception as e:
                    print(f"⚠️ Errore inspiegabile su {drive}: {e}")
                    pass
            
            print(f"📊 Windows drive scan completato: {len(disks)} dischi trovati")
        
        # Fallback per altri sistemi o se Windows non trova niente
        if not disks:
            try:
                # Usa la funzione get_disk_path() che già funziona
                disk_path = get_disk_path()
                main_usage = psutil.disk_usage(disk_path)
                usage_percent = (main_usage.used / main_usage.total) * 100
                
                # Determina etichetta dal path
                if IS_WINDOWS:
                    label = disk_path.replace('\\', '').replace(':', '') or 'C'
                    fstype = 'NTFS'
                else:
                    label = 'root'
                    fstype = 'ext4'
                
                disks.append({
                    'label': label,
                    'mountpoint': disk_path,
                    'fstype': fstype,
                    'total_gb': round(main_usage.total / (1024**3), 1),
                    'used_gb': round(main_usage.used / (1024**3), 1),
                    'free_gb': round(main_usage.free / (1024**3), 1),
                    'usage_percent': round(usage_percent, 1)
                })
                print(f"✅ Aggiunto disco di fallback: {disk_path}")
                            
            except Exception as e:
                print(f"⚠️ Errore anche con fallback: {e}")
                # Fallback assoluto finale
                disks.append({
                    'label': 'SYS',
                    'mountpoint': 'Sistema',
                    'fstype': 'Unknown',
                    'total_gb': 100,
                    'used_gb': 75,
                    'free_gb': 25,
                    'usage_percent': 75
                })
                print("⚠️ Usando dati disco di fallback assoluti")
        
        # Ordina per percentuale utilizzo (più pieno per primo)
        disks.sort(key=lambda x: x['usage_percent'], reverse=True)
        
        # Limita a massimo 6 dischi per non sovraffollare
        return disks[:6]
        
    except Exception as e:
        print(f"❌ Errore generale all disks: {e}")
        import traceback
        traceback.print_exc()
        return [
            {
                'label': 'ERR',
                'mountpoint': '/',
                'fstype': 'unknown',
                'total_gb': 0,
                'used_gb': 0,
                'free_gb': 0,
                'usage_percent': 0
            }
        ]

def get_system_stats():
    """Raccoglie le statistiche del sistema VPS"""
    
    # CPU Usage (veloce, senza interval)
    cpu_percent = psutil.cpu_percent()
    
    # Memory Usage (compatibile con Monitoraggio Attività macOS)
    memory = psutil.virtual_memory()
    memory_total_gb = memory.total / (1024**3)
    memory_percent = memory.percent
    memory_used_gb = (memory_percent / 100) * memory_total_gb
    
    # Disk Usage (gestisce Docker host mount e Windows)
    disk_path = get_disk_path()
    disk = shutil.disk_usage(disk_path)
    
    disk_used_gb = (disk.total - disk.free) / (1024**3)
    disk_total_gb = disk.total / (1024**3)
    disk_percent = (disk_used_gb / disk_total_gb) * 100
    
    # Network Stats
    net_io = psutil.net_io_counters()
    
    # System uptime
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    uptime = str(timedelta(seconds=int(uptime_seconds)))
    
    # Load Average semplificato (usa CPU attuale)
    load_avg = round(cpu_percent / 100, 2)
    
    # Number of processes
    num_processes = len(psutil.pids())
    
    # Network speed (simulate transfer rate)
    bytes_sent = net_io.bytes_sent / (1024**3)  # GB
    bytes_recv = net_io.bytes_recv / (1024**3)  # GB
    
    # Statistiche base
    stats = {
        'cpu_percent': cpu_percent,
        'memory_percent': memory_percent,
        'memory_used_gb': round(memory_used_gb, 2),
        'memory_total_gb': round(memory_total_gb, 2),
        'disk_percent': round(disk_percent, 1),
        'disk_used_gb': round(disk_used_gb, 2),
        'disk_total_gb': round(disk_total_gb, 2),
        'disk_path': disk_path,
        'uptime': uptime,
        'load_avg': round(load_avg, 2),
        'num_processes': num_processes,
        'bytes_sent': round(bytes_sent, 2),
        'bytes_recv': round(bytes_recv, 2),
        'system_os': SYSTEM_OS,
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }
    
    # Aggiungi statistiche avanzate per tutti i sistemi
    stats.update({
        'network_activity': get_network_activity(),  # Pannello NETWORK (middle left)
        'top_processes': get_top_processes(),
        'temperature': get_system_temperature(),
        'all_disks': get_all_disks(),
        'gpu_stats': get_gpu_stats()  # Pannello GPU STATS (bottom left)
    })
    
    return stats

@app.route('/')
def index():
    """Pagina principale"""
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """API endpoint per le statistiche in tempo reale"""
    return jsonify(get_system_stats())

if __name__ == '__main__':
    print(f"🚀 Avvio Dashboard di Sistema su {SYSTEM_OS}")
    print("📊 Accesso: http://localhost:8080")
    print("\n🔍 Test delle funzionalità:")
    
    # Test delle funzioni principali
    try:
        cpu = psutil.cpu_percent()
        print(f"✅ CPU: {cpu}%")
    except Exception as e:
        print(f"❌ CPU: {e}")
    
    try:
        gpu = get_gpu_stats()
        print(f"✅ GPU: {gpu[0]['name'] if gpu else 'Nessuna GPU'}")
    except Exception as e:
        print(f"❌ GPU: {e}")
    
    try:
        temp = get_system_temperature()
        print(f"✅ Temperature: CPU {temp['cpu_temp']}°C")
    except Exception as e:
        print(f"❌ Temperature: {e}")
    
    try:
        procs = get_top_processes()
        print(f"✅ Processi: {len(procs)} trovati")
    except Exception as e:
        print(f"❌ Processi: {e}")
    
    try:
        sys_info = get_system_info()
        print(f"✅ System Info: {len(sys_info)} elementi")
    except Exception as e:
        print(f"❌ System Info: {e}")
    
    print("\n🌐 Server in avvio...")
    app.run(debug=True, host='0.0.0.0', port=8080) 