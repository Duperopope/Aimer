#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pro Dashboard - Dashboard professionnel pour AIMER PRO
Interface de monitoring système avec graphiques temps réel et métriques avancées
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import math
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from collections import deque
import json

# Imports des composants core
try:
    from core.hardware_profiler import HardwareProfiler, SystemProfile
    from core.progress_manager import ProgressManager, format_size, format_speed, format_time
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.hardware_profiler import HardwareProfiler, SystemProfile
    from core.progress_manager import ProgressManager, format_size, format_speed, format_time

class AnimatedProgressBar:
    """Barre de progression animée avec effets visuels"""
    
    def __init__(self, parent, width=300, height=20, color='#00ff88'):
        self.parent = parent
        self.width = width
        self.height = height
        self.color = color
        self.value = 0.0
        self.target_value = 0.0
        self.animation_speed = 0.05
        
        # Canvas pour la barre
        self.canvas = tk.Canvas(parent, width=width, height=height, 
                               bg='#2b2b2b', highlightthickness=0)
        self.canvas.pack(pady=2)
        
        # Éléments graphiques
        self.bg_rect = self.canvas.create_rectangle(
            1, 1, width-1, height-1,
            fill='#404040', outline='#606060', width=1
        )
        
        self.progress_rect = self.canvas.create_rectangle(
            1, 1, 1, height-1,
            fill=color, outline='', width=0
        )
        
        self.text = self.canvas.create_text(
            width//2, height//2,
            text="0%", fill='white', font=('Segoe UI', 8, 'bold')
        )
        
        # Animation
        self.animate_progress()
    
    def set_value(self, value: float, text: str = None):
        """Met à jour la valeur cible"""
        self.target_value = max(0.0, min(1.0, value))
        if text:
            self.canvas.itemconfig(self.text, text=text)
        else:
            self.canvas.itemconfig(self.text, text=f"{int(self.target_value * 100)}%")
    
    def animate_progress(self):
        """Animation fluide de la barre de progression"""
        # Interpolation vers la valeur cible
        diff = self.target_value - self.value
        if abs(diff) > 0.001:
            self.value += diff * self.animation_speed
            
            # Mettre à jour la barre
            bar_width = (self.width - 2) * self.value
            self.canvas.coords(self.progress_rect, 1, 1, 1 + bar_width, self.height - 1)
            
            # Couleur dynamique basée sur la valeur
            if self.value < 0.5:
                color = '#00ff88'  # Vert
            elif self.value < 0.8:
                color = '#ffd93d'  # Jaune
            else:
                color = '#ff6b6b'  # Rouge
            
            self.canvas.itemconfig(self.progress_rect, fill=color)
        
        # Programmer la prochaine animation
        self.parent.after(50, self.animate_progress)

class RealTimeGraph:
    """Graphique temps réel avec courbes animées"""
    
    def __init__(self, parent, width=400, height=150, max_points=100):
        self.parent = parent
        self.width = width
        self.height = height
        self.max_points = max_points
        
        # Données
        self.data_series = {}  # {nom: deque([valeurs])}
        self.colors = ['#00ff88', '#6bb6ff', '#ffd93d', '#ff6b6b', '#9d4edd']
        self.color_index = 0
        
        # Canvas
        self.canvas = tk.Canvas(parent, width=width, height=height,
                               bg='#1a1a1a', highlightthickness=0)
        self.canvas.pack(pady=5)
        
        # Grille et axes
        self.draw_grid()
        
        # Légende
        self.legend_frame = tk.Frame(parent, bg='#2b2b2b')
        self.legend_frame.pack(fill='x', pady=2)
        self.legend_labels = {}
    
    def add_series(self, name: str, color: str = None):
        """Ajoute une série de données"""
        if name not in self.data_series:
            self.data_series[name] = deque(maxlen=self.max_points)
            
            # Couleur
            if not color:
                color = self.colors[self.color_index % len(self.colors)]
                self.color_index += 1
            
            # Ajouter à la légende
            legend_label = tk.Label(
                self.legend_frame,
                text=f"● {name}",
                fg=color,
                bg='#2b2b2b',
                font=('Segoe UI', 8)
            )
            legend_label.pack(side='left', padx=5)
            self.legend_labels[name] = (legend_label, color)
    
    def add_point(self, series_name: str, value: float):
        """Ajoute un point à une série"""
        if series_name in self.data_series:
            self.data_series[series_name].append(value)
            self.redraw()
    
    def draw_grid(self):
        """Dessine la grille de fond"""
        # Lignes horizontales
        for i in range(5):
            y = (self.height - 20) * i / 4 + 10
            self.canvas.create_line(
                30, y, self.width - 10, y,
                fill='#333333', width=1
            )
            # Labels Y
            self.canvas.create_text(
                25, y, text=f"{100 - i * 25}%",
                fill='#666666', font=('Segoe UI', 7), anchor='e'
            )
        
        # Lignes verticales
        for i in range(6):
            x = 30 + (self.width - 40) * i / 5
            self.canvas.create_line(
                x, 10, x, self.height - 10,
                fill='#333333', width=1
            )
    
    def redraw(self):
        """Redessine toutes les courbes"""
        # Effacer les anciennes courbes
        self.canvas.delete("curve")
        
        # Dessiner chaque série
        for series_name, data in self.data_series.items():
            if len(data) < 2:
                continue
            
            color = self.legend_labels[series_name][1]
            points = []
            
            for i, value in enumerate(data):
                x = 30 + (self.width - 40) * i / (self.max_points - 1)
                y = self.height - 10 - (self.height - 20) * (value / 100.0)
                points.extend([x, y])
            
            if len(points) >= 4:
                self.canvas.create_line(
                    points, fill=color, width=2, smooth=True, tags="curve"
                )

class SystemMetricCard:
    """Carte de métrique système avec animation"""
    
    def __init__(self, parent, title: str, icon: str, color: str = '#00ff88'):
        self.parent = parent
        self.title = title
        self.icon = icon
        self.color = color
        
        # Frame principale
        self.frame = tk.Frame(parent, bg='#3a3a3a', relief='raised', bd=1)
        self.frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # Header
        header_frame = tk.Frame(self.frame, bg='#3a3a3a')
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        tk.Label(
            header_frame,
            text=f"{icon} {title}",
            font=('Segoe UI', 10, 'bold'),
            fg='white',
            bg='#3a3a3a'
        ).pack(side='left')
        
        # Valeur principale
        self.main_value = tk.Label(
            self.frame,
            text="0%",
            font=('Segoe UI', 18, 'bold'),
            fg=color,
            bg='#3a3a3a'
        )
        self.main_value.pack(pady=5)
        
        # Barre de progression
        self.progress_bar = AnimatedProgressBar(self.frame, width=120, height=8, color=color)
        
        # Détails
        self.details_frame = tk.Frame(self.frame, bg='#3a3a3a')
        self.details_frame.pack(fill='x', padx=10, pady=(5, 10))
        
        self.detail_labels = {}
    
    def update_value(self, value: float, text: str = None):
        """Met à jour la valeur principale"""
        if text is None:
            text = f"{value:.1f}%"
        
        self.main_value.config(text=text)
        self.progress_bar.set_value(value / 100.0)
    
    def add_detail(self, key: str, value: str):
        """Ajoute ou met à jour un détail"""
        if key not in self.detail_labels:
            label = tk.Label(
                self.details_frame,
                text=f"{key}: {value}",
                font=('Segoe UI', 8),
                fg='#cccccc',
                bg='#3a3a3a'
            )
            label.pack(anchor='w')
            self.detail_labels[key] = label
        else:
            self.detail_labels[key].config(text=f"{key}: {value}")

class DownloadProgressWidget:
    """Widget de progression des téléchargements"""
    
    def __init__(self, parent, progress_manager: ProgressManager):
        self.parent = parent
        self.progress_manager = progress_manager
        
        # Frame principal
        self.frame = tk.LabelFrame(parent, text="📥 Téléchargements", 
                                  bg='#2b2b2b', fg='white', font=('Segoe UI', 10, 'bold'))
        self.frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Statistiques globales
        stats_frame = tk.Frame(self.frame, bg='#2b2b2b')
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        self.global_stats_label = tk.Label(
            stats_frame,
            text="Aucun téléchargement actif",
            font=('Segoe UI', 9),
            fg='#cccccc',
            bg='#2b2b2b'
        )
        self.global_stats_label.pack()
        
        # Liste des téléchargements actifs
        self.downloads_frame = tk.Frame(self.frame, bg='#2b2b2b')
        self.downloads_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Canvas avec scrollbar pour la liste
        self.canvas = tk.Canvas(self.downloads_frame, bg='#2b2b2b', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.downloads_frame, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#2b2b2b')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Widgets des tâches
        self.task_widgets = {}
        
        # Mise à jour périodique
        self.update_downloads()
    
    def update_downloads(self):
        """Met à jour l'affichage des téléchargements"""
        try:
            # Statistiques globales
            stats = self.progress_manager.get_global_stats()
            active_count = stats.get('active_downloads', 0)
            total_speed = stats.get('current_total_speed_mbps', 0)
            
            if active_count > 0:
                stats_text = f"{active_count} téléchargement(s) actif(s) • {total_speed:.1f} MB/s"
            else:
                stats_text = "Aucun téléchargement actif"
            
            self.global_stats_label.config(text=stats_text)
            
            # Tâches actives
            active_tasks = self.progress_manager.get_active_tasks()
            
            # Supprimer les widgets des tâches terminées
            current_task_ids = {task.task_id for task in active_tasks}
            for task_id in list(self.task_widgets.keys()):
                if task_id not in current_task_ids:
                    self.task_widgets[task_id].destroy()
                    del self.task_widgets[task_id]
            
            # Créer/mettre à jour les widgets des tâches actives
            for task in active_tasks:
                if task.task_id not in self.task_widgets:
                    self._create_task_widget(task)
                else:
                    self._update_task_widget(task)
            
        except Exception as e:
            print(f"Erreur mise à jour téléchargements: {e}")
        
        # Programmer la prochaine mise à jour
        self.parent.after(1000, self.update_downloads)
    
    def _create_task_widget(self, task):
        """Crée un widget pour une tâche"""
        # Frame de la tâche
        task_frame = tk.Frame(self.scrollable_frame, bg='#404040', relief='raised', bd=1)
        task_frame.pack(fill='x', pady=2)
        
        # Nom de la tâche
        name_label = tk.Label(
            task_frame,
            text=task.name,
            font=('Segoe UI', 9, 'bold'),
            fg='white',
            bg='#404040'
        )
        name_label.pack(anchor='w', padx=10, pady=(5, 0))
        
        # Barre de progression
        progress_bar = AnimatedProgressBar(task_frame, width=250, height=12)
        
        # Informations détaillées
        info_label = tk.Label(
            task_frame,
            text="",
            font=('Segoe UI', 8),
            fg='#cccccc',
            bg='#404040'
        )
        info_label.pack(anchor='w', padx=10, pady=(0, 5))
        
        # Stocker les références
        self.task_widgets[task.task_id] = {
            'frame': task_frame,
            'name_label': name_label,
            'progress_bar': progress_bar,
            'info_label': info_label
        }
    
    def _update_task_widget(self, task):
        """Met à jour un widget de tâche"""
        if task.task_id not in self.task_widgets:
            return
        
        widget = self.task_widgets[task.task_id]
        
        # Mettre à jour la barre de progression
        progress = task.metrics.progress_percent / 100.0
        widget['progress_bar'].set_value(progress, f"{task.metrics.progress_percent:.1f}%")
        
        # Informations détaillées
        info_parts = []
        
        if task.metrics.total_size > 0:
            downloaded = format_size(task.metrics.downloaded_size)
            total = format_size(task.metrics.total_size)
            info_parts.append(f"{downloaded} / {total}")
        
        if task.metrics.speed_bps > 0:
            speed = format_speed(task.metrics.speed_bps)
            info_parts.append(speed)
        
        if task.metrics.eta_seconds:
            eta = format_time(task.metrics.eta_seconds)
            info_parts.append(f"ETA: {eta}")
        
        if task.status.value != 'running':
            info_parts.append(f"Statut: {task.status.value.upper()}")
        
        info_text = " • ".join(info_parts) if info_parts else "Initialisation..."
        widget['info_label'].config(text=info_text)

class ProDashboard:
    """Dashboard professionnel principal"""
    
    def __init__(self, parent):
        self.parent = parent
        self.hardware_profiler = HardwareProfiler()
        self.progress_manager = ProgressManager()
        
        # Variables
        self.system_profile = None
        self.monitoring_active = False
        
        # Interface
        self.create_dashboard()
        
        # Démarrer le monitoring
        self.start_monitoring()
    
    def create_dashboard(self):
        """Crée l'interface du dashboard"""
        # Frame principal
        self.main_frame = tk.Frame(self.parent, bg='#2b2b2b')
        self.main_frame.pack(fill='both', expand=True)
        
        # Header avec titre et statut
        self.create_header()
        
        # Métriques système
        self.create_system_metrics()
        
        # Graphiques temps réel
        self.create_realtime_graphs()
        
        # Téléchargements
        self.create_downloads_section()
        
        # Informations système détaillées
        self.create_system_info()
    
    def create_header(self):
        """Crée l'en-tête du dashboard"""
        header_frame = tk.Frame(self.main_frame, bg='#404040', height=60)
        header_frame.pack(fill='x', padx=5, pady=5)
        header_frame.pack_propagate(False)
        
        # Titre
        title_label = tk.Label(
            header_frame,
            text="🖥️ DASHBOARD SYSTÈME - AIMER PRO",
            font=('Segoe UI', 16, 'bold'),
            fg='white',
            bg='#404040'
        )
        title_label.pack(side='left', padx=20, pady=15)
        
        # Statut système
        self.system_status = tk.Label(
            header_frame,
            text="🔄 Initialisation...",
            font=('Segoe UI', 12),
            fg='#ffd93d',
            bg='#404040'
        )
        self.system_status.pack(side='right', padx=20, pady=15)
    
    def create_system_metrics(self):
        """Crée les cartes de métriques système"""
        metrics_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        metrics_frame.pack(fill='x', padx=5, pady=5)
        
        # Cartes de métriques
        self.cpu_card = SystemMetricCard(metrics_frame, "CPU", "💻", '#6bb6ff')
        self.gpu_card = SystemMetricCard(metrics_frame, "GPU", "🎮", '#00ff88')
        self.memory_card = SystemMetricCard(metrics_frame, "RAM", "💾", '#ffd93d')
        self.storage_card = SystemMetricCard(metrics_frame, "Stockage", "💿", '#ff6b6b')
    
    def create_realtime_graphs(self):
        """Crée les graphiques temps réel"""
        graphs_frame = tk.LabelFrame(
            self.main_frame,
            text="📊 Monitoring Temps Réel",
            bg='#2b2b2b',
            fg='white',
            font=('Segoe UI', 10, 'bold')
        )
        graphs_frame.pack(fill='x', padx=5, pady=5)
        
        # Graphique principal
        self.main_graph = RealTimeGraph(graphs_frame, width=600, height=200)
        self.main_graph.add_series("CPU", '#6bb6ff')
        self.main_graph.add_series("GPU", '#00ff88')
        self.main_graph.add_series("RAM", '#ffd93d')
    
    def create_downloads_section(self):
        """Crée la section des téléchargements"""
        downloads_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        downloads_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.downloads_widget = DownloadProgressWidget(downloads_frame, self.progress_manager)
    
    def create_system_info(self):
        """Crée la section d'informations système"""
        info_frame = tk.LabelFrame(
            self.main_frame,
            text="ℹ️ Informations Système",
            bg='#2b2b2b',
            fg='white',
            font=('Segoe UI', 10, 'bold')
        )
        info_frame.pack(fill='x', padx=5, pady=5)
        
        self.system_info_text = tk.Text(
            info_frame,
            height=6,
            bg='#3a3a3a',
            fg='white',
            font=('Consolas', 9),
            wrap='word',
            state='disabled'
        )
        self.system_info_text.pack(fill='x', padx=10, pady=10)
    
    def start_monitoring(self):
        """Démarre le monitoring système"""
        self.monitoring_active = True
        
        # Profil initial
        threading.Thread(target=self.load_system_profile, daemon=True).start()
        
        # Monitoring continu
        self.hardware_profiler.start_monitoring(self.on_monitoring_update, interval=1.0)
        
        # Mise à jour périodique de l'interface
        self.update_interface()
    
    def stop_monitoring(self):
        """Arrête le monitoring"""
        self.monitoring_active = False
        self.hardware_profiler.stop_monitoring()
    
    def load_system_profile(self):
        """Charge le profil système complet"""
        try:
            self.system_profile = self.hardware_profiler.get_system_profile()
            self.parent.after(0, self.update_system_info)
            self.parent.after(0, lambda: self.system_status.config(
                text="✅ Système Analysé", fg='#00ff88'
            ))
        except Exception as e:
            self.parent.after(0, lambda: self.system_status.config(
                text=f"❌ Erreur: {e}", fg='#ff6b6b'
            ))
    
    def on_monitoring_update(self, metrics: Dict[str, Any]):
        """Callback pour les mises à jour de monitoring"""
        if not self.monitoring_active:
            return
        
        # Programmer la mise à jour de l'interface dans le thread principal
        self.parent.after(0, lambda: self.update_metrics(metrics))
    
    def update_metrics(self, metrics: Dict[str, Any]):
        """Met à jour les métriques affichées"""
        try:
            # CPU
            cpu_usage = metrics.get('cpu_usage', 0)
            self.cpu_card.update_value(cpu_usage)
            
            # GPU
            gpu_usage = metrics.get('gpu_usage', 0)
            gpu_memory = metrics.get('gpu_memory', 0)
            gpu_temp = metrics.get('gpu_temperature', 0)
            
            self.gpu_card.update_value(gpu_usage)
            if gpu_memory > 0:
                self.gpu_card.add_detail("VRAM", f"{gpu_memory:.1f}%")
            if gpu_temp > 0:
                self.gpu_card.add_detail("Temp", f"{gpu_temp:.0f}°C")
            
            # RAM
            memory_usage = metrics.get('memory_usage', 0)
            self.memory_card.update_value(memory_usage)
            
            # Ajouter aux graphiques
            self.main_graph.add_point("CPU", cpu_usage)
            self.main_graph.add_point("GPU", gpu_usage)
            self.main_graph.add_point("RAM", memory_usage)
            
        except Exception as e:
            print(f"Erreur mise à jour métriques: {e}")
    
    def update_system_info(self):
        """Met à jour les informations système"""
        if not self.system_profile:
            return
        
        try:
            profile = self.system_profile
            
            info_text = f"""💻 CPU: {profile.cpu.name}
   Cores: {profile.cpu.cores_physical}P/{profile.cpu.cores_logical}L @ {profile.cpu.frequency_current:.0f}MHz
   Cache: L1={profile.cpu.cache_l1}KB, L2={profile.cpu.cache_l2}KB, L3={profile.cpu.cache_l3}KB
   Instructions: {', '.join(profile.cpu.instructions)}

🎮 GPU: {len(profile.gpus)} périphérique(s)"""
            
            for i, gpu in enumerate(profile.gpus):
                info_text += f"""
   {i+1}. {gpu.name}
      VRAM: {gpu.memory_total}MB • Driver: {gpu.driver_version}"""
                if gpu.cuda_cores:
                    info_text += f" • CUDA: {gpu.cuda_cores} cores"
            
            info_text += f"""

💾 Mémoire: {profile.memory.total/(1024**3):.1f}GB"""
            if profile.memory.type:
                info_text += f" {profile.memory.type}"
            if profile.memory.speed:
                info_text += f" @ {profile.memory.speed}MHz"
            
            info_text += f"""

💿 Stockage: {len(profile.storage)} périphérique(s)"""
            for storage in profile.storage:
                storage_type = "SSD" if storage.is_ssd else "HDD"
                info_text += f"""
   {storage.device}: {storage.total/(1024**3):.1f}GB ({storage_type})"""
            
            info_text += f"""

⭐ Score Performance: {profile.performance_score:.1%}
🎯 Configuration Recommandée: {profile.recommended_config['yolo_model']} @ {profile.recommended_config['input_size']}px"""
            
            # Mettre à jour le texte
            self.system_info_text.config(state='normal')
            self.system_info_text.delete(1.0, tk.END)
            self.system_info_text.insert(1.0, info_text)
            self.system_info_text.config(state='disabled')
            
        except Exception as e:
            print(f"Erreur mise à jour info système: {e}")
    
    def update_interface(self):
        """Mise à jour périodique de l'interface"""
        if not self.monitoring_active:
            return
        
        try:
            # Mettre à jour les détails des cartes si le profil est disponible
            if self.system_profile:
                # CPU
                if self.system_profile.cpu.temperature:
                    self.cpu_card.add_detail("Temp", f"{self.system_profile.cpu.temperature:.0f}°C")
                self.cpu_card.add_detail("Freq", f"{self.system_profile.cpu.frequency_current:.0f}MHz")
                
                # Stockage
                total_storage = sum(s.total for s in self.system_profile.storage)
                used_storage = sum(s.used for s in self.system_profile.storage)
                storage_percent = (used_storage / total_storage) * 100 if total_storage > 0 else 0
                self.storage_card.update_value(storage_percent)
                self.storage_card.add_detail("Libre", format_size(total_storage - used_storage))
        
        except Exception as e:
            print(f"Erreur mise à jour interface: {e}")
        
        # Programmer la prochaine mise à jour
        self.parent.after(2000, self.update_interface)
    
    def get_progress_manager(self) -> ProgressManager:
        """Retourne le gestionnaire de progression"""
        return self.progress_manager

def create_pro_dashboard(parent) -> ProDashboard:
    """Crée et retourne un dashboard professionnel"""
    return ProDashboard(parent)

if __name__ == "__main__":
    # Test du dashboard
    root = tk.Tk()
    root.title("AIMER PRO - Dashboard Test")
    root.geometry("1000x800")
    root.configure(bg='#2b2b2b')
    
    dashboard = create_pro_dashboard(root)
    
    # Simuler quelques téléchargements pour le test
    def create_test_downloads():
        time.sleep(2)  # Attendre que l'interface soit prête
        
        pm = dashboard.get_progress_manager()
        
        # Créer des tâches de test
        pm.create_download_task(
            "test1", "Dataset COCO", 
            "https://httpbin.org/bytes/5242880",  # 5MB
            "test_coco.zip", "Téléchargement du dataset COCO"
        )
        
        pm.create_download_task(
            "test2", "Modèle YOLOv8", 
            "https://httpbin.org/bytes/10485760",  # 10MB
            "yolov8.pt", "Téléchargement du modèle YOLOv8"
        )
        
        # Démarrer les téléchargements
        pm.start_download("test1")
        time.sleep(1)
        pm.start_download("test2")
    
    # Lancer les téléchargements de test en arrière-plan
    threading.Thread(target=create_test_downloads, daemon=True).start()
    
    root.mainloop()
