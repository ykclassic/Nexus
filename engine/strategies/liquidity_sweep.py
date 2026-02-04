"""
Liquidity Sweep Strategy
Detects stop-hunt wicks + reversal probability
"""

def liquidity_sweep_signal(df):
    """
    df must contain: open, high, low, close
    """

    if len(df) < 5:
        return False

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # Detect long wick (stop hunt)
    candle_range = last["high"] - last["low"]
    body = abs(last["close"] - last["open"])
    wick_ratio = (candle_range - body) / candle_range if candle_range > 0 else 0

    # Sweep condition
    sweep = wick_ratio > 0.6  # long wick
    reversal = last["close"] > prev["close"]  # reversal signal

    return sweep and reversal
