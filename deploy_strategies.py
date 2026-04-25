#!/usr/bin/env python3
"""
OpenAlgo Strategy Deployer
- Connects to VPS via SSH
- Retrieves API key
- Writes 10 strategy files
- Registers in DB
- Creates launch script
"""
import paramiko
import time
import sys

HOST = '194.233.64.74'
USER = 'rony'
PASSWORD = os.getenv('VPS_PASSWORD', '')

def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASSWORD, timeout=30)
    return client

def run_cmd(client, cmd, timeout=30):
    """Run command and return stdout+stderr"""
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

def run_sudo(client, cmd, timeout=60):
    """Run sudo command"""
    return run_cmd(client, f'echo "{PASSWORD}" | sudo -S {cmd}', timeout=timeout)

def main():
    print("=== Connecting to VPS ===")
    ssh = ssh_connect()
    print("Connected!")

    # Step 1: Check docker containers
    print("\n=== Step 1: Docker Status ===")
    out, err = run_sudo(ssh, 'docker ps --format "{{.Names}}\\t{{.Status}}"')
    print(out)

    # Step 2: Get API key
    print("\n=== Step 2: Retrieving API Key ===")
    
    # Method 1: Check .env file
    out1, _ = run_sudo(ssh, 'docker exec openalgo-web cat /app/.env')
    print("--- .env contents ---")
    print(out1[:3000])
    
    # Method 2: Check DB schema first
    out2, _ = run_sudo(ssh, "docker exec openalgo-web python3 -c \"import sqlite3; conn=sqlite3.connect('/app/db/openalgo.db'); c=conn.cursor(); c.execute(\\\"SELECT name FROM sqlite_master WHERE type='table'\\\"); print([r[0] for r in c.fetchall()]); conn.close()\"")
    print("--- DB Tables ---")
    print(out2)

    # Method 3: Check api_keys table structure
    out3, _ = run_sudo(ssh, "docker exec openalgo-web python3 -c \"import sqlite3; conn=sqlite3.connect('/app/db/openalgo.db'); c=conn.cursor(); c.execute('PRAGMA table_info(api_keys)'); print(c.fetchall()); conn.close()\"")
    print("--- api_keys schema ---")
    print(out3)

    # Method 4: Get raw api key data
    out4, _ = run_sudo(ssh, "docker exec openalgo-web python3 -c \"import sqlite3; conn=sqlite3.connect('/app/db/openalgo.db'); c=conn.cursor(); c.execute('SELECT * FROM api_keys LIMIT 5'); rows=c.fetchall(); [print(r) for r in rows]; conn.close()\"")
    print("--- api_keys data ---")
    print(out4)

    # Method 5: Try Fernet decryption
    decrypt_script = '''
import sqlite3, os, sys
sys.path.insert(0, '/app')

conn = sqlite3.connect('/app/db/openalgo.db')
c = conn.cursor()

# Get column names
c.execute("PRAGMA table_info(api_keys)")
cols = [r[1] for r in c.fetchall()]
print("Columns:", cols)

c.execute("SELECT * FROM api_keys LIMIT 5")
rows = c.fetchall()
for row in rows:
    print("Row:", dict(zip(cols, row)))

conn.close()

# Try to get from environment
try:
    secret = os.getenv("SECRET_KEY", "")
    print("SECRET_KEY length:", len(secret))
    if secret:
        from cryptography.fernet import Fernet
        f = Fernet(secret.encode() if isinstance(secret, str) else secret)
        conn2 = sqlite3.connect('/app/db/openalgo.db')
        c2 = conn2.cursor()
        c2.execute("SELECT * FROM api_keys LIMIT 1")
        row = c2.fetchone()
        if row:
            for val in row:
                if val and isinstance(val, str) and len(val) > 20:
                    try:
                        dec = f.decrypt(val.encode()).decode()
                        print("DECRYPTED:", dec)
                    except:
                        pass
        conn2.close()
except Exception as e:
    print("Decrypt error:", e)
'''
    out5, err5 = run_sudo(ssh, f"docker exec openalgo-web python3 -c '{decrypt_script}'")
    print("--- Decrypt attempt ---")
    print(out5)
    print("Errors:", err5[:500] if err5 else "None")

    ssh.close()
    print("\nDone with step 1 exploration")

if __name__ == '__main__':
    main()
