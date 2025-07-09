import tkinter as tk
from tkinter import ttk
import threading
import time
import cv2
from detection.yolo_detector import AdaptiveYOLODetector
from database.db_manager import DatabaseManager
from utils.screen_capture import ScreenCapture

class AimingOverlay:
    def __init__(self, target_app="*"):
        self.target_app = target_app
        self.detector = AdaptiveYOLODetector()
        self.db_manager = DatabaseManager()
        self.screen_capture = ScreenCapture()
        
        self.root = tk.Tk()
        self.setup_overlay()
        self.running = False
        self.detection_thread = None
        
    def setup_overlay(self):
        self.root.title("Aiming Overlay")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.8)
        self.root.configure(bg='black')
        
        # Rendre la fenêtre cliquable à travers
        self.root.wm_attributes('-transparentcolor', 'black')
        
        # Contrôles
        control_frame = tk.Frame(self.root, bg='gray20')
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.start_btn = tk.Button(control_frame, text="Démarrer", 
                                  command=self.toggle_detection, bg='green')
        self.start_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.status_label = tk.Label(control_frame, text="Arrêté", 
                                    bg='gray20', fg='white')
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Canvas pour dessiner les détections
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind pour fermer
        self.root.bind('<Escape>', lambda e: self.root.quit())
        
    def toggle_detection(self):
        if not self.running:
            self.start_detection()
        else:
            self.stop_detection()
    
    def start_detection(self):
        self.running = True
        self.start_btn.configure(text="Arrêter", bg='red')
        self.status_label.configure(text="Détection Active")
        
        self.detection_thread = threading.Thread(target=self.detection_loop)
        self.detection_thread.daemon = True
        self.detection_thread.start()
    
    def stop_detection(self):
        self.running = False
        self.start_btn.configure(text="Démarrer", bg='green')
        self.status_label.configure(text="Arrêté")
        
    def detection_loop(self):
        while self.running:
            try:
                # Capturer l'écran
                screenshot = self.screen_capture.capture()
                if screenshot is None:
                    time.sleep(0.1)
                    continue
                
                # Détecter les objets
                detections = self.detector.detect_objects(screenshot)
                
                # Sauvegarder en base
                screenshot_id = self.db_manager.save_screenshot(
                    self.target_app, 
                    f"screenshot_{int(time.time())}.jpg",
                    f"{screenshot.shape[1]}x{screenshot.shape[0]}"
                )
                
                # Sauvegarder les détections
                for detection in detections:
                    self.db_manager.save_detection(
                        screenshot_id,
                        detection['bbox'],
                        detection['confidence'],
                        detection['class_name']
                    )
                
                # Mettre à jour l'affichage
                self.root.after(0, self.update_overlay, detections)
                
                time.sleep(0.05)  # 20 FPS
                
            except Exception as e:
                print(f"Erreur dans la boucle de détection: {e}")
                time.sleep(0.1)
    
    def update_overlay(self, detections):
        # Effacer le canvas
        self.canvas.delete("all")
        
        # Dessiner les détections
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            confidence = detection['confidence']
            class_name = detection['class_name']
            
            # Couleur basée sur la confiance
            if confidence > 0.8:
                color = 'green'
            elif confidence > 0.5:
                color = 'yellow'
            else:
                color = 'red'
            
            # Dessiner la bbox
            self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2)
            
            # Ajouter le texte
            text = f"{class_name}: {confidence:.2f}"
            self.canvas.create_text(x1, y1-10, text=text, fill=color, anchor='nw')
    
    def run(self):
        self.root.mainloop()
