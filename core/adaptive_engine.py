#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adaptive Engine - Moteur d'adaptation contextuelle intelligent
S'adapte dynamiquement aux capacités système et au contexte utilisateur
"""

import time
import threading
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime

from core.smart_system_profiler import SmartSystemProfiler, SystemCapabilities, SmartLogger

@dataclass
class AdaptationConfig:
    """Configuration d'adaptation calculée dynamiquement"""
    # Configuration YOLO
    yolo_model_size: str  # 'nano', 'small', 'medium', 'large', 'xlarge'
    confidence_threshold: float
    max_detections_per_frame: int
    
    # Configuration FPS
    target_fps: int
    adaptive_fps_enabled: bool
    fps_range: tuple  # (min_fps, max_fps)
    
    # Configuration mémoire
    memory_optimization_level: str  # 'minimal', 'balanced', 'aggressive'
    cache_size_mb: int
    buffer_size_frames: int
    
    # Configuration GPU
    gpu_acceleration: bool
    gpu_memory_fraction: float
    
    # Configuration threading
    worker_threads: int
    processing_priority: str  # 'low', 'normal', 'high'
    
    # Configuration interface
    ui_update_interval_ms: int
    realtime_preview: bool
    log_level: str
    
    # Métadonnées
    adaptation_reason: str
    confidence_score: float
    created_at: str

class ContextualAdaptationEngine:
    """Moteur d'adaptation contextuelle intelligent"""
    
    def __init__(self, profiler: SmartSystemProfiler = None):
        self.profiler = profiler or SmartSystemProfiler()
        self.logger = SmartLogger()
        
        # État actuel
        self.current_capabilities: Optional[SystemCapabilities] = None
        self.current_config: Optional[AdaptationConfig] = None
        self.adaptation_history: List[Dict] = []
        
        # Monitoring continu
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.adaptation_callbacks: List[Callable] = []
        
        # Cache des configurations
        self.config_cache: Dict[str, AdaptationConfig] = {}
        
    def initialize_adaptive_system(self) -> AdaptationConfig:
        """Initialise le système adaptatif avec découverte complète"""
        self.logger.log_system_analysis("ADAPTIVE_INIT_START", {"action": "Starting adaptive system initialization"})
        
        start_time = time.time()
        
        try:
            # Découverte des capacités système
            self.current_capabilities = self.profiler.discover_system_capabilities()
            
            # Calcul de la configuration optimale
            optimal_config = self.calculate_optimal_configuration(self.current_capabilities)
            self.current_config = optimal_config
            
            # Sauvegarde de la configuration
            self._save_configuration(optimal_config)
            
            # Démarrage du monitoring continu
            self.start_continuous_monitoring()
            
            init_time = time.time() - start_time
            
            self.logger.log_adaptation_decision(
                "INITIAL_CONFIGURATION",
                {
                    "performance_score": self.current_capabilities.performance_score,
                    "usage_mode": self.current_capabilities.user_context.get("usage_mode", "unknown"),
                    "init_time_seconds": init_time
                },
                optimal_config.confidence_score
            )
            
            self.logger.log_system_analysis("ADAPTIVE_INIT_COMPLETE", {
                "configuration": asdict(optimal_config),
                "init_time": f"{init_time:.2f}s"
            })
            
            return optimal_config
            
        except Exception as e:
            self.logger.log_error_with_context(e, {"phase": "adaptive_initialization"})
            return self._get_fallback_configuration()
    
    def calculate_optimal_configuration(self, capabilities: SystemCapabilities) -> AdaptationConfig:
        """Calcule la configuration optimale selon les capacités système"""
        try:
            # Analyse des capacités pour adaptation
            performance_score = capabilities.performance_score
            usage_mode = capabilities.user_context.get("usage_mode", "general")
            
            # Configuration YOLO adaptative
            yolo_config = self._adapt_yolo_configuration(capabilities)
            
            # Configuration FPS adaptative
            fps_config = self._adapt_fps_configuration(capabilities, usage_mode)
            
            # Configuration mémoire adaptative
            memory_config = self._adapt_memory_configuration(capabilities)
            
            # Configuration GPU adaptative
            gpu_config = self._adapt_gpu_configuration(capabilities)
            
            # Configuration threading adaptative
            threading_config = self._adapt_threading_configuration(capabilities)
            
            # Configuration interface adaptative
            ui_config = self._adapt_ui_configuration(capabilities, usage_mode)
            
            # Calcul du score de confiance
            confidence_score = self._calculate_adaptation_confidence(capabilities, {
                "yolo": yolo_config,
                "fps": fps_config,
                "memory": memory_config,
                "gpu": gpu_config
            })
            
            # Génération de la raison d'adaptation
            adaptation_reason = self._generate_adaptation_reason(capabilities, usage_mode)
            
            # Configuration finale
            config = AdaptationConfig(
                # YOLO
                yolo_model_size=yolo_config["model_size"],
                confidence_threshold=yolo_config["confidence_threshold"],
                max_detections_per_frame=yolo_config["max_detections"],
                
                # FPS
                target_fps=fps_config["target_fps"],
                adaptive_fps_enabled=fps_config["adaptive_enabled"],
                fps_range=fps_config["fps_range"],
                
                # Mémoire
                memory_optimization_level=memory_config["optimization_level"],
                cache_size_mb=memory_config["cache_size_mb"],
                buffer_size_frames=memory_config["buffer_size"],
                
                # GPU
                gpu_acceleration=gpu_config["acceleration_enabled"],
                gpu_memory_fraction=gpu_config["memory_fraction"],
                
                # Threading
                worker_threads=threading_config["worker_threads"],
                processing_priority=threading_config["priority"],
                
                # Interface
                ui_update_interval_ms=ui_config["update_interval_ms"],
                realtime_preview=ui_config["realtime_preview"],
                log_level=ui_config["log_level"],
                
                # Métadonnées
                adaptation_reason=adaptation_reason,
                confidence_score=confidence_score,
                created_at=datetime.now().isoformat()
            )
            
            # Cache de la configuration
            config_hash = self._generate_config_hash(capabilities)
            self.config_cache[config_hash] = config
            
            return config
            
        except Exception as e:
            self.logger.log_error_with_context(e, {"phase": "configuration_calculation"})
            return self._get_fallback_configuration()
    
    def _adapt_yolo_configuration(self, capabilities: SystemCapabilities) -> Dict[str, Any]:
        """Adapte la configuration YOLO selon les capacités"""
        performance_score = capabilities.performance_score
        gpu_available = capabilities.gpu_profile.get("available", False)
        memory_gb = capabilities.memory_profile.get("virtual", {}).get("available_gb", 4)
        
        # Sélection du modèle selon performance
        if performance_score > 0.8 and gpu_available and memory_gb > 8:
            model_size = "large"
            confidence_threshold = 0.3
            max_detections = 50
        elif performance_score > 0.6 and memory_gb > 6:
            model_size = "medium"
            confidence_threshold = 0.4
            max_detections = 30
        elif performance_score > 0.4 and memory_gb > 4:
            model_size = "small"
            confidence_threshold = 0.5
            max_detections = 20
        else:
            model_size = "nano"
            confidence_threshold = 0.6
            max_detections = 10
        
        return {
            "model_size": model_size,
            "confidence_threshold": confidence_threshold,
            "max_detections": max_detections
        }
    
    def _adapt_fps_configuration(self, capabilities: SystemCapabilities, usage_mode: str) -> Dict[str, Any]:
        """Adapte la configuration FPS selon le contexte"""
        performance_score = capabilities.performance_score
        cpu_cores = capabilities.hardware_profile.get("cpu", {}).get("cores_logical", 4)
        
        # Adaptation selon le mode d'usage
        if usage_mode == "gaming":
            # Mode gaming : FPS élevé prioritaire
            if performance_score > 0.7:
                target_fps = 60
                fps_range = (30, 120)
            else:
                target_fps = 30
                fps_range = (15, 60)
        elif usage_mode == "work":
            # Mode travail : équilibre performance/qualité
            target_fps = 30
            fps_range = (15, 45)
        elif usage_mode == "development":
            # Mode développement : qualité prioritaire
            target_fps = 20
            fps_range = (10, 30)
        else:
            # Mode général : adaptatif
            if performance_score > 0.6:
                target_fps = 30
                fps_range = (20, 60)
            else:
                target_fps = 20
                fps_range = (10, 30)
        
        # Ajustement selon CPU
        if cpu_cores >= 8:
            target_fps = min(target_fps * 1.5, fps_range[1])
        elif cpu_cores <= 2:
            target_fps = max(target_fps * 0.7, fps_range[0])
        
        return {
            "target_fps": int(target_fps),
            "adaptive_enabled": True,
            "fps_range": (int(fps_range[0]), int(fps_range[1]))
        }
    
    def _adapt_memory_configuration(self, capabilities: SystemCapabilities) -> Dict[str, Any]:
        """Adapte la configuration mémoire selon les capacités"""
        memory_info = capabilities.memory_profile.get("virtual", {})
        available_gb = memory_info.get("available_gb", 4)
        usage_percent = memory_info.get("percentage", 50)
        
        # Niveau d'optimisation selon mémoire disponible
        if available_gb < 2 or usage_percent > 80:
            optimization_level = "aggressive"
            cache_size_mb = 50
            buffer_size = 5
        elif available_gb < 4 or usage_percent > 60:
            optimization_level = "balanced"
            cache_size_mb = 100
            buffer_size = 10
        else:
            optimization_level = "minimal"
            cache_size_mb = min(200, int(available_gb * 50))  # 50MB par GB disponible
            buffer_size = min(20, int(available_gb * 2))
        
        return {
            "optimization_level": optimization_level,
            "cache_size_mb": cache_size_mb,
            "buffer_size": buffer_size
        }
    
    def _adapt_gpu_configuration(self, capabilities: SystemCapabilities) -> Dict[str, Any]:
        """Adapte la configuration GPU selon les capacités"""
        gpu_profile = capabilities.gpu_profile
        gpu_available = gpu_profile.get("available", False)
        
        if gpu_available:
            gpu_memory_gb = gpu_profile.get("memory_total_gb", 0)
            
            # Fraction de mémoire GPU selon disponibilité
            if gpu_memory_gb > 8:
                memory_fraction = 0.8
            elif gpu_memory_gb > 4:
                memory_fraction = 0.7
            else:
                memory_fraction = 0.6
            
            return {
                "acceleration_enabled": True,
                "memory_fraction": memory_fraction
            }
        else:
            return {
                "acceleration_enabled": False,
                "memory_fraction": 0.0
            }
    
    def _adapt_threading_configuration(self, capabilities: SystemCapabilities) -> Dict[str, Any]:
        """Adapte la configuration threading selon les capacités"""
        cpu_cores = capabilities.hardware_profile.get("cpu", {}).get("cores_logical", 4)
        performance_score = capabilities.performance_score
        usage_mode = capabilities.user_context.get("usage_mode", "general")
        
        # Nombre de threads selon CPU
        if cpu_cores >= 16:
            worker_threads = min(8, cpu_cores // 2)
        elif cpu_cores >= 8:
            worker_threads = min(6, cpu_cores // 2)
        elif cpu_cores >= 4:
            worker_threads = min(4, cpu_cores)
        else:
            worker_threads = 2
        
        # Priorité selon mode d'usage
        if usage_mode == "gaming":
            priority = "high"
        elif usage_mode == "work":
            priority = "normal"
        else:
            priority = "low" if performance_score < 0.3 else "normal"
        
        return {
            "worker_threads": worker_threads,
            "priority": priority
        }
    
    def _adapt_ui_configuration(self, capabilities: SystemCapabilities, usage_mode: str) -> Dict[str, Any]:
        """Adapte la configuration interface selon le contexte"""
        performance_score = capabilities.performance_score
        
        # Intervalle de mise à jour selon performance
        if performance_score > 0.7:
            update_interval_ms = 50  # 20 FPS UI
            realtime_preview = True
            log_level = "INFO"
        elif performance_score > 0.4:
            update_interval_ms = 100  # 10 FPS UI
            realtime_preview = True
            log_level = "WARNING"
        else:
            update_interval_ms = 200  # 5 FPS UI
            realtime_preview = False
            log_level = "ERROR"
        
        # Ajustement selon mode d'usage
        if usage_mode == "gaming":
            # Interface minimale pour gaming
            update_interval_ms *= 2
            realtime_preview = False
        elif usage_mode == "development":
            # Interface détaillée pour développement
            log_level = "DEBUG"
        
        return {
            "update_interval_ms": update_interval_ms,
            "realtime_preview": realtime_preview,
            "log_level": log_level
        }
    
    def _calculate_adaptation_confidence(self, capabilities: SystemCapabilities, configs: Dict) -> float:
        """Calcule le score de confiance de l'adaptation"""
        try:
            confidence_factors = []
            
            # Confiance basée sur la qualité des données système
            if capabilities.python_profile.get("compatibility", {}).get("score", 0) > 0.8:
                confidence_factors.append(0.9)
            else:
                confidence_factors.append(0.6)
            
            # Confiance basée sur la performance système
            performance_score = capabilities.performance_score
            confidence_factors.append(performance_score)
            
            # Confiance basée sur la disponibilité des informations
            info_completeness = 0
            profiles = [capabilities.hardware_profile, capabilities.memory_profile, 
                       capabilities.gpu_profile, capabilities.user_context]
            
            for profile in profiles:
                if profile and not profile.get("error"):
                    info_completeness += 0.25
            
            confidence_factors.append(info_completeness)
            
            # Score final
            final_confidence = sum(confidence_factors) / len(confidence_factors)
            return min(1.0, max(0.0, final_confidence))
            
        except Exception:
            return 0.5  # Confiance neutre en cas d'erreur
    
    def _generate_adaptation_reason(self, capabilities: SystemCapabilities, usage_mode: str) -> str:
        """Génère une explication de l'adaptation"""
        reasons = []
        
        performance_score = capabilities.performance_score
        if performance_score > 0.8:
            reasons.append("High performance system detected")
        elif performance_score < 0.3:
            reasons.append("Low performance system - optimized for efficiency")
        
        if capabilities.gpu_profile.get("available", False):
            reasons.append("GPU acceleration enabled")
        else:
            reasons.append("CPU-only processing optimized")
        
        memory_gb = capabilities.memory_profile.get("virtual", {}).get("available_gb", 4)
        if memory_gb < 2:
            reasons.append("Low memory - aggressive optimization")
        elif memory_gb > 16:
            reasons.append("Abundant memory - high quality settings")
        
        if usage_mode != "general":
            reasons.append(f"Optimized for {usage_mode} usage")
        
        return " | ".join(reasons) if reasons else "Standard adaptive configuration"
    
    def start_continuous_monitoring(self):
        """Démarre le monitoring continu pour adaptation dynamique"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="AdaptiveMonitoring"
        )
        self.monitoring_thread.start()
        
        self.logger.log_system_analysis("MONITORING_START", {"action": "Started continuous monitoring"})
    
    def stop_continuous_monitoring(self):
        """Arrête le monitoring continu"""
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=2.0)
        
        self.logger.log_system_analysis("MONITORING_STOP", {"action": "Stopped continuous monitoring"})
    
    def _monitoring_loop(self):
        """Boucle de monitoring continu"""
        last_adaptation_time = time.time()
        adaptation_interval = 30.0  # Réévaluation toutes les 30 secondes
        
        while self.monitoring_active:
            try:
                current_time = time.time()
                
                # Vérifier si une réévaluation est nécessaire
                if current_time - last_adaptation_time >= adaptation_interval:
                    self._check_adaptation_needed()
                    last_adaptation_time = current_time
                
                # Attente adaptative
                time.sleep(5.0)  # Vérification toutes les 5 secondes
                
            except Exception as e:
                self.logger.log_error_with_context(e, {"phase": "monitoring_loop"})
                time.sleep(10.0)  # Attente plus longue en cas d'erreur
    
    def _check_adaptation_needed(self):
        """Vérifie si une adaptation est nécessaire"""
        try:
            # Redécouverte rapide des capacités critiques
            current_memory = self.profiler._discover_memory_capabilities()
            current_context = self.profiler._analyze_user_context()
            
            # Comparaison avec l'état précédent
            adaptation_needed = False
            adaptation_reasons = []
            
            if self.current_capabilities:
                # Vérification mémoire
                old_memory_percent = self.current_capabilities.memory_profile.get("virtual", {}).get("percentage", 50)
                new_memory_percent = current_memory.get("virtual", {}).get("percentage", 50)
                
                if abs(new_memory_percent - old_memory_percent) > 20:
                    adaptation_needed = True
                    adaptation_reasons.append(f"Memory usage changed: {old_memory_percent}% → {new_memory_percent}%")
                
                # Vérification contexte utilisateur
                old_usage_mode = self.current_capabilities.user_context.get("usage_mode", "general")
                new_usage_mode = current_context.get("usage_mode", "general")
                
                if old_usage_mode != new_usage_mode:
                    adaptation_needed = True
                    adaptation_reasons.append(f"Usage mode changed: {old_usage_mode} → {new_usage_mode}")
            
            # Adaptation si nécessaire
            if adaptation_needed:
                self.logger.log_adaptation_decision(
                    "DYNAMIC_ADAPTATION_TRIGGERED",
                    {"reasons": adaptation_reasons},
                    0.8
                )
                
                # Recalcul de la configuration
                self._trigger_dynamic_adaptation(adaptation_reasons)
                
        except Exception as e:
            self.logger.log_error_with_context(e, {"phase": "adaptation_check"})
    
    def _trigger_dynamic_adaptation(self, reasons: List[str]):
        """Déclenche une adaptation dynamique"""
        try:
            # Redécouverte complète
            new_capabilities = self.profiler.discover_system_capabilities()
            
            # Nouveau calcul de configuration
            new_config = self.calculate_optimal_configuration(new_capabilities)
            
            # Mise à jour de l'état
            self.current_capabilities = new_capabilities
            old_config = self.current_config
            self.current_config = new_config
            
            # Historique d'adaptation
            adaptation_record = {
                "timestamp": datetime.now().isoformat(),
                "reasons": reasons,
                "old_config": asdict(old_config) if old_config else None,
                "new_config": asdict(new_config),
                "performance_change": new_capabilities.performance_score - (old_config.confidence_score if old_config else 0.5)
            }
            self.adaptation_history.append(adaptation_record)
            
            # Notification des callbacks
            for callback in self.adaptation_callbacks:
                try:
                    callback(new_config, adaptation_record)
                except Exception as e:
                    self.logger.log_error_with_context(e, {"phase": "adaptation_callback"})
            
            self.logger.log_adaptation_decision(
                "DYNAMIC_ADAPTATION_COMPLETE",
                {
                    "new_performance_score": new_capabilities.performance_score,
                    "config_changes": len([k for k in asdict(new_config) if asdict(new_config)[k] != asdict(old_config).get(k)]) if old_config else "all"
                },
                new_config.confidence_score
            )
            
        except Exception as e:
            self.logger.log_error_with_context(e, {"phase": "dynamic_adaptation"})
    
    def add_adaptation_callback(self, callback: Callable[[AdaptationConfig, Dict], None]):
        """Ajoute un callback pour les adaptations"""
        self.adaptation_callbacks.append(callback)
    
    def remove_adaptation_callback(self, callback: Callable):
        """Supprime un callback"""
        if callback in self.adaptation_callbacks:
            self.adaptation_callbacks.remove(callback)
    
    def get_current_configuration(self) -> Optional[AdaptationConfig]:
        """Retourne la configuration actuelle"""
        return self.current_config
    
    def get_adaptation_history(self) -> List[Dict]:
        """Retourne l'historique des adaptations"""
        return self.adaptation_history.copy()
    
    def _save_configuration(self, config: AdaptationConfig):
        """Sauvegarde la configuration"""
        try:
            config_file = Path("adaptive_config.json")
            with open(config_file, "w") as f:
                json.dump(asdict(config), f, indent=2)
        except Exception as e:
            self.logger.log_error_with_context(e, {"phase": "config_save"})
    
    def _generate_config_hash(self, capabilities: SystemCapabilities) -> str:
        """Génère un hash pour la configuration"""
        import hashlib
        
        key_data = {
            "performance_score": capabilities.performance_score,
            "usage_mode": capabilities.user_context.get("usage_mode", "general"),
            "memory_gb": capabilities.memory_profile.get("virtual", {}).get("total_gb", 8),
            "gpu_available": capabilities.gpu_profile.get("available", False),
            "cpu_cores": capabilities.hardware_profile.get("cpu", {}).get("cores_logical", 4)
        }
        
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()[:16]
    
    def _get_fallback_configuration(self) -> AdaptationConfig:
        """Configuration de fallback en cas d'erreur"""
        return AdaptationConfig(
            yolo_model_size="nano",
            confidence_threshold=0.5,
            max_detections_per_frame=10,
            target_fps=20,
            adaptive_fps_enabled=True,
            fps_range=(10, 30),
            memory_optimization_level="balanced",
            cache_size_mb=100,
            buffer_size_frames=10,
            gpu_acceleration=False,
            gpu_memory_fraction=0.0,
            worker_threads=2,
            processing_priority="normal",
            ui_update_interval_ms=100,
            realtime_preview=True,
            log_level="INFO",
            adaptation_reason="Fallback configuration due to discovery errors",
            confidence_score=0.3,
            created_at=datetime.now().isoformat()
        )

# Fonction utilitaire pour créer le moteur
def create_adaptive_engine(profiler: SmartSystemProfiler = None) -> ContextualAdaptationEngine:
    """Crée et initialise le moteur d'adaptation"""
    return ContextualAdaptationEngine(profiler)

if __name__ == "__main__":
    # Test du moteur d'adaptation
    print("🎯 Test du Moteur d'Adaptation Contextuelle")
    print("=" * 50)
    
    engine = ContextualAdaptationEngine()
    config = engine.initialize_adaptive_system()
    
    print(f"\n📊 Configuration Adaptative Générée:")
    print(f"🤖 YOLO Model: {config.yolo_model_size}")
    print(f"🎯 Confidence: {config.confidence_threshold}")
    print(f"📹 Target FPS: {config.target_fps}")
    print(f"💾 Memory Level: {config.memory_optimization_level}")
    print(f"🎮 GPU Accel: {config.gpu_acceleration}")
    print(f"🧵 Threads: {config.worker_threads}")
    print(f"📈 Confidence: {config.confidence_score:.2f}")
    print(f"💡 Reason: {config.adaptation_reason}")
