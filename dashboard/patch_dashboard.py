"""Patch the existing ITGYANI dashboard to add /ops route"""
import re

with open('/opt/itgyani-dashboard/main.py', 'r') as f:
    content = f.read()

ops_route = '''
@app.get("/ops", response_class=HTMLResponse)
async def ops_dashboard(request: Request, auth: bool = Depends(require_auth)):
    from pathlib import Path as P2
    ops_file = P2("/opt/itgyani-dashboard/frontend/ops.html")
    if ops_file.exists():
        return HTMLResponse(ops_file.read_text())
    return HTMLResponse("<h1>Ops Dashboard loading...</h1>")

@app.get("/api/mom", response_class=JSONResponse)
async def get_mom(auth: bool = Depends(require_auth)):
    from pathlib import Path as P3
    mom_file = P3("/opt/itgyani-dashboard/data/mom.json")
    if mom_file.exists():
        return JSONResponse(json.loads(mom_file.read_text()))
    return JSONResponse({"meetings": []})

'''

if '/ops' not in content:
    # Insert before catch-all
    content = content.replace(
        '    @app.get("/{full_path:path}"',
        ops_route + '    @app.get("/{full_path:path}"'
    )
    with open('/opt/itgyani-dashboard/main.py', 'w') as f:
        f.write(content)
    print("PATCHED: /ops and /api/mom routes added")
else:
    print("ALREADY PATCHED: /ops route exists")
