import time
import ccxt
from concurrent.futures import ThreadPoolExecutor, as_completed

from engine.config import SYMBOLS, MIN_CONFIDENCE, MAX_THREADS, TIMEFRAME
from engine.db import init_db, get_connection
from engine.elite_logger import log_event, log_error
from engine.discord_alert import send_discord_alert
from engine.intelligence.signal_scoring import score_signal

def fetch_market_data(exchange, symbol):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=50)
        ticker = exchange.fetch_ticker(symbol)
        if not ohlcv or not ticker: return None
        
        return {
            "symbol": symbol,
            "price": ticker["last"],
            "closes": [c[4] for c in ohlcv],
            "highs": [c[2] for c in ohlcv],
            "lows": [c[3] for c in ohlcv],
        }
    except Exception as e:
        log_error(f"Fetch error {symbol}: {e}")
        return None

def process_symbol(exchange, symbol):
    market = fetch_market_data(exchange, symbol)
    if not market: return None

    # Logic: Simple Trend + Sweep
    short_ma = sum(market["closes"][-5:]) / 5
    long_ma = sum(market["closes"][-20:]) / 20
    trend = short_ma > long_ma
    sweep_low = market["lows"][-1] < min(market["lows"][-10:-1])
    sweep_high = market["highs"][-1] > max(market["highs"][-10:-1])

    side = None
    if trend and sweep_low: side = "LONG"
    elif not trend and sweep_high: side = "SHORT"
    
    if not side: return None

    confidence = score_signal({"trend": trend, "sweep": True, "volatility": 0.006})
    
    if confidence < MIN_CONFIDENCE:
        return None

    entry = market["price"]
    sl = entry * 0.995 if side == "LONG" else entry * 1.005
    tp = entry * 1.015 if side == "LONG" else entry * 0.985

    signal = {
        "symbol": symbol, "side": side, "entry": entry,
        "sl": sl, "tp": tp, "confidence": confidence
    }

    # Save to DB
    conn = get_connection()
    try:
        curr = conn.cursor()
        curr.execute("INSERT INTO signals (symbol, side, entry, tp, sl, confidence) VALUES (?, ?, ?, ?, ?, ?)",
                     (symbol, side, entry, tp, sl, confidence))
        conn.commit()
    finally:
        conn.close()

    send_discord_alert(signal)
    log_event(f"🎯 Signal Generated: {symbol} {side} ({confidence}%)")
    return signal

def run_engine():
    log_event("🚀 Nexus Elite Engine Starting...")
    init_db()
    exchange = ccxt.gateio({"enableRateLimit": True})
    
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(process_symbol, exchange, s) for s in SYMBOLS]
        for future in as_completed(futures):
            future.result()
    
    log_event("✅ Engine Cycle Complete")
