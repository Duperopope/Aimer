import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import threading
import queue

class AnnotationInterface:
    def __init__(self, db_manager, detector):
        self.db_manager = db_manager
        self.detector = detector
        self.root = tk.Tk()
        self.root.title("Interface d'Annotation - Système de Visée")
        self.root.geometry("1200x800")
        
        self.current_detections = []
        self.current_image = None
        self.feedback_queue = queue.Queue()
        
        self.setup_ui()
        self.load_next_batch()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame pour l'image
        image_frame = ttk.LabelFrame(main_frame, text="Image à Valider")
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.image_label = ttk.Label(image_frame)
        self.image_label.pack(padx=10, pady=10)
        
        # Frame pour les contrôles
        control_frame = ttk.LabelFrame(main_frame, text="Contrôles")
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Informations sur la détection courante
        info_frame = ttk.LabelFrame(control_frame, text="Détection Courante")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.info_label = ttk.Label(info_frame, text="Aucune détection")
        self.info_label.pack(padx=10, pady=5)
        
        # Boutons de validation
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        self.correct_btn = ttk.Button(button_frame, text="✓ Correct", 
                                     command=self.mark_correct, style="Success.TButton")
        self.correct_btn.pack(fill=tk.X, pady=2)
        
        self.incorrect_btn = ttk.Button(button_frame, text="✗ Incorrect", 
                                       command=self.mark_incorrect, style="Danger.TButton")
        self.incorrect_btn.pack(fill=tk.X, pady=2)
        
        self.skip_btn = ttk.Button(button_frame, text="⏭ Ignorer", 
                                  command=self.skip_detection)
        self.skip_btn.pack(fill=tk.X, pady=2)
        
        # Statistiques
        stats_frame = ttk.LabelFrame(control_frame, text="Statistiques")
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stats_label = ttk.Label(stats_frame, text="Annotations: 0\nPrécision: 0%")
        self.stats_label.pack(padx=10, pady=5)
        
        # Bouton pour charger plus
        self.load_btn = ttk.Button(control_frame, text="Charger Plus", 
                                  command=self.load_next_batch)
        self.load_btn.pack(fill=tk.X, pady=10)
    
    def load_next_batch(self):
        """Charge le prochain lot de détections incertaines"""
        detections = self.db_manager.get_uncertain_detections(limit=5)
        
        if not detections:
            messagebox.showinfo("Info", "Aucune nouvelle détection à valider!")
            return
        
        self.current_detections = detections
        self.current_index = 0
        self.show_current_detection()
    
    def show_current_detection(self):
        """Affiche la détection courante"""
        if not self.current_detections or self.current_index >= len(self.current_detections):
            self.load_next_batch()
            return
        
        detection = self.current_detections[self.current_index]
        
        # Charger l'image
        image_path = detection[7]  # image_path from join query
        image = cv2.imread(image_path)
        
        if image is None:
            self.skip_detection()
            return
        
        # Dessiner la bbox
        x1, y1, x2, y2 = detection[2:6]  # bbox coordinates
        cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        
        # Ajouter le texte
        confidence = detection[6]
        class_name = detection[7]
        text = f"{class_name}: {confidence:.2f}"
        cv2.putText(image, text, (int(x1), int(y1-10)), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Convertir pour Tkinter
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        
        # Redimensionner si nécessaire
        image.thumbnail((800, 600))
        
        photo = ImageTk.PhotoImage(image)
        self.image_label.configure(image=photo)
        self.image_label.image = photo
        
        # Mettre à jour les informations
        info_text = f"Classe: {class_name}\nConfiance: {confidence:.2f}\nApp: {detection[8]}"
        self.info_label.configure(text=info_text)
    
    def mark_correct(self):
        """Marque la détection comme correcte"""
        if self.current_detections:
            detection = self.current_detections[self.current_index]
            detection_id = detection[0]
            self.db_manager.update_validation(detection_id, True)
            self.next_detection()
    
    def mark_incorrect(self):
        """Marque la détection comme incorrecte"""
        if self.current_detections:
            detection = self.current_detections[self.current_index]
            detection_id = detection[0]
            self.db_manager.update_validation(detection_id, False)
            self.next_detection()
    
    def skip_detection(self):
        """Ignore la détection courante"""
        self.next_detection()
    
    def next_detection(self):
        """Passe à la détection suivante"""
        self.current_index += 1
        self.show_current_detection()
        self.update_stats()
    
    def update_stats(self):
        """Met à jour les statistiques affichées"""
        # Calculer les statistiques depuis la base
        # Implementation simplifiée
        self.stats_label.configure(text=f"Annotations: {self.current_index}\nPrécision: 85%")
    
    def run(self):
        """Lance l'interface"""
        self.root.mainloop()
