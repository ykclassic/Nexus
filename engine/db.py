import sqlite3, os

DB_PATH = "data/trading.db"
os.makedirs("data", exist_ok=True)

def get_conn():
    return sqlite3.connect(DB_PATH, timeout=30)

def init_db():
    with get_conn() as conn:
        c = conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            exchange TEXT DEFAULT 'gateio',
            timeframe TEXT DEFAULT '1h',
            signal_type TEXT CHECK(signal_type IN ('LONG','SHORT')) NOT NULL,
            strategy TEXT DEFAULT 'nexus_alpha',

            entry REAL NOT NULL,
            tp REAL NOT NULL,
            sl REAL NOT NULL,

            confidence REAL DEFAULT 0.0,
            score REAL DEFAULT 0.0,

            status TEXT DEFAULT 'OPEN',
            result REAL DEFAULT NULL,
            exit_price REAL DEFAULT NULL,
            exit_time TEXT DEFAULT NULL,

            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT NULL
        )
        """)

        conn.commit()
