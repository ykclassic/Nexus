# engine/trade_lifecycle.py

from engine.db import get_connection
from engine.config import MIN_CONFIDENCE
from engine.logger import log_info, log_error

def create_signal(signal: dict):
    try:
        if signal["confidence"] < MIN_CONFIDENCE:
            return None

        conn = get_connection()
        c = conn.cursor()

        c.execute("""
            INSERT INTO signals (symbol, timeframe, direction, strategy, price, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            signal["symbol"],
            signal["timeframe"],
            signal["direction"],
            signal["strategy"],
            signal["price"],
            signal["confidence"]
        ))

        conn.commit()
        conn.close()

        log_info(f"💾 Signal saved → {signal}")
        return signal

    except Exception as e:
        log_error(f"DB Insert Error: {e}")
        return None
