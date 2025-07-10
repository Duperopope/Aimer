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
from pathlib import Path

def launch_web_interface():
    """Lance l'interface web AIMER"""
    print("🚀 Lancement de l'interface web AIMER PRO...")
    
    # Vérifier que l'auto-setup est fait
    try:
        # Lancer l'auto-setup si nécessaire
        print("🔧 Vérification de l'installation...")
        subprocess.run([sys.executable, "main.py", "--auto-fix"], 
                      check=True, capture_output=True)
        
        # Lancer le serveur web
        print("🌐 Démarrage du serveur web...")
        from ui.web_interface.server import AimerWebServer
        
        server = AimerWebServer(host="0.0.0.0", port=5000)
        
        # Ouvrir le navigateur
        print("🌍 Ouverture dans le navigateur...")
        webbrowser.open("http://localhost:5000")
        
        # Démarrer le serveur
        server.run()
        
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        print("💡 Essayez: python main.py --auto-fix")
        return False
    
    return True

if __name__ == "__main__":
    launch_web_interface()
