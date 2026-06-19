# 🛡️ BradlyAI — Advanced Python Driverless SOC & Incident Response Platform

![BradlyAI](https://img.shields.io/badge/BradlyAI%20Technology-AI%20Cyber%20Security-00f0ff?style=for-the-badge)
![Driverless](https://img.shields.io/badge/Driverless%20SOC-100%25%20Autonomous-10b981?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%2B%20SQLite-3b82f6?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-2.2.0--PRO-8b5cf6?style=for-the-badge)
![Tests](https://img.shields.io/badge/Tests-11%2F11%20Passing-22c55e?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

Welcome to the definitive full-stack **Python (FastAPI)** repository and interactive enterprise dashboard for **BradlyAI**, an AI-driven cybersecurity platform. This project gives developers complete control over their Security Operations Center (SOC) with real OpenAI / Groq generative streaming, WebSockets, Web Audio feedback, SQLite SIEM persistence, and **Wazuh SIEM integration** with full incident lifecycle management.

---

## 🌟 Architecture Highlights

1. **100% Extensible Python & Web:** Every line of anomaly parsing, SQLite persistence, and UI logic is visible and documented.
2. **True Generative AI:** Connect **OpenAI** or **Groq** API keys via `.env` or the in-app SOC Settings modal. Async HTTP (`httpx`) for zero-blocking LLM calls.
3. **Continuous Background Telemetry:** Async worker generates realistic packet logs, persists to SQLite, and broadcasts via WebSockets.
4. **Standalone Web Audio:** Custom `CyberAudio` class — laser, shield, alarm, radar sounds with **zero external files**.
5. **Async-First Architecture:** `aiosqlite` + `AsyncSession` for non-blocking DB, async LLM client, structured logging.
6. **Wazuh SIEM Integration:** Full incident lifecycle — Alert → Detect → Investigate → Evidence → Closure.
7. **Health Check:** `GET /health` returns DB connectivity, worker status, uptime — ready for monitoring.

---

## 🚀 Dashboard Features

### 📊 Executive Dashboard & Live Cyber Radar
- Enterprise Status Cards: Digital Resilience Index, Autonomous Containment Rate (99.4%), MTTR, monitored endpoints.
- Floating Diagnostic Node Hubs on the Live Multi-Model Threat Map with ping latencies, EDR agents, CPU loads.
- Activity Trends Canvas with real-time driverless interception charts.

### ⚡ Automated Incident Response (AIR) Live Pipeline
- Select adversary scenarios (**APT29 Lateral Movement** vs **Zero-Day Supply Chain**) and watch sub-second containment with typewriter-style streaming logs.

### 🌐 Attack Surface Management (ASM)
- Zero-Day Risk Inventory: web services, S3 buckets, Kubernetes clusters. One-click **Auto-Remediate** applies virtual firewall patches.

### 🔍 AI Threat Hunter & Memory Forensics
- Live Memory Branches: parent-child process trees with reflective DLL injection markers.
- Tactile Actions: **⚡ Kill PID**, **🛡️ Isolate Memory**, **💾 Download Memory Dump**.

### ⚙️ System Configuration
- SOC Settings modal: paste API keys, adjust auto-containment thresholds, toggle telemetry workers, purge database.

### 💬 AI Security Copilot
- Pre-baked quick prompts + custom queries via **FastAPI chunk-by-chunk streaming (`StreamingResponse`)**. Supports Groq (Llama-3) and OpenAI (GPT-4).

### 🆕 Wazuh SIEM Integration (API)
- `/api/v1/integration/wazuh/ingest` — Receive Wazuh webhook alerts
- `/api/v1/integration/wazuh/full-pipeline` — One-call: alert → detect → investigate → evidence → close
- `/api/v1/integration/incidents` — Full incident lifecycle management with 7-step investigation, IoC extraction, YARA rules, and closure reports

---

## 📂 Repository Structure

```text
.
├── .env.example           # Environment config template
├── .gitignore
├── docker-compose.yml     # One-click Docker deployment
├── Dockerfile             # Python 3.11 Slim container
├── README.md
├── CHANGELOG.md           # Full version history
├── CONTRIBUTING.md        # Developer onboarding guide
├── LICENSE                # MIT License
├── requirements.txt       # Python dependencies
├── pytest.ini
├── run.py                 # Local dev runner
├── bradlyai_cli.py        # Terminal CLI tool
├── .github/workflows/
│   └── ci.yml             # GitHub Actions CI
├── sample_logs/           # Sample logs for ingestion testing
├── tests/
│   └── test_api.py        # 11 integration tests — all passing ✅
└── bradlyai/              # Main Python package
    ├── main.py            # FastAPI entrypoint, lifespan, middleware, health check
    ├── config.py          # Pydantic Settings (14 config fields)
    ├── database.py        # SQLAlchemy sync + async engine
    ├── models/            # ORM models (Alert, Asset, Storyline)
    ├── schemas/           # Pydantic validation schemas
    ├── services/          # AI engine, copilot, detection, log ingestion, incident manager, AIR
    ├── routers/           # API routes (/api/v1/alerts, /chat, /ingest, /integration, /ws, etc.)
    └── static/            # Self-contained SPA (index.html, style.css, app.js)
```

---

## 🛠️ Quick Start

### Option A: Docker

```bash
git clone https://github.com/sushantkane123/BradlyAI.git
cd BradlyAI
docker-compose up -d --build
```

### Option B: Native Python

```bash
git clone https://github.com/sushantkane123/BradlyAI.git
cd BradlyAI
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
pip install -r requirements.txt
cp .env.example .env           # Edit .env with your API keys (optional)
python run.py
```

Access the dashboard at **`http://localhost:8000/`** and Swagger docs at **`http://localhost:8000/docs`**.

### CLI Usage

```bash
python bradlyai_cli.py --status
python bradlyai_cli.py --alerts CRITICAL
python bradlyai_cli.py --trigger-attack 0
```

---

## 🔌 API Overview

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check — DB, worker, uptime |
| `/api/v1/alerts` | GET | List/search/paginate security alerts |
| `/api/v1/alerts/{id}` | GET | Single alert with full storyline |
| `/api/v1/alerts/trigger-simulated-attack` | POST | Trigger a simulated cyber attack |
| `/api/v1/asm/assets` | GET | Attack Surface Management inventory |
| `/api/v1/asm/remediate/{id}` | POST | Auto-remediate an asset |
| `/api/v1/asm/rescan` | POST | Global asset deep scan |
| `/api/v1/air/run-pipeline/{idx}` | POST | Execute AIR pipeline scenario |
| `/api/v1/forensics/process-tree/{host}` | GET | Memory process tree for a host |
| `/api/v1/forensics/deep-scan/{host}` | POST | AI memory deep scan |
| `/api/v1/mitre/matrix` | GET | MITRE ATT&CK coverage matrix |
| `/api/v1/mitre/technique/{id}` | GET | Defensive guide for a technique |
| `/api/v1/chat` | POST | AI Copilot (streaming or JSON) |
| `/api/v1/chat/health` | GET | Copilot health + provider status |
| `/api/v1/ingest/logs/text` | POST | Ingest raw security logs |
| `/api/v1/ingest/logs/json` | POST | Ingest JSON logs |
| `/api/v1/ingest/logs/upload` | POST | Upload log file |
| `/api/v1/ingest/events` | GET | View ingested events |
| `/api/v1/ingest/alerts` | GET | View real detection alerts |
| `/api/v1/integration/wazuh/ingest` | POST | Wazuh SIEM webhook |
| `/api/v1/integration/wazuh/full-pipeline` | POST | 🚀 Full pipeline: alert → closure |
| `/api/v1/integration/incidents` | GET | List all incidents |
| `/api/v1/integration/incidents/{id}` | GET | Full incident detail |
| `/api/v1/integration/incidents/{id}/investigate` | POST | Run 7-step investigation |
| `/api/v1/integration/incidents/{id}/close` | POST | Close ticket + generate report |
| `/api/v1/integration/wazuh/health` | GET | Integration health + stats |
| `/api/v1/ws/stream` | WS | Real-time WebSocket telemetry |
| `/api/v1/system/config` | GET/POST | View/update system configuration |
| `/api/v1/system/reset-database` | POST | Purge and reseed database |

---

## 🧪 Running Tests

```bash
pip install pytest
pytest tests/ -v
```

```
tests/test_api.py::test_read_main           ✅
tests/test_api.py::test_health_check        ✅
tests/test_api.py::test_get_alerts          ✅
tests/test_api.py::test_get_assets          ✅
tests/test_api.py::test_trigger_attack      ✅
tests/test_api.py::test_ingest_real_logs    ✅
tests/test_api.py::test_chat_copilot        ✅
tests/test_api.py::test_get_mitre_matrix    ✅
tests/test_api.py::test_get_forensic_tree   ✅
tests/test_api.py::test_system_config       ✅
tests/test_api.py::test_system_reset        ✅
```

---

## 🛡️ Wazuh SIEM Integration

BradlyAI connects to your customer's Wazuh SIEM for fully autonomous incident response.

### Wazuh Configuration

Add to `ossec.conf`:

```xml
<integration>
  <name>custom-webhook</name>
  <hook_url>http://BRADLYAI_HOST:8000/api/v1/integration/wazuh/ingest</hook_url>
  <level>3</level>
</integration>
```

### Pipeline Flow

```
Wazuh Alert → BradlyAI Detection (6 rules) → Auto-create Incident
    → 7-Step Investigation → Evidence Collection → Auto-Containment
    → Closure Report → Ticket Closed
```

### Quick Demo (PowerShell)

```powershell
$body = '{"rule_level":12,"rule_description":"Suspicious PowerShell Execution","agent_name":"WEB-SRV01","agent_ip":"192.168.1.100","mitre_id":"T1059.001","auto_close":true}'
Invoke-RestMethod -Uri http://localhost:8000/api/v1/integration/wazuh/full-pipeline -Method POST -Body $body -ContentType "application/json"
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env`:

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `groq` | AI provider: `groq` or `openai` |
| `GROQ_API_KEY` | — | Groq API key (free at [console.groq.com](https://console.groq.com)) |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `AUTO_CONTAINMENT_THRESHOLD` | `0.85` | AI confidence threshold for auto-containment |
| `LIVE_SIMULATION_WORKER_ACTIVE` | `true` | Enable background telemetry simulation |
| `SIMULATION_INTERVAL_SECONDS` | `30` | Seconds between simulated alerts |
| `ENVIRONMENT` | `development` | Deployment environment |

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, style guide, and PR process.

## 📄 License

MIT — see [LICENSE](LICENSE).

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for full version history.

### v2.2.0 Highlights

- 🛡️ Wazuh SIEM integration with full incident lifecycle API
- 🚀 One-call pipeline: alert → detect → investigate → evidence → close
- 🔧 6 critical bugs fixed, async architecture, structured logging
- 🩺 Health check endpoint
- 🧪 11/11 tests passing
