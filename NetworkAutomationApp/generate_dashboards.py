#!/usr/bin/env python3
"""
Script pour générer tous les dashboards Plotly
À exécuter après la collecte de données
"""

import os
import json
from pathlib import Path
from datetime import datetime
import random

def create_dashboards_directory():
    """Crée le répertoire dashboards s'il n'existe pas"""
    Path('dashboards').mkdir(exist_ok=True)

def generate_example_data():
    """Génère des données d'exemple pour les dashboards"""
    return {
        'devices': ['server-1', 'server-2', 'server-3'],
        'latencies': [12.5, 15.3, 18.2],
        'availability': [98.5, 99.2, 97.8],
        'loss_rates': [0.1, 0.05, 0.15],
        'interfaces': {'server-1': 5, 'server-2': 4, 'server-3': 6}
    }

def create_main_dashboard_html(data):
    """Crée le dashboard principal"""
    
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Principal - Automatisation Réseau</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .header h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{
            color: #666;
            font-size: 1.1em;
        }}
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .chart-container {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .chart-container:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 50px rgba(0,0,0,0.2);
        }}
        .chart-container h2 {{
            color: #667eea;
            font-size: 1.3em;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .chart {{
            width: 100%;
            height: 400px;
        }}
        .footer {{
            text-align: center;
            color: white;
            padding: 20px;
            margin-top: 30px;
        }}
        .refresh-info {{
            background: rgba(255,255,255,0.1);
            color: white;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Dashboard Principal</h1>
            <p>Application d'Automatisation Réseau - Monitoring en temps réel</p>
            <p style="font-size: 0.9em; color: #999; margin-top: 10px;">
                Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </div>
        
        <div class="refresh-info">
            ⚡ Actualiser la page pour voir les données mises à jour
        </div>
        
        <div class="dashboard-grid">
            <div class="chart-container">
                <h2>🟢 État des Équipements</h2>
                <div id="chart1" class="chart"></div>
            </div>
            
            <div class="chart-container">
                <h2>📶 Disponibilité par Équipement</h2>
                <div id="chart2" class="chart"></div>
            </div>
            
            <div class="chart-container">
                <h2>⏱️ Latence Réseau (ms)</h2>
                <div id="chart3" class="chart"></div>
            </div>
            
            <div class="chart-container">
                <h2>📉 Taux de Perte de Paquets</h2>
                <div id="chart4" class="chart"></div>
            </div>
            
            <div class="chart-container">
                <h2>🌐 Interfaces Réseau</h2>
                <div id="chart5" class="chart"></div>
            </div>
            
            <div class="chart-container">
                <h2>📈 Historique Latence (24h)</h2>
                <div id="chart6" class="chart"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Données
        const devices = {json.dumps(data['devices'])};
        const latencies = {json.dumps(data['latencies'])};
        const availability = {json.dumps(data['availability'])};
        const loss_rates = {json.dumps(data['loss_rates'])};
        
        // Chart 1: Pie chart état équipements
        const chart1Data = [{{
            values: [3, 0],
            labels: ['En ligne', 'Hors ligne'],
            type: 'pie',
            marker: {{colors: ['#4caf50', '#f44336']}}
        }}];
        Plotly.newPlot('chart1', chart1Data, {{
            title: '',
            font: {{family: 'Arial'}},
            margin: {{l: 0, r: 0, t: 0, b: 0}}
        }}, {{responsive: true}});
        
        // Chart 2: Bar chart disponibilité
        const chart2Data = [{{
            x: devices,
            y: availability,
            type: 'bar',
            marker: {{color: availability.map(v => v > 99 ? '#4caf50' : v > 95 ? '#ff9800' : '#f44336')}},
            text: availability.map(v => v.toFixed(1) + '%'),
            textposition: 'outside'
        }}];
        Plotly.newPlot('chart2', chart2Data, {{
            title: '',
            yaxis: {{title: 'Disponibilité (%)'}},
            xaxis: {{title: 'Équipement'}},
            font: {{family: 'Arial'}},
            margin: {{l: 50, r: 50, t: 0, b: 50}}
        }}, {{responsive: true}});
        
        // Chart 3: Bar chart latence
        const chart3Data = [{{
            x: devices,
            y: latencies,
            type: 'bar',
            marker: {{color: '#2196f3'}},
            text: latencies.map(l => l.toFixed(1) + 'ms'),
            textposition: 'outside'
        }}];
        Plotly.newPlot('chart3', chart3Data, {{
            title: '',
            yaxis: {{title: 'Latence (ms)'}},
            xaxis: {{title: 'Équipement'}},
            font: {{family: 'Arial'}},
            margin: {{l: 50, r: 50, t: 0, b: 50}}
        }}, {{responsive: true}});
        
        // Chart 4: Line chart taux de perte
        const chart4Data = [{{
            x: devices,
            y: loss_rates,
            type: 'scatter',
            mode: 'lines+markers',
            marker: {{size: 10, color: '#f44336'}},
            fill: 'tozeroy',
            line: {{width: 2}}
        }}];
        Plotly.newPlot('chart4', chart4Data, {{
            title: '',
            yaxis: {{title: 'Perte (%)'}},
            xaxis: {{title: 'Équipement'}},
            font: {{family: 'Arial'}},
            margin: {{l: 50, r: 50, t: 0, b: 50}}
        }}, {{responsive: true}});
        
        // Chart 5: Pie chart interfaces
        const interfaces_data = {json.dumps(data['interfaces'])};
        const interface_values = Object.values(interfaces_data);
        const chart5Data = [{{
            values: interface_values,
            labels: devices,
            type: 'pie',
            marker: {{colors: ['#2196f3', '#4caf50', '#ff9800']}}
        }}];
        Plotly.newPlot('chart5', chart5Data, {{
            title: '',
            font: {{family: 'Arial'}},
            margin: {{l: 0, r: 0, t: 0, b: 0}}
        }}, {{responsive: true}});
        
        // Chart 6: Time series (historique)
        const hours = Array.from({{length: 24}}, (_, i) => i);
        const values = hours.map(h => Math.random() * 30 + 10);
        const chart6Data = [{{
            x: hours,
            y: values,
            type: 'scatter',
            mode: 'lines',
            fill: 'tozeroy',
            line: {{color: '#2196f3', width: 3}}
        }}];
        Plotly.newPlot('chart6', chart6Data, {{
            title: '',
            xaxis: {{title: 'Heure du jour'}},
            yaxis: {{title: 'Latence (ms)'}},
            font: {{family: 'Arial'}},
            margin: {{l: 50, r: 50, t: 0, b: 50}}
        }}, {{responsive: true}});
    </script>
    
    <div class="footer">
        <p>📊 Application d'Automatisation Réseau © 2025</p>
        <p>Cours: Automatisation Réseau - TCO M1 2025 | Auteur: Tafita Ralijaona</p>
    </div>
</body>
</html>"""
    
    filepath = 'dashboards/network_dashboard.html'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"[+] Créé: {filepath}")
    return filepath

def create_availability_dashboard():
    """Crée le dashboard de disponibilité"""
    
    html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Disponibilité - Automatisation Réseau</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
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
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .info {
            color: #666;
            margin-bottom: 30px;
            font-size: 0.95em;
        }
        #chart {
            width: 100%;
            height: 500px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Historique de Disponibilité</h1>
        <div class="info">
            Suivi de la disponibilité des équipements réseau au cours du temps
        </div>
        <div id="chart"></div>
    </div>
    
    <script>
        const devices = ['server-1', 'server-2', 'server-3'];
        const hours = Array.from({length: 24}, (_, i) => `${i}h`);
        
        const traces = devices.map((device, idx) => ({
            x: hours,
            y: Array.from({length: 24}, () => 95 + Math.random() * 5),
            mode: 'lines+markers',
            name: device,
            fill: 'tozeroy'
        }));
        
        Plotly.newPlot('chart', traces, {
            title: 'Disponibilité - Dernières 24h',
            xaxis: {title: 'Heure'},
            yaxis: {title: 'Disponibilité (%)'},
            hovermode: 'closest'
        }, {responsive: true});
    </script>
</body>
</html>"""
    
    filepath = 'dashboards/availability_dashboard.html'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"[+] Créé: {filepath}")
    return filepath

def create_interfaces_dashboard():
    """Crée le dashboard des interfaces"""
    
    html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interfaces Réseau - Automatisation Réseau</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
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
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .info {
            color: #666;
            margin-bottom: 30px;
        }
        .charts {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .chart-box {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
        }
        .chart-box h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 État des Interfaces Réseau</h1>
        <div class="info">
            Status des interfaces par équipement
        </div>
        
        <div class="charts">
            <div class="chart-box">
                <h3>État Global</h3>
                <div id="chart1" style="height: 300px;"></div>
            </div>
            <div class="chart-box">
                <h3>Interfaces par Équipement</h3>
                <div id="chart2" style="height: 300px;"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Chart 1: État global
        const chart1Data = [{
            labels: ['UP', 'DOWN'],
            values: [12, 3],
            type: 'pie',
            marker: {colors: ['#4caf50', '#f44336']}
        }];
        Plotly.newPlot('chart1', chart1Data, {margin: {l: 0, r: 0, t: 0, b: 0}}, {responsive: true});
        
        // Chart 2: Interfaces par équipement
        const chart2Data = [{
            x: ['server-1', 'server-2', 'server-3'],
            y: [5, 4, 6],
            type: 'bar',
            marker: {color: '#2196f3'}
        }];
        Plotly.newPlot('chart2', chart2Data, {
            xaxis: {title: 'Équipement'},
            yaxis: {title: 'Nombre'},
            margin: {l: 50, r: 50, t: 0, b: 50}
        }, {responsive: true});
    </script>
</body>
</html>"""
    
    filepath = 'dashboards/interfaces_dashboard.html'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"[+] Créé: {filepath}")
    return filepath

def create_latency_heatmap():
    """Crée la heatmap de latence"""
    
    html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Heatmap Latence - Automatisation Réseau</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
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
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
        }
        #chart {
            width: 100%;
            height: 500px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 Heatmap de Latence - Dernières 24h</h1>
        <div id="chart"></div>
    </div>
    
    <script>
        const devices = ['server-1', 'server-2', 'server-3'];
        const hours = Array.from({length: 24}, (_, i) => i);
        
        const z = devices.map(() =>
            hours.map(() => Math.random() * 30 + 10)
        );
        
        const trace = {
            z: z,
            x: hours,
            y: devices,
            type: 'heatmap',
            colorscale: 'RdYlGn_r',
            colorbar: {title: 'Latence (ms)'}
        };
        
        Plotly.newPlot('chart', [trace], {
            title: 'Latence par Équipement et Heure',
            xaxis: {title: 'Heure du jour'},
            yaxis: {title: 'Équipement'},
            width: 1100,
            height: 400
        }, {responsive: true});
    </script>
</body>
</html>"""
    
    filepath = 'dashboards/latency_heatmap.html'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"[+] Créé: {filepath}")
    return filepath

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║   Générateur de Dashboards Plotly                        ║
║   Application d'Automatisation Réseau                    ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    print("[*] Création du répertoire dashboards...")
    create_dashboards_directory()
    
    print("\n[*] Génération des données d'exemple...")
    data = generate_example_data()
    
    print("\n[*] Création des dashboards HTML...")
    create_main_dashboard_html(data)
    create_availability_dashboard()
    create_interfaces_dashboard()
    create_latency_heatmap()
    
    print("\n[+] Tous les dashboards ont été créés!")
    print("\n📊 Fichiers générés:")
    print("    - dashboards/network_dashboard.html")
    print("    - dashboards/availability_dashboard.html")
    print("    - dashboards/interfaces_dashboard.html")
    print("    - dashboards/latency_heatmap.html")
    print("\n[*] Ouvrez les fichiers HTML dans votre navigateur pour voir les dashboards")

if __name__ == '__main__':
    main()