#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Module - Modules centraux du système YOLO intelligent
Contient les composants fondamentaux pour le profiling, l'adaptation et la gestion
"""

from .smart_system_profiler import SmartSystemProfiler, SystemCapabilities, SmartLogger
from .adaptive_engine import ContextualAdaptationEngine, AdaptationConfig
from .intelligent_storage_manager import IntelligentStorageManager, StorageRecommendation, DriveInfo
from .professional_dataset_manager import ProfessionalDatasetManager, DatasetInfo, ImageAnalysis
from .project_cleaner import ProjectCleaner

__version__ = "2.0.0"
__author__ = "YOLO Ultimate System"

__all__ = [
    "SmartSystemProfiler",
    "SystemCapabilities", 
    "SmartLogger",
    "ContextualAdaptationEngine",
    "AdaptationConfig",
    "IntelligentStorageManager",
    "StorageRecommendation",
    "DriveInfo",
    "ProfessionalDatasetManager",
    "DatasetInfo",
    "ImageAnalysis",
    "ProjectCleaner"
]
