# engine/config.py

import os

# =========================
# PATH CONFIGURATION
# =========================

# Project root: Nexus/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data directory
DATA_DIR = os.path.join(BASE_DIR, "data")

# Database path
DB_PATH = os.path.join(DATA_DIR, "trading.db")

# Ensure data folder exists
os.makedirs(DATA_DIR, exist_ok=True)

# =========================
# TRADING CONFIG
# =========================

SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "BNB/USDT",
    "ADA/USDT",
    "XRP/USDT",
    "DOGE/USDT",
    "SUI/USDT",
    "LTC/USDT",
    "LINK/USDT",
]

# Timeframe for signals
TIMEFRAME = "5m"

# Elite signal threshold (quality > quantity)
MIN_CONFIDENCE = 0.82

# Thread control (GitHub Actions safe)
MAX_THREADS = 4

# =========================
# DISCORD CONFIG
# =========================

DISCORD_WEBHOOK_ENV = "DISCORD_WEBHOOK"
DISCORD_WEBHOOK = os.getenv(DISCORD_WEBHOOK_ENV, "")

# =========================
# ENGINE LIMITS (GITHUB SAFE)
# =========================

MAX_RUNTIME_SECONDS = 240  # GitHub timeout alignment
MAX_SIGNALS_PER_RUN = 3    # quality > quantity
