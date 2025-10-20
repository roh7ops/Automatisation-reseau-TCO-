#!/usr/bin/env python3
"""
Module de monitoring réseau
Ping monitoring, SNMP, collecte de métriques
"""

import subprocess
import sys
import re
from datetime import datetime
import statistics

class NetworkMonitoring:
    def __init__(self):
        self.monitoring_history = {}
    
    @staticmethod
    def ping_monitor(host, count=4, timeout=2):
        """
        Monitoring par ping avec statistiques détaillées
        
        Args:
            host: Adresse IP ou hostname
            count: Nombre de pings à envoyer
            timeout: Timeout par ping en secondes
        
        Returns:
            dict: Résultats du ping (succès, stats, RTT, etc.)
        """
        try:
            param = "-n" if sys.platform == "win32" else "-c"
            timeout_param = "-w" if sys.platform == "win32" else "-W"
            
            command = [
                "ping",
                param, str(count),
                timeout_param, str(timeout*1000),
                host
            ]
            
            result = subprocess.run(command, capture_output=True, text=True, timeout=count*timeout+2)
            
            if result.returncode == 0:
                return NetworkMonitoring._parse_ping_output(result.stdout, host)
            else:
                return {
                    'success': False,
                    'host': host,
                    'timestamp': datetime.now().isoformat(),
                    'stats': 'Impossible de joindre'
                }
        
        except Exception as e:
            return {
                'success': False,
                'host': host,
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'stats': 'Erreur'
            }
    
    @staticmethod
    def _parse_ping_output(output, host):
        """Parse la sortie du ping pour extraire les statistiques"""
        
        # Linux/Mac pattern
        match = re.search(r'min/avg/max/[a-z]+ = ([\d.]+)/([\d.]+)/([\d.]+)', output)
        if match:
            return {
                'success': True,
                'host': host,
                'timestamp': datetime.now().isoformat(),
                'min_rtt': float(match.group(1)),
                'avg_rtt': float(match.group(2)),
                'max_rtt': float(match.group(3)),
                'stats': f"min={match.group(1)}ms avg={match.group(2)}ms max={match.group(3)}ms"
            }
        
        # Windows pattern
        match = re.search(r'Minimum = (\d+)ms, Maximum = (\d+)ms, Average = (\d+)ms', output)
        if match:
            return {
                'success': True,
                'host': host,
                'timestamp': datetime.now().isoformat(),
                'min_rtt': int(match.group(1)),
                'max_rtt': int(match.group(2)),
                'avg_rtt': int(match.group(3)),
                'stats': f"min={match.group(1)}ms avg={match.group(3)}ms max={match.group(2)}ms"
            }
        
        return {
            'success': False,
            'host': host,
            'timestamp': datetime.now().isoformat(),
            'stats': 'Impossible de parser'
        }
    
    @staticmethod
    def check_interface_status(device, interface_name):
        """
        Vérifie l'état d'une interface réseau
        
        Args:
            device: Paramètres de connexion
            interface_name: Nom de l'interface (ex: eth0)
        
        Returns:
            dict: État de l'interface
        """
        try:
            import paramiko
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=device['host'],
                port=device.get('port', 22),
                username=device['username'],
                password=device['password'],
                timeout=5
            )
            
            stdin, stdout, stderr = client.exec_command(f"ip link show {interface_name}")
            output = stdout.read().decode('utf-8')
            
            is_up = 'UP' in output
            client.close()
            
            return {
                'interface': interface_name,
                'status': 'UP' if is_up else 'DOWN',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'interface': interface_name,
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    @staticmethod
    def get_interface_stats(device, interface_name):
        """
        Récupère les statistiques d'une interface
        
        Args:
            device: Paramètres de connexion
            interface_name: Nom de l'interface
        
        Returns:
            dict: Statistiques (RX/TX bytes, packets, errors)
        """
        try:
            import paramiko
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=device['host'],
                port=device.get('port', 22),
                username=device['username'],
                password=device['password'],
                timeout=5
            )
            
            stdin, stdout, stderr = client.exec_command(f"cat /sys/class/net/{interface_name}/statistics/rx_bytes")
            rx_bytes = stdout.read().decode('utf-8').strip()
            
            stdin, stdout, stderr = client.exec_command(f"cat /sys/class/net/{interface_name}/statistics/tx_bytes")
            tx_bytes = stdout.read().decode('utf-8').strip()
            
            client.close()
            
            return {
                'interface': interface_name,
                'rx_bytes': int(rx_bytes),
                'tx_bytes': int(tx_bytes),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'interface': interface_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def track_host_availability(self, host, duration_minutes=60):
        """
        Suivi de la disponibilité d'un hôte pendant une période donnée
        
        Args:
            host: Adresse IP
            duration_minutes: Durée du suivi en minutes
        
        Returns:
            dict: Statistiques de disponibilité
        """
        if host not in self.monitoring_history:
            self.monitoring_history[host] = []
        
        results = []
        intervals = duration_minutes
        
        for i in range(intervals):
            ping_result = self.ping_monitor(host, count=1)
            results.append(ping_result['success'])
            self.monitoring_history[host].append(ping_result)
        
        success_rate = (sum(results) / len(results)) * 100
        
        return {
            'host': host,
            'total_checks': len(results),
            'successful_checks': sum(results),
            'failed_checks': len(results) - sum(results),
            'availability_percentage': success_rate,
            'history': self.monitoring_history[host]
        }
    
    @staticmethod
    def check_cpu_usage(device):
        """
        Récupère l'utilisation CPU
        
        Args:
            device: Paramètres de connexion
        
        Returns:
            dict: Informations CPU
        """
        try:
            import paramiko
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=device['host'],
                port=device.get('port', 22),
                username=device['username'],
                password=device['password'],
                timeout=5
            )
            
            stdin, stdout, stderr = client.exec_command("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'")
            cpu_usage = stdout.read().decode('utf-8').strip()
            
            client.close()
            
            return {
                'cpu_usage': cpu_usage,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    @staticmethod
    def check_memory_usage(device):
        """
        Récupère l'utilisation mémoire
        
        Args:
            device: Paramètres de connexion
        
        Returns:
            dict: Informations mémoire
        """
        try:
            import paramiko
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=device['host'],
                port=device.get('port', 22),
                username=device['username'],
                password=device['password'],
                timeout=5
            )
            
            stdin, stdout, stderr = client.exec_command("free -h | grep Mem")
            memory_info = stdout.read().decode('utf-8').strip()
            
            client.close()
            
            return {
                'memory_info': memory_info,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }