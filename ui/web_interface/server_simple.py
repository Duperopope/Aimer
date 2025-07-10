#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Serveur Web Simplifié (Version Codespaces)
© 2025 - Licence Apache 2.0

Version simplifiée sans Detectron2 pour démonstration
"""

import os
import sys
import base64
import io
import cv2
import numpy as np
from pathlib import Path
from flask import Flask, render_template, jsonify, request

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

        @self.app.route("/api/detect", methods=["POST"])
        def api_detect():
            """API de détection basique avec OpenCV"""
            try:
                # Récupérer l'image uploadée
                if 'image' not in request.files:
                    return jsonify({"error": "Aucune image fournie"}), 400
                
                file = request.files['image']
                if file.filename == '':
                    return jsonify({"error": "Nom de fichier vide"}), 400

                # Lire l'image
                image_bytes = file.read()
                nparr = np.frombuffer(image_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if image is None:
                    return jsonify({"error": "Impossible de décoder l'image"}), 400

                # Détection basique avec OpenCV (contours/formes)
                results = self._basic_detection(image)
                
                # Encoder l'image traitée en base64
                _, buffer = cv2.imencode('.jpg', results['processed_image'])
                img_base64 = base64.b64encode(buffer.tobytes()).decode('utf-8')
                
                return jsonify({
                    "success": True,
                    "detections": results['detections'],
                    "processed_image": f"data:image/jpeg;base64,{img_base64}",
                    "stats": {
                        "image_size": f"{image.shape[1]}x{image.shape[0]}",
                        "objects_found": len(results['detections']),
                        "processing_method": "OpenCV Basic Detection"
                    }
                })
                
            except Exception as e:
                return jsonify({"error": f"Erreur traitement: {str(e)}"}), 500

    def _basic_detection(self, image):
        """Détection basique avec OpenCV (contours et formes)"""
        # Copie pour le traitement
        processed = image.copy()
        
        # Conversion en niveaux de gris
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Détection de contours
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        
        # Analyser les contours trouvés
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            
            # Filtrer les petits objets
            if area > 500:  # Seuil minimum
                # Calculer la boîte englobante
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculer quelques propriétés
                perimeter = cv2.arcLength(contour, True)
                circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
                
                # Déterminer la forme approximative
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Classification basique par nombre de côtés
                if len(approx) == 3:
                    shape = "Triangle"
                elif len(approx) == 4:
                    shape = "Rectangle/Carré"
                elif len(approx) > 8 and circularity > 0.7:
                    shape = "Cercle/Ellipse"
                else:
                    shape = "Forme complexe"
                
                # Dessiner la détection
                cv2.rectangle(processed, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(processed, f"{shape} #{i+1}", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                detections.append({
                    "id": i + 1,
                    "shape": shape,
                    "bbox": [x, y, w, h],
                    "area": int(area),
                    "circularity": round(circularity, 3),
                    "confidence": min(0.95, area / 10000)  # Score basique
                })
        
        return {
            "detections": detections,
            "processed_image": processed
        }

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
    
    def get_app(self):
        """Retourne l'instance Flask pour le déploiement"""
        return self.app
