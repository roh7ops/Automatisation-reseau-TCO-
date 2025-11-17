import React, { useState, useEffect } from 'react';
import { Activity, Server, BarChart3, AlertCircle, CheckCircle, RefreshCw, Plus, Trash2, Database, Network } from 'lucide-react';
import * as api from './api';

const NetworkAutomationApp = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [devices, setDevices] = useState([]);
  const [stats, setStats] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [newDevice, setNewDevice] = useState({
    hostname: '',
    ip: '',
    device_type: 'cisco_ios',
    username: '',
    password: ''
  });

  const API_URL = api.API_URL;

  useEffect(() => {
    const load = async () => {
      setDevices(await api.fetchDevices());
      setStats(await api.fetchStats());
    };
    load();
    const interval = setInterval(load, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchDevices = async () => {
    setDevices(await api.fetchDevices());
  };

  const fetchStats = async () => {
    setStats(await api.fetchStats());
  };

  const addDevice = async () => {
    if (!newDevice.hostname || !newDevice.ip || !newDevice.username) {
      alert('Veuillez remplir tous les champs');
      return;
    }
    const ok = await api.addDevice(newDevice);
    if (ok) {
      alert('Équipement ajouté avec succès');
      setNewDevice({ hostname: '', ip: '', device_type: 'cisco_ios', username: '', password: '' });
      fetchDevices();
    } else {
      alert('Échec ajout équipement');
    }
  };

  const deleteDevice = async (deviceId) => {
    if (!window.confirm('Êtes-vous sûr?')) return;
    const ok = await api.deleteDevice(deviceId);
    if (ok) {
      alert('Équipement supprimé');
      fetchDevices();
    } else {
      alert('Échec suppression');
    }
  };

  const scanNetwork = async () => {
    setIsLoading(true);
    try {
      await api.scanNetwork();
      setTimeout(fetchDevices, 2000);
    } finally {
      setIsLoading(false);
    }
  };

  const monitorDevice = async (deviceId) => {
    try {
      const data = await api.monitorDevice(deviceId);
      if (data) {
        alert(`Statut: ${data.status}`);
        fetchDevices();
      } else {
        alert('Échec monitoring');
      }
    } catch (error) {
      console.error(error);
    }
  };

  const backupDevice = async (deviceId) => {
    const ok = await api.backupDevice(deviceId);
    if (ok) {
      alert('Backup créé avec succès');
      fetchDevices();
    } else {
      alert('Échec backup');
    }
  };

  // télécharge un rapport PDF depuis le backend (/api/report/<type>)
  const downloadReport = async (type) => {
    try {
      const resp = await fetch(`${api.API_URL}/report/${type}`, { method: 'GET' });
      if (!resp.ok) {
        alert('Erreur génération rapport');
        return;
      }
      const cd = resp.headers.get('content-disposition') || '';
      const m = cd.match(/filename\*?=(?:UTF-8'')?["']?([^;"']+)/i);
      const filename = m ? decodeURIComponent(m[1]) : `${type}_report.pdf`;
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert('Erreur téléchargement');
    }
  };

  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Équipements Totaux</p>
              <p className="text-3xl font-bold mt-2">{stats.total_devices || 0}</p>
            </div>
            <Server className="w-12 h-12 text-blue-200" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">En Ligne</p>
              <p className="text-3xl font-bold mt-2">{stats.online_devices || 0}</p>
            </div>
            <CheckCircle className="w-12 h-12 text-green-200" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-100 text-sm">Hors Ligne</p>
              <p className="text-3xl font-bold mt-2">{stats.offline_devices || 0}</p>
            </div>
            <AlertCircle className="w-12 h-12 text-yellow-200" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Disponibilité</p>
              <p className="text-3xl font-bold mt-2">{(stats.availability || 0).toFixed(1)}%</p>
            </div>
            <Network className="w-12 h-12 text-purple-200" />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <BarChart3 className="w-5 h-5 mr-2 text-blue-600" />
          Statut des Équipements
        </h3>
        <div className="space-y-3">
          {devices.map(device => (
            <div key={device.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
              <div>
                <p className="font-medium text-gray-800">{device.hostname}</p>
                <p className="text-sm text-gray-600">{device.ip}</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                device.status === 'online' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {device.status === 'online' ? 'En ligne' : 'Hors ligne'}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderDevices = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">Gestion des Équipements</h2>
        <button
          onClick={scanNetwork}
          disabled={isLoading}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          {isLoading ? 'Scan en cours...' : 'Scanner'}
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {devices.map(device => (
          <div key={device.id} className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-800">{device.hostname}</h3>
                <p className="text-sm text-gray-600">{device.ip} • {device.device_type}</p>
                {device.uptime && (
                  <p className="text-sm text-gray-600 mt-2">Uptime: {device.uptime}</p>
                )}
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => monitorDevice(device.id)}
                  className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition"
                  title="Monitorer"
                >
                  <Activity className="w-5 h-5" />
                </button>
                <button
                  onClick={() => backupDevice(device.id)}
                  className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition"
                  title="Backup"
                >
                  <Database className="w-5 h-5" />
                </button>
                <button
                  onClick={() => deleteDevice(device.id)}
                  className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                  title="Supprimer"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="pt-4 border-t border-gray-200">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">CPU</span>
                    <span className="font-medium">{device.cpu_usage.toFixed(1)}%</span>
                  </div>
                  <div className="bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all ${device.cpu_usage > 60 ? 'bg-red-500' : 'bg-green-500'}`}
                      style={{ width: `${device.cpu_usage}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">Mémoire</span>
                    <span className="font-medium">{device.memory_usage.toFixed(1)}%</span>
                  </div>
                  <div className="bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all ${device.memory_usage > 60 ? 'bg-red-500' : 'bg-green-500'}`}
                      style={{ width: `${device.memory_usage}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderConfiguration = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Ajouter un Équipement</h2>
      
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Hostname"
              value={newDevice.hostname}
              onChange={(e) => setNewDevice({...newDevice, hostname: e.target.value})}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              placeholder="Adresse IP"
              value={newDevice.ip}
              onChange={(e) => setNewDevice({...newDevice, ip: e.target.value})}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="text"
              placeholder="Utilisateur"
              value={newDevice.username}
              onChange={(e) => setNewDevice({...newDevice, username: e.target.value})}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="password"
              placeholder="Mot de passe"
              value={newDevice.password}
              onChange={(e) => setNewDevice({...newDevice, password: e.target.value})}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button
            onClick={addDevice}
            className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition"
          >
            Ajouter l'Équipement
          </button>
        </div>
      </div>
    </div>
  );

  const renderReports = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Rapports et Monitoring</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Disponibilité</h3>
          <div className="space-y-4">
            {devices.map(device => (
              <div key={device.id}>
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-medium text-gray-800">{device.hostname}</span>
                  <span className="text-gray-600">
                    {device.status === 'online' ? '99.9%' : '0%'}
                  </span>
                </div>
                <div className="bg-gray-200 rounded-full h-3">
                  <div 
                    className={`h-3 rounded-full transition-all ${device.status === 'online' ? 'bg-green-500' : 'bg-red-500'}`}
                    style={{ width: device.status === 'online' ? '99.9%' : '0%' }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Statistiques</h3>
          <div className="space-y-4">
            {devices.map(device => (
              <div key={device.id} className="text-sm">
                <p className="font-medium text-gray-800 mb-2">{device.hostname}</p>
                <div className="flex justify-between mb-1">
                  <span className="text-gray-600">CPU: {device.cpu_usage.toFixed(1)}%</span>
                  <span className="text-gray-600">RAM: {device.memory_usage.toFixed(1)}%</span>
                </div>
                <div className="flex gap-2">
                  <div className="flex-1 bg-gray-200 rounded h-2">
                    <div className="bg-blue-500 h-2 rounded transition-all" style={{width: `${device.cpu_usage}%`}}></div>
                  </div>
                  <div className="flex-1 bg-gray-200 rounded h-2">
                    <div className="bg-purple-500 h-2 rounded transition-all" style={{width: `${device.memory_usage}%`}}></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Générer un Rapport</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button onClick={() => downloadReport('inventory')} className="p-4 border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 font-medium transition">
            Rapport d'Inventaire
          </button>
          <button onClick={() => downloadReport('performance')} className="p-4 border-2 border-green-600 text-green-600 rounded-lg hover:bg-green-50 font-medium transition">
            Rapport de Performance
          </button>
          <button onClick={() => downloadReport('audit')} className="p-4 border-2 border-purple-600 text-purple-600 rounded-lg hover:bg-purple-50 font-medium transition">
            Rapport d'Audit
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <nav className="bg-white shadow-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <Network className="w-8 h-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-800">Network Automation Platform</span>
            </div>
            <div className="flex items-center px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
              API: Connectée
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex space-x-4 mb-8 overflow-x-auto pb-2">
          {[
            { id: 'dashboard', label: 'Tableau de Bord', icon: BarChart3 },
            { id: 'devices', label: 'Équipements', icon: Server },
            { id: 'configuration', label: 'Ajouter', icon: Plus },
            { id: 'reports', label: 'Rapports', icon: Network }
          ].map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center px-6 py-3 rounded-lg font-medium transition-all whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                <Icon className="w-5 h-5 mr-2" />
                {tab.label}
              </button>
            );
          })}
        </div>

        <div>
          {activeTab === 'dashboard' && renderDashboard()}
          {activeTab === 'devices' && renderDevices()}
          {activeTab === 'configuration' && renderConfiguration()}
          {activeTab === 'reports' && renderReports()}
        </div>
      </div>
    </div>
  );
};

export default NetworkAutomationApp;