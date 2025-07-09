#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIMER PRO - Gestionnaire de Licence Commercial
© 2025 KairosForge - Tous droits réservés

Système de validation de licence avec protection hardware
"""

import os
import sys
import json
import hashlib
import platform
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import requests

class LicenseType:
    """Types de licences disponibles"""
    PERSONAL = "personal"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    TRIAL = "trial"

class LicenseStatus:
    """Statuts de licence"""
    VALID = "valid"
    EXPIRED = "expired"
    INVALID = "invalid"
    TRIAL_EXPIRED = "trial_expired"
    HARDWARE_MISMATCH = "hardware_mismatch"
    SERVER_ERROR = "server_error"

class LicenseManager:
    """
    Gestionnaire de licence commercial
    Gère la validation, l'activation et la protection
    """
    
    def __init__(self):
        self.logger = logging.getLogger("LicenseManager")
        
        # Configuration
        self.license_server_url = "https://api.kairosforge.com/license"  # À implémenter
        self.license_file = Path("license.dat")
        self.hardware_file = Path("hardware.dat")
        
        # Clé de chiffrement (à sécuriser en production)
        self.encryption_key = self._generate_encryption_key()
        
        # Cache licence
        self._cached_license: Optional[Dict] = None
        self._last_validation: Optional[datetime] = None
        
        # Initialisation
        self.hardware_fingerprint = self._generate_hardware_fingerprint()
        
        self.logger.info("Gestionnaire de licence initialisé")
    
    def _generate_encryption_key(self) -> bytes:
        """Génère une clé de chiffrement basée sur le système"""
        # En production, utiliser une clé plus sécurisée
        password = f"KairosForge-{platform.node()}-{platform.machine()}".encode()
        salt = b"aimer_pro_salt_2025"
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def _generate_hardware_fingerprint(self) -> str:
        """Génère une empreinte hardware unique"""
        try:
            # Collecte d'informations système
            system_info = {
                "platform": platform.platform(),
                "processor": platform.processor(),
                "machine": platform.machine(),
                "node": platform.node(),
                "mac_address": hex(uuid.getnode()),
            }
            
            # Tentative d'obtenir des infos supplémentaires
            try:
                import psutil
                system_info["cpu_count"] = psutil.cpu_count()
                system_info["memory"] = psutil.virtual_memory().total
            except ImportError:
                pass
            
            # Génération hash
            fingerprint_data = json.dumps(system_info, sort_keys=True)
            fingerprint_hash = hashlib.sha256(fingerprint_data.encode()).hexdigest()
            
            self.logger.info(f"Hardware fingerprint généré: {fingerprint_hash[:16]}...")
            return fingerprint_hash
            
        except Exception as e:
            self.logger.error(f"Erreur génération fingerprint: {e}")
            # Fallback basique
            return hashlib.sha256(f"{platform.node()}-{uuid.getnode()}".encode()).hexdigest()
    
    def validate_license(self) -> bool:
        """
        Valide la licence utilisateur
        Retourne True si la licence est valide
        """
        try:
            self.logger.info("Validation de la licence...")
            
            # Vérifier cache récent
            if self._is_cache_valid():
                self.logger.info("Utilisation du cache de licence")
                return self._cached_license.get("status") == LicenseStatus.VALID
            
            # Charger licence locale
            license_data = self._load_local_license()
            if not license_data:
                self.logger.warning("Aucune licence locale trouvée")
                return self._handle_no_license()
            
            # Validation locale
            if not self._validate_local_license(license_data):
                self.logger.error("Licence locale invalide")
                return False
            
            # Validation serveur (si connexion disponible)
            server_validation = self._validate_with_server(license_data)
            
            # Mise à jour cache
            self._update_cache(license_data, server_validation)
            
            # Résultat final
            is_valid = license_data.get("status") == LicenseStatus.VALID
            self.logger.info(f"Licence {'valide' if is_valid else 'invalide'}")
            
            return is_valid
            
        except Exception as e:
            self.logger.error(f"Erreur validation licence: {e}")
            return False
    
    def _is_cache_valid(self) -> bool:
        """Vérifie si le cache de licence est encore valide"""
        if not self._cached_license or not self._last_validation:
            return False
        
        # Cache valide pendant 1 heure
        cache_duration = timedelta(hours=1)
        return datetime.now() - self._last_validation < cache_duration
    
    def _load_local_license(self) -> Optional[Dict]:
        """Charge la licence depuis le fichier local"""
        try:
            if not self.license_file.exists():
                return None
            
            # Lire fichier chiffré
            with open(self.license_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Déchiffrer
            fernet = Fernet(self.encryption_key)
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # Parser JSON
            license_data = json.loads(decrypted_data.decode())
            
            self.logger.info("Licence locale chargée")
            return license_data
            
        except Exception as e:
            self.logger.error(f"Erreur chargement licence: {e}")
            return None
    
    def _validate_local_license(self, license_data: Dict) -> bool:
        """Valide la licence localement"""
        try:
            # Vérifications de base
            required_fields = ["license_key", "license_type", "expiry_date", "hardware_hash"]
            for field in required_fields:
                if field not in license_data:
                    self.logger.error(f"Champ manquant: {field}")
                    return False
            
            # Vérifier hardware
            if license_data["hardware_hash"] != self.hardware_fingerprint:
                self.logger.error("Hardware fingerprint ne correspond pas")
                license_data["status"] = LicenseStatus.HARDWARE_MISMATCH
                return False
            
            # Vérifier expiration
            expiry_date = datetime.fromisoformat(license_data["expiry_date"])
            if datetime.now() > expiry_date:
                self.logger.error("Licence expirée")
                license_data["status"] = LicenseStatus.EXPIRED
                return False
            
            # Licence valide localement
            license_data["status"] = LicenseStatus.VALID
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur validation locale: {e}")
            return False
    
    def _validate_with_server(self, license_data: Dict) -> bool:
        """Valide la licence avec le serveur (si disponible)"""
        try:
            # Préparer données de validation
            validation_data = {
                "license_key": license_data["license_key"],
                "hardware_hash": self.hardware_fingerprint,
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat()
            }
            
            # Requête serveur (timeout court)
            response = requests.post(
                f"{self.license_server_url}/validate",
                json=validation_data,
                timeout=5
            )
            
            if response.status_code == 200:
                server_response = response.json()
                if server_response.get("valid", False):
                    self.logger.info("Licence validée par le serveur")
                    return True
                else:
                    self.logger.warning("Licence rejetée par le serveur")
                    return False
            else:
                self.logger.warning(f"Erreur serveur: {response.status_code}")
                return True  # Continuer en mode offline
            
        except requests.RequestException as e:
            self.logger.warning(f"Impossible de contacter le serveur: {e}")
            return True  # Mode offline, continuer avec validation locale
        except Exception as e:
            self.logger.error(f"Erreur validation serveur: {e}")
            return True
    
    def _handle_no_license(self) -> bool:
        """Gère le cas où aucune licence n'est trouvée"""
        # Vérifier si trial disponible
        if self._can_start_trial():
            self.logger.info("Démarrage du mode trial")
            self._create_trial_license()
            return True
        else:
            self.logger.error("Aucune licence valide disponible")
            return False
    
    def _can_start_trial(self) -> bool:
        """Vérifie si un trial peut être démarré"""
        # Vérifier si trial déjà utilisé
        trial_marker = Path("trial_used.dat")
        return not trial_marker.exists()
    
    def _create_trial_license(self):
        """Crée une licence trial temporaire"""
        try:
            trial_data = {
                "license_key": f"TRIAL-{uuid.uuid4().hex[:16].upper()}",
                "license_type": LicenseType.TRIAL,
                "hardware_hash": self.hardware_fingerprint,
                "expiry_date": (datetime.now() + timedelta(days=14)).isoformat(),
                "status": LicenseStatus.VALID,
                "created_date": datetime.now().isoformat()
            }
            
            # Sauvegarder licence trial
            self._save_license(trial_data)
            
            # Marquer trial comme utilisé
            Path("trial_used.dat").touch()
            
            self.logger.info("Licence trial créée (14 jours)")
            
        except Exception as e:
            self.logger.error(f"Erreur création trial: {e}")
    
    def _save_license(self, license_data: Dict):
        """Sauvegarde la licence de manière chiffrée"""
        try:
            # Chiffrer données
            fernet = Fernet(self.encryption_key)
            json_data = json.dumps(license_data).encode()
            encrypted_data = fernet.encrypt(json_data)
            
            # Sauvegarder
            with open(self.license_file, 'wb') as f:
                f.write(encrypted_data)
            
            self.logger.info("Licence sauvegardée")
            
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde licence: {e}")
    
    def _update_cache(self, license_data: Dict, server_validation: bool):
        """Met à jour le cache de licence"""
        self._cached_license = license_data.copy()
        self._last_validation = datetime.now()
    
    def get_license_info(self) -> Dict:
        """Retourne les informations de licence"""
        if self._cached_license:
            return {
                "license_type": self._cached_license.get("license_type", "unknown"),
                "status": self._cached_license.get("status", "unknown"),
                "expiry_date": self._cached_license.get("expiry_date", "unknown"),
                "days_remaining": self._get_days_remaining()
            }
        else:
            return {
                "license_type": "none",
                "status": "invalid",
                "expiry_date": "unknown",
                "days_remaining": 0
            }
    
    def _get_days_remaining(self) -> int:
        """Calcule les jours restants de licence"""
        try:
            if not self._cached_license:
                return 0
            
            expiry_date = datetime.fromisoformat(self._cached_license["expiry_date"])
            remaining = expiry_date - datetime.now()
            return max(0, remaining.days)
            
        except Exception:
            return 0
    
    def activate_license(self, license_key: str) -> Tuple[bool, str]:
        """
        Active une nouvelle licence
        Retourne (succès, message)
        """
        try:
            self.logger.info(f"Activation licence: {license_key[:8]}...")
            
            # Préparer données d'activation
            activation_data = {
                "license_key": license_key,
                "hardware_hash": self.hardware_fingerprint,
                "platform": platform.platform(),
                "version": "1.0.0"
            }
            
            # Requête d'activation
            response = requests.post(
                f"{self.license_server_url}/activate",
                json=activation_data,
                timeout=10
            )
            
            if response.status_code == 200:
                activation_response = response.json()
                
                if activation_response.get("success", False):
                    # Créer licence locale
                    license_data = {
                        "license_key": license_key,
                        "license_type": activation_response.get("license_type", LicenseType.PERSONAL),
                        "hardware_hash": self.hardware_fingerprint,
                        "expiry_date": activation_response.get("expiry_date"),
                        "status": LicenseStatus.VALID,
                        "activated_date": datetime.now().isoformat()
                    }
                    
                    # Sauvegarder
                    self._save_license(license_data)
                    
                    # Mettre à jour cache
                    self._cached_license = license_data
                    self._last_validation = datetime.now()
                    
                    self.logger.info("Licence activée avec succès")
                    return True, "Licence activée avec succès"
                else:
                    error_msg = activation_response.get("error", "Activation échouée")
                    self.logger.error(f"Activation échouée: {error_msg}")
                    return False, error_msg
            else:
                self.logger.error(f"Erreur serveur activation: {response.status_code}")
                return False, "Erreur de communication avec le serveur"
            
        except requests.RequestException as e:
            self.logger.error(f"Erreur réseau activation: {e}")
            return False, "Impossible de contacter le serveur d'activation"
        except Exception as e:
            self.logger.error(f"Erreur activation: {e}")
            return False, "Erreur interne lors de l'activation"
    
    def deactivate_license(self) -> bool:
        """Désactive la licence actuelle"""
        try:
            # Supprimer fichiers de licence
            if self.license_file.exists():
                self.license_file.unlink()
            
            # Vider cache
            self._cached_license = None
            self._last_validation = None
            
            self.logger.info("Licence désactivée")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur désactivation: {e}")
            return False

def create_license_manager() -> LicenseManager:
    """Factory pour créer le gestionnaire de licence"""
    return LicenseManager()
