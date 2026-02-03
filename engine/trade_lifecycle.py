from engine.elite_logger import log_event


def register_trade(conn, signal):
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            direction TEXT,
            entry REAL,
            sl REAL,
            tp REAL,
            confidence REAL,
            status TEXT DEFAULT 'OPEN',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        INSERT INTO trades(symbol, direction, entry, sl, tp, confidence)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        signal["symbol"],
        signal["direction"],
        signal["entry"],
        signal["sl"],
        signal["tp"],
        signal["confidence"]
    ))
    conn.commit()

    log_event(f"Trade registered: {signal['symbol']}")
