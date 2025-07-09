# 🎯 Système de Visée Intelligent

Un système de détection d'objets en temps réel utilisant YOLO v8 avec interface interactive pour l'automatisation d'actions basées sur la vision par ordinateur.

## 📋 Fonctionnalités

- **Détection d'objets en temps réel** sur l'écran avec YOLO v8
- **Interface graphique interactive** avec vue en temps réel des détections
- **Configuration de zones de surveillance** personnalisées
- **Actions automatiques** (clic, double-clic, évitement) basées sur les détections
- **Système de logs** en temps réel
- **Configuration sauvegardable** (seuils de confiance, classes ciblées, etc.)

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- Windows 10/11 (testé)

### Installation des dépendances

1. Clonez le projet :
```bash
git clone <votre-repo>
cd Aimer
```

2. Créez un environnement virtuel :
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## 🎮 Utilisation

### Lancement de l'application

```bash
# Activez l'environnement virtuel
.venv\Scripts\activate

# Lancez l'interface interactive
python launcher_interactive.py
```

### Interface principale

L'application offre plusieurs fonctionnalités :

1. **🎯 DÉMARRER LA DÉTECTION** - Lance la détection continue
2. **📷 CAPTURE & ANALYSE** - Analyse ponctuelle de l'écran
3. **🎯 CONFIGURER ZONES** - Définit des zones de surveillance
4. **⚡ CONFIGURER ACTIONS** - Configure les actions automatiques

### Configuration

- **Seuil de confiance** : Ajustez la sensibilité de détection (10-90%)
- **Classes ciblées** : Spécifiez les objets à détecter (person, head, body, etc.)
- **Actions automatiques** : Configurez les réponses aux détections

## 📁 Structure du projet

```
Aimer/
├── launcher_interactive.py    # Point d'entrée principal
├── requirements.txt          # Dépendances Python
├── aiming_config.json       # Configuration utilisateur
├── yolov8n.pt              # Modèle YOLO
├── ui/                     # Interface utilisateur
│   ├── main_interactive.py # Interface principale
│   ├── annotation_ui.py    # Interface d'annotation
│   └── overlay.py          # Overlay graphique
├── detection/              # Système de détection
│   └── yolo_detector.py    # Détecteur YOLO
├── utils/                  # Utilitaires
│   └── screen_capture.py   # Capture d'écran
└── database/              # Gestion des données
    └── db_manager.py       # Gestionnaire de base de données
```

## ⚙️ Configuration avancée

### Classes d'objets supportées

Le système peut détecter 80+ classes d'objets COCO, incluant :
- `person` - Personnes
- `head` - Têtes (avec modèles personnalisés)
- `body` - Corps
- `bottle`, `cup` - Objets du quotidien
- Et bien d'autres...

### Actions automatiques

- **click_center** : Clic au centre de l'objet détecté
- **double_click** : Double-clic sur l'objet
- **right_click** : Clic droit sur l'objet
- **move_away** : Déplace la souris loin de l'objet

## 🔧 Développement

### Architecture technique

- **Frontend** : Tkinter (interface graphique)
- **Détection** : YOLO v8 (Ultralytics)
- **Vision** : OpenCV
- **Automatisation** : PyAutoGUI
- **Threading** : Détection non-bloquante

### Contribution

1. Forkez le projet
2. Créez une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## ⚠️ Avertissements

- **Usage responsable** : Ce logiciel est destiné à des fins éducatives et de développement
- **Respect des ToS** : Assurez-vous de respecter les conditions d'utilisation des applications tierces
- **Sécurité** : Les actions automatiques peuvent affecter votre système

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Pour toute question ou problème :
1. Vérifiez que toutes les dépendances sont installées
2. Consultez les logs en temps réel dans l'interface
3. Ouvrez une issue sur GitHub

---

**Développé avec ❤️ pour la communauté de vision par ordinateur**
