from concurrent.futures import ThreadPoolExecutor
from .exchange import create_exchange, safe_fetch
from .signals import generate_signal
from .lifecycle import update_trades
from .db import get_conn
from .config import SYMBOLS, TIMEFRAME, MAX_WORKERS
from .notifier import send
from .logger import log_error
import logging


def fetch_signal(exchange, symbol):
    """THREAD-SAFE: Only fetch data & generate signal."""
    try:
        ohlcv = safe_fetch(exchange, symbol, TIMEFRAME)
        if not ohlcv:
            return None

        signal = generate_signal(symbol, ohlcv)
        return signal
    except Exception as e:
        log_error(symbol, e)
        return None


def save_signal(conn, signal):
    """MAIN THREAD ONLY: Write to DB safely."""
    if not signal:
        return

    c = conn.cursor()
    c.execute("""
        INSERT INTO signals(symbol, signal_type, entry, tp, sl, confidence)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        signal["symbol"],
        signal["signal_type"],
        signal["entry"],
        signal["tp"],
        signal["sl"],
        signal["confidence"]
    ))
    conn.commit()


def run_engine():
    logging.info("Nexus Engine Started")

    exchange = create_exchange()

    with get_conn() as conn:

        # 1) Update existing trades (TP/SL lifecycle)
        update_trades(exchange, conn)

        # 2) Fetch signals in parallel (NO DB HERE)
        signals = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            results = executor.map(lambda s: fetch_signal(exchange, s), SYMBOLS)
            for sig in results:
                if sig:
                    signals.append(sig)

        # 3) Save signals sequentially (DB SAFE)
        for sig in signals:
            save_signal(conn, sig)

        # 4) Send top signal alert
        if signals:
            top = max(signals, key=lambda x: x["confidence"])
            send(
                f"🚀 TOP SIGNAL: {top['symbol']} {top['signal_type']} | "
                f"Entry {top['entry']:.4f} | TP {top['tp']:.4f} | SL {top['sl']:.4f} | "
                f"Conf {top['confidence']:.2%}"
            )

    logging.info("Nexus Engine Finished")
