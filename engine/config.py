# engine/config.py

SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "ADA/USDT",
    "XRP/USDT", "DOGE/USDT", "SUI/USDT", "LTC/USDT", "LINK/USDT"
]

MIN_CONFIDENCE = 0.6
MAX_THREADS = 4
TIMEFRAME = "1h"
DISCORD_WEBHOOK = "YOUR_DISCORD_WEBHOOK_HERE"  # Or use environment variable
DB_PATH = "data/trading.db"
