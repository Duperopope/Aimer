#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Gestionnaire de Configuration
© 2025 - Licence Apache 2.0

Gestionnaire centralisé de configuration
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """Gestionnaire de configuration centralisé"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialise le gestionnaire de configuration
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration depuis le fichier JSON"""
        if not self.config_path.exists():
            return self._get_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Erreur chargement config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut"""
        return {
            "app": {
                "name": "AIMER PRO",
                "version": "1.0.0",
                "description": "Application de Détection Universelle avec Detectron2",
                "license": "Apache 2.0",
                "author": "© 2025"
            },
            "detectron2": {
                "default_task": "detection",
                "confidence_threshold": 0.5,
                "models": {
                    "detection": "COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml",
                    "instance_segmentation": "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml",
                    "panoptic_segmentation": "COCO-PanopticSegmentation/panoptic_fpn_R_50_3x.yaml",
                    "keypoint_detection": "COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml"
                },
                "device": "auto",
                "batch_size": 1
            },
            "ui": {
                "theme": "dark",
                "language": "fr",
                "window": {
                    "width": 1280,
                    "height": 720,
                    "resizable": True
                },
                "font": {
                    "family": "Inter",
                    "size": 10
                }
            },
            "logging": {
                "level": "INFO",
                "file": "logs/aimer.log",
                "max_size_mb": 10,
                "backup_count": 5
            },
            "performance": {
                "gpu_optimization": True,
                "memory_limit_gb": 4,
                "max_concurrent_detections": 1
            },
            "paths": {
                "models": "models/",
                "datasets": "datasets/",
                "exports": "exports/",
                "screenshots": "screenshots/",
                "logs": "logs/"
            },
            "api": {
                "enabled": False,
                "host": "localhost",
                "port": 5000,
                "cors": True
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur de configuration
        
        Args:
            key: Clé de configuration (support notation pointée ex: "detectron2.confidence_threshold")
            default: Valeur par défaut si clé non trouvée
            
        Returns:
            Valeur de configuration ou default
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Définit une valeur de configuration
        
        Args:
            key: Clé de configuration (support notation pointée)
            value: Nouvelle valeur
        """
        keys = key.split('.')
        config = self._config
        
        # Naviguer jusqu'au parent de la clé finale
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Définir la valeur finale
        config[keys[-1]] = value
    
    def get_app_config(self) -> Dict[str, Any]:
        """Récupère la configuration de l'application"""
        return self._config.get("app", {})
    
    def get_detectron2_config(self) -> Dict[str, Any]:
        """Récupère la configuration Detectron2"""
        return self._config.get("detectron2", {})
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Récupère la configuration UI"""
        return self._config.get("ui", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Récupère la configuration de logging"""
        return self._config.get("logging", {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Récupère la configuration de performance"""
        return self._config.get("performance", {})
    
    def get_paths_config(self) -> Dict[str, Any]:
        """Récupère la configuration des chemins"""
        return self._config.get("paths", {})
    
    def get_api_config(self) -> Dict[str, Any]:
        """Récupère la configuration API"""
        return self._config.get("api", {})
    
    def save_config(self) -> bool:
        """
        Sauvegarde la configuration dans le fichier
        
        Returns:
            True si succès, False sinon
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Erreur sauvegarde config: {e}")
            return False
    
    def reload_config(self) -> None:
        """Recharge la configuration depuis le fichier"""
        self._config = self._load_config()
    
    def get_full_config(self) -> Dict[str, Any]:
        """Récupère la configuration complète"""
        return self._config.copy()
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """
        Met à jour la configuration avec un nouveau dictionnaire
        
        Args:
            new_config: Nouvelle configuration (fusion avec l'existante)
        """
        def deep_update(base_dict: Dict, update_dict: Dict) -> Dict:
            """Mise à jour récursive des dictionnaires"""
            for key, value in update_dict.items():
                if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                    deep_update(base_dict[key], value)
                else:
                    base_dict[key] = value
            return base_dict
        
        deep_update(self._config, new_config)
