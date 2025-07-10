#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Hardware Monitor
© 2025 - Licence Apache 2.0

Monitoring hardware temps réel pour optimisation IA
"""

import psutil
import platform
import time
import threading
import json
from datetime import datetime
from typing import Dict, Any, Optional

try:
    import GPUtil

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

from .logger import Logger


class HardwareMonitor:
    """Moniteur hardware temps réel"""

    def __init__(self):
        self.logger = Logger("HardwareMonitor")
        self.monitoring = False
        self.data_history = []
        self.max_history = 100
        self.update_interval = 1.0
        self.monitor_thread = None

    def get_system_info(self) -> Dict[str, Any]:
        """Informations système complètes"""
        try:
            return {
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "hostname": platform.node(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            self.logger.error(f"Erreur système info: {e}")
            return {"error": str(e)}

    def get_cpu_info(self) -> Dict[str, Any]:
        """Informations CPU détaillées"""
        try:
            cpu_freq = psutil.cpu_freq()
            cpu_times = psutil.cpu_times()

            return {
                "name": platform.processor(),
                "cores_physical": psutil.cpu_count(logical=False),
                "cores_logical": psutil.cpu_count(logical=True),
                "frequency": {
                    "current": cpu_freq.current if cpu_freq else 0,
                    "min": cpu_freq.min if cpu_freq else 0,
                    "max": cpu_freq.max if cpu_freq else 0,
                },
                "usage": {
                    "overall": psutil.cpu_percent(interval=0.1),
                    "per_core": psutil.cpu_percent(interval=0.1, percpu=True),
                },
                "times": {
                    "user": cpu_times.user,
                    "system": cpu_times.system,
                    "idle": cpu_times.idle,
                },
                "temperature": self.get_cpu_temperature(),
            }
        except Exception as e:
            self.logger.error(f"Erreur CPU info: {e}")
            return {"error": str(e)}

    def get_memory_info(self) -> Dict[str, Any]:
        """Informations mémoire"""
        try:
            virtual_mem = psutil.virtual_memory()
            swap_mem = psutil.swap_memory()

            return {
                "virtual": {
                    "total": virtual_mem.total,
                    "available": virtual_mem.available,
                    "used": virtual_mem.used,
                    "free": virtual_mem.free,
                    "percentage": virtual_mem.percent,
                    "cached": getattr(virtual_mem, "cached", 0),
                    "buffers": getattr(virtual_mem, "buffers", 0),
                },
                "swap": {
                    "total": swap_mem.total,
                    "used": swap_mem.used,
                    "free": swap_mem.free,
                    "percentage": swap_mem.percent,
                },
            }
        except Exception as e:
            self.logger.error(f"Erreur mémoire info: {e}")
            return {"error": str(e)}

    def get_gpu_info(self) -> Dict[str, Any]:
        """Informations GPU"""
        try:
            if not GPU_AVAILABLE:
                return {
                    "available": False,
                    "error": "GPUtil non disponible",
                    "gpus": [],
                }

            gpus = GPUtil.getGPUs()
            gpu_list = []

            for gpu in gpus:
                gpu_info = {
                    "id": gpu.id,
                    "name": gpu.name,
                    "memory": {
                        "total": gpu.memoryTotal,
                        "used": gpu.memoryUsed,
                        "free": gpu.memoryFree,
                        "percentage": (
                            (gpu.memoryUsed / gpu.memoryTotal) * 100
                            if gpu.memoryTotal > 0
                            else 0
                        ),
                    },
                    "load": gpu.load * 100,
                    "temperature": gpu.temperature,
                    "uuid": getattr(gpu, "uuid", "N/A"),
                }
                gpu_list.append(gpu_info)

            return {"available": True, "count": len(gpu_list), "gpus": gpu_list}

        except Exception as e:
            self.logger.error(f"Erreur GPU info: {e}")
            return {"available": False, "error": str(e), "gpus": []}

    def get_disk_info(self) -> Dict[str, Any]:
        """Informations disques"""
        try:
            disk_list = []

            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)

                    disk_info = {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percentage": (
                            (usage.used / usage.total) * 100 if usage.total > 0 else 0
                        ),
                    }
                    disk_list.append(disk_info)

                except (PermissionError, OSError):
                    continue

            return {
                "disks": disk_list,
                "total_space": sum(d["total"] for d in disk_list),
                "total_used": sum(d["used"] for d in disk_list),
                "total_free": sum(d["free"] for d in disk_list),
            }

        except Exception as e:
            self.logger.error(f"Erreur disque info: {e}")
            return {"error": str(e)}

    def get_network_info(self) -> Dict[str, Any]:
        """Informations réseau"""
        try:
            network_io = psutil.net_io_counters()

            return {
                "bytes_sent": network_io.bytes_sent,
                "bytes_recv": network_io.bytes_recv,
                "packets_sent": network_io.packets_sent,
                "packets_recv": network_io.packets_recv,
                "errin": network_io.errin,
                "errout": network_io.errout,
                "dropin": network_io.dropin,
                "dropout": network_io.dropout,
            }

        except Exception as e:
            self.logger.error(f"Erreur réseau info: {e}")
            return {"error": str(e)}

    def get_cpu_temperature(self) -> Optional[float]:
        """Température CPU (si disponible)"""
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if "cpu" in name.lower() or "core" in name.lower():
                            if entries:
                                return entries[0].current
            return None
        except:
            return None

    def get_complete_info(self) -> Dict[str, Any]:
        """Informations complètes du système"""
        return {
            "timestamp": datetime.now().isoformat(),
            "system": self.get_system_info(),
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "gpu": self.get_gpu_info(),
            "disk": self.get_disk_info(),
            "network": self.get_network_info(),
        }

    def calculate_ai_performance_score(self) -> Dict[str, Any]:
        """Calcule un score de performance pour l'IA"""
        try:
            info = self.get_complete_info()

            # Score CPU (0-100)
            cpu_score = max(0, 100 - info["cpu"]["usage"]["overall"])

            # Score mémoire (0-100)
            memory_score = max(0, 100 - info["memory"]["virtual"]["percentage"])

            # Score GPU (0-100)
            gpu_score = 50  # Score par défaut
            if info["gpu"]["available"] and info["gpu"]["gpus"]:
                gpu = info["gpu"]["gpus"][0]
                gpu_score = max(0, 100 - gpu["load"])

            # Score disque (0-100)
            disk_score = 100
            if "disks" in info["disk"]:
                avg_disk_usage = sum(
                    d["percentage"] for d in info["disk"]["disks"]
                ) / len(info["disk"]["disks"])
                disk_score = max(0, 100 - avg_disk_usage)

            # Score global
            overall_score = (cpu_score + memory_score + gpu_score + disk_score) / 4

            # Recommandations
            recommendations = []
            if cpu_score < 50:
                recommendations.append("CPU surchargé - fermer des applications")
            if memory_score < 50:
                recommendations.append("Mémoire insuffisante - libérer de la RAM")
            if gpu_score < 50:
                recommendations.append("GPU surchargé - réduire la qualité")
            if disk_score < 20:
                recommendations.append("Disque plein - libérer de l'espace")

            return {
                "overall_score": overall_score,
                "cpu_score": cpu_score,
                "memory_score": memory_score,
                "gpu_score": gpu_score,
                "disk_score": disk_score,
                "status": (
                    "excellent"
                    if overall_score > 80
                    else "good" if overall_score > 60 else "poor"
                ),
                "recommendations": recommendations,
                "ai_ready": overall_score > 60,
            }

        except Exception as e:
            self.logger.error(f"Erreur calcul performance: {e}")
            return {"error": str(e)}

    def start_monitoring(self, interval: float = 1.0):
        """Démarre le monitoring continu"""
        if self.monitoring:
            return

        self.monitoring = True
        self.update_interval = interval

        def monitor_loop():
            while self.monitoring:
                try:
                    data = self.get_complete_info()
                    data["performance"] = self.calculate_ai_performance_score()

                    self.data_history.append(data)

                    # Limiter l'historique
                    if len(self.data_history) > self.max_history:
                        self.data_history.pop(0)

                    time.sleep(self.update_interval)

                except Exception as e:
                    self.logger.error(f"Erreur monitoring: {e}")
                    time.sleep(self.update_interval)

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()

        self.logger.info("Monitoring hardware démarré")

    def stop_monitoring(self):
        """Arrête le monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        self.logger.info("Monitoring hardware arrêté")

    def get_latest_data(self) -> Optional[Dict[str, Any]]:
        """Récupère les dernières données"""
        return self.data_history[-1] if self.data_history else None

    def get_history(self, limit: int = 50) -> list:
        """Récupère l'historique des données"""
        return self.data_history[-limit:] if self.data_history else []

    def export_data(self, filepath: str):
        """Exporte les données vers un fichier JSON"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.data_history, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Données exportées vers {filepath}")
        except Exception as e:
            self.logger.error(f"Erreur export: {e}")
