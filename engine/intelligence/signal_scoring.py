# engine/intelligence/signal_scoring.py

def score_signal(features):
    score = 0

    if features.get("trend_strength", 0) > 0.6:
        score += 25

    if features.get("liquidity_sweep"):
        score += 20

    if features.get("volatility", 0) > 0.002:
        score += 20

    if features.get("rr_ratio", 0) >= 2.5:
        score += 20

    if features.get("structure_break"):
        score += 15

    return min(score, 100)
