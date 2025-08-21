console.log('🚀 VPS Monitor JavaScript caricato! Versione 10.0 - TEMP CLEAN + DISKS SCAN DIRETTO');

let isMonitoring = true;
let refreshInterval;

// Funzione per aggiornare le statistiche
async function updateStats() {
    if (!isMonitoring) return;
    
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        // Debug: stampa i dati ricevuti
        console.log('📊 Dati ricevuti:', stats);
        console.log('🌐 Network Activity:', stats.network_activity);
        console.log('🌡️ Temperature:', stats.temperature);
        console.log('💽 All Disks:', stats.all_disks);
        console.log('🎮 GPU Stats:', stats.gpu_stats);
        console.log('📋 Top Processes:', stats.top_processes);
        
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
        
        // Aggiorna GPU Stats
        updateGpuStats(stats.gpu_stats);
        
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
        
        // Aggiorna Network Activity
        updateNetworkActivity(stats.network_activity);
        
        // Aggiorna Top Processes
        updateTopProcesses(stats.top_processes);
        
        // Aggiorna Temperature
        updateTemperature(stats.temperature);
        
        // Aggiorna All Disks
        updateAllDisks(stats.all_disks);
        
    } catch (error) {
        console.error('Errore nel recupero delle statistiche:', error);
    }
}

// Funzione per aggiornare l'attività di rete
function updateNetworkActivity(netActivity) {
    console.log('🌐 updateNetworkActivity chiamata con:', netActivity);
    
    const netUpload = document.getElementById('net-upload');
    const netDownload = document.getElementById('net-download');
    const netConnections = document.getElementById('net-connections');
    
    console.log('🌐 Elementi Network trovati:', {
        netUpload: !!netUpload,
        netDownload: !!netDownload,
        netConnections: !!netConnections
    });
    
    if (netActivity) {
        if (netUpload) netUpload.textContent = `${netActivity.upload_speed} KB/s`;
        if (netDownload) netDownload.textContent = `${netActivity.download_speed} KB/s`;
        if (netConnections) netConnections.textContent = netActivity.connections;
        console.log('🌐 Network aggiornato:', netActivity);
    } else {
        if (netUpload) netUpload.textContent = '0 KB/s';
        if (netDownload) netDownload.textContent = '0 KB/s';
        if (netConnections) netConnections.textContent = '0';
        console.log('🌐 Network impostato su default');
    }
}

// Funzione per aggiornare le statistiche GPU (pannello bottom-left)
function updateGpuStats(gpuStats) {
    console.log('🎮 updateGpuStats chiamata con:', gpuStats);
    
    const gpuMainLoad = document.getElementById('gpu-main-load');
    const gpuMemory = document.getElementById('gpu-memory');
    const gpuTemp = document.getElementById('gpu-temp');
    
    console.log('🎮 Elementi GPU trovati:', {
        gpuMainLoad: !!gpuMainLoad,
        gpuMemory: !!gpuMemory,
        gpuTemp: !!gpuTemp
    });
    
    if (gpuStats && gpuStats.length > 0) {
        const gpu = gpuStats[0]; // Usa la prima GPU
        
        if (gpuMainLoad) gpuMainLoad.textContent = `${gpu.load}%`;
        if (gpuMemory) gpuMemory.textContent = `${gpu.memory_used}/${gpu.memory_total} GB`;
        if (gpuTemp) gpuTemp.textContent = `${gpu.temperature}°C`;
        
        console.log('🎮 GPU aggiornata:', gpu);
    } else {
        if (gpuMainLoad) gpuMainLoad.textContent = 'N/A';
        if (gpuMemory) gpuMemory.textContent = 'N/A';
        if (gpuTemp) gpuTemp.textContent = 'N/A';
        console.log('🎮 GPU impostata su N/A');
    }
}

// Funzione per aggiornare i processi top
function updateTopProcesses(processes) {
    const processesList = document.getElementById('processes-list');
    
    // Pulisci la lista esistente
    processesList.innerHTML = '';
    
    if (processes && processes.length > 0) {
        processes.forEach(proc => {
            const processRow = document.createElement('div');
            processRow.className = 'process-row';
            
            // Tronca il nome del processo se troppo lungo
            const processName = proc.name.length > 12 ? proc.name.substring(0, 12) + '...' : proc.name;
            
            processRow.innerHTML = `
                <span class="proc-name">${processName}</span>
                <span class="proc-cpu">${proc.cpu_percent.toFixed(1)}%</span>
                <span class="proc-memory">${proc.memory_percent.toFixed(1)}%</span>
            `;
            
            processesList.appendChild(processRow);
        });
    } else {
        processesList.innerHTML = '<div class="process-row"><span class="proc-name">No data</span><span class="proc-cpu">-</span><span class="proc-memory">-</span></div>';
    }
}

// Funzione per aggiornare le temperature (stile memory)
function updateTemperature(tempData) {
    console.log('🌡️ updateTemperature chiamata con:', tempData);
    
    const tempProgressBars = document.getElementById('temp-progress-bars');
    
    const tempComponents = [
        { name: 'cpu', displayName: 'CPU', temp: tempData.cpu_temp },
        { name: 'gpu', displayName: 'GPU', temp: tempData.gpu_temp },
        { name: 'system', displayName: 'SYS', temp: tempData.system_temp },
        { name: 'mb', displayName: 'MB', temp: tempData.mb_temp }
    ];
    
    // Crea o aggiorna le barre progress (stile memory)
    if (tempProgressBars) {
        // Crea le barre solo se non esistono già
        if (tempProgressBars.children.length === 0) {
            tempComponents.forEach((component, index) => {
                // Crea il container per label + barra
                const barContainer = document.createElement('div');
                
                // Crea l'etichetta
                const label = document.createElement('div');
                label.className = 'temp-bar-label';
                label.textContent = component.displayName;
                label.id = `temp-label-${index}`;
                
                // Crea la barra
                const progressBar = document.createElement('div');
                progressBar.className = 'temp-progress-bar';
                progressBar.id = `temp-bar-${index}`;
                
                // Aggiungi al container
                barContainer.appendChild(label);
                barContainer.appendChild(progressBar);
                tempProgressBars.appendChild(barContainer);
            });
        }
        
        // Aggiorna il contenuto delle barre esistenti
        tempComponents.forEach((component, index) => {
            const progressBar = document.getElementById(`temp-bar-${index}`);
            if (progressBar && component.temp > 0) {
                // Calcola percentuale (range 20-80°C)
                const minTemp = 20;
                const maxTemp = 80;
                const percentage = Math.min(100, Math.max(0, ((component.temp - minTemp) / (maxTemp - minTemp)) * 100));
                
                // Crea le barrette come caratteri (stile memory) - aumentiamo da 30 a 50 per riempire meglio
                const totalBars = 50; 
                const filledBars = Math.floor((percentage / 100) * totalBars);
                let progressText = '';
                
                // Determina colore basato su temperatura
                let colorStyle = '';
                if (component.temp < 40) {
                    colorStyle = 'color: #4a9eff;'; // Blu
                } else if (component.temp < 60) {
                    colorStyle = 'color: #ffa500;'; // Arancione
                } else if (component.temp < 75) {
                    colorStyle = 'color: #ff6b47;'; // Rosso chiaro
                } else {
                    colorStyle = 'color: #ff4a4a;'; // Rosso
                }
                
                // Crea barre piene
                for (let i = 0; i < filledBars; i++) {
                    progressText += `<span style="${colorStyle}">|</span>`;
                }
                
                // Crea barre vuote
                for (let i = filledBars; i < totalBars; i++) {
                    progressText += '<span style="color: #333">|</span>';
                }
                
                progressBar.innerHTML = progressText;
                
                console.log(`🌡️ ${component.name}: ${component.temp}°C, ${percentage}%, ${filledBars}/${totalBars} barre`);
            } else if (progressBar) {
                // Barra vuota se temperatura non disponibile
                const emptyBars = '|'.repeat(50);
                progressBar.innerHTML = `<span style="color: #333">${emptyBars}</span>`;
            }
        });
    }
}

// Funzione per aggiornare tutti i dischi (stile storage)
function updateAllDisks(allDisks) {
    console.log('💽 updateAllDisks chiamata con:', allDisks);
    console.log('💽 Tipo di allDisks:', typeof allDisks);
    console.log('💽 È array?', Array.isArray(allDisks));
    console.log('💽 Lunghezza:', allDisks ? allDisks.length : 'undefined');
    
    const disksBarsContainer = document.getElementById('disks-bars-container');
    const disksInfo = document.getElementById('disks-info');
    
    console.log('💽 disksBarsContainer trovato:', !!disksBarsContainer);
    console.log('💽 disksInfo trovato:', !!disksInfo);
    
    if (!disksBarsContainer || !disksInfo) {
        console.error('💽 Elementi disks non trovati!');
        console.error('💽 disksBarsContainer:', disksBarsContainer);
        console.error('💽 disksInfo:', disksInfo);
        return;
    }
    
    // Se non abbiamo dati o array vuoto, mostra messaggio
    if (!allDisks || !Array.isArray(allDisks) || allDisks.length === 0) {
        console.warn('💽 Nessun disco trovato, mostro placeholder');
        disksBarsContainer.innerHTML = '<div style="color: #ccc; text-align: center; padding: 20px;">Caricamento dischi...</div>';
        disksInfo.innerHTML = '<div style="color: #888; font-size: 10px;">Rilevamento dischi in corso</div>';
        return;
    }
    
    // Pulisci i container
    disksBarsContainer.innerHTML = '';
    disksInfo.innerHTML = '';
    
    if (allDisks && allDisks.length > 0) {
        console.log('💽 Aggiornamento con', allDisks.length, 'dischi');
        
        // Crea le barre verticali per ogni disco (stile storage)
        allDisks.forEach(disk => {
            const diskBar = document.createElement('div');
            diskBar.className = 'disk-storage-bar';
            
            // Calcola altezza barra basata su percentuale utilizzo
            const barHeight = Math.floor((disk.usage_percent / 100) * 60);
            diskBar.style.height = Math.max(8, barHeight) + 'px';
            
            // Colore basato su utilizzo
            if (disk.usage_percent > 80) {
                diskBar.style.backgroundColor = '#ff4a4a'; // Rosso
            } else if (disk.usage_percent > 60) {
                diskBar.style.backgroundColor = '#ffa500'; // Arancione
            } else {
                diskBar.style.backgroundColor = '#fff'; // Bianco
            }
            
            disksBarsContainer.appendChild(diskBar);
        });
        
        // Crea le info testuali
        allDisks.forEach(disk => {
            const diskInfoRow = document.createElement('div');
            diskInfoRow.className = 'disk-info-row';
            
            diskInfoRow.innerHTML = `
                <span class="left">${disk.label}</span>
                <span class="right">${disk.used_gb}/${disk.total_gb}GB</span>
            `;
            
            disksInfo.appendChild(diskInfoRow);
            
            console.log(`💽 Aggiunto: ${disk.label} - ${disk.usage_percent}% (${disk.used_gb}/${disk.total_gb}GB)`);
        });
        
        // Aggiungi percentuale media se ci sono più dischi
        if (allDisks.length > 1) {
            const avgUsage = allDisks.reduce((sum, disk) => sum + disk.usage_percent, 0) / allDisks.length;
            const totalUsed = allDisks.reduce((sum, disk) => sum + disk.used_gb, 0);
            const totalSize = allDisks.reduce((sum, disk) => sum + disk.total_gb, 0);
            
            const avgRow = document.createElement('div');
            avgRow.className = 'disk-info-row';
            avgRow.innerHTML = `
                <span class="left">AVG</span>
                <span class="right">${avgUsage.toFixed(1)}%</span>
            `;
            disksInfo.appendChild(avgRow);
        }
        
    } else {
        console.log('💽 Nessun disco trovato');
        disksBarsContainer.innerHTML = '<div class="disk-storage-bar" style="height: 8px; background: #333;"></div>';
        disksInfo.innerHTML = '<div class="disk-info-row"><span class="left">ERR</span><span class="right">N/A</span></div>';
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
    console.log('🎯 VPS Monitor inizializzato - DOM caricato');
    console.log('🔍 Verifico elementi HTML...');
    
    // Verifica che tutti gli elementi esistano
    const elements = [
        'cpu-radial', 'cpu-percent', 'memory-progress', 'memory-text', 'memory-overall',
        'uptime', 'gpu-load', 'gpu-memory', 'gpu-temp', 'processes-list', 
        'cpu-temp', 'gpu-temp', 'system-temp', 'mb-temp', 'services-list'
    ];
    
    elements.forEach(id => {
        const element = document.getElementById(id);
        console.log(`📋 ${id}:`, !!element);
    });
    
    console.log('🚀 Avvio aggiornamento statistiche...');
    
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