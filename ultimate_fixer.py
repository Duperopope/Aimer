#!/usr/bin/env python3
"""
AIMER PRO - Ultimate Fixer
Installation automatique complète d'AIMER PRO
Version: 1.0
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

class AimerProInstaller:
    def __init__(self):
        self.project_dir = Path.cwd() / "aimer_pro"
        self.venv_dir = self.project_dir / "venv"

    def log(self, message, level="INFO"):
        """Affichage des logs avec couleurs"""
        colors = {
            "INFO": "\033[94m",
            "SUCCESS": "\033[92m", 
            "WARNING": "\033[93m",
            "ERROR": "\033[91m",
            "RESET": "\033[0m"
        }
        print(f"{colors.get(level, '')}{level}: {message}{colors['RESET']}")

    def clean_previous_installation(self):
        """Nettoie l'installation précédente"""
        self.log("🧹 Nettoyage de l'installation précédente...")

        if self.project_dir.exists():
            try:
                shutil.rmtree(self.project_dir)
                self.log("Installation précédente supprimée", "SUCCESS")
            except Exception as e:
                self.log(f"Erreur lors du nettoyage: {e}", "ERROR")

    def create_project_structure(self):
        """Crée la structure du projet"""
        self.log("📁 Création de la structure du projet...")

        directories = [
            self.project_dir,
            self.project_dir / "static",
            self.project_dir / "templates",
            self.project_dir / "data"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        self.log("Structure créée avec succès", "SUCCESS")

    def create_virtual_environment(self):
        """Crée l'environnement virtuel"""
        self.log("🐍 Création de l'environnement virtuel...")

        try:
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_dir)], 
                         check=True, capture_output=True)
            self.log("Environnement virtuel créé", "SUCCESS")
        except subprocess.CalledProcessError as e:
            self.log(f"Erreur création venv: {e}", "ERROR")
            return False
        return True

    def get_pip_command(self):
        """Retourne la commande pip selon l'OS"""
        if os.name == 'nt':  # Windows
            return str(self.venv_dir / "Scripts" / "pip")
        else:  # Unix/Linux/Mac
            return str(self.venv_dir / "bin" / "pip")

    def install_dependencies(self):
        """Installe les dépendances Python"""
        self.log("📦 Installation des dépendances...")

        packages = [
            "flask",
            "flask-cors", 
            "requests",
            "beautifulsoup4",
            "lxml",
            "pandas",
            "numpy",
            "matplotlib",
            "seaborn",
            "plotly",
            "scikit-learn",
            "nltk",
            "textblob",
            "wordcloud",
            "Pillow"
        ]

        pip_cmd = self.get_pip_command()

        for package in packages:
            try:
                self.log(f"Installation de {package}...")
                subprocess.run([pip_cmd, "install", package], 
                             check=True, capture_output=True)
                self.log(f"✅ {package} installé", "SUCCESS")
            except subprocess.CalledProcessError as e:
                self.log(f"❌ Erreur installation {package}: {e}", "ERROR")

    def create_flask_server(self):
        """Crée le serveur Flask principal"""
        self.log("🌐 Création du serveur Flask...")

        flask_code = """from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from textblob import TextBlob
from wordcloud import WordCloud
import nltk
from datetime import datetime
import io
import base64

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'aimer-pro-secret-key-2024'
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

# Télécharger les données NLTK nécessaires
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except:
    pass

class AimerProAnalyzer:
    def __init__(self):
        self.data = []

    def scrape_web_data(self, url):
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'div'])
            texts = [elem.get_text().strip() for elem in text_elements if elem.get_text().strip()]

            return {
                'url': url,
                'title': soup.title.string if soup.title else 'Sans titre',
                'texts': texts[:50],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}

    def analyze_sentiment(self, texts):
        sentiments = []
        for text in texts:
            blob = TextBlob(text)
            sentiments.append({
                'text': text[:100],
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            })
        return sentiments

    def create_wordcloud(self, texts):
        try:
            all_text = ' '.join(texts)
            wordcloud = WordCloud(width=800, height=400, 
                                background_color='white').generate(all_text)

            img_path = os.path.join(DATA_DIR, 'wordcloud.png')
            wordcloud.to_file(img_path)
            return img_path
        except Exception as e:
            return None

analyzer = AimerProAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scrape', methods=['POST'])
def scrape_data():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL requise'}), 400

    result = analyzer.scrape_web_data(url)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'scraped_data_{timestamp}.json'
    filepath = os.path.join(DATA_DIR, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return jsonify(result)

@app.route('/api/analyze', methods=['POST'])
def analyze_data():
    data = request.json
    texts = data.get('texts', [])

    if not texts:
        return jsonify({'error': 'Textes requis'}), 400

    sentiments = analyzer.analyze_sentiment(texts)
    wordcloud_path = analyzer.create_wordcloud(texts)

    sentiment_fig = px.scatter(
        x=[s['polarity'] for s in sentiments],
        y=[s['subjectivity'] for s in sentiments],
        title='Analyse de Sentiment',
        labels={'x': 'Polarité', 'y': 'Subjectivité'}
    )

    result = {
        'sentiments': sentiments,
        'wordcloud': wordcloud_path,
        'sentiment_plot': json.dumps(sentiment_fig, cls=PlotlyJSONEncoder),
        'timestamp': datetime.now().isoformat()
    }

    return jsonify(result)

if __name__ == '__main__':
    print("🚀 AIMER PRO Server démarré!")
    print("📊 Interface disponible sur: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
"""

        with open(self.project_dir / "app.py", "w", encoding="utf-8") as f:
            f.write(flask_code)

        self.log("Serveur Flask créé", "SUCCESS")

    def create_html_frontend(self):
        """Crée l'interface HTML"""
        self.log("🎨 Création de l'interface HTML...")

        html_code = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIMER PRO - Analyseur Intelligent</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 3em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .card:hover { transform: translateY(-5px); }
        .input-group { margin-bottom: 20px; }
        .input-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #555; }
        .input-group input, .input-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }
        .input-group input:focus, .input-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .btn-secondary { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); color: #333; }
        .results { margin-top: 30px; }
        .result-item {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 0 8px 8px 0;
        }
        .loading { text-align: center; padding: 20px; color: #667eea; }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .status { padding: 10px; border-radius: 5px; margin-bottom: 15px; }
        .status.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .plot-container { margin: 20px 0; background: white; border-radius: 8px; padding: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AIMER PRO</h1>
            <p>Analyseur Intelligent Multi-Environnement Révolutionnaire</p>
        </div>

        <div class="grid">
            <div class="card">
                <h2>🌐 Scraping Web</h2>
                <div class="input-group">
                    <label for="url">URL à analyser:</label>
                    <input type="url" id="url" placeholder="https://example.com">
                </div>
                <button class="btn" onclick="scrapeData()">Scraper les données</button>
                <button class="btn btn-secondary" onclick="loadSampleData()">Données d'exemple</button>
            </div>

            <div class="card">
                <h2>📊 Analyse de Texte</h2>
                <div class="input-group">
                    <label for="texts">Textes à analyser (un par ligne):</label>
                    <textarea id="texts" rows="5" placeholder="Entrez vos textes ici..."></textarea>
                </div>
                <button class="btn" onclick="analyzeTexts()">Analyser</button>
            </div>
        </div>

        <div id="status"></div>
        <div id="results" class="results"></div>
    </div>

    <script>
        function showStatus(message, type = 'success') {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = `<div class="status ${type}">${message}</div>`;
            setTimeout(() => statusDiv.innerHTML = '', 5000);
        }

        function showLoading(message = 'Traitement en cours...') {
            document.getElementById('results').innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>${message}</p>
                </div>
            `;
        }

        async function scrapeData() {
            const url = document.getElementById('url').value;
            if (!url) {
                showStatus('Veuillez entrer une URL', 'error');
                return;
            }

            showLoading('Scraping des données...');

            try {
                const response = await axios.post('/api/scrape', { url });
                const data = response.data;

                if (data.error) {
                    showStatus(`Erreur: ${data.error}`, 'error');
                    return;
                }

                const textsArea = document.getElementById('texts');
                textsArea.value = data.texts.join('\n');

                showStatus('Données scrapées avec succès!');
                displayScrapedData(data);

            } catch (error) {
                showStatus(`Erreur: ${error.message}`, 'error');
                document.getElementById('results').innerHTML = '';
            }
        }

        async function analyzeTexts() {
            const textsValue = document.getElementById('texts').value;
            if (!textsValue.trim()) {
                showStatus('Veuillez entrer des textes à analyser', 'error');
                return;
            }

            const texts = textsValue.split('\n').filter(t => t.trim());
            showLoading('Analyse en cours...');

            try {
                const response = await axios.post('/api/analyze', { texts });
                const data = response.data;

                showStatus('Analyse terminée avec succès!');
                displayAnalysisResults(data);

            } catch (error) {
                showStatus(`Erreur: ${error.message}`, 'error');
                document.getElementById('results').innerHTML = '';
            }
        }

        function displayScrapedData(data) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = `
                <div class="card">
                    <h3>📄 Données Scrapées</h3>
                    <div class="result-item"><strong>Titre:</strong> ${data.title}</div>
                    <div class="result-item"><strong>URL:</strong> ${data.url}</div>
                    <div class="result-item"><strong>Textes extraits:</strong> ${data.texts.length} éléments</div>
                    <div class="result-item"><strong>Timestamp:</strong> ${new Date(data.timestamp).toLocaleString()}</div>
                </div>
            `;
        }

        function displayAnalysisResults(data) {
            const resultsDiv = document.getElementById('results');

            let html = '<div class="card"><h3>📊 Résultats d\'Analyse</h3>';

            if (data.sentiments && data.sentiments.length > 0) {
                html += '<h4>💭 Analyse de Sentiment</h4>';
                data.sentiments.forEach((sentiment, index) => {
                    const polarityLabel = sentiment.polarity > 0 ? 'Positif' : 
                                        sentiment.polarity < 0 ? 'Négatif' : 'Neutre';
                    html += `
                        <div class="result-item">
                            <strong>Texte ${index + 1}:</strong> ${sentiment.text}...<br>
                            <strong>Sentiment:</strong> ${polarityLabel} (${sentiment.polarity.toFixed(2)})<br>
                            <strong>Subjectivité:</strong> ${sentiment.subjectivity.toFixed(2)}
                        </div>
                    `;
                });
            }

            html += '</div>';

            if (data.sentiment_plot) {
                html += '<div class="plot-container" id="sentiment-plot"></div>';
            }

            resultsDiv.innerHTML = html;

            if (data.sentiment_plot) {
                const plotData = JSON.parse(data.sentiment_plot);
                Plotly.newPlot('sentiment-plot', plotData.data, plotData.layout);
            }
        }

        function loadSampleData() {
            const sampleTexts = [
                "J'adore ce produit, il est fantastique!",
                "Le service client est décevant et lent.",
                "Qualité correcte pour le prix payé.",
                "Expérience exceptionnelle, je recommande vivement!",
                "Problèmes techniques récurrents, très frustrant."
            ];

            document.getElementById('texts').value = sampleTexts.join('\n');
            showStatus('Données d\'exemple chargées!');
        }

        document.addEventListener('DOMContentLoaded', function() {
            showStatus('AIMER PRO initialisé et prêt!');
        });
    </script>
</body>
</html>"""

        templates_dir = self.project_dir / "templates"
        with open(templates_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html_code)

        self.log("Interface HTML créée", "SUCCESS")

    def create_launcher(self):
        """Crée le script de lancement"""
        self.log("🚀 Création du launcher...")

        if os.name == 'nt':  # Windows
            launcher_content = f"""@echo off
echo 🚀 Lancement d'AIMER PRO...
cd /d "{self.project_dir}"
"{self.venv_dir}\Scripts\python.exe" app.py
pause
"""
            launcher_path = self.project_dir / "launch_aimer_pro.bat"
        else:  # Unix/Linux/Mac
            launcher_content = f"""#!/bin/bash
echo "🚀 Lancement d'AIMER PRO..."
cd "{self.project_dir}"
"{self.venv_dir}/bin/python" app.py
"""
            launcher_path = self.project_dir / "launch_aimer_pro.sh"

        with open(launcher_path, "w", encoding="utf-8") as f:
            f.write(launcher_content)

        if os.name != 'nt':
            os.chmod(launcher_path, 0o755)

        self.log("Launcher créé", "SUCCESS")

    def create_requirements_file(self):
        """Crée le fichier requirements.txt"""
        requirements = """flask==2.3.3
flask-cors==4.0.0
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
pandas==2.1.1
numpy==1.24.3
matplotlib==3.7.2
seaborn==0.12.2
plotly==5.17.0
scikit-learn==1.3.0
nltk==3.8.1
textblob==0.17.1
wordcloud==1.9.2
Pillow==10.0.1
"""

        with open(self.project_dir / "requirements.txt", "w") as f:
            f.write(requirements)

        self.log("Fichier requirements.txt créé", "SUCCESS")

    def install_complete(self):
        """Installation complète d'AIMER PRO"""
        self.log("🎯 Début de l'installation complète d'AIMER PRO", "INFO")

        try:
            self.clean_previous_installation()
            self.create_project_structure()

            if not self.create_virtual_environment():
                return False

            self.install_dependencies()
            self.create_flask_server()
            self.create_html_frontend()
            self.create_launcher()
            self.create_requirements_file()

            self.log("✅ Installation terminée avec succès!", "SUCCESS")
            self.log(f"📁 Projet installé dans: {self.project_dir}", "INFO")

            if os.name == 'nt':
                launcher_file = "launch_aimer_pro.bat"
            else:
                launcher_file = "launch_aimer_pro.sh"

            self.log("🚀 Pour lancer AIMER PRO:", "INFO")
            self.log(f"   Double-cliquez sur: {launcher_file}", "INFO")
            self.log("   Ou exécutez: python app.py", "INFO")
            self.log("📊 Interface: http://localhost:5000", "INFO")

            return True

        except Exception as e:
            self.log(f"❌ Erreur lors de l'installation: {e}", "ERROR")
            return False

def main():
    """Fonction principale"""
    print("=" * 60)
    print("🤖 AIMER PRO - Ultimate Fixer")
    print("Installation automatique complète")
    print("=" * 60)

    installer = AimerProInstaller()
    success = installer.install_complete()

    if success:
        print("\n🎉 AIMER PRO installé avec succès!")
        print("Vous pouvez maintenant utiliser l'application.")
    else:
        print("\n❌ Échec de l'installation.")
        print("Vérifiez les logs ci-dessus pour plus de détails.")

    input("\nAppuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    main()
