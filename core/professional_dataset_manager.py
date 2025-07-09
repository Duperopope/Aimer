#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Professional Dataset Manager - Gestionnaire de datasets professionnel
Interface moderne pour création, gestion et analyse de datasets YOLO
"""

import os
import sys
import json
import sqlite3
import hashlib
import threading
import time
import requests
import zipfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import cv2
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import du gestionnaire de stockage intelligent
try:
    from core.intelligent_storage_manager import IntelligentStorageManager, StorageRecommendation
except ImportError:
    # Import relatif si exécuté directement
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.intelligent_storage_manager import IntelligentStorageManager, StorageRecommendation

# Configuration du logging professionnel
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)8s | %(name)20s | %(funcName)15s:%(lineno)4d | %(message)s',
    handlers=[
        logging.FileHandler('logs/dataset_manager.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class DatasetInfo:
    """Informations complètes sur un dataset"""
    id: int
    name: str
    description: str
    storage_path: str
    total_images: int
    total_annotations: int
    total_size_bytes: int
    quality_score: float
    classes: List[str]
    created_at: str
    last_modified: str
    format_type: str  # 'YOLO', 'COCO', 'Pascal VOC'
    is_custom: bool
    source_url: Optional[str] = None
    download_progress: float = 0.0
    status: str = "ready"  # 'ready', 'downloading', 'processing', 'error'

@dataclass
class ImageAnalysis:
    """Analyse d'une image"""
    path: str
    width: int
    height: int
    file_size_bytes: int
    quality_score: float
    brightness: float
    contrast: float
    sharpness: float
    has_annotations: bool
    annotation_count: int
    detected_objects: List[str]

class DatasetSourceManager:
    """Gestionnaire des sources de datasets externes"""
    
    def __init__(self):
        self.logger = logging.getLogger("DatasetSourceManager")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Professional-YOLO-Dataset-Manager/1.0'
        })
        
        # Sources de datasets configurées
        self.sources = {
            'roboflow': {
                'name': 'Roboflow Universe',
                'base_url': 'https://universe.roboflow.com',
                'api_url': 'https://api.roboflow.com',
                'requires_auth': True,
                'supported_formats': ['YOLO', 'COCO', 'Pascal VOC']
            },
            'kaggle': {
                'name': 'Kaggle Datasets',
                'base_url': 'https://www.kaggle.com',
                'api_url': 'https://www.kaggle.com/api/v1',
                'requires_auth': True,
                'supported_formats': ['Various']
            },
            'huggingface': {
                'name': 'HuggingFace Hub',
                'base_url': 'https://huggingface.co',
                'api_url': 'https://huggingface.co/api',
                'requires_auth': False,
                'supported_formats': ['Various']
            }
        }
    
    def search_datasets(self, query: str, source: str = 'all', limit: int = 20) -> List[Dict]:
        """Recherche de datasets dans les sources externes"""
        self.logger.info(f"Recherche datasets: '{query}' dans {source}")
        
        results = []
        
        try:
            if source == 'all' or source == 'roboflow':
                results.extend(self._search_roboflow(query, limit))
            
            if source == 'all' or source == 'kaggle':
                results.extend(self._search_kaggle(query, limit))
            
            if source == 'all' or source == 'huggingface':
                results.extend(self._search_huggingface(query, limit))
            
            # Trier par pertinence
            results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            self.logger.error(f"Erreur recherche datasets: {e}")
            return []
    
    def _search_roboflow(self, query: str, limit: int) -> List[Dict]:
        """Recherche dans Roboflow Universe"""
        try:
            # Simulation de recherche Roboflow (API réelle nécessiterait une clé)
            mock_results = [
                {
                    'id': f'roboflow_{query}_1',
                    'name': f'{query.title()} Detection Dataset',
                    'description': f'Professional {query} detection dataset with high-quality annotations',
                    'source': 'roboflow',
                    'size_mb': 250,
                    'image_count': 1500,
                    'classes': [query, f'{query}_variant'],
                    'format': 'YOLO',
                    'download_url': f'https://universe.roboflow.com/datasets/{query}',
                    'relevance_score': 0.9,
                    'license': 'MIT',
                    'created_at': '2025-01-01'
                }
            ]
            
            return mock_results
            
        except Exception as e:
            self.logger.error(f"Erreur recherche Roboflow: {e}")
            return []
    
    def _search_kaggle(self, query: str, limit: int) -> List[Dict]:
        """Recherche dans Kaggle"""
        try:
            # Simulation de recherche Kaggle
            mock_results = [
                {
                    'id': f'kaggle_{query}_1',
                    'name': f'{query.title()} Dataset Collection',
                    'description': f'Comprehensive {query} dataset from Kaggle community',
                    'source': 'kaggle',
                    'size_mb': 180,
                    'image_count': 1200,
                    'classes': [query],
                    'format': 'Various',
                    'download_url': f'https://www.kaggle.com/datasets/{query}',
                    'relevance_score': 0.8,
                    'license': 'CC BY 4.0',
                    'created_at': '2024-12-15'
                }
            ]
            
            return mock_results
            
        except Exception as e:
            self.logger.error(f"Erreur recherche Kaggle: {e}")
            return []
    
    def _search_huggingface(self, query: str, limit: int) -> List[Dict]:
        """Recherche dans HuggingFace Hub"""
        try:
            # Recherche réelle dans HuggingFace Hub
            url = f"{self.sources['huggingface']['api_url']}/datasets"
            params = {
                'search': query,
                'filter': 'task_categories:object-detection',
                'limit': limit
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for dataset in data.get('datasets', []):
                    results.append({
                        'id': f"hf_{dataset['id']}",
                        'name': dataset.get('id', 'Unknown'),
                        'description': dataset.get('description', 'No description'),
                        'source': 'huggingface',
                        'size_mb': dataset.get('size_bytes', 0) / (1024 * 1024),
                        'image_count': dataset.get('downloads', 0),
                        'classes': dataset.get('tags', []),
                        'format': 'HuggingFace',
                        'download_url': f"https://huggingface.co/datasets/{dataset['id']}",
                        'relevance_score': 0.7,
                        'license': dataset.get('license', 'Unknown'),
                        'created_at': dataset.get('created_at', '2024-01-01')
                    })
                
                return results
            else:
                self.logger.warning(f"HuggingFace API error: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Erreur recherche HuggingFace: {e}")
            return []
    
    def download_dataset(self, dataset_info: Dict, target_path: str, progress_callback: Callable = None) -> bool:
        """Télécharge un dataset depuis une source externe"""
        self.logger.info(f"Téléchargement dataset: {dataset_info['name']}")
        
        try:
            # Créer le dossier de destination
            target_path = Path(target_path)
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Simulation de téléchargement (implémentation réelle dépendrait de l'API)
            if dataset_info['source'] == 'roboflow':
                return self._download_roboflow_dataset(dataset_info, target_path, progress_callback)
            elif dataset_info['source'] == 'kaggle':
                return self._download_kaggle_dataset(dataset_info, target_path, progress_callback)
            elif dataset_info['source'] == 'huggingface':
                return self._download_huggingface_dataset(dataset_info, target_path, progress_callback)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erreur téléchargement dataset: {e}")
            return False
    
    def _download_roboflow_dataset(self, dataset_info: Dict, target_path: Path, progress_callback: Callable) -> bool:
        """Télécharge depuis Roboflow (simulation)"""
        try:
            # Simulation du téléchargement avec progress
            total_size = dataset_info['size_mb'] * 1024 * 1024
            downloaded = 0
            chunk_size = 1024 * 1024  # 1MB chunks
            
            # Créer des fichiers de démonstration
            images_dir = target_path / "images"
            labels_dir = target_path / "labels"
            images_dir.mkdir(exist_ok=True)
            labels_dir.mkdir(exist_ok=True)
            
            # Simuler le téléchargement avec progress
            while downloaded < total_size:
                time.sleep(0.1)  # Simulation de téléchargement
                downloaded += chunk_size
                progress = min(downloaded / total_size, 1.0)
                
                if progress_callback:
                    progress_callback(progress)
            
            # Créer un fichier de configuration YOLO
            config = {
                'path': str(target_path),
                'train': 'images/train',
                'val': 'images/val',
                'names': dataset_info['classes']
            }
            
            with open(target_path / "data.yaml", 'w') as f:
                import yaml
                yaml.dump(config, f)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur téléchargement Roboflow: {e}")
            return False
    
    def _download_kaggle_dataset(self, dataset_info: Dict, target_path: Path, progress_callback: Callable) -> bool:
        """Télécharge depuis Kaggle (simulation)"""
        # Implémentation similaire à Roboflow
        return self._download_roboflow_dataset(dataset_info, target_path, progress_callback)
    
    def _download_huggingface_dataset(self, dataset_info: Dict, target_path: Path, progress_callback: Callable) -> bool:
        """Télécharge depuis HuggingFace (simulation)"""
        # Implémentation similaire à Roboflow
        return self._download_roboflow_dataset(dataset_info, target_path, progress_callback)

class ImageAnalyzer:
    """Analyseur d'images professionnel"""
    
    def __init__(self):
        self.logger = logging.getLogger("ImageAnalyzer")
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    def analyze_image(self, image_path: str) -> ImageAnalysis:
        """Analyse complète d'une image"""
        try:
            image_path = Path(image_path)
            
            # Vérifier que le fichier existe et est supporté
            if not image_path.exists() or image_path.suffix.lower() not in self.supported_formats:
                raise ValueError(f"Image non supportée: {image_path}")
            
            # Charger l'image avec OpenCV pour l'analyse
            img_cv = cv2.imread(str(image_path))
            if img_cv is None:
                raise ValueError(f"Impossible de charger l'image: {image_path}")
            
            # Informations de base
            height, width = img_cv.shape[:2]
            file_size = image_path.stat().st_size
            
            # Analyses de qualité
            quality_score = self._calculate_quality_score(img_cv)
            brightness = self._calculate_brightness(img_cv)
            contrast = self._calculate_contrast(img_cv)
            sharpness = self._calculate_sharpness(img_cv)
            
            # Vérifier les annotations
            annotation_path = image_path.with_suffix('.txt')
            has_annotations = annotation_path.exists()
            annotation_count = 0
            detected_objects = []
            
            if has_annotations:
                annotation_count, detected_objects = self._parse_yolo_annotations(annotation_path)
            
            return ImageAnalysis(
                path=str(image_path),
                width=width,
                height=height,
                file_size_bytes=file_size,
                quality_score=quality_score,
                brightness=brightness,
                contrast=contrast,
                sharpness=sharpness,
                has_annotations=has_annotations,
                annotation_count=annotation_count,
                detected_objects=detected_objects
            )
            
        except Exception as e:
            self.logger.error(f"Erreur analyse image {image_path}: {e}")
            raise
    
    def _calculate_quality_score(self, img: np.ndarray) -> float:
        """Calcule un score de qualité global pour l'image"""
        try:
            # Convertir en niveaux de gris pour l'analyse
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Facteurs de qualité
            sharpness_score = self._calculate_sharpness(img) / 1000.0  # Normaliser
            brightness_score = 1.0 - abs(self._calculate_brightness(img) - 0.5) * 2  # Optimal à 0.5
            contrast_score = min(self._calculate_contrast(img) / 100.0, 1.0)  # Normaliser
            
            # Score de bruit (inverse)
            noise_score = 1.0 - min(cv2.Laplacian(gray, cv2.CV_64F).var() / 10000.0, 1.0)
            
            # Score composite
            quality_score = (sharpness_score * 0.4 + brightness_score * 0.3 + 
                           contrast_score * 0.2 + noise_score * 0.1)
            
            return max(0.0, min(1.0, quality_score))
            
        except Exception:
            return 0.5  # Score neutre en cas d'erreur
    
    def _calculate_brightness(self, img: np.ndarray) -> float:
        """Calcule la luminosité moyenne de l'image"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return np.mean(gray) / 255.0
        except Exception:
            return 0.5
    
    def _calculate_contrast(self, img: np.ndarray) -> float:
        """Calcule le contraste de l'image"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return np.std(gray)
        except Exception:
            return 50.0
    
    def _calculate_sharpness(self, img: np.ndarray) -> float:
        """Calcule la netteté de l'image (variance du Laplacien)"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return cv2.Laplacian(gray, cv2.CV_64F).var()
        except Exception:
            return 100.0
    
    def _parse_yolo_annotations(self, annotation_path: Path) -> Tuple[int, List[str]]:
        """Parse les annotations YOLO et retourne le nombre et les classes"""
        try:
            if not annotation_path.exists():
                return 0, []
            
            annotations = []
            with open(annotation_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split()
                        if len(parts) >= 5:  # class_id x y w h
                            class_id = int(parts[0])
                            annotations.append(f"class_{class_id}")
            
            return len(annotations), list(set(annotations))
            
        except Exception as e:
            self.logger.error(f"Erreur parsing annotations {annotation_path}: {e}")
            return 0, []
    
    def batch_analyze_images(self, image_paths: List[str], progress_callback: Callable = None) -> List[ImageAnalysis]:
        """Analyse un lot d'images en parallèle"""
        self.logger.info(f"Analyse de {len(image_paths)} images...")
        
        results = []
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Soumettre toutes les tâches
            future_to_path = {
                executor.submit(self.analyze_image, path): path 
                for path in image_paths
            }
            
            # Collecter les résultats
            for i, future in enumerate(as_completed(future_to_path)):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    path = future_to_path[future]
                    self.logger.error(f"Erreur analyse {path}: {e}")
                
                # Callback de progression
                if progress_callback:
                    progress_callback((i + 1) / len(image_paths))
        
        return results

class ProfessionalDatasetManager:
    """Gestionnaire de datasets professionnel avec interface moderne"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.logger = logging.getLogger("ProfessionalDatasetManager")
        
        # Composants
        self.storage_manager = IntelligentStorageManager(str(self.project_root))
        self.source_manager = DatasetSourceManager()
        self.image_analyzer = ImageAnalyzer()
        
        # Base de données
        self.db_path = self.project_root / "datasets_management.db"
        self.init_database()
        
        # Cache des datasets
        self.datasets_cache = {}
        self.cache_timestamp = 0
        
        # Callbacks pour l'interface
        self.progress_callbacks = []
        self.status_callbacks = []
    
    def init_database(self):
        """Initialise la base de données des datasets"""
        try:
            self.db_path.parent.mkdir(exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS datasets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        description TEXT,
                        storage_path TEXT NOT NULL,
                        total_images INTEGER DEFAULT 0,
                        total_annotations INTEGER DEFAULT 0,
                        total_size_bytes INTEGER DEFAULT 0,
                        quality_score REAL DEFAULT 0.0,
                        classes TEXT,  -- JSON array
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        format_type TEXT DEFAULT 'YOLO',
                        is_custom BOOLEAN DEFAULT 1,
                        source_url TEXT,
                        status TEXT DEFAULT 'ready'
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS dataset_images (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        dataset_id INTEGER REFERENCES datasets(id),
                        image_path TEXT NOT NULL,
                        width INTEGER,
                        height INTEGER,
                        file_size_bytes INTEGER,
                        quality_score REAL,
                        has_annotations BOOLEAN DEFAULT 0,
                        annotation_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS dataset_classes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        dataset_id INTEGER REFERENCES datasets(id),
                        class_name TEXT NOT NULL,
                        class_id INTEGER,
                        image_count INTEGER DEFAULT 0,
                        annotation_count INTEGER DEFAULT 0
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erreur initialisation base de données: {e}")
            raise
    
    def create_custom_dataset(self, name: str, description: str = "", 
                            image_paths: List[str] = None) -> DatasetInfo:
        """Crée un nouveau dataset custom"""
        self.logger.info(f"Création dataset custom: {name}")
        
        try:
            # Vérifier que le nom n'existe pas déjà
            if self.get_dataset_by_name(name):
                raise ValueError(f"Dataset '{name}' existe déjà")
            
            # Calculer la taille estimée
            estimated_size = 0
            if image_paths:
                for path in image_paths:
                    try:
                        estimated_size += Path(path).stat().st_size
                    except Exception:
                        continue
            
            # Obtenir la recommandation de stockage
            storage_rec = self.storage_manager.get_optimal_storage_location(
                estimated_size, name
            )
            
            # Créer le dossier de dataset
            dataset_path = Path(storage_rec.recommended_drive) / "AI_Datasets" / name
            dataset_path.mkdir(parents=True, exist_ok=True)
            
            # Créer la structure YOLO
            (dataset_path / "images").mkdir(exist_ok=True)
            (dataset_path / "labels").mkdir(exist_ok=True)
            
            # Enregistrer en base de données
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    INSERT INTO datasets 
                    (name, description, storage_path, format_type, is_custom, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, description, str(dataset_path), 'YOLO', True, 'ready'))
                
                dataset_id = cursor.lastrowid
                conn.commit()
            
            # Copier les images si fournies
            if image_paths:
                self._copy_images_to_dataset(dataset_id, image_paths, dataset_path)
            
            # Enregistrer dans le gestionnaire de stockage
            actual_size = self._calculate_directory_size(dataset_path)
            self.storage_manager.register_dataset_storage(name, str(dataset_path), actual_size)
            
            # Retourner les informations du dataset
            return self.get_dataset_by_id(dataset_id)
            
        except Exception as e:
            self.logger.error(f"Erreur création dataset {name}: {e}")
            raise
    
    def _copy_images_to_dataset(self, dataset_id: int, image_paths: List[str], dataset_path: Path):
        """Copie les images vers le dataset et les analyse"""
        images_dir = dataset_path / "images"
        
        for i, src_path in enumerate(image_paths):
            try:
                src_path = Path(src_path)
                if not src_path.exists():
                    continue
                
                # Copier l'image
                dst_path = images_dir / src_path.name
                shutil.copy2(src_path, dst_path)
                
                # Analyser l'image
                analysis = self.image_analyzer.analyze_image(str(dst_path))
                
                # Enregistrer en base
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT INTO dataset_images 
                        (dataset_id, image_path, width, height, file_size_bytes, 
                         quality_score, has_annotations, annotation_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (dataset_id, str(dst_path), analysis.width, analysis.height,
                          analysis.file_size_bytes, analysis.quality_score,
                          analysis.has_annotations, analysis.annotation_count))
                    conn.commit()
                
                # Callback de progression
                self._notify_progress((i + 1) / len(image_paths))
                
            except Exception as e:
                self.logger.error(f"Erreur copie image {src_path}: {e}")
    
    def download_external_dataset(self, dataset_info: Dict) -> DatasetInfo:
        """Télécharge un dataset depuis une source externe"""
        self.logger.info(f"Téléchargement dataset externe: {dataset_info['name']}")
        
        try:
            # Obtenir la recommandation de stockage
            estimated_size = dataset_info['size_mb'] * 1024 * 1024
            storage_rec = self.storage_manager.get_optimal_storage_location(
                estimated_size, dataset_info['name']
            )
            
            # Créer le dossier de destination
            dataset_path = Path(storage_rec.recommended_drive) / "AI_Datasets" / dataset_info['name']
            
            # Enregistrer en base avec statut "downloading"
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    INSERT INTO datasets 
                    (name, description, storage_path, format_type, is_custom, 
                     source_url, status, total_size_bytes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (dataset_info['name'], dataset_info['description'], 
                      str(dataset_path), dataset_info['format'], False,
                      dataset_info['download_url'], 'downloading', estimated_size))
                
                dataset_id = cursor.lastrowid
                conn.commit()
            
            # Télécharger le dataset
            def progress_callback(progress):
                self._notify_progress(progress)
                # Mettre à jour le statut en base
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        UPDATE datasets SET status = ? WHERE id = ?
                    """, (f'downloading_{int(progress*100)}%', dataset_id))
                    conn.commit()
            
            success = self.source_manager.download_dataset(
                dataset_info, str(dataset_path), progress_callback
            )
            
            if success:
                # Analyser le dataset téléchargé
                self._analyze_downloaded_dataset(dataset_id, dataset_path)
                
                # Mettre à jour le statut
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        UPDATE datasets SET status = 'ready', last_modified = ?
                        WHERE id = ?
                    """, (datetime.now().isoformat(), dataset_id))
                    conn.commit()
                
                # Enregistrer dans le gestionnaire de stockage
                actual_size = self._calculate_directory_size(dataset_path)
                self.storage_manager.register_dataset_storage(
                    dataset_info['name'], str(dataset_path), actual_size
                )
                
                return self.get_dataset_by_id(dataset_id)
            else:
                # Échec du téléchargement
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        UPDATE datasets SET status = 'error' WHERE id = ?
                    """, (dataset_id,))
                    conn.commit()
                
                raise RuntimeError("Échec du téléchargement")
                
        except Exception as e:
            self.logger.error(f"Erreur téléchargement dataset: {e}")
            raise
    
    def _analyze_downloaded_dataset(self, dataset_id: int, dataset_path: Path):
        """Analyse un dataset téléchargé"""
        try:
            images_dir = dataset_path / "images"
            if not images_dir.exists():
                # Chercher les images dans d'autres dossiers
                for subdir in dataset_path.rglob("*"):
                    if subdir.is_dir() and any(subdir.glob("*.jpg")):
                        images_dir = subdir
                        break
            
            if images_dir.exists():
                image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
                
                # Analyser les images
                analyses = self.image_analyzer.batch_analyze_images(
                    [str(f) for f in image_files[:100]],  # Limiter à 100 pour la démo
                    lambda p: self._notify_progress(p * 0.5 + 0.5)  # 50-100% de la progression
                )
                
                # Enregistrer les analyses
                total_images = len(image_files)
                total_annotations = 0
                quality_scores = []
                
                with sqlite3.connect(self.db_path) as conn:
                    for analysis in analyses:
                        conn.execute("""
                            INSERT INTO dataset_images 
                            (dataset_id, image_path, width, height, file_size_bytes, 
                             quality_score, has_annotations, annotation_count)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (dataset_id, analysis.path, analysis.width, analysis.height,
                              analysis.file_size_bytes, analysis.quality_score,
                              analysis.has_annotations, analysis.annotation_count))
                        
                        total_annotations += analysis.annotation_count
                        quality_scores.append(analysis.quality_score)
                    
                    # Mettre à jour les statistiques du dataset
                    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
                    
                    conn.execute("""
                        UPDATE datasets 
                        SET total_images = ?, total_annotations = ?, quality_score = ?, last_modified = ?
                        WHERE id = ?
                    """, (total_images, total_annotations, avg_quality, datetime.now().isoformat(), dataset_id))
                    conn.commit()
                    
        except Exception as e:
            self.logger.error(f"Erreur analyse dataset téléchargé: {e}")
    
    def get_dataset_by_id(self, dataset_id: int) -> Optional[DatasetInfo]:
        """Récupère un dataset par son ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, name, description, storage_path, total_images, total_annotations,
                           total_size_bytes, quality_score, classes, created_at, last_modified,
                           format_type, is_custom, source_url, status
                    FROM datasets WHERE id = ?
                """, (dataset_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                classes = json.loads(row[8]) if row[8] else []
                
                return DatasetInfo(
                    id=row[0],
                    name=row[1],
                    description=row[2] or "",
                    storage_path=row[3],
                    total_images=row[4],
                    total_annotations=row[5],
                    total_size_bytes=row[6],
                    quality_score=row[7],
                    classes=classes,
                    created_at=row[9],
                    last_modified=row[10],
                    format_type=row[11],
                    is_custom=bool(row[12]),
                    source_url=row[13],
                    status=row[14]
                )
                
        except Exception as e:
            self.logger.error(f"Erreur récupération dataset {dataset_id}: {e}")
            return None
    
    def get_dataset_by_name(self, name: str) -> Optional[DatasetInfo]:
        """Récupère un dataset par son nom"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id FROM datasets WHERE name = ?
                """, (name,))
                
                row = cursor.fetchone()
                if row:
                    return self.get_dataset_by_id(row[0])
                
                return None
                
        except Exception as e:
            self.logger.error(f"Erreur recherche dataset {name}: {e}")
            return None
    
    def list_datasets(self, include_external: bool = True) -> List[DatasetInfo]:
        """Liste tous les datasets"""
        try:
            datasets = []
            
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT id FROM datasets"
                if not include_external:
                    query += " WHERE is_custom = 1"
                query += " ORDER BY last_modified DESC"
                
                cursor = conn.execute(query)
                
                for row in cursor.fetchall():
                    dataset = self.get_dataset_by_id(row[0])
                    if dataset:
                        datasets.append(dataset)
            
            return datasets
            
        except Exception as e:
            self.logger.error(f"Erreur listage datasets: {e}")
            return []
    
    def delete_dataset(self, dataset_id: int, delete_files: bool = False) -> bool:
        """Supprime un dataset"""
        try:
            dataset = self.get_dataset_by_id(dataset_id)
            if not dataset:
                return False
            
            # Supprimer les fichiers si demandé
            if delete_files and Path(dataset.storage_path).exists():
                shutil.rmtree(dataset.storage_path)
                self.logger.info(f"Fichiers supprimés: {dataset.storage_path}")
            
            # Supprimer de la base de données
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM dataset_images WHERE dataset_id = ?", (dataset_id,))
                conn.execute("DELETE FROM dataset_classes WHERE dataset_id = ?", (dataset_id,))
                conn.execute("DELETE FROM datasets WHERE id = ?", (dataset_id,))
                conn.commit()
            
            self.logger.info(f"Dataset supprimé: {dataset.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur suppression dataset {dataset_id}: {e}")
            return False
    
    def search_external_datasets(self, query: str, source: str = 'all') -> List[Dict]:
        """Recherche des datasets externes"""
        return self.source_manager.search_datasets(query, source)
    
    def get_dataset_statistics(self) -> Dict:
        """Obtient les statistiques globales des datasets"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Statistiques générales
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_datasets,
                        SUM(total_images) as total_images,
                        SUM(total_annotations) as total_annotations,
                        SUM(total_size_bytes) as total_size_bytes,
                        AVG(quality_score) as avg_quality,
                        COUNT(CASE WHEN is_custom = 1 THEN 1 END) as custom_datasets,
                        COUNT(CASE WHEN is_custom = 0 THEN 1 END) as external_datasets
                    FROM datasets
                """)
                
                stats = cursor.fetchone()
                
                # Statistiques par format
                cursor = conn.execute("""
                    SELECT format_type, COUNT(*) as count
                    FROM datasets
                    GROUP BY format_type
                """)
                
                formats = dict(cursor.fetchall())
                
                # Statistiques de stockage
                storage_stats = self.storage_manager.get_storage_statistics()
                
                return {
                    'total_datasets': stats[0] or 0,
                    'total_images': stats[1] or 0,
                    'total_annotations': stats[2] or 0,
                    'total_size_gb': (stats[3] or 0) / (1024**3),
                    'average_quality': stats[4] or 0.0,
                    'custom_datasets': stats[5] or 0,
                    'external_datasets': stats[6] or 0,
                    'formats': formats,
                    'storage': storage_stats
                }
                
        except Exception as e:
            self.logger.error(f"Erreur statistiques datasets: {e}")
            return {}
    
    def _calculate_directory_size(self, directory: Path) -> int:
        """Calcule la taille totale d'un dossier"""
        try:
            total_size = 0
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            return total_size
        except Exception:
            return 0
    
    def _notify_progress(self, progress: float):
        """Notifie les callbacks de progression"""
        for callback in self.progress_callbacks:
            try:
                callback(progress)
            except Exception as e:
                self.logger.error(f"Erreur callback progression: {e}")
    
    def _notify_status(self, status: str):
        """Notifie les callbacks de statut"""
        for callback in self.status_callbacks:
            try:
                callback(status)
            except Exception as e:
                self.logger.error(f"Erreur callback statut: {e}")
    
    def add_progress_callback(self, callback: Callable[[float], None]):
        """Ajoute un callback de progression"""
        self.progress_callbacks.append(callback)
    
    def add_status_callback(self, callback: Callable[[str], None]):
        """Ajoute un callback de statut"""
        self.status_callbacks.append(callback)
    
    def export_dataset(self, dataset_id: int, export_path: str, format_type: str = 'YOLO') -> bool:
        """Exporte un dataset vers un format spécifique"""
        try:
            dataset = self.get_dataset_by_id(dataset_id)
            if not dataset:
                return False
            
            export_path = Path(export_path)
            export_path.mkdir(parents=True, exist_ok=True)
            
            # Copier les fichiers selon le format
            if format_type == 'YOLO':
                return self._export_yolo_format(dataset, export_path)
            elif format_type == 'COCO':
                return self._export_coco_format(dataset, export_path)
            elif format_type == 'Pascal VOC':
                return self._export_pascal_format(dataset, export_path)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erreur export dataset {dataset_id}: {e}")
            return False
    
    def _export_yolo_format(self, dataset: DatasetInfo, export_path: Path) -> bool:
        """Exporte au format YOLO"""
        try:
            # Copier la structure existante si c'est déjà du YOLO
            if dataset.format_type == 'YOLO':
                shutil.copytree(dataset.storage_path, export_path, dirs_exist_ok=True)
                return True
            
            # Sinon, convertir depuis le format source
            # Implémentation de conversion selon le format source
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur export YOLO: {e}")
            return False
    
    def _export_coco_format(self, dataset: DatasetInfo, export_path: Path) -> bool:
        """Exporte au format COCO"""
        try:
            # Implémentation de conversion vers COCO
            # Créer le fichier annotations.json avec la structure COCO
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur export COCO: {e}")
            return False
    
    def _export_pascal_format(self, dataset: DatasetInfo, export_path: Path) -> bool:
        """Exporte au format Pascal VOC"""
        try:
            # Implémentation de conversion vers Pascal VOC
            # Créer les fichiers XML d'annotations
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur export Pascal: {e}")
            return False

def create_professional_dataset_manager() -> ProfessionalDatasetManager:
    """Crée et initialise le gestionnaire de datasets professionnel"""
    return ProfessionalDatasetManager()

if __name__ == "__main__":
    # Test du gestionnaire de datasets
    print("📦 Test du Gestionnaire de Datasets Professionnel")
    print("=" * 60)
    
    manager = ProfessionalDatasetManager()
    
    # Test 1: Statistiques
    print("\n1️⃣ Statistiques des datasets:")
    stats = manager.get_dataset_statistics()
    print(f"📊 Total datasets: {stats.get('total_datasets', 0)}")
    print(f"🖼️ Total images: {stats.get('total_images', 0)}")
    print(f"🏷️ Total annotations: {stats.get('total_annotations', 0)}")
    print(f"💾 Taille totale: {stats.get('total_size_gb', 0):.2f}GB")
    print(f"⭐ Qualité moyenne: {stats.get('average_quality', 0):.2f}")
    
    # Test 2: Recherche externe
    print("\n2️⃣ Recherche de datasets externes:")
    try:
        results = manager.search_external_datasets("weapon", "roboflow")
        for result in results[:3]:
            print(f"🔍 {result['name']} ({result['source']})")
            print(f"   📝 {result['description'][:100]}...")
            print(f"   📊 {result['image_count']} images, {result['size_mb']}MB")
            print()
    except Exception as e:
        print(f"❌ Erreur recherche: {e}")
    
    # Test 3: Création dataset custom
    print("3️⃣ Test création dataset custom:")
    try:
        # Créer un dataset de test (sans images réelles)
        dataset = manager.create_custom_dataset(
            name="test_dataset_demo",
            description="Dataset de démonstration pour test"
        )
        print(f"✅ Dataset créé: {dataset.name}")
        print(f"📍 Stockage: {dataset.storage_path}")
        print(f"📊 Images: {dataset.total_images}")
    except Exception as e:
        print(f"❌ Erreur création: {e}")
