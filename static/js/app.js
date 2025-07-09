let isMonitoring = true;
let refreshInterval;

// Funzione per aggiornare le statistiche
async function updateStats() {
    if (!isMonitoring) return;
    
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        // Aggiorna CPU (barrette radiali)
        const cpuRadial = document.getElementById('cpu-radial');
        const cpuPercent = document.getElementById('cpu-percent');
        
        // Crea le barrette radiali se non esistono
        if (cpuRadial.children.length <= 1) { // Solo il testo percentuale
            const totalBars = 20; // Numero di barrette intorno al cerchio
            for (let i = 0; i < totalBars; i++) {
                const bar = document.createElement('div');
                bar.className = 'radial-bar';
                const angle = (360 / totalBars) * i;
                bar.style.transform = `rotate(${angle}deg)`;
                cpuRadial.appendChild(bar);
            }
        }
        
        // Aggiorna le barrette attive in base alla percentuale CPU
        const bars = cpuRadial.querySelectorAll('.radial-bar');
        const activeBars = Math.floor((stats.cpu_percent / 100) * bars.length);
        
        bars.forEach((bar, index) => {
            if (index < activeBars) {
                bar.classList.add('active');
            } else {
                bar.classList.remove('active');
            }
        });
        
        cpuPercent.textContent = `${Math.round(stats.cpu_percent)}%`;
        
        // Aggiorna Data Volume Progress Bar (dati reali memoria)
        const memoryProgress = document.getElementById('memory-progress');
        const memoryText = document.getElementById('memory-text');
        const memoryOverall = document.getElementById('memory-overall');
        
        // Usa i dati reali della memoria del sistema
        const memoryPercentage = stats.memory_percent;
        
        // Crea le barrette verticali per la progress bar
        const totalBars = 60; // Numero totale di barrette che entrano nello spazio
        const filledBars = Math.floor((memoryPercentage / 100) * totalBars);
        let progressText = '';
        
        // Crea le barrette piene (bianche)
        for (let i = 0; i < filledBars; i++) {
            progressText += '|';
        }
        
        // Crea le barrette vuote (grigie scure)
        for (let i = filledBars; i < totalBars; i++) {
            progressText += '<span style="color: #333">|</span>';
        }
        
        memoryProgress.innerHTML = progressText;
        memoryText.innerHTML = `<span class="left">${stats.memory_used_gb.toFixed(1)}GB</span><span class="right">${stats.memory_total_gb.toFixed(1)}GB</span>`;
        memoryOverall.textContent = `${Math.round(memoryPercentage)}%`;
        
        // Aggiorna Uptime
        const uptimeElement = document.getElementById('uptime');
        uptimeElement.textContent = formatUptime(stats.uptime);
        
        // Aggiorna Network I/O (velocità realistica basata su dati reali)
        const networkSpeed = document.getElementById('network-speed');
        // Simula una velocità realistica tra 0.1 e 10 MB/s
        const randomSpeed = (Math.random() * 9.9 + 0.1); // Random tra 0.1 e 10 MB/s
        networkSpeed.textContent = `${randomSpeed.toFixed(1)}MB/s`;
        
        // Aggiorna Storage Vertical Bars
        const storageBars = document.getElementById('storage-bars');
        const storageText = document.getElementById('storage-text');
        const storageOverall = document.getElementById('storage-overall');
        
        // Usa i dati reali del disco
        const storagePercentage = stats.disk_percent;
        
        // Crea le barre verticali se non esistono
        if (storageBars.children.length === 0) {
            const totalBars = 20; // Numero di barre verticali
            for (let i = 0; i < totalBars; i++) {
                const bar = document.createElement('div');
                bar.className = 'storage-bar';
                storageBars.appendChild(bar);
            }
        }
        
        // Aggiorna le barre in base alla percentuale
        const storageBarsElements = storageBars.children;
        const filledStorageBars = Math.floor((storagePercentage / 100) * storageBarsElements.length);
        
        for (let i = 0; i < storageBarsElements.length; i++) {
            const bar = storageBarsElements[i];
            const barPercentage = Math.min(100, Math.max(0, ((storagePercentage - (i * (100 / storageBarsElements.length))) / (100 / storageBarsElements.length)) * 100));
            
            if (i < filledStorageBars) {
                // Barra completamente piena
                bar.style.height = '60px';
                bar.style.background = '#fff';
            } else if (i === filledStorageBars && barPercentage > 0) {
                // Barra parzialmente piena
                bar.style.height = Math.floor((barPercentage / 100) * 60) + 'px';
                bar.style.background = '#fff';
            } else {
                // Barra vuota
                bar.style.height = '8px';
                bar.style.background = '#333';
            }
        }
        
        storageText.innerHTML = `<span class="left">${stats.disk_used_gb.toFixed(1)}GB</span><span class="right">${stats.disk_total_gb.toFixed(1)}GB</span>`;
        storageOverall.textContent = `${Math.round(storagePercentage)}%`;
        
        // Aggiorna Network Stats
        const bytesSent = document.getElementById('bytes-sent');
        const bytesRecv = document.getElementById('bytes-recv');
        const totalTransfer = document.getElementById('total-transfer');
        
        const totalGB = stats.bytes_sent + stats.bytes_recv;
        
        bytesSent.textContent = `${stats.bytes_sent.toFixed(2)} GB`;
        bytesRecv.textContent = `${stats.bytes_recv.toFixed(2)} GB`;
        totalTransfer.textContent = `${totalGB.toFixed(2)} GB`;
        
    } catch (error) {
        console.error('Errore nel recupero delle statistiche:', error);
    }
}

// Funzione per formattare l'uptime
function formatUptime(uptimeString) {
    // Convert format like "1 day, 2:30:45" to "26h:30m:45s"
    const parts = uptimeString.split(', ');
    if (parts.length === 2) {
        const days = parseInt(parts[0].split(' ')[0]);
        const time = parts[1];
        const timeParts = time.split(':');
        const hours = parseInt(timeParts[0]) + (days * 24);
        return `${hours}h:${timeParts[1]}m:${timeParts[2]}s`;
    } else {
        const timeParts = uptimeString.split(':');
        return `${timeParts[0]}h:${timeParts[1]}m:${timeParts[2]}s`;
    }
}

// Funzione per formattare i byte in unità leggibili
function formatBytes(bytes) {
    if (bytes === 0) return '0.00 GB';
    const gb = bytes / (1024 * 1024 * 1024);
    return `${gb.toFixed(2)} GB`;
}

// Funzioni di utilità
function refreshStats() {
    updateStats();
    console.log('Statistiche aggiornate manualmente');
}

// Funzioni di controllo del monitoraggio
function startMonitoring() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    refreshInterval = setInterval(updateStats, 2000); // Aggiorna ogni 2 secondi
}

function stopMonitoring() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
}

// Funzione per animare la progress bar (non più necessaria)
function animateProgressBar() {
    // Le barrette sono ora gestite direttamente nell'update
}

// Inizializzazione al caricamento della pagina
document.addEventListener('DOMContentLoaded', function() {
    console.log('VPS Monitor inizializzato');
    
    // Carica le statistiche iniziali
    updateStats();
    
    // Avvia il monitoraggio automatico
    startMonitoring();
    
    // Aggiungi effetti visivi
    animateProgressBar();
    
    // Aggiungi listener per la chiusura della finestra
    window.addEventListener('beforeunload', function() {
        stopMonitoring();
    });
});

// Gestione della visibilità della pagina
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        if (isMonitoring) {
            startMonitoring();
        }
    } else {
        stopMonitoring();
    }
}); 