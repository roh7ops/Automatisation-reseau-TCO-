/* javascript */
import React, { useState } from "react";
import "./App.css";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000/api";

const NetworkAutomationApp = () => {
  const [isLoading, setIsLoading] = useState(false);

  const downloadBlob = (blob, filename) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename || "report.pdf";
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  };

  const downloadReport = async (type) => {
    try {
      setIsLoading(true);
      const resp = await fetch(`${API_URL}/report/${type}`, {
        method: "GET",
        headers: { Accept: "application/pdf" },
      });
      if (!resp.ok) {
        console.error("Report request failed", resp.status);
        alert("Erreur lors de la génération du rapport.");
        return;
      }
      const blob = await resp.blob();
      // try to extract filename from Content-Disposition
      const cd = resp.headers.get("Content-Disposition");
      let filename = null;
      if (cd) {
        const match = /filename\*=UTF-8''(.+)$/.exec(cd) || /filename="?([^"]+)"?/.exec(cd);
        if (match) filename = decodeURIComponent(match[1]);
      }
      if (!filename) {
        filename = `${type}_report.pdf`;
      }
      downloadBlob(blob, filename);
    } catch (e) {
      console.error(e);
      alert("Erreur réseau lors du téléchargement.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Automatisation Réseau - Rapports</h1>
        <p>Utilisez les boutons ci-dessous pour générer et télécharger des rapports PDF.</p>
        <div style={{ display: "flex", gap: 12, marginTop: 12 }}>
          <button onClick={() => downloadReport("generate")} disabled={isLoading}>
            Générer un Rapport
          </button>
          <button onClick={() => downloadReport("inventory")} disabled={isLoading}>
            Rapport d'Inventaire
          </button>
          <button onClick={() => downloadReport("performance")} disabled={isLoading}>
            Rapport de Performance
          </button>
          <button onClick={() => downloadReport("audit")} disabled={isLoading}>
            Rapport d'Audit
          </button>
        </div>
        {isLoading && <p>Génération en cours...</p>}
      </header>
    </div>
  );
};

export default NetworkAutomationApp;
