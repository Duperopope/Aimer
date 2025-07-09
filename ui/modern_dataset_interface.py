#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modern Dataset Interface - Interface moderne pour la gestion de datasets
Interface Tkinter professionnelle avec thème sombre et fonctionnalités avancées
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from pathlib import Path
from typing import List, Dict, Optional, Callable
import json
from datetime import datetime

# Import des composants core
try:
    from core.professional_dataset_manager import ProfessionalDatasetManager, DatasetInfo
    from core.intelligent_storage_manager import IntelligentStorageManager
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.professional_dataset_manager import ProfessionalDatasetManager, DatasetInfo
    from core.intelligent_storage_manager import IntelligentStorageManager

class ModernProgressBar:
    """Barre de progression moderne avec animations"""
    
    def __init__(self, parent, width=400, height=20):
        self.parent = parent
        self.width = width
        self.height = height
        
        # Canvas pour la barre de progression
        self.canvas = tk.Canvas(parent, width=width, height=height, 
                               bg='#2b2b2b', highlightthickness=0)
        self.canvas.pack(pady=5)
        
        # Éléments graphiques
        self.bg_rect = self.canvas.create_rectangle(
            2, 2, width-2, height-2, 
            fill='#404040', outline='#606060', width=1
        )
        
        self.progress_rect = self.canvas.create_rectangle(
            2, 2, 2, height-2,
            fill='#00ff88', outline='', width=0
        )
        
        self.text = self.canvas.create_text(
            width//2, height//2,
            text="0%", fill='white', font=('Segoe UI', 9, 'bold')
        )
        
        self.progress = 0.0
        self.animated = False
    
    def set_progress(self, progress: float, text: str = None):
        """Met à jour la progression"""
        self.progress = max(0.0, min(1.0, progress))
        
        # Calculer la largeur de la barre
        bar_width = (self.width - 4) * self.progress
        
        # Mettre à jour la barre
        self.canvas.coords(self.progress_rect, 2, 2, 2 + bar_width, self.height - 2)
        
        # Mettre à jour le texte
        if text is None:
            text = f"{int(self.progress * 100)}%"
        
        self.canvas.itemconfig(self.text, text=text)
        
        # Couleur dynamique
        if self.progress < 0.3:
            color = '#ff6b6b'  # Rouge
        elif self.progress < 0.7:
            color = '#ffd93d'  # Jaune
        else:
            color = '#00ff88'  # Vert
        
        self.canvas.itemconfig(self.progress_rect, fill=color)
        
        self.parent.update_idletasks()
    
    def start_animation(self):
        """Démarre l'animation de chargement"""
        self.animated = True
        self._animate()
    
    def stop_animation(self):
        """Arrête l'animation"""
        self.animated = False
    
    def _animate(self):
        """Animation de la barre de progression"""
        if not self.animated:
            return
        
        # Animation de pulsation
        current_time = time.time()
        pulse = (1 + 0.3 * (1 + tk.math.sin(current_time * 3))) / 2
        
        # Modifier l'opacité (simulation)
        self.canvas.after(50, self._animate)

class DatasetCard:
    """Carte d'affichage d'un dataset"""
    
    def __init__(self, parent, dataset: DatasetInfo, on_select: Callable = None):
        self.parent = parent
        self.dataset = dataset
        self.on_select = on_select
        
        # Frame principale
        self.frame = tk.Frame(parent, bg='#3a3a3a', relief='raised', bd=1)
        self.frame.pack(fill='x', padx=5, pady=2)
        
        # Bind click events
        self.frame.bind("<Button-1>", self._on_click)
        self.frame.bind("<Enter>", self._on_enter)
        self.frame.bind("<Leave>", self._on_leave)
        
        self._create_content()
    
    def _create_content(self):
        """Crée le contenu de la carte"""
        # Header avec nom et statut
        header_frame = tk.Frame(self.frame, bg='#3a3a3a')
        header_frame.pack(fill='x', padx=10, pady=5)
        
        # Nom du dataset
        name_label = tk.Label(
            header_frame, 
            text=self.dataset.name,
            font=('Segoe UI', 12, 'bold'),
            fg='white', bg='#3a3a3a'
        )
        name_label.pack(side='left')
        
        # Statut
        status_color = {
            'ready': '#00ff88',
            'downloading': '#ffd93d',
            'processing': '#6bb6ff',
            'error': '#ff6b6b'
        }.get(self.dataset.status, '#888888')
        
        status_label = tk.Label(
            header_frame,
            text=self.dataset.status.upper(),
            font=('Segoe UI', 8, 'bold'),
            fg=status_color, bg='#3a3a3a'
        )
        status_label.pack(side='right')
        
        # Description
        if self.dataset.description:
            desc_label = tk.Label(
                self.frame,
                text=self.dataset.description[:100] + ("..." if len(self.dataset.description) > 100 else ""),
                font=('Segoe UI', 9),
                fg='#cccccc', bg='#3a3a3a',
                wraplength=400, justify='left'
            )
            desc_label.pack(anchor='w', padx=10)
        
        # Statistiques
        stats_frame = tk.Frame(self.frame, bg='#3a3a3a')
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        # Images
        images_label = tk.Label(
            stats_frame,
            text=f"📷 {self.dataset.total_images} images",
            font=('Segoe UI', 9),
            fg='#aaaaaa', bg='#3a3a3a'
        )
        images_label.pack(side='left')
        
        # Annotations
        if self.dataset.total_annotations > 0:
            annotations_label = tk.Label(
                stats_frame,
                text=f"🏷️ {self.dataset.total_annotations} annotations",
                font=('Segoe UI', 9),
                fg='#aaaaaa', bg='#3a3a3a'
            )
            annotations_label.pack(side='left', padx=(20, 0))
        
        # Taille
        size_mb = self.dataset.total_size_bytes / (1024 * 1024)
        size_label = tk.Label(
            stats_frame,
            text=f"💾 {size_mb:.1f}MB",
            font=('Segoe UI', 9),
            fg='#aaaaaa', bg='#3a3a3a'
        )
        size_label.pack(side='right')
        
        # Qualité
        if self.dataset.quality_score > 0:
            quality_label = tk.Label(
                stats_frame,
                text=f"⭐ {self.dataset.quality_score:.1%}",
                font=('Segoe UI', 9),
                fg='#aaaaaa', bg='#3a3a3a'
            )
            quality_label.pack(side='right', padx=(0, 20))
    
    def _on_click(self, event):
        """Gestion du clic"""
        if self.on_select:
            self.on_select(self.dataset)
    
    def _on_enter(self, event):
        """Survol de la souris"""
        self.frame.config(bg='#4a4a4a')
        for child in self.frame.winfo_children():
            if hasattr(child, 'config'):
                try:
                    child.config(bg='#4a4a4a')
                except:
                    pass
    
    def _on_leave(self, event):
        """Sortie de la souris"""
        self.frame.config(bg='#3a3a3a')
        for child in self.frame.winfo_children():
            if hasattr(child, 'config'):
                try:
                    child.config(bg='#3a3a3a')
                except:
                    pass

class ModernDatasetInterface:
    """Interface moderne pour la gestion de datasets"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 YOLO Dataset Manager Pro")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Gestionnaire de datasets
        self.dataset_manager = ProfessionalDatasetManager()
        self.storage_manager = IntelligentStorageManager()
        
        # Variables
        self.datasets = []
        self.selected_dataset = None
        self.search_results = []
        
        # Configuration du style
        self._setup_style()
        
        # Interface
        self._create_interface()
        
        # Charger les datasets
        self._refresh_datasets()
    
    def _setup_style(self):
        """Configure le style moderne"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configuration des couleurs
        style.configure('Modern.TFrame', background='#2b2b2b')
        style.configure('Modern.TLabel', background='#2b2b2b', foreground='white')
        style.configure('Modern.TButton', 
                       background='#404040', 
                       foreground='white',
                       borderwidth=1,
                       focuscolor='none')
        style.map('Modern.TButton',
                 background=[('active', '#505050')])
        
        style.configure('Modern.TEntry',
                       background='#404040',
                       foreground='white',
                       borderwidth=1,
                       insertcolor='white')
        
        style.configure('Modern.Treeview',
                       background='#3a3a3a',
                       foreground='white',
                       fieldbackground='#3a3a3a',
                       borderwidth=0)
        style.configure('Modern.Treeview.Heading',
                       background='#404040',
                       foreground='white',
                       borderwidth=1)
    
    def _create_interface(self):
        """Crée l'interface utilisateur"""
        # Menu principal
        self._create_menu()
        
        # Toolbar
        self._create_toolbar()
        
        # Contenu principal
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Panneau gauche - Liste des datasets
        self._create_datasets_panel(main_frame)
        
        # Panneau droit - Détails et actions
        self._create_details_panel(main_frame)
        
        # Barre de statut
        self._create_status_bar()
    
    def _create_menu(self):
        """Crée le menu principal"""
        menubar = tk.Menu(self.root, bg='#404040', fg='white')
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0, bg='#404040', fg='white')
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Nouveau Dataset", command=self._new_dataset)
        file_menu.add_command(label="Importer Dataset", command=self._import_dataset)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        
        # Menu Outils
        tools_menu = tk.Menu(menubar, tearoff=0, bg='#404040', fg='white')
        menubar.add_cascade(label="Outils", menu=tools_menu)
        tools_menu.add_command(label="Analyser Stockage", command=self._analyze_storage)
        tools_menu.add_command(label="Nettoyer Cache", command=self._clean_cache)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0, bg='#404040', fg='white')
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À propos", command=self._show_about)
    
    def _create_toolbar(self):
        """Crée la barre d'outils"""
        toolbar = tk.Frame(self.root, bg='#404040', height=40)
        toolbar.pack(fill='x', padx=5, pady=2)
        toolbar.pack_propagate(False)
        
        # Boutons principaux
        tk.Button(
            toolbar, text="➕ Nouveau", 
            bg='#00ff88', fg='black', font=('Segoe UI', 9, 'bold'),
            command=self._new_dataset, relief='flat', padx=15
        ).pack(side='left', padx=5, pady=5)
        
        tk.Button(
            toolbar, text="📥 Télécharger", 
            bg='#6bb6ff', fg='white', font=('Segoe UI', 9, 'bold'),
            command=self._download_dataset, relief='flat', padx=15
        ).pack(side='left', padx=5, pady=5)
        
        tk.Button(
            toolbar, text="🔄 Actualiser", 
            bg='#ffd93d', fg='black', font=('Segoe UI', 9, 'bold'),
            command=self._refresh_datasets, relief='flat', padx=15
        ).pack(side='left', padx=5, pady=5)
        
        # Barre de recherche
        search_frame = tk.Frame(toolbar, bg='#404040')
        search_frame.pack(side='right', padx=10, pady=5)
        
        tk.Label(search_frame, text="🔍", bg='#404040', fg='white', 
                font=('Segoe UI', 12)).pack(side='left')
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame, textvariable=self.search_var,
            bg='#505050', fg='white', font=('Segoe UI', 9),
            width=30, relief='flat'
        )
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<Return>', self._search_datasets)
    
    def _create_datasets_panel(self, parent):
        """Crée le panneau des datasets"""
        # Frame principal
        datasets_frame = tk.Frame(parent, bg='#2b2b2b', width=400)
        datasets_frame.pack(side='left', fill='both', expand=False, padx=(0, 10))
        datasets_frame.pack_propagate(False)
        
        # Titre
        title_label = tk.Label(
            datasets_frame, text="📦 Mes Datasets",
            font=('Segoe UI', 14, 'bold'),
            fg='white', bg='#2b2b2b'
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Frame avec scrollbar
        list_frame = tk.Frame(datasets_frame, bg='#2b2b2b')
        list_frame.pack(fill='both', expand=True)
        
        # Canvas et scrollbar pour la liste
        self.datasets_canvas = tk.Canvas(list_frame, bg='#2b2b2b', highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient='vertical', command=self.datasets_canvas.yview)
        self.scrollable_frame = tk.Frame(self.datasets_canvas, bg='#2b2b2b')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.datasets_canvas.configure(scrollregion=self.datasets_canvas.bbox("all"))
        )
        
        self.datasets_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.datasets_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.datasets_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        self.datasets_canvas.bind("<MouseWheel>", self._on_mousewheel)
    
    def _create_details_panel(self, parent):
        """Crée le panneau des détails"""
        details_frame = tk.Frame(parent, bg='#2b2b2b')
        details_frame.pack(side='right', fill='both', expand=True)
        
        # Titre
        self.details_title = tk.Label(
            details_frame, text="📊 Détails du Dataset",
            font=('Segoe UI', 14, 'bold'),
            fg='white', bg='#2b2b2b'
        )
        self.details_title.pack(anchor='w', pady=(0, 10))
        
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(details_frame, style='Modern.TNotebook')
        self.notebook.pack(fill='both', expand=True)
        
        # Onglet Informations
        self._create_info_tab()
        
        # Onglet Recherche
        self._create_search_tab()
        
        # Onglet Stockage
        self._create_storage_tab()
    
    def _create_info_tab(self):
        """Crée l'onglet d'informations"""
        info_frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(info_frame, text="ℹ️ Informations")
        
        # Zone d'informations
        self.info_text = tk.Text(
            info_frame, bg='#3a3a3a', fg='white',
            font=('Consolas', 10), wrap='word',
            state='disabled', relief='flat'
        )
        self.info_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Boutons d'actions
        actions_frame = tk.Frame(info_frame, bg='#2b2b2b')
        actions_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(
            actions_frame, text="📂 Ouvrir Dossier",
            bg='#505050', fg='white', font=('Segoe UI', 9),
            command=self._open_dataset_folder, relief='flat'
        ).pack(side='left', padx=5)
        
        tk.Button(
            actions_frame, text="📤 Exporter",
            bg='#505050', fg='white', font=('Segoe UI', 9),
            command=self._export_dataset, relief='flat'
        ).pack(side='left', padx=5)
        
        tk.Button(
            actions_frame, text="🗑️ Supprimer",
            bg='#ff6b6b', fg='white', font=('Segoe UI', 9),
            command=self._delete_dataset, relief='flat'
        ).pack(side='right', padx=5)
    
    def _create_search_tab(self):
        """Crée l'onglet de recherche"""
        search_frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(search_frame, text="🔍 Recherche")
        
        # Zone de recherche
        search_controls = tk.Frame(search_frame, bg='#2b2b2b')
        search_controls.pack(fill='x', padx=10, pady=10)
        
        tk.Label(search_controls, text="Rechercher des datasets:",
                font=('Segoe UI', 11, 'bold'), fg='white', bg='#2b2b2b').pack(anchor='w')
        
        search_input_frame = tk.Frame(search_controls, bg='#2b2b2b')
        search_input_frame.pack(fill='x', pady=5)
        
        self.external_search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_input_frame, textvariable=self.external_search_var,
            bg='#404040', fg='white', font=('Segoe UI', 10),
            relief='flat'
        )
        search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        tk.Button(
            search_input_frame, text="🔍 Rechercher",
            bg='#6bb6ff', fg='white', font=('Segoe UI', 9, 'bold'),
            command=self._search_external_datasets, relief='flat'
        ).pack(side='right')
        
        # Résultats de recherche
        results_frame = tk.Frame(search_frame, bg='#2b2b2b')
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.search_results_text = tk.Text(
            results_frame, bg='#3a3a3a', fg='white',
            font=('Segoe UI', 9), wrap='word',
            state='disabled', relief='flat'
        )
        self.search_results_text.pack(fill='both', expand=True)
    
    def _create_storage_tab(self):
        """Crée l'onglet de stockage"""
        storage_frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(storage_frame, text="💾 Stockage")
        
        # Informations de stockage
        self.storage_text = tk.Text(
            storage_frame, bg='#3a3a3a', fg='white',
            font=('Consolas', 9), wrap='word',
            state='disabled', relief='flat'
        )
        self.storage_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Actualiser les informations de stockage
        self._update_storage_info()
    
    def _create_status_bar(self):
        """Crée la barre de statut"""
        self.status_bar = tk.Frame(self.root, bg='#404040', height=25)
        self.status_bar.pack(fill='x', side='bottom')
        self.status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_bar, text="Prêt",
            bg='#404040', fg='white', font=('Segoe UI', 9)
        )
        self.status_label.pack(side='left', padx=10, pady=2)
        
        # Indicateur de progression
        self.progress_bar = ModernProgressBar(self.status_bar, width=200, height=15)
    
    def _refresh_datasets(self):
        """Actualise la liste des datasets"""
        self._set_status("Actualisation des datasets...")
        
        # Vider la liste actuelle
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Charger les datasets
        self.datasets = self.dataset_manager.list_datasets()
        
        # Créer les cartes
        for dataset in self.datasets:
            card = DatasetCard(self.scrollable_frame, dataset, self._select_dataset)
        
        self._set_status(f"{len(self.datasets)} datasets chargés")
    
    def _select_dataset(self, dataset: DatasetInfo):
        """Sélectionne un dataset"""
        self.selected_dataset = dataset
        self._update_dataset_info()
    
    def _update_dataset_info(self):
        """Met à jour les informations du dataset sélectionné"""
        if not self.selected_dataset:
            return
        
        # Mettre à jour le titre
        self.details_title.config(text=f"📊 {self.selected_dataset.name}")
        
        # Informations détaillées
        info = f"""
INFORMATIONS GÉNÉRALES
{'='*50}
Nom: {self.selected_dataset.name}
Description: {self.selected_dataset.description or 'Aucune description'}
Format: {self.selected_dataset.format_type}
Type: {'Custom' if self.selected_dataset.is_custom else 'Externe'}
Statut: {self.selected_dataset.status}

STATISTIQUES
{'='*50}
Images: {self.selected_dataset.total_images:,}
Annotations: {self.selected_dataset.total_annotations:,}
Taille: {self.selected_dataset.total_size_bytes / (1024*1024):.1f} MB
Qualité: {self.selected_dataset.quality_score:.1%}

CLASSES
{'='*50}
{', '.join(self.selected_dataset.classes) if self.selected_dataset.classes else 'Aucune classe définie'}

STOCKAGE
{'='*50}
Chemin: {self.selected_dataset.storage_path}

DATES
{'='*50}
Créé: {self.selected_dataset.created_at}
Modifié: {self.selected_dataset.last_modified}
"""
        
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)
        self.info_text.config(state='disabled')
    
    def _update_storage_info(self):
        """Met à jour les informations de stockage"""
        try:
            # Obtenir les statistiques de stockage
            storage_stats = self.storage_manager.get_storage_statistics()
            dataset_stats = self.dataset_manager.get_dataset_statistics()
            
            # Scanner les disques
            drives = self.storage_manager.scan_available_drives()
            
            info = f"""
STATISTIQUES GLOBALES
{'='*50}
Total datasets: {dataset_stats.get('total_datasets', 0)}
Total images: {dataset_stats.get('total_images', 0):,}
Espace utilisé: {dataset_stats.get('total_size_gb', 0):.2f} GB

DISQUES DISPONIBLES
{'='*50}
"""
            
            for drive in drives:
                drive_type = "SSD" if drive.is_ssd else "HDD"
                system_mark = " (SYSTÈME)" if drive.is_system_drive else ""
                
                info += f"""
📁 {drive.device} - {drive_type}{system_mark}
   Espace: {drive.free_bytes/(1024**3):.1f}GB libres / {drive.total_bytes/(1024**3):.1f}GB total
   Usage: {drive.usage_percent:.1f}%
   Performance: R={drive.read_speed_mbps:.0f}MB/s, W={drive.write_speed_mbps:.0f}MB/s
   Santé: {drive.health_score:.1%}
"""
            
            self.storage_text.config(state='normal')
            self.storage_text.delete(1.0, tk.END)
            self.storage_text.insert(1.0, info)
            self.storage_text.config(state='disabled')
            
        except Exception as e:
            self.storage_text.config(state='normal')
            self.storage_text.delete(1.0, tk.END)
            self.storage_text.insert(1.0, f"Erreur lors du chargement des informations de stockage:\n{e}")
            self.storage_text.config(state='disabled')
    
    def _new_dataset(self):
        """Crée un nouveau dataset"""
        dialog = DatasetCreationDialog(self.root, self.dataset_manager)
        if dialog.result:
            self._refresh_datasets()
            self._set_status(f"Dataset '{dialog.result.name}' créé avec succès")
    
    def _import_dataset(self):
        """Importe un dataset existant"""
        folder = filedialog.askdirectory(title="Sélectionner le dossier du dataset")
        if folder:
            # Logique d'import à implémenter
            self._set_status(f"Import depuis {folder}")
    
    def _download_dataset(self):
        """Télécharge un dataset externe"""
        self.notebook.select(1)  # Aller à l'onglet recherche
        self._set_status("Utilisez l'onglet Recherche pour télécharger des datasets")
    
    def _search_datasets(self, event=None):
        """Recherche dans les datasets locaux"""
        query = self.search_var.get().lower()
        if not query:
            self._refresh_datasets()
            return
        
        # Filtrer les datasets
        filtered_datasets = [
            dataset for dataset in self.datasets
            if query in dataset.name.lower() or 
               query in (dataset.description or "").lower() or
               any(query in cls.lower() for cls in dataset.classes)
        ]
        
        # Vider et recréer la liste
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        for dataset in filtered_datasets:
            card = DatasetCard(self.scrollable_frame, dataset, self._select_dataset)
        
        self._set_status(f"{len(filtered_datasets)} datasets trouvés")
    
    def _search_external_datasets(self):
        """Recherche des datasets externes"""
        query = self.external_search_var.get()
        if not query:
            return
        
        self._set_status("Recherche en cours...")
        
        def search_thread():
            try:
                results = self.dataset_manager.search_external_datasets(query)
                
                # Mettre à jour l'interface dans le thread principal
                self.root.after(0, lambda: self._display_search_results(results))
                
            except Exception as e:
                self.root.after(0, lambda: self._set_status(f"Erreur recherche: {e}"))
        
        # Lancer la recherche en arrière-plan
        threading.Thread(target=search_thread, daemon=True).start()
    
    def _display_search_results(self, results: List[Dict]):
        """Affiche les résultats de recherche"""
        self.search_results_text.config(state='normal')
        self.search_results_text.delete(1.0, tk.END)
        
        if not results:
            self.search_results_text.insert(tk.END, "Aucun résultat trouvé.")
        else:
            for i, result in enumerate(results, 1):
                text = f"""
{i}. {result['name']} ({result['source']})
   📝 {result['description'][:150]}...
   📊 {result['image_count']} images | {result['size_mb']}MB
   📄 Format: {result['format']} | Licence: {result['license']}
   🔗 {result['download_url']}
   
   [Cliquez pour télécharger]
   
{'='*60}
"""
                self.search_results_text.insert(tk.END, text)
        
        self.search_results_text.config(state='disabled')
        self._set_status(f"{len(results)} résultats trouvés")
    
    def _analyze_storage(self):
        """Analyse le stockage"""
        self.notebook.select(2)  # Aller à l'onglet stockage
        self._update_storage_info()
        self._set_status("Analyse du stockage terminée")
    
    def _clean_cache(self):
        """Nettoie le cache"""
        try:
            # Nettoyer le cache du gestionnaire de stockage
            self.storage_manager.drives_cache.clear()
            self.storage_manager.cache_timestamp = 0
            
            # Nettoyer le cache des datasets
            self.dataset_manager.datasets_cache.clear()
            self.dataset_manager.cache_timestamp = 0
            
            self._set_status("Cache nettoyé")
            messagebox.showinfo("Cache", "Cache nettoyé avec succès")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du nettoyage: {e}")
    
    def _show_about(self):
        """Affiche les informations sur l'application"""
        about_text = """
🎯 YOLO Dataset Manager Pro v2.0

Gestionnaire professionnel de datasets pour YOLO
avec intelligence artificielle et optimisation automatique.

Fonctionnalités:
• Gestion intelligente du stockage
• Analyse automatique de la qualité des images
• Recherche et téléchargement de datasets externes
• Interface moderne avec thème sombre
• Optimisation des performances

Développé avec ❤️ pour la communauté YOLO
"""
        messagebox.showinfo("À propos", about_text)
    
    def _open_dataset_folder(self):
        """Ouvre le dossier du dataset sélectionné"""
        if not self.selected_dataset:
            messagebox.showwarning("Attention", "Aucun dataset sélectionné")
            return
        
        try:
            import os
            import subprocess
            import platform
            
            path = self.selected_dataset.storage_path
            
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", path])
            else:  # Linux
                subprocess.run(["xdg-open", path])
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le dossier: {e}")
    
    def _export_dataset(self):
        """Exporte le dataset sélectionné"""
        if not self.selected_dataset:
            messagebox.showwarning("Attention", "Aucun dataset sélectionné")
            return
        
        # Dialogue de sélection du format
        format_dialog = ExportFormatDialog(self.root)
        if not format_dialog.result:
            return
        
        # Dialogue de sélection du dossier
        export_folder = filedialog.askdirectory(title="Sélectionner le dossier d'export")
        if not export_folder:
            return
        
        try:
            success = self.dataset_manager.export_dataset(
                self.selected_dataset.id, 
                export_folder, 
                format_dialog.result
            )
            
            if success:
                messagebox.showinfo("Export", f"Dataset exporté avec succès vers {export_folder}")
            else:
                messagebox.showerror("Erreur", "Échec de l'export")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")
    
    def _delete_dataset(self):
        """Supprime le dataset sélectionné"""
        if not self.selected_dataset:
            messagebox.showwarning("Attention", "Aucun dataset sélectionné")
            return
        
        # Confirmation
        response = messagebox.askyesnocancel(
            "Supprimer Dataset",
            f"Voulez-vous supprimer le dataset '{self.selected_dataset.name}' ?\n\n"
            "Oui: Supprimer de la base ET les fichiers\n"
            "Non: Supprimer seulement de la base\n"
            "Annuler: Ne rien faire"
        )
        
        if response is None:  # Annuler
            return
        
        try:
            success = self.dataset_manager.delete_dataset(
                self.selected_dataset.id, 
                delete_files=response
            )
            
            if success:
                self._refresh_datasets()
                self.selected_dataset = None
                self._clear_dataset_info()
                self._set_status("Dataset supprimé")
            else:
                messagebox.showerror("Erreur", "Échec de la suppression")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression: {e}")
    
    def _clear_dataset_info(self):
        """Efface les informations du dataset"""
        self.details_title.config(text="📊 Détails du Dataset")
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "Sélectionnez un dataset pour voir ses détails.")
        self.info_text.config(state='disabled')
    
    def _on_mousewheel(self, event):
        """Gestion de la molette de la souris"""
        self.datasets_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _set_status(self, message: str):
        """Met à jour le message de statut"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def run(self):
        """Lance l'interface"""
        self.root.mainloop()

class DatasetCreationDialog:
    """Dialogue de création de dataset"""
    
    def __init__(self, parent, dataset_manager: ProfessionalDatasetManager):
        self.parent = parent
        self.dataset_manager = dataset_manager
        self.result = None
        
        # Créer la fenêtre
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nouveau Dataset")
        self.dialog.geometry("500x400")
        self.dialog.configure(bg='#2b2b2b')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self._create_interface()
    
    def _create_interface(self):
        """Crée l'interface du dialogue"""
        # Titre
        title_label = tk.Label(
            self.dialog, text="➕ Créer un Nouveau Dataset",
            font=('Segoe UI', 14, 'bold'),
            fg='white', bg='#2b2b2b'
        )
        title_label.pack(pady=20)
        
        # Frame principal
        main_frame = tk.Frame(self.dialog, bg='#2b2b2b')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Nom du dataset
        tk.Label(main_frame, text="Nom du dataset:", 
                font=('Segoe UI', 10, 'bold'), fg='white', bg='#2b2b2b').pack(anchor='w')
        
        self.name_var = tk.StringVar()
        name_entry = tk.Entry(
            main_frame, textvariable=self.name_var,
            bg='#404040', fg='white', font=('Segoe UI', 10),
            relief='flat'
        )
        name_entry.pack(fill='x', pady=(5, 15))
        name_entry.focus()
        
        # Description
        tk.Label(main_frame, text="Description (optionnelle):", 
                font=('Segoe UI', 10, 'bold'), fg='white', bg='#2b2b2b').pack(anchor='w')
        
        self.description_text = tk.Text(
            main_frame, height=4,
            bg='#404040', fg='white', font=('Segoe UI', 9),
            relief='flat', wrap='word'
        )
        self.description_text.pack(fill='x', pady=(5, 15))
        
        # Images
        tk.Label(main_frame, text="Images (optionnel):", 
                font=('Segoe UI', 10, 'bold'), fg='white', bg='#2b2b2b').pack(anchor='w')
        
        images_frame = tk.Frame(main_frame, bg='#2b2b2b')
        images_frame.pack(fill='x', pady=(5, 15))
        
        self.images_label = tk.Label(
            images_frame, text="Aucune image sélectionnée",
            fg='#aaaaaa', bg='#2b2b2b', font=('Segoe UI', 9)
        )
        self.images_label.pack(side='left')
        
        tk.Button(
            images_frame, text="📁 Parcourir",
            bg='#505050', fg='white', font=('Segoe UI', 9),
            command=self._select_images, relief='flat'
        ).pack(side='right')
        
        self.selected_images = []
        
        # Boutons
        buttons_frame = tk.Frame(self.dialog, bg='#2b2b2b')
        buttons_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Button(
            buttons_frame, text="Annuler",
            bg='#505050', fg='white', font=('Segoe UI', 10),
            command=self._cancel, relief='flat', padx=20
        ).pack(side='right', padx=5)
        
        tk.Button(
            buttons_frame, text="Créer",
            bg='#00ff88', fg='black', font=('Segoe UI', 10, 'bold'),
            command=self._create, relief='flat', padx=20
        ).pack(side='right', padx=5)
    
    def _select_images(self):
        """Sélectionne les images"""
        filetypes = [
            ("Images", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
            ("Tous les fichiers", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Sélectionner les images",
            filetypes=filetypes
        )
        
        if files:
            self.selected_images = list(files)
            self.images_label.config(text=f"{len(files)} image(s) sélectionnée(s)")
    
    def _create(self):
        """Crée le dataset"""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Erreur", "Le nom du dataset est requis")
            return
        
        description = self.description_text.get(1.0, tk.END).strip()
        
        try:
            self.result = self.dataset_manager.create_custom_dataset(
                name=name,
                description=description,
                image_paths=self.selected_images if self.selected_images else None
            )
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création: {e}")
    
    def _cancel(self):
        """Annule la création"""
        self.dialog.destroy()

class ExportFormatDialog:
    """Dialogue de sélection du format d'export"""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        
        # Créer la fenêtre
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Format d'Export")
        self.dialog.geometry("300x200")
        self.dialog.configure(bg='#2b2b2b')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 100, parent.winfo_rooty() + 100))
        
        self._create_interface()
    
    def _create_interface(self):
        """Crée l'interface du dialogue"""
        # Titre
        title_label = tk.Label(
            self.dialog, text="📤 Format d'Export",
            font=('Segoe UI', 12, 'bold'),
            fg='white', bg='#2b2b2b'
        )
        title_label.pack(pady=20)
        
        # Options de format
        self.format_var = tk.StringVar(value="YOLO")
        
        formats = [
            ("YOLO", "YOLO"),
            ("COCO", "COCO"),
            ("Pascal VOC", "Pascal VOC")
        ]
        
        for text, value in formats:
            tk.Radiobutton(
                self.dialog, text=text, variable=self.format_var, value=value,
                bg='#2b2b2b', fg='white', selectcolor='#404040',
                font=('Segoe UI', 10)
            ).pack(anchor='w', padx=50, pady=5)
        
        # Boutons
        buttons_frame = tk.Frame(self.dialog, bg='#2b2b2b')
        buttons_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Button(
            buttons_frame, text="Annuler",
            bg='#505050', fg='white', font=('Segoe UI', 9),
            command=self._cancel, relief='flat'
        ).pack(side='right', padx=5)
        
        tk.Button(
            buttons_frame, text="OK",
            bg='#00ff88', fg='black', font=('Segoe UI', 9, 'bold'),
            command=self._ok, relief='flat'
        ).pack(side='right', padx=5)
    
    def _ok(self):
        """Confirme la sélection"""
        self.result = self.format_var.get()
        self.dialog.destroy()
    
    def _cancel(self):
        """Annule la sélection"""
        self.dialog.destroy()

def main():
    """Fonction principale"""
    app = ModernDatasetInterface()
    app.run()

if __name__ == "__main__":
    main()
