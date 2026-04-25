#!/usr/bin/env python3
"""
Full OpenAlgo Strategy Deployer
Deploys 10 production strategies to OpenAlgo on VPS
"""
import paramiko
import time
import sys
import json

HOST = '194.233.64.74'
USER = 'rony'
PASSWORD = os.getenv('VPS_PASSWORD', '')
API_KEY = os.getenv('OPENALGO_API_KEY', '')

def ssh_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASSWORD, timeout=30)
    return client

def run_sudo(client, cmd, timeout=60):
    full_cmd = f'echo "{PASSWORD}" | sudo -S bash -c \'{cmd}\''
    stdin, stdout, stderr = client.exec_command(full_cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

def docker_exec(client, py_script, timeout=60):
    """Write python script to a temp file and run in container"""
    # Escape for shell
    escaped = py_script.replace("'", "'\\''")
    cmd = f"docker exec openalgo-web python3 -c '{escaped}'"
    return run_sudo(client, cmd, timeout=timeout)

def write_file_via_ssh(sftp, remote_path, content):
    """Write a file to VPS via SFTP"""
    import io
    sftp.putfo(io.BytesIO(content.encode('utf-8')), remote_path)

def main():
    print("="*60)
    print("OpenAlgo Strategy Deployer")
    print("="*60)
    
    ssh = ssh_connect()
    print("✓ SSH Connected")
    
    sftp = ssh.open_sftp()
    
    # Step 1: Test API key
    print("\n=== Step 1: Testing API Key & Broker Connectivity ===")
    out, err = run_sudo(ssh, f'''curl -s -X POST http://127.0.0.1:5000/api/v1/funds \
  -H "Content-Type: application/json" \
  -d \'{{"apikey": "{API_KEY}"}}\'  ''')
    print(f"Funds API response: {out[:500]}")
    
    # Step 2: Check existing strategies to avoid duplicates
    print("\n=== Step 2: Checking existing strategies in DB ===")
    check_script = """
import sqlite3
conn = sqlite3.connect('/app/db/openalgo.db')
c = conn.cursor()
c.execute("SELECT name, platform FROM strategies WHERE platform='python' LIMIT 20")
rows = c.fetchall()
for r in rows:
    print(r)
print("Total python strategies:", len(rows))
conn.close()
"""
    out2, _ = run_sudo(ssh, f"docker exec openalgo-web python3 -c \"{check_script}\"")
    print(out2)
    
    # Step 3: Check /app/strategies directory
    print("\n=== Step 3: Checking /app/strategies directory ===")
    out3, _ = run_sudo(ssh, "docker exec openalgo-web ls -la /app/strategies/ 2>/dev/null || echo 'Directory does not exist'")
    print(out3)
    
    # Create strategies directory if needed
    run_sudo(ssh, "docker exec openalgo-web mkdir -p /app/strategies")
    run_sudo(ssh, "docker exec openalgo-web mkdir -p /app/log/strategies")
    print("✓ Directories created")
    
    # Step 4: Write all 10 strategy files
    print("\n=== Step 4: Writing 10 Strategy Files ===")
    
    strategies = get_all_strategies()
    
    for i, (filename, content) in enumerate(strategies, 1):
        # Write to /tmp on VPS first
        tmp_path = f'/tmp/{filename}'
        
        # Use heredoc via SSH to write the file
        write_script = f"cat > {tmp_path} << 'ENDOFFILE'\n{content}\nENDOFFILE"
        
        # Write via SFTP directly
        import io
        sftp.putfo(io.BytesIO(content.encode('utf-8')), tmp_path)
        
        # Copy to container
        out_cp, err_cp = run_sudo(ssh, f"docker cp {tmp_path} openalgo-web:/app/strategies/{filename}")
        
        if err_cp and 'Error' in err_cp:
            print(f"  ✗ Error copying {filename}: {err_cp}")
        else:
            print(f"  ✓ {i:2d}. {filename}")
    
    # Step 5: Register strategies in DB
    print("\n=== Step 5: Registering Strategies in DB ===")
    
    register_script = get_register_script()
    sftp.putfo(__import__('io').BytesIO(register_script.encode('utf-8')), '/tmp/register_strategies.py')
    run_sudo(ssh, "docker cp /tmp/register_strategies.py openalgo-web:/app/register_strategies.py")
    out_reg, err_reg = run_sudo(ssh, "docker exec openalgo-web python3 /app/register_strategies.py")
    print(out_reg)
    if err_reg:
        print("ERRORS:", err_reg[:500])
    
    # Step 6: Create launch script
    print("\n=== Step 6: Creating Launch Script ===")
    launch_script = get_launch_script()
    import io
    sftp.putfo(io.BytesIO(launch_script.encode('utf-8')), '/tmp/launch_all.sh')
    run_sudo(ssh, "docker cp /tmp/launch_all.sh openalgo-web:/app/strategies/launch_all.sh")
    run_sudo(ssh, "docker exec openalgo-web chmod +x /app/strategies/launch_all.sh")
    print("✓ Launch script created")
    
    # Step 7: Verify all files in container
    print("\n=== Step 7: Verifying Files in Container ===")
    out_ls, _ = run_sudo(ssh, "docker exec openalgo-web ls -la /app/strategies/")
    print(out_ls)
    
    # Step 8: Create .env update with API key export
    print("\n=== Step 8: Creating strategy env setup ===")
    env_setup = f'''#!/bin/bash
export OPENALGO_API_KEY="{API_KEY}"
export HOST_SERVER="http://127.0.0.1:5000"
export WEBSOCKET_URL="ws://127.0.0.1:8765"
'''
    import io
    sftp.putfo(io.BytesIO(env_setup.encode('utf-8')), '/tmp/strategy_env.sh')
    run_sudo(ssh, "docker cp /tmp/strategy_env.sh openalgo-web:/app/strategies/strategy_env.sh")
    run_sudo(ssh, "docker exec openalgo-web chmod +x /app/strategies/strategy_env.sh")
    
    # Step 9: Test run strategy_01 briefly (5 seconds, non-blocking)
    print("\n=== Step 9: Test Run strategy_01 (5s) ===")
    test_cmd = f'''docker exec -e OPENALGO_API_KEY={API_KEY} -e HOST_SERVER=http://127.0.0.1:5000 -e WEBSOCKET_URL=ws://127.0.0.1:8765 openalgo-web timeout 10 python3 /app/strategies/strategy_01_vwap_rsi_ICICIBANK.py 2>&1 | head -30'''
    out_test, err_test = run_sudo(ssh, test_cmd, timeout=30)
    print(out_test)
    if err_test:
        print("Test errors:", err_test[:300])
    
    # Step 10: Create the full launch-with-env script
    print("\n=== Step 10: Creating Full Launch Script (with env) ===")
    launch_with_env = f'''#!/bin/bash
# Launch all 10 strategies with proper environment
# Run this from inside the container or via docker exec

STRATEGIES_DIR="/app/strategies"
LOG_DIR="/app/log/strategies"
mkdir -p $LOG_DIR

export OPENALGO_API_KEY="{API_KEY}"
export HOST_SERVER="http://127.0.0.1:5000"
export WEBSOCKET_URL="ws://127.0.0.1:8765"

for strategy in $STRATEGIES_DIR/strategy_0*.py; do
    name=$(basename $strategy .py)
    if pgrep -f "$strategy" > /dev/null 2>&1; then
        echo "$name already running"
    else
        nohup python3 $strategy > $LOG_DIR/$name.log 2>&1 &
        echo "Started $name (PID: $!)"
        sleep 0.5
    fi
done
echo "All strategies launched."
echo "Use: tail -f $LOG_DIR/strategy_01_vwap_rsi_ICICIBANK.log to monitor"
'''
    import io
    sftp.putfo(io.BytesIO(launch_with_env.encode('utf-8')), '/tmp/launch_with_env.sh')
    run_sudo(ssh, "docker cp /tmp/launch_with_env.sh openalgo-web:/app/strategies/launch_with_env.sh")
    run_sudo(ssh, "docker exec openalgo-web chmod +x /app/strategies/launch_with_env.sh")
    
    print("\n" + "="*60)
    print("DEPLOYMENT COMPLETE")
    print("="*60)
    print(f"\nAPI Key: {API_KEY[:16]}...{API_KEY[-8:]}")
    print("\nTo launch all strategies:")
    print("  sudo docker exec openalgo-web bash /app/strategies/launch_with_env.sh")
    print("\nTo check logs:")
    print("  sudo docker exec openalgo-web tail -f /app/log/strategies/strategy_01_vwap_rsi_ICICIBANK.log")
    print("\nNote: Market is closed (Saturday). Strategies will loop in 'market closed' mode.")
    print("They will activate automatically on Monday 09:15 IST.")
    
    sftp.close()
    ssh.close()


def get_all_strategies():
    """Returns list of (filename, content) tuples for all 10 strategies"""
    
    HEADER = '''#!/usr/bin/env python3
from openalgo import api
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import os

api_key = os.getenv('OPENALGO_API_KEY', '')
host = os.getenv('HOST_SERVER', 'http://127.0.0.1:5000')
ws_url = os.getenv('WEBSOCKET_URL', 'ws://127.0.0.1:8765')

client = api(api_key=api_key, host=host, ws_url=ws_url)

def is_market_hours():
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=15, second=0, microsecond=0)
    return market_open <= now <= market_close

def get_data(symbol, exchange, interval, bars=50):
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
    df = client.history(symbol=symbol, exchange=exchange, interval=interval,
                        start_date=start_date, end_date=end_date)
    if df is not None and not df.empty:
        df.columns = [c.lower() for c in df.columns]
    return df
'''

    strategies = []
    
    # ============================================================
    # Strategy 01: VWAP + RSI Scalper - ICICIBANK 5m
    # ============================================================
    s01 = HEADER + '''
STRATEGY_NAME = "Yukti_vwap_rsi_ICICIBANK_5m"
SYMBOL = "ICICIBANK"
EXCHANGE = "NSE"
PRODUCT = "MIS"
QUANTITY = 1
INTERVAL = "5m"

def calc_vwap(df):
    df = df.copy()
    df['tp'] = (df['high'] + df['low'] + df['close']) / 3
    df['tpv'] = df['tp'] * df['volume']
    df['cum_tpv'] = df['tpv'].cumsum()
    df['cum_vol'] = df['volume'].cumsum()
    df['vwap'] = df['cum_tpv'] / df['cum_vol']
    return df

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))

def run_strategy():
    position = 0
    print(f"Starting {STRATEGY_NAME}...")
    while True:
        try:
            if not is_market_hours():
                print(f"[{datetime.now():%H:%M:%S}] Market closed. Sleeping 60s...")
                time.sleep(60)
                continue
            df = get_data(SYMBOL, EXCHANGE, INTERVAL)
            if df is None or df.empty or len(df) < 30:
                print("Insufficient data. Retrying in 30s...")
                time.sleep(30)
                continue
            df = calc_vwap(df)
            df['rsi'] = calc_rsi(df['close'])
            close = df['close'].iloc[-1]
            vwap = df['vwap'].iloc[-1]
            rsi = df['rsi'].iloc[-1]
            rsi_prev = df['rsi'].iloc[-2]
            buy_signal = (close > vwap) and (rsi_prev < 40) and (rsi >= 40)
            sell_signal = (close < vwap) and (rsi_prev > 60) and (rsi <= 60)
            print(f"[{datetime.now():%H:%M:%S}] Close={close:.2f} VWAP={vwap:.2f} RSI={rsi:.1f} Pos={position}")
            if buy_signal and position <= 0:
                position = QUANTITY
                resp = client.placesmartorder(strategy=STRATEGY_NAME, symbol=SYMBOL, action="BUY",
                    exchange=EXCHANGE, price_type="MARKET", product=PRODUCT,
                    quantity=QUANTITY, position_size=position)
                print(f"  >>> BUY SIGNAL: {resp}")
            elif sell_signal and position >= 0:
                position = -QUANTITY
                resp = client.placesmartorder(strategy=STRATEGY_NAME, symbol=SYMBOL, action="SELL",
                    exchange=EXCHANGE, price_type="MARKET", product=PRODUCT,
                    quantity=QUANTITY, position_size=position)
                print(f"  >>> SELL SIGNAL: {resp}")
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)
        time.sleep(30)

if __name__ == "__main__":
    run_strategy()
'''
    strategies.append(('strategy_01_vwap_rsi_ICICIBANK.py', s01))
    
    # ============================================================
    # Strategy 02: EMA Ribbon - HDFCBANK 5m
    # ============================================================
    s02 = HEADER + '''
STRATEGY_NAME = "Yukti_ema_ribbon_HDFCBANK_5m"
SYMBOL = "HDFCBANK"
EXCHANGE = "NSE"
PRODUCT = "MIS"
QUANTITY = 1
INTERVAL = "5m"

def run_strategy():
    position = 0
    print(f"Starting {STRATEGY_NAME}...")
    while True:
        try:
            if not is_market_hours():
                print(f"[{datetime.now():%H:%M:%S}] Market closed. Sleeping 60s...")
                time.sleep(60)
                continue
            df = get_data(SYMBOL, EXCHANGE, INTERVAL)
            if df is None or df.empty or len(df) < 30:
                print("Insufficient data. Retrying in 30s...")
                time.sleep(30)
                continue
            df['ema5'] = df['close'].ewm(span=5, adjust=False).mean()
            df['ema9'] = df['close'].ewm(span=9, adjust=False).mean()
            df['ema21'] = df['close'].ewm(span=21, adjust=False).mean()
            e5 = df['ema5'].iloc[-1]; e5_p = df['ema5'].iloc[-2]
            e9 = df['ema9'].iloc[-1]; e9_p = df['ema9'].iloc[-2]
            e21 = df['ema21'].iloc[-1]; e21_p = df['ema21'].iloc[-2]
            bullish_aligned = (e5 > e9 > e21) and (e5 > e5_p) and (e9 > e9_p) and (e21 > e21_p)
            bearish_aligned = (e5 < e9 < e21) and (e5 < e5_p) and (e9 < e9_p) and (e21 < e21_p)
            # Signal on fresh alignment (was not aligned before)
            e5_pp = df['ema5'].iloc[-3]; e9_pp = df['ema9'].iloc[-3]; e21_pp = df['ema21'].iloc[-3]
            prev_bull = (e5_p > e9_p > e21_p)
            prev_bear = (e5_p < e9_p < e21_p)
            buy_signal = bullish_aligned and not prev_bull
            sell_signal = bearish_aligned and not prev_bear
            print(f"[{datetime.now():%H:%M:%S}] EMA5={e5:.2f} EMA9={e9:.2f} EMA21={e21:.2f} Pos={position}")
            if buy_signal and position <= 0:
                position = QUANTITY
                resp = client.placesmartorder(strategy=STRATEGY_NAME, symbol=SYMBOL, action="BUY",
                    exchange=EXCHANGE, price_type="MARKET", product=PRODUCT,
                    quantity=QUANTITY, position_size=position)
                print(f"  >>> BUY: {resp}")
            elif sell_signal and position >= 0:
                position = -QUANTITY
                resp = client.placesmartorder(strategy=STRATEGY_NAME, symbol=SYMBOL, action="SELL",
                    exchange=EXCHANGE, price_type="MARKET", product=PRODUCT,
                    quantity=QUANTITY, position_size=position)
                print(f"  >>> SELL: {resp}")
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)
        time.sleep(30)

if __name__ == "__main__":
    run_strategy()
'''
    strategies.append(('strategy_02_ema_ribbon_HDFCBANK.py', s02))
    
    # ============================================================
    # Strategy 03: Supertrend ATR - RELIANCE 15m
    # ============================================================
    s03 = HEADER + '''
STRATEGY_NAME = "Yukti_supertrend_RELIANCE_15m"
SYMBOL = "RELIANCE"
EXCHANGE = "NSE"
PRODUCT = "MIS"
QUANTITY = 1
INTERVAL = "15m"

def calc_supertrend(df, atr_period=10, multiplier=3):
    df = df.copy()
    high = df['high']
    low = df['low']
    close = df['close']
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(span=atr_period, adjust=False).mean()
    hl2 = (high + low) / 2
    upper = hl2 + multiplier * atr
    lower = hl2 - multiplier * atr
    supertrend = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(index=df.index, dtype=int)
    for i in range(1, len(df)):
        if close.iloc[i] > upper.iloc[i-1]:
            direction.iloc[i] = 1
        elif close.iloc[i] < lower.iloc[i-1]:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = direction.iloc[i-1] if i > 1 else 1
        if direction.iloc[i] == 1:
            lower.iloc[i] = max(lower.iloc[i], lower.iloc[i-1]) if i > 1 else lower.iloc[i]
            supertrend.iloc[i] = lower.iloc[i]
        else:
            upper.iloc[i] = min(upper.iloc[i], upper.iloc[i-1]) if i > 1 else upper.iloc[i]
            supertrend.iloc[i] = upper.iloc[i]
    df['supertrend'] = supertrend
    df['st_dir'] = direction
    return df

def run_strategy():
    position = 0
    print(f"Starting {STRATEGY_NAME}...")
    while True:
        try:
            if not is_market_hours():
                print(f"[{datetime.now():%H:%M:%S}] Market closed. Sleeping 60s...")
                time.sleep(60)
                continue
            df = get_data(SYMBOL, EXCHANGE, INTERVAL)
            if df is None or df.empty or len(df) < 30:
                print("Insufficient data. Retrying in 30s...")
                time.sleep(30)
                continue
            df = calc_supertrend(df)
            dir_now = df['st_dir'].iloc[-1]
            dir_prev = df['st_dir'].iloc[-2]
            buy_signal = (dir_now == 1) and (dir_prev != 1)
            sell_signal = (dir_now == -1) and (dir_prev != -1)
            close = df['close'].iloc[-1]
            print(f"[{datetime.now():%H:%M:%S}] Close={close:.2f} ST_Dir={dir_now} Prev={dir_prev} Pos={position}")
            if buy_signal and position <= 0:
                position = QUANTITY
                resp = client.placesmartorder(strategy=STRATEGY_NAME, symbol=SYMBOL, action="BUY",
                    exchange=EXCHANGE, price_type="MARKET", product=PRODUCT,
                    quantity=QUANTITY, position_size=position)
                print(f"  >>> BUY (ST Flip Bullish): {resp}")
            elif sell_signal and position >= 0:
                position = -QUANTITY
                resp = client.placesmartorder(strategy=STRATEGY_NAME, symbol=SYMBOL, action="SELL",
                    exchange=EXCHANGE, price_type="MARKET", product=PRODUCT,
                    quantity=QUANTITY, position_size=position)
                print(f"  >>> SELL (ST Flip Bearish): {resp}")
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)
        time.sleep(60)

if __name__ == "__main__":
    run_strategy()
'''
    strategies.append(('strategy_03_supertrend_RELIANCE.py', s03))
    
    # ============================================================
    # Strategy 04: BB + RSI Mean Reversion - SBIN 5m
    # ============================================================
    s04 = HEADER + '''
STRATEGY_NAME = "Yukti_bb_rsi_SBIN_5m"
SYMBOL = "SBIN"
EXCHANGE = "NSE"
PRODUCT = "MIS"
QUANTITY = 1
INTERVAL = "5m"

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))

def run_strategy():
    position = 0
    print(f"Starting {STRATEGY_NAME}...")
    while True:
        try:
            if not is_market_hours():
                print(f"[{datetime.now():%H:%M:%S}] Market closed. Sleeping 60s...")
                time.sleep(60)
                continue
            df = get_data(SYMBOL, EXCHANGE, INTERVAL)
            if df is None or df.empty or len(df) < 30:
                print("Insufficient data. Retrying in 30s...")
                time.sleep(30)
                continue
            # Bollinger Bands (20, 2)
            df['bb_mid'] = df['close'].rolling(20).mean()
            df['bb_std'] = df['close'].rolling(20).std()
            df['bb_upper'] = df['bb_mid'] + 2 * df['bb_std']
            df['bb_lower'] = df['bb_mid'] - 2 * df['bb_std']
            df['rsi'] = calc_rsi(df['close'])
            close = df['close'].iloc[-1]
            bb_upper = df['bb_upper'].iloc[-1]
            bb_lower = df['bb_lower'].iloc[-1]
            rsi = df['rsi'].iloc[-1]
            # Mean reversion: touch lower band + oversold RSI
            buy_signal = (close <= bb_lower) and (rsi < 35)
            sell_signal = (close >= bb_upper) and (rsi > 65)
            print(f"[{datetime.now():%H:%M:%S}] Close={close:.2f} BB_L={bb_lower:.2f} BB_U={bb_upper:.2f} RSI={rsi:.1f} Pos={position}")
            if buy_signal and position <= 0:
                position = QUANTITY
                resp = client.placesmartorder(strategy=STRATEGY_NAME, symbol=SYMBOL, action="BUY",
                    exchange=EXCHANGE, price_type="MARKET", product=PRODUCT,
                    quantity=QUANTITY, position_size=position)
                print(f"  >>> BUY (BB Lower + RSI Oversold): {resp}")
            elif sell_signal and position >= 0:
                position = -QUANTITY
                resp = client.placesmartorder(strategy=STRATEGY_NAME, symbol=SYMBOL, action="SELL",
                    exchange=EXCHANGE, price_type="MARKET", product=PRODUCT,
                    quantity=QUANTITY, position_size=position)
                print(f"  >>> SELL (BB Upper + RSI Overbought): {resp}")
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)
        time.sleep(30)

if __name__ == "__main__":
    run_strategy()
'''
    strategies.append(('strategy_04_bb_rsi_SBIN.py', s04))
    
    # ============================================================
    # Strategy 05: MACD + Volume - TCS 15m
    # ============================================================
    s05 = HEADER + '''
STRATEGY_NAME = "Yukti_macd_volume_TCS_15m"
SYMBOL = "TCS"
EXCHANGE = "NSE"
PRODUCT = "MIS"
QUANTITY = 1
INTERVAL = "15m"

def run_strategy():
    position = 0
    print(f"Starting {STRATEGY_NAME}...")
    while True:
        try:
            if not is_market_hours():
                print(f"[{datetime.now():%H:%M:%S}] Market closed. Sleeping 60s...")
                time.sleep(60)
                continue
            df = get_data(SYMBOL, EXCHANGE, INTERVAL)
            if df is None or df.empty or len(df) < 35:
                print("Insufficient data. Retrying in 30s...")
                time.sleep(30)
                continue
            # MACD (12,26,9)
            df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
            df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = df['ema12'] - df['ema26']
            df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['vol_avg'] = df['volume'].rolling(20).mean()
            macd_now = df['macd'].iloc[-1]
            sig_now = df['signal'].iloc[-1]
            macd_prev = df['macd'].iloc[-2]
            sig_prev = df['signal'].iloc[-2]
            vol_now = df['volume'].iloc[-1]
            vol_avg = df['vol_avg'].iloc[-1]
            vol_surge = vol_now > 1.5 * vol_avg
            # Crossover detection
            bull_cross = (macd_prev <= sig_prev) and (macd_now > sig_now)
            bear_cross = (macd_prev >= sig_prev) and (macd_now < sig_now)
            buy_signal = bull_cross and vol_surge
            sell_signal = bear_cross and vol_surge
            print(f"[{datetime.now():%H:%M:%S}] MACD={macd_now:.3f} Sig={sig_now:.3f} Vol={vol_now:.0f}(avg={vol_avg:.0f}) Pos={position}")
            if buy_signal and position <= 0:
                position = QUANTITY
                resp = client.placesmartorder(strategy=STRATEGY_NAME, symbol=SYMBOL, action="BUY",
                    exchange=EXCHANGE, price_type="MARKET", product=PRODUCT,
                    quantity=QUANTITY, position_size=position)
                print(f"