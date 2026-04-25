#!/usr/bin/env python3
"""Strategy 09: Ichimoku Cloud — INFY 15m | MIS | Qty:1"""
from openalgo import api
import pandas as pd
import time
from datetime import datetime, timedelta
import os

api_key = os.getenv('OPENALGO_API_KEY', '')
host = os.getenv('HOST_SERVER', 'http://127.0.0.1:5000')
ws_url = os.getenv('WEBSOCKET_URL', 'ws://127.0.0.1:8765')
strategy = "Yukti_ichimoku_rsi_INFY_15m"
symbol = 'INFY'; exchange = 'NSE'; product = 'MIS'; quantity = 1; interval = '15m'
client = api(api_key=api_key, host=host, ws_url=ws_url)

def is_market_hours():
    now = datetime.now()
    if now.weekday() >= 5: return False
    return now.replace(hour=9,minute=15,second=0,microsecond=0) <= now <= now.replace(hour=15,minute=15,second=0,microsecond=0)

def ichimoku(df):
    h, l = df['high'], df['low']
    tenkan = (h.rolling(9).max() + l.rolling(9).min()) / 2
    kijun = (h.rolling(26).max() + l.rolling(26).min()) / 2
    spanA = ((tenkan + kijun) / 2).shift(26)
    spanB = ((h.rolling(52).max() + l.rolling(52).min()) / 2).shift(26)
    return tenkan, kijun, spanA, spanB

def run():
    position = 0
    print(f"[{strategy}] Starting...")
    while True:
        try:
            if not is_market_hours():
                time.sleep(60); continue
            end = datetime.now().strftime("%Y-%m-%d")
            start = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
            df = client.history(symbol=symbol, exchange=exchange, interval=interval, start_date=start, end_date=end)
            if df is None or df.empty or len(df) < 60:
                time.sleep(60); continue

            tenkan, kijun, spanA, spanB = ichimoku(df)
            price = df['close'].iloc[-2]
            t = tenkan.iloc[-2]; k = kijun.iloc[-2]
            sA = spanA.iloc[-2]; sB = spanB.iloc[-2]
            cloud_top = max(sA, sB); cloud_bot = min(sA, sB)

            buy_signal = (price > cloud_top) and (t > k) and (tenkan.iloc[-3] <= kijun.iloc[-3])
            sell_signal = (price < cloud_bot) and (t < k) and (tenkan.iloc[-3] >= kijun.iloc[-3])

            print(f"[{strategy}] Price={price:.2f} CloudTop={cloud_top:.2f} T={t:.2f} K={k:.2f} Pos={position}")

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
        time.sleep(60)

if __name__ == "__main__":
    run()
