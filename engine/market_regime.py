def detect_market_regime(features):
    trend = features["trend_strength"]
    vol = features["volatility"]

    if trend > 0.5 and vol < 0.6:
        return "TRENDING"
    elif vol > 0.8:
        return "HIGH_VOLATILITY"
    else:
        return "RANGING"
