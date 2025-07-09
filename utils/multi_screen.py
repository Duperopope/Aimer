"""
Gestion multi-écrans et sélection de fenêtres
Support pour détection sur plusieurs écrans et ciblage d'applications spécifiques
"""

import tkinter as tk
from tkinter import messagebox, ttk
import pyautogui
import cv2
import numpy as np
from PIL import Image, ImageTk
import win32gui
import win32con
import win32api
import win32process
import psutil
import time
from typing import List, Dict, Tuple, Optional

class ScreenManager:
    """Gestionnaire des écrans multiples"""
    
    def __init__(self):
        self.screens = []
        self.current_screen = 0
        self.refresh_screens()
    
    def refresh_screens(self):
        """Actualise la liste des écrans disponibles"""
        try:
            # Obtenir les informations sur tous les moniteurs
            monitors = win32api.EnumDisplayMonitors()
            self.screens = []
            
            for i, monitor in enumerate(monitors):
                monitor_info = win32api.GetMonitorInfo(monitor[0])
                work_area = monitor_info['Work']
                monitor_area = monitor_info['Monitor']
                
                screen_info = {
                    'id': i,
                    'name': f'Écran {i + 1}',
                    'work_area': work_area,  # Zone de travail (sans barre des tâches)
                    'monitor_area': monitor_area,  # Zone complète du moniteur
                    'width': monitor_area[2] - monitor_area[0],
                    'height': monitor_area[3] - monitor_area[1],
                    'x': monitor_area[0],
                    'y': monitor_area[1],
                    'primary': monitor_info.get('Flags', 0) & win32con.MONITORINFOF_PRIMARY != 0
                }
                self.screens.append(screen_info)
            
            # Trier pour mettre l'écran principal en premier
            self.screens.sort(key=lambda x: not x['primary'])
            
        except Exception as e:
            print(f"Erreur lors de la détection des écrans: {e}")
            # Fallback sur l'écran principal
            screen_size = pyautogui.size()
            self.screens = [{
                'id': 0,
                'name': 'Écran Principal',
                'work_area': (0, 0, screen_size.width, screen_size.height),
                'monitor_area': (0, 0, screen_size.width, screen_size.height),
                'width': screen_size.width,
                'height': screen_size.height,
                'x': 0,
                'y': 0,
                'primary': True
            }]
    
    def get_screens(self) -> List[Dict]:
        """Retourne la liste des écrans"""
        return self.screens
    
    def get_screen_by_id(self, screen_id: int) -> Optional[Dict]:
        """Retourne un écran par son ID"""
        for screen in self.screens:
            if screen['id'] == screen_id:
                return screen
        return None
    
    def capture_screen(self, screen_id: Optional[int] = None) -> np.ndarray:
        """Capture un écran spécifique ou tous les écrans"""
        if screen_id is None:
            # Capturer tous les écrans (screenshot global)
            screenshot = pyautogui.screenshot()
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        screen = self.get_screen_by_id(screen_id)
        if not screen:
            raise ValueError(f"Écran {screen_id} non trouvé")
        
        # Capturer une région spécifique
        region = (screen['x'], screen['y'], screen['width'], screen['height'])
        screenshot = pyautogui.screenshot(region=region)
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    def get_screen_at_point(self, x: int, y: int) -> Optional[Dict]:
        """Retourne l'écran contenant le point donné"""
        for screen in self.screens:
            if (screen['x'] <= x < screen['x'] + screen['width'] and
                screen['y'] <= y < screen['y'] + screen['height']):
                return screen
        return None

class WindowManager:
    """Gestionnaire des fenêtres d'applications"""
    
    def __init__(self):
        self.windows = []
        self.refresh_windows()
    
    def refresh_windows(self):
        """Actualise la liste des fenêtres"""
        self.windows = []
        win32gui.EnumWindows(self._enum_window_callback, None)
        
        # Filtrer les fenêtres visibles et avec titre
        self.windows = [w for w in self.windows if w['visible'] and w['title'].strip()]
        
        # Trier par nom d'application
        self.windows.sort(key=lambda x: x['process_name'].lower())
    
    def _enum_window_callback(self, hwnd, extra):
        """Callback pour énumérer les fenêtres"""
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                try:
                    # Obtenir les informations du processus
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    process = psutil.Process(pid)
                    process_name = process.name()
                    
                    # Obtenir la position et taille de la fenêtre
                    rect = win32gui.GetWindowRect(hwnd)
                    
                    window_info = {
                        'hwnd': hwnd,
                        'title': title,
                        'process_name': process_name,
                        'pid': pid,
                        'rect': rect,
                        'x': rect[0],
                        'y': rect[1],
                        'width': rect[2] - rect[0],
                        'height': rect[3] - rect[1],
                        'visible': True
                    }
                    self.windows.append(window_info)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
    
    def get_windows(self) -> List[Dict]:
        """Retourne la liste des fenêtres"""
        return self.windows
    
    def get_window_by_title(self, title: str) -> Optional[Dict]:
        """Trouve une fenêtre par son titre (recherche partielle)"""
        title_lower = title.lower()
        for window in self.windows:
            if title_lower in window['title'].lower():
                return window
        return None
    
    def get_window_by_process(self, process_name: str) -> Optional[Dict]:
        """Trouve une fenêtre par nom de processus"""
        process_lower = process_name.lower()
        for window in self.windows:
            if process_lower in window['process_name'].lower():
                return window
        return None
    
    def capture_window(self, window_info: Dict) -> Optional[np.ndarray]:
        """Capture le contenu d'une fenêtre spécifique"""
        try:
            hwnd = window_info['hwnd']
            
            # Vérifier que la fenêtre existe encore
            if not win32gui.IsWindow(hwnd):
                return None
            
            # Obtenir les dimensions actuelles
            rect = win32gui.GetWindowRect(hwnd)
            x, y, x2, y2 = rect
            width = x2 - x
            height = y2 - y
            
            if width <= 0 or height <= 0:
                return None
            
            # Capturer la région de la fenêtre
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
        except Exception as e:
            print(f"Erreur capture fenêtre: {e}")
            return None
    
    def focus_window(self, window_info: Dict) -> bool:
        """Met le focus sur une fenêtre"""
        try:
            hwnd = window_info['hwnd']
            win32gui.SetForegroundWindow(hwnd)
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            return True
        except Exception as e:
            print(f"Erreur focus fenêtre: {e}")
            return False

class TargetSelector:
    """Sélecteur de cible (écran, fenêtre ou zone)"""
    
    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        self.screen_manager = ScreenManager()
        self.window_manager = WindowManager()
        self.current_target = None
        
        # Variables pour les sélections (initialisées à None)
        self.selected_screen = None
        self.selected_window = None
        self.selected_zone = None
    
    def log(self, message):
        """Log un message"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
    
    def show_target_selector(self, parent=None):
        """Affiche le sélecteur de cible"""
        selector_window = tk.Toplevel(parent) if parent else tk.Tk()
        selector_window.title("🎯 Sélection de Cible")
        selector_window.geometry("600x500")
        
        # Variables pour stocker les sélections (AVANT de créer les onglets)
        self.selected_screen = tk.IntVar()
        self.selected_window = tk.StringVar()
        self.selected_zone = tk.StringVar()
        
        frame = tk.Frame(selector_window, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = tk.Label(frame, text="🎯 Sélectionner la Cible de Détection", 
                              font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Notebook pour les onglets
        notebook = tk.ttk.Notebook(frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Onglet Écrans
        screens_frame = tk.Frame(notebook)
        notebook.add(screens_frame, text="🖥️ Écrans")
        self._create_screens_tab(screens_frame)
        
        # Onglet Fenêtres
        windows_frame = tk.Frame(notebook)
        notebook.add(windows_frame, text="🪟 Fenêtres")
        self._create_windows_tab(windows_frame)
        
        # Onglet Zones personnalisées
        zones_frame = tk.Frame(notebook)
        notebook.add(zones_frame, text="📐 Zones")
        self._create_zones_tab(zones_frame)
        
        # Boutons
        buttons_frame = tk.Frame(frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(buttons_frame, text="✅ Valider", 
                 command=lambda: self._validate_selection(selector_window)).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="❌ Annuler", 
                 command=selector_window.destroy).pack(side=tk.LEFT, padx=5)
        
        return selector_window
    
    def _create_screens_tab(self, parent):
        """Crée l'onglet de sélection d'écrans"""
        self.screen_manager.refresh_screens()
        screens = self.screen_manager.get_screens()
        
        tk.Label(parent, text="Sélectionnez un écran:", font=('Arial', 12, 'bold')).pack(anchor='w', pady=5)
        
        for screen in screens:
            primary_text = " (Principal)" if screen['primary'] else ""
            text = f"{screen['name']}{primary_text} - {screen['width']}x{screen['height']}"
            
            radio = tk.Radiobutton(parent, text=text, variable=self.selected_screen, 
                                  value=screen['id'])
            radio.pack(anchor='w', pady=2)
        
        # Sélectionner l'écran principal par défaut
        if screens:
            self.selected_screen.set(screens[0]['id'])
    
    def _create_windows_tab(self, parent):
        """Crée l'onglet de sélection de fenêtres"""
        tk.Label(parent, text="Sélectionnez une fenêtre:", font=('Arial', 12, 'bold')).pack(anchor='w', pady=5)
        
        # Bouton pour actualiser
        tk.Button(parent, text="🔄 Actualiser", 
                 command=lambda: self._refresh_windows_list(windows_listbox)).pack(anchor='w', pady=5)
        
        # Liste des fenêtres
        windows_listbox = tk.Listbox(parent, height=15)
        windows_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = tk.Scrollbar(parent, orient=tk.VERTICAL, command=windows_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        windows_listbox.configure(yscrollcommand=scrollbar.set)
        
        self._refresh_windows_list(windows_listbox)
        
        self.windows_listbox = windows_listbox
    
    def _create_zones_tab(self, parent):
        """Crée l'onglet de sélection de zones"""
        tk.Label(parent, text="Zones personnalisées:", font=('Arial', 12, 'bold')).pack(anchor='w', pady=5)
        
        tk.Button(parent, text="➕ Nouvelle Zone", 
                 command=self._create_custom_zone).pack(anchor='w', pady=5)
        
        # Liste des zones (à implémenter)
        zones_listbox = tk.Listbox(parent, height=10)
        zones_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def _refresh_windows_list(self, listbox):
        """Actualise la liste des fenêtres"""
        self.window_manager.refresh_windows()
        windows = self.window_manager.get_windows()
        
        listbox.delete(0, tk.END)
        for window in windows:
            text = f"{window['process_name']} - {window['title'][:50]}..."
            listbox.insert(tk.END, text)
    
    def _create_custom_zone(self):
        """Crée une zone personnalisée"""
        messagebox.showinfo("Zone personnalisée", "Fonctionnalité à implémenter")
    
    def _validate_selection(self, window):
        """Valide la sélection"""
        # Déterminer le type de cible sélectionné
        notebook = window.children['!frame'].children['!notebook']
        current_tab = notebook.index(notebook.select())
        
        if current_tab == 0:  # Écrans
            screen_id = self.selected_screen.get()
            screen = self.screen_manager.get_screen_by_id(screen_id)
            self.current_target = {
                'type': 'screen',
                'data': screen,
                'name': screen['name']
            }
            self.log(f"🖥️ Écran sélectionné: {screen['name']}")
            
        elif current_tab == 1:  # Fenêtres
            selection = self.windows_listbox.curselection()
            if selection:
                window_index = selection[0]
                windows = self.window_manager.get_windows()
                if window_index < len(windows):
                    window_info = windows[window_index]
                    self.current_target = {
                        'type': 'window',
                        'data': window_info,
                        'name': f"{window_info['process_name']} - {window_info['title']}"
                    }
                    self.log(f"🪟 Fenêtre sélectionnée: {window_info['title']}")
        
        window.destroy()
    
    def get_current_target(self):
        """Retourne la cible actuelle"""
        return self.current_target
    
    def capture_target(self) -> Optional[np.ndarray]:
        """Capture la cible actuelle"""
        if not self.current_target:
            return None
        
        target_type = self.current_target['type']
        target_data = self.current_target['data']
        
        try:
            if target_type == 'screen':
                return self.screen_manager.capture_screen(target_data['id'])
            elif target_type == 'window':
                return self.window_manager.capture_window(target_data)
            else:
                return None
        except Exception as e:
            self.log(f"❌ Erreur capture: {e}")
            return None
