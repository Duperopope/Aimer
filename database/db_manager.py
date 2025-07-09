import sqlite3
import json
from datetime import datetime
import numpy as np

class DatabaseManager:
    def __init__(self, db_path="aim_training.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table pour les screenshots
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS screenshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                app_name TEXT,
                image_path TEXT,
                resolution TEXT,
                metadata TEXT
            )
        ''')
        
        # Table pour les détections
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                screenshot_id INTEGER,
                x1 REAL, y1 REAL, x2 REAL, y2 REAL,
                confidence REAL,
                class_name TEXT,
                is_validated BOOLEAN DEFAULT NULL,
                is_correct BOOLEAN DEFAULT NULL,
                user_feedback TEXT,
                FOREIGN KEY (screenshot_id) REFERENCES screenshots (id)
            )
        ''')
        
        # Table pour les métriques
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                precision_score REAL,
                recall_score REAL,
                f1_score REAL,
                total_samples INTEGER,
                correct_predictions INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_screenshot(self, app_name, image_path, resolution, metadata=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO screenshots (app_name, image_path, resolution, metadata)
            VALUES (?, ?, ?, ?)
        ''', (app_name, image_path, resolution, json.dumps(metadata or {})))
        
        screenshot_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return screenshot_id
    
    def save_detection(self, screenshot_id, bbox, confidence, class_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        x1, y1, x2, y2 = bbox
        cursor.execute('''
            INSERT INTO detections (screenshot_id, x1, y1, x2, y2, confidence, class_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (screenshot_id, x1, y1, x2, y2, confidence, class_name))
        
        detection_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return detection_id
    
    def update_validation(self, detection_id, is_correct, feedback=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE detections 
            SET is_validated = TRUE, is_correct = ?, user_feedback = ?
            WHERE id = ?
        ''', (is_correct, feedback, detection_id))
        
        conn.commit()
        conn.close()
    
    def get_uncertain_detections(self, limit=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.*, s.image_path, s.app_name 
            FROM detections d
            JOIN screenshots s ON d.screenshot_id = s.id
            WHERE d.is_validated IS NULL
            ORDER BY d.confidence ASC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        return results
