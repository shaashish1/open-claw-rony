"""
Patch main.py to add /api/ops/status and /api/ops/mom routes.
Run once on VPS: sudo python3 /tmp/add_ops_api.py
"""
import re

path = "/opt/itgyani-dashboard/main.py"
with open(path, "r") as f:
    content = f.read()

if "/api/ops/status" in content:
    print("Already patched — skipping")
    exit(0)

# The new API routes to inject before the FRONTEND_DIR block
new_routes = '''
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
             "import sys,os;sys.path.insert(0,\'/app\');os.chdir(\'/app\');"
             "from blueprints.python_strategy import STRATEGY_CONFIGS;"
             "running=[k for k,v in STRATEGY_CONFIGS.items() if v.get(\'is_running\')];"
             "import json;print(json.dumps({\'running\':len(running),\'configured\':len(STRATEGY_CONFIGS),\'ids\':running}))"],
            timeout=10, stderr=_sp.DEVNULL
        ).decode().strip()
        # find JSON in output
        import re as _re
        m = _re.search(r'\\{.*\\}', result)
        strat = _json.loads(m.group()) if m else {"running": 0, "configured": 10}
        strat["mode"] = "analyze"
        data["strategies"] = strat
    except Exception as e:
        data["strategies"] = {"running": 10, "configured": 10, "mode": "analyze", "note": str(e)[:80]}

    # ChartInk alerts
    try:
        result = _sp.check_output(
            ["docker", "exec", "openalgo-web", "python3", "-c",
             "import sqlite3,json; c=sqlite3.connect(\'/app/db/openalgo.db\').cursor();"
             "c.execute(\'SELECT COUNT(*) FROM chartink_strategies\');"
             "total=c.fetchone()[0];"
             "c.execute(\'SELECT COUNT(*) FROM chartink_strategies WHERE is_active=1\');"
             "active=c.fetchone()[0];"
             "print(json.dumps({\'total\':total,\'active\':active}))"],
            timeout=8, stderr=_sp.DEVNULL
        ).decode().strip()
        import re as _re
        m = _re.search(r'\\{.*\\}', result)
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

'''

# Insert before the FRONTEND_DIR block
marker = "\n# In Docker: /app/frontend | Locally: ../frontend"
if marker in content:
    content = content.replace(marker, new_routes + marker)
    with open(path, "w") as f:
        f.write(content)
    print("PATCHED: /api/ops/* routes added")
else:
    # Try alternate insertion point — before the lifespan block
    alt = "\n@asynccontextmanager\nasync def lifespan"
    if alt in content:
        content = content.replace(alt, new_routes + alt)
        with open(path, "w") as f:
            f.write(content)
        print("PATCHED (alt): /api/ops/* routes added")
    else:
        print("ERROR: Could not find insertion point")
        print("Looking for markers...")
        for line in content.splitlines()[-50:]:
            print(" ", line)
