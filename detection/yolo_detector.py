from ultralytics import YOLO
import cv2
import numpy as np
from typing import List, Tuple, Dict

class AdaptiveYOLODetector:
    def __init__(self, model_path="yolov8n.pt", confidence_threshold=0.3):
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        self.custom_classes = {}  # Classes personnalisées apprises
        
    def detect_objects(self, image: np.ndarray, target_classes: List[str] = None) -> List[Dict]:
        """
        Détecte les objets dans l'image
        Retourne une liste de détections avec incertitude
        """
        results = self.model(image, conf=self.confidence_threshold)
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    class_name = self.model.names[class_id]
                    
                    # Filtrer par classes cibles si spécifiées
                    if target_classes and class_name not in target_classes:
                        continue
                    
                    # Calculer l'incertitude (1 - confidence)
                    uncertainty = 1.0 - confidence
                    
                    detection = {
                        'bbox': [x1, y1, x2, y2],
                        'confidence': float(confidence),
                        'uncertainty': float(uncertainty),
                        'class_name': class_name,
                        'class_id': class_id
                    }
                    detections.append(detection)
        
        return detections
    
    def get_uncertain_detections(self, detections: List[Dict], top_k: int = 5) -> List[Dict]:
        """
        Retourne les détections les plus incertaines pour annotation
        """
        # Trier par incertitude décroissante
        uncertain_detections = sorted(detections, key=lambda x: x['uncertainty'], reverse=True)
        return uncertain_detections[:top_k]
    
    def update_with_feedback(self, image: np.ndarray, detections: List[Dict], feedback: List[bool]):
        """
        Met à jour le modèle avec le feedback utilisateur
        """
        # Cette fonction peut être étendue pour réentraîner le modèle
        # Pour l'instant, on stocke juste les statistiques
        correct_count = sum(feedback)
        total_count = len(feedback)
        
        print(f"Feedback: {correct_count}/{total_count} détections correctes")
        return correct_count / total_count if total_count > 0 else 0
