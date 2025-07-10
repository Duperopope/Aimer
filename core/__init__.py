#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Core Module
© 2025 - Licence Apache 2.0

Module principal contenant le moteur Detectron2 et les utilitaires
"""

from .detector import UniversalDetector
from .config import ConfigManager
from .logger import Logger

__version__ = "1.0.0"
__all__ = ["UniversalDetector", "ConfigManager", "Logger"]
