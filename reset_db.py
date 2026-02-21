import sqlite3
import os
from engine.db import get_connection, init_db, DB_PATH

def hard_reset_database():
    print(f"🔍 Targeting database exactly at: {DB_PATH}")
    
    if os.path.exists(DB_PATH):
        print("🗑️ Existing database file located. Accessing...")
    else:
        print("⚠️ No database file found at that path. It will be created now.")

    conn = get_connection()
    try:
        curr = conn.cursor()
        
        # 1. Forcibly destroy the old table and its corrupted schema
        curr.execute("DROP TABLE IF EXISTS signals")
        conn.commit()
        print("🧨 Old 'signals' table completely destroyed.")
        
    except sqlite3.Error as e:
        print(f"❌ SQLite Error during drop: {e}")
    finally:
        conn.close()

    # 2. Rebuild the table using your correct db.py logic
    print("🏗️ Rebuilding fresh table schema...")
    init_db()
    
    print("✅ Hard reset complete. The database is now ready for the Engine and Reports.")

if __name__ == "__main__":
    hard_reset_database()
