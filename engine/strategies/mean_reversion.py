def mean_reversion_signal(features):
    rsi = features["rsi"]
    return rsi < 35 or rsi > 65
