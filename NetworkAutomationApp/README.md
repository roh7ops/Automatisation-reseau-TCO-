# NetworkAutomationApp — Automatisation Réseau (TCO M1)

Résumé
- Application Python + React pour découverte, monitoring, sauvegarde et génération de rapports réseau.
- Backend: Flask (app.py) + SQLite.
- Frontend: React (frontend/) créé avec Create React App.
- Rapports texte/HTML/PDF dans le dossier `reports/`.

Prérequis
- Linux / macOS (Ubuntu recommandé)
- Python 3.10+
- Node.js 16+ et npm
- SSH accès aux équipements (pour collecte réelle)

Installation rapide
1. Depuis le répertoire NetworkAutomationApp :
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt

2. Frontend :
   cd frontend
   npm install
   # dev
   npm start
   # ou build pour production
   npm run build
   cd ..

Lancement
- Backend (API + sert le build si présent) :
  source venv/bin/activate
  python3 app.py
  -> API disponible sur http://localhost:5000

- Frontend dev :
  cd frontend
  npm start
  -> UI sur http://localhost:3000

Fonctionnalités utiles
- Endpoints de rapport (PDF téléchargeable) :
  /api/report/inventory
  /api/report/performance
  /api/report/audit

- Gestion des équipements via API :
  GET/POST/PUT/DELETE /api/devices

- Actions :
  POST /api/actions/scan
  POST /api/actions/monitor/<id>
  POST /api/actions/backup/<id>

Configuration
- Liste d'équipements : `devices.yaml` (racine ou `config/devices.yaml`).
- Rapports et sauvegardes : dossiers `reports/` et `backups/`.

Génération de rapports PDF
- Le backend transforme les .txt dans `reports/` en PDF lors de l'appel à /api/report/<type>.
- Le frontend déclenche le téléchargement via fetch + Content-Disposition.

Dépannage rapide
- Si `react-scripts` introuvable : `cd frontend && npm install`
- Problème ajv / ajv-keywords : installer `ajv@6.12.6` ou supprimer et réinstaller les modules (`rm -rf node_modules package-lock.json && npm install --legacy-peer-deps`).
- Vérifier que `reports/` contient des fichiers .txt pour générer le PDF.

Structure principale
- app.py — backend Flask
- main.py, modules/ — logique CLI / collecte / monitoring
- frontend/ — React UI
- reports/, backups/, dashboards/ — données et sorties

Contribuer
- Utiliser des branches git, commit clair, tests pytest si ajout de fonctions Python.

Licence
- Projet éducatif (ajoutez licence si besoin).