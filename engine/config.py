import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "trading.db")

SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
TIMEFRAME = "1h"

MIN_CONFIDENCE = 0.75
MAX_THREADS = 5

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", "")
