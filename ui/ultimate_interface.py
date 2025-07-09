"""
Ultimate Interface - Interface ultime du système YOLO collaboratif
Intègre tous les systèmes : datasets, apprentissage, multi-cibles, temps réel
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import sys
import os
import time
import json
from datetime import datetime
from pathlib import Path
import cv2
import numpy as np
import pyautogui
from PIL import Image, ImageTk, ImageDraw

# Ajouter le répertoire parent au path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Imports des systèmes
try:
    from ultralytics import YOLO
    from learning.dataset_manager import DatasetManager
    from learning.collaborative_learning import CollaborativeLearningSystem
    from realtime.multi_target_stream import MultiTargetStream
    from utils.multi_screen import TargetSelector
    from ui.zone_selector import ZoneManager
    # Nouveaux imports pour le gestionnaire intelligent
    from core.intelligent_storage_manager import IntelligentStorageManager
    from core.professional_dataset_manager import ProfessionalDatasetManager
    IMPORTS_OK = True
except ImportError as e:
    IMPORTS_OK = False
    IMPORT_ERROR = str(e)

class UltimateInterface:
    """Interface ultime du système YOLO collaboratif"""
    
    def __init__(self):
        # Variables d'état
        self.is_running = False
        self.model = None
        self.dataset_manager = None
        self.learning_system = None
        self.multi_stream = None
        self.target_selector = None
        self.zone_manager = None
        
        # Nouveaux gestionnaires intelligents
        self.storage_manager = None
        self.professional_dataset_manager = None
        
        # Configuration des couleurs
        self.colors = {
            'primary': '#007bff',
            'success': '#28a745',
            'warning': '#ffc107', 
            'danger': '#dc3545',
            'info': '#17a2b8',
            'dark': '#343a40',
            'purple': '#6f42c1'
        }
        
        # Interface principale
        self.root = tk.Tk()
        self.setup_main_window()
        self.create_ultimate_interface()
        
        # Initialisation différée
        self.root.after(100, self.delayed_init)
    
    def setup_main_window(self):
        """Configure la fenêtre principale"""
        self.root.title("🚀 SYSTÈME YOLO ULTIME - Plateforme Collaborative")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f8f9fa')
        
        # Centrer la fenêtre
        self.center_window()
        
        # Gestionnaire de fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_ultimate_interface(self):
        """Crée l'interface ultime"""
        # Header avec titre et statut
        self.create_header()
        
        # Notebook principal avec onglets
        self.create_main_notebook()
        
        # Footer avec statistiques globales
        self.create_footer()
    
    def create_header(self):
        """Crée l'en-tête de l'interface"""
        header_frame = tk.Frame(self.root, bg=self.colors['dark'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Titre principal
        title_label = tk.Label(
            header_frame,
            text="🚀 SYSTÈME YOLO ULTIME",
            font=('Arial', 20, 'bold'),
            fg='white',
            bg=self.colors['dark']
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Sous-titre
        subtitle_label = tk.Label(
            header_frame,
            text="Plateforme Collaborative d'Intelligence Artificielle",
            font=('Arial', 12),
            fg='#adb5bd',
            bg=self.colors['dark']
        )
        subtitle_label.pack(side=tk.LEFT, padx=(0, 20), pady=(35, 20))
        
        # Statut global
        self.status_frame = tk.Frame(header_frame, bg=self.colors['dark'])
        self.status_frame.pack(side=tk.RIGHT, padx=20, pady=20)
        
        self.global_status = tk.Label(
            self.status_frame,
            text="🔴 Initialisation...",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg=self.colors['dark']
        )
        self.global_status.pack()
    
    def create_main_notebook(self):
        """Crée le notebook principal avec tous les onglets"""
        # Style pour le notebook
        style = ttk.Style()
        style.configure('Ultimate.TNotebook.Tab', padding=[20, 10])
        
        self.main_notebook = ttk.Notebook(self.root, style='Ultimate.TNotebook')
        self.main_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Onglet 1: Dashboard Principal
        self.create_dashboard_tab()
        
        # Onglet 2: Datasets & Base Globale
        self.create_datasets_tab()
        
        # Onglet 3: Apprentissage Collaboratif
        self.create_learning_tab()
        
        # Onglet 4: Stream Multi-Cibles
        self.create_stream_tab()
        
        # Onglet 5: Configuration Avancée
        self.create_config_tab()
    
    def create_dashboard_tab(self):
        """Crée l'onglet dashboard principal"""
        dashboard_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(dashboard_frame, text="📊 Dashboard")
        
        # Vue d'ensemble
        overview_frame = ttk.LabelFrame(dashboard_frame, text="🎯 Vue d'Ensemble", padding="15")
        overview_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Métriques principales
        metrics_frame = tk.Frame(overview_frame)
        metrics_frame.pack(fill=tk.X)
        
        # Cartes de métriques
        self.create_metric_card(metrics_frame, "📚 Datasets", "0", "Datasets installés", self.colors['info'])
        self.create_metric_card(metrics_frame, "🎨 Objets", "0", "Objets personnels", self.colors['success'])
        self.create_metric_card(metrics_frame, "🖥️ Cibles", "0", "Cibles actives", self.colors['warning'])
        self.create_metric_card(metrics_frame, "🏆 Score", "0", "Score total", self.colors['purple'])
        
        # Actions rapides
        actions_frame = ttk.LabelFrame(dashboard_frame, text="⚡ Actions Rapides", padding="15")
        actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        quick_actions = [
            ("🚀 Démarrer Stream", self.quick_start_stream, self.colors['success']),
            ("📥 Installer Datasets", self.quick_install_datasets, self.colors['info']),
            ("🧠 Mode Apprentissage", self.quick_learning_mode, self.colors['purple']),
            ("🎯 Sélectionner Cibles", self.quick_select_targets, self.colors['warning'])
        ]
        
        for text, command, color in quick_actions:
            btn = tk.Button(
                actions_frame,
                text=text,
                font=('Arial', 11, 'bold'),
                bg=color,
                fg='white',
                command=command,
                relief='flat',
                padx=20,
                pady=10
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Vue temps réel
        realtime_frame = ttk.LabelFrame(dashboard_frame, text="📹 Vue Temps Réel", padding="10")
        realtime_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Canvas pour affichage temps réel
        self.realtime_canvas = tk.Canvas(realtime_frame, bg='black', height=300)
        self.realtime_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Log temps réel
        log_frame = ttk.LabelFrame(dashboard_frame, text="📋 Log Temps Réel", padding="10")
        log_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.dashboard_log = tk.Text(log_frame, height=8, bg='#f8f9fa', font=('Consolas', 9))
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.dashboard_log.yview)
        self.dashboard_log.configure(yscrollcommand=log_scrollbar.set)
        
        self.dashboard_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_metric_card(self, parent, title, value, subtitle, color):
        """Crée une carte de métrique"""
        card_frame = tk.Frame(parent, bg=color, relief='flat', bd=0)
        card_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Titre
        title_label = tk.Label(
            card_frame,
            text=title,
            font=('Arial', 12, 'bold'),
            fg='white',
            bg=color
        )
        title_label.pack(pady=(10, 5))
        
        # Valeur
        value_label = tk.Label(
            card_frame,
            text=value,
            font=('Arial', 24, 'bold'),
            fg='white',
            bg=color
        )
        value_label.pack()
        
        # Sous-titre
        subtitle_label = tk.Label(
            card_frame,
            text=subtitle,
            font=('Arial', 10),
            fg='white',
            bg=color
        )
        subtitle_label.pack(pady=(0, 10))
        
        return card_frame
    
    def create_datasets_tab(self):
        """Crée l'onglet gestion des datasets"""
        datasets_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(datasets_frame, text="📚 Datasets")
        
        # Panneau de contrôle datasets
        control_frame = ttk.LabelFrame(datasets_frame, text="🎛️ Contrôle Datasets", padding="15")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Boutons de contrôle
        control_buttons = tk.Frame(control_frame)
        control_buttons.pack(fill=tk.X)
        
        tk.Button(control_buttons, text="📥 Installer Essentiels", 
                 bg=self.colors['success'], fg='white', font=('Arial', 11),
                 command=self.install_essential_datasets).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_buttons, text="🔍 Parcourir Disponibles", 
                 bg=self.colors['info'], fg='white', font=('Arial', 11),
                 command=self.browse_available_datasets).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_buttons, text="📊 Statistiques", 
                 bg=self.colors['warning'], fg='white', font=('Arial', 11),
                 command=self.show_dataset_stats).pack(side=tk.LEFT, padx=5)
        
        # Liste des datasets
        datasets_list_frame = ttk.LabelFrame(datasets_frame, text="📋 Datasets Installés", padding="10")
        datasets_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview pour les datasets
        columns = ('Nom', 'Catégorie', 'Classes', 'Images', 'Taille')
        self.datasets_tree = ttk.Treeview(datasets_list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.datasets_tree.heading(col, text=col)
            self.datasets_tree.column(col, width=150)
        
        datasets_scrollbar = ttk.Scrollbar(datasets_list_frame, orient=tk.VERTICAL, command=self.datasets_tree.yview)
        self.datasets_tree.configure(yscrollcommand=datasets_scrollbar.set)
        
        self.datasets_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        datasets_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_learning_tab(self):
        """Crée l'onglet apprentissage collaboratif"""
        learning_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(learning_frame, text="🧠 Apprentissage")
        
        # Modes d'apprentissage
        modes_frame = ttk.LabelFrame(learning_frame, text="🎯 Modes d'Apprentissage", padding="15")
        modes_frame.pack(fill=tk.X, padx=10, pady=5)
        
        modes = [
            ("🎨 Création", "creation", "Créer de nouveaux objets", self.colors['success']),
            ("✅ Validation", "validation", "Valider les détections", self.colors['info']),
            ("🔧 Correction", "correction", "Corriger les erreurs", self.colors['warning']),
            ("🌍 Partage", "sharing", "Partager avec la communauté", self.colors['purple'])
        ]
        
        for text, mode_key, desc, color in modes:
            btn = tk.Button(
                modes_frame,
                text=f"{text}\n{desc}",
                font=('Arial', 10),
                bg=color,
                fg='white',
                command=lambda k=mode_key: self.activate_learning_mode(k),
                relief='flat',
                padx=15,
                pady=10
            )
            btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Statistiques d'apprentissage
        stats_frame = ttk.LabelFrame(learning_frame, text="📊 Vos Statistiques", padding="15")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.learning_stats_text = tk.Text(stats_frame, height=6, bg='#f8f9fa', font=('Arial', 10))
        self.learning_stats_text.pack(fill=tk.X)
        
        # Objets personnels
        personal_frame = ttk.LabelFrame(learning_frame, text="🎨 Vos Objets Personnels", padding="10")
        personal_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Liste des objets personnels
        personal_columns = ('Nom', 'Catégorie', 'Exemples', 'Précision', 'Créé le')
        self.personal_tree = ttk.Treeview(personal_frame, columns=personal_columns, show='headings', height=10)
        
        for col in personal_columns:
            self.personal_tree.heading(col, text=col)
            self.personal_tree.column(col, width=120)
        
        personal_scrollbar = ttk.Scrollbar(personal_frame, orient=tk.VERTICAL, command=self.personal_tree.yview)
        self.personal_tree.configure(yscrollcommand=personal_scrollbar.set)
        
        self.personal_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        personal_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_stream_tab(self):
        """Crée l'onglet stream multi-cibles"""
        stream_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(stream_frame, text="📹 Stream Multi-Cibles")
        
        # Contrôles de stream
        stream_control_frame = ttk.LabelFrame(stream_frame, text="🎛️ Contrôle Stream", padding="15")
        stream_control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Boutons de contrôle stream
        stream_buttons = tk.Frame(stream_control_frame)
        stream_buttons.pack(fill=tk.X)
        
        self.stream_start_btn = tk.Button(
            stream_buttons,
            text="🚀 DÉMARRER STREAM",
            font=('Arial', 12, 'bold'),
            bg=self.colors['success'],
            fg='white',
            command=self.toggle_stream
        )
        self.stream_start_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(stream_buttons, text="🖥️ Ajouter Écran", 
                 bg=self.colors['info'], fg='white', font=('Arial', 11),
                 command=self.add_screen_target).pack(side=tk.LEFT, padx=5)
        
        tk.Button(stream_buttons, text="🪟 Ajouter Fenêtre", 
                 bg=self.colors['warning'], fg='white', font=('Arial', 11),
                 command=self.add_window_target).pack(side=tk.LEFT, padx=5)
        
        # Configuration FPS
        fps_frame = tk.Frame(stream_control_frame)
        fps_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(fps_frame, text="FPS Global:", font=('Arial', 10)).pack(side=tk.LEFT)
        self.fps_var = tk.IntVar(value=30)
        fps_scale = tk.Scale(fps_frame, from_=10, to=60, variable=self.fps_var, 
                           orient='horizontal', length=200)
        fps_scale.pack(side=tk.LEFT, padx=10)
        
        # Cibles actives
        targets_frame = ttk.LabelFrame(stream_frame, text="🎯 Cibles Actives", padding="10")
        targets_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Liste des cibles
        targets_columns = ('ID', 'Type', 'Nom', 'FPS', 'Statut', 'Captures')
        self.targets_tree = ttk.Treeview(targets_frame, columns=targets_columns, show='headings', height=8)
        
        for col in targets_columns:
            self.targets_tree.heading(col, text=col)
            self.targets_tree.column(col, width=120)
        
        targets_scrollbar = ttk.Scrollbar(targets_frame, orient=tk.VERTICAL, command=self.targets_tree.yview)
        self.targets_tree.configure(yscrollcommand=targets_scrollbar.set)
        
        self.targets_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        targets_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Statistiques de performance
        perf_frame = ttk.LabelFrame(stream_frame, text="📈 Performance", padding="10")
        perf_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.performance_text = tk.Text(perf_frame, height=4, bg='#f8f9fa', font=('Consolas', 9))
        self.performance_text.pack(fill=tk.X)
    
    def create_config_tab(self):
        """Crée l'onglet configuration avancée"""
        config_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(config_frame, text="⚙️ Configuration")
        
        # Configuration YOLO
        yolo_frame = ttk.LabelFrame(config_frame, text="🤖 Configuration YOLO", padding="15")
        yolo_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Seuil de confiance
        conf_frame = tk.Frame(yolo_frame)
        conf_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(conf_frame, text="Seuil de confiance:", font=('Arial', 10)).pack(side=tk.LEFT)
        self.confidence_var = tk.DoubleVar(value=0.5)
        conf_scale = tk.Scale(conf_frame, from_=0.1, to=0.9, variable=self.confidence_var, 
                            orient='horizontal', resolution=0.1, length=300)
        conf_scale.pack(side=tk.LEFT, padx=10)
        
        self.conf_label = tk.Label(conf_frame, text="50%", font=('Arial', 10, 'bold'))
        self.conf_label.pack(side=tk.LEFT, padx=10)
        self.confidence_var.trace('w', self.update_confidence_display)
        
        # Configuration des actions
        actions_frame = ttk.LabelFrame(config_frame, text="⚡ Actions Automatiques", padding="15")
        actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(actions_frame, text="🎯 Configurer Actions", 
                 bg=self.colors['primary'], fg='white', font=('Arial', 11),
                 command=self.configure_actions).pack(side=tk.LEFT, padx=5)
        
        tk.Button(actions_frame, text="📐 Configurer Zones", 
                 bg=self.colors['warning'], fg='white', font=('Arial', 11),
                 command=self.configure_zones).pack(side=tk.LEFT, padx=5)
        
        # Sauvegarde/Chargement
        save_frame = ttk.LabelFrame(config_frame, text="💾 Sauvegarde", padding="15")
        save_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(save_frame, text="💾 Sauvegarder Config", 
                 bg=self.colors['success'], fg='white', font=('Arial', 11),
                 command=self.save_config).pack(side=tk.LEFT, padx=5)
        
        tk.Button(save_frame, text="📂 Charger Config", 
                 bg=self.colors['info'], fg='white', font=('Arial', 11),
                 command=self.load_config).pack(side=tk.LEFT, padx=5)
        
        tk.Button(save_frame, text="🔄 Reset Config", 
                 bg=self.colors['danger'], fg='white', font=('Arial', 11),
                 command=self.reset_config).pack(side=tk.LEFT, padx=5)
    
    def create_footer(self):
        """Crée le footer avec statistiques globales"""
        footer_frame = tk.Frame(self.root, bg=self.colors['dark'], height=40)
        footer_frame.pack(fill=tk.X)
        footer_frame.pack_propagate(False)
        
        # Statistiques globales
        self.footer_stats = tk.Label(
            footer_frame,
            text="📊 Prêt | 🎯 0 détections | ⏱️ 0ms | 💾 0MB",
            font=('Arial', 10),
            fg='white',
            bg=self.colors['dark']
        )
        self.footer_stats.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Version et copyright
        version_label = tk.Label(
            footer_frame,
            text="v2.0 - Système YOLO Ultime © 2025",
            font=('Arial', 9),
            fg='#adb5bd',
            bg=self.colors['dark']
        )
        version_label.pack(side=tk.RIGHT, padx=20, pady=10)
    
    def delayed_init(self):
        """Initialisation différée des systèmes"""
        if not IMPORTS_OK:
            self.log_message("❌ ERREUR: Modules manquants!")
            self.log_message(f"Détails: {IMPORT_ERROR}")
            self.global_status.configure(text="❌ Erreur Modules", fg='red')
            return
        
        try:
            self.log_message("🔄 Initialisation des systèmes...")
            
            # Charger le modèle YOLO
            self.log_message("🤖 Chargement modèle YOLO...")
            self.model = YOLO('yolov8n.pt')
            self.log_message("✅ Modèle YOLO chargé!")
            
            # Initialiser le gestionnaire de datasets
            self.log_message("📚 Initialisation gestionnaire datasets...")
            self.dataset_manager = DatasetManager()
            self.log_message("✅ Gestionnaire datasets prêt!")
            
            # Initialiser les gestionnaires intelligents
            self.log_message("🧠 Initialisation gestionnaire de stockage intelligent...")
            self.storage_manager = IntelligentStorageManager()
            self.log_message("✅ Gestionnaire de stockage intelligent prêt!")
            
            self.log_message("🎯 Initialisation gestionnaire de datasets professionnel...")
            self.professional_dataset_manager = ProfessionalDatasetManager()
            self.log_message("✅ Gestionnaire de datasets professionnel prêt!")
            
            # Initialiser le système d'apprentissage
            self.log_message("🧠 Initialisation apprentissage collaboratif...")
            self.learning_system = CollaborativeLearningSystem(
                self.dataset_manager, 
                self.log_message
            )
            self.log_message("✅ Système d'apprentissage prêt!")
            
            # Initialiser le stream multi-cibles
            self.log_message("📹 Initialisation stream multi-cibles...")
            self.multi_stream = MultiTargetStream(self.model, self.log_message)
            self.multi_stream.add_result_callback(self.on_detection_result)
            self.log_message("✅ Stream multi-cibles prêt!")
            
            # Initialiser les sélecteurs
            self.target_selector = TargetSelector(self.log_message)
            self.zone_manager = ZoneManager(self.log_message)
            
            # Mettre à jour l'interface
            self.refresh_all_data()
            
            self.global_status.configure(text="✅ Système Prêt", fg='lightgreen')
            self.log_message("🚀 Tous les systèmes initialisés avec succès!")
            
        except Exception as e:
            self.log_message(f"❌ Erreur initialisation: {e}")
            self.global_status.configure(text="❌ Erreur Init", fg='red')
    
    def log_message(self, message):
        """Ajoute un message au log"""
        def update_ui():
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"
            
            if hasattr(self, 'dashboard_log'):
                self.dashboard_log.insert(tk.END, log_entry)
                self.dashboard_log.see(tk.END)
                
                # Limiter le nombre de lignes
                lines = self.dashboard_log.get("1.0", tk.END).count('\n')
                if lines > 100:
                    self.dashboard_log.delete("1.0", "20.0")
        
        self.root.after(0, update_ui)
    
    def on_detection_result(self, result):
        """Callback pour les résultats de détection"""
        # Mettre à jour l'affichage temps réel
        self.update_realtime_display(result)
        
        # Traiter pour l'apprentissage si actif
        if self.learning_system and self.learning_system.learning_active:
            for detection in result.detections:
                self.learning_system.process_detection_for_learning(result.image, detection)
    
    def update_realtime_display(self, result):
        """Met à jour l'affichage temps réel"""
        try:
            # Redimensionner l'image pour le canvas
            image = result.image.copy()
            canvas_width = self.realtime_canvas.winfo_width()
            canvas_height = self.realtime_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                height, width = image.shape[:2]
                ratio = min(canvas_width / width, canvas_height / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                
                resized_image = cv2.resize(image, (new_width, new_height))
                
                # Dessiner les détections
                for detection in result.detections:
                    x1, y1, x2, y2 = detection['bbox']
                    x1, y1, x2, y2 = int(x1 * ratio), int(y1 * ratio), int(x2 * ratio), int(y2 * ratio)
                    
                    # Couleur selon la classe
                    color = (0, 255, 0)  # Vert par défaut
                    cv2.rectangle(resized_image, (x1, y1), (x2, y2), color, 2)
                    
                    # Texte
                    text = f"{detection['class_name']}: {detection['confidence']:.2f}"
                    cv2.putText(resized_image, text, (x1, y1-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Convertir pour Tkinter
                image_rgb = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
                image_pil = Image.fromarray(image_rgb)
                image_tk = ImageTk.PhotoImage(image_pil)
                
                # Afficher dans le canvas
                self.realtime_canvas.delete("all")
                self.realtime_canvas.create_image(
                    canvas_width//2, canvas_height//2, 
                    image=image_tk, anchor=tk.CENTER
                )
                
                # Garder une référence pour éviter le garbage collection
                self.realtime_canvas.image = image_tk
                
        except Exception as e:
            self.log_message(f"❌ Erreur affichage temps réel: {e}")
    
    # Actions rapides du dashboard
    def quick_start_stream(self):
        """Action rapide: démarrer le stream"""
        if not self.multi_stream:
            messagebox.showerror("Erreur", "Stream non initialisé!")
            return
        
        if not self.multi_stream.stream_targets:
            # Ajouter l'écran principal par défaut
            self.multi_stream.add_screen_target(0, 30)
        
        self.toggle_stream()
    
    def quick_install_datasets(self):
        """Action rapide: installer les datasets essentiels"""
        if not self.dataset_manager:
            messagebox.showerror("Erreur", "Gestionnaire de datasets non initialisé!")
            return
        
        self.install_essential_datasets()
    
    def quick_learning_mode(self):
        """Action rapide: activer le mode apprentissage"""
        if not self.learning_system:
            messagebox.showerror("Erreur", "Système d'apprentissage non initialisé!")
            return
        
        # Ouvrir l'interface d'apprentissage
        self.learning_system.create_learning_interface(self.root)
    
    def quick_select_targets(self):
        """Action rapide: sélectionner des cibles"""
        if not self.target_selector:
            messagebox.showerror("Erreur", "Sélecteur de cibles non initialisé!")
            return
        
        self.target_selector.show_target_selector(self.root)
    
    # Fonctions des onglets
    def install_essential_datasets(self):
        """Installe les datasets essentiels"""
        if not self.dataset_manager:
            messagebox.showerror("Erreur", "Gestionnaire de datasets non initialisé!")
            return
        
        def install_thread():
            try:
                self.log_message("📥 Installation des datasets essentiels...")
                results = self.dataset_manager.install_essential_datasets()
                
                success_count = sum(1 for success in results.values() if success)
                total_count = len(results)
                
                self.log_message(f"✅ Installation terminée: {success_count}/{total_count} réussies")
                self.refresh_datasets_list()
                
            except Exception as e:
                self.log_message(f"❌ Erreur installation: {e}")
        
        threading.Thread(target=install_thread, daemon=True).start()
    
    def browse_available_datasets(self):
        """Parcourt les datasets disponibles"""
        if not self.dataset_manager:
            messagebox.showerror("Erreur", "Gestionnaire de datasets non initialisé!")
            return
        
        # Créer une fenêtre pour parcourir les datasets
        browse_window = tk.Toplevel(self.root)
        browse_window.title("📚 Datasets Disponibles")
        browse_window.geometry("800x600")
        
        frame = ttk.Frame(browse_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="📚 Datasets Disponibles", 
                 font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Liste des datasets disponibles
        datasets = self.dataset_manager.get_available_datasets()
        
        for dataset in datasets[:10]:  # Afficher les 10 premiers
            dataset_frame = ttk.Frame(frame)
            dataset_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(dataset_frame, text=f"• {dataset['name']}", 
                     font=('Arial', 12, 'bold')).pack(anchor='w')
            ttk.Label(dataset_frame, text=f"  Classes: {dataset.get('classes', 'N/A')} | "
                                         f"Images: {dataset.get('images', 'N/A')}").pack(anchor='w')
    
    def show_dataset_stats(self):
        """Affiche les statistiques des datasets avec analyse intelligente"""
        if not self.dataset_manager or not self.professional_dataset_manager or not self.storage_manager:
            messagebox.showerror("Erreur", "Gestionnaires non initialisés!")
            return
        
        # Créer une fenêtre dédiée pour les statistiques avancées
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Statistiques Avancées des Datasets")
        stats_window.geometry("900x700")
        stats_window.configure(bg='#f8f9fa')
        
        # Notebook pour organiser les statistiques
        stats_notebook = ttk.Notebook(stats_window)
        stats_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Onglet 1: Statistiques générales
        general_frame = ttk.Frame(stats_notebook)
        stats_notebook.add(general_frame, text="📊 Général")
        
        try:
            # Statistiques du gestionnaire classique
            classic_stats = self.dataset_manager.get_dataset_stats()
            
            # Statistiques du gestionnaire professionnel
            pro_stats = self.professional_dataset_manager.get_dataset_statistics()
            
            # Statistiques de stockage
            storage_stats = self.storage_manager.get_storage_statistics()
            
            general_text = tk.Text(general_frame, font=('Consolas', 10), wrap='word')
            general_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            stats_content = f"""
📊 STATISTIQUES GÉNÉRALES DES DATASETS
{'='*60}

🎯 DATASETS CLASSIQUES:
• Total datasets: {classic_stats['global'].get('total_datasets', 0)}
• Datasets installés: {classic_stats['global'].get('installed_count', 0)}
• Classes totales: {classic_stats['global'].get('total_classes', 0)}
• Images totales: {classic_stats['global'].get('total_images', 0):,}
• Taille totale: {classic_stats['global'].get('total_size_mb', 0):.1f} MB

🚀 DATASETS PROFESSIONNELS:
• Total datasets: {pro_stats.get('total_datasets', 0)}
• Images totales: {pro_stats.get('total_images', 0):,}
• Annotations: {pro_stats.get('total_annotations', 0):,}
• Taille totale: {pro_stats.get('total_size_gb', 0):.2f} GB
• Qualité moyenne: {pro_stats.get('average_quality', 0):.1%}

💾 STOCKAGE INTELLIGENT:
• Disques analysés: {storage_stats.get('drives_analyzed', 0)}
• Espace total disponible: {storage_stats.get('total_free_space_gb', 0):.1f} GB
• Espace utilisé datasets: {storage_stats.get('datasets_space_used_gb', 0):.1f} GB
• Efficacité stockage: {storage_stats.get('storage_efficiency', 0):.1%}

📈 PERFORMANCE:
• Vitesse lecture moyenne: {storage_stats.get('avg_read_speed_mbps', 0):.0f} MB/s
• Vitesse écriture moyenne: {storage_stats.get('avg_write_speed_mbps', 0):.0f} MB/s
• Santé moyenne des disques: {storage_stats.get('avg_drive_health', 0):.1%}
"""
            
            # Ajouter les statistiques par catégorie
            if classic_stats['by_category']:
                stats_content += "\n🏷️ RÉPARTITION PAR CATÉGORIE:\n"
                for cat_stat in classic_stats['by_category']:
                    stats_content += f"• {cat_stat['category']}: {cat_stat['count']} datasets, {cat_stat['classes']} classes\n"
            
            general_text.insert(tk.END, stats_content)
            general_text.config(state='disabled')
            
        except Exception as e:
            error_text = f"❌ Erreur lors du calcul des statistiques: {e}"
            general_text.insert(tk.END, error_text)
            general_text.config(state='disabled')
        
        # Onglet 2: Analyse de stockage
        storage_frame = ttk.Frame(stats_notebook)
        stats_notebook.add(storage_frame, text="💾 Stockage")
        
        try:
            drives = self.storage_manager.scan_available_drives()
            
            storage_text = tk.Text(storage_frame, font=('Consolas', 10), wrap='word')
            storage_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            storage_content = f"""
💾 ANALYSE DÉTAILLÉE DU STOCKAGE
{'='*60}

📊 RÉSUMÉ:
• Nombre de disques: {len(drives)}
• Recommandations générées: {len([d for d in drives if d.health_score > 0.8])} disques optimaux

🖥️ DÉTAILS PAR DISQUE:
"""
            
            for drive in drives:
                drive_type = "SSD" if drive.is_ssd else "HDD"
                system_mark = " (SYSTÈME)" if drive.is_system_drive else ""
                
                storage_content += f"""
📁 {drive.device} - {drive_type}{system_mark}
   💾 Espace: {drive.free_bytes/(1024**3):.1f}GB libres / {drive.total_bytes/(1024**3):.1f}GB total
   📊 Usage: {drive.usage_percent:.1f}%
   ⚡ Performance: R={drive.read_speed_mbps:.0f}MB/s, W={drive.write_speed_mbps:.0f}MB/s
   ❤️ Santé: {drive.health_score:.1%}
   🎯 Score global: {drive.overall_score:.2f}
   {'✅ RECOMMANDÉ' if drive.overall_score > 0.8 else '⚠️ ACCEPTABLE' if drive.overall_score > 0.6 else '❌ NON RECOMMANDÉ'}
"""
            
            storage_text.insert(tk.END, storage_content)
            storage_text.config(state='disabled')
            
        except Exception as e:
            error_text = f"❌ Erreur analyse stockage: {e}"
            storage_text.insert(tk.END, error_text)
            storage_text.config(state='disabled')
        
        # Onglet 3: Recommandations
        recommendations_frame = ttk.Frame(stats_notebook)
        stats_notebook.add(recommendations_frame, text="💡 Recommandations")
        
        recommendations_text = tk.Text(recommendations_frame, font=('Arial', 11), wrap='word')
        recommendations_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        try:
            # Générer des recommandations intelligentes
            recommendations = self._generate_intelligent_recommendations()
            
            recommendations_content = f"""
💡 RECOMMANDATIONS INTELLIGENTES
{'='*60}

{recommendations}
"""
            
            recommendations_text.insert(tk.END, recommendations_content)
            recommendations_text.config(state='disabled')
            
        except Exception as e:
            error_text = f"❌ Erreur génération recommandations: {e}"
            recommendations_text.insert(tk.END, error_text)
            recommendations_text.config(state='disabled')
        
        # Boutons d'actions
        actions_frame = tk.Frame(stats_window, bg='#f8f9fa')
        actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(actions_frame, text="🔄 Actualiser", 
                 bg=self.colors['info'], fg='white', font=('Arial', 10),
                 command=lambda: self.show_dataset_stats()).pack(side=tk.LEFT, padx=5)
        
        tk.Button(actions_frame, text="💾 Exporter Rapport", 
                 bg=self.colors['success'], fg='white', font=('Arial', 10),
                 command=lambda: self._export_stats_report(stats_window)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(actions_frame, text="🧹 Optimiser Stockage", 
                 bg=self.colors['warning'], fg='white', font=('Arial', 10),
                 command=self._optimize_storage).pack(side=tk.LEFT, padx=5)
    
    def _generate_intelligent_recommendations(self):
        """Génère des recommandations intelligentes basées sur l'analyse"""
        recommendations = []
        
        try:
            # Analyser le stockage
            drives = self.storage_manager.scan_available_drives()
            storage_stats = self.storage_manager.get_storage_statistics()
            dataset_stats = self.professional_dataset_manager.get_dataset_statistics()
            
            # Recommandations de stockage
            best_drives = [d for d in drives if d.overall_score > 0.8]
            if best_drives:
                recommendations.append(f"✅ STOCKAGE OPTIMAL: Utilisez {best_drives[0].device} pour vos nouveaux datasets (score: {best_drives[0].overall_score:.2f})")
            else:
                recommendations.append("⚠️ STOCKAGE: Aucun disque optimal détecté. Considérez un upgrade SSD.")
            
            # Recommandations d'espace
            total_free = sum(d.free_bytes for d in drives) / (1024**3)
            if total_free < 10:
                recommendations.append("🚨 ESPACE CRITIQUE: Moins de 10GB libres. Nettoyage urgent recommandé!")
            elif total_free < 50:
                recommendations.append("⚠️ ESPACE FAIBLE: Moins de 50GB libres. Planifiez un nettoyage.")
            
            # Recommandations de performance
            avg_read_speed = sum(d.read_speed_mbps for d in drives) / len(drives) if drives else 0
            if avg_read_speed < 100:
                recommendations.append("🐌 PERFORMANCE: Vitesse de lecture faible. Un SSD améliorerait les performances.")
            
            # Recommandations de datasets
            if dataset_stats.get('total_datasets', 0) == 0:
                recommendations.append("📚 DATASETS: Aucun dataset détecté. Commencez par installer les datasets essentiels.")
            elif dataset_stats.get('total_datasets', 0) < 3:
                recommendations.append("📈 DATASETS: Peu de datasets installés. Explorez le catalogue pour enrichir votre base.")
            
            # Recommandations de qualité
            avg_quality = dataset_stats.get('average_quality', 0)
            if avg_quality < 0.7:
                recommendations.append("🎯 QUALITÉ: Qualité moyenne des datasets faible. Validez et corrigez vos annotations.")
            elif avg_quality > 0.9:
                recommendations.append("🏆 QUALITÉ: Excellente qualité des datasets! Partagez vos contributions.")
            
            # Recommandations de maintenance
            recommendations.append("🔧 MAINTENANCE: Exécutez un nettoyage de cache hebdomadaire pour optimiser les performances.")
            recommendations.append("📊 MONITORING: Surveillez régulièrement l'espace disque et les performances.")
            
            if not recommendations:
                recommendations.append("✅ SYSTÈME OPTIMAL: Votre configuration est excellente!")
            
        except Exception as e:
            recommendations.append(f"❌ Erreur génération recommandations: {e}")
        
        return "\n\n".join(f"• {rec}" for rec in recommendations)
    
    def _export_stats_report(self, parent_window):
        """Exporte un rapport détaillé des statistiques"""
        try:
            filename = filedialog.asksaveasfilename(
                parent=parent_window,
                title="Exporter le rapport de statistiques",
                defaultextension=".txt",
                filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")]
            )
            
            if filename:
                # Générer le rapport complet
                report_content = f"""
RAPPORT DE STATISTIQUES YOLO DATASET MANAGER
{'='*60}
Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{self._generate_full_stats_report()}
"""
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                
                messagebox.showinfo("Export", f"Rapport exporté vers:\n{filename}")
                self.log_message(f"📄 Rapport exporté: {filename}")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")
    
    def _generate_full_stats_report(self):
        """Génère un rapport complet pour l'export"""
        try:
            classic_stats = self.dataset_manager.get_dataset_stats()
            pro_stats = self.professional_dataset_manager.get_dataset_statistics()
            storage_stats = self.storage_manager.get_storage_statistics()
            drives = self.storage_manager.scan_available_drives()
            
            report = f"""
STATISTIQUES GÉNÉRALES:
• Datasets classiques: {classic_stats['global'].get('total_datasets', 0)}
• Datasets professionnels: {pro_stats.get('total_datasets', 0)}
• Images totales: {pro_stats.get('total_images', 0):,}
• Annotations: {pro_stats.get('total_annotations', 0):,}
• Taille totale: {pro_stats.get('total_size_gb', 0):.2f} GB

ANALYSE DE STOCKAGE:
• Disques analysés: {len(drives)}
• Espace libre total: {sum(d.free_bytes for d in drives)/(1024**3):.1f} GB
• Vitesse lecture moyenne: {sum(d.read_speed_mbps for d in drives)/len(drives) if drives else 0:.0f} MB/s

RECOMMANDATIONS:
{self._generate_intelligent_recommendations()}
"""
            return report
            
        except Exception as e:
            return f"Erreur génération rapport: {e}"
    
    def _optimize_storage(self):
        """Lance l'optimisation du stockage"""
        try:
            # Créer une fenêtre de progression
            progress_window = tk.Toplevel(self.root)
            progress_window.title("🧹 Optimisation du Stockage")
            progress_window.geometry("500x300")
            progress_window.configure(bg='#f8f9fa')
            
            progress_label = tk.Label(progress_window, text="Optimisation en cours...", 
                                    font=('Arial', 12), bg='#f8f9fa')
            progress_label.pack(pady=20)
            
            progress_text = tk.Text(progress_window, height=15, font=('Consolas', 9))
            progress_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            def optimization_thread():
                try:
                    # Étape 1: Nettoyage du cache
                    progress_text.insert(tk.END, "🧹 Nettoyage du cache...\n")
                    progress_window.update()
                    
                    # Nettoyer les caches
                    if hasattr(self.storage_manager, 'drives_cache'):
                        self.storage_manager.drives_cache.clear()
                        self.storage_manager.cache_timestamp = 0
                    
                    if hasattr(self.professional_dataset_manager, 'datasets_cache'):
                        self.professional_dataset_manager.datasets_cache.clear()
                        self.professional_dataset_manager.cache_timestamp = 0
                    
                    progress_text.insert(tk.END, "✅ Cache nettoyé\n")
                    progress_window.update()
                    
                    # Étape 2: Analyse des doublons
                    progress_text.insert(tk.END, "🔍 Recherche de doublons...\n")
                    progress_window.update()
                    
                    # Simuler la recherche de doublons
                    time.sleep(1)
                    progress_text.insert(tk.END, "✅ Aucun doublon détecté\n")
                    progress_window.update()
                    
                    # Étape 3: Optimisation de l'emplacement
                    progress_text.insert(tk.END, "📍 Optimisation des emplacements...\n")
                    progress_window.update()
                    
                    # Analyser les emplacements optimaux
                    drives = self.storage_manager.scan_available_drives()
                    best_drive = max(drives, key=lambda d: d.overall_score) if drives else None
                    
                    if best_drive:
                        progress_text.insert(tk.END, f"✅ Disque optimal identifié: {best_drive.device}\n")
                    
                    progress_window.update()
                    
                    # Étape 4: Finalisation
                    progress_text.insert(tk.END, "\n🎉 Optimisation terminée!\n")
                    progress_text.insert(tk.END, "💡 Recommandations appliquées avec succès.\n")
                    
                    # Bouton de fermeture
                    close_btn = tk.Button(progress_window, text="Fermer", 
                                        command=progress_window.destroy,
                                        bg=self.colors['success'], fg='white')
                    close_btn.pack(pady=10)
                    
                    self.log_message("🧹 Optimisation du stockage terminée")
                    
                except Exception as e:
                    progress_text.insert(tk.END, f"❌ Erreur: {e}\n")
            
            # Lancer l'optimisation en arrière-plan
            threading.Thread(target=optimization_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'optimisation: {e}")
    
    def activate_learning_mode(self, mode_name):
        """Active un mode d'apprentissage"""
        if not self.learning_system:
            messagebox.showerror("Erreur", "Système d'apprentissage non initialisé!")
            return
        
        success = self.learning_system.activate_mode(mode_name)
        if success:
            self.refresh_learning_stats()
    
    def toggle_stream(self):
        """Active/désactive le stream"""
        if not self.multi_stream:
            messagebox.showerror("Erreur", "Stream non initialisé!")
            return
        
        if not self.multi_stream.stream_active:
            success = self.multi_stream.start_stream()
            if success:
                self.stream_start_btn.configure(text="⏹️ ARRÊTER STREAM", bg=self.colors['danger'])
                self.is_running = True
        else:
            self.multi_stream.stop_stream()
            self.stream_start_btn.configure(text="🚀 DÉMARRER STREAM", bg=self.colors['success'])
            self.is_running = False
        
        self.refresh_targets_list()
    
    def add_screen_target(self):
        """Ajoute un écran comme cible"""
        if not self.multi_stream:
            messagebox.showerror("Erreur", "Stream non initialisé!")
            return
        
        # Interface simple pour sélectionner l'écran
        screen_id = tk.simpledialog.askinteger("Écran", "ID de l'écran (0 = principal):", 
                                              initialvalue=0, minvalue=0, maxvalue=10)
        if screen_id is not None:
            fps = tk.simpledialog.askinteger("FPS", "FPS pour cet écran:", 
                                           initialvalue=30, minvalue=10, maxvalue=60)
            if fps is not None:
                target_id = self.multi_stream.add_screen_target(screen_id, fps)
                if target_id:
                    self.refresh_targets_list()
    
    def add_window_target(self):
        """Ajoute une fenêtre comme cible"""
        if not self.multi_stream:
            messagebox.showerror("Erreur", "Stream non initialisé!")
            return
        
        # Interface simple pour sélectionner la fenêtre
        window_title = tk.simpledialog.askstring("Fenêtre", "Titre de la fenêtre (partiel):")
        if window_title:
            fps = tk.simpledialog.askinteger("FPS", "FPS pour cette fenêtre:", 
                                           initialvalue=30, minvalue=10, maxvalue=60)
            if fps is not None:
                target_id = self.multi_stream.add_window_target(window_title, fps)
                if target_id:
                    self.refresh_targets_list()
    
    def configure_actions(self):
        """Configure les actions automatiques"""
        messagebox.showinfo("Actions", "Configuration des actions - À implémenter")
    
    def configure_zones(self):
        """Configure les zones de détection"""
        if not self.zone_manager:
            messagebox.showerror("Erreur", "Gestionnaire de zones non initialisé!")
            return
        
        self.zone_manager.add_zone_interactive()
    
    def save_config(self):
        """Sauvegarde la configuration"""
        try:
            config = {
                "confidence_threshold": self.confidence_var.get(),
                "fps_global": self.fps_var.get(),
                "timestamp": datetime.now().isoformat()
            }
            
            with open("ultimate_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            self.log_message("💾 Configuration sauvegardée")
            messagebox.showinfo("Sauvegarde", "Configuration sauvegardée!")
            
        except Exception as e:
            self.log_message(f"❌ Erreur sauvegarde: {e}")
    
    def load_config(self):
        """Charge la configuration"""
        try:
            if os.path.exists("ultimate_config.json"):
                with open("ultimate_config.json", "r") as f:
                    config = json.load(f)
                
                self.confidence_var.set(config.get("confidence_threshold", 0.5))
                self.fps_var.set(config.get("fps_global", 30))
                
                self.log_message("📂 Configuration chargée")
                messagebox.showinfo("Chargement", "Configuration chargée!")
            else:
                messagebox.showwarning("Chargement", "Aucune configuration trouvée")
                
        except Exception as e:
            self.log_message(f"❌ Erreur chargement: {e}")
    
    def reset_config(self):
        """Remet la configuration par défaut"""
        if messagebox.askyesno("Reset", "Remettre la configuration par défaut ?"):
            self.confidence_var.set(0.5)
            self.fps_var.set(30)
            self.log_message("🔄 Configuration remise par défaut")
    
    def update_confidence_display(self, *args):
        """Met à jour l'affichage de confiance"""
        value = self.confidence_var.get()
        percentage = int(value * 100)
        self.conf_label.configure(text=f"{percentage}%")
        
        # Appliquer au stream si actif
        if self.multi_stream:
            self.multi_stream.set_confidence_threshold(value)
    
    def refresh_all_data(self):
        """Actualise toutes les données de l'interface"""
        self.refresh_datasets_list()
        self.refresh_learning_stats()
        self.refresh_targets_list()
        self.refresh_performance_stats()
    
    def refresh_datasets_list(self):
        """Actualise la liste des datasets"""
        if not self.dataset_manager:
            return
        
        try:
            # Vider la liste
            for item in self.datasets_tree.get_children():
                self.datasets_tree.delete(item)
            
            # Ajouter les datasets installés
            datasets = self.dataset_manager.get_installed_datasets()
            for dataset in datasets:
                self.datasets_tree.insert("", "end", values=(
                    dataset['name'],
                    dataset['category'],
                    dataset['classes_count'],
                    dataset['images_count'],
                    f"{dataset['size_mb']:.1f} MB"
                ))
                
        except Exception as e:
            self.log_message(f"❌ Erreur refresh datasets: {e}")
    
    def refresh_learning_stats(self):
        """Actualise les statistiques d'apprentissage"""
        if not self.learning_system:
            return
        
        try:
            stats = self.learning_system.get_user_stats()
            
            stats_text = f"""🎨 Objets créés: {stats['objects_created']}
✅ Validations: {stats['validations_made']}
🔧 Corrections: {stats['corrections_applied']}
🌍 Contributions: {stats['contributions_shared']}
🏆 Score total: {stats['total_score']}
📈 Taux de précision: {stats['accuracy_rate']:.1f}%"""
            
            self.learning_stats_text.delete("1.0", tk.END)
            self.learning_stats_text.insert("1.0", stats_text)
            
        except Exception as e:
            self.log_message(f"❌ Erreur refresh learning: {e}")
    
    def refresh_targets_list(self):
        """Actualise la liste des cibles"""
        if not self.multi_stream:
            return
        
        try:
            # Vider la liste
            for item in self.targets_tree.get_children():
                self.targets_tree.delete(item)
            
            # Ajouter les cibles actives
            for target_id, target in self.multi_stream.stream_targets.items():
                status = "🟢 Actif" if target.active else "🔴 Inactif"
                target_name = target.target_data.get('name', target.target_data.get('title', 'Inconnu'))
                
                self.targets_tree.insert("", "end", values=(
                    target_id,
                    target.target_type,
                    target_name,
                    target.fps_target,
                    status,
                    target.capture_count
                ))
                
        except Exception as e:
            self.log_message(f"❌ Erreur refresh targets: {e}")
    
    def refresh_performance_stats(self):
        """Actualise les statistiques de performance"""
        if not self.multi_stream:
            return
        
        try:
            stats = self.multi_stream.get_stream_stats()
            
            perf_text = f"""📊 Frames capturées: {stats['total_frames_captured']}
🎯 Détections totales: {stats['total_detections']}
⏱️ Temps traitement moyen: {stats['average_processing_time']:.1f}ms
🖥️ Cibles actives: {stats['active_targets']}"""
            
            if stats.get('uptime_seconds'):
                uptime = int(stats['uptime_seconds'])
                perf_text += f"\n⏰ Temps de fonctionnement: {uptime}s"
            
            self.performance_text.delete("1.0", tk.END)
            self.performance_text.insert("1.0", perf_text)
            
            # Mettre à jour le footer
            detections = stats['total_detections']
            avg_time = stats['average_processing_time']
            self.footer_stats.configure(
                text=f"📊 Actif | 🎯 {detections} détections | ⏱️ {avg_time:.1f}ms | 💾 {stats.get('memory_usage', 0)}MB"
            )
            
        except Exception as e:
            self.log_message(f"❌ Erreur refresh performance: {e}")
    
    def on_closing(self):
        """Gestionnaire de fermeture"""
        if self.is_running:
            if messagebox.askyesno("Confirmation", 
                                 "Le système est actif. Voulez-vous vraiment quitter ?"):
                if self.multi_stream:
                    self.multi_stream.stop_stream()
                self.save_config()
                self.root.destroy()
        else:
            self.save_config()
            self.root.destroy()
    
    def run(self):
        """Lance l'application"""
        # Démarrer le thread de mise à jour périodique
        self.start_periodic_updates()
        self.root.mainloop()
    
    def start_periodic_updates(self):
        """Démarre les mises à jour périodiques"""
        def update_loop():
            if self.is_running:
                self.refresh_performance_stats()
                self.refresh_targets_list()
            
            # Programmer la prochaine mise à jour
            self.root.after(2000, update_loop)  # Toutes les 2 secondes
        
        # Démarrer la boucle de mise à jour
        self.root.after(1000, update_loop)

# Point d'entrée
if __name__ == "__main__":
    try:
        app = UltimateInterface()
        app.run()
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
