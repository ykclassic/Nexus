def basic_filters(features: dict) -> bool:
    # Reject low volatility markets
    if features["atr"] < 0.001:
        return False

    # Reject weak volume
    if features["vol_spike"] < 1.2:
        return False

    # Reject neutral RSI
    if 45 < features["rsi"] < 55:
        return False

    return True
