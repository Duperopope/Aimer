"""
Collaborative Learning System - Système d'apprentissage collaboratif
Gère l'apprentissage en temps réel, la validation communautaire et les contributions
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable
from datetime import datetime
import json
import threading
import time
from dataclasses import dataclass

@dataclass
class LearningAnnotation:
    """Structure pour une annotation d'apprentissage"""
    object_name: str
    bbox: Tuple[float, float, float, float]  # x1, y1, x2, y2
    confidence: float
    image_path: str
    context: str
    created_by: str
    validated: bool = False
    validation_count: int = 0

class LearningMode:
    """Classe de base pour les modes d'apprentissage"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.active = False
    
    def activate(self):
        """Active le mode d'apprentissage"""
        self.active = True
    
    def deactivate(self):
        """Désactive le mode d'apprentissage"""
        self.active = False

class CreationMode(LearningMode):
    """Mode Création - Pour créer de nouveaux objets personnalisés"""
    
    def __init__(self, db_manager, log_callback=None):
        super().__init__("Création", "Créer de nouveaux objets personnalisés")
        self.db_manager = db_manager
        self.log_callback = log_callback
        self.pending_annotations = []
    
    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
    
    def create_new_object(self, image: np.ndarray, bbox: Tuple[float, float, float, float], 
                         suggested_name: str = None) -> Optional[str]:
        """Crée un nouvel objet personnalisé"""
        try:
            # Interface de création d'objet
            root = tk.Tk()
            root.withdraw()
            
            # Demander le nom de l'objet
            if not suggested_name:
                object_name = simpledialog.askstring(
                    "Nouvel Objet",
                    "Comment appelez-vous cet objet ?",
                    initialvalue="mon_objet"
                )
            else:
                object_name = simpledialog.askstring(
                    "Nouvel Objet",
                    f"Nom suggéré: '{suggested_name}'\nConfirmer ou modifier:",
                    initialvalue=suggested_name
                )
            
            if not object_name:
                root.destroy()
                return None
            
            # Demander la catégorie
            category = simpledialog.askstring(
                "Catégorie",
                "Dans quelle catégorie classer cet objet ?",
                initialvalue="personnel"
            )
            
            # Demander une description
            description = simpledialog.askstring(
                "Description",
                "Description de l'objet (optionnel):",
                initialvalue=""
            )
            
            root.destroy()
            
            # Sauvegarder l'image de l'objet
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"{object_name}_{timestamp}.jpg"
            image_path = Path("datasets/personal_objects") / image_filename
            image_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Extraire la région de l'objet
            x1, y1, x2, y2 = map(int, bbox)
            object_crop = image[y1:y2, x1:x2]
            cv2.imwrite(str(image_path), object_crop)
            
            # Enregistrer dans la base de données personnelle
            with sqlite3.connect("datasets/personal_library.db") as conn:
                cursor = conn.execute("""
                    INSERT INTO personal_objects 
                    (object_name, description, category, examples_count, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (object_name, description or "", category or "personnel", 1, datetime.now()))
                
                object_id = cursor.lastrowid
                
                # Ajouter l'annotation
                conn.execute("""
                    INSERT INTO annotations 
                    (object_id, image_path, bbox_x1, bbox_y1, bbox_x2, bbox_y2, confidence, validated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (object_id, str(image_path), x1, y1, x2, y2, 1.0, True))
            
            self.log(f"✅ Nouvel objet créé: '{object_name}' dans la catégorie '{category}'")
            return object_name
            
        except Exception as e:
            self.log(f"❌ Erreur création objet: {e}")
            return None

class ValidationMode(LearningMode):
    """Mode Validation - Pour valider les détections existantes"""
    
    def __init__(self, db_manager, log_callback=None):
        super().__init__("Validation", "Valider la précision des détections")
        self.db_manager = db_manager
        self.log_callback = log_callback
        self.validation_queue = []
        self.user_score = 0
        self.validation_streak = 0
    
    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
    
    def validate_detection(self, detection: Dict, is_correct: bool, 
                          correction: str = None) -> bool:
        """Valide une détection"""
        try:
            # Enregistrer la validation
            validation_data = {
                "detection_id": detection.get("id"),
                "object_name": detection.get("class_name"),
                "is_correct": is_correct,
                "correction": correction,
                "validator": "local_user",
                "validation_time": datetime.now(),
                "confidence_before": detection.get("confidence", 0.0)
            }
            
            # Mettre à jour les statistiques utilisateur
            if is_correct:
                self.user_score += 10
                self.validation_streak += 1
                self.log(f"✅ Validation correcte! Score: {self.user_score} (Série: {self.validation_streak})")
            else:
                self.validation_streak = 0
                if correction:
                    self.user_score += 5  # Points pour correction utile
                    self.log(f"🔧 Correction appliquée: '{correction}' - Score: {self.user_score}")
                else:
                    self.log(f"❌ Détection marquée comme incorrecte")
            
            # Sauvegarder dans la base de données
            self._save_validation(validation_data)
            
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur validation: {e}")
            return False
    
    def _save_validation(self, validation_data: Dict):
        """Sauvegarde une validation dans la base de données"""
        with sqlite3.connect("datasets/validations.db") as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS validations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    detection_id TEXT,
                    object_name TEXT,
                    is_correct BOOLEAN,
                    correction TEXT,
                    validator TEXT,
                    validation_time TIMESTAMP,
                    confidence_before REAL,
                    user_score INTEGER
                )
            """)
            
            conn.execute("""
                INSERT INTO validations 
                (detection_id, object_name, is_correct, correction, validator, 
                 validation_time, confidence_before, user_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                validation_data["detection_id"],
                validation_data["object_name"],
                validation_data["is_correct"],
                validation_data["correction"],
                validation_data["validator"],
                validation_data["validation_time"],
                validation_data["confidence_before"],
                self.user_score
            ))

class CorrectionMode(LearningMode):
    """Mode Correction - Pour corriger les erreurs de détection"""
    
    def __init__(self, db_manager, log_callback=None):
        super().__init__("Correction", "Corriger les erreurs de détection")
        self.db_manager = db_manager
        self.log_callback = log_callback
        self.corrections_made = 0
    
    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
    
    def correct_detection(self, wrong_detection: Dict, correct_name: str, 
                         new_bbox: Tuple[float, float, float, float] = None) -> bool:
        """Corrige une détection erronée"""
        try:
            # Enregistrer la correction
            correction_data = {
                "original_detection": wrong_detection,
                "correct_name": correct_name,
                "new_bbox": new_bbox or wrong_detection.get("bbox"),
                "corrected_by": "local_user",
                "correction_time": datetime.now()
            }
            
            # Sauvegarder la correction
            self._save_correction(correction_data)
            
            self.corrections_made += 1
            self.log(f"🔧 Correction appliquée: '{wrong_detection.get('class_name')}' → '{correct_name}'")
            self.log(f"📊 Total corrections: {self.corrections_made}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur correction: {e}")
            return False
    
    def _save_correction(self, correction_data: Dict):
        """Sauvegarde une correction dans la base de données"""
        with sqlite3.connect("datasets/corrections.db") as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS corrections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_name TEXT,
                    correct_name TEXT,
                    original_bbox TEXT,
                    new_bbox TEXT,
                    corrected_by TEXT,
                    correction_time TIMESTAMP,
                    applied BOOLEAN DEFAULT FALSE
                )
            """)
            
            conn.execute("""
                INSERT INTO corrections 
                (original_name, correct_name, original_bbox, new_bbox, 
                 corrected_by, correction_time)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                correction_data["original_detection"].get("class_name"),
                correction_data["correct_name"],
                json.dumps(correction_data["original_detection"].get("bbox")),
                json.dumps(correction_data["new_bbox"]),
                correction_data["corrected_by"],
                correction_data["correction_time"]
            ))

class SharingMode(LearningMode):
    """Mode Partage - Pour partager ses découvertes avec la communauté"""
    
    def __init__(self, db_manager, log_callback=None):
        super().__init__("Partage", "Partager avec la communauté")
        self.db_manager = db_manager
        self.log_callback = log_callback
        self.contributions_shared = 0
    
    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
    
    def share_object(self, object_name: str, privacy_level: str = "public") -> bool:
        """Partage un objet personnel avec la communauté"""
        try:
            # Vérifier que l'objet existe dans la base personnelle
            with sqlite3.connect("datasets/personal_library.db") as conn:
                cursor = conn.execute("""
                    SELECT id, object_name, description, category, examples_count
                    FROM personal_objects 
                    WHERE object_name = ?
                """, (object_name,))
                
                object_data = cursor.fetchone()
                if not object_data:
                    self.log(f"❌ Objet '{object_name}' non trouvé dans votre librairie")
                    return False
            
            # Demander confirmation de partage
            root = tk.Tk()
            root.withdraw()
            
            confirm = messagebox.askyesno(
                "Partager avec la communauté",
                f"Voulez-vous partager '{object_name}' avec la communauté ?\n\n"
                f"Cela aidera d'autres utilisateurs à détecter cet objet.\n"
                f"Niveau de confidentialité: {privacy_level}"
            )
            
            root.destroy()
            
            if not confirm:
                return False
            
            # Préparer les données pour le partage
            sharing_data = {
                "object_name": object_name,
                "description": object_data[2],
                "category": object_data[3],
                "examples_count": object_data[4],
                "shared_by": "local_user",
                "privacy_level": privacy_level,
                "share_time": datetime.now()
            }
            
            # Sauvegarder dans la base de partage
            self._save_shared_object(sharing_data)
            
            self.contributions_shared += 1
            self.log(f"🌍 Objet '{object_name}' partagé avec la communauté!")
            self.log(f"🤝 Total contributions: {self.contributions_shared}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur partage: {e}")
            return False
    
    def _save_shared_object(self, sharing_data: Dict):
        """Sauvegarde un objet partagé"""
        with sqlite3.connect("datasets/community_shared.db") as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS shared_objects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    object_name TEXT,
                    description TEXT,
                    category TEXT,
                    examples_count INTEGER,
                    shared_by TEXT,
                    privacy_level TEXT,
                    share_time TIMESTAMP,
                    downloads INTEGER DEFAULT 0,
                    rating REAL DEFAULT 0.0
                )
            """)
            
            conn.execute("""
                INSERT INTO shared_objects 
                (object_name, description, category, examples_count, 
                 shared_by, privacy_level, share_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                sharing_data["object_name"],
                sharing_data["description"],
                sharing_data["category"],
                sharing_data["examples_count"],
                sharing_data["shared_by"],
                sharing_data["privacy_level"],
                sharing_data["share_time"]
            ))

class CollaborativeLearningSystem:
    """Système principal d'apprentissage collaboratif"""
    
    def __init__(self, db_manager, log_callback=None):
        self.db_manager = db_manager
        self.log_callback = log_callback
        
        # Initialiser les modes d'apprentissage
        self.creation_mode = CreationMode(db_manager, log_callback)
        self.validation_mode = ValidationMode(db_manager, log_callback)
        self.correction_mode = CorrectionMode(db_manager, log_callback)
        self.sharing_mode = SharingMode(db_manager, log_callback)
        
        self.current_mode = None
        self.learning_active = False
        
        # Statistiques utilisateur
        self.user_stats = {
            "objects_created": 0,
            "validations_made": 0,
            "corrections_applied": 0,
            "contributions_shared": 0,
            "total_score": 0,
            "accuracy_rate": 0.0
        }
    
    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
    
    def activate_mode(self, mode_name: str) -> bool:
        """Active un mode d'apprentissage spécifique"""
        try:
            # Désactiver le mode actuel
            if self.current_mode:
                self.current_mode.deactivate()
            
            # Activer le nouveau mode
            if mode_name == "creation":
                self.current_mode = self.creation_mode
            elif mode_name == "validation":
                self.current_mode = self.validation_mode
            elif mode_name == "correction":
                self.current_mode = self.correction_mode
            elif mode_name == "sharing":
                self.current_mode = self.sharing_mode
            else:
                self.log(f"❌ Mode '{mode_name}' non reconnu")
                return False
            
            self.current_mode.activate()
            self.learning_active = True
            
            self.log(f"🎯 Mode '{self.current_mode.name}' activé")
            self.log(f"📋 {self.current_mode.description}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur activation mode: {e}")
            return False
    
    def deactivate_learning(self):
        """Désactive l'apprentissage"""
        if self.current_mode:
            self.current_mode.deactivate()
            self.log(f"⏹️ Mode '{self.current_mode.name}' désactivé")
        
        self.current_mode = None
        self.learning_active = False
    
    def process_detection_for_learning(self, image: np.ndarray, detection: Dict) -> Optional[str]:
        """Traite une détection selon le mode d'apprentissage actuel"""
        if not self.learning_active or not self.current_mode:
            return None
        
        try:
            if isinstance(self.current_mode, CreationMode):
                # Mode création - créer un nouvel objet
                bbox = detection.get("bbox", [0, 0, 100, 100])
                return self.current_mode.create_new_object(image, bbox)
            
            elif isinstance(self.current_mode, ValidationMode):
                # Mode validation - valider la détection
                # Interface de validation rapide
                root = tk.Tk()
                root.withdraw()
                
                is_correct = messagebox.askyesno(
                    "Validation",
                    f"Cette détection est-elle correcte ?\n\n"
                    f"Objet: {detection.get('class_name', 'Inconnu')}\n"
                    f"Confiance: {detection.get('confidence', 0.0):.2f}"
                )
                
                correction = None
                if not is_correct:
                    correction = simpledialog.askstring(
                        "Correction",
                        "Quel est le nom correct de cet objet ?",
                        initialvalue=""
                    )
                
                root.destroy()
                
                self.current_mode.validate_detection(detection, is_correct, correction)
                return "validated"
            
            elif isinstance(self.current_mode, CorrectionMode):
                # Mode correction - corriger la détection
                root = tk.Tk()
                root.withdraw()
                
                correct_name = simpledialog.askstring(
                    "Correction",
                    f"Nom correct pour cet objet ?\n\n"
                    f"Détecté comme: {detection.get('class_name', 'Inconnu')}",
                    initialvalue=""
                )
                
                root.destroy()
                
                if correct_name:
                    self.current_mode.correct_detection(detection, correct_name)
                    return correct_name
            
            return None
            
        except Exception as e:
            self.log(f"❌ Erreur traitement apprentissage: {e}")
            return None
    
    def get_user_stats(self) -> Dict:
        """Retourne les statistiques utilisateur"""
        # Mettre à jour les statistiques depuis les bases de données
        self._update_user_stats()
        return self.user_stats.copy()
    
    def _update_user_stats(self):
        """Met à jour les statistiques utilisateur depuis les bases de données"""
        try:
            # Objets créés
            with sqlite3.connect("datasets/personal_library.db") as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM personal_objects")
                self.user_stats["objects_created"] = cursor.fetchone()[0]
            
            # Validations effectuées
            try:
                with sqlite3.connect("datasets/validations.db") as conn:
                    cursor = conn.execute("SELECT COUNT(*), MAX(user_score) FROM validations")
                    result = cursor.fetchone()
                    self.user_stats["validations_made"] = result[0] or 0
                    self.user_stats["total_score"] = result[1] or 0
            except:
                pass
            
            # Corrections appliquées
            try:
                with sqlite3.connect("datasets/corrections.db") as conn:
                    cursor = conn.execute("SELECT COUNT(*) FROM corrections")
                    self.user_stats["corrections_applied"] = cursor.fetchone()[0]
            except:
                pass
            
            # Contributions partagées
            try:
                with sqlite3.connect("datasets/community_shared.db") as conn:
                    cursor = conn.execute("SELECT COUNT(*) FROM shared_objects")
                    self.user_stats["contributions_shared"] = cursor.fetchone()[0]
            except:
                pass
                
        except Exception as e:
            self.log(f"⚠️ Erreur mise à jour stats: {e}")
    
    def create_learning_interface(self, parent=None) -> tk.Toplevel:
        """Crée l'interface d'apprentissage collaboratif"""
        window = tk.Toplevel(parent) if parent else tk.Tk()
        window.title("🧠 Apprentissage Collaboratif")
        window.geometry("600x500")
        
        # Frame principal
        main_frame = ttk.Frame(window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, text="🧠 Système d'Apprentissage Collaboratif", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Sélection du mode
        mode_frame = ttk.LabelFrame(main_frame, text="Mode d'Apprentissage", padding="10")
        mode_frame.pack(fill=tk.X, pady=10)
        
        modes = [
            ("creation", "🎨 Création", "Créer de nouveaux objets personnalisés"),
            ("validation", "✅ Validation", "Valider la précision des détections"),
            ("correction", "🔧 Correction", "Corriger les erreurs de détection"),
            ("sharing", "🌍 Partage", "Partager avec la communauté")
        ]
        
        for mode_key, mode_name, mode_desc in modes:
            btn = ttk.Button(mode_frame, text=mode_name,
                           command=lambda k=mode_key: self.activate_mode(k))
            btn.pack(side=tk.LEFT, padx=5)
        
        # Statistiques utilisateur
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Vos Statistiques", padding="10")
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.stats_label = ttk.Label(stats_frame, text="Chargement des statistiques...")
        self.stats_label.pack()
        
        # Boutons d'action
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="📊 Actualiser Stats",
                  command=self._refresh_stats_display).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame, text="⏹️ Désactiver Apprentissage",
                  command=self.deactivate_learning).pack(side=tk.LEFT, padx=5)
        
        # Actualiser l'affichage initial
        self._refresh_stats_display()
        
        return window
    
    def _refresh_stats_display(self):
        """Actualise l'affichage des statistiques"""
        stats = self.get_user_stats()
        stats_text = f"""
🎨 Objets créés: {stats['objects_created']}
✅ Validations: {stats['validations_made']}
🔧 Corrections: {stats['corrections_applied']}
🌍 Contributions: {stats['contributions_shared']}
🏆 Score total: {stats['total_score']}
        """.strip()
        
        if hasattr(self, 'stats_label'):
            self.stats_label.configure(text=stats_text)

# Fonction utilitaire pour créer le système
def create_collaborative_learning_system(db_manager, log_callback=None) -> CollaborativeLearningSystem:
    """Crée et initialise le système d'apprentissage collaboratif"""
    return CollaborativeLearningSystem(db_manager, log_callback)

if __name__ == "__main__":
    # Test du système
    system = create_collaborative_learning_system(None)
    
    print("🧠 Système d'apprentissage collaboratif initialisé")
    print("📊 Modes disponibles:")
    print("  • Création - Créer de nouveaux objets")
    print("  • Validation - Valider les détections")
    print("  • Correction - Corriger les erreurs")
    print("  • Partage - Partager avec la communauté")
