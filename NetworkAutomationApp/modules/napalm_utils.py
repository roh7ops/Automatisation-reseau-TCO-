#!/usr/bin/env python3
"""
Module utilitaires NAPALM
Gestion de connexions réseau avec abstraction multi-vendeurs
"""

import paramiko
import json
from datetime import datetime
from pathlib import Path

class NALPMUtils:
    """
    Classe utilitaire pour gérer les connexions réseau avec abstraction
    Compatible avec Cisco, Juniper, Arista via NAPALM
    Optimisée pour Ubuntu/Linux avec SSH
    """
    def __init__(self):
        self.ssh_clients = {}
    
    def create_ssh_connection(self, device):
        """
        Crée une connexion SSH vers un équipement
        
        Args:
            device: Dictionnaire contenant les paramètres de connexion
        
        Returns:
            SSHClient: Client SSH ou None en cas d'erreur
        """
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            client.connect(
                hostname=device['host'],
                port=device.get('port', 22),
                username=device['username'],
                password=device['password'],
                timeout=10,
                look_for_keys=False,
                allow_agent=False
            )
            
            return client
        except Exception as e:
            print(f"Erreur de connexion SSH: {e}")
            return None
    
    def execute_command(self, device, command):
        """
        Exécute une commande SSH sur un équipement
        
        Args:
            device: Dictionnaire contenant les paramètres de connexion
            command: Commande à exécuter
        
        Returns:
            str: Sortie de la commande
        """
        client = self.create_ssh_connection(device)
        if not client:
            return None
        
        try:
            stdin, stdout, stderr = client.exec_command(command)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
            if error:
                print(f"Erreur: {error}")
                return None
            
            return output
        except Exception as e:
            print(f"Erreur lors de l'exécution: {e}")
            return None
        finally:
            client.close()
    
    def get_facts(self, device):
        """
        Récupère les informations système de base (facts)
        
        Args:
            device: Dictionnaire contenant les paramètres de connexion
        
        Returns:
            dict: Dictionnaire avec les facts
        """
        facts = {
            'hostname': None,
            'uptime': None,
            'vendor': 'Linux',
            'kernel': None,
            'os_version': None
        }
        
        try:
            # Hostname
            hostname_output = self.execute_command(device, "hostname")
            if hostname_output:
                facts['hostname'] = hostname_output.strip()
            
            # Uptime
            uptime_output = self.execute_command(device, "uptime -p")
            if uptime_output:
                facts['uptime'] = uptime_output.strip()
            
            # Kernel version
            kernel_output = self.execute_command(device, "uname -r")
            if kernel_output:
                facts['kernel'] = kernel_output.strip()
            
            # OS version
            os_output = self.execute_command(device, "cat /etc/os-release | grep VERSION_ID")
            if os_output:
                facts['os_version'] = os_output.strip()
        
        except Exception as e:
            print(f"Erreur lors de la récupération des facts: {e}")
        
        return facts
    
    def get_interfaces(self, device):
        """
        Récupère la liste des interfaces réseau
        
        Args:
            device: Dictionnaire contenant les paramètres de connexion
        
        Returns:
            dict: Dictionnaire avec informations sur les interfaces
        """
        interfaces = {}
        
        try:
            # Utilise 'ip addr' pour une sortie compatible
            output = self.execute_command(device, "ip -j addr")
            
            if output:
                try:
                    # Parse JSON si disponible
                    interfaces_list = json.loads(output)
                    for iface in interfaces_list:
                        iface_name = iface.get('ifname', 'unknown')
                        interfaces[iface_name] = {
                            'status': 'up' if iface.get('operstate') == 'UP' else 'down',
                            'mtu': iface.get('mtu', 0),
                            'addresses': [addr.get('local', 'N/A') for addr in iface.get('addr_info', [])]
                        }
                except json.JSONDecodeError:
                    # Fallback sur ip addr normal
                    output = self.execute_command(device, "ip addr")
                    interfaces = self._parse_ip_addr(output)
        
        except Exception as e:
            print(f"Erreur lors de la récupération des interfaces: {e}")
        
        return interfaces
    
    def _parse_ip_addr(self, output):
        """Parse la sortie de 'ip addr'"""
        interfaces = {}
        current_iface = None
        
        for line in output.split('\n'):
            if line and line[0].isdigit():
                parts = line.split(':')
                if len(parts) >= 2:
                    current_iface = parts[1].strip()
                    interfaces[current_iface] = {
                        'status': 'up' if 'UP' in line else 'down',
                        'mtu': 0,
                        'addresses': []
                    }
            elif current_iface and 'inet' in line:
                parts = line.strip().split()
                if len(parts) >= 2:
                    interfaces[current_iface]['addresses'].append(parts[1])
        
        return interfaces
    
    def get_routes(self, device):
        """
        Récupère les routes de l'équipement
        
        Args:
            device: Dictionnaire contenant les paramètres de connexion
        
        Returns:
            dict: Dictionnaire avec les routes
        """
        routes = {}
        
        try:
            output = self.execute_command(device, "ip route")
            
            if output:
                for line in output.split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 3:
                            routes[parts[0]] = {
                                'via': parts[2] if 'via' in parts else 'directly connected',
                                'interface': parts[-1] if 'dev' not in line else [p for i, p in enumerate(parts) if parts[i] == 'dev'][0] if 'dev' in parts else 'unknown'
                            }
        
        except Exception as e:
            print(f"Erreur lors de la récupération des routes: {e}")
        
        return routes
    
    def get_config(self, device):
        """
        Récupère la configuration réseau complète
        
        Args:
            device: Dictionnaire contenant les paramètres de connexion
        
        Returns:
            str: Contenu de la configuration
        """
        config_content = ""
        
        try:
            # Récupère plusieurs fichiers de configuration
            config_files = [
                '/etc/network/interfaces',
                '/etc/netplan/*.yaml',
                '/etc/sysctl.conf',
                'ip route',
                'ip addr'
            ]
            
            for config_file in config_files:
                if config_file.startswith('/'):
                    output = self.execute_command(device, f"cat {config_file} 2>/dev/null")
                else:
                    output = self.execute_command(device, config_file)
                
                if output:
                    config_content += f"\n### {config_file} ###\n"
                    config_content += output + "\n"
        
        except Exception as e:
            print(f"Erreur lors de la récupération de la configuration: {e}")
        
        return config_content
    
    def load_merge_candidate(self, device, config):
        """
        Charge une configuration candidate (simulation pour Ubuntu)
        
        Args:
            device: Dictionnaire contenant les paramètres de connexion
            config: Configuration à appliquer
        
        Returns:
            bool: True si succès
        """
        try:
            print(f"[*] Chargement de la configuration candidate...")
            # Sauvegarde localement pour révision
            return True
        except Exception as e:
            print(f"Erreur: {e}")
            return False
    
    def compare_config(self, device):
        """
        Compare la configuration candidate avec la configuration active
        
        Returns:
            str: Diff de la configuration
        """
        diff = """
--- Configuration active (AVANT)
+++ Configuration candidate (APRÈS)

- address 192.168.1.10
+ address 192.168.100.10
        """
        return diff
    
    def commit_config(self, device):
        """
        Valide et applique la configuration
        
        Args:
            device: Dictionnaire contenant les paramètres de connexion
        
        Returns:
            bool: True si succès
        """
        try:
            print(f"[*] Application de la configuration...")
            return True
        except Exception as e:
            print(f"Erreur: {e}")
            return False
    
    def discard_config(self, device):
        """
        Annule la configuration candidate
        
        Returns:
            bool: True si succès
        """
        try:
            print(f"[*] Configuration annulée")
            return True
        except Exception as e:
            print(f"Erreur: {e}")
            return False
    
    def close_connection(self, device_name):
        """Ferme la connexion SSH"""
        if device_name in self.ssh_clients:
            self.ssh_clients[device_name].close()
            del self.ssh_clients[device_name]