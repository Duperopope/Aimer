#!/usr/bin/env python3
"""
📊 AIMER Error Dashboard
Interface de visualisation des erreurs en temps réel
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path


class ErrorDashboard:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.status_file = self.base_path / ".error_monitor_status.json"
        self.log_file = self.base_path / "error_monitor.log"

    def clear_screen(self):
        """Efface l'écran"""
        os.system("cls" if os.name == "nt" else "clear")

    def load_current_status(self):
        """Charge le statut actuel"""
        try:
            if self.status_file.exists():
                with open(self.status_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return None

    def get_recent_logs(self, lines=10):
        """Récupère les logs récents"""
        try:
            if self.log_file.exists():
                with open(self.log_file, "r", encoding="utf-8") as f:
                    all_lines = f.readlines()
                    return all_lines[-lines:] if all_lines else []
        except Exception:
            pass
        return []

    def render_dashboard(self):
        """Affiche le dashboard"""
        self.clear_screen()

        print("📊 AIMER ERROR DASHBOARD - TEMPS RÉEL")
        print("=" * 60)
        print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("")

        # Statut du monitoring
        pid_file = self.base_path / ".error_monitor.pid"
        if pid_file.exists():
            print("🟢 MONITORING ACTIF")
        else:
            print("🔴 MONITORING INACTIF")
            print("💡 Lancez: python error_monitor.py")

        print("-" * 60)

        # Statut des erreurs
        status = self.load_current_status()
        if status:
            last_check = status.get("last_check", "Inconnu")
            error_count = status.get("error_count", 0)

            if error_count == 0:
                print("✅ AUCUNE ERREUR DÉTECTÉE")
                print("🎉 Tous les systèmes sont opérationnels!")
            else:
                print(f"🚨 {error_count} ERREUR(S) DÉTECTÉE(S)")
                print("")

                errors = status.get("errors", [])
                # Grouper par type
                error_types = {}
                for error in errors:
                    error_type = error.get("type", "Unknown")
                    if error_type not in error_types:
                        error_types[error_type] = []
                    error_types[error_type].append(error)

                for error_type, type_errors in error_types.items():
                    print(f"📋 {error_type}: {len(type_errors)} erreur(s)")
                    for error in type_errors[:3]:  # Limiter à 3 par type
                        file = error.get("file", "Unknown")
                        line = error.get("line", "")
                        line_info = f" (L{line})" if line else ""
                        message = (
                            error.get("message", "")[:50] + "..."
                            if len(error.get("message", "")) > 50
                            else error.get("message", "")
                        )
                        print(f"   📄 {file}{line_info}: {message}")

                    if len(type_errors) > 3:
                        print(f"   ... et {len(type_errors) - 3} autre(s)")
                    print("")

            print(f"🕒 Dernière vérification: {last_check}")
        else:
            print("⚠️ AUCUN STATUT DISPONIBLE")
            print("💡 Le monitoring n'a peut-être pas encore démarré")

        print("-" * 60)

        # Logs récents
        print("📝 LOGS RÉCENTS:")
        recent_logs = self.get_recent_logs(5)
        if recent_logs:
            for log in recent_logs:
                print(f"   {log.strip()}")
        else:
            print("   Aucun log disponible")

        print("")
        print("-" * 60)
        print("🔄 Actualisation automatique toutes les 5 secondes")
        print("🛑 Appuyez sur Ctrl+C pour quitter")
        print("💡 Commandes disponibles:")
        print("   - python error_monitor.py        (démarrer monitoring)")
        print("   - python auto_fix_advanced.py    (correction automatique)")
        print("   - python final_checker.py        (vérification complète)")

    def run_dashboard(self):
        """Lance le dashboard en boucle"""
        try:
            while True:
                self.render_dashboard()
                time.sleep(5)  # Actualisation toutes les 5 secondes
        except KeyboardInterrupt:
            self.clear_screen()
            print("👋 Dashboard fermé")


def main():
    """Point d'entrée principal"""
    dashboard = ErrorDashboard()
    dashboard.run_dashboard()


if __name__ == "__main__":
    main()
