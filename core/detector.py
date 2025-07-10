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
            "timestamp": self.timestamp,
        }

    def _format_instances(self) -> List[Dict[str, Any]]:
        """Formate les instances détectées"""
        if not self.instances or not hasattr(self.instances, "pred_boxes"):
            return []

        detections = []
        boxes = self.instances.pred_boxes.tensor.cpu().numpy()
        scores = self.instances.scores.cpu().numpy()
        classes = self.instances.pred_classes.cpu().numpy()

        for i, (box, score, cls) in enumerate(zip(boxes, scores, classes)):
            detection = {
                "id": i,
                "class_id": int(cls),
                "class_name": (
                    self.metadata.thing_classes[cls]
                    if self.metadata
                    else f"class_{cls}"
                ),
                "confidence": float(score),
                "bbox": {
                    "x1": float(box[0]),
                    "y1": float(box[1]),
                    "x2": float(box[2]),
                    "y2": float(box[3]),
                    "width": float(box[2] - box[0]),
                    "height": float(box[3] - box[1]),
                },
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

    def __init__(
        self, task_type: str = "detection", confidence_threshold: Optional[float] = None
    ):
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
        self.confidence_threshold = (
            confidence_threshold
            if confidence_threshold is not None
            else config.get("confidence_threshold", 0.5)
        )

        self.predictor = None
        self.cfg = None
        self.metadata = None

        # Métriques de performance
        self.performance_metrics = {
            "total_detections": 0,
            "average_inference_time": 0.0,
            "gpu_utilization": 0.0,
            "memory_usage": 0.0,
        }

        # Modèles disponibles
        self.task_models = config.get(
            "models",
            {
                "detection": "COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml",
                "instance_segmentation": "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml",
                "panoptic_segmentation": "COCO-PanopticSegmentation/panoptic_fpn_R_50_3x.yaml",
                "keypoint_detection": "COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml",
            },
        )

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
        device_config = self.config_manager.get_detectron2_config().get(
            "device", "auto"
        )
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
                "device": str(self.cfg.MODEL.DEVICE),
            }

            # Mise à jour métriques globales
            self._update_global_metrics(inference_time, len(instances))

            # Logging succès
            self.logger.info(
                f"Détection réussie: {len(instances)} objets en {inference_time*1000:.1f}ms"
            )

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

    def visualize_results(
        self, image: np.ndarray, result: DetectionResult
    ) -> np.ndarray:
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
            vis_output = visualizer.draw_instance_predictions(
                result.instances.to("cpu")
            )
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
        self.performance_metrics["average_inference_time"] = (current_avg * 0.9) + (
            inference_time * 0.1
        )

    def get_performance_report(self) -> Dict[str, Any]:
        """Génère rapport de performance pour monitoring"""
        return {
            "detector_info": {
                "task_type": self.task_type,
                "confidence_threshold": self.confidence_threshold,
                "device": str(self.cfg.MODEL.DEVICE) if self.cfg else "unknown",
            },
            "performance_metrics": self.performance_metrics,
            "system_info": {
                "cuda_available": torch.cuda.is_available(),
                "gpu_count": (
                    torch.cuda.device_count() if torch.cuda.is_available() else 0
                ),
            },
        }

    def cleanup(self):
        """Nettoyage des ressources"""
        if self.predictor:
            del self.predictor
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        self.logger.info("Nettoyage détecteur terminé")


# === SMART DETECTOR POUR WEB INTERFACE ===

class SmartDetector:
    """
    Détecteur intelligent pour l'interface web
    Combine détection heuristique et labels COCO
    """
    
    def __init__(self):
        self.logger = logging.getLogger('SmartDetector')
        
        # Labels COCO simplifiés pour classification intelligente
        self.coco_labels = {
            'person': 'Personne',
            'bicycle': 'Vélo',
            'car': 'Voiture',
            'motorcycle': 'Moto',
            'airplane': 'Avion',
            'bus': 'Bus',
            'train': 'Train',
            'truck': 'Camion',
            'boat': 'Bateau',
            'traffic light': 'Feu de circulation',
            'fire hydrant': 'Bouche incendie',
            'stop sign': 'Stop',
            'parking meter': 'Parcmètre',
            'bench': 'Banc',
            'bird': 'Oiseau',
            'cat': 'Chat',
            'dog': 'Chien',
            'horse': 'Cheval',
            'sheep': 'Mouton',
            'cow': 'Vache',
            'elephant': 'Éléphant',
            'bear': 'Ours',
            'zebra': 'Zèbre',
            'giraffe': 'Girafe',
            'backpack': 'Sac à dos',
            'umbrella': 'Parapluie',
            'handbag': 'Sac à main',
            'tie': 'Cravate',
            'suitcase': 'Valise',
            'frisbee': 'Frisbee',
            'skis': 'Skis',
            'snowboard': 'Snowboard',
            'sports ball': 'Ballon',
            'kite': 'Cerf-volant',
            'baseball bat': 'Batte baseball',
            'baseball glove': 'Gant baseball',
            'skateboard': 'Skateboard',
            'surfboard': 'Planche de surf',
            'tennis racket': 'Raquette tennis',
            'bottle': 'Bouteille',
            'wine glass': 'Verre à vin',
            'cup': 'Tasse',
            'fork': 'Fourchette',
            'knife': 'Couteau',
            'spoon': 'Cuillère',
            'bowl': 'Bol',
            'banana': 'Banane',
            'apple': 'Pomme',
            'sandwich': 'Sandwich',
            'orange': 'Orange',
            'broccoli': 'Brocoli',
            'carrot': 'Carotte',
            'hot dog': 'Hot-dog',
            'pizza': 'Pizza',
            'donut': 'Donut',
            'cake': 'Gâteau',
            'chair': 'Chaise',
            'couch': 'Canapé',
            'potted plant': 'Plante',
            'bed': 'Lit',
            'dining table': 'Table',
            'toilet': 'Toilette',
            'tv': 'Télévision',
            'laptop': 'Ordinateur portable',
            'mouse': 'Souris',
            'remote': 'Télécommande',
            'keyboard': 'Clavier',
            'cell phone': 'Téléphone',
            'microwave': 'Micro-onde',
            'oven': 'Four',
            'toaster': 'Grille-pain',
            'sink': 'Évier',
            'refrigerator': 'Réfrigérateur',
            'book': 'Livre',
            'clock': 'Horloge',
            'vase': 'Vase',
            'scissors': 'Ciseaux',
            'teddy bear': 'Ours en peluche',
            'hair drier': 'Sèche-cheveux',
            'toothbrush': 'Brosse à dents'
        }
        
        # Couleurs pour les différents types d'objets
        self.color_map = {
            'Personne': [255, 0, 0],      # Rouge
            'Véhicule': [0, 255, 0],      # Vert
            'Animal': [0, 0, 255],        # Bleu
            'Objet': [255, 255, 0],       # Jaune
            'Nourriture': [255, 0, 255],  # Magenta
            'Mobilier': [0, 255, 255],    # Cyan
            'Électronique': [128, 0, 255] # Violet
        }
        
        # Classificateur de visages
        try:
            # Utilisation plus robuste pour éviter les erreurs de typage
            import os
            # Accès sécurisé à cv2.data pour éviter les warnings Pylance
            cv2_data = getattr(cv2, 'data', None)
            if cv2_data and hasattr(cv2_data, 'haarcascades'):
                face_cascade_path = os.path.join(cv2_data.haarcascades, 'haarcascade_frontalface_default.xml')
                self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
            else:
                self.face_cascade = None
        except Exception as e:
            self.face_cascade = None
            self.logger.warning(f"Classificateur de visages non disponible: {e}")
        
        self.logger.info("SmartDetector initialisé")

    def detect_objects(self, image):
        """
        Détection intelligente multi-méthodes
        """
        detections = []
        
        if image is None or len(image.shape) != 3:
            return detections
        
        try:
            # 1. Détection de visages (Personne)
            face_detections = self._detect_faces(image)
            detections.extend(face_detections)
            
            # 2. Détection de contours géométriques
            shape_detections = self._detect_shapes(image)
            detections.extend(shape_detections)
            
            # 3. Détection de couleurs dominantes
            color_detections = self._detect_colors(image)
            detections.extend(color_detections)
            
            # 4. Filtrage et optimisation
            detections = self._filter_detections(detections)
            
        except Exception as e:
            self.logger.error(f"Erreur détection: {e}")
        
        return detections

    def _detect_faces(self, image):
        """Détection de visages avec Haar Cascades"""
        detections = []
        
        if self.face_cascade is None:
            return detections
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30)
            )
            
            for (x, y, w, h) in faces:
                detections.append({
                    'label': 'Personne',
                    'confidence': 0.85,
                    'bbox': [int(x), int(y), int(w), int(h)],
                    'color': self.color_map['Personne'],
                    'type': 'face'
                })
                
        except Exception as e:
            self.logger.error(f"Erreur détection visages: {e}")
        
        return detections

    def _detect_shapes(self, image):
        """Détection de formes géométriques"""
        detections = []
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Détection de contours
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Filtrer les petits contours
                if area < 1000:
                    continue
                
                # Analyser la forme
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 1
                
                # Classification intelligente basée sur la géométrie
                label = self._classify_by_geometry(aspect_ratio, area, w, h)
                
                detections.append({
                    'label': label,
                    'confidence': 0.6,
                    'bbox': [int(x), int(y), int(w), int(h)],
                    'color': self._get_color_for_label(label),
                    'type': 'shape'
                })
                
        except Exception as e:
            self.logger.error(f"Erreur détection formes: {e}")
        
        return detections

    def _detect_colors(self, image):
        """Détection basée sur les couleurs dominantes"""
        detections = []
        
        try:
            # Conversion en HSV pour une meilleure détection de couleurs
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Masques pour différentes couleurs
            color_ranges = {
                'rouge': ([0, 50, 50], [10, 255, 255]),
                'vert': ([50, 50, 50], [70, 255, 255]),
                'bleu': ([100, 50, 50], [130, 255, 255]),
                'jaune': ([20, 50, 50], [30, 255, 255])
            }
            
            for color_name, (lower, upper) in color_ranges.items():
                lower = np.array(lower)
                upper = np.array(upper)
                
                mask = cv2.inRange(hsv, lower, upper)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area < 500:
                        continue
                    
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Classification basée sur la couleur
                    label = self._classify_by_color(color_name, area)
                    
                    detections.append({
                        'label': label,
                        'confidence': 0.5,
                        'bbox': [int(x), int(y), int(w), int(h)],
                        'color': self._get_color_for_label(label),
                        'type': 'color'
                    })
                    
        except Exception as e:
            self.logger.error(f"Erreur détection couleurs: {e}")
        
        return detections

    def _classify_by_geometry(self, aspect_ratio, area, width, height):
        """Classification intelligente basée sur la géométrie"""
        
        # Véhicules (rectangulaires, aspect ratio spécifique)
        if 1.5 <= aspect_ratio <= 3.0 and area > 2000:
            return 'Voiture'
        
        # Écrans/Télévisions (rectangulaires, grands)
        if 1.3 <= aspect_ratio <= 2.0 and area > 5000:
            return 'Télévision'
        
        # Livres/Documents (rectangulaires, moyens)
        if 0.7 <= aspect_ratio <= 1.5 and 1000 < area < 3000:
            return 'Livre'
        
        # Mobilier (carrés/rectangulaires, grands)
        if 0.8 <= aspect_ratio <= 1.2 and area > 3000:
            return 'Mobilier'
        
        # Objets longs et fins
        if aspect_ratio > 3.0:
            return 'Objet long'
        
        # Objets ronds/carrés
        if 0.8 <= aspect_ratio <= 1.2:
            return 'Objet rond'
        
        return 'Objet'

    def _classify_by_color(self, color_name, area):
        """Classification basée sur la couleur dominante"""
        
        if color_name == 'rouge':
            if area > 2000:
                return 'Voiture'
            else:
                return 'Objet rouge'
        
        elif color_name == 'vert':
            if area > 3000:
                return 'Plante'
            else:
                return 'Objet vert'
        
        elif color_name == 'bleu':
            if area > 2000:
                return 'Ciel'
            else:
                return 'Objet bleu'
        
        elif color_name == 'jaune':
            return 'Banane'  # Ou autre objet jaune
        
        return 'Objet coloré'

    def _get_color_for_label(self, label):
        """Retourne la couleur appropriée pour un label"""
        
        # Mapping par catégorie
        if label in ['Personne']:
            return self.color_map['Personne']
        elif label in ['Voiture', 'Bus', 'Camion', 'Vélo', 'Moto']:
            return self.color_map['Véhicule']
        elif label in ['Chat', 'Chien', 'Oiseau']:
            return self.color_map['Animal']
        elif label in ['Pomme', 'Banane', 'Pizza', 'Sandwich']:
            return self.color_map['Nourriture']
        elif label in ['Chaise', 'Table', 'Canapé', 'Mobilier']:
            return self.color_map['Mobilier']
        elif label in ['Télévision', 'Ordinateur portable', 'Téléphone']:
            return self.color_map['Électronique']
        else:
            return self.color_map['Objet']

    def _filter_detections(self, detections):
        """Filtre et optimise les détections"""
        
        if not detections:
            return []
        
        # Supprimer les doublons basés sur la position
        filtered = []
        for detection in detections:
            bbox = detection['bbox']
            x, y, w, h = bbox
            
            # Vérifier si une détection similaire existe déjà
            is_duplicate = False
            for existing in filtered:
                ex, ey, ew, eh = existing['bbox']
                
                # Calcul de l'intersection
                overlap_x = max(0, min(x + w, ex + ew) - max(x, ex))
                overlap_y = max(0, min(y + h, ey + eh) - max(y, ey))
                overlap_area = overlap_x * overlap_y
                
                # Si plus de 50% de chevauchement, c'est un doublon
                total_area = w * h
                if total_area > 0 and overlap_area / total_area > 0.5:
                    is_duplicate = True
                    # Garder la détection avec la plus haute confiance
                    if detection['confidence'] > existing['confidence']:
                        filtered.remove(existing)
                        break
                    else:
                        break
            
            if not is_duplicate:
                filtered.append(detection)
        
        # Limiter le nombre de détections pour éviter le spam
        filtered = sorted(filtered, key=lambda x: x['confidence'], reverse=True)[:10]
        
        return filtered


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


# Factory pour compatibilité
def create_smart_detector() -> SmartDetector:
    """Crée un détecteur intelligent pour l'interface web"""
    return SmartDetector()
