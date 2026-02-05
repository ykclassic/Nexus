# Nexus/engine/intelligence/signal_scoring.py

def score_signal(signal):
    """
    Input: raw signal dict from strategy
    Output: confidence score (0 → 1)
    """

    entry = signal["entry"]
    tp = signal["tp"]
    sl = signal["sl"]

    # Risk-reward ratio
    rr = abs(tp - entry) / abs(entry - sl)

    score = 0.0

    # Reward high RR
    if rr >= 3:
        score += 0.4
    elif rr >= 2:
        score += 0.3
    elif rr >= 1.5:
        score += 0.2

    # Penalize tight SL (noise risk)
    sl_distance = abs(entry - sl) / entry
    if sl_distance > 0.003:
        score += 0.2

    # Direction bias (future AI hook)
    score += 0.3

    return min(round(score, 4), 1.0)
