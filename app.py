#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Application Web pour Déploiement
© 2025 - Licence Apache 2.0

Point d'entrée principal pour le déploiement web
"""

import os
from ui.web_interface.server_simple import AimerWebServerSimple

# Configuration pour le déploiement
host = "0.0.0.0"  # Accepter toutes les connexions
port = int(os.environ.get("PORT", 5000))  # Port dynamique pour Render/Railway

# Créer le serveur
server = AimerWebServerSimple(host=host, port=port)

# Instance Flask pour gunicorn
app = server.get_app()

def main():
    """Point d'entrée principal pour le test local"""
    print("🚀 AIMER PRO - Déploiement Web")
    print(f"🌐 Host: {host}")
    print(f"📡 Port: {port}")
    print("🎯 Mode: Production Web")
    
    # Lancement du serveur en mode développement
    server.run()

if __name__ == "__main__":
    main()
