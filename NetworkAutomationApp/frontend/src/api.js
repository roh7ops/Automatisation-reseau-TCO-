const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

export { API_URL };

export async function fetchDevices() {
  try {
    const r = await fetch(`${API_URL}/devices`);
    if (!r.ok) return [];
    return await r.json();
  } catch {
    return [];
  }
}

export async function fetchStats() {
  try {
    const r = await fetch(`${API_URL}/stats`);
    if (!r.ok) return {};
    return await r.json();
  } catch {
    return {};
  }
}

export async function addDevice(payload) {
  const r = await fetch(`${API_URL}/devices`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return r.ok;
}

export async function deleteDevice(id) {
  const r = await fetch(`${API_URL}/devices/${id}`, { method: 'DELETE' });
  return r.ok;
}

export async function scanNetwork() {
  const r = await fetch(`${API_URL}/actions/scan`, { method: 'POST' });
  return r.ok;
}

export async function monitorDevice(id) {
  const r = await fetch(`${API_URL}/actions/monitor/${id}`, { method: 'POST' });
  if (!r.ok) return null;
  return await r.json();
}

export async function backupDevice(id) {
  const r = await fetch(`${API_URL}/actions/backup/${id}`, { method: 'POST' });
  return r.ok;
}