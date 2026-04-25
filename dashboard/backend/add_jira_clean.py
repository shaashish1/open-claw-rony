"""Add /api/ops/jira-sprint endpoint to main.py cleanly."""
import re, os

path = "/opt/itgyani-dashboard/main.py"
with open(path, "r") as f:
    content = f.read()

if "/api/ops/jira-sprint" in content:
    print("Already has jira endpoint")
    exit(0)

# Find the right insertion point — before the FRONTEND_DIR or before the lifespan
# Use the ops_status endpoint as anchor — insert after it
anchor = '@app.get("/api/ops/mom")\nasync def ops_mom_get'
if anchor not in content:
    # Try another anchor
    anchor = '@app.post("/api/ops/mom")\nasync def ops_mom_post'

idx = content.find(anchor)
if idx == -1:
    print("ERROR: anchor not found")
    print("Looking for ops routes:")
    for line in content.splitlines():
        if 'api/ops' in line:
            print(" ", line)
    exit(1)

# Find end of ops_mom_post function (next @app decorator)
post_idx = content.find('\n\n# ─── END OPS', idx)
if post_idx == -1:
    post_idx = content.find('\n\n# In Docker', idx)
if post_idx == -1:
    # Find next @app route after mom
    post_idx = content.find('\n@app.', idx + 200)

jira_code = '''

# ─── JIRA SPRINT API ─────────────────────────────────────────────────────────
import base64 as _b64

_jira_cache = {"ts": 0, "data": []}

def _fetch_jira_sprint():
    global _jira_cache
    import time as _t2
    if _t2.time() - _jira_cache["ts"] < 120 and _jira_cache["data"]:
        return _jira_cache["data"]
    try:
        import os as _os2, urllib.request as _ur2, json as _j2
        email = _os2.environ.get("JIRA_EMAIL", "ashish@itgyani.com")
        token = _os2.environ.get("JIRA_TOKEN", "")
        domain = _os2.environ.get("JIRA_DOMAIN", "itgyani.atlassian.net")
        if not token:
            return []
        import base64 as _b642
        creds = _b642.b64encode(f"{email}:{token}".encode()).decode()
        url = f"https://{domain}/rest/agile/1.0/board/7/issue?maxResults=30&fields=summary,status,assignee,priority"
        req = _ur2.Request(url, headers={"Authorization": f"Basic {creds}", "Accept": "application/json"})
        resp = _ur2.urlopen(req, timeout=10)
        raw = _j2.loads(resp.read())
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
        _jira_cache = {"ts": _t2.time(), "data": issues}
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

# ─── END JIRA API ─────────────────────────────────────────────────────────────

'''

# Insert after the POST mom endpoint
insert_pos = post_idx
new_content = content[:insert_pos] + jira_code + content[insert_pos:]
with open(path, "w") as f:
    f.write(new_content)
print(f"PATCHED: /api/ops/jira-sprint inserted at pos {insert_pos}")
