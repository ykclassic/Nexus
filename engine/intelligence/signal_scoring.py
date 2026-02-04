
def score_signal(features):
    """
    features = dict of signal metrics
    """
    score = 0

    if features.get("trend_strength", 0) > 0.7:
        score += 30

    if features.get("liquidity_sweep"):
        score += 25

    if features.get("rarity_score", 0) > 0.8:
        score += 25

    if features.get("probability", 0) > 0.75:
        score += 20

    return min(score, 100)
