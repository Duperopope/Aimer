# 🤝 Guide de Contribution - Aimer

Merci de votre intérêt pour contribuer au projet **Aimer** ! Ce guide vous aidera à contribuer efficacement.

## 📋 Table des matières

- [🚀 Démarrage rapide](#-démarrage-rapide)
- [🐛 Signaler des bugs](#-signaler-des-bugs)
- [💡 Proposer des fonctionnalités](#-proposer-des-fonctionnalités)
- [🔧 Développement](#-développement)
- [📝 Standards de code](#-standards-de-code)
- [🧪 Tests](#-tests)
- [📚 Documentation](#-documentation)
- [🎯 Process de review](#-process-de-review)

---

## 🚀 Démarrage rapide

### 1. Fork et clone
```bash
# Fork le repository sur GitHub, puis :
git clone https://github.com/VOTRE-USERNAME/Aimer.git
cd Aimer
```

### 2. Configuration de l'environnement
```bash
# Créer l'environnement virtuel
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Installer les dépendances
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Dépendances de développement
```

### 3. Vérifier l'installation
```bash
# Lancer les tests
python -m pytest

# Lancer l'application
python launcher_interactive.py
```

---

## 🐛 Signaler des bugs

### Avant de signaler
1. **Vérifiez les issues existantes** : [Issues GitHub](https://github.com/Duperopope/Aimer/issues)
2. **Testez avec la dernière version** du code
3. **Reproduisez le bug** de manière consistante

### Template de bug report
```markdown
## 🐛 Description du bug
[Description claire et concise]

## 🔄 Étapes pour reproduire
1. Aller à '...'
2. Cliquer sur '...'
3. Voir l'erreur

## ✅ Comportement attendu
[Ce qui devrait se passer]

## 📱 Environnement
- OS: [Windows 10/11, Ubuntu 20.04, macOS 12, etc.]
- Python: [3.8, 3.9, 3.10, etc.]
- Version Aimer: [v1.0.0, main branch, etc.]

## 📎 Informations supplémentaires
- Logs d'erreur
- Screenshots si applicable
- Configuration utilisée
```

---

## 💡 Proposer des fonctionnalités

### Avant de proposer
1. **Consultez la roadmap** : [ROADMAP.md](ROADMAP.md)
2. **Discutez dans les issues** existantes
3. **Vérifiez la cohérence** avec la vision du projet

### Template de feature request
```markdown
## 🎯 Problème à résoudre
[Quel problème cette fonctionnalité résout-elle ?]

## 💡 Solution proposée
[Description détaillée de la solution]

## 🔄 Alternatives considérées
[Autres solutions envisagées]

## 📊 Impact estimé
- Utilisateurs concernés: [Tous, débutants, avancés, etc.]
- Complexité: [Faible, Moyenne, Élevée]
- Breaking changes: [Oui/Non]
```

---

## 🔧 Développement

### Structure du projet
```
Aimer/
├── ui/                    # Interface utilisateur
│   ├── main_interactive.py
│   ├── annotation_ui.py
│   └── overlay.py
├── detection/             # Système de détection
│   └── yolo_detector.py
├── utils/                 # Utilitaires
│   └── screen_capture.py
├── database/              # Gestion des données
│   └── db_manager.py
├── tests/                 # Tests (à créer)
├── docs/                  # Documentation (à créer)
└── scripts/               # Scripts utilitaires (à créer)
```

### Workflow de développement

1. **Créer une branche**
```bash
git checkout -b feature/nom-de-la-fonctionnalite
# ou
git checkout -b fix/nom-du-bug
```

2. **Développer et tester**
```bash
# Développer votre fonctionnalité
# Ajouter des tests
python -m pytest tests/

# Vérifier le style de code
flake8 .
black .
```

3. **Commit et push**
```bash
git add .
git commit -m "feat: ajouter nouvelle fonctionnalité X"
git push origin feature/nom-de-la-fonctionnalite
```

4. **Créer une Pull Request**

---

## 📝 Standards de code

### Style de code
- **Formatter** : [Black](https://black.readthedocs.io/)
- **Linter** : [Flake8](https://flake8.pycqa.org/)
- **Import sorting** : [isort](https://pycqa.github.io/isort/)

### Conventions de nommage
```python
# Variables et fonctions : snake_case
user_name = "john"
def calculate_distance():
    pass

# Classes : PascalCase
class YoloDetector:
    pass

# Constantes : UPPER_SNAKE_CASE
MAX_DETECTION_DISTANCE = 100

# Fichiers : snake_case.py
# yolo_detector.py, screen_capture.py
```

### Docstrings
```python
def detect_objects(image, confidence_threshold=0.5):
    """
    Détecte les objets dans une image en utilisant YOLO.
    
    Args:
        image (np.ndarray): Image d'entrée au format BGR
        confidence_threshold (float): Seuil de confiance (0.0-1.0)
        
    Returns:
        List[Dict]: Liste des détections avec bbox et classe
        
    Raises:
        ValueError: Si l'image est invalide
        
    Example:
        >>> detector = YoloDetector()
        >>> detections = detector.detect_objects(image, 0.7)
    """
```

### Messages de commit
Format : `type(scope): description`

**Types :**
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation
- `style`: Formatage, style
- `refactor`: Refactoring
- `test`: Ajout/modification de tests
- `chore`: Maintenance

**Exemples :**
```
feat(detection): ajouter support GPU pour YOLO
fix(ui): corriger crash lors du redimensionnement
docs(readme): mettre à jour guide d'installation
test(detector): ajouter tests unitaires pour YoloDetector
```

---

## 🧪 Tests

### Structure des tests
```
tests/
├── unit/                  # Tests unitaires
│   ├── test_detector.py
│   ├── test_screen_capture.py
│   └── test_config.py
├── integration/           # Tests d'intégration
│   ├── test_full_pipeline.py
│   └── test_ui_integration.py
├── fixtures/              # Données de test
│   ├── sample_images/
│   └── config_samples/
└── conftest.py           # Configuration pytest
```

### Écrire des tests
```python
import pytest
from detection.yolo_detector import YoloDetector

class TestYoloDetector:
    def setup_method(self):
        """Setup avant chaque test."""
        self.detector = YoloDetector()
    
    def test_load_model_success(self):
        """Test le chargement réussi du modèle."""
        assert self.detector.model is not None
        assert self.detector.is_loaded
    
    def test_detect_objects_valid_image(self):
        """Test la détection sur une image valide."""
        # Arrange
        image = load_test_image("sample.jpg")
        
        # Act
        detections = self.detector.detect_objects(image)
        
        # Assert
        assert isinstance(detections, list)
        assert len(detections) >= 0
    
    def test_detect_objects_invalid_image(self):
        """Test la gestion d'erreur avec image invalide."""
        with pytest.raises(ValueError):
            self.detector.detect_objects(None)
```

### Lancer les tests
```bash
# Tous les tests
python -m pytest

# Tests spécifiques
python -m pytest tests/unit/test_detector.py

# Avec couverture
python -m pytest --cov=. --cov-report=html

# Tests en mode verbose
python -m pytest -v
```

---

## 📚 Documentation

### Types de documentation

1. **Code documentation** : Docstrings dans le code
2. **API documentation** : Générée automatiquement
3. **User guides** : Guides d'utilisation
4. **Developer docs** : Documentation technique

### Écrire de la documentation
```markdown
# Titre principal

## Section

### Sous-section

- Utilisez des listes pour les étapes
- **Gras** pour les éléments importants
- `Code` pour les commandes et variables

```python
# Blocs de code avec syntaxe highlighting
def example_function():
    return "Hello World"
```

> **Note:** Utilisez les callouts pour les informations importantes

⚠️ **Attention:** Pour les avertissements
```

---

## 🎯 Process de review

### Checklist avant PR
- [ ] **Tests** : Tous les tests passent
- [ ] **Style** : Code formaté avec Black/Flake8
- [ ] **Documentation** : Docstrings et docs mises à jour
- [ ] **Commits** : Messages de commit clairs
- [ ] **Conflicts** : Pas de conflits avec main
- [ ] **Description** : PR description complète

### Template de Pull Request
```markdown
## 📝 Description
[Description des changements]

## 🔗 Issue liée
Fixes #[numéro]

## 🧪 Tests
- [ ] Tests unitaires ajoutés/mis à jour
- [ ] Tests d'intégration passent
- [ ] Tests manuels effectués

## 📋 Checklist
- [ ] Code formaté (Black)
- [ ] Linting passé (Flake8)
- [ ] Documentation mise à jour
- [ ] Pas de breaking changes non documentés

## 📸 Screenshots (si applicable)
[Screenshots des changements UI]
```

### Process de review
1. **Automated checks** : CI/CD vérifie automatiquement
2. **Code review** : Review par un mainteneur
3. **Testing** : Tests sur différents environnements
4. **Approval** : Approbation et merge

---

## 🏷️ Labels et priorités

### Labels de type
- `bug` : Correction de bug
- `enhancement` : Nouvelle fonctionnalité
- `documentation` : Amélioration documentation
- `good first issue` : Bon pour débuter
- `help wanted` : Aide recherchée

### Labels de priorité
- `priority: critical` : Critique (sécurité, crash)
- `priority: high` : Haute (fonctionnalité importante)
- `priority: medium` : Moyenne (amélioration)
- `priority: low` : Basse (nice-to-have)

### Labels de difficulté
- `difficulty: easy` : Facile (< 1 jour)
- `difficulty: medium` : Moyen (1-3 jours)
- `difficulty: hard` : Difficile (> 3 jours)

---

## 🆘 Besoin d'aide ?

- **Issues GitHub** : [github.com/Duperopope/Aimer/issues](https://github.com/Duperopope/Aimer/issues)
- **Discussions** : GitHub Discussions
- **Documentation** : [README.md](README.md) et [ROADMAP.md](ROADMAP.md)

---

## 📄 Code of Conduct

En participant à ce projet, vous acceptez de respecter notre code de conduite :

- **Respectueux** : Traitez tous les participants avec respect
- **Inclusif** : Accueillez les contributions de tous
- **Constructif** : Donnez des retours constructifs
- **Professionnel** : Maintenez un environnement professionnel

---

**Merci de contribuer à Aimer ! 🎯**

*Votre contribution, quelle que soit sa taille, est précieuse pour la communauté.*
