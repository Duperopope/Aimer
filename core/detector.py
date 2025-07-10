#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Détecteur Universel Detectron2
© 2025 - Licence Apache 2.0

Détecteur universel unifié basé sur Detectron2
"""

import cv2
import numpy as np
import torch
import time
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging

try:
    from detectron2 import model_zoo
    from detectron2.engine import DefaultPredictor
    from detectron2.config import get_cfg
    from detectron2.utils.visualizer import Visualizer
    from detectron2.data import MetadataCatalog
    DETECTRON2_AVAILABLE = True
except ImportError:
    DETECTRON2_AVAILABLE = False
    logging.warning("Detectron2 non disponible - installation requise")

from .config import ConfigManager
from .logger import Logger

class DetectionResult:
    """Résultat de détection structuré"""
    
    def __init__(self, instances, metadata, performance_metrics):
        self.instances = instances
        self.metadata = metadata
        self.performance_metrics = performance_metrics
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire pour API"""
        return {
            "detections": self._format_instances(),
            "count": len(self.instances) if self.instances else 0,
            "performance": self.performance_metrics,
            "timestamp": self.timestamp
        }
    
    def _format_instances(self) -> List[Dict[str, Any]]:
        """Formate les instances détectées"""
        if not self.instances or not hasattr(self.instances, 'pred_boxes'):
            return []
        
        detections = []
        boxes = self.instances.pred_boxes.tensor.cpu().numpy()
        scores = self.instances.scores.cpu().numpy()
        classes = self.instances.pred_classes.cpu().numpy()
        
        for i, (box, score, cls) in enumerate(zip(boxes, scores, classes)):
            detection = {
                "id": i,
                "class_id": int(cls),
                "class_name": self.metadata.thing_classes[cls] if self.metadata else f"class_{cls}",
                "confidence": float(score),
                "bbox": {
                    "x1": float(box[0]),
                    "y1": float(box[1]), 
                    "x2": float(box[2]),
                    "y2": float(box[3]),
                    "width": float(box[2] - box[0]),
                    "height": float(box[3] - box[1])
                }
            }
            detections.append(detection)
        
        return detections

class UniversalDetector:
    """
    Détecteur universel utilisant Detectron2
    
    Capacités:
    - Object Detection
    - Instance Segmentation
    - Panoptic Segmentation
    - Keypoint Detection
    """
    
    def __init__(self, task_type: str = "detection", confidence_threshold: Optional[float] = None):
        """
        Initialise le détecteur universel
        
        Args:
            task_type: Type de tâche (detection, instance_segmentation, etc.)
            confidence_threshold: Seuil de confiance minimum
        """
        self.config_manager = ConfigManager()
        self.logger = Logger("UniversalDetector")
        
        # Configuration depuis config.json
        config = self.config_manager.get_detectron2_config()
        
        self.task_type = task_type or config.get("default_task", "detection")
        self.confidence_threshold = confidence_threshold if confidence_threshold is not None else config.get("confidence_threshold", 0.5)
        
        self.predictor = None
        self.cfg = None
        self.metadata = None
        
        # Métriques de performance
        self.performance_metrics = {
            "total_detections": 0,
            "average_inference_time": 0.0,
            "gpu_utilization": 0.0,
            "memory_usage": 0.0
        }
        
        # Modèles disponibles
        self.task_models = config.get("models", {
            "detection": "COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml",
            "instance_segmentation": "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml",
            "panoptic_segmentation": "COCO-PanopticSegmentation/panoptic_fpn_R_50_3x.yaml",
            "keypoint_detection": "COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml"
        })
        
        # Initialisation
        self._initialize_detector()
    
    def _initialize_detector(self):
        """Initialise le détecteur avec gestion d'erreurs"""
        try:
            if not DETECTRON2_AVAILABLE:
                error_msg = "Detectron2 non installé - installation requise"
                self.logger.error(error_msg)
                raise ImportError(error_msg)
            
            self.logger.info(f"Initialisation détecteur - Tâche: {self.task_type}")
            
            # Configuration Detectron2
            self.cfg = get_cfg()
            self._setup_model_config()
            
            # Création du prédicteur
            self.predictor = DefaultPredictor(self.cfg)
            self.metadata = MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0])
            
            self.logger.info("Détecteur initialisé avec succès")
            
        except Exception as e:
            self.logger.error(f"Erreur initialisation détecteur: {e}")
            raise
    
    def _setup_model_config(self):
        """Configure le modèle selon la tâche"""
        if self.task_type not in self.task_models:
            raise ValueError(f"Tâche non supportée: {self.task_type}")
        
        model_config = self.task_models[self.task_type]
        
        # Configuration de base
        self.cfg.merge_from_file(model_zoo.get_config_file(model_config))
        self.cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(model_config)
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = self.confidence_threshold
        
        # Configuration device
        device_config = self.config_manager.get_detectron2_config().get("device", "auto")
        if device_config == "auto":
            self.cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.cfg.MODEL.DEVICE = device_config
        
        if not torch.cuda.is_available() and self.cfg.MODEL.DEVICE == "cuda":
            self.logger.warning("CUDA non disponible - utilisation CPU")
            self.cfg.MODEL.DEVICE = "cpu"
    
    def detect(self, image: Union[np.ndarray, str, Path]) -> DetectionResult:
        """
        Détection principale avec monitoring
        
        Args:
            image: Image (array numpy, chemin fichier, ou Path)
            
        Returns:
            DetectionResult: Résultat structuré avec métriques
        """
        start_time = time.time()
        
        try:
            # Préparation image
            processed_image = self._prepare_image(image)
            
            # Détection
            instances = self.predictor(processed_image)["instances"]
            
            # Calcul métriques
            inference_time = time.time() - start_time
            performance_metrics = {
                "inference_time_ms": inference_time * 1000,
                "detections_count": len(instances),
                "device": str(self.cfg.MODEL.DEVICE)
            }
            
            # Mise à jour métriques globales
            self._update_global_metrics(inference_time, len(instances))
            
            # Logging succès
            self.logger.info(f"Détection réussie: {len(instances)} objets en {inference_time*1000:.1f}ms")
            
            # Création résultat
            result = DetectionResult(instances, self.metadata, performance_metrics)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur détection: {e}")
            # Retourner résultat vide en cas d'erreur
            return DetectionResult(None, self.metadata, {"error": str(e)})
    
    def switch_task(self, new_task: str):
        """Change le type de tâche dynamiquement"""
        if new_task == self.task_type:
            return
        
        if new_task not in self.task_models:
            raise ValueError(f"Tâche non supportée: {new_task}")
        
        self.logger.info(f"Changement tâche: {self.task_type} -> {new_task}")
        
        self.task_type = new_task
        self._setup_model_config()
        self.predictor = DefaultPredictor(self.cfg)
        self.metadata = MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0])
    
    def visualize_results(self, image: np.ndarray, result: DetectionResult) -> np.ndarray:
        """
        Visualise les résultats de détection
        
        Args:
            image: Image originale
            result: Résultat de détection
            
        Returns:
            np.ndarray: Image avec visualisations
        """
        if not result.instances:
            return image
        
        try:
            visualizer = Visualizer(image[:, :, ::-1], self.metadata, scale=1.0)
            vis_output = visualizer.draw_instance_predictions(result.instances.to("cpu"))
            return vis_output.get_image()[:, :, ::-1]
            
        except Exception as e:
            self.logger.error(f"Erreur visualisation: {e}")
            return image
    
    def _prepare_image(self, image: Union[np.ndarray, str, Path]) -> np.ndarray:
        """Prépare l'image pour la détection"""
        if isinstance(image, (str, Path)):
            loaded_image = cv2.imread(str(image))
            if loaded_image is None:
                raise ValueError(f"Impossible de charger l'image: {image}")
            image = loaded_image
        
        if not isinstance(image, np.ndarray):
            raise ValueError(f"Type d'image non supporté: {type(image)}")
        
        # Conversion BGR vers RGB si nécessaire
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Detectron2 attend RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        return image
    
    def _update_global_metrics(self, inference_time: float, detection_count: int):
        """Met à jour les métriques globales"""
        self.performance_metrics["total_detections"] += detection_count
        
        # Moyenne mobile du temps d'inférence
        current_avg = self.performance_metrics["average_inference_time"]
        self.performance_metrics["average_inference_time"] = (
            (current_avg * 0.9) + (inference_time * 0.1)
        )
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Génère rapport de performance pour monitoring"""
        return {
            "detector_info": {
                "task_type": self.task_type,
                "confidence_threshold": self.confidence_threshold,
                "device": str(self.cfg.MODEL.DEVICE) if self.cfg else "unknown"
            },
            "performance_metrics": self.performance_metrics,
            "system_info": {
                "cuda_available": torch.cuda.is_available(),
                "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
            }
        }
    
    def cleanup(self):
        """Nettoyage des ressources"""
        if self.predictor:
            del self.predictor
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.logger.info("Nettoyage détecteur terminé")

# Factory functions pour création simplifiée
def create_detector(task_type: str = "detection", **kwargs) -> UniversalDetector:
    """Factory function pour créer un détecteur"""
    return UniversalDetector(task_type=task_type, **kwargs)

def create_object_detector(**kwargs) -> UniversalDetector:
    """Crée un détecteur d'objets"""
    return create_detector("detection", **kwargs)

def create_instance_segmenter(**kwargs) -> UniversalDetector:
    """Crée un segmenteur d'instances"""
    return create_detector("instance_segmentation", **kwargs)

def create_keypoint_detector(**kwargs) -> UniversalDetector:
    """Crée un détecteur de points clés"""
    return create_detector("keypoint_detection", **kwargs)
