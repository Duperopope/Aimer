#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Application de Détection Universelle avec Detectron2
© 2025 - Licence Apache 2.0

Point d'entrée principal unifié
"""

import sys
import os
import argparse
import logging
from pathlib import Path
import subprocess

# Configuration du chemin
sys.path.insert(0, str(Path(__file__).parent))


def setup_logging():
    """Configure le système de logging"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "aimer.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger("AIMER")


def check_dependencies():
    """Vérifie les dépendances critiques"""
    missing = []
    available = []

    try:
        import torch
        import torchvision

        available.append("PyTorch")
    except ImportError:
        missing.append("PyTorch")

    try:
        import detectron2

        available.append("Detectron2")
    except ImportError:
        missing.append("Detectron2")

    try:
        import cv2

        available.append("OpenCV")
    except ImportError:
        missing.append("OpenCV")

    try:
        from PyQt6.QtWidgets import QApplication

        available.append("PyQt6")
    except ImportError:
        missing.append("PyQt6")

    return missing, available


def run_cli_mode(args):
    """Mode ligne de commande"""
    logger = setup_logging()
    logger.info("Démarrage AIMER PRO - Mode CLI")

    try:
        # Vérification des dépendances pour la détection
        missing, available = check_dependencies()

        if args.check:
            # Vérification système
            print("=" * 60)
            print("AIMER PRO - Rapport Système")
            print("=" * 60)
            print("Dépendances disponibles:")
            for dep in available:
                print(f"  ✓ {dep}")

            if missing:
                print("\nDépendances manquantes:")
                for dep in missing:
                    print(f"  ✗ {dep}")

            print("=" * 60)
            return True

        elif args.detect:
            if "Detectron2" in missing:
                print("[ERREUR] Detectron2 requis pour la détection")
                print(
                    "Installation: pip install 'git+https://github.com/facebookresearch/detectron2.git'"
                )
                return False

            # Import dynamique du détecteur
            from core.detector import UniversalDetector

            # Création du détecteur
            detector = UniversalDetector(
                task_type=args.task, confidence_threshold=args.confidence
            )

            # Détection sur image
            logger.info(f"Détection sur: {args.detect}")

            if not Path(args.detect).exists():
                print(f"[ERREUR] Image non trouvée: {args.detect}")
                return False

            result = detector.detect(args.detect)

            if result.instances:
                detections = result.to_dict()
                print(f"[SUCCÈS] Détection réussie!")
                print(f"Objets détectés: {detections['count']}")
                print(
                    f"Temps: {result.performance_metrics.get('inference_time_ms', 0):.1f}ms"
                )

                # Top 5 détections
                for i, detection in enumerate(detections["detections"][:5]):
                    print(
                        f"  {i+1}. {detection['class_name']}: {detection['confidence']:.2f}"
                    )
            else:
                print("[INFO] Aucun objet détecté")

            # Nettoyage
            detector.cleanup()

        return True

    except Exception as e:
        logger.error(f"Erreur: {e}")
        print(f"[ERREUR] {e}")
        return False


def run_gui_mode():
    """Mode interface graphique"""
    logger = setup_logging()
    logger.info("Démarrage AIMER PRO - Mode GUI")

    try:
        # Vérification PyQt6
        missing, available = check_dependencies()

        if "PyQt6" in missing:
            print("[ERREUR] PyQt6 requis pour l'interface graphique")
            print("Installation: pip install PyQt6")
            print("[CONSEIL] Utilisez le mode CLI: python main.py --cli --check")
            return False

        # Import dynamique de l'interface
        from ui.main_window import MainWindow
        from PyQt6.QtWidgets import QApplication

        # Création de l'application Qt
        app = QApplication(sys.argv)
        app.setApplicationName("AIMER PRO")
        app.setApplicationVersion("1.0.0")

        # Création de la fenêtre principale
        window = MainWindow()
        window.show()

        # Lancement de la boucle d'événements
        return app.exec() == 0

    except Exception as e:
        logger.error(f"Erreur GUI: {e}")
        print(f"[ERREUR] Interface graphique: {e}")
        print("[CONSEIL] Utilisez le mode CLI: python main.py --cli --check")
        return False


# --- AUTO-SETUP POUR TEST FACILE ---
def is_venv_active():
    # Vérifie si le venv est actif
    return (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
        'VIRTUAL_ENV' in os.environ
    )


def get_venv_python():
    # Retourne le chemin du python du venv s'il existe
    venv_path = Path(__file__).parent / '.venv' / 'Scripts' / 'python.exe'
    return str(venv_path) if venv_path.exists() else None


def auto_setup(auto_fix=False):
    logger = setup_logging()
    # 1. Vérifie le venv
    if not is_venv_active():
        venv_python = get_venv_python()
        if venv_python:
            logger.warning("Le venv n'est pas activé. Relance automatique dans le venv...")
            print(f"[AUTO-SETUP] Le venv n'est pas activé. Relance automatique dans le venv...")
            os.execv(venv_python, [venv_python] + sys.argv)
        else:
            logger.error("Aucun venv détecté (.venv). Veuillez créer un venv Python 3.10 dans le dossier du projet.")
            print("[AUTO-SETUP] Aucun venv détecté (.venv). Veuillez créer un venv Python 3.10 dans le dossier du projet.")
            print("Commande : python -m venv .venv")
            sys.exit(1)

    # 2. Vérifie Detectron2 en priorité
    try:
        import detectron2
        detectron2_ok = True
    except ImportError:
        detectron2_ok = False
    if not detectron2_ok:
        url = "https://cdn.jsdelivr.net/gh/myhloli/wheels@main/assets/whl/detectron2/detectron2-0.6-cp310-cp310-win_amd64.whl"
        logger.warning("Detectron2 non installé. Installation depuis %s", url)
        print(f"[AUTO-SETUP] Detectron2 non installé. Installation depuis {url}")
        subprocess.run([sys.executable, '-m', 'pip', 'install', url], check=True)
        logger.info("Detectron2 installé. Relance automatique...")
        print("[AUTO-SETUP] Relance automatique après installation de Detectron2...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    # 3. Vérifie les requirements critiques restants
    missing = []
    try:
        import torch, torchvision
    except ImportError:
        missing.append('torch')
    try:
        import cv2
    except ImportError:
        missing.append('opencv-python')
    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError:
        missing.append('PyQt6')

    # 4. Vérifie toutes les dépendances du requirements (hors detectron2)
    req_file = Path(__file__).parent / 'requirements_stable.txt'
    if req_file.exists():
        with open(req_file, encoding='utf-8') as f:
            pkgs = []
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if 'detectron2' in line:
                    continue  # déjà géré
                pkg = line.split()[0]
                pkgs.append(pkg)
        # Vérifie si tout est installé
        import pkg_resources
        installed = {pkg.key for pkg in pkg_resources.working_set}
        to_install = [p for p in pkgs if p.lower().split('==')[0] not in installed]
        if to_install:
            logger.warning("Installation des dépendances requirements_stable.txt : %s", ', '.join(to_install))
            print(f"[AUTO-SETUP] Installation des dépendances requirements_stable.txt : {', '.join(to_install)}")
            if auto_fix or (input("Installer toutes les dépendances du projet ? [O/n] ").strip().lower() in ('', 'o', 'y', 'yes')):
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(req_file)], check=True)
                logger.info("requirements_stable.txt installé. Relance automatique...")
                print("[AUTO-SETUP] Relance automatique après installation...")
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                logger.error("Installation requirements_stable.txt refusée par l'utilisateur.")
                print("[AUTO-SETUP] Veuillez installer les dépendances puis relancer.")
                sys.exit(1)

    if missing:
        logger.warning("Dépendances critiques manquantes : %s", ', '.join(missing))
        print(f"[AUTO-SETUP] Dépendances critiques manquantes : {', '.join(missing)}")
        if auto_fix or (input("Installer automatiquement les dépendances critiques manquantes ? [O/n] ").strip().lower() in ('', 'o', 'y', 'yes')):
            for pkg in missing:
                logger.info("Installation de la dépendance critique : %s", pkg)
                print(f"[AUTO-SETUP] pip install {pkg}")
                subprocess.run([sys.executable, '-m', 'pip', 'install', pkg], check=True)
            logger.info("Dépendances critiques installées. Relance automatique...")
            print("[AUTO-SETUP] Relance automatique après installation...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            logger.error("Installation des dépendances critiques refusée par l'utilisateur.")
            print("[AUTO-SETUP] Veuillez installer les dépendances critiques puis relancer.")
            sys.exit(1)
# --- FIN AUTO-SETUP ---


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="AIMER PRO - Détection universelle avec Detectron2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python main.py                           # Interface graphique
  python main.py --cli --check             # Vérification système
  python main.py --cli --detect image.jpg  # Détection CLI
  python main.py --cli --detect image.jpg --task instance_segmentation
        """,
    )

    # Arguments principaux
    parser.add_argument("--cli", action="store_true", help="Mode ligne de commande")
    parser.add_argument("--check", action="store_true", help="Vérification système")
    parser.add_argument(
        "--detect", type=str, metavar="IMAGE", help="Détection sur image"
    )

    # Arguments de configuration
    parser.add_argument(
        "--task",
        type=str,
        default="detection",
        choices=[
            "detection",
            "instance_segmentation",
            "panoptic_segmentation",
            "keypoint_detection",
        ],
        help="Type de tâche",
    )
    parser.add_argument(
        "--confidence", type=float, default=0.5, help="Seuil de confiance (0.0-1.0)"
    )

    args = parser.parse_args()

    # Header
    print("=" * 60)
    print("AIMER PRO - Detectron2 Edition")
    print("(c) 2025 - Licence Apache 2.0")
    print("=" * 60)

    # Exécution
    try:
        if args.cli:
            success = run_cli_mode(args)
        else:
            success = run_gui_mode()

        print("\n" + "=" * 60)
        if success:
            print("[SUCCÈS] Exécution terminée avec succès")
        else:
            print("[ERREUR] Exécution terminée avec erreurs")
        print("=" * 60)

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n[ARRÊT] Arrêt demandé par utilisateur")
        return 0
    except Exception as e:
        print(f"\n[ERREUR] Erreur inattendue: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
