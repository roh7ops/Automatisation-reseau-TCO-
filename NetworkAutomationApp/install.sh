#!/bin/bash

#####################################################################
# Script d'Installation - Application d'Automatisation Réseau
# Cours: Automatisation Réseau - TCO M1 2025
# Auteur: Tafita Ralijaona
#####################################################################

set -e  # Exit on error

# Couleurs pour le terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
print_banner() {
    clear
    echo -e "${BLUE}"
    echo "╔═════════════════════════════════════════════════════════╗"
    echo "║  Application d'Automatisation Réseau                    ║"
    echo "║  Installation Automatisée                               ║"
    echo "║  Cours: TCO M1 2025                                     ║"
    echo "╚═════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Fonctions
print_step() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_error() {
    echo -e "${RED}[!]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Vérifier les prérequis
check_requirements() {
    print_step "Vérification des prérequis..."
    
    # Python3
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 non trouvé"
        print_step "Installation:"
        print_warning "Ubuntu/Debian: sudo apt-get install python3 python3-pip"
        print_warning "macOS: brew install python3"
        exit 1
    fi
    print_success "Python3 trouvé: $(python3 --version)"
    
    # pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 non trouvé"
        exit 1
    fi
    print_success "pip3 trouvé: $(pip3 --version)"
    
    # Git (optionnel)
    if command -v git &> /dev/null; then
        print_success "Git trouvé"
    else
        print_warning "Git non trouvé (optionnel)"
    fi
}

# Créer environnement virtuel
setup_venv() {
    print_step "Création de l'environnement virtuel..."
    
    if [ -d "venv" ]; then
        print_warning "L'environnement virtuel existe déjà"
        read -p "Voulez-vous le réinitialiser? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
            python3 -m venv venv
            print_success "Environnement virtuel réinitialisé"
        fi
    else
        python3 -m venv venv
        print_success "Environnement virtuel créé"
    fi
    
    # Activer l'environnement
    source venv/bin/activate
    print_success "Environnement virtuel activé"
}

# Mettre à jour pip
upgrade_pip() {
    print_step "Mise à jour de pip..."
    pip install --upgrade pip setuptools wheel > /dev/null 2>&1
    print_success "pip mis à jour"
}

# Installer les dépendances
install_dependencies() {
    print_step "Installation des dépendances..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt non trouvé"
        exit 1
    fi
    
    pip install -r requirements.txt
    print_success "Dépendances installées"
}

# Initialiser le projet
init_project() {
    print_step "Initialisation de la structure du projet..."
    
    if [ ! -f "setup.py" ]; then
        print_error "setup.py non trouvé"
        exit 1
    fi
    
    python3 setup.py
    print_success "Projet initialisé"
}

# Générer les dashboards
generate_dashboards() {
    print_step "Génération des dashboards..."
    
    if [ ! -f "generate_dashboards.py" ]; then
        print_error "generate_dashboards.py non trouvé"
        exit 1
    fi
    
    python3 generate_dashboards.py
    print_success "Dashboards générés"
}

# Tester l'installation
test_installation() {
    print_step "Test de l'installation..."
    
    python3 << 'EOF'
try:
    from modules.discovery import NetworkDiscovery
    from modules.napalm_utils import NALPMUtils
    from modules.monitoring import NetworkMonitoring
    from modules.reports import ReportGenerator
    print("✓ Tous les modules peuvent être importés")
except ImportError as e:
    print(f"✗ Erreur d'import: {e}")
    exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        print_success "Installation réussie"
    else
        print_error "Installation échouée"
        exit 1
    fi
}

# Afficher les instructions finales
show_next_steps() {
    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}Installation réussie!${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}Prochaines étapes:${NC}"
    echo ""
    echo "1. ${YELLOW}Configurer les équipements${NC}"
    echo "   Éditer: nano devices.yaml"
    echo ""
    echo "2. ${YELLOW}Tester la connexion SSH${NC}"
    echo "   Exemple: ssh ubuntu@192.168.1.100"
    echo ""
    echo "3. ${YELLOW}Lancer l'application${NC}"
    echo "   Commande: python3 main.py"
    echo ""
    echo "4. ${YELLOW}Consulter la documentation${NC}"
    echo "   Fichiers: README.md, QUICKSTART.md"
    echo ""
    echo -e "${BLUE}Commandes utiles:${NC}"
    echo "  • source venv/bin/activate          # Activer l'environnement"
    echo "  • python3 main.py                   # Lancer l'application"
    echo "  • python3 generate_dashboards.py    # Générer dashboards"
    echo "  • open dashboards/network_dashboard.html  # Voir dashboards"
    echo ""
    echo -e "${GREEN}Documentation:${NC}"
    echo "  • README.md       - Guide complet"
    echo "  • QUICKSTART.md   - Démarrage rapide (5 min)"
    echo "  • API.md          - Documentation API"
    echo ""
}

# Menu principal
main() {
    print_banner
    
    echo "Phases d'installation:"
    echo "1. Vérification des prérequis"
    echo "2. Configuration environnement virtuel"
    echo "3. Installation des dépendances"
    echo "4. Initialisation du projet"
    echo "5. Génération des dashboards"
    echo "6. Tests"
    echo ""
    read -p "Commencer l'installation? (y/n) " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Installation annulée"
        exit 1
    fi
    
    echo ""
    check_requirements
    echo ""
    setup_venv
    echo ""
    upgrade_pip
    echo ""
    install_dependencies
    echo ""
    init_project
    echo ""
    generate_dashboards
    echo ""
    test_installation
    echo ""
    show_next_steps
}

# Gestion des erreurs
trap 'print_error "Installation interrompue"; exit 1' INT TERM

# Lancer le script
main

exit 0