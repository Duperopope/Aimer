#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Serveur Web Intégré
© 2025 - Licence Apache 2.0

Serveur Flask avec interface web moderne et Detectron2
"""

import os
import sys
import json
import threading
import time
import base64
import io
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
import cv2
import numpy as np

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.logger import Logger
from core.config import Config
from core.detector import Detector
from core.hardware_monitor import HardwareMonitor
from core.gamification import GamificationSystem
from core.dataset_manager import DatasetManager


class AimerWebServer:
    """Serveur web AIMER avec interface moderne"""

    def __init__(self, host="localhost", port=5000):
        self.logger = Logger("WebServer")
        self.host = host
        self.port = port

        # Initialiser Flask
        self.app = Flask(__name__, template_folder="templates", static_folder="static")
        self.app.config["SECRET_KEY"] = "aimer_pro_secret_key_2025"

        # Initialiser SocketIO
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # Initialiser les composants
        self.config = Config()
        self.detector = None
        self.hardware_monitor = HardwareMonitor()
        self.gamification = GamificationSystem()
        self.dataset_manager = DatasetManager()

        # Variables d'état
        self.detection_active = False
        self.current_user_id = None

        # Configurer les routes
        self.setup_routes()
        self.setup_socketio_events()

        # Démarrer le monitoring hardware
        self.hardware_monitor.start_monitoring()

        self.logger.info("Serveur web AIMER initialisé")

    def setup_routes(self):
        """Configure les routes Flask"""

        @self.app.route("/")
        def index():
            """Page principale"""
            return render_template("index.html")

        @self.app.route("/api/hardware")
        def get_hardware():
            """API hardware info"""
            try:
                data = self.hardware_monitor.get_latest_data()
                if data:
                    return jsonify(data)
                else:
                    # Données par défaut si pas encore de monitoring
                    return jsonify(self.hardware_monitor.get_complete_info())
            except Exception as e:
                self.logger.error(f"Erreur API hardware: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/performance")
        def get_performance():
            """API score de performance IA"""
            try:
                score = self.hardware_monitor.calculate_ai_performance_score()
                return jsonify(score)
            except Exception as e:
                self.logger.error(f"Erreur API performance: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/user/login", methods=["POST"])
        def user_login():
            """Connexion utilisateur"""
            try:
                data = request.json
                username = data.get("username", "Player1")

                user_id = self.gamification.get_or_create_user(username)
                self.current_user_id = user_id

                # Enregistrer la connexion
                if user_id:
                    self.gamification.record_activity(
                        user_id, "login", f"Connexion de {username}"
                    )

                profile = self.gamification.get_user_profile(user_id)
                return jsonify(
                    {"success": True, "user_id": user_id, "profile": profile}
                )

            except Exception as e:
                self.logger.error(f"Erreur connexion utilisateur: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/user/profile")
        def get_user_profile():
            """Profil utilisateur actuel"""
            try:
                if not self.current_user_id:
                    return jsonify({"error": "Aucun utilisateur connecté"}), 401

                profile = self.gamification.get_user_profile(self.current_user_id)
                return jsonify(profile)

            except Exception as e:
                self.logger.error(f"Erreur profil utilisateur: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/leaderboard")
        def get_leaderboard():
            """Classement des joueurs"""
            try:
                leaderboard = self.gamification.get_leaderboard(10)
                return jsonify(leaderboard)
            except Exception as e:
                self.logger.error(f"Erreur leaderboard: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/datasets")
        def get_datasets():
            """Liste des datasets"""
            try:
                datasets = self.dataset_manager.get_all_datasets()
                return jsonify(datasets)
            except Exception as e:
                self.logger.error(f"Erreur datasets: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/datasets/popular")
        def get_popular_datasets():
            """Datasets populaires"""
            try:
                datasets = self.dataset_manager.get_popular_datasets()
                return jsonify(datasets)
            except Exception as e:
                self.logger.error(f"Erreur datasets populaires: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/detection/start", methods=["POST"])
        def start_detection():
            """Démarre la détection"""
            try:
                if not self.detector:
                    self.detector = Detector()

                self.detection_active = True

                # Enregistrer l'activité
                if self.current_user_id:
                    self.gamification.record_activity(
                        self.current_user_id,
                        "detection",
                        "Démarrage détection",
                        detections_count=1,
                    )

                return jsonify({"success": True, "message": "Détection démarrée"})

            except Exception as e:
                self.logger.error(f"Erreur démarrage détection: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/detection/stop", methods=["POST"])
        def stop_detection():
            """Arrête la détection"""
            try:
                self.detection_active = False
                return jsonify({"success": True, "message": "Détection arrêtée"})
            except Exception as e:
                self.logger.error(f"Erreur arrêt détection: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/detection/process", methods=["POST"])
        def process_detection():
            """Traite une image pour détection"""
            try:
                if not self.detector:
                    return jsonify({"error": "Détecteur non initialisé"}), 400

                # Récupérer l'image depuis la requête
                data = request.json
                image_data = data.get("image")

                if not image_data:
                    return jsonify({"error": "Aucune image fournie"}), 400

                # Décoder l'image base64
                image_bytes = base64.b64decode(image_data.split(",")[1])
                image = cv2.imdecode(
                    np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR
                )

                # Effectuer la détection
                start_time = time.time()
                results = self.detector.detect_objects(image)
                processing_time = (time.time() - start_time) * 1000

                # Enregistrer l'activité
                if self.current_user_id and results:
                    self.gamification.record_activity(
                        self.current_user_id,
                        "detection",
                        f"{len(results)} objets détectés",
                        detections_count=len(results),
                    )

                return jsonify(
                    {
                        "success": True,
                        "results": results,
                        "processing_time": processing_time,
                        "count": len(results),
                    }
                )

            except Exception as e:
                self.logger.error(f"Erreur traitement détection: {e}")
                return jsonify({"error": str(e)}), 500

    def setup_socketio_events(self):
        """Configure les événements SocketIO"""

        @self.socketio.on("connect")
        def handle_connect():
            """Connexion client"""
            self.logger.info("Client connecté via WebSocket")
            emit("status", {"message": "Connecté au serveur AIMER PRO"})

        @self.socketio.on("disconnect")
        def handle_disconnect():
            """Déconnexion client"""
            self.logger.info("Client déconnecté")

        @self.socketio.on("request_hardware_update")
        def handle_hardware_update():
            """Demande de mise à jour hardware"""
            try:
                data = self.hardware_monitor.get_latest_data()
                if data:
                    emit("hardware_update", data)
            except Exception as e:
                self.logger.error(f"Erreur mise à jour hardware: {e}")

        @self.socketio.on("start_detection_stream")
        def handle_start_detection_stream():
            """Démarre le stream de détection"""
            try:
                self.detection_active = True
                emit("detection_stream_started", {"status": "success"})

                # Démarrer le thread de détection en continu
                def detection_loop():
                    while self.detection_active:
                        try:
                            # Simuler des détections (remplacer par vraie capture)
                            fake_results = [
                                {
                                    "class": "person",
                                    "confidence": 0.95,
                                    "bbox": [100, 100, 200, 300],
                                    "mask": None,
                                },
                                {
                                    "class": "car",
                                    "confidence": 0.88,
                                    "bbox": [300, 150, 450, 250],
                                    "mask": None,
                                },
                            ]

                            self.socketio.emit(
                                "detection_results",
                                {
                                    "results": fake_results,
                                    "timestamp": datetime.now().isoformat(),
                                    "fps": 30,
                                },
                            )

                            time.sleep(0.1)  # 10 FPS

                        except Exception as e:
                            self.logger.error(f"Erreur loop détection: {e}")
                            break

                detection_thread = threading.Thread(target=detection_loop, daemon=True)
                detection_thread.start()

            except Exception as e:
                self.logger.error(f"Erreur démarrage stream: {e}")
                emit("error", {"message": str(e)})

        @self.socketio.on("stop_detection_stream")
        def handle_stop_detection_stream():
            """Arrête le stream de détection"""
            self.detection_active = False
            emit("detection_stream_stopped", {"status": "success"})

    def run(self, debug=False):
        """Démarre le serveur"""
        try:
            self.logger.info(
                f"Démarrage serveur web sur http://{self.host}:{self.port}"
            )
            self.socketio.run(
                self.app,
                host=self.host,
                port=self.port,
                debug=debug,
                allow_unsafe_werkzeug=True,
            )
        except Exception as e:
            self.logger.error(f"Erreur démarrage serveur: {e}")
            raise

    def stop(self):
        """Arrête le serveur"""
        try:
            self.detection_active = False
            self.hardware_monitor.stop_monitoring()
            self.logger.info("Serveur web arrêté")
        except Exception as e:
            self.logger.error(f"Erreur arrêt serveur: {e}")


if __name__ == "__main__":
    server = AimerWebServer()
    try:
        server.run(debug=True)
    except KeyboardInterrupt:
        server.stop()
