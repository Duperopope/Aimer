@echo off
echo.
echo 🎯 Système de Visée Intelligent
echo ================================
echo.

REM Vérifier si l'environnement virtuel existe
if not exist ".venv" (
    echo ❌ Environnement virtuel non trouvé!
    echo 💡 Créez-le avec: python -m venv .venv
    echo    Puis installez: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activer l'environnement virtuel
echo 🔄 Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat

REM Vérifier si les dépendances sont installées
python -c "import ultralytics, cv2, numpy, tkinter" 2>nul
if errorlevel 1 (
    echo ❌ Dépendances manquantes!
    echo 🔄 Installation automatique...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Erreur lors de l'installation
        pause
        exit /b 1
    )
)

echo ✅ Environnement prêt!
echo 🚀 Lancement de l'application...
echo.

REM Lancer l'application
python launcher_interactive.py

echo.
echo 👋 Application fermée
pause
