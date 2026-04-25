#!/usr/bin/env python3
"""
ITGYANI Strategy Auto-Starter v2
Starts all 10 Yukti strategies via OpenAlgo's internal /python/start/<id> route.
Uses the proper in-process call so strategies are tracked in RUNNING_STRATEGIES.
Called from app.py YuktiAutostart thread on container boot.
"""
import sys, os, shutil, time
from pathlib import Path
from datetime import datetime

os.chdir("/app")
sys.path.insert(0, "/app")

STRATEGIES = [
    "strategy_01", "strategy_02", "strategy_03", "strategy_04", "strategy_05",
    "strategy_06", "strategy_07", "strategy_08", "strategy_09", "strategy_10",
]

def wait_for_app(max_wait=30):
    import urllib.request
    for i in range(max_wait):
        try:
            urllib.request.urlopen("http://127.0.0.1:5000/api/v1/funds", timeout=2)
            return True
        except:
            time.sleep(1)
    return True  # proceed anyway after timeout

def main():
    print(f"[autostart] {datetime.now().isoformat()} Starting")
    wait_for_app(20)
    time.sleep(5)

    try:
        from blueprints.python_strategy import (
            start_strategy_process,
            STRATEGY_CONFIGS,
            RUNNING_STRATEGIES,
        )
    except Exception as e:
        print(f"[autostart] Import error: {e}")
        return

    scripts_dir = Path("/app/strategies/scripts")
    yukti_dir   = Path("/app/strategies/yukti")
    logs_dir    = Path("/app/log/strategies")
    for d in [scripts_dir, logs_dir]:
        d.mkdir(parents=True, exist_ok=True)

    launched = 0
    for sid in STRATEGIES:
        src = yukti_dir / f"{sid}.py"
        dst = scripts_dir / f"{sid}.py"

        if not src.exists():
            print(f"[autostart] SKIP {sid} — not found")
            continue

        shutil.copy2(src, dst)
        os.chmod(dst, 0o755)

        if sid in RUNNING_STRATEGIES:
            print(f"[autostart] {sid} already running")
            continue

        # Register in STRATEGY_CONFIGS exactly as OpenAlgo expects
        STRATEGY_CONFIGS[sid] = {
            "name":           sid,
            "file_path":      str(dst),
            "filename":       f"{sid}.py",
            "user_id":        "ashish.sharma14@gmail.com",
            "exchange":       "NSE",
            "start_time":     "09:15",
            "stop_time":      "15:15",
            "squareoff_time": "15:10",
            "is_active":      True,
            "is_running":     False,
            "pid":            None,
            "created_at":     datetime.now().isoformat(),
        }

        ok, msg = start_strategy_process(sid)
        status = "OK" if ok else "FAIL"
        print(f"[autostart] {status} {sid}: {msg}")
        if ok:
            launched += 1
        time.sleep(0.5)

    print(f"[autostart] Launched {launched}/10")
    print(f"[autostart] Running: {list(RUNNING_STRATEGIES.keys())}")

if __name__ == "__main__":
    main()
