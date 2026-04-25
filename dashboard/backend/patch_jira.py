"""
Patch main.py to add /api/ops/jira-sprint endpoint.
Fetches live Sprint 1 issues from Jira Cloud API.
"""
import os

path = "/opt/itgyani-dashboard/main.py"
with open(path, "r") as f:
    content = f.read()

if "/api/ops/jira" in content:
    print("Already has jira endpoint — skipping")
    exit(0)

jira_route = '''
# ─── JIRA SPRINT API ─────────────────────────────────────────────────────────
import base64 as _b64

_jira_cache = {"ts": 0, "data": []}

def _fetch_jira_sprint():
    global _jira_cache
    if _time.time() - _jira_cache["ts"] < 120 and _jira_cache["data"]:
        return _jira_cache["data"]

    try:
        import os as _os
        email = _os.environ.get("JIRA_EMAIL", "ashish@itgyani.com")
        token = _os.environ.get("JIRA_TOKEN", "")
        domain = _os.environ.get("JIRA_DOMAIN", "itgyani.atlassian.net")

        if not token:
            # Try reading from config
            try:
                import config as _cfg
                token = getattr(_cfg, "JIRA_API_TOKEN", "")
                email = getattr(_cfg, "JIRA_EMAIL", email)
                domain = getattr(_cfg, "JIRA_DOMAIN", domain)
            except Exception:
                pass

        if not token:
            return []

        creds = _b64.b64encode(f"{email}:{token}".encode()).decode()
        import urllib.request as _ur
        import urllib.parse as _up

        # Get Sprint 1 issues (board 7)
        jql = _up.quote('sprint = 1 ORDER BY status ASC')
        url = f"https://{domain}/rest/api/3/search?jql={jql}&maxResults=30&fields=summary,status,assignee,priority"
        req = _ur.Request(url, headers={
            "Authorization": f"Basic {creds}",
            "Accept": "application/json"
        })
        resp = _ur.urlopen(req, timeout=8)
        issues_raw = _json.loads(resp.read())

        issues = []
        for issue in issues_raw.get("issues", []):
            f = issue.get("fields", {})
            status = f.get("status", {}).get("name", "To Do")
            status_cat = f.get("status", {}).get("statusCategory", {}).get("key", "new")
            issues.append({
                "key": issue["key"],
                "summary": f.get("summary", "")[:60],
                "status": status,
                "status_cat": status_cat,  # new/indeterminate/done
                "assignee": (f.get("assignee") or {}).get("displayName", "Unassigned"),
                "priority": (f.get("priority") or {}).get("name", "Medium"),
            })

        _jira_cache = {"ts": _time.time(), "data": issues}
        return issues
    except Exception as e:
        return [{"key": "ERR", "summary": f"Jira API error: {str(e)[:60]}", "status": "Error", "status_cat": "new", "assignee": "-", "priority": "-"}]


@app.get("/api/ops/jira-sprint")
async def ops_jira_sprint():
    from fastapi.responses import JSONResponse
    issues = _fetch_jira_sprint()
    done = sum(1 for i in issues if i["status_cat"] == "done")
    in_prog = sum(1 for i in issues if i["status_cat"] == "indeterminate")
    return JSONResponse({"issues": issues, "total": len(issues), "done": done, "in_progress": in_prog})

# ─── END JIRA SPRINT API ─────────────────────────────────────────────────────

'''

# Insert before the FRONTEND_DIR block
marker = "\n# In Docker: /app/frontend | Locally: ../frontend"
if marker in content:
    content = content.replace(marker, jira_route + marker)
    with open(path, "w") as f:
        f.write(content)
    print("PATCHED: /api/ops/jira-sprint added")
else:
    print("ERROR: marker not found")
