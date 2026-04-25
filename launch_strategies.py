#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launches all 10 strategies persistently in the container
Uses a wrapper script that runs strategies as background processes
"""
import sys
import io as _io
sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import paramiko
import io
import time

HOST = '194.233.64.74'
USER = 'rony'
PASSWORD = os.getenv('VPS_PASSWORD', '')
API_KEY = os.getenv('OPENALGO_API_KEY', '')

def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASSWORD, timeout=30)
    return client

def run(client, cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

def sudo(client, cmd, timeout=60):
    return run(client, f'echo "{PASSWORD}" | sudo -S {cmd}', timeout=timeout)

def main():
    print("Connecting...")
    ssh = ssh_connect()
    sftp = ssh.open_sftp()
    
    # Write a supervisor-style launch script that properly backgrounds
    supervisor_script = f'''#!/bin/bash
export OPENALGO_API_KEY="{API_KEY}"
export HOST_SERVER="http://127.0.0.1:5000"
export WEBSOCKET_URL="ws://127.0.0.1:8765"

LOG_DIR="/app/log/strategies"
mkdir -p "$LOG_DIR"

STRATEGIES=(
    "/app/strategies/strategy_01_vwap_rsi_ICICIBANK.py"
    "/app/strategies/strategy_02_ema_ribbon_HDFCBANK.py"
    "/app/strategies/strategy_03_supertrend_RELIANCE.py"
    "/app/strategies/strategy_04_bb_rsi_SBIN.py"
    "/app/strategies/strategy_05_macd_volume_TCS.py"
    "/app/strategies/strategy_06_orb_NIFTY.py"
    "/app/strategies/strategy_07_stoch_rsi_macd_BAJFINANCE.py"
    "/app/strategies/strategy_08_donchian_LT.py"
    "/app/strategies/strategy_09_ichimoku_INFY.py"
    "/app/strategies/strategy_10_adx_di_AXISBANK.py"
)

echo "=== Launching Strategies at $(date) ==="
for script in "${{STRATEGIES[@]}}"; do
    name=$(basename "$script" .py)
    logfile="$LOG_DIR/$name.log"
    
    # Check if already running
    if pgrep -f "$script" > /dev/null 2>&1; then
        echo "  [RUNNING] $name"
    else
        python3 "$script" >> "$logfile" 2>&1 &
        echo "  [START] $name PID=$!"
        sleep 0.3
    fi
done

echo "Done. $(date)"
# Keep script running to show status
sleep 2
echo "=== Process Check ==="
pgrep -la python3 | grep strategy || echo "Processes may still be initializing"
'''
    
    # Upload the supervisor script
    sftp.putfo(io.BytesIO(supervisor_script.encode('utf-8')), '/tmp/run_strategies.sh')
    sudo(ssh, 'docker cp /tmp/run_strategies.sh openalgo-web:/app/strategies/run_strategies.sh')
    sudo(ssh, 'docker exec openalgo-web chmod +x /app/strategies/run_strategies.sh')
    print("[OK] Supervisor script uploaded")
    
    # Now run it inside a screen or via nohup properly using docker exec with env
    # The trick: run the bash script in background using a wrapper
    wrapper = f'''#!/bin/bash
# This runs inside the container
/app/strategies/run_strategies.sh
'''
    sftp.putfo(io.BytesIO(wrapper.encode('utf-8')), '/tmp/wrapper.sh')
    sudo(ssh, 'docker cp /tmp/wrapper.sh openalgo-web:/tmp/wrapper.sh')
    sudo(ssh, 'docker exec openalgo-web chmod +x /tmp/wrapper.sh')
    
    # Run it detached via docker exec with screen or at minimum nohup on host
    # Best approach: use 'at' or run directly
    print("Launching all strategies...")
    
    # Execute the script (it will background each strategy internally)
    out, err = sudo(ssh, (
        f'docker exec '
        f'-e OPENALGO_API_KEY={API_KEY} '
        f'-e HOST_SERVER=http://127.0.0.1:5000 '
        f'-e WEBSOCKET_URL=ws://127.0.0.1:8765 '
        f'openalgo-web bash /app/strategies/run_strategies.sh'
    ), timeout=30)
    print(out)
    if err.strip() and 'sudo' not in err.lower():
        print(f"stderr: {err[:300]}")
    
    # Wait and check
    time.sleep(3)
    print("\nChecking processes...")
    out_ps, _ = sudo(ssh, 'docker exec openalgo-web ps aux | grep "strategy_0" | grep -v grep | head -20')
    print(out_ps if out_ps.strip() else "  (no strategy processes found - may have exited)")
    
    out_pg, _ = sudo(ssh, 'docker exec openalgo-web pgrep -la python3 2>/dev/null | grep -i strat || echo "No strategy python processes"')
    print(out_pg)
    
    # Check logs
    print("\nChecking logs...")
    out_log, _ = sudo(ssh, 'docker exec openalgo-web ls -la /app/log/strategies/ 2>/dev/null')
    print(out_log if out_log.strip() else "  (no logs yet)")
    
    for i in [1, 2, 3]:
        names = {
            1: 'strategy_01_vwap_rsi_ICICIBANK',
            2: 'strategy_02_ema_ribbon_HDFCBANK',
            3: 'strategy_03_supertrend_RELIANCE'
        }
        out_l, _ = sudo(ssh, f'docker exec openalgo-web cat /app/log/strategies/{names[i]}.log 2>/dev/null | head -5 || echo "empty"')
        if out_l.strip():
            print(f"  Log {names[i]}: {out_l[:200]}")
    
    # Issue: docker exec exits when command finishes. The backgrounded processes may be orphaned.
    # Check if openalgo-web container keeps them alive
    print("\nContainer process tree:")
    out_top, _ = sudo(ssh, 'docker exec openalgo-web ps aux | head -30')
    print(out_top)
    
    sftp.close()
    ssh.close()

if __name__ == '__main__':
    main()
