import ccxt
import numpy as np
import pandas as pd
import time

# Инициализация API Binance
api_key = 'YOUR_API_KEY'
secret_key = 'YOUR_SECRET_KEY'
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': secret_key,
    'timeout': 30000,
    'enableRateLimit': True
})

symbol = 'BTC/USDT'
timeframe = '1h'
ema_short = 20
ema_long = 50
rsi_period = 14
leverage = 10
balance_percent = 0.1

def get_data():
    bars = exchange.fetch_ohlcv(symbol, timeframe)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['ema_short'] = df['close'].ewm(span=ema_short).mean()
    df['ema_long'] = df['close'].ewm(span=ema_long).mean()
    delta = df['close'].diff()
    gain, loss = delta.copy(), delta.copy()
    gain[gain < 0] = 0
    loss[loss > 0] = 0
    avg_gain = gain.rolling(window=rsi_period).mean()
    avg_loss = -loss.rolling(window=rsi_period).mean()
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))
    return df

def place_order(side, amount, price):
    if side == 'buy':
        order = exchange.create_market_buy_order(symbol, amount)
    elif side == 'sell':
        order = exchange.create_market_sell_order(symbol, amount)
    return order

while True:
    df = get_data()
    ema_short_current = df['ema_short'].iloc[-1]
    ema_long_current = df['ema_long'].iloc[-1]
    rsi_current = df['rsi'].iloc[-1]
    balance = exchange.fetch_balance()
    usdt_balance = balance['USDT']['free']

    if ema_short_current > ema_long_current and rsi_current < 30:
        # Покупка
        order_side = 'buy'
        amount = (usdt_balance * balance_percent) / df['close'].iloc[-1]
        order = place_order(order_side, amount
