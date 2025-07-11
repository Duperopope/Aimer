#!/usr/bin/env python3
"""
AIMER - Synchronisation Simple HTTPS
Version simplifiée utilisant HTTPS au lieu de SSH
"""

import os
import subprocess
import time
from datetime import datetime
from pathlib import Path


class SimpleSync:
    def __init__(self):
        self.repo_path = Path("G:/Code/Aimer/Aimer")
        self.sync_interval = 15  # secondes
        self.running = True
        self.last_commit = None

    def log(self, message, level="INFO"):
        """Log avec timestamp et couleurs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": "\033[94m",  # Bleu
            "SUCCESS": "\033[92m",  # Vert
            "WARNING": "\033[93m",  # Jaune
            "ERROR": "\033[91m",  # Rouge
            "RESET": "\033[0m",  # Reset
        }
        color = colors.get(level, colors["INFO"])
        print(f"{color}[{timestamp}] {level}: {message}{colors['RESET']}")

    def run_git_command(self, command):
        """Exécute une commande git"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return False, "", str(e)

    def setup_https_remote(self):
        """Configure le remote en HTTPS si nécessaire"""
        self.log("🔧 Vérification de la configuration remote...", "INFO")

        # Vérifier le remote actuel
        success, stdout, stderr = self.run_git_command("git remote get-url origin")
        if success and "https://" in stdout:
            self.log("✅ Remote HTTPS déjà configuré", "SUCCESS")
            return True

        # Configurer en HTTPS
        self.log("🔄 Configuration du remote en HTTPS...", "INFO")
        success, stdout, stderr = self.run_git_command(
            "git remote set-url origin https://github.com/Duperopope/Aimer.git"
        )

        if success:
            self.log("✅ Remote HTTPS configuré avec succès", "SUCCESS")
            return True
        else:
            self.log(f"❌ Erreur configuration remote: {stderr}", "ERROR")
            return False

    def get_current_commit(self):
        """Récupère le hash du commit actuel"""
        success, stdout, stderr = self.run_git_command("git rev-parse HEAD")
        if success:
            return stdout[:8]
        return None

    def sync_with_remote(self):
        """Synchronise avec GitHub"""
        try:
            # 1. Fetch simple
            self.log("🔄 Vérification des changements...", "INFO")
            success, stdout, stderr = self.run_git_command("git fetch origin")

            if not success:
                self.log(f"⚠️ Fetch échoué: {stderr}", "WARNING")
                return False

            # 2. Vérifier les modifications locales
            success, stdout, stderr = self.run_git_command("git status --porcelain")
            if success and stdout.strip():
                self.log("📝 Modifications locales détectées", "WARNING")
                # Ne pas stash automatiquement, juste informer

            # 3. Vérifier s'il y a des nouveaux commits
            current_branch = self.get_current_branch()
            success, stdout, stderr = self.run_git_command(
                f"git rev-list HEAD..origin/{current_branch} --count"
            )

            if success and stdout.strip() != "0":
                new_commits = stdout.strip()
                self.log(f"🔔 {new_commits} nouveau(x) commit(s) disponible(s)", "SUCCESS")

                # Pull les changements
                success, stdout, stderr = self.run_git_command(f"git pull origin {current_branch}")
                if success:
                    self.log("✅ Mise à jour effectuée", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Erreur pull: {stderr}", "ERROR")
                    return False
            else:
                self.log("✅ Repository à jour", "INFO")
                return False

        except Exception as e:
            self.log(f"❌ Erreur sync: {str(e)}", "ERROR")
            return False

    def get_current_branch(self):
        """Récupère la branche actuelle"""
        success, stdout, stderr = self.run_git_command("git branch --show-current")
        if success:
            return stdout.strip()
        return "main"  # Fallback

    def start_monitoring(self):
        """Démarre la surveillance"""
        print("\n🚀 AIMER - SYNCHRONISATION SIMPLE")
        print("=" * 40)
        print(f"📁 Répertoire: {self.repo_path}")
        print(f"⏱️  Intervalle: {self.sync_interval} secondes")
        print(f"🌿 Branche: {self.get_current_branch()}")
        print("🔄 Ctrl+C pour arrêter")
        print("=" * 40)

        # Configuration initiale
        if not self.setup_https_remote():
            self.log("❌ Impossible de configurer le remote", "ERROR")
            return False

        self.last_commit = self.get_current_commit()
        self.log(f"📝 Commit initial: {self.last_commit}", "INFO")

        # Boucle de surveillance
        try:
            while self.running:
                has_changes = self.sync_with_remote()

                if has_changes:
                    new_commit = self.get_current_commit()
                    self.log(f"🔄 Nouveau commit: {new_commit}", "SUCCESS")
                    self.last_commit = new_commit

                # Attendre avant la prochaine vérification
                for i in range(self.sync_interval):
                    if not self.running:
                        break
                    time.sleep(1)

        except KeyboardInterrupt:
            self.log("🛑 Arrêt demandé par l'utilisateur", "INFO")
        except Exception as e:
            self.log(f"❌ Erreur: {str(e)}", "ERROR")
        finally:
            self.log("👋 Synchronisation arrêtée", "INFO")


def main():
    import sys

    sync = SimpleSync()

    # Gestion des arguments
    if len(sys.argv) > 2 and sys.argv[1] == "--interval":
        try:
            sync.sync_interval = int(sys.argv[2])
            print(f"⏱️ Intervalle: {sync.sync_interval}s")
        except ValueError:
            print("❌ Intervalle invalide")
            return

    sync.start_monitoring()


if __name__ == "__main__":
    main()
