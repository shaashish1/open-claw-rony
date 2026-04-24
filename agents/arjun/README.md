# ARJUN — LinkedIn Job Search Agent

**A**utomated **R**ole **J**ob h**U**nter a**N**d scorer for Ashish Sharma (ITGYANI)

---

## What It Does

ARJUN searches LinkedIn's **public job listings** (no login required) for senior AI & Digital Transformation roles across Singapore, UAE, UK, and Thailand — then:

1. **Scrapes** job cards using Playwright stealth browser (anti-bot safe)
2. **Scores** each job 0–100 against Ashish's profile using Azure Foundry Claude Sonnet
3. **Saves** all results to a local SQLite database (`jobs.db`)
4. **Alerts** via Telegram for jobs scoring ≥ 70/100

> ⚠️ ARJUN **never auto-applies**. It only finds, scores, and alerts.

---

## Files

| File | Purpose |
|------|---------|
| `arjun.py` | Main agent — scrape → score → save → alert |
| `profile.json` | Ashish's structured profile for AI matching |
| `jobs.db` | SQLite database (created on first run) |
| `arjun.log` | Run logs |
| `requirements.txt` | Python dependencies |
| `install.sh` | One-time setup script |
| `run.sh` | Run script |

---

## Setup (One Time)

```bash
cd /root/.openclaw/workspace/agents/arjun
chmod +x install.sh run.sh
./install.sh
```

---

## Running ARJUN

### Manual run
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
./run.sh
```

### Or directly
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
python3 arjun.py
```

---

## Scheduling with Cron

Run twice daily (9 AM and 6 PM IST = 3:30 AM and 12:30 PM UTC):

```bash
# Edit crontab
crontab -e

# Add these lines:
30 3 * * * TELEGRAM_BOT_TOKEN=your_token AZURE_API_KEY=your_key /root/.openclaw/workspace/agents/arjun/run.sh >> /root/.openclaw/workspace/agents/arjun/cron.log 2>&1
30 12 * * * TELEGRAM_BOT_TOKEN=your_token AZURE_API_KEY=your_key /root/.openclaw/workspace/agents/arjun/run.sh >> /root/.openclaw/workspace/agents/arjun/cron.log 2>&1
```

---

## What ARJUN Searches

**Roles (keywords):**
- AI Transformation, Head of AI, Director AI, VP AI
- Chief AI Officer, Digital Transformation Director
- AI Strategy, Intelligent Automation, Enterprise AI

**Locations:**
- Singapore, Dubai, UAE, United Kingdom, London, Thailand, Bangkok

Each run performs up to **15 searches** (role × location combinations, randomized).

---

## Telegram Alert Format

```
💼 New Job Match (Score: 82/100)
*Head of AI* at TechCorp Singapore
📍 Singapore
🔗 https://linkedin.com/jobs/view/123456789

✅ Why:
  • Strong role-title alignment
  • Target location match
  • Senior level with sponsorship history

⚠️ Missing:
  • Specific industry domain mention
```

---

## Database Schema

```sql
CREATE TABLE jobs (
    job_id      TEXT PRIMARY KEY,
    title       TEXT,
    company     TEXT,
    location    TEXT,
    url         TEXT,
    score       INTEGER,
    verdict     TEXT,       -- apply / review / skip
    reasons     TEXT,       -- JSON array
    missing     TEXT,       -- JSON array
    scraped_at  TEXT,
    notified    INTEGER     -- 0 or 1
);
```

### Query high-scoring jobs
```bash
sqlite3 jobs.db "SELECT title, company, location, score, verdict FROM jobs WHERE score >= 70 ORDER BY score DESC;"
```

### Query all new jobs today
```bash
sqlite3 jobs.db "SELECT title, company, score, verdict FROM jobs WHERE scraped_at >= date('now') ORDER BY score DESC;"
```

---

## Scoring Guide

| Score | Verdict | Meaning |
|-------|---------|---------|
| 75–100 | `apply` | Strong match — act on this |
| 50–74 | `review` | Worth reviewing — check details |
| 0–49 | `skip` | Poor fit — skip |

Telegram alerts fire for **score ≥ 70** (review + apply).

---

## Rate Limiting & Anti-Bot

- Random 3–6s delay between page loads
- Random user agent rotation (5 realistic UAs)
- Webdriver fingerprint masked
- Max 15 searches per run
- Graceful stop if captcha/auth wall detected

---

## Troubleshooting

**No jobs found:**
- LinkedIn may have changed their HTML — check `arjun.log`
- Try running manually and check for auth wall messages

**Playwright not found:**
- Run `./install.sh` to install dependencies

**Telegram alerts not sending:**
- Ensure `TELEGRAM_BOT_TOKEN` env var is set
- Verify bot is started (send `/start` to the bot in Telegram)

**Scoring fails:**
- Check Azure AI endpoint connectivity
- Review `arjun.log` for HTTP error codes

---

*Built by RONY (OpenClaw AI) for Ashish Sharma | ITGYANI Intelligent Automation Solutions*
