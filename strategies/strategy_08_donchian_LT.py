#!/usr/bin/env python3
"""Strategy 08: Donchian Channel Breakout — LT 5m | MIS | Qty:1"""
from openalgo import api
import pandas as pd
import time
from datetime import datetime, timedelta
import os

api_key = os.getenv('OPENALGO_API_KEY', '')
host = os.getenv('HOST_SERVER', 'http://127.0.0.1:5000')
ws_url = os.getenv('WEBSOCKET_URL', 'ws://127.0.0.1:8765')
strategy = "Yukti_donchian_volume_breakout_LT_5m"
symbol = 'LT'; exchange = 'NSE'; product = 'MIS'; quantity = 1; interval = '5m'
client = api(api_key=api_key, host=host, ws_url=ws_url)

def is_market_hours():
    now = datetime.now()
    if now.weekday() >= 5: return False
    return now.replace(hour=9,minute=15,second=0,microsecond=0) <= now <= now.replace(hour=15,minute=15,second=0,microsecond=0)

def run():
    position = 0
    print(f"[{strategy}] Starting...")
    while True:
        try:
            if not is_market_hours():
                time.sleep(60); continue
            end = datetime.now().strftime("%Y-%m-%d")
            start = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
            df = client.history(symbol=symbol, exchange=exchange, interval=interval, start_date=start, end_date=end)
            if df is None or df.empty or len(df) < 30:
                time.sleep(30); continue

            period = 20
            upper = df['high'].rolling(period).max()
            lower = df['low'].rolling(period).min()
            vol_avg = df['volume'].rolling(period).mean()

            price = df['close'].iloc[-2]
            up = upper.iloc[-3]  # use -3 to avoid look-ahead
            lo = lower.iloc[-3]
            vol = df['volume'].iloc[-2]
            avg_vol = vol_avg.iloc[-2]
            vol_surge = vol > 1.5 * avg_vol

            buy_signal = (price > up) and vol_surge
            sell_signal = (price < lo) and vol_surge

            print(f"[{strategy}] Price={price:.2f} DC_H={up:.2f} DC_L={lo:.2f} Pos={position}")

            if buy_signal and position <= 0:
                position = quantity
                resp = client.placesmartorder(strategy=strategy, symbol=symbol, action="BUY",
                    exchange=exchange, price_type="MARKET", product=product, quantity=quantity, position_size=position)
                print(f"[{strategy}] BUY: {resp}")
            elif sell_signal and position >= 0:
                position = -quantity
                resp = client.placesmartorder(strategy=strategy, symbol=symbol, action="SELL",
                    exchange=exchange, price_type="MARKET", product=product, quantity=quantity, position_size=position)
                print(f"[{strategy}] SELL: {resp}")
        except Exception as e:
            print(f"[{strategy}] Error: {e}")
        time.sleep(30)

if __name__ == "__main__":
    run()
