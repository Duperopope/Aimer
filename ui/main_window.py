#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Fenêtre Principale
© 2025 - Licence Apache 2.0

Interface principale avec gestion des datasets
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QLabel,
    QStatusBar,
    QPushButton,
    QSplitter,
    QTextEdit,
    QProgressBar,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon

# Import des modules core
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.dataset_manager import DatasetManager
from core.logger import Logger

from .dataset_widget import DatasetWidget
from .progress_dialog import ProgressDialog
from .detection_interface import DetectionWidget
from .settings_widget import SettingsWidget


class MainWindow(QMainWindow):
    """
    Fenêtre principale de AIMER PRO

    Fonctionnalités:
    - Onglets pour différentes sections
    - Gestion des datasets
    - Interface de détection
    - Statistiques et monitoring
    """

    def __init__(self):
        super().__init__()
        self.logger = Logger("MainWindow")

        # Initialisation des managers
        self.dataset_manager = DatasetManager()

        # Configuration de la fenêtre
        self.setWindowTitle("AIMER PRO - Détection Universelle avec Detectron2")
        self.setGeometry(100, 100, 1200, 800)

        # Création de l'interface
        self.create_ui()

        # Timer pour les mises à jour
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_stats)
        self.update_timer.start(5000)  # Mise à jour toutes les 5 secondes

        self.logger.info("Fenêtre principale initialisée")

    def create_ui(self):
        """Crée l'interface utilisateur"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)

        # Header avec titre et infos
        header_layout = self.create_header()
        main_layout.addLayout(header_layout)

        # Onglets principaux
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Création des onglets
        self.create_tabs()

        # Barre de statut
        self.create_status_bar()

        # Style
        self.apply_style()

    def create_header(self) -> QHBoxLayout:
        """Crée l'en-tête de l'application"""
        header_layout = QHBoxLayout()

        # Titre
        title_label = QLabel("AIMER PRO")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)

        # Sous-titre
        subtitle_label = QLabel("Détection Universelle avec Detectron2")
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #666;")

        # Layout titre
        title_layout = QVBoxLayout()
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)

        # Boutons d'action rapide
        quick_actions = self.create_quick_actions()

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addLayout(quick_actions)

        return header_layout

    def create_quick_actions(self) -> QHBoxLayout:
        """Crée les boutons d'action rapide"""
        actions_layout = QHBoxLayout()

        # Bouton vérification système
        check_btn = QPushButton("Vérifier Système")
        check_btn.clicked.connect(self.check_system)

        # Bouton nettoyage cache
        clean_btn = QPushButton("Nettoyer Cache")
        clean_btn.clicked.connect(self.clean_cache)

        # Bouton aide
        help_btn = QPushButton("Aide")
        help_btn.clicked.connect(self.show_help)

        actions_layout.addWidget(check_btn)
        actions_layout.addWidget(clean_btn)
        actions_layout.addWidget(help_btn)

        return actions_layout

    def create_tabs(self):
        """Crée les onglets principaux"""
        # Onglet Datasets
        self.dataset_widget = DatasetWidget(self.dataset_manager)
        self.tab_widget.addTab(self.dataset_widget, "📊 Datasets")

        # Onglet Détection
        detection_widget = self.create_detection_tab()
        self.tab_widget.addTab(detection_widget, "🎯 Détection")

        # Onglet Statistiques
        stats_widget = self.create_stats_tab()
        self.tab_widget.addTab(stats_widget, "📈 Statistiques")

        # Onglet Paramètres
        settings_widget = self.create_settings_tab()
        self.tab_widget.addTab(settings_widget, "⚙️ Paramètres")

    def create_detection_tab(self) -> QWidget:
        """Crée l'onglet de détection"""
        return DetectionWidget()

    def create_stats_tab(self) -> QWidget:
        """Crée l'onglet des statistiques"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Titre
        title = QLabel("Statistiques de Stockage")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Zone de texte pour les stats
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        layout.addWidget(self.stats_text)

        # Mise à jour initiale
        self.update_stats()

        return widget

    def create_settings_tab(self) -> QWidget:
        """Crée l'onglet des paramètres"""
        return SettingsWidget()

    def create_status_bar(self):
        """Crée la barre de statut"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Message par défaut
        self.status_bar.showMessage("Prêt")

        # Barre de progression (cachée par défaut)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

    def apply_style(self):
        """Applique le style à l'interface"""
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f5f5f5;
            }

            QTabWidget::pane {
                border: 1px solid #ccc;
                background-color: white;
            }

            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }

            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #007acc;
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

            QStatusBar {
                background-color: #e0e0e0;
                border-top: 1px solid #ccc;
            }
        """
        )

    def check_system(self):
        """Vérifie l'état du système"""
        try:
            # Vérification des dépendances
            missing = []
            available = []

            try:
                import torch

                available.append("PyTorch")
            except ImportError:
                missing.append("PyTorch")

            try:
                import detectron2

                available.append("Detectron2")
            except ImportError:
                missing.append("Detectron2")

            try:
                import cv2

                available.append("OpenCV")
            except ImportError:
                missing.append("OpenCV")

            # Statistiques datasets
            stats = self.dataset_manager.get_storage_stats()

            # Message de résultat
            message = "=== VÉRIFICATION SYSTÈME ===\n\n"

            message += "Dépendances disponibles:\n"
            for dep in available:
                message += f"  ✓ {dep}\n"

            if missing:
                message += "\nDépendances manquantes:\n"
                for dep in missing:
                    message += f"  ✗ {dep}\n"

            message += f"\n=== STATISTIQUES DATASETS ===\n"
            message += f"Datasets téléchargés: {stats['num_downloaded']}\n"
            message += f"Datasets personnels: {stats['num_personal']}\n"
            message += f"Espace utilisé: {stats['total_size_mb']:.1f} MB\n"

            QMessageBox.information(self, "Vérification Système", message)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la vérification: {e}")

    def clean_cache(self):
        """Nettoie le cache"""
        try:
            self.dataset_manager.cleanup_cache()
            QMessageBox.information(self, "Cache", "Cache nettoyé avec succès!")
            self.update_stats()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du nettoyage: {e}")

    def show_help(self):
        """Affiche l'aide"""
        help_text = """
=== AIDE AIMER PRO ===

ONGLETS DISPONIBLES:

📊 Datasets:
- Télécharger des datasets populaires (COCO, Pascal VOC, etc.)
- Créer des datasets personnalisés
- Gérer le stockage

🎯 Détection:
- Interface de détection (en développement)
- Test des modèles sur images

📈 Statistiques:
- Statistiques de stockage
- Historique des téléchargements

⚙️ Paramètres:
- Configuration de l'application (en développement)

ACTIONS RAPIDES:
- Vérifier Système: Vérifie les dépendances
- Nettoyer Cache: Libère l'espace disque
- Aide: Affiche cette aide

Pour plus d'informations, consultez le README.md
        """

        QMessageBox.information(self, "Aide AIMER PRO", help_text)

    def update_stats(self):
        """Met à jour les statistiques"""
        try:
            stats = self.dataset_manager.get_storage_stats()

            stats_text = f"""
=== STATISTIQUES DE STOCKAGE ===

Datasets téléchargés: {stats['num_downloaded']}
Datasets personnels: {stats['num_personal']}

Espace utilisé:
  - Datasets téléchargés: {stats['downloaded_size_mb']:.1f} MB
  - Datasets personnels: {stats['personal_size_mb']:.1f} MB
  - Cache: {stats['cache_size_mb']:.1f} MB
  - Total: {stats['total_size_mb']:.1f} MB

=== HISTORIQUE RÉCENT ===
"""

            # Historique récent
            history = self.dataset_manager.get_download_history()
            for entry in history[:5]:  # 5 dernières entrées
                stats_text += f"{entry['timestamp'][:19]} - {entry['action']} - {entry['dataset_id']}\n"

            self.stats_text.setPlainText(stats_text)

        except Exception as e:
            self.logger.error(f"Erreur mise à jour stats: {e}")

    def show_progress(self, title: str, message: str):
        """Affiche une barre de progression"""
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage(f"{title}: {message}")

    def hide_progress(self):
        """Cache la barre de progression"""
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Prêt")

    def closeEvent(self, event):
        """Gestion de la fermeture de l'application"""
        self.logger.info("Fermeture de l'application")
        event.accept()
