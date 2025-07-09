#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test AIMER PRO Commercial
© 2025 KairosForge - Tous droits réservés

Script de test pour l'application commerciale
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Teste les imports de base"""
    print("🔍 Test des imports...")
    
    try:
        # Ajouter le path
        sys.path.insert(0, str(Path(__file__).parent / "kairosforge"))
        
        # Test imports core
        from kairosforge.core.application import KairosForgeApplication
        from kairosforge.core.license_manager import LicenseManager
        from kairosforge.core.settings_manager import SettingsManager
        print("✅ Imports core OK")
        
        # Test imports UI
        from kairosforge.ui.main_window import MainWindow
        from kairosforge.ui.sidebar_navigation import SidebarNavigation
        from kairosforge.ui.theme_manager import ThemeManager
        print("✅ Imports UI OK")
        
        # Test imports modules
        from kairosforge.modules.dashboard.dashboard_widget import DashboardWidget
        from kairosforge.modules.detection.detection_widget import DetectionWidget
        from kairosforge.modules.learning.learning_widget import LearningWidget
        from kairosforge.modules.settings.settings_widget import SettingsWidget
        print("✅ Imports modules OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_dependencies():
    """Teste les dépendances PyQt6"""
    print("\n🔍 Test des dépendances...")
    
    try:
        import PyQt6
        print("✅ PyQt6 disponible")
        
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont
        print("✅ PyQt6 widgets OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ PyQt6 manquant: {e}")
        print("💡 Installez avec: pip install PyQt6")
        return False

def main():
    """Test principal"""
    print("🚀 Test AIMER PRO Commercial")
    print("=" * 40)
    
    # Test dépendances
    if not test_dependencies():
        print("\n❌ Tests échoués - Dépendances manquantes")
        return False
    
    # Test imports
    if not test_imports():
        print("\n❌ Tests échoués - Problème imports")
        return False
    
    print("\n✅ Tous les tests passés !")
    print("🎉 AIMER PRO Commercial prêt à être lancé !")
    print("\n💡 Lancez avec: python aimer_pro_commercial.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
