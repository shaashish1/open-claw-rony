"""
ITGYANI Unified Email Dashboard — FastAPI Backend
RULE: DRAFT ONLY - Never call SMTP send
"""
import asyncio
import time
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import secrets
import os

# ── Basic Auth ───────────────────────────────────────────────────────────────
security = HTTPBasic()
DASH_USER = os.getenv("DASH_USER", "ashish")
DASH_PASS = os.getenv("DASH_PASS", "ITGyani@2026!")

def require_auth(credentials: HTTPBasicCredentials = Depends(security)):
    ok_user = secrets.compare_digest(credentials.username.encode(), DASH_USER.encode())
    ok_pass = secrets.compare_digest(credentials.password.encode(), DASH_PASS.encode())
    if not (ok_user and ok_pass):
        raise HTTPException(status_code=401, detail="Unauthorized",
                            headers={"WWW-Authenticate": "Basic"})
    return credentials.username

import database as db
from config import ACCOUNTS, ACCOUNTS_BY_EMAIL
import imap_sync
from telegram_alerts import dispatch_alerts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("main")

# ── Background task state ─────────────────────────────────────────────────────

_sync_lock = asyncio.Lock()
_sync_status = {"running": False, "last_run": None, "last_result": None}


async def background_sync():
    async with _sync_lock:
        _sync_status["running"] = True
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, imap_sync.sync_all_accounts
            )
            _sync_status["last_result"] = result
            _sync_status["last_run"] = int(time.time())
            logger.info("Sync complete")
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            _sync_status["last_result"] = [{"error": str(e)}]
        finally:
            _sync_status["running"] = False


async def alert_loop():
    """Run Telegram alert dispatch every 15 minutes."""
    while True:
        try:
            await dispatch_alerts()
        except Exception as e:
            logger.error(f"Alert dispatch error: {e}")
        await asyncio.sleep(15 * 60)  # 15 minutes


# ── App lifespan ──────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    logger.info("Database initialized")

    # Kick off initial sync in background (don't block startup)
    asyncio.create_task(background_sync())
    asyncio.create_task(alert_loop())

    yield
    logger.info("Shutting down")


app = FastAPI(
    title="ITGYANI Email Dashboard",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Pydantic models ───────────────────────────────────────────────────────────

class DraftReplyRequest(BaseModel):
    reply_text: str


# ── API Routes ────────────────────────────────────────────────────────────────

@app.get("/api/accounts")
def get_accounts(user: str = Depends(require_auth)):
    """List all accounts with unread counts."""
    result = []
    for acc in ACCOUNTS:
        email = acc["email"]
        unread = db.get_unread_count(email)
        result.append({
            "email": email,
            "label": acc["label"],
            "imap_host": acc["imap_host"],
            "unread": unread,
        })
    return result


@app.get("/api/emails")
def get_emails(
    user: str = Depends(require_auth),
    account: Optional[str] = Query(None),
    folder: str = Query("INBOX"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    tag: Optional[str] = Query(None),
):
    """List emails with optional filters."""
    emails = db.get_emails(
        account=account,
        folder=folder,
        page=page,
        limit=limit,
        tag_filter=tag,
    )
    return {"emails": emails, "page": page, "limit": limit, "count": len(emails)}


@app.get("/api/emails/{account}/{uid}")
def get_email_detail(account: str, uid: str, user: str = Depends(require_auth)):
    """Fetch full email body."""
    row = db.get_email_body(account, uid)
    if not row:
        raise HTTPException(status_code=404, detail="Email not found")
    return row


@app.post("/api/emails/{account}/{uid}/draft-reply")
def draft_reply(account: str, uid: str, body: DraftReplyRequest, user: str = Depends(require_auth)):
    """
    Save a draft reply. NEVER sends.
    RULE: DRAFT ONLY - Never call SMTP send
    """
    if account not in ACCOUNTS_BY_EMAIL:
        raise HTTPException(status_code=404, detail="Account not found")

    # Check email exists
    email_row = db.get_email_body(account, uid)
    if not email_row:
        raise HTTPException(status_code=404, detail="Email not found")

    now = int(time.time())
    draft_id = db.save_draft(account, uid, body.reply_text, now)

    return {
        "draft_id": draft_id,
        "account": account,
        "uid": uid,
        "status": "saved",
        "note": "DRAFT ONLY — this will never be sent automatically",
    }


@app.get("/api/drafts")
def get_drafts(user: str = Depends(require_auth)):
    """List all saved drafts."""
    drafts = db.get_drafts()
    return {"drafts": drafts, "count": len(drafts)}


@app.post("/api/sync")
async def trigger_sync(background_tasks: BackgroundTasks):
    """Trigger background sync of all accounts."""
    if _sync_status["running"]:
        return {"status": "already_running", "message": "Sync is already in progress"}

    background_tasks.add_task(background_sync)
    return {"status": "started", "message": "Sync started in background"}


@app.get("/api/sync/status")
def sync_status(user: str = Depends(require_auth)):
    return _sync_status


@app.get("/api/stats")
def get_stats(user: str = Depends(require_auth)):
    """Dashboard statistics."""
    stats = db.get_stats()
    return stats


# ── Serve Frontend ────────────────────────────────────────────────────────────

# In Docker: /app/frontend | Locally: ../frontend
_base = Path("/app") if Path("/app").exists() else Path(__file__).parent.parent
FRONTEND_DIR = _base / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def serve_index():
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return HTMLResponse("<h1>Frontend not found</h1>", status_code=404)

    @app.get("/{full_path:path}", response_class=HTMLResponse)
    async def serve_spa(full_path: str):
        # Don't intercept /api routes (handled above)
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return HTMLResponse("<h1>Not Found</h1>", status_code=404)
