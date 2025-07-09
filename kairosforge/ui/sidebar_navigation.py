#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Navigation Sidebar
© 2025 KairosForge - Tous droits réservés

Sidebar de navigation professionnelle
"""

from typing import Dict, List, Optional
import logging

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QButtonGroup, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon

class SidebarButton(QPushButton):
    """Bouton personnalisé pour la sidebar"""
    
    def __init__(self, text: str, icon_text: str = "", module_name: str = ""):
        super().__init__()
        
        self.module_name = module_name
        self.icon_text = icon_text
        
        # Configuration bouton
        self.setObjectName("sidebar_button")
        self.setCheckable(True)
        self.setAutoExclusive(False)  # Géré par QButtonGroup
        
        # Texte avec icône
        display_text = f"{icon_text} {text}" if icon_text else text
        self.setText(display_text)
        
        # Style et taille
        self.setMinimumHeight(48)
        self.setMaximumHeight(48)
        
        # Alignement texte
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 16px;
            }
        """)

class SidebarNavigation(QFrame):
    """
    Navigation sidebar professionnelle
    Gère la navigation entre modules
    """
    
    # Signaux
    module_selected = pyqtSignal(str)  # Émis quand un module est sélectionné
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = logging.getLogger("SidebarNavigation")
        
        # Configuration frame
        self.setObjectName("sidebar")
        self.setFixedWidth(240)
        
        # Groupe de boutons (exclusif)
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        
        # Boutons de navigation
        self.nav_buttons: Dict[str, SidebarButton] = {}
        
        # Module actif
        self.active_module = "dashboard"
        
        # Créer interface
        self.create_ui()
        
        # Connexions
        self.setup_connections()
        
        self.logger.info("Navigation sidebar initialisée")
    
    def create_ui(self):
        """Crée l'interface de la sidebar"""
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # En-tête avec logo/titre
        self.create_header(layout)
        
        # Zone de navigation
        self.create_navigation(layout)
        
        # Spacer pour pousser vers le bas
        layout.addStretch()
        
        # Pied de page
        self.create_footer(layout)
    
    def create_header(self, layout: QVBoxLayout):
        """Crée l'en-tête de la sidebar"""
        header_frame = QFrame()
        header_frame.setObjectName("sidebar_header")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 20, 16, 20)
        
        # Logo/Titre
        title_label = QLabel("AIMER PRO")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16pt;
                font-weight: bold;
                color: #1e40af;
                margin-bottom: 4px;
            }
        """)
        
        # Sous-titre
        subtitle_label = QLabel("KairosForge")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                color: #64748b;
                font-weight: 500;
            }
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
    
    def create_navigation(self, layout: QVBoxLayout):
        """Crée la zone de navigation"""
        nav_frame = QFrame()
        nav_frame.setObjectName("sidebar_nav")
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(8, 16, 8, 16)
        nav_layout.setSpacing(4)
        
        # Définition des modules
        modules = [
            {
                "name": "dashboard",
                "title": "Dashboard",
                "icon": "🏠",
                "description": "Monitoring système"
            },
            {
                "name": "detection",
                "title": "Détection Live",
                "icon": "🎯",
                "description": "Détection temps réel"
            },
            {
                "name": "datasets",
                "title": "Datasets",
                "icon": "📚",
                "description": "Gestion datasets"
            },
            {
                "name": "learning",
                "title": "Apprentissage",
                "icon": "🧠",
                "description": "Formation modèles"
            },
            {
                "name": "settings",
                "title": "Configuration",
                "icon": "⚙️",
                "description": "Paramètres app"
            }
        ]
        
        # Créer boutons de navigation
        for module in modules:
            button = self.create_nav_button(
                module["name"],
                module["title"],
                module["icon"]
            )
            
            # Tooltip
            button.setToolTip(module["description"])
            
            # Ajouter au layout et groupe
            nav_layout.addWidget(button)
            self.button_group.addButton(button)
            self.nav_buttons[module["name"]] = button
        
        layout.addWidget(nav_frame)
    
    def create_nav_button(self, module_name: str, title: str, icon: str) -> SidebarButton:
        """Crée un bouton de navigation"""
        button = SidebarButton(title, icon, module_name)
        
        # Connecter signal
        button.clicked.connect(lambda: self.on_button_clicked(module_name))
        
        return button
    
    def create_footer(self, layout: QVBoxLayout):
        """Crée le pied de page de la sidebar"""
        footer_frame = QFrame()
        footer_frame.setObjectName("sidebar_footer")
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setContentsMargins(16, 16, 16, 20)
        
        # Version
        version_label = QLabel("v1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                color: #64748b;
                margin-bottom: 8px;
            }
        """)
        
        # Copyright
        copyright_label = QLabel("© 2025 KairosForge")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet("""
            QLabel {
                font-size: 8pt;
                color: #64748b;
            }
        """)
        
        footer_layout.addWidget(version_label)
        footer_layout.addWidget(copyright_label)
        
        layout.addWidget(footer_frame)
    
    def setup_connections(self):
        """Configure les connexions de signaux"""
        # Connexion groupe de boutons
        self.button_group.buttonClicked.connect(self.on_group_button_clicked)
    
    def on_button_clicked(self, module_name: str):
        """Callback quand un bouton est cliqué"""
        self.set_active_module(module_name)
        self.module_selected.emit(module_name)
        
        self.logger.info(f"Module sélectionné: {module_name}")
    
    def on_group_button_clicked(self, button):
        """Callback pour le groupe de boutons"""
        if hasattr(button, 'module_name'):
            self.on_button_clicked(button.module_name)
    
    def set_active_module(self, module_name: str):
        """Définit le module actif"""
        if module_name in self.nav_buttons:
            # Désactiver tous les boutons
            for button in self.nav_buttons.values():
                button.setChecked(False)
            
            # Activer le bouton sélectionné
            self.nav_buttons[module_name].setChecked(True)
            self.active_module = module_name
            
            self.logger.debug(f"Module actif: {module_name}")
        else:
            self.logger.warning(f"Module inconnu: {module_name}")
    
    def get_active_module(self) -> str:
        """Retourne le module actuellement actif"""
        return self.active_module
    
    def add_custom_button(self, module_name: str, title: str, icon: str = "", position: int = -1):
        """Ajoute un bouton personnalisé"""
        if module_name in self.nav_buttons:
            self.logger.warning(f"Module {module_name} existe déjà")
            return
        
        # Créer bouton
        button = self.create_nav_button(module_name, title, icon)
        
        # Ajouter au groupe
        self.button_group.addButton(button)
        self.nav_buttons[module_name] = button
        
        # Ajouter au layout (position spécifique si demandée)
        nav_frame = self.findChild(QFrame, "sidebar_nav")
        if nav_frame:
            layout = nav_frame.layout()
            if position >= 0 and position < layout.count():
                layout.insertWidget(position, button)
            else:
                layout.addWidget(button)
        
        self.logger.info(f"Bouton personnalisé ajouté: {module_name}")
    
    def remove_button(self, module_name: str):
        """Supprime un bouton de navigation"""
        if module_name not in self.nav_buttons:
            self.logger.warning(f"Module {module_name} n'existe pas")
            return
        
        # Récupérer bouton
        button = self.nav_buttons[module_name]
        
        # Supprimer du groupe
        self.button_group.removeButton(button)
        
        # Supprimer du layout
        button.setParent(None)
        button.deleteLater()
        
        # Supprimer du dictionnaire
        del self.nav_buttons[module_name]
        
        # Si c'était le module actif, sélectionner dashboard
        if self.active_module == module_name:
            self.set_active_module("dashboard")
        
        self.logger.info(f"Bouton supprimé: {module_name}")
    
    def update_button_text(self, module_name: str, new_title: str):
        """Met à jour le texte d'un bouton"""
        if module_name in self.nav_buttons:
            button = self.nav_buttons[module_name]
            icon = button.icon_text
            display_text = f"{icon} {new_title}" if icon else new_title
            button.setText(display_text)
            
            self.logger.debug(f"Texte bouton mis à jour: {module_name} -> {new_title}")
    
    def set_button_enabled(self, module_name: str, enabled: bool):
        """Active/désactive un bouton"""
        if module_name in self.nav_buttons:
            self.nav_buttons[module_name].setEnabled(enabled)
            
            self.logger.debug(f"Bouton {'activé' if enabled else 'désactivé'}: {module_name}")
    
    def get_button_count(self) -> int:
        """Retourne le nombre de boutons"""
        return len(self.nav_buttons)
    
    def get_button_names(self) -> List[str]:
        """Retourne la liste des noms de modules"""
        return list(self.nav_buttons.keys())
    
    def highlight_button(self, module_name: str, highlight: bool = True):
        """Met en surbrillance un bouton (pour notifications)"""
        if module_name in self.nav_buttons:
            button = self.nav_buttons[module_name]
            
            if highlight:
                # Ajouter style de surbrillance
                button.setStyleSheet("""
                    QPushButton#sidebar_button {
                        background-color: #f59e0b;
                        color: white;
                        font-weight: bold;
                    }
                """)
            else:
                # Retirer style de surbrillance
                button.setStyleSheet("")
            
            self.logger.debug(f"Bouton {'surligné' if highlight else 'normal'}: {module_name}")

def create_sidebar_navigation(parent=None) -> SidebarNavigation:
    """Factory pour créer la navigation sidebar"""
    return SidebarNavigation(parent)
