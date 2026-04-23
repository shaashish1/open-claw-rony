# ITGYANI Email Dashboard

Unified mail client for all 9 ITGYANI accounts. Dark-themed, auto-tagging, draft-only.

## Quick Start (Docker — Recommended)

```bash
# 1. Clone / copy this folder to your laptop
# 2. From the dashboard/ directory:
docker compose up --build -d

# 3. Open in browser:
# http://localhost:8000
```

## First Run
- Dashboard starts and syncs all 9 accounts in background
- Auto-tags emails: Client / Job Lead / Payment / Spam
- Check sync status: http://localhost:8000/api/sync/status

## Telegram Alerts
Edit docker-compose.yml and set your bot token:
```yaml
TELEGRAM_BOT_TOKEN: "your-token-from-botfather"
```
Then restart: `docker compose restart`

## Accounts Connected
| Account | Brand |
|---|---|
| ashish.sharma14@gmail.com | Personal Gmail |
| ashish@itgyani.com | ITGYANI |
| ashish@cryptogyani.com | CryptoGyani |
| info@cryptogyani.com | CryptoGyani |
| trading@cryptogyani.com | CryptoGyani |
| ashish@theemployeefactory.com | Employee Factory |
| support@theemployeefactory.com | Employee Factory |
| ashish@technoflairlab.com | TechnoFlair Lab |
| info@kharadionline.com | Kharadi Online |

## API Endpoints
- `GET /api/accounts` — all accounts + unread counts
- `GET /api/emails?account=X&tag=client` — list emails
- `GET /api/emails/{account}/{uid}` — full email
- `POST /api/emails/{account}/{uid}/draft-reply` — save draft
- `GET /api/drafts` — all drafts
- `POST /api/sync` — trigger sync
- `GET /api/stats` — dashboard stats

## RULE: DRAFT ONLY
This system never sends emails. Draft replies are saved locally only.
Ashish reviews and sends manually.

## Stop
```bash
docker compose down
```
