from concurrent.futures import ThreadPoolExecutor
from .exchange import create_exchange, safe_fetch
from .signals import generate_signal
from .lifecycle import update_trades
from .db import get_conn
from .config import SYMBOLS, TIMEFRAME, MAX_WORKERS
from .notifier import send
import logging

def process_symbol(exchange, conn, symbol):
    ohlcv = safe_fetch(exchange, symbol, TIMEFRAME)
    if not ohlcv:
        return None

    signal = generate_signal(symbol, ohlcv)
    if not signal:
        return None

    c = conn.cursor()
    c.execute("""
        INSERT INTO signals(symbol, signal_type, entry, tp, sl, confidence)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (signal["symbol"], signal["signal_type"], signal["entry"],
          signal["tp"], signal["sl"], signal["confidence"]))
    conn.commit()

    return signal

def run_engine():
    logging.info("Nexus Engine Started")

    exchange = create_exchange()
    with get_conn() as conn:

        update_trades(exchange, conn)

        signals = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
            for s in ex.map(lambda sym: process_symbol(exchange, conn, sym), SYMBOLS):
                if s:
                    signals.append(s)

        if signals:
            top = max(signals, key=lambda x: x["confidence"])
            send(f"🚀 TOP SIGNAL: {top['symbol']} {top['signal_type']} | Conf {top['confidence']:.2%}")

    logging.info("Nexus Engine Finished")
