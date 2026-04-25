# BLUEPRINT.md — Agent OS Architecture

Adopted from: https://masterclass-prompts.netlify.app
Version: 2026-04-26

---

## 1. Model Routing (Cost Optimization)

Default: **Haiku** for everything routine
Escalate to **Sonnet** only when:
- Architecture decisions
- Production code review / complex debugging
- Security analysis (ARJUN always Sonnet)
- Strategic decisions affecting >1 revenue stream
- Anything Ashish will review

| Task Type | Model | Cost/1K tokens |
|-----------|-------|----------------|
| Email classification, lead scoring | Haiku | $0.00025 |
| Status checks, heartbeats | Haiku | $0.00025 |
| Code review, security | Sonnet | $0.003 |
| Architecture, strategy | Sonnet | $0.003 |
| Initial planning (rare) | Opus | $0.015 |
| Drafts, first pass | Kimi K2.5 (free) | Free |
| Heartbeats | Ollama llama3.2 (local) | Free |

**Azure AI models available:**
- `claude-sonnet-4-6` — primary reasoning
- `claude-opus-4-6` — architecture only
- `gpt-4o` — multimodal tasks
- `gpt-4o-mini-tts` — voice agent TTS
- `gpt-4o-transcribe` — voice agent STT
- `gpt-5.3-codex` — code generation

---

## 2. Memory Architecture

### Hierarchy (read order, smallest first)
```
Session start: SOUL.md + USER.md + IDENTITY.md + memory/TODAY.md
              (≈8KB — lean startup)
On demand:    memory_search() → specific snippet
              MEMORY.md (main session only, big context)
Never auto:   Session history, all prior messages
```

### Memory Types
| File | Purpose | When to Read | When to Write |
|------|---------|--------------|---------------|
| `SOUL.md` | Identity | Every session start | Never (edit only if role changes) |
| `USER.md` | About Ashish | Every session start | When Ashish prefs change |
| `MEMORY.md` | Long-term memory | Main session only | Weekly distillation |
| `memory/YYYY-MM-DD.md` | Daily log | Session start (today + yesterday) | End of session |
| `HEARTBEAT.md` | Active reminders | Heartbeat poll | When tasks added |
| `agents/*.agent.md` | Agent identity | Agent startup | When role/tasks change |

### Business Brain (Long-term memory priorities)
Things ALWAYS in MEMORY.md:
- Key decisions made (with date + rationale)
- Revenue milestones reached
- Credentials rotated (type only, not value)
- Architecture decisions
- Lessons learned (especially failures)
- Agent status changes

---

## 3. Security Module (ARJUN)

### RULE 0: Non-Negotiable
```
NO skill/script/automation runs without ARJUN credential review.
Violation = immediate halt of all agent workflows.
```

### Credential Storage
- All credentials: `.envelope` file only
- `.gitignore` must always include: `.envelope*`, `.env*`, `*.secret`
- No hardcoded fallbacks in code (use `os.environ.get("KEY", "")`)
- Git history: nuke and repush if any secret leaks

### Daily Security Checks (ARJUN)
```bash
# Secret scan
git log --all -p | grep -iE "password|token|secret|api_key|bearer"

# Container check
docker ps --format "{{.Names}}|{{.Status}}"

# Unusual processes
ps aux | grep -v "www-data\|root\|uvicorn\|python\|node" | tail -20

# Failed SSH attempts
grep "Failed password" /var/log/auth.log | tail -20
```

---

## 4. The 8-Phase Build Loop

For every significant build task, follow these phases:

```
1. CONTEXT   → Read room: memory, queue, blockers
2. PLAN      → Break into subtasks, define validation gates
3. TASK BOARD → Create Jira story, assign, move to Doing
4. BUILD     → Execute. Log every milestone. Heartbeat every 5 min.
5. VALIDATE  → Run all gates. Pass = Phase 7. Fail = Phase 6.
6. HEAL      → Self-fix max 5 attempts. Still broken? Escalate.
7. REPORT    → HTML report + summary insight
8. CLOSE     → Move to Done. Send Telegram alert. Log to memory.
```

### Heartbeat During Build
Every 5 minutes during active build:
```
Log: "Progress: X% — currently doing [action]. ETA: Xm. Blockers: none."
```
Dashboard flags runs with no heartbeat >10 min as STALE.

---

## 5. Voice Agent (Planned — gpt-4o-mini-tts)

### Architecture
```
User speaks → gpt-4o-transcribe (STT) → Claude Haiku (intent)
    → If simple: Haiku handles it
    → If complex: Haiku routes to Sonnet
    → Response → gpt-4o-mini-tts (TTS) → User hears answer
```

### Use Cases
- Morning briefing: "What's happening today?"
- Quick status: "How many strategies are running?"
- Task dispatch: "Assign ZARA to send 20 emails to fintech founders"
- Alert replay: "Read me the last 3 job alerts"

### Voice Models Available (Azure)
- STT: `gpt-4o-transcribe` (Azure deployment)
- TTS: `gpt-4o-mini-tts` (Azure deployment)

---

## 6. YouTube Agent (Planned — n8n + ffmpeg)

### Current n8n Workflows
| Workflow | Status | Issue |
|----------|--------|-------|
| Tamil→Hindi Shorts | Active | OAuth2 broken (@SPHNithyananda) |
| UGC Status Checker | Active | |
| Social Poster | Active | |
| UGC Ad Creator | Active | |

### YouTube Agent Architecture
```
Source video/blog post
    → Script generation (Haiku — draft, Sonnet — refine)
    → TTS narration (gpt-4o-mini-tts, voice: "Onyx" for Hindi)
    → Video assembly (ffmpeg-api container)
    → Thumbnail generation (DALL-E 3 or Cloudinary)
    → Upload to YouTube (OAuth2)
    → Auto-generate captions
    → Post description + tags
    → Share to social (n8n Social Poster workflow)
```

### Channels to Automate
1. CryptoGyani — market analysis shorts
2. ITGYANI — AI tips/tutorials
3. The Employee Factory — career/HR tips
4. Health/ASMR (AI ASMR channel)
5. Tamil content (SPHNithyananda)

---

## 7. Context Window Management

### Session Budget
```
Max context: 50,000 tokens (not 200K)
Startup load: ~8KB (SOUL + USER + today's memory)
Per API call: <20K ideally
Compact trigger: every 30 min or after major task
```

### Compact Discipline
```
/compact → when session >30 min old
openclaw session new → for completely fresh context
memory_search() → always before claiming context
```

---

## 8. Agent Communication Protocol

### Channels
- **Telegram** (@cryptogyani_official, ID 427179140) — real-time alerts
- **Jira** — async task management, blocker tracking
- **Dashboard** (`/ops` tab) — live agent status
- **memory/YYYY-MM-DD.md** — daily handoff notes

### Alert Levels
| Level | When | Channel |
|-------|------|---------|
| 🟢 INFO | Routine updates | Dashboard log only |
| 🟡 WARN | Potential issue | Dashboard + Jira comment |
| 🔴 ALERT | Blocker / failure | Telegram + Jira + Dashboard |
| 💥 CRITICAL | Data loss / security | Telegram IMMEDIATE + Ashish |
