#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lanceur pour la version interactive du Système de Visée
"""

import sys
import os
from pathlib import Path

def main():
    """Lance l'application interactive"""
    print("🎯 Système de Visée Intelligent - Mode Interactif")
    print("=" * 50)
    
    # Ajouter le répertoire racine au path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    try:
        from ui.main_interactive import InteractiveAimingSystem
        
        print("🚀 Lancement de l'interface interactive...")
        print("📋 Fonctionnalités disponibles:")
        print("   • Vue en temps réel des détections")
        print("   • Configuration des zones de surveillance")
        print("   • Actions automatiques personnalisables")
        print("   • Logs détaillés en temps réel")
        print()
        
        app = InteractiveAimingSystem()
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
