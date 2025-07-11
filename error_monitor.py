#!/usr/bin/env python3
"""
🔍 AIMER Real-Time Error Monitor
Surveillance en temps réel des erreurs VS Code et Python
Fonctionne de manière autonome sans intervention utilisateur
"""

import json
import os
import queue
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path


class AimerErrorMonitor:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.error_log_file = self.base_path / "error_monitor.log"
        self.status_file = self.base_path / ".error_monitor_status.json"
        self.errors_queue = queue.Queue()
        self.running = True
        self.last_errors = {}

    def log_message(self, message, level="INFO"):
        """Log des messages avec timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)

        try:
            with open(self.error_log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception:
            pass

    def check_python_syntax_errors(self):
        """Vérifie les erreurs de syntaxe Python"""
        python_files = list(self.base_path.glob("*.py"))
        errors_found = []

        for py_file in python_files:
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Tenter de compiler
                compile(content, str(py_file), "exec")

            except SyntaxError as e:
                error_info = {
                    "file": str(py_file.name),
                    "type": "SyntaxError",
                    "line": e.lineno,
                    "message": str(e.msg),
                    "timestamp": datetime.now().isoformat(),
                }
                errors_found.append(error_info)

            except Exception as e:
                error_info = {
                    "file": str(py_file.name),
                    "type": "CompileError",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
                errors_found.append(error_info)

        return errors_found

    def check_yaml_syntax_errors(self):
        """Vérifie les erreurs YAML"""
        workflows_dir = self.base_path / ".github" / "workflows"
        errors_found = []

        if workflows_dir.exists():
            for yaml_file in workflows_dir.glob("*.yml"):
                try:
                    # Vérification basique des patterns courants d'erreurs YAML
                    content = yaml_file.read_text(encoding="utf-8")

                    # Détecter des problèmes courants
                    lines = content.split("\n")
                    for i, line in enumerate(lines, 1):
                        # Vérifier l'indentation
                        if line.strip() and line.startswith(" ") and not line.startswith("  "):
                            if ":" in line:
                                error_info = {
                                    "file": str(yaml_file.name),
                                    "type": "YAMLIndentationError",
                                    "line": i,
                                    "message": "Possible indentation error",
                                    "timestamp": datetime.now().isoformat(),
                                }
                                errors_found.append(error_info)

                except Exception as e:
                    error_info = {
                        "file": str(yaml_file.name),
                        "type": "YAMLError",
                        "message": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                    errors_found.append(error_info)

        return errors_found

    def check_import_errors(self):
        """Vérifie les erreurs d'imports Python"""
        python_files = list(self.base_path.glob("*.py"))
        errors_found = []

        for py_file in python_files:
            try:
                # Exécuter une vérification d'imports avec subprocess
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(py_file)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode != 0 and result.stderr:
                    error_info = {
                        "file": str(py_file.name),
                        "type": "ImportError",
                        "message": result.stderr.strip(),
                        "timestamp": datetime.now().isoformat(),
                    }
                    errors_found.append(error_info)

            except Exception as e:
                error_info = {
                    "file": str(py_file.name),
                    "type": "CheckError",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
                errors_found.append(error_info)

        return errors_found

    def run_flake8_check(self):
        """Lance Flake8 pour vérifier le style"""
        errors_found = []

        try:
            result = subprocess.run(
                [sys.executable, "-m", "flake8", ".", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.stdout:
                try:
                    flake8_errors = json.loads(result.stdout)
                    for error in flake8_errors:
                        error_info = {
                            "file": Path(error["filename"]).name,
                            "type": "StyleError",
                            "line": error["line_number"],
                            "message": f"{error['code']}: {error['text']}",
                            "timestamp": datetime.now().isoformat(),
                        }
                        errors_found.append(error_info)
                except json.JSONDecodeError:
                    pass

        except Exception:
            pass

        return errors_found

    def generate_error_report(self, all_errors):
        """Génère un rapport d'erreurs formaté"""
        if not all_errors:
            return "✅ Aucune erreur détectée - Tous les systèmes sont opérationnels!"

        report = []
        report.append("🚨 RAPPORT D'ERREURS AIMER - TEMPS RÉEL")
        report.append("=" * 50)
        report.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Grouper par fichier
        errors_by_file = {}
        for error in all_errors:
            file = error["file"]
            if file not in errors_by_file:
                errors_by_file[file] = []
            errors_by_file[file].append(error)

        for file, errors in errors_by_file.items():
            report.append(f"📄 {file}")
            report.append("-" * len(file))

            for error in errors:
                line_info = f" (ligne {error['line']})" if "line" in error else ""
                report.append(f"  ❌ {error['type']}{line_info}: {error['message']}")

            report.append("")

        report.append(f"📊 Total: {len(all_errors)} erreurs détectées")

        return "\n".join(report)

    def save_status(self, errors):
        """Sauvegarde le statut actuel"""
        status = {
            "last_check": datetime.now().isoformat(),
            "error_count": len(errors),
            "errors": errors,
            "status": "errors" if errors else "clean",
        }

        try:
            with open(self.status_file, "w", encoding="utf-8") as f:
                json.dump(status, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def auto_fix_if_possible(self, errors):
        """Tente une auto-correction si possible"""
        fixable_errors = []

        for error in errors:
            # Auto-fix pour certains types d'erreurs courantes
            if error["type"] == "StyleError" and "line too long" in error["message"]:
                fixable_errors.append(error)
            elif error["type"] == "YAMLIndentationError":
                fixable_errors.append(error)

        if fixable_errors:
            self.log_message(f"🔧 Tentative d'auto-correction de {len(fixable_errors)} erreurs")
            try:
                # Lancer le script d'auto-fix
                subprocess.run(
                    [sys.executable, "auto_fix_advanced.py"],
                    capture_output=True,
                    timeout=60,
                )
                self.log_message("✅ Auto-correction exécutée")
            except Exception as e:
                self.log_message(f"❌ Échec auto-correction: {e}")

    def monitor_loop(self):
        """Boucle principale de monitoring"""
        self.log_message("🔍 Démarrage du monitoring des erreurs AIMER")

        while self.running:
            try:
                # Collecter toutes les erreurs
                all_errors = []

                # Vérifications Python
                python_errors = self.check_python_syntax_errors()
                all_errors.extend(python_errors)

                import_errors = self.check_import_errors()
                all_errors.extend(import_errors)

                # Vérifications YAML
                yaml_errors = self.check_yaml_syntax_errors()
                all_errors.extend(yaml_errors)

                # Vérifications de style (moins fréquentes)
                if int(time.time()) % 60 == 0:  # Toutes les minutes
                    style_errors = self.run_flake8_check()
                    # Filtrer les erreurs de style mineures
                    critical_style_errors = [
                        e
                        for e in style_errors
                        if "undefined name" in e["message"] or "syntax error" in e["message"]
                    ]
                    all_errors.extend(critical_style_errors)

                # Vérifier s'il y a de nouvelles erreurs
                error_signature = str(
                    sorted([f"{e['file']}:{e.get('line', 0)}:{e['type']}" for e in all_errors])
                )

                if error_signature != self.last_errors.get("signature", ""):
                    # Nouvelles erreurs détectées
                    report = self.generate_error_report(all_errors)
                    self.log_message(report, "ERROR" if all_errors else "INFO")

                    # Sauvegarder le statut
                    self.save_status(all_errors)

                    # Tentative d'auto-correction pour erreurs critiques
                    critical_errors = [
                        e for e in all_errors if e["type"] in ["SyntaxError", "ImportError"]
                    ]
                    if critical_errors:
                        self.auto_fix_if_possible(critical_errors)

                    self.last_errors["signature"] = error_signature
                    self.last_errors["count"] = len(all_errors)

                # Pause avant la prochaine vérification
                time.sleep(10)  # Vérification toutes les 10 secondes

            except KeyboardInterrupt:
                self.log_message("🛑 Arrêt du monitoring (Ctrl+C)")
                self.running = False
                break

            except Exception as e:
                self.log_message(f"❌ Erreur monitoring: {e}", "ERROR")
                time.sleep(30)  # Pause plus longue en cas d'erreur

    def start_monitoring(self):
        """Démarre le monitoring"""
        print("🔍 AIMER Error Monitor - Surveillance autonome")
        print("=" * 50)
        print("✨ Monitoring en temps réel des erreurs:")
        print("   - Syntaxe Python")
        print("   - Imports manquants")
        print("   - Erreurs YAML")
        print("   - Style critique")
        print("")
        print("📁 Logs sauvegardés dans: error_monitor.log")
        print("📊 Statut disponible dans: .error_monitor_status.json")
        print("")
        print("🔧 Auto-correction activée pour erreurs critiques")
        print("🛑 Appuyez sur Ctrl+C pour arrêter")
        print("=" * 50)

        try:
            self.monitor_loop()
        except Exception as e:
            self.log_message(f"💥 Erreur fatale du monitoring: {e}", "FATAL")
        finally:
            self.log_message("🏁 Monitoring terminé")


def main():
    """Point d'entrée principal"""
    monitor = AimerErrorMonitor()

    # Créer le fichier PID pour indiquer que le monitoring est actif
    pid_file = Path(".error_monitor.pid")

    try:
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))

        monitor.start_monitoring()

    finally:
        # Nettoyer le fichier PID
        if pid_file.exists():
            pid_file.unlink()


if __name__ == "__main__":
    main()
