import numpy as np
import pandas as pd
from engine.exchange_retry import safe_exchange_call
from engine.elite_logger import log_event


# =========================
# CONFIG (QUALITY > QUANTITY)
# =========================
TIMEFRAME = "15m"
HTF_TIMEFRAME = "1h"

MIN_ATR_RATIO = 0.002      # volatility filter
RSI_LONG_MIN = 50
RSI_LONG_MAX = 70
RSI_SHORT_MIN = 30
RSI_SHORT_MAX = 50


# =========================
# TECHNICAL INDICATORS
# =========================
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def compute_atr(df, period=14):
    high_low = df["high"] - df["low"]
    high_close = np.abs(df["high"] - df["close"].shift())
    low_close = np.abs(df["low"] - df["close"].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    return true_range.rolling(period).mean()


def detect_trend(df):
    # Simple but powerful trend logic: EMA slope + structure
    ema_fast = df["close"].ewm(span=50).mean()
    ema_slow = df["close"].ewm(span=200).mean()

    if ema_fast.iloc[-1] > ema_slow.iloc[-1]:
        return "UP"
    elif ema_fast.iloc[-1] < ema_slow.iloc[-1]:
        return "DOWN"
    return "NEUTRAL"


def detect_structure(df):
    # Market structure: higher highs / lower lows
    highs = df["high"].rolling(5).max()
    lows = df["low"].rolling(5).min()

    if highs.iloc[-1] > highs.iloc[-2]:
        return "BULLISH"
    elif lows.iloc[-1] < lows.iloc[-2]:
        return "BEARISH"
    return "RANGE"


# =========================
# DATA FETCH
# =========================
def fetch_ohlcv(exchange, symbol, timeframe, limit=200):
    data = safe_exchange_call(exchange.fetch_ohlcv, symbol, timeframe, limit=limit)
    if not data:
        return None

    df = pd.DataFrame(data, columns=["ts", "open", "high", "low", "close", "volume"])
    return df


# =========================
# ELITE SIGNAL GENERATOR
# =========================
def generate_signal(exchange, symbol):
    df = fetch_ohlcv(exchange, symbol, TIMEFRAME)
    htf_df = fetch_ohlcv(exchange, symbol, HTF_TIMEFRAME)

    if df is None or htf_df is None or len(df) < 100:
        return None

    # Indicators
    df["rsi"] = compute_rsi(df["close"])
    df["atr"] = compute_atr(df)

    trend = detect_trend(htf_df)
    structure = detect_structure(df)

    last = df.iloc[-1]
    price = last["close"]
    rsi = last["rsi"]
    atr = last["atr"]

    # Volatility filter (kills low-quality signals)
    atr_ratio = atr / price
    if atr_ratio < MIN_ATR_RATIO:
        log_event("SIGNAL_BLOCKED", symbol=symbol, reason="Low volatility")
        return None

    signal_type = None

    # =========================
    # LONG LOGIC (HIGH QUALITY)
    # =========================
    if (
        trend == "UP" and
        structure == "BULLISH" and
        RSI_LONG_MIN < rsi < RSI_LONG_MAX
    ):
        signal_type = "LONG"

    # =========================
    # SHORT LOGIC (HIGH QUALITY)
    # =========================
    if (
        trend == "DOWN" and
        structure == "BEARISH" and
        RSI_SHORT_MIN < rsi < RSI_SHORT_MAX
    ):
        signal_type = "SHORT"

    if not signal_type:
        return None

    # =========================
    # TP / SL LOGIC (SMART RR)
    # =========================
    if signal_type == "LONG":
        sl = price - atr * 1.2
        tp = price + atr * 3.0
    else:
        sl = price + atr * 1.2
        tp = price - atr * 3.0

    confidence = round(
        min(
            0.95,
            0.5
            + (0.2 if trend in ["UP", "DOWN"] else 0)
            + (0.2 if structure in ["BULLISH", "BEARISH"] else 0)
            + (0.1 if atr_ratio > MIN_ATR_RATIO * 2 else 0)
        ),
        4,
    )

    return {
        "symbol": symbol,
        "timeframe": TIMEFRAME,
        "signal_type": signal_type,
        "entry": float(price),
        "sl": float(sl),
        "tp": float(tp),
        "confidence": confidence,
        "trend": trend,
        "structure": structure,
        "rsi": float(rsi),
        "atr": float(atr),
        "min_atr": MIN_ATR_RATIO * price,
        "atr_norm": atr_ratio,
    }
