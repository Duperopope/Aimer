#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Module Dashboard
© 2025 KairosForge - Tous droits réservés

Widget dashboard avec monitoring système
"""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QProgressBar, QPushButton, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

class SystemCard(QFrame):
    """Carte d'information système"""
    
    def __init__(self, title: str, value: str = "0", unit: str = "", parent=None):
        super().__init__(parent)
        
        self.setObjectName("card")
        self.setMinimumHeight(120)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Titre
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12pt; font-weight: 600; color: #64748b;")
        
        # Valeur
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("font-size: 24pt; font-weight: bold; color: #1e40af;")
        
        # Unité
        if unit:
            unit_label = QLabel(unit)
            unit_label.setStyleSheet("font-size: 10pt; color: #64748b;")
            layout.addWidget(unit_label)
        
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()
    
    def update_value(self, value: str):
        """Met à jour la valeur affichée"""
        self.value_label.setText(value)

class DashboardWidget(QWidget):
    """
    Widget principal du dashboard
    Affiche les informations système et métriques
    """
    
    def __init__(self, settings_manager=None, theme_manager=None, parent=None):
        super().__init__(parent)
        
        self.logger = logging.getLogger("DashboardWidget")
        self.settings_manager = settings_manager
        self.theme_manager = theme_manager
        
        # Timer pour mise à jour
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_metrics)
        
        # Cartes système
        self.cpu_card: Optional[SystemCard] = None
        self.memory_card: Optional[SystemCard] = None
        self.gpu_card: Optional[SystemCard] = None
        self.disk_card: Optional[SystemCard] = None
        
        # Créer interface
        self.create_ui()
        
        # Démarrer monitoring
        self.start_monitoring()
        
        self.logger.info("Dashboard widget initialisé")
    
    def create_ui(self):
        """Crée l'interface du dashboard"""
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        
        # Titre
        title_label = QLabel("🏠 Dashboard Système")
        title_label.setStyleSheet("font-size: 20pt; font-weight: bold; margin-bottom: 16px;")
        layout.addWidget(title_label)
        
        # Grille de cartes système
        cards_layout = QGridLayout()
        cards_layout.setSpacing(16)
        
        # Créer cartes
        self.cpu_card = SystemCard("Processeur", "0", "%")
        self.memory_card = SystemCard("Mémoire", "0", "GB")
        self.gpu_card = SystemCard("GPU", "N/A", "")
        self.disk_card = SystemCard("Disque", "0", "GB")
        
        # Ajouter à la grille
        cards_layout.addWidget(self.cpu_card, 0, 0)
        cards_layout.addWidget(self.memory_card, 0, 1)
        cards_layout.addWidget(self.gpu_card, 1, 0)
        cards_layout.addWidget(self.disk_card, 1, 1)
        
        layout.addLayout(cards_layout)
        
        # Section actions rapides
        self.create_quick_actions(layout)
        
        # Spacer
        layout.addStretch()
    
    def create_quick_actions(self, layout: QVBoxLayout):
        """Crée la section actions rapides"""
        # Titre section
        actions_title = QLabel("Actions Rapides")
        actions_title.setStyleSheet("font-size: 16pt; font-weight: 600; margin-top: 16px;")
        layout.addWidget(actions_title)
        
        # Layout boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        # Boutons d'action
        detection_btn = QPushButton("🎯 Démarrer Détection")
        detection_btn.setMinimumHeight(40)
        detection_btn.clicked.connect(self.start_detection)
        
        learning_btn = QPushButton("🧠 Ouvrir Apprentissage")
        learning_btn.setMinimumHeight(40)
        learning_btn.clicked.connect(self.open_learning)
        
        settings_btn = QPushButton("⚙️ Configuration")
        settings_btn.setMinimumHeight(40)
        settings_btn.clicked.connect(self.open_settings)
        
        buttons_layout.addWidget(detection_btn)
        buttons_layout.addWidget(learning_btn)
        buttons_layout.addWidget(settings_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
    
    def start_monitoring(self):
        """Démarre le monitoring système"""
        # Démarrer timer (mise à jour toutes les 2 secondes)
        self.update_timer.start(2000)
        
        # Première mise à jour immédiate
        self.update_metrics()
    
    def update_metrics(self):
        """Met à jour les métriques système"""
        try:
            # Simulation de données (à remplacer par vraies métriques)
            import random
            
            # CPU
            cpu_usage = random.randint(10, 80)
            self.cpu_card.update_value(f"{cpu_usage}")
            
            # Mémoire (simulation 8-16 GB)
            memory_used = random.uniform(4.0, 12.0)
            self.memory_card.update_value(f"{memory_used:.1f}")
            
            # GPU
            self.gpu_card.update_value("GTX 1060")
            
            # Disque
            disk_free = random.uniform(50.0, 200.0)
            self.disk_card.update_value(f"{disk_free:.0f}")
            
        except Exception as e:
            self.logger.error(f"Erreur mise à jour métriques: {e}")
    
    def start_detection(self):
        """Démarre le module de détection"""
        self.logger.info("Démarrage détection demandé")
        # TODO: Émettre signal pour changer de module
    
    def open_learning(self):
        """Ouvre le module d'apprentissage"""
        self.logger.info("Ouverture apprentissage demandée")
        # TODO: Émettre signal pour changer de module
    
    def open_settings(self):
        """Ouvre les paramètres"""
        self.logger.info("Ouverture paramètres demandée")
        # TODO: Émettre signal pour changer de module
    
    def on_theme_changed(self, theme_name: str):
        """Callback quand le thème change"""
        self.logger.debug(f"Thème dashboard changé: {theme_name}")
        # Réappliquer styles si nécessaire
    
    def cleanup(self):
        """Nettoyage lors de la fermeture"""
        if self.update_timer.isActive():
            self.update_timer.stop()
        
        self.logger.info("Dashboard widget nettoyé")

def create_dashboard_widget(settings_manager=None, theme_manager=None, parent=None) -> DashboardWidget:
    """Factory pour créer le widget dashboard"""
    return DashboardWidget(settings_manager, theme_manager, parent)
