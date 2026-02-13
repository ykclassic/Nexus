import sqlite3
import os
from engine.config import DB_PATH
from engine.elite_logger import log_event, log_error

def get_connection():
    return sqlite3.connect(DB_PATH, timeout=30)

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    try:
        c = conn.cursor()
        
        # Check if table exists and has the correct columns
        c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='signals'")
        if c.fetchone()[0] == 1:
            # Check for 'symbol' column specifically
            c.execute("PRAGMA table_info(signals)")
            columns = [info[1] for info in c.fetchall()]
            if 'symbol' not in columns:
                log_event("⚠️ Outdated schema detected. Rebuilding signals table...")
                c.execute("DROP TABLE signals")
        
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
    except Exception as e:
        log_error(f"Database Init Error: {e}")
    finally:
        conn.close()
