# Frontend — NetworkAutomationApp

Ce dossier contient l'interface React (Create React App).

Démarrage local
1. Installer dépendances
   cd frontend
   npm install

2. Lancer en développement (proxy vers backend)
   npm start
   - Ouvrir http://localhost:3000
   - Par défaut le frontend appelle `http://localhost:5000/api`. Pour changer la cible, définir REACT_APP_API_URL dans un fichier `.env` (ex: REACT_APP_API_URL=http://localhost:5000/api).

Production (servir via Flask)
1. Générer le build
   npm run build
2. Lancer le backend (depuis NetworkAutomationApp) :
   python3 app.py
   - Flask servira `frontend/build` si présent.

Utilisation des boutons "Rapports"
- Les boutons appellent `/api/report/<inventory|performance|audit>` et déclenchent un téléchargement PDF.
- Si le backend retourne une erreur, vérifier les logs du backend et l'existence des fichiers `.txt` dans `../reports/`.

Notes
- Si `react-scripts` pose problème, supprimer `node_modules` et `package-lock.json` puis réinstaller:
  rm -rf node_modules package-lock.json
  npm install --legacy-peer-deps

- Pour le développement UI, gardez le backend en marche (python3 app.py) pour tester les interactions réelles.

Contribuer
- Garder les composants modulaires. Extraire appels HTTP dans `src/api.js`.
