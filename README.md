# README — Temporal (Python) Tutorial: Install & Run (macOS • Linux • Windows)

Deze gids zet je lokaal in < 10 minuten op:

- **Temporal dev‑server** + **Web UI**
- **Python 3** + **virtualenv**
- Dependencies uit `requirements.txt`
- Starten van **worker** en **client** demo

> ℹ️ De Temporal dev‑server is bedoeld voor **ontwikkeling**, niet voor productie. [1](https://docs.temporal.io/develop/python/failure-detection)

---

## Inhoud

1. [Wat je installeert](#wat-je-installeert)  
2. [Snelstart (kruis‑platform)](#snelstart-kruis-platform)  
3. [OS‑specifieke installatiehandleidingen](#- #fedorarhel  
   - #windowspowershell  
4. #project-run-volgorde  
5. #troubleshooting  
6. #optioneel-temporal-via-docker  
7. #appendix-nuttige-referenties

---

## Wat je installeert

- **Temporal CLI** (bevat een ingebouwde development server en start de **Web UI** automatisch). Starten met:  
  `temporal server start-dev` → Web UI op **http://localhost:8233** (standaard). [2](https://deepwiki.com/temporalio/sdk-python/4.3-heartbeating-and-cancellation)
- **Python 3** (Temporal Python SDK ondersteunt moderne Python‑versies; 3.10+ aanbevolen). [3](https://python.temporal.io/temporalio.exceptions.html)

---

## Snelstart (kruis‑platform)

> Gebruik deze TL;DR als je al Python 3 en de Temporal CLI hebt.

1) **Start de Temporal dev‑server** (laat dit venster open):
```bash
temporal server start-dev
# Web UI: http://localhost:8233



### MacOS/Linux
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

### Windows Powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

### Run
# Terminal A (dev‑server draait al):
python worker.py

# Terminal B:
python start.py