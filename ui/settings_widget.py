#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Widget de Paramètres
© 2025 - Licence Apache 2.0

Interface complète de configuration de l'application
"""

import sys
import json
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
    QScrollArea,
    QFrame,
    QDoubleSpinBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# Import des modules core
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.logger import Logger


class SettingsWidget(QWidget):
    """Widget de paramètres complet"""

    settings_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.logger = Logger("SettingsWidget")

        # Configuration simple avec dictionnaire
        self.settings = {
            "general": {
                "language": "Français",
                "theme": "Clair",
                "auto_start": False,
                "auto_update": True,
            },
            "detectron2": {
                "default_model": "COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml",
                "confidence_threshold": 0.5,
                "device": "auto",
            },
        }

        self.create_ui()
        self.load_settings()

    def create_ui(self):
        """Crée l'interface utilisateur"""
        layout = QVBoxLayout(self)

        # Titre
        title = QLabel("Paramètres AIMER PRO")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Onglets de paramètres
        self.tab_widget = QTabWidget()

        # Onglet Général
        general_tab = self.create_general_tab()
        self.tab_widget.addTab(general_tab, "🔧 Général")

        # Onglet Detectron2
        detectron_tab = self.create_detectron_tab()
        self.tab_widget.addTab(detectron_tab, "🎯 Detectron2")

        layout.addWidget(self.tab_widget)

        # Boutons d'action
        buttons_layout = self.create_action_buttons()
        layout.addLayout(buttons_layout)

    def create_general_tab(self) -> QWidget:
        """Crée l'onglet général"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Paramètres de base
        basic_group = QGroupBox("Paramètres de Base")
        basic_layout = QGridLayout(basic_group)

        # Langue
        basic_layout.addWidget(QLabel("Langue:"), 0, 0)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Français", "English", "Español", "Deutsch"])
        basic_layout.addWidget(self.language_combo, 0, 1)

        # Thème
        basic_layout.addWidget(QLabel("Thème:"), 1, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Clair", "Sombre", "Auto"])
        basic_layout.addWidget(self.theme_combo, 1, 1)

        # Démarrage automatique
        self.auto_start_check = QCheckBox("Démarrer avec Windows")
        basic_layout.addWidget(self.auto_start_check, 2, 0, 1, 2)

        # Vérification des mises à jour
        self.auto_update_check = QCheckBox("Vérifier les mises à jour automatiquement")
        basic_layout.addWidget(self.auto_update_check, 3, 0, 1, 2)

        layout.addWidget(basic_group)
        layout.addStretch()

        return widget

    def create_detectron_tab(self) -> QWidget:
        """Crée l'onglet Detectron2"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Configuration du modèle
        model_group = QGroupBox("Configuration du Modèle")
        model_layout = QGridLayout(model_group)

        # Modèle par défaut
        model_layout.addWidget(QLabel("Modèle par défaut:"), 0, 0)
        self.default_model_combo = QComboBox()
        self.default_model_combo.addItems(
            [
                "COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml",
                "COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml",
                "COCO-Detection/retinanet_R_50_FPN_3x.yaml",
                "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml",
                "COCO-PanopticSegmentation/panoptic_fpn_R_50_3x.yaml",
            ]
        )
        model_layout.addWidget(self.default_model_combo, 0, 1)

        # Seuil de confiance par défaut
        model_layout.addWidget(QLabel("Seuil de confiance:"), 1, 0)
        self.confidence_spin = QDoubleSpinBox()
        self.confidence_spin.setRange(0.1, 0.95)
        self.confidence_spin.setSingleStep(0.05)
        self.confidence_spin.setValue(0.5)
        model_layout.addWidget(self.confidence_spin, 1, 1)

        # Device par défaut
        model_layout.addWidget(QLabel("Device:"), 2, 0)
        self.device_combo = QComboBox()
        self.device_combo.addItems(["auto", "cpu", "cuda"])
        model_layout.addWidget(self.device_combo, 2, 1)

        layout.addWidget(model_group)
        layout.addStretch()

        return widget

    def create_action_buttons(self) -> QHBoxLayout:
        """Crée les boutons d'action"""
        layout = QHBoxLayout()

        # Bouton réinitialiser
        reset_btn = QPushButton("Réinitialiser")
        reset_btn.clicked.connect(self.reset_settings)
        reset_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #ffc107;
                color: black;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """
        )

        # Bouton appliquer
        apply_btn = QPushButton("Appliquer")
        apply_btn.clicked.connect(self.apply_settings)
        apply_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """
        )

        layout.addWidget(reset_btn)
        layout.addStretch()
        layout.addWidget(apply_btn)

        return layout

    def load_settings(self):
        """Charge les paramètres depuis la configuration"""
        try:
            # Charger depuis le fichier config.json s'il existe
            config_file = Path("config.json")
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)

            # Appliquer aux widgets
            self.language_combo.setCurrentText(self.settings["general"]["language"])
            self.theme_combo.setCurrentText(self.settings["general"]["theme"])
            self.auto_start_check.setChecked(self.settings["general"]["auto_start"])
            self.auto_update_check.setChecked(self.settings["general"]["auto_update"])

            self.default_model_combo.setCurrentText(
                self.settings["detectron2"]["default_model"]
            )
            self.confidence_spin.setValue(
                self.settings["detectron2"]["confidence_threshold"]
            )
            self.device_combo.setCurrentText(self.settings["detectron2"]["device"])

            self.logger.info("Paramètres chargés")

        except Exception as e:
            self.logger.error(f"Erreur chargement paramètres: {e}")
            QMessageBox.critical(
                self, "Erreur", f"Erreur lors du chargement des paramètres:\n{e}"
            )

    def apply_settings(self):
        """Applique les paramètres"""
        try:
            # Récupérer les valeurs des widgets
            self.settings["general"]["language"] = self.language_combo.currentText()
            self.settings["general"]["theme"] = self.theme_combo.currentText()
            self.settings["general"]["auto_start"] = self.auto_start_check.isChecked()
            self.settings["general"]["auto_update"] = self.auto_update_check.isChecked()

            self.settings["detectron2"][
                "default_model"
            ] = self.default_model_combo.currentText()
            self.settings["detectron2"][
                "confidence_threshold"
            ] = self.confidence_spin.value()
            self.settings["detectron2"]["device"] = self.device_combo.currentText()

            # Sauvegarder dans le fichier
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)

            # Émettre le signal de changement
            self.settings_changed.emit()

            QMessageBox.information(
                self, "Paramètres", "Paramètres appliqués avec succès!"
            )
            self.logger.info("Paramètres appliqués")

        except Exception as e:
            self.logger.error(f"Erreur application paramètres: {e}")
            QMessageBox.critical(
                self, "Erreur", f"Erreur lors de l'application des paramètres:\n{e}"
            )

    def reset_settings(self):
        """Remet les paramètres par défaut"""
        reply = QMessageBox.question(
            self,
            "Réinitialiser",
            "Êtes-vous sûr de vouloir remettre tous les paramètres par défaut?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Remettre les valeurs par défaut
                self.settings = {
                    "general": {
                        "language": "Français",
                        "theme": "Clair",
                        "auto_start": False,
                        "auto_update": True,
                    },
                    "detectron2": {
                        "default_model": "COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml",
                        "confidence_threshold": 0.5,
                        "device": "auto",
                    },
                }

                self.load_settings()
                QMessageBox.information(
                    self, "Réinitialisation", "Paramètres réinitialisés!"
                )

            except Exception as e:
                self.logger.error(f"Erreur réinitialisation: {e}")
                QMessageBox.critical(
                    self, "Erreur", f"Erreur lors de la réinitialisation:\n{e}"
                )
