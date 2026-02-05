import sqlite3
import os
from engine.config import DB_PATH

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_conn():
    return sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)


def init_db():
    with get_conn() as conn:
        c = conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            exchange TEXT DEFAULT 'gateio',
            timeframe TEXT DEFAULT '5m',
            signal_type TEXT CHECK(signal_type IN ('LONG','SHORT')) NOT NULL,
            strategy TEXT DEFAULT 'nexus_elite',

            entry REAL NOT NULL,
            tp REAL NOT NULL,
            sl REAL NOT NULL,

            confidence REAL DEFAULT 0.0,

            status TEXT DEFAULT 'OPEN',
            exit_price REAL DEFAULT NULL,
            exit_time TEXT DEFAULT NULL,

            created_at TEXT DEFAULT (datetime('now'))
        )
        """)

        conn.commit()
