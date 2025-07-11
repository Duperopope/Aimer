#!/usr/bin/env python3
"""
🎨 AIMER Style Fixer
Corrige automatiquement les erreurs de style Python avec Black et Flake8
"""

import subprocess
import sys
from pathlib import Path


def run_black_formatter():
    """Applique le formatage Black sur tous les fichiers Python"""
    print("🎨 Application du formatage Black...")

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "black",
                "--line-length",
                "88",  # Longueur de ligne plus flexible
                ".",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ Formatage Black appliqué avec succès")
            if result.stdout:
                print(f"📝 Fichiers formatés:\n{result.stdout}")
        else:
            print(f"⚠️ Avertissements Black: {result.stderr}")

    except Exception as e:
        print(f"❌ Erreur Black: {e}")


def run_isort():
    """Trie les imports avec isort"""
    print("📋 Tri des imports avec isort...")

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "isort",
                "--profile",
                "black",  # Compatible avec Black
                ".",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ Imports triés avec succès")
        else:
            print(f"⚠️ Avertissements isort: {result.stderr}")

    except Exception as e:
        print(f"❌ Erreur isort: {e}")


def install_formatters():
    """Installe les outils de formatage si nécessaires"""
    print("📦 Vérification des outils de formatage...")

    tools = ["black", "isort", "flake8"]

    for tool in tools:
        try:
            subprocess.run(
                [sys.executable, "-m", tool, "--version"],
                capture_output=True,
                check=True,
            )
            print(f"✅ {tool} disponible")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"📦 Installation de {tool}...")
            subprocess.run([sys.executable, "-m", "pip", "install", tool])


def fix_specific_issues():
    """Corrige des problèmes spécifiques détectés"""
    print("🔧 Correction de problèmes spécifiques...")

    python_files = list(Path(".").glob("*.py"))

    for py_file in python_files:
        try:
            content = py_file.read_text(encoding="utf-8")
            original_content = content

            # Corrections spécifiques
            fixes = [
                # Remplacer les f-strings vides
                ('"', '"'),
                ("f'", "'"),
                # Supprimer les trailing whitespaces (sera fait par Black)
                # Corriger les bare except
                ("except:", "except Exception:"),
            ]

            for old, new in fixes:
                # Appliquer uniquement si c'est sûr
                if old == '"' and '"' in content:
                    # Vérifier si c'est vraiment une f-string sans placeholder
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if 'f"' in line and "{" not in line and "}" not in line:
                            lines[i] = line.replace('"', '"')
                    content = "\n".join(lines)

            if content != original_content:
                py_file.write_text(content, encoding="utf-8")
                print(f"✅ {py_file.name} corrigé")

        except Exception as e:
            print(f"⚠️ Impossible de corriger {py_file.name}: {e}")


def main():
    """Point d'entrée principal"""
    print("🎨 AIMER Style Fixer - Correction du style Python")
    print("=" * 55)

    # 1. Installer les outils
    install_formatters()

    # 2. Corriger des problèmes spécifiques
    fix_specific_issues()

    # 3. Trier les imports
    run_isort()

    # 4. Appliquer le formatage Black
    run_black_formatter()

    print("\n🎉 Style Python corrigé!")
    print("💡 Conseil: Les erreurs restantes peuvent être des avertissements acceptables")


if __name__ == "__main__":
    main()
