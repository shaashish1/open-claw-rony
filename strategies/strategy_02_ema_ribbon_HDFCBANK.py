#!/usr/bin/env python3
"""Strategy 02: EMA Ribbon — HDFCBANK 5m | MIS | Qty:1"""
from openalgo import api
import pandas as pd
import time
from datetime import datetime, timedelta
import os

api_key = os.getenv('OPENALGO_API_KEY', '')
host = os.getenv('HOST_SERVER', 'http://127.0.0.1:5000')
ws_url = os.getenv('WEBSOCKET_URL', 'ws://127.0.0.1:8765')
strategy = "Yukti_ema_ribbon_HDFCBANK_5m"
symbol = 'HDFCBANK'; exchange = 'NSE'; product = 'MIS'; quantity = 1; interval = '5m'
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

            c = df['close']
            e5 = c.ewm(span=5, adjust=False).mean()
            e9 = c.ewm(span=9, adjust=False).mean()
            e21 = c.ewm(span=21, adjust=False).mean()

            buy_signal = (e5.iloc[-2] > e9.iloc[-2] > e21.iloc[-2]) and \
                         (e5.iloc[-2] > e5.iloc[-3]) and (e9.iloc[-2] > e9.iloc[-3])
            sell_signal = (e5.iloc[-2] < e9.iloc[-2] < e21.iloc[-2]) and \
                          (e5.iloc[-2] < e5.iloc[-3]) and (e9.iloc[-2] < e9.iloc[-3])

            print(f"[{strategy}] E5={e5.iloc[-2]:.2f} E9={e9.iloc[-2]:.2f} E21={e21.iloc[-2]:.2f} Pos={position}")

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
