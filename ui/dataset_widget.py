#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Widget de Gestion des Datasets
© 2025 - Licence Apache 2.0

Interface pour télécharger et gérer les datasets
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QTextEdit,
    QGroupBox,
    QScrollArea,
    QFrame,
    QMessageBox,
    QFileDialog,
    QInputDialog,
    QSplitter,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap

from core.dataset_manager import DatasetManager, DatasetInfo
from core.logger import Logger


class DownloadThread(QThread):
    """Thread pour téléchargement en arrière-plan"""

    progress_updated = pyqtSignal(dict)
    download_finished = pyqtSignal(str, bool)

    def __init__(self, dataset_manager: DatasetManager, dataset_id: str):
        super().__init__()
        self.dataset_manager = dataset_manager
        self.dataset_id = dataset_id

    def run(self):
        """Lance le téléchargement"""

        def progress_callback(progress_info):
            self.progress_updated.emit(progress_info)

        success = self.dataset_manager.download_dataset(
            self.dataset_id, progress_callback
        )

        self.download_finished.emit(self.dataset_id, success)


class DatasetCard(QFrame):
    """Carte d'affichage pour un dataset"""

    download_requested = pyqtSignal(str)
    delete_requested = pyqtSignal(str)

    def __init__(self, dataset: DatasetInfo):
        super().__init__()
        self.dataset = dataset
        self.logger = Logger("DatasetCard")

        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet(
            """
            QFrame {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: white;
                margin: 5px;
            }
            QFrame:hover {
                border-color: #007acc;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
        """
        )

        self.create_ui()

    def create_ui(self):
        """Crée l'interface de la carte"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # En-tête avec nom et statut
        header_layout = QHBoxLayout()

        # Nom du dataset
        name_label = QLabel(self.dataset.name)
        name_font = QFont()
        name_font.setPointSize(12)
        name_font.setBold(True)
        name_label.setFont(name_font)

        # Statut de téléchargement
        status_label = QLabel(
            "✓ Téléchargé" if self.dataset.is_downloaded else "⬇ Disponible"
        )
        status_label.setStyleSheet(
            "color: green; font-weight: bold;"
            if self.dataset.is_downloaded
            else "color: #007acc; font-weight: bold;"
        )

        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(status_label)

        layout.addLayout(header_layout)

        # Description
        desc_label = QLabel(self.dataset.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(desc_label)

        # Informations techniques
        info_layout = QGridLayout()

        info_layout.addWidget(QLabel("Taille:"), 0, 0)
        info_layout.addWidget(QLabel(f"{self.dataset.size_mb} MB"), 0, 1)

        info_layout.addWidget(QLabel("Images:"), 1, 0)
        info_layout.addWidget(QLabel(f"{self.dataset.num_images:,}"), 1, 1)

        info_layout.addWidget(QLabel("Classes:"), 0, 2)
        info_layout.addWidget(QLabel(str(self.dataset.num_classes)), 0, 3)

        info_layout.addWidget(QLabel("Format:"), 1, 2)
        info_layout.addWidget(QLabel(self.dataset.format.upper()), 1, 3)

        # Style pour les infos
        for i in range(info_layout.count()):
            widget = info_layout.itemAt(i).widget()
            if widget and i % 2 == 0:  # Labels
                widget.setStyleSheet("font-weight: bold; color: #333;")
            elif widget:  # Valeurs
                widget.setStyleSheet("color: #666;")

        layout.addLayout(info_layout)

        # Tâches supportées
        tasks_label = QLabel("Tâches: " + ", ".join(self.dataset.tasks))
        tasks_label.setStyleSheet("color: #007acc; font-size: 9px; font-style: italic;")
        layout.addWidget(tasks_label)

        # Barre de progression (cachée par défaut)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Boutons d'action
        buttons_layout = QHBoxLayout()

        if self.dataset.is_downloaded:
            # Bouton supprimer
            delete_btn = QPushButton("Supprimer")
            delete_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """
            )
            delete_btn.clicked.connect(
                lambda: self.delete_requested.emit(self.dataset.id)
            )
            buttons_layout.addWidget(delete_btn)

            # Bouton ouvrir dossier
            open_btn = QPushButton("Ouvrir Dossier")
            open_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """
            )
            open_btn.clicked.connect(self.open_folder)
            buttons_layout.addWidget(open_btn)
        else:
            # Bouton télécharger
            download_btn = QPushButton("Télécharger")
            download_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #007acc;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #005a9e;
                }
            """
            )
            download_btn.clicked.connect(
                lambda: self.download_requested.emit(self.dataset.id)
            )
            buttons_layout.addWidget(download_btn)

        layout.addLayout(buttons_layout)

        # Licence
        license_label = QLabel(f"Licence: {self.dataset.license}")
        license_label.setStyleSheet("color: #999; font-size: 8px;")
        layout.addWidget(license_label)

    def show_progress(self, progress_info: dict):
        """Affiche la progression du téléchargement"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(int(progress_info.get("progress", 0)))

        # Mise à jour du texte de statut
        status = progress_info.get("status", "Téléchargement...")
        speed = progress_info.get("speed", 0)

        if speed > 0:
            speed_text = f" ({speed/1024/1024:.1f} MB/s)"
        else:
            speed_text = ""

        self.progress_bar.setFormat(f"{status}{speed_text} - %p%")

    def hide_progress(self):
        """Cache la barre de progression"""
        self.progress_bar.setVisible(False)

    def open_folder(self):
        """Ouvre le dossier du dataset"""
        try:
            import os
            import subprocess

            if self.dataset.local_path:
                if os.name == "nt":  # Windows
                    os.startfile(self.dataset.local_path)
                elif os.name == "posix":  # Linux/Mac
                    subprocess.run(["xdg-open", self.dataset.local_path])
        except Exception as e:
            self.logger.error(f"Erreur ouverture dossier: {e}")


class DatasetWidget(QWidget):
    """
    Widget principal de gestion des datasets

    Fonctionnalités:
    - Affichage des datasets disponibles
    - Téléchargement avec progression
    - Gestion des datasets personnalisés
    - Statistiques de stockage
    """

    def __init__(self, dataset_manager: DatasetManager):
        super().__init__()
        self.dataset_manager = dataset_manager
        self.logger = Logger("DatasetWidget")

        # Threads de téléchargement actifs
        self.download_threads = {}

        self.create_ui()
        self.refresh_datasets()

        # Timer pour rafraîchissement
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_datasets)
        self.refresh_timer.start(10000)  # Rafraîchir toutes les 10 secondes

    def create_ui(self):
        """Crée l'interface utilisateur"""
        layout = QVBoxLayout(self)

        # En-tête avec actions
        header_layout = self.create_header()
        layout.addLayout(header_layout)

        # Splitter pour diviser l'interface
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Zone des datasets disponibles
        datasets_widget = self.create_datasets_section()
        splitter.addWidget(datasets_widget)

        # Zone des datasets personnels
        personal_widget = self.create_personal_section()
        splitter.addWidget(personal_widget)

        # Proportions du splitter
        splitter.setSizes([700, 300])

    def create_header(self) -> QHBoxLayout:
        """Crée l'en-tête avec les actions"""
        header_layout = QHBoxLayout()

        # Titre
        title = QLabel("Gestion des Datasets")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))

        # Boutons d'action
        refresh_btn = QPushButton("Actualiser")
        refresh_btn.clicked.connect(self.refresh_datasets)

        create_btn = QPushButton("Créer Dataset Personnel")
        create_btn.clicked.connect(self.create_personal_dataset)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        header_layout.addWidget(create_btn)

        return header_layout

    def create_datasets_section(self) -> QWidget:
        """Crée la section des datasets disponibles"""
        group = QGroupBox("Datasets Disponibles")
        layout = QVBoxLayout(group)

        # Zone de défilement
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Widget conteneur pour les cartes
        self.datasets_container = QWidget()
        self.datasets_layout = QVBoxLayout(self.datasets_container)
        self.datasets_layout.setSpacing(10)

        scroll_area.setWidget(self.datasets_container)
        layout.addWidget(scroll_area)

        return group

    def create_personal_section(self) -> QWidget:
        """Crée la section des datasets personnels"""
        group = QGroupBox("Datasets Personnels")
        layout = QVBoxLayout(group)

        # Liste des datasets personnels
        self.personal_list = QTextEdit()
        self.personal_list.setReadOnly(True)
        self.personal_list.setMaximumHeight(200)
        layout.addWidget(self.personal_list)

        # Statistiques
        stats_label = QLabel("Statistiques de Stockage")
        stats_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(stats_label)

        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(150)
        layout.addWidget(self.stats_text)

        return group

    def refresh_datasets(self):
        """Actualise la liste des datasets"""
        try:
            # Nettoyer les cartes existantes
            for i in reversed(range(self.datasets_layout.count())):
                child = self.datasets_layout.itemAt(i).widget()
                if child:
                    child.setParent(None)

            # Récupérer les datasets
            datasets = self.dataset_manager.get_available_datasets()

            # Créer les cartes
            for dataset in datasets:
                card = DatasetCard(dataset)
                card.download_requested.connect(self.start_download)
                card.delete_requested.connect(self.delete_dataset)

                self.datasets_layout.addWidget(card)

            # Spacer pour pousser les cartes vers le haut
            self.datasets_layout.addStretch()

            # Actualiser les datasets personnels
            self.refresh_personal_datasets()

            # Actualiser les statistiques
            self.refresh_stats()

        except Exception as e:
            self.logger.error(f"Erreur actualisation datasets: {e}")

    def refresh_personal_datasets(self):
        """Actualise la liste des datasets personnels"""
        try:
            personal_datasets = self.dataset_manager.get_personal_datasets()

            text = ""
            for dataset in personal_datasets:
                text += f"• {dataset['name']}\n"
                text += f"  {dataset['num_images']} images, {dataset['num_classes']} classes\n"
                text += f"  Format: {dataset['format']}\n\n"

            if not text:
                text = "Aucun dataset personnel créé"

            self.personal_list.setPlainText(text)

        except Exception as e:
            self.logger.error(f"Erreur actualisation datasets personnels: {e}")

    def refresh_stats(self):
        """Actualise les statistiques"""
        try:
            stats = self.dataset_manager.get_storage_stats()

            stats_text = f"""Datasets téléchargés: {stats['num_downloaded']}
Datasets personnels: {stats['num_personal']}

Espace utilisé:
• Téléchargés: {stats['downloaded_size_mb']:.1f} MB
• Personnels: {stats['personal_size_mb']:.1f} MB
• Cache: {stats['cache_size_mb']:.1f} MB
• Total: {stats['total_size_mb']:.1f} MB"""

            self.stats_text.setPlainText(stats_text)

        except Exception as e:
            self.logger.error(f"Erreur actualisation stats: {e}")

    def start_download(self, dataset_id: str):
        """Démarre le téléchargement d'un dataset"""
        if dataset_id in self.download_threads:
            QMessageBox.warning(self, "Téléchargement", "Téléchargement déjà en cours!")
            return

        try:
            # Créer le thread de téléchargement
            thread = DownloadThread(self.dataset_manager, dataset_id)
            thread.progress_updated.connect(
                lambda info: self.update_progress(dataset_id, info)
            )
            thread.download_finished.connect(self.download_finished)

            self.download_threads[dataset_id] = thread
            thread.start()

            self.logger.info(f"Téléchargement démarré: {dataset_id}")

        except Exception as e:
            self.logger.error(f"Erreur démarrage téléchargement: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors du démarrage: {e}")

    def update_progress(self, dataset_id: str, progress_info: dict):
        """Met à jour la progression d'un téléchargement"""
        # Trouver la carte correspondante
        for i in range(self.datasets_layout.count()):
            item = self.datasets_layout.itemAt(i)
            if item and item.widget():
                card = item.widget()
                if isinstance(card, DatasetCard) and card.dataset.id == dataset_id:
                    card.show_progress(progress_info)
                    break

    def download_finished(self, dataset_id: str, success: bool):
        """Gestion de la fin de téléchargement"""
        # Nettoyer le thread
        if dataset_id in self.download_threads:
            thread = self.download_threads[dataset_id]
            thread.quit()
            thread.wait()
            del self.download_threads[dataset_id]

        # Cacher la progression
        for i in range(self.datasets_layout.count()):
            item = self.datasets_layout.itemAt(i)
            if item and item.widget():
                card = item.widget()
                if isinstance(card, DatasetCard) and card.dataset.id == dataset_id:
                    card.hide_progress()
                    break

        # Message de résultat
        if success:
            QMessageBox.information(
                self, "Téléchargement", f"Dataset {dataset_id} téléchargé avec succès!"
            )
        else:
            QMessageBox.critical(
                self, "Erreur", f"Échec du téléchargement de {dataset_id}"
            )

        # Actualiser l'affichage
        self.refresh_datasets()

        self.logger.info(f"Téléchargement terminé: {dataset_id} - Succès: {success}")

    def delete_dataset(self, dataset_id: str):
        """Supprime un dataset"""
        reply = QMessageBox.question(
            self,
            "Supprimer Dataset",
            f"Êtes-vous sûr de vouloir supprimer le dataset {dataset_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.dataset_manager.delete_dataset(dataset_id)

                if success:
                    QMessageBox.information(
                        self, "Suppression", "Dataset supprimé avec succès!"
                    )
                    self.refresh_datasets()
                else:
                    QMessageBox.critical(
                        self, "Erreur", "Erreur lors de la suppression"
                    )

            except Exception as e:
                QMessageBox.critical(
                    self, "Erreur", f"Erreur lors de la suppression: {e}"
                )

    def create_personal_dataset(self):
        """Crée un dataset personnel"""
        try:
            # Demander le nom
            name, ok = QInputDialog.getText(self, "Nouveau Dataset", "Nom du dataset:")
            if not ok or not name.strip():
                return

            # Demander la description
            description, ok = QInputDialog.getText(
                self, "Nouveau Dataset", "Description:"
            )
            if not ok:
                description = ""

            # Sélectionner le dossier source
            source_path = QFileDialog.getExistingDirectory(
                self, "Sélectionner le dossier source"
            )
            if not source_path:
                return

            # Créer le dataset
            dataset_id = self.dataset_manager.create_personal_dataset(
                name.strip(), description.strip(), source_path
            )

            if dataset_id:
                QMessageBox.information(
                    self, "Dataset Créé", f"Dataset '{name}' créé avec succès!"
                )
                self.refresh_datasets()
            else:
                QMessageBox.critical(
                    self, "Erreur", "Erreur lors de la création du dataset"
                )

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la création: {e}")
