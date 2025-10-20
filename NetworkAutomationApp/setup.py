#!/usr/bin/env python3
"""
Script d'initialisation du projet NetworkAutomationApp
Crée la structure des répertoires et fichiers nécessaires
"""

import os
import sys
from pathlib import Path

def create_project_structure():
    """Crée la structure complète du projet"""
    
    print("""
╔══════════════════════════════════════════════════════════╗
║   Setup - Application d'Automatisation Réseau            ║
║   Installation de la structure du projet                 ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Répertoires à créer
    directories = [
        'modules',
        'dashboards',
        'reports',
        'backups',
        'logs',
        'config'
    ]
    
    print("[*] Création de la structure des répertoires...")
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"    [+] Créé: {directory}/")
    
    # Fichiers __init__.py dans modules
    print("\n[*] Création des fichiers Python...")
    
    modules_files = {
        'modules/__init__.py': '''"""
Modules d'automatisation réseau
"""

from .discovery import NetworkDiscovery
from .napalm_utils import NALPMUtils
from .monitoring import NetworkMonitoring
from .reports import ReportGenerator

__all__ = ['NetworkDiscovery', 'NALPMUtils', 'NetworkMonitoring', 'ReportGenerator']
''',
        'config/__init__.py': '''"""
Configuration globale
"""

CONFIG = {
    'APP_NAME': 'NetworkAutomationApp',
    'VERSION': '1.0.0',
    'AUTHOR': 'Tafita Ralijaona',
    'COURSE': 'Automatisation Réseau - TCO M1 2025'
}
''',
    }
    
    for filepath, content in modules_files.items():
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"    [+] Créé: {filepath}")
        else:
            print(f"    [~] Existe déjà: {filepath}")
    
    # Créer fichier .gitignore
    print("\n[*] Création de .gitignore...")
    gitignore_content = """# Environnement Python
venv/
env/
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Fichiers de configuration sensibles
devices.yaml.local
*.key
*.pem

# Fichiers de sortie
backups/*
reports/*
logs/*
dashboards/*.html

# IDE
.vscode/
.idea/
*.swp
*.swo

# Système
.DS_Store
Thumbs.db

# Tests
.pytest_cache/
.coverage
htmlcov/

# Distribution
build/
dist/
*.egg-info/
"""
    
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        print("    [+] Créé: .gitignore")
    
    # Créer fichier de configuration example
    print("\n[*] Création du fichier de configuration...")
    
    if not os.path.exists('devices.yaml'):
        print("    [!] devices.yaml n'existe pas")
        print("    [*] Créez-le avec la configuration de vos serveurs")
    else:
        print("    [+] devices.yaml existe déjà")
    
    # Créer fichier de log initial
    print("\n[*] Initialisation des logs...")
    logs_file = Path('logs/application.log')
    if not logs_file.exists():
        logs_file.touch()
        print("    [+] Créé: logs/application.log")
    
    print("\n[+] Installation complétée!")
    print("\nÉtapes suivantes:")
    print("  1. Configurez devices.yaml avec vos serveurs")
    print("  2. Installez les dépendances: pip install -r requirements.txt")
    print("  3. Lancez l'application: python3 main.py")

if __name__ == '__main__':
    create_project_structure()