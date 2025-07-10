#!/usr/bin/env python3
"""
Test simple pour identifier le problème d'import
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent))

print("Test des imports...")

try:
    from core.detector import SmartDetector
    print("✅ SmartDetector importé")
except Exception as e:
    print(f"❌ SmartDetector: {e}")

try:
    from core.config import ConfigManager
    print("✅ ConfigManager importé")
except Exception as e:
    print(f"❌ ConfigManager: {e}")

try:
    from core.logger import Logger
    print("✅ Logger importé")
except Exception as e:
    print(f"❌ Logger: {e}")

try:
    from core.dataset_manager import DatasetManager
    print("✅ DatasetManager importé")
except Exception as e:
    print(f"❌ DatasetManager: {e}")

print("Test import de la classe AimerWebServer...")

try:
    from ui.web_interface.server import AimerWebServer
    print("✅ AimerWebServer importé avec succès!")
    server = AimerWebServer()
    print("✅ Instance AimerWebServer créée avec succès!")
except Exception as e:
    print(f"❌ AimerWebServer: {e}")
    import traceback
    traceback.print_exc()
