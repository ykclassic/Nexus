# engine/runner.py

from engine.config import SYMBOLS
from engine.db import init_db
from engine.signal_engine import generate_signal
from engine.trade_lifecycle import create_signal
from engine.logger import log_info

def run_engine():
    log_info("🚀 Nexus Engine Started")

    init_db()

    results = []

    for symbol in SYMBOLS:
        signal = generate_signal(symbol)

        if signal:
            saved = create_signal(signal)
            if saved:
                results.append(saved)

    log_info(f"📊 Engine finished → {len(results)} signals generated")
    return results
