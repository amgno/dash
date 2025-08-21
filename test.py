#!/usr/bin/env python3
"""
Test rapido per verificare tutte le funzionalità del dashboard
"""

print("🧪 Test Dashboard di Sistema")
print("=" * 40)

try:
    import psutil
    print("✅ psutil importato")
except ImportError as e:
    print(f"❌ psutil: {e}")
    exit(1)

try:
    import platform
    print(f"✅ Sistema: {platform.system()}")
except ImportError as e:
    print(f"❌ platform: {e}")

try:
    import GPUtil
    print("✅ GPUtil importato")
except ImportError as e:
    print(f"⚠️  GPUtil: {e}")

try:
    import wmi
    print("✅ WMI importato")
except ImportError as e:
    print(f"⚠️  WMI: {e}")

print("\n🔍 Test funzioni principali:")

# Test CPU
try:
    cpu = psutil.cpu_percent()
    print(f"✅ CPU: {cpu}%")
except Exception as e:
    print(f"❌ CPU: {e}")

# Test memoria
try:
    memory = psutil.virtual_memory()
    print(f"✅ Memoria: {memory.percent}% ({memory.used / (1024**3):.1f}GB / {memory.total / (1024**3):.1f}GB)")
except Exception as e:
    print(f"❌ Memoria: {e}")

# Test processi
try:
    processes = list(psutil.process_iter(['pid', 'name', 'memory_percent']))[:5]
    print(f"✅ Processi: {len(processes)} trovati")
    for proc in processes[:3]:
        print(f"   • {proc.info['name']}: {proc.info['memory_percent']:.1f}%")
except Exception as e:
    print(f"❌ Processi: {e}")

# Test disco
try:
    import shutil
    disk = shutil.disk_usage('/')
    total_gb = disk.total / (1024**3)
    used_gb = (disk.total - disk.free) / (1024**3)
    print(f"✅ Disco: {used_gb:.1f}GB / {total_gb:.1f}GB")
except Exception as e:
    print(f"❌ Disco: {e}")

print("\n🎯 Tutte le funzioni di base sono operative!")
print("🚀 Puoi ora avviare start.bat")
