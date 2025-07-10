#!/bin/bash
# Script de démarrage pour GitHub Codespaces
# Lance automatiquement l'auto-setup d'AIMER

echo "🚀 Démarrage d'AIMER PRO dans GitHub Codespaces..."
echo "=================================================="

# Afficher les informations de l'environnement
echo "📍 Répertoire de travail: $(pwd)"
echo "🐍 Version Python: $(python --version)"
echo "💾 Espace disque disponible: $(df -h . | tail -1 | awk '{print $4}')"

# Lancer l'auto-setup AIMER
echo ""
echo "🔧 Lancement de l'auto-setup AIMER..."
python main.py --auto-fix

# Si l'auto-setup réussit, proposer de lancer l'interface web
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Auto-setup terminé avec succès !"
    echo ""
    echo "🌐 Options disponibles :"
    echo "  1. Interface graphique: python main.py"
    echo "  2. Interface web: python launch_web.py"
    echo "  3. CLI détection: python main.py --cli --detect image.jpg"
    echo ""
    echo "💡 L'interface web sera accessible sur le port 5000"
    echo "   (GitHub Codespaces ouvrira automatiquement le navigateur)"
else
    echo ""
    echo "❌ Erreur lors de l'auto-setup. Consultez les logs ci-dessus."
    echo "💡 Vous pouvez réessayer avec: python main.py --auto-fix"
fi
