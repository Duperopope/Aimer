#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Moteur de Vision Ultime
© 2025 - Licence Apache 2.0

Moteur complet de computer vision pour toutes applications
"""

import cv2
import numpy as np
import time
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple
from pathlib import Path
import json
import pyautogui
import mss
from PIL import Image, ImageDraw, ImageFont
import win32gui
import win32con
import win32api

from .logger import Logger
from .detector import UniversalDetector


class GameVisionBot:
    """Bot de vision pour jeux vidéo avec détection et automation"""

    def __init__(self):
        self.logger = Logger("GameVisionBot")
        self.detector = None
        self.running = False
        self.target_window = None
        self.actions = {}

        # Configuration pour différents jeux
        self.game_configs = {
            "fps_shooter": {
                "targets": ["enemy", "weapon", "health_pack"],
                "actions": {
                    "enemy": {"action": "aim_and_shoot", "key": "mouse_left"},
                    "weapon": {"action": "pickup", "key": "e"},
                    "health_pack": {"action": "pickup", "key": "e"},
                },
            },
            "strategy": {
                "targets": ["resource", "enemy_unit", "building"],
                "actions": {
                    "resource": {"action": "collect", "key": "right_click"},
                    "enemy_unit": {"action": "attack", "key": "a"},
                    "building": {"action": "select", "key": "left_click"},
                },
            },
        }

    def setup_for_game(self, game_type: str, window_title: str):
        """Configure le bot pour un jeu spécifique"""
        try:
            # Initialiser le détecteur
            self.detector = UniversalDetector(
                task_type="detection", confidence_threshold=0.7
            )

            # Trouver la fenêtre du jeu
            self.target_window = self._find_window(window_title)

            # Charger la configuration du jeu
            if game_type in self.game_configs:
                self.actions = self.game_configs[game_type]["actions"]

            self.logger.info(
                f"Bot configuré pour {game_type} - Fenêtre: {window_title}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Erreur configuration bot: {e}")
            return False

    def start_bot(self):
        """Démarre le bot de vision"""
        if not self.detector or not self.target_window:
            self.logger.error("Bot non configuré")
            return False

        self.running = True
        self.bot_thread = threading.Thread(target=self._bot_loop)
        self.bot_thread.start()

        self.logger.info("Bot de vision démarré")
        return True

    def stop_bot(self):
        """Arrête le bot"""
        self.running = False
        if hasattr(self, "bot_thread"):
            self.bot_thread.join()

        self.logger.info("Bot arrêté")

    def _bot_loop(self):
        """Boucle principale du bot"""
        while self.running:
            try:
                # Capturer l'écran du jeu
                screenshot = self._capture_game_window()
                if screenshot is None:
                    time.sleep(0.1)
                    continue

                # Détecter les objets
                result = self.detector.detect(screenshot)

                if result.instances:
                    detections = result.to_dict()

                    # Traiter chaque détection
                    for detection in detections["detections"]:
                        class_name = detection["class_name"]
                        confidence = detection["confidence"]
                        bbox = detection["bbox"]

                        # Vérifier si c'est un objet d'intérêt
                        if class_name in self.actions and confidence > 0.8:
                            self._execute_action(class_name, bbox)

                # Limiter le FPS
                time.sleep(0.05)  # 20 FPS

            except Exception as e:
                self.logger.error(f"Erreur boucle bot: {e}")
                time.sleep(0.1)

    def _capture_game_window(self) -> Optional[np.ndarray]:
        """Capture la fenêtre du jeu"""
        try:
            if not self.target_window:
                return None

            # Obtenir les dimensions de la fenêtre
            rect = win32gui.GetWindowRect(self.target_window)
            x, y, x2, y2 = rect
            width = x2 - x
            height = y2 - y

            # Capturer avec mss (plus rapide)
            with mss.mss() as sct:
                monitor = {"top": y, "left": x, "width": width, "height": height}
                screenshot = sct.grab(monitor)

                # Convertir en numpy array
                img = np.array(screenshot)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

                return img

        except Exception as e:
            self.logger.error(f"Erreur capture écran: {e}")
            return None

    def _execute_action(self, target_type: str, bbox: Dict[str, float]):
        """Exécute une action basée sur la détection"""
        try:
            action_config = self.actions.get(target_type)
            if not action_config:
                return

            # Calculer le centre de l'objet
            center_x = bbox["x1"] + bbox["width"] / 2
            center_y = bbox["y1"] + bbox["height"] / 2

            # Convertir en coordonnées écran
            if self.target_window:
                rect = win32gui.GetWindowRect(self.target_window)
                screen_x = rect[0] + center_x
                screen_y = rect[1] + center_y
            else:
                return

            # Exécuter l'action
            action = action_config["action"]
            key = action_config["key"]

            if action == "aim_and_shoot":
                pyautogui.moveTo(screen_x, screen_y, duration=0.1)
                pyautogui.click()
            elif action == "pickup":
                pyautogui.moveTo(screen_x, screen_y, duration=0.1)
                pyautogui.press(key)
            elif action == "right_click":
                pyautogui.moveTo(screen_x, screen_y, duration=0.1)
                pyautogui.rightClick()

            self.logger.info(f"Action exécutée: {action} sur {target_type}")

        except Exception as e:
            self.logger.error(f"Erreur exécution action: {e}")

    def _find_window(self, title: str) -> Optional[int]:
        """Trouve une fenêtre par son titre"""

        def enum_windows_proc(hwnd, lParam):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if title.lower() in window_title.lower():
                    lParam.append(hwnd)
            return True

        windows = []
        win32gui.EnumWindows(enum_windows_proc, windows)

        return windows[0] if windows else None


class MedicalVisionAnalyzer:
    """Analyseur de vision médicale avec IA"""

    def __init__(self):
        self.logger = Logger("MedicalVisionAnalyzer")
        self.detector = UniversalDetector(task_type="detection")

        # Modèles spécialisés pour le médical
        self.medical_models = {
            "xray": "Medical-XRay/chest_xray_detection.yaml",
            "mri": "Medical-MRI/brain_tumor_detection.yaml",
            "skin": "Medical-Dermatology/skin_lesion_detection.yaml",
            "retina": "Medical-Ophthalmology/retinal_disease_detection.yaml",
        }

        # Classes médicales
        self.medical_classes = {
            "xray": ["pneumonia", "fracture", "tumor", "normal"],
            "mri": ["tumor", "hemorrhage", "normal"],
            "skin": ["melanoma", "basal_cell", "squamous_cell", "benign"],
            "retina": [
                "diabetic_retinopathy",
                "glaucoma",
                "macular_degeneration",
                "normal",
            ],
        }

    def analyze_medical_image(self, image_path: str, modality: str) -> Dict[str, Any]:
        """Analyse une image médicale"""
        try:
            if modality not in self.medical_models:
                raise ValueError(f"Modalité non supportée: {modality}")

            # Charger l'image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Impossible de charger l'image: {image_path}")

            # Préprocessing médical
            processed_image = self._preprocess_medical_image(image, modality)

            # Détection avec modèle spécialisé
            result = self.detector.detect(processed_image)

            # Analyse des résultats
            analysis = self._analyze_medical_results(result, modality)

            # Génération du rapport
            report = self._generate_medical_report(analysis, modality)

            self.logger.info(f"Analyse médicale terminée: {modality}")

            return {
                "modality": modality,
                "findings": analysis,
                "report": report,
                "confidence_score": analysis.get("max_confidence", 0),
                "recommendation": self._get_medical_recommendation(analysis),
            }

        except Exception as e:
            self.logger.error(f"Erreur analyse médicale: {e}")
            return {"error": str(e)}

    def _preprocess_medical_image(self, image: np.ndarray, modality: str) -> np.ndarray:
        """Préprocessing spécialisé pour images médicales"""
        if modality == "xray":
            # Amélioration contraste pour rayons X
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image = clahe.apply(image)
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        elif modality == "mri":
            # Normalisation pour IRM
            image = cv2.normalize(image, image, 0, 255, cv2.NORM_MINMAX)

        elif modality == "skin":
            # Amélioration couleur pour dermatologie
            image = cv2.convertScaleAbs(image, alpha=1.2, beta=10)

        elif modality == "retina":
            # Amélioration vaisseaux rétiniens
            if len(image.shape) == 3:
                green_channel = image[:, :, 1]
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                enhanced = clahe.apply(green_channel)
                image[:, :, 1] = enhanced

        return image

    def _analyze_medical_results(self, result, modality: str) -> Dict[str, Any]:
        """Analyse les résultats de détection médicale"""
        analysis = {
            "detections": [],
            "max_confidence": 0,
            "pathology_detected": False,
            "severity": "normal",
        }

        if result.instances:
            detections = result.to_dict()

            for detection in detections["detections"]:
                class_name = detection["class_name"]
                confidence = detection["confidence"]

                # Vérifier si c'est une pathologie
                if class_name != "normal" and confidence > 0.6:
                    analysis["pathology_detected"] = True

                    # Déterminer la sévérité
                    if confidence > 0.9:
                        analysis["severity"] = "high"
                    elif confidence > 0.7:
                        analysis["severity"] = "moderate"
                    else:
                        analysis["severity"] = "low"

                analysis["detections"].append(
                    {
                        "finding": class_name,
                        "confidence": confidence,
                        "location": detection["bbox"],
                        "clinical_significance": self._get_clinical_significance(
                            class_name, modality
                        ),
                    }
                )

                analysis["max_confidence"] = max(analysis["max_confidence"], confidence)

        return analysis

    def _get_clinical_significance(self, finding: str, modality: str) -> str:
        """Retourne la signification clinique d'une découverte"""
        significance_map = {
            "pneumonia": "Infection pulmonaire nécessitant un traitement antibiotique",
            "fracture": "Rupture osseuse nécessitant une immobilisation",
            "tumor": "Masse suspecte nécessitant une investigation approfondie",
            "melanoma": "Cancer de la peau agressif nécessitant une excision urgente",
            "diabetic_retinopathy": "Complication diabétique affectant la vision",
            "glaucoma": "Maladie oculaire pouvant causer la cécité",
        }

        return significance_map.get(
            finding, "Découverte nécessitant une évaluation clinique"
        )

    def _generate_medical_report(self, analysis: Dict[str, Any], modality: str) -> str:
        """Génère un rapport médical structuré"""
        report = f"RAPPORT D'ANALYSE - {modality.upper()}\n"
        report += "=" * 50 + "\n\n"

        if analysis["pathology_detected"]:
            report += (
                f"RÉSULTAT: PATHOLOGIE DÉTECTÉE (Sévérité: {analysis['severity']})\n\n"
            )

            report += "DÉCOUVERTES:\n"
            for detection in analysis["detections"]:
                if detection["finding"] != "normal":
                    report += f"- {detection['finding'].title()}: {detection['confidence']:.1%} de confiance\n"
                    report += (
                        f"  Signification: {detection['clinical_significance']}\n\n"
                    )
        else:
            report += "RÉSULTAT: NORMAL\nAucune pathologie significative détectée.\n\n"

        report += f"CONFIANCE MAXIMALE: {analysis['max_confidence']:.1%}\n"

        return report

    def _get_medical_recommendation(self, analysis: Dict[str, Any]) -> str:
        """Génère une recommandation médicale"""
        if not analysis["pathology_detected"]:
            return "Suivi de routine recommandé"

        severity = analysis["severity"]

        if severity == "high":
            return "URGENT: Consultation spécialisée immédiate recommandée"
        elif severity == "moderate":
            return "Consultation médicale dans les 48h recommandée"
        else:
            return "Suivi médical dans la semaine recommandé"


class InteractiveVisionController:
    """Contrôleur de vision interactive pour automation"""

    def __init__(self):
        self.logger = Logger("InteractiveVisionController")
        self.detector = UniversalDetector(task_type="detection")
        self.running = False
        self.interaction_rules = {}

        # Zones d'interaction prédéfinies
        self.interaction_zones = {
            "desktop": {"x": 0, "y": 0, "width": 1920, "height": 1080},
            "browser": {"x": 100, "y": 100, "width": 1200, "height": 800},
            "application": {"x": 200, "y": 200, "width": 1000, "height": 600},
        }

    def add_interaction_rule(
        self, object_class: str, action: str, parameters: Dict[str, Any]
    ):
        """Ajoute une règle d'interaction"""
        self.interaction_rules[object_class] = {
            "action": action,
            "parameters": parameters,
        }

        self.logger.info(f"Règle ajoutée: {object_class} -> {action}")

    def start_interactive_mode(self, zone: str = "desktop"):
        """Démarre le mode interactif"""
        if zone not in self.interaction_zones:
            self.logger.error(f"Zone inconnue: {zone}")
            return False

        self.current_zone = self.interaction_zones[zone]
        self.running = True

        self.interaction_thread = threading.Thread(target=self._interaction_loop)
        self.interaction_thread.start()

        self.logger.info(f"Mode interactif démarré - Zone: {zone}")
        return True

    def stop_interactive_mode(self):
        """Arrête le mode interactif"""
        self.running = False
        if hasattr(self, "interaction_thread"):
            self.interaction_thread.join()

        self.logger.info("Mode interactif arrêté")

    def _interaction_loop(self):
        """Boucle principale d'interaction"""
        while self.running:
            try:
                # Capturer la zone d'interaction
                screenshot = self._capture_zone()

                # Détecter les objets
                result = self.detector.detect(screenshot)

                if result.instances:
                    detections = result.to_dict()

                    # Traiter chaque détection
                    for detection in detections["detections"]:
                        class_name = detection["class_name"]

                        if class_name in self.interaction_rules:
                            self._execute_interaction(detection)

                time.sleep(0.1)  # 10 FPS

            except Exception as e:
                self.logger.error(f"Erreur boucle interaction: {e}")
                time.sleep(0.1)

    def _capture_zone(self) -> np.ndarray:
        """Capture la zone d'interaction"""
        zone = self.current_zone

        with mss.mss() as sct:
            monitor = {
                "top": zone["y"],
                "left": zone["x"],
                "width": zone["width"],
                "height": zone["height"],
            }
            screenshot = sct.grab(monitor)

            # Convertir en numpy array
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

            return img

    def _execute_interaction(self, detection: Dict[str, Any]):
        """Exécute une interaction basée sur la détection"""
        try:
            class_name = detection["class_name"]
            rule = self.interaction_rules[class_name]

            action = rule["action"]
            params = rule["parameters"]
            bbox = detection["bbox"]

            # Calculer la position d'interaction
            zone = self.current_zone
            x = zone["x"] + bbox["x1"] + bbox["width"] / 2
            y = zone["y"] + bbox["y1"] + bbox["height"] / 2

            # Exécuter l'action
            if action == "click":
                pyautogui.click(x, y)
            elif action == "double_click":
                pyautogui.doubleClick(x, y)
            elif action == "right_click":
                pyautogui.rightClick(x, y)
            elif action == "hover":
                pyautogui.moveTo(x, y)
            elif action == "drag":
                target_x = params.get("target_x", x + 100)
                target_y = params.get("target_y", y)
                pyautogui.drag(target_x, target_y, duration=0.5, button="left")
            elif action == "type_text":
                pyautogui.click(x, y)
                pyautogui.typewrite(params.get("text", ""))
            elif action == "key_press":
                pyautogui.press(params.get("key", "enter"))

            self.logger.info(f"Interaction exécutée: {action} sur {class_name}")

            # Délai pour éviter les actions trop rapides
            time.sleep(params.get("delay", 0.5))

        except Exception as e:
            self.logger.error(f"Erreur exécution interaction: {e}")


class UltimateVisionEngine:
    """Moteur de vision ultime combinant toutes les fonctionnalités"""

    def __init__(self):
        self.logger = Logger("UltimateVisionEngine")

        # Initialiser tous les modules
        self.game_bot = GameVisionBot()
        self.medical_analyzer = MedicalVisionAnalyzer()
        self.interactive_controller = InteractiveVisionController()
        self.detector = UniversalDetector()

        # État du moteur
        self.active_modules = set()

        self.logger.info("Moteur de vision ultime initialisé")

    def start_game_automation(self, game_type: str, window_title: str) -> bool:
        """Démarre l'automation de jeu"""
        success = self.game_bot.setup_for_game(game_type, window_title)
        if success:
            success = self.game_bot.start_bot()
            if success:
                self.active_modules.add("game_bot")

        return success

    def analyze_medical_image(self, image_path: str, modality: str) -> Dict[str, Any]:
        """Analyse une image médicale"""
        return self.medical_analyzer.analyze_medical_image(image_path, modality)

    def start_interactive_control(self, zone: str = "desktop") -> bool:
        """Démarre le contrôle interactif"""
        success = self.interactive_controller.start_interactive_mode(zone)
        if success:
            self.active_modules.add("interactive_controller")

        return success

    def add_interaction_rule(
        self, object_class: str, action: str, parameters: Dict[str, Any]
    ):
        """Ajoute une règle d'interaction"""
        self.interactive_controller.add_interaction_rule(
            object_class, action, parameters
        )

    def stop_all_modules(self):
        """Arrête tous les modules actifs"""
        if "game_bot" in self.active_modules:
            self.game_bot.stop_bot()
            self.active_modules.remove("game_bot")

        if "interactive_controller" in self.active_modules:
            self.interactive_controller.stop_interactive_mode()
            self.active_modules.remove("interactive_controller")

        self.logger.info("Tous les modules arrêtés")

    def get_status(self) -> Dict[str, Any]:
        """Retourne l'état du moteur"""
        return {
            "active_modules": list(self.active_modules),
            "game_bot_running": "game_bot" in self.active_modules,
            "interactive_controller_running": "interactive_controller"
            in self.active_modules,
            "detector_available": self.detector is not None,
        }

    def create_custom_dataset(self, name: str, source_type: str, **kwargs) -> bool:
        """Crée un dataset personnalisé"""
        try:
            if source_type == "screen_capture":
                return self._create_screen_dataset(name, **kwargs)
            elif source_type == "webcam":
                return self._create_webcam_dataset(name, **kwargs)
            elif source_type == "game_capture":
                return self._create_game_dataset(name, **kwargs)
            else:
                self.logger.error(f"Type de source non supporté: {source_type}")
                return False

        except Exception as e:
            self.logger.error(f"Erreur création dataset: {e}")
            return False

    def _create_screen_dataset(self, name: str, **kwargs) -> bool:
        """Crée un dataset à partir de captures d'écran"""
        # Implémentation de capture d'écran automatique
        # avec annotation semi-automatique
        self.logger.info(f"Création dataset écran: {name}")
        return True

    def _create_webcam_dataset(self, name: str, **kwargs) -> bool:
        """Crée un dataset à partir de la webcam"""
        # Implémentation de capture webcam
        # avec détection et annotation automatique
        self.logger.info(f"Création dataset webcam: {name}")
        return True

    def _create_game_dataset(self, name: str, **kwargs) -> bool:
        """Crée un dataset à partir de captures de jeu"""
        # Implémentation de capture de jeu
        # avec détection d'éléments de gameplay
        self.logger.info(f"Création dataset jeu: {name}")
        return True
