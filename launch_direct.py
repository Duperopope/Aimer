#!/usr/bin/env python3
"""
AIMER PRO - Lanceur Direct Simplifié
Test direct du serveur sans import complexe
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                🎯 AIMER PRO - TEST DIRECT                   ║
║                   Lanceur Simplifié                         ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("🚀 Lancement direct du serveur...")
    
    # Changer vers le bon répertoire
    script_dir = Path(__file__).parent
    server_script = script_dir / "ui" / "web_interface" / "server.py"
    
    if not server_script.exists():
        print(f"❌ Serveur non trouvé: {server_script}")
        return False
    
    print(f"📍 Script serveur: {server_script}")
    print("🌐 Interface web: http://localhost:5000")
    print("\n🚀 Démarrage...")
    
    try:
        # Lancer le serveur directement
        subprocess.run([sys.executable, str(server_script), "--debug"], 
                      cwd=str(script_dir))
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
