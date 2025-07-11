@echo off
REM 🔍 AIMER Error Monitor - Launcher
REM Lance le monitoring des erreurs en arrière-plan

echo 🔍 AIMER Error Monitor - Demarrage
echo ====================================

REM Vérifier si Python est disponible
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python non trouve. Veuillez installer Python.
    pause
    exit /b 1
)

REM Vérifier si le monitoring est déjà actif
if exist ".error_monitor.pid" (
    echo ⚠️ Monitoring deja actif. Arrêt en cours...
    taskkill /F /PID /T < .error_monitor.pid >nul 2>&1
    del .error_monitor.pid >nul 2>&1
    timeout /t 2 >nul
)

echo 🚀 Lancement du monitoring des erreurs...
echo 📁 Dossier: %CD%
echo ⏰ Surveillance toutes les 10 secondes
echo 🔧 Auto-correction activee
echo 🛑 Utilisez Ctrl+C pour arreter
echo.

REM Lancer le monitoring
python error_monitor.py

echo.
echo 🏁 Monitoring termine.
pause
