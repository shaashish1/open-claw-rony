"""
Rewrite _fetch_jira_sprint to use board/7/issue (sprint is in future state).
"""
import re

path = "/opt/itgyani-dashboard/main.py"
with open(path, "r") as f:
    content = f.read()

# Find the function using regex and replace the entire body
pattern = r'(def _fetch_jira_sprint\(\):.*?)(        _jira_cache = \{"ts": _time\.time\(\), "data": issues\}\s+return issues)'
match = re.search(pattern, content, re.DOTALL)

if not match:
    print("ERROR: function not found by regex")
    idx = content.find("_fetch_jira_sprint")
    print(f"Found at idx {idx}:")
    print(content[idx:idx+500])
else:
    new_func = '''def _fetch_jira_sprint():
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

        # Board 7 issues — sprint is in "future" state so sprint/{id}/issue returns 404
        # Use board/issue which returns all 41 issues correctly
        url = f"https://{domain}/rest/agile/1.0/board/7/issue?maxResults=30&fields=summary,status,assignee,priority"
        req = _ur.Request(url, headers={"Authorization": f"Basic {creds}", "Accept": "application/json"})
        resp = _ur.urlopen(req, timeout=10)
        raw = _json.loads(resp.read())

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
        return issues'''

    # Replace from def to end of cache line
    new_content = content[:match.start()] + new_func + "\n" + content[match.end():]
    with open(path, "w") as f:
        f.write(new_content)
    print(f"PATCHED: function replaced ({match.start()}:{match.end()})")
