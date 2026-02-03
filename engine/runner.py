import sqlite3
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import ccxt

from engine.approval import approve_signal
from engine.logger import log_event
from engine.signals import generate_signal

DB_PATH = "data/trading.db"
SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "ADA/USDT",
           "XRP/USDT", "DOGE/USDT", "SUI/USDT", "LTC/USDT", "LINK/USDT"]

MAX_WORKERS = 5   # safe for GitHub Actions
EXCHANGE_RETRIES = 3
DB_RETRIES = 3


# =========================
# DATABASE UTILS (THREAD SAFE)
# =========================
def get_db_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def safe_db_execute(query, params=()):
    for i in range(DB_RETRIES):
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute(query, params)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            log_event("ERROR", f"DB error attempt {i+1}: {e}")
            time.sleep(0.5)
    return False


# =========================
# EXCHANGE SAFE FETCH
# =========================
def get_exchange():
    return ccxt.gateio({
        "enableRateLimit": True,
        "timeout": 10000
    })


def safe_exchange_call(func, *args, **kwargs):
    for i in range(EXCHANGE_RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_event("ERROR", f"Exchange error attempt {i+1}: {e}")
            time.sleep(1)
    return None


# =========================
# PROCESS SINGLE SYMBOL
# =========================
def process_symbol(symbol):
    try:
        exchange = get_exchange()

        # Generate raw signal from strategy brain
        signal = generate_signal(exchange, symbol)

        if not signal:
            log_event("INFO", f"{symbol} → No signal generated")
            return None

        # Elite approval pipeline
        approved, gates, rr, score, reason = approve_signal(signal)

        # Insert signal into DB
        safe_db_execute("""
            INSERT INTO signals (
                symbol, timeframe, signal_type, entry, tp, sl,
                rr, confidence, score, gates_passed, rejected, rejection_reason
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            symbol,
            signal["timeframe"],
            signal["signal_type"],
            signal["entry"],
            signal["tp"],
            signal["sl"],
            rr,
            signal["confidence"],
            score,
            gates,
            0 if approved else 1,
            reason
        ))

        if approved:
            log_event("SUCCESS", f"APPROVED {symbol} | {signal['signal_type']} | score={score}")
            return signal | {"score": score, "rr": rr}
        else:
            log_event("INFO", f"REJECTED {symbol} → {reason}")
            return None

    except Exception as e:
        log_event("CRITICAL", f"{symbol} crashed: {traceback.format_exc()}")
        return None


# =========================
# MAIN ENGINE LOOP
# =========================
def run_engine():
    start_time = datetime.now(timezone.utc)
    log_event("INFO", "🚀 Nexus Engine Started")

    approved_signals = []

    # Threaded execution (safe)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_symbol, sym): sym for sym in SYMBOLS}

        for future in as_completed(futures):
            result = future.result()
            if result:
                approved_signals.append(result)

    # Sort by elite score
    approved_signals.sort(key=lambda x: x["score"], reverse=True)

    if approved_signals:
        top_signal = approved_signals[0]
        log_event("SUCCESS", f"🔥 TOP SIGNAL: {top_signal['symbol']} | score={top_signal['score']}")
    else:
        log_event("INFO", "No elite signals approved this cycle")

    duration = (datetime.now(timezone.utc) - start_time).total_seconds()
    log_event("INFO", f"⏱ Engine completed in {duration:.2f}s")

    return approved_signals
