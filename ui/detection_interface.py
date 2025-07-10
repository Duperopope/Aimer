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
        self.detect_btn.clicked.connect(self.run_detection)
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

    def start_webcam(self):
        """Démarre la capture webcam"""
        self.logger.info("Appel de la fonctionnalité webcam (non implémentée)")
        QMessageBox.information(
            self, "Webcam", "Fonctionnalité webcam en développement"
        )

    def capture_screen(self):
        """Capture l'écran"""
        try:
            import mss

            with mss.mss() as sct:
                # Capturer l'écran principal
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)

                # Convertir en numpy array
                img = np.array(screenshot)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

                # Sauvegarder temporairement
                temp_path = "temp_screenshot.png"
                cv2.imwrite(temp_path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

                self.image_path_edit.setText(temp_path)
                self.display_image(temp_path)

                self.logger.info("Capture d'écran effectuée")

        except Exception as e:
            self.logger.error(f"Erreur capture écran: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur capture écran:\n{e}")

    def run_detection(self):
        """Lance la détection sur l'image actuelle"""
        if self.current_image is None:
            QMessageBox.warning(self, "Erreur", "Aucune image chargée")
            return

        if not self.detector:
            QMessageBox.critical(self, "Erreur", "Détecteur non initialisé")
            return

        try:
            # Configuration
            task = self.task_combo.currentText()
            confidence = self.confidence_slider.value() / 100.0
            device = self.device_combo.currentText()

            # Reconfigurer le détecteur si nécessaire
            if (
                self.detector.task_type != task
                or self.detector.confidence_threshold != confidence
            ):

                self.detector = UniversalDetector(
                    task_type=task, confidence_threshold=confidence
                )

            # Lancer la détection
            self.detect_btn.setText("🔄 Détection en cours...")
            self.detect_btn.setEnabled(False)

            import time

            start_time = time.time()

            result = self.detector.detect(self.current_image)

            processing_time = time.time() - start_time

            # Traiter les résultats
            self.detection_results = result
            self.display_results(result, processing_time)

            # Dessiner les annotations
            self.draw_annotations(result)

        except Exception as e:
            self.logger.error(f"Erreur détection: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur détection:\n{e}")

        finally:
            self.detect_btn.setText("🎯 DÉTECTER")
            self.detect_btn.setEnabled(True)

    def display_results(self, result, processing_time):
        """Affiche les résultats de détection"""
        try:
            if hasattr(result, "instances") and result.instances:
                detections = result.to_dict()

                results_text = f"=== RÉSULTATS DE DÉTECTION ===\n\n"
                results_text += f"Objets détectés: {detections['count']}\n"
                results_text += f"Temps de traitement: {processing_time:.2f}s\n\n"

                results_text += "DÉTECTIONS:\n"
                for i, detection in enumerate(detections["detections"], 1):
                    results_text += f"{i}. {detection['class_name']}: {detection['confidence']:.1%}\n"
                    bbox = detection["bbox"]
                    results_text += f"   Position: ({bbox['x1']:.0f}, {bbox['y1']:.0f}) - ({bbox['x2']:.0f}, {bbox['y2']:.0f})\n"

                self.results_text.setText(results_text)

                # Mettre à jour les infos
                self.info_objects.setText(str(detections["count"]))
                self.info_processing_time.setText(f"{processing_time:.2f}s")

            else:
                self.results_text.setText("Aucun objet détecté")
                self.info_objects.setText("0")
                self.info_processing_time.setText(f"{processing_time:.2f}s")

        except Exception as e:
            self.logger.error(f"Erreur affichage résultats: {e}")
            self.results_text.setText(f"Erreur affichage résultats: {e}")

    def draw_annotations(self, result):
        """Dessine les annotations sur l'image"""
        try:
            if not hasattr(result, "instances") or not result.instances:
                return

            # Copier l'image originale
            annotated_image = self.current_image.copy()

            detections = result.to_dict()

            # Couleurs pour les classes
            colors = [
                (255, 0, 0),
                (0, 255, 0),
                (0, 0, 255),
                (255, 255, 0),
                (255, 0, 255),
                (0, 255, 255),
                (128, 0, 0),
                (0, 128, 0),
                (0, 0, 128),
                (128, 128, 0),
                (128, 0, 128),
                (0, 128, 128),
            ]

            for i, detection in enumerate(detections["detections"]):
                bbox = detection["bbox"]
                class_name = detection["class_name"]
                confidence = detection["confidence"]

                # Couleur pour cette détection
                color = colors[i % len(colors)]

                # Dessiner le rectangle
                cv2.rectangle(
                    annotated_image,
                    (int(bbox["x1"]), int(bbox["y1"])),
                    (int(bbox["x2"]), int(bbox["y2"])),
                    color,
                    2,
                )

                # Texte de label
                label = f"{class_name}: {confidence:.1%}"

                # Fond pour le texte
                (text_width, text_height), _ = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                )

                cv2.rectangle(
                    annotated_image,
                    (int(bbox["x1"]), int(bbox["y1"]) - text_height - 10),
                    (int(bbox["x1"]) + text_width, int(bbox["y1"])),
                    color,
                    -1,
                )

                # Texte
                cv2.putText(
                    annotated_image,
                    label,
                    (int(bbox["x1"]), int(bbox["y1"]) - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )

            # Afficher l'image annotée
            height, width, channel = annotated_image.shape
            bytes_per_line = 3 * width
            rgb_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)

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

            # Sauvegarder l'image annotée pour export
            self.annotated_image = annotated_image

        except Exception as e:
            self.logger.error(f"Erreur annotation: {e}")

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
        if not hasattr(self, "annotated_image"):
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
