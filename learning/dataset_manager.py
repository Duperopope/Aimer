"""
Dataset Manager - Gestionnaire de datasets pour la base globale
Gère l'import, la conversion et l'intégration des datasets externes
"""

import os
import json
import requests
import zipfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sqlite3
from datetime import datetime
import hashlib
import yaml

class DatasetManager:
    """Gestionnaire principal des datasets pour la base globale"""
    
    def __init__(self, base_path: str = "datasets"):
        self.base_path = Path(base_path)
        self.global_db_path = self.base_path / "global_knowledge.db"
        self.personal_db_path = self.base_path / "personal_library.db"
        self.cache_path = self.base_path / "cache"
        
        # Créer les répertoires nécessaires
        self.base_path.mkdir(exist_ok=True)
        self.cache_path.mkdir(exist_ok=True)
        
        # Configuration des datasets disponibles
        self.available_datasets = self._load_dataset_config()
        
        # Initialiser les bases de données
        self._init_databases()
    
    def _load_dataset_config(self) -> Dict:
        """Charge la configuration des datasets disponibles"""
        return {
            "tier_1_essential": {
                "coco_dataset": {
                    "name": "Microsoft COCO Dataset",
                    "url": "https://cocodataset.org/",
                    "classes": 80,
                    "images": 120000,
                    "format": "COCO JSON",
                    "download_url": "http://images.cocodataset.org/zips/train2017.zip",
                    "annotations_url": "http://images.cocodataset.org/annotations/annotations_trainval2017.zip",
                    "status": "available",
                    "priority": 1
                },
                "open_images": {
                    "name": "Google Open Images Dataset",
                    "url": "https://storage.googleapis.com/openimages/web/index.html",
                    "classes": 600,
                    "images": 9000000,
                    "format": "CSV + Images",
                    "download_url": "https://storage.googleapis.com/openimages/v7/oidv7-train-annotations-bbox.csv",
                    "status": "available",
                    "priority": 1
                },
                "roboflow_universe": {
                    "name": "Roboflow Universe",
                    "url": "https://universe.roboflow.com/",
                    "classes": "Variable",
                    "datasets": 1000000,
                    "format": "YOLO, COCO, Pascal VOC",
                    "api_endpoint": "https://api.roboflow.com/",
                    "status": "api_required",
                    "priority": 2
                }
            },
            "tier_2_specialized": {
                "medical": {
                    "tcia_cancer": {
                        "name": "The Cancer Imaging Archive",
                        "url": "https://www.cancerimagingarchive.net/",
                        "specialty": "Medical - Cancer",
                        "format": "DICOM",
                        "status": "available",
                        "priority": 3
                    },
                    "brain_mri": {
                        "name": "Brain Tumor MRI Dataset",
                        "url": "https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset",
                        "classes": 4,
                        "images": 7023,
                        "specialty": "Medical - Neurology",
                        "format": "Images + Labels",
                        "status": "kaggle_api",
                        "priority": 3
                    }
                },
                "gaming": {
                    "weapon_detection": {
                        "name": "Weapon Detection Dataset",
                        "classes": ["pistol", "rifle", "knife"],
                        "images": 200000,
                        "specialty": "Gaming - FPS",
                        "format": "YOLO",
                        "status": "available",
                        "priority": 3
                    },
                    "gaming_objects": {
                        "name": "Gaming Objects Collection",
                        "classes": ["grenade", "ammo", "health_pack", "armor"],
                        "specialty": "Gaming - General",
                        "format": "Multiple",
                        "status": "roboflow",
                        "priority": 3
                    }
                },
                "industrial": {
                    "manufacturing_qc": {
                        "name": "Manufacturing Quality Control",
                        "specialty": "Industrial - QC",
                        "classes": ["defect", "normal", "anomaly"],
                        "format": "YOLO",
                        "status": "available",
                        "priority": 4
                    }
                },
                "geospatial": {
                    "usgs_satellite": {
                        "name": "USGS Earth Explorer",
                        "url": "https://earthexplorer.usgs.gov/",
                        "specialty": "Satellite - Earth",
                        "format": "GeoTIFF",
                        "status": "api_required",
                        "priority": 4
                    }
                }
            }
        }
    
    def _init_databases(self):
        """Initialise les bases de données SQLite"""
        # Base de données globale
        with sqlite3.connect(self.global_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS datasets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    specialty TEXT,
                    classes_count INTEGER,
                    images_count INTEGER,
                    format TEXT,
                    download_url TEXT,
                    status TEXT DEFAULT 'available',
                    priority INTEGER DEFAULT 5,
                    installed BOOLEAN DEFAULT FALSE,
                    install_date TIMESTAMP,
                    file_hash TEXT,
                    size_mb REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS classes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id INTEGER,
                    class_name TEXT NOT NULL,
                    class_id INTEGER,
                    description TEXT,
                    examples_count INTEGER DEFAULT 0,
                    confidence_threshold REAL DEFAULT 0.5,
                    FOREIGN KEY (dataset_id) REFERENCES datasets (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id INTEGER,
                    model_name TEXT NOT NULL,
                    model_path TEXT,
                    accuracy REAL,
                    precision_avg REAL,
                    recall_avg REAL,
                    f1_score REAL,
                    training_date TIMESTAMP,
                    model_size_mb REAL,
                    inference_time_ms REAL,
                    FOREIGN KEY (dataset_id) REFERENCES datasets (id)
                )
            """)
        
        # Base de données personnelle
        with sqlite3.connect(self.personal_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS personal_objects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    object_name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    category TEXT,
                    created_by_user TEXT DEFAULT 'local',
                    examples_count INTEGER DEFAULT 0,
                    confidence_threshold REAL DEFAULT 0.5,
                    last_trained TIMESTAMP,
                    accuracy REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS annotations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    object_id INTEGER,
                    image_path TEXT NOT NULL,
                    bbox_x1 REAL,
                    bbox_y1 REAL,
                    bbox_x2 REAL,
                    bbox_y2 REAL,
                    confidence REAL,
                    validated BOOLEAN DEFAULT FALSE,
                    validation_source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (object_id) REFERENCES personal_objects (id)
                )
            """)
    
    def get_available_datasets(self, category: str = None, priority: int = None) -> List[Dict]:
        """Retourne la liste des datasets disponibles"""
        datasets = []
        
        for tier_name, tier_data in self.available_datasets.items():
            if tier_name == "tier_1_essential":
                for dataset_key, dataset_info in tier_data.items():
                    if category is None or dataset_info.get("specialty", "").lower().find(category.lower()) != -1:
                        if priority is None or dataset_info.get("priority", 5) <= priority:
                            datasets.append({
                                "key": dataset_key,
                                "tier": tier_name,
                                **dataset_info
                            })
            else:  # tier_2_specialized
                for specialty, specialty_datasets in tier_data.items():
                    if category is None or specialty == category:
                        for dataset_key, dataset_info in specialty_datasets.items():
                            if priority is None or dataset_info.get("priority", 5) <= priority:
                                datasets.append({
                                    "key": dataset_key,
                                    "tier": tier_name,
                                    "specialty": specialty,
                                    **dataset_info
                                })
        
        return sorted(datasets, key=lambda x: x.get("priority", 5))
    
    def install_dataset(self, dataset_key: str, force_reinstall: bool = False) -> bool:
        """Installe un dataset spécifique"""
        try:
            # Trouver le dataset dans la configuration
            dataset_info = self._find_dataset_info(dataset_key)
            if not dataset_info:
                print(f"❌ Dataset '{dataset_key}' non trouvé")
                return False
            
            # Vérifier si déjà installé
            if not force_reinstall and self._is_dataset_installed(dataset_key):
                print(f"✅ Dataset '{dataset_key}' déjà installé")
                return True
            
            print(f"📥 Installation du dataset '{dataset_info['name']}'...")
            
            # Créer le répertoire du dataset
            dataset_path = self.base_path / "installed" / dataset_key
            dataset_path.mkdir(parents=True, exist_ok=True)
            
            # Télécharger selon le type
            success = False
            if dataset_info.get("status") == "available":
                success = self._download_standard_dataset(dataset_info, dataset_path)
            elif dataset_info.get("status") == "api_required":
                success = self._download_api_dataset(dataset_info, dataset_path)
            elif dataset_info.get("status") == "kaggle_api":
                success = self._download_kaggle_dataset(dataset_info, dataset_path)
            
            if success:
                # Enregistrer dans la base de données
                self._register_installed_dataset(dataset_key, dataset_info, dataset_path)
                print(f"✅ Dataset '{dataset_info['name']}' installé avec succès")
                return True
            else:
                print(f"❌ Échec de l'installation du dataset '{dataset_key}'")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de l'installation: {e}")
            return False
    
    def _find_dataset_info(self, dataset_key: str) -> Optional[Dict]:
        """Trouve les informations d'un dataset par sa clé"""
        for tier_name, tier_data in self.available_datasets.items():
            if tier_name == "tier_1_essential":
                if dataset_key in tier_data:
                    return tier_data[dataset_key]
            else:
                for specialty, specialty_datasets in tier_data.items():
                    if dataset_key in specialty_datasets:
                        return specialty_datasets[dataset_key]
        return None
    
    def _is_dataset_installed(self, dataset_key: str) -> bool:
        """Vérifie si un dataset est déjà installé"""
        with sqlite3.connect(self.global_db_path) as conn:
            cursor = conn.execute(
                "SELECT installed FROM datasets WHERE name = ?",
                (dataset_key,)
            )
            result = cursor.fetchone()
            return result and result[0]
    
    def _download_standard_dataset(self, dataset_info: Dict, dataset_path: Path) -> bool:
        """Télécharge un dataset standard via URL directe"""
        try:
            download_url = dataset_info.get("download_url")
            if not download_url:
                print("⚠️ URL de téléchargement non disponible")
                return False
            
            print(f"📥 Téléchargement depuis {download_url}")
            
            # Télécharger le fichier
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            # Sauvegarder le fichier
            filename = download_url.split("/")[-1]
            file_path = dataset_path / filename
            
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extraire si c'est un zip
            if filename.endswith(".zip"):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(dataset_path)
                os.remove(file_path)  # Supprimer le zip après extraction
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur téléchargement: {e}")
            return False
    
    def _download_api_dataset(self, dataset_info: Dict, dataset_path: Path) -> bool:
        """Télécharge un dataset via API (Roboflow, etc.)"""
        print("⚠️ Téléchargement API non encore implémenté")
        # TODO: Implémenter les connecteurs API
        return False
    
    def _download_kaggle_dataset(self, dataset_info: Dict, dataset_path: Path) -> bool:
        """Télécharge un dataset depuis Kaggle"""
        print("⚠️ Téléchargement Kaggle non encore implémenté")
        # TODO: Implémenter le connecteur Kaggle
        return False
    
    def _register_installed_dataset(self, dataset_key: str, dataset_info: Dict, dataset_path: Path):
        """Enregistre un dataset installé dans la base de données"""
        with sqlite3.connect(self.global_db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO datasets 
                (name, category, specialty, classes_count, images_count, format, 
                 download_url, status, priority, installed, install_date, size_mb)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dataset_key,
                dataset_info.get("specialty", "general"),
                dataset_info.get("specialty", ""),
                dataset_info.get("classes", 0),
                dataset_info.get("images", 0),
                dataset_info.get("format", "unknown"),
                dataset_info.get("download_url", ""),
                "installed",
                dataset_info.get("priority", 5),
                True,
                datetime.now(),
                self._calculate_folder_size(dataset_path)
            ))
    
    def _calculate_folder_size(self, folder_path: Path) -> float:
        """Calcule la taille d'un dossier en MB"""
        try:
            total_size = sum(f.stat().st_size for f in folder_path.rglob('*') if f.is_file())
            return total_size / (1024 * 1024)  # Convertir en MB
        except:
            return 0.0
    
    def get_installed_datasets(self) -> List[Dict]:
        """Retourne la liste des datasets installés"""
        with sqlite3.connect(self.global_db_path) as conn:
            cursor = conn.execute("""
                SELECT name, category, specialty, classes_count, images_count, 
                       format, install_date, size_mb
                FROM datasets 
                WHERE installed = TRUE
                ORDER BY priority, install_date DESC
            """)
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def install_essential_datasets(self) -> Dict[str, bool]:
        """Installe les datasets essentiels (Tier 1)"""
        results = {}
        essential_datasets = ["coco_dataset", "open_images"]
        
        print("🚀 Installation des datasets essentiels...")
        
        for dataset_key in essential_datasets:
            print(f"\n📦 Installation de {dataset_key}...")
            results[dataset_key] = self.install_dataset(dataset_key)
        
        return results
    
    def get_dataset_stats(self) -> Dict:
        """Retourne les statistiques des datasets"""
        with sqlite3.connect(self.global_db_path) as conn:
            # Statistiques globales
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_datasets,
                    SUM(CASE WHEN installed = TRUE THEN 1 ELSE 0 END) as installed_count,
                    SUM(classes_count) as total_classes,
                    SUM(images_count) as total_images,
                    SUM(size_mb) as total_size_mb
                FROM datasets
            """)
            global_stats = dict(zip([d[0] for d in cursor.description], cursor.fetchone()))
            
            # Statistiques par catégorie
            cursor = conn.execute("""
                SELECT category, COUNT(*) as count, SUM(classes_count) as classes
                FROM datasets 
                WHERE installed = TRUE
                GROUP BY category
            """)
            category_stats = [dict(zip([d[0] for d in cursor.description], row)) 
                            for row in cursor.fetchall()]
            
            return {
                "global": global_stats,
                "by_category": category_stats
            }

# Fonction utilitaire pour initialiser le gestionnaire
def create_dataset_manager(base_path: str = "datasets") -> DatasetManager:
    """Crée et initialise un gestionnaire de datasets"""
    return DatasetManager(base_path)

if __name__ == "__main__":
    # Test du gestionnaire
    manager = create_dataset_manager()
    
    print("📊 Datasets disponibles:")
    datasets = manager.get_available_datasets(priority=2)
    for dataset in datasets[:5]:  # Afficher les 5 premiers
        print(f"  • {dataset['name']} ({dataset.get('classes', 'N/A')} classes)")
    
    print(f"\n📈 Total: {len(datasets)} datasets disponibles")
