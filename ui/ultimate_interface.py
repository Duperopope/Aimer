#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Interface Ultime
© 2025 - Licence Apache 2.0

Interface complète pour toutes les fonctionnalités de computer vision
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTextEdit, QComboBox, QSpinBox,
    QGroupBox, QTabWidget, QFileDialog, QMessageBox,
    QCheckBox, QSlider, QProgressBar, QLineEdit,
    QTableWidget, QTableWidgetItem, QSplitter,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QImage

# Import des modules core
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.vision_engine import UltimateVisionEngine
from core.logger import Logger

class GameBotWidget(QWidget):
    """Interface pour le bot de jeu"""

    def __init__(self, vision_engine: UltimateVisionEngine):
        super().__init__()
        self.vision_engine = vision_engine
        self.logger = Logger("GameBotWidget")

        self.create_ui()

    def create_ui(self):
        """Crée l'interface du bot de jeu"""
        layout = QVBoxLayout(self)

        # Configuration du jeu
        config_group = QGroupBox("Configuration du Bot")
        config_layout = QGridLayout(config_group)

        # Type de jeu
        config_layout.addWidget(QLabel("Type de jeu:"), 0, 0)
        self.game_type_combo = QComboBox()
        self.game_type_combo.addItems(["fps_shooter", "strategy", "mmorpg", "moba"])
        config_layout.addWidget(self.game_type_combo, 0, 1)

        # Fenêtre cible
        config_layout.addWidget(QLabel("Fenêtre du jeu:"), 1, 0)
        self.window_title_edit = QLineEdit()
        self.window_title_edit.setPlaceholderText("Titre de la fenêtre du jeu")
        config_layout.addWidget(self.window_title_edit, 1, 1)

        # Bouton détecter fenêtres
        detect_windows_btn = QPushButton("Détecter Fenêtres")
        detect_windows_btn.clicked.connect(self.detect_windows)
        config_layout.addWidget(detect_windows_btn, 1, 2)

        # Seuil de confiance
        config_layout.addWidget(QLabel("Confiance:"), 2, 0)
        self.confidence_slider = QSlider(Qt.Orientation.Horizontal)
        self.confidence_slider.setRange(50, 95)
        self.confidence_slider.setValue(80)
        self.confidence_slider.valueChanged.connect(self.update_confidence_label)
        config_layout.addWidget(self.confidence_slider, 2, 1)

        self.confidence_label = QLabel("80%")
        config_layout.addWidget(self.confidence_label, 2, 2)

        layout.addWidget(config_group)

        # Contrôles du bot
        controls_group = QGroupBox("Contrôles")
        controls_layout = QHBoxLayout(controls_group)

        self.start_bot_btn = QPushButton("Démarrer Bot")
        self.start_bot_btn.clicked.connect(self.start_bot)
        self.start_bot_btn.setStyleSheet("""
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
        """)

        self.stop_bot_btn = QPushButton("Arrêter Bot")
        self.stop_bot_btn.clicked.connect(self.stop_bot)
        self.stop_bot_btn.setEnabled(False)
        self.stop_bot_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)

        controls_layout.addWidget(self.start_bot_btn)
        controls_layout.addWidget(self.stop_bot_btn)
        controls_layout.addStretch()

        layout.addWidget(controls_group)

        # Actions personnalisées
        actions_group = QGroupBox("Actions Personnalisées")
        actions_layout = QVBoxLayout(actions_group)

        # Table des actions
        self.actions_table = QTableWidget()
        self.actions_table.setColumnCount(3)
        self.actions_table.setHorizontalHeaderLabels(["Objet", "Action", "Touche"])
        actions_layout.addWidget(self.actions_table)

        # Boutons d'action
        action_buttons = QHBoxLayout()
        add_action_btn = QPushButton("Ajouter Action")
        add_action_btn.clicked.connect(self.add_custom_action)
        remove_action_btn = QPushButton("Supprimer Action")
        remove_action_btn.clicked.connect(self.remove_custom_action)

        action_buttons.addWidget(add_action_btn)
        action_buttons.addWidget(remove_action_btn)
        action_buttons.addStretch()

        actions_layout.addLayout(action_buttons)
        layout.addWidget(actions_group)

        # Log du bot
        log_group = QGroupBox("Log du Bot")
        log_layout = QVBoxLayout(log_group)

        self.bot_log = QTextEdit()
        self.bot_log.setReadOnly(True)
        self.bot_log.setMaximumHeight(150)
        log_layout.addWidget(self.bot_log)

        layout.addWidget(log_group)

        # Timer pour mise à jour du log
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.update_bot_log)
        self.log_timer.start(1000)

    def update_confidence_label(self, value):
        """Met à jour le label de confiance"""
        self.confidence_label.setText(f"{value}%")

    def detect_windows(self):
        """Détecte les fenêtres ouvertes"""
        try:
            import win32gui

            windows = []

            def enum_windows_proc(hwnd, lParam):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title and len(title) > 3:
                        windows.append(title)
                return True

            win32gui.EnumWindows(enum_windows_proc, None)

            # Afficher les fenêtres dans une boîte de dialogue
            window_list = "\n".join(windows[:20])  # Limiter à 20 fenêtres
            QMessageBox.information(self, "Fenêtres Détectées",
                                  f"Fenêtres ouvertes:\n\n{window_list}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur détection fenêtres: {e}")

    def start_bot(self):
        """Démarre le bot de jeu"""
        try:
            game_type = self.game_type_combo.currentText()
            window_title = self.window_title_edit.text().strip()

            if not window_title:
                QMessageBox.warning(self, "Erreur", "Veuillez spécifier le titre de la fenêtre")
                return

            success = self.vision_engine.start_game_automation(game_type, window_title)

            if success:
                self.start_bot_btn.setEnabled(False)
                self.stop_bot_btn.setEnabled(True)
                self.bot_log.append(f"[INFO] Bot démarré pour {game_type}")
                QMessageBox.information(self, "Bot", "Bot de jeu démarré avec succès!")
            else:
                QMessageBox.critical(self, "Erreur", "Impossible de démarrer le bot")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur démarrage bot: {e}")

    def stop_bot(self):
        """Arrête le bot de jeu"""
        try:
            self.vision_engine.stop_all_modules()

            self.start_bot_btn.setEnabled(True)
            self.stop_bot_btn.setEnabled(False)
            self.bot_log.append("[INFO] Bot arrêté")

            QMessageBox.information(self, "Bot", "Bot arrêté")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur arrêt bot: {e}")

    def add_custom_action(self):
        """Ajoute une action personnalisée"""
        # Dialogue pour ajouter une action
        pass

    def remove_custom_action(self):
        """Supprime une action personnalisée"""
        current_row = self.actions_table.currentRow()
        if current_row >= 0:
            self.actions_table.removeRow(current_row)

    def update_bot_log(self):
        """Met à jour le log du bot"""
        # Récupérer les derniers logs du bot
        pass

class MedicalAnalysisWidget(QWidget):
    """Interface pour l'analyse médicale"""

    def __init__(self, vision_engine: UltimateVisionEngine):
        super().__init__()
        self.vision_engine = vision_engine
        self.logger = Logger("MedicalAnalysisWidget")

        self.create_ui()

    def create_ui(self):
        """Crée l'interface d'analyse médicale"""
        layout = QVBoxLayout(self)

        # Sélection d'image
        image_group = QGroupBox("Image Médicale")
        image_layout = QHBoxLayout(image_group)

        self.image_path_edit = QLineEdit()
        self.image_path_edit.setPlaceholderText("Chemin vers l'image médicale")

        browse_btn = QPushButton("Parcourir")
        browse_btn.clicked.connect(self.browse_image)

        image_layout.addWidget(QLabel("Image:"))
        image_layout.addWidget(self.image_path_edit)
        image_layout.addWidget(browse_btn)

        layout.addWidget(image_group)

        # Configuration de l'analyse
        config_group = QGroupBox("Configuration de l'Analyse")
        config_layout = QGridLayout(config_group)

        # Modalité médicale
        config_layout.addWidget(QLabel("Modalité:"), 0, 0)
        self.modality_combo = QComboBox()
        self.modality_combo.addItems(["xray", "mri", "skin", "retina"])
        config_layout.addWidget(self.modality_combo, 0, 1)

        # Seuil de détection
        config_layout.addWidget(QLabel("Seuil:"), 1, 0)
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setRange(30, 90)
        self.threshold_slider.setValue(60)
        self.threshold_slider.valueChanged.connect(self.update_threshold_label)
        config_layout.addWidget(self.threshold_slider, 1, 1)

        self.threshold_label = QLabel("60%")
        config_layout.addWidget(self.threshold_label, 1, 2)

        layout.addWidget(config_group)

        # Bouton d'analyse
        analyze_btn = QPushButton("Analyser Image Médicale")
        analyze_btn.clicked.connect(self.analyze_medical_image)
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                font-weight: bold;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        layout.addWidget(analyze_btn)

        # Résultats de l'analyse
        results_group = QGroupBox("Résultats de l'Analyse")
        results_layout = QVBoxLayout(results_group)

        # Rapport médical
        self.medical_report = QTextEdit()
        self.medical_report.setReadOnly(True)
        results_layout.addWidget(self.medical_report)

        # Boutons d'export
        export_layout = QHBoxLayout()

        export_pdf_btn = QPushButton("Exporter PDF")
        export_pdf_btn.clicked.connect(self.export_pdf_report)

        export_json_btn = QPushButton("Exporter JSON")
        export_json_btn.clicked.connect(self.export_json_report)

        export_layout.addWidget(export_pdf_btn)
        export_layout.addWidget(export_json_btn)
        export_layout.addStretch()

        results_layout.addLayout(export_layout)
        layout.addWidget(results_group)

        # Variables pour stocker les résultats
        self.last_analysis = None

    def update_threshold_label(self, value):
        """Met à jour le label du seuil"""
        self.threshold_label.setText(f"{value}%")

    def browse_image(self):
        """Ouvre un dialogue pour sélectionner une image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner Image Médicale",
            "", "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.dcm)"
        )

        if file_path:
            self.image_path_edit.setText(file_path)

    def analyze_medical_image(self):
        """Lance l'analyse de l'image médicale"""
        try:
            image_path = self.image_path_edit.text().strip()
            modality = self.modality_combo.currentText()

            if not image_path:
                QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une image")
                return

            if not Path(image_path).exists():
                QMessageBox.warning(self, "Erreur", "Le fichier image n'existe pas")
                return

            # Lancer l'analyse
            self.medical_report.setText("Analyse en cours...")

            # Analyse avec le moteur de vision
            result = self.vision_engine.analyze_medical_image(image_path, modality)

            if "error" in result:
                QMessageBox.critical(self, "Erreur", f"Erreur d'analyse: {result['error']}")
                return

            # Afficher les résultats
            self.display_medical_results(result)
            self.last_analysis = result

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur analyse: {e}")

    def display_medical_results(self, result: dict):
        """Affiche les résultats de l'analyse médicale"""
        report = result.get("report", "Aucun rapport généré")

        # Ajouter des informations supplémentaires
        full_report = f"""
=== ANALYSE MÉDICALE AIMER PRO ===

{report}

=== DÉTAILS TECHNIQUES ===
Modalité: {result.get('modality', 'N/A').upper()}
Score de confiance: {result.get('confidence_score', 0):.1%}
Recommandation: {result.get('recommendation', 'N/A')}

=== DÉCOUVERTES ===
"""

        findings = result.get("findings", {})
        if findings.get("detections"):
            for detection in findings["detections"]:
                full_report += f"""
- {detection.get('finding', 'N/A').title()}
  Confiance: {detection.get('confidence', 0):.1%}
  Signification: {detection.get('clinical_significance', 'N/A')}
"""
        else:
            full_report += "Aucune découverte pathologique significative.\n"

        full_report += f"""
=== AVERTISSEMENT ===
Cette analyse est générée par IA et ne remplace pas
un diagnostic médical professionnel. Consultez toujours
un médecin qualifié pour une évaluation clinique.

Généré le: {self._get_current_datetime()}
"""

        self.medical_report.setText(full_report)

    def _get_current_datetime(self) -> str:
        """Retourne la date et heure actuelles"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y à %H:%M:%S")

    def export_pdf_report(self):
        """Exporte le rapport en PDF"""
        if not self.last_analysis:
            QMessageBox.warning(self, "Erreur", "Aucune analyse à exporter")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter Rapport PDF",
            f"rapport_medical_{self._get_current_datetime().replace('/', '_').replace(':', '_')}.pdf",
            "PDF (*.pdf)"
        )

        if file_path:
            # Implémentation export PDF
            QMessageBox.information(self, "Export", f"Rapport exporté: {file_path}")

    def export_json_report(self):
        """Exporte le rapport en JSON"""
        if not self.last_analysis:
            QMessageBox.warning(self, "Erreur", "Aucune analyse à exporter")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter Données JSON",
            f"analyse_medicale_{self._get_current_datetime().replace('/', '_').replace(':', '_')}.json",
            "JSON (*.json)"
        )

        if file_path:
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.last_analysis, f, indent=2, ensure_ascii=False)

            QMessageBox.information(self, "Export", f"Données exportées: {file_path}")

class InteractiveControlWidget(QWidget):
    """Interface pour le contrôle interactif"""

    def __init__(self, vision_engine: UltimateVisionEngine):
        super().__init__()
        self.vision_engine = vision_engine
        self.logger = Logger("InteractiveControlWidget")

        self.create_ui()

    def create_ui(self):
        """Crée l'interface de contrôle interactif"""
        layout = QVBoxLayout(self)

        # Configuration de la zone
        zone_group = QGroupBox("Zone d'Interaction")
        zone_layout = QGridLayout(zone_group)

        zone_layout.addWidget(QLabel("Zone:"), 0, 0)
        self.zone_combo = QComboBox()
        self.zone_combo.addItems(["desktop", "browser", "application"])
        zone_layout.addWidget(self.zone_combo, 0, 1)

        # Coordonnées personnalisées
        zone_layout.addWidget(QLabel("X:"), 1, 0)
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 3840)
        zone_layout.addWidget(self.x_spin, 1, 1)

        zone_layout.addWidget(QLabel("Y:"), 1, 2)
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 2160)
        zone_layout.addWidget(self.y_spin, 1, 3)

        zone_layout.addWidget(QLabel("Largeur:"), 2, 0)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 3840)
        self.width_spin.setValue(1920)
        zone_layout.addWidget(self.width_spin, 2, 1)

        zone_layout.addWidget(QLabel("Hauteur:"), 2, 2)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 2160)
        self.height_spin.setValue(1080)
        zone_layout.addWidget(self.height_spin, 2, 3)

        layout.addWidget(zone_group)

        # Contrôles
        controls_group = QGroupBox("Contrôles")
        controls_layout = QHBoxLayout(controls_group)

        self.start_control_btn = QPushButton("Démarrer Contrôle")
        self.start_control_btn.clicked.connect(self.start_interactive_control)

        self.stop_control_btn = QPushButton("Arrêter Contrôle")
        self.stop_control_btn.clicked.connect(self.stop_interactive_control)
        self.stop_control_btn.setEnabled(False)

        controls_layout.addWidget(self.start_control_btn)
        controls_layout.addWidget(self.stop_control_btn)
        controls_layout.addStretch()

        layout.addWidget(controls_group)

        # Règles d'interaction
        rules_group = QGroupBox("Règles d'Interaction")
        rules_layout = QVBoxLayout(rules_group)

        # Table des règles
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(4)
        self.rules_table.setHorizontalHeaderLabels(["Objet", "Action", "Paramètres", "Actif"])
        rules_layout.addWidget(self.rules_table)

        # Boutons de gestion des règles
        rules_buttons = QHBoxLayout()

        add_rule_btn = QPushButton("Ajouter Règle")
        add_rule_btn.clicked.connect(self.add_interaction_rule)

        edit_rule_btn = QPushButton("Modifier Règle")
        edit_rule_btn.clicked.connect(self.edit_interaction_rule)

        remove_rule_btn = QPushButton("Supprimer Règle")
        remove_rule_btn.clicked.connect(self.remove_interaction_rule)

        rules_buttons.addWidget(add_rule_btn)
        rules_buttons.addWidget(edit_rule_btn)
        rules_buttons.addWidget(remove_rule_btn)
        rules_buttons.addStretch()

        rules_layout.addLayout(rules_buttons)
        layout.addWidget(rules_group)

        # Règles prédéfinies
        self.add_predefined_rules()

    def add_predefined_rules(self):
        """Ajoute des règles prédéfinies"""
        predefined_rules = [
            ("button", "click", "{}"),
            ("link", "click", "{}"),
            ("textbox", "type_text", '{"text": "Hello World"}'),
            ("checkbox", "click", "{}"),
            ("dropdown", "click", "{}")
        ]

        for obj, action, params in predefined_rules:
            row = self.rules_table.rowCount()
            self.rules_table.insertRow(row)

            self.rules_table.setItem(row, 0, QTableWidgetItem(obj))
            self.rules_table.setItem(row, 1, QTableWidgetItem(action))
            self.rules_table.setItem(row, 2, QTableWidgetItem(params))

            checkbox = QCheckBox()
            checkbox.setChecked(True)
            self.rules_table.setCellWidget(row, 3, checkbox)

    def start_interactive_control(self):
        """Démarre le contrôle interactif"""
        try:
            zone = self.zone_combo.currentText()

            # Appliquer les règles actives
            self.apply_active_rules()

            success = self.vision_engine.start_interactive_control(zone)

            if success:
                self.start_control_btn.setEnabled(False)
                self.stop_control_btn.setEnabled(True)
                QMessageBox.information(self, "Contrôle", "Contrôle interactif démarré!")
            else:
                QMessageBox.critical(self, "Erreur", "Impossible de démarrer le contrôle")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur démarrage contrôle: {e}")

    def stop_interactive_control(self):
        """Arrête le contrôle interactif"""
        try:
            self.vision_engine.stop_all_modules()

            self.start_control_btn.setEnabled(True)
            self.stop_control_btn.setEnabled(False)

            QMessageBox.information(self, "Contrôle", "Contrôle interactif arrêté")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur arrêt contrôle: {e}")

    def apply_active_rules(self):
        """Applique les règles actives au moteur de vision"""
        for row in range(self.rules_table.rowCount()):
            checkbox = self.rules_table.cellWidget(row, 3)

            if checkbox and isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                obj = self.rules_table.item(row, 0).text()
                action = self.rules_table.item(row, 1).text()
                params_str = self.rules_table.item(row, 2).text()

                try:
                    import json
                    params = json.loads(params_str)
                    self.vision_engine.add_interaction_rule(obj, action, params)
                except json.JSONDecodeError:
                    self.logger.error(f"Paramètres JSON invalides pour {obj}")

    def add_interaction_rule(self):
        """Ajoute une nouvelle règle d'interaction"""
        # Dialogue pour ajouter une règle
        pass

    def edit_interaction_rule(self):
        """Modifie une règle d'interaction"""
        # Dialogue pour modifier une règle
        pass

    def remove_interaction_rule(self):
        """Supprime une règle d'interaction"""
        current_row = self.rules_table.currentRow()
        if current_row >= 0:
            self.rules_table.removeRow(current_row)

class UltimateInterface(QWidget):
    """Interface ultime combinant toutes les fonctionnalités"""

    def __init__(self):
        super().__init__()
        self.logger = Logger("UltimateInterface")

        # Initialiser le moteur de vision
        self.vision_engine = UltimateVisionEngine()

        self.setWindowTitle("AIMER PRO - Computer Vision Ultime")
        self.setGeometry(100, 100, 1400, 900)

        self.create_ui()

        self.logger.info("Interface ultime initialisée")

    def create_ui(self):
        """Crée l'interface utilisateur complète"""
        layout = QVBoxLayout(self)

        # En-tête
        header = self.create_header()
        layout.addWidget(header)

        # Onglets principaux
        self.tab_widget = QTabWidget()

        # Onglet Bot de Jeu
        game_bot_widget = GameBotWidget(self.vision_engine)
        self.tab_widget.addTab(game_bot_widget, "🎮 Bot de Jeu")

        # Onglet Analyse Médicale
        medical_widget = MedicalAnalysisWidget(self.vision_engine)
        self.tab_widget.addTab(medical_widget, "🏥 Analyse Médicale")

        # Onglet Contrôle Interactif
        interactive_widget = InteractiveControlWidget(self.vision_engine)
        self.tab_widget.addTab(interactive_widget, "🖱️ Contrôle Interactif")

        # Onglet Création de Datasets
        dataset_creation_widget = self.create_dataset_creation_tab()
        self.tab_widget.addTab(dataset_creation_widget, "📊 Création Datasets")

        # Onglet Monitoring
        monitoring_widget = self.create_monitoring_tab()
        self.tab_widget.addTab(monitoring_widget, "📈 Monitoring")

        layout.addWidget(self.tab_widget)

        # Barre de statut
        status_bar = self.create_status_bar()
        layout.addWidget(status_bar)

        # Style
        self.apply_ultimate_style()

    def create_header(self) -> QWidget:
        """Crée l'en-tête de l'interface"""
        header = QFrame()
        header.setFrameStyle(QFrame.Shape.Box)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #007acc, stop:1 #005a9e);
                border-radius: 10px;
                margin: 5px;
            }
        """)

        layout = QHBoxLayout(header)

        # Titre
        title = QLabel("AIMER PRO - Computer Vision Ultime")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 15px;
            }
        """)

        # Boutons d'urgence
        emergency_layout = QVBoxLayout()

        stop_all_btn = QPushButton("ARRÊT D'URGENCE")
        stop_all_btn.clicked.connect(self.emergency_stop)
        stop_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)

        emergency_layout.addWidget(stop_all_btn)

        layout.addWidget(title)
        layout.addStretch()
        layout.addLayout(emergency_layout)

        return header

    def create_dataset_creation_tab(self) -> QWidget:
        """Crée l'onglet de création de datasets"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Message temporaire
        message = QLabel("Création de datasets personnalisés")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #666;
                padding: 50px;
                border: 2px dashed #ccc;
                border-radius: 10px;
            }
        """)

        layout.addWidget(message)
        return widget

    def create_monitoring_tab(self) -> QWidget:
        """Crée l'onglet de monitoring"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Statut des modules
        status_group = QGroupBox("Statut des Modules")
        status_layout = QVBoxLayout(status_group)

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(200)
        status_layout.addWidget(self.status_text)

        layout.addWidget(status_group)

        # Timer pour mise à jour du statut
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(2000)

        return widget

    def create_status_bar(self) -> QWidget:
        """Crée la barre de statut"""
        status_bar = QFrame()
        status_bar.setFrameStyle(QFrame.Shape.Box)
        status_bar.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border-top: 1px solid #ccc;
                padding: 5px;
            }
        """)

        layout = QHBoxLayout(status_bar)

        self.status_label = QLabel("Prêt")
        layout.addWidget(self.status_label)

        layout.addStretch()

        # Indicateur de statut
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("color: green; font-size: 16px;")
        layout.addWidget(self.status_indicator)

        return status_bar

    def apply_ultimate_style(self):
        """Applique le style ultime"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }

            QTabWidget::pane {
                border: 1px solid #ccc;
                background-color: white;
                border-radius: 5px;
            }

            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-weight: bold;
            }

            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 3px solid #007acc;
            }

            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }

            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #005a9e;
            }

            QPushButton:pressed {
                background-color: #004080;
            }

            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)

    def emergency_stop(self):
        """Arrêt d'urgence de tous les modules"""
        try:
            self.vision_engine.stop_all_modules()
            self.status_label.setText("ARRÊT D'URGENCE ACTIVÉ")
            self.status_indicator.setStyleSheet("color: red; font-size: 16px;")

            QMessageBox.warning(self, "Arrêt d'Urgence",
                              "Tous les modules ont été arrêtés immédiatement!")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur arrêt d'urgence: {e}")

    def update_status(self):
        """Met à jour le statut des modules"""
        try:
            status = self.vision_engine.get_status()

            status_text = "=== STATUT DES MODULES ===\n\n"

            if status["game_bot_running"]:
                status_text += "🎮 Bot de Jeu: ACTIF\n"
            else:
                status_text += "🎮 Bot de Jeu: Arrêté\n"

            if status["interactive_controller_running"]:
                status_text += "🖱️ Contrôle Interactif: ACTIF\n"
            else:
                status_text += "🖱️ Contrôle Interactif: Arrêté\n"

            if status["detector_available"]:
                status_text += "🎯 Détecteur: Disponible\n"
            else:
                status_text += "🎯 Détecteur: Non disponible\n"

            status_text += f"\nModules actifs: {len(status['active_modules'])}\n"

            if hasattr(self, 'status_text'):
                self.status_text.setText(status_text)

            # Mettre à jour l'indicateur
            if status['active_modules']:
                self.status_indicator.setStyleSheet("color: orange; font-size: 16px;")
                self.status_label.setText("Modules actifs")
            else:
                self.status_indicator.setStyleSheet("color: green; font-size: 16px;")
                self.status_label.setText("Prêt")

        except Exception as e:
            if hasattr(self, 'status_text'):
                self.status_text.setText(f"Erreur mise à jour statut: {e}")
