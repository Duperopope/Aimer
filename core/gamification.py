#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Système de Gamification
© 2025 - Licence Apache 2.0

Système complet de progression, badges et récompenses
"""

import json
import sqlite3
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

from .logger import Logger

class GamificationSystem:
    """Système de gamification complet"""

    def __init__(self, db_path: str = "gamification.db"):
        self.logger = Logger("GamificationSystem")
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialise la base de données de gamification"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Table des utilisateurs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    level INTEGER DEFAULT 1,
                    xp INTEGER DEFAULT 0,
                    total_xp INTEGER DEFAULT 0,
                    coins INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Table des badges
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS badges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    icon TEXT,
                    category TEXT,
                    rarity TEXT DEFAULT 'common',
                    requirement_type TEXT,
                    requirement_value INTEGER,
                    xp_reward INTEGER DEFAULT 0,
                    coin_reward INTEGER DEFAULT 0
                )
            ''')

            # Table des badges utilisateurs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_badges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    badge_id INTEGER,
                    earned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (badge_id) REFERENCES badges (id)
                )
            ''')

            # Table des activités
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    activity_type TEXT,
                    description TEXT,
                    xp_gained INTEGER DEFAULT 0,
                    coins_gained INTEGER DEFAULT 0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            # Table des défis
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS challenges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    type TEXT,
                    target_value INTEGER,
                    xp_reward INTEGER,
                    coin_reward INTEGER,
                    start_date DATETIME,
                    end_date DATETIME,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')

            # Table des défis utilisateurs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_challenges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    challenge_id INTEGER,
                    progress INTEGER DEFAULT 0,
                    completed BOOLEAN DEFAULT 0,
                    completed_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (challenge_id) REFERENCES challenges (id)
                )
            ''')

            # Table des statistiques
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    detections_count INTEGER DEFAULT 0,
                    models_trained INTEGER DEFAULT 0,
                    datasets_created INTEGER DEFAULT 0,
                    cheats_created INTEGER DEFAULT 0,
                    best_accuracy REAL DEFAULT 0.0,
                    best_speed INTEGER DEFAULT 0,
                    total_time_spent INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            conn.commit()
            conn.close()

            # Initialiser les badges et défis par défaut
            self.init_default_badges()
            self.init_daily_challenges()

            self.logger.info("Base de données gamification initialisée")

        except Exception as e:
            self.logger.error(f"Erreur initialisation DB: {e}")

    def init_default_badges(self):
        """Initialise les badges par défaut"""
        default_badges = [
            # Badges de débutant
            {
                'name': 'Premier Pas',
                'description': 'Première détection d\'objet réalisée',
                'icon': '👶',
                'category': 'beginners',
                'rarity': 'common',
                'requirement_type': 'detections',
                'requirement_value': 1,
                'xp_reward': 10,
                'coin_reward': 5
            },
            {
                'name': 'Explorateur',
                'description': '10 détections réalisées avec succès',
                'icon': '🔍',
                'category': 'beginners',
                'rarity': 'common',
                'requirement_type': 'detections',
                'requirement_value': 10,
                'xp_reward': 50,
                'coin_reward': 25
            },

            # Badges de progression
            {
                'name': 'Détecteur Expérimenté',
                'description': '100 détections réalisées',
                'icon': '🎯',
                'category': 'progression',
                'rarity': 'uncommon',
                'requirement_type': 'detections',
                'requirement_value': 100,
                'xp_reward': 200,
                'coin_reward': 100
            },
            {
                'name': 'Maître Détecteur',
                'description': '1000 détections réalisées',
                'icon': '🏆',
                'category': 'progression',
                'rarity': 'rare',
                'requirement_type': 'detections',
                'requirement_value': 1000,
                'xp_reward': 500,
                'coin_reward': 250
            },

            # Badges de formation
            {
                'name': 'Formateur IA',
                'description': 'Premier modèle entraîné avec succès',
                'icon': '🧠',
                'category': 'training',
                'rarity': 'uncommon',
                'requirement_type': 'models_trained',
                'requirement_value': 1,
                'xp_reward': 100,
                'coin_reward': 50
            },
            {
                'name': 'Maître Formateur',
                'description': '10 modèles entraînés',
                'icon': '🎓',
                'category': 'training',
                'rarity': 'rare',
                'requirement_type': 'models_trained',
                'requirement_value': 10,
                'xp_reward': 300,
                'coin_reward': 150
            },

            # Badges de précision
            {
                'name': 'Œil de Lynx',
                'description': 'Détection avec 95% de précision',
                'icon': '👁️',
                'category': 'precision',
                'rarity': 'rare',
                'requirement_type': 'accuracy',
                'requirement_value': 95,
                'xp_reward': 200,
                'coin_reward': 100
            },
            {
                'name': 'Perfection Absolue',
                'description': 'Détection avec 99% de précision',
                'icon': '⭐',
                'category': 'precision',
                'rarity': 'epic',
                'requirement_type': 'accuracy',
                'requirement_value': 99,
                'xp_reward': 500,
                'coin_reward': 300
            },

            # Badges de vitesse
            {
                'name': 'Éclair',
                'description': 'Détection en moins de 100ms',
                'icon': '⚡',
                'category': 'speed',
                'rarity': 'uncommon',
                'requirement_type': 'speed',
                'requirement_value': 100,
                'xp_reward': 150,
                'coin_reward': 75
            },

            # Badges spéciaux
            {
                'name': 'Créateur de Données',
                'description': 'Premier dataset personnalisé créé',
                'icon': '🎨',
                'category': 'creation',
                'rarity': 'uncommon',
                'requirement_type': 'datasets_created',
                'requirement_value': 1,
                'xp_reward': 100,
                'coin_reward': 50
            },
            {
                'name': 'Hackeur Éthique',
                'description': 'Premier cheat de computer vision créé',
                'icon': '💻',
                'category': 'gaming',
                'rarity': 'rare',
                'requirement_type': 'cheats_created',
                'requirement_value': 1,
                'xp_reward': 200,
                'coin_reward': 100
            }
        ]

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for badge in default_badges:
                cursor.execute('''
                    INSERT OR IGNORE INTO badges
                    (name, description, icon, category, rarity, requirement_type, requirement_value, xp_reward, coin_reward)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    badge['name'], badge['description'], badge['icon'], badge['category'],
                    badge['rarity'], badge['requirement_type'], badge['requirement_value'],
                    badge['xp_reward'], badge['coin_reward']
                ))

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Erreur initialisation badges: {e}")

    def init_daily_challenges(self):
        """Initialise les défis quotidiens"""
        daily_challenges = [
            {
                'name': 'Détecteur Quotidien',
                'description': 'Réalise 20 détections aujourd\'hui',
                'type': 'daily',
                'target_value': 20,
                'xp_reward': 100,
                'coin_reward': 50
            },
            {
                'name': 'Précision Parfaite',
                'description': 'Atteins 90% de précision sur 10 détections',
                'type': 'daily',
                'target_value': 90,
                'xp_reward': 150,
                'coin_reward': 75
            },
            {
                'name': 'Marathon IA',
                'description': 'Utilise l\'application pendant 30 minutes',
                'type': 'daily',
                'target_value': 30,
                'xp_reward': 80,
                'coin_reward': 40
            }
        ]

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)

            for challenge in daily_challenges:
                cursor.execute('''
                    INSERT OR IGNORE INTO challenges
                    (name, description, type, target_value, xp_reward, coin_reward, start_date, end_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    challenge['name'], challenge['description'], challenge['type'],
                    challenge['target_value'], challenge['xp_reward'], challenge['coin_reward'],
                    today, tomorrow
                ))

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Erreur initialisation défis: {e}")

    def create_user(self, username: str) -> Optional[int]:
        """Crée un nouvel utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO users (username) VALUES (?)
            ''', (username,))

            user_id = cursor.lastrowid

            # Initialiser les statistiques
            cursor.execute('''
                INSERT INTO user_stats (user_id) VALUES (?)
            ''', (user_id,))

            # Initialiser les défis actifs pour l'utilisateur
            cursor.execute('''
                INSERT INTO user_challenges (user_id, challenge_id, progress)
                SELECT ?, id, 0 FROM challenges WHERE is_active = 1
            ''', (user_id,))

            conn.commit()
            conn.close()

            self.logger.info(f"Utilisateur {username} créé avec ID {user_id}")
            return user_id

        except sqlite3.IntegrityError:
            self.logger.warning(f"Utilisateur {username} existe déjà")
            return None
        except Exception as e:
            self.logger.error(f"Erreur création utilisateur: {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[int]:
        """Récupère l'ID utilisateur par nom"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()

            conn.close()

            return result[0] if result else None

        except Exception as e:
            self.logger.error(f"Erreur récupération utilisateur: {e}")
            return None

    def get_or_create_user(self, username: str) -> int:
        """Récupère ou crée un utilisateur"""
        user_id = self.get_user_by_username(username)
        if user_id is None:
            user_id = self.create_user(username)
        return user_id

    def add_xp(self, user_id: int, amount: int, activity_type: str, description: str = "") -> bool:
        """Ajoute de l'XP à un utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Calculer les coins (1 XP = 0.1 coins)
            coins_gained = int(amount * 0.1)

            # Récupérer les données actuelles
            cursor.execute('SELECT level, xp, total_xp FROM users WHERE id = ?', (user_id,))
            current_level, current_xp, total_xp = cursor.fetchone()

            # Calculer le nouveau total XP
            new_total_xp = total_xp + amount
            new_current_xp = current_xp + amount

            # Calculer le nouveau niveau
            new_level = self.calculate_level(new_total_xp)

            # Si niveau supérieur, ajuster l'XP actuelle
            if new_level > current_level:
                new_current_xp = new_total_xp - self.xp_for_level(new_level)

                # Bonus de niveau
                level_bonus = (new_level - current_level) * 50
                coins_gained += level_bonus

            # Mettre à jour l'utilisateur
            cursor.execute('''
                UPDATE users
                SET level = ?, xp = ?, total_xp = ?, coins = coins + ?
                WHERE id = ?
            ''', (new_level, new_current_xp, new_total_xp, coins_gained, user_id))

            # Enregistrer l'activité
            cursor.execute('''
                INSERT INTO activities (user_id, activity_type, description, xp_gained, coins_gained)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, activity_type, description, amount, coins_gained))

            conn.commit()
            conn.close()

            # Vérifier les badges
            self.check_badges(user_id)

            level_up = new_level > current_level
            if level_up:
                self.logger.info(f"Utilisateur {user_id} monte au niveau {new_level}!")

            return level_up

        except Exception as e:
            self.logger.error(f"Erreur ajout XP: {e}")
            return False

    def calculate_level(self, total_xp: int) -> int:
        """Calcule le niveau basé sur l'XP total"""
        # Formule : Level = floor(sqrt(total_xp / 100)) + 1
        return int((total_xp / 100) ** 0.5) + 1

    def xp_for_level(self, level: int) -> int:
        """XP nécessaire pour atteindre un niveau"""
        return ((level - 1) ** 2) * 100

    def check_badges(self, user_id: int):
        """Vérifie et attribue les badges"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Récupérer les statistiques utilisateur
            stats = self.get_user_stats(user_id)

            # Vérifier tous les badges
            cursor.execute('SELECT * FROM badges')
            badges = cursor.fetchall()

            for badge in badges:
                badge_id = badge[0]
                requirement_type = badge[5]
                requirement_value = badge[6]

                # Vérifier si l'utilisateur a déjà ce badge
                cursor.execute('''
                    SELECT COUNT(*) FROM user_badges
                    WHERE user_id = ? AND badge_id = ?
                ''', (user_id, badge_id))

                if cursor.fetchone()[0] > 0:
                    continue  # Badge déjà obtenu

                # Vérifier les conditions
                earned = False

                if requirement_type == 'detections' and stats['detections_count'] >= requirement_value:
                    earned = True
                elif requirement_type == 'models_trained' and stats['models_trained'] >= requirement_value:
                    earned = True
                elif requirement_type == 'accuracy' and stats['best_accuracy'] >= requirement_value:
                    earned = True
                elif requirement_type == 'speed' and stats['best_speed'] <= requirement_value and stats['best_speed'] > 0:
                    earned = True
                elif requirement_type == 'datasets_created' and stats['datasets_created'] >= requirement_value:
                    earned = True
                elif requirement_type == 'cheats_created' and stats['cheats_created'] >= requirement_value:
                    earned = True

                if earned:
                    # Attribuer le badge
                    cursor.execute('''
                        INSERT INTO user_badges (user_id, badge_id)
                        VALUES (?, ?)
                    ''', (user_id, badge_id))

                    # Donner les récompenses
                    xp_reward = badge[7]
                    coin_reward = badge[8]

                    cursor.execute('''
                        UPDATE users
                        SET xp = xp + ?, total_xp = total_xp + ?, coins = coins + ?
                        WHERE id = ?
                    ''', (xp_reward, xp_reward, coin_reward, user_id))

                    cursor.execute('''
                        INSERT INTO activities (user_id, activity_type, description, xp_gained, coins_gained)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (user_id, 'badge_earned', f'Badge "{badge[1]}" obtenu!', xp_reward, coin_reward))

                    self.logger.info(f"Badge {badge[1]} attribué à l'utilisateur {user_id}")

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Erreur vérification badges: {e}")

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Récupère les statistiques utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT detections_count, models_trained, datasets_created, cheats_created,
                       best_accuracy, best_speed, total_time_spent
                FROM user_stats WHERE user_id = ?
            ''', (user_id,))

            result = cursor.fetchone()
            conn.close()

            if result:
                return {
                    'detections_count': result[0],
                    'models_trained': result[1],
                    'datasets_created': result[2],
                    'cheats_created': result[3],
                    'best_accuracy': result[4],
                    'best_speed': result[5],
                    'total_time_spent': result[6]
                }
            else:
                return {
                    'detections_count': 0,
                    'models_trained': 0,
                    'datasets_created': 0,
                    'cheats_created': 0,
                    'best_accuracy': 0.0,
                    'best_speed': 0,
                    'total_time_spent': 0
                }

        except Exception as e:
            self.logger.error(f"Erreur récupération stats: {e}")
            return {}

    def update_user_stats(self, user_id: int, **kwargs):
        """Met à jour les statistiques utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Construire la requête dynamiquement
            updates = []
            values = []

            for key, value in kwargs.items():
                if key in ['detections_count', 'models_trained', 'datasets_created', 'cheats_created']:
                    updates.append(f"{key} = {key} + ?")
                    values.append(value)
                elif key in ['best_accuracy', 'best_speed', 'total_time_spent']:
                    updates.append(f"{key} = ?")
                    values.append(value)

            if updates:
                query = f"UPDATE user_stats SET {', '.join(updates)} WHERE user_id = ?"
                values.append(user_id)

                cursor.execute(query, values)
                conn.commit()

            conn.close()

        except Exception as e:
            self.logger.error(f"Erreur mise à jour stats: {e}")

    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Récupère le profil complet d'un utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Infos utilisateur
            cursor.execute('''
                SELECT username, level, xp, total_xp, coins, created_at, last_login
                FROM users WHERE id = ?
            ''', (user_id,))

            user_data = cursor.fetchone()
            if not user_data:
                return None

            # Badges obtenus
            cursor.execute('''
                SELECT b.name, b.description, b.icon, b.rarity, ub.earned_at
                FROM user_badges ub
                JOIN badges b ON ub.badge_id = b.id
                WHERE ub.user_id = ?
                ORDER BY ub.earned_at DESC
            ''', (user_id,))

            badges = cursor.fetchall()

            # Statistiques
            stats = self.get_user_stats(user_id)

            conn.close()

            return {
                'username': user_data[0],
                'level': user_data[1],
                'xp': user_data[2],
                'total_xp': user_data[3],
                'coins': user_data[4],
                'created_at': user_data[5],
                'last_login': user_data[6],
                'badges': [
                    {
                        'name': badge[0],
                        'description': badge[1],
                        'icon': badge[2],
                        'rarity': badge[3],
                        'earned_at': badge[4]
                    } for badge in badges
                ],
                'stats': stats
            }

        except Exception as e:
            self.logger.error(f"Erreur récupération profil: {e}")
            return None

    def record_activity(self, user_id: int, activity_type: str, details: str = "", **stats_updates) -> Dict[str, Any]:
        """Enregistre une activité et donne de l'XP"""
        xp_rewards = {
            'detection': 5,
            'training': 50,
            'dataset_creation': 100,
            'cheat_creation': 75,
            'login': 10,
            'daily_challenge': 100
        }

        xp_amount = xp_rewards.get(activity_type, 1)
        description = f"Activité: {activity_type}"

        if details:
            description += f" - {details}"

        # Ajouter XP
        level_up = self.add_xp(user_id, xp_amount, activity_type, description)

        # Mettre à jour les statistiques
        if stats_updates:
            self.update_user_stats(user_id, **stats_updates)

        return {
            'xp_gained': xp_amount,
            'level_up': level_up,
            'description': description
        }

    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupère le classement"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT username, level, total_xp,
                       (SELECT COUNT(*) FROM user_badges WHERE user_id = users.id) as badges_count
                FROM users
                ORDER BY total_xp DESC
                LIMIT ?
            ''', (limit,))

            leaderboard = []
            for i, row in enumerate(cursor.fetchall()):
                leaderboard.append({
                    'rank': i + 1,
                    'username': row[0],
                    'level': row[1],
                    'total_xp': row[2],
                    'badges_count': row[3]
                })

            conn.close()

            return leaderboard

        except Exception as e:
            self.logger.error(f"Erreur récupération leaderboard: {e}")
            return []
