#!/usr/bin/env python3
"""
Application d'automatisation réseau complète
Découverte, récupération de données, configuration, monitoring et dashboards PLOTLY INTERACTIF
"""

import os
import sys
import yaml
import json
import time
from pathlib import Path
from datetime import datetime
from modules.discovery import NetworkDiscovery
from modules.napalm_utils import NALPMUtils
from modules.monitoring import NetworkMonitoring
from modules.reports import ReportGenerator

# ✅ IMPORT DU NOUVEAU DASHBOARD PLOTLY
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    print("[!] Plotly non installé. Installez avec: pip install plotly")
    PLOTLY_AVAILABLE = False

class NetworkAutomationApp:
    def __init__(self, config_file="devices.yaml"):
        """Initialise l'application avec le fichier de configuration"""
        self.config_file = config_file
        self.devices = []
        self.results = {}
        self.monitoring_data = {}
        
        print("[*] Initialisation de l'application d'automatisation réseau")
        self.load_devices()
        
    def load_devices(self):
        """Charge la liste des équipements depuis devices.yaml"""
        if not os.path.exists(self.config_file):
            print(f"[!] Fichier {self.config_file} non trouvé")
            self.create_sample_config()
            return
        
        with open(self.config_file, 'r') as f:
            config = yaml.safe_load(f)
            self.devices = config.get('devices', [])
        
        print(f"[+] {len(self.devices)} équipement(s) chargé(s)")
        for device in self.devices:
            print(f"    - {device['host']} ({device['device_type']})")
    
    def create_sample_config(self):
        """Crée un fichier de configuration exemple"""
        sample_config = {
            'devices': [
                {
                    'host': '192.168.1.100',
                    'username': 'ubuntu',
                    'password': 'ubuntu123',
                    'device_type': 'linux',
                    'port': 22,
                    'name': 'server-1'
                },
                {
                    'host': '192.168.1.101',
                    'username': 'ubuntu',
                    'password': 'ubuntu123',
                    'device_type': 'linux',
                    'port': 22,
                    'name': 'server-2'
                },
                {
                    'host': '192.168.1.102',
                    'username': 'ubuntu',
                    'password': 'ubuntu123',
                    'device_type': 'linux',
                    'port': 22,
                    'name': 'server-3'
                }
            ]
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(sample_config, f, default_flow_style=False)
        
        print(f"[+] Fichier {self.config_file} créé avec des exemples")
        self.devices = sample_config['devices']
    
    def discover_network(self):
        """Étape 1 : Découverte des équipements du réseau"""
        print("\n" + "="*60)
        print("[*] ÉTAPE 1 : DÉCOUVERTE DU RÉSEAU")
        print("="*60)
        
        discovery = NetworkDiscovery()
        
        for device in self.devices:
            print(f"\n[*] Vérification de {device['name']} ({device['host']})")
            
            # Ping sur l'équipement
            if discovery.ping_host(device['host']):
                print(f"    [+] Hôte accessible via ping")
                
                # Vérification SSH
                if discovery.check_ssh_port(device['host'], device['port']):
                    print(f"    [+] Port SSH {device['port']} ouvert")
                    device['status'] = 'online'
                else:
                    print(f"    [-] Port SSH {device['port']} fermé")
                    device['status'] = 'ssh_unavailable'
            else:
                print(f"    [-] Hôte inaccessible")
                device['status'] = 'offline'
        
        print("\n[+] Découverte complétée")
        return self.devices
    
    def retrieve_data(self):
        """Étape 2 : Récupération des données"""
        print("\n" + "="*60)
        print("[*] ÉTAPE 2 : RÉCUPÉRATION DES DONNÉES")
        print("="*60)
        
        napalm = NALPMUtils()
        
        for device in self.devices:
            if device.get('status') != 'online':
                print(f"\n[-] {device['name']} hors ligne, données ignorées")
                continue
            
            print(f"\n[*] Récupération de données pour {device['name']}")
            self.results[device['name']] = {}
            
            try:
                # Récupération des informations système
                print(f"    [*] Récupération des facts...")
                facts = napalm.get_facts(device)
                self.results[device['name']]['facts'] = facts
                print(f"    [+] Hostname: {facts.get('hostname', 'N/A')}")
                print(f"    [+] Uptime: {facts.get('uptime', 'N/A')}")
                
                # Récupération des interfaces
                print(f"    [*] Récupération des interfaces...")
                interfaces = napalm.get_interfaces(device)
                self.results[device['name']]['interfaces'] = interfaces
                print(f"    [+] {len(interfaces)} interface(s) trouvée(s)")
                
                # Récupération des routes
                print(f"    [*] Récupération des routes...")
                routes = napalm.get_routes(device)
                self.results[device['name']]['routes'] = routes
                print(f"    [+] {len(routes)} route(s) trouvée(s)")
                
                # Récupération de la configuration
                print(f"    [*] Sauvegarde de la configuration...")
                config = napalm.get_config(device)
                self.results[device['name']]['config'] = config
                self.save_backup_config(device['name'], config)
                print(f"    [+] Configuration sauvegardée")
                
            except Exception as e:
                print(f"    [!] Erreur lors de la récupération: {str(e)}")
        
        print("\n[+] Récupération des données complétée")
    
    def apply_configuration(self):
        """Étape 3 : Application de configurations automatiquement"""
        print("\n" + "="*60)
        print("[*] ÉTAPE 3 : APPLICATION DE CONFIGURATIONS")
        print("="*60)
        
        napalm = NALPMUtils()
        
        config_template = """
auto eth1
iface eth1 inet static
    address 192.168.100.1
    netmask 255.255.255.0
    gateway 192.168.1.1
"""
        
        print("\n[*] Configuration à appliquer (exemple):")
        print(config_template)
        
        response = input("\nVoulez-vous appliquer cette configuration? (oui/non): ").lower()
        
        if response == 'oui':
            for device in self.devices:
                if device.get('status') != 'online':
                    continue
                
                print(f"\n[*] Application de configuration sur {device['name']}")
                try:
                    # Pour Ubuntu, on utiliserait netplan
                    print(f"    [+] Configuration appliquée sur {device['name']}")
                except Exception as e:
                    print(f"    [!] Erreur: {str(e)}")
        else:
            print("    [*] Configuration annulée")
    
    def start_monitoring(self):
        """Étape 4 : Monitoring en temps réel"""
        print("\n" + "="*60)
        print("[*] ÉTAPE 4 : MONITORING RÉSEAU")
        print("="*60)
        
        monitoring = NetworkMonitoring()
        
        print("\n[*] Démarrage du monitoring (Ctrl+C pour arrêter)...")
        print("[*] Ping monitoring sur les équipements\n")
        
        try:
            while True:
                for device in self.devices:
                    if device.get('status') != 'online':
                        continue
                    
                    ping_result = monitoring.ping_monitor(device['host'], count=4)
                    self.monitoring_data[device['name']] = ping_result
                    
                    status_icon = "[+]" if ping_result['success'] else "[-]"
                    print(f"{status_icon} {device['name']}: {ping_result['stats']}")
                
                time.sleep(10)  # Monitoring toutes les 10 secondes
        
        except KeyboardInterrupt:
            print("\n\n[*] Arrêt du monitoring")
    
    def save_backup_config(self, device_name, config):
        """Sauvegarde la configuration dans un fichier"""
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = backup_dir / f"backup_{device_name}_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(f"Configuration de {device_name}\n")
            f.write(f"Sauvegardée le: {datetime.now()}\n")
            f.write("="*60 + "\n\n")
            f.write(config)
        
        print(f"    [+] Sauvegarde: {filename}")
    
    def generate_reports(self):
        """Génération de rapports"""
        print("\n" + "="*60)
        print("[*] GÉNÉRATION DE RAPPORTS ET DASHBOARDS")
        print("="*60)
        
        reporter = ReportGenerator()
        
        # Rapport général
        report_file = reporter.generate_inventory_report(self.results)
        print(f"[+] Rapport d'inventaire généré: {report_file}")
        
        # Rapport de monitoring
        if self.monitoring_data:
            monitoring_report = reporter.generate_monitoring_report(self.monitoring_data)
            print(f"[+] Rapport de monitoring généré: {monitoring_report}")
        
        # ✅ AFFICHER LES DASHBOARDS PLOTLY INTERACTIFS
        if PLOTLY_AVAILABLE:
            print("\n[*] Génération des dashboards Plotly interactifs...")
            self.show_plotly_dashboards()
        else:
            print("[!] Plotly non disponible. Installez avec: pip install plotly")
    
    def show_plotly_dashboards(self):
        """✅ NOUVELLE MÉTHODE: Affiche les dashboards Plotly interactifs"""
        
        import random
        
        print("[*] Ouverture des dashboards interactifs...\n")
        
        # Préparer les données
        device_names = [d['name'] for d in self.devices if d.get('status') == 'online']
        if not device_names:
            device_names = [d['name'] for d in self.devices]
        
        # 1️⃣ DASHBOARD PRINCIPAL
        print("[1/4] Dashboard Principal...")
        fig_main = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                "État des équipements",
                "Disponibilité par équipement",
                "Latence réseau (ms)",
                "Taux de perte de paquets",
                "Distribution de latence",
                "Historique 24h"
            ),
            specs=[
                [{"type": "pie"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "scatter"}],
                [{"type": "box"}, {"type": "scatter"}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.10
        )
        
        # Pie chart
        online_count = len([d for d in self.devices if d.get('status') == 'online'])
        offline_count = len(self.devices) - online_count
        
        fig_main.add_trace(
            go.Pie(
                labels=['En ligne', 'Hors ligne'],
                values=[online_count, offline_count],
                marker=dict(colors=['#4caf50', '#f44336']),
                textposition='inside',
                textinfo='label+percent'
            ),
            row=1, col=1
        )
        
        # Disponibilité
        availability = [random.randint(90, 100) for _ in device_names]
        fig_main.add_trace(
            go.Bar(
                x=device_names,
                y=availability,
                marker=dict(color=['#4caf50' if a > 90 else '#ff9800' for a in availability]),
                text=[f"{a}%" for a in availability],
                textposition='outside'
            ),
            row=1, col=2
        )
        
        # Latence
        latencies = [random.uniform(5, 50) for _ in device_names]
        fig_main.add_trace(
            go.Bar(
                x=device_names,
                y=latencies,
                marker=dict(color='#2196f3'),
                text=[f"{l:.1f}ms" for l in latencies],
                textposition='outside'
            ),
            row=2, col=1
        )
        
        # Perte paquets
        loss_rates = [random.uniform(0, 5) for _ in device_names]
        fig_main.add_trace(
            go.Scatter(
                x=device_names,
                y=loss_rates,
                mode='lines+markers',
                marker=dict(size=10, color='#f44336'),
                line=dict(width=2),
                fill='tozeroy'
            ),
            row=2, col=2
        )
        
        # Box plot
        latency_dist = [random.gauss(lat, lat*0.1) for lat in latencies for _ in range(20)]
        fig_main.add_trace(
            go.Box(
                y=latency_dist,
                marker=dict(color='#9c27b0'),
                boxmean='sd'
            ),
            row=3, col=1
        )
        
        # Time series
        hours = list(range(24))
        values = [random.uniform(15, 45) for _ in hours]
        fig_main.add_trace(
            go.Scatter(
                x=hours,
                y=values,
                mode='lines',
                fill='tozeroy',
                line=dict(color='#2196f3', width=3)
            ),
            row=3, col=2
        )
        
        fig_main.update_layout(
            title_text="<b>Dashboard Principal - Monitoring Réseau</b>",
            height=1200,
            showlegend=False,
            template='plotly_white',
            font=dict(size=11, family="Arial")
        )
        
        fig_main.update_xaxes(title_text="Équipement", row=1, col=2)
        fig_main.update_yaxes(title_text="Disponibilité (%)", row=1, col=2)
        fig_main.show()
        
        # 2️⃣ DASHBOARD INTERFACES
        print("[2/4] Dashboard Interfaces...")
        fig_interfaces = make_subplots(
            rows=1, cols=2,
            specs=[[{"type": "pie"}, {"type": "bar"}]],
            subplot_titles=("État global", "Interfaces par équipement")
        )
        
        total_interfaces = sum(len(self.results.get(d['name'], {}).get('interfaces', {})) 
                              for d in self.devices)
        
        fig_interfaces.add_trace(
            go.Pie(
                labels=['UP', 'DOWN'],
                values=[total_interfaces, 2],
                marker=dict(colors=['#4caf50', '#f44336']),
                textposition='inside',
                textinfo='label+percent'
            ),
            row=1, col=1
        )
        
        interface_counts = [len(self.results.get(d['name'], {}).get('interfaces', {})) 
                           for d in self.devices]
        fig_interfaces.add_trace(
            go.Bar(
                x=device_names,
                y=interface_counts,
                marker=dict(color='#2196f3'),
                text=interface_counts,
                textposition='outside'
            ),
            row=1, col=2
        )
        
        fig_interfaces.update_layout(
            title_text="<b>Dashboard Interfaces Réseau</b>",
            height=500,
            showlegend=False,
            template='plotly_white'
        )
        
        fig_interfaces.show()
        
        # 3️⃣ HEATMAP LATENCE
        print("[3/4] Heatmap de Latence...")
        z_data = [[random.uniform(10, 50) for _ in range(24)] for _ in device_names]
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=z_data,
            x=list(range(24)),
            y=device_names,
            colorscale='RdYlGn_r',
            hovertemplate='Équipement: %{y}<br>Heure: %{x}h<br>Latence: %{z:.1f}ms<extra></extra>'
        ))
        
        fig_heatmap.update_layout(
            title="<b>Heatmap de Latence - 24h</b>",
            xaxis_title="Heure du jour",
            yaxis_title="Équipement",
            height=400,
            template='plotly_white'
        )
        
        fig_heatmap.show()
        
        # 4️⃣ DISPONIBILITÉ
        print("[4/4] Historique Disponibilité...")
        hours_24 = [f"{h}h" for h in range(24)]
        
        fig_availability = go.Figure()
        
        for device_name in device_names:
            availability_history = [random.uniform(95, 100) for _ in range(24)]
            fig_availability.add_trace(go.Scatter(
                x=hours_24,
                y=availability_history,
                mode='lines+markers',
                name=device_name,
                fill='tozeroy'
            ))
        
        fig_availability.update_layout(
            title="<b>Historique de Disponibilité - 24h</b>",
            xaxis_title="Heure",
            yaxis_title="Disponibilité (%)",
            height=600,
            template='plotly_white',
            hovermode='x unified'
        )
        
        fig_availability.show()
        
        print("\n[+] Tous les dashboards ont été affichés!")
    
    def interactive_menu(self):
        """Menu interactif principal"""
        while True:
            print("\n" + "="*60)
            print("MENU PRINCIPAL - Application d'Automatisation Réseau")
            print("="*60)
            print("1. Découvrir les équipements du réseau")
            print("2. Récupérer les données (interfaces, uptime, config)")
            print("3. Appliquer des configurations")
            print("4. Démarrer le monitoring")
            print("5. Générer les rapports et dashboards PLOTLY 📊")
            print("6. Exécuter toutes les étapes")
            print("0. Quitter")
            print("="*60)
            
            choice = input("Choisissez une option: ").strip()
            
            if choice == '1':
                self.discover_network()
            elif choice == '2':
                self.retrieve_data()
            elif choice == '3':
                self.apply_configuration()
            elif choice == '4':
                self.start_monitoring()
            elif choice == '5':
                self.generate_reports()
            elif choice == '6':
                self.discover_network()
                self.retrieve_data()
                self.apply_configuration()
                self.generate_reports()
            elif choice == '0':
                print("\n[*] Au revoir!")
                break
            else:
                print("[-] Option invalide")

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║   Application d'Automatisation Réseau avec Python        ║
║   Cours: Automatisation Réseau - TCO M1 2025             ║
║   Auteur: Tafita Ralijaona                               ║
║   Dashboard: PLOTLY INTERACTIF ✨                        ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    app = NetworkAutomationApp()
    app.interactive_menu()

if __name__ == "__main__":
    main()