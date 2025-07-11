#!/usr/bin/env python3
"""
🚀 AIMER Auto-Connect
Connexion automatique au système de monitoring d'erreurs
Lance tous les systèmes de surveillance sans intervention
"""

import os
import subprocess
import sys
import threading
import time
from pathlib import Path


class AimerAutoConnect:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.processes = {}
        self.running = True

    def log(self, message):
        """Log avec timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")

    def check_requirements(self):
        """Vérifie que tous les requirements sont installés"""
        self.log("🔍 Vérification des requirements...")

        try:
            # Installer automatiquement les packages manquants
            required_packages = [
                "rich",
                "cryptography",
                "psutil",
                "pyperclip",
                "click",
                "python-dotenv",
                "pydantic",
            ]

            for package in required_packages:
                try:
                    __import__(package.replace("-", "_"))
                    self.log(f"✅ {package} OK")
                except ImportError:
                    self.log(f"📦 Installation de {package}...")
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", package],
                        check=True,
                        capture_output=True,
                    )
                    self.log(f"✅ {package} installé")

            return True

        except Exception as e:
            self.log(f"❌ Erreur requirements: {e}")
            return False

    def start_error_monitor(self):
        """Lance le monitoring d'erreurs en arrière-plan"""
        self.log("🔍 Démarrage du monitoring d'erreurs...")

        try:
            # Vérifier si déjà actif
            pid_file = self.base_path / ".error_monitor.pid"
            if pid_file.exists():
                self.log("⚠️ Monitoring déjà actif")
                return True

            # Lancer le monitoring en arrière-plan
            process = subprocess.Popen(
                [sys.executable, "error_monitor.py"],
                cwd=self.base_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0,
            )

            self.processes["error_monitor"] = process
            self.log("✅ Monitoring d'erreurs démarré")

            # Attendre un peu pour vérifier que ça fonctionne
            time.sleep(3)
            if process.poll() is None:
                self.log("🟢 Monitoring actif et fonctionnel")
                return True
            else:
                self.log("❌ Échec démarrage monitoring")
                return False

        except Exception as e:
            self.log(f"❌ Erreur monitoring: {e}")
            return False

    def run_initial_health_check(self):
        """Lance une vérification de santé initiale"""
        self.log("🏥 Vérification de santé initiale...")

        try:
            result = subprocess.run(
                [sys.executable, "final_checker.py"],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                self.log("✅ Vérification de santé réussie")
                # Extraire le score du résultat
                output_lines = result.stdout.split("\n")
                for line in output_lines:
                    if "Score:" in line:
                        self.log(f"📊 {line.strip()}")
                        break
                return True
            else:
                self.log("⚠️ Vérification de santé avec avertissements")
                return False

        except Exception as e:
            self.log(f"❌ Erreur vérification: {e}")
            return False

    def auto_fix_critical_errors(self):
        """Lance une correction automatique des erreurs critiques"""
        self.log("🔧 Correction automatique des erreurs critiques...")

        try:
            result = subprocess.run(
                [sys.executable, "auto_fix_advanced.py"],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                self.log("✅ Correction automatique terminée")
                return True
            else:
                self.log("⚠️ Correction avec avertissements")
                return False

        except Exception as e:
            self.log(f"❌ Erreur correction: {e}")
            return False

    def start_dashboard_option(self):
        """Propose de lancer le dashboard"""
        self.log("📊 Dashboard d'erreurs disponible")
        self.log("💡 Pour voir le dashboard: python error_dashboard.py")
        self.log("💡 Ou utilisez: start_error_monitor.bat")

    def monitor_system_health(self):
        """Surveille la santé du système en arrière-plan"""
        while self.running:
            try:
                time.sleep(60)  # Vérification toutes les minutes

                # Vérifier que le monitoring tourne toujours
                pid_file = self.base_path / ".error_monitor.pid"
                if not pid_file.exists() and "error_monitor" in self.processes:
                    self.log("⚠️ Monitoring arrêté, redémarrage...")
                    self.start_error_monitor()

            except Exception as e:
                self.log(f"❌ Erreur surveillance: {e}")

    def setup_vscode_integration(self):
        """Configure l'intégration VS Code pour le monitoring"""
        self.log("🔧 Configuration de l'intégration VS Code...")

        try:
            vscode_dir = self.base_path / ".vscode"
            vscode_dir.mkdir(exist_ok=True)

            # Ajouter des tâches pour le monitoring
            tasks_file = vscode_dir / "tasks.json"

            if tasks_file.exists():
                import json

                with open(tasks_file, "r", encoding="utf-8") as f:
                    tasks = json.load(f)
            else:
                tasks = {"version": "2.0.0", "tasks": []}

            # Ajouter les tâches de monitoring
            monitoring_tasks = [
                {
                    "label": "AIMER: Start Error Monitor",
                    "type": "shell",
                    "command": "python",
                    "args": ["error_monitor.py"],
                    "group": "build",
                    "isBackground": True,
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "new",
                    },
                },
                {
                    "label": "AIMER: Error Dashboard",
                    "type": "shell",
                    "command": "python",
                    "args": ["error_dashboard.py"],
                    "group": "build",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": True,
                        "panel": "new",
                    },
                },
                {
                    "label": "AIMER: Auto-Connect",
                    "type": "shell",
                    "command": "python",
                    "args": ["auto_connect.py"],
                    "group": "build",
                },
            ]

            # Ajouter sans dupliquer
            existing_labels = [task.get("label", "") for task in tasks.get("tasks", [])]
            for task in monitoring_tasks:
                if task["label"] not in existing_labels:
                    tasks["tasks"].append(task)

            with open(tasks_file, "w", encoding="utf-8") as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)

            self.log("✅ Tâches VS Code configurées")
            return True

        except Exception as e:
            self.log(f"❌ Erreur config VS Code: {e}")
            return False

    def connect_and_monitor(self):
        """Lance la connexion complète et le monitoring"""
        self.log("🚀 AIMER Auto-Connect - Démarrage")
        self.log("=" * 50)

        # Étape 1: Vérifier les requirements
        if not self.check_requirements():
            self.log("💥 Échec vérification requirements")
            return False

        # Étape 2: Correction préventive
        self.auto_fix_critical_errors()

        # Étape 3: Vérification de santé
        self.run_initial_health_check()

        # Étape 4: Configuration VS Code
        self.setup_vscode_integration()

        # Étape 5: Démarrage du monitoring
        if not self.start_error_monitor():
            self.log("💥 Échec démarrage monitoring")
            return False

        # Étape 6: Informations pour l'utilisateur
        self.start_dashboard_option()

        self.log("=" * 50)
        self.log("🎉 AIMER Auto-Connect terminé avec succès!")
        self.log("🔍 Monitoring d'erreurs actif en arrière-plan")
        self.log("📊 Dashboard disponible via: python error_dashboard.py")
        self.log("🔧 Tâches VS Code configurées")
        self.log("💡 Le système surveille maintenant automatiquement:")
        self.log("   • Erreurs de syntaxe Python")
        self.log("   • Imports manquants")
        self.log("   • Erreurs YAML")
        self.log("   • Auto-correction des erreurs critiques")
        self.log("")
        self.log("🛑 Le monitoring continuera en arrière-plan")
        self.log("📱 Utilisez le dashboard pour voir les erreurs en temps réel")

        # Démarrer la surveillance de santé
        health_thread = threading.Thread(target=self.monitor_system_health, daemon=True)
        health_thread.start()

        return True

    def cleanup(self):
        """Nettoie les processus lors de l'arrêt"""
        self.running = False
        for name, process in self.processes.items():
            try:
                process.terminate()
                self.log(f"🛑 Arrêt de {name}")
            except Exception:
                pass


def main():
    """Point d'entrée principal"""
    connector = AimerAutoConnect()

    try:
        success = connector.connect_and_monitor()

        if success:
            print("\n" + "=" * 50)
            print("✨ CONNEXION AUTOMATIQUE RÉUSSIE!")
            print("🔍 Monitoring actif - Erreurs surveillées en temps réel")
            print("📊 Dashboard: python error_dashboard.py")
            print("🛑 Ctrl+C pour quitter ce script (monitoring continue)")
            print("=" * 50)

            # Garder le script actif pour la surveillance
            try:
                while True:
                    time.sleep(10)
            except KeyboardInterrupt:
                print("\n👋 Script Auto-Connect arrêté")
                print("🔍 Le monitoring continue en arrière-plan")
        else:
            print("\n❌ Échec de la connexion automatique")
            return 1

    except Exception as e:
        print(f"\n💥 Erreur fatale: {e}")
        return 1
    finally:
        connector.cleanup()

    return 0


if __name__ == "__main__":
    sys.exit(main())
