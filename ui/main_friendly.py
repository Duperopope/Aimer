# -*- coding: utf-8 -*-
"""
Système de Visée Intelligent - Interface avec Logging Complet
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import sys
import os
import time
import logging
from datetime import datetime
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent au path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Configuration pour éviter les erreurs d'importation
try:
    import cv2
    import numpy as np
    from ultralytics import YOLO
    import pyautogui
    from PIL import Image, ImageTk
    IMPORTS_OK = True
    logger.info("✅ Tous les modules importés avec succès")
except ImportError as e:
    IMPORTS_OK = False
    IMPORT_ERROR = str(e)
    logger.error(f"❌ Erreur d'importation: {e}")

class UserFriendlyAimingSystem:
    def __init__(self):
        logger.info("🚀 Initialisation du système de visée")
        
        # Variables d'état
        self.is_running = False
        self.detection_thread = None
        self.model = None
        self.total_detections = 0
        self.start_time = None
        
        # Configuration des couleurs
        self.colors = {
            'primary': '#007bff',
            'success': '#28a745',
            'warning': '#ffc107', 
            'danger': '#dc3545',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40'
        }
        
        # Interface principale
        self.root = tk.Tk()
        self.setup_main_window()
        self.create_interface()
        
        # Initialisation différée
        self.root.after(100, self.delayed_init)
        
        logger.info("✅ Interface initialisée")
    
    def setup_main_window(self):
        """Configure la fenêtre principale"""
        self.root.title("🎯 Système de Visée Intelligent - Version Debug")
        self.root.geometry("1000x800")
        self.root.configure(bg='#f8f9fa')
        
        # Centrer la fenêtre
        self.center_window()
        
        # Gestionnaire de fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        logger.info("🖥️ Fenêtre principale configurée")
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        logger.info(f"🖥️ Fenêtre centrée: {width}x{height} à position ({x}, {y})")
    
    def create_interface(self):
        """Crée l'interface utilisateur optimisée"""
        logger.info("🎨 Création de l'interface...")
        
        # Container principal SANS scrollbar pour éviter les problèmes
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sections organisées verticalement
        self.create_header(main_frame)
        self.create_control_panel(main_frame)
        self.create_status_display(main_frame)
        self.create_results_display(main_frame)
        
        logger.info("✅ Interface créée avec succès")
    
    def create_header(self, parent):
        """Crée l'en-tête compact"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Titre principal
        title_label = ttk.Label(header_frame, text="🎯 Système de Visée Intelligent", 
                               font=('Arial', 18, 'bold'))
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Version Debug avec Logging Complet", 
                                  font=('Arial', 10))
        subtitle_label.pack()
        
        logger.info("📋 En-tête créé")
    
    def create_control_panel(self, parent):
        """Crée le panneau de contrôle principal"""
        control_frame = ttk.LabelFrame(parent, text="🎮 Contrôles Principaux", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Ligne 1: Boutons d'action
        action_frame = ttk.Frame(control_frame)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.main_start_btn = tk.Button(action_frame, 
                                       text="🎯 DÉMARRER LA DÉTECTION", 
                                       font=('Arial', 12, 'bold'),
                                       bg=self.colors['success'], 
                                       fg='white',
                                       height=2,
                                       command=self.toggle_detection)
        self.main_start_btn.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        self.test_btn = tk.Button(action_frame, 
                                 text="🧪 TEST YOLO", 
                                 font=('Arial', 11),
                                 bg=self.colors['info'], 
                                 fg='white',
                                 height=2,
                                 command=self.test_yolo)
        self.test_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.log_btn = tk.Button(action_frame, 
                                text="📋 VOIR LOGS", 
                                font=('Arial', 11),
                                bg=self.colors['warning'], 
                                fg='white',
                                height=2,
                                command=self.show_logs)
        self.log_btn.pack(side=tk.LEFT)
        
        # Ligne 2: Paramètres
        settings_frame = ttk.Frame(control_frame)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Type de détection
        ttk.Label(settings_frame, text="Type de détection:", font=('Arial', 10)).pack(side=tk.LEFT)
        
        self.detection_type = tk.StringVar(value="Objets généraux")
        type_combo = ttk.Combobox(settings_frame, textvariable=self.detection_type, 
                                 values=["Objets généraux", "Personnes", "Véhicules", "Objets quotidiens"],
                                 state="readonly", width=20)
        type_combo.pack(side=tk.LEFT, padx=(10, 20))
        
        # Niveau de confiance
        ttk.Label(settings_frame, text="Confiance:", font=('Arial', 10)).pack(side=tk.LEFT)
        
        self.confidence_var = tk.DoubleVar(value=0.5)
        confidence_scale = ttk.Scale(settings_frame, from_=0.1, to=0.9, 
                                    variable=self.confidence_var, orient='horizontal',
                                    length=200)
        confidence_scale.pack(side=tk.LEFT, padx=(10, 10))
        
        self.confidence_label = ttk.Label(settings_frame, text="50%", font=('Arial', 10))
        self.confidence_label.pack(side=tk.LEFT)
        
        self.confidence_var.trace('w', self.update_confidence_display)
        
        logger.info("🎮 Panneau de contrôle créé")
    
    def create_status_display(self, parent):
        """Crée l'affichage de statut compact"""
        status_frame = ttk.LabelFrame(parent, text="📊 Statut en Temps Réel", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Statut principal
        self.status_text = tk.StringVar(value="🔴 Système arrêté - En attente")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_text, 
                                     font=('Arial', 12, 'bold'))
        self.status_label.pack(pady=(0, 5))
        
        # Métriques en ligne
        metrics_frame = ttk.Frame(status_frame)
        metrics_frame.pack(fill=tk.X)
        
        # Détections
        ttk.Label(metrics_frame, text="Détections:", font=('Arial', 10)).pack(side=tk.LEFT)
        self.detections_count = tk.StringVar(value="0")
        ttk.Label(metrics_frame, textvariable=self.detections_count, 
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(5, 20))
        
        # Temps actif
        ttk.Label(metrics_frame, text="Temps:", font=('Arial', 10)).pack(side=tk.LEFT)
        self.active_time = tk.StringVar(value="00:00")
        ttk.Label(metrics_frame, textvariable=self.active_time, 
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(5, 20))
        
        # Statut modèle
        ttk.Label(metrics_frame, text="Modèle:", font=('Arial', 10)).pack(side=tk.LEFT)
        self.model_status = tk.StringVar(value="⏳ Chargement...")
        ttk.Label(metrics_frame, textvariable=self.model_status, 
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(5, 0))
        
        logger.info("📊 Affichage de statut créé")
    
    def create_results_display(self, parent):
        """Crée l'affichage des résultats optimisé"""
        results_frame = ttk.LabelFrame(parent, text="📋 Journal des Détections", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Zone de texte avec scrollbar
        text_frame = ttk.Frame(results_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = tk.Text(text_frame, height=15, width=100, 
                                   bg='#ffffff', font=('Consolas', 9),
                                   wrap=tk.WORD)
        
        results_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, 
                                         command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Boutons d'action
        action_frame = ttk.Frame(results_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(action_frame, text="💾 Sauvegarder", 
                  command=self.save_results).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="🗑️ Effacer", 
                  command=self.clear_results).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="📤 Exporter Log", 
                  command=self.export_log).pack(side=tk.LEFT, padx=(0, 5))
        
        # Message initial
        self.log_message("🚀 Système de visée initialisé - Prêt à démarrer")
        self.log_message("📋 Cliquez sur 'DÉMARRER LA DÉTECTION' pour commencer")
        
        logger.info("📋 Zone de résultats créée")
    
    def delayed_init(self):
        """Initialisation différée avec logging détaillé"""
        logger.info("🔄 Début de l'initialisation différée")
        
        if not IMPORTS_OK:
            self.log_message("❌ ERREUR: Modules manquants!")
            self.log_message(f"Détails: {IMPORT_ERROR}")
            self.model_status.set("❌ Erreur")
            self.show_import_error()
            return
        
        try:
            self.log_message("🔄 Chargement du modèle YOLO...")
            self.model_status.set("⏳ Chargement...")
            
            # Chargement du modèle avec timeout
            self.model = YOLO('yolov8n.pt')
            
            self.log_message("✅ Modèle YOLO chargé avec succès!")
            self.log_message(f"📊 Classes disponibles: {len(self.model.names)}")
            
            # Afficher quelques classes disponibles
            sample_classes = list(self.model.names.values())[:10]
            self.log_message(f"🎯 Exemples de classes: {', '.join(sample_classes)}")
            
            self.status_text.set("✅ Système prêt - Cliquez sur 'DÉMARRER'")
            self.model_status.set("✅ Chargé")
            
            logger.info("✅ Initialisation terminée avec succès")
            
        except Exception as e:
            error_msg = f"❌ Erreur lors du chargement du modèle: {e}"
            self.log_message(error_msg)
            self.status_text.set("❌ Erreur d'initialisation")
            self.model_status.set("❌ Erreur")
            logger.error(error_msg)
    
    # === MÉTHODES DE CONTRÔLE ===
    
    def toggle_detection(self):
        """Active/désactive la détection avec logging"""
        if not self.is_running:
            self.start_detection()
        else:
            self.stop_detection()
    
    def start_detection(self):
        """Démarre la détection avec logging détaillé"""
        if not self.model:
            error_msg = "❌ Impossible de démarrer: Modèle YOLO non chargé"
            self.log_message(error_msg)
            messagebox.showerror("Erreur", error_msg)
            logger.error(error_msg)
            return
        
        self.log_message("🚀 Démarrage de la détection...")
        logger.info("🚀 Démarrage de la détection")
        
        self.is_running = True
        self.start_time = time.time()
        self.main_start_btn.configure(text="⏹️ ARRÊTER LA DÉTECTION", bg=self.colors['danger'])
        self.status_text.set("🟢 Détection ACTIVE - Surveillance en cours")
        
        # Démarrer le thread de détection
        self.detection_thread = threading.Thread(target=self.detection_loop)
        self.detection_thread.daemon = True
        self.detection_thread.start()
        
        # Démarrer le timer
        self.update_timer()
        
        self.log_message("✅ Détection démarrée avec succès!")
        self.log_message(f"⚙️ Seuil de confiance: {self.confidence_var.get():.1f}")
        self.log_message(f"🎯 Type de détection: {self.detection_type.get()}")
    
    def stop_detection(self):
        """Arrête la détection avec logging"""
        self.log_message("⏹️ Arrêt de la détection...")
        logger.info("⏹️ Arrêt de la détection")
        
        self.is_running = False
        self.main_start_btn.configure(text="🎯 DÉMARRER LA DÉTECTION", bg=self.colors['success'])
        self.status_text.set("🔴 Détection ARRÊTÉE - Prêt à redémarrer")
        
        # Statistiques finales
        if self.start_time:
            duration = time.time() - self.start_time
            self.log_message(f"📊 Session terminée: {duration:.1f}s, {self.total_detections} détections")
        
        self.log_message("✅ Détection arrêtée")
    
    def detection_loop(self):
        """Boucle de détection avec logging détaillé"""
        logger.info("🔄 Boucle de détection démarrée")
        detection_count = 0
        
        while self.is_running:
            try:
                # Capture d'écran
                screenshot = pyautogui.screenshot()
                screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                # Détection YOLO
                results = self.model(screenshot, conf=self.confidence_var.get(), verbose=False)
                
                detections = []
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            class_id = int(box.cls[0])
                            class_name = self.model.names[class_id]
                            confidence = float(box.conf[0])
                            
                            detections.append({
                                'class_name': class_name,
                                'confidence': confidence,
                                'bbox': box.xyxy[0].tolist()
                            })
                
                if detections:
                    detection_count += 1
                    self.total_detections += len(detections)
                    self.update_detection_display(detections)
                    
                    # Log détaillé toutes les 10 détections
                    if detection_count % 10 == 0:
                        logger.info(f"📊 {detection_count} cycles de détection, {self.total_detections} objets trouvés")
                
                time.sleep(0.2)  # 5 FPS
                
            except Exception as e:
                if self.is_running:
                    error_msg = f"❌ Erreur dans la boucle de détection: {e}"
                    self.log_message(error_msg)
                    logger.error(error_msg)
                time.sleep(1)
        
        logger.info("🔄 Boucle de détection terminée")
    
    def test_yolo(self):
        """Test complet du système YOLO"""
        self.log_message("🧪 === TEST YOLO DÉTAILLÉ ===")
        logger.info("🧪 Test YOLO démarré")
        
        if not self.model:
            self.log_message("❌ Test échoué: Modèle non chargé")
            return
        
        try:
            # Test 1: Informations du modèle
            self.log_message(f"📊 Modèle: {self.model.model}")
            self.log_message(f"📊 Classes disponibles: {len(self.model.names)}")
            
            # Test 2: Capture d'écran
            self.log_message("📷 Test de capture d'écran...")
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            self.log_message(f"✅ Capture réussie: {screenshot.shape}")
            
            # Test 3: Détection
            self.log_message("🎯 Test de détection...")
            results = self.model(screenshot, conf=0.3, verbose=False)
            
            detection_count = 0
            for result in results:
                if result.boxes is not None:
                    detection_count += len(result.boxes)
            
            self.log_message(f"🎯 Détections trouvées: {detection_count}")
            
            # Test 4: Performance
            start_time = time.time()
            for _ in range(3):
                self.model(screenshot, conf=0.5, verbose=False)
            avg_time = (time.time() - start_time) / 3
            
            self.log_message(f"⚡ Performance: {avg_time:.2f}s par détection")
            
            # Résultat final
            self.log_message("✅ === TEST YOLO RÉUSSI ===")
            messagebox.showinfo("Test YOLO", 
                              f"✅ Test réussi!\n\n"
                              f"• Modèle: Chargé\n"
                              f"• Capture: OK\n"
                              f"• Détections: {detection_count}\n"
                              f"• Performance: {avg_time:.2f}s")
            
            logger.info("✅ Test YOLO réussi")
            
        except Exception as e:
            error_msg = f"❌ Test échoué: {e}"
            self.log_message(error_msg)
            messagebox.showerror("Test YOLO", error_msg)
            logger.error(error_msg)
    
    # === MÉTHODES D'INTERFACE ===
    
    def update_confidence_display(self, *args):
        """Met à jour l'affichage de confiance"""
        value = self.confidence_var.get()
        percentage = int(value * 100)
        self.confidence_label.configure(text=f"{percentage}%")
    
    def update_detection_display(self, detections):
        """Met à jour l'affichage des détections"""
        def update_ui():
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Résumé des détections
            summary = {}
            for detection in detections:
                class_name = detection['class_name']
                if class_name in summary:
                    summary[class_name] += 1
                else:
                    summary[class_name] = 1
            
            # Affichage groupé
            self.results_text.insert(tk.END, f"[{timestamp}] 🔍 {len(detections)} détections:\n")
            
            for class_name, count in summary.items():
                if count > 1:
                    self.results_text.insert(tk.END, f"  • {class_name}: {count}x\n")
                else:
                    confidence = next(d['confidence'] for d in detections if d['class_name'] == class_name)
                    self.results_text.insert(tk.END, f"  • {class_name}: {confidence:.2f}\n")
            
            self.results_text.insert(tk.END, "\n")
            self.results_text.see(tk.END)
            
            # Mettre à jour les métriques
            self.detections_count.set(str(self.total_detections))
        
        self.root.after(0, update_ui)
    
    def update_timer(self):
        """Met à jour le timer"""
        if self.is_running and self.start_time:
            elapsed = int(time.time() - self.start_time)
            minutes, seconds = divmod(elapsed, 60)
            self.active_time.set(f"{minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_timer)
        else:
            self.active_time.set("00:00")
    
    def log_message(self, message):
        """Ajoute un message au log avec timestamp"""
        def update_ui():
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.results_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.results_text.see(tk.END)
            
            # Limiter le nombre de lignes
            lines = self.results_text.get("1.0", tk.END).count('\n')
            if lines > 500:
                self.results_text.delete("1.0", "50.0")
        
        self.root.after(0, update_ui)
    
    # === MÉTHODES DE FICHIERS ===
    
    def save_results(self):
        """Sauvegarde les résultats avec métadonnées"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Fichiers texte", "*.txt")],
                title="Sauvegarder les résultats"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("=== SYSTÈME DE VISÉE INTELLIGENT ===\n")
                    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Total détections: {self.total_detections}\n")
                    f.write(f"Seuil de confiance: {self.confidence_var.get():.2f}\n")
                    f.write(f"Type de détection: {self.detection_type.get()}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(self.results_text.get("1.0", tk.END))
                
                self.log_message(f"💾 Résultats sauvegardés: {filename}")
                messagebox.showinfo("Sauvegarde", "✅ Résultats sauvegardés!")
                
        except Exception as e:
            error_msg = f"❌ Erreur de sauvegarde: {e}"
            self.log_message(error_msg)
            messagebox.showerror("Erreur", error_msg)
    
    def clear_results(self):
        """Efface les résultats"""
        if messagebox.askyesno("Confirmation", "Effacer tous les résultats ?"):
            self.results_text.delete("1.0", tk.END)
            self.log_message("🗑️ Résultats effacés")
            self.log_message("🚀 Système prêt pour une nouvelle session")
    
    def export_log(self):
        """Exporte le log système"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("Fichiers log", "*.log"), ("Fichiers texte", "*.txt")],
                title="Exporter le log système"
            )
            
            if filename:
                # Copier le fichier de log
                with open('system.log', 'r', encoding='utf-8') as src:
                    with open(filename, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                
                self.log_message(f"📤 Log exporté: {filename}")
                messagebox.showinfo("Export", "✅ Log exporté!")
                
        except Exception as e:
            error_msg = f"❌ Erreur d'export: {e}"
            self.log_message(error_msg)
            messagebox.showerror("Erreur", error_msg)
    
    def show_logs(self):
        """Affiche les logs système dans une fenêtre"""
        try:
            log_window = tk.Toplevel(self.root)
            log_window.title("📋 Logs Système")
            log_window.geometry("800x600")
            
            log_text = tk.Text(log_window, wrap=tk.WORD, font=('Consolas', 9))
            log_scrollbar = ttk.Scrollbar(log_window, orient=tk.VERTICAL, command=log_text.yview)
            log_text.configure(yscrollcommand=log_scrollbar.set)
            
            # Charger le fichier de log
            if os.path.exists('system.log'):
                with open('system.log', 'r', encoding='utf-8') as f:
                    log_text.insert("1.0", f.read())
            else:
                log_text.insert("1.0", "Aucun fichier de log trouvé.")
            
            log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Bouton pour actualiser
            refresh_btn = ttk.Button(log_window, text="🔄 Actualiser", 
                                    command=lambda: self.refresh_logs(log_text))
            refresh_btn.pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"❌ Impossible d'afficher les logs: {e}")
    
    def refresh_logs(self, log_text):
        """Actualise les logs affichés"""
        try:
            log_text.delete("1.0", tk.END)
            if os.path.exists('system.log'):
                with open('system.log', 'r', encoding='utf-8') as f:
                    log_text.insert("1.0", f.read())
            log_text.see(tk.END)
        except Exception as e:
            log_text.insert(tk.END, f"\nErreur lors de l'actualisation: {e}")
    
    # === MÉTHODES D'AIDE ===
    
    def show_import_error(self):
        """Affiche l'erreur d'importation avec solution"""
        error_window = tk.Toplevel(self.root)
        error_window.title("❌ Erreur d'Installation")
        error_window.geometry("600x400")
        
        frame = ttk.Frame(error_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="❌ Dépendances Manquantes", 
                 font=('Arial', 16, 'bold')).pack(pady=10)
        
        error_text = f"""
Une ou plusieurs dépendances sont manquantes:

{IMPORT_ERROR}

Pour résoudre ce problème:

1. Ouvrez un terminal/PowerShell
2. Activez votre environnement virtuel:
   .venv\\Scripts\\Activate.ps1
3. Installez les dépendances:
   pip install ultralytics opencv-python pillow numpy pyautogui

4. Redémarrez l'application
"""
        
        ttk.Label(frame, text=error_text, justify='left').pack(pady=10)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="📋 Copier la commande", 
                  command=lambda: self.copy_to_clipboard("pip install ultralytics opencv-python pillow numpy pyautogui")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Fermer", 
                  command=error_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def copy_to_clipboard(self, text):
        """Copie du texte dans le presse-papiers"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Copié", "✅ Commande copiée dans le presse-papiers!")
        except Exception as e:
            messagebox.showerror("Erreur", f"❌ Erreur de copie: {e}")
    
    def on_closing(self):
        """Gestionnaire de fermeture avec confirmation"""
        if self.is_running:
            if messagebox.askyesno("Confirmation", 
                                 "🔄 La détection est encore active.\n"
                                 "Voulez-vous vraiment quitter?"):
                self.log_message("🔄 Fermeture forcée - Détection interrompue")
                self.is_running = False
                logger.info("🔄 Application fermée par l'utilisateur (détection active)")
                self.root.destroy()
        else:
            self.log_message("👋 Fermeture normale de l'application")
            logger.info("👋 Application fermée normalement")
            self.root.destroy()
    
    def run(self):
        """Lance l'application avec gestion d'erreurs"""
        try:
            logger.info("🎯 Démarrage de l'application principale")
            self.root.mainloop()
        except Exception as e:
            error_msg = f"❌ Erreur fatale dans l'application: {e}"
            logger.error(error_msg)
            messagebox.showerror("Erreur Fatale", error_msg)
        finally:
            logger.info("🔄 Nettoyage final de l'application")

# Point d'entrée principal
if __name__ == "__main__":
    try:
        logger.info("=" * 60)
        logger.info("🚀 DÉMARRAGE DU SYSTÈME DE VISÉE INTELLIGENT")
        logger.info("=" * 60)
        
        app = UserFriendlyAimingSystem()
        app.run()
        
        logger.info("👋 Application terminée normalement")
        
    except KeyboardInterrupt:
        logger.info("⚠️ Application interrompue par l'utilisateur (Ctrl+C)")
        print("\n👋 Application fermée par l'utilisateur")
        
    except Exception as e:
        error_msg = f"❌ Erreur fatale au démarrage: {e}"
        logger.error(error_msg)
        print(error_msg)
        import traceback
        traceback.print_exc()
        
    finally:
        logger.info("🔄 Nettoyage terminé")
