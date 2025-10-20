#!/usr/bin/env python3
"""
CLI intégré avec API REST
Envoie les données vers la base de données en temps réel
"""

import os
import sys
import yaml
import time
import requests
import json
from pathlib import Path
from datetime import datetime
from modules.discovery import NetworkDiscovery
from modules.napalm_utils import NALPMUtils
from modules.monitoring import NetworkMonitoring
from modules.reports import ReportGenerator

# Configuration API
API_URL = "http://localhost:5000/api"
TIMEOUT = 5

class NetworkAutomationCLI:
    def __init__(self, config_file="devices.yaml"):
        self.config_file = config_file
        self.devices = []
        self.results = {}
        self.monitoring_data = {}
        
        print("[*] Initialisation de l'application d'automatisation réseau")
        print("[*] Connexion à l'API: " + API_URL)
        
        # Vérifier la connexion API
        if not self.check_api_connection():
            print("[!] API non disponible. Continuez en mode local.")
            self.api_available = False
        else:
            print("[+] API disponible")
            self.api_available = True
        
        self.load_devices()
    
    def check_api_connection(self):
        """Vérifie si l'API est accessible"""
        try:
            response = requests.get(f"{API_URL}/health", timeout=TIMEOUT)
            return response.status_code == 200
        except:
            return False
    
    def load_devices(self):
        """Charge les équipements"""
        if not os.path.exists(self.config_file):
            print(f"[!] Fichier {self.config_file} non trouvé")
            return
        
        with open(self.config_file, 'r') as f:
            config = yaml.safe_load(f)
            self.devices = config.get('devices', [])
        
        print(f"[+] {len(self.devices)} équipement(s) chargé(s)")
        for device in self.devices:
            print(f"    - {device['host']} ({device.get('name', 'N/A')})")
    
    def sync_device_to_api(self, device, status='offline'):
        """Synchronise un équipement avec l'API"""
        if not self.api_available:
            return None
        
        try:
            device_data = {
                'hostname': device.get('name', device['host']),
                'ip': device['host'],
                'device_type': device.get('device_type', 'linux'),
                'username': device.get('username', 'ubuntu'),
                'password': device.get('password', ''),
                'status': status
            }
            
            # Vérifie si l'équipement existe déjà
            devices = requests.get(f"{API_URL}/devices", timeout=TIMEOUT).json()
            existing = next((d for d in devices if d['ip'] == device['host']), None)
            
            if existing:
                # Mettre à jour
                response = requests.put(
                    f"{API_URL}/devices/{existing['id']}",
                    json=device_data,
                    timeout=TIMEOUT
                )
                return response.json()
            else:
                # Créer
                response = requests.post(
                    f"{API_URL}/devices",
                    json=device_data,
                    timeout=TIMEOUT
                )
                return response.json()
        except Exception as e:
            print(f"[!] Erreur de synchronisation: {e}")
            return None
    
    def discover_network(self):
        """Étape 1: Découverte réseau"""
        print("\n" + "="*60)
        print("[*] ÉTAPE 1: DÉCOUVERTE DU RÉSEAU")
        print("="*60)
        
        discovery = NetworkDiscovery()
        
        for device in self.devices:
            print(f"\n[*] Vérification de {device.get('name', device['host'])}")
            
            if discovery.ping_host(device['host']):
                print(f"    [+] Hôte accessible")
                device['status'] = 'online'
            else:
                print(f"    [-] Hôte inaccessible")
                device['status'] = 'offline'
            
            # Synchroniser avec l'API
            self.sync_device_to_api(device, device['status'])
        
        print("\n[+] Découverte complétée")
    
    def retrieve_data(self):
        """Étape 2: Récupération de données"""
        print("\n" + "="*60)
        print("[*] ÉTAPE 2: RÉCUPÉRATION DES DONNÉES")
        print("="*60)
        
        napalm = NALPMUtils()
        
        for device in self.devices:
            if device.get('status') != 'online':
                print(f"\n[-] {device.get('name', device['host'])} hors ligne")
                continue
            
            device_name = device.get('name', device['host'])
            print(f"\n[*] Récupération de données pour {device_name}")
            self.results[device_name] = {}
            
            try:
                # Facts
                print(f"    [*] Récupération des facts...")
                facts = napalm.get_facts(device)
                self.results[device_name]['facts'] = facts
                print(f"    [+] Hostname: {facts.get('hostname', 'N/A')}")
                
                # Interfaces
                print(f"    [*] Récupération des interfaces...")
                interfaces = napalm.get_interfaces(device)
                self.results[device_name]['interfaces'] = interfaces
                print(f"    [+] {len(interfaces)} interface(s)")
                
                # Sauvegarder dans API
                if self.api_available:
                    try:
                        devices = requests.get(f"{API_URL}/devices", timeout=TIMEOUT).json()
                        device_record = next((d for d in devices if d['ip'] == device['host']), None)
                        
                        if device_record:
                            requests.put(
                                f"{API_URL}/devices/{device_record['id']}",
                                json={
                                    'status': 'online',
                                    'interfaces_count': len(interfaces),
                                    'uptime': facts.get('uptime', 'N/A')
                                },
                                timeout=TIMEOUT
                            )
                    except:
                        pass
                
            except Exception as e:
                print(f"    [!] Erreur: {str(e)}")
        
        print("\n[+] Récupération complétée")
    
    def monitoring_with_api_sync(self):
        """Monitoring avec synchronisation API"""
        print("\n" + "="*60)
        print("[*] MONITORING RÉSEAU (Ctrl+C pour arrêter)")
        print("="*60)
        
        monitoring = NetworkMonitoring()
        
        try:
            iteration = 0
            while True:
                iteration += 1
                print(f"\n[*] Itération {iteration} - {datetime.now().strftime('%H:%M:%S')}")
                
                for device in self.devices:
                    if device.get('status') != 'online':
                        continue
                    
                    device_name = device.get('name', device['host'])
                    ping_result = monitoring.ping_monitor(device['host'], count=4)
                    self.monitoring_data[device_name] = ping_result
                    
                    status = "[+]" if ping_result['success'] else "[-]"
                    print(f"{status} {device_name}: {ping_result['stats']}")
                    
                    # Synchroniser avec API
                    if self.api_available and ping_result['success']:
                        try:
                            devices = requests.get(f"{API_URL}/devices", timeout=TIMEOUT).json()
                            device_record = next((d for d in devices if d['ip'] == device['host']), None)
                            
                            if device_record:
                                monitoring_data = {
                                    'latency': ping_result.get('avg_rtt'),
                                    'packet_loss': 0,
                                    'availability': 100
                                }
                                
                                requests.post(
                                    f"{API_URL}/monitoring/{device_record['id']}",
                                    json=monitoring_data,
                                    timeout=TIMEOUT
                                )
                        except:
                            pass
                
                time.sleep(10)
        
        except KeyboardInterrupt:
            print("\n\n[*] Monitoring arrêté")
    
    def generate_reports_with_api(self):
        """Génère les rapports et les sauvegarde dans l'API"""
        print("\n" + "="*60)
        print("[*] GÉNÉRATION DE RAPPORTS")
        print("="*60)
        
        reporter = ReportGenerator()
        
        # Rapport d'inventaire
        report_file = reporter.generate_inventory_report(self.results)
        print(f"[+] Rapport généré: {report_file}")
        
        # Sauvegarder dans l'API
        if self.api_available and os.path.exists(report_file):
            try:
                with open(report_file, 'r') as f:
                    content = f.read()
                
                report_data = {
                    'name': Path(report_file).stem,
                    'report_type': 'inventory',
                    'filename': Path(report_file).name,
                    'content': content
                }
                
                response = requests.post(
                    f"{API_URL}/reports",
                    json=report_data,
                    timeout=TIMEOUT
                )
                print(f"[+] Rapport synchronisé avec l'API")
            except Exception as e:
                print(f"[!] Erreur de synchronisation: {e}")
    
    def interactive_menu(self):
        """Menu interactif"""
        while True:
            print("\n" + "="*60)
            print("MENU PRINCIPAL - Application d'Automatisation Réseau")
            if self.api_available:
                print("(Mode API activé - Synchronisation en temps réel)")
            else:
                print("(Mode local - Pas d'API disponible)")
            print("="*60)
            print("1. Découvrir les équipements")
            print("2. Récupérer les données")
            print("3. Monitoring réseau")
            print("4. Générer les rapports")
            print("5. Exécuter toutes les étapes")
            print("0. Quitter")
            print("="*60)
            
            choice = input("Choisissez une option: ").strip()
            
            if choice == '1':
                self.discover_network()
            elif choice == '2':
                self.retrieve_data()
            elif choice == '3':
                self.monitoring_with_api_sync()
            elif choice == '4':
                self.generate_reports_with_api()
            elif choice == '5':
                self.discover_network()
                self.retrieve_data()
                self.generate_reports_with_api()
            elif choice == '0':
                print("\n[*] Au revoir!")
                break
            else:
                print("[-] Option invalide")

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║   Application d'Automatisation Réseau                    ║
║   Mode: CLI + API + Base de Données                      ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    app = NetworkAutomationCLI()
    app.interactive_menu()

if __name__ == "__main__":
    main()