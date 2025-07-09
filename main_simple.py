# -*- coding: utf-8 -*-
"""
🎯 SYSTÈME DE VISÉE INTELLIGENT
Lanceur principal - Version Débutant
"""

import sys
import os
from pathlib import Path
import traceback

def main():
    """Point d'entrée principal"""
    print("🚀 Lancement du Système de Visée Intelligent...")
    print("📱 Interface utilisateur conviviale")
    print("🐍 Python 3.13 + YOLO Ultralytics")
    print("=" * 50)
    
    # Vérifier l'environnement virtuel
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Environnement virtuel activé")
    else:
        print("⚠️  Environnement virtuel non détecté")
    
    # Ajouter le répertoire racine au path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    print("🎯 Initialisation de l'interface...")
    
    try:
        # Import après avoir ajouté le path
        from ui.main_friendly import UserFriendlyAimingSystem
        
        # Lancer l'application
        app = UserFriendlyAimingSystem()
        app.run()
        
        print("👋 Merci d'avoir utilisé le Système de Visée Intelligent!")
        
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        print(f"📋 Type d'erreur: {type(e).__name__}")
        print("\n🔧 Solution:")
        print("1. Activez votre environnement virtuel:")
        print(r"   .venv\Scripts\Activate.ps1")  # Raw string pour éviter l'erreur
        print("2. Installez les dépendances:")
        print("   pip install ultralytics opencv-python pillow numpy pyautogui")
        print("3. Relancez l'application")
        print("\n📋 Trace complète:")
        traceback.print_exc()
        input("\nAppuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    main()
