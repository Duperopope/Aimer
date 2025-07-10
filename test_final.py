#!/usr/bin/env python3
"""
AIMER PRO - Test Final Complet
Validation de toute la structure unifiée
"""

import os
import sys
import importlib.util
from pathlib import Path

def test_file_structure():
    """Test de la structure de fichiers unifiée"""
    print("📁 TEST STRUCTURE DE FICHIERS")
    print("=" * 40)
    
    # Fichiers essentiels qui doivent exister
    essential_files = [
        "launch.py",
        "test_webcam.py",
        "ui/web_interface/server.py",
        "ui/web_interface/templates/index.html",
        "requirements_web.txt",
        ".github/workflows/deploy.yml",
        ".github/workflows/test.yml"
    ]
    
    # Fichiers qui ne doivent PLUS exister (doublons supprimés)
    forbidden_files = [
        "server_ultimate.py",
        "server_ultimate_fixed.py", 
        "server_advanced.py",
        "server_full.py",
        "launch_ultimate_web.py",
        "launch_ultimate_fixed.py",
        "launch_advanced_web.py",
        "launch_full_web.py",
        "launch_web_simple.py",
        "ui/web_interface/server_advanced.py",
        "ui/web_interface/server_full.py",
        "ui/web_interface/server_hybrid.py",
        "ui/web_interface/server_simple.py",
        "ui/web_interface/server_ultimate.py",
        "ui/web_interface/server_ultimate_fixed.py",
        "ui/web_interface/templates/ultimate_interface.html",
        "ui/web_interface/templates/advanced_interface.html"
    ]
    
    all_good = True
    
    print("\n✅ Fichiers Essentiels:")
    for file in essential_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MANQUANT")
            all_good = False
    
    print("\n🗑️ Vérification Doublons Supprimés:")
    for file in forbidden_files:
        if not os.path.exists(file):
            print(f"  ✅ {file} - Bien supprimé")
        else:
            print(f"  ❌ {file} - ENCORE PRÉSENT")
            all_good = False
    
    return all_good

def test_imports():
    """Test des imports critiques"""
    print("\n📦 TEST IMPORTS")
    print("=" * 40)
    
    imports_to_test = [
        ("core.detector", "SmartDetector"),
        ("core.config", "ConfigManager"),
        ("core.logger", "Logger"),
        ("core.dataset_manager", "DatasetManager")
    ]
    
    all_good = True
    
    for module_name, class_name in imports_to_test:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, class_name):
                print(f"  ✅ {module_name}.{class_name}")
            else:
                print(f"  ❌ {module_name}.{class_name} - Classe non trouvée")
                all_good = False
        except ImportError as e:
            print(f"  ❌ {module_name}.{class_name} - Import failed: {e}")
            all_good = False
    
    return all_good

def test_syntax():
    """Test de syntaxe des fichiers Python principaux"""
    print("\n🔍 TEST SYNTAXE")
    print("=" * 40)
    
    python_files = [
        "launch.py",
        "test_webcam.py",
        "ui/web_interface/server.py"
    ]
    
    all_good = True
    
    for file in python_files:
        if os.path.exists(file):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    source = f.read()
                compile(source, file, 'exec')
                print(f"  ✅ {file} - Syntaxe OK")
            except SyntaxError as e:
                print(f"  ❌ {file} - Erreur syntaxe: {e}")
                all_good = False
            except Exception as e:
                print(f"  ⚠️  {file} - Autre erreur: {e}")
        else:
            print(f"  ❌ {file} - Fichier manquant")
            all_good = False
    
    return all_good

def test_dependencies():
    """Test des dépendances critiques"""
    print("\n📚 TEST DÉPENDANCES")
    print("=" * 40)
    
    critical_deps = [
        "flask",
        "cv2",
        "numpy"
    ]
    
    all_good = True
    
    for dep in critical_deps:
        try:
            importlib.import_module(dep)
            print(f"  ✅ {dep}")
        except ImportError:
            print(f"  ❌ {dep} - Non installé")
            all_good = False
    
    return all_good

def test_workflows():
    """Test des fichiers workflow GitHub Actions"""
    print("\n⚙️ TEST WORKFLOWS GITHUB ACTIONS")
    print("=" * 40)
    
    workflow_files = [
        ".github/workflows/deploy.yml",
        ".github/workflows/test.yml"
    ]
    
    all_good = True
    
    for file in workflow_files:
        if os.path.exists(file):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Vérifications basiques YAML
                if 'name:' in content and 'on:' in content and 'jobs:' in content:
                    print(f"  ✅ {file} - Structure YAML OK")
                else:
                    print(f"  ❌ {file} - Structure YAML invalide")
                    all_good = False
                    
            except Exception as e:
                print(f"  ❌ {file} - Erreur lecture: {e}")
                all_good = False
        else:
            print(f"  ❌ {file} - Fichier manquant")
            all_good = False
    
    return all_good

def main():
    """Test principal"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                🧪 AIMER PRO - TEST FINAL                    ║
║              Validation Structure Unifiée                   ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Exécution des tests
    tests = [
        ("Structure Fichiers", test_file_structure),
        ("Imports Python", test_imports), 
        ("Syntaxe Code", test_syntax),
        ("Dépendances", test_dependencies),
        ("Workflows CI/CD", test_workflows)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n💥 Erreur dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résultats finaux
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS FINAUX")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHEC"
        print(f"  {status:<10} {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 TOUS LES TESTS PASSÉS!")
        print("✅ Structure unifiée validée")
        print("✅ Doublons supprimés")
        print("✅ Code fonctionnel")
        print("✅ Workflows configurés")
        print("\n🚀 AIMER PRO EST PRÊT POUR LA PRODUCTION!")
    else:
        print("⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez les erreurs ci-dessus")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
