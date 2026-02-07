import threading
from engine.config import SYMBOLS, TIMEFRAME, MAX_THREADS
from engine.trade_lifecycle import create_signal
from engine.exchange import fetch_price
from engine.logger import log_info


def process_symbol(symbol: str):
    price = fetch_price(symbol)

    # Example decision logic (you can plug AI here)
    direction = "LONG" if price % 2 == 0 else "SHORT"
    confidence = 0.75  # placeholder, replace with AI score

    signal = create_signal(
        asset=symbol,
        timeframe=TIMEFRAME,
        direction=direction,
        confidence=confidence,
        price=price,
        strategy="nexus_alpha"
    )

    if signal:
        log_info(f"✅ Signal created: {signal}")


def run_engine():
    threads = []

    for symbol in SYMBOLS:
        if len(threads) >= MAX_THREADS:
            break

        t = threading.Thread(target=process_symbol, args=(symbol,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
