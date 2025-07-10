#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Script de Déploiement Rapide
© 2025 - Licence Apache 2.0

Script pour tester et déployer l'application web rapidement
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Script principal de déploiement"""
    
    print("🚀 AIMER PRO - Script de Déploiement")
    print("=" * 50)
    
    # Vérifier qu'on est dans le bon répertoire
    if not Path("app.py").exists():
        print("❌ Erreur: app.py non trouvé. Exécutez ce script depuis le répertoire AIMER.")
        return
    
    print("✅ Fichiers de déploiement détectés")
    
    # Afficher les options
    print("\n📋 Options disponibles:")
    print("1. 🌐 Test local avec Flask (développement)")
    print("2. 🏭 Test local avec Waitress (production)")
    print("3. 📦 Installer dépendances web")
    print("4. 📖 Afficher guide de déploiement")
    print("5. 🚢 Commit et push vers GitHub")
    
    choice = input("\n👉 Votre choix (1-5): ").strip()
    
    if choice == "1":
        print("\n🌐 Lancement Flask (développement)...")
        os.system("python app.py")
        
    elif choice == "2":
        print("\n🏭 Installation Waitress...")
        os.system("pip install waitress")
        print("\n🏭 Lancement Waitress (production)...")
        print("📍 URL: http://localhost:5000")
        os.system("waitress-serve --host=0.0.0.0 --port=5000 app:app")
        
    elif choice == "3":
        print("\n📦 Installation des dépendances web...")
        os.system("pip install -r requirements_web.txt")
        print("✅ Installation terminée")
        
    elif choice == "4":
        print("\n📖 Guide de Déploiement:")
        print("-" * 30)
        if Path("DEPLOYMENT.md").exists():
            with open("DEPLOYMENT.md", "r", encoding="utf-8") as f:
                print(f.read())
        else:
            print("❌ DEPLOYMENT.md non trouvé")
            
    elif choice == "5":
        print("\n🚢 Commit et push...")
        os.system("git add .")
        commit_msg = input("💬 Message de commit (ou Entrée pour défaut): ")
        if not commit_msg:
            commit_msg = "update: Web deployment ready"
        os.system(f'git commit -m "{commit_msg}"')
        os.system("git push origin main")
        print("✅ Push terminé")
        
    else:
        print("❌ Option invalide")
        
    print("\n🎯 Pour déployer en ligne:")
    print("1. Aller sur https://railway.app")
    print("2. Connecter votre repo GitHub")
    print("3. Déploiement automatique !")

if __name__ == "__main__":
    main()
