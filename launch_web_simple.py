#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Lanceur Web Simple (Version Codespaces)
© 2025 - Licence Apache 2.0

Version simplifiée pour éviter l'auto-setup répétitif
"""

import os
import sys

def is_codespaces():
    """Détecte si on est dans GitHub Codespaces"""
    return os.getenv('CODESPACES') == 'true'

def launch_web_simple():
    """Lance directement l'interface web sans auto-setup"""
    print("🚀 Lancement direct de l'interface web AIMER PRO...")
    
    if is_codespaces():
        print("🌐 Détection: GitHub Codespaces")
        print("💡 L'interface web s'ouvrira automatiquement dans un nouvel onglet")
    
    try:
        print("🌐 Démarrage du serveur web...")
        from ui.web_interface.server import AimerWebServer
        
        # Configuration pour Codespaces ou local
        host = "0.0.0.0" if is_codespaces() else "localhost"
        server = AimerWebServer(host=host, port=5000)
        
        if not is_codespaces():
            import webbrowser
            print("🌍 Ouverture dans le navigateur...")
            webbrowser.open("http://localhost:5000")
        else:
            print("🎯 Interface accessible sur le port 5000")
            print("   GitHub Codespaces ouvrira automatiquement l'onglet")
        
        # Démarrer le serveur
        print("✅ Serveur web démarré !")
        print("🔗 URL: http://localhost:5000" if not is_codespaces() else "🔗 Interface accessible via Codespaces")
        server.run()
        
    except ImportError as e:
        print(f"❌ Module manquant: {e}")
        print("💡 Essayez d'abord: python main.py --auto-fix")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        print("💡 Vérifiez que tous les packages sont installés")
        return False
    
    return True

if __name__ == "__main__":
    launch_web_simple()
