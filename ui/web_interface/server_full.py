#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Serveur Web Complet (Webcam + YouTube)
© 2025 - Licence Apache 2.0

Version complète avec webcam temps réel et support YouTube
"""

import os
import sys
import base64
import io
import cv2
import numpy as np
import tempfile
import threading
import time
from pathlib import Path
from flask import Flask, render_template, jsonify, request, Response

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent.parent))

class AimerWebServerFull:
    """Serveur web AIMER complet avec webcam et YouTube"""

    def __init__(self, host="localhost", port=5000):
        self.host = host
        self.port = port

        # Initialiser Flask
        self.app = Flask(__name__, 
                        template_folder="templates", 
                        static_folder="static")
        self.app.config["SECRET_KEY"] = "aimer_pro_full_key_2025"

        # Variables pour la webcam
        self.webcam_active = False
        self.webcam_thread = None
        self.frame_queue = []
        self.max_queue_size = 30

        # Configuration des routes
        self._setup_routes()

    def _setup_routes(self):
        """Configuration des routes de l'application"""
        
        @self.app.route("/")
        def index():
            """Page d'accueil avec interface complète"""
            return render_template("full_interface.html")

        @self.app.route("/demo")
        def demo():
            """Page de démonstration simple"""
            return render_template("demo.html")

        @self.app.route("/simple")
        def simple():
            """Redirection vers la démo simple"""
            return render_template("demo.html")

        @self.app.route("/full")
        def full():
            """Interface complète (alias)"""
            return render_template("full_interface.html")

        @self.app.route("/api/status")
        def api_status():
            """API de statut"""
            return jsonify({
                "status": "running",
                "version": "0.2.0",
                "mode": "full",
                "features": {
                    "web_interface": True,
                    "webcam_realtime": True,
                    "youtube_support": True,
                    "detectron2": False,
                    "opencv_detection": True,
                    "codespaces": os.getenv('CODESPACES') == 'true'
                },
                "server_info": {
                    "host": self.host,
                    "port": self.port,
                    "webcam_active": self.webcam_active
                }
            })

        @self.app.route("/api/features")
        def api_features():
            """API des fonctionnalités disponibles"""
            return jsonify({
                "detection_modes": [
                    {
                        "name": "image_upload",
                        "description": "Upload et analyse d'images",
                        "supported_formats": ["jpg", "jpeg", "png", "bmp", "webp"]
                    },
                    {
                        "name": "webcam_realtime", 
                        "description": "Détection webcam temps réel",
                        "fps_target": 5,
                        "supported": True
                    },
                    {
                        "name": "youtube_video",
                        "description": "Analyse de vidéos YouTube",
                        "status": "development",
                        "supported": False
                    }
                ],
                "detection_algorithms": [
                    {
                        "name": "opencv_contours",
                        "description": "Détection de contours et formes OpenCV",
                        "speed": "fast",
                        "accuracy": "basic"
                    }
                ]
            })

        @self.app.route("/api/detect", methods=["POST"])
        def api_detect():
            """API de détection d'images"""
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

                # Détection avec OpenCV
                results = self._enhanced_detection(image)
                
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
                        "processing_method": "Enhanced OpenCV Detection",
                        "processing_time_ms": results.get('processing_time', 0)
                    },
                    "metadata": {
                        "timestamp": time.time(),
                        "server_version": "0.2.0"
                    }
                })
                
            except Exception as e:
                return jsonify({"error": f"Erreur traitement: {str(e)}"}), 500

        @self.app.route("/api/webcam/start", methods=["POST"])
        def api_webcam_start():
            """Démarrer la capture webcam"""
            try:
                if not self.webcam_active:
                    self.webcam_active = True
                    return jsonify({
                        "success": True,
                        "message": "Webcam démarrée",
                        "status": "active"
                    })
                else:
                    return jsonify({
                        "success": False,
                        "message": "Webcam déjà active"
                    })
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/webcam/stop", methods=["POST"])
        def api_webcam_stop():
            """Arrêter la capture webcam"""
            try:
                self.webcam_active = False
                return jsonify({
                    "success": True,
                    "message": "Webcam arrêtée",
                    "status": "inactive"
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/youtube/info", methods=["POST"])
        def api_youtube_info():
            """Récupérer les informations d'une vidéo YouTube"""
            try:
                data = request.get_json()
                url = data.get('url', '')
                
                if not url:
                    return jsonify({"error": "URL manquante"}), 400
                
                # Vérifier si yt-dlp est disponible
                try:
                    import yt_dlp
                    
                    # Configuration yt-dlp
                    ydl_opts = {
                        'quiet': True,
                        'no_warnings': True,
                        'format': 'best[height<=720]',  # Limiter à 720p pour les performances
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        # Extraire les informations
                        info = ydl.extract_info(url, download=False)
                        
                        return jsonify({
                            "success": True,
                            "info": {
                                "title": info.get('title', 'Titre inconnu'),
                                "duration": self._format_duration(info.get('duration', 0)),
                                "resolution": f"{info.get('width', 'N/A')}x{info.get('height', 'N/A')}",
                                "fps": info.get('fps', 'N/A'),
                                "uploader": info.get('uploader', 'Inconnu'),
                                "view_count": info.get('view_count', 0),
                                "thumbnail": info.get('thumbnail'),
                                "formats_available": [f.get('ext', 'unknown') for f in info.get('formats', [])[:5]],
                                "url": info.get('url'),
                                "status": "ready"
                            },
                            "message": "Informations YouTube récupérées avec succès"
                        })
                        
                except ImportError:
                    return jsonify({
                        "success": False,
                        "error": "yt-dlp non installé",
                        "message": "Installez yt-dlp pour activer le support YouTube"
                    }), 400
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"Erreur YouTube: {str(e)}",
                    "message": "Impossible de récupérer les informations de la vidéo"
                }), 500

        @self.app.route("/api/youtube/download", methods=["POST"])
        def api_youtube_download():
            """Télécharger une vidéo YouTube pour analyse"""
            try:
                data = request.get_json()
                url = data.get('url', '')
                
                if not url:
                    return jsonify({"error": "URL manquante"}), 400
                
                import yt_dlp
                import tempfile
                
                # Créer un dossier temporaire
                temp_dir = tempfile.mkdtemp()
                
                # Configuration pour télécharger
                ydl_opts = {
                    'format': 'best[height<=480]',  # Qualité réduite pour les performances
                    'outtmpl': f'{temp_dir}/video.%(ext)s',
                    'quiet': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Télécharger la vidéo
                    info = ydl.extract_info(url, download=True)
                    
                    # Trouver le fichier téléchargé
                    video_files = [f for f in os.listdir(temp_dir) if f.startswith('video.')]
                    
                    if video_files:
                        video_path = os.path.join(temp_dir, video_files[0])
                        
                        return jsonify({
                            "success": True,
                            "video_path": video_path,
                            "temp_dir": temp_dir,
                            "info": {
                                "title": info.get('title'),
                                "duration": self._format_duration(info.get('duration', 0)),
                                "file_size": os.path.getsize(video_path)
                            },
                            "message": "Vidéo téléchargée avec succès"
                        })
                    else:
                        return jsonify({"error": "Aucun fichier vidéo trouvé"}), 500
                
            except Exception as e:
                return jsonify({"error": f"Erreur téléchargement: {str(e)}"}), 500

        @self.app.route("/api/stats")
        def api_stats():
            """Statistiques du serveur"""
            return jsonify({
                "server_stats": {
                    "uptime_seconds": time.time(),
                    "webcam_active": self.webcam_active,
                    "queue_size": len(self.frame_queue),
                    "max_queue_size": self.max_queue_size
                },
                "performance": {
                    "avg_detection_time_ms": 50,  # Estimation
                    "supported_image_formats": ["jpg", "jpeg", "png", "bmp", "webp"],
                    "max_image_size_mb": 10
                }
            })

    def _enhanced_detection(self, image):
        """Détection améliorée avec OpenCV"""
        start_time = time.time()
        
        # Copie pour le traitement
        processed = image.copy()
        
        # Conversion en niveaux de gris
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Détection de contours améliorée
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        # Morphologie pour nettoyer
        kernel = np.ones((3,3), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        
        # Analyser les contours trouvés
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            
            # Filtrer les petits objets (seuil adaptatif basé sur la taille de l'image)
            min_area = max(500, (image.shape[0] * image.shape[1]) * 0.0001)
            
            if area > min_area:
                # Calculer la boîte englobante
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculer quelques propriétés
                perimeter = cv2.arcLength(contour, True)
                circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
                
                # Déterminer la forme approximative
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Classification améliorée
                shape_name, confidence = self._classify_shape(approx, circularity, area)
                
                # Couleur basée sur le type
                color = self._get_shape_color(shape_name)
                
                # Dessiner la détection
                cv2.rectangle(processed, (x, y), (x+w, y+h), color, 2)
                cv2.putText(processed, f"{shape_name} #{i+1}", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # Dessiner le contour
                cv2.drawContours(processed, [contour], -1, color, 1)
                
                detections.append({
                    "id": i + 1,
                    "shape": shape_name,
                    "bbox": [int(x), int(y), int(w), int(h)],
                    "area": int(area),
                    "circularity": round(circularity, 3),
                    "confidence": round(confidence, 3),
                    "vertices": len(approx),
                    "color": color
                })
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "detections": detections,
            "processed_image": processed,
            "processing_time": round(processing_time, 2)
        }

    def _classify_shape(self, approx, circularity, area):
        """Classification améliorée des formes"""
        vertices = len(approx)
        
        if vertices == 3:
            return "Triangle", 0.9
        elif vertices == 4:
            # Distinguer carré/rectangle
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = float(w) / h
            if 0.8 <= aspect_ratio <= 1.2:
                return "Carré", 0.95
            else:
                return "Rectangle", 0.9
        elif vertices > 8 and circularity > 0.7:
            if circularity > 0.9:
                return "Cercle", 0.95
            else:
                return "Ellipse", 0.85
        elif vertices == 5:
            return "Pentagone", 0.8
        elif vertices == 6:
            return "Hexagone", 0.8
        elif vertices > 6:
            return "Polygone", 0.7
        else:
            return "Forme complexe", 0.6

    def _get_shape_color(self, shape_name):
        """Couleurs spécifiques par type de forme"""
        colors = {
            "Triangle": (255, 0, 0),      # Rouge
            "Carré": (0, 255, 0),         # Vert
            "Rectangle": (0, 200, 100),   # Vert clair
            "Cercle": (255, 255, 0),      # Jaune
            "Ellipse": (255, 200, 0),     # Orange
            "Pentagone": (255, 0, 255),   # Magenta
            "Hexagone": (128, 0, 255),    # Violet
            "Polygone": (0, 255, 255),    # Cyan
            "Forme complexe": (128, 128, 128)  # Gris
        }
        return colors.get(shape_name, (0, 255, 0))

    def _format_duration(self, seconds):
        """Formater une durée en secondes vers HH:MM:SS"""
        if not seconds:
            return "00:00:00"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def run(self):
        """Démarre le serveur web"""
        print(f"🌐 Serveur AIMER PRO (Mode Complet) démarré")
        print(f"📍 Adresse: http://{self.host}:{self.port}")
        print(f"🎯 Mode: {'Codespaces' if os.getenv('CODESPACES') == 'true' else 'Local'}")
        print(f"✨ Features: Webcam + YouTube + API REST")
        
        # Démarrer le serveur
        self.app.run(
            host=self.host,
            port=self.port,
            debug=True,
            use_reloader=False,
            threaded=True  # Important pour la webcam
        )
    
    def get_app(self):
        """Retourne l'instance Flask pour le déploiement"""
        return self.app

# Point d'entrée pour test direct
if __name__ == "__main__":
    server = AimerWebServerFull(host="0.0.0.0", port=5000)
    server.run()
