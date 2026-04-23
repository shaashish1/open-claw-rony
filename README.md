# open-claw-rony

Rony's workspace — AI agent managing ITGYANI operations.

## Projects

| Project | URL | Status |
|---|---|---|
| Email Dashboard | https://dashboard.itgyani.com | ✅ Live |
| Job Assistant | Coming soon | 🔜 |
| n8n Automation | https://n8n.itgyani.com | 🔜 |

## Structure

```
dashboard/          → Unified email dashboard (9 accounts)
agents/             → Specialized agents (job, marketing, etc.)
memory/             → Agent memory files
config/             → Config (no secrets committed)
```

## Security
- `.env` files are git-ignored — never committed
- Dashboard: password protected + HTTPS
- Draft-only email rule: never sends automatically
