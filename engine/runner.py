import sqlite3
from concurrent.futures import ThreadPoolExecutor
from engine.elite_logger import log_event, log_error
from engine.discord_alert import send_discord_alert
from engine.trade_lifecycle import register_trade
from engine.intelligence.feature_engine import compute_features
from engine.intelligence.signal_filters import basic_filters
from engine.intelligence.signal_scoring import score_signal
from engine.intelligence.signal_ranker import select_elite_signals
from engine.intelligence.signal_validator import validate_trade

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
DB_FILE = "data/trading.db"


def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)


def fetch_market_data(symbol):
    # TODO: replace with real exchange fetch
    import random
    return {
        "entry": round(random.uniform(100, 200), 2),
        "sl": round(random.uniform(90, 99), 2),
        "tp": round(random.uniform(210, 250), 2),
        "direction": "LONG"
    }


def process_symbol(symbol):
    try:
        conn = get_connection()

        # Dummy OHLCV data (replace with real)
        import pandas as pd
        import numpy as np
        df = pd.DataFrame({
            "close": np.random.rand(100),
            "high": np.random.rand(100),
            "low": np.random.rand(100),
            "volume": np.random.rand(100)
        })

        features = compute_features(df)

        if not basic_filters(features):
            return None

        market = fetch_market_data(symbol)

        if not validate_trade(market["entry"], market["sl"], market["tp"]):
            return None

        confidence = score_signal(features, market["direction"])

        signal = {
            "symbol": symbol,
            "direction": market["direction"],
            "entry": market["entry"],
            "sl": market["sl"],
            "tp": market["tp"],
            "confidence": confidence
        }

        register_trade(conn, signal)

        conn.close()
        return signal

    except Exception as e:
        log_error(f"Symbol processing error {symbol}: {str(e)}")
        return None


def run_engine():
    log_event("Nexus Engine Started")

    signals = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(process_symbol, SYMBOLS)

    for s in results:
        if s:
            signals.append(s)

    elite_signals = select_elite_signals(signals, limit=1)

    for signal in elite_signals:
        log_event(f"ELITE SIGNAL: {signal}")
        send_discord_alert(signal)

    log_event(f"Signals generated: {len(signals)}, Elite: {len(elite_signals)}")
