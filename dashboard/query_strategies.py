import urllib.request, json, sys
try:
    req = urllib.request.Request(
        "http://127.0.0.1:5000/python/status",
        headers={"Accept": "application/json"}
    )
    r = urllib.request.urlopen(req, timeout=5)
    data = json.loads(r.read())
    print("Status:", json.dumps(data, indent=2)[:500])
except Exception as e:
    print("HTTP err:", e)

# Also check via scheduler
try:
    import sys, os; sys.path.insert(0, '/app'); os.chdir('/app')
    from blueprints.python_strategy import STRATEGY_CONFIGS
    running = [k for k, v in STRATEGY_CONFIGS.items() if v.get('is_running')]
    print(f"is_running in STRATEGY_CONFIGS: {len(running)} — {running}")
except Exception as e:
    print("Config check err:", e)
