#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dataset Manager Launcher - Lanceur du gestionnaire de datasets professionnel
Point d'entrée principal pour le système de gestion de datasets YOLO
"""

import sys
import os
import logging
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent))

def setup_logging():
    """Configure le système de logging"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)8s | %(name)20s | %(message)s',
        handlers=[
            logging.FileHandler('logs/dataset_manager_launcher.log'),
            logging.StreamHandler()
        ]
    )

def check_dependencies():
    """Vérifie les dépendances requises"""
    required_modules = [
        'tkinter',
        'cv2',
        'numpy',
        'PIL',
        'psutil',
        'requests',
        'sqlite3'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("❌ Modules manquants:")
        for module in missing_modules:
            print(f"   - {module}")
        print("\n💡 Installez les dépendances avec:")
        print("   pip install opencv-python pillow psutil requests")
        return False
    
    return True

def main():
    """Fonction principale du launcher"""
    print("🎯 YOLO Dataset Manager Pro - Launcher")
    print("=" * 50)
    
    # Configuration du logging
    setup_logging()
    logger = logging.getLogger("DatasetManagerLauncher")
    
    try:
        # Vérification des dépendances
        print("🔍 Vérification des dépendances...")
        if not check_dependencies():
            input("\nAppuyez sur Entrée pour quitter...")
            return
        
        print("✅ Toutes les dépendances sont installées")
        
        # Import et lancement de l'interface
        print("🚀 Lancement de l'interface...")
        
        from ui.modern_dataset_interface import ModernDatasetInterface
        
        # Créer et lancer l'application
        app = ModernDatasetInterface()
        
        print("✅ Interface chargée avec succès")
        print("📱 Ouverture de l'interface utilisateur...")
        
        # Lancer l'interface
        app.run()
        
    except ImportError as e:
        logger.error(f"Erreur d'import: {e}")
        print(f"❌ Erreur d'import: {e}")
        print("💡 Vérifiez que tous les modules sont installés")
        
    except Exception as e:
        logger.error(f"Erreur lors du lancement: {e}")
        print(f"❌ Erreur: {e}")
        
    finally:
        print("\n👋 Fermeture du Dataset Manager")
        input("Appuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    main()
