#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Progress Manager - Système de progression avancé pour AIMER PRO
Gestion des téléchargements avec barres de progression animées et notifications
"""

import threading
import time
import requests
import os
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
from pathlib import Path

class ProgressStatus(Enum):
    """États possibles d'une tâche de progression"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ProgressMetrics:
    """Métriques de progression d'une tâche"""
    total_size: int = 0
    downloaded_size: int = 0
    progress_percent: float = 0.0
    speed_bps: float = 0.0
    speed_mbps: float = 0.0
    eta_seconds: Optional[int] = None
    elapsed_seconds: float = 0.0
    start_time: Optional[datetime] = None
    last_update: Optional[datetime] = None

@dataclass
class ProgressTask:
    """Tâche de progression avec toutes ses informations"""
    task_id: str
    name: str
    description: str
    status: ProgressStatus = ProgressStatus.PENDING
    metrics: ProgressMetrics = field(default_factory=ProgressMetrics)
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    callbacks: List[Callable] = field(default_factory=list)
    
    # Données spécifiques au téléchargement
    url: Optional[str] = None
    destination: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Contrôle de la tâche
    cancel_event: threading.Event = field(default_factory=threading.Event)
    pause_event: threading.Event = field(default_factory=threading.Event)

class ProgressManager:
    """Gestionnaire principal des tâches de progression"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tasks: Dict[str, ProgressTask] = {}
        self.active_downloads: Dict[str, threading.Thread] = {}
        self.global_callbacks: List[Callable] = []
        
        # Configuration
        self.chunk_size = 8192  # 8KB par chunk
        self.update_interval = 0.1  # Mise à jour toutes les 100ms
        self.speed_calculation_window = 5.0  # Fenêtre de 5s pour calculer la vitesse
        
        # Historique des vitesses pour calcul de moyenne
        self.speed_history: Dict[str, List[tuple]] = {}
        
        # Statistiques globales
        self.global_stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'total_downloaded_mb': 0.0,
            'average_speed_mbps': 0.0
        }
    
    def create_download_task(self, task_id: str, name: str, url: str, 
                           destination: str, description: str = "",
                           headers: Dict[str, str] = None) -> ProgressTask:
        """Crée une nouvelle tâche de téléchargement"""
        if task_id in self.tasks:
            raise ValueError(f"Tâche {task_id} existe déjà")
        
        task = ProgressTask(
            task_id=task_id,
            name=name,
            description=description,
            url=url,
            destination=destination,
            headers=headers or {}
        )
        
        self.tasks[task_id] = task
        self.global_stats['total_tasks'] += 1
        
        self.logger.info(f"Tâche de téléchargement créée: {task_id}")
        self._notify_global_callbacks('task_created', task)
        
        return task
    
    def start_download(self, task_id: str) -> bool:
        """Démarre le téléchargement d'une tâche"""
        if task_id not in self.tasks:
            self.logger.error(f"Tâche {task_id} introuvable")
            return False
        
        task = self.tasks[task_id]
        
        if task.status == ProgressStatus.RUNNING:
            self.logger.warning(f"Tâche {task_id} déjà en cours")
            return False
        
        # Créer le thread de téléchargement
        download_thread = threading.Thread(
            target=self._download_worker,
            args=(task,),
            daemon=True,
            name=f"Download-{task_id}"
        )
        
        self.active_downloads[task_id] = download_thread
        task.status = ProgressStatus.RUNNING
        task.metrics.start_time = datetime.now()
        
        download_thread.start()
        
        self.logger.info(f"Téléchargement démarré: {task_id}")
        self._notify_task_callbacks(task, 'started')
        
        return True
    
    def pause_download(self, task_id: str) -> bool:
        """Met en pause un téléchargement"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.status != ProgressStatus.RUNNING:
            return False
        
        task.pause_event.set()
        task.status = ProgressStatus.PAUSED
        
        self.logger.info(f"Téléchargement mis en pause: {task_id}")
        self._notify_task_callbacks(task, 'paused')
        
        return True
    
    def resume_download(self, task_id: str) -> bool:
        """Reprend un téléchargement en pause"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.status != ProgressStatus.PAUSED:
            return False
        
        task.pause_event.clear()
        task.status = ProgressStatus.RUNNING
        
        self.logger.info(f"Téléchargement repris: {task_id}")
        self._notify_task_callbacks(task, 'resumed')
        
        return True
    
    def cancel_download(self, task_id: str) -> bool:
        """Annule un téléchargement"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.cancel_event.set()
        task.status = ProgressStatus.CANCELLED
        
        # Nettoyer le fichier partiel si il existe
        if task.destination and os.path.exists(task.destination):
            try:
                os.remove(task.destination)
            except:
                pass
        
        self.logger.info(f"Téléchargement annulé: {task_id}")
        self._notify_task_callbacks(task, 'cancelled')
        
        return True
    
    def retry_download(self, task_id: str) -> bool:
        """Relance un téléchargement échoué"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.status != ProgressStatus.FAILED:
            return False
        
        if task.retry_count >= task.max_retries:
            self.logger.warning(f"Nombre maximum de tentatives atteint pour {task_id}")
            return False
        
        task.retry_count += 1
        task.status = ProgressStatus.PENDING
        task.error_message = None
        task.cancel_event.clear()
        task.pause_event.clear()
        
        # Réinitialiser les métriques
        task.metrics = ProgressMetrics()
        
        return self.start_download(task_id)
    
    def get_task(self, task_id: str) -> Optional[ProgressTask]:
        """Récupère une tâche par son ID"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[ProgressTask]:
        """Récupère toutes les tâches"""
        return list(self.tasks.values())
    
    def get_active_tasks(self) -> List[ProgressTask]:
        """Récupère les tâches actives (en cours ou en pause)"""
        return [task for task in self.tasks.values() 
                if task.status in [ProgressStatus.RUNNING, ProgressStatus.PAUSED]]
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques globales"""
        # Calculer les statistiques en temps réel
        active_tasks = self.get_active_tasks()
        total_speed = sum(task.metrics.speed_mbps for task in active_tasks)
        
        self.global_stats.update({
            'active_downloads': len(active_tasks),
            'current_total_speed_mbps': total_speed,
            'tasks_in_queue': len([t for t in self.tasks.values() 
                                 if t.status == ProgressStatus.PENDING])
        })
        
        return self.global_stats.copy()
    
    def add_global_callback(self, callback: Callable):
        """Ajoute un callback global pour tous les événements"""
        self.global_callbacks.append(callback)
    
    def add_task_callback(self, task_id: str, callback: Callable):
        """Ajoute un callback spécifique à une tâche"""
        if task_id in self.tasks:
            self.tasks[task_id].callbacks.append(callback)
    
    def remove_task(self, task_id: str) -> bool:
        """Supprime une tâche terminée"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        # Ne pas supprimer les tâches actives
        if task.status in [ProgressStatus.RUNNING, ProgressStatus.PAUSED]:
            return False
        
        # Nettoyer le thread si il existe
        if task_id in self.active_downloads:
            del self.active_downloads[task_id]
        
        del self.tasks[task_id]
        self.logger.info(f"Tâche supprimée: {task_id}")
        
        return True
    
    def clear_completed_tasks(self):
        """Supprime toutes les tâches terminées"""
        completed_tasks = [
            task_id for task_id, task in self.tasks.items()
            if task.status in [ProgressStatus.COMPLETED, ProgressStatus.FAILED, ProgressStatus.CANCELLED]
        ]
        
        for task_id in completed_tasks:
            self.remove_task(task_id)
        
        self.logger.info(f"{len(completed_tasks)} tâches terminées supprimées")
    
    def _download_worker(self, task: ProgressTask):
        """Worker thread pour effectuer le téléchargement"""
        try:
            self.logger.info(f"Début téléchargement: {task.name}")
            
            # Préparer la requête
            headers = task.headers.copy()
            
            # Vérifier si le fichier existe déjà (reprise de téléchargement)
            resume_pos = 0
            if os.path.exists(task.destination):
                resume_pos = os.path.getsize(task.destination)
                headers['Range'] = f'bytes={resume_pos}-'
                self.logger.info(f"Reprise téléchargement à la position {resume_pos}")
            
            # Effectuer la requête
            response = requests.get(task.url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # Obtenir la taille totale
            content_length = response.headers.get('content-length')
            if content_length:
                total_size = int(content_length) + resume_pos
                task.metrics.total_size = total_size
            
            # Créer le répertoire de destination si nécessaire
            os.makedirs(os.path.dirname(task.destination), exist_ok=True)
            
            # Ouvrir le fichier en mode append si reprise, sinon en mode write
            file_mode = 'ab' if resume_pos > 0 else 'wb'
            
            with open(task.destination, file_mode) as file:
                task.metrics.downloaded_size = resume_pos
                last_update_time = time.time()
                last_downloaded = resume_pos
                
                # Initialiser l'historique des vitesses
                self.speed_history[task.task_id] = []
                
                for chunk in response.iter_content(chunk_size=self.chunk_size):
                    # Vérifier l'annulation
                    if task.cancel_event.is_set():
                        task.status = ProgressStatus.CANCELLED
                        return
                    
                    # Vérifier la pause
                    while task.pause_event.is_set():
                        if task.cancel_event.is_set():
                            task.status = ProgressStatus.CANCELLED
                            return
                        time.sleep(0.1)
                    
                    if chunk:
                        file.write(chunk)
                        task.metrics.downloaded_size += len(chunk)
                        
                        # Mettre à jour les métriques périodiquement
                        current_time = time.time()
                        if current_time - last_update_time >= self.update_interval:
                            self._update_task_metrics(task, current_time, last_update_time, 
                                                    last_downloaded)
                            last_update_time = current_time
                            last_downloaded = task.metrics.downloaded_size
                            
                            # Notifier les callbacks
                            self._notify_task_callbacks(task, 'progress')
            
            # Téléchargement terminé avec succès
            task.status = ProgressStatus.COMPLETED
            task.metrics.progress_percent = 100.0
            task.metrics.last_update = datetime.now()
            
            # Mettre à jour les statistiques globales
            self.global_stats['completed_tasks'] += 1
            self.global_stats['total_downloaded_mb'] += task.metrics.total_size / (1024 * 1024)
            
            self.logger.info(f"Téléchargement terminé: {task.name}")
            self._notify_task_callbacks(task, 'completed')
            
        except requests.exceptions.RequestException as e:
            self._handle_download_error(task, f"Erreur réseau: {e}")
        except IOError as e:
            self._handle_download_error(task, f"Erreur fichier: {e}")
        except Exception as e:
            self._handle_download_error(task, f"Erreur inattendue: {e}")
        finally:
            # Nettoyer
            if task.task_id in self.active_downloads:
                del self.active_downloads[task.task_id]
            if task.task_id in self.speed_history:
                del self.speed_history[task.task_id]
    
    def _update_task_metrics(self, task: ProgressTask, current_time: float, 
                           last_update_time: float, last_downloaded: int):
        """Met à jour les métriques d'une tâche"""
        # Calculer la progression
        if task.metrics.total_size > 0:
            task.metrics.progress_percent = (task.metrics.downloaded_size / task.metrics.total_size) * 100
        
        # Calculer la vitesse
        time_diff = current_time - last_update_time
        bytes_diff = task.metrics.downloaded_size - last_downloaded
        
        if time_diff > 0:
            current_speed = bytes_diff / time_diff  # bytes/sec
            
            # Ajouter à l'historique
            speed_entry = (current_time, current_speed)
            self.speed_history[task.task_id].append(speed_entry)
            
            # Nettoyer l'historique (garder seulement les dernières 5 secondes)
            cutoff_time = current_time - self.speed_calculation_window
            self.speed_history[task.task_id] = [
                entry for entry in self.speed_history[task.task_id]
                if entry[0] > cutoff_time
            ]
            
            # Calculer la vitesse moyenne
            if self.speed_history[task.task_id]:
                speeds = [entry[1] for entry in self.speed_history[task.task_id]]
                avg_speed = sum(speeds) / len(speeds)
                task.metrics.speed_bps = avg_speed
                task.metrics.speed_mbps = avg_speed / (1024 * 1024)
            
            # Calculer l'ETA
            if task.metrics.speed_bps > 0 and task.metrics.total_size > 0:
                remaining_bytes = task.metrics.total_size - task.metrics.downloaded_size
                task.metrics.eta_seconds = int(remaining_bytes / task.metrics.speed_bps)
        
        # Calculer le temps écoulé
        if task.metrics.start_time:
            task.metrics.elapsed_seconds = (datetime.now() - task.metrics.start_time).total_seconds()
        
        task.metrics.last_update = datetime.now()
    
    def _handle_download_error(self, task: ProgressTask, error_message: str):
        """Gère les erreurs de téléchargement"""
        task.status = ProgressStatus.FAILED
        task.error_message = error_message
        
        self.global_stats['failed_tasks'] += 1
        
        self.logger.error(f"Erreur téléchargement {task.name}: {error_message}")
        self._notify_task_callbacks(task, 'failed')
        
        # Tentative de retry automatique si configuré
        if task.retry_count < task.max_retries:
            self.logger.info(f"Tentative de retry automatique pour {task.task_id}")
            time.sleep(2)  # Attendre 2 secondes avant retry
            self.retry_download(task.task_id)
    
    def _notify_task_callbacks(self, task: ProgressTask, event_type: str):
        """Notifie les callbacks d'une tâche"""
        for callback in task.callbacks:
            try:
                callback(task, event_type)
            except Exception as e:
                self.logger.error(f"Erreur callback tâche {task.task_id}: {e}")
        
        # Notifier aussi les callbacks globaux
        self._notify_global_callbacks(event_type, task)
    
    def _notify_global_callbacks(self, event_type: str, task: ProgressTask):
        """Notifie les callbacks globaux"""
        for callback in self.global_callbacks:
            try:
                callback(event_type, task)
            except Exception as e:
                self.logger.error(f"Erreur callback global: {e}")
    
    def export_progress_report(self, filepath: str):
        """Exporte un rapport de progression"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'global_stats': self.get_global_stats(),
            'tasks': []
        }
        
        for task in self.tasks.values():
            task_data = {
                'id': task.task_id,
                'name': task.name,
                'description': task.description,
                'status': task.status.value,
                'progress_percent': task.metrics.progress_percent,
                'total_size_mb': task.metrics.total_size / (1024 * 1024),
                'downloaded_size_mb': task.metrics.downloaded_size / (1024 * 1024),
                'speed_mbps': task.metrics.speed_mbps,
                'eta_seconds': task.metrics.eta_seconds,
                'elapsed_seconds': task.metrics.elapsed_seconds,
                'retry_count': task.retry_count,
                'error_message': task.error_message,
                'created_at': task.created_at.isoformat()
            }
            report['tasks'].append(task_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Rapport de progression exporté: {filepath}")

# Utilitaires pour formater les données
def format_size(bytes_size: int) -> str:
    """Formate une taille en bytes en format lisible"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"

def format_speed(bytes_per_second: float) -> str:
    """Formate une vitesse en format lisible"""
    return f"{format_size(int(bytes_per_second))}/s"

def format_time(seconds: Optional[int]) -> str:
    """Formate un temps en format lisible"""
    if seconds is None:
        return "Inconnu"
    
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

# Fonction utilitaire pour créer un gestionnaire
def create_progress_manager() -> ProgressManager:
    """Crée et retourne un gestionnaire de progression"""
    return ProgressManager()

if __name__ == "__main__":
    # Test du gestionnaire de progression
    import time
    
    def progress_callback(task, event_type):
        if event_type == 'progress':
            print(f"📥 {task.name}: {task.metrics.progress_percent:.1f}% "
                  f"({format_speed(task.metrics.speed_bps)}) "
                  f"ETA: {format_time(task.metrics.eta_seconds)}")
        elif event_type == 'completed':
            print(f"✅ {task.name}: Téléchargement terminé!")
        elif event_type == 'failed':
            print(f"❌ {task.name}: Échec - {task.error_message}")
    
    # Créer le gestionnaire
    manager = create_progress_manager()
    
    # Créer une tâche de test
    task = manager.create_download_task(
        task_id="test_download",
        name="Test Download",
        url="https://httpbin.org/bytes/1048576",  # 1MB de test
        destination="test_download.bin",
        description="Téléchargement de test"
    )
    
    # Ajouter un callback
    manager.add_task_callback("test_download", progress_callback)
    
    # Démarrer le téléchargement
    print("🚀 Démarrage du téléchargement de test...")
    manager.start_download("test_download")
    
    # Attendre la fin
    while task.status == ProgressStatus.RUNNING:
        time.sleep(0.5)
    
    print(f"\n📊 Statistiques globales: {manager.get_global_stats()}")
