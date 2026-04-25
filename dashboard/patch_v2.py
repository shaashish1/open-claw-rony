"""
Patch ITGYANI dashboard to add /ops route BEFORE the catch-all.
The catch-all is inside a lifespan/startup block - we need to add routes
to the app object directly at module level instead.
"""
with open('/opt/itgyani-dashboard/main.py', 'r') as f:
    content = f.read()

# Check current state
if '@app.get("/ops"' in content:
    print("Already has /ops route - removing stale one first")
    # Will re-add cleanly

# The serve_spa catch-all is the problem - patch IT to serve ops.html for /ops path
old_spa = '''    @app.get("/{full_path:path}", response_class=HTMLResponse)
    async def serve_spa(full_path: str, request: Request):
        if full_path.startswith("api/") or full_path in ("login", "logout"):
            raise HTTPException(status_code=404)
        token = request.cookies.get("session")
        if not token or not secrets.compare_digest(token, SESSION_TOKEN):
            return RedirectResponse(url="/login", status_code=302)
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return HTMLResponse("<h1>Not Found</h1>", status_code=404)'''

new_spa = '''    @app.get("/{full_path:path}", response_class=HTMLResponse)
    async def serve_spa(full_path: str, request: Request):
        # OPS DASHBOARD - public, no auth required
        if full_path == "ops":
            ops_path = FRONTEND_DIR / "ops.html"
            if ops_path.exists():
                return FileResponse(str(ops_path))
            return HTMLResponse("<h1>Ops dashboard not found</h1>", status_code=404)
        if full_path.startswith("api/") or full_path in ("login", "logout"):
            raise HTTPException(status_code=404)
        token = request.cookies.get("session")
        if not token or not secrets.compare_digest(token, SESSION_TOKEN):
            return RedirectResponse(url="/login", status_code=302)
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return HTMLResponse("<h1>Not Found</h1>", status_code=404)'''

if old_spa in content:
    content = content.replace(old_spa, new_spa)
    with open('/opt/itgyani-dashboard/main.py', 'w') as f:
        f.write(content)
    print("PATCHED: /ops route added inside serve_spa catch-all")
else:
    print("ERROR: Could not find serve_spa to patch")
    # Show context
    idx = content.find('serve_spa')
    print(f"serve_spa context: {content[max(0,idx-100):idx+500]}")
