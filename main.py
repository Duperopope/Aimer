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
