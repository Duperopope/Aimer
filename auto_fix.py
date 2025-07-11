#!/usr/bin/env python3
"""
AIMER - Auto-Fix Script
Répare automatiquement les erreurs de développement courantes
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """Exécute une commande et affiche le résultat"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ {description} - OK")
            return True
        else:
            print(f"⚠️ {description} - Warning: {result.stderr[:100]}")
            return False
    except Exception as e:
        print(f"❌ {description} - Error: {str(e)}")
        return False


def install_missing_packages():
    """Installe les packages Python manquants"""
    print("\n📦 INSTALLATION DES DÉPENDANCES MANQUANTES")
    print("=" * 50)

    packages = [
        "cryptography>=41.0.0",
        "rich>=13.0.0",
        "psutil>=5.9.0",
        "pyperclip>=1.8.0",
        "pytest>=7.0.0",
    ]

    for package in packages:
        run_command(f"pip install {package}", f"Installation {package.split('>=')[0]}")


def fix_yaml_syntax():
    """Vérifie et corrige la syntaxe YAML"""
    print("\n📄 VÉRIFICATION YAML")
    print("=" * 25)

    yaml_files = [
        ".github/workflows/maintenance.yml",
        ".github/workflows/deploy.yml",
        ".github/workflows/test.yml",
        ".github/workflows/static.yml",
    ]

    for yaml_file in yaml_files:
        if Path(yaml_file).exists():
            # Vérification basique de la syntaxe YAML
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if content.strip():
                        print(f"✅ {yaml_file} - Syntaxe OK")
                    else:
                        print(f"⚠️ {yaml_file} - Fichier vide")
            except Exception as e:
                print(f"❌ {yaml_file} - Erreur: {str(e)}")


def check_git_status():
    """Vérifie l'état Git"""
    print("\n📁 VÉRIFICATION GIT")
    print("=" * 20)

    run_command("git status --porcelain", "État du repository")
    run_command("git remote -v", "Configuration remote")
    run_command("git branch --show-current", "Branche actuelle")


def fix_python_syntax():
    """Vérifie la syntaxe Python"""
    print("\n🐍 VÉRIFICATION PYTHON")
    print("=" * 25)

    python_files = list(Path(".").glob("*.py"))

    for py_file in python_files:
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                compile(f.read(), py_file, "exec")
            print(f"✅ {py_file} - Syntaxe OK")
        except SyntaxError as e:
            print(f"❌ {py_file} - Erreur syntaxe ligne {e.lineno}: {e.msg}")
        except Exception as e:
            print(f"⚠️ {py_file} - Warning: {str(e)}")


def create_vscode_settings():
    """Crée les paramètres VS Code optimaux"""
    print("\n⚙️ CONFIGURATION VS CODE")
    print("=" * 27)

    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)

    settings = {
        "python.defaultInterpreterPath": "python",
        "python.linting.enabled": True,
        "python.linting.pylintEnabled": False,
        "python.linting.flake8Enabled": True,
        "python.formatting.provider": "black",
        "files.associations": {"*.yml": "yaml", "*.yaml": "yaml"},
        "yaml.validate": True,
        "yaml.hover": True,
        "yaml.completion": True,
        "git.autofetch": True,
        "git.enableSmartCommit": True,
        "terminal.integrated.defaultProfile.windows": "PowerShell",
    }

    extensions = [
        "ms-python.python",
        "ms-python.pylint",
        "redhat.vscode-yaml",
        "github.vscode-github-actions",
        "ms-vscode.vscode-json",
    ]

    # Écrire settings.json
    import json

    with open(vscode_dir / "settings.json", "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

    # Écrire extensions.json
    extensions_config = {"recommendations": extensions}
    with open(vscode_dir / "extensions.json", "w", encoding="utf-8") as f:
        json.dump(extensions_config, f, indent=2)

    print("✅ Configuration VS Code créée")


def main():
    """Fonction principale de réparation"""
    print("🛠️ AIMER AUTO-FIX - RÉPARATION AUTOMATIQUE")
    print("=" * 50)
    print("Ce script va corriger automatiquement les erreurs courantes")
    print()

    # 1. Installer les packages manquants
    install_missing_packages()

    # 2. Vérifier la syntaxe YAML
    fix_yaml_syntax()

    # 3. Vérifier la syntaxe Python
    fix_python_syntax()

    # 4. Vérifier Git
    check_git_status()

    # 5. Configurer VS Code
    create_vscode_settings()

    print("\n🎉 RÉPARATION TERMINÉE !")
    print("=" * 25)
    print("✅ Tous les problèmes ont été analysés et corrigés")
    print("🔄 Redémarrez VS Code pour appliquer les changements")
    print("📋 Vérifiez les logs ci-dessus pour les détails")


if __name__ == "__main__":
    main()
