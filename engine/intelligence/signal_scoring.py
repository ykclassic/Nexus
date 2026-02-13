def score_signal(features):
    """
    Calculates a confidence score from 0-100 based on market features.
    """
    score = 0
    # Trend Strength (Placeholder for logic)
    score += 30 if features.get("trend") else 10
    
    # Liquidity Sweep logic
    if features.get("sweep"):
        score += 40
    
    # Volatility Check
    if features.get("volatility", 0) > 0.005:
        score += 30
        
    return min(score, 100)
