#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Launcher Principal
Application révolutionnaire de détection d'objets avec IA collaborative
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import threading
import time
import math
from pathlib import Path
from datetime import datetime
import json

# Ajouter le répertoire courant au path
sys.path.insert(0, str(Path(__file__).parent))

# Imports des composants
try:
    from ui.pro_dashboard import create_pro_dashboard
    from ui.ultimate_interface import UltimateInterface
    from core.hardware_profiler import create_hardware_profiler
    from core.progress_manager import create_progress_manager
    IMPORTS_OK = True
except ImportError as e:
    IMPORTS_OK = False
    IMPORT_ERROR = str(e)

class AimerProSplashScreen:
    """Écran de démarrage professionnel pour AIMER PRO"""
    
    def __init__(self):
        self.splash = tk.Toplevel()
        self.splash.title("AIMER PRO")
        self.splash.geometry("600x400")
        self.splash.configure(bg='#1a1a1a')
        self.splash.resizable(False, False)
        
        # Centrer l'écran
        self.center_window()
        
        # Supprimer les bordures
        self.splash.overrideredirect(True)
        
        # Interface de l'écran de démarrage
        self.create_splash_interface()
        
        # Variables de progression
        self.progress_value = 0
        self.status_text = "Initialisation..."
        
        # Démarrer l'animation
        self.animate_splash()
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.splash.update_idletasks()
        width = 600
        height = 400
        x = (self.splash.winfo_screenwidth() // 2) - (width // 2)
        y = (self.splash.winfo_screenheight() // 2) - (height // 2)
        self.splash.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_splash_interface(self):
        """Crée l'interface de l'écran de démarrage"""
        # Frame principal
        main_frame = tk.Frame(self.splash, bg='#1a1a1a')
        main_frame.pack(fill='both', expand=True)
        
        # Logo et titre
        logo_frame = tk.Frame(main_frame, bg='#1a1a1a')
        logo_frame.pack(expand=True, pady=50)
        
        # Titre principal
        title_label = tk.Label(
            logo_frame,
            text="🎯 AIMER PRO",
            font=('Segoe UI', 36, 'bold'),
            fg='#00ff88',
            bg='#1a1a1a'
        )
        title_label.pack(pady=10)
        
        # Sous-titre
        subtitle_label = tk.Label(
            logo_frame,
            text="Intelligence Artificielle • Détection d'Objets • Collaboration Mondiale",
            font=('Segoe UI', 12),
            fg='#cccccc',
            bg='#1a1a1a'
        )
        subtitle_label.pack(pady=5)
        
        # Version
        version_label = tk.Label(
            logo_frame,
            text="Version 2.0 Professional Edition",
            font=('Segoe UI', 10),
            fg='#666666',
            bg='#1a1a1a'
        )
        version_label.pack(pady=5)
        
        # Barre de progression
        progress_frame = tk.Frame(main_frame, bg='#1a1a1a')
        progress_frame.pack(side='bottom', fill='x', padx=50, pady=30)
        
        # Canvas pour la barre de progression personnalisée
        self.progress_canvas = tk.Canvas(
            progress_frame,
            width=500,
            height=20,
            bg='#2a2a2a',
            highlightthickness=0
        )
        self.progress_canvas.pack(pady=10)
        
        # Éléments de la barre de progression
        self.progress_bg = self.progress_canvas.create_rectangle(
            0, 0, 500, 20,
            fill='#2a2a2a',
            outline='#404040',
            width=1
        )
        
        self.progress_bar = self.progress_canvas.create_rectangle(
            0, 0, 0, 20,
            fill='#00ff88',
            outline='',
            width=0
        )
        
        # Texte de statut
        self.status_label = tk.Label(
            progress_frame,
            text="Initialisation...",
            font=('Segoe UI', 10),
            fg='#cccccc',
            bg='#1a1a1a'
        )
        self.status_label.pack()
        
        # Copyright
        copyright_label = tk.Label(
            main_frame,
            text="© 2025 AIMER PRO - Révolutionnez votre workflow IA",
            font=('Segoe UI', 8),
            fg='#666666',
            bg='#1a1a1a'
        )
        copyright_label.pack(side='bottom', pady=10)
    
    def update_progress(self, value: float, status: str):
        """Met à jour la progression"""
        self.progress_value = max(0, min(100, value))
        self.status_text = status
        
        # Mettre à jour la barre
        bar_width = (500 * self.progress_value) / 100
        self.progress_canvas.coords(self.progress_bar, 0, 0, bar_width, 20)
        
        # Couleur dynamique
        if self.progress_value < 30:
            color = '#ff6b6b'  # Rouge
        elif self.progress_value < 70:
            color = '#ffd93d'  # Jaune
        else:
            color = '#00ff88'  # Vert
        
        self.progress_canvas.itemconfig(self.progress_bar, fill=color)
        
        # Mettre à jour le texte
        self.status_label.config(text=f"{status} ({self.progress_value:.0f}%)")
        
        # Forcer la mise à jour
        self.splash.update()
    
    def animate_splash(self):
        """Animation de l'écran de démarrage"""
        # Animation de pulsation du titre
        try:
            current_time = time.time()
            alpha = (1 + math.sin(current_time * 3)) / 2  # Oscillation entre 0 et 1
            
            # Programmer la prochaine animation
            self.splash.after(50, self.animate_splash)
        except:
            pass
    
    def close(self):
        """Ferme l'écran de démarrage"""
        try:
            self.splash.destroy()
        except:
            pass

class AimerProLauncher:
    """Launcher principal d'AIMER PRO"""
    
    def __init__(self):
        # Variables d'état
        self.splash_screen = None
        self.main_window = None
        self.dashboard = None
        self.hardware_profiler = None
        self.progress_manager = None
        
        # Configuration
        self.config = {
            'theme': 'dark',
            'language': 'fr',
            'auto_start_monitoring': True,
            'show_splash': True
        }
        
        # Charger la configuration
        self.load_config()
        
        # Démarrer l'application
        self.start_application()
    
    def load_config(self):
        """Charge la configuration"""
        try:
            config_file = Path("aimer_pro_config.json")
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
        except Exception as e:
            print(f"Erreur chargement config: {e}")
    
    def save_config(self):
        """Sauvegarde la configuration"""
        try:
            with open("aimer_pro_config.json", 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur sauvegarde config: {e}")
    
    def start_application(self):
        """Démarre l'application"""
        # Créer la fenêtre principale cachée
        self.main_window = tk.Tk()
        self.main_window.withdraw()  # Cacher temporairement
        
        # Vérifier les imports
        if not IMPORTS_OK:
            self.show_error_dialog(
                "Erreur de Modules",
                f"Impossible de charger les modules requis:\n{IMPORT_ERROR}\n\n"
                "Veuillez vérifier l'installation des dépendances."
            )
            return
        
        # Afficher l'écran de démarrage si configuré
        if self.config.get('show_splash', True):
            self.splash_screen = AimerProSplashScreen()
            
            # Démarrer l'initialisation en arrière-plan
            threading.Thread(target=self.initialize_application, daemon=True).start()
        else:
            # Initialisation directe
            self.initialize_application()
    
    def initialize_application(self):
        """Initialise tous les composants de l'application"""
        try:
            steps = [
                ("Vérification du système...", self.check_system),
                ("Initialisation du profiler hardware...", self.init_hardware_profiler),
                ("Initialisation du gestionnaire de progression...", self.init_progress_manager),
                ("Création de l'interface principale...", self.create_main_interface),
                ("Initialisation du dashboard...", self.init_dashboard),
                ("Configuration finale...", self.finalize_setup)
            ]
            
            total_steps = len(steps)
            
            for i, (status, func) in enumerate(steps):
                if self.splash_screen:
                    progress = (i / total_steps) * 100
                    self.splash_screen.update_progress(progress, status)
                
                # Exécuter l'étape
                func()
                
                # Petite pause pour l'effet visuel
                time.sleep(0.5)
            
            # Finalisation
            if self.splash_screen:
                self.splash_screen.update_progress(100, "Démarrage terminé!")
                time.sleep(1)
            
            # Afficher l'interface principale
            self.show_main_interface()
            
        except Exception as e:
            self.handle_initialization_error(e)
    
    def check_system(self):
        """Vérifie la compatibilité du système"""
        import platform
        import sys
        
        # Vérifier Python
        if sys.version_info < (3, 8):
            raise Exception("Python 3.8+ requis")
        
        # Vérifier l'OS
        if platform.system() not in ['Windows', 'Linux', 'Darwin']:
            raise Exception("Système d'exploitation non supporté")
        
        # Vérifier les dépendances critiques
        try:
            import tkinter
            import threading
            import json
        except ImportError as e:
            raise Exception(f"Dépendance manquante: {e}")
    
    def init_hardware_profiler(self):
        """Initialise le profiler hardware"""
        self.hardware_profiler = create_hardware_profiler()
        
        # Test rapide
        profile = self.hardware_profiler.get_system_profile()
        if not profile:
            raise Exception("Impossible de profiler le système")
    
    def init_progress_manager(self):
        """Initialise le gestionnaire de progression"""
        self.progress_manager = create_progress_manager()
    
    def create_main_interface(self):
        """Crée l'interface principale"""
        # Configuration de la fenêtre principale
        self.main_window.title("🎯 AIMER PRO - Intelligence Artificielle Collaborative")
        self.main_window.geometry("1400x900")
        self.main_window.configure(bg='#2b2b2b')
        
        # Centrer la fenêtre
        self.center_main_window()
        
        # Gestionnaire de fermeture
        self.main_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Créer le notebook principal
        self.create_main_notebook()
    
    def create_main_notebook(self):
        """Crée le notebook principal avec tous les onglets"""
        # Style pour le notebook
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configuration du style sombre
        style.configure('TNotebook', background='#2b2b2b', borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background='#404040', 
                       foreground='white',
                       padding=[20, 10],
                       focuscolor='none')
        style.map('TNotebook.Tab',
                 background=[('selected', '#00ff88'), ('active', '#505050')],
                 foreground=[('selected', 'black'), ('active', 'white')])
        
        # Notebook principal
        self.main_notebook = ttk.Notebook(self.main_window)
        self.main_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Onglet 1: Dashboard Système
        self.dashboard_frame = tk.Frame(self.main_notebook, bg='#2b2b2b')
        self.main_notebook.add(self.dashboard_frame, text="🖥️ Dashboard Système")
        
        # Onglet 2: Interface Ultime (existante)
        self.ultimate_frame = tk.Frame(self.main_notebook, bg='#2b2b2b')
        self.main_notebook.add(self.ultimate_frame, text="🚀 Interface Ultime")
        
        # Onglet 3: Configuration
        self.config_frame = tk.Frame(self.main_notebook, bg='#2b2b2b')
        self.main_notebook.add(self.config_frame, text="⚙️ Configuration")
        
        # Créer l'interface de configuration
        self.create_config_interface()
    
    def init_dashboard(self):
        """Initialise le dashboard professionnel"""
        self.dashboard = create_pro_dashboard(self.dashboard_frame)
    
    def create_config_interface(self):
        """Crée l'interface de configuration"""
        # Titre
        title_label = tk.Label(
            self.config_frame,
            text="⚙️ Configuration AIMER PRO",
            font=('Segoe UI', 18, 'bold'),
            fg='white',
            bg='#2b2b2b'
        )
        title_label.pack(pady=20)
        
        # Frame des options
        options_frame = tk.LabelFrame(
            self.config_frame,
            text="Options Générales",
            bg='#3a3a3a',
            fg='white',
            font=('Segoe UI', 12, 'bold')
        )
        options_frame.pack(fill='x', padx=20, pady=10)
        
        # Options
        self.show_splash_var = tk.BooleanVar(value=self.config.get('show_splash', True))
        splash_check = tk.Checkbutton(
            options_frame,
            text="Afficher l'écran de démarrage",
            variable=self.show_splash_var,
            bg='#3a3a3a',
            fg='white',
            selectcolor='#404040',
            font=('Segoe UI', 10)
        )
        splash_check.pack(anchor='w', padx=10, pady=5)
        
        self.auto_monitoring_var = tk.BooleanVar(value=self.config.get('auto_start_monitoring', True))
        monitoring_check = tk.Checkbutton(
            options_frame,
            text="Démarrer le monitoring automatiquement",
            variable=self.auto_monitoring_var,
            bg='#3a3a3a',
            fg='white',
            selectcolor='#404040',
            font=('Segoe UI', 10)
        )
        monitoring_check.pack(anchor='w', padx=10, pady=5)
        
        # Boutons
        buttons_frame = tk.Frame(self.config_frame, bg='#2b2b2b')
        buttons_frame.pack(pady=20)
        
        save_btn = tk.Button(
            buttons_frame,
            text="💾 Sauvegarder",
            font=('Segoe UI', 11, 'bold'),
            bg='#00ff88',
            fg='black',
            command=self.save_configuration,
            padx=20,
            pady=10
        )
        save_btn.pack(side='left', padx=10)
        
        reset_btn = tk.Button(
            buttons_frame,
            text="🔄 Réinitialiser",
            font=('Segoe UI', 11, 'bold'),
            bg='#ff6b6b',
            fg='white',
            command=self.reset_configuration,
            padx=20,
            pady=10
        )
        reset_btn.pack(side='left', padx=10)
    
    def finalize_setup(self):
        """Finalise la configuration"""
        # Créer une interface simplifiée pour l'onglet ultime
        self.create_ultimate_tab_content()
    
    def create_ultimate_tab_content(self):
        """Crée le contenu de l'onglet interface ultime"""
        # Titre
        title_label = tk.Label(
            self.ultimate_frame,
            text="🚀 Interface Ultime YOLO",
            font=('Segoe UI', 18, 'bold'),
            fg='white',
            bg='#2b2b2b'
        )
        title_label.pack(pady=20)
        
        # Description
        desc_label = tk.Label(
            self.ultimate_frame,
            text="Interface complète de détection d'objets avec apprentissage collaboratif",
            font=('Segoe UI', 12),
            fg='#cccccc',
            bg='#2b2b2b'
        )
        desc_label.pack(pady=10)
        
        # Boutons d'actions principales
        actions_frame = tk.Frame(self.ultimate_frame, bg='#2b2b2b')
        actions_frame.pack(pady=30)
        
        # Bouton pour lancer l'interface ultime dans une nouvelle fenêtre
        launch_btn = tk.Button(
            actions_frame,
            text="🚀 Lancer Interface Ultime",
            font=('Segoe UI', 14, 'bold'),
            bg='#00ff88',
            fg='black',
            command=self.launch_ultimate_interface,
            padx=30,
            pady=15
        )
        launch_btn.pack(pady=10)
        
        # Bouton pour l'interface de datasets
        datasets_btn = tk.Button(
            actions_frame,
            text="📚 Gestionnaire de Datasets",
            font=('Segoe UI', 12, 'bold'),
            bg='#6bb6ff',
            fg='white',
            command=self.launch_dataset_manager,
            padx=25,
            pady=10
        )
        datasets_btn.pack(pady=5)
        
        # Bouton pour l'interface moderne
        modern_btn = tk.Button(
            actions_frame,
            text="🎨 Interface Moderne",
            font=('Segoe UI', 12, 'bold'),
            bg='#9d4edd',
            fg='white',
            command=self.launch_modern_interface,
            padx=25,
            pady=10
        )
        modern_btn.pack(pady=5)
        
        # Informations sur les fonctionnalités
        features_frame = tk.LabelFrame(
            self.ultimate_frame,
            text="🎯 Fonctionnalités Disponibles",
            bg='#3a3a3a',
            fg='white',
            font=('Segoe UI', 12, 'bold')
        )
        features_frame.pack(fill='x', padx=20, pady=20)
        
        features_text = """
• 🎮 Détection temps réel multi-écrans
• 🧠 Apprentissage collaboratif intelligent
• 📊 Monitoring système avancé
• 📚 Gestion de datasets professionnelle
• 🎯 Zones de détection personnalisées
• 🌍 Synchronisation communautaire
• 📈 Statistiques et analyses détaillées
• 🔧 Configuration adaptative automatique
        """
        
        features_label = tk.Label(
            features_frame,
            text=features_text,
            font=('Segoe UI', 10),
            fg='#cccccc',
            bg='#3a3a3a',
            justify='left'
        )
        features_label.pack(padx=20, pady=15)
    
    def launch_ultimate_interface(self):
        """Lance l'interface ultime dans une nouvelle fenêtre"""
        try:
            import subprocess
            subprocess.Popen([sys.executable, "launcher_ultimate.py"], 
                           cwd=str(Path(__file__).parent))
            
            # Notification
            messagebox.showinfo(
                "Interface Ultime",
                "Interface Ultime lancée dans une nouvelle fenêtre!"
            )
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Impossible de lancer l'interface ultime:\n{e}"
            )
    
    def launch_dataset_manager(self):
        """Lance le gestionnaire de datasets"""
        try:
            import subprocess
            subprocess.Popen([sys.executable, "launcher_dataset_manager.py"], 
                           cwd=str(Path(__file__).parent))
            
            messagebox.showinfo(
                "Gestionnaire de Datasets",
                "Gestionnaire de Datasets lancé!"
            )
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Impossible de lancer le gestionnaire:\n{e}"
            )
    
    def launch_modern_interface(self):
        """Lance l'interface moderne"""
        try:
            # Créer une nouvelle fenêtre pour l'interface moderne
            modern_window = tk.Toplevel(self.main_window)
            modern_window.title("🎨 Interface Moderne - AIMER PRO")
            modern_window.geometry("1200x800")
            modern_window.configure(bg='#2b2b2b')
            
            # Importer et créer l'interface moderne
            from ui.modern_dataset_interface import ModernDatasetInterface
            modern_interface = ModernDatasetInterface(modern_window)
            
            messagebox.showinfo(
                "Interface Moderne",
                "Interface Moderne ouverte!"
            )
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Impossible de lancer l'interface moderne:\n{e}"
            )
    
    def center_main_window(self):
        """Centre la fenêtre principale"""
        self.main_window.update_idletasks()
        width = 1400
        height = 900
        x = (self.main_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.main_window.winfo_screenheight() // 2) - (height // 2)
        self.main_window.geometry(f'{width}x{height}+{x}+{y}')
    
    def show_main_interface(self):
        """Affiche l'interface principale"""
        # Fermer l'écran de démarrage
        if self.splash_screen:
            self.splash_screen.close()
        
        # Afficher la fenêtre principale
        self.main_window.deiconify()
        self.main_window.lift()
        self.main_window.focus_force()
    
    def save_configuration(self):
        """Sauvegarde la configuration"""
        self.config['show_splash'] = self.show_splash_var.get()
        self.config['auto_start_monitoring'] = self.auto_monitoring_var.get()
        
        self.save_config()
        
        messagebox.showinfo(
            "Configuration",
            "Configuration sauvegardée avec succès!\n\n"
            "Certains changements prendront effet au prochain démarrage."
        )
    
    def reset_configuration(self):
        """Remet la configuration par défaut"""
        if messagebox.askyesno(
            "Réinitialisation",
            "Êtes-vous sûr de vouloir remettre la configuration par défaut?"
        ):
            self.config = {
                'theme': 'dark',
                'language': 'fr',
                'auto_start_monitoring': True,
                'show_splash': True
            }
            
            # Mettre à jour les variables
            self.show_splash_var.set(True)
            self.auto_monitoring_var.set(True)
            
            self.save_config()
            
            messagebox.showinfo(
                "Réinitialisation",
                "Configuration remise par défaut!"
            )
    
    def handle_initialization_error(self, error):
        """Gère les erreurs d'initialisation"""
        error_msg = f"Erreur lors de l'initialisation:\n{error}"
        
        if self.splash_screen:
            self.splash_screen.close()
        
        self.show_error_dialog("Erreur d'Initialisation", error_msg)
    
    def show_error_dialog(self, title, message):
        """Affiche une boîte de dialogue d'erreur"""
        # Créer une fenêtre temporaire pour l'erreur
        error_window = tk.Tk()
        error_window.withdraw()
        
        messagebox.showerror(title, message)
        
        error_window.destroy()
        
        # Quitter l'application
        if self.main_window:
            self.main_window.quit()
        sys.exit(1)
    
    def on_closing(self):
        """Gestionnaire de fermeture de l'application"""
        if messagebox.askyesno(
            "Fermeture",
            "Êtes-vous sûr de vouloir quitter AIMER PRO?"
        ):
            # Arrêter le monitoring
            if self.dashboard:
                self.dashboard.stop_monitoring()
            
            # Sauvegarder la configuration
            self.save_config()
            
            # Fermer l'application
            self.main_window.quit()
    
    def run(self):
        """Lance la boucle principale de l'application"""
        try:
            self.main_window.mainloop()
        except KeyboardInterrupt:
            print("\nArrêt demandé par l'utilisateur")
        except Exception as e:
            print(f"Erreur fatale: {e}")
        finally:
            # Nettoyage
            if self.dashboard:
                self.dashboard.stop_monitoring()

def main():
    """Point d'entrée principal"""
    print("🎯 Démarrage d'AIMER PRO...")
    print("=" * 50)
    
    try:
        # Créer et lancer l'application
        app = AimerProLauncher()
        app.run()
        
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n👋 AIMER PRO fermé. À bientôt!")

if __name__ == "__main__":
    main()
