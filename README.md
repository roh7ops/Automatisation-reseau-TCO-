# Automatisation Réseau — TCO M1

Application complète de gestion, monitoring et automatisation d'infrastructures réseau.

##  Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Prérequis](#prérequis)
- [Installation rapide](#installation-rapide)
- [Guide de prise en main](#guide-de-prise-en-main)
- [Architecture](#architecture)
- [Utilisation](#utilisation)
- [Dépannage](#dépannage)

##  Vue d'ensemble

Cette application offre :
- **Découverte réseau** : détection automatique des équipements
- **Monitoring** : surveillance en temps réel (ping, interfaces, performances)
- **Sauvegarde de configurations** : backup automatisé des configs réseau
- **Génération de rapports** : PDF d'inventaire, performance, audit
- **Dashboard web** : interface React moderne et responsive

**Stack technique** :
- Backend: Python 3.10+ + Flask 2.3+ + SQLite
- Frontend: React + Tailwind CSS
- Collecte: NAPALM (multi-vendeurs), SNMP, ping, SSH

## 🔧 Prérequis

- **Système** : Linux/macOS (Ubuntu 20.04+ recommandé)
- **Python** : 3.10 ou supérieur
  ```bash
  python3 --version
  ```
- **Node.js + npm** : 16.x ou supérieur
  ```bash
  node --version && npm --version
  ```
- **SSH** : accès aux équipements réseau (clés SSH recommandées)
- **pip** : pip3 à jour
  ```bash
  pip3 install --upgrade pip
  ```

## ⚡ Installation rapide

### 1️⃣ Cloner / Accéder au projet
```bash
cd /home/roh/Desktop/AutomatisationReseau
```

### 2️⃣ Initialiser l'environnement Python (backend)
```bash
cd NetworkAutomationApp
chmod +x install.sh
./install.sh
```

### 3️⃣ Initialiser le frontend
```bash
cd frontend
npm install
# ou avec --legacy-peer-deps si erreur de dépendances
npm install --legacy-peer-deps
cd ..
```

### 4️⃣ Tester les deux services

**Terminal 1 — Backend** :
```bash
source venv/bin/activate
python3 app.py
python3 main.py
# Attendez: "API running on http://0.0.0.0:5000"
```

**Terminal 2 — Frontend** (depuis NetworkAutomationApp/frontend) :
```bash
npm start
# S'ouvre auto sur http://localhost:3000
```

 **Succès** : voir l'interface web avec dashboard + boutons Rapports

---

##  Guide de prise en main

### A. Ajouter des équipements réseau

#### Via l'interface web (recommandé)
1. Ouvrir http://localhost:3000
2. Aller à l'onglet **Configuration**
3. Remplir le formulaire :
   - **Hostname** : nom du périphérique (ex: `router-paris`)
   - **IP** : adresse IP SSH (ex: `192.168.1.1`)
   - **Type** : type OS (ex: `cisco_ios`, `linux`)
   - **Username** : utilisateur SSH
   - **Password** : mot de passe (ou clé SSH)
4. Cliquer **Ajouter Équipement**
5. Voir la liste mise à jour

#### Via config YAML (pour bulk import)
1. Éditer `config/devices.yaml` :
   ```yaml
   devices:
     - host: 192.168.226.38
       hostname: server-production
       device_type: linux
       username: admin
       password: MyPassword123
     - host: 10.0.0.1
       hostname: router-main
       device_type: cisco_ios
       username: admin
       password: CiscoSecret
   ```
2. Relancer le backend
3. Les équipements sont chargés

### B. Scanner le réseau

1. **Interface web** → bouton **Scan Network** (onglet Dashboard)
2. Attend 10-30s selon la taille du réseau
3. Affiche les équipements trouvés

Ou **via API curl** :
```bash
curl -X POST http://localhost:5000/api/actions/scan
```

### C. Monitorer un équipement

1. **Interface web** → onglet Dashboard → liste Équipements
2. Cliquer **Monitor** sur l'équipement
3. Affiche status + métriques (CPU, mémoire, interfaces)

Ou **via API** :
```bash
curl http://localhost:5000/api/monitoring/1
```

### D. Créer une sauvegarde

1. **Interface web** → bouton **Backup** sur l'équipement
2. Fichier `.txt` créé dans `backups/` avec timestamp
3. Contient la config complète de l'équipement

Ou **via API** :
```bash
curl -X POST http://localhost:5000/api/actions/backup/1
```

### E. Générer et télécharger des rapports PDF

#### Depuis l'interface web
1. Onglet **Rapports**
2. Trois boutons disponibles :
   - **Rapport d'Inventaire** : liste équipements + specs
   - **Rapport de Performance** : CPU, mémoire, latence
   - **Rapport d'Audit** : conformité, logs actions
3. Clic = téléchargement auto PDF

#### Depuis API (curl)
```bash
# Rapport d'inventaire
curl -o inventaire.pdf http://localhost:5000/api/report/inventory

# Rapport de performance
curl -o performance.pdf http://localhost:5000/api/report/performance

# Rapport d'audit
curl -o audit.pdf http://localhost:5000/api/report/audit
```

### F. Afficher le Dashboard

1. Ouvrir http://localhost:3000
2. Onglet **Dashboard** : widgets résumés
   - Équipements totaux
   - Status réseau
   - Alertes (si config)
3. Onglet **Équipements** : tableau détaillé + actions

---

##  Architecture

```
AutomatisationReseau/
├── NetworkAutomationApp/          # Application principale
│   ├── app.py                     # Backend Flask (routes API)
│   ├── main.py                    # CLI principal
│   ├── setup.py                   # Initialisation
│   ├── requirements.txt           # Dépendances Python
│   ├── modules/                   # Logique métier
│   │   ├── discovery.py           # Découverte réseau
│   │   ├── monitoring.py          # Collecte métriques
│   │   ├── napalm_utils.py        # Abstraction multi-vendeurs
│   │   ├── reports.py             # Génération rapports
│   ├── config/                    # Configuration
│   │   ├── devices.yaml           # Liste équipements
│   │   ├── requirements.txt       # Dépendances optionnelles
│   ├── backups/                   # Sauvegardes configs (.txt)
│   ├── reports/                   # Rapports générés (.txt → .pdf)
│   ├── dashboards/                # Dashboards HTML/Plotly
│   ├── logs/                      # Logs application
├── frontend/                  # React App
│   ├── src/
│   │   ├── App.js             # Composant principal
│   │   ├── api.js             # Appels API
│   │   ├── index.css          # Styles globaux
│   ├── public/
│   ├── package.json
│   ├── package-lock.json
```

---

##  Utilisation avancée

### Endpoints API principaux

| Method | Route | Fonction |
|--------|-------|----------|
| GET | `/api/devices` | Liste tous les équipements |
| POST | `/api/devices` | Ajouter un équipement |
| PUT | `/api/devices/<id>` | Modifier équipement |
| DELETE | `/api/devices/<id>` | Supprimer équipement |
| GET | `/api/monitoring/<id>` | Statut/métriques d'un équipement |
| POST | `/api/actions/scan` | Lancer un scan réseau |
| POST | `/api/actions/backup/<id>` | Créer une sauvegarde |
| GET | `/api/report/inventory` | PDF inventaire |
| GET | `/api/report/performance` | PDF performance |
| GET | `/api/report/audit` | PDF audit |

### Tester l'API (postman / curl)

```bash
# Vérifier santé API
curl http://localhost:5000/api/health

# Lister équipements
curl http://localhost:5000/api/devices

# Ajouter équipement
curl -X POST http://localhost:5000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "test-device",
    "ip": "192.168.1.100",
    "device_type": "linux",
    "username": "root",
    "password": "password"
  }'
```

### Variables d'environnement

Pour le frontend (`.env` dans `frontend/`) :
```
REACT_APP_API_URL=http://localhost:5000/api
```

Pour le backend (`.env` à la racine NetworkAutomationApp) :
```
FLASK_ENV=development
FLASK_DEBUG=1
DATABASE_URL=sqlite:///network_automation.db
```

---

##  Dépannage

###  `react-scripts: not found`
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
npm start
```

###  `Cannot find module 'ajv/dist/compile/codegen'`
```bash
cd frontend
npm install ajv@6.12.6 --save-exact
npm start
```

### Backend ne démarre pas (`ModuleNotFoundError`)
```bash
source venv/bin/activate
pip install -r requirements.txt
pip install reportlab pyyaml
python3 app.py
```

###  Rapports PDF vides
- Vérifier que `reports/` contient des `.txt`
- Exécuter : `python3 main.py` pour générer des rapports initiaux
- Ou créer une fausse sauvegarde : `/api/actions/backup/1`

###  CORS error sur frontend
- Backend doit avoir `CORS` activé (voir `app.py` ligne 17)
- Redémarrer backend si erreur

###  Équipements non trouvés après scan
- Vérifier connectivité SSH : `ssh -v user@host`
- Vérifier `devices.yaml` mal formaté (indentation YAML stricte)
- Vérifier logs backend : `tail -f logs/application.log`

---

## Prochaines étapes

1. **Configurer SNMP** : ajouter collecte SNMP pour plus de métriques
2. **Alertes** : ajouter seuils d'alerte (ex: CPU > 80%)
3. **Historique** : intégrer base de données temps-réel (Prometheus, InfluxDB)
4. **Export avancé** : Excel, JSON pour intégration tiers
5. **Authentification** : ajouter login/JWT pour sécurité

---

##  Support & Contribution

- **Bugs** : ouvrir issue avec logs détaillés
- **Améliorations** : pull requests bienvenues
- **Questions** : documenté dans le wiki (à créer)

---

**Créé pour TCO M1 — Automatisation & Résilience Réseau**
