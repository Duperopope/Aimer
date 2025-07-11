#!/usr/bin/env python3
"""
🐙 AIMER GitHub Repository Manager
Gestion complète des repositories GitHub et organisation
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime


class GitHubRepoManager:
    def __init__(self):
        self.base_path = Path(__file__).parent
        
    def log(self, message, emoji="📋"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{emoji} [{timestamp}] {message}")
        
    def run_command(self, cmd, check=True):
        """Exécute une commande et retourne le résultat"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, 
                cwd=self.base_path, check=check
            )
            return result.stdout.strip(), result.stderr.strip()
        except subprocess.CalledProcessError as e:
            return None, e.stderr
            
    def check_github_connection(self):
        """Vérifie la connexion GitHub"""
        self.log("Vérification de la connexion GitHub...", "🔐")
        
        # Test SSH
        stdout, stderr = self.run_command("ssh -T git@github.com", check=False)
        if "successfully authenticated" in stderr:
            self.log("✅ Connexion SSH GitHub active", "🔑")
            return "ssh"
        
        # Test HTTPS
        stdout, stderr = self.run_command("git ls-remote origin", check=False)
        if not stderr:
            self.log("✅ Connexion HTTPS GitHub active", "🌐")
            return "https"
            
        self.log("❌ Pas de connexion GitHub détectée", "⚠️")
        return None
        
    def list_repositories(self):
        """Liste tous les repositories accessibles"""
        self.log("Recherche des repositories...", "🔍")
        
        # Repository local actuel
        stdout, stderr = self.run_command("git remote get-url origin")
        if stdout:
            current_repo = stdout.replace("https://github.com/", "").replace(".git", "")
            self.log(f"Repository actuel: {current_repo}", "📂")
            
        # Liste des branches
        stdout, stderr = self.run_command("git branch -a")
        if stdout:
            branches = [b.strip().replace("remotes/origin/", "") for b in stdout.split('\n') 
                       if b.strip() and not b.strip().startswith('*') and 'HEAD' not in b]
            self.log(f"Branches disponibles: {', '.join(set(branches))}", "🌿")
            
        return current_repo if 'current_repo' in locals() else None
        
    def create_branch_strategy(self):
        """Crée et propose une stratégie de branches"""
        self.log("Création d'une stratégie de branches optimale...", "🌿")
        
        strategy = {
            "monitoring": {
                "description": "Système de monitoring autonome",
                "from": "dev",
                "files": ["*monitor*", "*dashboard*", "*fix*", "*error*"]
            },
            "workflows": {
                "description": "GitHub Actions et CI/CD",
                "from": "dev", 
                "files": [".github/workflows/*"]
            },
            "documentation": {
                "description": "Documentation et guides",
                "from": "dev",
                "files": ["*.md", "*.txt"]
            }
        }
        
        print("\n🎯 STRATÉGIE DE BRANCHES RECOMMANDÉE:")
        print("=" * 50)
        for branch, info in strategy.items():
            print(f"🌿 {branch}")
            print(f"   📝 {info['description']}")
            print(f"   🔄 Créée depuis: {info['from']}")
            print(f"   📁 Fichiers: {', '.join(info['files'])}")
            print()
            
        return strategy
        
    def create_feature_branch(self, branch_name, base_branch="dev"):
        """Crée une nouvelle branche feature"""
        self.log(f"Création de la branche {branch_name} depuis {base_branch}...", "🌱")
        
        # Checkout base branch
        stdout, stderr = self.run_command(f"git checkout {base_branch}")
        if stderr:
            self.log(f"Erreur checkout {base_branch}: {stderr}", "❌")
            return False
            
        # Pull latest
        stdout, stderr = self.run_command("git pull origin " + base_branch, check=False)
        
        # Create new branch
        stdout, stderr = self.run_command(f"git checkout -b {branch_name}")
        if stderr and "already exists" not in stderr:
            self.log(f"Erreur création branche: {stderr}", "❌")
            return False
            
        self.log(f"✅ Branche {branch_name} créée avec succès", "🎉")
        return True
        
    def organize_repository_structure(self):
        """Organise la structure du repository"""
        self.log("Organisation de la structure du repository...", "🗂️")
        
        # Créer les dossiers recommandés
        folders_to_create = [
            "docs",           # Documentation
            "scripts",        # Scripts utilitaires
            "tests",          # Tests
            "config",         # Configuration
        ]
        
        for folder in folders_to_create:
            folder_path = self.base_path / folder
            if not folder_path.exists():
                folder_path.mkdir(exist_ok=True)
                gitkeep = folder_path / ".gitkeep"
                gitkeep.touch()
                self.log(f"📁 Dossier créé: {folder}/", "✨")
                
        # Proposer des déplacements de fichiers
        file_moves = {
            "docs/": ["*.md", "QUICK_START_GUIDE.md", "SYSTEM_COMPLETION_SUMMARY.md"],
            "scripts/": ["*monitor*.py", "*fix*.py", "*organizer*.py", "github_*.py"],
            "config/": ["setup.cfg", ".gitignore"]
        }
        
        print("\n📋 DÉPLACEMENTS DE FICHIERS RECOMMANDÉS:")
        print("=" * 50)
        for target_dir, patterns in file_moves.items():
            print(f"📁 {target_dir}")
            for pattern in patterns:
                print(f"   📄 {pattern}")
                
    def clean_repository(self):
        """Nettoie le repository"""
        self.log("Nettoyage du repository...", "🧹")
        
        # Supprimer les fichiers temporaires
        temp_patterns = [
            "*.log", "*.pid", "__pycache__", ".DS_Store", 
            "*.pyc", ".pytest_cache", ".coverage"
        ]
        
        for pattern in temp_patterns:
            stdout, stderr = self.run_command(f"find . -name '{pattern}' -delete", check=False)
            
        # Nettoyer Git
        stdout, stderr = self.run_command("git gc --aggressive")
        self.log("✅ Nettoyage terminé", "🎉")
        
    def suggest_commit_messages(self):
        """Suggère des messages de commit standardisés"""
        templates = {
            "feat": "✨ feat: Ajout de [fonctionnalité]",
            "fix": "🐛 fix: Correction de [problème]",
            "docs": "📚 docs: Mise à jour documentation",
            "style": "💄 style: Amélioration du formatage",
            "refactor": "♻️ refactor: Refactorisation de [module]",
            "test": "✅ test: Ajout de tests",
            "chore": "🔧 chore: Maintenance et configuration"
        }
        
        print("\n📝 TEMPLATES DE MESSAGES DE COMMIT:")
        print("=" * 50)
        for prefix, template in templates.items():
            print(f"{template}")
            
    def create_github_actions_suggestions(self):
        """Suggère des améliorations GitHub Actions"""
        suggestions = [
            "🚀 CI/CD Pipeline avec tests automatiques",
            "🔍 Analyse de code avec CodeQL",
            "📊 Coverage automatique avec Codecov", 
            "🏷️ Release automatique avec tags",
            "🔒 Scan de sécurité des dépendances",
            "📦 Build et publication automatique"
        ]
        
        print("\n🚀 AMÉLIORATIONS GITHUB ACTIONS SUGGÉRÉES:")
        print("=" * 50)
        for suggestion in suggestions:
            print(f"• {suggestion}")
            
    def interactive_menu(self):
        """Menu interactif pour la gestion du repository"""
        while True:
            print("\n🐙 GITHUB REPOSITORY MANAGER")
            print("=" * 40)
            print("1. 🔍 Analyser le repository")
            print("2. 🌿 Créer une branche feature")
            print("3. 🗂️ Organiser la structure")
            print("4. 🧹 Nettoyer le repository")
            print("5. 📝 Voir templates de commits")
            print("6. 🚀 Suggestions GitHub Actions")
            print("7. 🔐 Vérifier connexion GitHub")
            print("0. ❌ Quitter")
            
            choice = input("\n👉 Votre choix: ").strip()
            
            if choice == "1":
                self.check_github_connection()
                self.list_repositories()
                self.create_branch_strategy()
                
            elif choice == "2":
                branch_name = input("🌱 Nom de la nouvelle branche: ").strip()
                if branch_name:
                    self.create_feature_branch(branch_name)
                    
            elif choice == "3":
                self.organize_repository_structure()
                
            elif choice == "4":
                confirm = input("⚠️ Confirmer le nettoyage? (oui/non): ")
                if confirm.lower() in ['oui', 'o', 'yes', 'y']:
                    self.clean_repository()
                    
            elif choice == "5":
                self.suggest_commit_messages()
                
            elif choice == "6":
                self.create_github_actions_suggestions()
                
            elif choice == "7":
                connection = self.check_github_connection()
                if not connection:
                    print("\n🔧 SOLUTIONS:")
                    print("• Configurer SSH: ssh-keygen -t ed25519 -C 'votre@email.com'")
                    print("• Ou utiliser HTTPS avec token GitHub")
                    
            elif choice == "0":
                print("👋 Au revoir!")
                break
                
            else:
                print("❌ Choix invalide")


def main():
    manager = GitHubRepoManager()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        manager.interactive_menu()
    else:
        # Mode automatique
        print("🐙 AIMER GitHub Repository Manager")
        print("=" * 40)
        
        manager.check_github_connection()
        repo = manager.list_repositories()
        
        print(f"\n💡 Utilisez --interactive pour le mode interactif")
        print(f"💡 Ou lancez github_organizer.py pour organiser les commits")


if __name__ == "__main__":
    main()
