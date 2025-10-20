#!/usr/bin/env python3
"""
Module de génération de rapports
Rapports d'inventaire, monitoring, dashboards
"""

import json
from datetime import datetime
from pathlib import Path

class ReportGenerator:
    def __init__(self):
        self.report_dir = Path("reports")
        self.report_dir.mkdir(exist_ok=True)
    
    def generate_inventory_report(self, results):
        """
        Génère un rapport d'inventaire complet
        
        Args:
            results: Dictionnaire avec les données collectées
        
        Returns:
            str: Chemin du fichier rapport
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.report_dir / f"inventory_report_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write("="*70 + "\n")
            f.write("RAPPORT D'INVENTAIRE RÉSEAU\n")
            f.write(f"Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*70 + "\n\n")
            
            for device_name, device_data in results.items():
                f.write(f"\n{'─'*70}\n")
                f.write(f"ÉQUIPEMENT: {device_name}\n")
                f.write(f"{'─'*70}\n")
                
                # Facts
                if 'facts' in device_data:
                    facts = device_data['facts']
                    f.write("\n[INFORMATIONS SYSTÈME]\n")
                    f.write(f"  Hostname: {facts.get('hostname', 'N/A')}\n")
                    f.write(f"  Vendeur: {facts.get('vendor', 'N/A')}\n")
                    f.write(f"  Uptime: {facts.get('uptime', 'N/A')}\n")
                    f.write(f"  Kernel: {facts.get('kernel', 'N/A')}\n")
                    f.write(f"  Version OS: {facts.get('os_version', 'N/A')}\n")
                
                # Interfaces
                if 'interfaces' in device_data:
                    interfaces = device_data['interfaces']
                    f.write("\n[INTERFACES RÉSEAU]\n")
                    for iface_name, iface_data in interfaces.items():
                        f.write(f"  Interface: {iface_name}\n")
                        f.write(f"    État: {iface_data.get('status', 'N/A')}\n")
                        f.write(f"    MTU: {iface_data.get('mtu', 'N/A')}\n")
                        addresses = iface_data.get('addresses', [])
                        if addresses:
                            f.write(f"    Adresses IP:\n")
                            for addr in addresses:
                                f.write(f"      - {addr}\n")
                
                # Routes
                if 'routes' in device_data:
                    routes = device_data['routes']
                    f.write("\n[TABLE DE ROUTAGE]\n")
                    for route, route_data in list(routes.items())[:10]:  # Top 10
                        f.write(f"  Route: {route}\n")
                        f.write(f"    Via: {route_data.get('via', 'N/A')}\n")
                        f.write(f"    Interface: {route_data.get('interface', 'N/A')}\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("FIN DU RAPPORT\n")
            f.write("="*70 + "\n")
        
        print(f"[+] Rapport d'inventaire généré: {filename}")
        return str(filename)
    
    def generate_monitoring_report(self, monitoring_data):
        """
        Génère un rapport de monitoring
        
        Args:
            monitoring_data: Dictionnaire avec les données de monitoring
        
        Returns:
            str: Chemin du fichier rapport
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.report_dir / f"monitoring_report_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write("="*70 + "\n")
            f.write("RAPPORT DE MONITORING RÉSEAU\n")
            f.write(f"Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*70 + "\n\n")
            
            for device_name, data in monitoring_data.items():
                f.write(f"\n{'─'*70}\n")
                f.write(f"ÉQUIPEMENT: {device_name}\n")
                f.write(f"{'─'*70}\n")
                
                if isinstance(data, dict):
                    f.write(f"  Succès: {data.get('success', 'N/A')}\n")
                    f.write(f"  Statistiques: {data.get('stats', 'N/A')}\n")
                    
                    if 'min_rtt' in data:
                        f.write(f"  RTT Min: {data['min_rtt']}ms\n")
                        f.write(f"  RTT Avg: {data['avg_rtt']}ms\n")
                        f.write(f"  RTT Max: {data['max_rtt']}ms\n")
                    
                    f.write(f"  Timestamp: {data.get('timestamp', 'N/A')}\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("FIN DU RAPPORT\n")
            f.write("="*70 + "\n")
        
        print(f"[+] Rapport de monitoring généré: {filename}")
        return str(filename)
    
    def generate_json_report(self, results, report_name="report"):
        """
        Génère un rapport au format JSON
        
        Args:
            results: Données à exporter
            report_name: Nom du rapport
        
        Returns:
            str: Chemin du fichier rapport
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.report_dir / f"{report_name}_{timestamp}.json"
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'devices': results
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"[+] Rapport JSON généré: {filename}")
        return str(filename)
    
    def generate_html_report(self, results):
        """
        Génère un rapport HTML interactif
        
        Args:
            results: Données à afficher
        
        Returns:
            str: Chemin du fichier rapport
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.report_dir / f"report_{timestamp}.html"
        
        html_content = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport d'Automatisation Réseau</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .content {
            padding: 40px;
        }
        .device-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin-bottom: 30px;
            padding: 20px;
            background: #f9f9f9;
            transition: all 0.3s ease;
        }
        .device-card:hover {
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .device-title {
            font-size: 1.5em;
            color: #667eea;
            font-weight: bold;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-left: 10px;
        }
        .status-online { background: #4caf50; color: white; }
        .status-offline { background: #f44336; color: white; }
        .info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 15px;
        }
        .info-item {
            background: white;
            padding: 12px;
            border-left: 4px solid #667eea;
        }
        .info-label {
            font-weight: bold;
            color: #667eea;
            font-size: 0.9em;
        }
        .info-value {
            color: #333;
            margin-top: 5px;
        }
        .interfaces-section {
            margin-top: 20px;
        }
        .interfaces-section h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .interface-item {
            background: white;
            padding: 10px;
            margin: 5px 0;
            border-left: 3px solid #764ba2;
            border-radius: 3px;
        }
        .footer {
            background: #f5f5f5;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> Rapport d'Automatisation Réseau</h1>
            <p>Généré le """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        </div>
        
        <div class="content">
"""
        
        for device_name, device_data in results.items():
            html_content += f"""
            <div class="device-card">
                <div class="device-title">
                    🖥️ {device_name}
                    <span class="status-badge status-online">EN LIGNE</span>
                </div>
                
                <div class="info-grid">
"""
            
            if 'facts' in device_data:
                facts = device_data['facts']
                html_content += f"""
                    <div class="info-item">
                        <div class="info-label">Hostname</div>
                        <div class="info-value">{facts.get('hostname', 'N/A')}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Uptime</div>
                        <div class="info-value">{facts.get('uptime', 'N/A')}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Kernel</div>
                        <div class="info-value">{facts.get('kernel', 'N/A')}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">OS Version</div>
                        <div class="info-value">{facts.get('os_version', 'N/A')}</div>
                    </div>
"""
            
            if 'interfaces' in device_data:
                interfaces = device_data['interfaces']
                html_content += """
                </div>
                <div class="interfaces-section">
                    <h3> Interfaces Réseau</h3>
"""
                for iface_name, iface_data in interfaces.items():
                    status = "🟢 UP" if iface_data.get('status') == 'up' else "🔴 DOWN"
                    html_content += f"""
                    <div class="interface-item">
                        <strong>{iface_name}</strong> {status}
                        <div>MTU: {iface_data.get('mtu', 'N/A')} | Adresses: {', '.join(iface_data.get('addresses', ['N/A']))}</div>
                    </div>
"""
                html_content += """
                </div>
"""
            
            html_content += """
            </div>
"""
        
        html_content += """
        </div>
        
        <div class="footer">
            <p>Application d'Automatisation Réseau © 2025 | Cours: TCO M1</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[+] Rapport HTML généré: {filename}")
        return str(filename)
    
    def generate_summary(self, results):
        """
        Génère un résumé textuel
        
        Returns:
            str: Résumé formaté
        """
        summary = "\n"
        summary += "="*70 + "\n"
        summary += "RÉSUMÉ EXÉCUTIF\n"
        summary += "="*70 + "\n"
        
        total_devices = len(results)
        online_devices = len([d for d in results.values() if d])
        
        summary += f"\nNombre total d'équipements: {total_devices}\n"
        summary += f"Équipements en ligne: {online_devices}\n"
        summary += f"Taux de disponibilité: {(online_devices/total_devices*100):.1f}%\n"
        
        summary += "\nÉquipements:\n"
        for device_name in results.keys():
            summary += f"  ✓ {device_name}\n"
        
        summary += "\n" + "="*70 + "\n"
        return summary