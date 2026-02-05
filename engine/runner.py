# Nexus/engine/runner.py

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import ccxt

from Nexus.engine.config import SYMBOLS, MIN_CONFIDENCE, MAX_THREADS, TIMEFRAME
from Nexus.engine.db import init_db, get_connection
from Nexus.engine.elite_logger import log_event, log_error
from Nexus.engine.discord_alert import send_discord_alert
from Nexus.engine.exchange_retry import safe_call
from Nexus.engine.trade_lifecycle import create_signal
from Nexus.engine.intelligence.signal_scoring import score_signal


def fetch_market_data(exchange, symbol):
    ohlcv = safe_call(lambda: exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=50))
    ticker = safe_call(lambda: exchange.fetch_ticker(symbol))

    if not ohlcv or not ticker:
        return None

    closes = [c[4] for c in ohlcv]
    highs = [c[2] for c in ohlcv]
    lows = [c[3] for c in ohlcv]

    return {
        "symbol": symbol,
        "price": ticker["last"],
        "closes": closes,
        "highs": highs,
        "lows": lows,
    }


def elite_signal_logic(market):
    closes = market["closes"]
    highs = market["highs"]
    lows = market["lows"]
    price = market["price"]

    if len(closes) < 20:
        return None

    short_ma = sum(closes[-5:]) / 5
    long_ma = sum(closes[-20:]) / 20

    trend = "BULLISH" if short_ma > long_ma else "BEARISH"

    sweep_high = highs[-1] > max(highs[-10:-1])
    sweep_low = lows[-1] < min(lows[-10:-1])

    volatility = (max(highs[-10:]) - min(lows[-10:])) / price

    side = None
    if trend == "BULLISH" and sweep_low:
        side = "LONG"
    elif trend == "BEARISH" and sweep_high:
        side = "SHORT"

    if not side:
        return None

    # volatility filter (quality gate)
    if volatility < 0.002:
        return None

    entry = price

    if side == "LONG":
        sl = entry * 0.995
        tp = entry * 1.015
    else:
        sl = entry * 1.005
        tp = entry * 0.985

    return {
        "symbol": market["symbol"],
        "side": side,
        "entry": entry,
        "sl": sl,
        "tp": tp,
    }


def process_symbol(exchange, symbol):
    conn = get_connection()

    try:
        market = fetch_market_data(exchange, symbol)
        if not market:
            return None

        raw_signal = elite_signal_logic(market)
        if not raw_signal:
            return None

        confidence = score_signal(raw_signal)

        if confidence < MIN_CONFIDENCE:
            return None

        signal = {
            "symbol": raw_signal["symbol"],
            "side": raw_signal["side"],
            "entry": round(raw_signal["entry"], 6),
            "sl": round(raw_signal["sl"], 6),
            "tp": round(raw_signal["tp"], 6),
            "confidence": confidence,
        }

        create_signal(signal)
        send_discord_alert(signal)

        log_event(f"✅ Elite signal generated: {signal}")
        return signal

    except Exception as e:
        log_error(f"❌ Symbol processing error [{symbol}]: {e}")
        return None

    finally:
        conn.close()


def run_engine():
    start_time = time.time()

    log_event("🚀 Nexus Elite Engine Started")
    init_db()

    exchange = ccxt.gateio({"enableRateLimit": True})

    results = []
    errors = 0

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {
            executor.submit(process_symbol, exchange, symbol): symbol
            for symbol in SYMBOLS
        }

        for future in as_completed(futures):
            symbol = futures[future]
            try:
                result = future.result(timeout=15)
                if result:
                    results.append(result)
            except Exception as e:
                errors += 1
                log_error(f"Thread failure [{symbol}]: {e}")

    duration = round(time.time() - start_time, 2)

    log_event(
        f"📊 Engine Summary → Signals: {len(results)} | Errors: {errors} | Runtime: {duration}s"
    )

    return results
