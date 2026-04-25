#!/usr/bin/env python3
"""
Strategy 01: VWAP + RSI Scalper — ICICIBANK 5m
Buy: Price > VWAP AND RSI crosses above 40
Sell: Price < VWAP AND RSI crosses below 60
Product: MIS | Qty: 1 | Exchange: NSE
"""
from openalgo import api
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import os

api_key = os.getenv('OPENALGO_API_KEY', '')
host = os.getenv('HOST_SERVER', 'http://127.0.0.1:5000')
ws_url = os.getenv('WEBSOCKET_URL', 'ws://127.0.0.1:8765')

strategy = "Yukti_vwap_rsi_ICICIBANK_5m"
symbol = 'ICICIBANK'
exchange = 'NSE'
product = 'MIS'
quantity = 1
interval = '5m'

client = api(api_key=api_key, host=host, ws_url=ws_url)

def is_market_hours():
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    open_t = now.replace(hour=9, minute=15, second=0, microsecond=0)
    close_t = now.replace(hour=15, minute=15, second=0, microsecond=0)
    return open_t <= now <= close_t

def calc_vwap(df):
    df = df.copy()
    df['tp'] = (df['high'] + df['low'] + df['close']) / 3
    df['tpv'] = df['tp'] * df['volume']
    df['cum_tpv'] = df['tpv'].cumsum()
    df['cum_vol'] = df['volume'].cumsum()
    df['vwap'] = df['cum_tpv'] / df['cum_vol']
    return df['vwap']

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
                print(f"[{strategy}] Market closed. Waiting...")
                time.sleep(60)
                continue

            end = datetime.now().strftime("%Y-%m-%d")
            start = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
            df = client.history(symbol=symbol, exchange=exchange, interval=interval, start_date=start, end_date=end)

            if df is None or df.empty or len(df) < 30:
                time.sleep(30)
                continue

            vwap = calc_vwap(df)
            rsi = calc_rsi(df['close'])

            price = df['close'].iloc[-2]
            prev_price = df['close'].iloc[-3]
            vwap_val = vwap.iloc[-2]
            rsi_val = rsi.iloc[-2]
            rsi_prev = rsi.iloc[-3]

            buy_signal = (price > vwap_val) and (rsi_val > 40) and (rsi_prev <= 40)
            sell_signal = (price < vwap_val) and (rsi_val < 60) and (rsi_prev >= 60)

            print(f"[{strategy}] Price={price:.2f} VWAP={vwap_val:.2f} RSI={rsi_val:.2f} Pos={position}")

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
