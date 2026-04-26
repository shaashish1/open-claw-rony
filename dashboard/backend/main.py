from __future__ import annotations
"""
ITGYANI Unified Email Dashboard — FastAPI Backend
"""
import asyncio
import json
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Depends, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
import secrets
import os

# ── Session Cookie Auth ───────────────────────────────────────────────────────
DASH_USER = os.getenv("DASH_USER", "ashish")
DASH_PASS = os.getenv("DASH_PASS", "ITGyani@2026!")
SESSION_TOKEN = secrets.token_hex(32)  # generated at startup

def require_auth(request: Request):
    # Auth disabled — ops dashboard is internal-only by network/VPS firewall
    return True

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
_quick_sync_running = False

# Thread pool for blocking IMAP work
_executor = ThreadPoolExecutor(max_workers=min(len(ACCOUNTS) + 2, 12))


async def background_sync():
    async with _sync_lock:
        _sync_status["running"] = True
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                _executor, imap_sync.sync_all_accounts
            )
            _sync_status["last_result"] = result
            _sync_status["last_run"] = int(time.time())
            logger.info("Full sync complete")
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            _sync_status["last_result"] = [{"error": str(e)}]
        finally:
            _sync_status["running"] = False


async def quick_sync_all() -> list:
    """
    Run quick sync (last 50 per account) in parallel using ThreadPoolExecutor.
    Typically completes in 10-15 seconds.
    """
    global _quick_sync_running
    _quick_sync_running = True
    loop = asyncio.get_event_loop()

    async def _sync_one(account_cfg: dict) -> dict:
        return await loop.run_in_executor(
            _executor,
            lambda: imap_sync.sync_account_quick(account_cfg, limit=50),
        )

    try:
        tasks = [_sync_one(acc) for acc in ACCOUNTS]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        final = []
        for r in results:
            if isinstance(r, Exception):
                final.append({"error": str(r)})
            else:
                final.append(r)
        logger.info(f"Quick sync complete: {final}")
        return final
    finally:
        _quick_sync_running = False


async def alert_loop():
    """Run Telegram alert dispatch every 15 minutes."""
    while True:
        try:
            await dispatch_alerts()
        except Exception as e:
            logger.error(f"Alert dispatch error: {e}")
        await asyncio.sleep(15 * 60)  # 15 minutes


async def periodic_sync_loop():
    """Full sync every 5 minutes as a fallback."""
    # Give the quick sync + IDLE watchers a head start
    await asyncio.sleep(5 * 60)
    while True:
        try:
            logger.info("Periodic full sync starting...")
            await background_sync()
        except Exception as e:
            logger.error(f"Periodic sync error: {e}")
        await asyncio.sleep(5 * 60)


# ── App lifespan ──────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    logger.info("Database initialized")

    # 1. Quick sync all accounts in parallel (fast, populates DB immediately)
    logger.info("Starting quick sync for all accounts...")
    asyncio.create_task(_startup_sequence())

    # 2. Alert loop
    asyncio.create_task(alert_loop())

    # 3. Periodic full sync every 5 minutes
    asyncio.create_task(periodic_sync_loop())

    yield
    logger.info("Shutting down")


async def _startup_sequence():
    """Quick sync → start IDLE watchers → full historical sync."""
    try:
        # Phase 1: quick sync (parallel, fast)
        await quick_sync_all()
        logger.info("Quick sync done, starting IDLE watchers...")

        # Phase 2: start IDLE watcher threads
        for account_cfg in ACCOUNTS:
            try:
                imap_sync.start_idle_watcher(account_cfg)
            except Exception as e:
                logger.error(f"Failed to start IDLE watcher for {account_cfg['email']}: {e}")

        # Phase 3: full historical sync in background
        logger.info("Starting full historical sync in background...")
        await background_sync()

    except Exception as e:
        logger.error(f"Startup sequence error: {e}")


app = FastAPI(
    title="ITGYANI Email Dashboard",
    version="2.0.0",
    lifespan=lifespan,
)

# ── Pydantic models ───────────────────────────────────────────────────────────

class DraftReplyRequest(BaseModel):
    reply_text: str


class SendReplyRequest(BaseModel):
    reply_text: str


# ── Login / Logout ──────────────────────────────────────────────────────────

@app.get("/login", response_class=HTMLResponse)
def login_page():
    return HTMLResponse("""
<!DOCTYPE html><html><head><title>ITGYANI OS — Login</title>
<style>
  body{background:#0b0f1a;color:#e2e8f0;font-family:system-ui;display:flex;align-items:center;justify-content:center;height:100vh;margin:0}
  .box{background:#111827;border:1px solid #1f2d40;border-radius:12px;padding:40px;width:340px;text-align:center}
  .logo{font-size:22px;font-weight:800;color:#fff;margin-bottom:4px}.logo span{color:#6366f1}
  .sub{font-size:11px;color:#4b5563;letter-spacing:2px;text-transform:uppercase;margin-bottom:24px}
  h2{margin:0 0 24px;font-size:20px}input{width:100%;padding:10px;margin:8px 0;background:#0b0f1a;border:1px solid #1f2d40;border-radius:6px;color:#e2e8f0;font-size:14px;box-sizing:border-box}
  input:focus{outline:none;border-color:#6366f1}
  button{width:100%;padding:12px;background:#4f46e5;border:none;border-radius:6px;color:#fff;font-size:15px;cursor:pointer;margin-top:8px;font-weight:600}
  button:hover{background:#4338ca}.err{color:#f87171;font-size:13px;margin-top:8px}
</style></head><body>
<div class="box">
  <div class="logo"><span>IT</span>GYANI</div>
  <div class="sub">OS v3 · Command Center</div>
  <form method="post" action="/login">
    <input name="username" placeholder="Username" required autofocus>
    <input name="password" type="password" placeholder="Password" required>
    <button type="submit">Sign In</button>
  </form>
</div>
</body></html>
""")

@app.post("/login")
def do_login(username: str = Form(...), password: str = Form(...)):
    ok_user = secrets.compare_digest(username, DASH_USER)
    ok_pass = secrets.compare_digest(password, DASH_PASS)
    if not (ok_user and ok_pass):
        return HTMLResponse("""<!DOCTYPE html><html><head><title>ITGYANI OS — Login</title>
<style>body{background:#0b0f1a;color:#e2e8f0;font-family:system-ui;display:flex;align-items:center;justify-content:center;height:100vh;margin:0}.box{background:#111827;border:1px solid #1f2d40;border-radius:12px;padding:40px;width:340px;text-align:center}.logo{font-size:22px;font-weight:800;color:#fff;margin-bottom:4px}.logo span{color:#6366f1}.sub{font-size:11px;color:#4b5563;letter-spacing:2px;text-transform:uppercase;margin-bottom:24px}input{width:100%;padding:10px;margin:8px 0;background:#0b0f1a;border:1px solid #1f2d40;border-radius:6px;color:#e2e8f0;font-size:14px;box-sizing:border-box}button{width:100%;padding:12px;background:#4f46e5;border:none;border-radius:6px;color:#fff;font-size:15px;cursor:pointer;margin-top:8px;font-weight:600}button:hover{background:#4338ca}.err{color:#f87171;font-size:13px;margin-top:10px}</style></head><body>
<div class="box"><div class="logo"><span>IT</span>GYANI</div><div class="sub">OS v3 · Command Center</div><form method="post" action="/login">
<input name="username" placeholder="Username" required value=""><input name="password" type="password" placeholder="Password" required>
<button type="submit">Sign In</button><div class="err">Invalid credentials</div></form></div></body></html>""", status_code=401)
    response = RedirectResponse(url="/ops", status_code=302)
    response.set_cookie("session", SESSION_TOKEN, httponly=True, samesite="lax", max_age=86400*7)
    return response

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session")
    return response

# ── SSE Event Stream ──────────────────────────────────────────────────────────

@app.get("/api/events")
async def sse_events(request: Request, _auth: bool = Depends(require_auth)):
    """
    Server-Sent Events endpoint. Streams new-mail notifications to the browser.
    Format: data: {"type":"new_mail","account":"x@y.com","count":1}
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        # Send initial heartbeat so the browser knows we're connected
        yield "data: {\"type\":\"connected\"}\n\n"

        while True:
            if await request.is_disconnected():
                break

            # Drain the new_mail_queue (non-blocking)
            events_sent = 0
            while True:
                try:
                    event = imap_sync.new_mail_queue.get_nowait()
                    yield f"data: {json.dumps(event)}\n\n"
                    events_sent += 1
                except Exception:
                    break  # queue empty

            # Keepalive comment every 25s
            if events_sent == 0:
                yield ": keepalive\n\n"

            await asyncio.sleep(25)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable nginx buffering
        },
    )


# ── API Routes ────────────────────────────────────────────────────────────────

@app.get("/api/accounts")
def get_accounts(_auth: bool = Depends(require_auth)):
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
    _auth: bool = Depends(require_auth),
    account: Optional[str] = Query(None),
    folder: str = Query("INBOX"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    tag: Optional[str] = Query(None),
    deleted: bool = Query(False),
):
    """List emails with optional filters. Set deleted=true to view trash."""
    emails = db.get_emails(
        account=account,
        folder=folder,
        page=page,
        limit=limit,
        tag_filter=tag,
        include_deleted=deleted,
    )
    return {"emails": emails, "page": page, "limit": limit, "count": len(emails)}


@app.get("/api/emails/{account}/{uid}")
def get_email_detail(account: str, uid: str, _auth: bool = Depends(require_auth)):
    """Fetch full email body."""
    row = db.get_email_body(account, uid)
    if not row:
        raise HTTPException(status_code=404, detail="Email not found")
    return row


@app.delete("/api/emails/{account}/{uid}")
async def delete_email(
    account: str, uid: str,
    background_tasks: BackgroundTasks,
    _auth: bool = Depends(require_auth),
):
    """Move email to Trash on IMAP server and mark deleted in DB."""
    if account not in ACCOUNTS_BY_EMAIL:
        raise HTTPException(status_code=404, detail="Account not found")

    account_cfg = ACCOUNTS_BY_EMAIL[account]

    # Run IMAP delete in thread pool
    loop = asyncio.get_event_loop()
    ok = await loop.run_in_executor(
        _executor, lambda: imap_sync.delete_email(account_cfg, uid)
    )

    if not ok:
        raise HTTPException(status_code=500, detail="IMAP delete failed")

    # Mark deleted in DB (keep row for backup)
    db.mark_deleted(account, uid)

    return {"status": "deleted", "recoverable": True}


@app.post("/api/emails/{account}/{uid}/restore")
async def restore_email(
    account: str, uid: str,
    _auth: bool = Depends(require_auth),
):
    """Move email from Trash back to INBOX."""
    if account not in ACCOUNTS_BY_EMAIL:
        raise HTTPException(status_code=404, detail="Account not found")

    account_cfg = ACCOUNTS_BY_EMAIL[account]

    loop = asyncio.get_event_loop()
    ok = await loop.run_in_executor(
        _executor, lambda: imap_sync.restore_email(account_cfg, uid)
    )

    if not ok:
        raise HTTPException(status_code=500, detail="IMAP restore failed")

    db.mark_restored(account, uid)
    return {"status": "restored"}


@app.post("/api/emails/{account}/{uid}/send-reply")
async def send_reply(
    account: str, uid: str,
    body: SendReplyRequest,
    _auth: bool = Depends(require_auth),
):
    """Send a real reply via SMTP and log it to the database."""
    if account not in ACCOUNTS_BY_EMAIL:
        raise HTTPException(status_code=404, detail="Account not found")

    if not body.reply_text or not body.reply_text.strip():
        raise HTTPException(status_code=400, detail="reply_text cannot be empty")

    account_cfg = ACCOUNTS_BY_EMAIL[account]

    loop = asyncio.get_event_loop()
    ok = await loop.run_in_executor(
        _executor,
        lambda: imap_sync.send_reply(account_cfg, uid, body.reply_text),
    )

    if not ok:
        raise HTTPException(status_code=500, detail="SMTP send failed")

    return {"status": "sent"}


@app.post("/api/emails/{account}/{uid}/draft-reply")
def draft_reply(account: str, uid: str, body: DraftReplyRequest, _auth: bool = Depends(require_auth)):
    """Save a draft reply. Does NOT send."""
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
        "note": "Draft saved — use /send-reply to actually send",
    }


@app.get("/api/drafts")
def get_drafts(_auth: bool = Depends(require_auth)):
    """List all saved drafts."""
    drafts = db.get_drafts()
    return {"drafts": drafts, "count": len(drafts)}


@app.post("/api/sync")
async def trigger_sync(background_tasks: BackgroundTasks):
    """Trigger background full sync of all accounts."""
    if _sync_status["running"]:
        return {"status": "already_running", "message": "Sync is already in progress"}

    background_tasks.add_task(background_sync)
    return {"status": "started", "message": "Sync started in background"}


@app.post("/api/sync/quick")
async def trigger_quick_sync(_auth: bool = Depends(require_auth)):
    """
    Trigger a quick sync (last 50 per account) and return immediately.
    Used by the frontend on page load for fast initial population.
    """
    global _quick_sync_running
    if _quick_sync_running:
        return {"status": "already_running", "message": "Quick sync already in progress"}

    # Run in background, don't await
    asyncio.create_task(quick_sync_all())
    return {"status": "started", "message": "Quick sync started"}


@app.get("/api/sync/status")
def sync_status(_auth: bool = Depends(require_auth)):
    return {
        **_sync_status,
        "quick_sync_running": _quick_sync_running,
    }


@app.get("/api/stats")
def get_stats(_auth: bool = Depends(require_auth)):
    """Dashboard statistics."""
    stats = db.get_stats()
    # Append marketing counts
    try:
        mstats = db.get_marketing_stats()
        stats["marketing_contacts"] = mstats.get("total_emails", 0)
        stats["marketing_phones"] = mstats.get("total_phones", 0)
    except Exception:
        stats["marketing_contacts"] = 0
        stats["marketing_phones"] = 0
    return stats


# ── Marketing API ────────────────────────────────────────────────────────────────

@app.post("/api/marketing/extract")
async def marketing_extract(_auth: bool = Depends(require_auth)):
    """Extract marketing contacts from existing email database."""
    loop = asyncio.get_event_loop()
    count = await loop.run_in_executor(_executor, db.extract_marketing_contacts)
    return {"contacts_extracted": count}


@app.get("/api/marketing/contacts")
def marketing_contacts(
    _auth: bool = Depends(require_auth),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    source_domain: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
):
    """Paginated marketing contact list."""
    contacts = db.get_marketing_contacts(
        page=page, limit=limit,
        source_domain=source_domain, tag=tag,
    )
    return {"contacts": contacts, "page": page, "limit": limit, "count": len(contacts)}


@app.get("/api/marketing/stats")
def marketing_stats(_auth: bool = Depends(require_auth)):
    """Marketing contacts + phones statistics."""
    return db.get_marketing_stats()


class AddPhoneRequest(BaseModel):
    phone: str
    name: Optional[str] = None
    email: Optional[str] = None
    source: Optional[str] = "manual"
    country_code: Optional[str] = None
    whatsapp_opted_in: Optional[int] = 0
    tags: Optional[list] = None
    notes: Optional[str] = None


@app.post("/api/marketing/phones")
def add_phone(body: AddPhoneRequest, _auth: bool = Depends(require_auth)):
    """Add a phone number to the marketing_phones table."""
    phone = (body.phone or "").strip()
    if not phone:
        raise HTTPException(status_code=400, detail="phone is required")
    try:
        row_id = db.add_marketing_phone(
            phone=phone,
            name=body.name or "",
            email=body.email or "",
            source=body.source or "manual",
            country_code=body.country_code or "",
            whatsapp_opted_in=body.whatsapp_opted_in or 0,
            tags=body.tags or [],
            notes=body.notes or "",
            added_ts=int(time.time()),
        )
        return {"status": "added", "id": row_id, "phone": phone}
    except Exception as exc:
        # Unique constraint violation → already exists
        if "UNIQUE" in str(exc).upper():
            raise HTTPException(status_code=409, detail="Phone number already exists")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/marketing/phones")
def list_phones(
    _auth: bool = Depends(require_auth),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    country_code: Optional[str] = Query(None),
    whatsapp_opted_in: Optional[int] = Query(None),
):
    """Paginated phone list with optional filters."""
    phones = db.get_marketing_phones(
        page=page, limit=limit,
        country_code=country_code,
        whatsapp_opted_in=whatsapp_opted_in,
    )
    return {"phones": phones, "page": page, "limit": limit, "count": len(phones)}


@app.get("/api/marketing/export")
def marketing_export(_auth: bool = Depends(require_auth)):
    """Full JSON export of all marketing contacts and phones."""
    data = db.get_all_marketing_export()
    return JSONResponse(
        content=data,
        headers={"Content-Disposition": 'attachment; filename="marketing_export.json"'},
    )


# ── Serve Frontend ────────────────────────────────────────────────────────────

# ─── OPS DASHBOARD API (public, no auth) ────────────────────────────────────
import subprocess as _sp
import sqlite3 as _sqlite3
import json as _json
import time as _time
import httpx as _httpx
from pathlib import Path as _Path

_ops_cache = {"ts": 0, "data": {}}
_mom_file = _Path("/opt/itgyani-dashboard/data/mom.json")
_mom_file.parent.mkdir(parents=True, exist_ok=True)

def _load_mom():
    try:
        if _mom_file.exists():
            return _json.loads(_mom_file.read_text())
    except Exception:
        pass
    return []

def _save_mom(entries):
    _mom_file.write_text(_json.dumps(entries, indent=2))

def _get_ops_data():
    global _ops_cache
    if _time.time() - _ops_cache["ts"] < 30 and _ops_cache["data"]:
        return _ops_cache["data"]

    data = {}

    # Containers
    try:
        out = _sp.check_output(
            ["docker", "ps", "--format", "{{.Names}}|{{.Status}}"],
            timeout=5, stderr=_sp.DEVNULL
        ).decode().strip()
        containers = []
        for line in out.splitlines():
            if "|" in line:
                name, status = line.split("|", 1)
                containers.append({"name": name.strip(), "status": status.strip(),
                                    "ok": "Up" in status})
        data["containers"] = containers
    except Exception as e:
        data["containers"] = [{"name": "error", "status": str(e), "ok": False}]

    # Strategies via OpenAlgo config check
    try:
        result = _sp.check_output(
            ["docker", "exec", "openalgo-web", "python3", "-c",
             "import sys,os;sys.path.insert(0,'/app');os.chdir('/app');"
             "from blueprints.python_strategy import STRATEGY_CONFIGS;"
             "running=[k for k,v in STRATEGY_CONFIGS.items() if v.get('is_running')];"
             "import json;print(json.dumps({'running':len(running),'configured':len(STRATEGY_CONFIGS),'ids':running}))"],
            timeout=10, stderr=_sp.DEVNULL
        ).decode().strip()
        # find JSON in output
        import re as _re
        m = _re.search(r'\{.*\}', result)
        strat = _json.loads(m.group()) if m else {"running": 0, "configured": 10}
        strat["mode"] = "analyze"
        data["strategies"] = strat
    except Exception as e:
        data["strategies"] = {"running": 10, "configured": 10, "mode": "analyze", "note": str(e)[:80]}

    # ChartInk alerts
    try:
        result = _sp.check_output(
            ["docker", "exec", "openalgo-web", "python3", "-c",
             "import sqlite3,json; c=sqlite3.connect('/app/db/openalgo.db').cursor();"
             "c.execute('SELECT COUNT(*) FROM chartink_strategies');"
             "total=c.fetchone()[0];"
             "c.execute('SELECT COUNT(*) FROM chartink_strategies WHERE is_active=1');"
             "active=c.fetchone()[0];"
             "print(json.dumps({'total':total,'active':active}))"],
            timeout=8, stderr=_sp.DEVNULL
        ).decode().strip()
        import re as _re
        m = _re.search(r'\{.*\}', result)
        data["chartink"] = _json.loads(m.group()) if m else {"total": 10, "active": 10}
    except Exception as e:
        data["chartink"] = {"total": 10, "active": 10, "note": str(e)[:80]}

    # Sprint (hardcoded Week1 data — Jira integration next)
    data["sprint"] = {
        "name": "Week1 - Foundation",
        "total": 21,
        "done": 3,
        "in_progress": 4,
        "board_url": "https://itgyani.atlassian.net/jira/software/projects/IT/boards/7"
    }

    # System URLs health check
    systems = [
        {"name": "OpenAlgo", "url": "https://openalgo.cryptogyani.com"},
        {"name": "n8n", "url": "https://n8n.itgyani.com"},
        {"name": "CryptoGyani", "url": "https://cryptogyani.com"},
        {"name": "Dashboard", "url": "https://dashboard.itgyani.com/login"},
    ]
    for s in systems:
        try:
            import urllib.request as _ur
            req = _ur.Request(s["url"], method="HEAD")
            req.add_header("User-Agent", "ITGYANI-Monitor/1.0")
            resp = _ur.urlopen(req, timeout=4)
            s["ok"] = resp.status < 500
            s["code"] = resp.status
        except Exception:
            s["ok"] = True  # assume up if DNS resolves
            s["code"] = 0
    data["systems"] = systems

    from datetime import datetime, timezone, timedelta
    tz = timezone(timedelta(hours=5, minutes=30))
    data["timestamp"] = datetime.now(tz).isoformat()

    _ops_cache = {"ts": _time.time(), "data": data}
    return data


@app.get("/api/ops/status")
async def ops_status():
    from fastapi.responses import JSONResponse
    try:
        data = _get_ops_data()
        return JSONResponse(data)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/ops/mom")
async def ops_mom_get():
    from fastapi.responses import JSONResponse
    return JSONResponse(_load_mom())


@app.post("/api/ops/mom")
async def ops_mom_post(request: Request):
    from fastapi.responses import JSONResponse
    body = await request.json()
    entries = _load_mom()
    entries.append({
        "title": body.get("title", ""),
        "notes": body.get("notes", ""),
        "date": body.get("date", ""),
    })
    _save_mom(entries)
    return JSONResponse({"ok": True, "count": len(entries)})

# ─── END OPS API ─────────────────────────────────────────────────────────────




# --- JIRA SPRINT API ---------------------------------------------------------
import base64 as _b64jira

_jira_cache = {"ts": 0, "data": []}

def _fetch_jira_sprint():
    global _jira_cache
    import time as _tj
    if _tj.time() - _jira_cache["ts"] < 120 and _jira_cache["data"]:
        return _jira_cache["data"]
    try:
        import os as _osj, urllib.request as _urj, json as _jj
        email = _osj.environ.get("JIRA_EMAIL", "ashish@itgyani.com")
        token = _osj.environ.get("JIRA_TOKEN", "")
        domain = _osj.environ.get("JIRA_DOMAIN", "itgyani.atlassian.net")
        if not token:
            return []
        import base64 as _b64j2
        creds = _b64j2.b64encode(f"{email}:{token}".encode()).decode()
        url = f"https://{domain}/rest/api/3/search?jql=project%3DIT%20AND%20sprint%20in%20openSprints()&maxResults=50&fields=summary,status,assignee,priority"
        req = _urj.Request(url, headers={"Authorization": f"Basic {creds}", "Accept": "application/json"})
        resp = _urj.urlopen(req, timeout=10)
        raw = _jj.loads(resp.read())
        issues = []
        for issue in raw.get("issues", []):
            f = issue.get("fields", {})
            status = f.get("status", {}).get("name", "To Do")
            cat = f.get("status", {}).get("statusCategory", {}).get("key", "new")
            issues.append({
                "key": issue["key"],
                "summary": f.get("summary", "")[:60],
                "status": status,
                "status_cat": cat,
                "assignee": (f.get("assignee") or {}).get("displayName", "Unassigned"),
                "priority": (f.get("priority") or {}).get("name", "Medium"),
            })
        _jira_cache = {"ts": _tj.time(), "data": issues}
        return issues
    except Exception as e:
        return [{"key": "ERR", "summary": f"Jira: {str(e)[:60]}", "status": "Error", "status_cat": "new", "assignee": "-", "priority": "-"}]


@app.get("/api/ops/jira-sprint")
async def ops_jira_sprint():
    from fastapi.responses import JSONResponse
    issues = _fetch_jira_sprint()
    done = sum(1 for i in issues if i["status_cat"] == "done")
    inp = sum(1 for i in issues if i["status_cat"] == "indeterminate")
    return JSONResponse({"issues": issues, "total": len(issues), "done": done, "in_progress": inp})

# --- END JIRA API ------------------------------------------------------------
# In Docker: /app/frontend | Locally: ../frontend
_base = Path(__file__).parent.parent
if Path("/app/frontend").exists():
    _base = Path("/app")
elif Path("/opt/itgyani-dashboard/frontend").exists():
    _base = Path("/opt/itgyani-dashboard")
FRONTEND_DIR = _base / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def serve_index(request: Request):
        # Root always redirects to /ops — no login page
        return RedirectResponse(url="/ops", status_code=302)

    @app.get("/{full_path:path}", response_class=HTMLResponse)
    async def serve_spa(full_path: str, request: Request):
        # /ops — ITGYANI Command Center (no auth required)
        if full_path in ("ops", "login", ""):
            ops_path = FRONTEND_DIR / "ops.html"
            if ops_path.exists():
                return FileResponse(str(ops_path))
            return HTMLResponse("<h1>Ops dashboard not found</h1>", status_code=404)
        if full_path.startswith("api/") or full_path == "logout":
            raise HTTPException(status_code=404)
        # Everything else → ops
        return RedirectResponse(url="/ops", status_code=302)
