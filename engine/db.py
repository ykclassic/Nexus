import sqlite3
from engine.config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset TEXT,
        timeframe TEXT,
        direction TEXT,
        confidence REAL,
        price REAL,
        strategy TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()
