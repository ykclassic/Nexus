import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from engine.config import SYMBOLS, MIN_CONFIDENCE, MAX_THREADS, TIMEFRAME
from engine.db import init_db, get_conn
from engine.elite_logger import log_event, log_error
from engine.discord_alert import send_discord_alert
from engine.exchange_retry import safe_call
from engine.trade_lifecycle import create_signal
from engine.intelligence.signal_scoring import score_signal

import ccxt


def fetch_market_data(exchange, symbol):
    try:
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
    except Exception as e:
        log_error(f"Market data error [{symbol}]: {e}")
        return None


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

    if trend == "BULLISH" and sweep_low:
        side = "LONG"
    elif trend == "BEARISH" and sweep_high:
        side = "SHORT"
    else:
        return None

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
    conn = get_conn()

    try:
        market = fetch_market_data(exchange, symbol)
        if not market:
            return None

        raw_signal = elite_signal_logic(market)
        if not raw_signal:
            return None

        confidence = score_signal({
            "trend_strength": 0.8,
            "liquidity_sweep": True,
            "rarity_score": 0.7,
            "probability": 0.75,
        }) / 100.0

        if confidence < MIN_CONFIDENCE:
            return None

        signal = {
            "symbol": raw_signal["symbol"],
            "signal_type": raw_signal["side"],
            "entry": round(raw_signal["entry"], 6),
            "sl": round(raw_signal["sl"], 6),
            "tp": round(raw_signal["tp"], 6),
            "confidence": round(confidence, 4),
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

        for future in as_completed(futures, timeout=60):
            symbol = futures[future]
            try:
                result = future.result(timeout=10)
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
