# AIMER PRO v0.1.1 — Détection universelle (Windows / CPU stable)

![Version](https://img.shields.io/badge/version-0.1.1-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-green)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Duperopope/Aimer)
[![🌐 Test Web App](https://img.shields.io/badge/🌐%20Test-Web%20App-brightgreen)](https://aimer-pro.up.railway.app)
[![📖 Deploy Guide](https://img.shields.io/badge/📖%20Deploy-Guide-orange)](./DEPLOYMENT.md)

## 🚀 Lancement rapide

### Option 1: Tester en ligne (Nouveau !)
**[🌐 Cliquez ici pour tester l'application web en direct](https://aimer-pro.up.railway.app)**
- Interface web complète dans votre navigateur
- Upload d'images en drag & drop
- Détection en temps réel avec OpenCV
- API REST testable
- Aucune installation requise !

### Option 2: GitHub Codespaces
Cliquez sur le badge "Open in GitHub Codespaces" ci-dessus pour développer AIMER dans votre navigateur !

**Dans Codespaces :**
- L'auto-setup se lance automatiquement au démarrage
- Si ce n'est pas le cas, tapez : `python main.py --auto-fix`
- Pour l'interface web : `python launch_web.py`
- L'interface s'ouvrira automatiquement sur le port 5000

### Option 3: Interface Web Locale
```bash
git clone https://github.com/Duperopope/Aimer.git
cd Aimer
python launch_web.py
```

### Option 4: Installation Classique
```bash
git clone https://github.com/Duperopope/Aimer.git
cd Aimer
python main.py --auto-fix
```

### Option 5: Déployer votre propre instance
Voir le [Guide de Déploiement](./DEPLOYMENT.md) pour Railway, Render, Heroku

---

**Date de release : 10 juillet 2025**

## Nouveautés de la version 0.1.1

- Lancement all-in-one : `python main.py --auto-fix` installe automatiquement le venv, toutes les dépendances (requirements + Detectron2), relance et vérifie tout, même pour un utilisateur débutant.
- Installation automatique de Detectron2 (wheel Windows) si absent.
- Les logs sont maintenant ignorés par git (`logs/` dans `.gitignore`).
- Patch de robustesse auto-setup (relance automatique après install, gestion venv, etc).
- Mise à jour de la doc et du patchnote.

## Nouveautés de la version 0.1

- Interface graphique PyQt6 moderne et stable
- Détection d'objets, instance & panoptic segmentation (Detectron2)
- Webcam temps réel avec détection et affichage live (threadé, logs détaillés)
- Capture d'écran intégrée
- Gestionnaire de datasets (COCO, VOC, Open Images…)
- Tableaux de bord et métriques temps réel
- Système de logs unifié (fichier `logs/aimer.log`)
- Correction de nombreux warnings Pylance et stabilité accrue

## Utilisation

- Lancer l'interface graphique :
  ```bash
  python main.py
  ```
- Lancer la détection sur une image en ligne de commande :
  ```bash
  python main.py --cli --detect chemin/vers/image.jpg
  ```
- Lancer le mode all-in-one (auto-install, auto-fix, auto-venv) :
  ```bash
  python main.py --auto-fix
  ```
- Activer la webcam depuis l'onglet Détection (bouton Webcam, bouton Arrêter Webcam pour stopper)

## 🌐 Interface Web

AIMER inclut une interface web moderne accessible via navigateur :

### Lancement rapide de l'interface web :
```bash
python launch_web.py
```

### Fonctionnalités web :
- 🎯 Détection d'objets en temps réel
- 📊 Monitoring hardware en direct
- 🎮 Système de gamification
- 📈 Métriques et tableaux de bord
- 🌙 Interface moderne avec thème cyber

### Accès depuis GitHub :
- **GitHub Codespaces** : Interface complète dans le navigateur
- **GitHub Pages** : Version statique de démonstration
- **Port par défaut** : `http://localhost:5000`

## Debug & logs

![Version](https://img.shields.io/badge/version-0.1.1-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-green)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Duperopope/Aimer)
[![Launch Web Interface](https://img.shields.io/badge/🌐%20Launch-Web%20Interface-brightgreen)](https://duperopope.github.io/Aimer)

## 🚀 Lancement rapide

### Option 1: GitHub Codespaces (Recommandé)
Cliquez sur le badge "Open in GitHub Codespaces" ci-dessus pour lancer AIMER dans votre navigateur en un clic !

**Dans Codespaces :**
- L'auto-setup se lance automatiquement au démarrage
- Si ce n'est pas le cas, tapez : `python main.py --auto-fix`
- Pour l'interface web : `python launch_web.py`
- L'interface s'ouvrira automatiquement sur le port 5000

### Option 2: Interface Web Locale
```bash
git clone https://github.com/Duperopope/Aimer.git
cd Aimer
python launch_web.py
```

### Option 3: Installation Classique
```bash
git clone https://github.com/Duperopope/Aimer.git
cd Aimer
python main.py --auto-fix
```

---

**Date de release : 10 juillet 2025**

## Nouveautés de la version 0.1.1

- Lancement all-in-one : `python main.py --auto-fix` installe automatiquement le venv, toutes les dépendances (requirements + Detectron2), relance et vérifie tout, même pour un utilisateur débutant.
- Installation automatique de Detectron2 (wheel Windows) si absent.
- Les logs sont maintenant ignorés par git (`logs/` dans `.gitignore`).
- Patch de robustesse auto-setup (relance automatique après install, gestion venv, etc).
- Mise à jour de la doc et du patchnote.

## Nouveautés de la version 0.1

- Interface graphique PyQt6 moderne et stable
- Détection d’objets, instance & panoptic segmentation (Detectron2)
- Webcam temps réel avec détection et affichage live (threadé, logs détaillés)
- Capture d’écran intégrée
- Gestionnaire de datasets (COCO, VOC, Open Images…)
- Tableaux de bord et métriques temps réel
- Système de logs unifié (fichier `logs/aimer.log`)
- Correction de nombreux warnings Pylance et stabilité accrue

## Utilisation

- Lancer l’interface graphique :
  ```bash
  python main.py
  ```
- Lancer la détection sur une image en ligne de commande :
  ```bash
  python main.py --cli --detect chemin/vers/image.jpg
  ```
- Lancer le mode all-in-one (auto-install, auto-fix, auto-venv) :
  ```bash
  python main.py --auto-fix
  ```
- Activer la webcam depuis l’onglet Détection (bouton Webcam, bouton Arrêter Webcam pour stopper)

## Debug & logs

- Tous les événements importants sont tracés dans `logs/aimer.log`.
- Les logs ne sont pas versionnés (voir `.gitignore`).
- En cas de bug, consultez ce fichier et communiquez-le pour support.

## Gestion des fichiers et du versionnement (Git)

- Le projet utilise un fichier `.gitignore` pour éviter de versionner les fichiers temporaires, logs, bases de données locales, environnements virtuels, etc.
- Les logs d’exécution (`logs/` et `logs/aimer.log`) ne sont jamais envoyés sur le dépôt.
- Les datasets, fichiers .db, et tout ce qui est généré localement sont aussi ignorés.
- Pour contribuer, ne modifiez pas le .gitignore sans raison valable.
- Pour cloner et démarrer le projet :
  ```bash
  git clone <url-du-repo>
  cd Aimer
  python main.py --auto-fix
  ```

---

Important : ce README décrit l’environnement stable Windows sans GPU validé le 10 juillet 2025 (Torch 2.0.1 CPU + Detectron 0.6 + NumPy 1.26).

Si vous disposez d’un GPU CUDA ou d’une autre plate‑forme, consultez la section « Versions alternatives » plus loin.

🎯 Présentation rapide

AIMER PRO est une application de vision par ordinateur basée sur Detectron2 qui offre :

Détection d’objets, instance & panoptic segmentation,

Interface PyQt6 moderne et réactive,

Gestionnaire de datasets (COCO, VOC, Open Images…),

Tableaux de bord et métriques temps réel.

🆕 Quoi de neuf dans ce patch ?

Avant

Maintenant

Python ≥ 3.8

Python 3.10.x épinglé (roues Detectron 0.6)

Torch 2.7 CPU (incompatible)

Torch 2.0.1 + cpu + wheels officielles [PyTorch archive] (pytorch.org)

NumPy 2.x cassait l’ABI Torch / Detectron (ARRAY_API) (github.com)

NumPy 1.26.4 épinglé

OpenCV ≥ 4.11 ramenait NumPy 2 (github.com)

OpenCV 4.8.1.78 (--no‑deps)

Detectron2 à compiler

Wheel binaire detectron2‑0.6‑cp310‑win_amd64.whl (github.com)

Tout est regroupé dans requirements_stable.txt ; l’installeur a été réécrit pour appliquer automatiquement ces verrous.

⚙️ Installation rapide (stable‑CPU)

# 1) Cloner le dépôt
$ git clone https://github.com/Duperopope/Aimer.git
$ cd Aimer

# 2) Créer & activer le venv Python 3.10
$ "C:\Users\<YOU>\AppData\Local\Microsoft\WindowsApps\python3.10.exe" -m venv .venv310
$ .\.venv310\Scripts\Activate.ps1       # PowerShell

# 3) Installer les dépendances épinglées
(.venv310) $ python -m pip install -U pip
(.venv310) $ pip install -r requirements_stable.txt

# 4) Installer Detectron2 0.6 (wheel pré‑compilée)
(.venv310) $ pip install "https://cdn.jsdelivr.net/gh/myhloli/wheels@main/assets/whl/detectron2/detectron2-0.6-cp310-cp310-win_amd64.whl"

# 5) Vérification
(.venv310) $ python main.py --cli --check

Script automatisé

Un nouveau script install_aimer.py est fourni ; il :

détecte l’interpréteur 3.10 ;

crée le venv .venv310 ;

applique requirements_stable.txt ;

télécharge et installe la wheel Detectron ;

lance main.py --cli --check et affiche le rapport.

📦 Contenu de requirements_stable.txt

# Core PyTorch  (CPU)
torch==2.0.1+cpu        --index-url https://download.pytorch.org/whl/cpu
torchvision==0.15.2+cpu --index-url https://download.pytorch.org/whl/cpu
torchaudio==2.0.2+cpu   --index-url https://download.pytorch.org/whl/cpu

# ABI compatible libs
numpy==1.26.4   # < 2 pour éviter _ARRAY_API_  ([github.com](https://github.com/spyder-ide/spyder/issues/22187?utm_source=chatgpt.com))

# Vision
opencv-python==4.8.1.78 --no-deps         # dernières roues NumPy<2  ([pypi.org](https://pypi.org/project/opencv-python/?utm_source=chatgpt.com), [detectron2.readthedocs.io](https://detectron2.readthedocs.io/tutorials/install.html?utm_source=chatgpt.com))
Pillow>=11.0.0

# UI
PyQt6==6.9.1                     # wheels 2025‑05  ([pypi.org](https://pypi.org/project/PyQt6/?utm_source=chatgpt.com), [pypi.org](https://pypi.org/project/PyQt6-Qt6/?utm_source=chatgpt.com))

# Web / utilitaires / logging
Flask>=2.3.0
Flask-CORS>=4.0.0
requests>=2.31.0
structlog>=23.2.0
colorlog>=6.7.0
psutil>=5.9.0
tqdm>=4.66.0
pyyaml>=6.0.1
click>=8.1.7
rich>=13.6.0
cryptography>=41.0.0

🚀 Utilisation

# Détection rapide en CLI
git pull              # récupérer la dernière version
.\.venv310\Scripts\Activate.ps1
python main.py --cli --detect path\to\image.jpg

# Interface graphique PyQt
python main.py

# Lancement all-in-one (auto-install, auto-fix, auto-venv)
python main.py --auto-fix

📚 Versions alternatives

GPU / CUDA 11+ : passez à Torch 2.2+ & NumPy 2, puis compilez Detectron2 depuis les sources (detectron2.readthedocs.io, stackoverflow.com).

Linux / macOS : la même table de versions fonctionne ; supprimez simplement le flag --no-deps pour OpenCV.

🤝 Contribuer

Merci de tester les wheels plus récentes (Detectron 0.8, Torch 2.2, NumPy 2) et d’ouvrir un issue si vous trouvez une combinaison stable !

© 2025 Duperopope – Licence Apache 2.0
