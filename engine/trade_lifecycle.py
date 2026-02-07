from datetime import datetime
from engine.db import get_connection
from engine.config import MIN_CONFIDENCE

def create_signal(signal: dict):
    if signal["confidence"] < MIN_CONFIDENCE:
        return None

    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO signals (asset, timeframe, direction, confidence, price, strategy, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        signal["asset"],
        "1h",
        signal["direction"],
        signal["confidence"],
        signal["price"],
        signal["strategy"],
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()

    return signal
