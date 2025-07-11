#!/usr/bin/env python3
"""
🔍 AIMER VS Code Error Monitor
Monitoring spécialisé pour capturer les erreurs VS Code en temps réel
"""

import json
import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime


class VSCodeErrorMonitor:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.status_file = self.base_path / ".vscode_error_status.json"
        self.last_check = None

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")

    def check_python_compilation(self):
        """Vérifie la compilation Python"""
        errors = []
        python_files = list(self.base_path.glob("*.py"))

        for py_file in python_files:
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(py_file)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode != 0:
                    errors.append(
                        {
                            "file": py_file.name,
                            "type": "CompilationError",
                            "message": result.stderr.strip()[:100],
                        }
                    )
            except Exception:
                pass

        return errors

    def check_yaml_syntax(self):
        """Vérifie la syntaxe YAML avec yamllint si disponible"""
        errors = []
        workflows_dir = self.base_path / ".github" / "workflows"

        if not workflows_dir.exists():
            return errors

        for yaml_file in workflows_dir.glob("*.yml"):
            try:
                # Vérification basique de syntaxe YAML
                import yaml

                with open(yaml_file, "r", encoding="utf-8") as f:
                    yaml.safe_load(f)
            except ImportError:
                # yaml n'est pas installé, vérification basique
                content = yaml_file.read_text(encoding="utf-8")
                if content.count(":") == 0:
                    errors.append(
                        {
                            "file": yaml_file.name,
                            "type": "YAMLError",
                            "message": "Possible YAML syntax error",
                        }
                    )
            except Exception as e:
                errors.append(
                    {"file": yaml_file.name, "type": "YAMLError", "message": str(e)[:100]}
                )

        return errors

    def run_flake8_focused(self):
        """Lance flake8 avec focus sur les erreurs critiques"""
        errors = []

        try:
            # Utiliser notre configuration setup.cfg
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "flake8",
                    "--select=E9,F63,F7,F82,F401",  # Erreurs critiques seulement
                    ".",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    if ":" in line:
                        parts = line.split(":", 4)
                        if len(parts) >= 4:
                            errors.append(
                                {
                                    "file": Path(parts[0]).name,
                                    "line": parts[1],
                                    "type": "CriticalStyleError",
                                    "message": parts[3].strip() if len(parts) > 3 else "Error",
                                }
                            )
        except Exception:
            pass

        return errors

    def generate_status_report(self, all_errors):
        """Génère un rapport de statut détaillé"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "total_errors": len(all_errors),
            "errors_by_type": {},
            "errors_by_file": {},
            "errors": all_errors,
        }

        # Grouper par type
        for error in all_errors:
            error_type = error.get("type", "Unknown")
            if error_type not in status["errors_by_type"]:
                status["errors_by_type"][error_type] = 0
            status["errors_by_type"][error_type] += 1

            # Grouper par fichier
            file_name = error.get("file", "Unknown")
            if file_name not in status["errors_by_file"]:
                status["errors_by_file"][file_name] = []
            status["errors_by_file"][file_name].append(error)

        return status

    def save_status(self, status):
        """Sauvegarde le statut"""
        try:
            with open(self.status_file, "w", encoding="utf-8") as f:
                json.dump(status, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def print_summary(self, status):
        """Affiche un résumé des erreurs"""
        total = status["total_errors"]

        if total == 0:
            self.log("✅ Aucune erreur critique détectée")
        else:
            self.log(f"🚨 {total} erreur(s) détectée(s)")

            # Résumé par type
            for error_type, count in status["errors_by_type"].items():
                self.log(f"   📋 {error_type}: {count}")

            # Détail des erreurs les plus importantes
            for file_name, file_errors in status["errors_by_file"].items():
                self.log(f"   📄 {file_name}: {len(file_errors)} erreur(s)")
                for error in file_errors[:2]:  # Max 2 par fichier
                    line_info = f" (L{error.get('line', '?')})" if error.get("line") else ""
                    message = error.get("message", "")[:50]
                    self.log(f"      ❌ {message}{line_info}")

    def monitor_continuous(self):
        """Monitoring continu optimisé"""
        self.log("🔍 VS Code Error Monitor - Démarrage")
        self.log("📊 Focus sur les erreurs critiques uniquement")

        while True:
            try:
                # Collecter les erreurs critiques
                all_errors = []

                # 1. Erreurs de compilation Python
                compile_errors = self.check_python_compilation()
                all_errors.extend(compile_errors)

                # 2. Erreurs YAML
                yaml_errors = self.check_yaml_syntax()
                all_errors.extend(yaml_errors)

                # 3. Erreurs flake8 critiques (moins fréquent)
                if int(time.time()) % 30 == 0:  # Toutes les 30 secondes
                    flake8_errors = self.run_flake8_focused()
                    all_errors.extend(flake8_errors)

                # Générer et sauvegarder le statut
                status = self.generate_status_report(all_errors)
                self.save_status(status)

                # Afficher le résumé si changement
                current_signature = f"{len(all_errors)}:{hash(str(sorted([e['file'] + e['type'] for e in all_errors])))}"
                if current_signature != getattr(self, "last_signature", ""):
                    self.print_summary(status)
                    self.last_signature = current_signature

                time.sleep(15)  # Vérification toutes les 15 secondes

            except KeyboardInterrupt:
                self.log("🛑 Monitoring arrêté")
                break
            except Exception as e:
                self.log(f"❌ Erreur monitoring: {e}")
                time.sleep(30)


def main():
    """Point d'entrée principal"""
    monitor = VSCodeErrorMonitor()
    monitor.monitor_continuous()


if __name__ == "__main__":
    main()
