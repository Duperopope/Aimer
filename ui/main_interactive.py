# -*- coding: utf-8 -*-
"""
Système de Visée Intelligent - Version Interactive
Permet de voir ce que le système détecte et configurer des actions
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

# Configuration pour éviter les erreurs d'importation
try:
    from ultralytics import YOLO
    from ui.zone_selector import ZoneManager
    from utils.multi_screen import TargetSelector
    IMPORTS_OK = True
except ImportError as e:
    IMPORTS_OK = False
    IMPORT_ERROR = str(e)

class InteractiveAimingSystem:
    def __init__(self):
        # Variables d'état
        self.is_running = False
        self.detection_thread = None
        self.model = None
        self.total_detections = 0
        self.start_time = None
        self.last_screenshot = None
        
        # Configuration des zones et actions
        self.detection_zones = []  # Liste des zones à surveiller
        self.detection_actions = {}  # Actions à déclencher par classe
        self.current_detections = []  # Détections actuelles
        
        # Gestionnaire de zones
        self.zone_manager = None
        
        # Sélecteur de cible (écran/fenêtre)
        self.target_selector = None
        self.current_target = None
        
        # Configuration des couleurs
        self.colors = {
            'primary': '#007bff',
            'success': '#28a745',
            'warning': '#ffc107', 
            'danger': '#dc3545',
            'info': '#17a2b8'
        }
        
        # Interface principale
        self.root = tk.Tk()
        self.setup_main_window()
        self.create_interface()
        
        # Charger la configuration
        self.load_config()
        
        # Initialisation différée
        self.root.after(100, self.delayed_init)
    
    def setup_main_window(self):
        """Configure la fenêtre principale"""
        self.root.title("🎯 Système de Visée Intelligent - Mode Interactif")
        self.root.geometry("1200x800")
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
    
    def create_interface(self):
        """Crée l'interface utilisateur interactive"""
        # Panneau de contrôle principal
        control_panel = ttk.Frame(self.root, padding="10")
        control_panel.pack(side=tk.TOP, fill=tk.X)
        
        # Titre
        title_label = ttk.Label(control_panel, text="🎯 Système de Visée Intelligent - Mode Interactif", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=5)
        
        # Boutons de contrôle
        control_buttons = ttk.Frame(control_panel)
        control_buttons.pack(fill=tk.X, pady=5)
        
        self.main_start_btn = tk.Button(control_buttons, 
                                       text="🎯 DÉMARRER LA DÉTECTION", 
                                       font=('Arial', 12, 'bold'),
                                       bg=self.colors['success'], 
                                       fg='white',
                                       command=self.toggle_detection)
        self.main_start_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_buttons, 
                 text="📷 CAPTURE & ANALYSE", 
                 font=('Arial', 11),
                 bg=self.colors['info'], 
                 fg='white',
                 command=self.capture_and_analyze).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_buttons, 
                 text="🎯 CONFIGURER ZONES", 
                 font=('Arial', 11),
                 bg=self.colors['warning'], 
                 fg='white',
                 command=self.configure_zones).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_buttons, 
                 text="⚡ CONFIGURER ACTIONS", 
                 font=('Arial', 11),
                 bg=self.colors['primary'], 
                 fg='white',
                 command=self.configure_actions).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_buttons, 
                 text="🖥️ SÉLECTIONNER CIBLE", 
                 font=('Arial', 11),
                 bg='#6f42c1', 
                 fg='white',
                 command=self.select_target).pack(side=tk.LEFT, padx=5)
        
        # Panneau principal divisé
        main_panel = ttk.Frame(self.root)
        main_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Panneau gauche - Affichage visuel
        left_panel = ttk.LabelFrame(main_panel, text="🖥️ Vue en Temps Réel", padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Canvas pour afficher l'image avec détections
        self.image_canvas = tk.Canvas(left_panel, bg='black', width=600, height=400)
        self.image_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Panneau droit - Contrôles et logs
        right_panel = ttk.Frame(main_panel)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # Statut
        status_frame = ttk.LabelFrame(right_panel, text="📊 Statut", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_text = tk.StringVar(value="🔴 Arrêté")
        ttk.Label(status_frame, textvariable=self.status_text, 
                 font=('Arial', 12, 'bold')).pack()
        
        # Métriques
        metrics_frame = ttk.Frame(status_frame)
        metrics_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(metrics_frame, text="Détections:").pack(side=tk.LEFT)
        self.detections_count = tk.StringVar(value="0")
        ttk.Label(metrics_frame, textvariable=self.detections_count, 
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        # Configuration rapide
        config_frame = ttk.LabelFrame(right_panel, text="⚙️ Configuration", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Seuil de confiance
        ttk.Label(config_frame, text="Confiance:").pack(anchor='w')
        self.confidence_var = tk.DoubleVar(value=0.5)
        confidence_scale = ttk.Scale(config_frame, from_=0.1, to=0.9, 
                                    variable=self.confidence_var, orient='horizontal')
        confidence_scale.pack(fill=tk.X, pady=2)
        
        self.confidence_label = ttk.Label(config_frame, text="50%")
        self.confidence_label.pack()
        self.confidence_var.trace('w', self.update_confidence_display)
        
        # Classes ciblées
        ttk.Label(config_frame, text="Classes ciblées:").pack(anchor='w', pady=(10, 0))
        self.target_classes = tk.StringVar(value="person,head,body,chest,box")
        ttk.Entry(config_frame, textvariable=self.target_classes, width=25).pack(fill=tk.X, pady=2)
        
        # Log en temps réel
        log_frame = ttk.LabelFrame(right_panel, text="📋 Log Temps Réel", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, height=15, width=40, 
                               bg='#ffffff', font=('Consolas', 8))
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, 
                                     command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Message initial
        self.log_message("🚀 Système interactif initialisé")
        self.log_message("📋 Utilisez 'CAPTURE & ANALYSE' pour commencer")
    
    def delayed_init(self):
        """Initialisation différée"""
        if not IMPORTS_OK:
            self.log_message("❌ ERREUR: Modules manquants!")
            self.log_message(f"Détails: {IMPORT_ERROR}")
            return
        
        try:
            self.log_message("🔄 Chargement du modèle YOLO...")
            self.model = YOLO('yolov8n.pt')
            self.log_message("✅ Modèle YOLO chargé!")
            self.log_message(f"📊 {len(self.model.names)} classes disponibles")
            
            # Initialiser le gestionnaire de zones
            self.zone_manager = ZoneManager(log_callback=self.log_message)
            self.log_message("🎯 Gestionnaire de zones initialisé")
            
            # Initialiser le sélecteur de cible
            self.target_selector = TargetSelector(log_callback=self.log_message)
            self.log_message("🖥️ Sélecteur de cible initialisé")
            
            # Afficher les classes pertinentes pour les jeux
            gaming_classes = ['person', 'bottle', 'cup', 'bowl', 'laptop', 'mouse', 'keyboard', 'cell phone', 'book', 'clock', 'scissors', 'chair', 'dining table']
            available_gaming = [cls for cls in gaming_classes if cls in self.model.names.values()]
            self.log_message(f"🎮 Classes gaming: {', '.join(available_gaming[:5])}...")
            
            self.status_text.set("✅ Prêt")
            
        except Exception as e:
            self.log_message(f"❌ Erreur: {e}")
            self.status_text.set("❌ Erreur")
    
    def capture_and_analyze(self):
        """Capture l'écran et analyse les détections"""
        if not self.model:
            messagebox.showerror("Erreur", "Modèle YOLO non chargé!")
            return
        
        self.log_message("📷 Capture et analyse en cours...")
        
        try:
            # Capture d'écran
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            self.last_screenshot = screenshot.copy()
            
            # Détection
            results = self.model(screenshot, conf=self.confidence_var.get(), verbose=False)
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        class_id = int(box.cls[0])
                        class_name = self.model.names[class_id]
                        confidence = float(box.conf[0])
                        bbox = box.xyxy[0].tolist()
                        
                        # Filtrer par classes ciblées
                        target_list = [cls.strip() for cls in self.target_classes.get().split(',') if cls.strip()]
                        if not target_list or class_name in target_list:
                            detections.append({
                                'class_name': class_name,
                                'confidence': confidence,
                                'bbox': bbox,
                                'center': [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]
                            })
            
            self.current_detections = detections
            self.display_detections(screenshot, detections)
            
            self.log_message(f"🎯 Trouvé {len(detections)} objets")
            for detection in detections:
                self.log_message(f"  • {detection['class_name']}: {detection['confidence']:.2f}")
            
        except Exception as e:
            self.log_message(f"❌ Erreur capture: {e}")
    
    def display_detections(self, image, detections):
        """Affiche l'image avec les détections dans le canvas"""
        # Redimensionner l'image pour le canvas
        height, width = image.shape[:2]
        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()
        
        # Calculer le ratio pour maintenir l'aspect
        ratio = min(canvas_width / width, canvas_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        # Redimensionner l'image
        resized_image = cv2.resize(image, (new_width, new_height))
        
        # Dessiner les détections
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            # Adapter aux nouvelles dimensions
            x1, y1, x2, y2 = int(x1 * ratio), int(y1 * ratio), int(x2 * ratio), int(y2 * ratio)
            
            # Couleur selon la classe
            color = self.get_class_color(detection['class_name'])
            
            # Dessiner la boîte
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
        self.image_canvas.delete("all")
        self.image_canvas.create_image(canvas_width//2, canvas_height//2, 
                                      image=image_tk, anchor=tk.CENTER)
        
        # Garder une référence pour éviter le garbage collection
        self.image_canvas.image = image_tk
    
    def get_class_color(self, class_name):
        """Retourne une couleur BGR selon la classe"""
        color_map = {
            'person': (0, 255, 0),      # Vert
            'head': (0, 0, 255),        # Rouge
            'body': (255, 0, 0),        # Bleu
            'chest': (0, 255, 255),     # Jaune
            'box': (255, 0, 255),       # Magenta
            'bottle': (128, 0, 128),    # Violet
            'cup': (255, 165, 0),       # Orange
        }
        return color_map.get(class_name, (255, 255, 255))  # Blanc par défaut
    
    def configure_zones(self):
        """Configure les zones de détection"""
        zone_window = tk.Toplevel(self.root)
        zone_window.title("🎯 Configuration des Zones")
        zone_window.geometry("500x400")
        
        frame = ttk.Frame(zone_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="🎯 Zones de Détection", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Liste des zones
        zones_frame = ttk.Frame(frame)
        zones_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(zones_frame, text="Zones configurées:").pack(anchor='w')
        
        self.zones_listbox = tk.Listbox(zones_frame, height=10)
        self.zones_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Boutons pour les zones
        zones_buttons = ttk.Frame(frame)
        zones_buttons.pack(fill=tk.X, pady=10)
        
        ttk.Button(zones_buttons, text="➕ Ajouter Zone", 
                  command=self.add_detection_zone).pack(side=tk.LEFT, padx=5)
        ttk.Button(zones_buttons, text="🗑️ Supprimer", 
                  command=self.remove_detection_zone).pack(side=tk.LEFT, padx=5)
        
        # Instructions
        instructions = """
Instructions:
• Cliquez 'Ajouter Zone' pour définir une zone rectangulaire
• Utilisez la souris pour sélectionner la zone sur l'écran
• Les détections se feront uniquement dans ces zones
• Utile pour surveiller des zones spécifiques (coffres, ennemis, etc.)
        """
        
        ttk.Label(frame, text=instructions, justify='left').pack(pady=10)
        
        self.refresh_zones_list()
    
    def add_detection_zone(self):
        """Ajoute une zone de détection"""
        if not self.zone_manager:
            messagebox.showerror("Erreur", "Gestionnaire de zones non initialisé!")
            return
        
        # Utiliser le nouveau système de sélection interactive
        self.zone_manager.add_zone_interactive()
        
        # Mettre à jour la liste après sélection
        self.root.after(1000, self.sync_zones_from_manager)
    
    def remove_detection_zone(self):
        """Supprime une zone de détection"""
        selection = self.zones_listbox.curselection()
        if selection:
            index = selection[0]
            zone = self.detection_zones.pop(index)
            self.refresh_zones_list()
            self.log_message(f"🗑️ Zone supprimée: {zone['name']}")
    
    def sync_zones_from_manager(self):
        """Synchronise les zones depuis le gestionnaire"""
        if self.zone_manager:
            self.detection_zones = self.zone_manager.get_zones()
            self.refresh_zones_list()
    
    def refresh_zones_list(self):
        """Actualise la liste des zones"""
        if hasattr(self, 'zones_listbox'):
            self.zones_listbox.delete(0, tk.END)
            for zone in self.detection_zones:
                classes = zone.get('classes', [])
                self.zones_listbox.insert(tk.END, 
                    f"{zone['name']} - Classes: {', '.join(classes)}")
    
    def configure_actions(self):
        """Configure les actions à déclencher"""
        actions_window = tk.Toplevel(self.root)
        actions_window.title("⚡ Configuration des Actions")
        actions_window.geometry("600x500")
        
        frame = ttk.Frame(actions_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="⚡ Actions Automatiques", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Configuration des actions par classe
        config_frame = ttk.LabelFrame(frame, text="Actions par Classe d'Objet", padding=10)
        config_frame.pack(fill=tk.X, pady=10)
        
        # Exemples d'actions
        actions_examples = [
            ("🎯 Viser la tête", "person", "click_center"),
            ("📦 Ouvrir coffre", "box", "double_click"),
            ("🔫 Tirer", "head", "left_click"),
            ("🏃 Éviter", "enemy", "move_away"),
            ("💎 Collecter", "item", "right_click")
        ]
        
        for i, (desc, class_name, action) in enumerate(actions_examples):
            action_frame = ttk.Frame(config_frame)
            action_frame.pack(fill=tk.X, pady=2)
            
            var = tk.BooleanVar()
            ttk.Checkbutton(action_frame, text=desc, variable=var).pack(side=tk.LEFT)
            
            ttk.Label(action_frame, text=f"Classe: {class_name}").pack(side=tk.LEFT, padx=20)
            ttk.Label(action_frame, text=f"Action: {action}").pack(side=tk.LEFT, padx=20)
        
        # Configuration des délais
        timing_frame = ttk.LabelFrame(frame, text="Timing et Délais", padding=10)
        timing_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(timing_frame, text="Délai avant action (ms):").pack(side=tk.LEFT)
        self.action_delay = tk.IntVar(value=100)
        ttk.Scale(timing_frame, from_=0, to=1000, variable=self.action_delay, 
                 orient='horizontal').pack(side=tk.LEFT, padx=10)
        
        delay_label = ttk.Label(timing_frame, text="100ms")
        delay_label.pack(side=tk.LEFT)
        
        def update_delay(*args):
            delay_label.configure(text=f"{self.action_delay.get()}ms")
        self.action_delay.trace('w', update_delay)
        
        # Boutons
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(buttons_frame, text="💾 Sauvegarder Configuration", 
                  command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="📂 Charger Configuration", 
                  command=self.load_config).pack(side=tk.LEFT, padx=5)
        
        # Instructions
        instructions = """
Instructions pour Actions Automatiques:
• Sélectionnez les actions à déclencher pour chaque classe d'objet
• Ajustez les délais selon vos besoins
• 'Viser la tête' : Déplace la souris vers le centre de l'objet détecté
• 'Ouvrir coffre' : Double-clic sur l'objet
• 'Tirer' : Clic gauche à la position de l'objet
• 'Éviter' : Déplace la souris loin de l'objet
• 'Collecter' : Clic droit sur l'objet

⚠️ Attention: Les actions automatiques peuvent affecter votre jeu!
        """
        
        ttk.Label(frame, text=instructions, justify='left').pack(pady=10)
    
    def toggle_detection(self):
        """Active/désactive la détection continue"""
        if not self.is_running:
            self.start_detection()
        else:
            self.stop_detection()
    
    def start_detection(self):
        """Démarre la détection continue"""
        if not self.model:
            messagebox.showerror("Erreur", "Modèle YOLO non chargé!")
            return
        
        self.is_running = True
        self.start_time = time.time()
        self.main_start_btn.configure(text="⏹️ ARRÊTER", bg=self.colors['danger'])
        self.status_text.set("🟢 Détection Active")
        
        self.detection_thread = threading.Thread(target=self.detection_loop)
        self.detection_thread.daemon = True
        self.detection_thread.start()
        
        self.log_message("🚀 Détection continue démarrée")
    
    def stop_detection(self):
        """Arrête la détection continue"""
        self.is_running = False
        self.main_start_btn.configure(text="🎯 DÉMARRER LA DÉTECTION", bg=self.colors['success'])
        self.status_text.set("🔴 Arrêté")
        
        self.log_message("⏹️ Détection arrêtée")
    
    def detection_loop(self):
        """Boucle de détection continue"""
        while self.is_running:
            try:
                # Capture et détection
                screenshot = pyautogui.screenshot()
                screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                results = self.model(screenshot, conf=self.confidence_var.get(), verbose=False)
                
                detections = []
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            class_id = int(box.cls[0])
                            class_name = self.model.names[class_id]
                            confidence = float(box.conf[0])
                            bbox = box.xyxy[0].tolist()
                            
                            # Filtrer par classes ciblées
                            target_list = [cls.strip() for cls in self.target_classes.get().split(',') if cls.strip()]
                            if not target_list or class_name in target_list:
                                detections.append({
                                    'class_name': class_name,
                                    'confidence': confidence,
                                    'bbox': bbox,
                                    'center': [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]
                                })
                
                if detections:
                    self.total_detections += len(detections)
                    self.root.after(0, self.update_display, screenshot, detections)
                    
                    # Exécuter les actions configurées
                    self.execute_actions(detections)
                
                time.sleep(0.1)  # 10 FPS
                
            except Exception as e:
                if self.is_running:
                    self.log_message(f"❌ Erreur: {e}")
                time.sleep(1)
    
    def update_display(self, screenshot, detections):
        """Met à jour l'affichage (thread-safe)"""
        self.current_detections = detections
        self.display_detections(screenshot, detections)
        self.detections_count.set(str(self.total_detections))
    
    def execute_actions(self, detections):
        """Exécute les actions configurées pour les détections"""
        for detection in detections:
            class_name = detection['class_name']
            
            # Vérifier si une action est configurée pour cette classe
            if class_name in self.detection_actions:
                action = self.detection_actions[class_name]
                center_x, center_y = detection['center']
                
                # Délai avant action
                if hasattr(self, 'action_delay'):
                    time.sleep(self.action_delay.get() / 1000.0)
                
                # Exécuter l'action
                try:
                    if action == 'click_center':
                        pyautogui.click(center_x, center_y)
                        self.log_message(f"🎯 Clic sur {class_name} à ({center_x:.0f}, {center_y:.0f})")
                    elif action == 'double_click':
                        pyautogui.doubleClick(center_x, center_y)
                        self.log_message(f"📦 Double-clic sur {class_name}")
                    elif action == 'right_click':
                        pyautogui.rightClick(center_x, center_y)
                        self.log_message(f"💎 Clic droit sur {class_name}")
                    elif action == 'move_away':
                        # Déplacer la souris dans la direction opposée
                        current_x, current_y = pyautogui.position()
                        away_x = current_x + (current_x - center_x)
                        away_y = current_y + (current_y - center_y)
                        pyautogui.moveTo(away_x, away_y)
                        self.log_message(f"🏃 Évité {class_name}")
                        
                except Exception as e:
                    self.log_message(f"❌ Erreur action: {e}")
    
    def save_config(self):
        """Sauvegarde la configuration"""
        config = {
            'detection_zones': self.detection_zones,
            'detection_actions': self.detection_actions,
            'confidence_threshold': self.confidence_var.get(),
            'target_classes': self.target_classes.get(),
            'action_delay': getattr(self, 'action_delay', tk.IntVar(value=100)).get()
        }
        
        try:
            with open('aiming_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            self.log_message("💾 Configuration sauvegardée")
            messagebox.showinfo("Sauvegarde", "Configuration sauvegardée!")
        except Exception as e:
            self.log_message(f"❌ Erreur sauvegarde: {e}")
    
    def load_config(self):
        """Charge la configuration"""
        try:
            if os.path.exists('aiming_config.json'):
                with open('aiming_config.json', 'r') as f:
                    config = json.load(f)
                
                self.detection_zones = config.get('detection_zones', [])
                self.detection_actions = config.get('detection_actions', {})
                self.confidence_var.set(config.get('confidence_threshold', 0.5))
                self.target_classes.set(config.get('target_classes', "person,head,body,chest,box"))
                
                if hasattr(self, 'action_delay'):
                    self.action_delay.set(config.get('action_delay', 100))
                
                self.log_message("📂 Configuration chargée")
            else:
                self.log_message("⚠️ Aucune configuration trouvée")
                
        except Exception as e:
            self.log_message(f"❌ Erreur chargement: {e}")
    
    def update_confidence_display(self, *args):
        """Met à jour l'affichage de confiance"""
        value = self.confidence_var.get()
        percentage = int(value * 100)
        self.confidence_label.configure(text=f"{percentage}%")
    
    def select_target(self):
        """Sélectionne la cible de détection (écran/fenêtre)"""
        if not self.target_selector:
            messagebox.showerror("Erreur", "Sélecteur de cible non initialisé!")
            return
        
        # Afficher le sélecteur de cible
        self.target_selector.show_target_selector(parent=self.root)
        
        # Mettre à jour la cible après sélection
        self.root.after(1000, self.update_current_target)
    
    def update_current_target(self):
        """Met à jour la cible actuelle"""
        if self.target_selector:
            self.current_target = self.target_selector.get_current_target()
            if self.current_target:
                target_name = self.current_target.get('name', 'Cible inconnue')
                self.log_message(f"🎯 Cible sélectionnée: {target_name}")
                
                # Mettre à jour le titre de la vue
                if hasattr(self, 'left_panel'):
                    # Trouver le LabelFrame et mettre à jour son texte
                    for child in self.root.winfo_children():
                        if isinstance(child, ttk.Frame):
                            for subchild in child.winfo_children():
                                if isinstance(subchild, ttk.LabelFrame) and "Vue en Temps Réel" in str(subchild.cget('text')):
                                    subchild.configure(text=f"🖥️ Vue: {target_name}")
                                    break
    
    def log_message(self, message):
        """Ajoute un message au log"""
        def update_ui():
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)
            
            # Limiter le nombre de lignes
            lines = self.log_text.get("1.0", tk.END).count('\n')
            if lines > 100:
                self.log_text.delete("1.0", "20.0")
        
        if hasattr(self, 'log_text'):
            self.root.after(0, update_ui)
    
    def on_closing(self):
        """Gestionnaire de fermeture"""
        if self.is_running:
            if messagebox.askyesno("Confirmation", 
                                 "La détection est active. Voulez-vous vraiment quitter ?"):
                self.is_running = False
                self.save_config()
                self.root.destroy()
        else:
            self.save_config()
            self.root.destroy()
    
    def run(self):
        """Lance l'application"""
        self.root.mainloop()

# Point d'entrée
if __name__ == "__main__":
    try:
        app = InteractiveAimingSystem()
        app.run()
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
