#!/usr/bin/env python3
"""
AIMER PRO - Serveur de Test avec Debug Complet
VRAI debugging pour identifier tous les problèmes
"""

import os
import sys
from pathlib import Path
import traceback

print("🔍 DÉBUT DU DEBUG COMPLET")
print("=" * 50)

# 1. Vérification de l'environnement
print("\n1️⃣ VÉRIFICATION ENVIRONNEMENT")
print(f"📁 Répertoire actuel: {os.getcwd()}")
print(f"🐍 Python executable: {sys.executable}")
print(f"📂 Python path: {sys.path[:3]}...")

# 2. Vérification des fichiers critiques
print("\n2️⃣ VÉRIFICATION FICHIERS")
files_to_check = [
    "ui/web_interface/templates/index.html",
    "ui/web_interface/server.py", 
    "core/detector.py",
    "core/logger.py"
]

for file_path in files_to_check:
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"✅ {file_path} ({size} bytes)")
    else:
        print(f"❌ {file_path} - MANQUANT")

# 3. Test des imports critiques
print("\n3️⃣ TEST IMPORTS")
try:
    from flask import Flask, render_template, jsonify
    print("✅ Flask importé")
except Exception as e:
    print(f"❌ Flask: {e}")
    sys.exit(1)

try:
    import cv2
    print("✅ OpenCV importé")
except Exception as e:
    print(f"❌ OpenCV: {e}")

try:
    import numpy as np
    print("✅ NumPy importé")
except Exception as e:
    print(f"❌ NumPy: {e}")

# 4. Test import des modules AIMER
print("\n4️⃣ TEST MODULES AIMER")
sys.path.append(str(Path.cwd()))
try:
    from core.detector import SmartDetector
    print("✅ SmartDetector importé")
    detector = SmartDetector()
    print("✅ SmartDetector instancié")
except Exception as e:
    print(f"❌ SmartDetector: {e}")
    traceback.print_exc()

try:
    from core.logger import Logger
    print("✅ Logger importé")
    logger = Logger("Test")
    print("✅ Logger instancié")
except Exception as e:
    print(f"❌ Logger: {e}")
    traceback.print_exc()

# 5. Création du serveur Flask avec debug complet
print("\n5️⃣ CRÉATION SERVEUR FLASK")

app = Flask(__name__, 
           template_folder='ui/web_interface/templates',
           static_folder='ui/web_interface/static')

print(f"📁 Template folder: {app.template_folder}")
print(f"📁 Static folder: {app.static_folder}")

# Vérification que les dossiers existent
template_path = Path(app.template_folder) if app.template_folder else Path(".")
static_path = Path(app.static_folder) if app.static_folder else Path(".")

print(f"📁 Template path exists: {template_path.exists()}")
if template_path.exists():
    templates = list(template_path.glob("*.html"))
    print(f"📄 Templates trouvés: {[t.name for t in templates]}")

print(f"📁 Static path exists: {static_path.exists()}")

@app.route('/')
def index():
    """Page d'accueil avec debug"""
    print("🏠 Route / appelée")
    try:
        print("🔍 Tentative de rendu de index.html")
        return render_template('index.html')
    except Exception as e:
        print(f"❌ Erreur rendu template: {e}")
        return f"""
        <html>
            <head><title>AIMER PRO - Debug</title></head>
            <body>
                <h1>🔧 AIMER PRO - Mode Debug</h1>
                <h2>❌ Erreur Template</h2>
                <p><strong>Erreur:</strong> {e}</p>
                <p><strong>Template folder:</strong> {app.template_folder}</p>
                <p><strong>Working directory:</strong> {os.getcwd()}</p>
                <hr>
                <h3>Tests disponibles:</h3>
                <ul>
                    <li><a href="/test-simple">Test Simple</a></li>
                    <li><a href="/test-webcam">Test Webcam</a></li>
                    <li><a href="/debug-info">Debug Info</a></li>
                </ul>
            </body>
        </html>
        """

@app.route('/test-simple')
def test_simple():
    """Test simple sans template"""
    return """
    <html>
        <head>
            <title>AIMER PRO - Test Simple</title>
            <style>
                body { font-family: Arial; margin: 40px; background: #f0f0f0; }
                .container { background: white; padding: 20px; border-radius: 10px; }
                .success { color: green; font-weight: bold; }
                .error { color: red; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎯 AIMER PRO - Test Simple</h1>
                <div class="success">✅ Flask fonctionne !</div>
                <div class="success">✅ Serveur web actif</div>
                <div class="success">✅ Routes fonctionnelles</div>
                <p><a href="/">← Retour</a></p>
            </div>
        </body>
    </html>
    """

@app.route('/test-webcam')
def test_webcam():
    """Test webcam avec debug"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                h, w = frame.shape[:2]
                cap.release()
                status = f"✅ Webcam OK - Résolution: {w}x{h}"
                color = "green"
            else:
                cap.release()
                status = "⚠️ Webcam s'ouvre mais ne lit pas"
                color = "orange"
        else:
            status = "❌ Webcam non accessible"
            color = "red"
    except Exception as e:
        status = f"❌ Erreur webcam: {e}"
        color = "red"
    
    return f"""
    <html>
        <head><title>AIMER PRO - Test Webcam</title></head>
        <body style="font-family: Arial; margin: 40px; background: #f0f0f0;">
            <div style="background: white; padding: 20px; border-radius: 10px;">
                <h1>📹 AIMER PRO - Test Webcam</h1>
                <div style="color: {color}; font-weight: bold; font-size: 18px;">
                    {status}
                </div>
                <p><a href="/">← Retour</a></p>
            </div>
        </body>
    </html>
    """

@app.route('/debug-info')
def debug_info():
    """Informations de debug détaillées"""
    return f"""
    <html>
        <head><title>AIMER PRO - Debug Info</title></head>
        <body style="font-family: Arial; margin: 40px; background: #f0f0f0;">
            <div style="background: white; padding: 20px; border-radius: 10px;">
                <h1>🔧 AIMER PRO - Debug Info</h1>
                <h3>Environnement:</h3>
                <ul>
                    <li><strong>Working Directory:</strong> {os.getcwd()}</li>
                    <li><strong>Python:</strong> {sys.executable}</li>
                    <li><strong>Template Folder:</strong> {app.template_folder}</li>
                    <li><strong>Static Folder:</strong> {app.static_folder}</li>
                </ul>
                <h3>Fichiers:</h3>
                <ul>
                    <li>Templates: {Path(app.template_folder).exists() if app.template_folder else False}</li>
                    <li>Static: {Path(app.static_folder).exists() if app.static_folder else False}</li>
                </ul>
                <p><a href="/">← Retour</a></p>
            </div>
        </body>
    </html>
    """

def main():
    print("\n6️⃣ LANCEMENT SERVEUR")
    print("🌐 http://localhost:5000")
    print("🧪 http://localhost:5000/test-simple")
    print("📹 http://localhost:5000/test-webcam")
    print("🔧 http://localhost:5000/debug-info")
    print("\n🚀 Serveur prêt avec debug complet !")
    
    try:
        app.run(host='localhost', port=5000, debug=True)
    except Exception as e:
        print(f"❌ Erreur serveur: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    main()
