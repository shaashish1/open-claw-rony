#!/usr/bin/env python3
"""
ITGYANI Strategy Auto-Starter
Runs at container startup via /app/entrypoint_patch.sh
Injects and starts all 10 Yukti strategies into OpenAlgo's Python runner.
"""
import sys, os, shutil, time
from pathlib import Path
from datetime import datetime

os.chdir("/app")
sys.path.insert(0, "/app")

STRATEGIES = [
    ("strategy_01", "Yukti_vwap_rsi_ICICIBANK_5m"),
    ("strategy_02", "Yukti_ema_ribbon_HDFCBANK_5m"),
    ("strategy_03", "Yukti_supertrend_atr_expansion_RELIANCE_15m"),
    ("strategy_04", "Yukti_bb_rsi_SBIN_5m"),
    ("strategy_05", "Yukti_macd_rsi_combo_TCS_15m"),
    ("strategy_06", "Yukti_orb_scalper_NIFTY_15m"),
    ("strategy_07", "Yukti_stochastic_momentum_BAJFINANCE_5m"),
    ("strategy_08", "Yukti_donchian_volume_breakout_LT_5m"),
    ("strategy_09", "Yukti_ichimoku_rsi_INFY_15m"),
    ("strategy_10", "Yukti_adx_di_trend_AXISBANK_5m"),
]

def wait_for_app(max_wait=60):
    """Wait for OpenAlgo Flask app to be ready"""
    import urllib.request
    for i in range(max_wait):
        try:
            urllib.request.urlopen("http://127.0.0.1:5000", timeout=2)
            print(f"[autostart] OpenAlgo ready after {i}s")
            return True
        except:
            time.sleep(1)
    print("[autostart] WARNING: OpenAlgo not responding, starting anyway")
    return False

def main():
    print(f"[autostart] Starting at {datetime.now().isoformat()}")
    
    # Wait for Flask to be ready
    wait_for_app(30)
    time.sleep(3)  # Extra buffer
    
    from blueprints import python_strategy as ps_module

    scripts_dir = Path("/app/strategies/scripts")
    yukti_dir = Path("/app/strategies/yukti")
    logs_dir = Path("/app/log/strategies")
    scripts_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    launched = []
    for sid, name in STRATEGIES:
        src = yukti_dir / f"{sid}.py"
        dst = scripts_dir / f"{sid}.py"
        
        if not src.exists():
            print(f"[autostart] SKIP {sid} — file not found")
            continue
        
        shutil.copy2(src, dst)
        os.chmod(dst, 0o755)
        
        ps_module.STRATEGY_CONFIGS[sid] = {
            "name": sid,
            "file_path": str(dst),
            "filename": f"{sid}.py",
            "user_id": "ashish.sharma14@gmail.com",
            "exchange": "NSE",
            "start_time": "09:15",
            "stop_time": "15:15",
            "squareoff_time": "15:10",
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
        
        # Skip if already running
        if sid in ps_module.RUNNING_STRATEGIES:
            print(f"[autostart] {sid} already running, skipping")
            continue
        
        success, msg = ps_module.start_strategy_process(sid)
        status = "✅" if success else "❌"
        print(f"[autostart] {status} {sid}: {msg}")
        if success:
            launched.append(sid)
        time.sleep(0.5)
    
    print(f"\n[autostart] Launched {len(launched)}/10 strategies")
    print(f"[autostart] Running: {list(ps_module.RUNNING_STRATEGIES.keys())}")

if __name__ == "__main__":
    main()
