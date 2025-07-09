"""
Multi-Target Real-Time Stream - Système de stream temps réel multi-cibles
Gère la capture simultanée de plusieurs écrans et fenêtres avec détection YOLO
"""

import threading
import time
import queue
from typing import Dict, List, Optional, Tuple, Callable
import cv2
import numpy as np
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

# Imports locaux
from utils.multi_screen import ScreenManager, WindowManager, TargetSelector
from learning.collaborative_learning import CollaborativeLearningSystem

@dataclass
class StreamTarget:
    """Représente une cible de stream (écran ou fenêtre)"""
    target_id: str
    target_type: str  # 'screen' ou 'window'
    target_data: Dict
    active: bool = True
    fps_target: int = 30
    last_capture_time: float = 0.0
    capture_count: int = 0
    error_count: int = 0

@dataclass
class DetectionResult:
    """Résultat d'une détection"""
    target_id: str
    timestamp: float
    detections: List[Dict]
    image: np.ndarray
    processing_time_ms: float
    confidence_threshold: float

class FPSController:
    """Contrôleur de FPS adaptatif"""
    
    def __init__(self, target_fps: int = 30):
        self.target_fps = target_fps
        self.target_interval = 1.0 / target_fps
        self.last_frame_time = 0.0
        self.frame_times = []
        self.max_history = 30
    
    def should_capture(self) -> bool:
        """Détermine si on doit capturer maintenant"""
        current_time = time.time()
        elapsed = current_time - self.last_frame_time
        return elapsed >= self.target_interval
    
    def frame_captured(self):
        """Marque qu'une frame a été capturée"""
        current_time = time.time()
        if self.last_frame_time > 0:
            frame_time = current_time - self.last_frame_time
            self.frame_times.append(frame_time)
            if len(self.frame_times) > self.max_history:
                self.frame_times.pop(0)
        
        self.last_frame_time = current_time
    
    def get_actual_fps(self) -> float:
        """Retourne le FPS réel actuel"""
        if len(self.frame_times) < 2:
            return 0.0
        
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0
    
    def adjust_target_fps(self, new_fps: int):
        """Ajuste le FPS cible"""
        self.target_fps = max(1, min(60, new_fps))
        self.target_interval = 1.0 / self.target_fps

class MultiTargetStream:
    """Système de stream multi-cibles en temps réel"""
    
    def __init__(self, yolo_model, log_callback: Optional[Callable] = None):
        self.yolo_model = yolo_model
        self.log_callback = log_callback
        
        # Gestionnaires
        self.screen_manager = ScreenManager()
        self.window_manager = WindowManager()
        
        # Cibles de stream
        self.stream_targets: Dict[str, StreamTarget] = {}
        self.fps_controllers: Dict[str, FPSController] = {}
        
        # Threading
        self.stream_active = False
        self.capture_threads: Dict[str, threading.Thread] = {}
        self.detection_thread: Optional[threading.Thread] = None
        
        # Queues pour communication inter-threads
        self.capture_queue = queue.Queue(maxsize=100)
        self.detection_queue = queue.Queue(maxsize=50)
        self.result_callbacks: List[Callable] = []
        
        # Configuration
        self.global_fps = 30
        self.confidence_threshold = 0.5
        self.max_detections_per_frame = 20
        
        # Statistiques
        self.stats = {
            "total_frames_captured": 0,
            "total_detections": 0,
            "average_processing_time": 0.0,
            "active_targets": 0,
            "start_time": None
        }
    
    def log(self, message: str):
        """Log un message"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(f"[MultiStream] {message}")
    
    def add_screen_target(self, screen_id: int, fps: int = 30) -> str:
        """Ajoute un écran comme cible de stream"""
        try:
            screen = self.screen_manager.get_screen_by_id(screen_id)
            if not screen:
                self.log(f"❌ Écran {screen_id} non trouvé")
                return None
            
            target_id = f"screen_{screen_id}"
            
            # Créer la cible de stream
            stream_target = StreamTarget(
                target_id=target_id,
                target_type="screen",
                target_data=screen,
                fps_target=fps
            )
            
            self.stream_targets[target_id] = stream_target
            self.fps_controllers[target_id] = FPSController(fps)
            
            self.log(f"✅ Écran {screen['name']} ajouté au stream (FPS: {fps})")
            return target_id
            
        except Exception as e:
            self.log(f"❌ Erreur ajout écran: {e}")
            return None
    
    def add_window_target(self, window_title: str, fps: int = 30) -> str:
        """Ajoute une fenêtre comme cible de stream"""
        try:
            self.window_manager.refresh_windows()
            window = self.window_manager.get_window_by_title(window_title)
            
            if not window:
                self.log(f"❌ Fenêtre '{window_title}' non trouvée")
                return None
            
            target_id = f"window_{window['hwnd']}"
            
            # Créer la cible de stream
            stream_target = StreamTarget(
                target_id=target_id,
                target_type="window",
                target_data=window,
                fps_target=fps
            )
            
            self.stream_targets[target_id] = stream_target
            self.fps_controllers[target_id] = FPSController(fps)
            
            self.log(f"✅ Fenêtre '{window['title']}' ajoutée au stream (FPS: {fps})")
            return target_id
            
        except Exception as e:
            self.log(f"❌ Erreur ajout fenêtre: {e}")
            return None
    
    def remove_target(self, target_id: str) -> bool:
        """Supprime une cible de stream"""
        try:
            if target_id not in self.stream_targets:
                self.log(f"❌ Cible '{target_id}' non trouvée")
                return False
            
            # Marquer comme inactive
            self.stream_targets[target_id].active = False
            
            # Attendre que le thread se termine
            if target_id in self.capture_threads:
                thread = self.capture_threads[target_id]
                if thread.is_alive():
                    thread.join(timeout=2.0)
                del self.capture_threads[target_id]
            
            # Supprimer la cible
            del self.stream_targets[target_id]
            if target_id in self.fps_controllers:
                del self.fps_controllers[target_id]
            
            self.log(f"✅ Cible '{target_id}' supprimée du stream")
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur suppression cible: {e}")
            return False
    
    def start_stream(self) -> bool:
        """Démarre le stream multi-cibles"""
        try:
            if self.stream_active:
                self.log("⚠️ Stream déjà actif")
                return True
            
            if not self.stream_targets:
                self.log("❌ Aucune cible configurée")
                return False
            
            self.stream_active = True
            self.stats["start_time"] = time.time()
            
            # Démarrer les threads de capture pour chaque cible
            for target_id, target in self.stream_targets.items():
                if target.active:
                    thread = threading.Thread(
                        target=self._capture_loop,
                        args=(target_id,),
                        daemon=True,
                        name=f"Capture-{target_id}"
                    )
                    thread.start()
                    self.capture_threads[target_id] = thread
            
            # Démarrer le thread de détection
            self.detection_thread = threading.Thread(
                target=self._detection_loop,
                daemon=True,
                name="Detection-Loop"
            )
            self.detection_thread.start()
            
            active_count = len([t for t in self.stream_targets.values() if t.active])
            self.log(f"🚀 Stream démarré avec {active_count} cibles actives")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur démarrage stream: {e}")
            return False
    
    def stop_stream(self):
        """Arrête le stream multi-cibles"""
        try:
            if not self.stream_active:
                return
            
            self.log("⏹️ Arrêt du stream...")
            self.stream_active = False
            
            # Attendre que tous les threads se terminent
            for thread in self.capture_threads.values():
                if thread.is_alive():
                    thread.join(timeout=2.0)
            
            if self.detection_thread and self.detection_thread.is_alive():
                self.detection_thread.join(timeout=2.0)
            
            # Vider les queues
            while not self.capture_queue.empty():
                try:
                    self.capture_queue.get_nowait()
                except queue.Empty:
                    break
            
            while not self.detection_queue.empty():
                try:
                    self.detection_queue.get_nowait()
                except queue.Empty:
                    break
            
            self.capture_threads.clear()
            self.detection_thread = None
            
            self.log("✅ Stream arrêté")
            
        except Exception as e:
            self.log(f"❌ Erreur arrêt stream: {e}")
    
    def _capture_loop(self, target_id: str):
        """Boucle de capture pour une cible spécifique"""
        target = self.stream_targets[target_id]
        fps_controller = self.fps_controllers[target_id]
        
        self.log(f"📹 Démarrage capture pour {target_id}")
        
        while self.stream_active and target.active:
            try:
                # Vérifier si on doit capturer maintenant
                if not fps_controller.should_capture():
                    time.sleep(0.001)  # Petite pause pour éviter la surcharge CPU
                    continue
                
                # Capturer l'image selon le type de cible
                image = None
                if target.target_type == "screen":
                    image = self.screen_manager.capture_screen(target.target_data['id'])
                elif target.target_type == "window":
                    image = self.window_manager.capture_window(target.target_data)
                
                if image is not None:
                    # Ajouter à la queue de capture
                    capture_data = {
                        "target_id": target_id,
                        "image": image,
                        "timestamp": time.time()
                    }
                    
                    try:
                        self.capture_queue.put_nowait(capture_data)
                        target.capture_count += 1
                        fps_controller.frame_captured()
                    except queue.Full:
                        # Queue pleine, ignorer cette frame
                        pass
                else:
                    target.error_count += 1
                    if target.error_count > 10:
                        self.log(f"⚠️ Trop d'erreurs pour {target_id}, pause...")
                        time.sleep(1.0)
                        target.error_count = 0
                
            except Exception as e:
                target.error_count += 1
                if target.error_count % 10 == 0:
                    self.log(f"❌ Erreur capture {target_id}: {e}")
                time.sleep(0.1)
        
        self.log(f"📹 Arrêt capture pour {target_id}")
    
    def _detection_loop(self):
        """Boucle de détection YOLO"""
        self.log("🔍 Démarrage détection YOLO")
        
        while self.stream_active:
            try:
                # Récupérer une image de la queue
                try:
                    capture_data = self.capture_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                start_time = time.time()
                
                # Effectuer la détection YOLO
                image = capture_data["image"]
                results = self.yolo_model(image, conf=self.confidence_threshold, verbose=False)
                
                # Traiter les résultats
                detections = []
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            if len(detections) >= self.max_detections_per_frame:
                                break
                            
                            class_id = int(box.cls[0])
                            class_name = self.yolo_model.names[class_id]
                            confidence = float(box.conf[0])
                            bbox = box.xyxy[0].tolist()
                            
                            detections.append({
                                'class_name': class_name,
                                'confidence': confidence,
                                'bbox': bbox,
                                'center': [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]
                            })
                
                processing_time = (time.time() - start_time) * 1000  # en ms
                
                # Créer le résultat
                detection_result = DetectionResult(
                    target_id=capture_data["target_id"],
                    timestamp=capture_data["timestamp"],
                    detections=detections,
                    image=image,
                    processing_time_ms=processing_time,
                    confidence_threshold=self.confidence_threshold
                )
                
                # Mettre à jour les statistiques
                self.stats["total_frames_captured"] += 1
                self.stats["total_detections"] += len(detections)
                
                # Calculer le temps de traitement moyen
                if self.stats["total_frames_captured"] > 0:
                    old_avg = self.stats["average_processing_time"]
                    count = self.stats["total_frames_captured"]
                    self.stats["average_processing_time"] = (old_avg * (count - 1) + processing_time) / count
                
                # Envoyer le résultat aux callbacks
                for callback in self.result_callbacks:
                    try:
                        callback(detection_result)
                    except Exception as e:
                        self.log(f"❌ Erreur callback: {e}")
                
                # Ajouter à la queue de résultats
                try:
                    self.detection_queue.put_nowait(detection_result)
                except queue.Full:
                    # Queue pleine, ignorer ce résultat
                    pass
                
            except Exception as e:
                self.log(f"❌ Erreur détection: {e}")
                time.sleep(0.1)
        
        self.log("🔍 Arrêt détection YOLO")
    
    def add_result_callback(self, callback: Callable[[DetectionResult], None]):
        """Ajoute un callback pour les résultats de détection"""
        self.result_callbacks.append(callback)
    
    def remove_result_callback(self, callback: Callable[[DetectionResult], None]):
        """Supprime un callback"""
        if callback in self.result_callbacks:
            self.result_callbacks.remove(callback)
    
    def get_stream_stats(self) -> Dict:
        """Retourne les statistiques du stream"""
        stats = self.stats.copy()
        stats["active_targets"] = len([t for t in self.stream_targets.values() if t.active])
        
        # Ajouter les FPS par cible
        fps_by_target = {}
        for target_id, fps_controller in self.fps_controllers.items():
            fps_by_target[target_id] = fps_controller.get_actual_fps()
        
        stats["fps_by_target"] = fps_by_target
        
        # Calculer le temps de fonctionnement
        if stats["start_time"]:
            stats["uptime_seconds"] = time.time() - stats["start_time"]
        
        return stats
    
    def adjust_target_fps(self, target_id: str, new_fps: int) -> bool:
        """Ajuste le FPS d'une cible spécifique"""
        try:
            if target_id not in self.fps_controllers:
                return False
            
            self.fps_controllers[target_id].adjust_target_fps(new_fps)
            self.stream_targets[target_id].fps_target = new_fps
            
            self.log(f"🎛️ FPS ajusté pour {target_id}: {new_fps}")
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur ajustement FPS: {e}")
            return False
    
    def set_confidence_threshold(self, threshold: float):
        """Définit le seuil de confiance global"""
        self.confidence_threshold = max(0.1, min(0.9, threshold))
        self.log(f"🎛️ Seuil de confiance: {self.confidence_threshold}")
    
    def get_latest_results(self, max_results: int = 10) -> List[DetectionResult]:
        """Récupère les derniers résultats de détection"""
        results = []
        
        try:
            while len(results) < max_results and not self.detection_queue.empty():
                result = self.detection_queue.get_nowait()
                results.append(result)
        except queue.Empty:
            pass
        
        return results
    
    def save_stream_config(self, config_path: str = "stream_config.json"):
        """Sauvegarde la configuration du stream"""
        try:
            config = {
                "targets": [],
                "global_fps": self.global_fps,
                "confidence_threshold": self.confidence_threshold,
                "max_detections_per_frame": self.max_detections_per_frame
            }
            
            for target_id, target in self.stream_targets.items():
                target_config = {
                    "target_id": target_id,
                    "target_type": target.target_type,
                    "fps_target": target.fps_target,
                    "active": target.active
                }
                
                # Ajouter les données spécifiques selon le type
                if target.target_type == "screen":
                    target_config["screen_id"] = target.target_data["id"]
                elif target.target_type == "window":
                    target_config["window_title"] = target.target_data["title"]
                
                config["targets"].append(target_config)
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.log(f"💾 Configuration sauvegardée: {config_path}")
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur sauvegarde config: {e}")
            return False
    
    def load_stream_config(self, config_path: str = "stream_config.json") -> bool:
        """Charge la configuration du stream"""
        try:
            if not Path(config_path).exists():
                self.log(f"⚠️ Fichier config non trouvé: {config_path}")
                return False
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Appliquer la configuration globale
            self.global_fps = config.get("global_fps", 30)
            self.confidence_threshold = config.get("confidence_threshold", 0.5)
            self.max_detections_per_frame = config.get("max_detections_per_frame", 20)
            
            # Recréer les cibles
            for target_config in config.get("targets", []):
                if target_config["target_type"] == "screen":
                    self.add_screen_target(
                        target_config["screen_id"],
                        target_config["fps_target"]
                    )
                elif target_config["target_type"] == "window":
                    self.add_window_target(
                        target_config["window_title"],
                        target_config["fps_target"]
                    )
            
            self.log(f"📂 Configuration chargée: {config_path}")
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur chargement config: {e}")
            return False

# Fonction utilitaire pour créer le système
def create_multi_target_stream(yolo_model, log_callback=None) -> MultiTargetStream:
    """Crée et initialise le système de stream multi-cibles"""
    return MultiTargetStream(yolo_model, log_callback)

if __name__ == "__main__":
    # Test du système (nécessite un modèle YOLO)
    print("🚀 Test du système de stream multi-cibles")
    print("📋 Fonctionnalités:")
    print("  • Stream simultané de plusieurs écrans")
    print("  • Stream de fenêtres d'applications")
    print("  • Contrôle FPS adaptatif par cible")
    print("  • Détection YOLO en temps réel")
    print("  • Statistiques de performance")
