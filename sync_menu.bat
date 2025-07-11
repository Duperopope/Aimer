@echo off
title AIMER - Contrôleur de Synchronisation
echo 🔄 AIMER - CONTRÔLEUR DE SYNCHRONISATION
echo =======================================
echo.
echo Choisissez une action:
echo.
echo 1. 🚀 Démarrer la synchronisation (15s)
echo 2. ⚡ Démarrage rapide (5s)
echo 3. 🐌 Démarrage lent (30s)
echo 4. 📊 Voir le statut
echo 5. 🛑 Arrêter la synchronisation
echo 6. 📋 Menu complet (Python)
echo.
set /p choice="Votre choix (1-6): "

if "%choice%"=="1" (
    echo 🚀 Démarrage synchronisation standard...
    start "AIMER Sync" cmd /k "python realtime_sync.py"
    echo ✅ Synchronisation démarrée dans une nouvelle fenêtre
) else if "%choice%"=="2" (
    echo ⚡ Démarrage synchronisation rapide...
    start "AIMER Sync Rapide" cmd /k "python realtime_sync.py --interval 5"
    echo ✅ Synchronisation rapide démarrée
) else if "%choice%"=="3" (
    echo 🐌 Démarrage synchronisation lente...
    start "AIMER Sync Lent" cmd /k "python realtime_sync.py --interval 30"
    echo ✅ Synchronisation lente démarrée
) else if "%choice%"=="4" (
    echo 📊 Vérification du statut...
    git status
    git log -1 --oneline
) else if "%choice%"=="5" (
    echo 🛑 Arrêt des synchronisations...
    taskkill /f /im python.exe /fi "WINDOWTITLE eq AIMER Sync*" 2>nul
    echo ✅ Processus de synchronisation arrêtés
) else if "%choice%"=="6" (
    echo 📋 Ouverture du menu Python...
    python sync_controller.py
) else (
    echo ❌ Choix invalide
)

echo.
echo Appuyez sur une touche pour continuer...
pause >nul
