#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO COMMERCIAL - Launcher Principal
© 2025 KairosForge - Tous droits réservés

Application commerciale Single Window PyQt6
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire kairosforge au path
sys.path.insert(0, str(Path(__file__).parent / "kairosforge"))

def main():
    """Point d'entrée principal AIMER PRO Commercial"""
    try:
        # Import de l'application
        from kairosforge.core.application import create_application
        
        # Créer et lancer l'application
        app = create_application(sys.argv)
        
        # Lancer la boucle d'événements
        exit_code = app.exec()
        
        # Sortie propre
        sys.exit(exit_code)
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("💡 Installez les dépendances avec: pip install -r requirements-commercial.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
