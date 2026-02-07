def score(confidence: float, strategy: str) -> float:
    weights = {
        "breakout": 1.05,
        "trend": 1.07,
        "mean_reversion": 1.02,
        "liquidity_sweep": 1.1,
        "nexus_ai": 1.15
    }
    return round(confidence * weights.get(strategy, 1.0), 4)
