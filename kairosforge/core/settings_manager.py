#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Gestionnaire de Paramètres
© 2025 KairosForge - Tous droits réservés

Gestion centralisée des paramètres application
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
from PyQt6.QtCore import QSettings, QStandardPaths

@dataclass
class UISettings:
    """Paramètres d'interface utilisateur"""
    theme: str = "dark"
    language: str = "fr"
    window_geometry: str = ""
    window_state: str = ""
    sidebar_width: int = 240
    font_size: int = 10
    animations_enabled: bool = True
    show_tooltips: bool = True

@dataclass
class SystemSettings:
    """Paramètres système"""
    auto_start_monitoring: bool = True
    monitoring_interval: float = 1.0
    enable_gpu_monitoring: bool = True
    enable_notifications: bool = True
    log_level: str = "INFO"
    max_log_files: int = 10

@dataclass
class DetectionSettings:
    """Paramètres de détection"""
    confidence_threshold: float = 0.5
    nms_threshold: float = 0.4
    max_detections: int = 100
    input_size: int = 640
    device: str = "auto"  # auto, cpu, cuda
    model_path: str = "yolov8n.pt"
    enable_tracking: bool = False

@dataclass
class LearningSettings:
    """Paramètres d'apprentissage"""
    batch_size: int = 16
    epochs: int = 100
    learning_rate: float = 0.001
    augmentation_enabled: bool = True
    validation_split: float = 0.2
    save_best_only: bool = True
    early_stopping: bool = True

@dataclass
class ExportSettings:
    """Paramètres d'export"""
    default_format: str = "json"
    include_confidence: bool = True
    include_timestamps: bool = True
    output_directory: str = "exports"
    auto_open_results: bool = False

class SettingsManager:
    """
    Gestionnaire centralisé des paramètres
    Utilise QSettings pour la persistance cross-platform
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SettingsManager")
        
        # Configuration QSettings
        self.qsettings = QSettings("KairosForge", "AIMER PRO")
        
        # Paramètres par catégorie
        self.ui_settings = UISettings()
        self.system_settings = SystemSettings()
        self.detection_settings = DetectionSettings()
        self.learning_settings = LearningSettings()
        self.export_settings = ExportSettings()
        
        # Fichier de sauvegarde JSON (backup)
        self.config_dir = Path(QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppConfigLocation
        )) / "KairosForge" / "AIMER PRO"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "settings.json"
        
        # Charger paramètres
        self.load_settings()
        
        self.logger.info("Gestionnaire de paramètres initialisé")
    
    def load_settings(self):
        """Charge tous les paramètres"""
        try:
            # Charger depuis QSettings
            self._load_ui_settings()
            self._load_system_settings()
            self._load_detection_settings()
            self._load_learning_settings()
            self._load_export_settings()
            
            # Charger depuis fichier JSON (si disponible)
            self._load_from_json()
            
            self.logger.info("Paramètres chargés")
            
        except Exception as e:
            self.logger.error(f"Erreur chargement paramètres: {e}")
            self._load_defaults()
    
    def _load_ui_settings(self):
        """Charge les paramètres UI"""
        self.qsettings.beginGroup("UI")
        
        self.ui_settings.theme = self.qsettings.value("theme", self.ui_settings.theme)
        self.ui_settings.language = self.qsettings.value("language", self.ui_settings.language)
        self.ui_settings.window_geometry = self.qsettings.value("window_geometry", self.ui_settings.window_geometry)
        self.ui_settings.window_state = self.qsettings.value("window_state", self.ui_settings.window_state)
        self.ui_settings.sidebar_width = int(self.qsettings.value("sidebar_width", self.ui_settings.sidebar_width))
        self.ui_settings.font_size = int(self.qsettings.value("font_size", self.ui_settings.font_size))
        self.ui_settings.animations_enabled = self.qsettings.value("animations_enabled", self.ui_settings.animations_enabled, type=bool)
        self.ui_settings.show_tooltips = self.qsettings.value("show_tooltips", self.ui_settings.show_tooltips, type=bool)
        
        self.qsettings.endGroup()
    
    def _load_system_settings(self):
        """Charge les paramètres système"""
        self.qsettings.beginGroup("System")
        
        self.system_settings.auto_start_monitoring = self.qsettings.value("auto_start_monitoring", self.system_settings.auto_start_monitoring, type=bool)
        self.system_settings.monitoring_interval = float(self.qsettings.value("monitoring_interval", self.system_settings.monitoring_interval))
        self.system_settings.enable_gpu_monitoring = self.qsettings.value("enable_gpu_monitoring", self.system_settings.enable_gpu_monitoring, type=bool)
        self.system_settings.enable_notifications = self.qsettings.value("enable_notifications", self.system_settings.enable_notifications, type=bool)
        self.system_settings.log_level = self.qsettings.value("log_level", self.system_settings.log_level)
        self.system_settings.max_log_files = int(self.qsettings.value("max_log_files", self.system_settings.max_log_files))
        
        self.qsettings.endGroup()
    
    def _load_detection_settings(self):
        """Charge les paramètres de détection"""
        self.qsettings.beginGroup("Detection")
        
        self.detection_settings.confidence_threshold = float(self.qsettings.value("confidence_threshold", self.detection_settings.confidence_threshold))
        self.detection_settings.nms_threshold = float(self.qsettings.value("nms_threshold", self.detection_settings.nms_threshold))
        self.detection_settings.max_detections = int(self.qsettings.value("max_detections", self.detection_settings.max_detections))
        self.detection_settings.input_size = int(self.qsettings.value("input_size", self.detection_settings.input_size))
        self.detection_settings.device = self.qsettings.value("device", self.detection_settings.device)
        self.detection_settings.model_path = self.qsettings.value("model_path", self.detection_settings.model_path)
        self.detection_settings.enable_tracking = self.qsettings.value("enable_tracking", self.detection_settings.enable_tracking, type=bool)
        
        self.qsettings.endGroup()
    
    def _load_learning_settings(self):
        """Charge les paramètres d'apprentissage"""
        self.qsettings.beginGroup("Learning")
        
        self.learning_settings.batch_size = int(self.qsettings.value("batch_size", self.learning_settings.batch_size))
        self.learning_settings.epochs = int(self.qsettings.value("epochs", self.learning_settings.epochs))
        self.learning_settings.learning_rate = float(self.qsettings.value("learning_rate", self.learning_settings.learning_rate))
        self.learning_settings.augmentation_enabled = self.qsettings.value("augmentation_enabled", self.learning_settings.augmentation_enabled, type=bool)
        self.learning_settings.validation_split = float(self.qsettings.value("validation_split", self.learning_settings.validation_split))
        self.learning_settings.save_best_only = self.qsettings.value("save_best_only", self.learning_settings.save_best_only, type=bool)
        self.learning_settings.early_stopping = self.qsettings.value("early_stopping", self.learning_settings.early_stopping, type=bool)
        
        self.qsettings.endGroup()
    
    def _load_export_settings(self):
        """Charge les paramètres d'export"""
        self.qsettings.beginGroup("Export")
        
        self.export_settings.default_format = self.qsettings.value("default_format", self.export_settings.default_format)
        self.export_settings.include_confidence = self.qsettings.value("include_confidence", self.export_settings.include_confidence, type=bool)
        self.export_settings.include_timestamps = self.qsettings.value("include_timestamps", self.export_settings.include_timestamps, type=bool)
        self.export_settings.output_directory = self.qsettings.value("output_directory", self.export_settings.output_directory)
        self.export_settings.auto_open_results = self.qsettings.value("auto_open_results", self.export_settings.auto_open_results, type=bool)
        
        self.qsettings.endGroup()
    
    def _load_from_json(self):
        """Charge depuis le fichier JSON de sauvegarde"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Fusionner avec paramètres actuels
                if "ui" in data:
                    self._update_dataclass(self.ui_settings, data["ui"])
                if "system" in data:
                    self._update_dataclass(self.system_settings, data["system"])
                if "detection" in data:
                    self._update_dataclass(self.detection_settings, data["detection"])
                if "learning" in data:
                    self._update_dataclass(self.learning_settings, data["learning"])
                if "export" in data:
                    self._update_dataclass(self.export_settings, data["export"])
                
                self.logger.info("Paramètres JSON chargés")
                
        except Exception as e:
            self.logger.warning(f"Erreur chargement JSON: {e}")
    
    def _update_dataclass(self, obj, data: Dict):
        """Met à jour un dataclass avec des données"""
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
    
    def _load_defaults(self):
        """Charge les paramètres par défaut"""
        self.ui_settings = UISettings()
        self.system_settings = SystemSettings()
        self.detection_settings = DetectionSettings()
        self.learning_settings = LearningSettings()
        self.export_settings = ExportSettings()
        
        self.logger.info("Paramètres par défaut chargés")
    
    def save_settings(self):
        """Sauvegarde tous les paramètres"""
        try:
            # Sauvegarder dans QSettings
            self._save_ui_settings()
            self._save_system_settings()
            self._save_detection_settings()
            self._save_learning_settings()
            self._save_export_settings()
            
            # Sauvegarder dans JSON
            self._save_to_json()
            
            # Synchroniser QSettings
            self.qsettings.sync()
            
            self.logger.info("Paramètres sauvegardés")
            
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde paramètres: {e}")
    
    def _save_ui_settings(self):
        """Sauvegarde les paramètres UI"""
        self.qsettings.beginGroup("UI")
        
        self.qsettings.setValue("theme", self.ui_settings.theme)
        self.qsettings.setValue("language", self.ui_settings.language)
        self.qsettings.setValue("window_geometry", self.ui_settings.window_geometry)
        self.qsettings.setValue("window_state", self.ui_settings.window_state)
        self.qsettings.setValue("sidebar_width", self.ui_settings.sidebar_width)
        self.qsettings.setValue("font_size", self.ui_settings.font_size)
        self.qsettings.setValue("animations_enabled", self.ui_settings.animations_enabled)
        self.qsettings.setValue("show_tooltips", self.ui_settings.show_tooltips)
        
        self.qsettings.endGroup()
    
    def _save_system_settings(self):
        """Sauvegarde les paramètres système"""
        self.qsettings.beginGroup("System")
        
        self.qsettings.setValue("auto_start_monitoring", self.system_settings.auto_start_monitoring)
        self.qsettings.setValue("monitoring_interval", self.system_settings.monitoring_interval)
        self.qsettings.setValue("enable_gpu_monitoring", self.system_settings.enable_gpu_monitoring)
        self.qsettings.setValue("enable_notifications", self.system_settings.enable_notifications)
        self.qsettings.setValue("log_level", self.system_settings.log_level)
        self.qsettings.setValue("max_log_files", self.system_settings.max_log_files)
        
        self.qsettings.endGroup()
    
    def _save_detection_settings(self):
        """Sauvegarde les paramètres de détection"""
        self.qsettings.beginGroup("Detection")
        
        self.qsettings.setValue("confidence_threshold", self.detection_settings.confidence_threshold)
        self.qsettings.setValue("nms_threshold", self.detection_settings.nms_threshold)
        self.qsettings.setValue("max_detections", self.detection_settings.max_detections)
        self.qsettings.setValue("input_size", self.detection_settings.input_size)
        self.qsettings.setValue("device", self.detection_settings.device)
        self.qsettings.setValue("model_path", self.detection_settings.model_path)
        self.qsettings.setValue("enable_tracking", self.detection_settings.enable_tracking)
        
        self.qsettings.endGroup()
    
    def _save_learning_settings(self):
        """Sauvegarde les paramètres d'apprentissage"""
        self.qsettings.beginGroup("Learning")
        
        self.qsettings.setValue("batch_size", self.learning_settings.batch_size)
        self.qsettings.setValue("epochs", self.learning_settings.epochs)
        self.qsettings.setValue("learning_rate", self.learning_settings.learning_rate)
        self.qsettings.setValue("augmentation_enabled", self.learning_settings.augmentation_enabled)
        self.qsettings.setValue("validation_split", self.learning_settings.validation_split)
        self.qsettings.setValue("save_best_only", self.learning_settings.save_best_only)
        self.qsettings.setValue("early_stopping", self.learning_settings.early_stopping)
        
        self.qsettings.endGroup()
    
    def _save_export_settings(self):
        """Sauvegarde les paramètres d'export"""
        self.qsettings.beginGroup("Export")
        
        self.qsettings.setValue("default_format", self.export_settings.default_format)
        self.qsettings.setValue("include_confidence", self.export_settings.include_confidence)
        self.qsettings.setValue("include_timestamps", self.export_settings.include_timestamps)
        self.qsettings.setValue("output_directory", self.export_settings.output_directory)
        self.qsettings.setValue("auto_open_results", self.export_settings.auto_open_results)
        
        self.qsettings.endGroup()
    
    def _save_to_json(self):
        """Sauvegarde dans le fichier JSON"""
        try:
            data = {
                "ui": asdict(self.ui_settings),
                "system": asdict(self.system_settings),
                "detection": asdict(self.detection_settings),
                "learning": asdict(self.learning_settings),
                "export": asdict(self.export_settings),
                "metadata": {
                    "version": "1.0.0",
                    "saved_at": datetime.now().isoformat()
                }
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Paramètres JSON sauvegardés")
            
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde JSON: {e}")
    
    def reset_to_defaults(self):
        """Remet tous les paramètres par défaut"""
        try:
            # Effacer QSettings
            self.qsettings.clear()
            
            # Supprimer fichier JSON
            if self.config_file.exists():
                self.config_file.unlink()
            
            # Recharger défauts
            self._load_defaults()
            
            # Sauvegarder
            self.save_settings()
            
            self.logger.info("Paramètres remis par défaut")
            
        except Exception as e:
            self.logger.error(f"Erreur reset paramètres: {e}")
    
    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """Récupère un paramètre spécifique"""
        try:
            settings_obj = getattr(self, f"{category}_settings", None)
            if settings_obj and hasattr(settings_obj, key):
                return getattr(settings_obj, key)
            return default
        except Exception:
            return default
    
    def set_setting(self, category: str, key: str, value: Any):
        """Définit un paramètre spécifique"""
        try:
            settings_obj = getattr(self, f"{category}_settings", None)
            if settings_obj and hasattr(settings_obj, key):
                setattr(settings_obj, key, value)
                self.logger.info(f"Paramètre {category}.{key} = {value}")
        except Exception as e:
            self.logger.error(f"Erreur définition paramètre: {e}")
    
    def export_settings(self, file_path: str) -> bool:
        """Exporte les paramètres vers un fichier"""
        try:
            data = {
                "ui": asdict(self.ui_settings),
                "system": asdict(self.system_settings),
                "detection": asdict(self.detection_settings),
                "learning": asdict(self.learning_settings),
                "export": asdict(self.export_settings),
                "metadata": {
                    "version": "1.0.0",
                    "exported_at": datetime.now().isoformat(),
                    "application": "AIMER PRO",
                    "company": "KairosForge"
                }
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Paramètres exportés vers {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur export paramètres: {e}")
            return False
    
    def import_settings(self, file_path: str) -> bool:
        """Importe les paramètres depuis un fichier"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Valider structure
            if not all(key in data for key in ["ui", "system", "detection", "learning", "export"]):
                raise ValueError("Structure de fichier invalide")
            
            # Importer données
            self._update_dataclass(self.ui_settings, data["ui"])
            self._update_dataclass(self.system_settings, data["system"])
            self._update_dataclass(self.detection_settings, data["detection"])
            self._update_dataclass(self.learning_settings, data["learning"])
            self._update_dataclass(self.export_settings, data["export"])
            
            # Sauvegarder
            self.save_settings()
            
            self.logger.info(f"Paramètres importés depuis {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur import paramètres: {e}")
            return False

def create_settings_manager() -> SettingsManager:
    """Factory pour créer le gestionnaire de paramètres"""
    return SettingsManager()
