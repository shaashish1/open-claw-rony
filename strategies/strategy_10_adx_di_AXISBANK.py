#!/usr/bin/env python3
"""Strategy 10: ADX + DI Trend — AXISBANK 5m | MIS | Qty:1"""
from openalgo import api
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import os

api_key = os.getenv('OPENALGO_API_KEY', '')
host = os.getenv('HOST_SERVER', 'http://127.0.0.1:5000')
ws_url = os.getenv('WEBSOCKET_URL', 'ws://127.0.0.1:8765')
strategy = "Yukti_adx_di_trend_AXISBANK_5m"
symbol = 'AXISBANK'; exchange = 'NSE'; product = 'MIS'; quantity = 1; interval = '5m'
client = api(api_key=api_key, host=host, ws_url=ws_url)

def is_market_hours():
    now = datetime.now()
    if now.weekday() >= 5: return False
    return now.replace(hour=9,minute=15,second=0,microsecond=0) <= now <= now.replace(hour=15,minute=15,second=0,microsecond=0)

def calc_adx(df, period=14):
    h, l, c = df['high'], df['low'], df['close']
    tr = pd.concat([h-l, abs(h-c.shift()), abs(l-c.shift())], axis=1).max(axis=1)
    plus_dm = (h.diff()).clip(lower=0)
    minus_dm = (-l.diff()).clip(lower=0)
    mask = plus_dm < minus_dm; plus_dm[mask] = 0
    mask2 = minus_dm <= plus_dm; minus_dm[mask2] = 0
    atr = tr.rolling(period).mean()
    plus_di = 100 * plus_dm.rolling(period).mean() / atr
    minus_di = 100 * minus_dm.rolling(period).mean() / atr
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)
    adx = dx.rolling(period).mean()
    return adx, plus_di, minus_di

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
            if df is None or df.empty or len(df) < 35:
                time.sleep(30); continue

            adx, pdi, mdi = calc_adx(df)
            adx_val = adx.iloc[-2]
            pdi2 = pdi.iloc[-2]; mdi2 = mdi.iloc[-2]
            pdi3 = pdi.iloc[-3]; mdi3 = mdi.iloc[-3]

            strong_trend = adx_val > 25
            buy_signal = strong_trend and (pdi2 > mdi2) and (pdi3 <= mdi3)
            sell_signal = strong_trend and (mdi2 > pdi2) and (mdi3 <= pdi3)

            print(f"[{strategy}] ADX={adx_val:.1f} +DI={pdi2:.1f} -DI={mdi2:.1f} Pos={position}")

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
