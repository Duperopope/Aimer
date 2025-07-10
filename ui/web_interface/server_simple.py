#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Serveur Web Simplifié (Version Codespaces)
© 2025 - Licence Apache 2.0

Version simplifiée sans Detectron2 pour démonstration
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, jsonify

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent.parent))

class AimerWebServerSimple:
    """Serveur web AIMER simplifié pour démonstration"""

    def __init__(self, host="localhost", port=5000):
        self.host = host
        self.port = port

        # Initialiser Flask
        self.app = Flask(__name__, 
                        template_folder="templates", 
                        static_folder="static")
        self.app.config["SECRET_KEY"] = "aimer_pro_demo_key_2025"

        # Configuration des routes
        self._setup_routes()

    def _setup_routes(self):
        """Configuration des routes de l'application"""
        
        @self.app.route("/")
        def index():
            """Page d'accueil"""
            return render_template("demo.html")

        @self.app.route("/api/status")
        def api_status():
            """API de statut"""
            return jsonify({
                "status": "running",
                "version": "0.1.1",
                "mode": "demo",
                "features": {
                    "web_interface": True,
                    "detectron2": False,
                    "detection": False,
                    "codespaces": os.getenv('CODESPACES') == 'true'
                }
            })

        @self.app.route("/api/demo")
        def api_demo():
            """API de démonstration"""
            return jsonify({
                "message": "🎉 AIMER PRO fonctionne dans GitHub Codespaces !",
                "environment": "Codespaces" if os.getenv('CODESPACES') == 'true' else "Local",
                "packages_installed": [
                    "Flask ✅",
                    "OpenCV ✅", 
                    "NumPy ✅",
                    "PyTorch ✅",
                    "Detectron2 ❌ (pas nécessaire pour la démo)"
                ]
            })

    def run(self):
        """Démarre le serveur web"""
        print(f"🌐 Serveur AIMER PRO (Mode Démo) démarré")
        print(f"📍 Adresse: http://{self.host}:{self.port}")
        print(f"🎯 Mode: {'Codespaces' if os.getenv('CODESPACES') == 'true' else 'Local'}")
        
        # Démarrer le serveur
        self.app.run(
            host=self.host,
            port=self.port,
            debug=True,
            use_reloader=False  # Éviter les problèmes dans Codespaces
        )
