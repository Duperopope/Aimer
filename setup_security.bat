@echo off
echo 🚀 AIMER - Installation du Système de Sécurité
echo ============================================
echo.

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python non trouvé ! Installez Python 3.10+
    pause
    exit /b 1
)

echo ✅ Python détecté

REM Installer les dépendances de sécurité
echo 📦 Installation des dépendances de sécurité...
python -m pip install -r requirements_security.txt

if errorlevel 1 (
    echo ⚠️ Certaines dépendances ont échoué, mais on continue...
)

REM Créer le backup sécurisé initial
echo.
echo 🔐 Voulez-vous créer un backup SSH sécurisé maintenant ? (y/n)
set /p create_backup="Votre choix: "

if /i "%create_backup%"=="y" (
    echo 🔒 Lancement du système de backup sécurisé...
    python secure_ssh_recovery.py
)

REM Configuration Git
echo.
echo 🔧 Configuration Git locale pour AIMER...
git config user.name "Samir Medjaher"
git config user.email "s.medjaher@gmail.com"

echo.
echo ✅ INSTALLATION TERMINÉE !
echo.
echo 📋 PROCHAINES ÉTAPES :
echo 1. Testez la connexion SSH : ssh -T git@github.com
echo 2. Créez un backup sécurisé : python secure_ssh_recovery.py
echo 3. Poussez vos changements : git add . && git commit -m "🔧 Setup sécurité" && git push
echo 4. Vérifiez les workflows : https://github.com/Duperopope/aimer/actions
echo.
echo 🎉 Votre projet AIMER est maintenant ULTRA-SÉCURISÉ !
pause
