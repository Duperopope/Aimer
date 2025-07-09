#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart System Profiler - Système de profiling intelligent et adaptatif
Découvre dynamiquement les capacités système sans hardcoding
"""

import sys
import os
import platform
import psutil
import time
import json
import logging
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

@dataclass
class SystemCapabilities:
    """Structure des capacités système découvertes"""
    python_profile: Dict[str, Any]
    hardware_profile: Dict[str, Any]
    memory_profile: Dict[str, Any]
    gpu_profile: Dict[str, Any]
    thermal_profile: Dict[str, Any]
    storage_profile: Dict[str, Any]
    network_profile: Dict[str, Any]
    user_context: Dict[str, Any]
    performance_score: float
    adaptation_recommendations: List[str]

class SmartLogger:
    """Système de logging professionnel avec diagnostic intelligent"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Configuration logging professionnel
        self.setup_logging()
        
        # Métriques de performance
        self.performance_metrics = []
        self.error_patterns = {}
        
    def setup_logging(self):
        """Configure le système de logging professionnel"""
        log_format = '%(asctime)s | %(levelname)8s | %(name)20s | %(funcName)15s:%(lineno)4d | %(message)s'
        
        # Logger principal
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(self.log_dir / f"system_profiler_{datetime.now().strftime('%Y%m%d')}.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger("SmartSystemProfiler")
        
        # Logger séparé pour les métriques
        self.metrics_logger = logging.getLogger("PerformanceMetrics")
        metrics_handler = logging.FileHandler(self.log_dir / f"performance_metrics_{datetime.now().strftime('%Y%m%d')}.log")
        metrics_handler.setFormatter(logging.Formatter('%(asctime)s | METRICS | %(message)s'))
        self.metrics_logger.addHandler(metrics_handler)
        self.metrics_logger.setLevel(logging.INFO)
        
    def log_system_analysis(self, phase: str, analysis_result: Dict, success: bool = True):
        """Logs détaillés pour diagnostic précis"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        self.logger.info(f"{status} | {phase} | {json.dumps(analysis_result, indent=2)}")
        
    def log_adaptation_decision(self, decision: str, reasoning: Dict, confidence: float):
        """Trace les décisions d'adaptation avec justification"""
        self.logger.info(f"🎯 ADAPTATION | Decision: {decision} | Confidence: {confidence:.2f} | Reasoning: {reasoning}")
        
    def log_performance_metrics(self, metrics: Dict):
        """Métriques de performance pour optimisation"""
        self.metrics_logger.info(json.dumps(metrics))
        self.performance_metrics.append({
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        })
        
    def log_error_with_context(self, error: Exception, context: Dict):
        """Log d'erreur avec contexte pour diagnostic"""
        error_hash = hashlib.md5(str(error).encode()).hexdigest()[:8]
        
        if error_hash not in self.error_patterns:
            self.error_patterns[error_hash] = {"count": 0, "first_seen": datetime.now()}
        
        self.error_patterns[error_hash]["count"] += 1
        self.error_patterns[error_hash]["last_seen"] = datetime.now()
        
        self.logger.error(f"❌ ERROR #{error_hash} | {type(error).__name__}: {error} | Context: {context}")

class SmartSystemProfiler:
    """Découvre dynamiquement les capacités système réelles"""
    
    def __init__(self):
        self.logger = SmartLogger()
        self.capabilities_cache = {}
        self.benchmark_cache = {}
        
    def discover_system_capabilities(self) -> SystemCapabilities:
        """Point d'entrée principal - découvre toutes les capacités système"""
        self.logger.log_system_analysis("DISCOVERY_START", {"action": "Starting system capabilities discovery"})
        
        start_time = time.time()
        
        try:
            # Découverte par phases avec gestion d'erreurs
            python_profile = self._discover_python_capabilities()
            hardware_profile = self._discover_hardware_capabilities()
            memory_profile = self._discover_memory_capabilities()
            gpu_profile = self._discover_gpu_capabilities()
            thermal_profile = self._discover_thermal_capabilities()
            storage_profile = self._discover_storage_capabilities()
            network_profile = self._discover_network_capabilities()
            user_context = self._analyze_user_context()
            
            # Calcul du score de performance global
            performance_score = self._calculate_performance_score({
                "hardware": hardware_profile,
                "memory": memory_profile,
                "gpu": gpu_profile,
                "storage": storage_profile
            })
            
            # Génération des recommandations d'adaptation
            recommendations = self._generate_adaptation_recommendations({
                "python": python_profile,
                "hardware": hardware_profile,
                "memory": memory_profile,
                "gpu": gpu_profile,
                "performance_score": performance_score
            })
            
            capabilities = SystemCapabilities(
                python_profile=python_profile,
                hardware_profile=hardware_profile,
                memory_profile=memory_profile,
                gpu_profile=gpu_profile,
                thermal_profile=thermal_profile,
                storage_profile=storage_profile,
                network_profile=network_profile,
                user_context=user_context,
                performance_score=performance_score,
                adaptation_recommendations=recommendations
            )
            
            discovery_time = time.time() - start_time
            self.logger.log_performance_metrics({
                "discovery_time_seconds": discovery_time,
                "performance_score": performance_score,
                "capabilities_count": len(asdict(capabilities))
            })
            
            self.logger.log_system_analysis("DISCOVERY_COMPLETE", {
                "performance_score": performance_score,
                "discovery_time": f"{discovery_time:.2f}s",
                "recommendations_count": len(recommendations)
            })
            
            return capabilities
            
        except Exception as e:
            self.logger.log_error_with_context(e, {"phase": "system_discovery"})
            # Retourner des capacités minimales en cas d'erreur
            return self._get_fallback_capabilities()
    
    def _discover_python_capabilities(self) -> Dict[str, Any]:
        """Découvre les capacités Python réelles (pas de hardcoding de version)"""
        try:
            python_info = {
                "version": {
                    "major": sys.version_info.major,
                    "minor": sys.version_info.minor,
                    "micro": sys.version_info.micro,
                    "full": sys.version,
                    "version_string": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
                },
                "implementation": platform.python_implementation(),
                "compiler": platform.python_compiler(),
                "executable": sys.executable,
                "platform": sys.platform,
                "architecture": platform.architecture(),
                "capabilities": self._test_python_capabilities()
            }
            
            # Test de compatibilité intelligent (pas de version hardcodée)
            compatibility = self._assess_python_compatibility(python_info)
            python_info["compatibility"] = compatibility
            
            self.logger.log_system_analysis("PYTHON_DISCOVERY", python_info)
            return python_info
            
        except Exception as e:
            self.logger.log_error_with_context(e, {"phase": "python_discovery"})
            return {"version": {"major": 3, "minor": 8}, "compatibility": {"score": 0.5, "issues": ["Discovery failed"]}}
    
    def _test_python_capabilities(self) -> Dict[str, bool]:
        """Teste les capacités Python réelles"""
        capabilities = {}
        
        # Test des modules critiques
        test_modules = [
            "tkinter", "threading", "multiprocessing", "sqlite3",
            "json", "pathlib", "dataclasses", "typing"
        ]
        
        for module in test_modules:
            try:
                __import__(module)
                capabilities[f"has_{module}"] = True
            except ImportError:
                capabilities[f"has_{module}"] = False
        
        # Test des fonctionnalités avancées
        try:
            import asyncio
            capabilities["has_asyncio"] = True
        except ImportError:
            capabilities["has_asyncio"] = False
        
        # Test performance basique
        start_time = time.time()
        sum(range(100000))  # Test calcul simple
        capabilities["basic_performance_ms"] = (time.time() - start_time) * 1000
        
        return capabilities
    
    def _assess_python_compatibility(self, python_info: Dict) -> Dict[str, Any]:
        """Évalue la compatibilité Python de manière intelligente"""
        version = python_info["version"]
        capabilities = python_info["capabilities"]
        
        # Score de compatibilité basé sur les capacités réelles
        compatibility_score = 1.0
        issues = []
        recommendations = []
        
        # Vérification des modules critiques
        critical_modules = ["tkinter", "threading", "sqlite3", "json"]
        missing_critical = [mod for mod in critical_modules if not capabilities.get(f"has_{mod}", False)]
        
        if missing_critical:
            compatibility_score -= 0.3
            issues.append(f"Missing critical modules: {missing_critical}")
            recommendations.append("Install missing Python modules")
        
        # Évaluation performance
        perf_ms = capabilities.get("basic_performance_ms", 1000)
        if perf_ms > 100:  # Performance très lente
            compatibility_score -= 0.2
            issues.append("Slow Python performance detected")
            recommendations.append("Consider Python optimization or hardware upgrade")
        
        # Bonus pour versions récentes (sans hardcoding strict)
        if version["major"] >= 3 and version["minor"] >= 9:
            compatibility_score += 0.1
            recommendations.append("Modern Python version - excellent compatibility")
        
        return {
            "score": max(0.0, min(1.0, compatibility_score)),
            "issues": issues,
            "recommendations": recommendations,
            "is_compatible": compatibility_score >= 0.7
        }
    
    def _discover_hardware_capabilities(self) -> Dict[str, Any]:
        """Découvre les capacités hardware par benchmarking réel"""
        try:
            # Informations système de base
            hardware_info = {
                "cpu": {
                    "name": platform.processor(),
                    "architecture": platform.machine(),
                    "cores_physical": psutil.cpu_count(logical=False),
                    "cores_logical": psutil.cpu_count(logical=True),
                    "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                "system": {
                    "platform": platform.system(),
                    "release": platform.release(),
                    "version": platform.version(),
                    "machine": platform.machine(),
                    "node": platform.node()
                }
            }
            
            # Benchmark performance CPU réel
            cpu_benchmark = self._benchmark_cpu_performance()
            hardware_info["cpu"]["benchmark"] = cpu_benchmark
            
            # Score de performance calculé
            performance_score = self._calculate_cpu_performance_score(cpu_benchmark)
            hardware_info["cpu"]["performance_score"] = performance_score
            
            self.logger.log_system_analysis("HARDWARE_DISCOVERY", hardware_info)
            return hardware_info
            
        except Exception as e:
            self.logger.log_error_with_context(e, {"phase": "hardware_discovery"})
            return {"cpu": {"cores_logical": 4, "performance_score": 0.5}}
    
    def _benchmark_cpu_performance(self) -> Dict[str, float]:
        """Benchmark CPU réel (pas de suppositions)"""
        benchmarks = {}
        
        try:
            # Test calcul intensif
            start_time = time.time()
            result = sum(i * i for i in range(1000000))
            benchmarks["compute_intensive_ms"] = (time.time() - start_time) * 1000
            
            # Test utilisation CPU actuelle
            cpu_percent_samples = []
            for _ in range(5):
                cpu_percent_samples.append(psutil.cpu_percent(interval=0.1))
            benchmarks["current_cpu_usage"] = sum(cpu_percent_samples) / len(cpu_percent_samples)
            
            # Test mémoire/CPU
            start_time = time.time()
            data = [i for i in range(100000)]
            data.sort()
            benchmarks["memory_cpu_ms"] = (time.time() - start_time) * 1000
            
        except Exception as e:
            self.logger.log_error_with_context(e, {"phase": "cpu_benchmark"})
            benchmarks = {"compute_intensive_ms": 1000, "current_cpu_usage": 50}
        
        return benchmarks
    
    def _calculate_cpu_performance_score(self, benchmark: Dict[str, float]) -> float:
        """Calcule un score de performance CPU normalisé"""
        try:
            # Score basé sur les benchmarks réels
            compute_score = max(0, 1 - (benchmark.get("compute_intensive_ms", 1000) / 2000))
            usage_score = max(0, 1 - (benchmark.get("current_cpu_usage", 50) / 100))
            memory_score = max(0, 1 - (benchmark.get("memory_cpu_ms", 1000) / 1000))
            
            # Score pondéré
            overall_score = (compute_score * 0.5 + usage_score * 0.3 + memory_score * 0.2)
            return min(1.0, max(0.0, overall_score))
            
        except Exception:
            return 0.5  # Score neutre en cas d'erreur
    
    def _discover_memory_capabilities(self) -> Dict[str, Any]:
        """Découvre les capacités mémoire réelles"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            memory_info = {
                "virtual": {
                    "total_gb": memory.total / (1024**3),
                    "available_gb": memory.available / (1024**3),
                    "used_gb": memory.used / (1024**3),
                    "percentage": memory.percent
                },
                "swap": {
                    "total_gb": swap.total / (1024**3),
                    "used_gb": swap.used / (1024**3),
                    "percentage": swap.percent
                }
            }
            
            # Test performance mémoire
            memory_benchmark = self._benchmark_memory_performance()
            memory_info["benchmark"] = memory_benchmark
            
            # Recommandations basées sur l'usage réel
            memory_info["recommendations"] = self._generate_memory_recommendations(memory_info)
            
            self.logger.log_system_analysis("MEMORY_DISCOVERY", memory_info)
            return memory_info
            
        except Exception as e:
            self.logger.log_error_with_context(e, {"phase": "memory_discovery"})
            return {"virtual": {"total_gb": 8, "available_gb": 4, "percentage": 50}}
    
    def _benchmark_memory_performance(self) -> Dict[str, float]:
        """Benchmark performance mémoire"""
        benchmarks = {}
        
        try:
            # Test allocation/libération mémoire
            start_time = time.time()
            large_list = [i for i in range(1000000)]
            allocation_time = time.time() - start_time
            
            start_time = time.time()
            del large_list
            deallocation_time = time.time() - start_time
            
            benchmarks["allocation_ms"] = allocation_time * 1000
            benchmarks["deallocation_ms"] = deallocation_time * 1000
            
        except Exception as e:
            self.logger.log_error_with_context(e, {"phase": "memory_benchmark"})
            benchmarks = {"allocation_ms": 100, "deallocation_ms": 10}
        
        return benchmarks
    
    def _discover_gpu_capabilities(self) -> Dict[str, Any]:
        """Découvre les capacités GPU de manière intelligente"""
        gpu_info = {"available": False, "type": "none", "capabilities": {}}
        
        try:
            # Tentative détection NVIDIA
            try:
                import pynvml
                pynvml.nvmlInit()
                device_count = pynvml.nvmlDeviceGetCount()
                
                if device_count > 0:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    name = pynvml.nvmlDeviceGetName(handle).decode()
                    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    
                    gpu_info = {
                        "available": True,
                        "type": "nvidia",
                        "name": name,
                        "memory_total_gb": memory_info.total / (1024**3),
                        "memory_free_gb": memory_info.free / (1024**3),
                        "capabilities": {"cuda": True, "compute_capability": "unknown"}
                    }
                    
            except ImportError:
                # Pas de pynvml, essayer d'autres méthodes
                pass
            
            # Tentative détection via subprocess (nvidia-smi)
            if not gpu_info["available"]:
                try:
                    result = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0 and result.stdout.strip():
                        lines = result.stdout.strip().split('\n')
                        if lines:
                            parts = lines[0].split(', ')
                            gpu_info = {
                                "available": True,
                                "type": "nvidia",
                                "name": parts[0],
                                "memory_total_gb": float(parts[1]) / 1024 if len(parts) > 1 else 0,
                                "capabilities": {"cuda": True}
                            }
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                    pass
            
            # Test capacités GPU si disponible
            if gpu_info["available"]:
                gpu_benchmark = self._benchmark_gpu_performance()
                gpu_info["benchmark"] = gpu_benchmark
            
            self.logger.log_system_analysis("GPU_DISCOVERY", gpu_info)
            return gpu_info
            
        except Exception as e:
            self.logger.log_error_with_context(e, {"phase": "gpu_discovery"})
            return gpu_info
    
    def _benchmark_gpu_performance(self) -> Dict[str, Any]:
        """Benchmark GPU si possible"""
        try:
            # Test basique avec PyTorch si disponible
            try:
                import torch
                if torch.cuda.is_available():
                    device = torch.device("cuda")
                    
                    # Test simple
                    start_time = time.time()
                    x = torch.randn(1000, 1000, device=device)
                    y = torch.matmul(x, x)
                    torch.cuda.synchronize()
                    gpu_compute_time = time.time() - start_time
                    
                    return {
                        "pytorch_available": True,
                        "compute_test_ms": gpu_compute_time * 1000,
                        "device_name": torch.cuda.get_device_name(0)
                    }
            except ImportError:
                pass
            
            return {"pytorch_available": False, "note": "No GPU benchmark available"}
            
        except Exception as e:
            self.logger.log_error_with_context(e, {"phase": "gpu_benchmark"})
            return {"error": "GPU benchmark failed"}
    
    def _discover_thermal_capabilities(self) -> Dict[str, Any]:
        """Découvre les contraintes thermiques"""
        thermal_info = {"monitoring_available": False}
        
        try:
            # Tentative lecture températures
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    thermal_info["monitoring_available"] = True
                    thermal_info["sensors"] = {}
                    
                    for name, entries in temps.items():
                        thermal_info["sensors"][name] = [
                            {"label": entry.label, "current": entry.current, "high": entry.high, "critical": entry.critical}
                            for entry in entries
                        ]
            
            self.logger.log_system_analysis("THERMAL_DISCOVERY", thermal_info)
            return thermal_info
            
        except Exception as e:
            self.logger.log_error_with_context(e, {"phase": "thermal_discovery"})
            return thermal_info
    
    def _discover_storage_capabilities(self) -> Dict[str, Any]:
        """Découvre les capacités de stockage"""
        try:
            storage_info = {"disks": []}
            
            # Informations disques
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    storage_info["disks"].append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total_gb": usage.total / (1024**3),
                        "used_gb": usage.used / (1024**3),
                        "free_gb": usage.free / (1024**3),
                        "percentage": (usage.used / usage.total) * 100
                    })
                except PermissionError:
                    continue
            
            # Test performance I/O basique
            storage_benchmark = self._benchmark_storage_performance()
            storage_info["benchmark"] = storage_benchmark
            
            self.logger.log_system_analysis("STORAGE_DISCOVERY", storage_info)
            return storage_info
            
        except Exception as e:
            self.logger.log_error_with_context(e, {"phase": "storage_discovery"})
            return {"disks": [], "benchmark": {"error": "Storage discovery failed"}}
    
    def _benchmark_storage_performance(self) -> Dict[str, float]:
        """Benchmark performance stockage"""
        try:
            # Test écriture/lecture fichier temporaire
            test_file = Path("temp_benchmark_file.tmp")
            test_data = b"0" * (1024 * 1024)  # 1MB
            
            # Test écriture
            start_time = time.time()
            with open(test_file, "wb") as f:
                f.write(test_data)
                f.flush()
                os.fsync(f.fileno())
            write_time = time.time() - start_time
            
            # Test lecture
            start_time = time.time()
            with open(test_file, "rb") as f:
                data = f.read()
            read_time = time.time() - start_time
            
            # Nettoyage
            test_file.unlink(missing_ok=True)
            
            return {
                "write_speed_mbps": 1 / write_time if write_time > 0 else 0,
                "read_speed_mbps": 1 / read_time if read_time > 0 else 0,
                "write_time_ms": write_time * 1000,
                "read_time_ms": read_time * 1000
            }
            
        except Exception as e:
            self.logger.log_error_with_context(e, {"phase": "storage_benchmark"})
            return {"error": "Storage benchmark failed"}
    
    def _discover_network_capabilities(self) -> Dict[str, Any]:
        """Découvre les capacités réseau"""
        try:
            network_info = {"interfaces": []}
            
            # Informations interfaces réseau
            for interface, addrs in psutil.net_if_addrs().items():
                interface_info = {"name": interface, "addresses": []}
                
                for addr in addrs:
                    interface_info["addresses"].append({
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast
                    })
                
                network_info["interfaces"].append(interface_info)
            
            # Statistiques réseau
            net_stats = psutil.net_io_counters()
            if net_stats:
                network_info["stats"] = {
                    "bytes_sent": net_stats.bytes_sent,
                    "bytes_recv": net_stats.bytes_recv,
                    "packets_sent": net_stats.packets_sent,
                    "packets_recv": net_stats.packets_recv
                }
            
            self.logger.log_system_analysis("NETWORK_DISCOVERY", network_info)
            return network_info
            
        except Exception as e:
            self.logger.log_error_with_context(e, {"phase": "network_discovery"})
            return {"interfaces": [], "error": "Network discovery failed"}
    
    def _analyze_user_context(self) -> Dict[str, Any]:
        """Analyse le contexte utilisateur de manière intelligente"""
        try:
            context = {
                "timestamp": datetime.now().isoformat(),
                "system_load": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
                "active_processes": len(psutil.pids()),
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
            }
            
            # Analyse des processus actifs pour détecter le contexte
            context["process_analysis"] = self._analyze_running_processes()
            
            # Détection du mode d'utilisation probable
            context["usage_mode"] = self._infer_usage_mode(context["process_analysis"])
            
            self.logger.log_system_analysis("USER_CONTEXT_ANALYSIS", context)
            return context
            
        except Exception as e:
            self.logger.log_error_with_context(e, {"phase": "user_context_analysis"})
            return {"timestamp": datetime.now().isoformat(), "error": "Context analysis failed"}
    
    def _analyze_running_processes(self) -> Dict[str, Any]:
        """Analyse les processus en cours pour comprendre le contexte"""
        try:
            processes = []
            gaming_indicators = 0
            work_indicators = 0
            development_indicators = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] > 5 or proc_info['memory_percent'] > 5:  # Processus actifs
                        processes.append(proc_info)
                        
                        # Détection heuristique du type d'activité
                        name_lower = proc_info['name'].lower()
                        if any(game_word in name_lower for game_word in ['game', 'steam', 'epic', 'valorant', 'league', 'discord']):
                            gaming_indicators += 1
                        elif any(work_word in name_lower for work_word in ['office', 'word', 'excel', 'teams', 'zoom', 'slack']):
                            work_indicators += 1
                        elif any(dev_word in name_lower for dev_word in ['code', 'visual', 'pycharm', 'git', 'docker', 'python']):
                            development_indicators += 1
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                "active_processes": processes[:10],  # Top 10 processus actifs
                "gaming_indicators": gaming_indicators,
                "work_indicators": work_indicators,
                "development_indicators": development_indicators,
                "total_analyzed": len(processes)
            }
            
        except Exception as e:
            self.logger.log_error_with_context(e, {"phase": "process_analysis"})
            return {"error": "Process analysis failed"}
    
    def _infer_usage_mode(self, process_analysis: Dict) -> str:
        """Infère le mode d'utilisation probable"""
        try:
            gaming = process_analysis.get("gaming_indicators", 0)
            work = process_analysis.get("work_indicators", 0)
            dev = process_analysis.get("development_indicators", 0)
            
            if gaming > work and gaming > dev:
                return "gaming"
            elif work > gaming and work > dev:
                return "work"
            elif dev > gaming and dev > work:
                return "development"
            else:
                return "general"
                
        except Exception:
            return "unknown"
    
    def _calculate_performance_score(self, profiles: Dict) -> float:
        """Calcule un score de performance global"""
        try:
            scores = []
            
            # Score CPU
            if "hardware" in profiles and "cpu" in profiles["hardware"]:
                cpu_score = profiles["hardware"]["cpu"].get("performance_score", 0.5)
                scores.append(cpu_score * 0.3)  # 30% du score total
            
            # Score mémoire
            if "memory" in profiles and "virtual" in profiles["memory"]:
                memory_available = profiles["memory"]["virtual"].get("available_gb", 4)
                memory_score = min(1.0, memory_available / 8)  # Normalisé sur 8GB
                scores.append(memory_score * 0.3)  # 30% du score total
            
            # Score GPU
            if "gpu" in profiles and profiles["gpu"].get("available", False):
                gpu_score = 0.8  # Bonus pour GPU disponible
                scores.append(gpu_score * 0.2)  # 20% du score total
            else:
                scores.append(0.2 * 0.2)  # Score minimal sans GPU
            
            # Score stockage
            if "storage" in profiles and "benchmark" in profiles["storage"]:
                storage_benchmark = profiles["storage"]["benchmark"]
                if "write_speed_mbps" in storage_benchmark and "read_speed_mbps" in storage_benchmark:
                    write_speed = storage_benchmark["write_speed_mbps"]
                    read_speed = storage_benchmark["read_speed_mbps"]
                    storage_score = min(1.0, (write_speed + read_speed) / 200)  # Normalisé sur 100MB/s chaque
                    scores.append(storage_score * 0.2)  # 20% du score total
                else:
                    scores.append(0.3 * 0.2)  # Score moyen sans benchmark
            else:
                scores.append(0.3 * 0.2)  # Score moyen par défaut
            
            # Score final
            final_score = sum(scores) if scores else 0.5
            return min(1.0, max(0.0, final_score))
            
        except Exception as e:
            return 0.5  # Score neutre en cas d'erreur
    
    def _generate_adaptation_recommendations(self, profiles: Dict) -> List[str]:
        """Génère des recommandations d'adaptation intelligentes"""
        recommendations = []
        
        try:
            # Recommandations Python
            python_profile = profiles.get("python", {})
            if python_profile.get("compatibility", {}).get("score", 1.0) < 0.8:
                recommendations.append("Consider updating Python or installing missing modules")
            
            # Recommandations hardware
            hardware_profile = profiles.get("hardware", {})
            cpu_score = hardware_profile.get("cpu", {}).get("performance_score", 0.5)
            if cpu_score < 0.3:
                recommendations.append("CPU performance is low - consider reducing processing intensity")
            elif cpu_score > 0.8:
                recommendations.append("Excellent CPU performance - can handle intensive processing")
            
            # Recommandations mémoire
            memory_profile = profiles.get("memory", {})
            memory_available = memory_profile.get("virtual", {}).get("available_gb", 4)
            if memory_available < 2:
                recommendations.append("Low memory available - enable memory optimization mode")
            elif memory_available > 8:
                recommendations.append("Abundant memory - can enable high-quality processing")
            
            # Recommandations GPU
            gpu_profile = profiles.get("gpu", {})
            if gpu_profile.get("available", False):
                recommendations.append("GPU detected - enable GPU acceleration for better performance")
            else:
                recommendations.append("No GPU detected - optimize for CPU-only processing")
            
            # Recommandations basées sur le score global
            performance_score = profiles.get("performance_score", 0.5)
            if performance_score < 0.3:
                recommendations.append("Overall low performance - enable power saving mode")
            elif performance_score > 0.8:
                recommendations.append("High performance system - enable maximum quality settings")
            
        except Exception as e:
            recommendations.append("Error generating recommendations - using default settings")
        
        return recommendations
    
    def _generate_memory_recommendations(self, memory_info: Dict) -> List[str]:
        """Génère des recommandations spécifiques à la mémoire"""
        recommendations = []
        
        try:
            virtual = memory_info.get("virtual", {})
            percentage = virtual.get("percentage", 50)
            available_gb = virtual.get("available_gb", 4)
            
            if percentage > 80:
                recommendations.append("High memory usage - close unnecessary applications")
            elif percentage < 30:
                recommendations.append("Low memory usage - can increase buffer sizes")
            
            if available_gb < 2:
                recommendations.append("Critical memory shortage - enable aggressive memory optimization")
            elif available_gb > 16:
                recommendations.append("Abundant memory - can enable memory-intensive features")
            
            # Recommandations swap
            swap = memory_info.get("swap", {})
            if swap.get("percentage", 0) > 50:
                recommendations.append("High swap usage - consider adding more RAM")
                
        except Exception:
            recommendations.append("Unable to analyze memory - using default settings")
        
        return recommendations
    
    def _get_fallback_capabilities(self) -> SystemCapabilities:
        """Retourne des capacités minimales en cas d'erreur"""
        return SystemCapabilities(
            python_profile={"version": {"major": 3, "minor": 8}, "compatibility": {"score": 0.5}},
            hardware_profile={"cpu": {"cores_logical": 4, "performance_score": 0.5}},
            memory_profile={"virtual": {"total_gb": 8, "available_gb": 4, "percentage": 50}},
            gpu_profile={"available": False, "type": "none"},
            thermal_profile={"monitoring_available": False},
            storage_profile={"disks": []},
            network_profile={"interfaces": []},
            user_context={"usage_mode": "unknown"},
            performance_score=0.5,
            adaptation_recommendations=["Using fallback configuration due to discovery errors"]
        )

# Fonction utilitaire pour créer le profiler
def create_smart_system_profiler() -> SmartSystemProfiler:
    """Crée et initialise le profiler système intelligent"""
    return SmartSystemProfiler()

if __name__ == "__main__":
    # Test du profiler
    profiler = SmartSystemProfiler()
    
    print("🔍 Test du Smart System Profiler")
    print("=" * 50)
    
    capabilities = profiler.discover_system_capabilities()
    
    print(f"\n📊 Résultats de découverte:")
    print(f"🐍 Python: {capabilities.python_profile['version']['version_string']}")
    print(f"💻 CPU Cores: {capabilities.hardware_profile['cpu']['cores_logical']}")
    print(f"💾 Memory: {capabilities.memory_profile['virtual']['total_gb']:.1f}GB")
    print(f"🎮 GPU: {'Available' if capabilities.gpu_profile['available'] else 'Not detected'}")
    print(f"📈 Performance Score: {capabilities.performance_score:.2f}")
    print(f"🎯 Usage Mode: {capabilities.user_context['usage_mode']}")
    
    print(f"\n💡 Recommandations:")
    for i, rec in enumerate(capabilities.adaptation_recommendations, 1):
        print(f"  {i}. {rec}")
