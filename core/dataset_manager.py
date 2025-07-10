#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Gestionnaire de Datasets
© 2025 - Licence Apache 2.0

Gestionnaire complet pour téléchargement et gestion des datasets
"""

import os
import json
import sqlite3
import requests
import zipfile
import tarfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from urllib.parse import urlparse
import hashlib
import time
from dataclasses import dataclass, asdict
from datetime import datetime

from .logger import Logger


@dataclass
class DatasetInfo:
    """Information sur un dataset"""

    id: str
    name: str
    description: str
    size_mb: int
    num_images: int
    num_classes: int
    tasks: List[str]  # detection, segmentation, etc.
    license: str
    url: str
    format: str  # coco, pascal_voc, etc.
    checksum: Optional[str] = None
    is_downloaded: bool = False
    download_date: Optional[str] = None
    local_path: Optional[str] = None


class ProgressCallback:
    """Callback pour le suivi de progression"""

    def __init__(self, callback_func: Optional[Callable] = None):
        self.callback_func = callback_func
        self.start_time = time.time()

    def update(self, downloaded: int, total: int, status: str = ""):
        """Met à jour la progression"""
        if self.callback_func:
            elapsed = time.time() - self.start_time
            speed = downloaded / elapsed if elapsed > 0 else 0
            progress = (downloaded / total * 100) if total > 0 else 0

            self.callback_func(
                {
                    "downloaded": downloaded,
                    "total": total,
                    "progress": progress,
                    "speed": speed,
                    "status": status,
                    "elapsed": elapsed,
                }
            )


class DatasetManager:
    """
    Gestionnaire principal des datasets

    Fonctionnalités:
    - Téléchargement automatique des datasets populaires
    - Gestion des datasets personnalisés
    - Conversion de formats
    - Cache et métadonnées
    """

    def __init__(self, base_path: str = "datasets"):
        self.logger = Logger("DatasetManager")
        self.base_path = Path(base_path)
        self.downloaded_path = self.base_path / "downloaded"
        self.personal_path = self.base_path / "personal"
        self.cache_path = self.base_path / "cache"

        # Création des dossiers
        for path in [self.downloaded_path, self.personal_path, self.cache_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Base de données SQLite
        self.db_path = self.base_path / "datasets.db"
        self._init_database()

        # Datasets disponibles
        self.available_datasets = self._load_available_datasets()

        self.logger.info(f"DatasetManager initialisé - Base: {self.base_path}")

    def _init_database(self):
        """Initialise la base de données SQLite"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS datasets (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    size_mb INTEGER,
                    num_images INTEGER,
                    num_classes INTEGER,
                    tasks TEXT,  -- JSON array
                    license TEXT,
                    url TEXT,
                    format TEXT,
                    checksum TEXT,
                    is_downloaded BOOLEAN DEFAULT FALSE,
                    download_date TEXT,
                    local_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS personal_datasets (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    path TEXT NOT NULL,
                    num_images INTEGER,
                    num_classes INTEGER,
                    format TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS download_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id TEXT,
                    action TEXT,  -- download, delete, update
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details TEXT  -- JSON
                )
            """
            )

    def _load_available_datasets(self) -> Dict[str, DatasetInfo]:
        """Charge la liste des datasets disponibles"""
        datasets = {
            "coco_2017": DatasetInfo(
                id="coco_2017",
                name="COCO 2017",
                description="Common Objects in Context - Dataset de référence pour la détection d'objets",
                size_mb=25000,  # ~25GB
                num_images=330000,
                num_classes=80,
                tasks=["detection", "segmentation", "keypoints"],
                license="CC BY 4.0",
                url="http://images.cocodataset.org/zips/train2017.zip",
                format="coco",
                checksum="cced6f7f71b7629ddf16f17bbcfab6b2",
            ),
            "pascal_voc_2012": DatasetInfo(
                id="pascal_voc_2012",
                name="Pascal VOC 2012",
                description="Pascal Visual Object Classes - Dataset classique pour la détection",
                size_mb=2000,  # ~2GB
                num_images=17125,
                num_classes=20,
                tasks=["detection", "segmentation"],
                license="Academic Use",
                url="http://host.robots.ox.ac.uk/pascal/VOC/voc2012/VOCtrainval_11-May-2012.tar",
                format="pascal_voc",
                checksum="6cd6e144f989b92b3379bac3b3de84fd",
            ),
            "open_images_v7": DatasetInfo(
                id="open_images_v7",
                name="Open Images V7 (Subset)",
                description="Google Open Images - Subset de 10K images pour tests rapides",
                size_mb=5000,  # ~5GB subset
                num_images=10000,
                num_classes=600,
                tasks=["detection", "segmentation"],
                license="CC BY 4.0",
                url="https://storage.googleapis.com/openimages/web/download_v7.html",
                format="coco",
                checksum="a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
            ),
            "cifar10": DatasetInfo(
                id="cifar10",
                name="CIFAR-10",
                description="Dataset de classification - 10 classes, 60K images 32x32",
                size_mb=170,  # ~170MB
                num_images=60000,
                num_classes=10,
                tasks=["classification"],
                license="Academic Use",
                url="https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz",
                format="cifar",
                checksum="c58f30108f718f92721af3b95e74349a",
            ),
            "cityscapes_demo": DatasetInfo(
                id="cityscapes_demo",
                name="Cityscapes Demo",
                description="Cityscapes - Subset démo pour scènes urbaines",
                size_mb=1000,  # ~1GB
                num_images=2975,
                num_classes=19,
                tasks=["segmentation"],
                license="Academic Use",
                url="https://www.cityscapes-dataset.com/file-handling/?packageID=1",
                format="cityscapes",
                checksum="demo123456789abcdef",
            ),
        }

        # Mise à jour de la base de données
        self._update_database_datasets(datasets)

        return datasets

    def _update_database_datasets(self, datasets: Dict[str, DatasetInfo]):
        """Met à jour la base de données avec les datasets disponibles"""
        with sqlite3.connect(self.db_path) as conn:
            for dataset in datasets.values():
                conn.execute(
                    """
                    INSERT OR REPLACE INTO datasets
                    (id, name, description, size_mb, num_images, num_classes,
                     tasks, license, url, format, checksum)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        dataset.id,
                        dataset.name,
                        dataset.description,
                        dataset.size_mb,
                        dataset.num_images,
                        dataset.num_classes,
                        json.dumps(dataset.tasks),
                        dataset.license,
                        dataset.url,
                        dataset.format,
                        dataset.checksum,
                    ),
                )

    def get_available_datasets(self) -> List[DatasetInfo]:
        """Retourne la liste des datasets disponibles"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM datasets ORDER BY name
            """
            )

            datasets = []
            for row in cursor.fetchall():
                dataset = DatasetInfo(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    size_mb=row[3],
                    num_images=row[4],
                    num_classes=row[5],
                    tasks=json.loads(row[6]),
                    license=row[7],
                    url=row[8],
                    format=row[9],
                    checksum=row[10],
                    is_downloaded=bool(row[11]),
                    download_date=row[12],
                    local_path=row[13],
                )
                datasets.append(dataset)

            return datasets

    def get_downloaded_datasets(self) -> List[DatasetInfo]:
        """Retourne la liste des datasets téléchargés"""
        return [ds for ds in self.get_available_datasets() if ds.is_downloaded]

    def download_dataset(
        self, dataset_id: str, progress_callback: Optional[Callable] = None
    ) -> bool:
        """
        Télécharge un dataset avec suivi de progression

        Args:
            dataset_id: ID du dataset à télécharger
            progress_callback: Fonction de callback pour la progression

        Returns:
            bool: True si succès, False sinon
        """
        if dataset_id not in self.available_datasets:
            self.logger.error(f"Dataset inconnu: {dataset_id}")
            return False

        dataset = self.available_datasets[dataset_id]

        # Vérifier si déjà téléchargé
        if self.is_downloaded(dataset_id):
            self.logger.info(f"Dataset {dataset_id} déjà téléchargé")
            if progress_callback:
                progress_callback(
                    {
                        "downloaded": dataset.size_mb * 1024 * 1024,
                        "total": dataset.size_mb * 1024 * 1024,
                        "progress": 100,
                        "speed": 0,
                        "status": "Déjà téléchargé",
                        "elapsed": 0,
                    }
                )
            return True

        self.logger.info(f"Début téléchargement: {dataset.name}")

        try:
            # Dossier de destination
            dataset_dir = self.downloaded_path / dataset_id
            dataset_dir.mkdir(exist_ok=True)

            # Nom du fichier
            filename = Path(urlparse(dataset.url).path).name
            if not filename:
                filename = f"{dataset_id}.zip"

            file_path = dataset_dir / filename

            # Téléchargement avec progression
            success = self._download_file(dataset.url, file_path, progress_callback)

            if success:
                # Vérification checksum si disponible
                if dataset.checksum and not self._verify_checksum(
                    file_path, dataset.checksum
                ):
                    self.logger.error(f"Checksum invalide pour {dataset_id}")
                    return False

                # Extraction si nécessaire
                if filename.endswith((".zip", ".tar", ".tar.gz")):
                    self._extract_archive(file_path, dataset_dir, progress_callback)

                # Mise à jour base de données
                self._mark_as_downloaded(dataset_id, str(dataset_dir))

                # Historique
                self._add_to_history(dataset_id, "download", {"success": True})

                self.logger.info(f"Téléchargement terminé: {dataset.name}")
                return True

        except Exception as e:
            self.logger.error(f"Erreur téléchargement {dataset_id}: {e}")
            self._add_to_history(
                dataset_id, "download", {"success": False, "error": str(e)}
            )

        return False

    def _download_file(
        self, url: str, file_path: Path, progress_callback: Optional[Callable] = None
    ) -> bool:
        """Télécharge un fichier avec suivi de progression"""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            callback = ProgressCallback(progress_callback)

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        callback.update(downloaded, total_size, "Téléchargement...")

            return True

        except Exception as e:
            self.logger.error(f"Erreur téléchargement {url}: {e}")
            return False

    def _extract_archive(
        self,
        archive_path: Path,
        extract_dir: Path,
        progress_callback: Optional[Callable] = None,
    ):
        """Extrait une archive"""
        try:
            if progress_callback:
                progress_callback(
                    {
                        "downloaded": 0,
                        "total": 100,
                        "progress": 0,
                        "speed": 0,
                        "status": "Extraction...",
                        "elapsed": 0,
                    }
                )

            if archive_path.suffix == ".zip":
                with zipfile.ZipFile(archive_path, "r") as zip_ref:
                    zip_ref.extractall(extract_dir)
            elif archive_path.suffix in [".tar", ".gz"]:
                with tarfile.open(archive_path, "r:*") as tar_ref:
                    tar_ref.extractall(extract_dir)

            # Suppression de l'archive après extraction
            archive_path.unlink()

            if progress_callback:
                progress_callback(
                    {
                        "downloaded": 100,
                        "total": 100,
                        "progress": 100,
                        "speed": 0,
                        "status": "Extraction terminée",
                        "elapsed": 0,
                    }
                )

        except Exception as e:
            self.logger.error(f"Erreur extraction {archive_path}: {e}")

    def _verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Vérifie le checksum MD5 d'un fichier"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)

            return hash_md5.hexdigest() == expected_checksum

        except Exception as e:
            self.logger.error(f"Erreur vérification checksum: {e}")
            return False

    def _mark_as_downloaded(self, dataset_id: str, local_path: str):
        """Marque un dataset comme téléchargé"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE datasets
                SET is_downloaded = TRUE, download_date = ?, local_path = ?
                WHERE id = ?
            """,
                (datetime.now().isoformat(), local_path, dataset_id),
            )

    def is_downloaded(self, dataset_id: str) -> bool:
        """Vérifie si un dataset est téléchargé"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT is_downloaded FROM datasets WHERE id = ?
            """,
                (dataset_id,),
            )

            result = cursor.fetchone()
            return bool(result[0]) if result else False

    def delete_dataset(self, dataset_id: str) -> bool:
        """Supprime un dataset téléchargé"""
        try:
            dataset_dir = self.downloaded_path / dataset_id
            if dataset_dir.exists():
                shutil.rmtree(dataset_dir)

            # Mise à jour base de données
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE datasets
                    SET is_downloaded = FALSE, download_date = NULL, local_path = NULL
                    WHERE id = ?
                """,
                    (dataset_id,),
                )

            self._add_to_history(dataset_id, "delete", {"success": True})
            self.logger.info(f"Dataset {dataset_id} supprimé")
            return True

        except Exception as e:
            self.logger.error(f"Erreur suppression {dataset_id}: {e}")
            return False

    def create_personal_dataset(
        self, name: str, description: str, source_path: str
    ) -> Optional[str]:
        """
        Crée un dataset personnel

        Args:
            name: Nom du dataset
            description: Description
            source_path: Chemin vers les données source

        Returns:
            str: ID du dataset créé, None si erreur
        """
        try:
            # Génération ID unique
            dataset_id = f"personal_{int(time.time())}"

            # Dossier de destination
            dataset_dir = self.personal_path / dataset_id
            dataset_dir.mkdir(exist_ok=True)

            # Copie des données
            source = Path(source_path)
            if source.is_file():
                shutil.copy2(source, dataset_dir)
            elif source.is_dir():
                shutil.copytree(source, dataset_dir / source.name)

            # Analyse du dataset
            stats = self._analyze_personal_dataset(dataset_dir)

            # Sauvegarde en base
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO personal_datasets
                    (id, name, description, path, num_images, num_classes, format)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        dataset_id,
                        name,
                        description,
                        str(dataset_dir),
                        stats.get("num_images", 0),
                        stats.get("num_classes", 0),
                        stats.get("format", "unknown"),
                    ),
                )

            self.logger.info(f"Dataset personnel créé: {name}")
            return dataset_id

        except Exception as e:
            self.logger.error(f"Erreur création dataset personnel: {e}")
            return None

    def _analyze_personal_dataset(self, dataset_dir: Path) -> Dict[str, Any]:
        """Analyse un dataset personnel pour extraire les statistiques"""
        stats = {"num_images": 0, "num_classes": 0, "format": "unknown"}

        try:
            # Compter les images
            image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
            image_files = []

            for ext in image_extensions:
                image_files.extend(dataset_dir.rglob(f"*{ext}"))
                image_files.extend(dataset_dir.rglob(f"*{ext.upper()}"))

            stats["num_images"] = len(image_files)

            # Détecter le format
            if (dataset_dir / "annotations").exists():
                stats["format"] = "coco"
            elif any(dataset_dir.rglob("*.xml")):
                stats["format"] = "pascal_voc"
            elif any(dataset_dir.rglob("*.txt")):
                stats["format"] = "yolo"

            # Compter les classes (approximatif)
            if stats["format"] == "coco":
                # Chercher fichier annotations COCO
                for ann_file in dataset_dir.rglob("*.json"):
                    try:
                        with open(ann_file) as f:
                            data = json.load(f)
                            if "categories" in data:
                                stats["num_classes"] = len(data["categories"])
                                break
                    except:
                        continue

        except Exception as e:
            self.logger.error(f"Erreur analyse dataset: {e}")

        return stats

    def get_personal_datasets(self) -> List[Dict[str, Any]]:
        """Retourne la liste des datasets personnels"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM personal_datasets ORDER BY created_at DESC
            """
            )

            datasets = []
            for row in cursor.fetchall():
                datasets.append(
                    {
                        "id": row[0],
                        "name": row[1],
                        "description": row[2],
                        "path": row[3],
                        "num_images": row[4],
                        "num_classes": row[5],
                        "format": row[6],
                        "created_at": row[7],
                        "updated_at": row[8],
                    }
                )

            return datasets

    def _add_to_history(self, dataset_id: str, action: str, details: Dict[str, Any]):
        """Ajoute une entrée à l'historique"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO download_history (dataset_id, action, details)
                VALUES (?, ?, ?)
            """,
                (dataset_id, action, json.dumps(details)),
            )

    def get_download_history(self) -> List[Dict[str, Any]]:
        """Retourne l'historique des téléchargements"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM download_history ORDER BY timestamp DESC LIMIT 50
            """
            )

            history = []
            for row in cursor.fetchall():
                history.append(
                    {
                        "id": row[0],
                        "dataset_id": row[1],
                        "action": row[2],
                        "timestamp": row[3],
                        "details": json.loads(row[4]) if row[4] else {},
                    }
                )

            return history

    def get_storage_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de stockage"""

        def get_dir_size(path: Path) -> int:
            total = 0
            try:
                for file_path in path.rglob("*"):
                    if file_path.is_file():
                        total += file_path.stat().st_size
            except:
                pass
            return total

        downloaded_size = get_dir_size(self.downloaded_path)
        personal_size = get_dir_size(self.personal_path)
        cache_size = get_dir_size(self.cache_path)

        return {
            "downloaded_size_mb": downloaded_size / (1024 * 1024),
            "personal_size_mb": personal_size / (1024 * 1024),
            "cache_size_mb": cache_size / (1024 * 1024),
            "total_size_mb": (downloaded_size + personal_size + cache_size)
            / (1024 * 1024),
            "num_downloaded": len(self.get_downloaded_datasets()),
            "num_personal": len(self.get_personal_datasets()),
        }

    def cleanup_cache(self):
        """Nettoie le cache"""
        try:
            if self.cache_path.exists():
                shutil.rmtree(self.cache_path)
                self.cache_path.mkdir(exist_ok=True)

            self.logger.info("Cache nettoyé")

        except Exception as e:
            self.logger.error(f"Erreur nettoyage cache: {e}")

    def get_all_datasets(self) -> List[DatasetInfo]:
        """Retourne tous les datasets disponibles"""
        return self.get_available_datasets()

    def get_popular_datasets(self) -> List[DatasetInfo]:
        """Retourne les datasets populaires/recommandés"""
        popular_ids = ["coco_2017", "pascal_voc_2012", "cifar10"]
        all_datasets = self.get_available_datasets()
        return [ds for ds in all_datasets if ds.id in popular_ids]
