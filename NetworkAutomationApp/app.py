#!/usr/bin/env python3
"""
Flask API Backend pour Application d'Automatisation Réseau
Compatible avec Flask 2.3+
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json
from pathlib import Path

# Configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///network_automation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

db = SQLAlchemy(app)
CORS(app)

# ===== MODÈLES DE BASE DE DONNÉES =====

class Device(db.Model):
    """Modèle pour les équipements réseau"""
    __tablename__ = 'devices'
    
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), unique=True, nullable=False)
    ip = db.Column(db.String(15), unique=True, nullable=False)
    device_type = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='offline')
    uptime = db.Column(db.String(100))
    interfaces_count = db.Column(db.Integer, default=0)
    cpu_usage = db.Column(db.Float, default=0)
    memory_usage = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_check = db.Column(db.DateTime)
    
    # Relations
    monitoring_data = db.relationship('MonitoringData', backref='device', lazy=True, cascade='all, delete-orphan')
    backups = db.relationship('Backup', backref='device', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'hostname': self.hostname,
            'ip': self.ip,
            'device_type': self.device_type,
            'status': self.status,
            'uptime': self.uptime,
            'interfaces_count': self.interfaces_count,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'last_check': self.last_check.isoformat() if self.last_check else None
        }

class MonitoringData(db.Model):
    """Modèle pour les données de monitoring"""
    __tablename__ = 'monitoring_data'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    latency = db.Column(db.Float)  # ms
    packet_loss = db.Column(db.Float)  # %
    cpu_usage = db.Column(db.Float)  # %
    memory_usage = db.Column(db.Float)  # %
    availability = db.Column(db.Float)  # %
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'timestamp': self.timestamp.isoformat(),
            'latency': self.latency,
            'packet_loss': self.packet_loss,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'availability': self.availability
        }

class Backup(db.Model):
    """Modèle pour les sauvegardes de configuration"""
    __tablename__ = 'backups'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    size = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'filename': self.filename,
            'size': self.size,
            'created_at': self.created_at.isoformat()
        }

class Report(db.Model):
    """Modèle pour les rapports"""
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # inventory, monitoring, audit
    filename = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'report_type': self.report_type,
            'filename': self.filename,
            'created_at': self.created_at.isoformat()
        }

# ===== INITIALISATION BASE DE DONNÉES =====

def init_db():
    """Initialise la base de données"""
    with app.app_context():
        db.create_all()
        print("[+] Base de données initialisée")

# ===== ROUTES API =====

# 1. DEVICES ENDPOINTS
@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Récupère tous les équipements"""
    devices = Device.query.all()
    return jsonify([d.to_dict() for d in devices])

@app.route('/api/devices/<int:device_id>', methods=['GET'])
def get_device(device_id):
    """Récupère un équipement spécifique"""
    device = Device.query.get_or_404(device_id)
    return jsonify(device.to_dict())

@app.route('/api/devices', methods=['POST'])
def create_device():
    """Crée un nouvel équipement"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('hostname', 'ip', 'device_type', 'username', 'password')):
        return jsonify({'error': 'Données manquantes'}), 400
    
    if Device.query.filter_by(ip=data['ip']).first():
        return jsonify({'error': 'Cet équipement existe déjà'}), 409
    
    device = Device(
        hostname=data['hostname'],
        ip=data['ip'],
        device_type=data['device_type'],
        username=data['username'],
        password=data['password']
    )
    
    db.session.add(device)
    db.session.commit()
    
    return jsonify(device.to_dict()), 201

@app.route('/api/devices/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    """Met à jour un équipement"""
    device = Device.query.get_or_404(device_id)
    data = request.get_json()
    
    device.status = data.get('status', device.status)
    device.uptime = data.get('uptime', device.uptime)
    device.interfaces_count = data.get('interfaces_count', device.interfaces_count)
    device.cpu_usage = data.get('cpu_usage', device.cpu_usage)
    device.memory_usage = data.get('memory_usage', device.memory_usage)
    device.last_check = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(device.to_dict())

@app.route('/api/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    """Supprime un équipement"""
    device = Device.query.get_or_404(device_id)
    db.session.delete(device)
    db.session.commit()
    
    return jsonify({'message': 'Équipement supprimé'}), 204

# 2. MONITORING ENDPOINTS
@app.route('/api/monitoring/<int:device_id>', methods=['GET'])
def get_monitoring_data(device_id):
    """Récupère les données de monitoring d'un équipement"""
    device = Device.query.get_or_404(device_id)
    
    # Dernières 100 mesures
    data = MonitoringData.query.filter_by(device_id=device_id)\
        .order_by(MonitoringData.timestamp.desc())\
        .limit(100).all()
    
    return jsonify([d.to_dict() for d in reversed(data)])

@app.route('/api/monitoring/<int:device_id>', methods=['POST'])
def create_monitoring_data(device_id):
    """Crée une nouvelle mesure de monitoring"""
    device = Device.query.get_or_404(device_id)
    data = request.get_json()
    
    monitoring = MonitoringData(
        device_id=device_id,
        latency=data.get('latency'),
        packet_loss=data.get('packet_loss'),
        cpu_usage=data.get('cpu_usage'),
        memory_usage=data.get('memory_usage'),
        availability=data.get('availability', 100)
    )
    
    db.session.add(monitoring)
    db.session.commit()
    
    return jsonify(monitoring.to_dict()), 201

# 3. BACKUPS ENDPOINTS
@app.route('/api/backups', methods=['GET'])
def get_backups():
    """Récupère tous les backups"""
    backups = Backup.query.order_by(Backup.created_at.desc()).all()
    return jsonify([b.to_dict() for b in backups])

@app.route('/api/backups/<int:device_id>', methods=['GET'])
def get_device_backups(device_id):
    """Récupère les backups d'un équipement"""
    backups = Backup.query.filter_by(device_id=device_id)\
        .order_by(Backup.created_at.desc()).all()
    return jsonify([b.to_dict() for b in backups])

@app.route('/api/backups', methods=['POST'])
def create_backup():
    """Crée un nouveau backup"""
    data = request.get_json()
    
    backup = Backup(
        device_id=data['device_id'],
        filename=data['filename'],
        content=data.get('content'),
        size=len(data.get('content', '')) if data.get('content') else 0
    )
    
    db.session.add(backup)
    db.session.commit()
    
    return jsonify(backup.to_dict()), 201

# 4. REPORTS ENDPOINTS
@app.route('/api/reports', methods=['GET'])
def get_reports():
    """Récupère tous les rapports"""
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return jsonify([r.to_dict() for r in reports])

@app.route('/api/reports', methods=['POST'])
def create_report():
    """Crée un nouveau rapport"""
    data = request.get_json()
    
    report = Report(
        name=data['name'],
        report_type=data['report_type'],
        filename=data['filename'],
        content=data.get('content')
    )
    
    db.session.add(report)
    db.session.commit()
    
    return jsonify(report.to_dict()), 201

# 5. STATS ENDPOINTS
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Récupère les statistiques globales"""
    total_devices = Device.query.count()
    online_devices = Device.query.filter_by(status='online').count()
    total_interfaces = db.session.query(db.func.sum(Device.interfaces_count)).scalar() or 0
    
    # Moyenne CPU/Mémoire
    avg_cpu = db.session.query(db.func.avg(Device.cpu_usage)).scalar() or 0
    avg_memory = db.session.query(db.func.avg(Device.memory_usage)).scalar() or 0
    
    return jsonify({
        'total_devices': total_devices,
        'online_devices': online_devices,
        'offline_devices': total_devices - online_devices,
        'total_interfaces': total_interfaces,
        'avg_cpu': round(avg_cpu, 2),
        'avg_memory': round(avg_memory, 2),
        'availability': round((online_devices / total_devices * 100) if total_devices > 0 else 0, 2)
    })

# 6. ACTIONS ENDPOINTS
@app.route('/api/actions/scan', methods=['POST'])
def scan_network():
    """Lance une découverte réseau"""
    return jsonify({
        'status': 'scanning',
        'message': 'Scan en cours...'
    }), 202

@app.route('/api/actions/monitor/<int:device_id>', methods=['POST'])
def start_monitoring(device_id):
    """Lance le monitoring sur un équipement"""
    device = Device.query.get_or_404(device_id)
    
    try:
        from modules.monitoring import NetworkMonitoring
        monitoring = NetworkMonitoring()
        
        ping_result = monitoring.ping_monitor(device.ip, count=4)
        
        # Sauvegarder les données
        if ping_result['success']:
            mon_data = MonitoringData(
                device_id=device_id,
                latency=ping_result.get('avg_rtt'),
                packet_loss=0,
                availability=100
            )
            db.session.add(mon_data)
            device.status = 'online'
        else:
            device.status = 'offline'
        
        device.last_check = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': device.status,
            'result': ping_result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/actions/backup/<int:device_id>', methods=['POST'])
def backup_device(device_id):
    """Sauvegarde la configuration d'un équipement"""
    device = Device.query.get_or_404(device_id)
    
    try:
        from modules.napalm_utils import NALPMUtils
        napalm = NALPMUtils()
        
        device_info = {
            'host': device.ip,
            'username': device.username,
            'password': device.password,
            'port': 22,
            'device_type': device.device_type
        }
        
        config = napalm.get_config(device_info)
        
        # Sauvegarder dans DB
        backup = Backup(
            device_id=device_id,
            filename=f'backup_{device.hostname}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.txt',
            content=config,
            size=len(config)
        )
        
        db.session.add(backup)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'backup_id': backup.id,
            'message': 'Backup réussi'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Ressource non trouvée'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Erreur interne du serveur'}), 500

# ===== HEALTH CHECK =====

@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérifie la santé de l'API"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    # Initialiser la BD avant de lancer l'app
    init_db()
    
    print("""
╔══════════════════════════════════════════════════╗
║   API Flask - Automatisation Réseau             ║
║   Démarrage sur http://0.0.0.0:5000             ║
╚══════════════════════════════════════════════════╝
    """)
    
    app.run(debug=True, host='0.0.0.0', port=5000)