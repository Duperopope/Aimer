AIMER PRO — Détection universelle (Windows / CPU stable)

      

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

📚 Versions alternatives

GPU / CUDA 11+ : passez à Torch 2.2+ & NumPy 2, puis compilez Detectron2 depuis les sources (detectron2.readthedocs.io, stackoverflow.com).

Linux / macOS : la même table de versions fonctionne ; supprimez simplement le flag --no-deps pour OpenCV.

🤝 Contribuer

Merci de tester les wheels plus récentes (Detectron 0.8, Torch 2.2, NumPy 2) et d’ouvrir un issue si vous trouvez une combinaison stable !

© 2025 Duperopope – Licence Apache 2.0

