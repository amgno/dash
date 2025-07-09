@echo off
echo ================================================
echo     🚀 DASHBOARD DI SISTEMA - AVVIO WINDOWS
echo ================================================
echo.

REM Controlla se Python è installato
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERRORE: Python non è installato o non è nel PATH
    echo 📥 Installa Python da: https://www.python.org/downloads/
    echo ⚠️  Assicurati di selezionare "Add Python to PATH" durante l'installazione
    pause
    exit /b 1
)

echo ✅ Python trovato:
python --version

REM Controlla se pip è disponibile
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERRORE: pip non è disponibile
    echo 🔧 Prova a reinstallare Python con pip incluso
    pause
    exit /b 1
)

echo ✅ pip trovato:
pip --version
echo.

REM Installa le dipendenze
echo 📦 Installazione dipendenze...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ ERRORE: Impossibile installare le dipendenze
    echo 🔍 Controlla la connessione internet e riprova
    pause
    exit /b 1
)

echo ✅ Dipendenze installate con successo!
echo.

REM Avvia l'applicazione
echo 🌟 Avvio Dashboard di Sistema...
echo 🌐 L'applicazione sarà disponibile su: http://localhost:8080
echo 🛑 Premi Ctrl+C per fermare il server
echo.

python app.py

echo.
echo 👋 Dashboard fermata
pause 