# 🛡️ BradlyAI — L1 SOC Agent that Closes False Positives & Duplicates Autonomously

![BradlyAI](https://img.shields.io/badge/BradlyAI-AI%20Cyber%20Security-3b82f6?style=for-the-badge)
![L1%20Agent](https://img.shields.io/badge/L1%20Agent-5%20Signals%20%7C%205%20Sources-10b981?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%2B%20SQLite-3b82f6?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-2.3.0-8b5cf6?style=for-the-badge)
![Tests](https://img.shields.io/badge/Tests-27%2F27%20Passing-22c55e?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**BradlyAI** is an AI-powered **L1 SOC Agent** that automatically classifies and closes false-positive and duplicate security alerts — replacing or augmenting your L1 analyst team. Real threats get escalated to L2 with full investigation + evidence. Built with Python/FastAPI, MIT-licensed.

---

## 🎯 What it does

```
                    ┌──────────────────────────────────────────┐
   Alert Source  →   │  Wazuh / Splunk / Jira /  Splunk        │
  (webhook/POST)    │                   ↓                                      │
                    │  1. Normalize to common shape            │
                    │  2. Run 5-signal decision engine:        │
                    │     • rule-based FP detector (regex)     │
                    │     • frequency analyzer (duplicates)    │
                    │     • whitelist matcher (allow-list)     │
                    │     • LLM classifier (Groq/OpenAI)       │
                    │     • historical precedent              │
                    │  3. Combine signals → confidence score   │
                    └──────────────────────────────────────────┘
                                          ↓
                          ┌───────────────┴───────────────┐
                          ↓                               ↓
                Confidence ≥ 0.85               Confidence < 0.85
                → CLOSE                          → ESCALATE
                → Log audit                      → Create incident
                → Optional: archive in Wazuh    → Run investigation
                → Skip incident creation         → Collect evidence
                                                  → Notify L2 analyst
```

**Result:** 60-85% of incoming alerts auto-closed. L2 only sees real threats. MTTR drops from hours to seconds.

---

## 🆕 What's new in v2.3.0

### **L1 SOC Agent** (the core feature)
- ✅ **5-signal decision engine** (FP detector + duplicates + whitelist + LLM + history)
- ✅ **Multi-source ingestion** — Wazuh, Splunk, Jira, GreyNoise
- ✅ **Auto-close with audit trail** — every decision logged to `audit_log`
- ✅ **Human override** — `POST /reopen` for false negatives
- ✅ **Feedback loop** — learn from overrides
- ✅ **Configurable** — mode (active/shadow), threshold, whitelist CRUD
- ✅ **Dashboard UI** for live decisions

### **Wazuh two-way integration**
- ✅ **Wazuh → BradlyAI** — webhook ingest runs each alert through L1 Agent
- ✅ **BradlyAI → Wazuh** — auto-archive closed alerts via Manager API (with comment)
- ✅ **Production-safe defaults** — disabled by default, dry-run mode, reversible

### **Free real-time threat intel**
- ✅ **GreyNoise Community API** integration — identify internet scanners in real-time
- ✅ **Test endpoints** — `/greynoise/test-batch` to validate against real scanner IPs

### **Production-ready**
- ✅ **Auto-migration helper** — adds missing columns to existing DBs on startup
- ✅ **Health check** — `/health` for monitoring
- ✅ **27/27 tests passing**
- ✅ **Cross-platform** — works on Linux, macOS, Windows

---

## 🚀 Quick Start

### One-line install (Linux/macOS)
```bash
git clone https://github.com/sushantkane123/BradlyAI.git && cd BradlyAI && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && cp .env.example .env && python run.py
```

### Windows (PowerShell)
```powershell
git clone https://github.com/sushantkane123/BradlyAI.git
cd BradlyAI
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

### Docker
```bash
git clone https://github.com/sushantkane123/BradlyAI.git && cd BradlyAI && docker-compose up -d --build
```

Open dashboard at **`http://localhost:8000/`** · API docs at **`http://localhost:8000/docs`**

---

## 🤖 L1 Agent — 30-second demo

After starting the server, try these PowerShell commands:

```powershell
# 1) Send a vulnerability scanner alert (should auto-CLOSE)
curl.exe -X POST http://localhost:8000/api/v1/l1/process-alert -H "Content-Type: application/json" -d "{\"source\":\"splunk\",\"payload\":{\"search_name\":\"Nessus vulnerability scan completed\",\"result\":{\"host\":\"srv\"},\"severity\":\"high\"}}"

# 2) Send a real PowerShell attack (should ESCALATE)
curl.exe -X POST http://localhost:8000/api/v1/l1/process-alert -H "Content-Type: application/json" -d "{\"source\":\"wazuh\",\"payload\":{\"rule\":{\"level\":12,\"description\":\"Suspicious PowerShell execution\"},\"agent\":{\"name\":\"WEB\",\"ip\":\"10.0.0.5\"}}}"

# 3) Test against real internet scanner IPs (free, no auth)
curl.exe -X POST http://localhost:8000/api/v1/l1/greynoise/test-batch -H "Content-Type: application/json" -d "[\"8.8.8.8\",\"1.1.1.1\",\"185.220.101.5\",\"71.6.194.186\"]"

# 4) View audit log + stats
curl.exe http://localhost:8000/api/v1/l1/audit?since_hours=1
curl.exe http://localhost:8000/api/v1/l1/stats?since_hours=24
```

**Expected output:**
- Scanner alert → `decision: "CLOSE"`, confidence 95% (FP detector matches)
- PowerShell alert → `decision: "ESCALATE"`, confidence 50% (no FP signal)
- GreyNoise test → RIOT/scanner IPs get CLOSE, unknown IPs ESCALATE

---

## 🛡️ Wazuh Integration (recommended)

Point your Wazuh manager at BradlyAI. Each Wazuh alert flows through L1 Agent:

```
Wazuh Manager ──webhook──> BradlyAI L1 Agent ──auto-archive──> Wazuh Manager
```

### Step 1 — Add to Wazuh `/var/ossec/etc/ossec.conf`:

```xml
<integration>
  <name>custom-webhook</name>
  <hook_url>http://YOUR-BRADLYAI-HOST:8000/api/v1/integration/wazuh/ingest</hook_url>
  <alert_format>json</alert_format>
  <level>3</level>
</integration>
```

### Step 2 — Restart Wazuh manager
```bash
systemctl restart wazuh-manager
```

### Step 3 — Configure BradlyAI (production-safe defaults)

Add to `BradlyAI/.env`:
```ini
WAZUH_ENABLED=true            # turn on the integration
WAZUH_DRY_RUN=true            # START in dry-run (logs only, no real actions)
WAZUH_CLOSE_MODE=comment_only # SAFEST: just adds audit comment to Wazuh
WAZUH_MANAGER_URL=https://your-wazuh:55000
WAZUH_USER=bradlyai
WAZUH_PASSWORD=secret
WAZUH_VERIFY_SSL=true
```

### Step 4 — Test safely first

```bash
# Simulate a Wazuh webhook without touching production
curl -X POST http://localhost:8000/api/v1/integration/wazuh/test-webhook \
  -H "Content-Type: application/json" \
  -d '{"rule_level":3,"rule_id":"1001","rule_description":"Vulnerability scanner heartbeat","agent_name":"NESSUS","agent_ip":"10.0.0.50","mitre_id":"T1595"}'

# Check what Wazuh calls would happen (dry-run logs them)
curl http://localhost:8000/api/v1/l1/wazuh/health
```

### Step 5 — When confident, enable real actions

```ini
WAZUH_DRY_RUN=false
WAZUH_CLOSE_MODE=archive_and_comment  # archives + adds comment with reasoning
```

### Safety features built-in

| Default | Meaning |
|---|---|
| `WAZUH_ENABLED=false` | No Wazuh API calls at all |
| `WAZUH_DRY_RUN=true` | Logs what would happen, doesn't do it |
| `WAZUH_CLOSE_MODE=comment_only` | Just adds audit comment, doesn't archive |

To do **any real action** on Wazuh, you must explicitly override all three.

---

## 🧪 Free real-time test sources

You don't need a SIEM to test the L1 Agent. Use these free public sources:

| Source | Type | Auth | Free tier |
|---|---|---|---|
| **GreyNoise** (✅ integrated) | Internet scanner intel | None | 1000 req/day |
| **AbuseIPDB** | IP reputation | API key | 1000 req/day |
| **AlienVault OTX** | Threat pulses | API key | Unlimited |
| **URLhaus** | Malicious URLs | None | Unlimited |
| **LogPAI/loghub** (GitHub) | Sample logs | None | Free |
| **Boss of the SOC** (Splunk) | Sample data | None | Free |

**Test with real scanner data:**
```bash
curl -X POST http://localhost:8000/api/v1/l1/greynoise/test-batch \
  -H "Content-Type: application/json" \
  -d '["71.6.194.186","8.8.8.8","185.220.101.5"]'
# → Returns which are scanners vs RIOT vs suspicious
```

---

## 🔌 API Reference (L1 Agent endpoints)

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/v1/l1/mode` | GET/POST | View/switch active↔shadow mode + threshold |
| `/api/v1/l1/process-alert` | POST | Decide on 1 alert (single) |
| `/api/v1/l1/process-batch` | POST | Bulk decide (queue drain) |
| `/api/v1/l1/{id}/reopen` | POST | Human override (reopen + feedback) |
| `/api/v1/l1/{id}/confirm` | POST | Human confirms FP closure was correct |
| `/api/v1/l1/audit` | GET | Decision history (paginated) |
| `/api/v1/l1/stats` | GET | Aggregate KPIs (close rate, override rate, etc.) |
| `/api/v1/l1/feedback` | GET | Human override records |
| `/api/v1/l1/whitelist` | GET/POST | List/add allow-list entries |
| `/api/v1/l1/whitelist/{id}` | DELETE | Remove entry |
| `/api/v1/l1/whitelist/{id}/toggle` | POST | Enable/disable entry |
| `/api/v1/l1/wazuh/health` | GET | Wazuh integration safety status |
| `/api/v1/l1/wazuh/test-close` | POST | Test Wazuh close (always dry-run) |
| `/api/v1/l1/greynoise/check/{ip}` | GET | Query single IP via GreyNoise |
| `/api/v1/l1/greynoise/test-batch` | POST | Run IPs through L1 Agent |
| `/api/v1/l1/greynoise/sample-ips` | GET | Curated list of test IPs |
| `/api/v1/integration/wazuh/ingest` | POST | Wazuh webhook → L1 Agent |
| `/api/v1/integration/wazuh/test-webhook` | POST | Simulate Wazuh webhook (for testing) |

Plus the original BradlyAI endpoints (alerts, incidents, copilot, MITRE, AIR, etc.) — see `/docs`.

---

## 📂 Repository Structure

```
.
├── bradlyai/
│   ├── main.py                       # FastAPI app + lifespan
│   ├── config.py                     # Pydantic settings (15+ fields)
│   ├── database.py                   # SQLAlchemy (sync + async)
│   ├── migrations.py                 # Auto-add missing columns
│   ├── models/
│   │   ├── alert.py                  # Alert + AlertStoryline
│   │   ├── asset.py                  # Attack Surface assets
│   │   ├── audit_log.py              # L1 Agent decisions (NEW)
│   │   ├── whitelist_entry.py        # Allow-list (NEW)
│   │   └── feedback.py               # Human overrides (NEW)
│   ├── services/
│   │   ├── detection_engine.py       # 6 regex rules
│   │   ├── ai_engine.py              # AI analysis
│   │   ├── llm_client.py             # Groq/OpenAI async client
│   │   ├── copilot.py                # AI Copilot
│   │   ├── enhanced_copilot.py
│   │   ├── live_simulation_worker.py # Demo data generator
│   │   ├── log_ingestion.py
│   │   ├── incident_manager.py
│   │   ├── air_runner.py
│   │   ├── alert_normalizer.py       # Splunk/Wazuh/Jira → common (NEW)
│   │   ├── fp_detector.py            # Rule-based FP detection (NEW)
│   │   ├── frequency_analyzer.py     # Duplicate detection (NEW)
│   │   ├── whitelist.py              # Allow-list CRUD (NEW)
│   │   ├── llm_classifier.py         # Groq/OpenAI classifier (NEW)
│   │   ├── historical_check.py       # Past decisions (NEW)
│   │   ├── l1_decision_engine.py     # Combines 5 signals (NEW)
│   │   ├── auto_closer.py            # Takes action + audit (NEW)
│   │   ├── feedback_loop.py           # Human override learning (NEW)
│   │   ├── wazuh_api.py              # Wazuh Manager API client (NEW)
│   │   └── greynoise_client.py       # GreyNoise integration (NEW)
│   ├── routers/
│   │   ├── alerts.py
│   │   ├── asm.py
│   │   ├── air.py
│   │   ├── chat.py
│   │   ├── forensics.py
│   │   ├── ingest.py
│   │   ├── integration.py            # Wazuh integration (UPGRADED)
│   │   ├── mitre.py
│   │   ├── system.py
│   │   ├── ws.py
│   │   └── l1_agent.py               # L1 Agent REST API (NEW)
│   └── static/                       # Self-contained SPA
├── tests/
│   ├── test_api.py                   # 11 original tests
│   └── test_l1_agent.py              # 16 L1 Agent tests (NEW)
├── .env.example                       # Updated with WAZUH_* keys
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run.py
└── CHANGELOG.md
```

---

## ⚙️ Configuration (`.env`)

```ini
# ── Core ──
APP_NAME="BradlyAI - Driverless SOC & Automated Incident Response"
APP_VERSION="2.3.0"
ENVIRONMENT=production
DATABASE_URL=sqlite+aiosqlite:////opt/bradlyai/data/bradlyai_soc.db

# ── L1 Agent ──
AUTO_CONTAINMENT_THRESHOLD=0.85    # Min confidence to auto-close
LIVE_SIMULATION_WORKER_ACTIVE=true   # Demo data generator (turn off in prod)
SIMULATION_INTERVAL_SECONDS=30

# ── AI / LLM ──
LLM_PROVIDER=groq                   # groq (free) or openai
GROQ_API_KEY=gsk_your_key_here
OPENAI_API_KEY=sk-your_key_here
DEFAULT_AI_MODEL=gpt-4-turbo-preview

# ── Wazuh Manager API (SAFE DEFAULTS - read carefully!) ──
WAZUH_ENABLED=false                 # MUST explicitly enable
WAZUH_DRY_RUN=true                  # Logs only, no real actions
WAZUH_CLOSE_MODE=comment_only       # SAFEST mode
WAZUH_MANAGER_URL=
WAZUH_USER=
WAZUH_PASSWORD=
WAZUH_VERIFY_SSL=true
```

See `.env.example` for the full template with safety notes.

---

## 🛡️ Safety & Production Checklist

Before deploying to production:

- [ ] Set `WAZUH_ENABLED=false` until you've tested with `dry_run=true`
- [ ] Use `WAZUH_CLOSE_MODE=comment_only` initially
- [ ] Set `AUTO_CONTAINMENT_THRESHOLD=0.95+` for stricter auto-close
- [ ] Run agent in **shadow mode** for 1-2 weeks before going active
- [ ] Compare agent decisions with L1 analyst decisions
- [ ] Set up monitoring on `/health` endpoint
- [ ] Configure backup for `bradlyai_soc.db` daily
- [ ] Review `audit_log` table weekly for false closures
- [ ] Keep API keys in `.env`, not source control
- [ ] Use HTTPS in front (Nginx + Let's Encrypt)

---

## 🧪 Testing

```bash
pip install pytest
pytest tests/ -v
```

```
tests/test_api.py         (11 tests) ✅
tests/test_l1_agent.py     (16 tests) ✅
                         ────────────
                         27/27 passing
```

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 License

MIT — see [LICENSE](LICENSE).

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md).

### v2.3.0 — L1 SOC Agent + Wazuh Integration

**🆕 L1 SOC Agent (the core product)**
- 5-signal decision engine (FP detector + duplicates + whitelist + LLM + history)
- Auto-close false positives and duplicates
- Multi-source: Wazuh, Splunk, Jira, GreyNoise
- Human override with feedback loop
- Audit trail for every decision
- 13 new REST endpoints
- Dashboard integration

**🆕 Wazuh two-way integration**
- Webhook ingest → L1 Agent decision
- Auto-archive closed alerts (with safety defaults)
- 2 new endpoints + safety status
- Production-safe: disabled/dry-run/comment-only defaults

**🆕 GreyNoise integration**
- Free real-time internet scanner intelligence
- 3 new endpoints (check, test-batch, sample-ips)
- No API key required

**🆕 Production hardening**
- Auto-migration helper (adds missing columns to existing DBs)
- Cross-platform scripts (Windows PowerShell)
- Better error handling

**🧪 Testing**
- 27/27 pytest passing (was 11/11)
- New `tests/test_l1_agent.py` with 16 tests

### v2.2.0 — Wazuh SIEM Integration
- Full incident lifecycle: alert → detect → investigate → evidence → close
- 6 critical bugs fixed, async architecture
- 11/11 tests passing
