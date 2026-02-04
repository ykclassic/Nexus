def probability_score(features):
    score = (
        features["trend_strength"] * 0.3 +
        features["momentum"] * 0.2 +
        features["volume_spike"] * 0.2 +
        (1 - features["volatility"]) * 0.15 +
        (1 if 40 < features["rsi"] < 60 else 0.15)
    )

    return round(score * 100, 2)
