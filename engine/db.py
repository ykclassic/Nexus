# engine/db.py

import sqlite3
import os
from engine.config import DB_PATH
from engine.logger import log_info

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH, timeout=30)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Drop old table if schema is incompatible (safe reset)
    c.execute("DROP TABLE IF EXISTS signals")

    c.execute("""
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        timeframe TEXT NOT NULL,
        direction TEXT NOT NULL,
        strategy TEXT NOT NULL,
        price REAL NOT NULL,
        confidence REAL NOT NULL,
        created_at TEXT DEFAULT (datetime('now'))
    )
    """)

    conn.commit()
    conn.close()

    log_info("✅ Database initialized with new schema")
