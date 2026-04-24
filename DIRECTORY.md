# ITGYANI — Project Directory Structure

## VPS: 194.233.64.74 (panel.kharadionline.com)

```
/opt/itgyani-dashboard/          # MAYA — Email Dashboard (port 8002)
├── main.py                      # FastAPI app
├── imap_sync.py                 # IMAP IDLE + sync
├── database.py                  # SQLite layer
├── config.py                    # Account configs
├── telegram_alerts.py           # Alert system
├── frontend/index.html          # Dashboard UI
├── data/dashboard.db            # Email + marketing DB
└── venv/                        # Python 3.8 env

/home/n8n.itgyani.com/public_html/n8n/   # NIKKI — n8n automation
├── docker-compose.yml           # n8n + postgres + ffmpeg-api
└── [n8n data volume]            # Workflows, credentials

/home/theemployeefactory.com/public_html/  # TEF main site (PHP)
└── openmaic/                    # 🔜 OpenMAIC AI classroom (port 8003)

/home/kharadionline.com/public_html/  # KIRAN — Shopify/eComm site (WP)

/home/cryptogyani.com/public_html/    # CryptoGyani site (WP)

/home/algoproject/yukti.ai/          # Yukti quant platform (being backed up)
├── venv/                        # Celery workers (concurrency=1 now)
└── docker-compose.yml           # OpenAlgo containers

/tmp/rony-deploy/                # GitHub auto-deploy staging
```

## GitHub Repos

```
shaashish1/open-claw-rony        # Main workspace (this repo)
├── dashboard/                   # MAYA email dashboard
│   ├── backend/                 # FastAPI + IMAP
│   └── frontend/                # Dashboard UI
├── agents/                      # All agent code
│   ├── ai_client.py             # Azure Foundry wrapper
│   ├── job-assistant/           # ARJUN spec + tracker
│   └── ROSTER.md                # Team roster
├── n8n-workflows/               # Workflow JSONs
├── scripts/                     # Utility scripts (transcribe, etc.)
├── skills/                      # Installed OpenClaw skills
├── config/.env                  # Secrets (gitignored)
├── memory/                      # Daily logs
├── COMPANY_OS.md                # V3 dual engine OS
├── TEAM.md                      # This team structure
└── DIRECTORY.md                 # This file

shaashish1/The-Employee-Factory---OpenMAIC  # TEF AI classroom platform
```

## Domains & Services

| Domain | Service | Port | Status |
|---|---|---|---|
| dashboard.itgyani.com | MAYA Email Dashboard | 8002 | ✅ Live |
| n8n.itgyani.com | n8n Automation | 5678 | ✅ Live |
| theemployeefactory.com | TEF main site | 80/443 | ✅ Live |
| learn.theemployeefactory.com | OpenMAIC AI Classroom | 8003 | 🔜 Deploying |
| kharadionline.com | eCommerce (WP) | 80/443 | ✅ Live |
| cryptogyani.com | Crypto blog (WP) | 80/443 | ✅ Live |
| itgyani.com | Main site | 80/443 | ⚠️ Thin |

## Jira Board Structure (Proposed)

```
Projects:
├── RONY   — COO Operations (VPS, infra, deployments)
├── MAYA   — Email & Marketing
├── ARJUN  — Job Search + Security
├── ENGINE1 — Cash Flow (leads, sales, n8n services)
├── ENGINE2 — Utility Apps (SEO tools, passive income)
├── TEF    — The Employee Factory platform
└── STORE  — kharadionline.com eCommerce

Sprint Cadence: Weekly (Mon–Sun)
Daily standup: Rony brief → Telegram 7 AM IST
```

## Azure Foundry Models in Use

| Model | Used by | Purpose |
|---|---|---|
| claude-sonnet-4-6 | All agents | Daily tasks, drafts, analysis |
| claude-opus-4-6 | VIKRAM, DISHA | Strategy, heavy reasoning |
| gpt-4o | NIKKI, TEF-AI | Multi-modal, fallback |
| gpt-4o-transcribe | MAYA | Voice note transcription |
| gpt-4o-mini-tts | Reports | Text to speech |
