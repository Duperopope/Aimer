#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Système de Logging
© 2025 - Licence Apache 2.0

Système de logging unifié et intelligent
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime


class Logger:
    """Système de logging unifié pour AIMER PRO"""

    def __init__(self, name: str, log_level: str = "INFO"):
        """
        Initialise le logger

        Args:
            name: Nom du logger
            log_level: Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.name = name
        self.logger = logging.getLogger(name)

        # Éviter la duplication des handlers
        if not self.logger.handlers:
            self._setup_logger(log_level)

    def _setup_logger(self, log_level: str):
        """Configure le logger avec handlers console et fichier"""
        # Niveau de log
        level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger.setLevel(level)

        # Format des messages
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Handler console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Handler fichier
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)

            file_handler = logging.FileHandler(log_dir / "aimer.log", encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Erreur création handler fichier: {e}")

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log niveau DEBUG"""
        self._log(logging.DEBUG, message, extra)

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log niveau INFO"""
        self._log(logging.INFO, message, extra)

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log niveau WARNING"""
        self._log(logging.WARNING, message, extra)

    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log niveau ERROR"""
        self._log(logging.ERROR, message, extra)

    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log niveau CRITICAL"""
        self._log(logging.CRITICAL, message, extra)

    def _log(self, level: int, message: str, extra: Optional[Dict[str, Any]] = None):
        """
        Log interne avec données supplémentaires

        Args:
            level: Niveau de log
            message: Message principal
            extra: Données supplémentaires à logger
        """
        if extra:
            # Formater les données supplémentaires
            extra_str = " | ".join([f"{k}={v}" for k, v in extra.items()])
            full_message = f"{message} | {extra_str}"
        else:
            full_message = message

        self.logger.log(level, full_message)

    def log_performance(self, operation: str, duration_ms: float, **kwargs):
        """
        Log spécialisé pour les performances

        Args:
            operation: Nom de l'opération
            duration_ms: Durée en millisecondes
            **kwargs: Métriques supplémentaires
        """
        metrics = {
            "operation": operation,
            "duration_ms": f"{duration_ms:.2f}",
            **kwargs,
        }
        self.info(f"Performance: {operation}", metrics)

    def log_detection(self, task_type: str, count: int, duration_ms: float, **kwargs):
        """
        Log spécialisé pour les détections

        Args:
            task_type: Type de tâche de détection
            count: Nombre d'objets détectés
            duration_ms: Durée de détection
            **kwargs: Métriques supplémentaires
        """
        metrics = {
            "task": task_type,
            "detections": count,
            "duration_ms": f"{duration_ms:.2f}",
            **kwargs,
        }
        self.info(f"Détection: {task_type}", metrics)

    def log_system_info(self, component: str, info: Dict[str, Any]):
        """
        Log d'informations système

        Args:
            component: Composant système
            info: Informations à logger
        """
        self.info(f"Système: {component}", info)

    def log_user_action(self, action: str, **kwargs):
        """
        Log d'actions utilisateur

        Args:
            action: Action effectuée
            **kwargs: Détails de l'action
        """
        self.info(f"Action: {action}", kwargs)

    def log_error_with_context(self, error: Exception, context: Dict[str, Any]):
        """
        Log d'erreur avec contexte détaillé

        Args:
            error: Exception capturée
            context: Contexte de l'erreur
        """
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            **context,
        }
        self.error(f"Erreur: {type(error).__name__}", error_info)


# Instance globale pour faciliter l'utilisation
_global_logger = None


def get_logger(name: str = "AIMER") -> Logger:
    """
    Récupère ou crée un logger

    Args:
        name: Nom du logger

    Returns:
        Instance de Logger
    """
    global _global_logger
    if _global_logger is None or _global_logger.name != name:
        _global_logger = Logger(name)
    return _global_logger


def setup_logging(level: str = "INFO"):
    """
    Configure le logging global

    Args:
        level: Niveau de log global
    """
    global _global_logger
    _global_logger = Logger("AIMER", level)
    return _global_logger
