#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Fenêtre Principale
© 2025 KairosForge - Tous droits réservés

Single Window Application avec sidebar navigation
"""

import sys
from typing import Optional, Dict, Any
import logging

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QFrame, QPushButton, QLabel, QStackedWidget,
    QStatusBar, QMenuBar, QMenu, QMessageBox,
    QSplitter, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QIcon, QFont

# Imports locaux
from .sidebar_navigation import SidebarNavigation
from ..modules.dashboard.dashboard_widget import DashboardWidget
from ..modules.detection.detection_widget import DetectionWidget
from ..modules.learning.learning_widget import LearningWidget
from ..modules.settings.settings_widget import SettingsWidget

class MainWindow(QMainWindow):
    """
    Fenêtre principale AIMER PRO
    Architecture Single Window Application
    """
    
    # Signaux
    module_changed = pyqtSignal(str)  # Émis quand on change de module
    
    def __init__(self, settings_manager, theme_manager, license_manager):
        super().__init__()
        
        self.logger = logging.getLogger("MainWindow")
        
        # Gestionnaires
        self.settings_manager = settings_manager
        self.theme_manager = theme_manager
        self.license_manager = license_manager
        
        # Variables d'instance
        self.sidebar: Optional[SidebarNavigation] = None
        self.content_stack: Optional[QStackedWidget] = None
        self.status_bar: Optional[QStatusBar] = None
        
        # Modules
        self.modules: Dict[str, QWidget] = {}
        self.current_module = "dashboard"
        
        # Configuration fenêtre
        self.setup_window()
        
        # Interface utilisateur
        self.create_ui()
        
        # Menu et barre de statut
        self.create_menu_bar()
        self.create_status_bar()
        
        # Connexions
        self.setup_connections()
        
        # Appliquer thème
        self.apply_theme()
        
        # Restaurer géométrie
        self.restore_geometry()
        
        self.logger.info("Fenêtre principale initialisée")
    
    def setup_window(self):
        """Configure les propriétés de la fenêtre"""
        # Titre et icône
        self.setWindowTitle("AIMER PRO - KairosForge")
        
        # Taille et position
        self.setMinimumSize(1280, 720)
        self.resize(1400, 900)
        
        # Propriétés fenêtre
        self.setWindowFlags(Qt.WindowType.Window)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
    
    def create_ui(self):
        """Crée l'interface utilisateur principale"""
        # Layout principal horizontal
        main_layout = QHBoxLayout(self.centralWidget())
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Créer sidebar
        self.sidebar = SidebarNavigation(self)
        self.sidebar.setObjectName("sidebar")
        
        # Créer zone de contenu
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("content_area")
        
        # Ajouter au layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_stack, 1)  # Stretch factor 1
        
        # Créer modules
        self.create_modules()
        
        # Module par défaut
        self.show_module("dashboard")
    
    def create_modules(self):
        """Crée tous les modules de l'application"""
        try:
            # Module Dashboard
            self.modules["dashboard"] = DashboardWidget(
                settings_manager=self.settings_manager,
                theme_manager=self.theme_manager
            )
            self.content_stack.addWidget(self.modules["dashboard"])
            
            # Module Détection
            self.modules["detection"] = DetectionWidget(
                settings_manager=self.settings_manager,
                theme_manager=self.theme_manager
            )
            self.content_stack.addWidget(self.modules["detection"])
            
            # Module Apprentissage
            self.modules["learning"] = LearningWidget(
                settings_manager=self.settings_manager,
                theme_manager=self.theme_manager
            )
            self.content_stack.addWidget(self.modules["learning"])
            
            # Module Paramètres
            self.modules["settings"] = SettingsWidget(
                settings_manager=self.settings_manager,
                theme_manager=self.theme_manager,
                license_manager=self.license_manager
            )
            self.content_stack.addWidget(self.modules["settings"])
            
            self.logger.info("Modules créés avec succès")
            
        except Exception as e:
            self.logger.error(f"Erreur création modules: {e}")
            # Créer modules de fallback
            self.create_fallback_modules()
    
    def create_fallback_modules(self):
        """Crée des modules de fallback en cas d'erreur"""
        for module_name in ["dashboard", "detection", "learning", "settings"]:
            if module_name not in self.modules:
                fallback_widget = self.create_fallback_widget(module_name)
                self.modules[module_name] = fallback_widget
                self.content_stack.addWidget(fallback_widget)
    
    def create_fallback_widget(self, module_name: str) -> QWidget:
        """Crée un widget de fallback pour un module"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Titre
        title = QLabel(f"Module {module_name.title()}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18pt; font-weight: bold; margin: 20px;")
        
        # Message
        message = QLabel("Module en cours de développement...")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setStyleSheet("color: #64748b; font-size: 12pt;")
        
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(message)
        layout.addStretch()
        
        return widget
    
    def create_menu_bar(self):
        """Crée la barre de menu"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("&Fichier")
        
        # Action Nouveau projet
        new_action = QAction("&Nouveau projet", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        # Action Ouvrir
        open_action = QAction("&Ouvrir...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Action Quitter
        quit_action = QAction("&Quitter", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Menu Affichage
        view_menu = menubar.addMenu("&Affichage")
        
        # Action Basculer thème
        theme_action = QAction("Basculer &thème", self)
        theme_action.setShortcut("Ctrl+T")
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)
        
        # Menu Aide
        help_menu = menubar.addMenu("&Aide")
        
        # Action À propos
        about_action = QAction("À &propos", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Action Licence
        license_action = QAction("&Licence", self)
        license_action.triggered.connect(self.show_license_info)
        help_menu.addAction(license_action)
    
    def create_status_bar(self):
        """Crée la barre de statut"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Message par défaut
        self.status_bar.showMessage("Prêt")
        
        # Informations licence (à droite)
        license_info = self.license_manager.get_license_info()
        license_text = f"Licence: {license_info['license_type'].title()}"
        if license_info['days_remaining'] > 0:
            license_text += f" ({license_info['days_remaining']} jours restants)"
        
        license_label = QLabel(license_text)
        license_label.setStyleSheet("color: #64748b; margin-right: 10px;")
        self.status_bar.addPermanentWidget(license_label)
    
    def setup_connections(self):
        """Configure les connexions de signaux"""
        # Connexion sidebar
        if self.sidebar:
            self.sidebar.module_selected.connect(self.show_module)
        
        # Connexion thème
        if self.theme_manager:
            self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    def show_module(self, module_name: str):
        """Affiche un module spécifique"""
        if module_name in self.modules:
            widget = self.modules[module_name]
            self.content_stack.setCurrentWidget(widget)
            self.current_module = module_name
            
            # Mettre à jour sidebar
            if self.sidebar:
                self.sidebar.set_active_module(module_name)
            
            # Mettre à jour barre de statut (seulement si elle existe)
            if self.status_bar:
                self.status_bar.showMessage(f"Module: {module_name.title()}")
            
            # Émettre signal
            self.module_changed.emit(module_name)
            
            self.logger.info(f"Module affiché: {module_name}")
        else:
            self.logger.warning(f"Module inconnu: {module_name}")
    
    def apply_theme(self):
        """Applique le thème actuel"""
        if self.theme_manager:
            current_theme = self.settings_manager.get_setting("ui", "theme", "dark")
            self.theme_manager.set_theme(current_theme)
    
    def toggle_theme(self):
        """Bascule le thème"""
        if self.theme_manager:
            self.theme_manager.toggle_theme()
            
            # Sauvegarder nouveau thème
            new_theme = self.theme_manager.get_current_theme()
            self.settings_manager.set_setting("ui", "theme", new_theme)
            self.settings_manager.save_settings()
    
    def on_theme_changed(self, theme_name: str):
        """Callback quand le thème change"""
        self.logger.info(f"Thème changé: {theme_name}")
        
        # Notifier les modules
        for module in self.modules.values():
            if hasattr(module, 'on_theme_changed'):
                module.on_theme_changed(theme_name)
    
    def restore_geometry(self):
        """Restaure la géométrie de la fenêtre"""
        try:
            geometry = self.settings_manager.get_setting("ui", "window_geometry", "")
            state = self.settings_manager.get_setting("ui", "window_state", "")
            
            if geometry:
                self.restoreGeometry(geometry.encode())
            if state:
                self.restoreState(state.encode())
                
        except Exception as e:
            self.logger.warning(f"Erreur restauration géométrie: {e}")
    
    def save_geometry(self):
        """Sauvegarde la géométrie de la fenêtre"""
        try:
            geometry = self.saveGeometry().data().decode()
            state = self.saveState().data().decode()
            
            self.settings_manager.set_setting("ui", "window_geometry", geometry)
            self.settings_manager.set_setting("ui", "window_state", state)
            
        except Exception as e:
            self.logger.warning(f"Erreur sauvegarde géométrie: {e}")
    
    def new_project(self):
        """Crée un nouveau projet"""
        # TODO: Implémenter création nouveau projet
        self.status_bar.showMessage("Nouveau projet - Fonctionnalité en développement")
    
    def open_project(self):
        """Ouvre un projet existant"""
        # TODO: Implémenter ouverture projet
        self.status_bar.showMessage("Ouvrir projet - Fonctionnalité en développement")
    
    def show_about(self):
        """Affiche la boîte À propos"""
        about_text = """
        <h2>AIMER PRO</h2>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>Développé par:</b> KairosForge</p>
        <p><b>Description:</b> Application révolutionnaire de détection d'objets avec IA collaborative</p>
        <br>
        <p><b>Fonctionnalités:</b></p>
        <ul>
        <li>Dashboard système avec monitoring temps réel</li>
        <li>Détection d'objets YOLO avancée</li>
        <li>Apprentissage collaboratif intelligent</li>
        <li>Interface professionnelle moderne</li>
        </ul>
        <br>
        <p><i>© 2025 KairosForge - Tous droits réservés</i></p>
        """
        
        QMessageBox.about(self, "À propos d'AIMER PRO", about_text)
    
    def show_license_info(self):
        """Affiche les informations de licence"""
        license_info = self.license_manager.get_license_info()
        
        info_text = f"""
        <h3>Informations de Licence</h3>
        <p><b>Type:</b> {license_info['license_type'].title()}</p>
        <p><b>Statut:</b> {license_info['status'].title()}</p>
        <p><b>Expiration:</b> {license_info['expiry_date']}</p>
        <p><b>Jours restants:</b> {license_info['days_remaining']}</p>
        <br>
        <p><i>Pour renouveler votre licence, contactez KairosForge</i></p>
        """
        
        QMessageBox.information(self, "Licence AIMER PRO", info_text)
    
    def get_current_module(self) -> str:
        """Retourne le module actuellement affiché"""
        return self.current_module
    
    def get_module_widget(self, module_name: str) -> Optional[QWidget]:
        """Retourne le widget d'un module"""
        return self.modules.get(module_name)
    
    def closeEvent(self, event):
        """Gère la fermeture de la fenêtre"""
        try:
            # Sauvegarder géométrie
            self.save_geometry()
            
            # Sauvegarder paramètres
            self.settings_manager.save_settings()
            
            # Nettoyer modules
            for module in self.modules.values():
                if hasattr(module, 'cleanup'):
                    module.cleanup()
            
            self.logger.info("Fenêtre principale fermée")
            event.accept()
            
        except Exception as e:
            self.logger.error(f"Erreur fermeture fenêtre: {e}")
            event.accept()

def create_main_window(settings_manager, theme_manager, license_manager) -> MainWindow:
    """Factory pour créer la fenêtre principale"""
    return MainWindow(settings_manager, theme_manager, license_manager)
