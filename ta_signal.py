import ccxt
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from telegram import Bot

# === BOT NASTROYKALARI ===
TOKEN = '7772940211:AAEaD3pqOYYUxjdRZAnEDM7AlSuXRId_hs0'
CHAT_ID = '7595780336'
bot = Bot(token=TOKEN)

# === BIRJA ULANISHI ===
exchange = ccxt.binance({
    'options': {'defaultType': 'future'}
})

symbol = 'BTC/USDT'
timeframe = '1h'
limit = 100

ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# === TEXNIK INDIKATORLAR ===
df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()
df['ema20'] = EMAIndicator(close=df['close'], window=20).ema_indicator()
df['ema50'] = EMAIndicator(close=df['close'], window=50).ema_indicator()
macd = MACD(close=df['close'])
df['macd'] = macd.macd()
df['macd_signal'] = macd.macd_signal()

# === SO‘NGGI CANDLE — ANALIZ ===
last = df.iloc[-1]
close = last['close']
rsi = last['rsi']
ema20 = last['ema20']
ema50 = last['ema50']
macd_val = last['macd']
macd_sig = last['macd_signal']

print(f"\n📊 Close: ${close:.2f} | RSI: {rsi:.2f} | EMA20: {ema20:.2f} | EMA50: {ema50:.2f} | MACD: {macd_val:.2f} | Signal: {macd_sig:.2f}")

# === ENTRY SIGNAL YUBORISH ===
if rsi < 30 and ema20 > ema50 and macd_val > macd_sig:
    message = f"📈 BUY Signal\nPrice: ${close:.2f}\nRSI: {rsi:.2f}\nEMA20 > EMA50\nMACD bullish"
    print("✅ BUY signal found, sending to Telegram...")
    bot.send_message(chat_id=CHAT_ID, text=message)

elif rsi > 70 and ema20 < ema50 and macd_val < macd_sig:
    message = f"📉 SELL Signal\nPrice: ${close:.2f}\nRSI: {rsi:.2f}\nEMA20 < EMA50\nMACD bearish"
    print("❌ SELL signal found, sending to Telegram...")
    bot.send_message(chat_id=CHAT_ID, text=message)

else:
    print("⏳ No clear signal found.")
