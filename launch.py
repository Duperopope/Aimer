#!/usr/bin/env python3
"""
AIMER PRO - Lanceur Unifié ✨
Plus de doublons ! Version finale et propre
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def print_banner():
    """Affiche le banner AIMER PRO UNIFIÉ"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🎯 AIMER PRO UNIFIÉ                      ║
║                  VERSION FINALE - CLEAN                     ║
║                                                              ║
║    ✅ Serveur Unique et Optimisé                             ║
║    ✅ Détection COCO Intelligente                            ║
║    ✅ Test Webcam Intégré                                    ║
║    🧹 Plus de Doublons !                                     ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Vérifie les dépendances essentielles"""
    try:
        import flask
        import cv2
        import numpy
        print("✅ Dépendances Flask, OpenCV, NumPy: OK")
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("🔧 Installez avec: pip install -r requirements_web.txt")
        return False
    
    try:
        import yt_dlp
        print("✅ Dépendance YouTube (yt-dlp): OK")
    except ImportError:
        print("⚠️  yt-dlp manquant (YouTube non disponible)")
    
    try:
        from flask_socketio import SocketIO
        print("✅ Dépendance SocketIO: OK")
    except ImportError:
        print("❌ flask-socketio manquant")
        return False
    
    return True

def check_webcam_simple():
    """Test rapide de la webcam"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                print("✅ Webcam: Détectée et fonctionnelle")
                return True
        
        print("⚠️  Webcam: Non détectée (test détaillé dans l'interface)")
        return False
    except Exception as e:
        print(f"⚠️  Webcam: Erreur test - {e}")
        return False

def main():
    """Point d'entrée principal"""
    print_banner()
    
    # Arguments
    import argparse
    parser = argparse.ArgumentParser(description='AIMER PRO Lanceur Unifié')
    parser.add_argument('--host', default='localhost', help='Adresse IP (défaut: localhost)')
    parser.add_argument('--port', type=int, default=5000, help='Port (défaut: 5000)')
    parser.add_argument('--debug', action='store_true', help='Mode debug')
    parser.add_argument('--no-browser', action='store_true', help='Ne pas ouvrir le navigateur')
    
    args = parser.parse_args()
    
    print("🔍 Vérifications système...")
    
    # Vérifications
    if not check_dependencies():
        print("❌ Dépendances manquantes. Arrêt.")
        return
    
    webcam_ok = check_webcam_simple()
    webcam_status = '✅' if webcam_ok else '⚠️ (test détaillé dans l\'interface)'
    
    print(f"""
🚀 Configuration du serveur:
  📍 Host: {args.host}
  🔌 Port: {args.port}
  🐛 Debug: {'✅' if args.debug else '❌'}
  📹 Webcam: {webcam_status}

🌐 Interface web: http://{args.host}:{args.port}
    """)
    
    # Lancement du serveur
    try:
        print("🚀 Lancement du serveur AIMER PRO...")
        
        # Import du serveur directement
        sys.path.append(str(Path(__file__).parent / "ui" / "web_interface"))
        from ui.web_interface.server import AimerWebServer
        
        # Ouverture du navigateur (sauf si --no-browser)
        if not args.no_browser:
            def open_browser():
                import time
                time.sleep(3)  # Attendre que le serveur démarre
                webbrowser.open(f"http://{args.host}:{args.port}")
            
            import threading
            threading.Thread(target=open_browser, daemon=True).start()
        
        # Lancement du serveur
        server = AimerWebServer(host=args.host, port=args.port)
        server.run(debug=args.debug)
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lancement: {e}")

if __name__ == '__main__':
    main()
