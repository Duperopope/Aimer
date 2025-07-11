import json
import os

import matplotlib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request, send_file
from flask_cors import CORS

matplotlib.use("Agg")
import base64
import io
from datetime import datetime

import matplotlib.pyplot as plt
import nltk
import plotly.express as px
import plotly.graph_objects as go
import requests
import seaborn as sns
from bs4 import BeautifulSoup
from plotly.utils import PlotlyJSONEncoder
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from textblob import TextBlob
from wordcloud import WordCloud

app = Flask(__name__)
CORS(app)

# Configuration
app.config["SECRET_KEY"] = "aimer-pro-secret-key-2024"
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Télécharger les données NLTK nécessaires
try:
    nltk.download("punkt", quiet=True)
    nltk.download("stopwords", quiet=True)
    nltk.download("vader_lexicon", quiet=True)
except:
    pass


class AimerProAnalyzer:
    def __init__(self):
        self.data = []

    def scrape_web_data(self, url):
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")

            text_elements = soup.find_all(["p", "h1", "h2", "h3", "div"])
            texts = [elem.get_text().strip() for elem in text_elements if elem.get_text().strip()]

            return {
                "url": url,
                "title": soup.title.string if soup.title else "Sans titre",
                "texts": texts[:50],
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"error": str(e)}

    def analyze_sentiment(self, texts):
        sentiments = []
        for text in texts:
            blob = TextBlob(text)
            sentiments.append(
                {
                    "text": text[:100],
                    "polarity": blob.sentiment.polarity,
                    "subjectivity": blob.sentiment.subjectivity,
                }
            )
        return sentiments

    def create_wordcloud(self, texts):
        try:
            all_text = " ".join(texts)
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate(
                all_text
            )

            img_path = os.path.join(DATA_DIR, "wordcloud.png")
            wordcloud.to_file(img_path)
            return img_path
        except Exception as e:
            return None


analyzer = AimerProAnalyzer()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/scrape", methods=["POST"])
def scrape_data():
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL requise"}), 400

    result = analyzer.scrape_web_data(url)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scraped_data_{timestamp}.json"
    filepath = os.path.join(DATA_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return jsonify(result)


@app.route("/api/analyze", methods=["POST"])
def analyze_data():
    data = request.json
    texts = data.get("texts", [])

    if not texts:
        return jsonify({"error": "Textes requis"}), 400

    sentiments = analyzer.analyze_sentiment(texts)
    wordcloud_path = analyzer.create_wordcloud(texts)

    sentiment_fig = px.scatter(
        x=[s["polarity"] for s in sentiments],
        y=[s["subjectivity"] for s in sentiments],
        title="Analyse de Sentiment",
        labels={"x": "Polarité", "y": "Subjectivité"},
    )

    result = {
        "sentiments": sentiments,
        "wordcloud": wordcloud_path,
        "sentiment_plot": json.dumps(sentiment_fig, cls=PlotlyJSONEncoder),
        "timestamp": datetime.now().isoformat(),
    }

    return jsonify(result)


if __name__ == "__main__":
    print("🚀 AIMER PRO Server démarré!")
    print("📊 Interface disponible sur: http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
