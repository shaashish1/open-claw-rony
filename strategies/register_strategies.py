#!/usr/bin/env python3
"""
Register 10 Python strategies in OpenAlgo DB
"""
import sqlite3
from datetime import datetime
import uuid

DB_PATH = '/app/db/openalgo.db'
USER_ID = 'ashish.sharma14@gmail.com'

strategies = [
    {
        'name': 'Yukti_vwap_rsi_ICICIBANK_5m',
        'description': 'VWAP + RSI Scalper | ICICIBANK | 5m | MIS',
    },
    {
        'name': 'Yukti_ema_ribbon_HDFCBANK_5m',
        'description': 'EMA Ribbon | HDFCBANK | 5m | MIS',
    },
    {
        'name': 'Yukti_supertrend_RELIANCE_15m',
        'description': 'Supertrend ATR | RELIANCE | 15m | MIS',
    },
    {
        'name': 'Yukti_bb_rsi_SBIN_5m',
        'description': 'BB + RSI Mean Reversion | SBIN | 5m | MIS',
    },
    {
        'name': 'Yukti_macd_volume_TCS_15m',
        'description': 'MACD + Volume | TCS | 15m | MIS',
    },
    {
        'name': 'Yukti_orb_NIFTY_15m',
        'description': 'Opening Range Breakout | NIFTY | 15m | MIS',
    },
    {
        'name': 'Yukti_stoch_rsi_macd_BAJFINANCE_5m',
        'description': 'StochRSI + MACD | BAJFINANCE | 5m | MIS',
    },
    {
        'name': 'Yukti_donchian_LT_5m',
        'description': 'Donchian Channel | LT | 5m | MIS',
    },
    {
        'name': 'Yukti_ichimoku_INFY_15m',
        'description': 'Ichimoku Cloud | INFY | 15m | MIS',
    },
    {
        'name': 'Yukti_adx_di_AXISBANK_5m',
        'description': 'ADX + DI Trend | AXISBANK | 5m | MIS',
    },
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Check existing columns
c.execute("PRAGMA table_info(strategies)")
cols = [r[1] for r in c.fetchall()]
print("Strategy table columns:", cols)

# Check existing strategies
c.execute("SELECT name FROM strategies WHERE platform='python'")
existing = {r[0] for r in c.fetchall()}
print(f"Existing Python strategies: {existing}")

inserted = 0
skipped = 0
for s in strategies:
    if s['name'] in existing:
        print(f"  SKIP (exists): {s['name']}")
        skipped += 1
        continue
    
    webhook_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    try:
        # Try with all common columns
        if 'trading_mode' in cols and 'squareoff_time' in cols:
            c.execute("""INSERT OR IGNORE INTO strategies 
                        (name, webhook_id, user_id, platform, is_active, is_intraday, 
                         trading_mode, start_time, end_time, squareoff_time, created_at)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                     (s['name'], webhook_id, USER_ID, 'python', 1, 1,
                      'BOTH', '09:15', '15:00', '15:15', now))
        elif 'trading_mode' in cols:
            c.execute("""INSERT OR IGNORE INTO strategies 
                        (name, webhook_id, user_id, platform, is_active, is_intraday, 
                         trading_mode, start_time, end_time, created_at)
                        VALUES (?,?,?,?,?,?,?,?,?,?)""",
                     (s['name'], webhook_id, USER_ID, 'python', 1, 1,
                      'BOTH', '09:15', '15:00', now))
        else:
            c.execute("""INSERT OR IGNORE INTO strategies 
                        (name, webhook_id, user_id, platform, is_active, created_at)
                        VALUES (?,?,?,?,?,?)""",
                     (s['name'], webhook_id, USER_ID, 'python', 1, now))
        
        inserted += 1
        print(f"  OK: {s['name']}")
    except Exception as e:
        print(f"  ERROR inserting {s['name']}: {e}")

conn.commit()
conn.close()

print(f"\nDone. Inserted={inserted} Skipped={skipped}")
