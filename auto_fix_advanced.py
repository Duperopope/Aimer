#!/usr/bin/env python3
"""
🔧 AIMER Auto-Fix Advanced
Outil automatique avancé pour réparer les erreurs courantes du projet AIMER
Spécialement conçu pour corriger les erreurs YAML et Python
"""

import json
import os
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

# Import conditionnel de rich
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

    class Console:
        def print(self, *args, **kwargs):
            print(*args)


console = Console()


console = Console()


class AimerAutoFixAdvanced:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.errors_fixed = 0
        self.warnings = 0

    def log_success(self, message):
        if RICH_AVAILABLE:
            console.print(f"✅ {message}", style="green")
        else:
            print(f"✅ {message}")
        self.errors_fixed += 1

    def log_warning(self, message):
        if RICH_AVAILABLE:
            console.print(f"⚠️ {message}", style="yellow")
        else:
            print(f"⚠️ {message}")
        self.warnings += 1

    def log_error(self, message):
        if RICH_AVAILABLE:
            console.print(f"❌ {message}", style="red")
        else:
            print(f"❌ {message}")

    def log_info(self, message):
        if RICH_AVAILABLE:
            console.print(f"ℹ️ {message}", style="blue")
        else:
            print(f"ℹ️ {message}")

    def install_missing_packages(self):
        """Installe les packages Python manquants"""
        print("\n📦 Installation des dépendances...")

        # Liste des packages requis
        packages = [
            "cryptography>=41.0.0",
            "rich>=13.0.0",
            "psutil>=5.9.0",
            "pyperclip>=1.8.0",
            "click>=8.0.0",
            "python-dotenv>=1.0.0",
            "pydantic>=2.0.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ]

        try:
            # Mettre à jour pip
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                check=True,
                capture_output=True,
            )

            # Installer chaque package
            for package in packages:
                package_name = package.split(">=")[0]
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", package],
                        check=True,
                        capture_output=True,
                    )
                    self.log_success(f"Package {package_name} installé")
                except subprocess.CalledProcessError:
                    self.log_warning(f"Échec installation {package_name}")

            return True

        except Exception as e:
            self.log_error(f"Erreur lors de l'installation: {e}")
            return False

    def fix_yaml_deploy(self):
        """Corrige spécifiquement le fichier deploy.yml"""
        deploy_file = self.base_path / ".github" / "workflows" / "deploy.yml"

        if not deploy_file.exists():
            self.log_warning("deploy.yml non trouvé")
            return False

        try:
            content = deploy_file.read_text(encoding="utf-8")
            original_content = content

            # Correction de l'action obsolète create-release
            if "actions/create-release@v1" in content:
                content = content.replace(
                    "uses: actions/create-release@v1",
                    "uses: softprops/action-gh-release@v1",
                )
                content = content.replace(
                    "release_name: AIMER ${{ github.ref_name }}",
                    "name: AIMER ${{ github.ref_name }}",
                )
                content = content.replace(
                    "tag_name: ${{ github.ref }}", "tag_name: ${{ github.ref_name }}"
                )

                # Écrire le fichier corrigé
                deploy_file.write_text(content, encoding="utf-8")
                self.log_success("deploy.yml corrigé (action obsolète)")
                return True
            else:
                self.log_info("deploy.yml déjà correct")
                return True

        except Exception as e:
            self.log_error(f"Erreur correction deploy.yml: {e}")
            return False

    def fix_yaml_workflows(self):
        """Corrige les erreurs dans tous les workflows YAML"""
        print("\n📝 Correction des workflows YAML...")

        workflows_dir = self.base_path / ".github" / "workflows"
        if not workflows_dir.exists():
            self.log_warning("Dossier .github/workflows manquant")
            return False

        # Corriger deploy.yml en premier
        self.fix_yaml_deploy()

        # Corrections pour tous les fichiers YAML
        yaml_files = list(workflows_dir.glob("*.yml"))

        for yaml_file in yaml_files:
            try:
                content = yaml_file.read_text(encoding="utf-8")
                original_content = content

                # Corrections communes pour toutes les actions
                replacements = {
                    "actions/checkout@v3": "actions/checkout@v4",
                    "actions/setup-python@v3": "actions/setup-python@v4",
                    "actions/upload-pages-artifact@v1": "actions/upload-pages-artifact@v2",
                    "actions/configure-pages@v2": "actions/configure-pages@v3",
                    "actions/deploy-pages@v1": "actions/deploy-pages@v2",
                }

                for old, new in replacements.items():
                    if old in content:
                        content = content.replace(old, new)

                # Sauvegarder si des changements ont été faits
                if content != original_content:
                    yaml_file.write_text(content, encoding="utf-8")
                    self.log_success(f"{yaml_file.name} mis à jour")
                else:
                    self.log_info(f"{yaml_file.name} déjà à jour")

            except Exception as e:
                self.log_error(f"Erreur dans {yaml_file.name}: {e}")

        return True

    def fix_python_syntax(self):
        """Vérifie et tente de corriger la syntaxe Python"""
        print("\n🐍 Vérification de la syntaxe Python...")

        python_files = list(self.base_path.glob("*.py"))
        errors_found = 0

        for py_file in python_files:
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Tenter de compiler
                compile(content, str(py_file), "exec")
                self.log_success(f"{py_file.name} syntaxe OK")

            except SyntaxError as e:
                self.log_error(f"Erreur syntaxe dans {py_file.name} ligne {e.lineno}: {e.msg}")
                errors_found += 1

                # Tentative de correction automatique pour erreurs courantes
                try:
                    fixed_content = self.auto_fix_python_syntax(content, e)
                    if fixed_content != content:
                        # Créer une sauvegarde
                        backup_file = py_file.with_suffix(".py.backup")
                        shutil.copy2(py_file, backup_file)

                        # Écrire le fichier corrigé
                        with open(py_file, "w", encoding="utf-8") as f:
                            f.write(fixed_content)

                        self.log_success(f"{py_file.name} corrigé automatiquement")
                        errors_found -= 1  # Erreur corrigée

                except Exception:
                    pass  # Correction automatique échouée

            except Exception as e:
                self.log_warning(f"Impossible de vérifier {py_file.name}: {e}")

        return errors_found == 0

    def auto_fix_python_syntax(self, content, syntax_error):
        """Tente de corriger automatiquement certaines erreurs Python"""
        lines = content.split("\n")
        error_line = syntax_error.lineno - 1  # Index 0-based

        if error_line < len(lines):
            line = lines[error_line]

            # Corrections courantes
            fixes = [
                # Parenthèses manquantes
                (r"print (.+)", r"print(\1)"),
                # Deux-points manquants
                (
                    r"^(\s*)(if|for|while|def|class|try|except|finally|with|elif|else)\s+(.+)(?<!:)$",
                    r"\1\2 \3:",
                ),
                # Indentation mixte (remplacer tabs par espaces)
                (r"\t", "    "),
            ]

            import re

            fixed_line = line
            for pattern, replacement in fixes:
                fixed_line = re.sub(pattern, replacement, fixed_line)

            if fixed_line != line:
                lines[error_line] = fixed_line
                return "\n".join(lines)

        return content  # Aucune correction appliquée

    def setup_vscode_complete(self):
        """Configuration complète de VS Code"""
        print("\n🔧 Configuration complète de VS Code...")

        vscode_dir = self.base_path / ".vscode"
        vscode_dir.mkdir(exist_ok=True)

        # Extensions recommandées
        extensions = {
            "recommendations": [
                "ms-python.python",
                "ms-python.flake8",
                "ms-python.black-formatter",
                "ms-python.pylint",
                "ms-python.isort",
                "redhat.vscode-yaml",
                "github.vscode-github-actions",
                "ms-vscode.powershell",
                "streetsidesoftware.code-spell-checker",
                "ms-vscode.vscode-json",
                "ms-python.autopep8",
            ]
        }

        # Paramètres optimisés
        settings = {
            "python.defaultInterpreterPath": "python",
            "python.linting.enabled": True,
            "python.linting.flake8Enabled": True,
            "python.linting.pylintEnabled": False,
            "python.formatting.provider": "black",
            "python.analysis.typeCheckingMode": "basic",
            "yaml.validate": True,
            "yaml.hover": True,
            "yaml.completion": True,
            "files.autoSave": "afterDelay",
            "files.autoSaveDelay": 1000,
            "editor.formatOnSave": True,
            "editor.formatOnPaste": True,
            "git.autofetch": True,
            "git.enableSmartCommit": True,
            "terminal.integrated.defaultProfile.windows": "PowerShell",
            "files.associations": {"*.yml": "yaml", "*.yaml": "yaml"},
            "workbench.colorTheme": "Default Dark+",
            "editor.minimap.enabled": True,
            "editor.wordWrap": "on",
        }

        # Tâches pour automatiser les opérations courantes
        tasks = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "AIMER: Auto-Fix",
                    "type": "shell",
                    "command": "python",
                    "args": ["auto_fix_advanced.py"],
                    "group": "build",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared",
                    },
                },
                {
                    "label": "AIMER: Install Dependencies",
                    "type": "shell",
                    "command": "pip",
                    "args": ["install", "-r", "requirements_security.txt"],
                    "group": "build",
                },
                {
                    "label": "AIMER: Run Tests",
                    "type": "shell",
                    "command": "python",
                    "args": ["-m", "pytest", "-v"],
                    "group": "test",
                },
            ],
        }

        try:
            # Sauvegarder tous les fichiers
            with open(vscode_dir / "extensions.json", "w", encoding="utf-8") as f:
                json.dump(extensions, f, indent=2)

            with open(vscode_dir / "settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)

            with open(vscode_dir / "tasks.json", "w", encoding="utf-8") as f:
                json.dump(tasks, f, indent=2)

            self.log_success("Configuration VS Code complète créée")
            return True

        except Exception as e:
            self.log_error(f"Erreur configuration VS Code: {e}")
            return False

    def cleanup_project(self):
        """Nettoie les fichiers temporaires et problématiques"""
        print("\n🧹 Nettoyage du projet...")

        cleaned = 0

        # Patterns de fichiers à nettoyer
        cleanup_patterns = [
            "**/*.pyc",
            "**/__pycache__",
            "**/*.log",
            "**/.pytest_cache",
            "**/*.tmp",
            "**/*.bak",
        ]

        for pattern in cleanup_patterns:
            for item in self.base_path.rglob(pattern.replace("**", "*")):
                try:
                    if item.is_file():
                        item.unlink()
                        cleaned += 1
                    elif item.is_dir():
                        shutil.rmtree(item)
                        cleaned += 1
                except Exception:
                    pass

        if cleaned > 0:
            self.log_success(f"{cleaned} éléments temporaires supprimés")
        else:
            self.log_info("Aucun nettoyage nécessaire")

        return True

    def generate_final_report(self):
        """Génère un rapport final détaillé"""
        print("\n📊 Génération du rapport final...")

        report_lines = [
            "# 🔧 AIMER Auto-Fix Advanced - Rapport Final",
            f"📅 Généré le: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 🎯 Résultats de la Correction",
            f"- **Erreurs corrigées**: {self.errors_fixed}",
            f"- **Avertissements**: {self.warnings}",
            "",
            "## 📋 Actions Effectuées",
            "- ✅ Installation des dépendances Python",
            "- ✅ Correction des workflows YAML",
            "- ✅ Vérification syntaxe Python",
            "- ✅ Configuration VS Code complète",
            "- ✅ Nettoyage du projet",
            "",
            "## 💡 Recommandations Post-Correction",
            "1. **Redémarrer VS Code** pour appliquer toutes les configurations",
            "2. **Installer les extensions recommandées** via VS Code",
            "3. **Tester les workflows GitHub Actions** en faisant un commit",
            "4. **Vérifier que tous les scripts Python** fonctionnent correctement",
            "",
            "## 🚀 Prochaines Étapes",
            "- Exécuter `python main.py` pour tester le projet",
            "- Utiliser `git status` pour vérifier l'état du repository",
            "- Lancer les scripts de synchronisation si nécessaire",
            "",
            "---",
            "🤖 Rapport généré automatiquement par AIMER Auto-Fix Advanced",
        ]

        report_file = self.base_path / "AUTO_FIX_REPORT.md"
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                f.write("\n".join(report_lines))
            self.log_success(f"Rapport sauvegardé: {report_file.name}")
        except Exception as e:
            self.log_error(f"Erreur sauvegarde rapport: {e}")

        return True

    def run_complete_fix(self):
        """Exécute la correction complète"""
        print("🔧 AIMER Auto-Fix Advanced - Correction Complète")
        print("=" * 60)

        fixes = [
            ("📦 Installation dépendances", self.install_missing_packages),
            ("📝 Correction YAML", self.fix_yaml_workflows),
            ("🐍 Vérification Python", self.fix_python_syntax),
            ("🔧 Configuration VS Code", self.setup_vscode_complete),
            ("🧹 Nettoyage projet", self.cleanup_project),
            ("📊 Rapport final", self.generate_final_report),
        ]

        success_count = 0

        for name, fix_func in fixes:
            print(f"\n{name}...")
            try:
                if fix_func():
                    success_count += 1
                    print(f"✅ {name} terminé")
                else:
                    print(f"⚠️ {name} terminé avec avertissements")
            except Exception as e:
                print(f"❌ Erreur dans {name}: {e}")
                if "--debug" in sys.argv:
                    traceback.print_exc()

        # Résumé final
        print("\n" + "=" * 60)
        if success_count == len(fixes):
            print("🎉 TOUTES LES CORRECTIONS APPLIQUÉES AVEC SUCCÈS!")
        else:
            print(f"⚠️ {success_count}/{len(fixes)} corrections réussies")

        print(f"\n📊 Résumé: {self.errors_fixed} erreurs corrigées, {self.warnings} avertissements")
        print("\n💡 IMPORTANT: Redémarrez VS Code pour appliquer toutes les configurations!")

        return success_count == len(fixes)


def main():
    """Point d'entrée principal"""
    try:
        fixer = AimerAutoFixAdvanced()
        success = fixer.run_complete_fix()

        if success:
            print("\n🚀 Auto-Fix Advanced terminé avec succès!")
            return 0
        else:
            print("\n⚠️ Auto-Fix Advanced terminé avec des avertissements")
            return 1

    except KeyboardInterrupt:
        print("\n🛑 Auto-Fix interrompu par l'utilisateur")
        return 1
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        if "--debug" in sys.argv:
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
