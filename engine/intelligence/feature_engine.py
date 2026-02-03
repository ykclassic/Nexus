import pandas as pd
import numpy as np

def compute_features(df: pd.DataFrame) -> dict:
    close = df["close"]

    # Trend
    ema_fast = close.ewm(span=9).mean().iloc[-1]
    ema_slow = close.ewm(span=21).mean().iloc[-1]

    # Momentum
    rsi = compute_rsi(close)
    macd = ema_fast - ema_slow

    # Volatility
    atr = compute_atr(df)

    # Volume anomaly
    vol_spike = df["volume"].iloc[-1] / df["volume"].rolling(20).mean().iloc[-1]

    return {
        "ema_fast": ema_fast,
        "ema_slow": ema_slow,
        "rsi": rsi,
        "macd": macd,
        "atr": atr,
        "vol_spike": vol_spike,
    }


def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs)).iloc[-1]


def compute_atr(df, period=14):
    high_low = df["high"] - df["low"]
    high_close = np.abs(df["high"] - df["close"].shift())
    low_close = np.abs(df["low"] - df["close"].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    return ranges.max(axis=1).rolling(period).mean().iloc[-1]
