#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Module Apprentissage
© 2025 KairosForge - Tous droits réservés

Widget d'apprentissage et formation
"""

import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class LearningWidget(QWidget):
    """Widget d'apprentissage (placeholder)"""
    
    def __init__(self, settings_manager=None, theme_manager=None, parent=None):
        super().__init__(parent)
        
        self.logger = logging.getLogger("LearningWidget")
        self.settings_manager = settings_manager
        self.theme_manager = theme_manager
        
        self.create_ui()
        self.logger.info("Learning widget initialisé")
    
    def create_ui(self):
        """Crée l'interface"""
        layout = QVBoxLayout(self)
        
        title = QLabel("🧠 Module Apprentissage")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18pt; font-weight: bold; margin: 20px;")
        
        message = QLabel("Module d'apprentissage en cours de développement...")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setStyleSheet("color: #64748b; font-size: 12pt;")
        
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(message)
        layout.addStretch()
    
    def on_theme_changed(self, theme_name: str):
        """Callback changement thème"""
        pass
    
    def cleanup(self):
        """Nettoyage"""
        pass
