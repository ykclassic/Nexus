# Nexus/engine/config.py

SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "ADA/USDT",
    "XRP/USDT", "DOGE/USDT", "SUI/USDT", "LTC/USDT", "LINK/USDT"
]

TIMEFRAME = "5m"

# Quality > Quantity
MIN_CONFIDENCE = 0.82

# Thread control (GitHub safe)
MAX_THREADS = 4

# Database path (absolute-safe)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "trading.db")

# Discord webhook env variable
DISCORD_WEBHOOK_ENV = "DISCORD_WEBHOOK"
