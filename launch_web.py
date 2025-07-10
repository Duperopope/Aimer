#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Lanceur Web Simple
© 2025 - Licence Apache 2.0

Script pour lancer rapidement l'interface web
"""

import subprocess
import sys
import webbrowser
import time
import os
from pathlib import Path

def is_codespaces():
    """Détecte si on est dans GitHub Codespaces"""
    return os.getenv('CODESPACES') == 'true'

def launch_web_interface():
    """Lance l'interface web AIMER"""
    print("🚀 Lancement de l'interface web AIMER PRO...")
    
    if is_codespaces():
        print("🌐 Détection: GitHub Codespaces")
        print("💡 L'interface web s'ouvrira automatiquement dans un nouvel onglet")
    
    # Vérifier que l'auto-setup est fait
    try:
        # Lancer l'auto-setup si nécessaire
        print("🔧 Vérification de l'installation...")
        result = subprocess.run([sys.executable, "main.py", "--auto-fix"], 
                               capture_output=False, text=True)
        
        if result.returncode != 0:
            print("⚠️  Auto-setup nécessaire, lancement en cours...")
        
        # Lancer le serveur web
        print("🌐 Démarrage du serveur web...")
        from ui.web_interface.server import AimerWebServer
        
        # Configuration pour Codespaces ou local
        host = "0.0.0.0" if is_codespaces() else "localhost"
        server = AimerWebServer(host=host, port=5000)
        
        # Ouvrir le navigateur (seulement en local)
        if not is_codespaces():
            print("🌍 Ouverture dans le navigateur...")
            webbrowser.open("http://localhost:5000")
        else:
            print("🎯 Interface accessible sur le port 5000")
            print("   GitHub Codespaces ouvrira automatiquement l'onglet")
        
        # Démarrer le serveur
        print("✅ Serveur web démarré !")
        server.run()
        
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        print("💡 Essayez: python main.py --auto-fix")
        return False
    
    return True

if __name__ == "__main__":
    launch_web_interface()
