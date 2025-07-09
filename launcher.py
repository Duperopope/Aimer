#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lanceur simplifié pour le Système de Visée Intelligent
"""

import sys
import os
from pathlib import Path

def main():
    """Lance l'application avec vérifications"""
    print("🚀 Système de Visée Intelligent - Lanceur")
    print("=" * 50)
    
    # Vérifier Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requis")
        print(f"Version actuelle: {sys.version}")
        input("Appuyez sur Entrée pour quitter...")
        return
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Vérifier les fichiers
    project_root = Path(__file__).parent
    ui_file = project_root / "ui" / "main_friendly.py"
    
    if not ui_file.exists():
        print("❌ Fichier main_friendly.py manquant")
        input("Appuyez sur Entrée pour quitter...")
        return
    
    print("✅ Fichiers trouvés")
    
    # Ajouter au path
    sys.path.insert(0, str(project_root))
    
    try:
        # Importer et lancer
        from ui.main_friendly import UserFriendlyAimingSystem
        
        print("🎯 Lancement de l'interface...")
        app = UserFriendlyAimingSystem()
        app.run()
        
    except ImportError as e:
        print(f"❌ Erreur d'importation: {e}")
        print("\n💡 Solution:")
        print("1. Activez votre environnement virtuel")
        print("2. Installez: pip install ultralytics opencv-python pillow numpy pyautogui")
        input("\nAppuyez sur Entrée pour quitter...")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        input("\nAppuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    main()
