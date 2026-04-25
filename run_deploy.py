#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master deployment script - uploads and deploys all 10 strategies
"""
import sys
import io as _io
sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import paramiko
import io
import os
import time

HOST = '194.233.64.74'
USER = 'rony'
PASSWORD = os.getenv('VPS_PASSWORD', '')
API_KEY = os.getenv('OPENALGO_API_KEY', '')

STRATEGIES_DIR = r'C:\Antigravity\projects\open-claw-rony\strategies'

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
    print("="*60)
    print("OpenAlgo Strategy Deployer — Full Run")
    print("="*60)
    
    ssh = ssh_connect()
    sftp = ssh.open_sftp()
    print("[OK] SSH + SFTP Connected")
    
    # 1. Test API Key
    print("\n[1] Testing API Key + Broker...")
    out, _ = sudo(ssh, f'curl -s -X POST http://127.0.0.1:5000/api/v1/funds -H "Content-Type: application/json" -d \'{{"apikey":"{API_KEY}"}}\'')
    print(f"  Funds API: {out[:200]}")
    
    # 2. Create directories in container
    print("\n[2] Creating directories...")
    sudo(ssh, 'docker exec openalgo-web mkdir -p /app/strategies')
    sudo(ssh, 'docker exec openalgo-web mkdir -p /app/log/strategies')
    print("  [OK] Directories created")
    
    # 3. Upload all strategy files
    print("\n[3] Uploading strategy files...")
    files_to_upload = []
    for f in os.listdir(STRATEGIES_DIR):
        if f.endswith('.py') or f.endswith('.sh'):
            files_to_upload.append(f)
    
    for fname in sorted(files_to_upload):
        local_path = os.path.join(STRATEGIES_DIR, fname)
        with open(local_path, 'rb') as fh:
            content = fh.read()
        
        # Upload to /tmp on VPS
        tmp_path = f'/tmp/{fname}'
        sftp.putfo(io.BytesIO(content), tmp_path)
        
        # Copy to container
        out_cp, err_cp = sudo(ssh, f'docker cp {tmp_path} openalgo-web:/app/strategies/{fname}')
        
        if 'Error' in err_cp or 'error' in err_cp.lower():
            print(f"  [ERR] {fname}: {err_cp[:100]}")
        else:
            print(f"  [OK] {fname}")
    
    # Make shell scripts executable
    sudo(ssh, 'docker exec openalgo-web chmod +x /app/strategies/launch_with_env.sh')
    
    # 4. Register strategies in DB
    print("\n[4] Registering strategies in DB...")
    out_reg, err_reg = sudo(ssh, 'docker exec openalgo-web python3 /app/strategies/register_strategies.py')
    print(out_reg)
    if err_reg.strip() and 'sudo' not in err_reg:
        print(f"  Errors: {err_reg[:300]}")
    
    # 5. Verify files
    print("\n[5] Verifying files in container...")
    out_ls, _ = sudo(ssh, 'docker exec openalgo-web ls -la /app/strategies/')
    print(out_ls)
    
    # 6. Test run strategy_01 for 15 seconds
    print("\n[6] Test run strategy_01 (15 seconds)...")
    test_cmd = (
        f'docker exec '
        f'-e OPENALGO_API_KEY={API_KEY} '
        f'-e HOST_SERVER=http://127.0.0.1:5000 '
        f'-e WEBSOCKET_URL=ws://127.0.0.1:8765 '
        f'openalgo-web timeout 15 python3 /app/strategies/strategy_01_vwap_rsi_ICICIBANK.py'
    )
    out_test, err_test = sudo(ssh, test_cmd, timeout=25)
    print(out_test)
    if err_test.strip() and 'sudo' not in err_test:
        print(f"  Test stderr: {err_test[:500]}")
    
    # 7. Launch all strategies in background
    print("\n[7] Launching all 10 strategies...")
    launch_cmd = (
        f'docker exec -d '
        f'-e OPENALGO_API_KEY={API_KEY} '
        f'-e HOST_SERVER=http://127.0.0.1:5000 '
        f'-e WEBSOCKET_URL=ws://127.0.0.1:8765 '
        f'openalgo-web bash /app/strategies/launch_with_env.sh'
    )
    # Note: -d flag runs detached, so we do it differently
    # Use nohup inside the container
    for i in range(1, 11):
        strat_num = f"{i:02d}"
        # Find matching strategy file
        import glob
        matches = [f for f in files_to_upload if f.startswith(f'strategy_{strat_num}_') and f.endswith('.py')]
        if not matches:
            print(f"  [ERR] No file found for strategy_{strat_num}")
            continue
        fname = matches[0]
        name = fname.replace('.py', '')
        cmd = (
            f'docker exec '
            f'-e OPENALGO_API_KEY={API_KEY} '
            f'-e HOST_SERVER=http://127.0.0.1:5000 '
            f'-e WEBSOCKET_URL=ws://127.0.0.1:8765 '
            f'openalgo-web bash -c '
            f'"nohup python3 /app/strategies/{fname} > /app/log/strategies/{name}.log 2>&1 &"'
        )
        out_l, err_l = sudo(ssh, cmd, timeout=10)
        print(f"  [OK] Launched {fname}")
        time.sleep(0.5)
    
    # 8. Wait a moment then check processes
    time.sleep(5)
    print("\n[8] Checking running strategy processes...")
    out_ps, _ = sudo(ssh, 'docker exec openalgo-web ps aux | grep strategy_0 | grep -v grep')
    print(out_ps if out_ps.strip() else "  (checking...)")
    
    # Also check with pgrep
    out_pg, _ = sudo(ssh, 'docker exec openalgo-web pgrep -la python3 2>/dev/null | grep strategy || echo "No strategy processes found"')
    print(out_pg)
    
    # 9. Tail first strategy log
    print("\n[9] Last 20 lines of strategy_01 log...")
    out_log, _ = sudo(ssh, 'docker exec openalgo-web tail -20 /app/log/strategies/strategy_01_vwap_rsi_ICICIBANK.log 2>/dev/null || echo "Log empty/not found"')
    print(out_log)
    
    sftp.close()
    ssh.close()
    
    print("\n" + "="*60)
    print("DEPLOYMENT SUMMARY")
    print("="*60)
    print(f"[OK] API Key: {API_KEY[:16]}...{API_KEY[-8:]}")
    print(f"[OK] Files uploaded: {len(files_to_upload)}")
    print(f"[OK] Container: openalgo-web")
    print(f"[OK] Strategies dir: /app/strategies/")
    print(f"[OK] Log dir: /app/log/strategies/")
    print()
    print("Commands to manage:")
    print(f'  # Check processes:')
    print(f'  sudo docker exec openalgo-web pgrep -la python3')
    print(f'  # View logs:')
    print(f'  sudo docker exec openalgo-web tail -f /app/log/strategies/strategy_01_vwap_rsi_ICICIBANK.log')
    print(f'  # Stop all:')
    print(f'  sudo docker exec openalgo-web pkill -f "strategy_0"')
    print(f'  # Restart all:')
    print(f'  sudo docker exec openalgo-web bash /app/strategies/launch_with_env.sh')
    print()
    print("NOTE: Market closed (Saturday). Strategies loop 'market closed' every 60s.")
    print("Will activate automatically Monday 09:15 IST.")

if __name__ == '__main__':
    main()
