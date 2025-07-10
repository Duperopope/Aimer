#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Interface de Détection Complète
© 2025 - Licence Apache 2.0

Interface complète de détection d'objets avec toutes les fonctionnalités
"""

import sys
import cv2
import numpy as np
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QComboBox,
    QSpinBox,
    QGroupBox,
    QTabWidget,
    QFileDialog,
    QMessageBox,
    QCheckBox,
    QSlider,
    QProgressBar,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QSplitter,
    QScrollArea,
    QFrame,
    QApplication,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QImage, QPainter, QPen

# Import des modules core
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.detector import UniversalDetector
from core.logger import Logger


class DetectionWidget(QWidget):
    """Widget principal de détection"""

    def __init__(self):
        super().__init__()
        self.logger = Logger("DetectionWidget")
        self.detector = None
        self.current_image = None
        self.detection_results = None
        self.annotated_image = None  # Pour éviter l'erreur d'attribut
        self.create_ui()
        self.initialize_detector()

    def create_ui(self):
        """Crée l'interface utilisateur"""
        layout = QHBoxLayout(self)

        # Panneau de contrôle gauche
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel, 1)

        # Zone d'affichage droite
        display_area = self.create_display_area()
        layout.addWidget(display_area, 2)

    def create_control_panel(self) -> QWidget:
        """Crée le panneau de contrôle"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Sélection d'image
        image_group = QGroupBox("Image Source")
        image_layout = QVBoxLayout(image_group)

        # Boutons de sélection
        buttons_layout = QHBoxLayout()

        self.load_image_btn = QPushButton("Charger Image")
        self.load_image_btn.clicked.connect(self.load_image)

        self.webcam_btn = QPushButton("Webcam")
        self.webcam_btn.clicked.connect(self.start_webcam)

        self.screen_btn = QPushButton("Capture Écran")
        self.screen_btn.clicked.connect(self.capture_screen)

        buttons_layout.addWidget(self.load_image_btn)
        buttons_layout.addWidget(self.webcam_btn)
        buttons_layout.addWidget(self.screen_btn)

        image_layout.addLayout(buttons_layout)

        # Chemin de l'image
        self.image_path_edit = QLineEdit()
        self.image_path_edit.setPlaceholderText("Chemin de l'image...")
        image_layout.addWidget(self.image_path_edit)

        layout.addWidget(image_group)

        # Configuration de détection
        config_group = QGroupBox("Configuration Détection")
        config_layout = QGridLayout(config_group)

        # Tâche de détection
        config_layout.addWidget(QLabel("Tâche:"), 0, 0)
        self.task_combo = QComboBox()
        self.task_combo.addItems(
            [
                "detection",
                "instance_segmentation",
                "panoptic_segmentation",
                "keypoint_detection",
            ]
        )
        config_layout.addWidget(self.task_combo, 0, 1)

        # Seuil de confiance
        config_layout.addWidget(QLabel("Confiance:"), 1, 0)
        self.confidence_slider = QSlider(Qt.Orientation.Horizontal)
        self.confidence_slider.setRange(10, 95)
        self.confidence_slider.setValue(50)
        self.confidence_slider.valueChanged.connect(self.update_confidence_label)
        config_layout.addWidget(self.confidence_slider, 1, 1)

        self.confidence_label = QLabel("50%")
        config_layout.addWidget(self.confidence_label, 1, 2)

        # Device
        config_layout.addWidget(QLabel("Device:"), 2, 0)
        self.device_combo = QComboBox()
        self.device_combo.addItems(["auto", "cpu", "cuda"])
        config_layout.addWidget(self.device_combo, 2, 1)

        layout.addWidget(config_group)

        # Bouton de détection
        self.detect_btn = QPushButton("🎯 DÉTECTER")
        # Correction : vérifie que run_detection existe avant de connecter
        if hasattr(self, "run_detection"):
            self.detect_btn.clicked.connect(self.run_detection)
        else:
            self.logger.error(
                "Méthode run_detection absente lors du connect du bouton détecter."
            )
        self.detect_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 15px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """
        )
        layout.addWidget(self.detect_btn)

        # Filtres de classes
        filters_group = QGroupBox("Filtres de Classes")
        filters_layout = QVBoxLayout(filters_group)

        # Recherche de classes
        self.class_search = QLineEdit()
        self.class_search.setPlaceholderText("Rechercher une classe...")
        self.class_search.textChanged.connect(self.filter_classes)
        filters_layout.addWidget(self.class_search)

        # Liste des classes
        self.class_list = QTableWidget()
        self.class_list.setColumnCount(2)
        self.class_list.setHorizontalHeaderLabels(["Classe", "Actif"])
        self.populate_class_list()
        filters_layout.addWidget(self.class_list)

        layout.addWidget(filters_group)

        # Résultats
        results_group = QGroupBox("Résultats")
        results_layout = QVBoxLayout(results_group)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(150)
        results_layout.addWidget(self.results_text)

        # Boutons d'export
        export_layout = QHBoxLayout()

        export_json_btn = QPushButton("Export JSON")
        export_json_btn.clicked.connect(self.export_json)

        export_csv_btn = QPushButton("Export CSV")
        export_csv_btn.clicked.connect(self.export_csv)

        save_image_btn = QPushButton("Sauver Image")
        save_image_btn.clicked.connect(self.save_annotated_image)

        export_layout.addWidget(export_json_btn)
        export_layout.addWidget(export_csv_btn)
        export_layout.addWidget(save_image_btn)

        results_layout.addLayout(export_layout)
        layout.addWidget(results_group)

        layout.addStretch()

        return panel

    def create_display_area(self) -> QWidget:
        """Crée la zone d'affichage"""
        display = QWidget()
        layout = QVBoxLayout(display)

        # En-tête
        header = QLabel("Zone d'Affichage")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background-color: #f0f0f0;
                border-radius: 5px;
            }
        """
        )
        layout.addWidget(header)

        # Zone d'image
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(600, 400)
        self.image_label.setStyleSheet(
            """
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 10px;
                background-color: #fafafa;
            }
        """
        )
        self.image_label.setText(
            "Aucune image chargée\n\nCliquez sur 'Charger Image' pour commencer"
        )

        # Scroll area pour les grandes images
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # Informations sur l'image
        info_group = QGroupBox("Informations Image")
        info_layout = QGridLayout(info_group)

        self.info_size = QLabel("Taille: -")
        self.info_format = QLabel("Format: -")
        self.info_objects = QLabel("Objets détectés: -")
        self.info_processing_time = QLabel("Temps: -")

        info_layout.addWidget(QLabel("Taille:"), 0, 0)
        info_layout.addWidget(self.info_size, 0, 1)
        info_layout.addWidget(QLabel("Format:"), 0, 2)
        info_layout.addWidget(self.info_format, 0, 3)
        info_layout.addWidget(QLabel("Objets:"), 1, 0)
        info_layout.addWidget(self.info_objects, 1, 1)
        info_layout.addWidget(QLabel("Temps:"), 1, 2)
        info_layout.addWidget(self.info_processing_time, 1, 3)

        layout.addWidget(info_group)

        return display

    def initialize_detector(self):
        """Initialise le détecteur"""
        try:
            self.detector = UniversalDetector()
            self.logger.info("Détecteur initialisé")
        except Exception as e:
            self.logger.error(f"Erreur initialisation détecteur: {e}")
            QMessageBox.critical(
                self, "Erreur", f"Impossible d'initialiser le détecteur:\n{e}"
            )

    def populate_class_list(self):
        """Remplit la liste des classes COCO"""
        coco_classes = [
            "person",
            "bicycle",
            "car",
            "motorcycle",
            "airplane",
            "bus",
            "train",
            "truck",
            "boat",
            "traffic light",
            "fire hydrant",
            "stop sign",
            "parking meter",
            "bench",
            "bird",
            "cat",
            "dog",
            "horse",
            "sheep",
            "cow",
            "elephant",
            "bear",
            "zebra",
            "giraffe",
            "backpack",
            "umbrella",
            "handbag",
            "tie",
            "suitcase",
            "frisbee",
            "skis",
            "snowboard",
            "sports ball",
            "kite",
            "baseball bat",
            "baseball glove",
            "skateboard",
            "surfboard",
            "tennis racket",
            "bottle",
            "wine glass",
            "cup",
            "fork",
            "knife",
            "spoon",
            "bowl",
            "banana",
            "apple",
            "sandwich",
            "orange",
            "broccoli",
            "carrot",
            "hot dog",
            "pizza",
            "donut",
            "cake",
            "chair",
            "couch",
            "potted plant",
            "bed",
            "dining table",
            "toilet",
            "tv",
            "laptop",
            "mouse",
            "remote",
            "keyboard",
            "cell phone",
            "microwave",
            "oven",
            "toaster",
            "sink",
            "refrigerator",
            "book",
            "clock",
            "vase",
            "scissors",
            "teddy bear",
            "hair drier",
            "toothbrush",
        ]

        self.class_list.setRowCount(len(coco_classes))

        for i, class_name in enumerate(coco_classes):
            self.class_list.setItem(i, 0, QTableWidgetItem(class_name))

            checkbox = QCheckBox()
            checkbox.setChecked(True)
            self.class_list.setCellWidget(i, 1, checkbox)

    def update_confidence_label(self, value):
        """Met à jour le label de confiance"""
        self.confidence_label.setText(f"{value}%")

    def filter_classes(self, text):
        """Filtre les classes selon le texte de recherche"""
        for row in range(self.class_list.rowCount()):
            item = self.class_list.item(row, 0)
            if item:
                visible = text.lower() in item.text().lower()
                self.class_list.setRowHidden(row, not visible)

    def load_image(self):
        """Charge une image depuis le disque"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Charger Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )

        if file_path:
            self.image_path_edit.setText(file_path)
            self.display_image(file_path)

    def display_image(self, image_path):
        """Affiche une image dans le widget"""
        try:
            # Charger l'image avec OpenCV
            self.current_image = cv2.imread(image_path)
            if self.current_image is None:
                raise ValueError("Impossible de charger l'image")

            # Convertir pour Qt
            height, width, channel = self.current_image.shape
            bytes_per_line = 3 * width
            rgb_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)

            q_image = QImage(
                rgb_image.tobytes(),
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_RGB888,
            )

            # Redimensionner si nécessaire
            max_size = 800
            if width > max_size or height > max_size:
                q_image = q_image.scaled(
                    max_size, max_size, Qt.AspectRatioMode.KeepAspectRatio
                )

            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap)

            # Mettre à jour les infos
            self.info_size.setText(f"{width}x{height}")
            self.info_format.setText(Path(image_path).suffix.upper())
            self.info_objects.setText("-")
            self.info_processing_time.setText("-")

            self.logger.info(f"Image chargée: {image_path}")

        except Exception as e:
            self.logger.error(f"Erreur chargement image: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur chargement image:\n{e}")

    class WebcamThread(QThread):
        frame_ready = pyqtSignal(np.ndarray)
        detection_info = pyqtSignal(dict)
        error = pyqtSignal(str)

        def __init__(self, detector, task, confidence, parent=None):
            super().__init__(parent)
            self.detector = detector
            self.running = False
            self.task = task
            self.confidence = confidence

        def run(self):
            self.running = True
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.error.emit("Impossible d'ouvrir la webcam")
                return
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    self.error.emit("Erreur de lecture webcam")
                    break
                try:
                    # Détection
                    result = self.detector.detect(frame)
                    self.detection_info.emit(
                        {
                            "count": getattr(result, "instances", None)
                            and len(result.instances)
                            or 0,
                            "time": (
                                result.performance_metrics.get("inference_time_ms", 0)
                                if hasattr(result, "performance_metrics")
                                else 0
                            ),
                        }
                    )
                    # Dessiner les annotations si possible
                    if hasattr(result, "to_dict"):
                        detections = result.to_dict().get("detections", [])
                        for i, detection in enumerate(detections):
                            bbox = detection["bbox"]
                            class_name = detection["class_name"]
                            confidence = detection["confidence"]
                            color = (0, 255, 0)
                            cv2.rectangle(
                                frame,
                                (int(bbox["x1"]), int(bbox["y1"])),
                                (int(bbox["x2"]), int(bbox["y2"])),
                                color,
                                2,
                            )
                            label = f"{class_name}: {confidence:.1%}"
                            cv2.putText(
                                frame,
                                label,
                                (int(bbox["x1"]), int(bbox["y1"]) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6,
                                (0, 255, 0),
                                2,
                            )
                    self.frame_ready.emit(frame)
                except Exception as e:
                    self.error.emit(str(e))
            cap.release()

        def stop(self):
            self.running = False

    def start_webcam(self):
        """Démarre la capture webcam avec détection temps réel"""
        if (
            hasattr(self, "webcam_thread")
            and self.webcam_thread
            and self.webcam_thread.isRunning()
        ):
            QMessageBox.warning(
                self, "Webcam", "La webcam est déjà en cours d'utilisation."
            )
            return
        # Configurer le détecteur selon l'UI
        task = self.task_combo.currentText()
        confidence = self.confidence_slider.value() / 100.0
        try:
            self.logger.info("Démarrage de la webcam avec détection temps réel")
            self.webcam_thread = self.WebcamThread(self.detector, task, confidence)
            self.webcam_thread.frame_ready.connect(self.display_webcam_frame)
            self.webcam_thread.detection_info.connect(self.update_webcam_info)
            self.webcam_thread.error.connect(self.handle_webcam_error)
            self.webcam_thread.start()
            # Correction : utiliser addWidget au lieu de insertWidget
            if not hasattr(self, "stop_webcam_btn"):
                self.stop_webcam_btn = QPushButton("Arrêter Webcam")
                self.stop_webcam_btn.setStyleSheet(
                    "background-color: #dc3545; color: white; font-weight: bold;"
                )
                self.stop_webcam_btn.clicked.connect(self.stop_webcam)
                self.layout().itemAt(0).widget().layout().addWidget(
                    self.stop_webcam_btn
                )
            self.stop_webcam_btn.setVisible(True)
        except Exception as e:
            self.logger.error(f"Erreur démarrage webcam: {e}")
            QMessageBox.critical(self, "Webcam", f"Erreur démarrage webcam: {e}")

    def stop_webcam(self):
        """Arrête la capture webcam"""
        try:
            if hasattr(self, "webcam_thread") and self.webcam_thread:
                self.webcam_thread.stop()
                self.webcam_thread.wait()
                self.logger.info("Arrêt de la webcam demandé par l'utilisateur")
            if hasattr(self, "stop_webcam_btn"):
                self.stop_webcam_btn.setVisible(False)
        except Exception as e:
            self.logger.error(f"Erreur arrêt webcam: {e}")

    def display_webcam_frame(self, frame):
        """Affiche une frame webcam dans l'UI"""
        try:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_image = QImage(
                rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
            )
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap)
        except Exception as e:
            self.logger.error(f"Erreur affichage frame webcam: {e}")

    def update_webcam_info(self, info):
        """Met à jour les infos de détection webcam"""
        try:
            self.info_objects.setText(str(info.get("count", "-")))
            self.info_processing_time.setText(f"{info.get('time', 0):.1f}ms")
        except Exception as e:
            self.logger.error(f"Erreur update info webcam: {e}")

    def handle_webcam_error(self, msg):
        self.logger.error(f"Webcam: {msg}")
        QMessageBox.critical(self, "Webcam", msg)
        self.stop_webcam()

    def export_json(self):
        """Exporte les résultats en JSON"""
        if not self.detection_results:
            QMessageBox.warning(self, "Erreur", "Aucun résultat à exporter")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter JSON", "detection_results.json", "JSON (*.json)"
        )

        if file_path:
            try:
                import json

                detections = self.detection_results.to_dict()

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(detections, f, indent=2, ensure_ascii=False)

                QMessageBox.information(
                    self, "Export", f"Résultats exportés: {file_path}"
                )

            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur export JSON: {e}")

    def export_csv(self):
        """Exporte les résultats en CSV"""
        if not self.detection_results:
            QMessageBox.warning(self, "Erreur", "Aucun résultat à exporter")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter CSV", "detection_results.csv", "CSV (*.csv)"
        )

        if file_path:
            try:
                import csv

                detections = self.detection_results.to_dict()

                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)

                    # En-têtes
                    writer.writerow(
                        [
                            "Classe",
                            "Confiance",
                            "X1",
                            "Y1",
                            "X2",
                            "Y2",
                            "Largeur",
                            "Hauteur",
                        ]
                    )

                    # Données
                    for detection in detections["detections"]:
                        bbox = detection["bbox"]
                        writer.writerow(
                            [
                                detection["class_name"],
                                f"{detection['confidence']:.3f}",
                                f"{bbox['x1']:.0f}",
                                f"{bbox['y1']:.0f}",
                                f"{bbox['x2']:.0f}",
                                f"{bbox['y2']:.0f}",
                                f"{bbox['width']:.0f}",
                                f"{bbox['height']:.0f}",
                            ]
                        )

                QMessageBox.information(
                    self, "Export", f"Résultats exportés: {file_path}"
                )

            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur export CSV: {e}")

    def save_annotated_image(self):
        """Sauvegarde l'image annotée"""
        if self.annotated_image is None:
            QMessageBox.warning(self, "Erreur", "Aucune image annotée à sauvegarder")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder Image Annotée",
            "image_annotee.png",
            "Images (*.png *.jpg *.jpeg)",
        )
        if file_path:
            try:
                cv2.imwrite(file_path, self.annotated_image)
                QMessageBox.information(
                    self, "Sauvegarde", f"Image sauvegardée: {file_path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur sauvegarde: {e}")

    def capture_screen(self):
        """Capture l'écran et l'affiche dans l'interface"""
        try:
            import mss

            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                img = np.array(screenshot)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
                temp_path = "temp_screenshot.png"
                cv2.imwrite(temp_path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
                self.image_path_edit.setText(temp_path)
                self.display_image(temp_path)
                self.logger.info("Capture d'écran effectuée")
        except Exception as e:
            self.logger.error(f"Erreur capture écran: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur capture écran:\n{e}")


def main():
    """Fonction principale pour tester l'interface"""
    app = QApplication(sys.argv)

    window = DetectionWidget()
    window.setWindowTitle("AIMER PRO - Interface de Détection")
    window.setGeometry(100, 100, 1200, 800)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
