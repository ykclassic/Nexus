import numpy as np

def generate_signal(symbol, ohlcv):
    closes = np.array([c[4] for c in ohlcv])
    sma_fast = closes[-5:].mean()
    sma_slow = closes[-20:].mean()

    entry = closes[-1]
    signal_type = None

    if sma_fast > sma_slow:
        signal_type = "LONG"
    elif sma_fast < sma_slow:
        signal_type = "SHORT"
    else:
        return None

    tp = entry * (1.01 if signal_type == "LONG" else 0.99)
    sl = entry * (0.995 if signal_type == "LONG" else 1.005)

    confidence = abs(sma_fast - sma_slow) / entry

    return {
        "symbol": symbol,
        "signal_type": signal_type,
        "entry": entry,
        "tp": tp,
        "sl": sl,
        "confidence": confidence
    }
