import sqlite3
from engine.db import get_connection

def generate_report():
    print("📊 --- Nexus Elite Performance Report --- 📊\n")
    
    conn = get_connection()
    try:
        curr = conn.cursor()
        
        # 1. Total Signals Generated
        curr.execute("SELECT COUNT(*) FROM signals")
        total_signals = curr.fetchone()[0]
        
        # 2. Breakdown by Symbol
        curr.execute("SELECT symbol, COUNT(*) FROM signals GROUP BY symbol ORDER BY COUNT(*) DESC")
        symbol_stats = curr.fetchall()
        
        # 3. Breakdown by Side (Long/Short)
        curr.execute("SELECT side, COUNT(*) FROM signals GROUP BY side")
        side_stats = curr.fetchall()

        # 4. Average Confidence
        curr.execute("SELECT AVG(confidence) FROM signals")
        avg_conf = curr.fetchone()[0] or 0

        # Display Results
        print(f"✅ Total Signals: {total_signals}")
        print(f"🎯 Avg Confidence: {avg_conf:.2f}%")
        print("\n📈 Signals by Asset:")
        for sym, count in symbol_stats:
            print(f" - {sym}: {count}")

        print("\n⚖️  Market Bias:")
        for side, count in side_stats:
            print(f" - {side}: {count}")

    except Exception as e:
        print(f"❌ Error reading database: {e}")
    finally:
        conn.close()
    
    print("\n" + "="*40)

if __name__ == "__main__":
    generate_report()
