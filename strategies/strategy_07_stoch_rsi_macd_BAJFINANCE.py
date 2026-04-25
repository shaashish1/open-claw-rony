#!/usr/bin/env python3
"""Strategy 07: Stoch RSI + MACD — BAJFINANCE 5m | MIS | Qty:1"""
from openalgo import api
import pandas as pd
import time
from datetime import datetime, timedelta
import os

api_key = os.getenv('OPENALGO_API_KEY', '')
host = os.getenv('HOST_SERVER', 'http://127.0.0.1:5000')
ws_url = os.getenv('WEBSOCKET_URL', 'ws://127.0.0.1:8765')
strategy = "Yukti_stochastic_momentum_BAJFINANCE_5m"
symbol = 'BAJFINANCE'; exchange = 'NSE'; product = 'MIS'; quantity = 1; interval = '5m'
client = api(api_key=api_key, host=host, ws_url=ws_url)

def is_market_hours():
    now = datetime.now()
    if now.weekday() >= 5: return False
    return now.replace(hour=9,minute=15,second=0,microsecond=0) <= now <= now.replace(hour=15,minute=15,second=0,microsecond=0)

def stoch_rsi(close, period=14, smooth_k=3, smooth_d=3):
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rsi = 100 - (100 / (1 + gain/loss))
    rsi_min = rsi.rolling(period).min()
    rsi_max = rsi.rolling(period).max()
    k = 100 * (rsi - rsi_min) / (rsi_max - rsi_min + 1e-10)
    k = k.rolling(smooth_k).mean()
    d = k.rolling(smooth_d).mean()
    return k, d

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
            if df is None or df.empty or len(df) < 40:
                time.sleep(30); continue

            close = df['close']
            k, d = stoch_rsi(close)
            ema12 = close.ewm(span=12, adjust=False).mean()
            ema26 = close.ewm(span=26, adjust=False).mean()
            macd = ema12 - ema26

            k2 = k.iloc[-2]; d2 = d.iloc[-2]
            k3 = k.iloc[-3]; d3 = d.iloc[-3]

            buy_signal = (k2 > d2) and (k3 <= d3) and (k3 < 20) and (macd.iloc[-2] > 0)
            sell_signal = (k2 < d2) and (k3 >= d3) and (k3 > 80) and (macd.iloc[-2] < 0)

            print(f"[{strategy}] K={k2:.1f} D={d2:.1f} MACD={macd.iloc[-2]:.2f} Pos={position}")

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
