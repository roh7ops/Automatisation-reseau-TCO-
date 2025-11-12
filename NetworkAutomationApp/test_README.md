# Tests for Report Generation and Download (test_README.md)

This file contains tests and manual verification steps for the new PDF report endpoints and frontend buttons.

Prerequisites:
- Backend running: python3 app.py (ensure reportlab is installed: pip install reportlab pyyaml flask flask-cors)
- Frontend running in development: cd frontend && npm start (or use built build)

Automated curl checks (run in terminal):

1) Inventory report
curl -v -o /tmp/inventory_report.pdf http://localhost:5000/api/report/inventory
# Verify HTTP 200 and Content-Type: application/pdf
# Check file non-empty:
test -s /tmp/inventory_report.pdf && echo "OK inventory report file saved" || echo "FAILED inventory report"

2) Performance report
curl -v -o /tmp/perf_report.pdf http://localhost:5000/api/report/performance
test -s /tmp/perf_report.pdf && echo "OK performance report" || echo "FAILED performance report"

3) Audit report
curl -v -o /tmp/audit_report.pdf http://localhost:5000/api/report/audit
test -s /tmp/audit_report.pdf && echo "OK audit report" || echo "FAILED audit report"

4) Health check
curl -sS http://localhost:5000/api/health

Manual browser tests (frontend):
- Open frontend (http://localhost:3000 or served build).
- Click "Rapport d'Inventaire" button.
- A download should start (inventory_report_YYYYMMDD_HHMMSS.pdf).
- Open the PDF to inspect contents.
- Repeat for "Rapport de Performance" and "Rapport d'Audit".

Automated pytest example (optional):
- Create tests/test_reports.py with requests to /api/report/* and assert response headers:
  import requests
  def test_inventory():
      r = requests.get("http://localhost:5000/api/report/inventory")
      assert r.status_code == 200
      assert r.headers["Content-Type"] == "application/pdf"
      assert len(r.content) > 100

Notes:
- If reports are empty, ensure config/devices.yaml exists under config/ or root and contains devices list.
- Install python deps: pip install -r requirements.txt && pip install reportlab PyYAML
