#!/usr/bin/env python3
"""
🧹 AIMER GitHub Repository Organizer
Organisation et nettoyage intelligent du repository GitHub
"""

import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime


class GitHubRepoOrganizer:
    def __init__(self):
        self.base_path = Path(__file__).parent
        
    def log(self, message, emoji="📋"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{emoji} [{timestamp}] {message}")
        
    def run_git_command(self, cmd_args, check=True):
        """Exécute une commande git et retourne le résultat"""
        try:
            result = subprocess.run(
                ["git"] + cmd_args, 
                capture_output=True, 
                text=True, 
                cwd=self.base_path,
                check=check
            )
            return result.stdout.strip(), result.stderr.strip()
        except subprocess.CalledProcessError as e:
            return None, e.stderr
            
    def get_repo_status(self):
        """Analyse le statut actuel du repository"""
        self.log("Analyse du repository GitHub...", "🔍")
        
        # Informations de base
        stdout, stderr = self.run_git_command(["remote", "-v"])
        if stdout:
            self.log(f"Remote: {stdout.split()[1]}", "🌐")
            
        stdout, stderr = self.run_git_command(["branch", "--show-current"])
        if stdout:
            self.log(f"Branche actuelle: {stdout}", "🌿")
            
        # Statut des fichiers
        stdout, stderr = self.run_git_command(["status", "--porcelain"])
        if stdout:
            lines = stdout.split('\n')
            modified = [l for l in lines if l.startswith(' M')]
            untracked = [l for l in lines if l.startswith('??')]
            
            self.log(f"Fichiers modifiés: {len(modified)}", "📝")
            self.log(f"Fichiers non trackés: {len(untracked)}", "❓")
            
            return {
                "modified": [l[3:] for l in modified],
                "untracked": [l[3:] for l in untracked]
            }
        return {"modified": [], "untracked": []}
        
    def organize_files_by_category(self, status):
        """Organise les fichiers par catégorie"""
        self.log("Organisation des fichiers par catégorie...", "📁")
        
        categories = {
            "monitoring": [],
            "workflows": [],
            "documentation": [],
            "core": [],
            "config": [],
            "temp": []
        }
        
        all_files = status["modified"] + status["untracked"]
        
        for file in all_files:
            if any(keyword in file.lower() for keyword in ["monitor", "dashboard", "error", "fix"]):
                categories["monitoring"].append(file)
            elif ".github/workflows" in file:
                categories["workflows"].append(file)
            elif file.endswith(('.md', '.txt')) and not file.startswith('.'):
                categories["documentation"].append(file)
            elif file.endswith(('.py', '.bat', '.sh')) and file in ["main.py", "install_aimer.py"]:
                categories["core"].append(file)
            elif file in [".gitignore", "setup.cfg", "requirements_security.txt"]:
                categories["config"].append(file)
            else:
                categories["temp"].append(file)
                
        for category, files in categories.items():
            if files:
                self.log(f"{category.upper()}: {len(files)} fichiers", "📂")
                for file in files[:3]:  # Afficher les 3 premiers
                    self.log(f"  - {file}", "  ")
                if len(files) > 3:
                    self.log(f"  ... et {len(files) - 3} autres", "  ")
                    
        return categories
        
    def create_commit_strategy(self, categories):
        """Crée une stratégie de commits organisée"""
        self.log("Création de la stratégie de commits...", "📝")
        
        commit_plan = []
        
        # 1. Configuration et setup
        if categories["config"]:
            commit_plan.append({
                "message": "🔧 Configuration: Mise à jour setup.cfg, .gitignore et requirements",
                "files": categories["config"],
                "type": "config"
            })
            
        # 2. Workflows GitHub Actions
        if categories["workflows"]:
            commit_plan.append({
                "message": "🚀 CI/CD: Mise à jour workflows GitHub Actions",
                "files": categories["workflows"],
                "type": "workflows"
            })
            
        # 3. Système de monitoring
        if categories["monitoring"]:
            commit_plan.append({
                "message": "🔍 Monitoring: Système autonome de surveillance et correction d'erreurs",
                "files": categories["monitoring"],
                "type": "monitoring"
            })
            
        # 4. Fichiers core
        if categories["core"]:
            commit_plan.append({
                "message": "⚡ Core: Améliorations des modules principaux",
                "files": categories["core"],
                "type": "core"
            })
            
        # 5. Documentation
        if categories["documentation"]:
            commit_plan.append({
                "message": "📚 Documentation: Guides et documentation système",
                "files": categories["documentation"],
                "type": "docs"
            })
            
        return commit_plan
        
    def execute_commit_plan(self, commit_plan, dry_run=True):
        """Exécute le plan de commits"""
        if dry_run:
            self.log("=== SIMULATION DU PLAN DE COMMITS ===", "🎭")
        else:
            self.log("=== EXÉCUTION DU PLAN DE COMMITS ===", "🚀")
            
        for i, commit in enumerate(commit_plan, 1):
            self.log(f"Commit {i}: {commit['message']}", "📝")
            self.log(f"Fichiers ({len(commit['files'])}): {', '.join(commit['files'][:3])}{'...' if len(commit['files']) > 3 else ''}", "  ")
            
            if not dry_run:
                # Ajouter les fichiers
                for file in commit['files']:
                    stdout, stderr = self.run_git_command(["add", file], check=False)
                    if stderr:
                        self.log(f"Erreur ajout {file}: {stderr}", "❌")
                        
                # Faire le commit
                stdout, stderr = self.run_git_command(["commit", "-m", commit['message']], check=False)
                if stderr and "nothing to commit" not in stderr:
                    self.log(f"Erreur commit: {stderr}", "❌")
                else:
                    self.log(f"✅ Commit réussi", "✅")
                    
    def suggest_branch_strategy(self):
        """Suggère une stratégie de branches"""
        self.log("Stratégie de branches recommandée:", "🌿")
        print("""
        📋 STRATÉGIE DE BRANCHES GITHUB
        ===============================
        
        🌿 main         : Version stable en production
        🌿 dev          : Développement principal (ACTUELLE)
        🌿 feature/*    : Nouvelles fonctionnalités
        🌿 hotfix/*     : Corrections urgentes
        🌿 monitoring   : Système de monitoring (à créer)
        
        💡 RECOMMANDATION:
        1. Créer une branche 'monitoring' pour le système de surveillance
        2. Merger les commits de monitoring dans 'dev'
        3. Faire un PR de 'dev' vers 'main' quand stable
        """)
        
    def clean_and_organize(self, execute=False):
        """Processus complet de nettoyage et organisation"""
        self.log("🧹 NETTOYAGE ET ORGANISATION DU REPOSITORY GITHUB", "🎯")
        self.log("=" * 60, "")
        
        # Analyse
        status = self.get_repo_status()
        categories = self.organize_files_by_category(status)
        commit_plan = self.create_commit_strategy(categories)
        
        # Plan de commits
        self.log("\n📋 PLAN DE COMMITS PROPOSÉ:", "")
        self.execute_commit_plan(commit_plan, dry_run=not execute)
        
        # Stratégie de branches
        self.suggest_branch_strategy()
        
        if not execute:
            print(f"\n🔄 Pour exécuter le plan: python {__file__.split('/')[-1]} --execute")
            
        return commit_plan


def main():
    organizer = GitHubRepoOrganizer()
    
    execute = "--execute" in sys.argv or "-e" in sys.argv
    
    if execute:
        print("⚠️  EXÉCUTION EN MODE RÉEL")
        response = input("Confirmer l'exécution des commits? (oui/non): ")
        if response.lower() not in ['oui', 'o', 'yes', 'y']:
            print("❌ Annulé par l'utilisateur")
            return
            
    commit_plan = organizer.clean_and_organize(execute=execute)
    
    print(f"\n🎉 Organisation terminée!")
    print(f"📊 {len(commit_plan)} commits planifiés")


if __name__ == "__main__":
    main()
