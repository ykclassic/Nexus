# signals.py
import pandas as pd
import numpy as np

# ============================
# CONFIG
# ============================

MIN_CONFIDENCE = 70
ATR_PERIOD = 14
ADX_PERIOD = 14
VOL_Z_PERIOD = 20
STRUCTURE_LOOKBACK = 20
LIQUIDITY_LOOKBACK = 10

# ============================
# UTILITY FUNCTIONS
# ============================

def calculate_atr(df, period=ATR_PERIOD):
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    return true_range.rolling(period).mean()

def calculate_adx(df, period=ADX_PERIOD):
    df = df.copy()

    df['up_move'] = df['high'] - df['high'].shift()
    df['down_move'] = df['low'].shift() - df['low']

    df['plus_dm'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), df['up_move'], 0)
    df['minus_dm'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), df['down_move'], 0)

    atr = calculate_atr(df, period)

    plus_di = 100 * (df['plus_dm'].rolling(period).mean() / atr)
    minus_di = 100 * (df['minus_dm'].rolling(period).mean() / atr)

    dx = (np.abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    adx = dx.rolling(period).mean()

    return adx

def volatility_zscore(df, period=VOL_Z_PERIOD):
    returns = df['close'].pct_change()
    vol = returns.rolling(period).std()
    mean = vol.rolling(period).mean()
    std = vol.rolling(period).std()
    return (vol - mean) / std

# ============================
# MARKET STRUCTURE DETECTION
# ============================

def detect_market_structure(df):
    highs = df['high'].rolling(STRUCTURE_LOOKBACK).max()
    lows = df['low'].rolling(STRUCTURE_LOOKBACK).min()

    structure = np.where(df['close'] > highs.shift(), "BULLISH_BREAK",
                np.where(df['close'] < lows.shift(), "BEARISH_BREAK", "RANGE"))

    return structure

# ============================
# LIQUIDITY SWEEP DETECTION
# ============================

def detect_liquidity_sweep(df):
    recent_high = df['high'].rolling(LIQUIDITY_LOOKBACK).max()
    recent_low = df['low'].rolling(LIQUIDITY_LOOKBACK).min()

    sweep_up = (df['high'] > recent_high.shift()) & (df['close'] < recent_high.shift())
    sweep_down = (df['low'] < recent_low.shift()) & (df['close'] > recent_low.shift())

    return sweep_up, sweep_down

# ============================
# ORDER FLOW APPROXIMATION
# ============================

def volume_delta(df):
    delta = np.where(df['close'] > df['open'], df['volume'], -df['volume'])
    return pd.Series(delta).rolling(10).sum()

# ============================
# SIGNAL GENERATOR
# ============================

def generate_signal(df):
    df = df.copy()

    df['ATR'] = calculate_atr(df)
    df['ADX'] = calculate_adx(df)
    df['VOL_Z'] = volatility_zscore(df)
    df['STRUCTURE'] = detect_market_structure(df)
    df['VOL_DELTA'] = volume_delta(df)

    sweep_up, sweep_down = detect_liquidity_sweep(df)

    last = df.iloc[-1]

    signal = "NONE"
    confidence = 0
    reasons = []

    # ============================
    # LONG LOGIC
    # ============================
    if (
        last['STRUCTURE'] == "BULLISH_BREAK" and
        sweep_down.iloc[-1] and
        last['ADX'] > 20 and
        last['VOL_Z'] > 0 and
        last['VOL_DELTA'] > 0
    ):
        signal = "LONG"
        confidence += 40
        reasons.append("Bullish structure break")
        confidence += min(last['ADX'], 40)
        confidence += min(abs(last['VOL_Z'] * 10), 20)

    # ============================
    # SHORT LOGIC
    # ============================
    elif (
        last['STRUCTURE'] == "BEARISH_BREAK" and
        sweep_up.iloc[-1] and
        last['ADX'] > 20 and
        last['VOL_Z'] > 0 and
        last['VOL_DELTA'] < 0
    ):
        signal = "SHORT"
        confidence += 40
        reasons.append("Bearish structure break")
        confidence += min(last['ADX'], 40)
        confidence += min(abs(last['VOL_Z'] * 10), 20)

    confidence = round(min(confidence, 100), 2)

    if confidence < MIN_CONFIDENCE:
        signal = "NONE"

    return {
        "signal": signal,
        "confidence": confidence,
        "atr": round(last['ATR'], 6),
        "adx": round(last['ADX'], 2),
        "volatility_z": round(last['VOL_Z'], 2),
        "structure": last['STRUCTURE'],
        "reasons": reasons
    }
