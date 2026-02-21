import sqlite3
import os

# Ensure the data directory exists relative to the project root
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "trading.db")

def get_connection():
    """Establishes and returns a connection to the SQLite database."""
    # Create the data directory if it doesn't exist
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initializes the database schema. Creates the table if it doesn't exist."""
    conn = get_connection()
    try:
        curr = conn.cursor()
        # Create the table with the exact schema needed for the Nexus Engine
        curr.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                entry REAL NOT NULL,
                tp REAL NOT NULL,
                sl REAL NOT NULL,
                confidence REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("✅ Database initialized successfully at:", DB_PATH)
