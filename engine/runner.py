import time
import os
import requests
import ccxt
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from engine.config import SYMBOLS, MIN_CONFIDENCE, MAX_THREADS, TIMEFRAME
from engine.db import init_db, get_connection
from engine.elite_logger import log_event, log_error
from engine.discord_alert import send_discord_alert
from engine.intelligence.signal_scoring import score_signal

def fetch_market_data(exchange, symbol):
    """Fetches OHLCV and Ticker data, including timestamps for freshness verification."""
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=50)
        ticker = exchange.fetch_ticker(symbol)
        if not ohlcv or not ticker:
            return None
        
        return {
            "symbol": symbol,
            "price": ticker["last"],
            "timestamp": ohlcv[-1][0],  # Last candle timestamp in milliseconds
            "closes": [c[4] for c in ohlcv],
            "highs": [c[2] for c in ohlcv],
            "lows": [c[3] for c in ohlcv],
        }
    except Exception as e:
        log_error(f"Fetch error {symbol}: {e}")
        return None

def process_symbol(exchange, symbol):
    """Analyzes a single symbol for Trend + Sweep setups with freshness filtering."""
    market = fetch_market_data(exchange, symbol)
    if not market:
        return None

    # --- FEATURE: FRESHNESS CHECK ---
    # Ensure data is not older than 15 minutes (900 seconds)
    last_candle_time = market["timestamp"] / 1000
    current_time = time.time()
    if (current_time - last_candle_time) > 900:
        log_event(f"⏩ Skipping {symbol}: Stale data ({int((current_time - last_candle_time)/60)}m old)")
        return None

    # Logic: Simple Trend + Sweep
    short_ma = sum(market["closes"][-5:]) / 5
    long_ma = sum(market["closes"][-20:]) / 20
    trend = short_ma > long_ma
    
    sweep_low = market["lows"][-1] < min(market["lows"][-10:-1])
    sweep_high = market["highs"][-1] > max(market["highs"][-10:-1])

    side = None
    if trend and sweep_low:
        side = "LONG"
    elif not trend and sweep_high:
        side = "SHORT"
    
    if not side:
        return None

    # Intelligence Scoring
    confidence = score_signal({"trend": trend, "sweep": True, "volatility": 0.006})
    
    if confidence < MIN_CONFIDENCE:
        return None

    # Risk Management Calculation
    entry = market["price"]
    sl = entry * 0.995 if side == "LONG" else entry * 1.005
    tp = entry * 1.015 if side == "LONG" else entry * 0.985

    signal = {
        "symbol": symbol, 
        "side": side, 
        "entry": entry,
        "sl": sl, 
        "tp": tp, 
        "confidence": confidence,
        "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    }

    # FEATURE: PERSISTENCE - Save to DB
    conn = get_connection()
    try:
        curr = conn.cursor()
        curr.execute(
            "INSERT INTO signals (symbol, side, entry, tp, sl, confidence) VALUES (?, ?, ?, ?, ?, ?)",
            (symbol, side, entry, tp, sl, confidence)
        )
        conn.commit()
    finally:
        conn.close()

    # Dispatch Alert
    send_discord_alert(signal)
    log_event(f"🎯 Signal Generated: {symbol} {side} ({confidence}%)")
    return signal

def send_patience_message():
    """FEATURE: HEARTBEAT - Sends the 'Patience' message to Discord if no signals found."""
    webhook_url = os.getenv("DISCORD_WEBHOOK")
    if not webhook_url:
        return

    payload = {
        "username": "Nexus Command Centre",
        "embeds": [{
            "description": "🛡️ No high-probability setups detected this cycle.\n\n> *With Nexus, Patience is directly proportional to Profit*",
            "color": 8421504,
            "footer": {"text": "Nexus Intelligence Engine v2.0 | Heartbeat Active"}
        }]
    }
    try:
        requests.post(webhook_url, json=payload, timeout=10)
    except Exception as e:
        log_error(f"Patience message failed: {e}")

def run_engine():
    """Main execution loop using ThreadPoolExecutor for concurrent scanning."""
    log_event("🚀 Nexus Elite Engine Starting...")
    init_db()
    
    # Initialize exchange (Gate.io as specified)
    exchange = ccxt.gateio({"enableRateLimit": True})
    
    found_signals = []
    
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(process_symbol, exchange, s) for s in SYMBOLS]
        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    found_signals.append(result)
            except Exception as e:
                log_error(f"Thread execution error: {e}")

    # FEATURE: HEARTBEAT CHECK
    if not found_signals:
        log_event("⏳ No signals found. Sending patience alert.")
        send_patience_message()
    
    log_event("✅ Engine Cycle Complete")
