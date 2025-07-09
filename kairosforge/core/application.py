#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Application Principale PyQt6
© 2025 KairosForge - Tous droits réservés

Application commerciale Single Window avec architecture MVC
"""

import sys
import os
from pathlib import Path
from typing import Optional
import logging

from PyQt6.QtWidgets import QApplication, QMainWindow, QSplashScreen
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap, QIcon, QFont

# Imports locaux
from .license_manager import LicenseManager
from .settings_manager import SettingsManager
from ..ui.main_window import MainWindow
from ..ui.theme_manager import ThemeManager

class KairosForgeApplication(QApplication):
    """
    Application principale AIMER PRO
    Gère l'initialisation, la licence, et le cycle de vie
    """
    
    # Signaux
    license_validated = pyqtSignal(bool)
    initialization_complete = pyqtSignal()
    
    def __init__(self, argv):
        super().__init__(argv)
        
        # Configuration application
        self.setApplicationName("AIMER PRO")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("KairosForge")
        self.setOrganizationDomain("kairosforge.com")
        
        # Variables d'instance
        self.main_window: Optional[MainWindow] = None
        self.splash_screen: Optional[QSplashScreen] = None
        self.license_manager: Optional[LicenseManager] = None
        self.settings_manager: Optional[SettingsManager] = None
        self.theme_manager: Optional[ThemeManager] = None
        
        # Configuration logging
        self.setup_logging()
        
        # Configuration interface
        self.setup_ui_properties()
        
        # Démarrage
        self.initialize_application()
    
    def setup_logging(self):
        """Configure le système de logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "aimer_pro.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("KairosForgeApp")
        self.logger.info("Démarrage AIMER PRO")
    
    def setup_ui_properties(self):
        """Configure les propriétés UI globales"""
        # Police système
        font = QFont("Inter", 10)
        font.setStyleHint(QFont.StyleHint.SansSerif)
        self.setFont(font)
        
        # Style global
        self.setStyle("Fusion")
        
        # Configuration haute résolution (PyQt6 compatible)
        try:
            self.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        except AttributeError:
            # PyQt6 gère automatiquement le high DPI
            pass
        
        try:
            self.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        except AttributeError:
            # PyQt6 gère automatiquement les pixmaps high DPI
            pass
    
    def initialize_application(self):
        """Initialise l'application étape par étape"""
        self.logger.info("Initialisation de l'application...")
        
        # Initialisation directe (sans splash screen pour debug)
        self.initialize_components()
    
    def show_splash_screen(self):
        """Affiche l'écran de démarrage"""
        try:
            # Créer un pixmap pour le splash (temporaire - sera remplacé par logo)
            pixmap = QPixmap(600, 400)
            pixmap.fill(Qt.GlobalColor.black)
            
            self.splash_screen = QSplashScreen(pixmap)
            self.splash_screen.setWindowFlags(
                Qt.WindowType.WindowStaysOnTopHint | 
                Qt.WindowType.FramelessWindowHint
            )
            
            # Message de démarrage
            self.splash_screen.showMessage(
                "🎯 AIMER PRO - KairosForge\nInitialisation...",
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
                Qt.GlobalColor.white
            )
            
            self.splash_screen.show()
            self.processEvents()
            
        except Exception as e:
            self.logger.error(f"Erreur splash screen: {e}")
    
    def initialize_components(self):
        """Initialise les composants principaux"""
        try:
            # 1. Gestionnaire de paramètres
            self.logger.info("Chargement des paramètres...")
            self.settings_manager = SettingsManager()
            
            # 2. Gestionnaire de thèmes
            self.logger.info("Configuration des thèmes...")
            self.theme_manager = ThemeManager(self)
            
            # 3. Gestionnaire de licence
            self.logger.info("Validation de la licence...")
            self.license_manager = LicenseManager()
            
            # 4. Validation licence
            if not self.validate_license():
                self.logger.error("Licence invalide")
                self.quit()
                return
            
            # 5. Fenêtre principale
            self.logger.info("Chargement de l'interface...")
            self.create_main_window()
            
            # 6. Finalisation
            self.finalize_initialization()
            
        except Exception as e:
            self.logger.error(f"Erreur initialisation: {e}")
            self.quit()
    
    def update_splash_message(self, message: str):
        """Met à jour le message du splash screen"""
        if self.splash_screen and not self.splash_screen.isHidden():
            try:
                self.splash_screen.showMessage(
                    f"🎯 AIMER PRO - KairosForge\n{message}",
                    Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
                    Qt.GlobalColor.white
                )
                self.processEvents()
            except Exception as e:
                self.logger.debug(f"Erreur mise à jour splash: {e}")
    
    def validate_license(self) -> bool:
        """Valide la licence utilisateur"""
        try:
            if not self.license_manager:
                return False
            
            # Validation licence (implémentation basique pour l'instant)
            is_valid = self.license_manager.validate_license()
            
            if is_valid:
                self.logger.info("✅ Licence validée")
                self.license_validated.emit(True)
            else:
                self.logger.warning("❌ Licence invalide")
                self.license_validated.emit(False)
            
            return is_valid
            
        except Exception as e:
            self.logger.error(f"Erreur validation licence: {e}")
            return False
    
    def create_main_window(self):
        """Crée la fenêtre principale"""
        try:
            self.logger.info("Création MainWindow...")
            self.main_window = MainWindow(
                settings_manager=self.settings_manager,
                theme_manager=self.theme_manager,
                license_manager=self.license_manager
            )
            
            self.logger.info("Configuration fenêtre...")
            # Configuration fenêtre
            self.main_window.setWindowTitle("AIMER PRO - KairosForge")
            self.main_window.setMinimumSize(1280, 720)
            
            # Icône application (temporaire)
            # self.main_window.setWindowIcon(QIcon("assets/icon.ico"))
            
            self.logger.info("Fenêtre principale créée avec succès")
            
        except Exception as e:
            import traceback
            self.logger.error(f"Erreur création fenêtre: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def finalize_initialization(self):
        """Finalise l'initialisation"""
        try:
            # Fermer splash screen AVANT d'afficher la fenêtre principale
            if self.splash_screen:
                self.splash_screen.close()
                self.splash_screen = None
            
            # Petit délai pour s'assurer que le splash est fermé
            self.processEvents()
            
            # Afficher fenêtre principale
            if self.main_window:
                self.main_window.show()
                self.main_window.raise_()
                self.main_window.activateWindow()
            
            # Signal d'initialisation complète
            self.initialization_complete.emit()
            
            self.logger.info("✅ Initialisation terminée")
            
        except Exception as e:
            self.logger.error(f"Erreur finalisation: {e}")
    
    def get_main_window(self) -> Optional[MainWindow]:
        """Retourne la fenêtre principale"""
        return self.main_window
    
    def get_settings_manager(self) -> Optional[SettingsManager]:
        """Retourne le gestionnaire de paramètres"""
        return self.settings_manager
    
    def get_theme_manager(self) -> Optional[ThemeManager]:
        """Retourne le gestionnaire de thèmes"""
        return self.theme_manager
    
    def get_license_manager(self) -> Optional[LicenseManager]:
        """Retourne le gestionnaire de licence"""
        return self.license_manager
    
    def closeEvent(self, event):
        """Gère la fermeture de l'application"""
        self.logger.info("Fermeture de l'application")
        
        # Sauvegarder les paramètres
        if self.settings_manager:
            self.settings_manager.save_settings()
        
        # Nettoyage
        if self.main_window:
            self.main_window.close()
        
        event.accept()

def create_application(argv) -> KairosForgeApplication:
    """Factory pour créer l'application"""
    return KairosForgeApplication(argv)

def main():
    """Point d'entrée principal"""
    try:
        # Créer application
        app = create_application(sys.argv)
        
        # Lancer boucle événements
        exit_code = app.exec()
        
        # Nettoyage final
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"Erreur fatale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
