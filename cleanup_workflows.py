#!/usr/bin/env python3
"""
Script pour nettoyer les workflows GitHub échoués
Nécessite un token GitHub avec les permissions 'actions:write'
"""

import requests
import json

def cleanup_failed_workflows():
    """Supprime tous les workflows échoués du dépôt"""
    
    # Configuration
    REPO_OWNER = "Duperopope"
    REPO_NAME = "Aimer"
    # TOKEN = "your_github_token_here"  # Remplacez par votre token
    
    print("⚠️  Pour utiliser ce script, vous devez :")
    print("1. Créer un token GitHub avec les permissions 'actions:write'")
    print("2. Remplacer 'your_github_token_here' par votre token dans ce fichier")
    print("3. Relancer le script")
    print("")
    print("💡 Ou alors, supprimez manuellement depuis GitHub Actions")
    print(f"   👉 https://github.com/{REPO_OWNER}/{REPO_NAME}/actions")
    
    # Code pour supprimer les workflows (à activer avec un token valide)
    """
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Récupérer la liste des workflows
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        runs = response.json()["workflow_runs"]
        
        for run in runs:
            if run["conclusion"] == "failure":
                run_id = run["id"]
                delete_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}"
                
                delete_response = requests.delete(delete_url, headers=headers)
                if delete_response.status_code == 204:
                    print(f"✅ Supprimé le workflow {run_id}")
                else:
                    print(f"❌ Erreur lors de la suppression de {run_id}")
    else:
        print(f"❌ Erreur: {response.status_code}")
    """

if __name__ == "__main__":
    cleanup_failed_workflows()
