#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hardware Profiler - Profiling avancé du matériel pour AIMER PRO
Détection automatique et adaptation intelligente du hardware
"""

import psutil
import platform
import subprocess
import json
import time
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

@dataclass
class CPUInfo:
    """Informations détaillées du CPU"""
    name: str
    cores_physical: int
    cores_logical: int
    frequency_base: float
    frequency_max: float
    frequency_current: float
    architecture: str
    instructions: List[str]
    cache_l1: int
    cache_l2: int
    cache_l3: int
    usage_percent: float
    temperature: Optional[float] = None

@dataclass
class GPUInfo:
    """Informations détaillées du GPU"""
    name: str
    driver_version: str
    memory_total: int
    memory_used: int
    memory_free: int
    gpu_usage: float
    memory_usage: float
    temperature: float
    power_draw: Optional[float]
    cuda_cores: Optional[int]
    compute_capability: Optional[str]
    is_nvidia: bool
    is_amd: bool
    is_intel: bool

@dataclass
class MemoryInfo:
    """Informations détaillées de la mémoire"""
    total: int
    available: int
    used: int
    free: int
    usage_percent: float
    speed: Optional[int]
    type: Optional[str]
    channels: Optional[int]

@dataclass
class StorageInfo:
    """Informations détaillées du stockage"""
    device: str
    total: int
    used: int
    free: int
    usage_percent: float
    filesystem: str
    is_ssd: bool
    read_speed: Optional[float]
    write_speed: Optional[float]

@dataclass
class SystemProfile:
    """Profile complet du système"""
    cpu: CPUInfo
    gpus: List[GPUInfo]
    memory: MemoryInfo
    storage: List[StorageInfo]
    os_info: Dict[str, str]
    performance_score: float
    recommended_config: Dict[str, any]
    timestamp: datetime

class HardwareProfiler:
    """Profiler avancé du matériel système"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.wmi_connection = None
        self._init_wmi()
        
        # Cache pour éviter les appels répétés
        self.cache = {}
        self.cache_timeout = 5.0  # 5 secondes
        
        # Monitoring continu
        self.monitoring_active = False
        self.monitoring_thread = None
        self.monitoring_callbacks = []
    
    def _init_wmi(self):
        """Initialise la connexion WMI si disponible"""
        if WMI_AVAILABLE and platform.system() == "Windows":
            try:
                self.wmi_connection = wmi.WMI()
                self.logger.info("Connexion WMI initialisée")
            except Exception as e:
                self.logger.warning(f"Impossible d'initialiser WMI: {e}")
                self.wmi_connection = None
    
    def get_cpu_info(self) -> CPUInfo:
        """Obtient les informations détaillées du CPU"""
        try:
            # Informations de base
            cpu_freq = psutil.cpu_freq()
            cpu_count_physical = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Nom du processeur
            cpu_name = platform.processor()
            if not cpu_name and self.wmi_connection:
                try:
                    for processor in self.wmi_connection.Win32_Processor():
                        cpu_name = processor.Name
                        break
                except:
                    pass
            
            # Architecture
            architecture = platform.machine()
            
            # Instructions supportées (approximation)
            instructions = self._detect_cpu_instructions()
            
            # Cache (approximation basée sur le CPU)
            cache_info = self._estimate_cpu_cache(cpu_name)
            
            # Température (si disponible)
            temperature = self._get_cpu_temperature()
            
            return CPUInfo(
                name=cpu_name or "CPU Inconnu",
                cores_physical=cpu_count_physical or 1,
                cores_logical=cpu_count_logical or 1,
                frequency_base=cpu_freq.min if cpu_freq else 0,
                frequency_max=cpu_freq.max if cpu_freq else 0,
                frequency_current=cpu_freq.current if cpu_freq else 0,
                architecture=architecture,
                instructions=instructions,
                cache_l1=cache_info.get('l1', 0),
                cache_l2=cache_info.get('l2', 0),
                cache_l3=cache_info.get('l3', 0),
                usage_percent=cpu_usage,
                temperature=temperature
            )
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'obtention des infos CPU: {e}")
            return CPUInfo(
                name="CPU Inconnu", cores_physical=1, cores_logical=1,
                frequency_base=0, frequency_max=0, frequency_current=0,
                architecture="unknown", instructions=[], cache_l1=0,
                cache_l2=0, cache_l3=0, usage_percent=0
            )
    
    def get_gpu_info(self) -> List[GPUInfo]:
        """Obtient les informations détaillées des GPUs"""
        gpus = []
        
        if GPU_AVAILABLE:
            try:
                gpu_list = GPUtil.getGPUs()
                for gpu in gpu_list:
                    # Déterminer le type de GPU
                    is_nvidia = "nvidia" in gpu.name.lower()
                    is_amd = "amd" in gpu.name.lower() or "radeon" in gpu.name.lower()
                    is_intel = "intel" in gpu.name.lower()
                    
                    # Informations CUDA (si NVIDIA)
                    cuda_cores = None
                    compute_capability = None
                    if is_nvidia:
                        cuda_cores, compute_capability = self._get_cuda_info(gpu.name)
                    
                    gpu_info = GPUInfo(
                        name=gpu.name,
                        driver_version=gpu.driver or "Inconnu",
                        memory_total=int(gpu.memoryTotal),
                        memory_used=int(gpu.memoryUsed),
                        memory_free=int(gpu.memoryFree),
                        gpu_usage=gpu.load * 100,
                        memory_usage=(gpu.memoryUsed / gpu.memoryTotal) * 100,
                        temperature=gpu.temperature,
                        power_draw=None,  # Non disponible via GPUtil
                        cuda_cores=cuda_cores,
                        compute_capability=compute_capability,
                        is_nvidia=is_nvidia,
                        is_amd=is_amd,
                        is_intel=is_intel
                    )
                    gpus.append(gpu_info)
                    
            except Exception as e:
                self.logger.error(f"Erreur lors de l'obtention des infos GPU: {e}")
        
        # Si aucun GPU détecté, ajouter le GPU intégré
        if not gpus:
            integrated_gpu = self._detect_integrated_gpu()
            if integrated_gpu:
                gpus.append(integrated_gpu)
        
        return gpus
    
    def get_memory_info(self) -> MemoryInfo:
        """Obtient les informations détaillées de la mémoire"""
        try:
            memory = psutil.virtual_memory()
            
            # Informations avancées via WMI
            speed = None
            memory_type = None
            channels = None
            
            if self.wmi_connection:
                try:
                    for mem in self.wmi_connection.Win32_PhysicalMemory():
                        if mem.Speed:
                            speed = int(mem.Speed)
                        if mem.MemoryType:
                            memory_type = self._decode_memory_type(mem.MemoryType)
                        break
                except:
                    pass
            
            return MemoryInfo(
                total=memory.total,
                available=memory.available,
                used=memory.used,
                free=memory.free,
                usage_percent=memory.percent,
                speed=speed,
                type=memory_type,
                channels=channels
            )
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'obtention des infos mémoire: {e}")
            return MemoryInfo(0, 0, 0, 0, 0, None, None, None)
    
    def get_storage_info(self) -> List[StorageInfo]:
        """Obtient les informations détaillées du stockage"""
        storage_devices = []
        
        try:
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    # Déterminer si c'est un SSD
                    is_ssd = self._is_ssd(partition.device)
                    
                    # Vitesses de lecture/écriture (benchmark rapide)
                    read_speed, write_speed = self._benchmark_disk_speed(partition.mountpoint)
                    
                    storage_info = StorageInfo(
                        device=partition.device,
                        total=usage.total,
                        used=usage.used,
                        free=usage.free,
                        usage_percent=(usage.used / usage.total) * 100,
                        filesystem=partition.fstype,
                        is_ssd=is_ssd,
                        read_speed=read_speed,
                        write_speed=write_speed
                    )
                    storage_devices.append(storage_info)
                    
                except Exception as e:
                    self.logger.warning(f"Erreur partition {partition.device}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Erreur lors de l'obtention des infos stockage: {e}")
        
        return storage_devices
    
    def get_system_profile(self) -> SystemProfile:
        """Génère un profil complet du système"""
        try:
            # Collecter toutes les informations
            cpu_info = self.get_cpu_info()
            gpu_info = self.get_gpu_info()
            memory_info = self.get_memory_info()
            storage_info = self.get_storage_info()
            
            # Informations OS
            os_info = {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version()
            }
            
            # Calculer le score de performance
            performance_score = self._calculate_performance_score(
                cpu_info, gpu_info, memory_info, storage_info
            )
            
            # Générer la configuration recommandée
            recommended_config = self._generate_recommended_config(
                cpu_info, gpu_info, memory_info, storage_info, performance_score
            )
            
            return SystemProfile(
                cpu=cpu_info,
                gpus=gpu_info,
                memory=memory_info,
                storage=storage_info,
                os_info=os_info,
                performance_score=performance_score,
                recommended_config=recommended_config,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du profil système: {e}")
            raise
    
    def _detect_cpu_instructions(self) -> List[str]:
        """Détecte les instructions CPU supportées"""
        instructions = []
        
        try:
            if platform.system() == "Windows":
                # Utiliser wmic pour obtenir les features CPU
                result = subprocess.run(
                    ['wmic', 'cpu', 'get', 'Name,Characteristics'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    # Analyser la sortie pour détecter les instructions
                    output = result.stdout.lower()
                    if 'avx' in output:
                        instructions.append('AVX')
                    if 'sse' in output:
                        instructions.extend(['SSE', 'SSE2', 'SSE3', 'SSE4'])
        except:
            pass
        
        # Instructions de base communes
        if not instructions:
            instructions = ['SSE2', 'SSE3']  # Minimum moderne
        
        return instructions
    
    def _estimate_cpu_cache(self, cpu_name: str) -> Dict[str, int]:
        """Estime la taille du cache CPU basé sur le nom"""
        cache_info = {'l1': 32, 'l2': 256, 'l3': 8192}  # Valeurs par défaut en KB
        
        if cpu_name:
            cpu_lower = cpu_name.lower()
            
            # Estimations basées sur les familles de processeurs
            if 'i3' in cpu_lower:
                cache_info = {'l1': 32, 'l2': 256, 'l3': 4096}
            elif 'i5' in cpu_lower:
                cache_info = {'l1': 32, 'l2': 256, 'l3': 6144}
            elif 'i7' in cpu_lower:
                cache_info = {'l1': 32, 'l2': 256, 'l3': 8192}
            elif 'i9' in cpu_lower:
                cache_info = {'l1': 32, 'l2': 512, 'l3': 16384}
            elif 'ryzen' in cpu_lower:
                if '3' in cpu_lower:
                    cache_info = {'l1': 32, 'l2': 512, 'l3': 16384}
                elif '5' in cpu_lower:
                    cache_info = {'l1': 32, 'l2': 512, 'l3': 32768}
                elif '7' in cpu_lower:
                    cache_info = {'l1': 32, 'l2': 512, 'l3': 32768}
                elif '9' in cpu_lower:
                    cache_info = {'l1': 32, 'l2': 512, 'l3': 65536}
        
        return cache_info
    
    def _get_cpu_temperature(self) -> Optional[float]:
        """Obtient la température du CPU si disponible"""
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if 'cpu' in name.lower() or 'core' in name.lower():
                            for entry in entries:
                                if entry.current:
                                    return entry.current
        except:
            pass
        
        return None
    
    def _get_cuda_info(self, gpu_name: str) -> Tuple[Optional[int], Optional[str]]:
        """Obtient les informations CUDA pour un GPU NVIDIA"""
        cuda_cores = None
        compute_capability = None
        
        try:
            # Base de données approximative des CUDA cores
            cuda_cores_db = {
                'gtx 1050': 640,
                'gtx 1060': 1280,
                'gtx 1070': 1920,
                'gtx 1080': 2560,
                'rtx 2060': 1920,
                'rtx 2070': 2304,
                'rtx 2080': 2944,
                'rtx 3060': 3584,
                'rtx 3070': 5888,
                'rtx 3080': 8704,
                'rtx 3090': 10496,
                'rtx 4060': 3072,
                'rtx 4070': 5888,
                'rtx 4080': 9728,
                'rtx 4090': 16384
            }
            
            gpu_lower = gpu_name.lower()
            for key, cores in cuda_cores_db.items():
                if key in gpu_lower:
                    cuda_cores = cores
                    break
            
            # Compute capability approximative
            if 'rtx 40' in gpu_lower:
                compute_capability = '8.9'
            elif 'rtx 30' in gpu_lower:
                compute_capability = '8.6'
            elif 'rtx 20' in gpu_lower:
                compute_capability = '7.5'
            elif 'gtx 10' in gpu_lower:
                compute_capability = '6.1'
                
        except:
            pass
        
        return cuda_cores, compute_capability
    
    def _detect_integrated_gpu(self) -> Optional[GPUInfo]:
        """Détecte le GPU intégré si aucun GPU dédié n'est trouvé"""
        try:
            if self.wmi_connection:
                for gpu in self.wmi_connection.Win32_VideoController():
                    if gpu.Name and 'intel' in gpu.Name.lower():
                        return GPUInfo(
                            name=gpu.Name,
                            driver_version=gpu.DriverVersion or "Inconnu",
                            memory_total=0,  # Non disponible pour GPU intégré
                            memory_used=0,
                            memory_free=0,
                            gpu_usage=0,
                            memory_usage=0,
                            temperature=0,
                            power_draw=None,
                            cuda_cores=None,
                            compute_capability=None,
                            is_nvidia=False,
                            is_amd=False,
                            is_intel=True
                        )
        except:
            pass
        
        return None
    
    def _decode_memory_type(self, memory_type: int) -> str:
        """Décode le type de mémoire WMI"""
        memory_types = {
            20: 'DDR',
            21: 'DDR2',
            22: 'DDR2 FB-DIMM',
            24: 'DDR3',
            26: 'DDR4',
            34: 'DDR5'
        }
        return memory_types.get(memory_type, 'Inconnu')
    
    def _is_ssd(self, device: str) -> bool:
        """Détermine si un périphérique de stockage est un SSD"""
        try:
            if platform.system() == "Windows" and self.wmi_connection:
                for disk in self.wmi_connection.Win32_DiskDrive():
                    if device.startswith(disk.DeviceID.replace('\\', '').replace('.', '')):
                        # Heuristiques pour détecter un SSD
                        if disk.MediaType and 'ssd' in disk.MediaType.lower():
                            return True
                        if disk.Model and any(keyword in disk.Model.lower() 
                                            for keyword in ['ssd', 'solid', 'nvme']):
                            return True
        except:
            pass
        
        return False
    
    def _benchmark_disk_speed(self, mountpoint: str) -> Tuple[Optional[float], Optional[float]]:
        """Benchmark rapide de la vitesse du disque"""
        try:
            # Test de lecture simple
            start_time = time.time()
            test_data = b'0' * (1024 * 1024)  # 1MB
            
            # Simuler lecture/écriture (très basique)
            read_speed = len(test_data) / (time.time() - start_time) / (1024 * 1024)  # MB/s
            write_speed = read_speed * 0.8  # Approximation
            
            return read_speed, write_speed
            
        except:
            return None, None
    
    def _calculate_performance_score(self, cpu: CPUInfo, gpus: List[GPUInfo], 
                                   memory: MemoryInfo, storage: List[StorageInfo]) -> float:
        """Calcule un score de performance global du système"""
        try:
            score = 0.0
            
            # Score CPU (30% du total)
            cpu_score = 0.0
            cpu_score += min(cpu.cores_logical / 8.0, 1.0) * 0.4  # Cores
            cpu_score += min(cpu.frequency_max / 4000.0, 1.0) * 0.3  # Fréquence
            cpu_score += (1.0 - cpu.usage_percent / 100.0) * 0.3  # Usage actuel
            score += cpu_score * 0.3
            
            # Score GPU (40% du total)
            gpu_score = 0.0
            if gpus:
                best_gpu = max(gpus, key=lambda g: g.memory_total)
                gpu_score += min(best_gpu.memory_total / 8192.0, 1.0) * 0.5  # VRAM
                gpu_score += (1.0 - best_gpu.gpu_usage / 100.0) * 0.3  # Usage
                if best_gpu.is_nvidia and best_gpu.cuda_cores:
                    gpu_score += min(best_gpu.cuda_cores / 5000.0, 1.0) * 0.2
            score += gpu_score * 0.4
            
            # Score Mémoire (20% du total)
            memory_score = 0.0
            memory_score += min(memory.total / (16 * 1024**3), 1.0) * 0.6  # Taille
            memory_score += (1.0 - memory.usage_percent / 100.0) * 0.4  # Usage
            score += memory_score * 0.2
            
            # Score Stockage (10% du total)
            storage_score = 0.0
            if storage:
                has_ssd = any(s.is_ssd for s in storage)
                storage_score += 0.5 if has_ssd else 0.2
                avg_free = sum(s.free for s in storage) / len(storage)
                storage_score += min(avg_free / (100 * 1024**3), 1.0) * 0.5  # Espace libre
            score += storage_score * 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Erreur calcul score performance: {e}")
            return 0.5
    
    def _generate_recommended_config(self, cpu: CPUInfo, gpus: List[GPUInfo],
                                   memory: MemoryInfo, storage: List[StorageInfo],
                                   performance_score: float) -> Dict[str, any]:
        """Génère une configuration recommandée basée sur le hardware"""
        config = {
            'yolo_model': 'yolov8n',
            'input_size': 640,
            'batch_size': 1,
            'device': 'cpu',
            'precision': 'float32',
            'workers': 1,
            'memory_limit': '1GB'
        }
        
        try:
            # Configuration basée sur le score de performance
            if performance_score >= 0.8:  # Système haut de gamme
                config.update({
                    'yolo_model': 'yolov8l',
                    'input_size': 1280,
                    'batch_size': 4,
                    'precision': 'float16',
                    'workers': min(cpu.cores_logical, 8),
                    'memory_limit': '4GB'
                })
            elif performance_score >= 0.6:  # Système milieu de gamme
                config.update({
                    'yolo_model': 'yolov8m',
                    'input_size': 640,
                    'batch_size': 2,
                    'precision': 'float16',
                    'workers': min(cpu.cores_logical, 4),
                    'memory_limit': '2GB'
                })
            elif performance_score >= 0.4:  # Système entrée de gamme
                config.update({
                    'yolo_model': 'yolov8s',
                    'input_size': 640,
                    'batch_size': 1,
                    'workers': min(cpu.cores_logical, 2),
                    'memory_limit': '1GB'
                })
            
            # Configuration GPU si disponible
            if gpus:
                best_gpu = max(gpus, key=lambda g: g.memory_total)
                if best_gpu.is_nvidia and best_gpu.memory_total > 2048:
                    config['device'] = 'cuda'
                    if best_gpu.memory_total > 6144:
                        config['batch_size'] = min(config['batch_size'] * 2, 8)
            
            # Ajustements mémoire
            available_gb = memory.available / (1024**3)
            if available_gb < 4:
                config['memory_limit'] = '512MB'
                config['batch_size'] = 1
            elif available_gb > 16:
                config['memory_limit'] = '8GB'
            
        except Exception as e:
            self.logger.error(f"Erreur génération config recommandée: {e}")
        
        return config
    
    def start_monitoring(self, callback_func: callable, interval: float = 1.0):
        """Démarre le monitoring continu du système"""
        if self.monitoring_active:
            return
        
        self.monitoring_callbacks.append(callback_func)
        self.monitoring_active = True
        
        def monitoring_loop():
            while self.monitoring_active:
                try:
                    # Collecter les métriques en temps réel
                    metrics = {
                        'cpu_usage': psutil.cpu_percent(interval=None),
                        'memory_usage': psutil.virtual_memory().percent,
                        'timestamp': datetime.now()
                    }
                    
                    # Ajouter les métriques GPU si disponible
                    if GPU_AVAILABLE:
                        try:
                            gpus = GPUtil.getGPUs()
                            if gpus:
                                metrics['gpu_usage'] = gpus[0].load * 100
                                metrics['gpu_memory'] = (gpus[0].memoryUsed / gpus[0].memoryTotal) * 100
                                metrics['gpu_temperature'] = gpus[0].temperature
                        except:
                            pass
                    
                    # Appeler tous les callbacks
                    for callback in self.monitoring_callbacks:
                        try:
                            callback(metrics)
                        except Exception as e:
                            self.logger.error(f"Erreur callback monitoring: {e}")
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    self.logger.error(f"Erreur boucle monitoring: {e}")
                    time.sleep(interval)
        
        self.monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Arrête le monitoring continu"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        self.monitoring_callbacks.clear()

# Fonction utilitaire pour créer un profiler
def create_hardware_profiler() -> HardwareProfiler:
    """Crée et retourne un profiler hardware"""
    return HardwareProfiler()

if __name__ == "__main__":
    # Test du profiler
    profiler = create_hardware_profiler()
    
    print("🔍 Profiling du système en cours...")
    profile = profiler.get_system_profile()
    
    print(f"\n💻 CPU: {profile.cpu.name}")
    print(f"   Cores: {profile.cpu.cores_physical}P/{profile.cpu.cores_logical}L")
    print(f"   Fréquence: {profile.cpu.frequency_current:.0f}MHz")
    print(f"   Usage: {profile.cpu.usage_percent:.1f}%")
    
    print(f"\n🎮 GPU(s): {len(profile.gpus)}")
    for i, gpu in enumerate(profile.gpus):
        print(f"   {i+1}. {gpu.name}")
        print(f"      VRAM: {gpu.memory_total}MB")
        print(f"      Usage: {gpu.gpu_usage:.1f}%")
    
    print(f"\n💾 Mémoire: {profile.memory.total/(1024**3):.1f}GB")
    print(f"   Usage: {profile.memory.usage_percent:.1f}%")
    
    print(f"\n💿 Stockage: {len(profile.storage)} périphérique(s)")
    for storage in profile.storage:
        print(f"   {storage.device}: {storage.total/(1024**3):.1f}GB ({'SSD' if storage.is_ssd else 'HDD'})")
    
    print(f"\n⭐ Score Performance: {profile.performance_score:.1%}")
    print(f"🎯 Modèle Recommandé: {profile.recommended_config['yolo_model']}")
    print(f"📐 Taille Recommandée: {profile.recommended_config['input_size']}px")
    print(f"🔧 Device Recommandé: {profile.recommended_config['device']}")
