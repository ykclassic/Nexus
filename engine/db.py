import sqlite3
import os
from engine.config import DB_PATH

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        side TEXT CHECK(side IN ('LONG','SHORT')) NOT NULL,
        entry REAL NOT NULL,
        tp REAL NOT NULL,
        sl REAL NOT NULL,
        confidence REAL DEFAULT 0.0,
        status TEXT DEFAULT 'OPEN',
        created_at TEXT DEFAULT (datetime('now'))
    )
    """)
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH, timeout=30)
