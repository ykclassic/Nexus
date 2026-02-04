import sqlite3

DB_FILE = "data/trading.db"

def get_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_conn()
    with open("engine/db/schema.sql") as f:
        conn.executescript(f.read())
    conn.close()
