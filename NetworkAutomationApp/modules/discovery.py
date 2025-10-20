#!/usr/bin/env python3
"""
Module de découverte réseau
Vérifie la disponibilité des équipements (ping, SSH, etc.)
"""

import socket
import subprocess
import sys
from pathlib import Path

class NetworkDiscovery:
    def __init__(self):
        pass
    
    @staticmethod
    def ping_host(host, timeout=2):
        """
        Teste la connectivité d'un hôte via ping
        
        Args:
            host: Adresse IP ou hostname
            timeout: Timeout en secondes
        
        Returns:
            bool: True si l'hôte est accessible, False sinon
        """
        try:
            # Adaptation pour Windows et Linux/Mac
            param = "-n" if sys.platform == "win32" else "-c"
            command = ["ping", param, "1", "-W" if sys.platform != "win32" else "-w", 
                      str(timeout*1000), host]
            
            result = subprocess.run(command, capture_output=True, timeout=timeout+1)
            return result.returncode == 0
        except Exception as e:
            print(f"Erreur lors du ping: {e}")
            return False
    
    @staticmethod
    def check_ssh_port(host, port=22, timeout=2):
        """
        Vérifie si le port SSH est ouvert
        
        Args:
            host: Adresse IP ou hostname
            port: Port SSH (défaut 22)
            timeout: Timeout en secondes
        
        Returns:
            bool: True si le port est ouvert, False sinon
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception as e:
            print(f"Erreur lors de la vérification SSH: {e}")
            return False
    
    @staticmethod
    def check_common_ports(host, ports=None, timeout=1):
        """
        Vérifie les ports courants
        
        Args:
            host: Adresse IP ou hostname
            ports: Liste des ports à vérifier (défaut: [22, 80, 443])
            timeout: Timeout en secondes
        
        Returns:
            dict: Dictionnaire avec état des ports
        """
        if ports is None:
            ports = [22, 80, 443, 161]  # SSH, HTTP, HTTPS, SNMP
        
        open_ports = {}
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                sock.close()
                open_ports[port] = (result == 0)
            except Exception:
                open_ports[port] = False
        
        return open_ports
    
    @staticmethod
    def get_hostname(host, timeout=2):
        """
        Récupère le hostname d'une adresse IP
        
        Args:
            host: Adresse IP
            timeout: Timeout en secondes
        
        Returns:
            str: Hostname ou l'IP si non résolvable
        """
        try:
            hostname = socket.gethostbyaddr(host)[0]
            return hostname
        except (socket.herror, socket.timeout):
            return host
    
    @staticmethod
    def scan_network(network_range):
        """
        Scan simple d'une plage réseau
        
        Args:
            network_range: Plage sous forme "192.168.1.0/24" ou "192.168.1.1-254"
        
        Returns:
            list: Liste des hôtes accessibles
        """
        accessible_hosts = []
        
        # Exemple simple: scan de 192.168.1.1 à 192.168.1.254
        if "-" in network_range:
            parts = network_range.split(".")
            start = int(network_range.split("-")[1].split(".")[0])
            end = int(network_range.split("-")[1])
            base = ".".join(parts[:-1])
            
            for i in range(start, end+1):
                host = f"{base}.{i}"
                if NetworkDiscovery.ping_host(host, timeout=1):
                    accessible_hosts.append(host)
        
        return accessible_hosts