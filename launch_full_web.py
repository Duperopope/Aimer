#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Lanceur Interface Web Complète
© 2025 - Licence Apache 2.0

Lanceur pour l'interface web avec webcam temps réel et support YouTube
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Vérifier les dépendances nécessaires"""
    print("🔍 Vérification des dépendances...")
    
    missing_deps = []
    
    try:
        import flask
        print("✅ Flask installé")
    except ImportError:
        missing_deps.append("flask")
    
    try:
        import cv2
        print("✅ OpenCV installé")
    except ImportError:
        missing_deps.append("opencv-python-headless")
    
    try:
        import numpy
        print("✅ NumPy installé")
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        import yt_dlp
        print("✅ yt-dlp installé")
    except ImportError:
        missing_deps.append("yt-dlp")
    
    if missing_deps:
        print(f"❌ Dépendances manquantes: {', '.join(missing_deps)}")
        print("💡 Installation automatique...")
        
        try:
            for dep in missing_deps:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print("✅ Toutes les dépendances installées !")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur installation: {e}")
            return False
    
    return True

def main():
    """Fonction principale"""
    print("🚀 AIMER PRO - Interface Web Complète")
    print("=" * 50)
    print("Features: 📤 Upload | 📹 Webcam | 📺 YouTube | 🔌 API")
    print()
    
    # Vérifier qu'on est dans le bon répertoire
    if not Path("ui/web_interface/server_full.py").exists():
        print("❌ Erreur: Exécutez ce script depuis le répertoire racine AIMER")
        return
    
    # Vérifier les dépendances
    if not check_dependencies():
        print("❌ Impossible de continuer sans les dépendances")
        return
    
    # Détecter l'environnement
    is_codespaces = os.getenv('CODESPACES') == 'true'
    is_local = not is_codespaces
    
    print(f"🌍 Environnement: {'GitHub Codespaces' if is_codespaces else 'Local'}")
    
    # Configuration du serveur
    host = "0.0.0.0" if is_codespaces else "localhost"
    port = 5000
    
    print(f"🌐 Serveur: http://{host}:{port}")
    print()
    print("📋 Fonctionnalités disponibles:")
    print("  • 📤 Upload d'images avec détection")
    print("  • 📹 Webcam temps réel (nécessite autorisation navigateur)")
    print("  • 📺 Analyse vidéo YouTube (en développement)")
    print("  • 🔌 API REST complète")
    print()
    
    try:
        # Ajouter le répertoire au path
        sys.path.append(str(Path.cwd()))
        
        # Importer et démarrer le serveur
        from ui.web_interface.server_full import AimerWebServerFull
        
        print("⚡ Démarrage du serveur...")
        server = AimerWebServerFull(host=host, port=port)
        
        # Ouvrir le navigateur automatiquement en local
        if is_local:
            print("🌍 Ouverture automatique du navigateur...")
            time.sleep(2)  # Laisser le temps au serveur de démarrer
            webbrowser.open(f"http://localhost:{port}")
        
        print()
        print("🎯 Instructions:")
        if is_codespaces:
            print("  • L'interface s'ouvrira automatiquement dans Codespaces")
            print("  • Utilisez l'onglet 'Ports' pour accéder à l'interface")
        else:
            print(f"  • Ouvrez http://localhost:{port} dans votre navigateur")
        
        print("  • Autorisez l'accès webcam pour la détection temps réel")
        print("  • Utilisez Ctrl+C pour arrêter le serveur")
        print()
        
        # Démarrer le serveur
        server.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté par l'utilisateur")
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("💡 Vérifiez que tous les fichiers sont présents")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        print("💡 Vérifiez la configuration et réessayez")

if __name__ == "__main__":
    main()
