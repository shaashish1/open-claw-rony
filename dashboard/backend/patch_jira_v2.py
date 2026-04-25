"""
Fix the Jira sprint API to use board sprints endpoint instead of JQL search.
"""
import re

path = "/opt/itgyani-dashboard/main.py"
with open(path, "r") as f:
    content = f.read()

old_fetch = '''def _fetch_jira_sprint():
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
        return [{"key": "ERR", "summary": f"Jira API error: {str(e)[:60]}", "status": "Error", "status_cat": "new", "assignee": "-", "priority": "-"}]'''

new_fetch = '''def _fetch_jira_sprint():
    global _jira_cache
    if _time.time() - _jira_cache["ts"] < 120 and _jira_cache["data"]:
        return _jira_cache["data"]

    try:
        import os as _os
        email = _os.environ.get("JIRA_EMAIL", "ashish@itgyani.com")
        token = _os.environ.get("JIRA_TOKEN", "")
        domain = _os.environ.get("JIRA_DOMAIN", "itgyani.atlassian.net")
        if not token:
            return []

        creds = _b64.b64encode(f"{email}:{token}".encode()).decode()
        import urllib.request as _ur

        # Use board sprints API — get active sprint issues for board 7
        # Step 1: get active sprint ID
        url = f"https://{domain}/rest/agile/1.0/board/7/sprint?state=active,future&maxResults=5"
        req = _ur.Request(url, headers={"Authorization": f"Basic {creds}", "Accept": "application/json"})
        resp = _ur.urlopen(req, timeout=8)
        sprints_data = _json.loads(resp.read())
        sprints = sprints_data.get("values", [])
        if not sprints:
            return []
        sprint_id = sprints[0]["id"]

        # Step 2: get issues in sprint
        url2 = f"https://{domain}/rest/agile/1.0/sprint/{sprint_id}/issue?maxResults=30&fields=summary,status,assignee,priority"
        req2 = _ur.Request(url2, headers={"Authorization": f"Basic {creds}", "Accept": "application/json"})
        resp2 = _ur.urlopen(req2, timeout=8)
        raw = _json.loads(resp2.read())

        issues = []
        for issue in raw.get("issues", []):
            f = issue.get("fields", {})
            status = f.get("status", {}).get("name", "To Do")
            status_cat = f.get("status", {}).get("statusCategory", {}).get("key", "new")
            issues.append({
                "key": issue["key"],
                "summary": f.get("summary", "")[:60],
                "status": status,
                "status_cat": status_cat,
                "assignee": (f.get("assignee") or {}).get("displayName", "Unassigned"),
                "priority": (f.get("priority") or {}).get("name", "Medium"),
            })

        _jira_cache = {"ts": _time.time(), "data": issues}
        return issues
    except Exception as e:
        return [{"key": "ERR", "summary": f"Jira error: {str(e)[:80]}", "status": "Error", "status_cat": "new", "assignee": "-", "priority": "-"}]'''

if old_fetch in content:
    content = content.replace(old_fetch, new_fetch)
    with open(path, "w") as f:
        f.write(content)
    print("PATCHED: Jira fetch now uses Agile board sprint API")
else:
    print("ERROR: old fetch function not found exactly")
    idx = content.find("_fetch_jira_sprint")
    print(f"Found at: {idx}, context: {content[idx:idx+100]}")
