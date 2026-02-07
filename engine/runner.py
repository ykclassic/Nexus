from engine.config import SYMBOLS
from engine.db import init_db
from engine.signal_engine import generate_signal
from engine.trade_lifecycle import create_signal
from engine.logger import log_info

def run_engine():
    init_db()

    for symbol in SYMBOLS:
        signal = generate_signal(symbol)

        if signal:
            saved = create_signal(signal)
            if saved:
                log_info(f"🔥 Signal: {saved}")
