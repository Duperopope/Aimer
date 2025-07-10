#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Dialogue de Progression
© 2025 - Licence Apache 2.0

Dialogue pour afficher la progression des opérations longues
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QPushButton, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class ProgressDialog(QDialog):
    """
    Dialogue de progression pour les opérations longues
    
    Fonctionnalités:
    - Barre de progression
    - Affichage du statut
    - Vitesse de téléchargement
    - Log des opérations
    """
    
    def __init__(self, title: str = "Progression", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        self.create_ui()
    
    def create_ui(self):
        """Crée l'interface du dialogue"""
        layout = QVBoxLayout(self)
        
        # Titre
        self.title_label = QLabel("Opération en cours...")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Informations de statut
        self.status_label = QLabel("Initialisation...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Informations de vitesse
        self.speed_label = QLabel("")
        self.speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speed_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.speed_label)
        
        # Zone de log (optionnelle)
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setReadOnly(True)
        self.log_text.setVisible(False)
        layout.addWidget(self.log_text)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        # Bouton afficher/masquer log
        self.toggle_log_btn = QPushButton("Afficher Log")
        self.toggle_log_btn.clicked.connect(self.toggle_log)
        buttons_layout.addWidget(self.toggle_log_btn)
        
        buttons_layout.addStretch()
        
        # Bouton annuler
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def update_progress(self, progress_info: dict):
        """
        Met à jour la progression
        
        Args:
            progress_info: Dictionnaire avec les infos de progression
                - progress: Pourcentage (0-100)
                - status: Message de statut
                - speed: Vitesse en bytes/sec
                - downloaded: Bytes téléchargés
                - total: Total bytes
                - elapsed: Temps écoulé
        """
        # Progression
        progress = progress_info.get('progress', 0)
        self.progress_bar.setValue(int(progress))
        
        # Statut
        status = progress_info.get('status', 'En cours...')
        self.status_label.setText(status)
        
        # Vitesse et informations
        speed = progress_info.get('speed', 0)
        downloaded = progress_info.get('downloaded', 0)
        total = progress_info.get('total', 0)
        elapsed = progress_info.get('elapsed', 0)
        
        if speed > 0:
            speed_mb = speed / (1024 * 1024)
            speed_text = f"Vitesse: {speed_mb:.1f} MB/s"
            
            if total > 0:
                downloaded_mb = downloaded / (1024 * 1024)
                total_mb = total / (1024 * 1024)
                speed_text += f" | {downloaded_mb:.1f}/{total_mb:.1f} MB"
            
            if elapsed > 0:
                remaining = (total - downloaded) / speed if speed > 0 else 0
                if remaining > 0:
                    remaining_min = remaining / 60
                    speed_text += f" | Restant: {remaining_min:.1f} min"
            
            self.speed_label.setText(speed_text)
        else:
            self.speed_label.setText("")
        
        # Log
        if status and hasattr(self, '_last_status') and status != self._last_status:
            self.add_log(status)
        self._last_status = status
    
    def add_log(self, message: str):
        """Ajoute un message au log"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def toggle_log(self):
        """Affiche/masque la zone de log"""
        if self.log_text.isVisible():
            self.log_text.setVisible(False)
            self.toggle_log_btn.setText("Afficher Log")
            self.setFixedSize(400, 200)
        else:
            self.log_text.setVisible(True)
            self.toggle_log_btn.setText("Masquer Log")
            self.setFixedSize(400, 300)
    
    def set_title(self, title: str):
        """Change le titre de l'opération"""
        self.title_label.setText(title)
    
    def set_finished(self, success: bool, message: str = ""):
        """Marque l'opération comme terminée"""
        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText(message or "Terminé avec succès!")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.cancel_btn.setText("Fermer")
        else:
            self.status_label.setText(message or "Erreur lors de l'opération")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.cancel_btn.setText("Fermer")
        
        self.speed_label.setText("")
        
        if message:
            self.add_log(message)
