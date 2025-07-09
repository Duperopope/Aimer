#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Gestionnaire de Thèmes
© 2025 KairosForge - Tous droits réservés

Système de thèmes professionnel avec QSS
"""

import os
from pathlib import Path
from typing import Dict, Optional
import logging
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor

class ThemeManager(QObject):
    """
    Gestionnaire de thèmes professionnel
    Gère les thèmes sombre/clair avec QSS
    """
    
    # Signaux
    theme_changed = pyqtSignal(str)  # Émis quand le thème change
    
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.logger = logging.getLogger("ThemeManager")
        
        # Thème actuel
        self.current_theme = "dark"
        
        # Définition des couleurs par thème
        self.themes = {
            "dark": {
                "primary": "#1e40af",
                "primary_hover": "#1d4ed8",
                "secondary": "#64748b",
                "accent": "#3b82f6",
                "success": "#10b981",
                "warning": "#f59e0b",
                "error": "#ef4444",
                "background": "#0f172a",
                "surface": "#1e293b",
                "surface_hover": "#334155",
                "card": "#1e293b",
                "border": "#334155",
                "text_primary": "#f1f5f9",
                "text_secondary": "#94a3b8",
                "text_muted": "#64748b",
                "sidebar_bg": "#1e293b",
                "sidebar_hover": "#334155",
                "sidebar_active": "#1e40af",
                "content_bg": "#0f172a",
                "input_bg": "#334155",
                "input_border": "#475569",
                "button_bg": "#1e40af",
                "button_hover": "#1d4ed8",
                "scrollbar": "#475569",
                "scrollbar_hover": "#64748b"
            },
            
            "light": {
                "primary": "#1e40af",
                "primary_hover": "#1d4ed8",
                "secondary": "#64748b",
                "accent": "#3b82f6",
                "success": "#10b981",
                "warning": "#f59e0b",
                "error": "#ef4444",
                "background": "#ffffff",
                "surface": "#f8fafc",
                "surface_hover": "#f1f5f9",
                "card": "#ffffff",
                "border": "#e2e8f0",
                "text_primary": "#0f172a",
                "text_secondary": "#475569",
                "text_muted": "#64748b",
                "sidebar_bg": "#f8fafc",
                "sidebar_hover": "#f1f5f9",
                "sidebar_active": "#1e40af",
                "content_bg": "#ffffff",
                "input_bg": "#ffffff",
                "input_border": "#d1d5db",
                "button_bg": "#1e40af",
                "button_hover": "#1d4ed8",
                "scrollbar": "#d1d5db",
                "scrollbar_hover": "#9ca3af"
            }
        }
        
        self.logger.info("Gestionnaire de thèmes initialisé")
    
    def get_theme_colors(self, theme_name: str = None) -> Dict[str, str]:
        """Retourne les couleurs du thème spécifié"""
        if theme_name is None:
            theme_name = self.current_theme
        
        return self.themes.get(theme_name, self.themes["dark"])
    
    def set_theme(self, theme_name: str):
        """Applique un thème à l'application"""
        if theme_name not in self.themes:
            self.logger.warning(f"Thème inconnu: {theme_name}")
            return
        
        self.current_theme = theme_name
        colors = self.themes[theme_name]
        
        # Générer le QSS
        qss = self._generate_qss(colors)
        
        # Appliquer le style
        self.app.setStyleSheet(qss)
        
        # Émettre signal
        self.theme_changed.emit(theme_name)
        
        self.logger.info(f"Thème appliqué: {theme_name}")
    
    def _generate_qss(self, colors: Dict[str, str]) -> str:
        """Génère le QSS complet pour le thème"""
        
        qss = f"""
        /* ===== STYLE GLOBAL ===== */
        QWidget {{
            background-color: {colors['background']};
            color: {colors['text_primary']};
            font-family: "Inter", "Segoe UI", sans-serif;
            font-size: 10pt;
        }}
        
        /* ===== FENÊTRE PRINCIPALE ===== */
        QMainWindow {{
            background-color: {colors['background']};
            border: none;
        }}
        
        /* ===== SIDEBAR NAVIGATION ===== */
        QFrame#sidebar {{
            background-color: {colors['sidebar_bg']};
            border-right: 1px solid {colors['border']};
            min-width: 240px;
            max-width: 240px;
        }}
        
        /* ===== BOUTONS SIDEBAR ===== */
        QPushButton#sidebar_button {{
            background-color: transparent;
            color: {colors['text_secondary']};
            border: none;
            padding: 12px 16px;
            text-align: left;
            font-size: 11pt;
            font-weight: 500;
            border-radius: 6px;
            margin: 2px 8px;
        }}
        
        QPushButton#sidebar_button:hover {{
            background-color: {colors['sidebar_hover']};
            color: {colors['text_primary']};
        }}
        
        QPushButton#sidebar_button:pressed {{
            background-color: {colors['sidebar_active']};
            color: white;
        }}
        
        QPushButton#sidebar_button:checked {{
            background-color: {colors['sidebar_active']};
            color: white;
            font-weight: 600;
        }}
        
        /* ===== ZONE CONTENU ===== */
        QFrame#content_area {{
            background-color: {colors['content_bg']};
            border: none;
            border-radius: 8px;
            margin: 8px;
        }}
        
        /* ===== CARTES ET PANELS ===== */
        QFrame#card {{
            background-color: {colors['card']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 16px;
        }}
        
        QGroupBox {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            font-weight: 600;
            font-size: 11pt;
            color: {colors['text_primary']};
            padding-top: 16px;
            margin-top: 8px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px 0 8px;
            color: {colors['text_primary']};
            background-color: {colors['surface']};
        }}
        
        /* ===== BOUTONS PRINCIPAUX ===== */
        QPushButton {{
            background-color: {colors['button_bg']};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            font-size: 10pt;
        }}
        
        QPushButton:hover {{
            background-color: {colors['button_hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['primary_hover']};
        }}
        
        QPushButton:disabled {{
            background-color: {colors['secondary']};
            color: {colors['text_muted']};
        }}
        
        /* ===== BOUTONS SECONDAIRES ===== */
        QPushButton#secondary_button {{
            background-color: transparent;
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
        }}
        
        QPushButton#secondary_button:hover {{
            background-color: {colors['surface_hover']};
            border-color: {colors['primary']};
        }}
        
        /* ===== BOUTONS DANGER ===== */
        QPushButton#danger_button {{
            background-color: {colors['error']};
            color: white;
        }}
        
        QPushButton#danger_button:hover {{
            background-color: #dc2626;
        }}
        
        /* ===== BOUTONS SUCCESS ===== */
        QPushButton#success_button {{
            background-color: {colors['success']};
            color: white;
        }}
        
        QPushButton#success_button:hover {{
            background-color: #059669;
        }}
        
        /* ===== CHAMPS DE SAISIE ===== */
        QLineEdit {{
            background-color: {colors['input_bg']};
            border: 1px solid {colors['input_border']};
            border-radius: 6px;
            padding: 8px 12px;
            color: {colors['text_primary']};
            font-size: 10pt;
        }}
        
        QLineEdit:focus {{
            border-color: {colors['primary']};
            outline: none;
        }}
        
        QLineEdit:disabled {{
            background-color: {colors['surface']};
            color: {colors['text_muted']};
        }}
        
        /* ===== ZONES DE TEXTE ===== */
        QTextEdit {{
            background-color: {colors['input_bg']};
            border: 1px solid {colors['input_border']};
            border-radius: 6px;
            padding: 8px;
            color: {colors['text_primary']};
            font-size: 10pt;
        }}
        
        QTextEdit:focus {{
            border-color: {colors['primary']};
        }}
        
        /* ===== COMBOBOX ===== */
        QComboBox {{
            background-color: {colors['input_bg']};
            border: 1px solid {colors['input_border']};
            border-radius: 6px;
            padding: 8px 12px;
            color: {colors['text_primary']};
            font-size: 10pt;
        }}
        
        QComboBox:hover {{
            border-color: {colors['primary']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid {colors['text_secondary']};
            margin-right: 8px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            color: {colors['text_primary']};
            selection-background-color: {colors['primary']};
        }}
        
        /* ===== SPINBOX ===== */
        QSpinBox, QDoubleSpinBox {{
            background-color: {colors['input_bg']};
            border: 1px solid {colors['input_border']};
            border-radius: 6px;
            padding: 8px 12px;
            color: {colors['text_primary']};
            font-size: 10pt;
        }}
        
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {colors['primary']};
        }}
        
        /* ===== SLIDERS ===== */
        QSlider::groove:horizontal {{
            background-color: {colors['surface']};
            height: 6px;
            border-radius: 3px;
        }}
        
        QSlider::handle:horizontal {{
            background-color: {colors['primary']};
            width: 16px;
            height: 16px;
            border-radius: 8px;
            margin: -5px 0;
        }}
        
        QSlider::handle:horizontal:hover {{
            background-color: {colors['primary_hover']};
        }}
        
        QSlider::sub-page:horizontal {{
            background-color: {colors['primary']};
            border-radius: 3px;
        }}
        
        /* ===== CHECKBOX ===== */
        QCheckBox {{
            color: {colors['text_primary']};
            font-size: 10pt;
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {colors['input_border']};
            border-radius: 3px;
            background-color: {colors['input_bg']};
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {colors['primary']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {colors['primary']};
            border-color: {colors['primary']};
        }}
        
        /* ===== RADIO BUTTON ===== */
        QRadioButton {{
            color: {colors['text_primary']};
            font-size: 10pt;
            spacing: 8px;
        }}
        
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {colors['input_border']};
            border-radius: 8px;
            background-color: {colors['input_bg']};
        }}
        
        QRadioButton::indicator:hover {{
            border-color: {colors['primary']};
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {colors['primary']};
            border-color: {colors['primary']};
        }}
        
        /* ===== PROGRESS BAR ===== */
        QProgressBar {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            text-align: center;
            color: {colors['text_primary']};
            font-weight: 500;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['primary']};
            border-radius: 5px;
        }}
        
        /* ===== SCROLLBAR ===== */
        QScrollBar:vertical {{
            background-color: {colors['surface']};
            width: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors['scrollbar']};
            border-radius: 6px;
            min-height: 20px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors['scrollbar_hover']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background-color: {colors['surface']};
            height: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {colors['scrollbar']};
            border-radius: 6px;
            min-width: 20px;
            margin: 2px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {colors['scrollbar_hover']};
        }}
        
        /* ===== TABLEAUX ===== */
        QTableWidget {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            gridline-color: {colors['border']};
            color: {colors['text_primary']};
        }}
        
        QTableWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {colors['border']};
        }}
        
        QTableWidget::item:selected {{
            background-color: {colors['primary']};
            color: white;
        }}
        
        QHeaderView::section {{
            background-color: {colors['surface_hover']};
            color: {colors['text_primary']};
            padding: 8px;
            border: none;
            border-bottom: 1px solid {colors['border']};
            font-weight: 600;
        }}
        
        /* ===== LISTES ===== */
        QListWidget {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            color: {colors['text_primary']};
        }}
        
        QListWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {colors['border']};
        }}
        
        QListWidget::item:selected {{
            background-color: {colors['primary']};
            color: white;
        }}
        
        QListWidget::item:hover {{
            background-color: {colors['surface_hover']};
        }}
        
        /* ===== TABS ===== */
        QTabWidget::pane {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
        }}
        
        QTabBar::tab {{
            background-color: {colors['surface']};
            color: {colors['text_secondary']};
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['primary']};
            color: white;
        }}
        
        QTabBar::tab:hover {{
            background-color: {colors['surface_hover']};
            color: {colors['text_primary']};
        }}
        
        /* ===== TOOLTIPS ===== */
        QToolTip {{
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 6px 8px;
            font-size: 9pt;
        }}
        
        /* ===== MENUS ===== */
        QMenuBar {{
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            border-bottom: 1px solid {colors['border']};
        }}
        
        QMenuBar::item {{
            padding: 6px 12px;
            background-color: transparent;
        }}
        
        QMenuBar::item:selected {{
            background-color: {colors['surface_hover']};
        }}
        
        QMenu {{
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
        }}
        
        QMenu::item {{
            padding: 6px 12px;
        }}
        
        QMenu::item:selected {{
            background-color: {colors['primary']};
            color: white;
        }}
        
        /* ===== BARRE DE STATUT ===== */
        QStatusBar {{
            background-color: {colors['surface']};
            color: {colors['text_secondary']};
            border-top: 1px solid {colors['border']};
            font-size: 9pt;
        }}
        
        /* ===== SPLITTER ===== */
        QSplitter::handle {{
            background-color: {colors['border']};
        }}
        
        QSplitter::handle:horizontal {{
            width: 2px;
        }}
        
        QSplitter::handle:vertical {{
            height: 2px;
        }}
        
        /* ===== ANIMATIONS ===== */
        * {{
            transition: all 0.2s ease-in-out;
        }}
        """
        
        return qss
    
    def get_current_theme(self) -> str:
        """Retourne le thème actuel"""
        return self.current_theme
    
    def toggle_theme(self):
        """Bascule entre thème sombre et clair"""
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.set_theme(new_theme)
    
    def get_color(self, color_name: str, theme_name: str = None) -> str:
        """Retourne une couleur spécifique du thème"""
        if theme_name is None:
            theme_name = self.current_theme
        
        colors = self.themes.get(theme_name, self.themes["dark"])
        return colors.get(color_name, "#000000")
    
    def create_custom_theme(self, name: str, colors: Dict[str, str]):
        """Crée un thème personnalisé"""
        # Valider les couleurs requises
        required_colors = list(self.themes["dark"].keys())
        for color in required_colors:
            if color not in colors:
                self.logger.error(f"Couleur manquante pour thème {name}: {color}")
                return False
        
        # Ajouter le thème
        self.themes[name] = colors
        self.logger.info(f"Thème personnalisé créé: {name}")
        return True
    
    def get_available_themes(self) -> list:
        """Retourne la liste des thèmes disponibles"""
        return list(self.themes.keys())

def create_theme_manager(app: QApplication) -> ThemeManager:
    """Factory pour créer le gestionnaire de thèmes"""
    return ThemeManager(app)
