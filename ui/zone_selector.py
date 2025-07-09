"""
Sélecteur de zones interactif pour le système de visée
Permet de sélectionner des zones rectangulaires sur l'écran
"""

import tkinter as tk
from tkinter import messagebox
import pyautogui
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw
import threading
import time

class ZoneSelector:
    def __init__(self, parent_callback=None):
        self.parent_callback = parent_callback
        self.selected_zone = None
        self.is_selecting = False
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        
    def select_zone(self):
        """Lance la sélection interactive d'une zone"""
        try:
            # Capturer l'écran complet
            screenshot = pyautogui.screenshot()
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Créer une fenêtre plein écran pour la sélection
            self.create_selection_window(screenshot_cv)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de capturer l'écran: {e}")
            return None
    
    def create_selection_window(self, screenshot):
        """Crée la fenêtre de sélection plein écran"""
        self.selection_window = tk.Toplevel()
        self.selection_window.title("Sélection de Zone - Cliquez et glissez")
        
        # Plein écran
        self.selection_window.attributes('-fullscreen', True)
        self.selection_window.attributes('-topmost', True)
        self.selection_window.configure(cursor='crosshair')
        
        # Convertir l'image pour Tkinter
        height, width = screenshot.shape[:2]
        screenshot_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
        screenshot_pil = Image.fromarray(screenshot_rgb)
        self.screenshot_tk = ImageTk.PhotoImage(screenshot_pil)
        
        # Canvas pour afficher l'image et dessiner la sélection
        self.canvas = tk.Canvas(self.selection_window, 
                               width=width, height=height,
                               highlightthickness=0)
        self.canvas.pack()
        
        # Afficher l'image de fond
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.screenshot_tk)
        
        # Instructions
        instructions = tk.Label(self.selection_window, 
                               text="🎯 Cliquez et glissez pour sélectionner une zone • Échap pour annuler • Entrée pour valider",
                               font=('Arial', 14, 'bold'),
                               bg='yellow', fg='black')
        instructions.place(x=10, y=10)
        
        # Bindings pour la sélection
        self.canvas.bind('<Button-1>', self.start_selection)
        self.canvas.bind('<B1-Motion>', self.update_selection)
        self.canvas.bind('<ButtonRelease-1>', self.end_selection)
        
        # Bindings clavier
        self.selection_window.bind('<Escape>', self.cancel_selection)
        self.selection_window.bind('<Return>', self.confirm_selection)
        self.selection_window.focus_set()
        
        # Variables pour le rectangle de sélection
        self.selection_rect = None
        self.selection_text = None
    
    def start_selection(self, event):
        """Commence la sélection"""
        self.is_selecting = True
        self.start_x = event.x
        self.start_y = event.y
        
        # Supprimer l'ancien rectangle s'il existe
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        if self.selection_text:
            self.canvas.delete(self.selection_text)
    
    def update_selection(self, event):
        """Met à jour la sélection pendant le glissement"""
        if not self.is_selecting:
            return
        
        self.end_x = event.x
        self.end_y = event.y
        
        # Supprimer l'ancien rectangle
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        if self.selection_text:
            self.canvas.delete(self.selection_text)
        
        # Dessiner le nouveau rectangle
        self.selection_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.end_x, self.end_y,
            outline='red', width=3, fill='red', stipple='gray25'
        )
        
        # Afficher les dimensions
        width = abs(self.end_x - self.start_x)
        height = abs(self.end_y - self.start_y)
        text = f"Zone: {width}x{height} px"
        
        text_x = min(self.start_x, self.end_x) + 5
        text_y = min(self.start_y, self.end_y) - 25
        
        self.selection_text = self.canvas.create_text(
            text_x, text_y, text=text,
            fill='red', font=('Arial', 12, 'bold'),
            anchor='nw'
        )
    
    def end_selection(self, event):
        """Termine la sélection"""
        self.is_selecting = False
        self.end_x = event.x
        self.end_y = event.y
        
        # Calculer les coordonnées finales (normalisées)
        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)
        
        # Vérifier que la zone n'est pas trop petite
        if (x2 - x1) < 20 or (y2 - y1) < 20:
            messagebox.showwarning("Zone trop petite", 
                                 "La zone sélectionnée est trop petite (minimum 20x20 pixels)")
            return
        
        self.selected_zone = {
            'coords': [x1, y1, x2, y2],
            'width': x2 - x1,
            'height': y2 - y1
        }
        
        # Mettre à jour l'affichage avec confirmation
        self.show_confirmation()
    
    def show_confirmation(self):
        """Affiche la confirmation de sélection"""
        if not self.selected_zone:
            return
        
        coords = self.selected_zone['coords']
        width = self.selected_zone['width']
        height = self.selected_zone['height']
        
        # Ajouter un texte de confirmation
        confirm_text = f"✅ Zone sélectionnée: {width}x{height} px\nAppuyez sur Entrée pour confirmer ou Échap pour annuler"
        
        # Supprimer l'ancien texte
        if self.selection_text:
            self.canvas.delete(self.selection_text)
        
        self.selection_text = self.canvas.create_text(
            coords[0] + 5, coords[1] - 50,
            text=confirm_text,
            fill='green', font=('Arial', 12, 'bold'),
            anchor='nw'
        )
    
    def confirm_selection(self, event=None):
        """Confirme la sélection"""
        if self.selected_zone:
            self.close_selection_window()
            if self.parent_callback:
                self.parent_callback(self.selected_zone)
        else:
            messagebox.showwarning("Aucune sélection", "Veuillez d'abord sélectionner une zone")
    
    def cancel_selection(self, event=None):
        """Annule la sélection"""
        self.selected_zone = None
        self.close_selection_window()
    
    def close_selection_window(self):
        """Ferme la fenêtre de sélection"""
        if hasattr(self, 'selection_window'):
            self.selection_window.destroy()

class ZoneManager:
    """Gestionnaire des zones de détection"""
    
    def __init__(self, log_callback=None):
        self.zones = []
        self.log_callback = log_callback
        self.zone_selector = ZoneSelector(self.on_zone_selected)
    
    def log(self, message):
        """Log un message"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
    
    def add_zone_interactive(self):
        """Ajoute une zone de manière interactive"""
        self.log("🎯 Démarrage de la sélection de zone...")
        self.zone_selector.select_zone()
    
    def on_zone_selected(self, zone_data):
        """Callback appelé quand une zone est sélectionnée"""
        if not zone_data:
            self.log("❌ Sélection de zone annulée")
            return
        
        # Demander le nom de la zone
        zone_name = self.get_zone_name()
        if not zone_name:
            return
        
        # Demander les classes à détecter
        target_classes = self.get_target_classes()
        if not target_classes:
            target_classes = ['person', 'head', 'body']
        
        # Créer la zone
        new_zone = {
            'name': zone_name,
            'coords': zone_data['coords'],
            'width': zone_data['width'],
            'height': zone_data['height'],
            'classes': target_classes,
            'active': True,
            'created_at': time.time()
        }
        
        self.zones.append(new_zone)
        self.log(f"✅ Zone '{zone_name}' ajoutée: {zone_data['width']}x{zone_data['height']} px")
        self.log(f"   Classes: {', '.join(target_classes)}")
        
        return new_zone
    
    def get_zone_name(self):
        """Demande le nom de la zone à l'utilisateur"""
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre principale
        
        name = tk.simpledialog.askstring(
            "Nom de la zone",
            f"Nom pour cette zone (Zone {len(self.zones) + 1}):",
            initialvalue=f"Zone {len(self.zones) + 1}"
        )
        
        root.destroy()
        return name
    
    def get_target_classes(self):
        """Demande les classes cibles à l'utilisateur"""
        root = tk.Tk()
        root.withdraw()
        
        classes_str = tk.simpledialog.askstring(
            "Classes à détecter",
            "Classes d'objets à détecter (séparées par des virgules):",
            initialvalue="person,head,body,chest"
        )
        
        root.destroy()
        
        if classes_str:
            return [cls.strip() for cls in classes_str.split(',') if cls.strip()]
        return None
    
    def remove_zone(self, index):
        """Supprime une zone par index"""
        if 0 <= index < len(self.zones):
            removed_zone = self.zones.pop(index)
            self.log(f"🗑️ Zone '{removed_zone['name']}' supprimée")
            return removed_zone
        return None
    
    def get_zones(self):
        """Retourne la liste des zones"""
        return self.zones
    
    def is_point_in_zone(self, x, y, zone):
        """Vérifie si un point est dans une zone"""
        coords = zone['coords']
        return coords[0] <= x <= coords[2] and coords[1] <= y <= coords[3]
    
    def filter_detections_by_zones(self, detections):
        """Filtre les détections selon les zones actives"""
        if not self.zones:
            return detections  # Pas de zones = toutes les détections
        
        filtered_detections = []
        
        for detection in detections:
            bbox = detection.get('bbox', [])
            if len(bbox) >= 4:
                # Centre de la détection
                center_x = (bbox[0] + bbox[2]) / 2
                center_y = (bbox[1] + bbox[3]) / 2
                
                # Vérifier si dans une zone active
                for zone in self.zones:
                    if zone.get('active', True):
                        if self.is_point_in_zone(center_x, center_y, zone):
                            # Vérifier si la classe est ciblée
                            if detection.get('class_name') in zone.get('classes', []):
                                filtered_detections.append(detection)
                                break
        
        return filtered_detections
    
    def save_zones(self, filename='zones_config.json'):
        """Sauvegarde les zones dans un fichier"""
        import json
        try:
            with open(filename, 'w') as f:
                json.dump(self.zones, f, indent=2)
            self.log(f"💾 Zones sauvegardées dans {filename}")
            return True
        except Exception as e:
            self.log(f"❌ Erreur sauvegarde: {e}")
            return False
    
    def load_zones(self, filename='zones_config.json'):
        """Charge les zones depuis un fichier"""
        import json
        import os
        
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    self.zones = json.load(f)
                self.log(f"📂 {len(self.zones)} zones chargées depuis {filename}")
                return True
            else:
                self.log(f"⚠️ Fichier {filename} non trouvé")
                return False
        except Exception as e:
            self.log(f"❌ Erreur chargement: {e}")
            return False

# Import pour simpledialog
import tkinter.simpledialog
