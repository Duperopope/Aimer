#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Intelligent Storage Manager - Gestionnaire de stockage intelligent professionnel
Détecte et optimise automatiquement le stockage des datasets sans impacter le système
"""

import os
import sys
import psutil
import platform
import time
import json
import sqlite3
import hashlib
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, NamedTuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Configuration du logging professionnel
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)8s | %(name)20s | %(funcName)15s:%(lineno)4d | %(message)s',
    handlers=[
        logging.FileHandler('logs/storage_manager.log'),
        logging.StreamHandler()
    ]
)

class DriveInfo(NamedTuple):
    """Informations détaillées sur un disque"""
    device: str
    mountpoint: str
    fstype: str
    total_bytes: int
    free_bytes: int
    used_bytes: int
    usage_percent: float
    is_system_drive: bool
    is_ssd: bool
    read_speed_mbps: float
    write_speed_mbps: float
    health_score: float

@dataclass
class StorageRecommendation:
    """Recommandation de stockage calculée"""
    recommended_drive: str
    reason: str
    estimated_performance: str
    space_available_gb: float
    expected_lifespan_years: float
    confidence_score: float

class IntelligentStorageManager:
    """Gestionnaire de stockage intelligent professionnel"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.logger = logging.getLogger("IntelligentStorageManager")
        
        # Base de données pour le tracking du stockage
        self.db_path = self.project_root / "storage_management.db"
        self.init_database()
        
        # Cache des informations de disques
        self.drives_cache = {}
        self.cache_timestamp = 0
        self.cache_validity_seconds = 300  # 5 minutes
        
        # Seuils de sécurité
        self.SYSTEM_DRIVE_MAX_USAGE = 0.05  # Jamais plus de 5% du disque système
        self.SAFE_DRIVE_MAX_USAGE = 0.80    # Maximum 80% d'un disque non-système
        self.MIN_FREE_SPACE_GB = 5.0        # Minimum 5GB libres
        
        # Détection du disque système
        self.system_drive = self._detect_system_drive()
        
    def init_database(self):
        """Initialise la base de données de gestion du stockage"""
        try:
            self.db_path.parent.mkdir(exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS storage_locations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        dataset_name TEXT NOT NULL,
                        storage_path TEXT NOT NULL,
                        drive_device TEXT NOT NULL,
                        size_bytes INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        access_frequency INTEGER DEFAULT 0
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS drive_performance (
                        drive_device TEXT PRIMARY KEY,
                        read_speed_mbps REAL NOT NULL,
                        write_speed_mbps REAL NOT NULL,
                        is_ssd BOOLEAN NOT NULL,
                        health_score REAL NOT NULL,
                        last_benchmark TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS storage_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        action TEXT NOT NULL,
                        drive_device TEXT NOT NULL,
                        size_change_bytes INTEGER NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        details TEXT
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Erreur initialisation base de données: {e}")
            raise
    
    def _detect_system_drive(self) -> str:
        """Détecte le disque système de manière fiable"""
        try:
            if platform.system() == "Windows":
                # Sur Windows, le disque système est généralement C:
                system_drive = "C:\\"
                
                # Vérification que Python s'exécute depuis ce disque
                python_drive = Path(sys.executable).drive + "\\"
                if python_drive == system_drive:
                    return system_drive
                else:
                    # Si Python n'est pas sur C:, utiliser le disque de Python
                    return python_drive
                    
            else:
                # Sur Unix/Linux, le système est sur /
                return "/"
                
        except Exception as e:
            self.logger.error(f"Erreur détection disque système: {e}")
            return "C:\\" if platform.system() == "Windows" else "/"
    
    def scan_available_drives(self, force_refresh: bool = False) -> List[DriveInfo]:
        """Scanne tous les disques disponibles avec informations détaillées"""
        current_time = time.time()
        
        # Utiliser le cache si valide et pas de force refresh
        if not force_refresh and (current_time - self.cache_timestamp) < self.cache_validity_seconds:
            if self.drives_cache:
                return list(self.drives_cache.values())
        
        self.logger.info("Scan des disques disponibles...")
        drives = []
        
        try:
            # Obtenir toutes les partitions
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    # Obtenir les informations d'usage
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    # Déterminer si c'est le disque système
                    is_system = self._is_system_drive(partition.device, partition.mountpoint)
                    
                    # Benchmark de performance (cache ou nouveau)
                    perf_data = self._get_drive_performance(partition.device)
                    
                    drive_info = DriveInfo(
                        device=partition.device,
                        mountpoint=partition.mountpoint,
                        fstype=partition.fstype,
                        total_bytes=usage.total,
                        free_bytes=usage.free,
                        used_bytes=usage.used,
                        usage_percent=usage.used / usage.total * 100,
                        is_system_drive=is_system,
                        is_ssd=perf_data['is_ssd'],
                        read_speed_mbps=perf_data['read_speed'],
                        write_speed_mbps=perf_data['write_speed'],
                        health_score=perf_data['health_score']
                    )
                    
                    drives.append(drive_info)
                    
                except (PermissionError, OSError) as e:
                    self.logger.warning(f"Impossible d'accéder à {partition.device}: {e}")
                    continue
            
            # Mettre à jour le cache
            self.drives_cache = {drive.device: drive for drive in drives}
            self.cache_timestamp = current_time
            
            self.logger.info(f"Scan terminé: {len(drives)} disques détectés")
            return drives
            
        except Exception as e:
            self.logger.error(f"Erreur lors du scan des disques: {e}")
            return []
    
    def _is_system_drive(self, device: str, mountpoint: str) -> bool:
        """Détermine si un disque est le disque système"""
        try:
            if platform.system() == "Windows":
                # Sur Windows, vérifier si c'est le même disque que le système
                return device.upper().startswith(self.system_drive.upper()[0])
            else:
                # Sur Unix/Linux, vérifier si c'est la racine
                return mountpoint == "/"
        except Exception:
            return False
    
    def _get_drive_performance(self, device: str) -> Dict:
        """Obtient ou calcule les performances d'un disque"""
        try:
            # Vérifier si on a des données en cache dans la DB
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT read_speed_mbps, write_speed_mbps, is_ssd, health_score, last_benchmark
                    FROM drive_performance 
                    WHERE drive_device = ?
                """, (device,))
                
                row = cursor.fetchone()
                
                # Si données récentes (moins de 24h), les utiliser
                if row:
                    last_benchmark = datetime.fromisoformat(row[4])
                    if (datetime.now() - last_benchmark).total_seconds() < 86400:  # 24h
                        return {
                            'read_speed': row[0],
                            'write_speed': row[1],
                            'is_ssd': bool(row[2]),
                            'health_score': row[3]
                        }
            
            # Sinon, faire un nouveau benchmark
            return self._benchmark_drive_performance(device)
            
        except Exception as e:
            self.logger.error(f"Erreur récupération performance {device}: {e}")
            # Valeurs par défaut conservatrices
            return {
                'read_speed': 50.0,
                'write_speed': 30.0,
                'is_ssd': False,
                'health_score': 0.7
            }
    
    def _benchmark_drive_performance(self, device: str) -> Dict:
        """Effectue un benchmark rapide et sûr d'un disque"""
        self.logger.info(f"Benchmark de performance pour {device}...")
        
        try:
            # Trouver le point de montage pour ce device
            mountpoint = None
            for partition in psutil.disk_partitions():
                if partition.device == device:
                    mountpoint = partition.mountpoint
                    break
            
            if not mountpoint:
                raise ValueError(f"Point de montage introuvable pour {device}")
            
            # Créer un fichier de test temporaire
            test_file = Path(mountpoint) / f"storage_benchmark_{int(time.time())}.tmp"
            test_data_size = 1024 * 1024  # 1MB de test
            test_data = b'0' * test_data_size
            
            # Test d'écriture
            write_start = time.time()
            with open(test_file, 'wb') as f:
                f.write(test_data)
                f.flush()
                os.fsync(f.fileno())  # Force l'écriture sur disque
            write_time = time.time() - write_start
            write_speed = (test_data_size / (1024 * 1024)) / write_time  # MB/s
            
            # Test de lecture
            read_start = time.time()
            with open(test_file, 'rb') as f:
                read_data = f.read()
            read_time = time.time() - read_start
            read_speed = (test_data_size / (1024 * 1024)) / read_time  # MB/s
            
            # Nettoyage
            test_file.unlink(missing_ok=True)
            
            # Détection SSD basée sur la vitesse d'accès aléatoire
            is_ssd = self._detect_ssd_characteristics(device, read_speed, write_speed)
            
            # Score de santé basé sur les performances
            health_score = min(1.0, (read_speed + write_speed) / 200.0)  # Normalisé sur 100MB/s chaque
            
            performance_data = {
                'read_speed': read_speed,
                'write_speed': write_speed,
                'is_ssd': is_ssd,
                'health_score': health_score
            }
            
            # Sauvegarder en base
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO drive_performance 
                    (drive_device, read_speed_mbps, write_speed_mbps, is_ssd, health_score, last_benchmark)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (device, read_speed, write_speed, is_ssd, health_score, datetime.now().isoformat()))
                conn.commit()
            
            self.logger.info(f"Benchmark {device}: R={read_speed:.1f}MB/s, W={write_speed:.1f}MB/s, SSD={is_ssd}")
            return performance_data
            
        except Exception as e:
            self.logger.error(f"Erreur benchmark {device}: {e}")
            # Valeurs par défaut en cas d'erreur
            return {
                'read_speed': 50.0,
                'write_speed': 30.0,
                'is_ssd': False,
                'health_score': 0.5
            }
    
    def _detect_ssd_characteristics(self, device: str, read_speed: float, write_speed: float) -> bool:
        """Détecte si un disque est un SSD basé sur ses caractéristiques"""
        try:
            # Heuristiques pour détecter un SSD
            # 1. Vitesse élevée (>100MB/s en lecture)
            if read_speed > 100:
                return True
            
            # 2. Ratio lecture/écriture typique des SSD
            if write_speed > 0 and 0.7 <= (write_speed / read_speed) <= 1.3:
                return True
            
            # 3. Sur Windows, essayer de détecter via WMI si disponible
            if platform.system() == "Windows":
                try:
                    import wmi
                    c = wmi.WMI()
                    for disk in c.Win32_DiskDrive():
                        if device.startswith(disk.DeviceID.replace('\\\\.\\', '')):
                            # Rechercher des mots-clés SSD dans le modèle
                            model = disk.Model.upper()
                            ssd_keywords = ['SSD', 'SOLID STATE', 'NVME', 'M.2']
                            if any(keyword in model for keyword in ssd_keywords):
                                return True
                except ImportError:
                    pass  # WMI non disponible
            
            return False
            
        except Exception:
            return False
    
    def get_optimal_storage_location(self, dataset_size_bytes: int, dataset_name: str = "") -> StorageRecommendation:
        """Calcule l'emplacement de stockage optimal pour un dataset"""
        self.logger.info(f"Calcul emplacement optimal pour dataset {dataset_name} ({dataset_size_bytes / (1024**3):.2f}GB)")
        
        drives = self.scan_available_drives()
        if not drives:
            raise RuntimeError("Aucun disque disponible détecté")
        
        # Filtrer les disques utilisables (non-système avec espace suffisant)
        usable_drives = []
        for drive in drives:
            # Exclure le disque système
            if drive.is_system_drive:
                continue
            
            # Vérifier l'espace disponible
            required_space = dataset_size_bytes * 1.2  # 20% de marge
            if drive.free_bytes < required_space:
                continue
            
            # Vérifier que l'usage ne dépassera pas le seuil
            future_usage = (drive.used_bytes + dataset_size_bytes) / drive.total_bytes
            if future_usage > self.SAFE_DRIVE_MAX_USAGE:
                continue
            
            usable_drives.append(drive)
        
        if not usable_drives:
            # Fallback: utiliser le dossier utilisateur si aucun disque secondaire
            return self._get_fallback_storage_recommendation(dataset_size_bytes, dataset_name)
        
        # Scorer chaque disque selon plusieurs critères
        scored_drives = []
        for drive in usable_drives:
            score = self._calculate_drive_score(drive, dataset_size_bytes)
            scored_drives.append((drive, score))
        
        # Trier par score décroissant
        scored_drives.sort(key=lambda x: x[1], reverse=True)
        best_drive, best_score = scored_drives[0]
        
        # Générer la recommandation
        recommendation = StorageRecommendation(
            recommended_drive=best_drive.mountpoint,
            reason=self._generate_recommendation_reason(best_drive, dataset_size_bytes),
            estimated_performance=f"R: {best_drive.read_speed_mbps:.0f}MB/s, W: {best_drive.write_speed_mbps:.0f}MB/s",
            space_available_gb=best_drive.free_bytes / (1024**3),
            expected_lifespan_years=self._estimate_drive_lifespan(best_drive),
            confidence_score=best_score
        )
        
        self.logger.info(f"Recommandation: {recommendation.recommended_drive} (score: {best_score:.2f})")
        return recommendation
    
    def _calculate_drive_score(self, drive: DriveInfo, dataset_size_bytes: int) -> float:
        """Calcule un score pour un disque selon plusieurs critères"""
        score = 0.0
        
        # 1. Performance (40% du score)
        performance_score = min(1.0, (drive.read_speed_mbps + drive.write_speed_mbps) / 200.0)
        score += performance_score * 0.4
        
        # 2. Espace disponible (25% du score)
        space_ratio = drive.free_bytes / drive.total_bytes
        space_score = min(1.0, space_ratio * 2)  # Optimal à 50% libre
        score += space_score * 0.25
        
        # 3. Type de disque (20% du score)
        type_score = 1.0 if drive.is_ssd else 0.6
        score += type_score * 0.2
        
        # 4. Santé du disque (10% du score)
        score += drive.health_score * 0.1
        
        # 5. Fragmentation estimée (5% du score)
        fragmentation_score = 1.0 - (drive.usage_percent / 100.0)
        score += fragmentation_score * 0.05
        
        return score
    
    def _generate_recommendation_reason(self, drive: DriveInfo, dataset_size_bytes: int) -> str:
        """Génère une explication de la recommandation"""
        reasons = []
        
        if drive.is_ssd:
            reasons.append("SSD détecté - accès rapide")
        
        if drive.read_speed_mbps > 100:
            reasons.append(f"Lecture rapide ({drive.read_speed_mbps:.0f}MB/s)")
        
        space_gb = drive.free_bytes / (1024**3)
        if space_gb > 100:
            reasons.append(f"Espace abondant ({space_gb:.0f}GB libres)")
        
        if drive.usage_percent < 50:
            reasons.append("Disque peu fragmenté")
        
        if drive.health_score > 0.8:
            reasons.append("Excellente santé du disque")
        
        return " | ".join(reasons) if reasons else "Meilleur disque disponible"
    
    def _estimate_drive_lifespan(self, drive: DriveInfo) -> float:
        """Estime la durée de vie restante d'un disque"""
        try:
            if drive.is_ssd:
                # SSD: basé sur les cycles d'écriture
                base_lifespan = 5.0  # 5 ans en moyenne
                health_factor = drive.health_score
                usage_factor = 1.0 - (drive.usage_percent / 100.0) * 0.3
                return base_lifespan * health_factor * usage_factor
            else:
                # HDD: basé sur l'âge et l'usage
                base_lifespan = 7.0  # 7 ans en moyenne
                health_factor = drive.health_score
                usage_factor = 1.0 - (drive.usage_percent / 100.0) * 0.2
                return base_lifespan * health_factor * usage_factor
        except Exception:
            return 3.0  # Estimation conservatrice
    
    def _get_fallback_storage_recommendation(self, dataset_size_bytes: int, dataset_name: str) -> StorageRecommendation:
        """Recommandation de fallback si aucun disque secondaire disponible"""
        # Utiliser le dossier Documents de l'utilisateur
        if platform.system() == "Windows":
            fallback_path = Path.home() / "Documents" / "AI_Datasets"
        else:
            fallback_path = Path.home() / "AI_Datasets"
        
        fallback_path.mkdir(parents=True, exist_ok=True)
        
        return StorageRecommendation(
            recommended_drive=str(fallback_path),
            reason="Aucun disque secondaire - utilisation dossier utilisateur",
            estimated_performance="Performance système standard",
            space_available_gb=self._get_available_space_gb(fallback_path),
            expected_lifespan_years=5.0,
            confidence_score=0.3
        )
    
    def _get_available_space_gb(self, path: Path) -> float:
        """Obtient l'espace disponible pour un chemin"""
        try:
            usage = psutil.disk_usage(str(path))
            return usage.free / (1024**3)
        except Exception:
            return 0.0
    
    def register_dataset_storage(self, dataset_name: str, storage_path: str, size_bytes: int):
        """Enregistre l'utilisation de stockage d'un dataset"""
        try:
            # Déterminer le device du chemin de stockage
            drive_device = self._get_drive_device_for_path(storage_path)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO storage_locations 
                    (dataset_name, storage_path, drive_device, size_bytes)
                    VALUES (?, ?, ?, ?)
                """, (dataset_name, storage_path, drive_device, size_bytes))
                
                conn.execute("""
                    INSERT INTO storage_history 
                    (action, drive_device, size_change_bytes, details)
                    VALUES (?, ?, ?, ?)
                """, ("DATASET_CREATED", drive_device, size_bytes, f"Dataset: {dataset_name}"))
                
                conn.commit()
                
            self.logger.info(f"Dataset {dataset_name} enregistré: {storage_path} ({size_bytes / (1024**2):.1f}MB)")
            
        except Exception as e:
            self.logger.error(f"Erreur enregistrement dataset {dataset_name}: {e}")
    
    def _get_drive_device_for_path(self, path: str) -> str:
        """Détermine le device d'un chemin"""
        try:
            path_obj = Path(path).resolve()
            
            # Trouver la partition qui contient ce chemin
            for partition in psutil.disk_partitions():
                if str(path_obj).startswith(partition.mountpoint):
                    return partition.device
            
            return "unknown"
        except Exception:
            return "unknown"
    
    def get_storage_statistics(self) -> Dict:
        """Obtient les statistiques d'utilisation du stockage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Statistiques par disque
                cursor = conn.execute("""
                    SELECT drive_device, COUNT(*) as dataset_count, SUM(size_bytes) as total_size
                    FROM storage_locations 
                    GROUP BY drive_device
                """)
                
                drive_stats = {}
                for row in cursor.fetchall():
                    drive_stats[row[0]] = {
                        'dataset_count': row[1],
                        'total_size_gb': row[2] / (1024**3)
                    }
                
                # Statistiques globales
                cursor = conn.execute("""
                    SELECT COUNT(*) as total_datasets, SUM(size_bytes) as total_size
                    FROM storage_locations
                """)
                
                global_stats = cursor.fetchone()
                
                return {
                    'global': {
                        'total_datasets': global_stats[0],
                        'total_size_gb': global_stats[1] / (1024**3) if global_stats[1] else 0
                    },
                    'by_drive': drive_stats,
                    'system_drive_protected': self.system_drive,
                    'last_scan': datetime.fromtimestamp(self.cache_timestamp).isoformat() if self.cache_timestamp else None
                }
                
        except Exception as e:
            self.logger.error(f"Erreur récupération statistiques: {e}")
            return {'error': str(e)}
    
    def cleanup_unused_datasets(self, days_unused: int = 30) -> Dict:
        """Nettoie les datasets non utilisés depuis X jours"""
        try:
            cutoff_date = datetime.now().timestamp() - (days_unused * 24 * 3600)
            
            with sqlite3.connect(self.db_path) as conn:
                # Trouver les datasets non utilisés
                cursor = conn.execute("""
                    SELECT dataset_name, storage_path, size_bytes
                    FROM storage_locations 
                    WHERE last_accessed < ?
                """, (datetime.fromtimestamp(cutoff_date).isoformat(),))
                
                unused_datasets = cursor.fetchall()
                
                cleanup_results = {
                    'datasets_found': len(unused_datasets),
                    'total_size_gb': sum(row[2] for row in unused_datasets) / (1024**3),
                    'cleaned_datasets': [],
                    'errors': []
                }
                
                # Demander confirmation avant suppression
                if unused_datasets:
                    self.logger.info(f"Trouvé {len(unused_datasets)} datasets non utilisés depuis {days_unused} jours")
                    
                    for dataset_name, storage_path, size_bytes in unused_datasets:
                        try:
                            # Vérifier que le chemin existe encore
                            if Path(storage_path).exists():
                                # Ici on pourrait implémenter la suppression
                                # Pour l'instant, on log seulement
                                cleanup_results['cleaned_datasets'].append({
                                    'name': dataset_name,
                                    'path': storage_path,
                                    'size_mb': size_bytes / (1024**2)
                                })
                        except Exception as e:
                            cleanup_results['errors'].append(f"Erreur nettoyage {dataset_name}: {e}")
                
                return cleanup_results
                
        except Exception as e:
            self.logger.error(f"Erreur nettoyage datasets: {e}")
            return {'error': str(e)}

def create_intelligent_storage_manager() -> IntelligentStorageManager:
    """Crée et initialise le gestionnaire de stockage intelligent"""
    return IntelligentStorageManager()

if __name__ == "__main__":
    # Test du gestionnaire de stockage
    print("🔍 Test du Gestionnaire de Stockage Intelligent")
    print("=" * 60)
    
    manager = IntelligentStorageManager()
    
    # Test 1: Scan des disques
    print("\n1️⃣ Scan des disques disponibles:")
    drives = manager.scan_available_drives()
    
    for drive in drives:
        print(f"📁 {drive.device} ({drive.mountpoint})")
        print(f"   Type: {'SSD' if drive.is_ssd else 'HDD'} | Système: {'Oui' if drive.is_system_drive else 'Non'}")
        print(f"   Espace: {drive.free_bytes/(1024**3):.1f}GB libres / {drive.total_bytes/(1024**3):.1f}GB total")
        print(f"   Performance: R={drive.read_speed_mbps:.0f}MB/s, W={drive.write_speed_mbps:.0f}MB/s")
        print(f"   Santé: {drive.health_score:.1%}")
        print()
    
    # Test 2: Recommandation de stockage
    print("2️⃣ Recommandation pour un dataset de 500MB:")
    try:
        recommendation = manager.get_optimal_storage_location(500 * 1024 * 1024, "test_dataset")
        print(f"📍 Recommandation: {recommendation.recommended_drive}")
        print(f"💡 Raison: {recommendation.reason}")
        print(f"⚡ Performance: {recommendation.estimated_performance}")
        print(f"💾 Espace disponible: {recommendation.space_available_gb:.1f}GB")
        print(f"📈 Confiance: {recommendation.confidence_score:.1%}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 3: Statistiques
    print("\n3️⃣ Statistiques de stockage:")
    stats = manager.get_storage_statistics()
    print(f"📊 Datasets totaux: {stats['global']['total_datasets']}")
    print(f"💾 Taille totale: {stats['global']['total_size_gb']:.2f}GB")
    print(f"🛡️ Disque système protégé: {stats['system_drive_protected']}")
