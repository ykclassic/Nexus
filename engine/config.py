# engine/config.py

SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "ADA/USDT",
    "XRP/USDT", "DOGE/USDT", "SUI/USDT", "LTC/USDT", "LINK/USDT"
]

TIMEFRAME = "5m"

# Elite signal threshold (quality > quantity)
MIN_CONFIDENCE = 0.82

# Thread control (GitHub-safe)
MAX_THREADS = 4

# Database path
DB_PATH = "data/trading.db"

# Discord webhook env variable
DISCORD_WEBHOOK_ENV = "DISCORD_WEBHOOK"
