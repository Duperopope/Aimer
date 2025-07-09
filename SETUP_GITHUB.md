# 🚀 Guide de Configuration GitHub

## Étapes pour créer votre dépôt GitHub privé

### 1. Connexion à GitHub
1. Allez sur [github.com](https://github.com)
2. Connectez-vous à votre compte (ou créez-en un si nécessaire)

### 2. Création du dépôt privé
1. Cliquez sur le bouton **"New"** ou allez sur [github.com/new](https://github.com/new)
2. Configurez votre dépôt :
   - **Repository name** : `aimer-intelligent-targeting`
   - **Description** : `🎯 Système de Visée Intelligent - Détection d'objets en temps réel avec YOLO v8`
   - **Visibility** : ✅ **Private** (IMPORTANT !)
   - **Initialize** : ❌ Ne pas cocher (nous avons déjà du code)
3. Cliquez sur **"Create repository"**

### 3. Connexion de votre dépôt local
Une fois le dépôt créé, GitHub vous donnera des commandes. Utilisez celles-ci dans votre terminal :

```bash
# Ajouter l'origine distante (remplacez USERNAME par votre nom d'utilisateur GitHub)
git remote add origin https://github.com/USERNAME/aimer-intelligent-targeting.git

# Renommer la branche principale
git branch -M main

# Pousser votre code
git push -u origin main
```

### 4. Commandes prêtes à utiliser
Voici les commandes exactes à exécuter dans votre terminal PowerShell :

```powershell
# 1. Ajouter l'origine (REMPLACEZ 'USERNAME' par votre nom d'utilisateur GitHub)
git remote add origin https://github.com/USERNAME/aimer-intelligent-targeting.git

# 2. Renommer la branche
git branch -M main

# 3. Pousser le code
git push -u origin main
```

### 5. Vérification
Après avoir exécuté ces commandes :
- Votre code sera visible sur GitHub
- Le dépôt sera privé (seul vous y avez accès)
- Vous pourrez cloner le projet depuis n'importe où
- L'historique Git sera préservé

## 🔧 Commandes Git utiles pour la suite

```bash
# Voir le statut
git status

# Ajouter des modifications
git add .

# Créer un commit
git commit -m "Description des changements"

# Pousser vers GitHub
git push

# Voir l'historique
git log --oneline

# Créer une nouvelle branche
git checkout -b nouvelle-fonctionnalite

# Revenir à la branche principale
git checkout main
```

## 🛡️ Sécurité
- ✅ Dépôt configuré comme **privé**
- ✅ Fichiers sensibles exclus via `.gitignore`
- ✅ Pas de clés API ou mots de passe dans le code
- ✅ Documentation complète pour les collaborateurs

## 📞 Support
Si vous rencontrez des problèmes :
1. Vérifiez que vous êtes connecté à GitHub
2. Assurez-vous que le nom du dépôt est disponible
3. Vérifiez votre connexion internet
4. Consultez la documentation GitHub : [docs.github.com](https://docs.github.com)

---
**Votre projet est maintenant prêt pour GitHub ! 🎉**
