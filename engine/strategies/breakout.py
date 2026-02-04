def breakout_signal(features):
    if features["volatility"] > 0.5 and features["volume_spike"] > 1.2:
        return True
    return False
