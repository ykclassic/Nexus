import sqlite3
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import ccxt
import traceback

from engine.elite_logger import log_event, log_error
from engine.discord_alert import send_discord_alert
from engine.trade_lifecycle import TradeLifecycle
from engine.exchange_retry import safe_exchange_call
from engine.approval import approve_signal
from engine.signals import generate_signal


# =========================
# CONFIG
# =========================
DB_PATH = "data/trading.db"

SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "ADA/USDT",
    "XRP/USDT", "DOGE/USDT", "SUI/USDT", "LTC/USDT", "LINK/USDT"
]

MAX_WORKERS = 5   # GitHub Actions safe
EXCHANGE_TIMEOUT = 10000


# =========================
# GLOBAL TRADE ENGINE
# =========================
trade_engine = TradeLifecycle()


# =========================
# DATABASE CONNECTION (THREAD SAFE)
# =========================
def get_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def insert_signal(signal, approved, gates, rr, score, reason):
    try:
        conn = get_db()
        c = conn.cursor()

        c.execute("""
            INSERT INTO signals (
                symbol, timeframe, signal_type, entry, tp, sl,
                rr, confidence, score, gates_passed, rejected, rejection_reason, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            signal["symbol"],
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
            reason,
            "OPEN" if approved else "REJECTED"
        ))

        conn.commit()
        conn.close()

    except Exception as e:
        log_error("DB_INSERT_FAILED", e)


# =========================
# EXCHANGE INSTANCE
# =========================
def get_exchange():
    return ccxt.gateio({
        "enableRateLimit": True,
        "timeout": EXCHANGE_TIMEOUT
    })


# =========================
# PROCESS SYMBOL (CORE LOGIC)
# =========================
def process_symbol(symbol):
    try:
        exchange = get_exchange()

        # Generate raw signal
        signal = generate_signal(exchange, symbol)

        if not signal:
            log_event("NO_SIGNAL", symbol=symbol)
            return None

        # Elite approval pipeline
        approved, gates, rr, score, reason = approve_signal(signal)

        # Save to DB
        insert_signal(signal, approved, gates, rr, score, reason)

        # If approved → open trade + Discord alert
        if approved:
            trade_id = str(uuid.uuid4())

            trade_engine.open_trade(
                trade_id=trade_id,
                symbol=signal["symbol"],
                entry=signal["entry"],
                sl=signal["sl"],
                tp=signal["tp"],
                confidence=signal["confidence"]
            )

            send_discord_alert(
                title="🧠 NEXUS ELITE SIGNAL APPROVED",
                message=f"{signal['symbol']} | {signal['signal_type']}",
                data={
                    "Entry": signal["entry"],
                    "Stop Loss": signal["sl"],
                    "Take Profit": signal["tp"],
                    "Confidence": f"{signal['confidence']:.2%}",
                    "RR": round(rr, 2),
                    "Score": round(score, 3),
                    "Filters Passed": f"{gates}/5"
                }
            )

            log_event(
                "SIGNAL_APPROVED",
                symbol=symbol,
                score=score,
                rr=rr,
                confidence=signal["confidence"]
            )

            return signal | {"score": score, "rr": rr}

        else:
            log_event("SIGNAL_REJECTED", symbol=symbol, reason=reason)
            return None

    except Exception as e:
        log_error("SYMBOL_PROCESS_CRASH", e, symbol=symbol)
        return None


# =========================
# MAIN ENGINE LOOP
# =========================
def run_engine():
    start = datetime.now(timezone.utc)

    log_event("ENGINE_START", time=start.isoformat())

    approved_signals = []

    try:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(process_symbol, sym): sym for sym in SYMBOLS}

            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        approved_signals.append(result)
                except Exception as e:
                    log_error("THREAD_CRASH", e)

        # Rank by score
        approved_signals.sort(key=lambda x: x["score"], reverse=True)

        if approved_signals:
            top = approved_signals[0]

            log_event(
                "TOP_SIGNAL_SELECTED",
                symbol=top["symbol"],
                score=top["score"]
            )

        else:
            log_event("NO_ELITE_SIGNALS")

    except Exception as e:
        log_error("ENGINE_FATAL_ERROR", e)

    duration = (datetime.now(timezone.utc) - start).total_seconds()

    log_event("ENGINE_END", duration=duration)

    return approved_signals
