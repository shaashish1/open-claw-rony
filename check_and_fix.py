#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check if strategies are running and fix if needed.
Uses OpenAlgo's built-in Python strategy runner.
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
    print("Connecting to VPS...")
    ssh = ssh_connect()
    sftp = ssh.open_sftp()
    
    # Check if there's a process manager in OpenAlgo we can use
    print("\n[1] Checking OpenAlgo's built-in strategy runner...")
    out, _ = sudo(ssh, 'docker exec openalgo-web find /app -name "*.py" | xargs grep -l "strategy_runner\|StrategyRunner\|manage_strategy" 2>/dev/null | head -10')
    print(out[:500])
    
    # Check the strategies routes
    out2, _ = sudo(ssh, 'docker exec openalgo-web find /app -path "*/blueprints/strategy*" -o -name "strategy*.py" 2>/dev/null | grep -v __pycache__ | head -20')
    print(out2[:500])
    
    # Check existing strategy runner mechanism
    print("\n[2] Checking for strategy management API...")
    out3, _ = sudo(ssh, 'docker exec openalgo-web find /app -name "*.py" | xargs grep -l "run_strategy\|start_strategy\|strategy_process" 2>/dev/null | head -10')
    print(out3[:500])
    
    # Check what processes are running in the container from the HOST side
    print("\n[3] Container processes (from host)...")
    # Docker uses /proc - check from host
    out4, _ = sudo(ssh, "docker exec openalgo-web ls /proc | grep '^[0-9]' | wc -l")
    print(f"  Total processes: {out4.strip()}")
    
    # Look for python processes
    out5, _ = sudo(ssh, "docker exec openalgo-web ls /proc/*/cmdline 2>/dev/null | head -50")
    # Check each proc for python
    out6, _ = sudo(ssh, r"for pid in $(ls /proc | grep '^[0-9]'); do cmd=$(cat /proc/$pid/cmdline 2>/dev/null | tr '\0' ' '); if echo $cmd | grep -q 'python3.*strategy'; then echo \"PID=$pid: $cmd\"; fi; done")
    if out6.strip():
        print(f"  Python strategy processes on HOST: {out6[:500]}")
    
    # Check strategy processes from within container using /proc
    out7, _ = sudo(ssh, r"docker exec openalgo-web sh -c \"for pid in \$(ls /proc | grep '^[0-9]'); do cmd=\$(cat /proc/\$pid/cmdline 2>/dev/null | tr '\0' ' '); if echo \$cmd | grep -q 'strategy'; then echo PID=\$pid: \$cmd; fi; done\"")
    print(f"  Strategy processes in container: {out7[:1000] if out7.strip() else 'None found'}")
    
    # Check recent logs
    print("\n[4] Recent log content...")
    for num, name in [(1, 'strategy_01_vwap_rsi_ICICIBANK'), (2, 'strategy_02_ema_ribbon_HDFCBANK')]:
        out_l, _ = sudo(ssh, f'docker exec openalgo-web cat /app/log/strategies/{name}.log 2>/dev/null')
        print(f"\n  {name}:")
        print(f"  {out_l[:300].strip()}")
    
    # Since docker exec bg processes die with the exec session,
    # we need a proper solution. Check if OpenAlgo has a process endpoint
    print("\n[5] Checking OpenAlgo API for strategy management...")
    out8, _ = sudo(ssh, f'curl -s http://127.0.0.1:5000/api/v1/strategy/start -X POST -H "Content-Type: application/json" -d \'{{"apikey":"{API_KEY}"}}\' 2>/dev/null | head -200')
    print(f"  Strategy start API: {out8[:300]}")
    
    # Check what routes OpenAlgo has
    out9, _ = sudo(ssh, "docker exec openalgo-web grep -r 'def.*strategy' /app/blueprints/ 2>/dev/null | grep -v '#' | head -20")
    print(f"\n  Strategy routes: {out9[:500]}")
    
    # Look for the Python Strategy runner in OpenAlgo
    out10, _ = sudo(ssh, "docker exec openalgo-web cat /app/blueprints/strategy/views.py 2>/dev/null | head -100")
    if out10.strip():
        print(f"\n  Strategy views: {out10[:500]}")
    else:
        out10b, _ = sudo(ssh, "docker exec openalgo-web find /app -name 'views.py' | xargs grep -l 'python\|strategy' 2>/dev/null | head -5")
        print(f"  Views with python/strategy: {out10b[:300]}")
    
    # THE REAL FIX: Run strategies as host-level docker exec processes
    # using nohup on the HOST (not inside container)
    print("\n[6] Launching strategies as persistent host-level processes...")
    
    for i in range(1, 11):
        names = {
            1: 'strategy_01_vwap_rsi_ICICIBANK',
            2: 'strategy_02_ema_ribbon_HDFCBANK',
            3: 'strategy_03_supertrend_RELIANCE',
            4: 'strategy_04_bb_rsi_SBIN',
            5: 'strategy_05_macd_volume_TCS',
            6: 'strategy_06_orb_NIFTY',
            7: 'strategy_07_stoch_rsi_macd_BAJFINANCE',
            8: 'strategy_08_donchian_LT',
            9: 'strategy_09_ichimoku_INFY',
            10: 'strategy_10_adx_di_AXISBANK',
        }
        name = names[i]
        fname = f'{name}.py'
        logfile = f'/tmp/strat_{i:02d}.log'
        
        # Launch via nohup on the HOST, running docker exec
        cmd = (
            f'nohup sudo docker exec '
            f'-e OPENALGO_API_KEY={API_KEY} '
            f'-e HOST_SERVER=http://127.0.0.1:5000 '
            f'-e WEBSOCKET_URL=ws://127.0.0.1:8765 '
            f'openalgo-web python3 /app/strategies/{fname} '
            f'> {logfile} 2>&1 &'
        )
        out_l, err_l = run(ssh, cmd, timeout=5)
        print(f"  Launched strategy {i:02d}: {name}")
        time.sleep(0.5)
    
    time.sleep(5)
    
    # Now check from host side
    print("\n[7] Checking from host side...")
    out_h, _ = run(ssh, "ps aux | grep 'docker exec.*strategy' | grep -v grep | head -20")
    print(out_h if out_h.strip() else "  Processes not found with ps aux")
    
    # Check with pgrep
    out_pg, _ = run(ssh, "pgrep -la docker | grep strategy | head -20")
    print(out_pg if out_pg.strip() else "  pgrep found nothing")
    
    # Check processes as the user running them
    out_pr, _ = run(ssh, "ps -u rony | head -20")
    print(f"  rony's processes: {out_pr[:500]}")
    
    # Check logs
    time.sleep(3)
    print("\n[8] Log check after 3s...")
    for i in [1, 2, 3]:
        out_l, _ = run(ssh, f'cat /tmp/strat_{i:02d}.log 2>/dev/null | head -5')
        print(f"  strat_{i:02d}.log: {out_l[:200].strip()}")
    
    sftp.close()
    ssh.close()
    print("\nDone.")

if __name__ == '__main__':
    main()
