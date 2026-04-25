#!/usr/bin/env python3
"""Strategy 06: Opening Range Breakout — NIFTY 15m | MIS | Qty:1"""
from openalgo import api
import pandas as pd
import time
from datetime import datetime, timedelta
import os

api_key = os.getenv('OPENALGO_API_KEY', '')
host = os.getenv('HOST_SERVER', 'http://127.0.0.1:5000')
ws_url = os.getenv('WEBSOCKET_URL', 'ws://127.0.0.1:8765')
strategy = "Yukti_orb_scalper_NIFTY_15m"
symbol = 'NIFTY'; exchange = 'NSE'; product = 'MIS'; quantity = 1; interval = '15m'
client = api(api_key=api_key, host=host, ws_url=ws_url)

def is_market_hours():
    now = datetime.now()
    if now.weekday() >= 5: return False
    return now.replace(hour=9,minute=15,second=0,microsecond=0) <= now <= now.replace(hour=15,minute=15,second=0,microsecond=0)

def run():
    position = 0
    orb_high = None
    orb_low = None
    orb_set = False
    last_day = None
    print(f"[{strategy}] Starting...")
    while True:
        try:
            if not is_market_hours():
                orb_high = orb_low = None; orb_set = False
                time.sleep(60); continue

            end = datetime.now().strftime("%Y-%m-%d")
            start = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
            df = client.history(symbol=symbol, exchange=exchange, interval=interval, start_date=start, end_date=end)
            if df is None or df.empty or len(df) < 5:
                time.sleep(60); continue

            today = datetime.now().date()
            if last_day != today:
                last_day = today
                orb_set = False
                position = 0

            # Set ORB from first candle of today (9:15 candle)
            if not orb_set and datetime.now().hour >= 9 and datetime.now().minute >= 30:
                today_df = df[df.index.date == today] if hasattr(df.index[0], 'date') else df.tail(10)
                if len(today_df) >= 1:
                    orb_high = today_df['high'].iloc[0]
                    orb_low = today_df['low'].iloc[0]
                    orb_set = True
                    print(f"[{strategy}] ORB set: High={orb_high} Low={orb_low}")

            if not orb_set:
                time.sleep(60); continue

            price = df['close'].iloc[-2]
            vol = df['volume'].iloc[-2]
            avg_vol = df['volume'].rolling(10).mean().iloc[-2]
            vol_surge = vol > 1.2 * avg_vol

            buy_signal = (price > orb_high) and vol_surge
            sell_signal = (price < orb_low) and vol_surge

            print(f"[{strategy}] Price={price:.2f} ORB_H={orb_high} ORB_L={orb_low} Pos={position}")

            if buy_signal and position <= 0:
                position = quantity
                resp = client.placesmartorder(strategy=strategy, symbol=symbol, action="BUY",
                    exchange=exchange, price_type="MARKET", product=product, quantity=quantity, position_size=position)
                print(f"[{strategy}] BUY breakout: {resp}")
            elif sell_signal and position >= 0:
                position = -quantity
                resp = client.placesmartorder(strategy=strategy, symbol=symbol, action="SELL",
                    exchange=exchange, price_type="MARKET", product=product, quantity=quantity, position_size=position)
                print(f"[{strategy}] SELL breakdown: {resp}")
        except Exception as e:
            print(f"[{strategy}] Error: {e}")
        time.sleep(60)

if __name__ == "__main__":
    run()
