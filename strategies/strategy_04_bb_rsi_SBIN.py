#!/usr/bin/env python3
"""Strategy 04: BB + RSI Mean Reversion — SBIN 5m | MIS | Qty:1"""
from openalgo import api
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import os

api_key = os.getenv('OPENALGO_API_KEY', '')
host = os.getenv('HOST_SERVER', 'http://127.0.0.1:5000')
ws_url = os.getenv('WEBSOCKET_URL', 'ws://127.0.0.1:8765')
strategy = "Yukti_bb_rsi_SBIN_5m"
symbol = 'SBIN'; exchange = 'NSE'; product = 'MIS'; quantity = 1; interval = '5m'
client = api(api_key=api_key, host=host, ws_url=ws_url)

def is_market_hours():
    now = datetime.now()
    if now.weekday() >= 5: return False
    return now.replace(hour=9,minute=15,second=0,microsecond=0) <= now <= now.replace(hour=15,minute=15,second=0,microsecond=0)

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

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

            close = df['close']
            mid = close.rolling(20).mean()
            std = close.rolling(20).std()
            upper_bb = mid + 2 * std
            lower_bb = mid - 2 * std
            rsi = calc_rsi(close)

            price = close.iloc[-2]
            rsi_val = rsi.iloc[-2]
            low_bb = lower_bb.iloc[-2]
            up_bb = upper_bb.iloc[-2]

            buy_signal = (price <= low_bb) and (rsi_val < 35)
            sell_signal = (price >= up_bb) and (rsi_val > 65)

            print(f"[{strategy}] Price={price:.2f} LBB={low_bb:.2f} UBB={up_bb:.2f} RSI={rsi_val:.1f} Pos={position}")

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
