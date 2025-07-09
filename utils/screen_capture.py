import cv2
import numpy as np
from PIL import ImageGrab
import time
import threading
from typing import Optional, Tuple

class ScreenCapture:
    def __init__(self, region: Optional[Tuple[int, int, int, int]] = None):
        """
        Initialise la capture d'écran
        region: (x, y, width, height) ou None pour tout l'écran
        """
        self.region = region
        self.last_capture = None
        self.capture_lock = threading.Lock()
        
    def capture(self) -> Optional[np.ndarray]:
        """Capture l'écran et retourne une image OpenCV"""
        try:
            with self.capture_lock:
                # Utiliser PIL pour capturer l'écran
                if self.region:
                    x, y, w, h = self.region
                    screenshot = ImageGrab.grab(bbox=(x, y, x + w, y + h))
                else:
                    screenshot = ImageGrab.grab()
                
                # Convertir en format OpenCV
                screenshot = np.array(screenshot)
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
                
                self.last_capture = screenshot
                return screenshot
                
        except Exception as e:
            print(f"❌ Erreur lors de la capture: {e}")
            return None
    
    def set_region(self, region: Optional[Tuple[int, int, int, int]]):
        """Définit la région de capture"""
        self.region = region
        
    def get_screen_size(self) -> Tuple[int, int]:
        """Retourne la taille de l'écran"""
        try:
            screenshot = ImageGrab.grab()
            return screenshot.size
        except:
            return (1920, 1080)  # Valeur par défaut
    
    def capture_window(self, window_title: str) -> Optional[np.ndarray]:
        """Capture une fenêtre spécifique (placeholder)"""
        try:
            # Cette fonction nécessiterait pygetwindow
            # Pour l'instant, on retourne une capture d'écran complète
            return self.capture()
        except Exception as e:
            print(f"❌ Erreur lors de la capture de fenêtre: {e}")
            return None
