#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Cleaner - Nettoyeur de projet intelligent
Analyse et nettoie automatiquement les fichiers obsolètes et redondants
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Set, Optional
import json
import time
from datetime import datetime
import hashlib

class ProjectCleaner:
    """Nettoyeur de projet intelligent"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.analysis_results = {}
        self.cleanup_log = []
        
        # Fichiers et dossiers à conserver absolument
        self.essential_files = {
            # Nouveaux systèmes révolutionnaires
            "core/smart_system_profiler.py",
            "core/adaptive_engine.py",
            "launcher_ultimate.py",
            "ui/ultimate_interface.py",
            "learning/dataset_manager.py",
            "learning/collaborative_learning.py",
            "realtime/multi_target_stream.py",
            "utils/multi_screen.py",
            "ui/zone_selector.py",
            
            # Fichiers système essentiels
            "README_ULTIMATE.md",
            "requirements.txt",
            "LICENSE",
            ".gitignore",
            "yolov8n.pt",
            
            # Dossiers de données
            "datasets/",
            "logs/",
            "exports/",
            "screenshots/",
            "models/"
        }
        
        # Fichiers potentiellement obsolètes
        self.potentially_obsolete = {
            # Anciens launchers
            "launcher.py",
            "launcher_interactive.py",
            "start.bat",
            
            # Anciens fichiers UI
            "ui/main_friendly.py",
            "ui/main_interactive.py",
            "ui/annotation_ui.py",
            "ui/overlay.py",
            
            # Anciens utilitaires
            "utils/screen_capture.py",
            
            # Anciens détecteurs
            "detection/yolo_detector.py",
            
            # Anciens gestionnaires
            "database/db_manager.py",
            
            # Fichiers de documentation obsolètes
            "README.md",
            "SETUP_GITHUB.md",
            "PROJET_COMPLETE.md",
            "ROADMAP.md",
            "CONTRIBUTING.md",
            "VALIDATION_LOG.md",
            
            # Fichiers de configuration obsolètes
            "aiming_config.json",
            "requirements-dev.txt"
        }
        
        # Extensions de fichiers temporaires
        self.temp_extensions = {
            ".tmp", ".temp", ".bak", ".backup", ".old", ".orig",
            ".pyc", ".pyo", "__pycache__", ".DS_Store", "Thumbs.db"
        }
    
    def analyze_project_structure(self) -> Dict:
        """Analyse la structure du projet pour identifier les redondances"""
        print("🔍 Analyse de la structure du projet...")
        
        analysis = {
            "total_files": 0,
            "total_size_mb": 0,
            "file_types": {},
            "duplicate_files": [],
            "obsolete_files": [],
            "temp_files": [],
            "large_files": [],
            "empty_directories": [],
            "recommendations": []
        }
        
        # Parcourir tous les fichiers
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                analysis["total_files"] += 1
                
                # Taille du fichier
                size_bytes = file_path.stat().st_size
                size_mb = size_bytes / (1024 * 1024)
                analysis["total_size_mb"] += size_mb
                
                # Type de fichier
                extension = file_path.suffix.lower()
                if extension not in analysis["file_types"]:
                    analysis["file_types"][extension] = {"count": 0, "size_mb": 0}
                analysis["file_types"][extension]["count"] += 1
                analysis["file_types"][extension]["size_mb"] += size_mb
                
                # Fichiers volumineux (>10MB)
                if size_mb > 10:
                    analysis["large_files"].append({
                        "path": str(file_path.relative_to(self.project_root)),
                        "size_mb": round(size_mb, 2)
                    })
                
                # Fichiers temporaires
                if any(str(file_path).endswith(ext) for ext in self.temp_extensions) or \
                   any(part in str(file_path) for part in ["__pycache__", ".pytest_cache"]):
                    analysis["temp_files"].append(str(file_path.relative_to(self.project_root)))
                
                # Fichiers potentiellement obsolètes
                relative_path = str(file_path.relative_to(self.project_root))
                if relative_path in self.potentially_obsolete:
                    analysis["obsolete_files"].append(relative_path)
        
        # Détecter les doublons
        analysis["duplicate_files"] = self._find_duplicate_files()
        
        # Détecter les dossiers vides
        analysis["empty_directories"] = self._find_empty_directories()
        
        # Générer des recommandations
        analysis["recommendations"] = self._generate_cleanup_recommendations(analysis)
        
        self.analysis_results = analysis
        return analysis
    
    def _find_duplicate_files(self) -> List[Dict]:
        """Trouve les fichiers dupliqués par hash"""
        print("🔍 Recherche de fichiers dupliqués...")
        
        file_hashes = {}
        duplicates = []
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and file_path.stat().st_size > 0:
                try:
                    # Calculer le hash du fichier
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    
                    if file_hash in file_hashes:
                        # Doublon trouvé
                        duplicates.append({
                            "original": str(file_hashes[file_hash].relative_to(self.project_root)),
                            "duplicate": str(file_path.relative_to(self.project_root)),
                            "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2)
                        })
                    else:
                        file_hashes[file_hash] = file_path
                        
                except (PermissionError, OSError):
                    continue
        
        return duplicates
    
    def _find_empty_directories(self) -> List[str]:
        """Trouve les dossiers vides"""
        empty_dirs = []
        
        for dir_path in self.project_root.rglob("*"):
            if dir_path.is_dir():
                try:
                    # Vérifier si le dossier est vide (pas de fichiers, seulement des sous-dossiers vides)
                    if not any(dir_path.iterdir()):
                        empty_dirs.append(str(dir_path.relative_to(self.project_root)))
                except (PermissionError, OSError):
                    continue
        
        return empty_dirs
    
    def _generate_cleanup_recommendations(self, analysis: Dict) -> List[str]:
        """Génère des recommandations de nettoyage"""
        recommendations = []
        
        # Recommandations basées sur les fichiers temporaires
        if analysis["temp_files"]:
            recommendations.append(f"Supprimer {len(analysis['temp_files'])} fichiers temporaires")
        
        # Recommandations basées sur les doublons
        if analysis["duplicate_files"]:
            total_duplicate_size = sum(dup["size_mb"] for dup in analysis["duplicate_files"])
            recommendations.append(f"Supprimer {len(analysis['duplicate_files'])} doublons ({total_duplicate_size:.1f}MB)")
        
        # Recommandations basées sur les fichiers obsolètes
        if analysis["obsolete_files"]:
            recommendations.append(f"Archiver {len(analysis['obsolete_files'])} fichiers obsolètes")
        
        # Recommandations basées sur les dossiers vides
        if analysis["empty_directories"]:
            recommendations.append(f"Supprimer {len(analysis['empty_directories'])} dossiers vides")
        
        # Recommandations basées sur la taille
        if analysis["total_size_mb"] > 1000:  # Plus de 1GB
            recommendations.append("Projet volumineux - considérer l'archivage des anciens fichiers")
        
        return recommendations
    
    def clean_project(self, interactive: bool = True) -> Dict:
        """Nettoie le projet selon l'analyse"""
        if not self.analysis_results:
            self.analyze_project_structure()
        
        cleanup_results = {
            "files_deleted": 0,
            "directories_deleted": 0,
            "space_freed_mb": 0,
            "actions_taken": [],
            "errors": []
        }
        
        print("🧹 Début du nettoyage du projet...")
        
        # 1. Supprimer les fichiers temporaires
        if self.analysis_results["temp_files"]:
            if not interactive or self._confirm_action(f"Supprimer {len(self.analysis_results['temp_files'])} fichiers temporaires ?"):
                cleanup_results.update(self._clean_temp_files())
        
        # 2. Supprimer les doublons
        if self.analysis_results["duplicate_files"]:
            if not interactive or self._confirm_action(f"Supprimer {len(self.analysis_results['duplicate_files'])} fichiers dupliqués ?"):
                cleanup_results.update(self._clean_duplicate_files())
        
        # 3. Archiver les fichiers obsolètes
        if self.analysis_results["obsolete_files"]:
            if not interactive or self._confirm_action(f"Archiver {len(self.analysis_results['obsolete_files'])} fichiers obsolètes ?"):
                cleanup_results.update(self._archive_obsolete_files())
        
        # 4. Supprimer les dossiers vides
        if self.analysis_results["empty_directories"]:
            if not interactive or self._confirm_action(f"Supprimer {len(self.analysis_results['empty_directories'])} dossiers vides ?"):
                cleanup_results.update(self._clean_empty_directories())
        
        # Sauvegarder le log de nettoyage
        self._save_cleanup_log(cleanup_results)
        
        return cleanup_results
    
    def _clean_temp_files(self) -> Dict:
        """Supprime les fichiers temporaires"""
        results = {"files_deleted": 0, "space_freed_mb": 0, "actions_taken": [], "errors": []}
        
        for temp_file in self.analysis_results["temp_files"]:
            try:
                file_path = self.project_root / temp_file
                if file_path.exists():
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                    
                    results["files_deleted"] += 1
                    results["space_freed_mb"] += size_mb
                    results["actions_taken"].append(f"Supprimé: {temp_file}")
                    
            except Exception as e:
                results["errors"].append(f"Erreur suppression {temp_file}: {e}")
        
        return results
    
    def _clean_duplicate_files(self) -> Dict:
        """Supprime les fichiers dupliqués"""
        results = {"files_deleted": 0, "space_freed_mb": 0, "actions_taken": [], "errors": []}
        
        for duplicate in self.analysis_results["duplicate_files"]:
            try:
                duplicate_path = self.project_root / duplicate["duplicate"]
                if duplicate_path.exists():
                    duplicate_path.unlink()
                    
                    results["files_deleted"] += 1
                    results["space_freed_mb"] += duplicate["size_mb"]
                    results["actions_taken"].append(f"Supprimé doublon: {duplicate['duplicate']}")
                    
            except Exception as e:
                results["errors"].append(f"Erreur suppression doublon {duplicate['duplicate']}: {e}")
        
        return results
    
    def _archive_obsolete_files(self) -> Dict:
        """Archive les fichiers obsolètes"""
        results = {"files_deleted": 0, "space_freed_mb": 0, "actions_taken": [], "errors": []}
        
        # Créer le dossier d'archive
        archive_dir = self.project_root / "archive_obsolete" / datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        for obsolete_file in self.analysis_results["obsolete_files"]:
            try:
                source_path = self.project_root / obsolete_file
                if source_path.exists():
                    # Créer la structure de dossiers dans l'archive
                    archive_path = archive_dir / obsolete_file
                    archive_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Déplacer le fichier vers l'archive
                    shutil.move(str(source_path), str(archive_path))
                    
                    results["files_deleted"] += 1
                    results["actions_taken"].append(f"Archivé: {obsolete_file}")
                    
            except Exception as e:
                results["errors"].append(f"Erreur archivage {obsolete_file}: {e}")
        
        return results
    
    def _clean_empty_directories(self) -> Dict:
        """Supprime les dossiers vides"""
        results = {"directories_deleted": 0, "actions_taken": [], "errors": []}
        
        # Trier par profondeur décroissante pour supprimer les sous-dossiers en premier
        empty_dirs = sorted(self.analysis_results["empty_directories"], key=lambda x: x.count('/'), reverse=True)
        
        for empty_dir in empty_dirs:
            try:
                dir_path = self.project_root / empty_dir
                if dir_path.exists() and dir_path.is_dir():
                    # Vérifier que le dossier est toujours vide
                    if not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        results["directories_deleted"] += 1
                        results["actions_taken"].append(f"Supprimé dossier vide: {empty_dir}")
                        
            except Exception as e:
                results["errors"].append(f"Erreur suppression dossier {empty_dir}: {e}")
        
        return results
    
    def _confirm_action(self, message: str) -> bool:
        """Demande confirmation à l'utilisateur"""
        response = input(f"{message} (o/N): ").lower()
        return response in ['o', 'oui', 'y', 'yes']
    
    def _save_cleanup_log(self, results: Dict):
        """Sauvegarde le log de nettoyage"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "analysis": self.analysis_results
        }
        
        log_file = self.project_root / "logs" / f"cleanup_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_file.parent.mkdir(exist_ok=True)
        
        with open(log_file, 'w') as f:
            json.dump(log_entry, f, indent=2)
    
    def generate_cleanup_report(self) -> str:
        """Génère un rapport de nettoyage"""
        if not self.analysis_results:
            return "Aucune analyse disponible. Exécutez analyze_project_structure() d'abord."
        
        analysis = self.analysis_results
        
        report = f"""
🧹 RAPPORT DE NETTOYAGE DE PROJET
═══════════════════════════════════════════════════════════════

📊 STATISTIQUES GÉNÉRALES:
• Total fichiers: {analysis['total_files']}
• Taille totale: {analysis['total_size_mb']:.1f} MB
• Types de fichiers: {len(analysis['file_types'])}

🗑️ ÉLÉMENTS À NETTOYER:
• Fichiers temporaires: {len(analysis['temp_files'])}
• Fichiers dupliqués: {len(analysis['duplicate_files'])}
• Fichiers obsolètes: {len(analysis['obsolete_files'])}
• Dossiers vides: {len(analysis['empty_directories'])}

📁 TYPES DE FICHIERS:
"""
        
        # Top 10 des types de fichiers
        sorted_types = sorted(analysis['file_types'].items(), 
                            key=lambda x: x[1]['size_mb'], reverse=True)[:10]
        
        for ext, info in sorted_types:
            ext_display = ext if ext else "(sans extension)"
            report += f"• {ext_display}: {info['count']} fichiers, {info['size_mb']:.1f} MB\n"
        
        if analysis['large_files']:
            report += f"\n📦 FICHIERS VOLUMINEUX (>10MB):\n"
            for large_file in analysis['large_files'][:5]:  # Top 5
                report += f"• {large_file['path']}: {large_file['size_mb']:.1f} MB\n"
        
        if analysis['recommendations']:
            report += f"\n💡 RECOMMANDATIONS:\n"
            for i, rec in enumerate(analysis['recommendations'], 1):
                report += f"{i}. {rec}\n"
        
        # Estimation de l'espace libérable
        temp_size = sum(Path(self.project_root / f).stat().st_size 
                       for f in analysis['temp_files'] 
                       if (self.project_root / f).exists()) / (1024 * 1024)
        
        duplicate_size = sum(dup['size_mb'] for dup in analysis['duplicate_files'])
        
        total_freeable = temp_size + duplicate_size
        
        report += f"\n💾 ESPACE LIBÉRABLE ESTIMÉ: {total_freeable:.1f} MB\n"
        
        return report

def clean_project_interactive():
    """Interface interactive pour nettoyer le projet"""
    print("🧹 NETTOYEUR DE PROJET INTELLIGENT")
    print("=" * 50)
    
    cleaner = ProjectCleaner()
    
    # Analyse du projet
    print("\n1️⃣ Analyse du projet en cours...")
    analysis = cleaner.analyze_project_structure()
    
    # Affichage du rapport
    print("\n2️⃣ Rapport d'analyse:")
    print(cleaner.generate_cleanup_report())
    
    # Demander confirmation pour le nettoyage
    if analysis['recommendations']:
        print("\n3️⃣ Nettoyage recommandé:")
        response = input("Voulez-vous procéder au nettoyage interactif ? (o/N): ")
        
        if response.lower() in ['o', 'oui', 'y', 'yes']:
            results = cleaner.clean_project(interactive=True)
            
            print(f"\n✅ Nettoyage terminé!")
            print(f"• Fichiers supprimés: {results['files_deleted']}")
            print(f"• Dossiers supprimés: {results['directories_deleted']}")
            print(f"• Espace libéré: {results['space_freed_mb']:.1f} MB")
            
            if results['errors']:
                print(f"⚠️ Erreurs rencontrées: {len(results['errors'])}")
                for error in results['errors'][:5]:  # Afficher les 5 premières erreurs
                    print(f"  • {error}")
        else:
            print("Nettoyage annulé.")
    else:
        print("\n✅ Projet déjà propre! Aucun nettoyage nécessaire.")

if __name__ == "__main__":
    clean_project_interactive()
