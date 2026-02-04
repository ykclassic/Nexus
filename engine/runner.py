import ccxt
import pandas as pd
from engine.elite_logger import log_event, log_error
from engine.exchange_retry import safe_call
from engine.db.db_utils import init_db, get_conn
from engine.trade_lifecycle import register_trade
from engine.discord_alert import send_discord_alert

from engine.intelligence.feature_engine import compute_features
from engine.intelligence.market_regime import detect_market_regime
from engine.intelligence.consensus_engine import consensus
from engine.intelligence.probability_engine import probability_score
from engine.intelligence.signal_validator import validate_trade
from engine.intelligence.rarity_control import allow_signal

SYMBOLS = ["BTC/USDT","ETH/USDT","SOL/USDT","BNB/USDT","XRP/USDT"]
TIMEFRAME = "1h"


def fetch_ohlcv(exchange, symbol):
    data = safe_call(lambda: exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=200))
    if not data:
        return None
    df = pd.DataFrame(data, columns=["time","open","high","low","close","volume"])
    return df


def run_engine():
    init_db()
    log_event("🚀 Nexus Engine Started")

    exchange = ccxt.gateio({"enableRateLimit": True})
    approved = []
    signals_today = 0

    for symbol in SYMBOLS:
        try:
            df = fetch_ohlcv(exchange, symbol)
            if df is None:
                continue

            features = compute_features(df)
            regime = detect_market_regime(features)

            if not consensus(features, regime):
                continue

            entry = float(df["close"].iloc[-1])
            sl = entry * 0.99
            tp = entry * 1.03
            direction = "LONG"

            if not validate_trade(entry, sl, tp):
                continue

            confidence = probability_score(features)
            rr = abs(tp - entry) / abs(entry - sl)

            if not allow_signal(signals_today):
                continue

            signal = {
                "symbol": symbol,
                "direction": direction,
                "entry": round(entry, 4),
                "sl": round(sl, 4),
                "tp": round(tp, 4),
                "confidence": confidence,
                "rr": rr,
                "regime": regime,
                "features": features
            }

            conn = get_conn()
            register_trade(conn, signal)
            conn.close()

            approved.append(signal)
            signals_today += 1

        except Exception as e:
            log_error(f"{symbol} failed: {e}")

    if approved:
        best = sorted(approved, key=lambda s: s["confidence"], reverse=True)[0]
        send_discord_alert(best)
        log_event(f"🔥 Elite signal sent: {best['symbol']}")

    log_event(f"Engine finished | Signals: {len(approved)}")
