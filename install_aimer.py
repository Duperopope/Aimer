#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO – Installateur Windows CPU (Py 3.10)
© 2025 – Licence Apache 2.0
"""

import subprocess, sys, platform, textwrap, shutil, os
from pathlib import Path

PY_REQUIRED = (3, 10)  # 3.10 +
VENV = Path(sys.prefix)  # racine du venv actuel

# Versions épinglées
NUMPY_VER = "1.26.4"
OPENCV_WHL_URL = (
    "https://files.pythonhosted.org/packages/2f/ae/"
    "b861a2f8093d34c4714bc889eb0bb65fd0fc71e782a392e81ee4d42a6fdd/"
    "opencv_python-4.8.1.78-cp310-cp310-win_amd64.whl"
)
TORCH_PKGS = (
    "torch==2.0.1+cpu "
    "torchvision==0.15.2+cpu "
    "torchaudio==2.0.2+cpu "
    "--index-url https://download.pytorch.org/whl/cpu"
)
DETECTRON_WHL = (
    "https://cdn.jsdelivr.net/gh/myhloli/wheels@main/assets/whl/"
    "detectron2/detectron2-0.6-cp310-cp310-win_amd64.whl"
)


def run(cmd: str, desc: str) -> None:
    print(f"🔧 {desc}…")
    subprocess.run(cmd, check=True, shell=True)


def main() -> int:
    # 0. Version Python
    if sys.version_info < PY_REQUIRED:
        print(f"❌ Python {PY_REQUIRED[0]}.{PY_REQUIRED[1]} minimum requis")
        return 1
    print(f"✅ Python {platform.python_version()} détecté")

    # 1. Mise à jour pip
    run(f"{sys.executable} -m pip install -U pip", "Mise à jour pip")

    # 2. NumPy 1.26.4 explicitement
    run(
        f"{sys.executable} -m pip install numpy=={NUMPY_VER}",
        "Installation NumPy 1.x compatible",
    )

    # 3. PyTorch CPU + libs
    run(
        f"{sys.executable} -m pip install {TORCH_PKGS}",
        "Installation PyTorch CPU 2.0.1",
    )

    # 4. OpenCV 4.8.1 wheel (sans dépendances pour ne pas ré-installer NumPy 2)
    run(
        f'{sys.executable} -m pip install "{OPENCV_WHL_URL}" --no-deps',
        "Installation OpenCV 4.8.1 (CPU)",
    )

    # 5. PyQt6 pour la GUI
    run(f"{sys.executable} -m pip install PyQt6==6.9.1", "Installation PyQt6")

    # 6. Detectron2 0.6 wheel
    run(
        f'{sys.executable} -m pip install "{DETECTRON_WHL}"',
        "Installation Detectron2 0.6 (wheel)",
    )

    # 7. Tests rapides d’import
    test_code = textwrap.dedent(
        """
        import numpy, cv2, torch, detectron2
        assert numpy.__version__.startswith('1.26')
        print('NumPy      :', numpy.__version__)
        print('OpenCV     :', cv2.__version__)
        print('Torch      :', torch.__version__, '| CUDA ?', torch.cuda.is_available())
        print('Detectron2 :', detectron2.__version__)
    """
    )
    run(f'{sys.executable} - << "PY"\n{test_code}\nPY', "Vérification imports")

    print("\n🎉 Installation AIMER PRO terminée avec succès !")
    print("   Lance :  python main.py --cli --check")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.CalledProcessError as err:
        print("❌ Échec !", err)
        sys.exit(1)
