#!/usr/bin/env python3
"""
AIMER PRO - Serveur de Démonstration Simplifié
Test rapide de l'interface web avec détection basique
"""

import os
import sys
import json
import base64
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent.parent))

from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np

# Imports locaux
from core.detector import SmartDetector
from core.logger import Logger

app = Flask(__name__, 
           template_folder='ui/web_interface/templates',
           static_folder='ui/web_interface/static')

# Initialisation des composants
logger = Logger("AimerDemo")
detector = SmartDetector()

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/test-webcam')
def test_webcam():
    """Test de la webcam"""
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                cap.release()
                return jsonify({
                    'success': True,
                    'message': 'Webcam fonctionnelle !',
                    'resolution': f"{frame.shape[1]}x{frame.shape[0]}"
                })
        cap.release()
        return jsonify({
            'success': False,
            'message': 'Webcam non disponible'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur webcam: {str(e)}'
        })

@app.route('/detect-image', methods=['POST'])
def detect_image():
    """Détection d'objets sur image uploadée"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Aucune image fournie'})
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'})
        
        # Lire l'image
        file_bytes = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': 'Image invalide'})
        
        # Détection d'objets
        logger.info("🎯 Détection d'objets en cours...")
        detections = detector.detect_objects(image)
        
        # Dessiner les détections (méthode simplifiée)
        annotated_image = image.copy()
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            cv2.rectangle(annotated_image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(annotated_image, f"{detection['class_name']}: {detection['confidence']:.2f}",
                       (int(x1), int(y1-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Encoder l'image en base64
        _, buffer = cv2.imencode('.jpg', annotated_image)
        image_base64 = base64.b64encode(buffer.tobytes()).decode('utf-8')
        
        # Préparer les résultats
        objects_found = []
        for detection in detections:
            objects_found.append({
                'class_name': detection['class_name'],
                'confidence': round(detection['confidence'], 2),
                'bbox': detection['bbox']
            })
        
        return jsonify({
            'success': True,
            'image': f"data:image/jpeg;base64,{image_base64}",
            'objects': objects_found,
            'total_objects': len(objects_found),
            'processing_info': {
                'image_size': f"{image.shape[1]}x{image.shape[0]}",
                'detector': 'COCO (Detectron2)'
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur détection: {e}")
        return jsonify({'error': f'Erreur détection: {str(e)}'})

@app.route('/api/stats')
def get_stats():
    """Statistiques de l'application"""
    return jsonify({
        'status': 'active',
        'detector': 'Detectron2 COCO',
        'classes_available': 80,
        'webcam_status': 'ready',
        'version': '3.0.0'
    })

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                🎯 AIMER PRO - DÉMO                          ║
║              Serveur de Démonstration                       ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("✅ Initialisation du serveur de démonstration...")
    print("🌐 Interface web: http://localhost:5000")
    print("📹 Test webcam: http://localhost:5000/test-webcam")
    print("🎯 API stats: http://localhost:5000/api/stats")
    print("\n🚀 Serveur démarré ! Ouvrez votre navigateur.")
    
    try:
        app.run(host='localhost', port=5000, debug=True)
    except Exception as e:
        print(f"❌ Erreur serveur: {e}")

if __name__ == '__main__':
    main()
