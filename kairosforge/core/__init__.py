#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Core Package
© 2025 KairosForge - Tous droits réservés

Package core avec composants fondamentaux
"""

from .application import KairosForgeApplication, create_application
from .license_manager import LicenseManager, create_license_manager
from .settings_manager import SettingsManager, create_settings_manager

__all__ = [
    "KairosForgeApplication",
    "create_application", 
    "LicenseManager",
    "create_license_manager",
    "SettingsManager", 
    "create_settings_manager"
]
