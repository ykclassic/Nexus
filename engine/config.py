# engine/config.py

import os

SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "ADA/USDT",
    "XRP/USDT", "DOGE/USDT", "SUI/USDT", "LTC/USDT", "LINK/USDT"
]

TIMEFRAME = "5m"

MIN_CONFIDENCE = 0.82
MAX_THREADS = 4

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "trading.db")

DISCORD_WEBHOOK_ENV = "DISCORD_WEBHOOK"
