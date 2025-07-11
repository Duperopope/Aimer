#!/usr/bin/env python3
"""
🚀 AIMER Monitoring Quick Start
Démarrage rapide du système de monitoring et dashboard
"""

import subprocess
import sys
import time
from pathlib import Path


def main():
    print("🚀 AIMER Monitoring System - Démarrage Rapide")
    print("=" * 50)
    
    base_path = Path(__file__).parent
    
    print("🔧 Vérification des dépendances...")
    
    # Vérifier si les modules requis sont installés
    required_modules = ['rich', 'yaml']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            missing_modules.append(module if module != 'yaml' else 'pyyaml')
            print(f"   ❌ {module}")
    
    # Installer les modules manquants
    if missing_modules:
        print(f"\n📦 Installation des modules manquants: {', '.join(missing_modules)}")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing_modules, 
                         check=True, capture_output=True)
            print("   ✅ Modules installés avec succès")
        except subprocess.CalledProcessError:
            print("   ❌ Erreur lors de l'installation")
            return
    
    print("\n🔍 Lancement du système de monitoring...")
    
    # Options disponibles
    print("\nOptions disponibles:")
    print("1. 📊 Dashboard temps réel")
    print("2. 🔍 Monitoring en arrière-plan")
    print("3. 🧠 Correction automatique")
    print("4. 🔧 Monitoring VS Code")
    print("5. 📋 Guide complet")
    print("0. Quitter")
    
    try:
        choice = input("\nVotre choix (1-5, 0 pour quitter): ").strip()
        
        if choice == "1":
            print("\n📊 Lancement du dashboard...")
            subprocess.run([sys.executable, "error_dashboard.py"])
            
        elif choice == "2":
            print("\n🔍 Démarrage du monitoring...")
            subprocess.Popen([sys.executable, "error_monitor.py"])
            print("   ✅ Monitoring démarré en arrière-plan")
            print("   💡 Utilisez le dashboard (option 1) pour voir l'état")
            
        elif choice == "3":
            print("\n🧠 Lancement de la correction automatique...")
            subprocess.run([sys.executable, "smart_error_fixer.py"])
            
        elif choice == "4":
            print("\n🔧 Lancement du monitoring VS Code...")
            subprocess.run([sys.executable, "vscode_error_monitor.py"])
            
        elif choice == "5":
            print("\n📋 Ouverture du guide complet...")
            guide_file = base_path / "MONITORING_SYSTEM_GUIDE.md"
            if guide_file.exists():
                try:
                    subprocess.run(["code", str(guide_file)], check=True)
                    print("   ✅ Guide ouvert dans VS Code")
                except (subprocess.CalledProcessError, FileNotFoundError):
                    # Si code n'est pas disponible, afficher le contenu
                    print("   📖 Contenu du guide:")
                    print("   💡 Consultez MONITORING_SYSTEM_GUIDE.md")
                    print("   📁 Ou utilisez VS Code: Ctrl+Shift+P → 'AIMER: View Monitoring Guide'")
            else:
                print("   ❌ Guide non trouvé")
                
        elif choice == "0":
            print("\n👋 Au revoir!")
            
        else:
            print("\n❌ Choix invalide")
            
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")


if __name__ == "__main__":
    main()
